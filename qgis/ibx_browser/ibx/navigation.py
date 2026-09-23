"""Catalog, baskets, objects and relationships.

Mirrors ``ch.interlis.ibx.navigation.Navigation``: catalog and relationship
pages come from the Q/R key ranges of the B+ tree, class pages from C, and
single objects from O or the FID ranges.
"""

import base64

from . import cbor, spatial
from .container import IbxError
from .objects import ObjectCursor, decode_record

CATALOG = "Q"
REVERSE = "R"


def _decode_cursor(after):
    if not after:
        return None
    try:
        return base64.urlsafe_b64decode(after)
    except (ValueError, TypeError) as error:
        raise IbxError("Invalid cursor") from error


def _encode_cursor(key):
    return base64.urlsafe_b64encode(key).decode("ascii")


def _check_limit(limit):
    if limit < 1 or limit > 256:
        raise IbxError("Page size must be 1..256")


class Navigation:
    """Read-only object and relationship access for one container."""

    def __init__(self, container):
        self.container = container
        self.meta = container.metadata
        self.reverse_indexed = bool(self.meta.get("reverseIndex"))
        self.concrete_classes = set(self.meta.get("concreteClasses") or ())

    # -- description --------------------------------------------------------

    def describe(self):
        return {
            "metadata": self.meta,
            "spatial": spatial.manifest(self.container),
        }

    # -- pages --------------------------------------------------------------

    def baskets(self, after=None, limit=256):
        _check_limit(limit)
        items, next_cursor = self.container.basket_page(after, limit)
        return {"items": items, "next": next_cursor}

    def catalog(self, after=None, limit=256):
        return self._index_page(CATALOG + "\0", after, limit, objects=False)

    def related(self, fid, after=None, limit=50):
        _check_limit(limit)
        if not self.reverse_indexed:
            return {"indexed": False, "items": []}
        page = self._index_page(
            REVERSE + "\0%d\0" % int(fid), after, limit, objects=True
        )
        page["indexed"] = True
        return page

    def _index_page(self, prefix, after, limit, objects):
        _check_limit(limit)
        cursor = self.container.tree.items(prefix, _decode_cursor(after))
        rows = []
        last = None
        try:
            while len(rows) < limit and cursor.has_next():
                last, value = cursor.next()
                try:
                    row = cbor.loads(value)
                except cbor.CborError as error:
                    raise IbxError("Invalid index row: %s" % error) from error
                if not isinstance(row, dict):
                    raise IbxError("Invalid index row")
                if objects:
                    row["object"] = self.object(int(row["sourceFid"]))
                rows.append(row)
            more = cursor.has_next()
        finally:
            cursor.close()
        return {"items": rows, "next": _encode_cursor(last) if more else None}

    # -- single objects -----------------------------------------------------

    def object(self, fid):
        location = self.container.get_fid(fid)
        if location is None:
            return None
        return self._first(location)

    def resolve(self, tid, bid=None):
        location = self.container.get_object(tid)
        if location is None:
            return None
        obj = self._first(location)
        if obj is None or (bid is not None and bid != obj.get("bid")):
            return None
        return obj

    def _first(self, location):
        cursor = FeatureCursor(self.container, self, [location])
        try:
            return cursor.next() if cursor.has_next() else None
        finally:
            cursor.close()

    # -- class queries ------------------------------------------------------

    def query(self, className, geometry=None, box=None, bids=()):
        if className not in self.concrete_classes:
            raise IbxError("Unknown concrete class: %s" % className)
        if box is not None:
            locations = spatial.candidates(
                self.container, className, geometry, box
            )
            locations = self.container.prefetch(locations)
        else:
            locations = self.container.get_class(className)
        return FeatureCursor(
            self.container, self, locations, className, set(bids or ())
        )


class FeatureCursor:
    """Lazily yields decoded objects of one class or location list."""

    def __init__(self, container, navigation, locations, className=None, bids=frozenset()):
        self.container = container
        self.navigation = navigation
        self.meta = container.metadata
        self.dictionary = self.meta.get("dictionary", [])
        self.locations = iter(locations)
        self.className = className
        self.bids = set(bids)
        self.cursor = None
        self.location = None
        self.basket = None
        self.offset = -1
        self.ordinal = 0
        self.closed = False
        self._next = None

    def has_next(self):
        if self._next is not None:
            return True
        if self.closed:
            return False
        while True:
            if self.location is None:
                try:
                    self.location = next(self.locations)
                except StopIteration:
                    self.close()
                    return False
            if self.location.chunk_offset == 0:
                self.location = None
                continue
            if self.cursor is None or self.offset != self.location.chunk_offset:
                if self.cursor is not None:
                    self.cursor.close()
                self.cursor = self.container.cursor(self.location)
                self.offset = self.location.chunk_offset
                self.ordinal = 0
                self.basket = self.container.basket(self.location)
                if self.location.ordinal > 0:
                    self.cursor.seek(self.location.ordinal)
                    self.ordinal = self.location.ordinal
            if self.bids and self.basket.get("bid") not in self.bids:
                self.location = None
                continue
            targeted = self.location.ordinal >= 0
            while self.cursor.has_next():
                current = self.ordinal
                self.ordinal += 1
                if targeted and current != self.location.ordinal:
                    self.cursor.skip_record()
                    continue
                record = self.cursor.next_record()
                if targeted:
                    self.location = None
                try:
                    name = self.dictionary[int(record[0])]
                except (IndexError, TypeError, ValueError) as error:
                    raise IbxError("Invalid dictionary id") from error
                if self.className is None or self.className == name:
                    obj = decode_record(self.meta, record)
                    obj["fid"] = self.cursor.first_fid + current
                    obj["bid"] = self.basket.get("bid")
                    self._next = obj
                    return True
                if targeted:
                    break
            self.location = None

    def next(self):
        if not self.has_next():
            raise StopIteration
        obj = self._next
        self._next = None
        return obj

    def close(self):
        if self.closed:
            return
        self.closed = True
        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None
        close = getattr(self.locations, "close", None)
        if close is not None:
            close()

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

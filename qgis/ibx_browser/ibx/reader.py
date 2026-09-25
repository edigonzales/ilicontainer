"""High-level read access to one IBX container.

Mirrors ``ch.interlis.ibx.api.IbxContainer`` for the read path: header, footer,
metadata, B+ tree, basket and object access plus optional prefetching.  The
writer, the XTF export and the CLI stay in Java.
"""

import base64
import threading
from array import array
from collections import OrderedDict

from . import cbor
from .container import (
    BASKET,
    CHUNK,
    HEADER_SIZE,
    METADATA,
    Chunk,
    FrameRef,
    FrameStore,
    IbxError,
    Location,
    Metrics,
    check_header,
    footer,
)
from .index import (
    BASKET_CHUNKS,
    BASKET_META,
    BASKET_ORDER,
    CLASS_CHUNKS,
    FID_RANGE,
    OBJECT,
    TOPIC,
    BTree,
    encode_key,
    starts_with,
)

DEFAULT_CACHE_BYTES = 32 * 1024 * 1024
CHUNK_CACHE_ENTRIES = 8
POSITION_CACHE_CHUNKS = 4096


class Container:
    """One open, read-only container; access is serialized by the caller."""

    def __init__(self, source, metrics=None, cache_bytes=DEFAULT_CACHE_BYTES):
        self.source = source
        self.metrics = metrics if metrics is not None else Metrics()
        self.store = FrameStore(source, self.metrics, cache_bytes)
        self.closed = False
        self._chunks = OrderedDict()
        self._chunks_lock = threading.Lock()
        # Record start offsets per chunk make repeated targeted lookups cheap.
        self._positions = OrderedDict()
        self._positions_lock = threading.Lock()
        try:
            self.version = check_header(source)
            (
                self.index_root,
                self.index_length,
                self.spatial_root,
                self.spatial_length,
            ) = footer(source)
            frame = self.store.read(HEADER_SIZE)
            if frame.type != METADATA:
                raise IbxError("Missing metadata")
            try:
                self.metadata = cbor.loads(frame.data)
            except cbor.CborError as error:
                raise IbxError("Invalid metadata: %s" % error) from error
            self._validate_metadata()
            self.tree = BTree(self.store, FrameRef(self.index_root, self.index_length))
        except Exception:
            source.close()
            raise

    def _validate_metadata(self):
        meta = self.metadata
        if not isinstance(meta, dict):
            raise IbxError("Invalid metadata")
        if str(meta.get("version")) not in ("2.3", "2.4") or int(meta.get("mappingVersion", 0)) != 1:
            raise IbxError("Unsupported transfer/mapping version")
        encoding = meta.get("geometryEncoding")
        if encoding not in ("iom", "wkb"):
            raise IbxError("Unsupported geometry profile/header combination")
        if encoding == "wkb" and meta.get("geometryProfile") != "wkb-iso-v1":
            raise IbxError("Unsupported geometry profile/header combination")
        for name in ("dictionary", "classes", "geometries", "scalarTypes"):
            if not isinstance(meta.get(name), dict if name != "dictionary" else list):
                raise IbxError("Invalid metadata field %s" % name)

    # -- source information -------------------------------------------------

    @property
    def size(self):
        return self.source.size()

    @property
    def index_ref(self):
        return FrameRef(self.index_root, self.index_length)

    @property
    def spatial_ref(self):
        return FrameRef(self.spatial_root, self.spatial_length)

    def state(self):
        return "%s:%s" % (self.metadata.get("datasetId"), self.source.revision())

    def close(self):
        if not self.closed:
            self.closed = True
            self.store.clear()
            with self._chunks_lock:
                self._chunks.clear()
            with self._positions_lock:
                self._positions.clear()
            self.source.close()

    def check_open(self):
        if self.closed:
            raise IbxError("Container closed")

    # -- baskets, chunks and locations --------------------------------------

    def basket(self, location):
        self.check_open()
        frame = self.store.read_ref(
            FrameRef(location.basket_offset, location.basket_length)
        )
        if frame.type != BASKET:
            raise IbxError("Invalid basket reference")
        try:
            basket = cbor.loads(frame.data)
        except cbor.CborError as error:
            raise IbxError("Invalid basket context: %s" % error) from error
        if not isinstance(basket, dict) or basket.get("position") != location.basket_position:
            raise IbxError("Basket position mismatch")
        return basket

    def objects(self, location):
        self.check_open()
        frame = self.store.read_ref(
            FrameRef(location.chunk_offset, location.chunk_length)
        )
        if frame.type != CHUNK:
            raise IbxError("Invalid chunk reference")
        with self._chunks_lock:
            chunk = self._chunks.get(location.chunk_offset)
            if chunk is None:
                chunk = Chunk.unpack(frame.data)
                self._chunks[location.chunk_offset] = chunk
                while len(self._chunks) > CHUNK_CACHE_ENTRIES:
                    self._chunks.popitem(last=False)
            else:
                self._chunks.move_to_end(location.chunk_offset)
        info = chunk.info
        if (
            info.get("id") != location.chunk_id
            or info.get("basketPosition") != location.basket_position
            or info.get("basketOffset") != location.basket_offset
            or location.ordinal >= int(info.get("count", 0))
        ):
            raise IbxError("Invalid object/chunk reference")
        return chunk

    def cursor(self, location):
        """Object cursor for one location, sharing cached record positions."""

        from .objects import ObjectCursor

        chunk = self.objects(location)
        key = location.chunk_offset
        with self._positions_lock:
            positions = self._positions.get(key)
            if positions is None:
                positions = array("Q", [0])
                self._positions[key] = positions
                while len(self._positions) > POSITION_CACHE_CHUNKS:
                    self._positions.popitem(last=False)
            else:
                self._positions.move_to_end(key)
        return ObjectCursor(chunk, positions=positions)

    # -- simple lookups ------------------------------------------------------

    def locations(self, prefix, after=None):
        cursor = self.tree.items(prefix, after)
        try:
            for _, value in cursor:
                yield Location.decode(value)
        finally:
            cursor.close()

    def get_class(self, name):
        self.check_open()
        if name not in (self.metadata.get("classes") or {}):
            raise IbxError("Unknown class: %s" % name)
        return self.locations(CLASS_CHUNKS + "\0" + name + "\0")

    def get_topic(self, name):
        self.check_open()
        if name not in (self.metadata.get("topics") or set()):
            raise IbxError("Unknown topic: %s" % name)
        return self.locations(TOPIC + "\0" + name + "\0")

    def get_object(self, tid):
        self.check_open()
        value = self.tree.get(OBJECT + "\0" + tid)
        return Location.decode(value) if value is not None else None

    def get_basket(self, bid):
        self.check_open()
        value = self.tree.get(BASKET_META + "\0" + bid)
        locations = []
        if value is not None:
            first = Location.decode(value)
            locations.append(first)
            locations.extend(
                self.locations(
                    BASKET_CHUNKS + "\0" + str(first.basket_position) + "\0"
                )
            )
        return locations

    def get_fid(self, fid):
        """Resolve a global FID through the F ranges; ``None`` when unknown."""

        self.check_open()
        if fid is None or fid < 0:
            return None
        entry = self.tree.floor(FID_RANGE + "\0" + str(fid))
        if entry is None or not starts_with(entry[0], encode_key(FID_RANGE + "\0")):
            return None
        value = entry[1]
        if len(value) != 57:
            raise IbxError("Invalid FID range")
        first = int.from_bytes(entry[0][-8:], "big")
        count = int.from_bytes(value[53:57], "big", signed=True)
        if count < 1 or first < 0 or first > 2**63 - 1 - count:
            raise IbxError("Invalid FID count")
        if fid - first >= count:
            return None
        location = Location.decode(value[:53])
        location.ordinal = int(fid - first)
        return location

    def basket_page(self, after=None, limit=256):
        """One page of baskets in container order: ``(items, next)``."""

        entries = []
        cursor = self.tree.items(
            BASKET_ORDER + "\0", base64.urlsafe_b64decode(after) if after else None
        )
        try:
            while len(entries) < limit and cursor.has_next():
                key, value = cursor.next()
                entries.append((key, Location.decode(value)))
            more = cursor.has_next()
        finally:
            cursor.close()
        items = []
        for _, location in entries:
            basket = self.basket(location)
            items.append({"bid": basket.get("bid"), "topic": basket.get("topic")})
        next_cursor = (
            base64.urlsafe_b64encode(entries[-1][0]).decode() if more else None
        )
        return items, next_cursor

    def prefetch(self, locations, positions=32, gap=4096, maximum=1024 * 1024):
        """Merge nearby frames for spatial cursors, like the Java container."""

        if positions <= 0:
            return locations

        def merged():
            ready = []
            iterator = iter(locations)
            while True:
                if not ready:
                    refs = []
                    for _ in range(positions):
                        try:
                            location = next(iterator)
                        except StopIteration:
                            break
                        ready.append(location)
                        refs.append(
                            FrameRef(location.basket_offset, location.basket_length)
                        )
                        if location.chunk_offset:
                            refs.append(
                                FrameRef(location.chunk_offset, location.chunk_length)
                            )
                    if refs:
                        self.store.prefetch(refs, gap, maximum)
                if not ready:
                    return
                yield ready.pop(0)

        return merged()

"""Immutable B+ tree directory of container format 4.

Mirrors ``ch.interlis.ibx.index.BTree`` and ``Keys`` for reading.  Pages are
prefix-compressed; long fields live in OVERFLOW frames.  Keys are compared as
unsigned bytes.
"""

import struct

from .container import (
    BRANCH,
    FOOTER_SIZE,
    HEADER_SIZE,
    LEAF,
    OVERFLOW,
    FrameRef,
    IbxError,
)

# Index prefixes, as ASCII bytes, before the structured key components.
BASKET_META = "B"
BASKET_ORDER = "P"
OBJECT = "O"
CLASS_CHUNKS = "C"
BASKET_CHUNKS = "D"
TOPIC = "T"
FID_RANGE = "F"
CATALOG = "Q"
REVERSE = "R"

_TEXT_PREFIXES = frozenset((BASKET_META, OBJECT, CATALOG))


def compare(first, second):
    """Unsigned lexicographic byte comparison."""

    common = len(first)
    if len(second) < common:
        common = len(second)
    for index in range(common):
        left = first[index]
        right = second[index]
        if left != right:
            return -1 if left < right else 1
    return (len(first) > len(second)) - (len(first) < len(second))


def starts_with(value, prefix):
    return value[: len(prefix)] == prefix


def common_prefix(first, second):
    length = min(len(first), len(second))
    index = 0
    while index < length and first[index] == second[index]:
        index += 1
    return index


def encode_key(key):
    """Encode a logical key such as ``C\\0Class\\0`` into its byte form.

    Numeric components become a marker byte and a non-negative i64; text
    components are NUL-escaped and terminated, exactly like ``Keys.encode``.
    """

    if "\0" not in key:
        return key.encode("utf-8")
    parts = key.split("\0")
    head = parts[0]
    if not head:
        raise IbxError("Empty index key")
    out = bytearray()
    out.append(ord(head[0]))
    for index in range(1, len(parts)):
        part = parts[index]
        if not part and index == len(parts) - 1:
            break
        text = (
            head in _TEXT_PREFIXES
            or (head == REVERSE and index == 3)
            or (head in (CLASS_CHUNKS, TOPIC) and index == 1)
            or part == "!basket"
        )
        if text:
            out.append(1)
            for byte in part.encode("utf-8"):
                out.append(byte)
                if byte == 0:
                    out.append(255)
            out.extend(b"\x00\x00")
        else:
            value = int(part)
            if value < 0:
                raise IbxError("Negative position key")
            out.append(2)
            out.extend(value.to_bytes(8, "big"))
    return bytes(out)


class BTree:
    """Read-only B+ tree; pages are fetched lazily through the frame store."""

    def __init__(self, store, root):
        self.store = store
        self.root = root if isinstance(root, FrameRef) else FrameRef(root, 0)

    def _page(self, ref):
        frame = self.store.read_ref(ref)
        if frame.type not in (LEAF, BRANCH):
            raise IbxError("Invalid B-tree page type")
        data = frame.data
        if len(data) < 4:
            raise IbxError("Invalid B-tree page")
        (count,) = struct.unpack_from(">i", data, 0)
        if count < 0 or count > len(data) // 8:
            raise IbxError("Invalid B-tree page count")
        position = 4
        previous = b""
        entries = []
        for index in range(count):
            (prefix,) = struct.unpack_from(">i", data, position)
            position += 4
            if prefix < 0 or prefix > len(previous) or (index == 0 and prefix != 0):
                raise IbxError("Invalid key prefix")
            suffix, position = self._field(data, position)
            key = previous[:prefix] + suffix
            value, position = self._field(data, position)
            if index > 0 and compare(previous, key) >= 0:
                raise IbxError("Invalid B-tree ordering")
            entries.append((key, value))
            previous = key
        if position != len(data):
            raise IbxError("Trailing index bytes")
        return frame.type == LEAF, entries

    def _field(self, data, position):
        if position + 4 > len(data):
            raise IbxError("Invalid index field")
        (size,) = struct.unpack_from(">i", data, position)
        position += 4
        if size == -1:
            if position + 16 > len(data):
                raise IbxError("Invalid overflow reference")
            ref = FrameRef(*struct.unpack_from(">qq", data, position))
            ref.validate(self.store.source.size() - FOOTER_SIZE)
            frame = self.store.read_ref(ref)
            if frame.type != OVERFLOW:
                raise IbxError("Invalid overflow reference")
            return frame.data, position + 16
        if size < 0 or size > len(data) - position:
            raise IbxError("Invalid index field length")
        return data[position:position + size], position + size

    @staticmethod
    def _pointer(value, parent):
        if len(value) != 16:
            raise IbxError("Invalid branch reference")
        ref = FrameRef.decode(value)
        if ref.offset >= parent or ref.offset < HEADER_SIZE:
            raise IbxError("Invalid/cyclic branch reference")
        return ref

    def get(self, key):
        wanted = encode_key(key)
        cursor = self.items(wanted)
        try:
            if cursor.has_next():
                entry = cursor.next()
                if entry[0] == wanted:
                    return entry[1]
            return None
        finally:
            cursor.close()

    def floor(self, key):
        """Largest entry with a key <= ``key``, or ``None``."""

        wanted = encode_key(key)
        ref = self.root
        for _ in range(65):
            leaf, entries = self._page(ref)
            found = None
            for entry in entries:
                if compare(entry[0], wanted) > 0:
                    break
                found = entry
            if found is None:
                return None
            if leaf:
                return found
            ref = self._pointer(found[1], ref.offset)
        raise IbxError("Excessive B-tree depth")

    def items(self, prefix, after=None):
        """Cursor over all entries whose key starts with ``prefix``."""

        if isinstance(prefix, str):
            prefix = encode_key(prefix)
        return Cursor(self, prefix, after)


class Cursor:
    __slots__ = ("tree", "prefix", "seek", "stack", "next_item")

    def __init__(self, tree, prefix, after=None):
        self.tree = tree
        self.prefix = prefix
        if after is not None and not starts_with(after, prefix):
            raise IbxError("Cursor outside query")
        self.seek = after if after is not None else prefix
        self.stack = []
        self.next_item = None
        self._descend(tree.root, True, 0)
        self._advance()
        if (
            after is not None
            and self.next_item is not None
            and compare(self.next_item[0], after) == 0
        ):
            self._advance()

    def _descend(self, ref, seek, depth):
        if depth + len(self.stack) > 64:
            raise IbxError("B-tree cycle/excessive depth")
        leaf, entries = self.tree._page(ref)
        if leaf:
            index = 0
            if seek:
                while index < len(entries) and compare(entries[index][0], self.seek) < 0:
                    index += 1
            self.stack.append([entries, index, True, ref.offset])
            return
        if not entries:
            raise IbxError("Empty branch")
        index = 0
        if seek:
            while index + 1 < len(entries) and compare(entries[index + 1][0], self.seek) <= 0:
                index += 1
        self.stack.append([entries, index + 1, False, ref.offset])
        child = self.tree._pointer(entries[index][1], ref.offset)
        self._descend(child, seek, depth + 1)

    def _advance(self):
        self.next_item = None
        while self.stack:
            level = self.stack[-1]
            entries, index = level[0], level[1]
            if index >= len(entries):
                self.stack.pop()
                continue
            level[1] = index + 1
            key, value = entries[index]
            if level[2]:
                if starts_with(key, self.prefix):
                    self.next_item = (key, value)
                    return
                self.stack.clear()
                return
            child = self.tree._pointer(value, level[3])
            self._descend(child, False, 0)

    def has_next(self):
        return self.next_item is not None

    def next(self):
        if self.next_item is None:
            raise StopIteration
        item = self.next_item
        self._advance()
        return item

    def close(self):
        self.stack.clear()
        self.next_item = None

    def __iter__(self):
        return self

    def __next__(self):
        if self.next_item is None:
            raise StopIteration
        return self.next()

"""Minimal CBOR decoder for the IBX container subset.

The Java writer uses Jackson's CBOR format.  Jackson emits definite-length
scalars and arrays, but indefinite-length maps for the generated structures.
The decoder therefore accepts both forms and covers every value the format
stores: unsigned and negative integers, byte and text strings, arrays, maps,
booleans, null and float16/32/64.  Tags 2 and 3 (big integers) are unwrapped
into Python integers; every other tag is rejected because the format does not
produce them and silently ignoring one would hide a real format change.

No encoder is provided: the plugin only reads.
"""

import struct


class CborError(ValueError):
    """Raised for malformed or unsupported CBOR input."""


_UNSIGNED = 0
_NEGATIVE = 1
_BYTES = 2
_TEXT = 3
_ARRAY = 4
_MAP = 5
_TAG = 6
_SIMPLE = 7

_UNSIGNED_BYTES = (1, 2, 4, 8)


class Decoder:
    """Streaming decoder; ``pos`` advances after every :meth:`decode` call.

    The implementation keeps the hot scalar paths free of helper calls because
    a full class scan decodes millions of small values.
    """

    __slots__ = ("data", "pos", "length")

    def __init__(self, data, pos=0):
        if not isinstance(data, (bytes, bytearray, memoryview)):
            raise CborError("CBOR input must be bytes")
        self.data = bytes(data)
        self.pos = pos
        self.length = len(self.data)

    def at_end(self):
        return self.pos >= self.length

    def decode(self):
        data = self.data
        pos = self.pos
        if pos >= self.length:
            raise CborError("Unexpected end of CBOR input")
        initial = data[pos]
        # Fast paths for the most frequent values: small integers, short text
        # and byte strings, and short arrays.  A full class scan decodes
        # millions of these.
        if initial < 0x18:
            self.pos = pos + 1
            return initial
        if 0x60 <= initial < 0x78:
            end = pos + 1 + initial - 0x60
            if end > self.length:
                raise CborError("Truncated CBOR text string")
            value = data[pos + 1:end].decode("utf-8")
            self.pos = end
            return value
        if 0x40 <= initial < 0x58:
            end = pos + 1 + initial - 0x40
            if end > self.length:
                raise CborError("Truncated CBOR byte string")
            value = data[pos + 1:end]
            self.pos = end
            return value
        if 0x20 <= initial < 0x38:
            self.pos = pos + 1
            return -1 - (initial - 0x20)
        if 0x80 <= initial < 0x98:
            count = initial - 0x80
            self.pos = pos + 1
            if count == 0:
                return []
            return self._decode_items(count)
        pos += 1
        major = initial >> 5
        info = initial & 0x1F
        if info < 24:
            argument = info
            raw = b""
        elif info < 28:
            end = pos + _UNSIGNED_BYTES[info - 24]
            if end > self.length:
                raise CborError("Truncated CBOR argument")
            raw = data[pos:end]
            argument = int.from_bytes(raw, "big")
            pos = end
        elif info == 31:
            argument = 0
            raw = b""
        else:
            raise CborError("Reserved CBOR additional information %d" % info)

        if major == _TEXT:
            if info == 31:
                self.pos = pos
                return self._chunks(_TEXT)
            end = pos + argument
            if end > self.length:
                raise CborError("Truncated CBOR text string")
            value = data[pos:end].decode("utf-8")
            self.pos = end
            return value
        if major == _ARRAY:
            if info == 31:
                self.pos = pos
                items = []
                while not self._at_break():
                    items.append(self.decode())
                self.pos += 1
                return items
            if argument == 0:
                self.pos = pos
                return []
            self.pos = pos
            return self._decode_items(argument)
        if major == _UNSIGNED:
            self.pos = pos
            return argument
        if major == _NEGATIVE:
            self.pos = pos
            return -1 - argument
        if major == _MAP:
            self.pos = pos
            result = {}
            if info == 31:
                while not self._at_break():
                    key = self.decode()
                    result[key] = self.decode()
                self.pos += 1
                return result
            for _ in range(argument):
                key = self.decode()
                result[key] = self.decode()
            return result
        if major == _BYTES:
            if info == 31:
                self.pos = pos
                return self._chunks(_BYTES)
            end = pos + argument
            if end > self.length:
                raise CborError("Truncated CBOR byte string")
            value = data[pos:end]
            self.pos = end
            return value
        if major == _TAG:
            if argument in (2, 3):
                self.pos = pos
                value = self.decode()
                if not isinstance(value, (bytes, bytearray)):
                    raise CborError("Invalid big integer payload")
                number = int.from_bytes(value, "big")
                return number if argument == 2 else -1 - number
            raise CborError("Unsupported CBOR tag %d" % argument)
        # major == _SIMPLE: `info` selects float widths and simple values.
        if info == 20:
            self.pos = pos
            return False
        if info == 21:
            self.pos = pos
            return True
        if info in (22, 23):
            self.pos = pos
            return None
        if info == 25:
            self.pos = pos
            return struct.unpack(">e", raw)[0]
        if info == 26:
            self.pos = pos
            return struct.unpack(">f", raw)[0]
        if info == 27:
            self.pos = pos
            return struct.unpack(">d", raw)[0]
        raise CborError("Unsupported CBOR simple value %d" % info)

    def skip(self):
        """Advance past one value without building Python objects.

        Object lookups skip many successful records inside a chunk; scanning
        their structure is much cheaper than decoding them.
        """

        data = self.data
        pos = self.pos
        if pos >= self.length:
            raise CborError("Unexpected end of CBOR input")
        initial = data[pos]
        pos += 1
        major = initial >> 5
        info = initial & 0x1F
        if info < 24:
            argument = info
        elif info < 28:
            end = pos + _UNSIGNED_BYTES[info - 24]
            if end > self.length:
                raise CborError("Truncated CBOR argument")
            argument = int.from_bytes(data[pos:end], "big")
            pos = end
        elif info == 31:
            argument = 0
        else:
            raise CborError("Reserved CBOR additional information %d" % info)
        self.pos = pos
        if major in (_UNSIGNED, _NEGATIVE, _SIMPLE):
            return
        if major in (_BYTES, _TEXT):
            if info == 31:
                while not self._at_break():
                    self.skip()
                self.pos += 1
                return
            end = pos + argument
            if end > self.length:
                raise CborError("Truncated CBOR string")
            self.pos = end
            return
        if major == _ARRAY:
            self.pos = pos
            if info == 31:
                while not self._at_break():
                    self._skip_values(1)
                self.pos += 1
                return
            self._skip_values(argument)
            return
        if major == _MAP:
            self.pos = pos
            if info == 31:
                while not self._at_break():
                    self._skip_values(2)
                self.pos += 1
                return
            self._skip_values(2 * argument)
            return
        if major == _TAG:
            self.skip()
            return
        raise CborError("Unsupported CBOR major type %d" % major)

    def _decode_items(self, count):
        """Decode ``count`` array items, handling scalars without a call."""

        data = self.data
        length = self.length
        items = []
        append = items.append
        for _ in range(count):
            pos = self.pos
            if pos >= length:
                raise CborError("Unexpected end of CBOR input")
            initial = data[pos]
            if initial < 0x18:
                append(initial)
                self.pos = pos + 1
                continue
            if 0x60 <= initial < 0x78:
                end = pos + 1 + initial - 0x60
                if end > length:
                    raise CborError("Truncated CBOR text string")
                append(data[pos + 1:end].decode("utf-8"))
                self.pos = end
                continue
            append(self.decode())
        return items

    def _skip_values(self, count):
        """Skip ``count`` values, handling inline scalars without a call."""

        data = self.data
        length = self.length
        for _ in range(count):
            pos = self.pos
            if pos >= length:
                raise CborError("Unexpected end of CBOR input")
            initial = data[pos]
            if initial < 0x18:
                self.pos = pos + 1
                continue
            if 0x60 <= initial < 0x78:
                end = pos + 1 + initial - 0x60
                if end > length:
                    raise CborError("Truncated CBOR text string")
                self.pos = end
                continue
            if 0x40 <= initial < 0x58:
                end = pos + 1 + initial - 0x40
                if end > length:
                    raise CborError("Truncated CBOR byte string")
                self.pos = end
                continue
            if 0x20 <= initial < 0x38:
                self.pos = pos + 1
                continue
            self.skip()

    def _at_break(self):
        if self.pos >= self.length:
            raise CborError("Unterminated indefinite-length item")
        return self.data[self.pos] == 0xFF

    def _chunks(self, major):
        if major == _BYTES:
            parts = []
            while not self._at_break():
                value = self.decode()
                if not isinstance(value, (bytes, bytearray)):
                    raise CborError("Invalid indefinite byte string chunk")
                parts.append(bytes(value))
            self.pos += 1
            return b"".join(parts)
        parts = []
        while not self._at_break():
            value = self.decode()
            if not isinstance(value, str):
                raise CborError("Invalid indefinite text string chunk")
            parts.append(value)
        self.pos += 1
        return "".join(parts)


def loads(data):
    """Decode exactly one CBOR value and reject trailing bytes."""

    decoder = Decoder(data)
    value = decoder.decode()
    if not decoder.at_end():
        raise CborError("Trailing bytes after CBOR value")
    return value

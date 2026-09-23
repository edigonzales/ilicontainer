"""Object records: decoding, cursors and page projection.

Mirrors ``ch.interlis.ibx.codec.ObjectCodec`` and
``ch.interlis.ibx.navigation.Navigation`` for reading.  Geometry values stay
WKB: they are passed to QGIS unchanged and never converted to IOM.
"""

import base64
from array import array

from . import cbor
from .container import IbxError


def plain_decimal(mantissa, scale):
    """Render ``mantissa * 10**-scale`` exactly like BigDecimal.toPlainString."""

    sign = "-" if mantissa < 0 else ""
    digits = str(abs(int(mantissa)))
    if scale <= 0:
        return sign + digits + "0" * (-scale)
    digits = "0" * (scale - len(digits) + 1) + digits
    return sign + digits[:-scale] + "." + digits[-scale:]


def _text(value):
    """Java's JsonNode.asText for numbers and booleans."""

    if value.__class__ is str or value is None:
        return value
    if value.__class__ is bool:
        return "true" if value else "false"
    if value.__class__ is int:
        return str(value)
    if value.__class__ is float:
        if value == int(value) and abs(value) < 2**53:
            return str(int(value))
        return repr(value)
    return str(value)


def _dictionary(meta):
    dictionary = meta.get("dictionary")
    if not isinstance(dictionary, list):
        raise IbxError("Invalid dictionary")
    return dictionary


def dictionary_name(meta, index):
    dictionary = _dictionary(meta)
    try:
        number = int(index)
    except (TypeError, ValueError):
        raise IbxError("Invalid dictionary id")
    if number < 0 or number >= len(dictionary):
        raise IbxError("Invalid dictionary id %s" % index)
    return dictionary[number]


def decode_value(meta, className, attribute, value):
    """Decode one attribute value into the plugin's presentation shape."""

    if value.__class__ is str:
        return {
            "kind": "scalar",
            "type": (meta.get("scalarTypes") or {}).get(className + "." + attribute),
            "value": value,
        }
    if value is None:
        return {
            "kind": "scalar",
            "type": (meta.get("scalarTypes") or {}).get(className + "." + attribute),
            "value": None,
        }
    if isinstance(value, list):
        return _structure(meta, value)
    if isinstance(value, dict):
        if "wkb" in value:
            return {
                "kind": "geometry",
                "descriptor": _text(value.get("geometry")),
                "wkb": base64.b64encode(value["wkb"]).decode("ascii"),
            }
        if "m" in value:
            return {
                "kind": "scalar",
                "type": (meta.get("scalarTypes") or {}).get(
                    className + "." + attribute
                ),
                "value": plain_decimal(
                    int.from_bytes(value["m"], "big", signed=True),
                    int(value.get("s", 0)),
                ),
            }
    return {
        "kind": "scalar",
        "type": (meta.get("scalarTypes") or {}).get(className + "." + attribute),
        "value": _text(value),
    }


def _structure(meta, value):
    child = decode_record(meta, value)
    reference = len(value) >= 3 and value[2] is not None
    child["kind"] = "reference" if reference else "structure"
    if reference:
        child["tid"] = _text(value[2])
        child["bid"] = _text(value[3]) if len(value) >= 4 and value[3] is not None else None
        child["order"] = int(value[4] or 0) if len(value) >= 5 else 0
    return child


def decode_record(meta, record):
    """Decode one CBOR object record into the navigation shape."""

    if record.__class__ is not list or len(record) != 8:
        raise IbxError("Invalid object record")
    dictionary = _dictionary(meta)
    size = len(dictionary)
    index = record[0]
    if index.__class__ is not int or index < 0 or index >= size:
        raise IbxError("Invalid dictionary id %r" % (index,))
    className = dictionary[index]
    attributes = record[7]
    if attributes.__class__ is not list:
        raise IbxError("Invalid object record")
    scalar_types = meta.get("scalarTypes") or {}
    fields = {}
    text_type = str
    list_type = list
    dict_type = dict
    for attribute in attributes:
        if attribute.__class__ is not list or len(attribute) != 2:
            raise IbxError("Invalid object attribute")
        name_index = attribute[0]
        if name_index.__class__ is not int or name_index < 0 or name_index >= size:
            raise IbxError("Invalid dictionary id %r" % (name_index,))
        name = dictionary[name_index]
        scalar_type = scalar_types.get(className + "." + name)
        values = attribute[1]
        if values.__class__ is not list:
            raise IbxError("Invalid object attribute values")
        decoded = []
        for value in values:
            kind = value.__class__
            if kind is text_type:
                decoded.append({"kind": "scalar", "type": scalar_type, "value": value})
            elif value is None:
                decoded.append({"kind": "scalar", "type": scalar_type, "value": None})
            elif kind is list_type:
                decoded.append(_structure(meta, value))
            elif kind is dict_type:
                if "wkb" in value:
                    decoded.append(
                        {
                            "kind": "geometry",
                            "descriptor": value.get("geometry"),
                            "wkb": base64.b64encode(value["wkb"]).decode("ascii"),
                        }
                    )
                elif "m" in value:
                    decoded.append(
                        {
                            "kind": "scalar",
                            "type": scalar_type,
                            "value": plain_decimal(
                                int.from_bytes(value["m"], "big", signed=True),
                                int(value.get("s", 0)),
                            ),
                        }
                    )
                else:
                    decoded.append(
                        {"kind": "scalar", "type": scalar_type, "value": _text(value)}
                    )
            else:
                decoded.append(
                    {"kind": "scalar", "type": scalar_type, "value": _text(value)}
                )
        fields[name] = decoded
    return {
        "className": className,
        "tid": _text(record[1]) if record[1] is not None else None,
        "fields": fields,
    }


class ObjectCursor:
    """Record cursor over one decompressed chunk.

    ``positions`` optionally shares record start offsets with other cursors of
    the same chunk.  Appends only extend a contiguous chain, so cursors that
    are not the one building the chain cannot corrupt it; callers still
    serialize container access like the Java API does.
    """

    __slots__ = ("decoder", "remaining", "first_fid", "count", "index", "positions")

    def __init__(self, chunk, positions=None):
        self.decoder = cbor.Decoder(chunk.objects)
        self.count = int(chunk.info.get("count", 0))
        self.remaining = self.count
        self.first_fid = int(chunk.info.get("firstFid", 0))
        self.index = 0
        if positions is None:
            positions = array("Q", [0])
        elif len(positions) == 0:
            positions.append(0)
        self.positions = positions

    def has_next(self):
        return self.remaining > 0

    def _advance(self):
        self.remaining -= 1
        self.index += 1
        positions = self.positions
        position = self.decoder.pos
        if self.index == len(positions) and position > positions[-1]:
            positions.append(position)
        if self.remaining == 0 and self.decoder.pos < self.decoder.length:
            raise IbxError("Too many objects in chunk")

    def next_record(self):
        if self.remaining <= 0:
            raise StopIteration
        decoder = self.decoder
        if decoder.pos >= decoder.length:
            raise IbxError("Too few objects in chunk")
        record = decoder.decode()
        self._advance()
        return record

    def skip_record(self):
        """Advance one record without decoding it (used by targeted lookups)."""

        if self.remaining <= 0:
            raise StopIteration
        decoder = self.decoder
        if decoder.pos >= decoder.length:
            raise IbxError("Too few objects in chunk")
        decoder.skip()
        self._advance()

    def seek(self, ordinal):
        """Move to the record with the given zero-based ordinal."""

        if ordinal <= 0:
            return
        positions = self.positions
        known = len(positions) - 1
        if ordinal <= known:
            self.decoder.pos = positions[ordinal]
        else:
            self.decoder.pos = positions[known]
            self.remaining = self.count - known
            self.index = known
            while self.index < ordinal:
                self.skip_record()
            return
        self.remaining = self.count - ordinal
        self.index = ordinal

    def close(self):
        self.remaining = 0


def page_item(obj, fid, bid, geometry=None, fields=None, no_geometry=False):
    """Project one decoded object into the paged query item shape."""

    attributes = {}
    wkb = None
    for name, values in obj.get("fields", {}).items():
        if geometry is not None and name == geometry:
            if values:
                wkb = values[0].get("wkb")
            continue
        if fields is not None and name not in fields:
            continue
        if len(values) == 1 and values[0].get("kind") == "geometry":
            continue
        if len(values) == 1 and values[0].get("kind") == "scalar":
            attributes[name] = values[0].get("value")
        else:
            attributes[name] = {"items": values}
    return {
        "fid": fid,
        "tid": obj.get("tid"),
        "bid": bid,
        "attributes": attributes,
        "wkb": None if no_geometry else wkb,
    }

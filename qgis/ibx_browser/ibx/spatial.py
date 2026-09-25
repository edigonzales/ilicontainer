"""Packed R-tree access for spatial candidate selection.

Mirrors the read side of ``ch.interlis.ibx.spatial.SpatialIndex``: the manifest
maps ``Class\\0Attribute`` to a root frame, and leaves carry conservative XY
bounding boxes plus physical object locations.  The index narrows candidates;
the exact geometric test stays with QGIS.
"""

import math
import struct

from . import cbor
from .remote import HttpRangeSource
from .container import (
    FOOTER_SIZE,
    HEADER_SIZE,
    SPATIAL_BRANCH,
    SPATIAL_LEAF,
    SPATIAL_MANIFEST,
    FrameRef,
    IbxError,
    Location,
)

KEY_SEPARATOR = "\0"


def index_key(className, attribute):
    return className + KEY_SEPARATOR + attribute


def manifest(container):
    """Return the spatial manifest, or an empty one when no index exists."""

    if not container.spatial_root:
        return {"indexes": {}}
    frame = container.store.read_ref(container.spatial_ref)
    if frame.type != SPATIAL_MANIFEST:
        raise IbxError("Invalid spatial manifest")
    try:
        data = cbor.loads(frame.data)
    except cbor.CborError as error:
        raise IbxError("Invalid spatial manifest: %s" % error) from error
    if not isinstance(data, dict) or not isinstance(data.get("indexes"), dict):
        raise IbxError("Invalid spatial manifest")
    return data


def index_info(container, className, attribute):
    indexes = manifest(container).get("indexes", {})
    info = indexes.get(index_key(className, attribute))
    if info is None:
        raise IbxError("No spatial index for %s.%s" % (className, attribute))
    return info


def _valid_box(box):
    if not isinstance(box, dict):
        return False
    try:
        values = [float(box[name]) for name in ("minX", "minY", "maxX", "maxY")]
    except (KeyError, TypeError, ValueError):
        return False
    if any(
        value != value or value in (float("inf"), float("-inf")) for value in values
    ):
        return False
    return values[0] <= values[2] and values[1] <= values[3]


def _intersects(box, query):
    return (
        box["minX"] <= query["maxX"]
        and box["maxX"] >= query["minX"]
        and box["minY"] <= query["maxY"]
        and box["maxY"] >= query["minY"]
    )


def candidates(container, className, attribute, box):
    """Return candidate locations in deterministic container order."""

    info = index_info(container, className, attribute)
    if info.get("leafLayout") not in (1, 2):
        raise IbxError("Unsupported spatial leaf layout")
    root = FrameRef(int(info["root"]), int(info["rootLength"]))
    locations = []
    _visit(container, root, box, locations, 0, int(info.get("leafLayout", 0)))
    locations.sort(key=Location.sort_key)
    return locations


def _visit(container, ref, box, locations, depth, leaf_layout):
    if depth > 64:
        raise IbxError("Spatial tree excessive depth")
    ref.validate(container.size - FOOTER_SIZE)
    frame = container.store.read_ref(ref)
    if frame.type not in (SPATIAL_LEAF, SPATIAL_BRANCH):
        raise IbxError("Invalid spatial node")
    layout = 3 if frame.type == SPATIAL_BRANCH else leaf_layout
    entries = decode_page(frame.data, layout, ref.offset, container.size - FOOTER_SIZE)
    if layout == 3:
        matches = [
            FrameRef(e["child"], e["childLength"])
            for e in entries
            if _intersects(e["box"], box)
        ]
        total = sum(ref.length for ref in matches)
        if (
            isinstance(container.source, HttpRangeSource)
            and len(matches) > 1
            and total <= min(container.store.budget, 1024 * 1024)
        ):
            container.store.prefetch(matches, 64 * 1024, 1024 * 1024)
    for entry in entries:
        if not isinstance(entry, dict) or not _valid_box(entry.get("box")):
            raise IbxError("Invalid spatial bounds")
        if not _intersects(entry["box"], box):
            continue
        if frame.type == SPATIAL_LEAF:
            raw = entry.get("location")
            if raw is None:
                raise IbxError("Invalid spatial location")
            location = Location.decode(raw)
            if location.ordinal < 0:
                raise IbxError("Invalid spatial location")
            locations.append(location)
        else:
            child = int(entry.get("child", 0))
            child_length = int(entry.get("childLength", 0))
            if child < HEADER_SIZE or child >= ref.offset:
                raise IbxError("Invalid/cyclic spatial pointer")
            _visit(
                container,
                FrameRef(child, child_length),
                box,
                locations,
                depth + 1,
                leaf_layout,
            )


def decode_page(data, expected_layout, offset, end):
    if len(data) < 8 or len(data) > 16384:
        raise IbxError("Invalid spatial page length")
    version, layout, reserved, count = struct.unpack_from(">BBHI", data)
    size = {1: 85, 2: 69, 3: 48}.get(layout)
    if version != 1 or layout != expected_layout or reserved or size is None:
        raise IbxError("Unsupported spatial page version/layout/reserved fields")
    if len(data) != 8 + count * size:
        raise IbxError("Invalid spatial entry count/length")
    entries = []
    position = 8
    for _ in range(count):
        x, y = struct.unpack_from(">dd", data, position)
        position += 16
        if layout == 2:
            xmax, ymax = x, y
        else:
            xmax, ymax = struct.unpack_from(">dd", data, position)
            position += 16
        box = dict(minX=x, minY=y, maxX=xmax, maxY=ymax)
        if not _valid_box(box):
            raise IbxError("Invalid spatial bounds")
        if layout == 2:
            box = dict(
                minX=math.nextafter(x, -math.inf),
                minY=math.nextafter(y, -math.inf),
                maxX=math.nextafter(x, math.inf),
                maxY=math.nextafter(y, math.inf),
            )
            if not _valid_box(box):
                raise IbxError("Invalid spatial bounds")
        entry = {"box": box}
        if layout == 3:
            child, length = struct.unpack_from(">qq", data, position)
            position += 16
            FrameRef(child, length).validate(end)
            if child >= offset or length > offset - child:
                raise IbxError("Invalid/cyclic spatial pointer")
            entry.update(child=child, childLength=length)
        else:
            raw = data[position : position + 53]
            position += 53
            loc = Location.decode(raw)
            if loc.ordinal < 0:
                raise IbxError("Invalid spatial location")
            FrameRef(loc.chunk_offset, loc.chunk_length).validate(end)
            FrameRef(loc.basket_offset, loc.basket_length).validate(end)
            entry["location"] = raw
        entries.append(entry)
    return entries

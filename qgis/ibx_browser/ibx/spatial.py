"""Packed R-tree access for spatial candidate selection.

Mirrors the read side of ``ch.interlis.ibx.spatial.SpatialIndex``: the manifest
maps ``Class\\0Attribute`` to a root frame, and leaves carry conservative XY
bounding boxes plus physical object locations.  The index narrows candidates;
the exact geometric test stays with QGIS.
"""

from . import cbor
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
    if any(value != value or value in (float("inf"), float("-inf")) for value in values):
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
    root = FrameRef(int(info["root"]), int(info["rootLength"]))
    locations = []
    _visit(container, root, box, locations, 0)
    locations.sort(key=Location.sort_key)
    return locations


def _visit(container, ref, box, locations, depth):
    if depth > 64:
        raise IbxError("Spatial tree excessive depth")
    ref.validate(container.size - FOOTER_SIZE)
    frame = container.store.read_ref(ref)
    if frame.type not in (SPATIAL_LEAF, SPATIAL_BRANCH):
        raise IbxError("Invalid spatial node")
    try:
        node = cbor.loads(frame.data)
    except cbor.CborError as error:
        raise IbxError("Invalid spatial node: %s" % error) from error
    entries = node.get("entries") if isinstance(node, dict) else None
    if not isinstance(entries, list):
        raise IbxError("Invalid spatial node")
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
            _visit(container, FrameRef(child, child_length), box, locations, depth + 1)

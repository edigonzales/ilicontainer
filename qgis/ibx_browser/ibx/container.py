"""Frames, sources, caching and chunk decoding of container format 4.

Mirrors ``ch.interlis.ibx.container`` and ``ch.interlis.ibx.remote`` for the
read path.  All binary fields are big endian; offsets are absolute byte
positions; every frame carries a CRC32 over its payload.
"""

import os
import struct
import threading
import zlib
from collections import OrderedDict

from . import cbor

MAGIC = b"IBXCONT1"
FOOTER_MAGIC = b"IBXFOOT1"
VERSION = 4
HEADER_SIZE = 16
FRAME_HEADER = 16
FOOTER_SIZE = 64

METADATA = 1
BASKET = 2
CHUNK = 3
END_BASKET = 4
END_TRANSFER = 5
LEAF = 6
BRANCH = 7
SPATIAL_LEAF = 8
SPATIAL_BRANCH = 9
SPATIAL_MANIFEST = 10
OVERFLOW = 11

FRAME_TYPES = {
    METADATA: "metadata",
    BASKET: "basket",
    CHUNK: "chunk",
    END_BASKET: "basket-end",
    END_TRANSFER: "transfer-end",
    LEAF: "index-leaf",
    BRANCH: "index-branch",
    SPATIAL_LEAF: "spatial-leaf",
    SPATIAL_BRANCH: "spatial-branch",
    SPATIAL_MANIFEST: "spatial-manifest",
    OVERFLOW: "overflow",
}

MAX_FRAME = 2**31 - 32

READ_COUNTERS = (
    "requests",
    "bytesRead",
    "indexBytes",
    "chunkBytes",
    "metadataBytes",
    "cacheHits",
    "chunksRead",
    "indexPages",
    "logicalReads",
    "logicalBytes",
    "prefetchedBytes",
    "additionalRangeBytes",
)


class IbxError(Exception):
    """Raised for malformed containers and unreadable sources."""


class Metrics:
    """Read counters shared by sources and the frame store."""

    __slots__ = READ_COUNTERS + ("maxCacheBytes",)

    def __init__(self):
        self.reset()

    def reset(self):
        for name in READ_COUNTERS:
            setattr(self, name, 0)
        self.maxCacheBytes = 0

    def snapshot(self):
        result = {name: int(getattr(self, name)) for name in READ_COUNTERS}
        result["maxCacheBytes"] = int(self.maxCacheBytes)
        return result


class Source:
    """Random-access byte source; local file or HTTPS range."""

    def size(self):
        raise NotImplementedError

    def read(self, offset, length):
        raise NotImplementedError

    def revision(self):
        return str(self.size())

    def close(self):
        pass


class LocalSource(Source):
    """Local file that detects replacement while it is open."""

    def __init__(self, path, metrics):
        self.path = os.fspath(path)
        self.metrics = metrics
        try:
            stat = os.stat(self.path)
        except OSError as error:
            raise IbxError("IBX-Datei nicht lesbar: %s" % error) from error
        self._identity = _identity(stat)
        self._file = open(self.path, "rb")
        self._lock = threading.Lock()

    def _check(self):
        try:
            stat = os.stat(self.path)
        except OSError as error:
            raise IbxError("IBX-Quelle wurde entfernt: %s" % error) from error
        if _identity(stat) != self._identity:
            raise IbxError("Local IBX source changed; reopen file")

    def size(self):
        return self._identity[0]

    def read(self, offset, length):
        self._check()
        if offset < 0 or length < 0 or offset > self.size() - length:
            raise IbxError("Range outside container")
        if length == 0:
            return b""
        if hasattr(os, "pread"):
            data = os.pread(self._file.fileno(), length, offset)
        else:
            with self._lock:
                self._file.seek(offset)
                data = self._file.read(length)
        if len(data) != length:
            raise IbxError("Short read from local file")
        self.metrics.bytesRead += length
        return data

    def close(self):
        self._file.close()


def _identity(stat):
    # st_ino/st_dev are zero on some platforms; size and mtime still detect
    # replacements, and every read re-checks them like the Java LocalSource.
    return (
        stat.st_size,
        getattr(stat, "st_mtime_ns", int(stat.st_mtime * 1e9)),
        getattr(stat, "st_ino", 0),
        getattr(stat, "st_dev", 0),
    )


def crc32(data):
    return zlib.crc32(data) & 0xFFFFFFFF


class FrameRef:
    __slots__ = ("offset", "length")

    def __init__(self, offset, length):
        self.offset = int(offset)
        self.length = int(length)

    def bytes(self):
        return struct.pack(">qq", self.offset, self.length)

    @staticmethod
    def decode(data):
        if len(data) != 16:
            raise IbxError("Invalid frame reference")
        ref = FrameRef(*struct.unpack(">qq", data))
        ref.validate(2**63 - 1)
        return ref

    def validate(self, limit):
        if (
            self.offset < HEADER_SIZE
            or self.length < FRAME_HEADER
            or self.length > MAX_FRAME
            or self.offset > limit
            or self.length > limit - self.offset
        ):
            raise IbxError("Invalid frame reference bounds")


class Frame:
    __slots__ = ("type", "data", "end")

    def __init__(self, type, data, end):
        self.type = type
        self.data = data
        self.end = end


def decode_frame(data, ref=None):
    if len(data) < FRAME_HEADER:
        raise IbxError("Invalid frame length")
    type, length, checksum = struct.unpack_from(">iqI", data, 0)
    if length < 0 or length > MAX_FRAME or FRAME_HEADER + length != len(data):
        raise IbxError("Invalid frame length")
    if ref is not None and len(data) != ref.length:
        raise IbxError("Frame reference length mismatch")
    payload = data[FRAME_HEADER:]
    if crc32(payload) != checksum:
        raise IbxError("Frame checksum mismatch")
    end = (ref.offset + ref.length) if ref is not None else len(data)
    return Frame(type, payload, end)


def read_frame(source, offset):
    if offset < HEADER_SIZE or offset > source.size() - FRAME_HEADER:
        raise IbxError("Invalid frame offset")
    header = source.read(offset, FRAME_HEADER)
    type, length, checksum = struct.unpack(">iqI", header)
    if (
        length < 0
        or length > MAX_FRAME
        or length > source.size() - offset - FRAME_HEADER
    ):
        raise IbxError("Invalid frame length")
    payload = source.read(offset + FRAME_HEADER, length)
    if crc32(payload) != checksum:
        raise IbxError("Frame checksum mismatch at %d" % offset)
    return Frame(type, payload, offset + FRAME_HEADER + length)


def read_ref(source, ref):
    ref.validate(source.size() - FOOTER_SIZE)
    return decode_frame(source.read(ref.offset, ref.length), ref)


def check_header(source):
    magic, version, features = struct.unpack(">8sII", source.read(0, HEADER_SIZE))
    if magic == b"ILICONT1":
        raise IbxError(
            "Containerformat %d wird nicht mehr unterstützt; aus dem "
            "ursprünglichen XTF neu erstellen." % version
        )
    if magic != MAGIC or version != VERSION or features != 0:
        raise IbxError("Unsupported IBX header/version/features")
    return version


def footer(source):
    size = source.size()
    if size < HEADER_SIZE + FOOTER_SIZE:
        raise IbxError("Truncated container")
    data = source.read(size - FOOTER_SIZE, FOOTER_SIZE)
    (
        magic,
        root,
        root_length,
        spatial,
        spatial_length,
        stored_size,
        version,
        reserved,
        checksum,
        tail,
    ) = struct.unpack(">qqqqqqiIII", data)
    if (
        struct.pack(">q", magic) != FOOTER_MAGIC
        or stored_size != size
        or version != VERSION
        or reserved != 0
        or tail != 0
        or checksum != crc32(data[:56])
    ):
        raise IbxError("Invalid/truncated footer")
    FrameRef(root, root_length).validate(size - FOOTER_SIZE)
    if spatial != 0:
        FrameRef(spatial, spatial_length).validate(size - FOOTER_SIZE)
    elif spatial_length != 0:
        raise IbxError("Invalid empty spatial reference")
    return root, root_length, spatial, spatial_length


class FrameStore:
    """Verified-frame cache with a byte budget, shared by all cursors."""

    def __init__(self, source, metrics, budget):
        self.source = source
        self.metrics = metrics
        self.budget = int(budget) if budget else 0
        self.used = 0
        self.cache = OrderedDict()
        self.lock = threading.RLock()
        if self.budget <= 0:  # Java default: 32 MiB
            self.budget = 32 * 1024 * 1024

    def read(self, offset):
        return self.read_ref(FrameRef(offset, 0))

    def read_ref(self, ref):
        with self.lock:
            metrics = self.metrics
            metrics.maxCacheBytes = max(metrics.maxCacheBytes, self.used)
            metrics.logicalReads += 1
            if ref.length > 0:
                metrics.logicalBytes += ref.length
            offset = ref.offset
            if ref.length > 0:
                ref.validate(self.source.size() - FOOTER_SIZE)
            frame = self.cache.get(offset)
            if frame is not None:
                if ref.length != 0 and len(frame.data) + FRAME_HEADER != ref.length:
                    raise IbxError("Cached reference length mismatch")
                metrics.cacheHits += 1
                return frame
            if ref.length == 0:
                frame = read_frame(self.source, offset)
                metrics.logicalBytes += len(frame.data) + FRAME_HEADER
            else:
                frame = read_ref(self.source, ref)
            self._record(frame)
            self._cache(offset, frame)
            return frame

    def _record(self, frame):
        size = len(frame.data) + FRAME_HEADER
        if frame.type == CHUNK:
            self.metrics.chunkBytes += size
            self.metrics.chunksRead += 1
        elif frame.type >= LEAF:
            self.metrics.indexBytes += size
            self.metrics.indexPages += 1
        else:
            self.metrics.metadataBytes += size

    def _cache(self, offset, frame):
        size = len(frame.data) + FRAME_HEADER
        if size <= self.budget and offset not in self.cache:
            while self.used + size > self.budget and self.cache:
                _, old = self.cache.popitem(last=False)
                self.used -= len(old.data) + FRAME_HEADER
            self.cache[offset] = frame
            self.used += size
            self.metrics.maxCacheBytes = max(self.metrics.maxCacheBytes, self.used)

    def prefetch(self, refs, gap, maximum):
        """Merge close ranges; only verified frames enter the shared cache."""

        with self.lock:
            pending = {}
            for ref in refs:
                ref.validate(self.source.size() - FOOTER_SIZE)
                if (
                    ref.length <= self.budget
                    and ref.length <= maximum
                    and ref.offset not in self.cache
                ):
                    pending[ref.offset] = ref
            group = []
            start = end = total = 0
            for ref in [pending[key] for key in sorted(pending)]:
                if group and (
                    ref.offset - end > gap
                    or ref.offset + ref.length - start > maximum
                    or total + ref.length > self.budget
                ):
                    self._fetch(group, start, end)
                    group, total = [], 0
                if not group:
                    start = ref.offset
                group.append(ref)
                end = ref.offset + ref.length
                total += ref.length
            if group:
                self._fetch(group, start, end)

    def _fetch(self, group, start, end):
        data = self.source.read(start, end - start)
        useful = 0
        frames = []
        for ref in group:
            begin = ref.offset - start
            frames.append(decode_frame(data[begin:begin + ref.length], ref))
            useful += ref.length
        self.metrics.prefetchedBytes += useful
        self.metrics.additionalRangeBytes += len(data) - useful
        for index, ref in enumerate(group):
            self._record(frames[index])
            self._cache(ref.offset, frames[index])

    def clear(self):
        with self.lock:
            self.cache.clear()
            self.used = 0


class Location:
    """53-byte physical object address: chunk, basket and ordinal."""

    __slots__ = (
        "codec",
        "chunk_offset",
        "chunk_length",
        "basket_offset",
        "basket_length",
        "basket_position",
        "chunk_id",
        "ordinal",
    )

    def __init__(
        self,
        chunk_offset,
        basket_offset,
        basket_position,
        chunk_id,
        ordinal=-1,
        chunk_length=0,
        basket_length=0,
        codec=1,
    ):
        self.codec = codec
        self.chunk_offset = chunk_offset
        self.chunk_length = chunk_length
        self.basket_offset = basket_offset
        self.basket_length = basket_length
        self.basket_position = basket_position
        self.chunk_id = chunk_id
        self.ordinal = ordinal

    def bytes(self):
        return struct.pack(
            ">bqqqqqqi",
            1,
            self.chunk_offset,
            self.chunk_length,
            self.basket_offset,
            self.basket_length,
            self.basket_position,
            self.chunk_id,
            self.ordinal,
        )

    @staticmethod
    def decode(data):
        if len(data) != 53:
            raise IbxError("Invalid location length")
        (
            codec,
            chunk,
            chunk_length,
            basket,
            basket_length,
            position,
            chunk_id,
            ordinal,
        ) = struct.unpack(">bqqqqqqi", data)
        if codec != 1:
            raise IbxError("Unsupported location codec")
        if (
            basket < HEADER_SIZE
            or basket_length < FRAME_HEADER
            or basket_length > MAX_FRAME
            or (
                chunk == 0
                and (chunk_length != 0 or ordinal != -1)
            )
            or (
                chunk != 0
                and (chunk < HEADER_SIZE or chunk_length < FRAME_HEADER)
            )
            or chunk_length > MAX_FRAME
            or ordinal < -1
            or position < 0
            or chunk_id < 0
        ):
            raise IbxError("Invalid location ordinal")
        return Location(
            chunk,
            basket,
            position,
            chunk_id,
            ordinal,
            chunk_length,
            basket_length,
            codec,
        )

    def sort_key(self):
        return (self.basket_position, self.chunk_id, self.ordinal)


class Chunk:
    """Chunk header plus decompressed CBOR object sequence."""

    __slots__ = ("info", "objects")

    def __init__(self, info, objects):
        self.info = info
        self.objects = objects

    @staticmethod
    def unpack(data):
        if len(data) < 4:
            raise IbxError("Invalid chunk header")
        header_length = struct.unpack_from(">i", data, 0)[0]
        if header_length < 0 or header_length > len(data) - 4:
            raise IbxError("Invalid chunk header")
        try:
            info = cbor.loads(data[4:4 + header_length])
        except cbor.CborError as error:
            raise IbxError("Invalid chunk metadata: %s" % error) from error
        if not isinstance(info, dict):
            raise IbxError("Invalid chunk metadata")
        first_fid = int(info.get("firstFid", -1))
        count = int(info.get("count", 0))
        uncompressed = int(info.get("uncompressedLength", -1))
        if (
            first_fid < 0
            or first_fid > 2**63 - 1 - count
            or count < 1
            or uncompressed < 0
            or uncompressed > MAX_FRAME
        ):
            raise IbxError("Invalid chunk dimensions")
        compressed = data[4 + header_length:]
        compression = info.get("compression")
        if compression == "zstd":
            from . import zstd

            try:
                raw = zstd.decompress(compressed, uncompressed)
            except zstd.ZstdUnavailable:
                raise
            except ValueError as error:
                raise IbxError("Invalid Zstandard chunk") from error
        elif compression == "deflate":
            try:
                raw = zlib.decompress(compressed)
            except zlib.error as error:
                raise IbxError("Invalid deflate chunk") from error
        elif compression == "none":
            raw = compressed
        else:
            raise IbxError("Unsupported compression %r" % (compression,))
        if len(raw) != uncompressed:
            raise IbxError("Chunk length mismatch")
        return Chunk(info, raw)

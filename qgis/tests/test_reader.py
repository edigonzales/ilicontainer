"""Java-free tests for the pure-Python IBX reader.

Run with any CPython 3.9+ (no QGIS, no Java)::

    PYTHONPATH=qgis python3 qgis/tests/test_reader.py -v

Zstandard-dependent cases are skipped when no libzstd can be found; the
``deflate`` and ``none`` fixtures always run.
"""

import glob
import hashlib
import http.server
import os
from pathlib import Path
import struct
import sys
import tempfile
import threading
import unittest
import urllib.parse

ROOT = Path(__file__).resolve().parents[2]
try:  # keep working when the packaged plugin is already on sys.path
    import ibx_browser  # noqa: F401
except ImportError:
    sys.path.insert(0, str(ROOT / "qgis"))

from ibx_browser.ibx import cbor, index, zstd  # noqa: E402
from ibx_browser.ibx.container import (  # noqa: E402
    FOOTER_SIZE,
    HEADER_SIZE,
    FrameRef,
    IbxError,
    LocalSource,
    Location,
    Metrics,
)
from ibx_browser.ibx.navigation import Navigation  # noqa: E402
from ibx_browser.ibx.objects import ObjectCursor, decode_record, plain_decimal  # noqa: E402
from ibx_browser.ibx.reader import Container  # noqa: E402
from ibx_browser.ibx.remote import HttpRangeSource  # noqa: E402

QUARTIER = ROOT / "demo/quartier.ibx"
PARKANLAGE = ROOT / "demo/parkanlage.ibx"
DEFLATE = Path(__file__).resolve().parent / "fixtures/deflate.ibx"
NONE = Path(__file__).resolve().parent / "fixtures/none.ibx"


def find_zstd():
    candidates = []
    app = os.environ.get("QGIS_APP")
    if app:
        candidates.append(f"{app}/Contents/Frameworks")
    candidates.extend(glob.glob("/Applications/QGIS*.app/Contents/Frameworks"))
    candidates.extend(["/opt/homebrew/lib", "/usr/local/lib", "/usr/lib/x86_64-linux-gnu"])
    try:
        return zstd.load(candidates) is not None
    except zstd.ZstdUnavailable:
        return False


HAVE_ZSTD = find_zstd()


def open_container(path):
    metrics = Metrics()
    source = LocalSource(str(path), metrics)
    container = Container(source, metrics)
    return container, Navigation(container)


class CborTests(unittest.TestCase):
    def test_scalars_and_containers(self):
        self.assertEqual(10, cbor.loads(b"\x0a"))
        self.assertEqual(-1, cbor.loads(b"\x20"))
        self.assertEqual(100, cbor.loads(b"\x18\x64"))
        self.assertEqual("abc", cbor.loads(b"\x63abc"))
        self.assertEqual(b"\x01\x02", cbor.loads(b"\x42\x01\x02"))
        self.assertEqual([1, 2], cbor.loads(b"\x82\x01\x02"))
        self.assertEqual({"a": 1}, cbor.loads(b"\xa1\x61a\x01"))
        self.assertIs(True, cbor.loads(b"\xf5"))
        self.assertIs(False, cbor.loads(b"\xf4"))
        self.assertIsNone(cbor.loads(b"\xf6"))
        self.assertEqual(1.5, cbor.loads(struct.pack(">Bd", 0xFB, 1.5)))
        self.assertEqual(1.5, cbor.loads(struct.pack(">Bf", 0xFA, 1.5)))
        self.assertEqual(1.5, cbor.loads(struct.pack(">Be", 0xF9, 1.5)))
        self.assertEqual(12345, cbor.loads(b"\xc2\x42\x30\x39"))
        self.assertEqual(-12346, cbor.loads(b"\xc3\x42\x30\x39"))

    def test_indefinite_length(self):
        self.assertEqual([1, 2], cbor.loads(b"\x9f\x01\x02\xff"))
        self.assertEqual({"a": 1}, cbor.loads(b"\xbf\x61a\x01\xff"))
        self.assertEqual(b"ab", cbor.loads(b"\x5f\x41a\x41b\xff"))
        self.assertEqual("ab", cbor.loads(b"\x7f\x61a\x61b\xff"))

    def test_malformed_input_is_rejected(self):
        for payload in (
            b"",
            b"\x18",
            b"\x82\x01",
            b"\x1c",
            b"\xfc",
            b"\xc4\x01",
            b"\x01\x02",
        ):
            with self.assertRaises(cbor.CborError, msg=payload):
                cbor.loads(payload)

    def test_decimal_rendering_matches_bigdecimal(self):
        for mantissa, scale, expected in [
            (0, 3, "0.000"),
            (5, 3, "0.005"),
            (12345, 3, "12.345"),
            (-12345, 3, "-12.345"),
            (12345, 0, "12345"),
            (12345, -2, "1234500"),
            (1, 1, "0.1"),
        ]:
            self.assertEqual(expected, plain_decimal(mantissa, scale))


class KeyTests(unittest.TestCase):
    def test_text_and_numeric_components(self):
        self.assertEqual(b"C\x01Foo\x00\x00", index.encode_key("C\0Foo\0"))
        self.assertEqual(b"O\x01g0\x00\x00", index.encode_key("O\0g0"))
        self.assertEqual(
            b"F\x02" + (7).to_bytes(8, "big"), index.encode_key("F\0" + "7")
        )
        self.assertEqual(
            b"R\x02" + (1).to_bytes(8, "big") + b"\x02" + (2).to_bytes(8, "big")
            + b"\x01/x\x00\x00",
            index.encode_key("R\0" + "1" + "\0" + "2" + "\0/x"),
        )
        self.assertEqual(b"Q\x01A\x00\x00", index.encode_key("Q\0A\0"))
        self.assertEqual(
            b"O\x01a\x00\x00\x01\x00\x00", index.encode_key("O\0a\0\x00")
        )

    def test_negative_positions_are_rejected(self):
        with self.assertRaises(IbxError):
            index.encode_key("F\0-1")

    def test_compare_is_unsigned(self):
        self.assertLess(index.compare(b"\x01", b"\xff"), 0)
        self.assertGreater(index.compare(b"\xff", b"\x01"), 0)


class ContainerTests(unittest.TestCase):
    def test_header_footer_and_metadata(self):
        container, navigation = open_container(QUARTIER)
        try:
            self.assertEqual(4, container.version)
            self.assertEqual(container.size, os.path.getsize(QUARTIER))
            metadata = navigation.describe()["metadata"]
            self.assertEqual("wkb", metadata["geometryEncoding"])
            self.assertEqual("2.4", metadata["version"])
            self.assertTrue(metadata["concreteClasses"])
        finally:
            container.close()

    def test_corrupt_payload_is_detected(self):
        data = bytearray(QUARTIER.read_bytes())
        data[HEADER_SIZE + 20] ^= 0xFF
        metrics = Metrics()
        with tempfile.NamedTemporaryFile(suffix=".ibx", delete=False) as handle:
            handle.write(bytes(data))
            path = handle.name
        try:
            source = LocalSource(path, metrics)
            with self.assertRaises(IbxError):
                Container(source)
        finally:
            os.unlink(path)

    def test_location_roundtrip_and_validation(self):
        location = Location(100, 200, 300, 400, 7, 53, 64)
        decoded = Location.decode(location.bytes())
        self.assertEqual(
            (100, 200, 300, 400, 7, 53, 64),
            (
                decoded.chunk_offset,
                decoded.basket_offset,
                decoded.basket_position,
                decoded.chunk_id,
                decoded.ordinal,
                decoded.chunk_length,
                decoded.basket_length,
            ),
        )
        with self.assertRaises(IbxError):
            Location.decode(b"\x00" * 53)
        with self.assertRaises(IbxError):
            Location.decode(b"\x01" * 52)

    def test_frame_ref_bounds(self):
        with self.assertRaises(IbxError):
            FrameRef(4, 16).validate(1000)
        with self.assertRaises(IbxError):
            FrameRef(HEADER_SIZE, 8).validate(1000)
        FrameRef(HEADER_SIZE, 16).validate(1000)

    def test_object_cursor_rejects_wrong_count(self):
        short = type(
            "Chunk", (), {"info": {"count": 2, "firstFid": 0}, "objects": b"\x01"}
        )()
        cursor = ObjectCursor(short)
        self.assertTrue(cursor.has_next())
        cursor.next_record()
        with self.assertRaises(IbxError):
            cursor.next_record()
        long = type(
            "Chunk", (), {"info": {"count": 1, "firstFid": 0}, "objects": b"\x01\x02"}
        )()
        with self.assertRaises(IbxError):
            ObjectCursor(long).next_record()


class NavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not HAVE_ZSTD:
            raise unittest.SkipTest("no libzstd available")
        cls.container, cls.navigation = open_container(QUARTIER)

    @classmethod
    def tearDownClass(cls):
        cls.container.close()

    def test_catalog_and_baskets(self):
        catalog = self.navigation.catalog(limit=256)
        self.assertEqual(7, len(catalog["items"]))
        self.assertIsNone(catalog["next"])
        names = {row["className"] for row in catalog["items"]}
        self.assertIn("Quartier.Unterhalt.Gebaeude", names)
        baskets = self.navigation.baskets()
        self.assertEqual(["leer", "nord", "sued"], sorted(b["bid"] for b in baskets["items"]))

    def test_object_lookup_by_tid_and_fid(self):
        obj = self.navigation.resolve("g0")
        self.assertEqual("Quartier.Unterhalt.Gebaeude", obj["className"])
        self.assertEqual("nord", obj["bid"])
        by_fid = self.navigation.object(obj["fid"])
        self.assertEqual(obj["tid"], by_fid["tid"])
        self.assertIsNone(self.navigation.resolve("missing"))
        self.assertIsNone(self.navigation.object(10**6))
        self.assertIsNone(self.navigation.resolve("g0", "sued"))

    def test_class_scan_and_geometry(self):
        cursor = self.navigation.query("Quartier.Unterhalt.Gebaeude", "Grundriss")
        objects = list(cursor)
        self.assertEqual(24, len(objects))
        geometry = objects[0]["fields"]["Grundriss"][0]
        self.assertEqual("geometry", geometry["kind"])
        self.assertTrue(geometry["wkb"])
        with self.assertRaises(IbxError):
            self.navigation.query("Quartier.Unterhalt.Unbekannt", None)

    def test_bbox_uses_spatial_index(self):
        before = self.container.metrics.chunksRead
        cursor = self.navigation.query(
            "Quartier.Unterhalt.Gebaeude",
            "Grundriss",
            {"minX": 2600001, "minY": 1200001, "maxX": 2600010, "maxY": 1200010},
        )
        items = list(cursor)
        self.assertEqual(["g0"], [item["tid"] for item in items])
        self.assertEqual(before + 1, self.container.metrics.chunksRead)

    def test_related_pages(self):
        order = self.navigation.resolve("auftrag0")
        page = self.navigation.related(order["fid"], limit=2)
        self.assertTrue(page["indexed"])
        self.assertEqual(2, len(page["items"]))
        collected = list(page["items"])
        while page["next"]:
            page = self.navigation.related(order["fid"], page["next"], limit=2)
            collected.extend(page["items"])
        self.assertEqual(7, len(collected))
        self.assertTrue(all("object" in row for row in collected))
        self.assertEqual(
            7, len({(row["sourceFid"], row["path"]) for row in collected})
        )

    def test_targeted_reads_match_sequential_positions(self):
        sequential = list(
            self.navigation.query("Quartier.Unterhalt.Gebaeude", "Grundriss")
        )
        self.assertEqual(24, len(sequential))
        for expected in reversed(sequential):
            found = self.navigation.object(expected["fid"])
            self.assertEqual(expected["tid"], found["tid"])
            self.assertEqual(expected["className"], found["className"])
            self.assertEqual(expected["fid"], found["fid"])

    def test_missing_index_and_unknown_operations(self):
        page = self.navigation.related(10**6)
        self.assertEqual([], page["items"])


class CompressionTests(unittest.TestCase):
    def test_deflate_fixture(self):
        container, navigation = open_container(DEFLATE)
        try:
            self.assertTrue(navigation.describe()["metadata"]["concreteClasses"])
            cursor = navigation.query("Parkanlage.Park.Spielgeraet", "Position")
            self.assertGreater(len(list(cursor)), 0)
            self.assertEqual(
                "deflate",
                self._compression(container, "Parkanlage.Park.Spielgeraet"),
            )
        finally:
            container.close()

    def test_none_fixture(self):
        container, navigation = open_container(NONE)
        try:
            cursor = navigation.query("Parkanlage.Park.Spielgeraet", "Position")
            self.assertGreater(len(list(cursor)), 0)
            self.assertEqual(
                "none", self._compression(container, "Parkanlage.Park.Spielgeraet")
            )
        finally:
            container.close()

    @staticmethod
    def _compression(container, className):
        for location in container.get_class(className):
            chunk = container.objects(location)
            return chunk.info["compression"]
        raise AssertionError("no chunk")

    @unittest.skipUnless(HAVE_ZSTD, "no libzstd available")
    def test_zstd_fixture(self):
        container, navigation = open_container(QUARTIER)
        try:
            self.assertEqual(
                "zstd",
                self._compression(container, "Quartier.Unterhalt.Gebaeude"),
            )
        finally:
            container.close()

    @unittest.skipUnless(HAVE_ZSTD, "no libzstd available")
    def test_zstd_library_reports_version(self):
        self.assertGreaterEqual(zstd.version(), 10500)


class HttpRangeTests(unittest.TestCase):
    """Core range semantics against a local HTTP server (no TLS, no QGIS)."""

    def setUp(self):
        self.data = DEFLATE.read_bytes()
        self.tag = '"' + hashlib.sha256(self.data).hexdigest() + '"'
        self.requests = []
        self.behaviour = {}
        test = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                if test.behaviour.get("full"):
                    self.send_response(200)
                    self.send_header("Content-Length", str(len(test.data)))
                    self.end_headers()
                    self.wfile.write(test.data)
                    return
                value = self.headers.get("Range")
                if value is None:
                    self.send_response(200)
                    self.end_headers()
                    return
                start, end = map(int, value[6:].split("-"))
                test.requests.append((start, end, self.headers.get("If-Match")))
                tag = test.behaviour.get("tag", test.tag)
                if test.behaviour.get("no_etag"):
                    tag = None
                self.send_response(206)
                self.send_header("Content-Range", f"bytes {start}-{end}/{len(test.data)}")
                self.send_header("Content-Length", str(end - start + 1))
                if tag:
                    self.send_header("ETag", tag)
                self.end_headers()
                self.wfile.write(test.data[start : end + 1])

        self.server = http.server.ThreadingHTTPServer(("localhost", 0), Handler)
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(self.server.shutdown)
        self.addCleanup(self.server.server_close)
        self.url = f"http://localhost:{self.server.server_port}/data.ibx"

    def source(self, **options):
        return HttpRangeSource(self.url, options, Metrics())

    def test_range_reads_and_etag_pinning(self):
        source = self.source()
        try:
            header = source.read(0, 16)
            self.assertEqual(b"IBXCONT1", header[:8])
            size = source.size()
            self.assertEqual(len(self.data), size)
            tail = source.read(size - FOOTER_SIZE, FOOTER_SIZE)
            self.assertEqual(self.data[-FOOTER_SIZE:], tail)
            self.assertTrue(self.requests[0][2] is None)
            self.assertTrue(all(tag == self.tag for _, _, tag in self.requests[1:]))
        finally:
            source.close()

    def test_etag_change_aborts(self):
        source = self.source()
        try:
            self.behaviour["tag"] = '"changed"'
            with self.assertRaises(IbxError):
                source.read(16, 32)
        finally:
            source.close()

    def test_weak_or_missing_etag_is_rejected(self):
        self.behaviour["no_etag"] = True
        with self.assertRaises(IbxError):
            self.source()
        self.behaviour["no_etag"] = False
        self.assertTrue(self.source(immutableUrl=True))

    def test_full_response_needs_explicit_permission(self):
        self.behaviour["full"] = True
        with self.assertRaises(IbxError):
            self.source()
        source = self.source(allowFullDownload=True)
        try:
            self.assertEqual(len(self.data), source.size())
            self.assertEqual(self.data[16:48], source.read(16, 32))
            self.assertIsNotNone(source.snapshot)
        finally:
            source.close()


class ReaderAcceptanceTests(unittest.TestCase):
    def test_demo_files_are_unchanged_by_reading(self):
        files = [DEFLATE, NONE]
        if HAVE_ZSTD:
            files.append(QUARTIER)
        for path in files:
            with self.subTest(path=path.name):
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                container, navigation = open_container(path)
                try:
                    for name in navigation.concrete_classes:
                        for _ in navigation.query(name):
                            pass
                finally:
                    container.close()
                self.assertEqual(digest, hashlib.sha256(path.read_bytes()).hexdigest())

    @unittest.skipUnless(HAVE_ZSTD, "no libzstd available")
    def test_parkanlage_relationships(self):
        container, navigation = open_container(PARKANLAGE)
        try:
            device = navigation.resolve("geraet1")
            self.assertEqual("Parkanlage.Park.Spielgeraet", device["className"])
            self.assertEqual("geraet1", device["tid"])
            playground = navigation.resolve("park0")
            related = navigation.related(playground["fid"])
            self.assertEqual(2, len(related["items"]))
            self.assertTrue(all("object" in row for row in related["items"]))
        finally:
            container.close()


if __name__ == "__main__":
    unittest.main()

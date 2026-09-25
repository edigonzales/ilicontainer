import json
import math
from pathlib import Path
import struct
import unittest
from ibx_browser.ibx.spatial import decode_page
from ibx_browser.ibx.container import IbxError, check_header


class SpatialCodecTest(unittest.TestCase):
    def test_format4_is_rejected(self):
        class Source:
            def read(self, offset, length):
                return struct.pack(">8sII", b"IBXCONT1", 4, 0)

        with self.assertRaisesRegex(IbxError, "format 4"):
            check_header(Source())

    def test_shared_fixtures_and_corruption(self):
        cases = json.loads(
            (Path(__file__).parent / "fixtures/spatial-pages.json").read_text()
        )
        for case in cases:
            data = bytes.fromhex(case["hex"])
            layout = case["layout"]
            entries = decode_page(data, layout, 1024, 2048)
            self.assertEqual(len(entries), 0 if case["name"].startswith("empty") else 1)
            if entries and layout == 2:
                self.assertEqual(
                    entries[0]["box"]["minX"], math.nextafter(-10.25, -math.inf)
                )
                self.assertEqual(
                    entries[0]["box"]["maxY"], math.nextafter(20.5, math.inf)
                )
            for length in range(len(data)):
                with self.assertRaises(IbxError):
                    decode_page(data[:length], layout, 1024, 2048)
            for at in (0, 1, 2, 4):
                bad = bytearray(data)
                bad[at] = 255
                with self.assertRaises(IbxError):
                    decode_page(bad, layout, 1024, 2048)
            if entries:
                bad = bytearray(data)
                struct.pack_into(">d", bad, 8, math.nan)
                with self.assertRaises(IbxError):
                    decode_page(bad, layout, 1024, 2048)


if __name__ == "__main__":
    unittest.main()

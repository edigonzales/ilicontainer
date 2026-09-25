"""Compare reader versions in isolated processes; caller supplies the package directory."""

import sys, pathlib, threading, http.server, json, time, hashlib, re

sys.path.insert(0, sys.argv[1])
from ibx_browser.ibx.container import LocalSource, Metrics
from ibx_browser.ibx.reader import Container
from ibx_browser.ibx.navigation import Navigation
from ibx_browser.ibx.remote import HttpRangeSource
from ibx_browser.ibx import zstd, spatial
import glob

try:
    zstd.load()
except zstd.ZstdUnavailable:
    zstd.load(
        glob.glob("/Applications/QGIS*.app/Contents/Frameworks") + ["/opt/homebrew/lib"]
    )
file = pathlib.Path(sys.argv[2])
cls, attr, tid = sys.argv[3:6]
x, y = map(float, sys.argv[6:8])


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_HEAD(self):
        self.serve(False)

    def do_GET(self):
        self.serve(True)

    def serve(self, body):
        size = file.stat().st_size
        v = self.headers.get("Range")
        lo, hi = (
            map(int, re.fullmatch(r"bytes=(\d+)-(\d+)", v).groups())
            if v
            else (0, size - 1)
        )
        self.send_response(206 if v else 200)
        self.send_header("Content-Length", str(hi - lo + 1))
        self.send_header("ETag", '"fixed"')
        self.send_header("Accept-Ranges", "bytes")
        if v:
            self.send_header("Content-Range", f"bytes {lo}-{hi}/{size}")
        self.end_headers()
        if body:
            with file.open("rb") as f:
                f.seek(lo)
                self.wfile.write(f.read(hi - lo + 1))


server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()


def query(nav, radius):
    if radius < 0:
        obj = nav.resolve(tid)
        return (
            ("1:" + hashlib.sha256((obj["tid"] + "\n").encode()).hexdigest())
            if obj
            else "0"
        )
    locations = spatial.candidates(
        nav.container,
        cls,
        attr,
        dict(minX=x - radius, minY=y - radius, maxX=x + radius, maxY=y + radius),
    )
    h = hashlib.sha256()
    n = 0
    for loc in locations:
        h.update(f"{loc.basket_position}:{loc.chunk_id}:{loc.ordinal}\n".encode())
        n += 1

    return str(n) + ":" + h.hexdigest()


for transport in ["local", "http"]:
    for radius in ([-1] if attr == "-" else [-1, 20, 1000, 10000]):
        for cache in ["cold", "warm"]:
            m = Metrics()
            source = (
                LocalSource(str(file), m)
                if transport == "local"
                else HttpRangeSource(
                    f"http://127.0.0.1:{server.server_port}/data.ibx", {}, m
                )
            )
            c = Container(source, m)
            nav = Navigation(c)
            try:
                for _ in range(3):
                    query(nav, radius)
                runs = []
                expected = None
                for _ in range(10):
                    if cache == "cold":
                        c.store.clear()
                    c._chunks.clear()
                    c._positions.clear()
                    before = m.snapshot()
                    start = time.perf_counter()
                    result = query(nav, radius)
                    ms = (time.perf_counter() - start) * 1000
                    after = m.snapshot()
                    assert expected is None or expected == result
                    expected = result
                    runs.append(
                        dict(
                            ms=ms,
                            metrics={k: after[k] - before.get(k, 0) for k in after},
                        )
                    )
                print(
                    json.dumps(
                        dict(
                            reader="python",
                            scope="object" if radius < 0 else "spatial-candidates",
                            file=file.name,
                            transport=transport,
                            cache=cache,
                            radius=radius,
                            result=expected,
                            runs=runs,
                        )
                    ),
                    flush=True,
                )
            finally:
                c.close()
server.shutdown()

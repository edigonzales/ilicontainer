#!/usr/bin/env python3
"""Reproducible 100k-object read/selectivity check with the Python reader.

The container is created with the Java CLI once (the writer stays in Java);
every read measurement below uses the pure-Python reader that ships inside the
QGIS plugin.  Optional ``--size 1000000``.
"""

import argparse
import glob
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "qgis"))

from ibx_browser.ibx import zstd  # noqa: E402
from ibx_browser.ibx.container import LocalSource, Metrics  # noqa: E402
from ibx_browser.ibx.navigation import Navigation  # noqa: E402
from ibx_browser.ibx.reader import Container  # noqa: E402

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--size", type=int, default=100000)
p.add_argument("--skip-create", action="store_true")
a = p.parse_args()
work = root / "build/large"
work.mkdir(parents=True, exist_ok=True)
data = work / "large.ibx"


def bind_zstd():
    try:
        zstd.load()
        return
    except zstd.ZstdUnavailable:
        pass
    candidates = []
    app = os.environ.get("QGIS_APP")
    if app:
        candidates.append(f"{app}/Contents/Frameworks")
    candidates.extend(glob.glob("/Applications/QGIS*.app/Contents/Frameworks"))
    candidates.extend(["/opt/homebrew/lib", "/usr/local/lib", "/usr/lib/x86_64-linux-gnu"])
    zstd.load(candidates)


if not a.skip_create or not data.exists():
    spec = importlib.util.spec_from_file_location("generate", root / "demo/generate.py")
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    gen.write(work / "large.xtf", a.size)
    args = [
        str(root / "build/install/ibx/bin/ibx"),
        "create",
        str(work / "large.xtf"),
        str(data),
        "--overwrite",
        "--model-file",
        str(root / "demo/Quartier.ili"),
        "--geometry-encoding",
        "wkb",
        "--spatial",
        "Quartier.Unterhalt.Gebaeude:Grundriss",
        "--crs",
        "EPSG:2056",
    ]
    for key in [
        "Gebaeude.Grundriss",
        "Gebaeude.Beschriftung",
        "Anlage.Position",
        "Spielplatz.Position",
        "Technik.Position",
        "Kontrolle.Standort",
    ]:
        args += ["--geometry-crs", f"Quartier.Unterhalt.{key}=EPSG:2056"]
    subprocess.run(args, cwd=root, check=True)

bind_zstd()
digest = hashlib.sha256(data.read_bytes()).hexdigest()
metrics = Metrics()


def snapshot():
    return metrics.snapshot()


def delta(before, after):
    return {key: after.get(key, 0) - before.get(key, 0) for key in after}


started = time.perf_counter()
container = Container(LocalSource(str(data), metrics), metrics)
navigation = Navigation(container)
catalog = navigation.catalog()
opening = snapshot()
open_seconds = time.perf_counter() - started
assert (
    sum(row["count"] for row in catalog["items"] if row["className"].endswith(".Gebaeude"))
    == a.size
)
assert opening["chunksRead"] == 0

before = snapshot()
obj = navigation.resolve("auftrag0")
single = delta(before, snapshot())
assert single["chunksRead"] == 1

before = snapshot()
page = navigation.related(obj["fid"], limit=50)
first_page = delta(before, snapshot())
seen = set()
while True:
    for row in page["items"]:
        key = (row["sourceFid"], row["path"])
        assert key not in seen
        seen.add(key)
    if page["next"] is None:
        break
    page = navigation.related(obj["fid"], page["next"], limit=50)
assert len(seen) == min(a.size, 10000) + 4 if a.size > 1000 else len(seen) > 0

started = time.perf_counter()
count = 0
for _ in navigation.query("Quartier.Unterhalt.Gebaeude", "Grundriss"):
    count += 1
scan_seconds = time.perf_counter() - started
assert count == a.size

started = time.perf_counter()
candidates = list(
    navigation.query(
        "Quartier.Unterhalt.Gebaeude",
        "Grundriss",
        dict(minX=2600001, minY=1200001, maxX=2600010, maxY=1200010),
    )
)
bbox_seconds = time.perf_counter() - started
assert len(candidates) == 1

assert hashlib.sha256(data.read_bytes()).hexdigest() == digest
total = snapshot()
container.close()
report = dict(
    size=a.size,
    bytes=data.stat().st_size,
    sha256=digest,
    runtime="python-reader",
    openSeconds=round(open_seconds, 4),
    opening=opening,
    singleObject=single,
    firstRelationshipPage=first_page,
    relationships=len(seen),
    classScan=dict(
        objects=count, seconds=round(scan_seconds, 4), perSecond=round(count / scan_seconds)
    ),
    bbox=dict(items=len(candidates), seconds=round(bbox_seconds, 4)),
    total=total,
)
(work / "report.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))

#!/usr/bin/env python3
"""Reproducible 100k-object read/selectivity check; optional --size 1000000."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import urllib.request

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--size", type=int, default=100000)
a = p.parse_args()
work = root / "build/large"
work.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location("generate", root / "demo/generate.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)
gen.write(work / "large.xtf", a.size)
args = [
    str(root / "build/install/ibx/bin/ibx"),
    "create",
    str(work / "large.xtf"),
    str(work / "large.ibx"),
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
java = str(Path(os.environ["JAVA_HOME"]) / "bin/java")
process = subprocess.Popen(
    [
        java,
        "-Xmx128m",
        "-cp",
        str(root / "build/install/ibx/lib/*"),
        "ch.interlis.ibx.bridge.BridgeMain",
    ],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True,
)
hello = json.loads(process.stdout.readline())


def call(op, **kw):
    req = urllib.request.Request(
        f'http://127.0.0.1:{hello["port"]}/v1',
        data=json.dumps(dict(op=op, **kw)).encode(),
        headers={"X-IBX-Token": hello["token"]},
    )
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(
        req, timeout=60
    ) as response:
        return json.load(response)


try:
    digest = hashlib.sha256((work / "large.ibx").read_bytes()).hexdigest()
    session = call("open", source=str(work / "large.ibx"))["session"]
    catalog = call("catalog", session=session)["items"]
    assert (
        sum(r["count"] for r in catalog if r["className"].endswith(".Gebaeude"))
        == a.size
    )
    opened = call("metrics", session=session)
    assert opened["chunksRead"] == 0
    obj = call("object", session=session, tid="auftrag0")
    single = call("metrics", session=session)
    assert single["chunksRead"] == 1
    after = None
    seen = set()
    first_page = None
    while True:
        page = call("related", session=session, fid=obj["fid"], after=after, limit=50)
        for row in page["items"]:
            key = (row["sourceFid"], row["path"])
            assert key not in seen
            seen.add(key)
        if first_page is None:
            first_page = call("metrics", session=session)
        after = page["next"]
        if after is None:
            break
    assert len(seen) == min(a.size, 10000) + 4 if a.size > 1000 else len(seen) > 0
    result = call(
        "query",
        session=session,
        className="Quartier.Unterhalt.Gebaeude",
        geometry="Grundriss",
        bbox=dict(minX=2600001, minY=1200001, maxX=2600010, maxY=1200010),
    )
    assert len(result["items"]) == 1 and result["cursor"] is None
    assert hashlib.sha256((work / "large.ibx").read_bytes()).hexdigest() == digest
    report = dict(
        size=a.size,
        bytes=(work / "large.ibx").stat().st_size,
        sha256=digest,
        opening=opened,
        singleObject=single,
        firstRelationshipPage=first_page,
        relationships=len(seen),
        total=call("metrics", session=session),
    )
    (work / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
finally:
    process.stdin.close()
    process.wait(timeout=10)

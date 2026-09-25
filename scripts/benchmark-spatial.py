"""Run paired Swisstopo benchmarks after saving baseline-format4 readers.

Use IBX_BENCH_READERS=java or python, IBX_BENCH_VERSIONS=format4 or format5,
and optional IBX_BENCH_DATASET substring to repeat a subset. Outputs are local.
"""

import pathlib, subprocess, json, os

root = pathlib.Path(__file__).resolve().parents[1]
w = root / "benchmark-data/swisstopo-wkb"
java = pathlib.Path(os.environ.get("JAVA_HOME", str(pathlib.Path.home() / ".sdkman/candidates/java/21.0.10-tem"))) / "bin/java"
cases = [
    (
        "amtliches-gebaeudeadressverzeichnis_ch_2056",
        "OfficialIndexOfAddresses_V2_2.OfficialIndexOfAddresses.Address",
        "PNT_SHAPE",
        "102435015",
        2612677.919,
        1266615.227,
    ),
    (
        "amtliches-strassenverzeichnis_ch_2056",
        "OfficialIndexOfStreets_V2_2.OfficialIndexOfStreets.Localisation",
        "-",
        "10241849",
        2612677.919,
        1266615.227,
    ),
    (
        "ortschaftenverzeichnis_plz_2056",
        "OfficialIndexOfLocalities_V1_0.OfficialIndexOfLocalities.Locality",
        "Geometry",
        "-",
        2612677.919,
        1266615.227,
    ),
]
# Read one real locality OID directly from the original XML, without depending on either reader.
import xml.etree.ElementTree as ET

for event, e in ET.iterparse(
    w
    / "sources/ortschaftenverzeichnis_plz_2056/AMTOVZ_INTERLIS24/OfficialIndexOfLocalities_V1_0.xtf",
    events=["start"],
):
    if e.tag.endswith("}Locality"):
        tid = next(v for k, v in e.attrib.items() if k.endswith("}tid"))
        cases[2] = (*cases[2][:3], tid, *cases[2][4:])
        break
for reader in os.environ.get("IBX_BENCH_READERS", "java,python").split(","):
    for name, cls, attr, tid, x, y in cases:
        if os.environ.get("IBX_BENCH_DATASET", "") not in name:
            continue
        for version in os.environ.get("IBX_BENCH_VERSIONS", "format4,format5").split(
            ","
        ):
            file = (w if version == "format4" else w / "format5") / (name + ".ibx")
            out = w / "format5" / f"benchmark-{reader}-{version}-{name}.jsonl"
            args = [str(file), cls, attr, tid, str(x), str(y)]
            if reader == "java":
                libs = (
                    w / "baseline-format4/cli/lib"
                    if version == "format4"
                    else root / "build/install/ibx/lib"
                )
                cmd = [
                    str(java),
                    "-Xmx2g",
                    "-cp",
                    f"{libs}/*:{w}/baseline-format4",
                    "SpatialBenchmark",
                    *args,
                ]
            else:
                package = (
                    w / "baseline-format4" if version == "format4" else root / "qgis"
                )
                cmd = [
                    "python3",
                    str(root / "scripts/benchmark-spatial-python.py"),
                    str(package),
                    *args,
                ]
            print("START", reader, version, name, flush=True)
            with out.open("w") as f:
                subprocess.run(cmd, stdout=f, check=True, cwd=root)
            print("DONE", reader, version, name, flush=True)

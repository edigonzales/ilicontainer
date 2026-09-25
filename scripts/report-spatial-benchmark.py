"""Summarize paired measurements; never silently accept mismatched results."""

import pathlib, json, statistics, sys

w = pathlib.Path(sys.argv[1])
pairs = {}
for p in sorted(w.glob("benchmark-*.jsonl")):
    version = "format4" if "-format4-" in p.name else "format5"
    for line in p.read_text().splitlines():
        r = json.loads(line)
        key = (r["reader"], r["file"], r["transport"], r["cache"], r["radius"])
        pairs.setdefault(key, {})[version] = r
report = []
for key, p in pairs.items():
    if len(p) != 2:
        continue
    a, b = p["format4"], p["format5"]
    assert a["result"] == b["result"], (key, a["result"], b["result"])
    row = dict(zip(("reader", "file", "transport", "cache", "radius"), key))
    row["result"] = a["result"]
    for v, r in p.items():
        times = sorted(x["ms"] for x in r["runs"])
        assert len(times) >= 10
        row[v] = dict(
            medianMs=statistics.median(times),
            p95Ms=times[min(len(times) - 1, int(len(times) * 0.95))],
            metrics={
                k: statistics.median(x["metrics"][k] for x in r["runs"])
                for k in r["runs"][0]["metrics"]
            },
        )
    row["ratio"] = row["format5"]["medianMs"] / row["format4"]["medianMs"]
    report.append(row)
(w / "benchmark-summary.json").write_text(json.dumps(report, indent=2) + "\n")
print("Paired scenarios:", len(report))
for r in report:
    if r["ratio"] > 1.1:
        print(
            "RECHECK",
            r["reader"],
            r["file"],
            r["transport"],
            r["cache"],
            r["radius"],
            round(r["ratio"], 2),
            round(r["format4"]["medianMs"], 2),
            round(r["format5"]["medianMs"], 2),
        )

#!/usr/bin/env python3
"""Copy completed geometry matrices and write a compact, reproducible comparison."""
import json
import pathlib
import shutil
import statistics

root = pathlib.Path(__file__).resolve().parents[1]
out = root / "docs/benchmarks/wkb"
out.mkdir(parents=True, exist_ok=True)
lines = ["# WKB-Benchmarks", "", "Drei bestehende Datensätze, je IOM/WKB × vier Chunk-Zielgrössen (64, 256, 1024, 4096 KiB),",
         "skalare Kodierung lexical, Zstandard-Level 3, Java 21 und 384 MiB maximaler Heap.",
         "Jede erfolgreich erzeugte Variante wurde unabhängig als XTF gegen das Original geprüft.", "",
         "## Standardgrösse 256 KiB", "",
         "Lesezeiten sind Mediane aus drei lokalen Klassenabfragen mit kaltem Anwendungscache.",
         "IOX und GIS beziehen sich hier auf dieselbe konkrete Klasse; fehlende Geometrien zählen mit.", "",
         "| Datensatz | IOM Bytes | WKB Bytes | Änderung | IOM IOX ms | WKB IOX ms | WKB GIS ms |",
         "|---|---:|---:|---:|---:|---:|---:|"]
for name in ("dmav", "fixpoints", "localities"):
    source = root / ("benchmark-data/wkb-final-" + name)
    data = json.loads((source / "results.json").read_text())
    rows = data["rows"]
    creates = {r["variant"]: r for r in rows if r["operation"] in ("create", "create-rejected")}
    assert len(creates) == 8, f"Incomplete matrix: {name}"
    for r in creates.values():
        if r["operation"] == "create":
            assert r.get("semanticRoundtripRecords", 0) > 0
    for ext in ("json", "md"):
        shutil.copyfile(source / ("results." + ext), out / (name + "." + ext))
    def creation(encoding):
        return creates[encoding + "-lexical-262144"]
    def median(encoding, operation):
        return statistics.median(r["wallMillis"] for r in rows
                                 if r["variant"] == encoding + "-lexical-262144"
                                 and r["operation"] == operation and r.get("cache") == "cold"
                                 and r.get("remote") is False)
    a, b = creation("iom"), creation("wkb")
    if b["operation"] == "create-rejected":
        lines.append(f"| {name} | {a['fileBytes']} | abgelehnt | {b['diagnosis']} | — | — | — |")
    else:
        delta = (b['fileBytes'] / a['fileBytes'] - 1) * 100
        lines.append(f"| {name} | {a['fileBytes']} | {b['fileBytes']} | {delta:+.1f}% | "
                     f"{median('iom','class'):.3f} | {median('wkb','class'):.3f} | {median('wkb','gis-scan'):.3f} |")
lines += ["", "## Rohwerte und Grenzen", "",
          "- [DMAV-Toleranzstufen](dmav.md), [JSON](dmav.json)",
          "- [Fixpunkte](fixpoints.md), [JSON](fixpoints.json)",
          "- [Ortschaften](localities.md), [JSON](localities.json)", "",
          "Die JSON-Berichte enthalten Eingabe-SHA-256, Modelle und Quelldigests, Laufzeitumgebung,",
          "Erstellungszeiten, temporären Speicher, Heap-Spitzen, Index-/Chunkbytes und Anfragen.",
          "`geometryConversionAndProofMillis` misst gemeinsam die WKB-Konversion und deren",
          "Reversibilitätsprüfung während der Erstellung. Es ist kein isolierter Codec-Durchsatz.", "",
          "WKB-Grössen enthalten zusätzliche Modelldeskriptoren und den FID-Index.",
          "Der Fingerabdruck der gemessenen Bibliothek steht in [build.json](build.json).",
          "Nach der Messung wurde zusätzlich die Ablehnung unaufgelöster CRS-Zuordnungen",
          "nach einem vorhergehenden Basket abgesichert. Die expliziten CRS-Zuordnungen dieser",
          "Datensätze und das Dateiformat sind davon unverändert.",
          "Kalt/warm betrifft den Anwendungscache; Betriebssystemcaches wurden nicht geleert.",
          "HTTP-Messungen verwenden Loopback. Der Host war nicht exklusiv reserviert;",
          "insbesondere die kleinen Datensätze erlauben keine belastbare allgemeine Geschwindigkeitsaussage.",
          "Die gespeicherten Bogenstützpunkte werden nicht linearisiert. GIS liest WKB direkt,",
          "während der IOX-Pfad daraus vollständige IOM-Geometrien rekonstruiert.", "",
          "## Reproduktion", "",
          "Die Befehle unter [BENCHMARKS.md](../../BENCHMARKS.md) verwenden für diese Auswertung",
          "`--geometry-matrix` statt `--matrix`, weiterhin `--repeats 3`, und die Ausgabeverzeichnisse",
          "`benchmark-data/wkb-final-dmav`, `benchmark-data/wkb-final-fixpoints` sowie",
          "`benchmark-data/wkb-final-localities`. Danach:", "",
          "```sh", "python3 scripts/summarize-wkb-benchmarks.py", "```", ""]
(out / "README.md").write_text("\n".join(lines))

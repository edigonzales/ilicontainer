# WKB-Benchmarks

Drei bestehende Datensätze, je IOM/WKB × vier Chunk-Zielgrössen (64, 256, 1024, 4096 KiB),
skalare Kodierung lexical, Zstandard-Level 3, Java 21 und 384 MiB maximaler Heap.
Jede erfolgreich erzeugte Variante wurde unabhängig als XTF gegen das Original geprüft.

## Standardgrösse 256 KiB

Lesezeiten sind Mediane aus drei lokalen Klassenabfragen mit kaltem Anwendungscache.
IOX und GIS beziehen sich hier auf dieselbe konkrete Klasse; fehlende Geometrien zählen mit.

| Datensatz | IOM Bytes | WKB Bytes | Änderung | IOM IOX ms | WKB IOX ms | WKB GIS ms |
|---|---:|---:|---:|---:|---:|---:|
| dmav | 41601 | 49949 | +20.1% | 0.532 | 0.307 | 0.115 |
| fixpoints | 153959 | 222268 | +44.4% | 1.396 | 1.276 | 2.723 |
| localities | 50490731 | 44923687 | -11.0% | 1180.882 | 459.485 | 60.181 |

## Rohwerte und Grenzen

- [DMAV-Toleranzstufen](dmav.md), [JSON](dmav.json)
- [Fixpunkte](fixpoints.md), [JSON](fixpoints.json)
- [Ortschaften](localities.md), [JSON](localities.json)

Die JSON-Berichte enthalten Eingabe-SHA-256, Modelle und Quelldigests, Laufzeitumgebung,
Erstellungszeiten, temporären Speicher, Heap-Spitzen, Index-/Chunkbytes und Anfragen.
`geometryConversionAndProofMillis` misst gemeinsam die WKB-Konversion und deren
Reversibilitätsprüfung während der Erstellung. Es ist kein isolierter Codec-Durchsatz.

WKB-Grössen enthalten zusätzliche Modelldeskriptoren und den FID-Index.
Der Fingerabdruck der gemessenen Bibliothek steht in [build.json](build.json).
Nach der Messung wurde zusätzlich die Ablehnung unaufgelöster CRS-Zuordnungen
nach einem vorhergehenden Basket abgesichert. Die expliziten CRS-Zuordnungen dieser
Datensätze und das Dateiformat sind davon unverändert.
Kalt/warm betrifft den Anwendungscache; Betriebssystemcaches wurden nicht geleert.
HTTP-Messungen verwenden Loopback. Der Host war nicht exklusiv reserviert;
insbesondere die kleinen Datensätze erlauben keine belastbare allgemeine Geschwindigkeitsaussage.
Die gespeicherten Bogenstützpunkte werden nicht linearisiert. GIS liest WKB direkt,
während der IOX-Pfad daraus vollständige IOM-Geometrien rekonstruiert.

## Reproduktion

Die Befehle unter [BENCHMARKS.md](../../BENCHMARKS.md) verwenden für diese Auswertung
`--geometry-matrix` statt `--matrix`, weiterhin `--repeats 3`, und die Ausgabeverzeichnisse
`benchmark-data/wkb-final-dmav`, `benchmark-data/wkb-final-fixpoints` sowie
`benchmark-data/wkb-final-localities`. Danach:

```sh
python3 scripts/summarize-wkb-benchmarks.py
```

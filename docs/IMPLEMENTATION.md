# Implementierung und Abnahme

## Zuständigkeiten

Ein Gradle-Projekt mit `java-library` und `application`, Java 21 für Build/Laufzeit und `--release 8` für sämtliche Java-Kompilierungen. Die Packages trennen API, IOX-Anbindung, CBOR, Container, Verzeichnisse, HTTP, räumliche Suche, CLI und Benchmarkwerkzeuge. Es gibt keine Java-Objektserialisierung von ili2c-Klassen.

| Meilenstein | Implementierung | Nachweis |
|---|---|---|
| M1 | `ModelBridge`, `LosslessXtfWriter`, `ObjectCodec` | Roundtrip, präzise Zahlen, LIST-Strukturen, Referenzen, XML-/Binär-Blackboxes, OID-lose Assoziation, zusätzliche IOX-Modellvalidierung der gültigen Fixture |
| M2 | `ContainerWriter`, `SequentialReader`, `Frames`, `Chunk` | Leerer Transfer/Basket, ungeteilte übergrosse Objekte, Lesen ohne Directory/Footer, 100’000 Objekte mit 64 MiB Writer- und 32 MiB Reader-Heap |
| M3 | `BTree`, `ExternalSort`, `IliContainer`, `Fragment` | 10’000 Verzeichniseinträge, mehrstufiges externes Sortieren, Überlaufeinträge, unabhängige Fragmentansichten, maximal ein gelesener Daten-Chunk beim Objektzugriff |
| M4 | `HttpRangeSource`, `FrameStore` | Kontrollierter HTTP-Server: ETag-Wechsel, fehlende Ranges, expliziter Gesamtdownload, fehlender ETag, falscher Content-Range; ein Standwechsel während des Exports ersetzt kein bestehendes Ziel |
| M5 | `SpatialIndex`, `GeometryBounds` | Mehrseitiger Index mit 4’096 Punkten, unabhängige Gitterreferenz, analytische Bogenreferenz mit festem Zufallsseed, Randberührung, Höhen, fehlende/fehlerhafte Geometrien |
| M6 | `PrepareData`, `BenchmarkMain`, `RoundtripVerifier` | Reale DMAV- und Ortschaften-Matrizen, unabhängiger XTF-Vergleich, Grössen/Scans/selektive und räumliche Zugriffe, JSON und Markdown |

Die messbaren Ergebnisse und Grenzen stehen in [BENCHMARKS.md](BENCHMARKS.md). Die Formatentscheidung steht in [FORMAT.md](FORMAT.md). CI für Linux und macOS ist konfiguriert; ein lokaler erfolgreicher Lauf ersetzt keine Ausführung beider CI-Jobs.

## Integritäts- und Ressourcenvertrag

- Erstellung und dateibasierte CLI-Exporte veröffentlichen ihr Ziel erst nach erfolgreichem Abschluss. Überschreiben erfordert `--overwrite`.
- Nicht-FULL, falsche Version, fehlende/duplizierte Identitäten, defekte Prüfsummen, abgeschnittene Dateien und zyklische Indexverweise werden abgewiesen. Eine vollständige Constraint-/Referenzvalidierung ist optional ausserhalb dieser Erstellung auszuführen.
- Sortier-Runs werden schon während der Erstellung stufenweise zusammengeführt. Jede der 16 Stufen enthält höchstens 31 abgeschlossene Runs; 32 Inputs werden jeweils zusammengeführt. 32^16 übersteigt die adressierbare 64-Bit-Dateigrösse. Auch die Verwaltung der Dateinamen bleibt damit beschränkt. Verzeichnisse werden ohne vollständige Pfadliste aufgeräumt.
- Das aktive Objekt und der aktive Chunk dürfen die Zielgrösse überschreiten; diese Zielgrösse ist kein allgemeines Heap-Limit. Der feste Heap-Test verwendet ein konstantes Modell und kleine Objekte.
- Fragmente und ihre Streams sind zu schliessen. Ein vorzeitig abgebrochener Stream kann noch Ressourcen halten, bis Stream oder Fragment geschlossen werden.
- Bei einem Remote-Fehler gibt es keinen erfolgreichen gemischten Transfer. Eine stdout-Ausgabe kann vor dem Fehler bereits unvollständiges XML enthalten; der Exit-Code bleibt ungleich null. Dateiausgaben bleiben unveröffentlicht.
- Ein fehlgeschlagener optionaler räumlicher Index erhält den bereits erstellten Core. Der CLI-Aufruf meldet trotzdem einen Fehler.

## Bewusste Prototypgrenzen

Keine exakte Intersects-Prüfung, CRS-Transformation, automatische Referenznachladung, vollständige obligatorische Modellvalidierung, Schreibkonkurrenz oder dauerhafte Binärkompatibilitätszusage. Einzelne Frames sind durch Java-Arrays auf weniger als 2 GiB begrenzt; die Datei selbst verwendet 64-Bit-Offsets. Explizite Radiusbögen und numerisch mehrdeutige Bögen werden für die Indexierung mit Diagnose abgewiesen und bleiben im Core erhalten.

Die Modellabbildung ist für Offline-Export vollständig; eingebettete ILI-Quellen sind zusätzlich optional. Der Offline-Prozesstest verwendet sowohl einen leeren als auch einen gefüllten Transfer, ein neues Arbeitsverzeichnis und nicht erreichbare HTTP-/HTTPS-Proxys.

## Optionale WKB-Erweiterung

Das Profil `wkb-iso-v1` bietet ISO-WKB mit echten Kreisbögen, einen
seitenweisen FID-Index und die direkte `GisLayer`-/`GisFeature`-API.
IOM bleibt Standard. Beide Kodierungen verwenden jetzt ausschliesslich Format 3. Modell- und
Basketmetadaten ermöglichen weiterhin Offline-XTF-Export.

Die Kurvenkodierung adaptiert die Vorarbeit aus dem Hop-Geometrieplugin ohne
Hop-/JTS-Geometrieobjekte und ohne implizite Linearisierung. Die ursprünglichen
Dezimalwerte und Kontrollpunkte werden vor Veröffentlichung durch einen
semantischen Rückvergleich abgesichert. Eine vollständige Constraintvalidierung
ist weiterhin nicht Teil der Erstellung.

Der frühere WKB-Abnahmelauf umfasste 50 erfolgreiche Java-Tests; Format 3 ergänzt gezielte Prüfungen.
Die vorhandenen Semantik-, Container-, Remote- und Spatial-Paging-Tests werden
für beide Profile ausgeführt. Die GIS-API wird zusätzlich gegen unabhängige
Gittererwartungen, FID-Einzelzugriffe, verschachtelte Geometrien und einen
wechselnden HTTP-Dateistand geprüft. Linux-GDAL liest 22 unabhängige XY-/XYZ-
Geometriefixtures und bestätigt deren Typen, Komponenten und ISO-WKB-Bytes.

Bedienung und Profilgrenzen: [WKB.md](WKB.md).
Messergebnisse: [WKB-Matrix](benchmarks/wkb/README.md).
Ein QGIS-/GDAL-Dateitreiber und schreibender GIS-Zugriff sind spätere Erweiterungen.

## Format 3

- 64-Byte-Footer, vollständige FrameRefs, binäre und präfixkomprimierte Verzeichnisse, FID-Bereiche pro Chunk; kein Legacy-Reader.
- STR als Standard, X-Packung als Vergleichsoption; Knotengrenzen anhand kodierter Bytes und externe Sortierung auf jeder Ebene.
- Optionale Hilbert-Reihenfolge je Basket/Klasse, fehlende Geometrien zuletzt, FIDs nach Sortierung.
- Bekannte Frames mit einer Range-Anfrage; räumliches Vorladen im gemeinsamen Cache, weiterhin strikte ETag-/CRC-Prüfung.
- `Format3Test` prüft ein unabhängig spezifiziertes Binärfixture, alte Header, FID-Grenzen, Präzisions-/Bytegrenzen, HTTP-Zugriffszahlen und Mehrseitenabfragen gegen einen unabhängigen Punkt-Scan.
- Der Wachstumstest schreibt jetzt auch mit Hilbert-Sortierung unter 64 MiB Heap und liest unter 32 MiB.
- Die gesicherte Referenzdistribution und die Format-3-Distribution laufen für Vergleichsmessungen in getrennten Prozessen. Ergebnisse tragen den SHA-256 des tatsächlich geladenen Bibliotheks-JARs.

Der lokale Format-3-Abnahmelauf besteht aus 60 erfolgreichen Java-Tests sowie der Linux-GDAL-Gegenprüfung aller 22 WKB-Fixtures. Die Vergleichsmatrix und ihr Abschlussstand stehen im [Format-3-Bericht](benchmarks/format3/README.md).

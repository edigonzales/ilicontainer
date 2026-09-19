# Benchmarks und Reproduktion

Die Messungen dienen der Bewertung des Prototyps. Ein Grössenvorteil gegenüber komprimiertem XTF ist kein Abnahmekriterium. Grosse Quelldateien, Container und temporäre Dateien liegen unter `benchmark-data/` und sind von Git ausgeschlossen.

## Datensätze vorbereiten

Downloads sind ausdrücklich auszulösen; normale Tests benötigen diese Daten nicht.

```sh
./gradlew prepareData -Pdataset=dmav -PdataDir=benchmark-data/dmav
./gradlew prepareData -Pdataset=localities -PdataDir=benchmark-data/localities
./gradlew prepareData -Pdataset=addresses -PdataDir=benchmark-data/addresses
./gradlew prepareData -Pdataset=dmav-pipes -PdataDir=benchmark-data/pipes
./gradlew prepareData -Pdataset=dmav-fixpoints -Pcommunity=2542 -PdataDir=benchmark-data/fixpoints-2542
```

Die Vorbereitung erzeugt `manifest.json` mit URL, Abrufdatum, Archivmitglied, SHA-256, Grösse, deklarierten Modellen, XTF-Version und FULL-Prüfung. Ein vorhandener Download wird wiederverwendet; für einen neuen Datenstand ist ein neues Ausgabeverzeichnis zu verwenden. Relative Solothurner Katalogpfade werden gegen die Katalog-URL aufgelöst.

Am 15. September 2026:

- Toleranzstufen, Gemeinde 2541: 70’626 Bytes XTF 2.4 FULL, fünf Objekte; drei davon in der abgefragten Geometrieklasse.
- Ortschaftenverzeichnis: XTF 2.4 FULL mit Mehrfachflächen, 382’750’705 Bytes (rund 365 MiB) unkomprimiert.
- Gebäudeadressverzeichnis: 3’361’952’905 Bytes XTF 2.3. Der tatsächliche `create`-Aufruf wurde mit einer Versionsdiagnose abgelehnt; keine Konversion und kein Container erstellt.
- Rohrleitungen, Gemeinde 2541: XTF 2.4 FULL mit einem leeren Basket. Erstellung und Export erhalten diesen Basket. Mangels Objekten ist dies ein Semantiktest, kein aussagekräftiger Spatial-Benchmark.
- Fixpunkte Kategorie 3, Gemeinde 2541: im Katalog vorhanden, aber HTTP 500 beim Abruf. Als verfügbare Alternative wurde Gemeinde 2542 heruntergeladen: 1’017’973 Bytes XTF 2.4 FULL, 502 Objekte einschliesslich 391 LFP3-Punkten.

## Messläufe

Java 21, Gradle-Task mit 384 MiB maximalem Java-Heap:

```sh
./gradlew benchmark --args='--input benchmark-data/dmav/source.xtf --output benchmark-data/results-dmav --class DMAV_Toleranzstufen_V1_1.Toleranzstufen.Toleranzstufe --geometry Geometrie --crs EPSG:2056 --model-dir https://models.geo.admin.ch --model-dir https://models.interlis.ch --matrix --repeats 3'

./gradlew benchmark --args='--input benchmark-data/localities/AMTOVZ_INTERLIS24/OfficialIndexOfLocalities_V1_0.xtf --output benchmark-data/results-localities --class OfficialIndexOfLocalities_V1_0.OfficialIndexOfLocalities.Locality --geometry Geometry --crs EPSG:2056 --model-dir https://models.geo.admin.ch --model-dir https://models.interlis.ch --matrix --repeats 3'
```

Die zusätzliche Punktmessung verwendet:

```sh
./gradlew benchmark --args='--input benchmark-data/fixpoints-2542/source.xtf --output benchmark-data/results-fixpoints --class DMAV_FixpunkteAVKategorie3_V1_0.FixpunkteAVKategorie3.LFP3 --geometry Geometrie --crs EPSG:2056 --model-dir https://models.geo.admin.ch --model-dir https://models.interlis.ch --matrix --repeats 3'
```

Jeder vollständige Lauf erzeugt `results.json`, `results.md`, ZIP-/Zstandard-Vergleichsdateien und acht Core-/Spatial-Varianten. Die Matrix verwendet `lexical` und `decimal` mit 64 KiB, 256 KiB, 1 MiB und 4 MiB Chunk-Zielgrösse. Zstandard-Level ist 3. Der ZIP-Vergleich verwendet Java Deflate mit Standardeinstellung und einem XTF-Mitglied.

`--refresh-spatial` erneuert in einem vorhandenen vollständigen Ergebnisverzeichnis ausschliesslich Spatial-Indizes und deren Zugriffsmessungen. Eingabehash und Abfrageparameter müssen übereinstimmen. Die vorhandenen Core-Erstellungs-, Roundtrip- und Scanwerte bleiben erhalten. Das erlaubt eine getrennte Nachmessung der numerisch abgesicherten Bogenumhüllung. Zusätzlich erlaubt `--reuse-identical-access`, vorhandene Zugriffswerte nur bei identischem SHA-256 der neu aufgebauten Spatial-Datei und identischer Wiederholungszahl zu übernehmen. Der erneute Indexaufbau wird immer gemessen; die Wiederverwendung wird pro Variante im JSON ausgewiesen.

## Was gemessen und geprüft wird

- XTF, XTF.zip und XTF.zst: vollständiges Lesen über `Xtf24Reader` mit derselben kompilierten Modellabbildung.
- Core: Erstellung, vollständiger Scan und Export. Original und Export werden unabhängig als XTF gelesen, kanonisiert und extern sortiert verglichen. Attribute werden nach Namen verglichen, Wertefolgen bleiben geordnet; Zahlen werden dezimal normalisiert. Die zulässige Umordnung von Hauptobjekten innerhalb eines Baskets wird berücksichtigt. `semanticRoundtripRecords` zählt Header, Baskets und Objekte.
- Core und Spatial: Objekt-, Basket- und Klassenabfragen lokal und über einen echten Loopback-HTTP-Range-Server.
- Spatial: drei zentrierte Abfragefenster mit 1 %, 10 % und 100 % der linearen Ausdehnung der gewählten Klasse. Gemessen werden Kandidaten, gelesene Chunks, Bytes, Indexbytes und Anfragen. Die Abfragen sind deterministisch; erster TID/BID und Ausdehnung stehen im JSON.
- Drei Wiederholungen je Zugriff und vollständigem Scan. Die Berichte enthalten Rohwerte; Zusammenfassungen verwenden den Median. Erstellung und Indexaufbau werden je Variante einmal gemessen.
- Zeit bis zum ersten Objekt, Gesamtdauer, CPU-Zeit des aufrufenden Threads, Durchsatz und Summe der Heap-Pool-Spitzenwerte.
- Temporärer Speicher der Erstellung wird alle 25 ms abgetastet; `temporaryPeakSampledBytes` ist eine beobachtete Untergrenze des tatsächlichen Maximums. `objectDirectoryEntryBytes` misst die logische Summe der TID-Verzeichniseinträge, einschliesslich Sortierframing, nicht einen separat komprimierten Dateibereich.

## Aussagegrenzen

Der Messhost war nicht exklusiv reserviert; parallele Entwicklungsaktivität kann Laufzeiten beeinflussen. Kalt/warm bezeichnet den 32-MiB-Anwendungscache. Betriebssystemcaches werden nicht geleert. Selektive Zeiten und Bytezähler beginnen nach dem Öffnen von Header, Footer und Modellmetadaten; sie sind keine vollständigen Startkosten einer neuen CLI. CPU-Werte enthalten nicht die CPU-Zeit des Loopback-Serverthreads. Die Summe der Heap-Pool-Spitzen ist kein exakt zeitgleiches Heapmaximum und misst keinen nativen Speicher.

Loopback misst das Range-Protokoll und die tatsächliche Byteauswahl, aber keine Internetlatenz. Für reale Netze sind Requestzahl und Bytevolumen deshalb aussagekräftiger als diese Laufzeiten. Räumliche Kandidaten werden vor Ausgabe extern in Containerreihenfolge sortiert; dies beeinflusst die Zeit bis zum ersten Objekt.

Der kleine DMAV-Transfer eignet sich für Semantik und Metadatenkosten, nicht zur allgemeinen Vorhersage der Kompressionsrate. Seine Chunk-Zielgrössen ergeben dieselben physischen Chunks, weil die Objekte je Klasse schon unterhalb der kleinsten Zielgrösse liegen. Der grosse Flächendatensatz untersucht zusätzlich übergrosse Einzelobjekte und die Kosten mehrerer Kandidaten im selben Chunk.

Ein erster grosser Lauf mit 1 GiB Heap endete mit Exit-Code 137. Er wurde verworfen; die protokollierten Läufe verwenden 384 MiB Heap und explizit geschlossene komprimierte Eingabeströme. Die Ursache des externen Prozessabbruchs wurde nicht eindeutig nachgewiesen.

## Ergebnisse

Die eingecheckten Rohwerte, Eingabemanifeste und die kompakte Auswertung stehen unter [benchmarks](benchmarks/). Kompressions- und Layoutentscheidungen bleiben experimentell. Die vollständigen automatisierten Referenztests stehen ergänzend im Gradle-Testbericht.

## IOM/WKB-Geometriematrix

`--geometry-matrix` ersetzt die Zahlenkodierungsmatrix durch IOM/WKB × 64 KiB,
256 KiB, 1 MiB und 4 MiB. Beide Profile verwenden `lexical` für skalare Werte und
Zstandard-Level 3. Nicht auflösbare CRS werden für diese bekannten LV95-Datensätze
explizit mit dem angegebenen Benchmark-CRS belegt; dies ist keine Transformation.

Die bestehenden Befehle können mit `--geometry-matrix --repeats 3` in separaten
Ausgabeverzeichnissen ausgeführt werden. Zusätzlich werden lokale und entfernte
GIS-Klassenscans sowie kleine Spatial-Kandidatenabfragen gemessen, jeweils kalt und
warm. `geometryConversionAndProofMillis` weist die gemeinsame Konversions- und
Reversibilitätsprüfzeit bei der Erstellung aus. Ein nicht unterstützter Inhalt
erscheint als `create-rejected` mit Diagnose; es erfolgt keine Datenkonversion
in ein anderes Profil und kein stiller Rückfall auf IOM.

[Rohwerte und Vergleich der WKB-Matrix](benchmarks/wkb/README.md).

## Format-3-Optimierungen reproduzieren

[Einordnung und Empfehlungen](benchmarks/format3/ASSESSMENT.md), [vollständige Messwerte](benchmarks/format3/README.md), [Rohwerte](benchmarks/format3/results.json) und [Distributions-Hashes/Parameter](benchmarks/format3/run.json).

Die früheren Ergebnisse oben dokumentieren die damaligen Formate. Neue Container werden aus den XTF-Quellen erstellt; der aktuelle Reader liest keine alten Container.

```sh
./gradlew test installDist
python3 scripts/benchmark-format3.py
python3 scripts/benchmark-format3-controls.py benchmark-data/format3
python3 scripts/report-format3.py benchmark-data/format3 docs/benchmarks/format3
```

Vor dem Umbau wurde die Distribution unter `benchmark-data/format3-reference/distribution` mit Manifest gesichert. Das Skript prüft sämtliche Referenzdateien gegen deren SHA-256. Für eine neue Maschine ist diese gesicherte Distribution bereitzustellen oder aus dem im Manifest genannten Commit getrennt zu bauen; der Hash eines Neubaus ist gesondert festzuhalten. Legacy-Code wird nicht in die aktuelle Bibliothek eingebunden.

Das Skript kopiert auch die aktuelle Distribution in sein Ergebnisverzeichnis. Ein kleiner Worker-JAR enthält ausschliesslich Messcode und den verzögerten Loopback-Server. Derselbe Worker wird mit jeweils einer isolierten Bibliothek gestartet. Jeder Fall schreibt Parameter, Bibliotheks- und Eingabe-Hash, Rohmessungen sowie ein Abschlusskennzeichen. `--dataset` begrenzt die Datensätze, `--only` die Varianten; `--repeats` und `--delays` erlauben ausdrücklich kleinere Probeläufe. Standard sind drei Wiederholungen und lokal/HTTP 0/20/80 ms. Das vollständige Raster ist ein längerer expliziter Benchmark, kein normaler Test.

Die erste Referenz legt TID und 23 Fenster fest: die drei bisherigen zentralen Fenster plus 20 Fenster um tatsächlich vorhandene Geometrien, Seed 20260917. Dieselben Fenster werden für alle Varianten verwendet. FID-Zugriffe zielen auf dasselbe Objekt; bei der IOM-Referenz fehlt die Funktion und wird als nicht verfügbar ausgewiesen. Der synthetische Millionenbestand wird lokal erzeugt und gezielt mit vier Core-Varianten verglichen: Referenz/Format 3 × IOM/WKB bei 256 KiB. Dabei werden Verzeichnisbytes, Erstellung, Roundtrip, Vollscan sowie TID-/FID-Zugriffe lokal und mit denselben HTTP-Latenzen gemessen. Ein Spatial Index wird für diese Verzeichnisbewertung nicht erstellt. Zusammen mit den 48 Varianten der drei realen Datensätze sind dies 52 Messfälle. Alle Worker laufen mit 384 MiB Heap.

`heapPeakPoolSumBytes` ist die Summe der Spitzenwerte der JVM-Heap-Pools während der Operation, keine RSS-Messung. Temporärer Speicher wird beim Erstellen periodisch abgetastet. HTTP-Latenz wird pro Anfrage im lokalen Testserver hinzugefügt. Netzwerktransfer ausserhalb der Loopback-Verbindung und Betriebssystemcache-Effekte werden damit nicht simuliert.

Rohdaten unterscheiden `logicalReads`/`logicalBytes` (Frameanforderungen einschliesslich Cache), `requests`/`bytesRead` (RangeSource; bei HTTP tatsächliche Anfragen/Bytes), `prefetchedBytes` (vorab geladene Framebytes), `additionalRangeBytes` (Zwischenräume), Index-/Metadaten-/Chunkbytes und Cachebelegung. Öffnen wird separat aufgezeichnet. Header und Footer sind in `bytesRead` enthalten; die Kategorien für Metadaten, Index und Chunks zählen dagegen Framebytes. `prefetchedBytes` zählt vorab geladene benötigte Frames, `additionalRangeBytes` nur zusätzlich übertragene Zwischenräume. Alte Referenzmetriken haben naturgemäss nicht alle neuen Felder. `info --storage` weist die physischen Verzeichnisanteile aus.

Die veröffentlichte Format-3-Matrix wurde lokal auf Apple M1 mit 16 GiB RAM, macOS 15.7.9 und Java 21.0.7 ausgeführt. Der GDAL-Test läuft separat in einem Linux-Container mit GDAL 3.11.4. Die Latenzmessungen verwenden weiterhin den lokalen HTTP-Server; sie sind keine Messung eines öffentlichen Objektspeichers.

Nach der Abfragematrix ergänzt `benchmark-format3-controls.py` zwei weitere Erstellungs-, Indexaufbau- und Exportmessungen je Variante. Zusammen mit der ersten Beobachtung sind dies drei Wiederholungen; dieselben isolierten Bibliotheken und Parameter werden verwendet. Die zusätzlichen Container werden danach gelöscht, ihre Rohwerte bleiben erhalten. Der semantische Roundtrip wird im Hauptlauf geprüft; die zusätzlichen Zeitmessungen wiederholen diese Prüfung nicht. Der Bericht prüft unveränderte Eingabe-/Bibliotheks-Digests und Dateigrössen und markiert die Gegenkontrollen bis zum vollständigen Abschluss separat. `--report docs/benchmarks/format3` aktualisiert den Bericht nach jedem Fall.

`run.json` hält die Worker-Hashes für Abfragen, synthetische Core-Vergleiche und zusätzliche Gegenkontrollen getrennt fest. Innerhalb jeder Messart verwendet der Vergleich denselben Worker für Referenz und Format 3. Der gespeicherte `productionProof` weist zusätzlich nach, dass die 87 Produktionsklassen der eingefrorenen Format-3-Bibliothek und des aktuellen Builds bytegleich sind; Unterschiede betreffen ausschliesslich Messcode.

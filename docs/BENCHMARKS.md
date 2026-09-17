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

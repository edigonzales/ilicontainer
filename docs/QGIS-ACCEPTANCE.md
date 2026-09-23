# Abnahme des IBX-Prototyps

Stand: 23. September 2026. Lokal geprüft auf macOS mit QGIS 4.2.2, dessen
Python 3.12 und Qt 6.11.1. Das Plugin selbst benötigt keine Java-Laufzeit;
Java 21 wird nur noch für die Kommandozeile (Erstellen und Export) sowie für
die Java-Tests verwendet. Eine plattformübergreifende CI-Aufgabe prüft den
Python-Leser unter Linux, macOS und Windows ohne QGIS und ohne Java.

## Ausgeführte Prüfungen

| Prüfung | Ergebnis |
|---|---|
| `./gradlew test build installDist` | 67 Java-Tests, keine Fehler oder übersprungenen Tests |
| `test_reader.py` mit beliebigem Python 3.9+ | 29 Tests: CBOR, Schlüssel, Frames/Footer, B+-Baum, Katalog, Objekte, Beziehungen, räumliche Kandidaten, HTTP-Range mit ETag, `deflate`/`none`-Fixtures |
| `test_provider.py` mit QGIS-Python | 8 Tests: Features, Filter, Projektion, CRS, Rendering, parallele Iteratoren, Abbruch, Dateistand und Projekt-Neuladen |
| `test_ui.py` mit QGIS-Python | 5 Tests: echter Qt-Kartenklick, Layerauswahl, Inline-Lesen, Diagnoseverlauf, Karte und Verlauf |
| `test_presentation.py` | 10 Tests: binäre und dreiseitige Assoziationen, Gegenrollen, Strukturen, Mehrfachverweise und exakte Werte |
| `test_object_tree.py` mit QGIS-Python | 9 Tests: Inline-Laden, Tastatur, Zyklen, Pagination, Quellentrennung, Abbruch, verspätete Antworten und Farbschemata |
| `test_https.py` mit QGIS-Python | 1 Test: Python-Provider → echter HTTPS-Range-Server mit testlokalem Zertifikat |
| Java-HTTPS-Test | Testlokales Vertrauen; Zertifikatsfehler, Redirects, Downgrade, ETag-Wechsel, fehlerhafte Ranges, fehlende Ranges und Timeout |
| `verify-wkb-gdal.py` | 22 WKB-Fälle, einschliesslich Kurven und XYZ, mit lokalem GDAL 3.13.3 |
| INTERLIS-Demo | Modellvalidierung und unabhängiger XTF-Roundtrip; Strukturen und OID-lose Assoziationen |
| Paketprüfung | ZIP separat entpackt; 86'127 Bytes ohne JARs oder Hilfsprozess; enthaltene Demos mit 24 bzw. 2 Leitobjekten gelesen |

Die 62 Python-Tests laufen ohne JVM. `relation_fixtures.py` enthält zusätzliche
typisierte Protokollfixtures; diese sind bewusst keine zusätzlichen validierten
INTERLIS-Transferdateien. Der Bedienablauf prüft einen einzelnen Zielzugriff beim
Aufklappen, keinen Zugriff beim Wiederaufklappen und keine automatische
Referenznachladung. Paketprüfung: `python3 scripts/verify-qgis-package.py`.

Die QGIS-Tests verwenden echte QGIS-/Qt-Klassen und gerenderte Widgets im
Offscreen-Modus. Sie ersetzen keine längerfristige Bedienerprobung durch
Datenanwender. Es wurde kein vorhandenes Benutzerprofil verändert. Die
Testbilder liegen unter `build/qgis/`.

## Zugriffstest mit 100'000 Gebäuden

Deterministisch erzeugter Dateninhalt mit zusätzlichen Anlagen, Organisationen,
Aufträgen und Beziehungen; IBX-Dateigrösse 50'879'894 Bytes. Die folgenden Werte
sind **kumulierte tatsächliche Lesezugriffe**, nicht die Summe logischer
Cache-Anfragen. Der Kaltstart ist enthalten. Erzeugung mit der Java-CLI,
Messung ausschliesslich mit dem Python-Leser des Plugins.

| Schritt | Gelesene Bytes | Daten-Chunks |
|---|---:|---:|
| Öffnen und Katalog | 55'360 | 0 |
| Einzelobjekt zusätzlich | 16'830 | 1 |
| Erste Beziehungsseite zusätzlich | 43'418 | 1 |
| Gesamter Prüflauf | 3'899'157 | 248 |

10'004 eingehende Beziehungen wurden vollständig seitenweise gelesen, ohne
Lücken oder Duplikate. Der Quelldatei-Hash blieb unverändert. Der Einzelobjekttest
weist genau einen Daten-Chunk nach; fehlende Ziele und fehlender Rückwärtsindex
werden ausdrücklich unterschieden.

Zeitmessungen desselben Laufs auf dem Referenzrechner (Median nicht erhoben,
daher als Einzelmessung ausgewiesen). Vergleichswerte der früheren Java-Bridge
stammen aus einem Lauf derselben Sitzung auf derselben Datei:

| Zugriff | Python-Leser | frühere Java-Bridge |
|---|---:|---:|
| Öffnen und Katalog | 2.1 ms | 69 ms (inkl. JVM-Start) |
| Vollständiger Klassen-Scan, 100'000 Objekte | ca. 5 s (rund 20'000 Objekte/s) | 3.0 s über JSON-RPC |
| Räumliche Abfrage mit Index | 2.5 ms | nicht vergleichbar gemessen |

Der vollständige Prüflauf inklusive 10'004 Beziehungen, Klassen-Scan und
Hash-Kontrollen dauerte rund 13 s. Vollständige Klassenabfragen bleiben der
langsamste Python-Pfad (vollständiges Dekodieren in CPython); gezielte Lese-,
Karten- und Beziehungszugriffe sind für die Bedienung ausreichend schnell. Die
Java-Zahlen dienen nur der Einordnung und sind keine Zusage.

Reproduktion: `python3 scripts/verify-large.py`. Die detaillierten Zähler und
der konkrete Datei-Hash stehen in `build/large/report.json`. Eine erneute
Erzeugung kann wegen der absichtlich neuen Dataset-UUID einen anderen
Datei-Hash ergeben. Die Zahlen sind ein protokollierter Messlauf, keine
allgemeine Laufzeit- oder Grössengarantie.

## Zstandard-Bibliothek

Der Leser bindet die von QGIS mitgelieferte Zstandard-Bibliothek zur Laufzeit
über `ctypes` (macOS: `Contents/Frameworks/libzstd.1.dylib`, verifiziert mit
1.5.7). Ist keine Bibliothek auffindbar, bleiben `deflate`- und unkomprimierte
Dateien lesbar; zstd-komprimierte Dateien melden den Grund und lassen sich unter
**IBX → Einstellungen** über einen expliziten Pfad öffnen. Das Plugin liefert
keine Binärdateien aus.

## Bewusste Grenzen

Der Provider ist lesend. Ein allgemeiner verlustfreier GIS-Rückexport,
Authentisierung und Navigation zwischen Dateien sind nicht implementiert.
Der XTF-Export bleibt der Java-Kommandozeile vorbehalten. Ein laufender
Netzwerk-Leseaufruf kann trotz Abbruch bis zum konfigurierten Timeout dauern.
Grosse räumliche Kandidatenmengen werden im Arbeitsspeicher sortiert; eine sehr
grosse Abfrage kann vor der ersten Seite Arbeit verursachen.

Installation, Bedienablauf und reproduzierbare Befehle: [QGIS.md](QGIS.md).

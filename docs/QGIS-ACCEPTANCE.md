# Abnahme des IBX-Prototyps

Stand: 19. September 2026. Lokal geprüft auf macOS mit QGIS 4.2.2,
dessen Python 3.12 und Qt 6.11.1 sowie Java 21.0.10.

## Ausgeführte Prüfungen

| Prüfung | Ergebnis |
|---|---|
| `./gradlew test build installDist` | 67 Tests, keine Fehler oder übersprungenen Tests |
| `test_provider.py` mit QGIS-Python | 6 Tests: Features, Filter, Projektion, CRS, Rendering, parallele Iteratoren, Abbruch, Dateistand und Projekt-Neuladen |
| `test_ui.py` mit QGIS-Python | 3 Tests: echter Qt-Kartenklick, Layerauswahl, Inline-Lesen über Java, Diagnoseverlauf, Karte und Verlauf |
| `test_presentation.py` | 10 Tests: binäre und dreiseitige Assoziationen, Gegenrollen, Strukturen, Mehrfachverweise und exakte Werte |
| `test_object_tree.py` mit QGIS-Python | 9 Tests: Inline-Laden, Tastatur, Zyklen, Pagination, Quellentrennung, Abbruch, verspätete Antworten und Farbschemata |
| `test_https.py` mit QGIS-Python | 1 Test: Python-Provider → Java-Bridge → tatsächlicher HTTPS-Range-Server |
| Java-HTTPS-Test | Testlokales Vertrauen; Zertifikatsfehler, Redirects, Downgrade, ETag-Wechsel, fehlerhafte Ranges, fehlende Ranges und Timeout |
| `verify-wkb-gdal.py` | 22 WKB-Fälle, einschliesslich Kurven und XYZ, mit lokalem GDAL 3.13.3 |
| INTERLIS-Demo | Modellvalidierung und unabhängiger XTF-Roundtrip; Strukturen und OID-lose Assoziationen |
| Paketprüfung | ZIP separat entpackt; enthaltene Bridge gestartet, enthaltene Demo mit 24 Gebäude-Features gelesen |

Die erweiterte Objektansicht wurde mit 28 Python-Tests in der lokalen
QGIS-Laufzeit geprüft (6 Provider-, 3 Bedienablauf-, 10 Aufbereitungs-,
9 Objektbaum- und 1 HTTPS-Test). `relation_fixtures.py` enthält zusätzliche
typisierte Protokollfixtures; diese sind bewusst keine zusätzlichen validierten
INTERLIS-Transferdateien. Der bestehende Bedienablauf verwendet weiterhin die
echte `.ibx`-Demo und die Java-Bridge. Er prüft einen einzelnen Zielzugriff beim
Aufklappen, keinen Zugriff beim Wiederaufklappen und keine automatische
Referenznachladung. Prüfung des extrahierten ZIP samt eigener Bridge:
`python3 scripts/verify-qgis-package.py`.

Die QGIS-Tests verwenden echte QGIS-/Qt-Klassen und gerenderte Widgets im
Offscreen-Modus. Sie ersetzen keine längerfristige Bedienerprobung durch
Datenanwender. Es wurde kein vorhandenes Benutzerprofil verändert. Die
Testbilder liegen unter `build/qgis/`.

## Zugriffstest mit 100'000 Gebäuden

Deterministisch erzeugter Dateninhalt mit zusätzlichen Anlagen, Organisationen,
Aufträgen und Beziehungen; IBX-Dateigrösse 50'879'894 Bytes. Ausführung mit
128 MiB maximalem Java-Heap und deaktiviertem Prefetch. Die folgenden Werte
sind **kumulierte tatsächliche Lesezugriffe**, nicht die Summe logischer
Cache-Anfragen. Der Kaltstart ist enthalten.

| Schritt | Gelesene Bytes | Daten-Chunks |
|---|---:|---:|
| Öffnen und Katalog | 55'560 | 0 |
| Einzelobjekt zusätzlich | 72'390 | 1 |
| Erste Beziehungsseite zusätzlich | 115'808 | 2 |
| Gesamter Prüflauf | 1'365'322 | 29 |

10'004 eingehende Beziehungen wurden vollständig seitenweise gelesen, ohne
Lücken oder Duplikate. Der beobachtete maximale Cache lag bei 1'365'242 Bytes.
Der Quelldatei-Hash blieb unverändert. Der separate Einzelobjekttest weist
genau einen Daten-Chunk nach; fehlende Ziele und fehlender Rückwärtsindex
werden ausdrücklich unterschieden.

Reproduktion: `python3 scripts/verify-large.py`. Die detaillierten Zähler und
der konkrete Datei-Hash stehen in `build/large/report.json`. Eine erneute
Erzeugung kann wegen der absichtlich neuen Dataset-UUID einen anderen
Datei-Hash ergeben. Die Zahlen sind ein protokollierter Messlauf, keine
allgemeine Laufzeit- oder Grössengarantie.

## Bewusste Grenzen

Der Provider ist lesend. Ein allgemeiner verlustfreier GIS-Rückexport,
Authentisierung und Navigation zwischen Dateien sind nicht implementiert.
Der Fragmentexport erhält vollständige ausgewählte Originalobjekte, lädt
aber keine Referenzziele automatisch nach. Ein laufender Netzwerk-Leseaufruf
kann trotz Abbruch bis zum konfigurierten Timeout dauern. Grosse räumliche
Kandidatenmengen können vor der ersten Seite Sortierarbeit verursachen.

Installation, Bedienablauf und reproduzierbare Befehle: [QGIS.md](QGIS.md).

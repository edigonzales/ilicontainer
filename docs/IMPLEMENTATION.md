# Implementierung und Abnahme

IBX verwendet Format 5, Java-Packages `ch.interlis.ibx`, die API `IbxContainer`
und die CLI `ibx`. Der bisherige Java-Kern bleibt erhalten; NavigationBuilder
schreibt den Katalog und den Rückwärtsindex über begrenzte externe Sortierung.
`Navigation` bietet vollständige typisierte Objekte, Katalogseiten und eingehende
Beziehungen. Die bestehende GIS-API bleibt für direkte WKB-Zugriffe verfügbar.
Das QGIS-Plugin enthält eine zweite, Java-freie Read-Implementierung des Formats
(`qgis/ibx_browser/ibx/`); die frühere Bridge bleibt als Java-Protokoll und
Java-Testgegenstand erhalten, wird aber nicht mehr ausgeliefert.

## Prüfungen

- Bisherige 67 Java-Regressionstests: Semantik, WKB, Kurven, Indexseiten, HTTP,
  feste Heapgrenzen, unabhängiges Binärfixture und alte Header.
- NavigationTest: Katalog ohne Daten-Chunks, Einzelobjektzugriff, mehrseitige
  Rückwärtsnavigation, Strukturreferenzen, OID-lose Assoziationen, fehlender Index,
  Bridge-Authentisierung, Fragmentexport, Quelldateiintegrität, unabhängiger
  Demo-Roundtrip und vollständige INTERLIS-Validierung.
- HttpsTest: echter TLS-Server mit temporärem Testzertifikat und ausschliesslich
  testlokalem Vertrauen. Unbekanntes Zertifikat, HTTPS-Downgrade, defekte Ranges,
  fehlender ETag, fehlende Ranges, expliziter Snapshot und Timeout werden geprüft.
- Python-Lesertests (`qgis/tests/test_reader.py`, ohne QGIS und Java): CBOR,
  Schlüsselkodierung, Frame-/Footerprüfung, B+-Baum, Katalog, Objekt- und
  Beziehungszugriff, räumliche Kandidaten sowie HTTP-Range mit ETag. Je eine
  `deflate`- und eine unkomprimierte Datei liegen als Fixture bei; Zstd-Fälle
  werden ohne gefundene Bibliothek übersprungen.
- QGIS-Providertests: reale Layer, FIDs, Bounding Box, exakte Filter, Ausdrücke,
  Feldprojektion, NoGeometry, Limits, Subsets, Iterator-Rewind, Tabellen,
  parallele Iteratoren, Rendering, CRS-Transformation und Projekt-Neuladen.
- QGIS-HTTPS-Test: echter HTTPS-Range-Server direkt durch den Python-Leser und
  QGIS-Layer, mit testlokalem Zertifikat, Kartenabfrage und Beziehungsnavigation.
- QGIS-GUI-Test: asynchrone Objektnavigation, ungeöffnete Zielklassen,
  bedarfsweises Kartenlayer-Laden, Historie, fehlende Ziele und Attributtabelle.
  Prüfbilder entstehen unter `build/qgis/`.
- `scripts/verify-large.py`: reproduzierbare 100'000-Objekt-Demo, 10'000 eingehende
  Gebäudereferenzen, Pagination ohne Duplikate, räumlicher Zugriff, vollständiger
  Klassen-Scan und Read-only-Hash. Die Datei entsteht mit der Java-CLI; alle
  Messungen stammen vom Python-Leser.

Ausführung und Grenzen stehen in [QGIS.md](QGIS.md), das verbindliche Format in
[FORMAT.md](FORMAT.md), der Transportvertrag der Java-Bridge im
[Protokoll](../protocol/README.md). Die historischen Berichte unter
`docs/benchmarks/` bleiben Ergebnisse der damaligen Formatversionen und sind keine
IBX-4-Leistungsmessung. Java-CI ist für macOS/Linux konfiguriert, die
Python-Lesertests zusätzlich für Windows; lokale Läufe ersetzen keine Ausführung
beider CI-Jobs.

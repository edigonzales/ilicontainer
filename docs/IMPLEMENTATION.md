# Implementierung und Abnahme

IBX verwendet Format 4, Java-Packages `ch.interlis.ibx`, die API `IbxContainer`
und die CLI `ibx`. Der bisherige Java-Kern bleibt erhalten; NavigationBuilder
schreibt den Katalog und den Rückwärtsindex über begrenzte externe Sortierung.
`Navigation` bietet vollständige typisierte Objekte, Katalogseiten und eingehende
Beziehungen. Die bestehende GIS-API bleibt für direkte WKB-Zugriffe verfügbar.
Die QGIS-Bridge verwendet dieselben Container-, Modell- und HTTP-Reader.

## Prüfungen

- Bisherige 60 Regressionstests: Semantik, WKB, Kurven, Indexseiten, HTTP,
  feste Heapgrenzen, unabhängiges Binärfixture und alte Header.
- NavigationTest: Katalog ohne Daten-Chunks, Einzelobjektzugriff, mehrseitige
  Rückwärtsnavigation, Strukturreferenzen, OID-lose Assoziationen, fehlender Index,
  Bridge-Authentisierung, Fragmentexport, Quelldateiintegrität, unabhängiger
  Demo-Roundtrip und vollständige INTERLIS-Validierung.
- HttpsTest: echter TLS-Server mit temporärem Testzertifikat und ausschliesslich
  testlokalem Vertrauen. Unbekanntes Zertifikat, HTTPS-Downgrade, defekte Ranges,
  fehlender ETag, fehlende Ranges, expliziter Snapshot und Timeout werden geprüft.
- QGIS-Providertests: reale Layer, FIDs, Bounding Box, exakte Filter, Ausdrücke,
  Feldprojektion, NoGeometry, Limits, Subsets, Iterator-Rewind, Tabellen,
  parallele Iteratoren, Rendering, CRS-Transformation und Projekt-Neuladen.
- QGIS-HTTPS-Test: echter HTTPS-Range-Server über Java-Bridge und QGIS-Layer,
  mit testlokalem Truststore, Kartenabfrage und Beziehungsnavigation.
- QGIS-GUI-Test: asynchrone Objektnavigation, ungeöffnete Zielklassen,
  bedarfsweises Kartenlayer-Laden, Historie, fehlende Ziele und Attributtabelle.
  Prüfbilder entstehen unter `build/qgis/`.
- `scripts/verify-large.py`: reproduzierbare 100'000-Objekt-Demo, 10'000 eingehende
  Gebäudereferenzen, Pagination ohne Duplikate, räumlicher Zugriff und Read-only-Hash.

Ausführung und Grenzen stehen in [QGIS.md](QGIS.md), das verbindliche Format in
[FORMAT.md](FORMAT.md), der Transportvertrag im [Protokoll](../protocol/README.md).
Die historischen Berichte unter `docs/benchmarks/` bleiben Ergebnisse der damaligen
Formatversionen und sind keine IBX-4-Leistungsmessung. Java-CI ist für macOS/Linux
konfiguriert; lokale Läufe ersetzen keine Ausführung beider CI-Jobs.

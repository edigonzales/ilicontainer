# WKB-Geometrieprofil (`wkb-iso-v1`)

Das optionale Profil ersetzt IOM-Geometriebäume durch ISO-WKB. Es speichert keine
zweite Geometriekopie. Attribute, Referenzen, Strukturen, Identitäten und
Basketkontexte bleiben im Objekt enthalten. Standard ist weiterhin `iom`.
Ein QGIS-/GDAL-Dateitreiber ist noch nicht enthalten. Die GIS-API stellt bereits
Layerbeschreibungen, skalare Attribute und WKB für einen solchen Reader bereit.

## Erstellen und exportieren

```sh
ilicontainer create input.xtf output.ilic --model-dir ./models \
  --geometry-encoding wkb \
  --geometry-crs MyModel.Topic.Class.Geometry=EPSG:2056
ilicontainer info output.ilic
ilicontainer export output.ilic roundtrip.xtf
ilicontainer add-spatial-index output.ilic MyModel.Topic.Class Geometry
```

`--geometry-crs` ist wiederholbar. Bekannte Modell-CRS werden übernommen;
Basketzuordnungen generischer Koordinatendomains werden beim Einlesen aufgelöst.
Unbekannte CRS benötigen eine explizite Zuordnung. Widersprüche zwischen Modell,
Basket und expliziter Zuordnung führen zum Abbruch. Eine explizite Zuordnung ist
eine Aussage des Aufrufers über vorhandene Koordinaten, keine Transformation.

IOM- und WKB-Dateien verwenden ausschliesslich Containerformat 3. Alte Dateien
der Formate 1 und 2 müssen aus ihren XTF-Quellen neu erstellt werden. Ein WKB-Erstellungsfehler veröffentlicht keine
Zieldatei und überschreibt keine vorhandene Datei. Ein späterer Fehler beim
optionalen Indexaufbau lässt den vollständigen Core-Container bestehen.

## Unterstützte Geometrien

| INTERLIS | ISO-WKB |
|---|---|
| COORD / MULTICOORD | Point / MultiPoint |
| POLYLINE | LineString; bei Bögen CompoundCurve mit CircularString-Bestandteilen |
| MULTIPOLYLINE | MultiLineString / MultiCurve |
| SURFACE / AREA | Polygon / CurvePolygon |
| MULTISURFACE / MULTIAREA | MultiPolygon / MultiSurface |

Unterstützt werden XY und XYZ. WKB verwendet Little Endian und den ISO-Z-Offset
1000; SRID steht nicht in den Geometriebytes. Die Modellabbildung erhält Typ,
Dimension, Zahlenbereiche und Genauigkeit, Linienformen, Richtung, Achsen und CRS.
Verschachtelte Strukturen werden ebenfalls rekursiv kodiert.

Koordinaten und Bogenstützpunkte bleiben numerisch identisch. Jede ursprüngliche
Dezimalzahl muss `BigDecimal -> double -> Double.toString -> BigDecimal` ohne
Wertänderung überstehen. Es wird nicht auf Modellgenauigkeit gerundet.
Bogenstützpunkte erhalten bei XYZ eine abgeleitete Höhe entsprechend dem Anteil
an der Winkelstrecke; im rekonstruierten INTERLIS-Bogen wird keine A3 ergänzt.
Es gibt keine Linearisierung und keine automatische Geometriereparatur.

Fehlende Geometrien bleiben fehlend. Definierte leere Geometrien, M, explizite
Bogenradien, benutzerdefinierte Linienformen, unvollständige Geometrien,
widersprüchliche Dimensionen und numerisch instabile Bögen werden abgelehnt.
Diagnosen nennen BID, TID und Attributpfad. Die Prüfung garantiert den unterstützten
Geometrie-Roundtrip, ist aber keine vollständige INTERLIS-Constraint- oder
AREA-Topologievalidierung.

Nach jeder Kodierung wird WKB zurückgelesen, nach IOM rekonstruiert und unabhängig
von der WKB-Darstellung mit dem Original verglichen. Nur die Aufteilung eines
Flächenrings auf mehrere Polylinien darf normalisiert werden. Reihenfolge,
Richtung und Kontrollpunkte bleiben erhalten. Zahlenformatierungen dürfen sich
ändern (`1.2300` zu `1.23`).

## Direkter GIS-Zugriff

```java
try (IliContainer container = IliContainer.open(Paths.get("output.ilic"));
     GisLayer layer = container.openLayer("MyModel.Topic.Class.Geometry");
     Stream<GisFeature> features = layer.features()) {
  features.forEach(feature -> {
    byte[] wkb = feature.getWkb(); // null bei fehlender Geometrie
    long fid = feature.getFid();
    String tid = feature.getTid();
    String bid = feature.getBid();
    Map<String, Object> attributes = feature.getAttributes();
  });
}
```

`layers()` liefert die IDs konkreter Klassen mit direkten Geometrieattributen.
Mehrere Geometrieattribute erzeugen mehrere Layer desselben Objekts.
`getGeometryDescriptor()` beschreibt Geometrie und CRS; `fields()` liefert
skalare Feldtypen. Geometrien in Strukturen erzeugen keinen eigenen Layer.
Referenzen, Strukturen und Blackboxes bleiben über die vollständige IOX-API
zugänglich; es gibt keine automatische Abflachung.

Ganzzahlen werden als `BigInteger`, Dezimalzahlen als `BigDecimal`, boolesche Werte
als `Boolean` und übrige skalare Werte als `String` geliefert. Mehrere skalare
Werte werden als geordnete Liste geliefert; fehlende Werte sind `null`.
Metadaten und Basketkontexte sind für lesende Verwendung vorgesehen.

`getFeature(fid)` liefert ein `Optional<GisFeature>`. Eine FID ist die globale,
nullbasierte Objektposition in der physischen Containerreihenfolge. Sie gilt nur
innerhalb dieser Datei, wird von mehreren Layern desselben Objekts geteilt und
wird beim Neuaufbau nicht als externe Identität garantiert. Unbekannte FIDs und
FIDs anderer Klassen liefern leere Ergebnisse. Der Zugriff liest höchstens
einen Daten-Chunk zusätzlich zu Metadaten und Indexseiten.

`queryCandidates(BoundingBox)` benötigt einen Spatial Index und liefert Kandidaten
in Containerreihenfolge. Randberührungen zählen, Z wird ignoriert. Die Ausgabe
prüft die konservative Objektumhüllung erneut. Keine CRS-Transformation und keine
exakte Intersects-Prüfung. Die Bogenumhüllung verwendet dieselbe analytische,
nach aussen gerundete Rechnung wie der IOM-Pfad.

Alle Streams sind unabhängig und zu schliessen, insbesondere bei `findFirst()`.
Auch Layer und Container sind zu schliessen. Die GIS-API verlangt das WKB-Profil; sie
führt bei IOM-Dateien keine versteckte Konversion aus. Der Feature-Scan liest die
CBOR-Objektrecords und liefert die gespeicherten WKB-Bytes ohne IOM-Rekonstruktion.

## Prüfung und Reproduktion

```sh
./gradlew build installDist
python3 scripts/verify-wkb-gdal.py  # benötigt GDAL-Python-Bindings
```

Linux-CI installiert `python3-gdal` und führt den unabhängigen Test verpflichtend
aus. 22 explizite XY-/XYZ-Testgeometrien werden gegen unabhängig geschriebene
WKT-Erwartungen geprüft, einschliesslich Typ, Dimension, Kontrollpunkten und
byteidentischer ISO-WKB-Rückgabe. Ein lokaler Linux-Lauf wurde mit GDAL 3.11.4
im Container `ghcr.io/osgeo/gdal:ubuntu-small-3.11.4` durchgeführt.

Die vorhandenen Container-, Semantik-, Spatial-Paging- und Remote-Tests laufen
für IOM und WKB. Dazu gehören Export im frischen Prozess ohne Modellserver,
100000 Objekte mit konstantem Geometrieumfang bei 64 MiB Writer-/32 MiB Reader-Heap,
Fragmentkontexte, übergrosse Chunks und HTTP-Standwechsel.
Zusätzliche Tests prüfen Präzisionsverlust, verschachtelte Geometrien, atomaren
Abbruch, FID-Zugriffe, ungültige WKB und fehlende Indizes.

Benchmark-Reproduktion und Ergebnisse: [WKB-Benchmarks](benchmarks/wkb/README.md).
Herkunft der Kurvenkodierung: [THIRD_PARTY.md](../THIRD_PARTY.md).

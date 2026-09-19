# Experimentelles Dateiformat 3

Diese Beschreibung konkretisiert die Architektur-Spezifikation v0.3. Reader und Writer unterstützen **ausschliesslich Format 3**, für IOM und WKB. Dateien der Formate 1 und 2 werden ausdrücklich abgelehnt und müssen aus dem ursprünglichen XTF neu erstellt werden. Es gibt keine Migration und keine Formatversionsoption. Die Formatversion ist unabhängig von der Spezifikationsversion; langfristige Binärkompatibilität ist noch nicht zugesagt.

## Aufbau

Alle festen Zahlenfelder verwenden Big Endian. Offsets sind absolute, nichtnegative 64-Bit-Bytepositionen. Längen sind 64-Bit-Werte; die Java-Implementierung begrenzt einen einzelnen Frame auf weniger als 2 GiB. Grössere Dateien sind möglich. Ein übergrosses Objekt wird niemals auf mehrere Chunks aufgeteilt; der Heap muss sein Dekodieren ermöglichen.

| Abschnitt | Darstellung |
|---|---|
| Header, 16 Bytes | Magic `ILICONT1` (8), Version (4), erforderliche Featurebits (4; derzeit 0) |
| Metadaten | CBOR mit versionierter Modellabbildung, Dictionary und Transfermetadaten |
| Datenbereich | Je Basket Metadaten, null oder mehr Chunks, Basketende; danach Transferende |
| Verzeichnisse | Unveränderlicher B+-Baum, Überlaufbereiche |
| Optionale räumliche Indizes | Gepackte R-Bäume und Manifest |
| Footer, 64 Bytes | Magic, Verzeichnis- und Spatial-FrameRef, Dateilänge, Version, reservierte Felder, CRC32; genaue Belegung unten |

Ein Frame besteht aus Typ (4 Bytes), Nutzdatenlänge (8), CRC32 der Nutzdaten (4) und Nutzdaten. Typen: Metadaten 1, Basket 2, Chunk 3, Basketende 4, Transferende 5, Indexblatt 6, Indexzweig 7, räumliches Blatt 8, räumlicher Zweig 9, Spatial-Manifest 10, Überlauf 11. Unbekannte erforderliche Features und unerwartete Frame-Typen werden abgelehnt.

Der sequenzielle Reader benötigt nur Header, Metadaten und Datenbereich. Er endet am Transferende und prüft dabei Daten-Frame-Prüfsummen; er validiert nicht nachgelagerte Verzeichnisse oder den Footer. `IliContainer.open` prüft zusätzlich den Footer. Indexseiten werden beim Zugriff geprüft.

## Modellabbildung und Objekte

Die Modellabbildung enthält die Informationen für `ViewableProperties`, insbesondere Attributreihenfolge, qualifizierte Namen, XML-Namensabbildung und die Eigenschaften von Blackbox-, OID- und Mehrfachgeometrieattributen. Es werden keine Java-Objekte serialisiert. Das spätere Lesen und Exportieren benötigt weder ILI-Dateien noch Modellserver.

Das Dictionary ist eine Liste von Namen; ihre Position ist die jeweilige ID. Objektwerte sind rekursive CBOR-Arrays:

```text
[tagId, tid, referenceTid, referenceBid, referenceOrder,
 operation, consistency, [[attributeId, [value, ...]], ...]]
```

Ein Wert ist ein String, null, ein verschachteltes Objektarray oder eine explizite Dezimaldarstellung. `lexical` erhält die ursprünglichen skalaren Zeichenfolgen. `decimal` speichert bei modellbekannten Zahlen sowie Geometrieordinaten die ganzzahlige Mantisse als Zweierkomplement-Bytes und die Dezimalskala. Dekodierung: `mantissa × 10^(-scale)`. Es erfolgt keine Umwandlung der gespeicherten Werte in `double`. LIST-/BAG-Wertfolgen und Referenzreihenfolgen bleiben erhalten. Hauptobjekte dürfen innerhalb eines Baskets nach konkreter Klasse umgeordnet werden.

Ein Chunk-Frame enthält die Länge seines CBOR-Headers (4 Bytes), den Header und komprimierte CBOR-Objektsequenzen. Der Header enthält Chunk-ID, Basketposition/-offset, BID, Topic, Klasse, Objektzahl, Kompression und unkomprimierte Länge. Unterstützt werden `zstd`, `deflate` und `none`. Standard: Zstandard 3 und 256 KiB unkomprimierte Nutzdaten.

## Fachliche Verzeichnisse

Ein gemeinsamer B+-Baum enthält getrennte Schlüsselbereiche. Die folgende Tabelle verwendet `\0` lediglich zur lesbaren Darstellung von Komponenten. Auf der Platte stehen binäre Schlüssel gemäss der Bytebelegung unten, keine dezimalen Positionszeichenketten.

| Präfix | Bedeutung |
|---|---|
| `B\0BID` | Basketmetadaten, einschliesslich leerer Baskets |
| `P\0Basketposition` | Basket in ursprünglicher Reihenfolge |
| `O\0TID` | Objektposition: Basket, Chunk, nullbasiertes Objektordinal |
| `C\0Klasse\0Basketposition\0Chunk-ID` | Klassen-Chunks |
| `D\0Basketposition\0Chunk-ID` | Basket-Chunks |
| `T\0Topic\0Basketposition\0…` | Basketmetadaten und Topic-Chunks |
| `F\0ersteFID` | FID-Bereich eines Chunks, Objektanzahl und direkte Chunk-/Basketadresse |

Jede Seite enthält eine Anzahl und präfixkomprimierte Schlüssel-Wert-Paare. Interne Werte sind vollständige FrameRefs; Separatoren sind die kleinsten Schlüssel ihrer Teilbäume. Kinder werden vor ihren Eltern geschrieben. Die kodierte Nutzdatengrösse bestimmt die 16-KiB-Seitengrenze. Lange Felder liegen in Überlauf-Frames. Das zuvor doppelte Chunkverzeichnis entfällt; Chunkmetadaten stehen im Chunk.

Externe Sortierung verwendet begrenzte Runs und höchstens 32 gleichzeitig zusammengeführte Eingabedateien. Überlange einzelne Schlüssel/Werte können die Sortierzielgrösse überschreiten. Duplikate der TID- und BID-Schlüssel führen zum Abbruch. OID-lose Assoziationsinstanzen erhalten keinen erfundenen TID-Schlüssel und bleiben über Klasse/Basket/Topic zugänglich.

## Räumlicher Zugriff

Ein R-Baum wird standardmässig mit STR gepackt: Auf jeder Ebene werden Bounding-Box-Mittelpunkte nach X in Streifen gruppiert und innerhalb der Streifen nach Y sortiert. Externe Sortierung und temporäre Ebenendateien begrenzen den Speicher. Knotengrenzen richten sich nach 16 KiB kodierten Nutzdaten. `x` bleibt als Vergleichsvariante verfügbar. Blätter speichern konservative XY-Bounding-Boxes und physische Objektadressen. Das Manifest ordnet Klasse und Geometrieattribut einer Wurzel, einem CRS, den Achsen `C1,C2` und der Objektzahl zu.

Kreisbögen werden analytisch umschlossen, ohne Linearisierung. Die gemeinsame, IOM-unabhängige Geometrieberechnung prüft die Berechenbarkeit. Orientierung und Zugehörigkeit der vier Achsenextrema werden zusätzlich mit exakten Dezimaloperationen bestimmt; Mittelpunkt und Radius erhalten nach aussen gerundete rationale beziehungsweise Dezimalgrenzen. Koordinatengrenzen werden nach aussen gerundet. Nicht berechenbare Bögen und Bögen mit explizitem R-Attribut werden für die Indexierung ausdrücklich abgelehnt; ihre IOM-Core-Kodierung bleibt erhalten. Das WKB-Profil lehnt solche Inhalte bereits bei der Erstellung ab. Fehlende Geometrien erzeugen keinen Eintrag. Gemischte Basket-Domainzuordnungen werden nicht gemeinsam indexiert. Bei generischen Domainzuordnungen ist zusätzlich eine explizite CRS-Angabe erforderlich.

Kandidaten werden anhand der gespeicherten Objekt-Bounding-Boxes geprüft. Für deterministische Containerreihenfolge werden die Kandidatenpositionen extern sortiert. Dadurch bleibt der Speicher begrenzt; die erste Objektausgabe wartet jedoch auf die Indexauswertung und Sortierung. Keine exakte geometrische Intersects-Prüfung.

Optionale Indizes entstehen in einer neuen Dateifassung. Eine fehlgeschlagene Indexerstellung lässt die vorhandene Core-Datei unverändert. Erneutes Indexieren ersetzt den Manifestverweis; bisherige Indexseiten können in der neuen Datei verbleiben. Es gibt noch keine Kompaktierung.

## IOX-Kompatibilitätsadapter

- Der mitgelieferte StAX-Serviceprovider auf Basis von Woodstox aktiviert Text-Coalescing, damit der Koordinatenreader von iox-ili unabhängig von Eingabeblockgrenzen funktioniert. DTDs und externe Entitäten sind deaktiviert. Anwendungen, die selbst einen StAX-Provider vorgeben, müssen diese Einstellungen ebenfalls sicherstellen.
- iox-ili 1.24.4 maskiert XML-Blackboxes beim Schreiben als normalen Text. `LosslessXtfWriter` ersetzt ausschliesslich diese modellbekannten Werte durch temporäre Marker und stellt nach dem Schreiben eines Events das XML-Fragment wieder her. Die eigentliche XTF-Struktur wird weiterhin vollständig von iox-ili geschrieben. Das XML-Fragment wird vorher auf Wohlgeformtheit geprüft; der Eventpuffer ist durch das grösste ausgegebene Objekt bestimmt.

## Lebensdauer und Integrität

Container und Fragmente sind zu schliessen; zurückgegebene Streams ebenfalls, insbesondere bei vorzeitigem Abbruch. Basket- und Objektansicht eines Fragments öffnen unabhängige Cursor. Metadatenobjekte sind für lesende Verwendung vorgesehen; die API ist nicht für parallele Mutation ausgelegt.

Remote-Zugriffe verwenden einen starken ETag mit `If-Match` oder eine vom Aufrufer ausdrücklich als unveränderlich deklarierte URL. Antworten müssen 206, den angeforderten Bereich und dieselbe Dateilänge enthalten. Ein vollständiger Download ist ausschliesslich beim Öffnen und nach ausdrücklicher Freigabe erlaubt; er wird als neue lokale Momentaufnahme verwendet. Spätere Vollantworten und Standwechsel brechen den Zugriff ab.

CRC32 dient der Erkennung von Beschädigungen, nicht der Authentifizierung. Der Container ist ein experimentelles Transferformat, keine Datenbank und kein Transaktionssystem.

## Zahlenkodierung: Entscheidung im Prototyp

Die Modellskala bleibt in `numericTypes` verfügbar. Die Dezimalvariante speichert trotzdem die tatsächliche Mantisse und Skala jedes Werts. Eine ausschliesslich aus dem Modell abgeleitete Skalierung würde bei ungeprüften Eingaben entweder runden oder einen zusätzlichen Ausnahmefall benötigen. Da die Erstellung keine vollständige Modellvalidierung voraussetzt, bleibt die explizite Skala der robuste erste Messpunkt. Native CBOR-Integer für Mantissen und das Weglassen wiederholter Modellskalen sind weitere Kompressionsoptimierungen; sie sind nicht Bestandteil von Dateiformat 3.

Die Reihenfolge der Modell-/Quellprovenienzlisten kann von der Auflösungsreihenfolge des Compilers abhängen. Sie hat keine Transfersemantik; byteidentische Container über getrennte Erstellungen werden daher noch nicht zugesagt. Der abschliessende Neuaufbau der grossen 256-KiB-Standardvariante ergab identische Daten-/Verzeichnisframes und identische Metadaten nach Sortierung dieser Provenienzlisten.

## WKB-Profil in Format 3

Metadaten ergänzen `geometryEncoding=wkb`, `geometryProfile=wkb-iso-v1`,
`geometries` (nach qualifiziertem Attributpfad), `scalarTypes` und
`concreteClasses`. Geometriedeskriptoren enthalten Modelltyp, Dimension,
Minima/Maxima/Genauigkeiten, Linienformen, Richtung, Achsen, Domain und CRS.
`mappingVersion=1` bezeichnet weiterhin die rekonstruierbare IOX-Writerabbildung.

An der Position eines Geometriewerts steht eine CBOR-Map:

```
{"geometry": "Model.Topic.Class.Attribute", "root": "MULTISURFACE", "wkb": h'...'}
```

`geometry` referenziert den Modelldeskriptor, `root` die IOM-Wurzelform für die
Rekonstruktion. `wkb` ist eine binäre ISO-WKB-Geometrie, kein IOM-Baum.
Die expliziten Schlüssel unterscheiden diesen Wert von Dezimalmaps (`m`, `s`),
Objektarrays und Blackboxes. Die Ersetzung erfolgt auch in Strukturen.

Chunk-Metadaten enthalten zusätzlich `firstFid`, die globale nullbasierte
Objektordinalzahl des ersten Objekts. FID = `firstFid + Objektordinal im Chunk`.
Das Verzeichnis enthält pro Chunk einen `F`-Bereichseintrag mit erster FID und Objektanzahl. Eine Vorgängersuche liefert den zuständigen Chunk; unbekannte FIDs ergeben eine leere Auswahl. Auch IOM-Chunks erhalten FID-Bereiche. Die GIS-API setzt weiterhin WKB voraus.

Der neutrale Objektcursor liefert CBOR-Records wahlweise direkt oder als IOM.
GIS-Zugriff und WKB-Indexaufbau verwenden den direkten Weg. Die Geometriekodierung
und analytische Umhüllung benötigen weder Hop noch LocationTech JTS. Details und
Profilgrenzen stehen in [WKB.md](WKB.md).

## Format 3 — verbindliche Bytebelegung

Format 3 ersetzt die Formate 1 und 2. Der 16-Byte-Header behält Familien-Magic,
Versionsfeld (3) und Featurefeld (0). Frames behalten Typ i32, Nutzlänge i64,
CRC32 i32 und Nutzdaten. Alle binären Felder sind Big Endian, ausgenommen WKB.
Eine FrameRef besteht aus Offset i64 und vollständiger Framelänge i64.

Der 64-Byte-Footer enthält: Magic i64, Hauptverzeichnis-FrameRef (16 Bytes),
Spatial-Manifest-FrameRef (16 Bytes, beide Werte 0 wenn fehlend), Dateilänge i64,
Version i32, reserviert i32 (0), CRC32 i32 über die ersten 56 Bytes, reserviert
i32 (0). Referenzen müssen vollständig vor dem Footer liegen.

B+-Baumseiten beginnen mit Eintragszahl i32. Pro Eintrag folgen gemeinsame
Präfixlänge i32, Suffixfeld und Wertfeld. Ein Feld besteht aus Länge i32 und Bytes;
Länge -1 verweist über eine FrameRef auf einen OVERFLOW-Frame. Das erste Präfix
ist 0. Branchwerte sind FrameRefs. Schlüssel werden unsigned lexikografisch nach
Bytes verglichen. Strukturierte Schlüssel beginnen mit dem bisherigen
Eintragstyp als ASCII-Byte. Textkomponenten haben Marker 1, UTF-8 mit 00→00 FF
und Abschluss 00 00. Positionskomponenten haben Marker 2 und einen nichtnegativen
i64-Wert. Damit ersetzen acht Bytes die bisherigen zwanzig Dezimalziffern.

Locations: Codecversion u8 (1), Chunk-FrameRef, Basket-FrameRef,
Basketposition i64, Chunk-ID i64, Objektordinal i32 (-1 für den ganzen Chunk).
Die Länge beträgt 53 Bytes. Basketverweise verwenden eine leere Chunk-FrameRef.
FID-Bereichseinträge: erste FID im Schlüssel, Location (53 Bytes), Objektanzahl
i32. Pro Chunk existiert genau ein Bereich; die Vorgängersuche prüft dessen Ende.

Chunkmetadaten enthalten firstFid für beide Geometriekodierungen. Metadaten
enthalten Geometriekodierung und optionale räumliche Sortierung.
Spatial-Knoten verwenden weiterhin CBOR, Kindreferenzen enthalten zusätzlich
Framelängen; Blatt-Locations werden als binäre 53-Byte-Werte gespeichert.

## Datenanordnung und Zugriff

`WriterOptions.spatialOrder` beziehungsweise `--spatial-order Klasse.Attribut` sortiert ausschliesslich innerhalb einer Basket-/Klassen-Gruppe. Die konservativen Umhüllungsmittelpunkte werden auf je 32 Bit normalisiert und nach dem unsigned 64-Bit-Hilbert-Wert geordnet. Gleiche Werte behalten die ursprüngliche Reihenfolge; fehlende Geometrien stehen am Ende. Gruppen und Sortierläufe liegen in temporären Dateien. FIDs werden erst danach vergeben. Ohne Option bleibt die ursprüngliche Reihenfolge innerhalb einer Klasse bestehen.

HTTP beginnt mit einer einzigen 16-Byte-Headeranfrage. Bekannte Frames werden mit einer Anfrage einschliesslich CRC geladen. Räumliche Objektcursor betrachten bis zu 32 Positionen voraus. Bereiche mit bis zu 4 KiB Zwischenraum werden bis 1 MiB zusammengefasst; grössere Frames werden beim Zugriff einzeln geladen. Nur vollständig geprüfte Frames gelangen in den gemeinsamen, standardmässig 32 MiB grossen Cache. Die temporäre zusammengefasste Antwort ist auf 1 MiB begrenzt. `RemoteOptions.prefetchPositions=0` deaktiviert das Vorladen.

`info --storage` zählt physische Bytes je Abschnittstyp sowie Schlüssel- und Wertfelder nach Eintragstyp. Gemeinsame Seitenkosten (Frameheader und Eintragsanzahl) und Überlauf-Frames werden separat ausgewiesen. Lesemetriken unterscheiden logische Framezugriffe, HTTP-Anfragen, zusätzliche Zwischenraumbytes, geladene Metadaten/Indexseiten/Chunks und maximale Cachebelegung.

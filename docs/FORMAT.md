# Experimentelles Dateiformat 1

Diese Beschreibung konkretisiert die Architektur-Spezifikation v0.3 für den Java-Prototyp. Die Dateiformatversion ist `1`; sie ist unabhängig von der Spezifikationsversion. Es besteht noch keine Zusage einer langfristigen Binärkompatibilität.

## Aufbau

Alle festen Zahlenfelder verwenden Big Endian. Offsets sind absolute, nichtnegative 64-Bit-Bytepositionen. Längen sind 64-Bit-Werte; die Java-Implementierung begrenzt einen einzelnen Frame auf weniger als 2 GiB. Grössere Dateien sind möglich. Ein übergrosses Objekt wird niemals auf mehrere Chunks aufgeteilt; der Heap muss sein Dekodieren ermöglichen.

| Abschnitt | Darstellung |
|---|---|
| Header, 16 Bytes | Magic `ILICONT1` (8), Version (4), erforderliche Featurebits (4; derzeit 0) |
| Metadaten | CBOR mit versionierter Modellabbildung, Dictionary und Transfermetadaten |
| Datenbereich | Je Basket Metadaten, null oder mehr Chunks, Basketende; danach Transferende |
| Verzeichnisse | Unveränderlicher B+-Baum, Überlaufbereiche |
| Optionale räumliche Indizes | Gepackte R-Bäume und Manifest |
| Footer, 40 Bytes | Magic `ILICFOO1` (8), B+-Baum-Wurzel (8), Spatial-Manifest oder 0 (8), Dateilänge (8), CRC32 über erste 32 Bytes (4), Version (4) |

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

Ein gemeinsamer B+-Baum enthält getrennte Schlüsselbereiche. `\0` bezeichnet ein NUL-Trennzeichen; Positionen werden als 20-stellige Dezimalzahlen kodiert, sodass Zeichenkettenvergleich der physischen Reihenfolge entspricht.

| Präfix | Bedeutung |
|---|---|
| `B\0BID` | Basketmetadaten, einschliesslich leerer Baskets |
| `P\0Basketposition` | Basket in ursprünglicher Reihenfolge |
| `O\0TID` | Objektposition: Basket, Chunk, nullbasiertes Objektordinal |
| `C\0Klasse\0Basketposition\0Chunk-ID` | Klassen-Chunks |
| `D\0Basketposition\0Chunk-ID` | Basket-Chunks |
| `T\0Topic\0Basketposition\0…` | Basketmetadaten und Topic-Chunks |
| `N\0Chunk-ID` | Chunk-Verzeichniseintrag mit Offset, gepackter Nutzdatenlänge und Chunk-Header |

`compressedLength` im N-Eintrag ist die gesamte gepackte Chunk-Nutzdatenlänge einschliesslich des kleinen Chunk-Headers, ohne den 16-Byte-Frameheader. Die reine komprimierte Objektsequenz beginnt nach dem Chunk-Header.

Jede Seite enthält eine Anzahl und Schlüssel-Wert-Paare. Ein Feld besteht aus einer 4-Byte-Länge und den Bytes. Länge `-1` bedeutet, dass ein 8-Byte-Offset auf einen Überlauf-Frame folgt. Interne Werte sind Kinder-Offsets; Separatoren sind die kleinsten Schlüssel ihrer Teilbäume. Kinder werden vor ihren Eltern geschrieben. Zielgrösse normaler Seiten: 16 KiB.

Externe Sortierung verwendet begrenzte Runs und höchstens 32 gleichzeitig zusammengeführte Eingabedateien. Überlange einzelne Schlüssel/Werte können die Sortierzielgrösse überschreiten. Duplikate der TID- und BID-Schlüssel führen zum Abbruch. OID-lose Assoziationsinstanzen erhalten keinen erfundenen TID-Schlüssel und bleiben über Klasse/Basket/Topic zugänglich.

## Räumlicher Zugriff

Ein R-Baum wird nach der X-Untergrenze gepackt; bis zu 64 Einträge pro Blatt/Zweig. Blätter speichern konservative XY-Bounding-Boxes und physische Objektadressen. Das Manifest ordnet Klasse und Geometrieattribut einer Wurzel, einem CRS, den Achsen `C1,C2` und der Objektzahl zu.

Kreisbögen werden analytisch umschlossen, ohne Linearisierung. Der Kurvenbaustein von iox-ili prüft die Berechenbarkeit. Orientierung und Zugehörigkeit der vier Achsenextrema werden zusätzlich mit exakten Dezimaloperationen bestimmt; Mittelpunkt und Radius erhalten nach aussen gerundete rationale beziehungsweise Dezimalgrenzen. Koordinatengrenzen werden nach aussen gerundet. Instabile/degenerierte Bögen und Bögen mit explizitem R-Attribut werden derzeit für die Indexierung ausdrücklich abgelehnt; ihre Core-Kodierung bleibt erhalten. Fehlende Geometrien erzeugen keinen Eintrag. Gemischte Basket-Domainzuordnungen werden nicht gemeinsam indexiert. Bei generischen Domainzuordnungen ist zusätzlich eine explizite CRS-Angabe erforderlich.

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

Die Modellskala bleibt in `numericTypes` verfügbar. Die Dezimalvariante speichert trotzdem die tatsächliche Mantisse und Skala jedes Werts. Eine ausschliesslich aus dem Modell abgeleitete Skalierung würde bei ungeprüften Eingaben entweder runden oder einen zusätzlichen Ausnahmefall benötigen. Da die Erstellung keine vollständige Modellvalidierung voraussetzt, bleibt die explizite Skala der robuste erste Messpunkt. Native CBOR-Integer für Mantissen und das Weglassen wiederholter Modellskalen sind weitere Kompressionsoptimierungen; sie sind nicht Bestandteil von Dateiformat 1.

Die Reihenfolge der Modell-/Quellprovenienzlisten kann von der Auflösungsreihenfolge des Compilers abhängen. Sie hat keine Transfersemantik; byteidentische Container über getrennte Erstellungen werden daher noch nicht zugesagt. Der abschliessende Neuaufbau der grossen 256-KiB-Standardvariante ergab identische Daten-/Verzeichnisframes und identische Metadaten nach Sortierung dieser Provenienzlisten.

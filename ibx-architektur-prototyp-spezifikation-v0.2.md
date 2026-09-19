> Historischer Architekturentwurf. Verbindlicher aktueller Stand: [IBX-Format 4](docs/FORMAT.md) und [QGIS-Prototyp](docs/QGIS.md).

# IbxContainer – Architektur und Prototyp-Spezifikation v0.2

**Status:** Entwurf / Prototyp-Spezifikation  
**Version:** 0.2  
**Projekt:** IbxContainer  
**Repository:** `edigonzales/ibx`

---

## 1. Ziel

IbxContainer ist ein experimenteller, cloud-optimierter Datencontainer für INTERLIS-Daten.

Die erste Version soll bewusst **kein allgemeines Abfrage- oder Datenbanksystem** sein. Im Vordergrund stehen fünf Eigenschaften:

> **compact – streamable – chunked – addressable – optionally spatially indexed**

IbxContainer soll damit insbesondere folgende Probleme heutiger XTF-Transfers adressieren:

- relativ grosse Dateigrösse,
- textbasierte Kodierung,
- fehlender direkter Zugriff auf Teile eines Transfers,
- fehlender Random Access auf Topics, Baskets, Klassen und einzelne Objekte,
- fehlender effizienter räumlicher Teilzugriff,
- Notwendigkeit, für kleine Ausschnitte häufig die gesamte Datei zu übertragen.

Die vollständige INTERLIS-Semantik bleibt erhalten. Selektiv gelesene **Fragmente** dürfen jedoch unvollständig und für sich allein nicht modellkonform sein.

---

## 2. Nicht-Ziele der Version 0.2

Folgende Funktionen gehören **nicht** zum Kern dieser Version:

- beliebige Attributfilter,
- sekundäre Attributindizes,
- SQL oder eine SQL-ähnliche Abfragesprache,
- automatische Auflösung oder Traversierung von Assoziationen,
- automatische Nachlieferung referenzierter Objekte,
- vollständige semantische Schliessung eines Ausschnitts,
- Validierung von Teilmengen als eigenständige Transfers,
- Bearbeitung oder Transaktionen innerhalb des Containers,
- Delta- oder Versionsketten,
- verteilte Speicherung über mehrere Containerdateien,
- serverseitige INTERLIS-Abfrage-APIs.

Diese Funktionen können später ergänzt werden, dürfen den Kernentwurf jedoch nicht unnötig verkomplizieren.

---

## 3. Primäre Use Cases

### 3.1 Vollständiger Transfer

Ein vollständiger XTF-Transfer soll verlustfrei in einen IbxContainer überführt und wieder als semantisch gleichwertiger XTF-Transfer ausgegeben werden können.

```text
data.xtf
   │
   ▼
data.ibx
   │
   ▼
roundtrip.xtf
```

Das Ziel ist semantische Gleichheit, nicht Byte-Gleichheit des XML-Dokuments.

### 3.2 Streaming-Verarbeitung

Ein IbxContainer muss sequenziell mit begrenztem Speicher gelesen werden können.

Ein Reader soll Objekte fortlaufend liefern können, ohne die gesamte Datei oder alle Verzeichnisse vollständig in den Speicher laden zu müssen.

```text
File / HTTP stream
        │
        ▼
IbxContainerReader
        │
        ▼
IoxEvent / IomObject
```

### 3.3 Selektiver Zugriff auf Transferteile

Folgende Einheiten sollen ohne vollständigen Download des Containers adressierbar sein:

- Topic,
- Basket,
- Klasse,
- einzelnes Objekt über seine INTERLIS-Identität.

Beispiele:

```text
getTopic("DMAV_Bodenbedeckung_V1_1.Bodenbedeckung")
getBasket("b123")
getClass("DMAV_Bodenbedeckung_V1_1.Bodenbedeckung.BoFlaeche")
getObject("o4711")
```

Das Ergebnis kann mehrere getrennte Bytebereiche des Containers benötigen.

### 3.4 Räumlicher Teilzugriff

Für eine Klasse und ein konkretes Geometrieattribut soll optional ein räumlicher Index vorhanden sein.

```text
querySpatial(
    class = "Model.Topic.BoFlaeche",
    geometryAttribute = "Geometrie",
    bbox = [2600000, 1200000, 2601000, 1201000]
)
```

Der räumliche Index liefert Kandidaten. Die exakte geometrische Prüfung erfolgt auf den geladenen Objekten.

---

## 4. Vollständiger Transfer und Fragment

IbxContainer unterscheidet ausdrücklich zwischen einem **vollständigen Transfer** und einem **Fragment**.

### 4.1 Vollständiger Transfer

Ein vollständiger IbxContainer repräsentiert einen vollständigen INTERLIS-Transfer mit den vorhandenen:

- Modellen,
- Topics,
- Baskets,
- Objekten,
- Strukturen,
- Referenzen,
- Assoziationsinstanzen,
- Geometrien,
- Transfermetadaten.

Für einen vollständigen Container gelten die normalen INTERLIS-Transferregeln.

### 4.2 Fragment

Ein Fragment entsteht durch selektives Lesen, beispielsweise:

```text
eine Klasse
ein Basket
ein einzelnes Objekt
eine räumliche Auswahl
```

Ein Fragment:

- muss die ausgewählten Objekte verlustfrei enthalten,
- muss deren ursprüngliche Basketzugehörigkeit erhalten,
- darf offene Referenzen enthalten,
- darf unvollständige Baskets enthalten,
- darf Kardinalitäten oder Constraints verletzen,
- muss nicht als eigenständiger INTERLIS-Transfer gültig sein.

Beispiel:

```text
Gebaeude g1
   REF Nachfuehrung n17
```

Wenn `n17` nicht Teil der Auswahl ist, bleibt die Referenz erhalten. Das Zielobjekt wird in Version 0.2 nicht automatisch nachgeladen.

---

## 5. Grundarchitektur

Der Container besteht konzeptionell aus:

```text
┌───────────────────────────────────────────────┐
│ Header                                        │
├───────────────────────────────────────────────┤
│ Dictionary / Modell- und Transfermetadaten    │
├───────────────────────────────────────────────┤
│ Directory                                     │
│   - Topics                                    │
│   - Baskets                                   │
│   - Classes                                   │
│   - Objects                                   │
│   - Chunks                                    │
│   - optionale Spatial Indexes                 │
├───────────────────────────────────────────────┤
│ Data Chunk 1                                  │
├───────────────────────────────────────────────┤
│ Data Chunk 2                                  │
├───────────────────────────────────────────────┤
│ ...                                           │
├───────────────────────────────────────────────┤
│ Data Chunk n                                  │
└───────────────────────────────────────────────┘
```

Die konkrete Byte-Reihenfolge ist im Prototyp noch nicht normativ festgelegt.

---

## 6. Chunks als physische Zugriffseinheit

### 6.1 Motivation

Topics, Baskets und Klassen überschneiden sich logisch.

Ein Basket kann Objekte mehrerer Klassen enthalten. Eine Klasse kann in mehreren Baskets vorkommen.

Daher wird keine dieser fachlichen Einheiten direkt als einzige physische Blockstruktur verwendet.

Stattdessen werden **Chunks** eingeführt.

### 6.2 Chunk-Eigenschaften

Ein Chunk enthält Objekte:

- genau eines Topics,
- genau eines Baskets,
- genau einer Klasse.

Beispiel:

```text
Chunk 17
  Topic:   DMAV.Bodenbedeckung
  Basket:  b123
  Class:   BoFlaeche
  Objects: 438
```

Ein weiterer Chunk desselben Baskets kann eine andere Klasse enthalten:

```text
Chunk 18
  Topic:   DMAV.Bodenbedeckung
  Basket:  b123
  Class:   Einzelobjekt
  Objects: 71
```

Dieselbe Klasse kann in weiteren Baskets vorkommen:

```text
Chunk 57
  Topic:   DMAV.Bodenbedeckung
  Basket:  b456
  Class:   BoFlaeche
  Objects: 512
```

### 6.3 Chunk-Grösse

Ein Chunk darf nicht beliebig gross werden.

Die optimale Zielgrösse ist Gegenstand des Prototyps. Zu untersuchen sind beispielsweise:

- 64 KiB,
- 256 KiB,
- 1 MiB,
- 4 MiB.

Zielkonflikt:

- kleinere Chunks ermöglichen präzisere Teilzugriffe,
- grössere Chunks verbessern typischerweise Kompression und sequentielle Verarbeitung.

---

## 7. Directory

Das Directory bildet fachliche Identitäten auf physische Dateibereiche ab.

### 7.1 Chunk Directory

Jeder Chunk besitzt mindestens:

```text
chunkId
topicId
basketId
classId
offset
compressedLength
uncompressedLength
compression
objectCount
```

Optional können zusätzliche Statistiken gespeichert werden.

### 7.2 Topic Directory

```text
Topic A
  → Chunk 1
  → Chunk 2
  → Chunk 7
```

### 7.3 Basket Directory

```text
Basket b123
  → Chunk 17
  → Chunk 18
  → Chunk 19
```

Ein `getBasket()` liefert alle Objekte dieser Chunks.

### 7.4 Class Directory

```text
Class BoFlaeche
  → Chunk 17
  → Chunk 57
  → Chunk 81
```

Ein `getClass()` darf Objekte aus mehreren Baskets liefern. Die ursprüngliche Basket-ID jedes Objekts bleibt erhalten.

### 7.5 Object Directory

Der Zugriff auf ein einzelnes Objekt gehört zum Core.

Das Object Directory bildet daher die INTERLIS-Objektidentität auf die physische Position ab.

```text
TID "o4711"
  → Chunk 57
  → Object 183
```

Der genaue Indexaufbau ist noch offen. Er muss auch bei sehr grossen Datenbeständen seitenweise beziehungsweise teilweise lesbar sein.

---

## 8. Dictionary

Wiederkehrende Bezeichnungen sollen nicht in jedem Objekt vollständig gespeichert werden.

Das Container-Header-Dictionary kann beispielsweise IDs vergeben für:

```text
Models
Topics
Classes
Attributes
Roles
Enumerations
Geometry attributes
```

Beispiel:

```text
class 17 = DMAV_Bodenbedeckung_V1_1.Bodenbedeckung.BoFlaeche

attribute 1 = Geometrie
attribute 2 = Qualitaet
attribute 3 = Entstehung
```

Ein Objekt muss dann nicht lange qualifizierte Namen wiederholen.

Das Dictionary ist Bestandteil des Core-Formats und kein optionaler Index.

---

## 9. Objektkodierung

Die Objektkodierung muss:

- verlustfrei sein,
- INTERLIS-Typinformationen erhalten,
- Strukturen erhalten,
- BAG- und LIST-Reihenfolgen erhalten,
- Referenzen erhalten,
- Assoziationsinstanzen erhalten,
- Geometrien verlustfrei erhalten,
- streamingfähig dekodierbar sein.

### 9.1 Arbeitshypothese: CBOR

Für den Prototyp wird CBOR als erste Kodierungsvariante untersucht.

Mögliche Eigenschaften:

- kompakte binäre Darstellung,
- native Zahlen und Bytefolgen,
- Arrays und Maps,
- verschachtelte Strukturen,
- sequenzielles Decoding,
- keine XML-Tag-Wiederholung.

CBOR ist in Version 0.2 eine **Prototypentscheidung**, noch keine normative Festlegung.

### 9.2 CBOR Sequence

Innerhalb eines Chunks kann eine Folge unabhängig dekodierbarer Objekte verwendet werden.

```text
Chunk Header
Object 1
Object 2
Object 3
...
Object n
```

Eine mögliche konkrete Umsetzung ist CBOR Sequence.

### 9.3 Zahlen

Die Kodierung muss numerische INTERLIS-Werte ohne unbeabsichtigten Präzisionsverlust erhalten.

Insbesondere darf nicht pauschal jeder numerische Wert in `double` umgewandelt werden.

Im Prototyp sollen mindestens untersucht werden:

- Integer,
- skalierte Integer,
- Decimal Fraction / Mantisse + Exponent.

---

## 10. Kompression

### 10.1 Kompression pro Chunk

Die gesamte Containerdatei darf nicht als ein einziger Kompressionsstrom behandelt werden.

Stattdessen wird jeder Chunk separat komprimiert:

```text
Chunk 1 → compressed
Chunk 2 → compressed
Chunk 3 → compressed
```

Dadurch bleibt Random Access möglich.

### 10.2 Arbeitshypothese: Zstandard

Für den Prototyp soll Zstandard als erste Kompressionsvariante untersucht werden.

Zu messen sind:

- Kompressionsrate,
- Dekompressionsgeschwindigkeit,
- Einfluss unterschiedlicher Chunk-Grössen,
- Vergleich mit ZIP/Deflate und XTF.

### 10.3 Dateigrössenvergleich

Die Core-Datei wird **ohne optionale fachliche oder räumliche Indizes** mit folgenden Varianten verglichen:

```text
data.xtf
data.xtf.zip
data.xtf.zst
data.ibx
```

Ein optional räumlich indexierter Container wird separat betrachtet:

```text
data.ibx
data-spatial.ibx
```

Damit werden Core-Format und Index-Overhead nicht vermischt.

---

## 11. Streaming

### 11.1 Reader

Ein vollständiger Container muss sequenziell gelesen werden können.

Der Reader darf dabei nicht voraussetzen, dass der gesamte Container im Speicher vorhanden ist.

```text
while (reader.hasNext()) {
    object = reader.next();
}
```

### 11.2 Writer

Der Writer muss in Version 0.2 **nicht zwingend One-Pass-Streaming auf stdout** unterstützen.

Er darf:

1. Eingabedaten analysieren,
2. temporäre Chunks erzeugen,
3. Directory und Dictionary aufbauen,
4. die finale Datei schreiben.

Damit wird der Dateiaufbau nicht unnötig durch eine strengere Streaming-Vorgabe eingeschränkt.

---

## 12. Räumlicher Index

### 12.1 Optional

Ein räumlicher Index ist **kein Bestandteil des minimalen Core-Containers**.

Der Container muss ohne räumlichen Index vollständig lesbar und streambar bleiben.

### 12.2 Pro Klasse und Geometrieattribut

Ein Spatial Index gehört immer zu genau:

```text
Class + Geometry Attribute
```

Bei mehreren Geometrieattributen einer Klasse können mehrere räumliche Indizes existieren.

### 12.3 Anfrage

Eine räumliche Anfrage besteht mindestens aus:

```text
class
geometryAttribute
boundingBox
```

### 12.4 Kandidaten und exakte Prüfung

```text
Query BBOX
   ↓
Spatial Index
   ↓
Candidate Object IDs
   ↓
betroffene Chunks lesen
   ↓
Geometrien dekodieren
   ↓
exakte Intersects-Prüfung
```

Ein Bounding-Box-Treffer ist somit nicht automatisch ein geometrischer Treffer.

### 12.5 Noch keine Beziehungserweiterung

Das Ergebnis enthält nur die räumlich ausgewählten Objekte.

Referenzierte oder referenzierende Objekte werden nicht automatisch ergänzt.

---

## 13. INTERLIS-Semantik

### 13.1 Modelle

Der Container muss eindeutig dokumentieren, welche INTERLIS-Modelle für den Transfer relevant sind.

Zu speichern sind mindestens:

```text
modelName
modelVersion
modelIssuer / modelUri, soweit vorhanden
```

Optional kann das eigentliche INTERLIS-Modell eingebettet oder über einen Digest referenziert werden.

Die genaue Strategie ist im Prototyp zu evaluieren.

### 13.2 Baskets

Folgende Basket-Informationen müssen erhalten bleiben:

- BID,
- Topic,
- Transferart beziehungsweise Zustand, soweit im Ausgangstransfer vorhanden,
- weitere normative Basket-Metadaten.

Ein vollständig gelesener Basket muss semantisch dem ursprünglichen Basket entsprechen.

### 13.3 Objektidentität

INTERLIS-Identitäten dürfen nicht durch interne Record- oder Chunk-IDs ersetzt werden.

```text
internal object id != INTERLIS TID
```

### 13.4 Strukturen

Strukturen gehören logisch zum Hauptobjekt.

Wird ein vollständiges Objekt gelesen, werden seine Strukturen vollständig mitgeliefert.

LIST-Reihenfolgen müssen erhalten bleiben.

### 13.5 Referenzen und Assoziationen

Referenzen und Assoziationsinstanzen müssen im vollständigen Container verlustfrei erhalten bleiben.

Version 0.2 verlangt jedoch **keine automatische Navigation über diese Beziehungen**.

### 13.6 Geometrien

Geometrien müssen so kodiert werden, dass die für den unterstützten INTERLIS-Umfang erforderliche Semantik nicht verloren geht.

Insbesondere dürfen Kreisbögen oder andere relevante Liniensegmente nicht stillschweigend linearisiert werden.

Die genaue binäre Geometriekodierung ist Teil des Prototyps.

---

## 14. HTTP Range Access

Ein zentraler Use Case ist das Lesen eines entfernten Containers über statisches HTTP.

Der Server muss das Containerformat nicht kennen. Er muss lediglich Byte-Range-Zugriffe unterstützen.

```http
GET /data.ibx
Range: bytes=1835008-1900543
```

### 14.1 Ziele

Über HTTP sollen insbesondere möglich sein:

- Directory lesen,
- Topic laden,
- Basket laden,
- Klasse laden,
- Objekt laden,
- räumlichen Index teilweise lesen,
- benötigte Chunks laden.

### 14.2 Unveränderlicher Dateistand

Alle Teilzugriffe innerhalb einer Abfrage müssen denselben Containerstand betreffen.

Geeignete Mechanismen sind beispielsweise:

- unveränderliche Versions-URLs,
- ETag,
- bedingte Range Requests.

### 14.3 Kein stiller Full Download

Ein Remote Reader muss erkennen können, wenn ein Server Range Requests nicht unterstützt und stattdessen die gesamte Datei liefert.

Dieses Verhalten muss sichtbar sein.

---

## 15. API des Prototyps

Eine erste Java-API könnte ungefähr folgende Operationen anbieten:

```java
IbxContainer open(Path path);
IbxContainer open(URI uri);

Stream<IomObject> streamAll();
Stream<IomObject> getTopic(String topicName);
Stream<IomObject> getBasket(String bid);
Stream<IomObject> getClass(String className);
Optional<IomObject> getObject(String oid);

Stream<IomObject> querySpatial(
    String className,
    String geometryAttribute,
    BoundingBox bbox
);
```

Die genaue API ist nicht Teil des Dateiformatstandards. Sie dient lediglich dem Prototyp.

---

## 16. CLI des Prototyps

Mögliche Befehle:

```bash
ibx create data.xtf data.ibx
```

```bash
ibx info data.ibx
```

```bash
ibx export data.ibx data.xtf
```

```bash
ibx get-basket data.ibx b123
```

```bash
ibx get-class \
  data.ibx \
  DMAV_Bodenbedeckung_V1_1.Bodenbedeckung.BoFlaeche
```

```bash
ibx get-object data.ibx o4711
```

```bash
ibx bbox \
  data.ibx \
  DMAV_Bodenbedeckung_V1_1.Bodenbedeckung.BoFlaeche \
  Geometrie \
  2600000 1200000 2601000 1201000
```

Für Remote-Zugriff:

```bash
ibx get-object \
  https://example.org/data.ibx \
  o4711
```

---

## 17. Referenztests

### 17.1 Roundtrip

```text
XTF
 ↓
IbxContainer
 ↓
XTF
```

Zu vergleichen sind mindestens:

- Modelle,
- Topics,
- Baskets,
- TIDs,
- Klassen,
- Attribute,
- Strukturen,
- LIST-Reihenfolgen,
- Referenzen,
- Assoziationen,
- Geometrien.

### 17.2 Streaming

Der vollständige Container muss mit begrenztem Speicher gelesen werden können.

Gemessen werden:

- Objects/s,
- MB/s,
- Peak Heap,
- Zeit bis zum ersten Objekt.

### 17.3 Topic-Zugriff

Für ein Topic werden nur dessen benötigte Chunks gelesen.

Erwartete Objekte müssen identisch mit einem vollständigen Scan plus Topic-Filter sein.

### 17.4 Basket-Zugriff

`getBasket(bid)` muss exakt alle Objekte dieses Baskets liefern.

### 17.5 Class-Zugriff

`getClass(className)` muss alle Objekte dieser Klasse über alle Baskets liefern.

### 17.6 Object-Zugriff

`getObject(oid)` muss genau das bezeichnete Objekt liefern.

Dazu wird gemessen:

- Anzahl gelesener Directory-Seiten,
- Anzahl gelesener Chunks,
- übertragene Bytes bei Remote-Zugriff.

### 17.7 Spatial-Zugriff

Für eine BBOX-Abfrage werden die Ergebnisse mit einer vollständigen Referenzauswertung verglichen.

Gemessen werden:

- gelesene Indexbytes,
- gelesene Chunkbytes,
- Anzahl Kandidaten,
- Anzahl tatsächlicher Treffer,
- HTTP Requests,
- Gesamtdauer.

---

## 18. Benchmark

Der erste Benchmark soll mit mindestens einem realistischen DMAV-Datensatz durchgeführt werden.

Zu vergleichen sind:

```text
XTF
XTF.zip
XTF.zst
IbxContainer Core
IbxContainer Core + Spatial Index
```

### 18.1 Dateigrösse

Gemessen wird:

```text
Bytes absolut
Bytes pro Objekt
Index-Overhead
```

Die Core-Dateigrösse muss separat vom Spatial-Index-Overhead ausgewiesen werden.

### 18.2 Full Scan

Gemessen werden:

```text
MB/s
Objects/s
Peak RAM
CPU time
Wall clock time
```

### 18.3 Selective Access

Mindestens:

```text
ein Basket
eine Klasse
ein Objekt
```

Gemessen werden lokal und remote:

```text
Bytes read
HTTP requests
Time to first object
Total time
```

### 18.4 Spatial Access

Mindestens drei Selektivitäten:

```text
kleiner Ausschnitt
mittlerer Ausschnitt
grosser Ausschnitt
```

---

## 19. Erfolgskriterien des Prototyps

Der Prototyp gilt als erfolgreich, wenn folgende Punkte gezeigt werden können:

1. Ein vollständiger XTF-Transfer kann semantisch verlustfrei in IbxContainer und zurück überführt werden.
2. IbxContainer ist mit begrenztem Speicher vollständig streambar.
3. Topics, Baskets, Klassen und einzelne Objekte können ohne vollständigen Dateidownload gelesen werden.
4. Ein optionaler Spatial Index ermöglicht BBOX-Abfragen auf einer konkreten Klasse und einem Geometrieattribut.
5. Remote-Zugriff funktioniert über HTTP Range Requests.
6. Core-Container und Index-Overhead können getrennt gemessen werden.
7. Die Dateigrösse und Performance sind reproduzierbar gegen XTF, XTF.zip und XTF.zst benchmarkbar.

Ein festes Ziel wie

```text
IbxContainer muss immer 30 % kleiner als XTF.zip sein
```

wird in Version 0.2 bewusst **nicht** vorgegeben.

Die Benchmarks sollen zunächst zeigen, wo die tatsächlichen Vorteile liegen.

---

## 20. Entwicklungsmeilensteine

### M1 – Logisches Objektformat

- INTERLIS → interne Objektkodierung
- interne Objektkodierung → INTERLIS
- Roundtrip kleiner Testmodelle
- CBOR-Prototyp

### M2 – Chunked Core Container

- Chunk Header
- Dictionary
- Chunk Directory
- per-Chunk-Kompression
- vollständiger sequentieller Reader

### M3 – Selektiver Zugriff

- Topic Directory
- Basket Directory
- Class Directory
- Object Directory
- lokale Teilzugriffe

### M4 – HTTP Range Reader

- Remote Directory Access
- Chunk Range Requests
- Cache
- Messung übertragener Bytes

### M5 – Spatial Index

- Index pro Klasse und Geometrieattribut
- BBOX Candidate Search
- exakte geometrische Nachprüfung

### M6 – DMAV Benchmark

- realer DMAV-Bestand
- Grössenvergleich
- Streaming-Benchmark
- Selective-Access-Benchmark
- Spatial-Benchmark
- Dokumentation der Ergebnisse

---

## 21. Mögliche spätere Erweiterungen

Nicht Teil von Version 0.2:

```text
Secondary Attribute Indexes
Relationship Indexes
Relationship Traversal
Query Planner
Combined Attribute + Spatial Filters
Full-text Index
Statistics / Min-Max metadata
Validation-aware subsets
Semantic closure of fragments
Column projections
Server-side APIs
Delta containers
Mutable containers
```

Diese Erweiterungen sollen auf dem Core-Format aufbauen können, ohne dessen Grundstruktur zu ersetzen.

---

## 22. Offene Fragen für den Prototyp

Folgende Punkte sind ausdrücklich noch nicht festgelegt:

1. endgültige Container-Endung (`.ibx`, `.ibx`, andere),
2. endgültige Objektkodierung,
3. konkrete CBOR-Darstellung,
4. Geometriekodierung,
5. exakte Chunk-Zielgrösse,
6. Aufbau des Object Directory,
7. Aufbau des räumlichen Index,
8. Position von Directory und Footer innerhalb der Datei,
9. Kompressionsverfahren und Parameter,
10. Einbettung oder Referenzierung der INTERLIS-Modelle,
11. Verhalten bei ungültigen oder nicht vollständig indexierbaren Objekten,
12. Behandlung sehr grosser Einzelobjekte,
13. Umgang mit doppelten TIDs in fehlerhaften Eingangsdaten.

Diese Fragen werden durch Prototypen und Benchmarks entschieden.

---

## 23. Leitprinzip

Die Version 0.2 verfolgt bewusst folgende Reihenfolge:

```text
1. INTERLIS verlustfrei kodieren
2. kleiner und schneller als XTF werden
3. Streaming erhalten
4. fachliche Einheiten adressierbar machen
5. räumliche Teilabfragen ermöglichen
6. erst danach komplexe Query-Funktionalität hinzufügen
```

Der erste IbxContainer soll damit kein Ersatz für eine Datenbank sein.

Er soll zunächst ein **besser adressierbares, kompakteres und cloud-freundlicheres INTERLIS-Transferformat** sein.

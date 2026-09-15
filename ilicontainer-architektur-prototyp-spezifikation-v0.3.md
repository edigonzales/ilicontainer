# IliContainer – Architektur und Prototyp-Spezifikation v0.3

**Status:** Entwurf / Prototyp-Spezifikation  
**Version:** 0.3  
**Projekt:** IliContainer  
**Repository:** `edigonzales/ilicontainer`

---

## 1. Ziel

IliContainer ist ein experimenteller, cloud-optimierter Datencontainer für INTERLIS-Daten.

Die erste Version soll bewusst **kein allgemeines Abfrage- oder Datenbanksystem** sein. Im Vordergrund stehen fünf Eigenschaften:

> **compact – streamable – chunked – addressable – optionally spatially indexed**

IliContainer soll damit insbesondere folgende Probleme heutiger XTF-Transfers adressieren:

- relativ grosse Dateigrösse,
- textbasierte Kodierung,
- fehlender direkter Zugriff auf Teile eines Transfers,
- fehlender Random Access auf Topics, Baskets, Klassen und einzelne Objekte,
- fehlender effizienter räumlicher Teilzugriff,
- Notwendigkeit, für kleine Ausschnitte häufig die gesamte Datei zu übertragen.

Version 0.3 unterstützt ausschliesslich **INTERLIS 2.4 und die Transferart FULL**. Der Writer muss andere INTERLIS-/XTF-Versionen sowie INITIAL- und UPDATE-Transfers ausdrücklich mit einer Diagnose ablehnen; eine stillschweigende Konvertierung ist nicht erlaubt.

Innerhalb dieses Umfangs bleibt die vollständige INTERLIS-Semantik erhalten. Selektiv gelesene **Fragmente** dürfen jedoch unvollständig und für sich allein nicht modellkonform sein. Nicht unterstützte Inhalte dürfen nicht stillschweigend weggelassen oder vereinfacht werden.

---

## 2. Nicht-Ziele der Version 0.3

Folgende Funktionen gehören **nicht** zum Kern dieser Version:

- andere INTERLIS-/XTF-Versionen als 2.4 und die Transferarten INITIAL/UPDATE,
- exakte geometrische Intersects-Prüfung und automatische Koordinatentransformation,
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

Ein vollständiger INTERLIS-2.4-FULL-Transfer soll verlustfrei in einen IliContainer überführt und wieder als semantisch gleichwertiger XTF-Transfer ausgegeben werden können.

```text
data.xtf
   │
   ▼
data.ilic
   │
   ▼
roundtrip.xtf
```

Das Ziel ist semantische Gleichheit, nicht Byte-Gleichheit des XML-Dokuments.

### 3.2 Streaming-Verarbeitung

Ein IliContainer muss sequenziell mit begrenztem Speicher gelesen werden können.

Ein Reader soll Objekte fortlaufend liefern können, ohne die gesamte Datei oder alle Verzeichnisse vollständig in den Speicher laden zu müssen.

```text
File / HTTP stream
        │
        ▼
IliContainerReader
        │
        ▼
IoxEvent (mit Transfer- und Basketkontext)
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
querySpatialCandidates(
    class = "Model.Topic.BoFlaeche",
    geometryAttribute = "Geometrie",
    bbox = [2600000, 1200000, 2601000, 1201000]
)
```

Der räumliche Index liefert vollständige Objekte mit Basketkontext, deren zweidimensionale Geometrie-Bounding-Box die Suchbox überlappt oder berührt. Zusätzliche Kandidaten gegenüber einer geometrischen Intersects-Prüfung sind erlaubt; tatsächlich schneidende Geometrien dürfen nicht verloren gehen. Eine exakte geometrische Nachprüfung ist ein späterer Ausbauschritt.

---

## 4. Vollständiger Transfer und Fragment

IliContainer unterscheidet ausdrücklich zwischen einem **vollständigen Transfer** und einem **Fragment**.

### 4.1 Vollständiger Transfer

Ein vollständiger IliContainer repräsentiert einen vollständigen INTERLIS-Transfer mit den vorhandenen:

- Modellen,
- Topics,
- Baskets,
- Objekten,
- Strukturen,
- Referenzen,
- Assoziationsinstanzen,
- Geometrien,
- Transfermetadaten.

Für einen vollständigen Container gelten die INTERLIS-2.4-Transferregeln für FULL. Transfermetadaten, leere Baskets und Transfers ohne Objekte müssen erhalten bleiben.

Die ursprüngliche Basketreihenfolge bleibt erhalten. Objekte innerhalb eines Baskets dürfen umgeordnet werden. Reihenfolgen innerhalb von LISTs und geordneten Beziehungen bleiben erhalten.

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
- muss deren ursprünglichen Basketkontext einschliesslich Basketmetadaten erhalten,
- muss im API-Ergebnis und bei einem Export ausdrücklich als Fragment gekennzeichnet sein,
- darf offene Referenzen enthalten,
- darf unvollständige Baskets enthalten,
- darf Kardinalitäten oder Constraints verletzen,
- muss nicht als eigenständiger INTERLIS-Transfer gültig sein.

Beispiel:

```text
Gebaeude g1
   REF Nachfuehrung n17
```

Wenn `n17` nicht Teil der Auswahl ist, bleibt die Referenz erhalten. Das Zielobjekt wird in Version 0.3 nicht automatisch nachgeladen.

Jedes ausgewählte Objekt enthält seine Strukturen vollständig. Ein Fragmentexport darf nicht als vollständiger, modellkonformer Transfer ausgewiesen werden. Die Zusage eines semantisch gleichwertigen XTF-Roundtrips gilt für den vollständigen Export. Ein selektierter leerer Basket bleibt als Basketkontext auch ohne Objekt erhalten.

---

## 5. Grundarchitektur

Für den Prototyp gilt folgende Abschnittsreihenfolge:

```text
Header
Dictionary / Modell- und Transfermetadaten
Basket 1: Metadaten → Daten-Chunks → Basketende
Basket 2: Metadaten → Daten-Chunks → Basketende
...
Transferende
Verzeichnisse (Topics, Baskets, Classes, Objects, Chunks)
Optionale Spatial-Indizes
Footer mit Einstiegspunkten in die Verzeichnisse und Indizes
```

Basketabschnitte stehen in ursprünglicher Basketreihenfolge. Ein leerer Basket enthält Metadaten und Basketende, aber keine Daten-Chunks. Auch ein Transfer ohne Baskets ist darstellbar.

Der sequenzielle Reader rekonstruiert Transfer- und Basketgrenzen direkt aus dem Datenbereich. Er muss vor dem ersten Objekt weder das Object Directory noch räumliche Indizes lesen. Dictionary und notwendige Metadaten stehen vor ihrer ersten Verwendung bereit.

Der selektive Reader erschliesst die Verzeichnisse über den Footer und lädt nur benötigte Metadaten, Indexseiten und Chunks. Grosse Verzeichnisse und räumliche Indizes müssen seitenweise lesbar sein.

Die konkrete Bytekodierung der Abschnitte bleibt eine Prototypentscheidung; diese Streaming- und Zugriffsgarantien gelten unabhängig davon.

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
- genau einer konkreten Klasse.

Ein Chunk ist mit seinem Header, dem bereits verfügbaren Dictionary und dem Basketkontext unabhängig dekodierbar und dekomprimierbar. Er darf keine vorherigen Daten-Chunks zum Dekodieren benötigen.

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

Die Chunk-Zielgrösse bezieht sich auf die **unkomprimierten Nutzdaten**. Reguläre Chunks werden an Objektgrenzen begrenzt.

Ein Objekt einschliesslich seiner Strukturen wird niemals über mehrere Chunks verteilt. Überschreitet ein Einzelobjekt die Zielgrösse, erhält es einen eigenen übergrossen Chunk. Die Speicherzusage des Readers berücksichtigt dieses grösste Objekt beziehungsweise diesen grössten Chunk.

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

Das Directory bildet fachliche Identitäten auf physische Dateibereiche ab. Grosse Verzeichnisse müssen seitenweise lesbar sein; ein Zugriff darf nicht das vollständige Object Directory im Speicher voraussetzen.

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

Ein `getBasket()` liefert den Basketkontext und alle Objekte dieser Chunks als Fragment.

Für jeden Basket werden BID, Topic, ursprüngliche Position, Basketmetadaten und der Zugriff auf seinen Basketabschnitt unabhängig von der Chunkliste erfasst. Ein leerer Basket besitzt einen Eintrag mit leerer Chunkliste und bleibt auch über das Topic Directory auffindbar.

### 7.4 Class Directory

```text
Class BoFlaeche
  → Chunk 17
  → Chunk 57
  → Chunk 81
```

Ein `getClass()` liefert Objekte der angegebenen konkreten Klasse aus gegebenenfalls mehreren Baskets. Der ursprüngliche Basketkontext jedes Objekts bleibt erhalten.

### 7.5 Object Directory

Der Zugriff auf ein einzelnes Objekt gehört zum Core.

Das Object Directory bildet daher die INTERLIS-Objektidentität auf die physische Position ab.

```text
TID "o4711"
  → Chunk 57
  → Object 183
```

Der genaue Indexaufbau ist noch offen. Er muss auch bei sehr grossen Datenbeständen seitenweise beziehungsweise teilweise lesbar sein.

Ein erfolgreicher Einzelobjektzugriff liest und dekomprimiert höchstens einen Daten-Chunk zusätzlich zu benötigten Metadaten- und Indexseiten. Die Objektposition innerhalb einer Sequenz kann ein Dekodieren vorheriger Objekte desselben Chunks erfordern; eine zusätzliche Offsettabelle bleibt eine Optimierungsoption.

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

Das Dictionary ist Bestandteil des Core-Formats und kein optionaler Index. Es enthält zusammen mit den gespeicherten Metadaten alle Informationen zur Rekonstruktion der unterstützten Transferinhalte.

Lesen, Selektieren und Exportieren müssen ohne Modellserverzugriff möglich sein. Die Rekonstruktion darf nicht von einem nachträglichen Download externer Modelle abhängen.

---

## 9. Objektkodierung

Die Objektkodierung muss:

- verlustfrei sein,
- INTERLIS-Typinformationen erhalten,
- Strukturen erhalten,
- BAG- und LIST-Reihenfolgen sowie die Reihenfolge geordneter Beziehungen erhalten,
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

CBOR ist in Version 0.3 eine **Prototypentscheidung**, noch keine normative Festlegung.

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
data.ilic
```

Ein optional räumlich indexierter Container wird separat betrachtet:

```text
data.ilic
data-spatial.ilic
```

Damit werden Core-Format und Index-Overhead nicht vermischt.

---

## 11. Streaming

### 11.1 Reader

Ein vollständiger Container muss sequenziell als IOX-Eventfolge gelesen werden können:

```text
StartTransferEvent
  StartBasketEvent
    ObjectEvent ...
  EndBasketEvent
  ...
EndTransferEvent
```

Transfer- und Basketmetadaten sowie leere Baskets müssen auch ohne Objekt-Events erhalten bleiben. Der Reader benötigt vor und während der Objektausgabe weder das Object Directory noch die Spatial-Indizes.

Der Speicherbedarf darf vom Dictionary, vom grössten Objekt beziehungsweise Chunk und von begrenzten Caches abhängen, aber nicht von der Gesamtzahl der Objekte. Basketmetadaten werden beim sequenziellen Lesen basketweise verarbeitet; nicht alle Baskets müssen gleichzeitig im Speicher liegen. Ein sequenzieller HTTP-Stream benötigt keinen Range-Zugriff.

### 11.2 Writer

Der Writer muss in Version 0.3 **nicht zwingend One-Pass-Streaming auf stdout** unterstützen.

Er darf:

1. Eingabedaten analysieren und den unterstützten Versions-/Transferumfang prüfen,
2. temporäre Chunks erzeugen,
3. Directory und Dictionary aufbauen,
4. die finale Datei im Layout aus Kapitel 5 schreiben.

Damit wird der Dateiaufbau nicht unnötig durch eine strengere Streaming-Vorgabe eingeschränkt.

---

## 12. Räumlicher Index

### 12.1 Optional

Ein räumlicher Index ist **kein Bestandteil des minimalen Core-Containers**.

Der Container muss ohne räumlichen Index vollständig lesbar und streambar bleiben.

### 12.2 Pro Klasse und Geometrieattribut

Ein Spatial Index gehört immer zu genau einer konkreten Klasse und einem Geometrieattribut. Bei mehreren Geometrieattributen einer Klasse können mehrere Indizes existieren.

Der Index dokumentiert Koordinatensystem und Achsenreihenfolge eindeutig. Eine gemeinsame Indexierung unterschiedlicher oder uneindeutiger Koordinatensysteme ist in Version 0.3 nicht vorgesehen.

### 12.3 Anfrage

Eine räumliche Anfrage besteht aus:

```text
class
geometryAttribute
boundingBox = [minX, minY, maxX, maxY]
```

Die Suche erfolgt zweidimensional im dokumentierten Koordinatensystem und in der Achsenreihenfolge des indexierten Attributs. Eine automatische Koordinatentransformation findet nicht statt. Höhen bleiben in den Objekten erhalten, werden für die Suche aber ignoriert.

### 12.4 Kandidatenvertrag

```text
Query BBOX
   ↓
Spatial Index seitenweise durchsuchen
   ↓
Objektkandidaten bestimmen
   ↓
betroffene Chunks lesen und Objekte dekodieren
   ↓
vollständige Kandidatenobjekte mit Basketkontext als Fragment liefern
```

`querySpatialCandidates()` liefert diejenigen Objekte, deren Geometrie-Bounding-Box die Suchbox überlappt oder berührt. Randberührungen zählen als Treffer. Interne Indexseiten können gröbere Kandidaten liefern; vor der Rückgabe ist das Bounding-Box-Kriterium auf Objektebene sicherzustellen.

Die Bounding Box muss die gesamte Geometrie einschliesslich Kreisbögen umschliessen. Tatsächlich schneidende Geometrien dürfen nicht durch den Index verloren gehen. Zusätzliche Kandidaten gegenüber einer exakten geometrischen Intersects-Prüfung sind erlaubt.

Eine exakte geometrische Nachprüfung gehört nicht zu Version 0.3. Sie kann später als separater Schritt ergänzt werden.

### 12.5 Fehlende Geometrien und Fehlerfälle

- Eine fehlende Geometrie ergibt keinen räumlichen Kandidaten.
- Ein fehlender Index führt zu einem expliziten Fehler; es gibt keinen automatischen vollständigen Scan.
- Bei nicht zuverlässig indexierbaren Geometrien oder uneindeutigem Koordinatensystem wird die betreffende Indexerstellung mit Diagnose abgebrochen. Problematische Objekte dürfen nicht stillschweigend ausgelassen werden.
- Ein unvollständiger Index darf nicht als verwendbar ausgewiesen werden. Der Core-Container bleibt unabhängig von der optionalen Indexerstellung nutzbar, sofern seine Inhalte verlustfrei kodiert werden können.

### 12.6 Noch keine Beziehungserweiterung

Das Ergebnis enthält nur die räumlichen Kandidatenobjekte, jeweils vollständig mit Strukturen und ursprünglichem Basketkontext. Referenzierte oder referenzierende Objekte werden nicht automatisch ergänzt.

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

Die genaue Einbettungs- oder Referenzierungsstrategie ist im Prototyp zu evaluieren. Unabhängig davon müssen Lesen, Selektieren und Exportieren ohne Modellserverzugriff funktionieren. Eine separate Modellvalidierung darf zusätzliche Modelle benötigen.

### 13.2 Baskets

Folgende Basket-Informationen müssen erhalten bleiben:

- BID,
- Topic,
- Transferart FULL und die im unterstützten Ausgangstransfer vorhandenen Metadaten,
- weitere normative Basket-Metadaten.

Ein vollständig gelesener Basket muss semantisch dem ursprünglichen Basket entsprechen, auch wenn er leer ist. Basketmetadaten dürfen nicht ausschliesslich aus vorhandenen Objekten oder Chunks abgeleitet werden. Die ursprüngliche Basketreihenfolge bleibt erhalten.

### 13.3 Objektidentität

INTERLIS-Identitäten dürfen nicht durch interne Record- oder Chunk-IDs ersetzt werden.

```text
internal object id != INTERLIS TID
```

### 13.4 Strukturen

Strukturen gehören logisch zum Hauptobjekt.

Wird ein vollständiges Objekt gelesen, werden seine Strukturen vollständig mitgeliefert.

LIST-Reihenfolgen müssen erhalten bleiben. Eine zulässige Umordnung der Hauptobjekte innerhalb eines Baskets darf diese Reihenfolgen nicht verändern.

### 13.5 Referenzen und Assoziationen

Referenzen und Assoziationsinstanzen einschliesslich geordneter Beziehungen müssen im vollständigen Container verlustfrei erhalten bleiben.

Version 0.3 verlangt jedoch **keine automatische Navigation über diese Beziehungen**.

### 13.6 Geometrien

Geometrien müssen so kodiert werden, dass die für INTERLIS 2.4 FULL erforderliche Semantik nicht verloren geht. Die zweidimensionale Kandidatensuche schränkt die verlustfreie Speicherung der Geometrie nicht ein.

Insbesondere dürfen Kreisbögen oder andere relevante Liniensegmente nicht stillschweigend linearisiert werden.

Die genaue binäre Geometriekodierung ist Teil des Prototyps.

---

## 14. HTTP Range Access

Ein zentraler Use Case ist das Lesen eines entfernten Containers über statisches HTTP.

Der Server muss das Containerformat nicht kennen. Er muss lediglich Byte-Range-Zugriffe unterstützen.

```http
GET /data.ilic
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

Ändert sich der Dateistand während einer Auswahl oder kann ein einheitlicher Stand nicht sichergestellt werden, bricht der selektive Reader mit einer verständlichen Fehlermeldung ab. Ergebnisse verschiedener Containerstände dürfen nicht vermischt werden.

### 14.3 Kein stiller Full Download

Ein Remote Reader muss erkennen können, wenn ein Server Range Requests nicht unterstützt und stattdessen die gesamte Datei liefert.

Der selektive Reader bricht in diesem Fall standardmässig mit einer verständlichen Fehlermeldung ab und übernimmt die Vollantwort nicht stillschweigend als Download. Ein vollständiger Download ist nur nach ausdrücklicher Freigabe durch den Aufrufer erlaubt. Diese Freigabe hebt die Anforderung eines einheitlichen Containerstands nicht auf.

---

## 15. API des Prototyps

### 15.1 Verbindlicher Technologie-Stack

Der Prototyp wird in **Java** implementiert. Für den gesamten Java-Quellcode einschliesslich Tests und Beispielen ist **Java-8-kompatible Syntax** vorgeschrieben. Neuere Sprachmerkmale wie Records, `var`, Text Blocks oder Switch Expressions dürfen nicht verwendet werden. Datenklassen werden als gewöhnliche Java-Klassen mit Konstruktoren und Zugriffsmethoden umgesetzt.

Als Buildsystem wird **Gradle mit Groovy DSL** verwendet (`build.gradle` und `settings.gradle`, keine Kotlin DSL). Ein Gradle Wrapper und festgelegte Abhängigkeitsversionen machen den Build reproduzierbar. Die Java-Kompilierung muss das Sprachlevel Java 8 erzwingen.

Für die INTERLIS-Verarbeitung sind die bestehenden Bibliotheken zu verwenden:

- **iox-ili** für das Lesen und Schreiben von INTERLIS-2.4-XTF-Transfers,
- **iox-api / IOM** für IOX-Events und `IomObject` als Objektmodell,
- **ili2c** für das Kompilieren und Auswerten der INTERLIS-Modelle, soweit bei der Erstellung des Containers Modellinformationen benötigt werden.

Weitere passende Bibliotheken aus dem INTERLIS-Ökosystem können ergänzend verwendet werden. Ein eigener XTF-Parser oder INTERLIS-Modellcompiler ist nicht vorgesehen. Die Anforderung, fertige Container ohne Modellserverzugriff lesen, selektieren und exportieren zu können, bleibt bestehen.

Die Syntaxvorgabe ist von der Laufzeitumgebung zu unterscheiden: Sie legt allein noch keine Ausführbarkeit unter einer Java-8-JVM fest. Das JDK für Gradle und die Prototyp-Laufzeit sowie die konkreten Bibliotheksversionen werden bei der Projektinitialisierung festgelegt und dokumentiert; sie müssen INTERLIS 2.4 unterstützen und mit dem gewählten Build zusammenpassen.

### 15.2 API-Skizze

Eine erste Java-API könnte ungefähr folgende Operationen anbieten:

```java
IliContainer open(Path path);
IliContainer open(URI uri); // selektiv: kein automatischer Full Download

IoxReader openTransferReader(); // vollständiger Transfer als IOX-Events

Fragment getTopic(String topicName);
Fragment getBasket(String bid);
Fragment getClass(String className);
Fragment getObject(String tid); // kein oder ein SelectedObject im Ergebnisstrom

Fragment querySpatialCandidates(
    String className,
    String geometryAttribute,
    BoundingBox bbox
);

final class SelectedObject {
    private final BasketContext basket;
    private final IomObject object;

    public SelectedObject(BasketContext basket, IomObject object) {
        this.basket = basket;
        this.object = object;
    }

    public BasketContext getBasket() {
        return basket;
    }

    public IomObject getObject() {
        return object;
    }
}

interface Fragment extends AutoCloseable {
    TransferMetadata transferMetadata();
    Stream<BasketContext> baskets(); // auch selektierte leere Baskets
    Stream<SelectedObject> objects();
    void close();
}
```

`Fragment` kennzeichnet die selektive Herkunft unabhängig von der Anzahl der Treffer. `getObject()` liefert bei unbekannter TID einen leeren Objektstrom. `BasketContext` enthält BID, Topic, ursprüngliche Basketposition und Basketmetadaten; `TransferMetadata` enthält die erhaltenen Transfermetadaten. Die Basket- und Objektströme werden verzögert und mit begrenztem Speicher gelesen. Beide Sichten bleiben bis zum Schliessen des Fragments zugänglich; der Konsum einer Sicht darf die andere nicht unbrauchbar machen.

Der vollständige Reader liefert Start-/End-Events für Transfer und Baskets sowie Objekt-Events und erhält dadurch auch leere Baskets. Reader, Container und Fragmente müssen ihre Ressourcen schliessen können.

Die genaue API ist nicht Teil des Dateiformatstandards. Sie dient lediglich dem Prototyp. Explizite Fragmentkennzeichnung, vollständiger Basketkontext und IOX-Events für vollständige Transfers sind jedoch verbindliche Anforderungen.

---

## 16. CLI des Prototyps

Mögliche Befehle:

`create` akzeptiert ausschliesslich INTERLIS 2.4 FULL. `export` erzeugt den vollständigen semantisch gleichwertigen XTF-Transfer. Selektive Befehle weisen ihre Ausgabe ausdrücklich als Fragment aus und erhalten den Basketkontext. Die konkrete Serialisierung der Fragmentausgabe wird im Prototyp festgelegt; eine reine unmarkierte Objektliste genügt nicht.

```bash
ilicontainer create data.xtf data.ilic
```

```bash
ilicontainer info data.ilic
```

```bash
ilicontainer export data.ilic data.xtf
```

```bash
ilicontainer get-basket data.ilic b123
```

```bash
ilicontainer get-class \
  data.ilic \
  DMAV_Bodenbedeckung_V1_1.Bodenbedeckung.BoFlaeche
```

```bash
ilicontainer get-object data.ilic o4711
```

```bash
ilicontainer bbox-candidates \
  data.ilic \
  DMAV_Bodenbedeckung_V1_1.Bodenbedeckung.BoFlaeche \
  Geometrie \
  2600000 1200000 2601000 1201000
```

`bbox-candidates` liefert Bounding-Box-Kandidaten, keine abschliessend geometrisch geprüften Treffer.

Für Remote-Zugriff:

```bash
ilicontainer get-object \
  https://example.org/data.ilic \
  o4711
```

---

## 17. Referenztests

### 17.1 Roundtrip

```text
XTF
 ↓
IliContainer
 ↓
XTF
```

Zu vergleichen sind mindestens:

- Modelle,
- Topics,
- Baskets einschliesslich leerer Baskets und ursprünglicher Basketreihenfolge,
- Transfer- und Basketmetadaten,
- TIDs,
- Klassen,
- Attribute,
- Strukturen,
- LIST-Reihenfolgen und geordnete Beziehungen,
- präzise numerische Werte,
- Referenzen einschliesslich unverändert erhaltener offener Referenzen in Auswahlen,
- Assoziationen,
- Geometrien.

Der Vergleich erfolgt semantisch: Hauptobjekte werden anhand ihrer Identität und ihres Basketkontexts verglichen; deren Reihenfolge innerhalb eines Baskets darf abweichen. Reihenfolgen von Baskets, LISTs und geordneten Beziehungen müssen erhalten bleiben. Die Referenzdaten enthalten verschachtelte Strukturen, Kreisbögen, Höhen sowie Transfers ohne Objekte.

Andere INTERLIS-/XTF-Versionen und INITIAL/UPDATE müssen in gezielten Negativtests mit Diagnose abgelehnt werden. Lesen, Selektieren und Exportieren werden ohne Netzwerkzugriff auf Modellserver geprüft.

### 17.2 Streaming

Der vollständige Container muss mit begrenztem Speicher als IOX-Eventfolge gelesen werden können. Tests prüfen leere Baskets, Transfers ohne Objekte und einzelne Objekte oberhalb der Chunk-Zielgrösse. Das erste Objekt muss ohne vorheriges Lesen der Objekt- oder Spatial-Indizes verfügbar sein. Bei wachsender Objektzahl und gleichbleibendem Dictionary sowie maximaler Objekt-/Chunk-Grösse darf der Speicherbedarf nicht proportional zur Objektzahl wachsen.

Gemessen werden:

- Objects/s,
- MB/s,
- Peak Heap,
- Zeit bis zum ersten Objekt.

### 17.3 Topic-Zugriff

Für ein Topic werden nur dessen benötigte Chunks gelesen.

Erwartete Objekte und Basketkontexte einschliesslich leerer Baskets müssen identisch mit einem vollständigen Scan plus Topic-Filter sein. Das Ergebnis muss als Fragment gekennzeichnet sein.

### 17.4 Basket-Zugriff

`getBasket(bid)` muss exakt alle Objekte dieses Baskets und seinen vollständigen Basketkontext als Fragment liefern. Ein leerer Basket liefert einen Basketkontext und keine Objekte.

### 17.5 Class-Zugriff

`getClass(className)` muss alle Objekte der konkreten Klasse über alle Baskets liefern. Objekte und ursprüngliche Basketkontexte werden gegen einen vollständigen Scan plus Klassenfilter verglichen; das Ergebnis bleibt als Fragment gekennzeichnet.

### 17.6 Object-Zugriff

`getObject(tid)` muss genau das bezeichnete Objekt einschliesslich Strukturen und Basketkontext als Fragment liefern; eine unbekannte TID liefert keine Objekte. Der Vergleich erfolgt gegen einen vollständigen Scan. Ein erfolgreicher Zugriff darf höchstens einen Daten-Chunk lesen und dekomprimieren.

Dazu wird gemessen:

- Anzahl gelesener Directory-Seiten,
- Anzahl gelesener Chunks,
- übertragene Bytes bei Remote-Zugriff.

### 17.7 Spatial-Zugriff

Für eine BBOX-Kandidatenabfrage werden die Ergebnisse mit einer unabhängigen vollständigen Bounding-Box-Referenzauswertung verglichen. Erwartet werden genau die Objekte mit überlappenden oder berührenden Geometrie-Bounding-Boxes, jeweils mit vollständigen Strukturen und Basketkontext.

Testfälle umfassen Randberührungen, Kreisbögen mit Extrema ausserhalb ihrer Endpunkte, unterschiedliche Höhen bei gleicher XY-Lage, fehlende Geometrien, fehlende Indizes und fehlgeschlagene Indexerstellung bei nicht zuverlässig indexierbaren Geometrien oder uneindeutigem Koordinatensystem. Ein Fall mit Bounding-Box-Überlappung ohne geometrischen Schnitt muss als Kandidat enthalten sein. Eine exakte Intersects-Auswertung ist keine Voraussetzung für die Abnahme.

Gemessen werden:

- gelesene Indexbytes,
- gelesene Chunkbytes,
- Anzahl Kandidaten,
- Anzahl erwarteter Bounding-Box-Kandidaten laut Referenzauswertung,
- HTTP Requests,
- Gesamtdauer.

### 17.8 Remote-Fehlerfälle

Zu prüfen sind Server ohne Range-Unterstützung, Vollantworten auf Range-Anfragen und ein Wechsel des Containerstands zwischen Teilzugriffen. Der Reader muss verständlich abbrechen und darf weder stillschweigend vollständig herunterladen noch Ergebnisse verschiedener Stände vermischen.

Ein ausdrücklich erlaubter vollständiger Download wird separat getestet; auch dabei muss ein einheitlicher Containerstand gewahrt bleiben.

---

## 18. Benchmark

Der erste Benchmark soll mit mindestens einem realistischen INTERLIS-2.4-FULL-DMAV-Datensatz durchgeführt werden. Erste Grössen- und Streaming-Messungen beginnen bereits nach M2. Selektive und räumliche Messungen folgen mit den entsprechenden Meilensteinen; M6 konsolidiert die Ergebnisse.

Zu vergleichen sind:

```text
XTF
XTF.zip
XTF.zst
IliContainer Core
IliContainer Core + Spatial Index
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

1. Ein vollständiger INTERLIS-2.4-FULL-Transfer kann einschliesslich Metadaten, leerer Baskets und erforderlicher Reihenfolgen semantisch verlustfrei in IliContainer und zurück überführt werden; andere Versionen und Transferarten werden ausdrücklich abgelehnt.
2. IliContainer ist mit begrenztem Speicher als IOX-Eventfolge vollständig streambar, ohne zuvor Objekt- oder Spatial-Indizes lesen zu müssen.
3. Topics, Baskets, Klassen und einzelne Objekte können ohne vollständigen Dateidownload als Fragmente mit ursprünglichem Basketkontext gelesen werden.
4. Ein optionaler Spatial Index ermöglicht korrekte zweidimensionale BBOX-Kandidatenabfragen auf einer konkreten Klasse und einem Geometrieattribut; eine exakte geometrische Nachprüfung ist nicht erforderlich.
5. Remote-Zugriff funktioniert über HTTP Range Requests auf einem einheitlichen Containerstand; fehlende Range-Unterstützung und Standwechsel führen zu expliziten Fehlern.
6. Core-Container und Index-Overhead können getrennt gemessen werden.
7. Die Dateigrösse und Performance sind reproduzierbar gegen XTF, XTF.zip und XTF.zst benchmarkbar.
8. Lesen, Selektieren und Exportieren funktionieren ohne Modellserverzugriff.

Ein festes Ziel wie

```text
IliContainer muss immer 30 % kleiner als XTF.zip sein
```

wird in Version 0.3 bewusst **nicht** vorgegeben.

Die Benchmarks sollen zunächst zeigen, wo die tatsächlichen Vorteile liegen.

---

## 20. Entwicklungsmeilensteine

### M1 – Logisches Objektformat

- Java-Projekt mit Gradle Groovy DSL, Gradle Wrapper und erzwungenem Java-8-Sprachlevel initialisieren
- iox-ili, iox-api / IOM und ili2c einbinden; JDK- und Bibliotheksversionen dokumentieren
- INTERLIS 2.4 FULL → interne Objektkodierung mit Transfer- und Basketkontext
- interne Objektkodierung → INTERLIS 2.4 FULL
- explizite Ablehnung anderer Versionen und Transferarten
- Roundtrip kleiner Testmodelle
- CBOR-Prototyp

### M2 – Chunked Core Container

- Chunk Header
- Dictionary
- Chunk Directory
- per-Chunk-Kompression
- basketweises Layout mit Metadaten, leeren Baskets und Footer
- vollständiger sequenzieller IOX-Reader ohne vorheriges Lesen der Objekt-/Spatial-Indizes
- eigene Chunks für übergrosse Einzelobjekte
- erste DMAV-Grössen- und Streaming-Messungen nach M2

### M3 – Selektiver Zugriff

- Topic Directory
- Basket Directory
- Class Directory
- Object Directory
- lokale Teilzugriffe als Fragmente mit Basketkontext
- seitenweise Verzeichnisse und höchstens ein Daten-Chunk pro Einzelobjektzugriff

### M4 – HTTP Range Reader

- Remote Directory Access
- Chunk Range Requests
- begrenzter Cache
- Abbruch bei fehlender Range-Unterstützung oder wechselndem Dateistand
- Messung übertragener Bytes

### M5 – Spatial Index

- Index pro Klasse und Geometrieattribut
- zweidimensionale BBOX-Kandidatensuche einschliesslich Randberührungen und korrekter Bogen-Bounding-Boxes
- eindeutige Koordinatensystem-Metadaten und explizite Indexfehler
- Vergleich mit unabhängiger Bounding-Box-Referenzauswertung

### M6 – Konsolidierter DMAV Benchmark

- realer DMAV-Bestand
- Grössenvergleich
- Streaming-Benchmark
- Selective-Access-Benchmark
- Spatial-Benchmark
- Dokumentation der Ergebnisse

---

## 21. Mögliche spätere Erweiterungen

Nicht Teil von Version 0.3:

```text
Exact geometry intersection checks
Coordinate transformations
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

1. endgültige Container-Endung (`.ilic`, `.ilicontainer`, andere),
2. endgültige Objektkodierung und konkrete CBOR-Darstellung,
3. verlustfreie Geometriekodierung,
4. exakte Chunk-Zielgrösse für unkomprimierte Nutzdaten,
5. Aufbau des seitenweise lesbaren Object Directory und optionale Objekt-Offsets innerhalb eines Chunks,
6. Aufbau des räumlichen Index und mögliche räumliche Objektanordnung innerhalb einer Basket-Klassen-Gruppe,
7. konkrete Bytekodierung der Abschnitte im festgelegten Prototyplayout,
8. Kompressionsverfahren und Parameter,
9. Einbettung oder Referenzierung der INTERLIS-Modelle, unter Wahrung der Rekonstruktion ohne Modellserverzugriff,
10. Behandlung sonstiger ungültiger Eingangsdaten einschliesslich doppelter TIDs, ohne stillschweigenden Datenverlust,
11. konkrete Serialisierung ausdrücklich gekennzeichneter Fragmentexporte.

Codec, Kompressionsparameter, Chunk-Zielgrösse und Indexstrukturen werden durch Prototypen und Benchmarks entschieden. Regeln für ungültige Eingaben und Fragmentausgaben werden vor Implementierung der jeweiligen Schnittstelle konkretisiert.

Bereits festgelegt sind der Umfang INTERLIS 2.4 FULL, das Prototyplayout, ungeteilte übergrosse Einzelobjekte, der Kandidatenvertrag und die Fehlerbehandlung bei nicht zuverlässig räumlich indexierbaren Inhalten. Diese Zusagen werden nicht durch Benchmarks neu entschieden.

---

## 23. Leitprinzip

Die Version 0.3 verfolgt bewusst folgende Reihenfolge:

```text
1. INTERLIS 2.4 FULL verlustfrei kodieren
2. kleiner und schneller als XTF werden
3. Streaming erhalten
4. fachliche Einheiten adressierbar machen
5. räumliche Kandidatenabfragen ermöglichen
6. erst danach komplexe Query-Funktionalität hinzufügen
```

Der erste IliContainer soll damit kein Ersatz für eine Datenbank sein.

Er soll zunächst ein **besser adressierbares, kompakteres und cloud-freundlicheres INTERLIS-Transferformat** sein.

# IliContainer

Experimenteller Java-Prototyp eines kompakten, streambaren und selektiv lesbaren Containers für **INTERLIS 2.4 FULL**. Initial-/Update-Transfers und XTF 2.3 werden ausdrücklich abgelehnt.

- [Architektur und Prototyp-Spezifikation v0.3](ilicontainer-architektur-prototyp-spezifikation-v0.3.md)
- [Experimentelles Dateiformat und Implementierungsdetails](docs/FORMAT.md)
- [Implementierung und Abnahmenachweise](docs/IMPLEMENTATION.md)
- [Optionales WKB-Profil und direkte GIS-API](docs/WKB.md)
- [Benchmarks und Reproduktion](docs/BENCHMARKS.md)

**Kompatibilitätsbruch:** Reader und Writer unterstützen ausschliesslich Containerformat 3. Dateien der Formate 1 und 2 müssen aus den ursprünglichen XTF-Quellen neu erstellt werden.

## Build und Tests

Java 21 ist für Build und Ausführung erforderlich. Der Quellcode wird mit `--release 8` kompiliert; eine Java-8-Laufzeit wird nicht zugesagt. Buildsystem: Gradle Groovy DSL mit gepinntem Wrapper und gesperrten Abhängigkeiten.

```sh
./gradlew test build installDist
build/install/ilicontainer/bin/ilicontainer --help
```

`test` verwendet kleine lokale Modelle, einen Loopback-HTTP-Server und einen separaten Prozess mit 32 MiB Heap. Es lädt keine Benchmark-Datensätze herunter. Die Bibliotheken werden beim ersten Gradle-Build aufgelöst. CI ist für Linux und macOS mit Java 21 konfiguriert.

## Container erstellen und exportieren

```sh
ilicontainer create data.xtf data.ilic \
  --model-dir ./models \
  --model-dir https://models.geo.admin.ch \
  --model-dir https://models.interlis.ch

ilicontainer info data.ilic
ilicontainer export data.ilic roundtrip.xtf
```

Alternativ kann eine ILI-Datei über `--model-file ./models/MyModel.ili` angegeben werden. `--model-dir` und `--model-file` sind wiederholbar. Modelle werden beim Erstellen aufgelöst; Lesen und Export benötigen anschliessend keinen Modellserver und keine lokalen ILI-Dateien.

Optionen für `create`:

| Option | Standard / Wirkung |
|---|---|
| `--chunk-size` | 262144 unkomprimierte Bytes; ganze Objekte bleiben zusammen |
| `--compression` | `zstd`; alternativ `deflate`, `none` |
| `--compression-level` | Zstandard-Level 3 |
| `--numeric-encoding` | `lexical`; alternativ `decimal` ohne Präzisionsverlust |
| `--embed-models` | ILI-Quellen samt Abhängigkeiten zusätzlich einbetten |
| `--overwrite` | Bestehende Zieldatei nach erfolgreichem Schreiben ersetzen |
| `--spatial Klasse:Attribut` | Optionalen Index nach Erstellung des Core ergänzen |
| `--spatial-order Klasse.Attribut` | Optionale Hilbert-Sortierung innerhalb jeder Basket-/Klassen-Gruppe |
| `--spatial-packing` | `str`; alternativ `x` für Vergleichsmessungen |
| `--geometry-encoding` | `iom`; alternativ `wkb` für direkten GIS-Zugriff |
| `--geometry-crs Klasse.Attribut=CRS` | Explizite Geometrie-CRS-Zuordnung, wenn das Modell keine eindeutige Zuordnung liefert |
| `--crs EPSG:2056` | Explizite CRS-Angabe für Indexierung, wenn erforderlich |

Es findet keine obligatorische vollständige Modellvalidierung statt. Unlesbare oder nicht darstellbare Inhalte, unzulässige Transferarten und doppelte Identitäten werden abgelehnt. OID-lose Assoziationen bleiben erhalten.

## Selektiver Zugriff

```sh
ilicontainer get-topic data.ilic Model.Topic --output topic.xtf
ilicontainer get-basket data.ilic b123 --output basket.xtf
ilicontainer get-class data.ilic Model.Topic.Class --output class.xtf
ilicontainer get-object data.ilic o4711 --output object.xtf
```

Ohne `--output` wird XTF nach stdout geschrieben. Diagnosen gehen nach stderr. Selektive Ausgaben sind **Fragmente**: Der Headerkommentar enthält `IliContainer fragment`, Auswahlart und Unvollständigkeitshinweis. Bestehende Kommentare, Basketkontexte und Referenzen bleiben erhalten. Fragmente sind möglicherweise nicht modellkonform; referenzierte Objekte werden nicht nachgeladen.

Klassenabfragen betreffen die konkrete Klasse. Unbekannte TIDs/BIDs ergeben leere Fragmente; unbekannte Klassen/Topics führen zu einer Diagnose.

## Räumliche Kandidaten

```sh
ilicontainer add-spatial-index data.ilic Model.Topic.Class Geometrie --crs EPSG:2056
ilicontainer bbox-candidates data.ilic Model.Topic.Class Geometrie \
  2600000 1200000 2601000 1201000 --output candidates.xtf
```

Gesucht wird zweidimensional im CRS des Index. Randberührungen zählen; Z-Werte bleiben gespeichert, beeinflussen die Suche aber nicht. Es gibt keine Transformation und keine exakte Intersects-Prüfung. Ohne passenden Index erfolgt ein Fehler statt eines automatischen Full Scans. Nicht zuverlässig indexierbare Geometrien führen zum Indexfehler; die vorhandene Core-Datei bleibt verfügbar.

## Datenanordnung und Diagnose

```sh
ilicontainer create data.xtf spatial.ilic --model-dir ./models \
  --geometry-encoding wkb \
  --geometry-crs Model.Topic.Class.Geometrie=EPSG:2056 \
  --spatial-order Model.Topic.Class.Geometrie \
  --spatial Model.Topic.Class:Geometrie --crs EPSG:2056
ilicontainer info spatial.ilic --storage
```

`--spatial-order` ist je Klasse einmal und für mehrere Klassen wiederholbar. Es sortiert Hauptobjekte innerhalb derselben Basket-/Klassen-Gruppe; Basket-, LIST- und Beziehungsreihenfolgen bleiben erhalten. FIDs entstehen nach der Sortierung und sind innerhalb einer Datei stabil. Beim Neuerstellen mit anderer Anordnung können sie sich ändern; TIDs bleiben erhalten. Objekte ohne Geometrie stehen am Gruppenende.

Die STR-Packung des Index und die Hilbert-Anordnung der Daten sind unabhängig: Ein vorhandener Container kann einen STR-Index erhalten, ohne seine Daten-Chunks umzuordnen. Eine andere Datenanordnung erfordert die Neuerstellung aus XTF. `info --storage` liest für die physische Bytebilanz sämtliche Abschnittsheader und Verzeichnisse; bei HTTP ist dies eine umfassende Diagnose, keine kleine Einzelobjektabfrage.

## HTTP Range Access

```sh
ilicontainer get-object https://example.org/data.ilic o4711 --output object.xtf
```

Standardmässig sind gültige Range-Antworten und ein starker ETag erforderlich. Bei tatsächlich unveränderlichen URLs kann `--immutable-url` verwendet werden. `--allow-full-download` erlaubt beim Öffnen ausdrücklich eine vollständige lokale Momentaufnahme, falls der Server keine Ranges unterstützt. Wechselnde Dateistände werden niemals zu einem erfolgreichen Ergebnis vermischt.

## Java-API

```java
try (IliContainer container = IliContainer.open(Paths.get("data.ilic"));
     Fragment fragment = container.getBasket("b123");
     Stream<SelectedObject> objects = fragment.objects()) {
    objects.forEach(selected -> {
        System.out.println(selected.getBasket().bid);
        System.out.println(selected.getObject().getobjectoid());
    });
}
```

`fragment.baskets()` liefert auch selektierte leere Baskets. Die Basket- und Objektansichten können unabhängig gelesen werden. Vollständiges Lesen erfolgt mit `container.openTransferReader()` oder direkt sequenziell mit `IliContainer.stream(inputStream)` als IOX-Eventfolge. Der Reader übernimmt den ihm übergebenen Eingabestream und muss geschlossen werden.

Für Vergleichsmessungen kann das räumliche Vorladen über die Java-API deaktiviert werden:

```java
RemoteOptions options = new RemoteOptions();
options.prefetchPositions = 0;
try (IliContainer container = IliContainer.open(uri, options)) {
    // Abfragen verwenden weiterhin denselben begrenzten Framecache.
}
```

Standardmässig werden höchstens 32 Objektpositionen vorausgelesen. Bytebereiche werden nur bei höchstens 4 KiB Abstand und bis zu insgesamt 1 MiB zusammengefasst. Vorab geladene Frames und normale Lesezugriffe teilen sich den 32-MiB-Cache; Frames oberhalb des Cachebudgets werden bei Bedarf gelesen und nicht dauerhaft gespeichert. `RemoteOptions` ist auch bei `open(Path, options)` verwendbar. Chunk-Grösse, räumliche Anordnung und Vorladen sind anhand des eigenen Abfragemusters zu vergleichen; die [Messmatrix](docs/benchmarks/format3/README.md) weist auch Verschlechterungen aus.

Die Distribution enthält Bibliotheks-JAR, Abhängigkeiten und Startskripte. Noch keine Veröffentlichung in einem Maven-Repository und keine langfristige Garantie für Dateiformat oder API.

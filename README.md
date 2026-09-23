# IBX — INTERLIS Binary eXchange

Experimenteller Java-Prototyp eines kompakten, streambaren und selektiv lesbaren Containers für **INTERLIS 2.4 FULL**. Initial-/Update-Transfers und XTF 2.3 werden ausdrücklich abgelehnt.

- [Architektur und Prototyp-Spezifikation v0.3](ibx-architektur-prototyp-spezifikation-v0.3.md)
- [Experimentelles Dateiformat und Implementierungsdetails](docs/FORMAT.md)
- [Implementierung und Abnahmenachweise](docs/IMPLEMENTATION.md)
- [Optionales WKB-Profil und direkte GIS-API](docs/WKB.md)
- [Benchmarks und Reproduktion](docs/BENCHMARKS.md)

**Kompatibilitätsbruch:** Reader und Writer unterstützen ausschliesslich IBX-Containerformat 4. IliContainer-Dateien der Formate 1, 2 und 3 müssen aus den ursprünglichen XTF-Quellen neu erstellt werden.

## QGIS-Prototyp

Der lesende Python-Provider für QGIS 4.2.2 öffnet lokale und öffentliche HTTPS-Dateien.
Der Objektbrowser zeigt eingebettete Strukturen und navigiert in beide Beziehungsrichtungen.
Für das Plugin sind weder Java noch Zusatzbibliotheken nötig; es liest das
Containerformat direkt in Python.
[Installation und Demo](docs/QGIS.md) · [Testdaten](demo/README.md).

```sh
./scripts/build-demo.sh
python3 scripts/package-qgis.py
```

Das plattformunabhängige Paket liegt unter `build/ibx-qgis-0.5.0.zip`; Java 21
wird nur noch für die Kommandozeile (Erstellen und Export) gebraucht.

## Build und Tests

Für den Java-Teil (Bibliothek, CLI, Writer und Java-Tests) ist Java 21 erforderlich.
Der Quellcode wird mit `--release 8` kompiliert; eine Java-8-Laufzeit wird nicht
zugesagt. Buildsystem: Gradle Groovy DSL mit gepinntem Wrapper und gesperrten
Abhängigkeiten. Das QGIS-Plugin selbst ist reines Python und wird ohne Gradle
gebaut (`python3 scripts/package-qgis.py`).

```sh
./gradlew test build installDist
build/install/ibx/bin/ibx --help
```

`test` verwendet kleine lokale Modelle, einen Loopback-HTTP-Server und einen separaten Prozess mit 32 MiB Heap. Es lädt keine Benchmark-Datensätze herunter. Die Bibliotheken werden beim ersten Gradle-Build aufgelöst. CI ist für Linux und macOS mit Java 21 konfiguriert; zusätzlich prüft eine plattformübergreifende Python-Job den Container-Leser des Plugins ohne QGIS und Java (`qgis/tests/test_reader.py`).

## Container erstellen und exportieren

```sh
ibx create data.xtf data.ibx \
  --model-dir ./models \
  --model-dir https://models.geo.admin.ch \
  --model-dir https://models.interlis.ch

ibx info data.ibx
ibx export data.ibx roundtrip.xtf
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
ibx get-topic data.ibx Model.Topic --output topic.xtf
ibx get-basket data.ibx b123 --output basket.xtf
ibx get-class data.ibx Model.Topic.Class --output class.xtf
ibx get-object data.ibx o4711 --output object.xtf
```

Ohne `--output` wird XTF nach stdout geschrieben. Diagnosen gehen nach stderr. Selektive Ausgaben sind **Fragmente**: Der Headerkommentar enthält `IBX fragment`, Auswahlart und Unvollständigkeitshinweis. Bestehende Kommentare, Basketkontexte und Referenzen bleiben erhalten. Fragmente sind möglicherweise nicht modellkonform; referenzierte Objekte werden nicht nachgeladen.

Klassenabfragen betreffen die konkrete Klasse. Unbekannte TIDs/BIDs ergeben leere Fragmente; unbekannte Klassen/Topics führen zu einer Diagnose.

## Räumliche Kandidaten

```sh
ibx add-spatial-index data.ibx Model.Topic.Class Geometrie --crs EPSG:2056
ibx bbox-candidates data.ibx Model.Topic.Class Geometrie \
  2600000 1200000 2601000 1201000 --output candidates.xtf
```

Gesucht wird zweidimensional im CRS des Index. Randberührungen zählen; Z-Werte bleiben gespeichert, beeinflussen die Suche aber nicht. Es gibt keine Transformation und keine exakte Intersects-Prüfung. Ohne passenden Index erfolgt ein Fehler statt eines automatischen Full Scans. Nicht zuverlässig indexierbare Geometrien führen zum Indexfehler; die vorhandene Core-Datei bleibt verfügbar.

## Datenanordnung und Diagnose

```sh
ibx create data.xtf spatial.ibx --model-dir ./models \
  --geometry-encoding wkb \
  --geometry-crs Model.Topic.Class.Geometrie=EPSG:2056 \
  --spatial-order Model.Topic.Class.Geometrie \
  --spatial Model.Topic.Class:Geometrie --crs EPSG:2056
ibx info spatial.ibx --storage
```

`--spatial-order` ist je Klasse einmal und für mehrere Klassen wiederholbar. Es sortiert Hauptobjekte innerhalb derselben Basket-/Klassen-Gruppe; Basket-, LIST- und Beziehungsreihenfolgen bleiben erhalten. FIDs entstehen nach der Sortierung und sind innerhalb einer Datei stabil. Beim Neuerstellen mit anderer Anordnung können sie sich ändern; TIDs bleiben erhalten. Objekte ohne Geometrie stehen am Gruppenende.

Die STR-Packung des Index und die Hilbert-Anordnung der Daten sind unabhängig: Ein vorhandener Container kann einen STR-Index erhalten, ohne seine Daten-Chunks umzuordnen. Eine andere Datenanordnung erfordert die Neuerstellung aus XTF. `info --storage` liest für die physische Bytebilanz sämtliche Abschnittsheader und Verzeichnisse; bei HTTP ist dies eine umfassende Diagnose, keine kleine Einzelobjektabfrage.

## HTTP Range Access

```sh
ibx get-object https://example.org/data.ibx o4711 --output object.xtf
```

Standardmässig sind gültige Range-Antworten und ein starker ETag erforderlich. Bei tatsächlich unveränderlichen URLs kann `--immutable-url` verwendet werden. `--allow-full-download` erlaubt beim Öffnen ausdrücklich eine vollständige lokale Momentaufnahme, falls der Server keine Ranges unterstützt. Wechselnde Dateistände werden niemals zu einem erfolgreichen Ergebnis vermischt.

## Java-API

```java
try (IbxContainer container = IbxContainer.open(Paths.get("data.ibx"));
     Fragment fragment = container.getBasket("b123");
     Stream<SelectedObject> objects = fragment.objects()) {
    objects.forEach(selected -> {
        System.out.println(selected.getBasket().bid);
        System.out.println(selected.getObject().getobjectoid());
    });
}
```

`fragment.baskets()` liefert auch selektierte leere Baskets. Die Basket- und Objektansichten können unabhängig gelesen werden. Vollständiges Lesen erfolgt mit `container.openTransferReader()` oder direkt sequenziell mit `IbxContainer.stream(inputStream)` als IOX-Eventfolge. Der Reader übernimmt den ihm übergebenen Eingabestream und muss geschlossen werden.

Für Vergleichsmessungen kann das räumliche Vorladen über die Java-API deaktiviert werden:

```java
RemoteOptions options = new RemoteOptions();
options.prefetchPositions = 0;
try (IbxContainer container = IbxContainer.open(uri, options)) {
    // Abfragen verwenden weiterhin denselben begrenzten Framecache.
}
```

Standardmässig werden höchstens 32 Objektpositionen vorausgelesen. Bytebereiche werden nur bei höchstens 4 KiB Abstand und bis zu insgesamt 1 MiB zusammengefasst. Vorab geladene Frames und normale Lesezugriffe teilen sich den 32-MiB-Cache; Frames oberhalb des Cachebudgets werden bei Bedarf gelesen und nicht dauerhaft gespeichert. `RemoteOptions` ist auch bei `open(Path, options)` verwendbar. Chunk-Grösse, räumliche Anordnung und Vorladen sind anhand des eigenen Abfragemusters zu vergleichen; die [Messmatrix](docs/benchmarks/format3/README.md) weist auch Verschlechterungen aus.

Die Distribution enthält Bibliotheks-JAR, Abhängigkeiten und Startskripte. Noch keine Veröffentlichung in einem Maven-Repository und keine langfristige Garantie für Dateiformat oder API.

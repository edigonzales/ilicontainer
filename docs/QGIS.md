# IBX in QGIS 4.2.2

Lesender Prototyp für macOS, Linux und Windows / Qt 6. Der Python-Provider liest
`.ibx` direkt in QGIS; es gibt keine Java-Bridge, keinen Hilfsprozess und keine
Java-Abhängigkeit. Es wird weder in GeoPackage importiert noch ein vollständiger
Memory-Layer angelegt. Zstd-komprimierte Chunks verwendet der Reader über die
von QGIS mitgelieferte Zstandard-Bibliothek.

Die tatsächlich ausgeführten Prüfungen und Zugriffsmessungen stehen im
[Abnahmeprotokoll](QGIS-ACCEPTANCE.md).

## Schnellstart

```sh
./scripts/build-demo.sh
python3 scripts/package-qgis.py
```

In QGIS unter **Erweiterungen → Erweiterungen verwalten → Aus ZIP installieren**
`build/ibx-qgis-0.5.0.zip` auswählen. Das ZIP ist plattformunabhängig und enthält
nur Python, die Demodateien, Modelle und XTF. QGIS anschliessend neu starten.
Unter **IBX → Einstellungen** kann bei Bedarf der Pfad zur
Zstandard-Bibliothek angegeben werden; leer bedeutet automatische Erkennung.

**IBX → Demo öffnen** öffnet die Auswahl der mitgelieferten Beispiele. **Parkanlage**
ist der empfohlene Einstieg: **Spielplatz / Fläche** oder **Spielgerät / Position**
hinzufügen, dann ein Spielgerät mit **IBX-Objekt erkunden** anklicken. Im Objektfenster
lassen sich Kontrollen mit Messwerten aufklappen, zum verknüpften Spielplatz wechseln
und dort über **Spielplatz-Zuordnung · Spielgeräte** die zugeordneten Geräte ansehen.
Die einfache Demo verwendet eine binäre 1:n-Assoziation ohne eigene Attribute oder
OID. Sie hat keine Vererbung oder n:m-Beziehungen.

Über denselben Menüpunkt lässt sich **Quartier und Unterhalt** öffnen. Als
komplexere Demo enthält sie Vererbungen, Assoziationen, Selbstbezüge und mehrere
Geometriesichten. Zum Einstieg einen **Gebaeude / Grundriss**-Layer hinzufügen.
Das Modell enthält absichtlich keine `ibx.*`-Metaattribute: Klassen- und
Attributnamen werden aus den Modellbezeichnern angezeigt.

Die Layerauswahl trennt **Name**, **Modellart** (Klasse oder Assoziation),
**Geometrie** und **Anzahl**. **Modellnamen anzeigen** blendet die qualifizierten
Originalnamen ein; die Wahl wird im QGIS-Profil gespeichert. Die Suche findet
auch ausgeblendete Modellnamen. Die Anzahl folgt der Basket-Auswahl und zählt
Instanzen; mehrere Geometriesichten derselben Klasse sind nicht zu addieren.
Assoziationen lassen sich als eigene Tabellen öffnen, sofern sie als eigene
Instanzen im Katalog enthalten sind.

Mit **IBX-Objekt erkunden** ein Gebäude anklicken. Im Objektfenster:

1. Kontrollen und Messungen aufklappen.
2. `Auftrag` mit dem Baumpfeil aufklappen. Seine Angaben erscheinen im
   Haus; das Haus bleibt Hauptobjekt. Mit **Öffnen →** in der Aktionsspalte zum
   Auftrag wechseln. Der Auftrag muss nicht als Layer geladen sein.
3. Unter **Arbeit · Betroffene Objekte** einen Spielplatz aufklappen oder öffnen.
4. „Auf Karte zeigen“ lädt bei Bedarf den passenden Layer und hebt das Objekt hervor.
5. Mit „Zurück“ zum Auftrag und Gebäude zurückkehren.

Originalobjekte lassen sich weiterhin mit der Java-Kommandozeile als
XTF-Fragment exportieren (`ibx get-object`, `ibx get-class`, …); das
Python-Plugin selbst schreibt keine Dateien.

Die Spalten **Eigenschaft · Inhalt · Aktion** trennen Angaben von Bedienung.
Ein Klick auf den Inhalt markiert nur die Zeile. Der Baumpfeil lädt das Ziel erst
bei Bedarf; **Öffnen →** macht es zum Hauptobjekt. Die Eingabetaste führt die
Aktion der markierten Zeile aus, Rechts/Links klappt auf/zu. Das Kontextmenü
bietet Aktionen und **Kopieren**; Strukturen bleiben Teile desselben Objekts.

Bei **Zustaendigkeit · Organisation** stehen Funktion und Gültigkeit unter
**Angaben zur Zustaendigkeit**. Die Organisationsangaben werden separat
aufgeklappt. **Öffnen →** führt zur Organisation; **Assoziation öffnen** im
Kontextmenü öffnet die vollständige Zuständigkeitsinstanz. Verschiedene
Zuständigkeiten zum gleichen Ziel bleiben getrennt. Assoziationen mit mehr als
zwei Rollen behalten alle Rollen in einer gemeinsamen Ansicht.

**Noch nicht geladen** bedeutet, dass noch kein Zugriff auf das Ziel erfolgt ist.
**Weitere Angaben zum Objekt → Laden** liest die erste Seite seiner eingehenden
Beziehungen. **Weitere Einträge laden** holt jeweils höchstens 50 Indexeinträge;
„geladen“ kennzeichnet vorläufige Mengen. Fehlende Indizes und fehlende Ziele
werden ausdrücklich angezeigt. Fehler lassen sich an der betroffenen Zeile
wiederholen. Ein bereits übergeordnetes Objekt erscheint als **Bereits weiter
oben angezeigt**; die Aktion springt zu dieser Darstellung. Aufklappen verändert
den Besuchsverlauf nicht. Karte und Tabelle unten beziehen sich auf das
Hauptobjekt. **Technische Details** stehen als normaler, aufklappbarer Knoten am
Ende des Objektbaums und lassen sich wie andere Baumzeilen kopieren.

Der **Besuchsverlauf** ist beim Öffnen eingeklappt und zeigt die Anzahl der
Besuche. Aufgeklappt erscheint die vollständige Reihenfolge in einer Liste mit
eigener Bildlaufleiste; ein Eintrag öffnet den jeweiligen Besuch, der aktuelle
Eintrag ist fett markiert. Die Klappstellung bleibt bei Objektwechseln erhalten.
Zurück/Vorwärts bleiben verfügbar. Ein neuer Beziehungsklick nach
„Zurück“ verwirft spätere Einträge und beginnt dort einen neuen Verlauf. Fehler
und Abbruch verändern die aktuelle Position nicht. **Baskets** filtern die
Layerauswahl; keine Auswahl bedeutet alle Baskets.

„Attributtabelle“ bietet zusätzlich eine normale QGIS-Tabelle der Klasse.
Bestehende Layerfilter werden beim Navigieren nicht verändert. Hervorhebungen
können daher auch ein Objekt ausserhalb des sichtbaren Layerfilters zeigen.

## HTTPS

Im Öffnungsdialog eine öffentliche `https://…/datei.ibx`-Adresse eingeben.
Erforderlich sind Byte-Range-Antworten und ein starker ETag. TLS-Zertifikate werden
über den Zertifikatsspeicher der Python-Laufzeit geprüft (`SSL_CERT_FILE`
funktioniert als zusätzlicher Vertrauensanker). Der Server darf keine komprimierte
HTTP-Antwort liefern; die interne IBX-Kompression ist davon unabhängig.

Ohne Ranges kann bewusst „Vollständigen Download erlauben“ aktiviert werden.
Dann wird eine temporäre lokale Momentaufnahme verwendet. „URL ist unveränderlich“
ist nur für tatsächlich unveränderliche URLs ohne starken ETag vorgesehen.
HTTPS→HTTP-Weiterleitungen werden abgelehnt. Es gibt keine Authentisierung und
keine automatische Navigation in andere Dateien.

**IBX → Zugriffsdiagnose** öffnet ein andockbares Fenster für die Datenquelle des
aktuell erkundeten Objekts oder des aktiven IBX-Layers. Ist kein Layer aktiv,
wird die einzige IBX-Quelle im Projekt gewählt; bei mehreren erscheint eine
Auswahl. Das Fenster zeigt den letzten Verlauf von bis zu 200 Vorgängen,
einschliesslich laufender, wartender, erfolgreicher und fehlgeschlagener Zugriffe.
Neueste Vorgänge stehen standardmässig oben; jede Spalte lässt sich über ihren
Titel sortieren. **Info** erklärt die Spalten und Messwerte. Das Fenster
aktualisiert sich etwa jede Sekunde, solange es sichtbar ist. Die Summen seit
dem Öffnen enthalten auch Datei- und HTTP-Lesezugriffe, Daten-Chunkframes,
Indexseiten und Cachetreffer. Das Protokoll bleibt im Arbeitsspeicher und wird
nicht dauerhaft gespeichert. Angezeigt werden nur Dateiname oder Hostname, keine
lokalen Vollpfade oder URL-Parameter.

## Erstellen eigener Dateien

```sh
build/install/ibx/bin/ibx create quelle.xtf daten.ibx \
  --model-file MeinModell.ili --geometry-encoding wkb \
  --geometry-crs Modell.Thema.Klasse.Geometrie=EPSG:2056 \
  --spatial Modell.Thema.Klasse:Geometrie --crs EPSG:2056 --embed-models
```

Weitere Geometrieattribute benötigen weitere `--spatial`- und gegebenenfalls
`--geometry-crs`-Angaben. Der Rückwärtsindex entsteht automatisch;
`--no-reverse-index` schaltet ihn aus. IOM bleibt der CLI-Standard, QGIS setzt WKB
voraus. Fehlende Indizes werden erklärt, nicht durch einen unsichtbaren Scan ersetzt.

Optionale INTERLIS-Metadaten vor einer Klasse oder einem Attribut:

```text
!!@ ibx.label = "Gebäude"
!!@ ibx.titleAttribute = "Name"
```

`ibx.label` benennt das Modellelement in der Oberfläche, beispielsweise die
Klasse „Gebäude“. `ibx.titleAttribute` bezeichnet dagegen ein vorhandenes skalares
Attribut der Klasse, dessen Wert den Titel eines einzelnen Objekts bildet.
Das Quartier-Demomodell verwendet diese Metadaten bewusst nicht.
Es erzeugt kein neues Attribut und verändert keine Daten. Dokumentation,
Kardinalitäten, Strukturtypen, Rollen, Vererbung, Einheiten und Aufzählungen werden
beim Erstellen gespeichert. Zum Lesen wird kein Modellserver benötigt.

## Entwicklung und Tests

Ein eigenes Profil `ibx-dev` oder `ibx-demo` über QGIS starten. In dessen
Python-Konsole `QgsApplication.qgisSettingsDirPath()` ermitteln, dann:

```sh
python3 scripts/install-qgis-dev.py --profile '/der/von/QGIS/gelieferte/Profilpfad'
```

Der Installer legt einen Link an und ersetzt keine bestehende Installation.
Provideränderungen erfordern einen QGIS-Neustart. Builds, Pakete, Prüfbilder und
Lastdaten bleiben unter `build/`; ein normaler Build verändert kein QGIS-Profil.

```sh
./gradlew test build installDist
PYTHONPATH=qgis python3 qgis/tests/test_reader.py -v   # ohne QGIS und Java
scripts/qgis-python.sh qgis/tests/test_provider.py -v
scripts/qgis-python.sh qgis/tests/test_ui.py -v
scripts/qgis-python.sh qgis/tests/test_presentation.py -v
scripts/qgis-python.sh qgis/tests/test_object_tree.py -v
scripts/qgis-python.sh qgis/tests/test_https.py -v
python3 scripts/verify-qgis-package.py
python3 scripts/verify-large.py                 # 100'000 Gebäude
python3 scripts/verify-large.py --size 1000000  # optional
```

`QGIS_APP` kann den lokalen App-Pfad überschreiben. Die QGIS-Tests laufen mit den
Python-/Qt-Bindings der App. `test_reader.py` prüft den Container-Leser direkt und
benötigt weder QGIS noch Java; Zstd-Fälle werden übersprungen, wenn keine
Zstandard-Bibliothek gefunden wird. Die Fixtures unter `qgis/tests/fixtures/`
enthalten je eine `deflate`- und eine unkomprimierte Datei. `test_ui.py` prüft den
asynchronen Bedienablauf und schreibt Prüfbilder nach `build/qgis/`. Der Lasttest
erzeugt die Datei mit der Java-CLI, misst aber ausschliesslich mit dem
Python-Leser und schreibt Zugriffszahlen nach `build/large/report.json`.

## Grenzen

- Format 4 mit neuer IBX-Magic; alte IliContainer-Dateien aus XTF neu erstellen.
- Keine Schreiboperationen und kein GDAL-Dateitreiber. Der XTF-Export bleibt der
  Java-Kommandozeile vorbehalten.
- Zstd-komprimierte Dateien benötigen eine auffindbare Zstandard-Bibliothek
  (QGIS liefert sie normalerweise mit); `deflate`- und unkomprimierte Dateien
  laufen ohne sie.
- Dezimalwerte und ganze Zahlen ausserhalb des modellseitig zugesicherten
  64-Bit-Bereichs erscheinen exakt als Text; 64-Bit-Ganzzahlen und Boolesche Werte
  sind native Felder. Strukturfelder sind zusätzlich als typisiertes JSON abfragbar.
- Strukturgeometrien lassen sich hervorheben, bilden aber keine eigenen Layer.
- Vollständige Klassenabfragen über sehr viele Objekte sind in Python langsamer
  als mit der früheren Java-Bridge; gezielte Karten- und Objektzugriffe sind
  gleichwertig oder schneller. Messwerte stehen im Abnahmeprotokoll.
- Räumliche Indexauswertung sammelt Kandidaten im Arbeitsspeicher; eine sehr
  grosse Abfrage kann vor der ersten Seite Arbeit benötigen. Die Kandidatenreihenfolge
  entspricht der Container-Reihenfolge der früheren Java-Umsetzung.
- Netzwerkfehler werden begrenzt durch Verbindungs-/Lesetimeouts. Abbruch wird
  zwischen Leseoperationen geprüft; ein laufender Socket kann bis zum Timeout benötigen.

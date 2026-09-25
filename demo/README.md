# QGIS-Demos

Beide Demos sind fiktive INTERLIS-2.4-Datensätze in EPSG:2056. Das QGIS-Plugin
enthält jeweils Modell, XTF-Quelldaten und eine offline lesbare IBX-Datei mit
eingebettetem Modell und räumlichen Indizes. Über **IBX → Demo öffnen** kann
zwischen den Beispielen gewählt werden; „Parkanlage“ ist der einfache Einstieg.

## Parkanlage

Das einfache Modell enthält drei Spielplätze mit Flächengeometrie und sechs
Spielgeräte mit Punktgeometrie. Die binäre Assoziation `SpielplatzZuordnung`
ordnet jedes Spielgerät genau einem Spielplatz zu; ein Spielplatz kann beliebig
viele Geräte haben. Die Rolle `Spielplatz` hat Kardinalität `{1}`, die Rolle
`Spielgeraete` `{0..*}`. Die Assoziation gilt innerhalb des einzelnen Baskets und
hat keine eigenen Attribute oder OID.
Spielgeräte enthalten Kontrollen und darin Messwert-Strukturen; es gibt weder
Vererbung noch n:m-Beziehungen.

Die Daten zeigen alle Kontrollresultate, verschachtelte Messwerte und ein Gerät
ohne Kontrollen. Ein guter Einstieg ist `geraet0` / „Nestschaukel“: Die Kontrolle
aufklappen, zum Spielplatz navigieren und dort die eingehenden Gerätebeziehungen
erkunden.

```sh
python3 demo/generate_parkanlage.py
scripts/build-demo.sh
```

Der Generator schreibt deterministisches `parkanlage.xtf`; `build-demo.sh`
erstellt daraus `parkanlage.ibx` mit WKB-Geometrien und räumlichen Indizes.

## Quartier und Unterhalt

Fiktive, modellvalidierte INTERLIS-2.4-Daten in EPSG:2056. Keine realen Gebäude,
Adressen oder Personen. Die Datei `quartier.ibx` ist eine komplette, offline
lesbare Demo mit eingebettetem Modell, räumlichen Indizes und Rückwärtsindex.

| Bestand | Anzahl |
|---|---:|
| Gebäude (je Grundriss + Beschriftungsposition) | 24 |
| Spielplätze | 6 |
| Technische Anlagen | 6 |
| Unterhaltsaufträge | 8 |
| Organisationen | 6 |
| OID-lose Zuständigkeiten mit Funktion/Gültigkeit | 24 |
| Folgeauftragsbeziehungen (Zyklus) | 2 |
| Hauptobjekte gesamt | 76 |

16 Gebäude besitzen je zwei Kontrollen. Jede Kontrolle enthält eine Messung,
eine Organisation als Referenzziel und eine Punktgeometrie. Organisationen und
Aufträge liegen im Datenbereich `nord`, Anlagen und Assoziationen in `sued`.
`leer` ist ein leerer Datenbereich. Basketübergreifende Rollen sind ausdrücklich
`EXTERNAL`; die kleine Demo besteht die vollständige IOX-Modellvalidierung.
Das Quartier-Modell enthält absichtlich keine `ibx.*`-Metaattribute. Seine
Elementnamen folgen den Modellbezeichnern; Objekttitel verwenden den allgemeinen
Fallback des Providers.

Erwarteter Einstieg: `g0` (Attribut `Name`: „Haus am Park 1“) → `auftrag0` → rückwärts
`anlage0` / „Spielplatz 1“. Auftrag 0 besitzt sieben eingehende Kanten:
`g0`, `g8`, `g16`, `anlage0`, `anlage8` und zwei OID-lose Folgeauftragsinstanzen.
Die Objekt-FIDs werden nicht als fachliche Identitäten festgeschrieben.

```sh
python3 demo/generate.py
scripts/build-demo.sh
```

Der Quartier-Generator schreibt deterministisches XTF. Der IBX-Writer vergibt
pro Erstellung eine neue Dataset-UUID. Die Binärdatei muss daher nicht
byteidentisch sein.

`--size 100000 --output build/large.xtf` erzeugt einen grösseren Bestand. Die ersten
10'000 Gebäude zeigen dann auf Auftrag 0, die übrigen auf Aufträge 1–7. Der
vollständige Lasttest samt Indexaufbau ist `scripts/verify-large.py`.

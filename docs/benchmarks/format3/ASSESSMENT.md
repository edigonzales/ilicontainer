# Einordnung der Format-3-Messungen

Die Abfragematrix umfasst 52 abgeschlossene Varianten. Erstellung, Spatial-Indexaufbau (wo vorgesehen), Export und Leseabfragen wurden dreifach gemessen. Alle Hauptläufe bestehen den semantischen XTF-Roundtrip. Eingabe-Digests, Abfragefenster und Kandidatenzahlen stimmen zwischen den jeweiligen Varianten überein.

## Was sich verbessert

Für das mittlere Ortschaftenfenster mit 47 Kandidaten, 256-KiB-Chunks und kaltem Anwendungscache ergibt sich:

| Profil | HTTP-Anfragen | Daten-Chunks | Abfragezeit bei 80 ms Zusatzlatenz |
|---|---:|---:|---:|
| IOM | 116 → 12 | 45 → 12 | 10,31 → 1,13 s |
| WKB / direkte GIS-API | 106 → 11 | 40 → 7 | 9,31 → 0,94 s |

Verglichen werden die alte Referenz mit X-Packung und die kombinierte Format-3-Variante mit Hilbert-Anordnung, STR und Vorladen. Öffnen ist in diesen Abfragewerten nicht enthalten. Der stufenweise Vergleich im vollständigen Bericht trennt die einzelnen Effekte.

Beim synthetischen Bestand mit einer Million Punktobjekten wirken vor allem die kompakten Verzeichnisse und FID-Bereiche pro Chunk:

| Profil | Core-Datei Referenz → Format 3 | Änderung |
|---|---:|---:|
| IOM | 90’230’960 → 69’563’961 Bytes | -22.9 % |
| WKB | 194’286’392 → 70’708’591 Bytes | -63.6 % |

Der synthetische Vergleich enthält keinen Spatial Index und keine räumliche Sortierung. Die alte IOM-Referenz besitzt keinen FID-Zugriff; dieser wird als nicht verfügbar ausgewiesen.

## Kosten und Grenzen

- Hilbert ist keine kostenlose Optimierung: Beim Ortschaftenbestand mit IOM steigt die mediane Erstellungszeit von 9,74 auf 12,79 s; der abgetastete temporäre Speicher steigt von rund 224 auf 368 MB.
- Kleine IOM-Bestände werden teilweise grösser: Bei DMAV steigt die indexierte Datei in der kombinierten Variante von 42’289 auf 48’848 Bytes. Die vollständigeren IOM-Metadaten und Formatänderungen fallen hier stärker ins Gewicht.
- Kleinere Chunks sind nicht generell besser. Bei gleicher Hilbert-Anordnung benötigt der vollständige IOM-Klassenabruf 1’583 Anfragen mit 64 KiB, gegenüber 352 mit 256 KiB.
- Grössere Chunks sparen Anfragen, können aber mehr unbenötigte Bytes liefern. Beim mittleren IOM-Fenster benötigt 1 MiB zehn Anfragen und rund 1,38 MB, gegenüber zwölf Anfragen und 0,75 MB bei 256 KiB.
- Die HTTP-Messung verwendet einen lokalen Server mit zusätzlicher Verzögerung, keine begrenzte Netzwerkbandbreite. Kalte und warme Zustände beziehen sich auf den Anwendungscache. Heap-Pool-Spitzen und abgetasteter temporärer Speicher sind Näherungswerte; sie sind keine RSS-Messung.

## Empfehlung

Die festgelegten Standards bleiben bestehen: IOM, 256-KiB-Chunks, Zstandard-Level 3 und STR. Für häufige räumliche Auswahlen ist Hilbert eine sinnvolle ausdrückliche Option. Für direkten GIS-Zugriff wird WKB gewählt; eine pauschale Grössen- oder Geschwindigkeitsgarantie ergibt sich daraus nicht. Chunk-Grössen sollten am tatsächlichen Verhältnis zwischen Einzelzugriffen, räumlichen Fenstern und breiten Klassenabfragen geprüft werden.

[Vollständige Tabellen](README.md) · [Rohmessungen](results.json) · [Hashes und Parameter](run.json)

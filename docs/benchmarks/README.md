# Messergebnisse vom 15. September 2026

Java 21 / macOS arm64. Median aus drei Scans beziehungsweise Zugriffen; Erstellung und Indexaufbau jeweils einmal. Methodik und Einschränkungen: [BENCHMARKS.md](../BENCHMARKS.md).

## Standard: 256 KiB / Zstandard 3

| Datensatz | Objekte gesamt | XTF Bytes | ZIP Bytes | XTF.zst Bytes | Core lexical Bytes | Core decimal Bytes | Spatial-Zusatz lexical Bytes |
|---|---:|---:|---:|---:|---:|---:|---:|
| DMAV Toleranzstufen | 5 | 70626 | 8836 | 8033 | 41739 | 39968 | 688 |
| DMAV Fixpunkte 2542 | 502 | 1017973 | 57846 | 51088 | 154106 | 150189 | 59030 |
| Ortschaften | 8047 | 382750705 | 49213862 | 51686744 | 50490877 | 40674780 | 604275 |

## Vollständiges Lesen

| Datensatz | XTF ms | ZIP ms | XTF.zst ms | Core lexical 256 KiB ms | Core decimal 256 KiB ms |
|---|---:|---:|---:|---:|---:|
| DMAV Toleranzstufen | 2.585 | 2.764 | 2.602 | 0.510 | 0.683 |
| DMAV Fixpunkte 2542 | 11.837 | 12.656 | 12.122 | 4.145 | 5.082 |
| Ortschaften | 2529.615 | 3124.857 | 2681.042 | 2109.780 | 3783.932 |

## Selektiver Standardzugriff

Lexical 256 KiB, Spatial-Datei, kalter Anwendungscache. Die Bytes umfassen Index-, Basket- und Chunkframes, ohne die bereits geöffneten Transfermetadaten. TTFO: Zeit bis zum ersten Objekt.

| Datensatz | Anfrage | Kandidaten/Objekte | Chunks | Bytes | HTTP-Anfragen | Lokal ms | HTTP ms | HTTP TTFO ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| DMAV Toleranzstufen | object | 1 | 1 | 3101 | 6 | 0.131 | 1.397 | 1.388 |
| DMAV Toleranzstufen | basket | 5 | 2 | 9892 | 8 | 0.555 | 2.205 | 1.292 |
| DMAV Toleranzstufen | class | 3 | 1 | 9413 | 6 | 0.501 | 1.845 | 1.556 |
| DMAV Toleranzstufen | bbox-small | 1 | 1 | 7655 | 8 | 1.139 | 3.929 | 3.628 |
| DMAV Toleranzstufen | bbox-medium | 1 | 1 | 7655 | 8 | 0.920 | 2.613 | 2.385 |
| DMAV Toleranzstufen | bbox-large | 3 | 1 | 7655 | 8 | 1.312 | 4.534 | 3.953 |
| DMAV Fixpunkte 2542 | object | 1 | 1 | 31208 | 8 | 0.287 | 1.790 | 1.783 |
| DMAV Fixpunkte 2542 | basket | 502 | 4 | 58079 | 14 | 3.479 | 6.307 | 1.820 |
| DMAV Fixpunkte 2542 | class | 391 | 1 | 28983 | 8 | 1.500 | 4.459 | 2.885 |
| DMAV Fixpunkte 2542 | bbox-small | 0 | 0 | 10374 | 6 | 0.529 | 2.117 | — |
| DMAV Fixpunkte 2542 | bbox-medium | 18 | 1 | 38370 | 12 | 2.193 | 5.537 | 4.087 |
| DMAV Fixpunkte 2542 | bbox-large | 391 | 1 | 77514 | 22 | 4.122 | 10.831 | 8.963 |
| Ortschaften | object | 1 | 1 | 87602 | 10 | 0.600 | 2.901 | 2.898 |
| Ortschaften | basket | 8047 | 702 | 49021295 | 1432 | 2193.242 | 2646.696 | 3.212 |
| Ortschaften | class | 3974 | 349 | 24346390 | 722 | 1069.216 | 1295.816 | 2.548 |
| Ortschaften | bbox-small | 4 | 4 | 327006 | 22 | 9.044 | 13.626 | 5.483 |
| Ortschaften | bbox-medium | 47 | 45 | 3265542 | 116 | 78.567 | 106.546 | 7.591 |
| Ortschaften | bbox-large | 3974 | 349 | 24874583 | 830 | 1106.755 | 1344.702 | 36.655 |

## Kodierungs- und Chunkmatrix

| Datensatz | Variante | Core Bytes | Erstellen ms | Temp-Maximum abgetastet Bytes | Logische TID-Einträge Bytes | Vergleichsdatensätze im Roundtrip |
|---|---|---:|---:|---:|---:|---:|
| DMAV Toleranzstufen | lexical-65536 | 41739 | 912.859 | 1849945 | 565 | 7 |
| DMAV Toleranzstufen | lexical-262144 | 41739 | 897.331 | 1785993 | 565 | 7 |
| DMAV Toleranzstufen | lexical-1048576 | 41739 | 857.499 | 1785993 | 565 | 7 |
| DMAV Toleranzstufen | lexical-4194304 | 41739 | 879.674 | 1785993 | 565 | 7 |
| DMAV Toleranzstufen | decimal-65536 | 39968 | 859.167 | 1785993 | 565 | 7 |
| DMAV Toleranzstufen | decimal-262144 | 39968 | 829.822 | 1849815 | 565 | 7 |
| DMAV Toleranzstufen | decimal-1048576 | 39968 | 800.741 | 1785993 | 565 | 7 |
| DMAV Toleranzstufen | decimal-4194304 | 39968 | 984.819 | 1785993 | 565 | 7 |
| DMAV Fixpunkte 2542 | lexical-65536 | 159216 | 1200.465 | 2159836 | 57182 | 504 |
| DMAV Fixpunkte 2542 | lexical-262144 | 154106 | 1026.687 | 1793191 | 57347 | 504 |
| DMAV Fixpunkte 2542 | lexical-1048576 | 154106 | 1271.826 | 2166919 | 57347 | 504 |
| DMAV Fixpunkte 2542 | lexical-4194304 | 154106 | 1022.246 | 1793191 | 57347 | 504 |
| DMAV Fixpunkte 2542 | decimal-65536 | 155102 | 944.254 | 1793191 | 57182 | 504 |
| DMAV Fixpunkte 2542 | decimal-262144 | 150189 | 1169.646 | 1793191 | 57347 | 504 |
| DMAV Fixpunkte 2542 | decimal-1048576 | 150189 | 1048.562 | 1793191 | 57347 | 504 |
| DMAV Fixpunkte 2542 | decimal-4194304 | 150189 | 907.003 | 1793191 | 57347 | 504 |
| Ortschaften | lexical-65536 | 50124340 | 11019.510 | 228882111 | 940811 | 8049 |
| Ortschaften | lexical-262144 | 50490877 | 9940.897 | 224142281 | 938308 | 8049 |
| Ortschaften | lexical-1048576 | 49331365 | 10276.882 | 225828927 | 936258 | 8049 |
| Ortschaften | lexical-4194304 | 49762526 | 10250.342 | 226152086 | 935562 | 8049 |
| Ortschaften | decimal-65536 | 41765865 | 13134.309 | 209781123 | 940791 | 8049 |
| Ortschaften | decimal-262144 | 40674780 | 12288.935 | 210604884 | 938201 | 8049 |
| Ortschaften | decimal-1048576 | 42499062 | 12336.941 | 212933274 | 936323 | 8049 |
| Ortschaften | decimal-4194304 | 43378912 | 13656.141 | 214493392 | 935556 | 8049 |

## Einordnung

- Kleine Transfers tragen die Modellabbildung und Verzeichnisse relativ stark mit. Für Toleranzstufen ist komprimiertes XTF wesentlich kleiner als der Container.
- Ein Objektzugriff liest in allen gemessenen Varianten genau einen Daten-Chunk. Ein warmer Anwendungscache kann den erneuten Dateizugriff vermeiden; Dekodierung bleibt erforderlich.
- Die räumliche Auswahl liefert vollständige Objekte. Mehrere Kandidaten in einem Chunk werden gemeinsam gelesen; die Indexauswertung garantiert keinen kleinen Byteumfang für jedes Objekt.
- Die Zahlenkodierung ist keine allgemeine Grössenoptimierung: Die JSON-Rohwerte dokumentieren ihre Auswirkung für jeden Datensatz.
- Sämtliche 24 Core-Varianten bestehen den unabhängigen semantischen Vergleich von Original und Export. Die Vergleichszahl enthält Header und Baskets zusätzlich zu den Objekten.

## Rohdaten und Herkunft

- [DMAV Toleranzstufen: JSON](dmav.json)
- [DMAV Fixpunkte 2542: JSON](fixpoints.json)
- [Ortschaften: JSON](localities.json)
- [dmav: Eingabemanifest](dmav-manifest.json)
- [localities: Eingabemanifest](localities-manifest.json)
- [addresses: Eingabemanifest](addresses-manifest.json)
- [pipes: Eingabemanifest](pipes-manifest.json)
- [fixpoints-2542: Eingabemanifest](fixpoints-2542-manifest.json)

Spatial-Indizes des grossen Laufs wurden nach der numerischen Präzisierung erneut aufgebaut. Zugriffswerte wurden nur bei SHA-256-identischer Datei übernommen; dies steht bei den Indexaufbauzeilen im JSON.

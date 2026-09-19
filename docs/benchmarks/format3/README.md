# Format-3-Vergleich

**Status: Abfragematrix 52/52; dreifache Gegenkontrollen 52/52.** Die vollständige Vergleichsmatrix ist abgeschlossen.

Laufzeiten sind Mediane der protokollierten Wiederholungen. Öffnen und Abfragen werden getrennt gemessen. `delay=-1` bezeichnet lokale Zugriffe. Cachezustände beziehen sich auf den Anwendungscache, nicht den Betriebssystemcache.


## Kompakter Vergleich: Referenz → Hilbert + STR, 256 KiB

Diese Übersicht enthält nur vollständig gemessene Paare. Die mittlere zentrale Bounding Box ist `bbox-1`; Zugriffe sind kalt über HTTP ohne künstliche Verzögerung, ohne Öffnen.

| Datensatz / Profil | Dateigrösse Bytes | BBox Requests | BBox Chunks |
|---|---:|---:|---:|
| dmav/iom | 42289 → 48848 | 8 → 3 | 1 → 1 |
| dmav/wkb | 50637 → 49379 | 8 → 3 | 1 → 1 |
| fixpoints/iom | 212989 → 218489 | 12 → 5 | 1 → 1 |
| fixpoints/wkb | 282080 → 221586 | 12 → 5 | 1 → 1 |
| localities/iom | 51095006 → 46610324 | 116 → 12 | 45 → 12 |
| localities/wkb | 45527116 → 39890718 | 106 → 11 | 40 → 7 |

## Vollständiges Variantenraster

Beim synthetischen Millionenbestand wird kein Spatial Index ergänzt; die zweite Grössenangabe entspricht deshalb dem Core. Der Aufbau der obligatorischen B+-Baum-Verzeichnisse ist in der Erstellungszeit enthalten.

| Datensatz / Variante | Vollständig | Core Bytes | mit Index Bytes | Erstellung ms | Roundtrip geprüft |
|---|---:|---:|---:|---:|---:|
| dmav/hilbert-str-iom-1048576 | True | 48131 | 48848 | 791.78 | 7 |
| dmav/hilbert-str-iom-262144 | True | 48131 | 48848 | 767.48 | 7 |
| dmav/hilbert-str-iom-4194304 | True | 48131 | 48848 | 768.12 | 7 |
| dmav/hilbert-str-iom-65536 | True | 48131 | 48848 | 742.43 | 7 |
| dmav/hilbert-str-wkb-1048576 | True | 48662 | 49379 | 786.87 | 7 |
| dmav/hilbert-str-wkb-262144 | True | 48662 | 49379 | 781.18 | 7 |
| dmav/hilbert-str-wkb-4194304 | True | 48662 | 49379 | 735.71 | 7 |
| dmav/hilbert-str-wkb-65536 | True | 48662 | 49379 | 730.67 | 7 |
| dmav/reference-iom-262144 | True | 41601 | 42289 | 766.31 | 7 |
| dmav/reference-wkb-262144 | True | 49949 | 50637 | 786.76 | 7 |
| dmav/str-iom-262144 | True | 48092 | 48809 | 746.61 | 7 |
| dmav/str-wkb-262144 | True | 48587 | 49304 | 684.70 | 7 |
| dmav/x-direct-iom-262144 | True | 48092 | 48807 | 704.13 | 7 |
| dmav/x-direct-wkb-262144 | True | 48587 | 49302 | 705.54 | 7 |
| dmav/x-prefetch-iom-262144 | True | 48092 | 48807 | 729.05 | 7 |
| dmav/x-prefetch-wkb-262144 | True | 48587 | 49302 | 815.75 | 7 |
| fixpoints/hilbert-str-iom-1048576 | True | 159822 | 218489 | 1072.97 | 504 |
| fixpoints/hilbert-str-iom-262144 | True | 159822 | 218489 | 1108.39 | 504 |
| fixpoints/hilbert-str-iom-4194304 | True | 159822 | 218489 | 1273.53 | 504 |
| fixpoints/hilbert-str-iom-65536 | True | 164145 | 222812 | 1037.34 | 504 |
| fixpoints/hilbert-str-wkb-1048576 | True | 162919 | 221586 | 1136.69 | 504 |
| fixpoints/hilbert-str-wkb-262144 | True | 162919 | 221586 | 1160.85 | 504 |
| fixpoints/hilbert-str-wkb-4194304 | True | 162919 | 221586 | 1268.34 | 504 |
| fixpoints/hilbert-str-wkb-65536 | True | 163857 | 222524 | 1044.34 | 504 |
| fixpoints/reference-iom-262144 | True | 153959 | 212989 | 1061.81 | 504 |
| fixpoints/reference-wkb-262144 | True | 222268 | 282080 | 1162.92 | 504 |
| fixpoints/str-iom-262144 | True | 159538 | 218205 | 1174.13 | 504 |
| fixpoints/str-wkb-262144 | True | 162592 | 221259 | 1191.53 | 504 |
| fixpoints/x-direct-iom-262144 | True | 159538 | 218203 | 1011.86 | 504 |
| fixpoints/x-direct-wkb-262144 | True | 162592 | 221257 | 1150.42 | 504 |
| fixpoints/x-prefetch-iom-262144 | True | 159538 | 218203 | 1093.65 | 504 |
| fixpoints/x-prefetch-wkb-262144 | True | 162592 | 221257 | 1226.99 | 504 |
| localities/hilbert-str-iom-1048576 | True | 43711248 | 44304943 | 12404.19 | 8049 |
| localities/hilbert-str-iom-262144 | True | 46016629 | 46610324 | 12788.00 | 8049 |
| localities/hilbert-str-iom-4194304 | True | 43597139 | 44190834 | 12303.12 | 8049 |
| localities/hilbert-str-iom-65536 | True | 46702463 | 47296158 | 12354.47 | 8049 |
| localities/hilbert-str-wkb-1048576 | True | 36892494 | 37486189 | 12028.01 | 8049 |
| localities/hilbert-str-wkb-262144 | True | 39297023 | 39890718 | 11645.78 | 8049 |
| localities/hilbert-str-wkb-4194304 | True | 36484759 | 37078454 | 11334.17 | 8049 |
| localities/hilbert-str-wkb-65536 | True | 41788746 | 42382441 | 11963.77 | 8049 |
| localities/reference-iom-262144 | True | 50490731 | 51095006 | 9739.92 | 8049 |
| localities/reference-wkb-262144 | True | 44923687 | 45527116 | 11320.36 | 8049 |
| localities/str-iom-262144 | True | 49974157 | 50567852 | 9833.81 | 8049 |
| localities/str-wkb-262144 | True | 43816820 | 44410515 | 11127.25 | 8049 |
| localities/x-direct-iom-262144 | True | 49974157 | 50567342 | 10057.80 | 8049 |
| localities/x-direct-wkb-262144 | True | 43816820 | 44410005 | 11754.57 | 8049 |
| localities/x-prefetch-iom-262144 | True | 49974157 | 50567342 | 9706.95 | 8049 |
| localities/x-prefetch-wkb-262144 | True | 43816820 | 44410005 | 11466.75 | 8049 |
| million/reference-iom-262144 | True | 90230960 | 90230960 | 5642.85 | 1000002 |
| million/reference-wkb-262144 | True | 194286392 | 194286392 | 8782.81 | 1000002 |
| million/x-direct-iom-262144 | True | 69563961 | 69563961 | 5616.55 | 1000002 |
| million/x-direct-wkb-262144 | True | 70708591 | 70708591 | 6494.39 | 1000002 |

## Erstellung und Gegenkontrollen

Erstellung, Indexaufbau und Export umfassen nach Abschluss der Gegenkontrollen je drei Beobachtungen; davor sind ihre Mediane vorläufig. Vollscans umfassen drei Wiederholungen. Heapwerte sind Pool-Spitzen, kein RSS. Temporärer Speicher ist abgetastet.

| Datensatz / Variante | Spatial-Index ms | Export ms | Vollscan ms | Erstellung Heap Bytes | Temporärer Speicher Bytes |
|---|---:|---:|---:|---:|---:|
| dmav/hilbert-str-iom-1048576 | 40.07 | 19.23 | 1.48 | 6.86069e+07 | 1.92055e+06 |
| dmav/hilbert-str-iom-262144 | 35.33 | 18.51 | 1.59 | 6.85879e+07 | 1.92055e+06 |
| dmav/hilbert-str-iom-4194304 | 35.44 | 19.71 | 1.47 | 6.82274e+07 | 1.92055e+06 |
| dmav/hilbert-str-iom-65536 | 41.38 | 18.91 | 2.09 | 6.90729e+07 | 1.92055e+06 |
| dmav/hilbert-str-wkb-1048576 | 44.02 | 21.91 | 1.77 | 6.51533e+07 | 1.86676e+06 |
| dmav/hilbert-str-wkb-262144 | 40.08 | 20.48 | 2.06 | 6.70066e+07 | 1.86676e+06 |
| dmav/hilbert-str-wkb-4194304 | 48.42 | 19.15 | 1.57 | 6.53276e+07 | 1.86676e+06 |
| dmav/hilbert-str-wkb-65536 | 36.07 | 20.03 | 2.17 | 6.51289e+07 | 1.86676e+06 |
| dmav/reference-iom-262144 | 38.10 | 21.19 | 1.62 | 6.6032e+07 | 1.85046e+06 |
| dmav/reference-wkb-262144 | 33.41 | 21.44 | 1.71 | 6.60432e+07 | 1.83932e+06 |
| dmav/str-iom-262144 | 43.25 | 18.32 | 2.19 | 6.60715e+07 | 1.85783e+06 |
| dmav/str-wkb-262144 | 43.09 | 18.77 | 2.01 | 6.53462e+07 | 1.83933e+06 |
| dmav/x-direct-iom-262144 | 46.03 | 19.79 | 1.94 | 6.63304e+07 | 1.85732e+06 |
| dmav/x-direct-wkb-262144 | 39.22 | 19.47 | 1.44 | 6.48275e+07 | 1.83933e+06 |
| dmav/x-prefetch-iom-262144 | 46.87 | 19.41 | 2.13 | 6.53761e+07 | 1.85732e+06 |
| dmav/x-prefetch-wkb-262144 | 42.06 | 19.31 | 1.88 | 6.51105e+07 | 1.83933e+06 |
| fixpoints/hilbert-str-iom-1048576 | 75.49 | 49.30 | 10.06 | 1.10513e+08 | 2.30469e+06 |
| fixpoints/hilbert-str-iom-262144 | 76.78 | 39.60 | 5.02 | 9.7458e+07 | 2.30469e+06 |
| fixpoints/hilbert-str-iom-4194304 | 74.79 | 42.41 | 5.01 | 1.10448e+08 | 2.46924e+06 |
| fixpoints/hilbert-str-iom-65536 | 76.93 | 41.54 | 5.31 | 1.10629e+08 | 2.30469e+06 |
| fixpoints/hilbert-str-wkb-1048576 | 78.73 | 41.96 | 5.01 | 1.12838e+08 | 2.1877e+06 |
| fixpoints/hilbert-str-wkb-262144 | 80.51 | 45.07 | 5.12 | 1.1249e+08 | 2.19566e+06 |
| fixpoints/hilbert-str-wkb-4194304 | 78.10 | 46.27 | 6.01 | 1.11922e+08 | 2.30378e+06 |
| fixpoints/hilbert-str-wkb-65536 | 77.60 | 43.19 | 7.26 | 1.11924e+08 | 2.30378e+06 |
| fixpoints/reference-iom-262144 | 55.11 | 47.47 | 5.07 | 1.00116e+08 | 2.14848e+06 |
| fixpoints/reference-wkb-262144 | 47.73 | 42.46 | 5.25 | 1.05784e+08 | 2.15737e+06 |
| fixpoints/str-iom-262144 | 85.88 | 43.17 | 5.96 | 1.00223e+08 | 2.16259e+06 |
| fixpoints/str-wkb-262144 | 84.48 | 42.97 | 5.62 | 1.04968e+08 | 2.15743e+06 |
| fixpoints/x-direct-iom-262144 | 84.38 | 44.76 | 5.26 | 9.99373e+07 | 2.25439e+06 |
| fixpoints/x-direct-wkb-262144 | 83.02 | 45.73 | 7.46 | 1.04818e+08 | 2.13721e+06 |
| fixpoints/x-prefetch-iom-262144 | 90.25 | 48.94 | 7.71 | 1.00284e+08 | 2.18091e+06 |
| fixpoints/x-prefetch-wkb-262144 | 84.52 | 44.94 | 7.69 | 1.00516e+08 | 2.13721e+06 |
| localities/hilbert-str-iom-1048576 | 1542.43 | 3634.77 | 2225.77 | 2.96518e+08 | 3.66533e+08 |
| localities/hilbert-str-iom-262144 | 1597.84 | 3494.09 | 2045.48 | 2.58368e+08 | 3.68363e+08 |
| localities/hilbert-str-iom-4194304 | 1560.36 | 3557.53 | 2115.03 | 3.22921e+08 | 3.65721e+08 |
| localities/hilbert-str-iom-65536 | 1537.89 | 3453.37 | 2224.73 | 2.75757e+08 | 3.69351e+08 |
| localities/hilbert-str-wkb-1048576 | 375.30 | 2262.27 | 968.05 | 2.98172e+08 | 1.63105e+08 |
| localities/hilbert-str-wkb-262144 | 314.81 | 2172.08 | 888.35 | 2.48112e+08 | 1.64205e+08 |
| localities/hilbert-str-wkb-4194304 | 349.59 | 2219.69 | 976.34 | 2.95466e+08 | 1.61121e+08 |
| localities/hilbert-str-wkb-65536 | 363.04 | 2339.09 | 1364.27 | 2.33383e+08 | 1.66778e+08 |
| localities/reference-iom-262144 | 1502.56 | 3682.35 | 1993.17 | 2.52271e+08 | 2.24452e+08 |
| localities/reference-wkb-262144 | 216.47 | 2261.66 | 900.15 | 2.34181e+08 | 1.20537e+08 |
| localities/str-iom-262144 | 1558.23 | 3490.59 | 2102.34 | 2.52588e+08 | 2.25839e+08 |
| localities/str-wkb-262144 | 371.58 | 2292.11 | 950.98 | 2.30357e+08 | 1.19771e+08 |
| localities/x-direct-iom-262144 | 1581.87 | 3824.26 | 2174.40 | 2.48361e+08 | 2.24312e+08 |
| localities/x-direct-wkb-262144 | 337.04 | 2176.01 | 848.14 | 2.52411e+08 | 1.17717e+08 |
| localities/x-prefetch-iom-262144 | 1590.79 | 3561.65 | 2142.35 | 2.52903e+08 | 2.2439e+08 |
| localities/x-prefetch-wkb-262144 | 335.57 | 2260.39 | 905.17 | 2.34849e+08 | 1.19493e+08 |
| million/reference-iom-262144 | n/a | 3683.71 | 752.68 | 2.00869e+08 | 2.81733e+08 |
| million/reference-wkb-262144 | n/a | 3906.53 | 723.47 | 1.96061e+08 | 5.35245e+08 |
| million/x-direct-iom-262144 | n/a | 3825.29 | 750.18 | 2.9952e+08 | 2.46158e+08 |
| million/x-direct-wkb-262144 | n/a | 3873.27 | 737.82 | 3.03114e+08 | 2.90125e+08 |

## Zwanzig reproduzierbare räumliche Fenster

Je Fenster zuerst der Median der drei Wiederholungen, anschliessend der Median über die 20 Fenster. HTTP ohne künstliche Verzögerung, kalter Anwendungscache. Öffnen ist nicht enthalten.

| Datensatz / Variante | ms | Requests | Chunks | Übertragene Bytes | Zusätzliche Zwischenraumbytes |
|---|---:|---:|---:|---:|---:|
| dmav/hilbert-str-iom-1048576 | 1.82 | 3 | 1 | 8187 | 504 |
| dmav/hilbert-str-iom-262144 | 1.95 | 3 | 1 | 8187 | 504 |
| dmav/hilbert-str-iom-4194304 | 1.90 | 3 | 1 | 8187 | 504 |
| dmav/hilbert-str-iom-65536 | 1.96 | 3 | 1 | 8187 | 504 |
| dmav/hilbert-str-wkb-1048576 | 1.49 | 3 | 1 | 8812 | 504 |
| dmav/hilbert-str-wkb-262144 | 2.24 | 3 | 1 | 8812 | 504 |
| dmav/hilbert-str-wkb-4194304 | 1.55 | 3 | 1 | 8812 | 504 |
| dmav/hilbert-str-wkb-65536 | 1.77 | 3 | 1 | 8812 | 504 |
| dmav/reference-iom-262144 | 2.81 | 8 | 1 | 7655 | 0 |
| dmav/reference-wkb-262144 | 3.01 | 8 | 1 | 8254 | 0 |
| dmav/str-iom-262144 | 1.77 | 3 | 1 | 8213 | 504 |
| dmav/str-wkb-262144 | 1.55 | 3 | 1 | 8802 | 504 |
| dmav/x-direct-iom-262144 | 2.06 | 4 | 1 | 7707 | 0 |
| dmav/x-direct-wkb-262144 | 2.45 | 4 | 1 | 8296 | 0 |
| dmav/x-prefetch-iom-262144 | 1.89 | 3 | 1 | 8211 | 504 |
| dmav/x-prefetch-wkb-262144 | 1.65 | 3 | 1 | 8800 | 504 |
| fixpoints/hilbert-str-iom-1048576 | 2.54 | 5 | 1 | 35719 | 0 |
| fixpoints/hilbert-str-iom-262144 | 2.52 | 5 | 1 | 35719 | 0 |
| fixpoints/hilbert-str-iom-4194304 | 2.49 | 5 | 1 | 35719 | 0 |
| fixpoints/hilbert-str-iom-65536 | 2.31 | 5 | 1 | 25356 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | 2.30 | 5 | 1 | 37667 | 0 |
| fixpoints/hilbert-str-wkb-262144 | 3.13 | 5 | 1 | 37667 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | 2.63 | 5 | 1 | 37667 | 0 |
| fixpoints/hilbert-str-wkb-65536 | 2.27 | 5 | 1 | 27648 | 0 |
| fixpoints/reference-iom-262144 | 4.02 | 10 | 1 | 28852 | 0 |
| fixpoints/reference-wkb-262144 | 3.89 | 10 | 1 | 30896 | 0 |
| fixpoints/str-iom-262144 | 2.71 | 5 | 1 | 35505 | 0 |
| fixpoints/str-wkb-262144 | 2.65 | 5 | 1 | 37410 | 0 |
| fixpoints/x-direct-iom-262144 | 2.75 | 5 | 1 | 35503 | 0 |
| fixpoints/x-direct-wkb-262144 | 2.63 | 5 | 1 | 37408 | 0 |
| fixpoints/x-prefetch-iom-262144 | 2.88 | 5 | 1 | 35503 | 0 |
| fixpoints/x-prefetch-wkb-262144 | 2.70 | 5 | 1 | 37408 | 0 |
| localities/hilbert-str-iom-1048576 | 14.39 | 5.5 | 1.5 | 360532 | 0 |
| localities/hilbert-str-iom-262144 | 6.48 | 6 | 2 | 141778 | 0 |
| localities/hilbert-str-iom-4194304 | 39.70 | 5.5 | 1 | 915663 | 0 |
| localities/hilbert-str-iom-65536 | 4.23 | 6 | 4 | 86582 | 0 |
| localities/hilbert-str-wkb-1048576 | 3.61 | 5 | 1 | 470332 | 0 |
| localities/hilbert-str-wkb-262144 | 2.59 | 5.5 | 2 | 256402 | 0 |
| localities/hilbert-str-wkb-4194304 | 7.10 | 5 | 1 | 1.7209e+06 | 0 |
| localities/hilbert-str-wkb-65536 | 2.22 | 6 | 3 | 112330 | 0 |
| localities/reference-iom-262144 | 17.09 | 28 | 6 | 480267 | 0 |
| localities/reference-wkb-262144 | 8.54 | 28 | 6 | 956972 | 0 |
| localities/str-iom-262144 | 13.42 | 11 | 6 | 463607 | 0 |
| localities/str-wkb-262144 | 6.85 | 11 | 6 | 940314 | 0 |
| localities/x-direct-iom-262144 | 14.96 | 12.5 | 6 | 487667 | 0 |
| localities/x-direct-wkb-262144 | 6.09 | 12.5 | 6 | 964374 | 0 |
| localities/x-prefetch-iom-262144 | 15.03 | 12.5 | 6 | 487667 | 0 |
| localities/x-prefetch-wkb-262144 | 6.20 | 12.5 | 6 | 964374 | 0 |

## Selektiver Zugriff

| Datensatz / Variante | Query | Delay ms | Cache | ms | Requests | Bytes | Chunks |
|---|---|---:|---|---:|---:|---:|---:|
| dmav/hilbert-str-iom-1048576 | bbox-0 | -1 | cold | 1.10 | 0 | 8187 | 1 |
| dmav/hilbert-str-iom-1048576 | bbox-0 | -1 | warm | 0.92 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | bbox-0 | 0 | cold | 2.32 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-1048576 | bbox-0 | 0 | warm | 0.74 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | bbox-0 | 20 | cold | 74.51 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-1048576 | bbox-0 | 20 | warm | 1.83 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | bbox-0 | 80 | cold | 259.88 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-1048576 | bbox-0 | 80 | warm | 2.18 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | bbox-1 | -1 | cold | 1.08 | 0 | 8187 | 1 |
| dmav/hilbert-str-iom-1048576 | bbox-1 | -1 | warm | 0.76 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | bbox-1 | 0 | cold | 1.65 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-1048576 | bbox-1 | 0 | warm | 0.65 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | bbox-1 | 20 | cold | 75.22 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-1048576 | bbox-1 | 20 | warm | 1.81 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | bbox-1 | 80 | cold | 257.41 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-1048576 | bbox-1 | 80 | warm | 2.04 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | bbox-2 | -1 | cold | 1.42 | 0 | 8187 | 1 |
| dmav/hilbert-str-iom-1048576 | bbox-2 | -1 | warm | 1.34 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | bbox-2 | 0 | cold | 2.00 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-1048576 | bbox-2 | 0 | warm | 0.95 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | bbox-2 | 20 | cold | 77.03 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-1048576 | bbox-2 | 20 | warm | 3.77 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | bbox-2 | 80 | cold | 259.69 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-1048576 | bbox-2 | 80 | warm | 3.85 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | class | -1 | cold | 0.95 | 0 | 8487 | 1 |
| dmav/hilbert-str-iom-1048576 | class | -1 | warm | 0.86 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | class | 0 | cold | 1.42 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-1048576 | class | 0 | warm | 0.51 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | class | 20 | cold | 75.20 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-1048576 | class | 20 | warm | 1.40 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | class | 80 | cold | 259.95 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-1048576 | class | 80 | warm | 1.95 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | fid | -1 | cold | 0.49 | 0 | 8487 | 1 |
| dmav/hilbert-str-iom-1048576 | fid | -1 | warm | 0.37 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | fid | 0 | cold | 1.16 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-1048576 | fid | 0 | warm | 0.26 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | fid | 20 | cold | 70.86 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-1048576 | fid | 20 | warm | 0.70 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | fid | 80 | cold | 257.34 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-1048576 | fid | 80 | warm | 0.83 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | tid | -1 | cold | 0.53 | 0 | 8487 | 1 |
| dmav/hilbert-str-iom-1048576 | tid | -1 | warm | 0.44 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | tid | 0 | cold | 0.98 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-1048576 | tid | 0 | warm | 0.22 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | tid | 20 | cold | 73.11 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-1048576 | tid | 20 | warm | 0.56 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-1048576 | tid | 80 | cold | 255.77 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-1048576 | tid | 80 | warm | 0.72 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | bbox-0 | -1 | cold | 1.15 | 0 | 8187 | 1 |
| dmav/hilbert-str-iom-262144 | bbox-0 | -1 | warm | 0.93 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | bbox-0 | 0 | cold | 2.41 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-262144 | bbox-0 | 0 | warm | 1.07 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | bbox-0 | 20 | cold | 85.71 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-262144 | bbox-0 | 20 | warm | 2.43 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | bbox-0 | 80 | cold | 258.63 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-262144 | bbox-0 | 80 | warm | 2.69 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | bbox-1 | -1 | cold | 1.06 | 0 | 8187 | 1 |
| dmav/hilbert-str-iom-262144 | bbox-1 | -1 | warm | 0.97 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | bbox-1 | 0 | cold | 1.58 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-262144 | bbox-1 | 0 | warm | 0.87 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | bbox-1 | 20 | cold | 74.53 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-262144 | bbox-1 | 20 | warm | 2.91 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | bbox-1 | 80 | cold | 256.70 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-262144 | bbox-1 | 80 | warm | 4.02 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | bbox-2 | -1 | cold | 1.35 | 0 | 8187 | 1 |
| dmav/hilbert-str-iom-262144 | bbox-2 | -1 | warm | 1.68 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | bbox-2 | 0 | cold | 1.94 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-262144 | bbox-2 | 0 | warm | 1.23 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | bbox-2 | 20 | cold | 81.32 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-262144 | bbox-2 | 20 | warm | 3.27 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | bbox-2 | 80 | cold | 255.52 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-262144 | bbox-2 | 80 | warm | 2.79 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | class | -1 | cold | 0.89 | 0 | 8487 | 1 |
| dmav/hilbert-str-iom-262144 | class | -1 | warm | 0.92 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | class | 0 | cold | 1.21 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-262144 | class | 0 | warm | 0.49 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | class | 20 | cold | 75.15 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-262144 | class | 20 | warm | 2.14 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | class | 80 | cold | 254.27 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-262144 | class | 80 | warm | 1.88 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | fid | -1 | cold | 0.53 | 0 | 8487 | 1 |
| dmav/hilbert-str-iom-262144 | fid | -1 | warm | 0.38 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | fid | 0 | cold | 0.97 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-262144 | fid | 0 | warm | 0.31 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | fid | 20 | cold | 71.84 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-262144 | fid | 20 | warm | 0.46 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | fid | 80 | cold | 255.31 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-262144 | fid | 80 | warm | 0.85 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | tid | -1 | cold | 0.44 | 0 | 8487 | 1 |
| dmav/hilbert-str-iom-262144 | tid | -1 | warm | 0.36 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | tid | 0 | cold | 1.36 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-262144 | tid | 0 | warm | 0.23 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | tid | 20 | cold | 73.70 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-262144 | tid | 20 | warm | 0.44 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-262144 | tid | 80 | cold | 252.32 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-262144 | tid | 80 | warm | 0.68 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | bbox-0 | -1 | cold | 1.05 | 0 | 8187 | 1 |
| dmav/hilbert-str-iom-4194304 | bbox-0 | -1 | warm | 0.80 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | bbox-0 | 0 | cold | 1.81 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-4194304 | bbox-0 | 0 | warm | 0.67 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | bbox-0 | 20 | cold | 78.49 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-4194304 | bbox-0 | 20 | warm | 2.36 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | bbox-0 | 80 | cold | 256.93 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-4194304 | bbox-0 | 80 | warm | 2.17 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | bbox-1 | -1 | cold | 0.96 | 0 | 8187 | 1 |
| dmav/hilbert-str-iom-4194304 | bbox-1 | -1 | warm | 0.86 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | bbox-1 | 0 | cold | 1.97 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-4194304 | bbox-1 | 0 | warm | 0.65 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | bbox-1 | 20 | cold | 78.04 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-4194304 | bbox-1 | 20 | warm | 3.27 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | bbox-1 | 80 | cold | 257.53 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-4194304 | bbox-1 | 80 | warm | 2.24 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | bbox-2 | -1 | cold | 1.50 | 0 | 8187 | 1 |
| dmav/hilbert-str-iom-4194304 | bbox-2 | -1 | warm | 1.53 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | bbox-2 | 0 | cold | 2.04 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-4194304 | bbox-2 | 0 | warm | 1.02 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | bbox-2 | 20 | cold | 72.06 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-4194304 | bbox-2 | 20 | warm | 4.21 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | bbox-2 | 80 | cold | 261.20 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-4194304 | bbox-2 | 80 | warm | 3.88 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | class | -1 | cold | 0.86 | 0 | 8487 | 1 |
| dmav/hilbert-str-iom-4194304 | class | -1 | warm | 0.90 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | class | 0 | cold | 1.40 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-4194304 | class | 0 | warm | 0.49 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | class | 20 | cold | 79.50 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-4194304 | class | 20 | warm | 2.07 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | class | 80 | cold | 253.97 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-4194304 | class | 80 | warm | 1.81 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | fid | -1 | cold | 0.39 | 0 | 8487 | 1 |
| dmav/hilbert-str-iom-4194304 | fid | -1 | warm | 0.36 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | fid | 0 | cold | 1.21 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-4194304 | fid | 0 | warm | 0.24 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | fid | 20 | cold | 76.47 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-4194304 | fid | 20 | warm | 1.09 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | fid | 80 | cold | 256.57 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-4194304 | fid | 80 | warm | 0.92 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | tid | -1 | cold | 0.39 | 0 | 8487 | 1 |
| dmav/hilbert-str-iom-4194304 | tid | -1 | warm | 0.30 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | tid | 0 | cold | 1.35 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-4194304 | tid | 0 | warm | 0.22 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | tid | 20 | cold | 74.86 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-4194304 | tid | 20 | warm | 0.96 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-4194304 | tid | 80 | cold | 255.35 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-4194304 | tid | 80 | warm | 1.14 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | bbox-0 | -1 | cold | 1.05 | 0 | 8187 | 1 |
| dmav/hilbert-str-iom-65536 | bbox-0 | -1 | warm | 0.94 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | bbox-0 | 0 | cold | 1.74 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-65536 | bbox-0 | 0 | warm | 0.78 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | bbox-0 | 20 | cold | 79.60 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-65536 | bbox-0 | 20 | warm | 3.09 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | bbox-0 | 80 | cold | 255.21 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-65536 | bbox-0 | 80 | warm | 2.93 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | bbox-1 | -1 | cold | 1.14 | 0 | 8187 | 1 |
| dmav/hilbert-str-iom-65536 | bbox-1 | -1 | warm | 0.91 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | bbox-1 | 0 | cold | 1.95 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-65536 | bbox-1 | 0 | warm | 0.79 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | bbox-1 | 20 | cold | 82.43 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-65536 | bbox-1 | 20 | warm | 2.95 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | bbox-1 | 80 | cold | 261.10 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-65536 | bbox-1 | 80 | warm | 3.11 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | bbox-2 | -1 | cold | 1.75 | 0 | 8187 | 1 |
| dmav/hilbert-str-iom-65536 | bbox-2 | -1 | warm | 1.31 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | bbox-2 | 0 | cold | 2.55 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-65536 | bbox-2 | 0 | warm | 0.98 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | bbox-2 | 20 | cold | 77.50 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-65536 | bbox-2 | 20 | warm | 3.57 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | bbox-2 | 80 | cold | 260.34 | 3 | 8187 | 1 |
| dmav/hilbert-str-iom-65536 | bbox-2 | 80 | warm | 3.18 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | class | -1 | cold | 1.00 | 0 | 8487 | 1 |
| dmav/hilbert-str-iom-65536 | class | -1 | warm | 0.93 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | class | 0 | cold | 1.30 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-65536 | class | 0 | warm | 0.49 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | class | 20 | cold | 76.82 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-65536 | class | 20 | warm | 1.98 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | class | 80 | cold | 254.32 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-65536 | class | 80 | warm | 1.47 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | fid | -1 | cold | 0.45 | 0 | 8487 | 1 |
| dmav/hilbert-str-iom-65536 | fid | -1 | warm | 0.41 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | fid | 0 | cold | 1.15 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-65536 | fid | 0 | warm | 0.25 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | fid | 20 | cold | 72.23 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-65536 | fid | 20 | warm | 1.43 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | fid | 80 | cold | 256.30 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-65536 | fid | 80 | warm | 0.88 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | tid | -1 | cold | 0.46 | 0 | 8487 | 1 |
| dmav/hilbert-str-iom-65536 | tid | -1 | warm | 0.35 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | tid | 0 | cold | 1.12 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-65536 | tid | 0 | warm | 0.23 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | tid | 20 | cold | 79.46 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-65536 | tid | 20 | warm | 1.00 | 0 | 0 | 0 |
| dmav/hilbert-str-iom-65536 | tid | 80 | cold | 253.36 | 3 | 8487 | 1 |
| dmav/hilbert-str-iom-65536 | tid | 80 | warm | 0.81 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | bbox-0 | -1 | cold | 0.80 | 0 | 8812 | 1 |
| dmav/hilbert-str-wkb-1048576 | bbox-0 | -1 | warm | 0.72 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | bbox-0 | 0 | cold | 1.55 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-1048576 | bbox-0 | 0 | warm | 0.58 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | bbox-0 | 20 | cold | 73.58 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-1048576 | bbox-0 | 20 | warm | 0.92 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | bbox-0 | 80 | cold | 253.70 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-1048576 | bbox-0 | 80 | warm | 2.73 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | bbox-1 | -1 | cold | 1.02 | 0 | 8812 | 1 |
| dmav/hilbert-str-wkb-1048576 | bbox-1 | -1 | warm | 0.62 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | bbox-1 | 0 | cold | 1.69 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-1048576 | bbox-1 | 0 | warm | 0.54 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | bbox-1 | 20 | cold | 75.35 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-1048576 | bbox-1 | 20 | warm | 0.78 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | bbox-1 | 80 | cold | 259.56 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-1048576 | bbox-1 | 80 | warm | 2.24 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | bbox-2 | -1 | cold | 0.89 | 0 | 8812 | 1 |
| dmav/hilbert-str-wkb-1048576 | bbox-2 | -1 | warm | 0.79 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | bbox-2 | 0 | cold | 1.91 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-1048576 | bbox-2 | 0 | warm | 0.61 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | bbox-2 | 20 | cold | 76.81 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-1048576 | bbox-2 | 20 | warm | 2.30 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | bbox-2 | 80 | cold | 255.59 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-1048576 | bbox-2 | 80 | warm | 2.20 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | class | -1 | cold | 0.22 | 0 | 9112 | 1 |
| dmav/hilbert-str-wkb-1048576 | class | -1 | warm | 0.15 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | class | 0 | cold | 1.46 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-1048576 | class | 0 | warm | 0.12 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | class | 20 | cold | 73.95 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-1048576 | class | 20 | warm | 0.28 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | class | 80 | cold | 254.02 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-1048576 | class | 80 | warm | 0.60 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | fid | -1 | cold | 0.30 | 0 | 9112 | 1 |
| dmav/hilbert-str-wkb-1048576 | fid | -1 | warm | 0.15 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | fid | 0 | cold | 0.94 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-1048576 | fid | 0 | warm | 0.12 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | fid | 20 | cold | 75.57 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-1048576 | fid | 20 | warm | 0.26 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | fid | 80 | cold | 251.29 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-1048576 | fid | 80 | warm | 0.45 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | tid | -1 | cold | 0.34 | 0 | 9112 | 1 |
| dmav/hilbert-str-wkb-1048576 | tid | -1 | warm | 0.23 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | tid | 0 | cold | 1.04 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-1048576 | tid | 0 | warm | 0.19 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | tid | 20 | cold | 77.90 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-1048576 | tid | 20 | warm | 0.22 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-1048576 | tid | 80 | cold | 252.00 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-1048576 | tid | 80 | warm | 0.73 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | bbox-0 | -1 | cold | 1.18 | 0 | 8812 | 1 |
| dmav/hilbert-str-wkb-262144 | bbox-0 | -1 | warm | 0.90 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | bbox-0 | 0 | cold | 2.15 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-262144 | bbox-0 | 0 | warm | 1.45 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | bbox-0 | 20 | cold | 74.74 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-262144 | bbox-0 | 20 | warm | 1.63 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | bbox-0 | 80 | cold | 253.32 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-262144 | bbox-0 | 80 | warm | 2.43 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | bbox-1 | -1 | cold | 1.03 | 0 | 8812 | 1 |
| dmav/hilbert-str-wkb-262144 | bbox-1 | -1 | warm | 1.08 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | bbox-1 | 0 | cold | 2.03 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-262144 | bbox-1 | 0 | warm | 0.80 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | bbox-1 | 20 | cold | 82.36 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-262144 | bbox-1 | 20 | warm | 1.83 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | bbox-1 | 80 | cold | 256.61 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-262144 | bbox-1 | 80 | warm | 2.65 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | bbox-2 | -1 | cold | 1.08 | 0 | 8812 | 1 |
| dmav/hilbert-str-wkb-262144 | bbox-2 | -1 | warm | 0.80 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | bbox-2 | 0 | cold | 2.45 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-262144 | bbox-2 | 0 | warm | 0.87 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | bbox-2 | 20 | cold | 72.63 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-262144 | bbox-2 | 20 | warm | 1.60 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | bbox-2 | 80 | cold | 253.66 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-262144 | bbox-2 | 80 | warm | 1.68 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | class | -1 | cold | 0.40 | 0 | 9112 | 1 |
| dmav/hilbert-str-wkb-262144 | class | -1 | warm | 0.25 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | class | 0 | cold | 1.25 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-262144 | class | 0 | warm | 0.16 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | class | 20 | cold | 72.23 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-262144 | class | 20 | warm | 0.31 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | class | 80 | cold | 252.47 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-262144 | class | 80 | warm | 0.31 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | fid | -1 | cold | 0.27 | 0 | 9112 | 1 |
| dmav/hilbert-str-wkb-262144 | fid | -1 | warm | 0.13 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | fid | 0 | cold | 1.21 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-262144 | fid | 0 | warm | 0.12 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | fid | 20 | cold | 74.91 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-262144 | fid | 20 | warm | 0.41 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | fid | 80 | cold | 254.57 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-262144 | fid | 80 | warm | 0.43 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | tid | -1 | cold | 0.38 | 0 | 9112 | 1 |
| dmav/hilbert-str-wkb-262144 | tid | -1 | warm | 0.25 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | tid | 0 | cold | 1.88 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-262144 | tid | 0 | warm | 0.22 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | tid | 20 | cold | 74.50 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-262144 | tid | 20 | warm | 0.55 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-262144 | tid | 80 | cold | 257.16 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-262144 | tid | 80 | warm | 0.55 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | bbox-0 | -1 | cold | 0.93 | 0 | 8812 | 1 |
| dmav/hilbert-str-wkb-4194304 | bbox-0 | -1 | warm | 0.84 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | bbox-0 | 0 | cold | 1.60 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-4194304 | bbox-0 | 0 | warm | 0.53 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | bbox-0 | 20 | cold | 74.08 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-4194304 | bbox-0 | 20 | warm | 2.27 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | bbox-0 | 80 | cold | 258.82 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-4194304 | bbox-0 | 80 | warm | 2.51 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | bbox-1 | -1 | cold | 0.90 | 0 | 8812 | 1 |
| dmav/hilbert-str-wkb-4194304 | bbox-1 | -1 | warm | 0.71 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | bbox-1 | 0 | cold | 1.54 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-4194304 | bbox-1 | 0 | warm | 0.56 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | bbox-1 | 20 | cold | 74.38 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-4194304 | bbox-1 | 20 | warm | 1.00 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | bbox-1 | 80 | cold | 259.66 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-4194304 | bbox-1 | 80 | warm | 2.42 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | bbox-2 | -1 | cold | 0.99 | 0 | 8812 | 1 |
| dmav/hilbert-str-wkb-4194304 | bbox-2 | -1 | warm | 0.75 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | bbox-2 | 0 | cold | 1.55 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-4194304 | bbox-2 | 0 | warm | 0.57 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | bbox-2 | 20 | cold | 72.94 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-4194304 | bbox-2 | 20 | warm | 2.13 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | bbox-2 | 80 | cold | 255.13 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-4194304 | bbox-2 | 80 | warm | 2.54 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | class | -1 | cold | 0.25 | 0 | 9112 | 1 |
| dmav/hilbert-str-wkb-4194304 | class | -1 | warm | 0.16 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | class | 0 | cold | 1.28 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-4194304 | class | 0 | warm | 0.12 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | class | 20 | cold | 75.34 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-4194304 | class | 20 | warm | 0.63 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | class | 80 | cold | 253.19 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-4194304 | class | 80 | warm | 0.49 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | fid | -1 | cold | 0.23 | 0 | 9112 | 1 |
| dmav/hilbert-str-wkb-4194304 | fid | -1 | warm | 0.13 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | fid | 0 | cold | 1.00 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-4194304 | fid | 0 | warm | 0.08 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | fid | 20 | cold | 76.27 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-4194304 | fid | 20 | warm | 0.38 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | fid | 80 | cold | 254.41 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-4194304 | fid | 80 | warm | 0.45 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | tid | -1 | cold | 0.34 | 0 | 9112 | 1 |
| dmav/hilbert-str-wkb-4194304 | tid | -1 | warm | 0.31 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | tid | 0 | cold | 1.23 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-4194304 | tid | 0 | warm | 0.20 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | tid | 20 | cold | 76.45 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-4194304 | tid | 20 | warm | 0.68 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-4194304 | tid | 80 | cold | 253.34 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-4194304 | tid | 80 | warm | 0.72 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | bbox-0 | -1 | cold | 1.83 | 0 | 8812 | 1 |
| dmav/hilbert-str-wkb-65536 | bbox-0 | -1 | warm | 0.88 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | bbox-0 | 0 | cold | 1.64 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-65536 | bbox-0 | 0 | warm | 0.53 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | bbox-0 | 20 | cold | 76.42 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-65536 | bbox-0 | 20 | warm | 1.70 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | bbox-0 | 80 | cold | 258.60 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-65536 | bbox-0 | 80 | warm | 2.40 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | bbox-1 | -1 | cold | 0.83 | 0 | 8812 | 1 |
| dmav/hilbert-str-wkb-65536 | bbox-1 | -1 | warm | 0.71 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | bbox-1 | 0 | cold | 4.16 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-65536 | bbox-1 | 0 | warm | 0.58 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | bbox-1 | 20 | cold | 78.69 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-65536 | bbox-1 | 20 | warm | 1.43 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | bbox-1 | 80 | cold | 266.70 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-65536 | bbox-1 | 80 | warm | 1.91 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | bbox-2 | -1 | cold | 1.08 | 0 | 8812 | 1 |
| dmav/hilbert-str-wkb-65536 | bbox-2 | -1 | warm | 0.78 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | bbox-2 | 0 | cold | 1.76 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-65536 | bbox-2 | 0 | warm | 0.66 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | bbox-2 | 20 | cold | 75.21 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-65536 | bbox-2 | 20 | warm | 2.43 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | bbox-2 | 80 | cold | 260.62 | 3 | 8812 | 1 |
| dmav/hilbert-str-wkb-65536 | bbox-2 | 80 | warm | 2.15 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | class | -1 | cold | 0.51 | 0 | 9112 | 1 |
| dmav/hilbert-str-wkb-65536 | class | -1 | warm | 0.19 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | class | 0 | cold | 0.93 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-65536 | class | 0 | warm | 0.10 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | class | 20 | cold | 70.84 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-65536 | class | 20 | warm | 0.29 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | class | 80 | cold | 254.85 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-65536 | class | 80 | warm | 0.28 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | fid | -1 | cold | 0.24 | 0 | 9112 | 1 |
| dmav/hilbert-str-wkb-65536 | fid | -1 | warm | 0.13 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | fid | 0 | cold | 1.02 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-65536 | fid | 0 | warm | 0.10 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | fid | 20 | cold | 77.55 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-65536 | fid | 20 | warm | 0.27 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | fid | 80 | cold | 255.21 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-65536 | fid | 80 | warm | 0.29 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | tid | -1 | cold | 0.38 | 0 | 9112 | 1 |
| dmav/hilbert-str-wkb-65536 | tid | -1 | warm | 0.24 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | tid | 0 | cold | 1.37 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-65536 | tid | 0 | warm | 0.20 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | tid | 20 | cold | 73.26 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-65536 | tid | 20 | warm | 0.58 | 0 | 0 | 0 |
| dmav/hilbert-str-wkb-65536 | tid | 80 | cold | 254.05 | 3 | 9112 | 1 |
| dmav/hilbert-str-wkb-65536 | tid | 80 | warm | 0.73 | 0 | 0 | 0 |
| dmav/reference-iom-262144 | bbox-0 | -1 | cold | 1.16 | 0 | 7655 | 1 |
| dmav/reference-iom-262144 | bbox-0 | -1 | warm | 0.73 | 0 | 0 | 0 |
| dmav/reference-iom-262144 | bbox-0 | 0 | cold | 2.79 | 8 | 7655 | 1 |
| dmav/reference-iom-262144 | bbox-0 | 0 | warm | 0.70 | 0 | 0 | 0 |
| dmav/reference-iom-262144 | bbox-0 | 20 | cold | 196.02 | 8 | 7655 | 1 |
| dmav/reference-iom-262144 | bbox-0 | 20 | warm | 3.04 | 0 | 0 | 0 |
| dmav/reference-iom-262144 | bbox-0 | 80 | cold | 673.69 | 8 | 7655 | 1 |
| dmav/reference-iom-262144 | bbox-0 | 80 | warm | 3.08 | 0 | 0 | 0 |
| dmav/reference-iom-262144 | bbox-1 | -1 | cold | 0.85 | 0 | 7655 | 1 |
| dmav/reference-iom-262144 | bbox-1 | -1 | warm | 0.68 | 0 | 0 | 0 |
| dmav/reference-iom-262144 | bbox-1 | 0 | cold | 2.83 | 8 | 7655 | 1 |
| dmav/reference-iom-262144 | bbox-1 | 0 | warm | 0.66 | 0 | 0 | 0 |
| dmav/reference-iom-262144 | bbox-1 | 20 | cold | 200.45 | 8 | 7655 | 1 |
| dmav/reference-iom-262144 | bbox-1 | 20 | warm | 3.19 | 0 | 0 | 0 |
| dmav/reference-iom-262144 | bbox-1 | 80 | cold | 684.83 | 8 | 7655 | 1 |
| dmav/reference-iom-262144 | bbox-1 | 80 | warm | 3.65 | 0 | 0 | 0 |
| dmav/reference-iom-262144 | bbox-2 | -1 | cold | 1.23 | 0 | 7655 | 1 |
| dmav/reference-iom-262144 | bbox-2 | -1 | warm | 1.06 | 0 | 0 | 0 |
| dmav/reference-iom-262144 | bbox-2 | 0 | cold | 3.01 | 8 | 7655 | 1 |
| dmav/reference-iom-262144 | bbox-2 | 0 | warm | 1.01 | 0 | 0 | 0 |
| dmav/reference-iom-262144 | bbox-2 | 20 | cold | 203.10 | 8 | 7655 | 1 |
| dmav/reference-iom-262144 | bbox-2 | 20 | warm | 3.70 | 0 | 0 | 0 |
| dmav/reference-iom-262144 | bbox-2 | 80 | cold | 680.85 | 8 | 7655 | 1 |
| dmav/reference-iom-262144 | bbox-2 | 80 | warm | 4.05 | 0 | 0 | 0 |
| dmav/reference-iom-262144 | class | -1 | cold | 0.49 | 0 | 9413 | 1 |
| dmav/reference-iom-262144 | class | -1 | warm | 0.44 | 0 | 0 | 0 |
| dmav/reference-iom-262144 | class | 0 | cold | 1.81 | 6 | 9413 | 1 |
| dmav/reference-iom-262144 | class | 0 | warm | 0.67 | 0 | 0 | 0 |
| dmav/reference-iom-262144 | class | 20 | cold | 149.33 | 6 | 9413 | 1 |
| dmav/reference-iom-262144 | class | 20 | warm | 1.93 | 0 | 0 | 0 |
| dmav/reference-iom-262144 | class | 80 | cold | 511.46 | 6 | 9413 | 1 |
| dmav/reference-iom-262144 | class | 80 | warm | 1.84 | 0 | 0 | 0 |
| dmav/reference-iom-262144 | tid | -1 | cold | 0.31 | 0 | 9413 | 1 |
| dmav/reference-iom-262144 | tid | -1 | warm | 0.23 | 0 | 0 | 0 |
| dmav/reference-iom-262144 | tid | 0 | cold | 1.91 | 6 | 9413 | 1 |
| dmav/reference-iom-262144 | tid | 0 | warm | 0.19 | 0 | 0 | 0 |
| dmav/reference-iom-262144 | tid | 20 | cold | 154.87 | 6 | 9413 | 1 |
| dmav/reference-iom-262144 | tid | 20 | warm | 0.65 | 0 | 0 | 0 |
| dmav/reference-iom-262144 | tid | 80 | cold | 509.32 | 6 | 9413 | 1 |
| dmav/reference-iom-262144 | tid | 80 | warm | 1.28 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | bbox-0 | -1 | cold | 1.80 | 0 | 8254 | 1 |
| dmav/reference-wkb-262144 | bbox-0 | -1 | warm | 0.91 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | bbox-0 | 0 | cold | 3.18 | 8 | 8254 | 1 |
| dmav/reference-wkb-262144 | bbox-0 | 0 | warm | 0.63 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | bbox-0 | 20 | cold | 200.36 | 8 | 8254 | 1 |
| dmav/reference-wkb-262144 | bbox-0 | 20 | warm | 3.04 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | bbox-0 | 80 | cold | 681.19 | 8 | 8254 | 1 |
| dmav/reference-wkb-262144 | bbox-0 | 80 | warm | 2.58 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | bbox-1 | -1 | cold | 0.99 | 0 | 8254 | 1 |
| dmav/reference-wkb-262144 | bbox-1 | -1 | warm | 0.69 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | bbox-1 | 0 | cold | 3.08 | 8 | 8254 | 1 |
| dmav/reference-wkb-262144 | bbox-1 | 0 | warm | 0.60 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | bbox-1 | 20 | cold | 199.50 | 8 | 8254 | 1 |
| dmav/reference-wkb-262144 | bbox-1 | 20 | warm | 3.13 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | bbox-1 | 80 | cold | 686.19 | 8 | 8254 | 1 |
| dmav/reference-wkb-262144 | bbox-1 | 80 | warm | 3.20 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | bbox-2 | -1 | cold | 1.68 | 0 | 8254 | 1 |
| dmav/reference-wkb-262144 | bbox-2 | -1 | warm | 0.97 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | bbox-2 | 0 | cold | 3.83 | 8 | 8254 | 1 |
| dmav/reference-wkb-262144 | bbox-2 | 0 | warm | 0.73 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | bbox-2 | 20 | cold | 202.61 | 8 | 8254 | 1 |
| dmav/reference-wkb-262144 | bbox-2 | 20 | warm | 1.61 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | bbox-2 | 80 | cold | 686.41 | 8 | 8254 | 1 |
| dmav/reference-wkb-262144 | bbox-2 | 80 | warm | 5.35 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | class | -1 | cold | 0.29 | 0 | 10517 | 1 |
| dmav/reference-wkb-262144 | class | -1 | warm | 0.15 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | class | 0 | cold | 1.87 | 6 | 10517 | 1 |
| dmav/reference-wkb-262144 | class | 0 | warm | 0.11 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | class | 20 | cold | 148.02 | 6 | 10517 | 1 |
| dmav/reference-wkb-262144 | class | 20 | warm | 0.44 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | class | 80 | cold | 507.73 | 6 | 10517 | 1 |
| dmav/reference-wkb-262144 | class | 80 | warm | 0.47 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | fid | -1 | cold | 1.40 | 0 | 10517 | 1 |
| dmav/reference-wkb-262144 | fid | -1 | warm | 0.19 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | fid | 0 | cold | 2.65 | 6 | 10517 | 1 |
| dmav/reference-wkb-262144 | fid | 0 | warm | 0.19 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | fid | 20 | cold | 145.84 | 6 | 10517 | 1 |
| dmav/reference-wkb-262144 | fid | 20 | warm | 0.30 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | fid | 80 | cold | 505.41 | 6 | 10517 | 1 |
| dmav/reference-wkb-262144 | fid | 80 | warm | 0.38 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | tid | -1 | cold | 0.39 | 0 | 10517 | 1 |
| dmav/reference-wkb-262144 | tid | -1 | warm | 0.23 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | tid | 0 | cold | 2.62 | 6 | 10517 | 1 |
| dmav/reference-wkb-262144 | tid | 0 | warm | 0.20 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | tid | 20 | cold | 143.61 | 6 | 10517 | 1 |
| dmav/reference-wkb-262144 | tid | 20 | warm | 0.41 | 0 | 0 | 0 |
| dmav/reference-wkb-262144 | tid | 80 | cold | 511.30 | 6 | 10517 | 1 |
| dmav/reference-wkb-262144 | tid | 80 | warm | 0.55 | 0 | 0 | 0 |
| dmav/str-iom-262144 | bbox-0 | -1 | cold | 1.00 | 0 | 8213 | 1 |
| dmav/str-iom-262144 | bbox-0 | -1 | warm | 0.82 | 0 | 0 | 0 |
| dmav/str-iom-262144 | bbox-0 | 0 | cold | 1.75 | 3 | 8213 | 1 |
| dmav/str-iom-262144 | bbox-0 | 0 | warm | 0.75 | 0 | 0 | 0 |
| dmav/str-iom-262144 | bbox-0 | 20 | cold | 74.56 | 3 | 8213 | 1 |
| dmav/str-iom-262144 | bbox-0 | 20 | warm | 2.60 | 0 | 0 | 0 |
| dmav/str-iom-262144 | bbox-0 | 80 | cold | 258.86 | 3 | 8213 | 1 |
| dmav/str-iom-262144 | bbox-0 | 80 | warm | 2.64 | 0 | 0 | 0 |
| dmav/str-iom-262144 | bbox-1 | -1 | cold | 1.07 | 0 | 8213 | 1 |
| dmav/str-iom-262144 | bbox-1 | -1 | warm | 0.71 | 0 | 0 | 0 |
| dmav/str-iom-262144 | bbox-1 | 0 | cold | 1.52 | 3 | 8213 | 1 |
| dmav/str-iom-262144 | bbox-1 | 0 | warm | 0.66 | 0 | 0 | 0 |
| dmav/str-iom-262144 | bbox-1 | 20 | cold | 76.40 | 3 | 8213 | 1 |
| dmav/str-iom-262144 | bbox-1 | 20 | warm | 1.90 | 0 | 0 | 0 |
| dmav/str-iom-262144 | bbox-1 | 80 | cold | 258.72 | 3 | 8213 | 1 |
| dmav/str-iom-262144 | bbox-1 | 80 | warm | 2.88 | 0 | 0 | 0 |
| dmav/str-iom-262144 | bbox-2 | -1 | cold | 1.28 | 0 | 8213 | 1 |
| dmav/str-iom-262144 | bbox-2 | -1 | warm | 1.42 | 0 | 0 | 0 |
| dmav/str-iom-262144 | bbox-2 | 0 | cold | 2.48 | 3 | 8213 | 1 |
| dmav/str-iom-262144 | bbox-2 | 0 | warm | 1.02 | 0 | 0 | 0 |
| dmav/str-iom-262144 | bbox-2 | 20 | cold | 78.57 | 3 | 8213 | 1 |
| dmav/str-iom-262144 | bbox-2 | 20 | warm | 2.67 | 0 | 0 | 0 |
| dmav/str-iom-262144 | bbox-2 | 80 | cold | 260.43 | 3 | 8213 | 1 |
| dmav/str-iom-262144 | bbox-2 | 80 | warm | 4.21 | 0 | 0 | 0 |
| dmav/str-iom-262144 | class | -1 | cold | 0.68 | 0 | 8513 | 1 |
| dmav/str-iom-262144 | class | -1 | warm | 0.61 | 0 | 0 | 0 |
| dmav/str-iom-262144 | class | 0 | cold | 1.22 | 3 | 8513 | 1 |
| dmav/str-iom-262144 | class | 0 | warm | 0.54 | 0 | 0 | 0 |
| dmav/str-iom-262144 | class | 20 | cold | 79.03 | 3 | 8513 | 1 |
| dmav/str-iom-262144 | class | 20 | warm | 1.77 | 0 | 0 | 0 |
| dmav/str-iom-262144 | class | 80 | cold | 257.28 | 3 | 8513 | 1 |
| dmav/str-iom-262144 | class | 80 | warm | 1.82 | 0 | 0 | 0 |
| dmav/str-iom-262144 | fid | -1 | cold | 0.36 | 0 | 8513 | 1 |
| dmav/str-iom-262144 | fid | -1 | warm | 0.30 | 0 | 0 | 0 |
| dmav/str-iom-262144 | fid | 0 | cold | 0.98 | 3 | 8513 | 1 |
| dmav/str-iom-262144 | fid | 0 | warm | 0.26 | 0 | 0 | 0 |
| dmav/str-iom-262144 | fid | 20 | cold | 74.88 | 3 | 8513 | 1 |
| dmav/str-iom-262144 | fid | 20 | warm | 0.91 | 0 | 0 | 0 |
| dmav/str-iom-262144 | fid | 80 | cold | 255.34 | 3 | 8513 | 1 |
| dmav/str-iom-262144 | fid | 80 | warm | 0.89 | 0 | 0 | 0 |
| dmav/str-iom-262144 | tid | -1 | cold | 0.41 | 0 | 8513 | 1 |
| dmav/str-iom-262144 | tid | -1 | warm | 0.29 | 0 | 0 | 0 |
| dmav/str-iom-262144 | tid | 0 | cold | 1.18 | 3 | 8513 | 1 |
| dmav/str-iom-262144 | tid | 0 | warm | 0.23 | 0 | 0 | 0 |
| dmav/str-iom-262144 | tid | 20 | cold | 77.11 | 3 | 8513 | 1 |
| dmav/str-iom-262144 | tid | 20 | warm | 0.75 | 0 | 0 | 0 |
| dmav/str-iom-262144 | tid | 80 | cold | 258.17 | 3 | 8513 | 1 |
| dmav/str-iom-262144 | tid | 80 | warm | 0.91 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | bbox-0 | -1 | cold | 0.84 | 0 | 8802 | 1 |
| dmav/str-wkb-262144 | bbox-0 | -1 | warm | 0.60 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | bbox-0 | 0 | cold | 1.61 | 3 | 8802 | 1 |
| dmav/str-wkb-262144 | bbox-0 | 0 | warm | 0.55 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | bbox-0 | 20 | cold | 80.81 | 3 | 8802 | 1 |
| dmav/str-wkb-262144 | bbox-0 | 20 | warm | 2.23 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | bbox-0 | 80 | cold | 258.38 | 3 | 8802 | 1 |
| dmav/str-wkb-262144 | bbox-0 | 80 | warm | 2.52 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | bbox-1 | -1 | cold | 0.74 | 0 | 8802 | 1 |
| dmav/str-wkb-262144 | bbox-1 | -1 | warm | 0.62 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | bbox-1 | 0 | cold | 1.70 | 3 | 8802 | 1 |
| dmav/str-wkb-262144 | bbox-1 | 0 | warm | 0.53 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | bbox-1 | 20 | cold | 74.35 | 3 | 8802 | 1 |
| dmav/str-wkb-262144 | bbox-1 | 20 | warm | 2.58 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | bbox-1 | 80 | cold | 254.83 | 3 | 8802 | 1 |
| dmav/str-wkb-262144 | bbox-1 | 80 | warm | 2.36 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | bbox-2 | -1 | cold | 0.88 | 0 | 8802 | 1 |
| dmav/str-wkb-262144 | bbox-2 | -1 | warm | 0.71 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | bbox-2 | 0 | cold | 1.81 | 3 | 8802 | 1 |
| dmav/str-wkb-262144 | bbox-2 | 0 | warm | 0.57 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | bbox-2 | 20 | cold | 76.19 | 3 | 8802 | 1 |
| dmav/str-wkb-262144 | bbox-2 | 20 | warm | 2.35 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | bbox-2 | 80 | cold | 254.34 | 3 | 8802 | 1 |
| dmav/str-wkb-262144 | bbox-2 | 80 | warm | 2.16 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | class | -1 | cold | 0.22 | 0 | 9102 | 1 |
| dmav/str-wkb-262144 | class | -1 | warm | 0.15 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | class | 0 | cold | 0.96 | 3 | 9102 | 1 |
| dmav/str-wkb-262144 | class | 0 | warm | 0.10 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | class | 20 | cold | 74.91 | 3 | 9102 | 1 |
| dmav/str-wkb-262144 | class | 20 | warm | 0.40 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | class | 80 | cold | 253.64 | 3 | 9102 | 1 |
| dmav/str-wkb-262144 | class | 80 | warm | 0.44 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | fid | -1 | cold | 0.22 | 0 | 9102 | 1 |
| dmav/str-wkb-262144 | fid | -1 | warm | 0.12 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | fid | 0 | cold | 1.02 | 3 | 9102 | 1 |
| dmav/str-wkb-262144 | fid | 0 | warm | 0.09 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | fid | 20 | cold | 74.81 | 3 | 9102 | 1 |
| dmav/str-wkb-262144 | fid | 20 | warm | 0.30 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | fid | 80 | cold | 248.94 | 3 | 9102 | 1 |
| dmav/str-wkb-262144 | fid | 80 | warm | 0.43 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | tid | -1 | cold | 0.37 | 0 | 9102 | 1 |
| dmav/str-wkb-262144 | tid | -1 | warm | 0.29 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | tid | 0 | cold | 1.22 | 3 | 9102 | 1 |
| dmav/str-wkb-262144 | tid | 0 | warm | 0.20 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | tid | 20 | cold | 76.66 | 3 | 9102 | 1 |
| dmav/str-wkb-262144 | tid | 20 | warm | 0.83 | 0 | 0 | 0 |
| dmav/str-wkb-262144 | tid | 80 | cold | 254.49 | 3 | 9102 | 1 |
| dmav/str-wkb-262144 | tid | 80 | warm | 0.86 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | bbox-0 | -1 | cold | 1.02 | 0 | 7707 | 1 |
| dmav/x-direct-iom-262144 | bbox-0 | -1 | warm | 0.85 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | bbox-0 | 0 | cold | 1.84 | 4 | 7707 | 1 |
| dmav/x-direct-iom-262144 | bbox-0 | 0 | warm | 0.70 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | bbox-0 | 20 | cold | 98.08 | 4 | 7707 | 1 |
| dmav/x-direct-iom-262144 | bbox-0 | 20 | warm | 1.76 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | bbox-0 | 80 | cold | 342.73 | 4 | 7707 | 1 |
| dmav/x-direct-iom-262144 | bbox-0 | 80 | warm | 2.54 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | bbox-1 | -1 | cold | 0.98 | 0 | 7707 | 1 |
| dmav/x-direct-iom-262144 | bbox-1 | -1 | warm | 0.74 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | bbox-1 | 0 | cold | 2.19 | 4 | 7707 | 1 |
| dmav/x-direct-iom-262144 | bbox-1 | 0 | warm | 0.65 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | bbox-1 | 20 | cold | 103.22 | 4 | 7707 | 1 |
| dmav/x-direct-iom-262144 | bbox-1 | 20 | warm | 2.30 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | bbox-1 | 80 | cold | 341.52 | 4 | 7707 | 1 |
| dmav/x-direct-iom-262144 | bbox-1 | 80 | warm | 3.38 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | bbox-2 | -1 | cold | 1.43 | 0 | 7707 | 1 |
| dmav/x-direct-iom-262144 | bbox-2 | -1 | warm | 1.53 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | bbox-2 | 0 | cold | 2.86 | 4 | 7707 | 1 |
| dmav/x-direct-iom-262144 | bbox-2 | 0 | warm | 0.98 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | bbox-2 | 20 | cold | 103.08 | 4 | 7707 | 1 |
| dmav/x-direct-iom-262144 | bbox-2 | 20 | warm | 2.96 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | bbox-2 | 80 | cold | 341.70 | 4 | 7707 | 1 |
| dmav/x-direct-iom-262144 | bbox-2 | 80 | warm | 3.97 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | class | -1 | cold | 0.83 | 0 | 8513 | 1 |
| dmav/x-direct-iom-262144 | class | -1 | warm | 0.88 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | class | 0 | cold | 1.39 | 3 | 8513 | 1 |
| dmav/x-direct-iom-262144 | class | 0 | warm | 0.47 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | class | 20 | cold | 74.36 | 3 | 8513 | 1 |
| dmav/x-direct-iom-262144 | class | 20 | warm | 1.52 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | class | 80 | cold | 256.14 | 3 | 8513 | 1 |
| dmav/x-direct-iom-262144 | class | 80 | warm | 1.35 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | fid | -1 | cold | 0.56 | 0 | 8513 | 1 |
| dmav/x-direct-iom-262144 | fid | -1 | warm | 0.36 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | fid | 0 | cold | 0.99 | 3 | 8513 | 1 |
| dmav/x-direct-iom-262144 | fid | 0 | warm | 0.24 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | fid | 20 | cold | 77.98 | 3 | 8513 | 1 |
| dmav/x-direct-iom-262144 | fid | 20 | warm | 0.58 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | fid | 80 | cold | 250.64 | 3 | 8513 | 1 |
| dmav/x-direct-iom-262144 | fid | 80 | warm | 1.10 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | tid | -1 | cold | 0.46 | 0 | 8513 | 1 |
| dmav/x-direct-iom-262144 | tid | -1 | warm | 0.32 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | tid | 0 | cold | 1.23 | 3 | 8513 | 1 |
| dmav/x-direct-iom-262144 | tid | 0 | warm | 0.23 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | tid | 20 | cold | 76.17 | 3 | 8513 | 1 |
| dmav/x-direct-iom-262144 | tid | 20 | warm | 0.60 | 0 | 0 | 0 |
| dmav/x-direct-iom-262144 | tid | 80 | cold | 250.50 | 3 | 8513 | 1 |
| dmav/x-direct-iom-262144 | tid | 80 | warm | 0.75 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | bbox-0 | -1 | cold | 1.09 | 0 | 8296 | 1 |
| dmav/x-direct-wkb-262144 | bbox-0 | -1 | warm | 0.68 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | bbox-0 | 0 | cold | 2.19 | 4 | 8296 | 1 |
| dmav/x-direct-wkb-262144 | bbox-0 | 0 | warm | 0.75 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | bbox-0 | 20 | cold | 99.39 | 4 | 8296 | 1 |
| dmav/x-direct-wkb-262144 | bbox-0 | 20 | warm | 1.71 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | bbox-0 | 80 | cold | 338.45 | 4 | 8296 | 1 |
| dmav/x-direct-wkb-262144 | bbox-0 | 80 | warm | 2.08 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | bbox-1 | -1 | cold | 0.97 | 0 | 8296 | 1 |
| dmav/x-direct-wkb-262144 | bbox-1 | -1 | warm | 0.92 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | bbox-1 | 0 | cold | 3.46 | 4 | 8296 | 1 |
| dmav/x-direct-wkb-262144 | bbox-1 | 0 | warm | 0.76 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | bbox-1 | 20 | cold | 98.76 | 4 | 8296 | 1 |
| dmav/x-direct-wkb-262144 | bbox-1 | 20 | warm | 1.46 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | bbox-1 | 80 | cold | 342.88 | 4 | 8296 | 1 |
| dmav/x-direct-wkb-262144 | bbox-1 | 80 | warm | 2.35 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | bbox-2 | -1 | cold | 1.16 | 0 | 8296 | 1 |
| dmav/x-direct-wkb-262144 | bbox-2 | -1 | warm | 1.59 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | bbox-2 | 0 | cold | 2.80 | 4 | 8296 | 1 |
| dmav/x-direct-wkb-262144 | bbox-2 | 0 | warm | 0.85 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | bbox-2 | 20 | cold | 100.32 | 4 | 8296 | 1 |
| dmav/x-direct-wkb-262144 | bbox-2 | 20 | warm | 1.48 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | bbox-2 | 80 | cold | 339.49 | 4 | 8296 | 1 |
| dmav/x-direct-wkb-262144 | bbox-2 | 80 | warm | 1.51 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | class | -1 | cold | 0.29 | 0 | 9102 | 1 |
| dmav/x-direct-wkb-262144 | class | -1 | warm | 0.20 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | class | 0 | cold | 1.67 | 3 | 9102 | 1 |
| dmav/x-direct-wkb-262144 | class | 0 | warm | 0.13 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | class | 20 | cold | 69.77 | 3 | 9102 | 1 |
| dmav/x-direct-wkb-262144 | class | 20 | warm | 0.24 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | class | 80 | cold | 254.18 | 3 | 9102 | 1 |
| dmav/x-direct-wkb-262144 | class | 80 | warm | 0.37 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | fid | -1 | cold | 1.00 | 0 | 9102 | 1 |
| dmav/x-direct-wkb-262144 | fid | -1 | warm | 0.20 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | fid | 0 | cold | 1.80 | 3 | 9102 | 1 |
| dmav/x-direct-wkb-262144 | fid | 0 | warm | 0.25 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | fid | 20 | cold | 78.04 | 3 | 9102 | 1 |
| dmav/x-direct-wkb-262144 | fid | 20 | warm | 0.27 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | fid | 80 | cold | 254.25 | 3 | 9102 | 1 |
| dmav/x-direct-wkb-262144 | fid | 80 | warm | 0.80 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | tid | -1 | cold | 0.64 | 0 | 9102 | 1 |
| dmav/x-direct-wkb-262144 | tid | -1 | warm | 0.75 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | tid | 0 | cold | 1.35 | 3 | 9102 | 1 |
| dmav/x-direct-wkb-262144 | tid | 0 | warm | 0.22 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | tid | 20 | cold | 73.21 | 3 | 9102 | 1 |
| dmav/x-direct-wkb-262144 | tid | 20 | warm | 0.39 | 0 | 0 | 0 |
| dmav/x-direct-wkb-262144 | tid | 80 | cold | 254.77 | 3 | 9102 | 1 |
| dmav/x-direct-wkb-262144 | tid | 80 | warm | 0.43 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | bbox-0 | -1 | cold | 1.28 | 0 | 8211 | 1 |
| dmav/x-prefetch-iom-262144 | bbox-0 | -1 | warm | 0.92 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | bbox-0 | 0 | cold | 1.68 | 3 | 8211 | 1 |
| dmav/x-prefetch-iom-262144 | bbox-0 | 0 | warm | 1.19 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | bbox-0 | 20 | cold | 76.56 | 3 | 8211 | 1 |
| dmav/x-prefetch-iom-262144 | bbox-0 | 20 | warm | 3.18 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | bbox-0 | 80 | cold | 253.20 | 3 | 8211 | 1 |
| dmav/x-prefetch-iom-262144 | bbox-0 | 80 | warm | 3.14 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | bbox-1 | -1 | cold | 1.08 | 0 | 8211 | 1 |
| dmav/x-prefetch-iom-262144 | bbox-1 | -1 | warm | 0.94 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | bbox-1 | 0 | cold | 1.82 | 3 | 8211 | 1 |
| dmav/x-prefetch-iom-262144 | bbox-1 | 0 | warm | 0.64 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | bbox-1 | 20 | cold | 79.88 | 3 | 8211 | 1 |
| dmav/x-prefetch-iom-262144 | bbox-1 | 20 | warm | 2.48 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | bbox-1 | 80 | cold | 254.90 | 3 | 8211 | 1 |
| dmav/x-prefetch-iom-262144 | bbox-1 | 80 | warm | 3.21 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | bbox-2 | -1 | cold | 1.62 | 0 | 8211 | 1 |
| dmav/x-prefetch-iom-262144 | bbox-2 | -1 | warm | 1.41 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | bbox-2 | 0 | cold | 1.86 | 3 | 8211 | 1 |
| dmav/x-prefetch-iom-262144 | bbox-2 | 0 | warm | 1.00 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | bbox-2 | 20 | cold | 80.23 | 3 | 8211 | 1 |
| dmav/x-prefetch-iom-262144 | bbox-2 | 20 | warm | 2.91 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | bbox-2 | 80 | cold | 263.04 | 3 | 8211 | 1 |
| dmav/x-prefetch-iom-262144 | bbox-2 | 80 | warm | 3.23 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | class | -1 | cold | 0.91 | 0 | 8513 | 1 |
| dmav/x-prefetch-iom-262144 | class | -1 | warm | 0.85 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | class | 0 | cold | 1.32 | 3 | 8513 | 1 |
| dmav/x-prefetch-iom-262144 | class | 0 | warm | 0.47 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | class | 20 | cold | 80.23 | 3 | 8513 | 1 |
| dmav/x-prefetch-iom-262144 | class | 20 | warm | 1.82 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | class | 80 | cold | 258.22 | 3 | 8513 | 1 |
| dmav/x-prefetch-iom-262144 | class | 80 | warm | 1.96 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | fid | -1 | cold | 0.43 | 0 | 8513 | 1 |
| dmav/x-prefetch-iom-262144 | fid | -1 | warm | 0.42 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | fid | 0 | cold | 1.01 | 3 | 8513 | 1 |
| dmav/x-prefetch-iom-262144 | fid | 0 | warm | 0.23 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | fid | 20 | cold | 74.75 | 3 | 8513 | 1 |
| dmav/x-prefetch-iom-262144 | fid | 20 | warm | 0.86 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | fid | 80 | cold | 255.63 | 3 | 8513 | 1 |
| dmav/x-prefetch-iom-262144 | fid | 80 | warm | 0.84 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | tid | -1 | cold | 0.54 | 0 | 8513 | 1 |
| dmav/x-prefetch-iom-262144 | tid | -1 | warm | 0.39 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | tid | 0 | cold | 1.06 | 3 | 8513 | 1 |
| dmav/x-prefetch-iom-262144 | tid | 0 | warm | 0.23 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | tid | 20 | cold | 75.81 | 3 | 8513 | 1 |
| dmav/x-prefetch-iom-262144 | tid | 20 | warm | 0.94 | 0 | 0 | 0 |
| dmav/x-prefetch-iom-262144 | tid | 80 | cold | 257.13 | 3 | 8513 | 1 |
| dmav/x-prefetch-iom-262144 | tid | 80 | warm | 0.63 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | bbox-0 | -1 | cold | 1.08 | 0 | 8800 | 1 |
| dmav/x-prefetch-wkb-262144 | bbox-0 | -1 | warm | 0.71 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | bbox-0 | 0 | cold | 1.60 | 3 | 8800 | 1 |
| dmav/x-prefetch-wkb-262144 | bbox-0 | 0 | warm | 0.48 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | bbox-0 | 20 | cold | 73.68 | 3 | 8800 | 1 |
| dmav/x-prefetch-wkb-262144 | bbox-0 | 20 | warm | 1.38 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | bbox-0 | 80 | cold | 258.39 | 3 | 8800 | 1 |
| dmav/x-prefetch-wkb-262144 | bbox-0 | 80 | warm | 2.67 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | bbox-1 | -1 | cold | 1.08 | 0 | 8800 | 1 |
| dmav/x-prefetch-wkb-262144 | bbox-1 | -1 | warm | 0.67 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | bbox-1 | 0 | cold | 1.70 | 3 | 8800 | 1 |
| dmav/x-prefetch-wkb-262144 | bbox-1 | 0 | warm | 0.60 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | bbox-1 | 20 | cold | 76.51 | 3 | 8800 | 1 |
| dmav/x-prefetch-wkb-262144 | bbox-1 | 20 | warm | 1.50 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | bbox-1 | 80 | cold | 255.52 | 3 | 8800 | 1 |
| dmav/x-prefetch-wkb-262144 | bbox-1 | 80 | warm | 2.08 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | bbox-2 | -1 | cold | 1.25 | 0 | 8800 | 1 |
| dmav/x-prefetch-wkb-262144 | bbox-2 | -1 | warm | 0.76 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | bbox-2 | 0 | cold | 1.96 | 3 | 8800 | 1 |
| dmav/x-prefetch-wkb-262144 | bbox-2 | 0 | warm | 0.62 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | bbox-2 | 20 | cold | 76.15 | 3 | 8800 | 1 |
| dmav/x-prefetch-wkb-262144 | bbox-2 | 20 | warm | 1.94 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | bbox-2 | 80 | cold | 260.09 | 3 | 8800 | 1 |
| dmav/x-prefetch-wkb-262144 | bbox-2 | 80 | warm | 2.01 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | class | -1 | cold | 0.25 | 0 | 9102 | 1 |
| dmav/x-prefetch-wkb-262144 | class | -1 | warm | 0.16 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | class | 0 | cold | 1.04 | 3 | 9102 | 1 |
| dmav/x-prefetch-wkb-262144 | class | 0 | warm | 0.11 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | class | 20 | cold | 73.39 | 3 | 9102 | 1 |
| dmav/x-prefetch-wkb-262144 | class | 20 | warm | 0.23 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | class | 80 | cold | 258.29 | 3 | 9102 | 1 |
| dmav/x-prefetch-wkb-262144 | class | 80 | warm | 0.57 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | fid | -1 | cold | 0.24 | 0 | 9102 | 1 |
| dmav/x-prefetch-wkb-262144 | fid | -1 | warm | 0.13 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | fid | 0 | cold | 1.54 | 3 | 9102 | 1 |
| dmav/x-prefetch-wkb-262144 | fid | 0 | warm | 0.12 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | fid | 20 | cold | 77.41 | 3 | 9102 | 1 |
| dmav/x-prefetch-wkb-262144 | fid | 20 | warm | 0.32 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | fid | 80 | cold | 253.22 | 3 | 9102 | 1 |
| dmav/x-prefetch-wkb-262144 | fid | 80 | warm | 0.27 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | tid | -1 | cold | 0.37 | 0 | 9102 | 1 |
| dmav/x-prefetch-wkb-262144 | tid | -1 | warm | 0.25 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | tid | 0 | cold | 1.07 | 3 | 9102 | 1 |
| dmav/x-prefetch-wkb-262144 | tid | 0 | warm | 0.21 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | tid | 20 | cold | 77.82 | 3 | 9102 | 1 |
| dmav/x-prefetch-wkb-262144 | tid | 20 | warm | 0.36 | 0 | 0 | 0 |
| dmav/x-prefetch-wkb-262144 | tid | 80 | cold | 259.63 | 3 | 9102 | 1 |
| dmav/x-prefetch-wkb-262144 | tid | 80 | warm | 0.69 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | bbox-0 | -1 | cold | 0.49 | 0 | 16995 | 0 |
| fixpoints/hilbert-str-iom-1048576 | bbox-0 | -1 | warm | 0.33 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | bbox-0 | 0 | cold | 1.13 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-iom-1048576 | bbox-0 | 0 | warm | 0.26 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | bbox-0 | 20 | cold | 71.88 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-iom-1048576 | bbox-0 | 20 | warm | 0.70 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | bbox-0 | 80 | cold | 257.38 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-iom-1048576 | bbox-0 | 80 | warm | 1.11 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | bbox-1 | -1 | cold | 2.22 | 0 | 35719 | 1 |
| fixpoints/hilbert-str-iom-1048576 | bbox-1 | -1 | warm | 2.52 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | bbox-1 | 0 | cold | 3.58 | 5 | 35719 | 1 |
| fixpoints/hilbert-str-iom-1048576 | bbox-1 | 0 | warm | 1.95 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | bbox-1 | 20 | cold | 124.42 | 5 | 35719 | 1 |
| fixpoints/hilbert-str-iom-1048576 | bbox-1 | 20 | warm | 3.15 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | bbox-1 | 80 | cold | 430.55 | 5 | 35719 | 1 |
| fixpoints/hilbert-str-iom-1048576 | bbox-1 | 80 | warm | 2.91 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | bbox-2 | -1 | cold | 5.70 | 0 | 77391 | 1 |
| fixpoints/hilbert-str-iom-1048576 | bbox-2 | -1 | warm | 5.01 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | bbox-2 | 0 | cold | 6.13 | 8 | 77391 | 1 |
| fixpoints/hilbert-str-iom-1048576 | bbox-2 | 0 | warm | 3.78 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | bbox-2 | 20 | cold | 206.94 | 8 | 77391 | 1 |
| fixpoints/hilbert-str-iom-1048576 | bbox-2 | 20 | warm | 5.17 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | bbox-2 | 80 | cold | 690.60 | 8 | 77391 | 1 |
| fixpoints/hilbert-str-iom-1048576 | bbox-2 | 80 | warm | 8.47 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | class | -1 | cold | 1.56 | 0 | 35355 | 1 |
| fixpoints/hilbert-str-iom-1048576 | class | -1 | warm | 1.78 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | class | 0 | cold | 2.50 | 4 | 35355 | 1 |
| fixpoints/hilbert-str-iom-1048576 | class | 0 | warm | 1.43 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | class | 20 | cold | 104.21 | 4 | 35355 | 1 |
| fixpoints/hilbert-str-iom-1048576 | class | 20 | warm | 2.73 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | class | 80 | cold | 347.07 | 4 | 35355 | 1 |
| fixpoints/hilbert-str-iom-1048576 | class | 80 | warm | 4.41 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | fid | -1 | cold | 1.57 | 0 | 35355 | 1 |
| fixpoints/hilbert-str-iom-1048576 | fid | -1 | warm | 1.38 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | fid | 0 | cold | 2.53 | 4 | 35355 | 1 |
| fixpoints/hilbert-str-iom-1048576 | fid | 0 | warm | 1.36 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | fid | 20 | cold | 100.30 | 4 | 35355 | 1 |
| fixpoints/hilbert-str-iom-1048576 | fid | 20 | warm | 3.80 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | fid | 80 | cold | 346.61 | 4 | 35355 | 1 |
| fixpoints/hilbert-str-iom-1048576 | fid | 80 | warm | 3.96 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | tid | -1 | cold | 1.49 | 0 | 35358 | 1 |
| fixpoints/hilbert-str-iom-1048576 | tid | -1 | warm | 1.42 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | tid | 0 | cold | 2.78 | 4 | 35358 | 1 |
| fixpoints/hilbert-str-iom-1048576 | tid | 0 | warm | 1.34 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | tid | 20 | cold | 97.73 | 4 | 35358 | 1 |
| fixpoints/hilbert-str-iom-1048576 | tid | 20 | warm | 3.14 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-1048576 | tid | 80 | cold | 344.92 | 4 | 35358 | 1 |
| fixpoints/hilbert-str-iom-1048576 | tid | 80 | warm | 3.91 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | bbox-0 | -1 | cold | 0.56 | 0 | 16995 | 0 |
| fixpoints/hilbert-str-iom-262144 | bbox-0 | -1 | warm | 0.37 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | bbox-0 | 0 | cold | 1.13 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-iom-262144 | bbox-0 | 0 | warm | 0.23 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | bbox-0 | 20 | cold | 75.05 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-iom-262144 | bbox-0 | 20 | warm | 1.13 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | bbox-0 | 80 | cold | 256.06 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-iom-262144 | bbox-0 | 80 | warm | 0.94 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | bbox-1 | -1 | cold | 2.30 | 0 | 35719 | 1 |
| fixpoints/hilbert-str-iom-262144 | bbox-1 | -1 | warm | 2.30 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | bbox-1 | 0 | cold | 3.26 | 5 | 35719 | 1 |
| fixpoints/hilbert-str-iom-262144 | bbox-1 | 0 | warm | 1.91 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | bbox-1 | 20 | cold | 131.78 | 5 | 35719 | 1 |
| fixpoints/hilbert-str-iom-262144 | bbox-1 | 20 | warm | 5.04 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | bbox-1 | 80 | cold | 433.72 | 5 | 35719 | 1 |
| fixpoints/hilbert-str-iom-262144 | bbox-1 | 80 | warm | 5.02 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | bbox-2 | -1 | cold | 6.55 | 0 | 77391 | 1 |
| fixpoints/hilbert-str-iom-262144 | bbox-2 | -1 | warm | 5.26 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | bbox-2 | 0 | cold | 5.69 | 8 | 77391 | 1 |
| fixpoints/hilbert-str-iom-262144 | bbox-2 | 0 | warm | 3.23 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | bbox-2 | 20 | cold | 213.63 | 8 | 77391 | 1 |
| fixpoints/hilbert-str-iom-262144 | bbox-2 | 20 | warm | 7.86 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | bbox-2 | 80 | cold | 689.90 | 8 | 77391 | 1 |
| fixpoints/hilbert-str-iom-262144 | bbox-2 | 80 | warm | 6.56 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | class | -1 | cold | 1.66 | 0 | 35355 | 1 |
| fixpoints/hilbert-str-iom-262144 | class | -1 | warm | 1.46 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | class | 0 | cold | 2.73 | 4 | 35355 | 1 |
| fixpoints/hilbert-str-iom-262144 | class | 0 | warm | 1.43 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | class | 20 | cold | 105.64 | 4 | 35355 | 1 |
| fixpoints/hilbert-str-iom-262144 | class | 20 | warm | 4.14 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | class | 80 | cold | 345.59 | 4 | 35355 | 1 |
| fixpoints/hilbert-str-iom-262144 | class | 80 | warm | 4.26 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | fid | -1 | cold | 1.50 | 0 | 35355 | 1 |
| fixpoints/hilbert-str-iom-262144 | fid | -1 | warm | 1.42 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | fid | 0 | cold | 2.53 | 4 | 35355 | 1 |
| fixpoints/hilbert-str-iom-262144 | fid | 0 | warm | 1.36 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | fid | 20 | cold | 104.66 | 4 | 35355 | 1 |
| fixpoints/hilbert-str-iom-262144 | fid | 20 | warm | 3.73 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | fid | 80 | cold | 347.73 | 4 | 35355 | 1 |
| fixpoints/hilbert-str-iom-262144 | fid | 80 | warm | 3.32 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | tid | -1 | cold | 1.46 | 0 | 35358 | 1 |
| fixpoints/hilbert-str-iom-262144 | tid | -1 | warm | 1.39 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | tid | 0 | cold | 2.64 | 4 | 35358 | 1 |
| fixpoints/hilbert-str-iom-262144 | tid | 0 | warm | 1.32 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | tid | 20 | cold | 105.55 | 4 | 35358 | 1 |
| fixpoints/hilbert-str-iom-262144 | tid | 20 | warm | 3.99 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-262144 | tid | 80 | cold | 342.30 | 4 | 35358 | 1 |
| fixpoints/hilbert-str-iom-262144 | tid | 80 | warm | 3.89 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | bbox-0 | -1 | cold | 0.54 | 0 | 16995 | 0 |
| fixpoints/hilbert-str-iom-4194304 | bbox-0 | -1 | warm | 0.38 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | bbox-0 | 0 | cold | 1.30 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-iom-4194304 | bbox-0 | 0 | warm | 0.26 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | bbox-0 | 20 | cold | 74.91 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-iom-4194304 | bbox-0 | 20 | warm | 1.27 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | bbox-0 | 80 | cold | 256.31 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-iom-4194304 | bbox-0 | 80 | warm | 1.07 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | bbox-1 | -1 | cold | 2.19 | 0 | 35719 | 1 |
| fixpoints/hilbert-str-iom-4194304 | bbox-1 | -1 | warm | 2.26 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | bbox-1 | 0 | cold | 3.73 | 5 | 35719 | 1 |
| fixpoints/hilbert-str-iom-4194304 | bbox-1 | 0 | warm | 2.05 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | bbox-1 | 20 | cold | 133.49 | 5 | 35719 | 1 |
| fixpoints/hilbert-str-iom-4194304 | bbox-1 | 20 | warm | 5.30 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | bbox-1 | 80 | cold | 437.56 | 5 | 35719 | 1 |
| fixpoints/hilbert-str-iom-4194304 | bbox-1 | 80 | warm | 5.57 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | bbox-2 | -1 | cold | 5.66 | 0 | 77391 | 1 |
| fixpoints/hilbert-str-iom-4194304 | bbox-2 | -1 | warm | 4.62 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | bbox-2 | 0 | cold | 5.87 | 8 | 77391 | 1 |
| fixpoints/hilbert-str-iom-4194304 | bbox-2 | 0 | warm | 3.38 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | bbox-2 | 20 | cold | 200.87 | 8 | 77391 | 1 |
| fixpoints/hilbert-str-iom-4194304 | bbox-2 | 20 | warm | 7.75 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | bbox-2 | 80 | cold | 706.27 | 8 | 77391 | 1 |
| fixpoints/hilbert-str-iom-4194304 | bbox-2 | 80 | warm | 8.82 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | class | -1 | cold | 2.09 | 0 | 35355 | 1 |
| fixpoints/hilbert-str-iom-4194304 | class | -1 | warm | 1.45 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | class | 0 | cold | 2.59 | 4 | 35355 | 1 |
| fixpoints/hilbert-str-iom-4194304 | class | 0 | warm | 1.44 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | class | 20 | cold | 103.86 | 4 | 35355 | 1 |
| fixpoints/hilbert-str-iom-4194304 | class | 20 | warm | 4.62 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | class | 80 | cold | 344.13 | 4 | 35355 | 1 |
| fixpoints/hilbert-str-iom-4194304 | class | 80 | warm | 4.20 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | fid | -1 | cold | 1.48 | 0 | 35355 | 1 |
| fixpoints/hilbert-str-iom-4194304 | fid | -1 | warm | 1.35 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | fid | 0 | cold | 2.58 | 4 | 35355 | 1 |
| fixpoints/hilbert-str-iom-4194304 | fid | 0 | warm | 1.41 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | fid | 20 | cold | 100.99 | 4 | 35355 | 1 |
| fixpoints/hilbert-str-iom-4194304 | fid | 20 | warm | 4.12 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | fid | 80 | cold | 342.29 | 4 | 35355 | 1 |
| fixpoints/hilbert-str-iom-4194304 | fid | 80 | warm | 4.33 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | tid | -1 | cold | 1.41 | 0 | 35358 | 1 |
| fixpoints/hilbert-str-iom-4194304 | tid | -1 | warm | 1.68 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | tid | 0 | cold | 2.88 | 4 | 35358 | 1 |
| fixpoints/hilbert-str-iom-4194304 | tid | 0 | warm | 1.45 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | tid | 20 | cold | 100.89 | 4 | 35358 | 1 |
| fixpoints/hilbert-str-iom-4194304 | tid | 20 | warm | 3.94 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-4194304 | tid | 80 | cold | 348.92 | 4 | 35358 | 1 |
| fixpoints/hilbert-str-iom-4194304 | tid | 80 | warm | 3.99 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | bbox-0 | -1 | cold | 2.13 | 0 | 16995 | 0 |
| fixpoints/hilbert-str-iom-65536 | bbox-0 | -1 | warm | 0.49 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | bbox-0 | 0 | cold | 1.53 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-iom-65536 | bbox-0 | 0 | warm | 0.23 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | bbox-0 | 20 | cold | 78.31 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-iom-65536 | bbox-0 | 20 | warm | 1.34 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | bbox-0 | 80 | cold | 256.42 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-iom-65536 | bbox-0 | 80 | warm | 0.83 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | bbox-1 | -1 | cold | 2.43 | 0 | 36141 | 2 |
| fixpoints/hilbert-str-iom-65536 | bbox-1 | -1 | warm | 2.07 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | bbox-1 | 0 | cold | 3.37 | 5 | 36141 | 2 |
| fixpoints/hilbert-str-iom-65536 | bbox-1 | 0 | warm | 1.67 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | bbox-1 | 20 | cold | 126.57 | 5 | 36141 | 2 |
| fixpoints/hilbert-str-iom-65536 | bbox-1 | 20 | warm | 4.07 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | bbox-1 | 80 | cold | 433.93 | 5 | 36141 | 2 |
| fixpoints/hilbert-str-iom-65536 | bbox-1 | 80 | warm | 4.50 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | bbox-2 | -1 | cold | 5.82 | 0 | 77813 | 2 |
| fixpoints/hilbert-str-iom-65536 | bbox-2 | -1 | warm | 5.99 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | bbox-2 | 0 | cold | 6.86 | 9 | 77813 | 2 |
| fixpoints/hilbert-str-iom-65536 | bbox-2 | 0 | warm | 3.63 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | bbox-2 | 20 | cold | 235.36 | 9 | 77813 | 2 |
| fixpoints/hilbert-str-iom-65536 | bbox-2 | 20 | warm | 8.63 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | bbox-2 | 80 | cold | 774.62 | 9 | 77813 | 2 |
| fixpoints/hilbert-str-iom-65536 | bbox-2 | 80 | warm | 9.37 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | class | -1 | cold | 1.61 | 0 | 35775 | 2 |
| fixpoints/hilbert-str-iom-65536 | class | -1 | warm | 1.53 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | class | 0 | cold | 3.10 | 5 | 35775 | 2 |
| fixpoints/hilbert-str-iom-65536 | class | 0 | warm | 1.53 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | class | 20 | cold | 126.09 | 5 | 35775 | 2 |
| fixpoints/hilbert-str-iom-65536 | class | 20 | warm | 4.82 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | class | 80 | cold | 431.14 | 5 | 35775 | 2 |
| fixpoints/hilbert-str-iom-65536 | class | 80 | warm | 5.72 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | fid | -1 | cold | 0.64 | 0 | 24052 | 1 |
| fixpoints/hilbert-str-iom-65536 | fid | -1 | warm | 0.57 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | fid | 0 | cold | 1.72 | 4 | 24052 | 1 |
| fixpoints/hilbert-str-iom-65536 | fid | 0 | warm | 0.59 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | fid | 20 | cold | 105.22 | 4 | 24052 | 1 |
| fixpoints/hilbert-str-iom-65536 | fid | 20 | warm | 2.04 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | fid | 80 | cold | 336.53 | 4 | 24052 | 1 |
| fixpoints/hilbert-str-iom-65536 | fid | 80 | warm | 1.98 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | tid | -1 | cold | 0.67 | 0 | 24059 | 1 |
| fixpoints/hilbert-str-iom-65536 | tid | -1 | warm | 0.76 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | tid | 0 | cold | 1.90 | 4 | 24059 | 1 |
| fixpoints/hilbert-str-iom-65536 | tid | 0 | warm | 0.54 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | tid | 20 | cold | 101.94 | 4 | 24059 | 1 |
| fixpoints/hilbert-str-iom-65536 | tid | 20 | warm | 1.75 | 0 | 0 | 0 |
| fixpoints/hilbert-str-iom-65536 | tid | 80 | cold | 345.31 | 4 | 24059 | 1 |
| fixpoints/hilbert-str-iom-65536 | tid | 80 | warm | 2.03 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-0 | -1 | cold | 0.58 | 0 | 16995 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-0 | -1 | warm | 0.48 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-0 | 0 | cold | 1.13 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-0 | 0 | warm | 0.27 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-0 | 20 | cold | 72.94 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-0 | 20 | warm | 0.48 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-0 | 80 | cold | 252.61 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-0 | 80 | warm | 0.89 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-1 | -1 | cold | 2.61 | 0 | 37667 | 1 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-1 | -1 | warm | 2.44 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-1 | 0 | cold | 3.36 | 5 | 37667 | 1 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-1 | 0 | warm | 1.78 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-1 | 20 | cold | 128.39 | 5 | 37667 | 1 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-1 | 20 | warm | 3.98 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-1 | 80 | cold | 432.77 | 5 | 37667 | 1 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-1 | 80 | warm | 4.89 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-2 | -1 | cold | 9.32 | 0 | 79339 | 1 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-2 | -1 | warm | 9.04 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-2 | 0 | cold | 6.11 | 8 | 79339 | 1 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-2 | 0 | warm | 4.62 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-2 | 20 | cold | 204.87 | 8 | 79339 | 1 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-2 | 20 | warm | 5.75 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-2 | 80 | cold | 681.60 | 8 | 79339 | 1 |
| fixpoints/hilbert-str-wkb-1048576 | bbox-2 | 80 | warm | 8.90 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | class | -1 | cold | 5.04 | 0 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-1048576 | class | -1 | warm | 3.55 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | class | 0 | cold | 3.27 | 4 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-1048576 | class | 0 | warm | 1.82 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | class | 20 | cold | 103.88 | 4 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-1048576 | class | 20 | warm | 4.43 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | class | 80 | cold | 343.92 | 4 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-1048576 | class | 80 | warm | 8.20 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | fid | -1 | cold | 1.35 | 0 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-1048576 | fid | -1 | warm | 1.11 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | fid | 0 | cold | 2.30 | 4 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-1048576 | fid | 0 | warm | 1.08 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | fid | 20 | cold | 101.53 | 4 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-1048576 | fid | 20 | warm | 1.69 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | fid | 80 | cold | 343.96 | 4 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-1048576 | fid | 80 | warm | 2.83 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | tid | -1 | cold | 1.93 | 0 | 37306 | 1 |
| fixpoints/hilbert-str-wkb-1048576 | tid | -1 | warm | 1.77 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | tid | 0 | cold | 2.90 | 4 | 37306 | 1 |
| fixpoints/hilbert-str-wkb-1048576 | tid | 0 | warm | 1.57 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | tid | 20 | cold | 105.44 | 4 | 37306 | 1 |
| fixpoints/hilbert-str-wkb-1048576 | tid | 20 | warm | 3.29 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-1048576 | tid | 80 | cold | 341.43 | 4 | 37306 | 1 |
| fixpoints/hilbert-str-wkb-1048576 | tid | 80 | warm | 3.48 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | bbox-0 | -1 | cold | 0.84 | 0 | 16995 | 0 |
| fixpoints/hilbert-str-wkb-262144 | bbox-0 | -1 | warm | 0.58 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | bbox-0 | 0 | cold | 1.75 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-wkb-262144 | bbox-0 | 0 | warm | 0.45 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | bbox-0 | 20 | cold | 78.53 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-wkb-262144 | bbox-0 | 20 | warm | 1.18 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | bbox-0 | 80 | cold | 270.31 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-wkb-262144 | bbox-0 | 80 | warm | 1.54 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | bbox-1 | -1 | cold | 2.84 | 0 | 37667 | 1 |
| fixpoints/hilbert-str-wkb-262144 | bbox-1 | -1 | warm | 2.62 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | bbox-1 | 0 | cold | 5.48 | 5 | 37667 | 1 |
| fixpoints/hilbert-str-wkb-262144 | bbox-1 | 0 | warm | 2.47 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | bbox-1 | 20 | cold | 142.12 | 5 | 37667 | 1 |
| fixpoints/hilbert-str-wkb-262144 | bbox-1 | 20 | warm | 5.65 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | bbox-1 | 80 | cold | 456.15 | 5 | 37667 | 1 |
| fixpoints/hilbert-str-wkb-262144 | bbox-1 | 80 | warm | 5.88 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | bbox-2 | -1 | cold | 12.45 | 0 | 79339 | 1 |
| fixpoints/hilbert-str-wkb-262144 | bbox-2 | -1 | warm | 10.09 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | bbox-2 | 0 | cold | 9.46 | 8 | 79339 | 1 |
| fixpoints/hilbert-str-wkb-262144 | bbox-2 | 0 | warm | 7.79 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | bbox-2 | 20 | cold | 229.99 | 8 | 79339 | 1 |
| fixpoints/hilbert-str-wkb-262144 | bbox-2 | 20 | warm | 8.41 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | bbox-2 | 80 | cold | 719.70 | 8 | 79339 | 1 |
| fixpoints/hilbert-str-wkb-262144 | bbox-2 | 80 | warm | 8.73 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | class | -1 | cold | 6.26 | 0 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-262144 | class | -1 | warm | 4.54 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | class | 0 | cold | 4.36 | 4 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-262144 | class | 0 | warm | 2.90 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | class | 20 | cold | 115.82 | 4 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-262144 | class | 20 | warm | 4.77 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | class | 80 | cold | 355.41 | 4 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-262144 | class | 80 | warm | 4.83 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | fid | -1 | cold | 1.76 | 0 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-262144 | fid | -1 | warm | 1.50 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | fid | 0 | cold | 3.18 | 4 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-262144 | fid | 0 | warm | 1.61 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | fid | 20 | cold | 120.38 | 4 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-262144 | fid | 20 | warm | 2.82 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | fid | 80 | cold | 362.95 | 4 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-262144 | fid | 80 | warm | 3.57 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | tid | -1 | cold | 2.54 | 0 | 37306 | 1 |
| fixpoints/hilbert-str-wkb-262144 | tid | -1 | warm | 2.30 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | tid | 0 | cold | 3.97 | 4 | 37306 | 1 |
| fixpoints/hilbert-str-wkb-262144 | tid | 0 | warm | 2.22 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | tid | 20 | cold | 112.50 | 4 | 37306 | 1 |
| fixpoints/hilbert-str-wkb-262144 | tid | 20 | warm | 3.68 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-262144 | tid | 80 | cold | 360.37 | 4 | 37306 | 1 |
| fixpoints/hilbert-str-wkb-262144 | tid | 80 | warm | 2.72 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-0 | -1 | cold | 0.86 | 0 | 16995 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-0 | -1 | warm | 0.41 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-0 | 0 | cold | 1.73 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-0 | 0 | warm | 0.29 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-0 | 20 | cold | 74.29 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-0 | 20 | warm | 0.80 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-0 | 80 | cold | 257.85 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-0 | 80 | warm | 0.70 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-1 | -1 | cold | 2.09 | 0 | 37667 | 1 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-1 | -1 | warm | 2.68 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-1 | 0 | cold | 3.84 | 5 | 37667 | 1 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-1 | 0 | warm | 1.71 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-1 | 20 | cold | 127.83 | 5 | 37667 | 1 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-1 | 20 | warm | 4.32 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-1 | 80 | cold | 434.72 | 5 | 37667 | 1 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-1 | 80 | warm | 5.24 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-2 | -1 | cold | 8.07 | 0 | 79339 | 1 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-2 | -1 | warm | 7.49 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-2 | 0 | cold | 7.01 | 8 | 79339 | 1 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-2 | 0 | warm | 5.03 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-2 | 20 | cold | 208.01 | 8 | 79339 | 1 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-2 | 20 | warm | 8.26 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-2 | 80 | cold | 689.80 | 8 | 79339 | 1 |
| fixpoints/hilbert-str-wkb-4194304 | bbox-2 | 80 | warm | 8.01 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | class | -1 | cold | 3.53 | 0 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-4194304 | class | -1 | warm | 4.21 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | class | 0 | cold | 3.67 | 4 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-4194304 | class | 0 | warm | 2.69 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | class | 20 | cold | 105.36 | 4 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-4194304 | class | 20 | warm | 4.28 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | class | 80 | cold | 347.49 | 4 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-4194304 | class | 80 | warm | 5.60 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | fid | -1 | cold | 1.29 | 0 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-4194304 | fid | -1 | warm | 1.84 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | fid | 0 | cold | 2.46 | 4 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-4194304 | fid | 0 | warm | 1.13 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | fid | 20 | cold | 101.82 | 4 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-4194304 | fid | 20 | warm | 2.68 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | fid | 80 | cold | 345.27 | 4 | 37303 | 1 |
| fixpoints/hilbert-str-wkb-4194304 | fid | 80 | warm | 2.88 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | tid | -1 | cold | 2.03 | 0 | 37306 | 1 |
| fixpoints/hilbert-str-wkb-4194304 | tid | -1 | warm | 2.44 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | tid | 0 | cold | 3.32 | 4 | 37306 | 1 |
| fixpoints/hilbert-str-wkb-4194304 | tid | 0 | warm | 1.63 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | tid | 20 | cold | 97.30 | 4 | 37306 | 1 |
| fixpoints/hilbert-str-wkb-4194304 | tid | 20 | warm | 2.50 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-4194304 | tid | 80 | cold | 342.63 | 4 | 37306 | 1 |
| fixpoints/hilbert-str-wkb-4194304 | tid | 80 | warm | 2.85 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | bbox-0 | -1 | cold | 0.57 | 0 | 16995 | 0 |
| fixpoints/hilbert-str-wkb-65536 | bbox-0 | -1 | warm | 0.41 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | bbox-0 | 0 | cold | 1.32 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-wkb-65536 | bbox-0 | 0 | warm | 0.28 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | bbox-0 | 20 | cold | 75.20 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-wkb-65536 | bbox-0 | 20 | warm | 0.55 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | bbox-0 | 80 | cold | 260.55 | 3 | 16995 | 0 |
| fixpoints/hilbert-str-wkb-65536 | bbox-0 | 80 | warm | 0.68 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | bbox-1 | -1 | cold | 1.97 | 0 | 38336 | 2 |
| fixpoints/hilbert-str-wkb-65536 | bbox-1 | -1 | warm | 2.58 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | bbox-1 | 0 | cold | 3.41 | 5 | 38336 | 2 |
| fixpoints/hilbert-str-wkb-65536 | bbox-1 | 0 | warm | 1.65 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | bbox-1 | 20 | cold | 128.26 | 5 | 38336 | 2 |
| fixpoints/hilbert-str-wkb-65536 | bbox-1 | 20 | warm | 3.67 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | bbox-1 | 80 | cold | 428.18 | 5 | 38336 | 2 |
| fixpoints/hilbert-str-wkb-65536 | bbox-1 | 80 | warm | 3.88 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | bbox-2 | -1 | cold | 8.37 | 0 | 80008 | 2 |
| fixpoints/hilbert-str-wkb-65536 | bbox-2 | -1 | warm | 6.91 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | bbox-2 | 0 | cold | 7.24 | 9 | 80008 | 2 |
| fixpoints/hilbert-str-wkb-65536 | bbox-2 | 0 | warm | 4.19 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | bbox-2 | 20 | cold | 227.93 | 9 | 80008 | 2 |
| fixpoints/hilbert-str-wkb-65536 | bbox-2 | 20 | warm | 6.20 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | bbox-2 | 80 | cold | 778.38 | 9 | 80008 | 2 |
| fixpoints/hilbert-str-wkb-65536 | bbox-2 | 80 | warm | 9.64 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | class | -1 | cold | 3.80 | 0 | 37972 | 2 |
| fixpoints/hilbert-str-wkb-65536 | class | -1 | warm | 4.44 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | class | 0 | cold | 4.96 | 5 | 37972 | 2 |
| fixpoints/hilbert-str-wkb-65536 | class | 0 | warm | 3.02 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | class | 20 | cold | 123.88 | 5 | 37972 | 2 |
| fixpoints/hilbert-str-wkb-65536 | class | 20 | warm | 4.44 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | class | 80 | cold | 426.22 | 5 | 37972 | 2 |
| fixpoints/hilbert-str-wkb-65536 | class | 80 | warm | 2.07 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | fid | -1 | cold | 0.72 | 0 | 27284 | 1 |
| fixpoints/hilbert-str-wkb-65536 | fid | -1 | warm | 0.64 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | fid | 0 | cold | 1.78 | 4 | 27284 | 1 |
| fixpoints/hilbert-str-wkb-65536 | fid | 0 | warm | 0.55 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | fid | 20 | cold | 100.04 | 4 | 27284 | 1 |
| fixpoints/hilbert-str-wkb-65536 | fid | 20 | warm | 1.20 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | fid | 80 | cold | 341.04 | 4 | 27284 | 1 |
| fixpoints/hilbert-str-wkb-65536 | fid | 80 | warm | 1.34 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | tid | -1 | cold | 1.41 | 0 | 27290 | 1 |
| fixpoints/hilbert-str-wkb-65536 | tid | -1 | warm | 0.94 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | tid | 0 | cold | 2.09 | 4 | 27290 | 1 |
| fixpoints/hilbert-str-wkb-65536 | tid | 0 | warm | 0.90 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | tid | 20 | cold | 97.26 | 4 | 27290 | 1 |
| fixpoints/hilbert-str-wkb-65536 | tid | 20 | warm | 2.26 | 0 | 0 | 0 |
| fixpoints/hilbert-str-wkb-65536 | tid | 80 | cold | 344.74 | 4 | 27290 | 1 |
| fixpoints/hilbert-str-wkb-65536 | tid | 80 | warm | 1.94 | 0 | 0 | 0 |
| fixpoints/reference-iom-262144 | bbox-0 | -1 | cold | 0.55 | 0 | 10374 | 0 |
| fixpoints/reference-iom-262144 | bbox-0 | -1 | warm | 0.36 | 0 | 0 | 0 |
| fixpoints/reference-iom-262144 | bbox-0 | 0 | cold | 1.75 | 6 | 10374 | 0 |
| fixpoints/reference-iom-262144 | bbox-0 | 0 | warm | 0.26 | 0 | 0 | 0 |
| fixpoints/reference-iom-262144 | bbox-0 | 20 | cold | 150.61 | 6 | 10374 | 0 |
| fixpoints/reference-iom-262144 | bbox-0 | 20 | warm | 0.49 | 0 | 0 | 0 |
| fixpoints/reference-iom-262144 | bbox-0 | 80 | cold | 506.82 | 6 | 10374 | 0 |
| fixpoints/reference-iom-262144 | bbox-0 | 80 | warm | 0.80 | 0 | 0 | 0 |
| fixpoints/reference-iom-262144 | bbox-1 | -1 | cold | 2.55 | 0 | 38370 | 1 |
| fixpoints/reference-iom-262144 | bbox-1 | -1 | warm | 2.29 | 0 | 0 | 0 |
| fixpoints/reference-iom-262144 | bbox-1 | 0 | cold | 5.73 | 12 | 38370 | 1 |
| fixpoints/reference-iom-262144 | bbox-1 | 0 | warm | 2.25 | 0 | 0 | 0 |
| fixpoints/reference-iom-262144 | bbox-1 | 20 | cold | 304.04 | 12 | 38370 | 1 |
| fixpoints/reference-iom-262144 | bbox-1 | 20 | warm | 5.11 | 0 | 0 | 0 |
| fixpoints/reference-iom-262144 | bbox-1 | 80 | cold | 1026.05 | 12 | 38370 | 1 |
| fixpoints/reference-iom-262144 | bbox-1 | 80 | warm | 6.18 | 0 | 0 | 0 |
| fixpoints/reference-iom-262144 | bbox-2 | -1 | cold | 6.13 | 0 | 77514 | 1 |
| fixpoints/reference-iom-262144 | bbox-2 | -1 | warm | 6.34 | 0 | 0 | 0 |
| fixpoints/reference-iom-262144 | bbox-2 | 0 | cold | 9.91 | 22 | 77514 | 1 |
| fixpoints/reference-iom-262144 | bbox-2 | 0 | warm | 7.55 | 0 | 0 | 0 |
| fixpoints/reference-iom-262144 | bbox-2 | 20 | cold | 550.75 | 22 | 77514 | 1 |
| fixpoints/reference-iom-262144 | bbox-2 | 20 | warm | 5.94 | 0 | 0 | 0 |
| fixpoints/reference-iom-262144 | bbox-2 | 80 | cold | 1882.25 | 22 | 77514 | 1 |
| fixpoints/reference-iom-262144 | bbox-2 | 80 | warm | 9.38 | 0 | 0 | 0 |
| fixpoints/reference-iom-262144 | class | -1 | cold | 1.95 | 0 | 28983 | 1 |
| fixpoints/reference-iom-262144 | class | -1 | warm | 1.98 | 0 | 0 | 0 |
| fixpoints/reference-iom-262144 | class | 0 | cold | 3.06 | 8 | 28983 | 1 |
| fixpoints/reference-iom-262144 | class | 0 | warm | 1.58 | 0 | 0 | 0 |
| fixpoints/reference-iom-262144 | class | 20 | cold | 202.95 | 8 | 28983 | 1 |
| fixpoints/reference-iom-262144 | class | 20 | warm | 4.05 | 0 | 0 | 0 |
| fixpoints/reference-iom-262144 | class | 80 | cold | 676.28 | 8 | 28983 | 1 |
| fixpoints/reference-iom-262144 | class | 80 | warm | 4.14 | 0 | 0 | 0 |
| fixpoints/reference-iom-262144 | tid | -1 | cold | 0.30 | 0 | 28840 | 1 |
| fixpoints/reference-iom-262144 | tid | -1 | warm | 0.14 | 0 | 0 | 0 |
| fixpoints/reference-iom-262144 | tid | 0 | cold | 2.96 | 8 | 28840 | 1 |
| fixpoints/reference-iom-262144 | tid | 0 | warm | 0.14 | 0 | 0 | 0 |
| fixpoints/reference-iom-262144 | tid | 20 | cold | 196.53 | 8 | 28840 | 1 |
| fixpoints/reference-iom-262144 | tid | 20 | warm | 0.53 | 0 | 0 | 0 |
| fixpoints/reference-iom-262144 | tid | 80 | cold | 676.18 | 8 | 28840 | 1 |
| fixpoints/reference-iom-262144 | tid | 80 | warm | 0.62 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | bbox-0 | -1 | cold | 0.52 | 0 | 10502 | 0 |
| fixpoints/reference-wkb-262144 | bbox-0 | -1 | warm | 0.39 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | bbox-0 | 0 | cold | 1.53 | 6 | 10502 | 0 |
| fixpoints/reference-wkb-262144 | bbox-0 | 0 | warm | 0.27 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | bbox-0 | 20 | cold | 147.52 | 6 | 10502 | 0 |
| fixpoints/reference-wkb-262144 | bbox-0 | 20 | warm | 0.75 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | bbox-0 | 80 | cold | 522.82 | 6 | 10502 | 0 |
| fixpoints/reference-wkb-262144 | bbox-0 | 80 | warm | 1.35 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | bbox-1 | -1 | cold | 2.83 | 0 | 40542 | 1 |
| fixpoints/reference-wkb-262144 | bbox-1 | -1 | warm | 2.22 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | bbox-1 | 0 | cold | 4.72 | 12 | 40542 | 1 |
| fixpoints/reference-wkb-262144 | bbox-1 | 0 | warm | 1.67 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | bbox-1 | 20 | cold | 304.77 | 12 | 40542 | 1 |
| fixpoints/reference-wkb-262144 | bbox-1 | 20 | warm | 5.43 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | bbox-1 | 80 | cold | 1077.19 | 12 | 40542 | 1 |
| fixpoints/reference-wkb-262144 | bbox-1 | 80 | warm | 5.60 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | bbox-2 | -1 | cold | 9.25 | 0 | 80212 | 1 |
| fixpoints/reference-wkb-262144 | bbox-2 | -1 | warm | 8.67 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | bbox-2 | 0 | cold | 11.03 | 22 | 80212 | 1 |
| fixpoints/reference-wkb-262144 | bbox-2 | 0 | warm | 5.27 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | bbox-2 | 20 | cold | 548.23 | 22 | 80212 | 1 |
| fixpoints/reference-wkb-262144 | bbox-2 | 20 | warm | 6.38 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | bbox-2 | 80 | cold | 1912.73 | 22 | 80212 | 1 |
| fixpoints/reference-wkb-262144 | bbox-2 | 80 | warm | 9.44 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | class | -1 | cold | 3.38 | 0 | 31886 | 1 |
| fixpoints/reference-wkb-262144 | class | -1 | warm | 3.33 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | class | 0 | cold | 4.45 | 8 | 31886 | 1 |
| fixpoints/reference-wkb-262144 | class | 0 | warm | 1.82 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | class | 20 | cold | 206.50 | 8 | 31886 | 1 |
| fixpoints/reference-wkb-262144 | class | 20 | warm | 4.81 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | class | 80 | cold | 714.07 | 8 | 31886 | 1 |
| fixpoints/reference-wkb-262144 | class | 80 | warm | 5.48 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | fid | -1 | cold | 0.28 | 0 | 31886 | 1 |
| fixpoints/reference-wkb-262144 | fid | -1 | warm | 0.14 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | fid | 0 | cold | 1.92 | 8 | 31886 | 1 |
| fixpoints/reference-wkb-262144 | fid | 0 | warm | 0.18 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | fid | 20 | cold | 195.01 | 8 | 31886 | 1 |
| fixpoints/reference-wkb-262144 | fid | 20 | warm | 0.77 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | fid | 80 | cold | 691.50 | 8 | 31886 | 1 |
| fixpoints/reference-wkb-262144 | fid | 80 | warm | 0.96 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | tid | -1 | cold | 0.34 | 0 | 30930 | 1 |
| fixpoints/reference-wkb-262144 | tid | -1 | warm | 0.13 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | tid | 0 | cold | 1.88 | 8 | 30930 | 1 |
| fixpoints/reference-wkb-262144 | tid | 0 | warm | 0.14 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | tid | 20 | cold | 200.68 | 8 | 30930 | 1 |
| fixpoints/reference-wkb-262144 | tid | 20 | warm | 0.39 | 0 | 0 | 0 |
| fixpoints/reference-wkb-262144 | tid | 80 | cold | 693.43 | 8 | 30930 | 1 |
| fixpoints/reference-wkb-262144 | tid | 80 | warm | 0.46 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | bbox-0 | -1 | cold | 0.55 | 0 | 16995 | 0 |
| fixpoints/str-iom-262144 | bbox-0 | -1 | warm | 0.43 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | bbox-0 | 0 | cold | 1.17 | 3 | 16995 | 0 |
| fixpoints/str-iom-262144 | bbox-0 | 0 | warm | 0.24 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | bbox-0 | 20 | cold | 70.87 | 3 | 16995 | 0 |
| fixpoints/str-iom-262144 | bbox-0 | 20 | warm | 1.22 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | bbox-0 | 80 | cold | 251.70 | 3 | 16995 | 0 |
| fixpoints/str-iom-262144 | bbox-0 | 80 | warm | 0.97 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | bbox-1 | -1 | cold | 3.19 | 0 | 35505 | 1 |
| fixpoints/str-iom-262144 | bbox-1 | -1 | warm | 2.55 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | bbox-1 | 0 | cold | 3.34 | 5 | 35505 | 1 |
| fixpoints/str-iom-262144 | bbox-1 | 0 | warm | 2.04 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | bbox-1 | 20 | cold | 133.80 | 5 | 35505 | 1 |
| fixpoints/str-iom-262144 | bbox-1 | 20 | warm | 5.67 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | bbox-1 | 80 | cold | 427.93 | 5 | 35505 | 1 |
| fixpoints/str-iom-262144 | bbox-1 | 80 | warm | 5.18 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | bbox-2 | -1 | cold | 5.62 | 0 | 77177 | 1 |
| fixpoints/str-iom-262144 | bbox-2 | -1 | warm | 5.39 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | bbox-2 | 0 | cold | 6.89 | 8 | 77177 | 1 |
| fixpoints/str-iom-262144 | bbox-2 | 0 | warm | 4.40 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | bbox-2 | 20 | cold | 207.73 | 8 | 77177 | 1 |
| fixpoints/str-iom-262144 | bbox-2 | 20 | warm | 6.93 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | bbox-2 | 80 | cold | 693.75 | 8 | 77177 | 1 |
| fixpoints/str-iom-262144 | bbox-2 | 80 | warm | 7.58 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | class | -1 | cold | 1.53 | 0 | 35141 | 1 |
| fixpoints/str-iom-262144 | class | -1 | warm | 1.89 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | class | 0 | cold | 2.85 | 4 | 35141 | 1 |
| fixpoints/str-iom-262144 | class | 0 | warm | 1.56 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | class | 20 | cold | 105.19 | 4 | 35141 | 1 |
| fixpoints/str-iom-262144 | class | 20 | warm | 4.30 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | class | 80 | cold | 346.78 | 4 | 35141 | 1 |
| fixpoints/str-iom-262144 | class | 80 | warm | 4.53 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | fid | -1 | cold | 0.28 | 0 | 35141 | 1 |
| fixpoints/str-iom-262144 | fid | -1 | warm | 0.20 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | fid | 0 | cold | 1.38 | 4 | 35141 | 1 |
| fixpoints/str-iom-262144 | fid | 0 | warm | 0.18 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | fid | 20 | cold | 99.22 | 4 | 35141 | 1 |
| fixpoints/str-iom-262144 | fid | 20 | warm | 0.54 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | fid | 80 | cold | 343.35 | 4 | 35141 | 1 |
| fixpoints/str-iom-262144 | fid | 80 | warm | 0.76 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | tid | -1 | cold | 0.38 | 0 | 35144 | 1 |
| fixpoints/str-iom-262144 | tid | -1 | warm | 0.19 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | tid | 0 | cold | 1.16 | 4 | 35144 | 1 |
| fixpoints/str-iom-262144 | tid | 0 | warm | 0.16 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | tid | 20 | cold | 100.55 | 4 | 35144 | 1 |
| fixpoints/str-iom-262144 | tid | 20 | warm | 0.37 | 0 | 0 | 0 |
| fixpoints/str-iom-262144 | tid | 80 | cold | 336.76 | 4 | 35144 | 1 |
| fixpoints/str-iom-262144 | tid | 80 | warm | 0.69 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | bbox-0 | -1 | cold | 0.63 | 0 | 16995 | 0 |
| fixpoints/str-wkb-262144 | bbox-0 | -1 | warm | 0.46 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | bbox-0 | 0 | cold | 1.12 | 3 | 16995 | 0 |
| fixpoints/str-wkb-262144 | bbox-0 | 0 | warm | 0.29 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | bbox-0 | 20 | cold | 88.19 | 3 | 16995 | 0 |
| fixpoints/str-wkb-262144 | bbox-0 | 20 | warm | 1.21 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | bbox-0 | 80 | cold | 270.61 | 3 | 16995 | 0 |
| fixpoints/str-wkb-262144 | bbox-0 | 80 | warm | 1.63 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | bbox-1 | -1 | cold | 2.88 | 0 | 37410 | 1 |
| fixpoints/str-wkb-262144 | bbox-1 | -1 | warm | 2.69 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | bbox-1 | 0 | cold | 3.13 | 5 | 37410 | 1 |
| fixpoints/str-wkb-262144 | bbox-1 | 0 | warm | 1.75 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | bbox-1 | 20 | cold | 143.39 | 5 | 37410 | 1 |
| fixpoints/str-wkb-262144 | bbox-1 | 20 | warm | 4.92 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | bbox-1 | 80 | cold | 450.98 | 5 | 37410 | 1 |
| fixpoints/str-wkb-262144 | bbox-1 | 80 | warm | 4.60 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | bbox-2 | -1 | cold | 8.47 | 0 | 79082 | 1 |
| fixpoints/str-wkb-262144 | bbox-2 | -1 | warm | 8.11 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | bbox-2 | 0 | cold | 6.93 | 8 | 79082 | 1 |
| fixpoints/str-wkb-262144 | bbox-2 | 0 | warm | 4.63 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | bbox-2 | 20 | cold | 240.67 | 8 | 79082 | 1 |
| fixpoints/str-wkb-262144 | bbox-2 | 20 | warm | 10.04 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | bbox-2 | 80 | cold | 712.32 | 8 | 79082 | 1 |
| fixpoints/str-wkb-262144 | bbox-2 | 80 | warm | 9.69 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | class | -1 | cold | 4.77 | 0 | 37046 | 1 |
| fixpoints/str-wkb-262144 | class | -1 | warm | 4.08 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | class | 0 | cold | 3.05 | 4 | 37046 | 1 |
| fixpoints/str-wkb-262144 | class | 0 | warm | 2.20 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | class | 20 | cold | 121.97 | 4 | 37046 | 1 |
| fixpoints/str-wkb-262144 | class | 20 | warm | 4.67 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | class | 80 | cold | 358.80 | 4 | 37046 | 1 |
| fixpoints/str-wkb-262144 | class | 80 | warm | 4.22 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | fid | -1 | cold | 0.27 | 0 | 37046 | 1 |
| fixpoints/str-wkb-262144 | fid | -1 | warm | 0.18 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | fid | 0 | cold | 1.61 | 4 | 37046 | 1 |
| fixpoints/str-wkb-262144 | fid | 0 | warm | 0.20 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | fid | 20 | cold | 107.81 | 4 | 37046 | 1 |
| fixpoints/str-wkb-262144 | fid | 20 | warm | 0.71 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | fid | 80 | cold | 339.47 | 4 | 37046 | 1 |
| fixpoints/str-wkb-262144 | fid | 80 | warm | 0.84 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | tid | -1 | cold | 0.37 | 0 | 37049 | 1 |
| fixpoints/str-wkb-262144 | tid | -1 | warm | 0.18 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | tid | 0 | cold | 1.30 | 4 | 37049 | 1 |
| fixpoints/str-wkb-262144 | tid | 0 | warm | 0.18 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | tid | 20 | cold | 110.74 | 4 | 37049 | 1 |
| fixpoints/str-wkb-262144 | tid | 20 | warm | 0.56 | 0 | 0 | 0 |
| fixpoints/str-wkb-262144 | tid | 80 | cold | 348.12 | 4 | 37049 | 1 |
| fixpoints/str-wkb-262144 | tid | 80 | warm | 0.58 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | bbox-0 | -1 | cold | 0.56 | 0 | 16993 | 0 |
| fixpoints/x-direct-iom-262144 | bbox-0 | -1 | warm | 0.40 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | bbox-0 | 0 | cold | 1.13 | 3 | 16993 | 0 |
| fixpoints/x-direct-iom-262144 | bbox-0 | 0 | warm | 0.23 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | bbox-0 | 20 | cold | 77.82 | 3 | 16993 | 0 |
| fixpoints/x-direct-iom-262144 | bbox-0 | 20 | warm | 1.19 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | bbox-0 | 80 | cold | 251.25 | 3 | 16993 | 0 |
| fixpoints/x-direct-iom-262144 | bbox-0 | 80 | warm | 1.18 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | bbox-1 | -1 | cold | 2.53 | 0 | 35503 | 1 |
| fixpoints/x-direct-iom-262144 | bbox-1 | -1 | warm | 2.47 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | bbox-1 | 0 | cold | 3.36 | 5 | 35503 | 1 |
| fixpoints/x-direct-iom-262144 | bbox-1 | 0 | warm | 1.96 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | bbox-1 | 20 | cold | 129.16 | 5 | 35503 | 1 |
| fixpoints/x-direct-iom-262144 | bbox-1 | 20 | warm | 5.85 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | bbox-1 | 80 | cold | 428.58 | 5 | 35503 | 1 |
| fixpoints/x-direct-iom-262144 | bbox-1 | 80 | warm | 5.60 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | bbox-2 | -1 | cold | 5.55 | 0 | 77175 | 1 |
| fixpoints/x-direct-iom-262144 | bbox-2 | -1 | warm | 4.64 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | bbox-2 | 0 | cold | 5.64 | 8 | 77175 | 1 |
| fixpoints/x-direct-iom-262144 | bbox-2 | 0 | warm | 3.90 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | bbox-2 | 20 | cold | 213.88 | 8 | 77175 | 1 |
| fixpoints/x-direct-iom-262144 | bbox-2 | 20 | warm | 8.49 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | bbox-2 | 80 | cold | 688.07 | 8 | 77175 | 1 |
| fixpoints/x-direct-iom-262144 | bbox-2 | 80 | warm | 5.09 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | class | -1 | cold | 1.94 | 0 | 35141 | 1 |
| fixpoints/x-direct-iom-262144 | class | -1 | warm | 1.61 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | class | 0 | cold | 2.44 | 4 | 35141 | 1 |
| fixpoints/x-direct-iom-262144 | class | 0 | warm | 1.49 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | class | 20 | cold | 105.40 | 4 | 35141 | 1 |
| fixpoints/x-direct-iom-262144 | class | 20 | warm | 4.34 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | class | 80 | cold | 342.75 | 4 | 35141 | 1 |
| fixpoints/x-direct-iom-262144 | class | 80 | warm | 3.44 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | fid | -1 | cold | 1.97 | 0 | 35141 | 1 |
| fixpoints/x-direct-iom-262144 | fid | -1 | warm | 0.22 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | fid | 0 | cold | 1.39 | 4 | 35141 | 1 |
| fixpoints/x-direct-iom-262144 | fid | 0 | warm | 0.18 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | fid | 20 | cold | 101.47 | 4 | 35141 | 1 |
| fixpoints/x-direct-iom-262144 | fid | 20 | warm | 0.73 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | fid | 80 | cold | 340.00 | 4 | 35141 | 1 |
| fixpoints/x-direct-iom-262144 | fid | 80 | warm | 0.48 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | tid | -1 | cold | 0.33 | 0 | 35144 | 1 |
| fixpoints/x-direct-iom-262144 | tid | -1 | warm | 0.19 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | tid | 0 | cold | 1.44 | 4 | 35144 | 1 |
| fixpoints/x-direct-iom-262144 | tid | 0 | warm | 0.14 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | tid | 20 | cold | 96.88 | 4 | 35144 | 1 |
| fixpoints/x-direct-iom-262144 | tid | 20 | warm | 0.38 | 0 | 0 | 0 |
| fixpoints/x-direct-iom-262144 | tid | 80 | cold | 335.89 | 4 | 35144 | 1 |
| fixpoints/x-direct-iom-262144 | tid | 80 | warm | 0.38 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | bbox-0 | -1 | cold | 0.89 | 0 | 16993 | 0 |
| fixpoints/x-direct-wkb-262144 | bbox-0 | -1 | warm | 0.60 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | bbox-0 | 0 | cold | 1.44 | 3 | 16993 | 0 |
| fixpoints/x-direct-wkb-262144 | bbox-0 | 0 | warm | 0.25 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | bbox-0 | 20 | cold | 89.89 | 3 | 16993 | 0 |
| fixpoints/x-direct-wkb-262144 | bbox-0 | 20 | warm | 1.42 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | bbox-0 | 80 | cold | 257.52 | 3 | 16993 | 0 |
| fixpoints/x-direct-wkb-262144 | bbox-0 | 80 | warm | 1.22 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | bbox-1 | -1 | cold | 3.58 | 0 | 37408 | 1 |
| fixpoints/x-direct-wkb-262144 | bbox-1 | -1 | warm | 3.38 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | bbox-1 | 0 | cold | 3.21 | 5 | 37408 | 1 |
| fixpoints/x-direct-wkb-262144 | bbox-1 | 0 | warm | 1.69 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | bbox-1 | 20 | cold | 151.52 | 5 | 37408 | 1 |
| fixpoints/x-direct-wkb-262144 | bbox-1 | 20 | warm | 5.16 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | bbox-1 | 80 | cold | 444.79 | 5 | 37408 | 1 |
| fixpoints/x-direct-wkb-262144 | bbox-1 | 80 | warm | 5.31 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | bbox-2 | -1 | cold | 10.15 | 0 | 79080 | 1 |
| fixpoints/x-direct-wkb-262144 | bbox-2 | -1 | warm | 11.97 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | bbox-2 | 0 | cold | 7.05 | 8 | 79080 | 1 |
| fixpoints/x-direct-wkb-262144 | bbox-2 | 0 | warm | 4.17 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | bbox-2 | 20 | cold | 235.30 | 8 | 79080 | 1 |
| fixpoints/x-direct-wkb-262144 | bbox-2 | 20 | warm | 8.65 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | bbox-2 | 80 | cold | 718.39 | 8 | 79080 | 1 |
| fixpoints/x-direct-wkb-262144 | bbox-2 | 80 | warm | 12.79 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | class | -1 | cold | 5.22 | 0 | 37046 | 1 |
| fixpoints/x-direct-wkb-262144 | class | -1 | warm | 5.17 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | class | 0 | cold | 2.96 | 4 | 37046 | 1 |
| fixpoints/x-direct-wkb-262144 | class | 0 | warm | 1.78 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | class | 20 | cold | 118.23 | 4 | 37046 | 1 |
| fixpoints/x-direct-wkb-262144 | class | 20 | warm | 5.67 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | class | 80 | cold | 356.52 | 4 | 37046 | 1 |
| fixpoints/x-direct-wkb-262144 | class | 80 | warm | 3.84 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | fid | -1 | cold | 0.54 | 0 | 37046 | 1 |
| fixpoints/x-direct-wkb-262144 | fid | -1 | warm | 0.27 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | fid | 0 | cold | 1.46 | 4 | 37046 | 1 |
| fixpoints/x-direct-wkb-262144 | fid | 0 | warm | 0.20 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | fid | 20 | cold | 107.51 | 4 | 37046 | 1 |
| fixpoints/x-direct-wkb-262144 | fid | 20 | warm | 0.68 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | fid | 80 | cold | 344.25 | 4 | 37046 | 1 |
| fixpoints/x-direct-wkb-262144 | fid | 80 | warm | 0.89 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | tid | -1 | cold | 0.48 | 0 | 37049 | 1 |
| fixpoints/x-direct-wkb-262144 | tid | -1 | warm | 0.25 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | tid | 0 | cold | 1.52 | 4 | 37049 | 1 |
| fixpoints/x-direct-wkb-262144 | tid | 0 | warm | 0.19 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | tid | 20 | cold | 109.04 | 4 | 37049 | 1 |
| fixpoints/x-direct-wkb-262144 | tid | 20 | warm | 0.63 | 0 | 0 | 0 |
| fixpoints/x-direct-wkb-262144 | tid | 80 | cold | 351.37 | 4 | 37049 | 1 |
| fixpoints/x-direct-wkb-262144 | tid | 80 | warm | 0.65 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | bbox-0 | -1 | cold | 0.56 | 0 | 16993 | 0 |
| fixpoints/x-prefetch-iom-262144 | bbox-0 | -1 | warm | 0.45 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | bbox-0 | 0 | cold | 1.30 | 3 | 16993 | 0 |
| fixpoints/x-prefetch-iom-262144 | bbox-0 | 0 | warm | 0.22 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | bbox-0 | 20 | cold | 71.81 | 3 | 16993 | 0 |
| fixpoints/x-prefetch-iom-262144 | bbox-0 | 20 | warm | 0.75 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | bbox-0 | 80 | cold | 256.83 | 3 | 16993 | 0 |
| fixpoints/x-prefetch-iom-262144 | bbox-0 | 80 | warm | 1.19 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | bbox-1 | -1 | cold | 3.50 | 0 | 35503 | 1 |
| fixpoints/x-prefetch-iom-262144 | bbox-1 | -1 | warm | 5.26 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | bbox-1 | 0 | cold | 3.94 | 5 | 35503 | 1 |
| fixpoints/x-prefetch-iom-262144 | bbox-1 | 0 | warm | 2.22 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | bbox-1 | 20 | cold | 140.25 | 5 | 35503 | 1 |
| fixpoints/x-prefetch-iom-262144 | bbox-1 | 20 | warm | 3.12 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | bbox-1 | 80 | cold | 429.21 | 5 | 35503 | 1 |
| fixpoints/x-prefetch-iom-262144 | bbox-1 | 80 | warm | 5.97 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | bbox-2 | -1 | cold | 7.40 | 0 | 77175 | 1 |
| fixpoints/x-prefetch-iom-262144 | bbox-2 | -1 | warm | 6.11 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | bbox-2 | 0 | cold | 6.64 | 8 | 77175 | 1 |
| fixpoints/x-prefetch-iom-262144 | bbox-2 | 0 | warm | 4.78 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | bbox-2 | 20 | cold | 202.72 | 8 | 77175 | 1 |
| fixpoints/x-prefetch-iom-262144 | bbox-2 | 20 | warm | 5.32 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | bbox-2 | 80 | cold | 691.37 | 8 | 77175 | 1 |
| fixpoints/x-prefetch-iom-262144 | bbox-2 | 80 | warm | 8.85 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | class | -1 | cold | 1.71 | 0 | 35141 | 1 |
| fixpoints/x-prefetch-iom-262144 | class | -1 | warm | 2.19 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | class | 0 | cold | 2.58 | 4 | 35141 | 1 |
| fixpoints/x-prefetch-iom-262144 | class | 0 | warm | 1.57 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | class | 20 | cold | 104.55 | 4 | 35141 | 1 |
| fixpoints/x-prefetch-iom-262144 | class | 20 | warm | 3.63 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | class | 80 | cold | 343.03 | 4 | 35141 | 1 |
| fixpoints/x-prefetch-iom-262144 | class | 80 | warm | 4.46 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | fid | -1 | cold | 0.31 | 0 | 35141 | 1 |
| fixpoints/x-prefetch-iom-262144 | fid | -1 | warm | 0.19 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | fid | 0 | cold | 1.64 | 4 | 35141 | 1 |
| fixpoints/x-prefetch-iom-262144 | fid | 0 | warm | 0.21 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | fid | 20 | cold | 95.65 | 4 | 35141 | 1 |
| fixpoints/x-prefetch-iom-262144 | fid | 20 | warm | 0.46 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | fid | 80 | cold | 342.60 | 4 | 35141 | 1 |
| fixpoints/x-prefetch-iom-262144 | fid | 80 | warm | 0.64 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | tid | -1 | cold | 0.51 | 0 | 35144 | 1 |
| fixpoints/x-prefetch-iom-262144 | tid | -1 | warm | 0.21 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | tid | 0 | cold | 3.25 | 4 | 35144 | 1 |
| fixpoints/x-prefetch-iom-262144 | tid | 0 | warm | 0.18 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | tid | 20 | cold | 97.42 | 4 | 35144 | 1 |
| fixpoints/x-prefetch-iom-262144 | tid | 20 | warm | 0.40 | 0 | 0 | 0 |
| fixpoints/x-prefetch-iom-262144 | tid | 80 | cold | 335.53 | 4 | 35144 | 1 |
| fixpoints/x-prefetch-iom-262144 | tid | 80 | warm | 0.47 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | bbox-0 | -1 | cold | 0.59 | 0 | 16993 | 0 |
| fixpoints/x-prefetch-wkb-262144 | bbox-0 | -1 | warm | 0.44 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | bbox-0 | 0 | cold | 1.56 | 3 | 16993 | 0 |
| fixpoints/x-prefetch-wkb-262144 | bbox-0 | 0 | warm | 0.31 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | bbox-0 | 20 | cold | 72.19 | 3 | 16993 | 0 |
| fixpoints/x-prefetch-wkb-262144 | bbox-0 | 20 | warm | 1.09 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | bbox-0 | 80 | cold | 264.56 | 3 | 16993 | 0 |
| fixpoints/x-prefetch-wkb-262144 | bbox-0 | 80 | warm | 1.51 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | bbox-1 | -1 | cold | 2.69 | 0 | 37408 | 1 |
| fixpoints/x-prefetch-wkb-262144 | bbox-1 | -1 | warm | 2.63 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | bbox-1 | 0 | cold | 3.09 | 5 | 37408 | 1 |
| fixpoints/x-prefetch-wkb-262144 | bbox-1 | 0 | warm | 1.88 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | bbox-1 | 20 | cold | 139.86 | 5 | 37408 | 1 |
| fixpoints/x-prefetch-wkb-262144 | bbox-1 | 20 | warm | 2.95 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | bbox-1 | 80 | cold | 446.03 | 5 | 37408 | 1 |
| fixpoints/x-prefetch-wkb-262144 | bbox-1 | 80 | warm | 5.42 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | bbox-2 | -1 | cold | 9.34 | 0 | 79080 | 1 |
| fixpoints/x-prefetch-wkb-262144 | bbox-2 | -1 | warm | 8.85 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | bbox-2 | 0 | cold | 6.77 | 8 | 79080 | 1 |
| fixpoints/x-prefetch-wkb-262144 | bbox-2 | 0 | warm | 4.16 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | bbox-2 | 20 | cold | 230.98 | 8 | 79080 | 1 |
| fixpoints/x-prefetch-wkb-262144 | bbox-2 | 20 | warm | 8.88 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | bbox-2 | 80 | cold | 712.39 | 8 | 79080 | 1 |
| fixpoints/x-prefetch-wkb-262144 | bbox-2 | 80 | warm | 4.05 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | class | -1 | cold | 3.79 | 0 | 37046 | 1 |
| fixpoints/x-prefetch-wkb-262144 | class | -1 | warm | 3.90 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | class | 0 | cold | 4.44 | 4 | 37046 | 1 |
| fixpoints/x-prefetch-wkb-262144 | class | 0 | warm | 2.25 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | class | 20 | cold | 122.87 | 4 | 37046 | 1 |
| fixpoints/x-prefetch-wkb-262144 | class | 20 | warm | 5.15 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | class | 80 | cold | 348.99 | 4 | 37046 | 1 |
| fixpoints/x-prefetch-wkb-262144 | class | 80 | warm | 5.30 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | fid | -1 | cold | 0.29 | 0 | 37046 | 1 |
| fixpoints/x-prefetch-wkb-262144 | fid | -1 | warm | 0.21 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | fid | 0 | cold | 1.73 | 4 | 37046 | 1 |
| fixpoints/x-prefetch-wkb-262144 | fid | 0 | warm | 0.21 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | fid | 20 | cold | 102.05 | 4 | 37046 | 1 |
| fixpoints/x-prefetch-wkb-262144 | fid | 20 | warm | 0.58 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | fid | 80 | cold | 361.22 | 4 | 37046 | 1 |
| fixpoints/x-prefetch-wkb-262144 | fid | 80 | warm | 0.61 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | tid | -1 | cold | 0.37 | 0 | 37049 | 1 |
| fixpoints/x-prefetch-wkb-262144 | tid | -1 | warm | 0.19 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | tid | 0 | cold | 1.54 | 4 | 37049 | 1 |
| fixpoints/x-prefetch-wkb-262144 | tid | 0 | warm | 0.19 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | tid | 20 | cold | 113.28 | 4 | 37049 | 1 |
| fixpoints/x-prefetch-wkb-262144 | tid | 20 | warm | 0.54 | 0 | 0 | 0 |
| fixpoints/x-prefetch-wkb-262144 | tid | 80 | cold | 361.24 | 4 | 37049 | 1 |
| fixpoints/x-prefetch-wkb-262144 | tid | 80 | warm | 0.47 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | bbox-0 | -1 | cold | 19.67 | 0 | 687244 | 3 |
| localities/hilbert-str-iom-1048576 | bbox-0 | -1 | warm | 19.00 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | bbox-0 | 0 | cold | 21.43 | 7 | 687244 | 3 |
| localities/hilbert-str-iom-1048576 | bbox-0 | 0 | warm | 19.12 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | bbox-0 | 20 | cold | 215.30 | 7 | 687244 | 3 |
| localities/hilbert-str-iom-1048576 | bbox-0 | 20 | warm | 27.29 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | bbox-0 | 80 | cold | 632.91 | 7 | 687244 | 3 |
| localities/hilbert-str-iom-1048576 | bbox-0 | 80 | warm | 26.99 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | bbox-1 | -1 | cold | 61.13 | 0 | 1.38046e+06 | 6 |
| localities/hilbert-str-iom-1048576 | bbox-1 | -1 | warm | 60.29 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | bbox-1 | 0 | cold | 65.06 | 10 | 1.38046e+06 | 6 |
| localities/hilbert-str-iom-1048576 | bbox-1 | 0 | warm | 60.83 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | bbox-1 | 20 | cold | 343.78 | 10 | 1.38046e+06 | 6 |
| localities/hilbert-str-iom-1048576 | bbox-1 | 20 | warm | 62.08 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | bbox-1 | 80 | cold | 951.21 | 10 | 1.38046e+06 | 6 |
| localities/hilbert-str-iom-1048576 | bbox-1 | 80 | warm | 69.55 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | bbox-2 | -1 | cold | 1128.66 | 0 | 1.9125e+07 | 84 |
| localities/hilbert-str-iom-1048576 | bbox-2 | -1 | warm | 1083.44 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | bbox-2 | 0 | cold | 1194.42 | 126 | 1.9125e+07 | 84 |
| localities/hilbert-str-iom-1048576 | bbox-2 | 0 | warm | 1084.37 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | bbox-2 | 20 | cold | 4441.20 | 126 | 1.9125e+07 | 84 |
| localities/hilbert-str-iom-1048576 | bbox-2 | 20 | warm | 1085.04 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | bbox-2 | 80 | cold | 12833.36 | 126 | 1.9125e+07 | 84 |
| localities/hilbert-str-iom-1048576 | bbox-2 | 80 | warm | 1085.37 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | class | -1 | cold | 1091.53 | 0 | 1.85512e+07 | 84 |
| localities/hilbert-str-iom-1048576 | class | -1 | warm | 1076.47 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | class | 0 | cold | 1163.29 | 87 | 1.85512e+07 | 84 |
| localities/hilbert-str-iom-1048576 | class | 0 | warm | 1073.54 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | class | 20 | cold | 3463.16 | 87 | 1.85512e+07 | 84 |
| localities/hilbert-str-iom-1048576 | class | 20 | warm | 1066.49 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | class | 80 | cold | 9508.78 | 87 | 1.85512e+07 | 84 |
| localities/hilbert-str-iom-1048576 | class | 80 | warm | 1083.42 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | fid | -1 | cold | 5.66 | 0 | 238618 | 1 |
| localities/hilbert-str-iom-1048576 | fid | -1 | warm | 5.96 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | fid | 0 | cold | 6.58 | 4 | 238618 | 1 |
| localities/hilbert-str-iom-1048576 | fid | 0 | warm | 5.42 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | fid | 20 | cold | 108.92 | 4 | 238618 | 1 |
| localities/hilbert-str-iom-1048576 | fid | 20 | warm | 6.96 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | fid | 80 | cold | 350.11 | 4 | 238618 | 1 |
| localities/hilbert-str-iom-1048576 | fid | 80 | warm | 11.33 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | tid | -1 | cold | 6.41 | 0 | 238648 | 1 |
| localities/hilbert-str-iom-1048576 | tid | -1 | warm | 5.87 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | tid | 0 | cold | 6.20 | 4 | 238648 | 1 |
| localities/hilbert-str-iom-1048576 | tid | 0 | warm | 5.58 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | tid | 20 | cold | 112.69 | 4 | 238648 | 1 |
| localities/hilbert-str-iom-1048576 | tid | 20 | warm | 5.93 | 0 | 0 | 0 |
| localities/hilbert-str-iom-1048576 | tid | 80 | cold | 349.23 | 4 | 238648 | 1 |
| localities/hilbert-str-iom-1048576 | tid | 80 | warm | 11.73 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | bbox-0 | -1 | cold | 7.27 | 0 | 258164 | 4 |
| localities/hilbert-str-iom-262144 | bbox-0 | -1 | warm | 6.82 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | bbox-0 | 0 | cold | 8.97 | 7 | 258164 | 4 |
| localities/hilbert-str-iom-262144 | bbox-0 | 0 | warm | 6.75 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | bbox-0 | 20 | cold | 207.07 | 7 | 258164 | 4 |
| localities/hilbert-str-iom-262144 | bbox-0 | 20 | warm | 15.84 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | bbox-0 | 80 | cold | 645.48 | 7 | 258164 | 4 |
| localities/hilbert-str-iom-262144 | bbox-0 | 80 | warm | 15.49 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | bbox-1 | -1 | cold | 29.82 | 0 | 754091 | 12 |
| localities/hilbert-str-iom-262144 | bbox-1 | -1 | warm | 29.19 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | bbox-1 | 0 | cold | 34.66 | 12 | 754091 | 12 |
| localities/hilbert-str-iom-262144 | bbox-1 | 0 | warm | 29.21 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | bbox-1 | 20 | cold | 402.68 | 12 | 754091 | 12 |
| localities/hilbert-str-iom-262144 | bbox-1 | 20 | warm | 47.97 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | bbox-1 | 80 | cold | 1129.22 | 12 | 754091 | 12 |
| localities/hilbert-str-iom-262144 | bbox-1 | 80 | warm | 48.82 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | bbox-2 | -1 | cold | 1042.88 | 0 | 2.09161e+07 | 348 |
| localities/hilbert-str-iom-262144 | bbox-2 | -1 | warm | 1029.25 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | bbox-2 | 0 | cold | 1123.72 | 167 | 2.09161e+07 | 348 |
| localities/hilbert-str-iom-262144 | bbox-2 | 0 | warm | 1033.85 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | bbox-2 | 20 | cold | 6364.43 | 167 | 2.09161e+07 | 348 |
| localities/hilbert-str-iom-262144 | bbox-2 | 20 | warm | 1044.91 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | bbox-2 | 80 | cold | 17801.07 | 167 | 2.09161e+07 | 348 |
| localities/hilbert-str-iom-262144 | bbox-2 | 80 | warm | 1045.74 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | class | -1 | cold | 1009.32 | 0 | 2.0359e+07 | 348 |
| localities/hilbert-str-iom-262144 | class | -1 | warm | 997.24 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | class | 0 | cold | 1195.49 | 352 | 2.0359e+07 | 348 |
| localities/hilbert-str-iom-262144 | class | 0 | warm | 1009.56 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | class | 20 | cold | 12098.11 | 352 | 2.0359e+07 | 348 |
| localities/hilbert-str-iom-262144 | class | 20 | warm | 1045.15 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | class | 80 | cold | 35425.33 | 352 | 2.0359e+07 | 348 |
| localities/hilbert-str-iom-262144 | class | 80 | warm | 1062.43 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | fid | -1 | cold | 3.09 | 0 | 76563 | 1 |
| localities/hilbert-str-iom-262144 | fid | -1 | warm | 2.94 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | fid | 0 | cold | 4.18 | 4 | 76563 | 1 |
| localities/hilbert-str-iom-262144 | fid | 0 | warm | 2.98 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | fid | 20 | cold | 118.20 | 4 | 76563 | 1 |
| localities/hilbert-str-iom-262144 | fid | 20 | warm | 8.45 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | fid | 80 | cold | 355.13 | 4 | 76563 | 1 |
| localities/hilbert-str-iom-262144 | fid | 80 | warm | 8.06 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | tid | -1 | cold | 2.91 | 0 | 76603 | 1 |
| localities/hilbert-str-iom-262144 | tid | -1 | warm | 2.87 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | tid | 0 | cold | 3.84 | 4 | 76603 | 1 |
| localities/hilbert-str-iom-262144 | tid | 0 | warm | 2.90 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | tid | 20 | cold | 114.52 | 4 | 76603 | 1 |
| localities/hilbert-str-iom-262144 | tid | 20 | warm | 7.61 | 0 | 0 | 0 |
| localities/hilbert-str-iom-262144 | tid | 80 | cold | 366.09 | 4 | 76603 | 1 |
| localities/hilbert-str-iom-262144 | tid | 80 | warm | 8.59 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | bbox-0 | -1 | cold | 76.44 | 0 | 2.6798e+06 | 3 |
| localities/hilbert-str-iom-4194304 | bbox-0 | -1 | warm | 72.82 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | bbox-0 | 0 | cold | 72.06 | 7 | 2.6798e+06 | 3 |
| localities/hilbert-str-iom-4194304 | bbox-0 | 0 | warm | 68.15 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | bbox-0 | 20 | cold | 286.66 | 7 | 2.6798e+06 | 3 |
| localities/hilbert-str-iom-4194304 | bbox-0 | 20 | warm | 68.43 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | bbox-0 | 80 | cold | 714.06 | 7 | 2.6798e+06 | 3 |
| localities/hilbert-str-iom-4194304 | bbox-0 | 80 | warm | 67.76 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | bbox-1 | -1 | cold | 95.30 | 0 | 3.60951e+06 | 4 |
| localities/hilbert-str-iom-4194304 | bbox-1 | -1 | warm | 88.08 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | bbox-1 | 0 | cold | 93.14 | 10 | 3.60951e+06 | 4 |
| localities/hilbert-str-iom-4194304 | bbox-1 | 0 | warm | 87.39 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | bbox-1 | 20 | cold | 406.14 | 10 | 3.60951e+06 | 4 |
| localities/hilbert-str-iom-4194304 | bbox-1 | 20 | warm | 87.12 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | bbox-1 | 80 | cold | 1007.50 | 10 | 3.60951e+06 | 4 |
| localities/hilbert-str-iom-4194304 | bbox-1 | 80 | warm | 88.35 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | bbox-2 | -1 | cold | 1073.16 | 0 | 1.87671e+07 | 21 |
| localities/hilbert-str-iom-4194304 | bbox-2 | -1 | warm | 1049.30 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | bbox-2 | 0 | cold | 1162.15 | 64 | 1.87671e+07 | 21 |
| localities/hilbert-str-iom-4194304 | bbox-2 | 0 | warm | 1105.73 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | bbox-2 | 20 | cold | 2899.44 | 64 | 1.87671e+07 | 21 |
| localities/hilbert-str-iom-4194304 | bbox-2 | 20 | warm | 1130.64 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | bbox-2 | 80 | cold | 6983.80 | 64 | 1.87671e+07 | 21 |
| localities/hilbert-str-iom-4194304 | bbox-2 | 80 | warm | 1080.87 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | class | -1 | cold | 1054.89 | 0 | 1.81932e+07 | 21 |
| localities/hilbert-str-iom-4194304 | class | -1 | warm | 1072.95 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | class | 0 | cold | 1055.73 | 24 | 1.81932e+07 | 21 |
| localities/hilbert-str-iom-4194304 | class | 0 | warm | 1045.17 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | class | 20 | cold | 1802.59 | 24 | 1.81932e+07 | 21 |
| localities/hilbert-str-iom-4194304 | class | 20 | warm | 1030.64 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | class | 80 | cold | 3352.94 | 24 | 1.81932e+07 | 21 |
| localities/hilbert-str-iom-4194304 | class | 80 | warm | 1023.32 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | fid | -1 | cold | 40.34 | 0 | 882484 | 1 |
| localities/hilbert-str-iom-4194304 | fid | -1 | warm | 40.32 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | fid | 0 | cold | 46.59 | 4 | 882484 | 1 |
| localities/hilbert-str-iom-4194304 | fid | 0 | warm | 40.71 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | fid | 20 | cold | 162.96 | 4 | 882484 | 1 |
| localities/hilbert-str-iom-4194304 | fid | 20 | warm | 40.45 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | fid | 80 | cold | 419.03 | 4 | 882484 | 1 |
| localities/hilbert-str-iom-4194304 | fid | 80 | warm | 41.82 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | tid | -1 | cold | 40.12 | 0 | 882547 | 1 |
| localities/hilbert-str-iom-4194304 | tid | -1 | warm | 40.13 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | tid | 0 | cold | 41.95 | 4 | 882547 | 1 |
| localities/hilbert-str-iom-4194304 | tid | 0 | warm | 39.87 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | tid | 20 | cold | 162.62 | 4 | 882547 | 1 |
| localities/hilbert-str-iom-4194304 | tid | 20 | warm | 41.29 | 0 | 0 | 0 |
| localities/hilbert-str-iom-4194304 | tid | 80 | cold | 416.82 | 4 | 882547 | 1 |
| localities/hilbert-str-iom-4194304 | tid | 80 | warm | 41.97 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | bbox-0 | -1 | cold | 3.14 | 0 | 80837 | 4 |
| localities/hilbert-str-iom-65536 | bbox-0 | -1 | warm | 2.68 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | bbox-0 | 0 | cold | 5.08 | 7 | 80837 | 4 |
| localities/hilbert-str-iom-65536 | bbox-0 | 0 | warm | 3.74 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | bbox-0 | 20 | cold | 177.76 | 7 | 80837 | 4 |
| localities/hilbert-str-iom-65536 | bbox-0 | 20 | warm | 5.41 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | bbox-0 | 80 | cold | 622.16 | 7 | 80837 | 4 |
| localities/hilbert-str-iom-65536 | bbox-0 | 80 | warm | 7.96 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | bbox-1 | -1 | cold | 23.57 | 0 | 530963 | 33 |
| localities/hilbert-str-iom-65536 | bbox-1 | -1 | warm | 23.98 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | bbox-1 | 0 | cold | 27.53 | 13 | 530963 | 33 |
| localities/hilbert-str-iom-65536 | bbox-1 | 0 | warm | 23.39 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | bbox-1 | 20 | cold | 369.63 | 13 | 530963 | 33 |
| localities/hilbert-str-iom-65536 | bbox-1 | 20 | warm | 34.97 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | bbox-1 | 80 | cold | 1179.19 | 13 | 530963 | 33 |
| localities/hilbert-str-iom-65536 | bbox-1 | 80 | warm | 45.31 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | bbox-2 | -1 | cold | 1101.19 | 0 | 2.2169e+07 | 1574 |
| localities/hilbert-str-iom-65536 | bbox-2 | -1 | warm | 1073.47 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | bbox-2 | 0 | cold | 1177.69 | 168 | 2.2169e+07 | 1574 |
| localities/hilbert-str-iom-65536 | bbox-2 | 0 | warm | 1074.13 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | bbox-2 | 20 | cold | 5557.73 | 168 | 2.2169e+07 | 1574 |
| localities/hilbert-str-iom-65536 | bbox-2 | 20 | warm | 1127.26 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | bbox-2 | 80 | cold | 17445.50 | 168 | 2.2169e+07 | 1574 |
| localities/hilbert-str-iom-65536 | bbox-2 | 80 | warm | 1140.71 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | class | -1 | cold | 1088.24 | 0 | 2.16948e+07 | 1574 |
| localities/hilbert-str-iom-65536 | class | -1 | warm | 1072.75 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | class | 0 | cold | 1537.44 | 1583 | 2.16948e+07 | 1574 |
| localities/hilbert-str-iom-65536 | class | 0 | warm | 1094.50 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | class | 20 | cold | 41999.46 | 1583 | 2.16948e+07 | 1574 |
| localities/hilbert-str-iom-65536 | class | 20 | warm | 1173.01 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | class | 80 | cold | 141425.28 | 1583 | 2.16948e+07 | 1574 |
| localities/hilbert-str-iom-65536 | class | 80 | warm | 1169.91 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | fid | -1 | cold | 0.94 | 0 | 36048 | 1 |
| localities/hilbert-str-iom-65536 | fid | -1 | warm | 0.90 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | fid | 0 | cold | 1.69 | 4 | 36048 | 1 |
| localities/hilbert-str-iom-65536 | fid | 0 | warm | 0.85 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | fid | 20 | cold | 105.44 | 4 | 36048 | 1 |
| localities/hilbert-str-iom-65536 | fid | 20 | warm | 2.38 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | fid | 80 | cold | 341.86 | 4 | 36048 | 1 |
| localities/hilbert-str-iom-65536 | fid | 80 | warm | 2.73 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | tid | -1 | cold | 1.12 | 0 | 36098 | 1 |
| localities/hilbert-str-iom-65536 | tid | -1 | warm | 0.86 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | tid | 0 | cold | 1.72 | 4 | 36098 | 1 |
| localities/hilbert-str-iom-65536 | tid | 0 | warm | 0.76 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | tid | 20 | cold | 100.75 | 4 | 36098 | 1 |
| localities/hilbert-str-iom-65536 | tid | 20 | warm | 2.48 | 0 | 0 | 0 |
| localities/hilbert-str-iom-65536 | tid | 80 | cold | 344.17 | 4 | 36098 | 1 |
| localities/hilbert-str-iom-65536 | tid | 80 | warm | 2.33 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | bbox-0 | -1 | cold | 4.32 | 0 | 1.30986e+06 | 3 |
| localities/hilbert-str-wkb-1048576 | bbox-0 | -1 | warm | 3.96 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | bbox-0 | 0 | cold | 6.81 | 7 | 1.30986e+06 | 3 |
| localities/hilbert-str-wkb-1048576 | bbox-0 | 0 | warm | 3.26 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | bbox-0 | 20 | cold | 184.97 | 7 | 1.30986e+06 | 3 |
| localities/hilbert-str-wkb-1048576 | bbox-0 | 20 | warm | 9.15 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | bbox-0 | 80 | cold | 611.44 | 7 | 1.30986e+06 | 3 |
| localities/hilbert-str-wkb-1048576 | bbox-0 | 80 | warm | 9.21 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | bbox-1 | -1 | cold | 6.43 | 0 | 1.77014e+06 | 4 |
| localities/hilbert-str-wkb-1048576 | bbox-1 | -1 | warm | 5.96 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | bbox-1 | 0 | cold | 9.85 | 9 | 1.77014e+06 | 4 |
| localities/hilbert-str-wkb-1048576 | bbox-1 | 0 | warm | 5.40 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | bbox-1 | 20 | cold | 241.38 | 9 | 1.77014e+06 | 4 |
| localities/hilbert-str-wkb-1048576 | bbox-1 | 20 | warm | 12.47 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | bbox-1 | 80 | cold | 797.45 | 9 | 1.77014e+06 | 4 |
| localities/hilbert-str-wkb-1048576 | bbox-1 | 80 | warm | 15.09 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | bbox-2 | -1 | cold | 101.75 | 0 | 1.5592e+07 | 35 |
| localities/hilbert-str-wkb-1048576 | bbox-2 | -1 | warm | 86.51 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | bbox-2 | 0 | cold | 128.21 | 78 | 1.5592e+07 | 35 |
| localities/hilbert-str-wkb-1048576 | bbox-2 | 0 | warm | 82.27 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | bbox-2 | 20 | cold | 2204.65 | 78 | 1.5592e+07 | 35 |
| localities/hilbert-str-wkb-1048576 | bbox-2 | 20 | warm | 111.44 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | bbox-2 | 80 | cold | 6984.70 | 78 | 1.5592e+07 | 35 |
| localities/hilbert-str-wkb-1048576 | bbox-2 | 80 | warm | 119.51 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | class | -1 | cold | 48.30 | 0 | 1.5018e+07 | 35 |
| localities/hilbert-str-wkb-1048576 | class | -1 | warm | 41.65 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | class | 0 | cold | 69.63 | 38 | 1.5018e+07 | 35 |
| localities/hilbert-str-wkb-1048576 | class | 0 | warm | 40.18 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | class | 20 | cold | 1121.85 | 38 | 1.5018e+07 | 35 |
| localities/hilbert-str-wkb-1048576 | class | 20 | warm | 70.39 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | class | 80 | cold | 3427.87 | 38 | 1.5018e+07 | 35 |
| localities/hilbert-str-wkb-1048576 | class | 80 | warm | 75.23 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | fid | -1 | cold | 1.22 | 0 | 443502 | 1 |
| localities/hilbert-str-wkb-1048576 | fid | -1 | warm | 0.92 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | fid | 0 | cold | 2.99 | 4 | 443502 | 1 |
| localities/hilbert-str-wkb-1048576 | fid | 0 | warm | 0.90 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | fid | 20 | cold | 102.83 | 4 | 443502 | 1 |
| localities/hilbert-str-wkb-1048576 | fid | 20 | warm | 2.90 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | fid | 80 | cold | 344.13 | 4 | 443502 | 1 |
| localities/hilbert-str-wkb-1048576 | fid | 80 | warm | 3.29 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | tid | -1 | cold | 2.87 | 0 | 443527 | 1 |
| localities/hilbert-str-wkb-1048576 | tid | -1 | warm | 2.20 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | tid | 0 | cold | 3.44 | 4 | 443527 | 1 |
| localities/hilbert-str-wkb-1048576 | tid | 0 | warm | 1.86 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | tid | 20 | cold | 104.31 | 4 | 443527 | 1 |
| localities/hilbert-str-wkb-1048576 | tid | 20 | warm | 4.91 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-1048576 | tid | 80 | cold | 349.97 | 4 | 443527 | 1 |
| localities/hilbert-str-wkb-1048576 | tid | 80 | warm | 5.27 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | bbox-0 | -1 | cold | 1.70 | 0 | 386524 | 3 |
| localities/hilbert-str-wkb-262144 | bbox-0 | -1 | warm | 1.32 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | bbox-0 | 0 | cold | 4.59 | 7 | 386524 | 3 |
| localities/hilbert-str-wkb-262144 | bbox-0 | 0 | warm | 1.34 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | bbox-0 | 20 | cold | 173.93 | 7 | 386524 | 3 |
| localities/hilbert-str-wkb-262144 | bbox-0 | 20 | warm | 2.42 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | bbox-0 | 80 | cold | 591.71 | 7 | 386524 | 3 |
| localities/hilbert-str-wkb-262144 | bbox-0 | 80 | warm | 4.35 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | bbox-1 | -1 | cold | 4.59 | 0 | 884386 | 7 |
| localities/hilbert-str-wkb-262144 | bbox-1 | -1 | warm | 3.73 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | bbox-1 | 0 | cold | 7.05 | 11 | 884386 | 7 |
| localities/hilbert-str-wkb-262144 | bbox-1 | 0 | warm | 3.33 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | bbox-1 | 20 | cold | 294.95 | 11 | 884386 | 7 |
| localities/hilbert-str-wkb-262144 | bbox-1 | 20 | warm | 10.87 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | bbox-1 | 80 | cold | 940.39 | 11 | 884386 | 7 |
| localities/hilbert-str-wkb-262144 | bbox-1 | 80 | warm | 9.70 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | bbox-2 | -1 | cold | 105.38 | 0 | 1.73214e+07 | 143 |
| localities/hilbert-str-wkb-262144 | bbox-2 | -1 | warm | 93.35 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | bbox-2 | 0 | cold | 155.01 | 159 | 1.73214e+07 | 143 |
| localities/hilbert-str-wkb-262144 | bbox-2 | 0 | warm | 90.30 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | bbox-2 | 20 | cold | 4400.97 | 159 | 1.73214e+07 | 143 |
| localities/hilbert-str-wkb-262144 | bbox-2 | 20 | warm | 125.65 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | bbox-2 | 80 | cold | 13704.71 | 159 | 1.73214e+07 | 143 |
| localities/hilbert-str-wkb-262144 | bbox-2 | 80 | warm | 124.16 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | class | -1 | cold | 56.21 | 0 | 1.67477e+07 | 143 |
| localities/hilbert-str-wkb-262144 | class | -1 | warm | 50.49 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | class | 0 | cold | 109.70 | 146 | 1.67477e+07 | 143 |
| localities/hilbert-str-wkb-262144 | class | 0 | warm | 45.95 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | class | 20 | cold | 3898.07 | 146 | 1.67477e+07 | 143 |
| localities/hilbert-str-wkb-262144 | class | 20 | warm | 65.03 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | class | 80 | cold | 12506.28 | 146 | 1.67477e+07 | 143 |
| localities/hilbert-str-wkb-262144 | class | 80 | warm | 69.40 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | fid | -1 | cold | 0.58 | 0 | 131899 | 1 |
| localities/hilbert-str-wkb-262144 | fid | -1 | warm | 0.43 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | fid | 0 | cold | 1.85 | 4 | 131899 | 1 |
| localities/hilbert-str-wkb-262144 | fid | 0 | warm | 0.42 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | fid | 20 | cold | 104.84 | 4 | 131899 | 1 |
| localities/hilbert-str-wkb-262144 | fid | 20 | warm | 1.91 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | fid | 80 | cold | 334.21 | 4 | 131899 | 1 |
| localities/hilbert-str-wkb-262144 | fid | 80 | warm | 0.92 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | tid | -1 | cold | 3.15 | 0 | 131910 | 1 |
| localities/hilbert-str-wkb-262144 | tid | -1 | warm | 2.75 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | tid | 0 | cold | 4.31 | 4 | 131910 | 1 |
| localities/hilbert-str-wkb-262144 | tid | 0 | warm | 2.58 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | tid | 20 | cold | 110.50 | 4 | 131910 | 1 |
| localities/hilbert-str-wkb-262144 | tid | 20 | warm | 6.99 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-262144 | tid | 80 | cold | 344.84 | 4 | 131910 | 1 |
| localities/hilbert-str-wkb-262144 | tid | 80 | warm | 2.84 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | bbox-0 | -1 | cold | 13.09 | 0 | 4.53484e+06 | 3 |
| localities/hilbert-str-wkb-4194304 | bbox-0 | -1 | warm | 10.97 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | bbox-0 | 0 | cold | 16.90 | 7 | 4.53484e+06 | 3 |
| localities/hilbert-str-wkb-4194304 | bbox-0 | 0 | warm | 10.23 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | bbox-0 | 20 | cold | 199.08 | 7 | 4.53484e+06 | 3 |
| localities/hilbert-str-wkb-4194304 | bbox-0 | 20 | warm | 20.84 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | bbox-0 | 80 | cold | 638.07 | 7 | 4.53484e+06 | 3 |
| localities/hilbert-str-wkb-4194304 | bbox-0 | 80 | warm | 22.35 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | bbox-1 | -1 | cold | 13.96 | 0 | 4.56745e+06 | 3 |
| localities/hilbert-str-wkb-4194304 | bbox-1 | -1 | warm | 12.03 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | bbox-1 | 0 | cold | 19.16 | 9 | 4.56745e+06 | 3 |
| localities/hilbert-str-wkb-4194304 | bbox-1 | 0 | warm | 11.83 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | bbox-1 | 20 | cold | 270.29 | 9 | 4.56745e+06 | 3 |
| localities/hilbert-str-wkb-4194304 | bbox-1 | 20 | warm | 25.58 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | bbox-1 | 80 | cold | 811.01 | 9 | 4.56745e+06 | 3 |
| localities/hilbert-str-wkb-4194304 | bbox-1 | 80 | warm | 27.08 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | bbox-2 | -1 | cold | 96.30 | 0 | 1.52718e+07 | 9 |
| localities/hilbert-str-wkb-4194304 | bbox-2 | -1 | warm | 89.47 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | bbox-2 | 0 | cold | 117.24 | 53 | 1.52718e+07 | 9 |
| localities/hilbert-str-wkb-4194304 | bbox-2 | 0 | warm | 84.11 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | bbox-2 | 20 | cold | 1519.00 | 53 | 1.52718e+07 | 9 |
| localities/hilbert-str-wkb-4194304 | bbox-2 | 20 | warm | 89.33 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | bbox-2 | 80 | cold | 4760.12 | 53 | 1.52718e+07 | 9 |
| localities/hilbert-str-wkb-4194304 | bbox-2 | 80 | warm | 111.49 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | class | -1 | cold | 49.58 | 0 | 1.46978e+07 | 9 |
| localities/hilbert-str-wkb-4194304 | class | -1 | warm | 42.21 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | class | 0 | cold | 58.83 | 12 | 1.46978e+07 | 9 |
| localities/hilbert-str-wkb-4194304 | class | 0 | warm | 41.40 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | class | 20 | cold | 428.59 | 12 | 1.46978e+07 | 9 |
| localities/hilbert-str-wkb-4194304 | class | 20 | warm | 58.94 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | class | 80 | cold | 1166.08 | 12 | 1.46978e+07 | 9 |
| localities/hilbert-str-wkb-4194304 | class | 80 | warm | 70.45 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | fid | -1 | cold | 4.36 | 0 | 1.68397e+06 | 1 |
| localities/hilbert-str-wkb-4194304 | fid | -1 | warm | 3.75 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | fid | 0 | cold | 6.86 | 4 | 1.68397e+06 | 1 |
| localities/hilbert-str-wkb-4194304 | fid | 0 | warm | 3.35 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | fid | 20 | cold | 108.91 | 4 | 1.68397e+06 | 1 |
| localities/hilbert-str-wkb-4194304 | fid | 20 | warm | 9.85 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | fid | 80 | cold | 355.52 | 4 | 1.68397e+06 | 1 |
| localities/hilbert-str-wkb-4194304 | fid | 80 | warm | 9.49 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | tid | -1 | cold | 20.44 | 0 | 1.68397e+06 | 1 |
| localities/hilbert-str-wkb-4194304 | tid | -1 | warm | 17.80 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | tid | 0 | cold | 18.78 | 4 | 1.68397e+06 | 1 |
| localities/hilbert-str-wkb-4194304 | tid | 0 | warm | 16.77 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | tid | 20 | cold | 135.36 | 4 | 1.68397e+06 | 1 |
| localities/hilbert-str-wkb-4194304 | tid | 20 | warm | 26.06 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-4194304 | tid | 80 | cold | 382.12 | 4 | 1.68397e+06 | 1 |
| localities/hilbert-str-wkb-4194304 | tid | 80 | warm | 28.23 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | bbox-0 | -1 | cold | 1.21 | 0 | 147812 | 4 |
| localities/hilbert-str-wkb-65536 | bbox-0 | -1 | warm | 1.04 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | bbox-0 | 0 | cold | 2.56 | 7 | 147812 | 4 |
| localities/hilbert-str-wkb-65536 | bbox-0 | 0 | warm | 0.96 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | bbox-0 | 20 | cold | 174.97 | 7 | 147812 | 4 |
| localities/hilbert-str-wkb-65536 | bbox-0 | 20 | warm | 3.97 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | bbox-0 | 80 | cold | 602.90 | 7 | 147812 | 4 |
| localities/hilbert-str-wkb-65536 | bbox-0 | 80 | warm | 3.55 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | bbox-1 | -1 | cold | 3.20 | 0 | 525888 | 16 |
| localities/hilbert-str-wkb-65536 | bbox-1 | -1 | warm | 3.08 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | bbox-1 | 0 | cold | 5.27 | 12 | 525888 | 16 |
| localities/hilbert-str-wkb-65536 | bbox-1 | 0 | warm | 2.99 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | bbox-1 | 20 | cold | 301.44 | 12 | 525888 | 16 |
| localities/hilbert-str-wkb-65536 | bbox-1 | 20 | warm | 6.91 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | bbox-1 | 80 | cold | 1031.05 | 12 | 525888 | 16 |
| localities/hilbert-str-wkb-65536 | bbox-1 | 80 | warm | 9.81 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | bbox-2 | -1 | cold | 132.03 | 0 | 1.90919e+07 | 616 |
| localities/hilbert-str-wkb-65536 | bbox-2 | -1 | warm | 107.53 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | bbox-2 | 0 | cold | 164.41 | 167 | 1.90919e+07 | 616 |
| localities/hilbert-str-wkb-65536 | bbox-2 | 0 | warm | 101.34 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | bbox-2 | 20 | cold | 4653.36 | 167 | 1.90919e+07 | 616 |
| localities/hilbert-str-wkb-65536 | bbox-2 | 20 | warm | 132.23 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | bbox-2 | 80 | cold | 14719.58 | 167 | 1.90919e+07 | 616 |
| localities/hilbert-str-wkb-65536 | bbox-2 | 80 | warm | 131.69 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | class | -1 | cold | 70.93 | 0 | 1.85514e+07 | 616 |
| localities/hilbert-str-wkb-65536 | class | -1 | warm | 61.92 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | class | 0 | cold | 175.06 | 621 | 1.85514e+07 | 616 |
| localities/hilbert-str-wkb-65536 | class | 0 | warm | 59.67 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | class | 20 | cold | 15753.71 | 621 | 1.85514e+07 | 616 |
| localities/hilbert-str-wkb-65536 | class | 20 | warm | 88.88 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | class | 80 | cold | 53339.14 | 621 | 1.85514e+07 | 616 |
| localities/hilbert-str-wkb-65536 | class | 80 | warm | 117.75 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | fid | -1 | cold | 0.33 | 0 | 46617 | 1 |
| localities/hilbert-str-wkb-65536 | fid | -1 | warm | 0.22 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | fid | 0 | cold | 1.17 | 4 | 46617 | 1 |
| localities/hilbert-str-wkb-65536 | fid | 0 | warm | 0.22 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | fid | 20 | cold | 103.25 | 4 | 46617 | 1 |
| localities/hilbert-str-wkb-65536 | fid | 20 | warm | 0.88 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | fid | 80 | cold | 342.14 | 4 | 46617 | 1 |
| localities/hilbert-str-wkb-65536 | fid | 80 | warm | 1.06 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | tid | -1 | cold | 1.03 | 0 | 46668 | 1 |
| localities/hilbert-str-wkb-65536 | tid | -1 | warm | 0.85 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | tid | 0 | cold | 1.76 | 4 | 46668 | 1 |
| localities/hilbert-str-wkb-65536 | tid | 0 | warm | 0.77 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | tid | 20 | cold | 100.43 | 4 | 46668 | 1 |
| localities/hilbert-str-wkb-65536 | tid | 20 | warm | 2.35 | 0 | 0 | 0 |
| localities/hilbert-str-wkb-65536 | tid | 80 | cold | 344.67 | 4 | 46668 | 1 |
| localities/hilbert-str-wkb-65536 | tid | 80 | warm | 3.18 | 0 | 0 | 0 |
| localities/reference-iom-262144 | bbox-0 | -1 | cold | 8.37 | 0 | 327006 | 4 |
| localities/reference-iom-262144 | bbox-0 | -1 | warm | 8.16 | 0 | 0 | 0 |
| localities/reference-iom-262144 | bbox-0 | 0 | cold | 13.00 | 22 | 327006 | 4 |
| localities/reference-iom-262144 | bbox-0 | 0 | warm | 7.42 | 0 | 0 | 0 |
| localities/reference-iom-262144 | bbox-0 | 20 | cold | 562.39 | 22 | 327006 | 4 |
| localities/reference-iom-262144 | bbox-0 | 20 | warm | 18.70 | 0 | 0 | 0 |
| localities/reference-iom-262144 | bbox-0 | 80 | cold | 1967.98 | 22 | 327006 | 4 |
| localities/reference-iom-262144 | bbox-0 | 80 | warm | 20.25 | 0 | 0 | 0 |
| localities/reference-iom-262144 | bbox-1 | -1 | cold | 75.22 | 0 | 3.26554e+06 | 45 |
| localities/reference-iom-262144 | bbox-1 | -1 | warm | 73.31 | 0 | 0 | 0 |
| localities/reference-iom-262144 | bbox-1 | 0 | cold | 104.42 | 116 | 3.26554e+06 | 45 |
| localities/reference-iom-262144 | bbox-1 | 0 | warm | 72.91 | 0 | 0 | 0 |
| localities/reference-iom-262144 | bbox-1 | 20 | cold | 3037.30 | 116 | 3.26554e+06 | 45 |
| localities/reference-iom-262144 | bbox-1 | 20 | warm | 101.59 | 0 | 0 | 0 |
| localities/reference-iom-262144 | bbox-1 | 80 | cold | 10313.47 | 116 | 3.26554e+06 | 45 |
| localities/reference-iom-262144 | bbox-1 | 80 | warm | 101.54 | 0 | 0 | 0 |
| localities/reference-iom-262144 | bbox-2 | -1 | cold | 1022.09 | 0 | 2.48746e+07 | 349 |
| localities/reference-iom-262144 | bbox-2 | -1 | warm | 1000.82 | 0 | 0 | 0 |
| localities/reference-iom-262144 | bbox-2 | 0 | cold | 1336.33 | 830 | 2.48746e+07 | 349 |
| localities/reference-iom-262144 | bbox-2 | 0 | warm | 1012.26 | 0 | 0 | 0 |
| localities/reference-iom-262144 | bbox-2 | 20 | cold | 23194.35 | 830 | 2.48746e+07 | 349 |
| localities/reference-iom-262144 | bbox-2 | 20 | warm | 1032.29 | 0 | 0 | 0 |
| localities/reference-iom-262144 | bbox-2 | 80 | cold | 75437.11 | 830 | 2.48746e+07 | 349 |
| localities/reference-iom-262144 | bbox-2 | 80 | warm | 1067.45 | 0 | 0 | 0 |
| localities/reference-iom-262144 | class | -1 | cold | 1006.17 | 0 | 2.43464e+07 | 349 |
| localities/reference-iom-262144 | class | -1 | warm | 984.89 | 0 | 0 | 0 |
| localities/reference-iom-262144 | class | 0 | cold | 1270.90 | 722 | 2.43464e+07 | 349 |
| localities/reference-iom-262144 | class | 0 | warm | 1001.47 | 0 | 0 | 0 |
| localities/reference-iom-262144 | class | 20 | cold | 20426.76 | 722 | 2.43464e+07 | 349 |
| localities/reference-iom-262144 | class | 20 | warm | 1012.06 | 0 | 0 | 0 |
| localities/reference-iom-262144 | class | 80 | cold | 65083.57 | 722 | 2.43464e+07 | 349 |
| localities/reference-iom-262144 | class | 80 | warm | 1076.28 | 0 | 0 | 0 |
| localities/reference-iom-262144 | tid | -1 | cold | 0.99 | 0 | 87602 | 1 |
| localities/reference-iom-262144 | tid | -1 | warm | 0.42 | 0 | 0 | 0 |
| localities/reference-iom-262144 | tid | 0 | cold | 2.59 | 10 | 87602 | 1 |
| localities/reference-iom-262144 | tid | 0 | warm | 0.40 | 0 | 0 | 0 |
| localities/reference-iom-262144 | tid | 20 | cold | 251.07 | 10 | 87602 | 1 |
| localities/reference-iom-262144 | tid | 20 | warm | 1.25 | 0 | 0 | 0 |
| localities/reference-iom-262144 | tid | 80 | cold | 848.69 | 10 | 87602 | 1 |
| localities/reference-iom-262144 | tid | 80 | warm | 1.35 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | bbox-0 | -1 | cold | 2.61 | 0 | 638670 | 4 |
| localities/reference-wkb-262144 | bbox-0 | -1 | warm | 1.91 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | bbox-0 | 0 | cold | 6.91 | 22 | 638670 | 4 |
| localities/reference-wkb-262144 | bbox-0 | 0 | warm | 2.02 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | bbox-0 | 20 | cold | 595.90 | 22 | 638670 | 4 |
| localities/reference-wkb-262144 | bbox-0 | 20 | warm | 5.52 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | bbox-0 | 80 | cold | 1937.38 | 22 | 638670 | 4 |
| localities/reference-wkb-262144 | bbox-0 | 80 | warm | 6.45 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | bbox-1 | -1 | cold | 17.15 | 0 | 6.06191e+06 | 40 |
| localities/reference-wkb-262144 | bbox-1 | -1 | warm | 14.67 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | bbox-1 | 0 | cold | 40.35 | 106 | 6.06191e+06 | 40 |
| localities/reference-wkb-262144 | bbox-1 | 0 | warm | 13.72 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | bbox-1 | 20 | cold | 2917.86 | 106 | 6.06191e+06 | 40 |
| localities/reference-wkb-262144 | bbox-1 | 20 | warm | 33.63 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | bbox-1 | 80 | cold | 9309.46 | 106 | 6.06191e+06 | 40 |
| localities/reference-wkb-262144 | bbox-1 | 80 | warm | 34.74 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | bbox-2 | -1 | cold | 125.74 | 0 | 2.18488e+07 | 143 |
| localities/reference-wkb-262144 | bbox-2 | -1 | warm | 106.64 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | bbox-2 | 0 | cold | 237.69 | 418 | 2.18488e+07 | 143 |
| localities/reference-wkb-262144 | bbox-2 | 0 | warm | 100.85 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | bbox-2 | 20 | cold | 11671.09 | 418 | 2.18488e+07 | 143 |
| localities/reference-wkb-262144 | bbox-2 | 20 | warm | 135.10 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | bbox-2 | 80 | cold | 36364.88 | 418 | 2.18488e+07 | 143 |
| localities/reference-wkb-262144 | bbox-2 | 80 | warm | 132.81 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | class | -1 | cold | 73.05 | 0 | 2.12833e+07 | 143 |
| localities/reference-wkb-262144 | class | -1 | warm | 52.66 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | class | 0 | cold | 154.56 | 300 | 2.12833e+07 | 143 |
| localities/reference-wkb-262144 | class | 0 | warm | 55.22 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | class | 20 | cold | 8367.65 | 300 | 2.12833e+07 | 143 |
| localities/reference-wkb-262144 | class | 20 | warm | 85.67 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | class | 80 | cold | 26307.87 | 300 | 2.12833e+07 | 143 |
| localities/reference-wkb-262144 | class | 80 | warm | 90.47 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | fid | -1 | cold | 0.66 | 0 | 169738 | 1 |
| localities/reference-wkb-262144 | fid | -1 | warm | 0.41 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | fid | 0 | cold | 3.30 | 10 | 169738 | 1 |
| localities/reference-wkb-262144 | fid | 0 | warm | 0.37 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | fid | 20 | cold | 276.58 | 10 | 169738 | 1 |
| localities/reference-wkb-262144 | fid | 20 | warm | 0.77 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | fid | 80 | cold | 869.89 | 10 | 169738 | 1 |
| localities/reference-wkb-262144 | fid | 80 | warm | 1.29 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | tid | -1 | cold | 0.72 | 0 | 165047 | 1 |
| localities/reference-wkb-262144 | tid | -1 | warm | 0.45 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | tid | 0 | cold | 2.45 | 10 | 165047 | 1 |
| localities/reference-wkb-262144 | tid | 0 | warm | 0.60 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | tid | 20 | cold | 265.91 | 10 | 165047 | 1 |
| localities/reference-wkb-262144 | tid | 20 | warm | 0.78 | 0 | 0 | 0 |
| localities/reference-wkb-262144 | tid | 80 | cold | 861.82 | 10 | 165047 | 1 |
| localities/reference-wkb-262144 | tid | 80 | warm | 1.11 | 0 | 0 | 0 |
| localities/str-iom-262144 | bbox-0 | -1 | cold | 8.16 | 0 | 303626 | 4 |
| localities/str-iom-262144 | bbox-0 | -1 | warm | 7.89 | 0 | 0 | 0 |
| localities/str-iom-262144 | bbox-0 | 0 | cold | 10.23 | 8 | 303626 | 4 |
| localities/str-iom-262144 | bbox-0 | 0 | warm | 7.37 | 0 | 0 | 0 |
| localities/str-iom-262144 | bbox-0 | 20 | cold | 232.59 | 8 | 303626 | 4 |
| localities/str-iom-262144 | bbox-0 | 20 | warm | 14.76 | 0 | 0 | 0 |
| localities/str-iom-262144 | bbox-0 | 80 | cold | 709.31 | 8 | 303626 | 4 |
| localities/str-iom-262144 | bbox-0 | 80 | warm | 16.18 | 0 | 0 | 0 |
| localities/str-iom-262144 | bbox-1 | -1 | cold | 78.55 | 0 | 3.21805e+06 | 45 |
| localities/str-iom-262144 | bbox-1 | -1 | warm | 76.61 | 0 | 0 | 0 |
| localities/str-iom-262144 | bbox-1 | 0 | cold | 88.35 | 43 | 3.21805e+06 | 45 |
| localities/str-iom-262144 | bbox-1 | 0 | warm | 78.13 | 0 | 0 | 0 |
| localities/str-iom-262144 | bbox-1 | 20 | cold | 1317.24 | 43 | 3.21805e+06 | 45 |
| localities/str-iom-262144 | bbox-1 | 20 | warm | 84.30 | 0 | 0 | 0 |
| localities/str-iom-262144 | bbox-1 | 80 | cold | 3917.80 | 43 | 3.21805e+06 | 45 |
| localities/str-iom-262144 | bbox-1 | 80 | warm | 82.87 | 0 | 0 | 0 |
| localities/str-iom-262144 | bbox-2 | -1 | cold | 1105.45 | 0 | 2.48734e+07 | 349 |
| localities/str-iom-262144 | bbox-2 | -1 | warm | 1062.52 | 0 | 0 | 0 |
| localities/str-iom-262144 | bbox-2 | 0 | cold | 1182.76 | 167 | 2.48734e+07 | 349 |
| localities/str-iom-262144 | bbox-2 | 0 | warm | 1074.76 | 0 | 0 | 0 |
| localities/str-iom-262144 | bbox-2 | 20 | cold | 6124.78 | 167 | 2.48734e+07 | 349 |
| localities/str-iom-262144 | bbox-2 | 20 | warm | 1062.80 | 0 | 0 | 0 |
| localities/str-iom-262144 | bbox-2 | 80 | cold | 17041.14 | 167 | 2.48734e+07 | 349 |
| localities/str-iom-262144 | bbox-2 | 80 | warm | 1138.17 | 0 | 0 | 0 |
| localities/str-iom-262144 | class | -1 | cold | 1056.27 | 0 | 2.43163e+07 | 349 |
| localities/str-iom-262144 | class | -1 | warm | 1033.67 | 0 | 0 | 0 |
| localities/str-iom-262144 | class | 0 | cold | 1240.98 | 353 | 2.43163e+07 | 349 |
| localities/str-iom-262144 | class | 0 | warm | 1054.30 | 0 | 0 | 0 |
| localities/str-iom-262144 | class | 20 | cold | 11954.38 | 353 | 2.43163e+07 | 349 |
| localities/str-iom-262144 | class | 20 | warm | 1078.44 | 0 | 0 | 0 |
| localities/str-iom-262144 | class | 80 | cold | 33835.59 | 353 | 2.43163e+07 | 349 |
| localities/str-iom-262144 | class | 80 | warm | 1070.71 | 0 | 0 | 0 |
| localities/str-iom-262144 | fid | -1 | cold | 0.90 | 0 | 94131 | 1 |
| localities/str-iom-262144 | fid | -1 | warm | 0.57 | 0 | 0 | 0 |
| localities/str-iom-262144 | fid | 0 | cold | 2.64 | 4 | 94131 | 1 |
| localities/str-iom-262144 | fid | 0 | warm | 0.57 | 0 | 0 | 0 |
| localities/str-iom-262144 | fid | 20 | cold | 115.43 | 4 | 94131 | 1 |
| localities/str-iom-262144 | fid | 20 | warm | 1.39 | 0 | 0 | 0 |
| localities/str-iom-262144 | fid | 80 | cold | 349.13 | 4 | 94131 | 1 |
| localities/str-iom-262144 | fid | 80 | warm | 1.43 | 0 | 0 | 0 |
| localities/str-iom-262144 | tid | -1 | cold | 0.65 | 0 | 94157 | 1 |
| localities/str-iom-262144 | tid | -1 | warm | 0.50 | 0 | 0 | 0 |
| localities/str-iom-262144 | tid | 0 | cold | 1.63 | 4 | 94157 | 1 |
| localities/str-iom-262144 | tid | 0 | warm | 0.48 | 0 | 0 | 0 |
| localities/str-iom-262144 | tid | 20 | cold | 112.80 | 4 | 94157 | 1 |
| localities/str-iom-262144 | tid | 20 | warm | 1.28 | 0 | 0 | 0 |
| localities/str-iom-262144 | tid | 80 | cold | 343.25 | 4 | 94157 | 1 |
| localities/str-iom-262144 | tid | 80 | warm | 1.52 | 0 | 0 | 0 |
| localities/str-wkb-262144 | bbox-0 | -1 | cold | 3.49 | 0 | 615309 | 4 |
| localities/str-wkb-262144 | bbox-0 | -1 | warm | 1.90 | 0 | 0 | 0 |
| localities/str-wkb-262144 | bbox-0 | 0 | cold | 5.25 | 8 | 615309 | 4 |
| localities/str-wkb-262144 | bbox-0 | 0 | warm | 2.04 | 0 | 0 | 0 |
| localities/str-wkb-262144 | bbox-0 | 20 | cold | 210.57 | 8 | 615309 | 4 |
| localities/str-wkb-262144 | bbox-0 | 20 | warm | 3.61 | 0 | 0 | 0 |
| localities/str-wkb-262144 | bbox-0 | 80 | cold | 688.64 | 8 | 615309 | 4 |
| localities/str-wkb-262144 | bbox-0 | 80 | warm | 5.22 | 0 | 0 | 0 |
| localities/str-wkb-262144 | bbox-1 | -1 | cold | 17.12 | 0 | 6.01394e+06 | 40 |
| localities/str-wkb-262144 | bbox-1 | -1 | warm | 14.53 | 0 | 0 | 0 |
| localities/str-wkb-262144 | bbox-1 | 0 | cold | 29.67 | 32 | 6.01394e+06 | 40 |
| localities/str-wkb-262144 | bbox-1 | 0 | warm | 13.35 | 0 | 0 | 0 |
| localities/str-wkb-262144 | bbox-1 | 20 | cold | 833.56 | 32 | 6.01394e+06 | 40 |
| localities/str-wkb-262144 | bbox-1 | 20 | warm | 27.37 | 0 | 0 | 0 |
| localities/str-wkb-262144 | bbox-1 | 80 | cold | 2777.02 | 32 | 6.01394e+06 | 40 |
| localities/str-wkb-262144 | bbox-1 | 80 | warm | 29.21 | 0 | 0 | 0 |
| localities/str-wkb-262144 | bbox-2 | -1 | cold | 117.64 | 0 | 2.18412e+07 | 143 |
| localities/str-wkb-262144 | bbox-2 | -1 | warm | 101.74 | 0 | 0 | 0 |
| localities/str-wkb-262144 | bbox-2 | 0 | cold | 240.66 | 165 | 2.18412e+07 | 143 |
| localities/str-wkb-262144 | bbox-2 | 0 | warm | 100.18 | 0 | 0 | 0 |
| localities/str-wkb-262144 | bbox-2 | 20 | cold | 4526.36 | 165 | 2.18412e+07 | 143 |
| localities/str-wkb-262144 | bbox-2 | 20 | warm | 129.86 | 0 | 0 | 0 |
| localities/str-wkb-262144 | bbox-2 | 80 | cold | 14541.92 | 165 | 2.18412e+07 | 143 |
| localities/str-wkb-262144 | bbox-2 | 80 | warm | 129.16 | 0 | 0 | 0 |
| localities/str-wkb-262144 | class | -1 | cold | 65.29 | 0 | 2.12675e+07 | 143 |
| localities/str-wkb-262144 | class | -1 | warm | 57.17 | 0 | 0 | 0 |
| localities/str-wkb-262144 | class | 0 | cold | 146.92 | 146 | 2.12675e+07 | 143 |
| localities/str-wkb-262144 | class | 0 | warm | 52.80 | 0 | 0 | 0 |
| localities/str-wkb-262144 | class | 20 | cold | 3884.06 | 146 | 2.12675e+07 | 143 |
| localities/str-wkb-262144 | class | 20 | warm | 87.48 | 0 | 0 | 0 |
| localities/str-wkb-262144 | class | 80 | cold | 12676.99 | 146 | 2.12675e+07 | 143 |
| localities/str-wkb-262144 | class | 80 | warm | 89.07 | 0 | 0 | 0 |
| localities/str-wkb-262144 | fid | -1 | cold | 0.59 | 0 | 172086 | 1 |
| localities/str-wkb-262144 | fid | -1 | warm | 0.42 | 0 | 0 | 0 |
| localities/str-wkb-262144 | fid | 0 | cold | 2.43 | 4 | 172086 | 1 |
| localities/str-wkb-262144 | fid | 0 | warm | 0.46 | 0 | 0 | 0 |
| localities/str-wkb-262144 | fid | 20 | cold | 102.51 | 4 | 172086 | 1 |
| localities/str-wkb-262144 | fid | 20 | warm | 1.84 | 0 | 0 | 0 |
| localities/str-wkb-262144 | fid | 80 | cold | 348.20 | 4 | 172086 | 1 |
| localities/str-wkb-262144 | fid | 80 | warm | 1.74 | 0 | 0 | 0 |
| localities/str-wkb-262144 | tid | -1 | cold | 1.02 | 0 | 172097 | 1 |
| localities/str-wkb-262144 | tid | -1 | warm | 0.48 | 0 | 0 | 0 |
| localities/str-wkb-262144 | tid | 0 | cold | 2.04 | 4 | 172097 | 1 |
| localities/str-wkb-262144 | tid | 0 | warm | 0.46 | 0 | 0 | 0 |
| localities/str-wkb-262144 | tid | 20 | cold | 102.96 | 4 | 172097 | 1 |
| localities/str-wkb-262144 | tid | 20 | warm | 1.65 | 0 | 0 | 0 |
| localities/str-wkb-262144 | tid | 80 | cold | 341.61 | 4 | 172097 | 1 |
| localities/str-wkb-262144 | tid | 80 | warm | 1.68 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | bbox-0 | -1 | cold | 9.36 | 0 | 335840 | 4 |
| localities/x-direct-iom-262144 | bbox-0 | -1 | warm | 8.47 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | bbox-0 | 0 | cold | 11.06 | 10 | 335840 | 4 |
| localities/x-direct-iom-262144 | bbox-0 | 0 | warm | 7.42 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | bbox-0 | 20 | cold | 264.88 | 10 | 335840 | 4 |
| localities/x-direct-iom-262144 | bbox-0 | 20 | warm | 18.79 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | bbox-0 | 80 | cold | 866.45 | 10 | 335840 | 4 |
| localities/x-direct-iom-262144 | bbox-0 | 80 | warm | 8.05 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | bbox-1 | -1 | cold | 79.39 | 0 | 3.28288e+06 | 45 |
| localities/x-direct-iom-262144 | bbox-1 | -1 | warm | 76.68 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | bbox-1 | 0 | cold | 96.07 | 55 | 3.28288e+06 | 45 |
| localities/x-direct-iom-262144 | bbox-1 | 0 | warm | 77.74 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | bbox-1 | 20 | cold | 1538.37 | 55 | 3.28288e+06 | 45 |
| localities/x-direct-iom-262144 | bbox-1 | 20 | warm | 104.63 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | bbox-1 | 80 | cold | 4862.15 | 55 | 3.28288e+06 | 45 |
| localities/x-direct-iom-262144 | bbox-1 | 80 | warm | 105.59 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | bbox-2 | -1 | cold | 1092.85 | 0 | 2.48729e+07 | 349 |
| localities/x-direct-iom-262144 | bbox-2 | -1 | warm | 1071.03 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | bbox-2 | 0 | cold | 1265.72 | 389 | 2.48729e+07 | 349 |
| localities/x-direct-iom-262144 | bbox-2 | 0 | warm | 1071.16 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | bbox-2 | 20 | cold | 11717.24 | 389 | 2.48729e+07 | 349 |
| localities/x-direct-iom-262144 | bbox-2 | 20 | warm | 1089.55 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | bbox-2 | 80 | cold | 35843.64 | 389 | 2.48729e+07 | 349 |
| localities/x-direct-iom-262144 | bbox-2 | 80 | warm | 1080.44 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | class | -1 | cold | 1081.42 | 0 | 2.43163e+07 | 349 |
| localities/x-direct-iom-262144 | class | -1 | warm | 1063.99 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | class | 0 | cold | 1258.87 | 353 | 2.43163e+07 | 349 |
| localities/x-direct-iom-262144 | class | 0 | warm | 1040.61 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | class | 20 | cold | 11023.80 | 353 | 2.43163e+07 | 349 |
| localities/x-direct-iom-262144 | class | 20 | warm | 1070.98 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | class | 80 | cold | 32442.68 | 353 | 2.43163e+07 | 349 |
| localities/x-direct-iom-262144 | class | 80 | warm | 1073.23 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | fid | -1 | cold | 0.63 | 0 | 94131 | 1 |
| localities/x-direct-iom-262144 | fid | -1 | warm | 0.53 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | fid | 0 | cold | 1.83 | 4 | 94131 | 1 |
| localities/x-direct-iom-262144 | fid | 0 | warm | 0.56 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | fid | 20 | cold | 100.80 | 4 | 94131 | 1 |
| localities/x-direct-iom-262144 | fid | 20 | warm | 1.53 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | fid | 80 | cold | 340.62 | 4 | 94131 | 1 |
| localities/x-direct-iom-262144 | fid | 80 | warm | 1.40 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | tid | -1 | cold | 0.61 | 0 | 94157 | 1 |
| localities/x-direct-iom-262144 | tid | -1 | warm | 0.50 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | tid | 0 | cold | 2.03 | 4 | 94157 | 1 |
| localities/x-direct-iom-262144 | tid | 0 | warm | 0.56 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | tid | 20 | cold | 98.07 | 4 | 94157 | 1 |
| localities/x-direct-iom-262144 | tid | 20 | warm | 1.15 | 0 | 0 | 0 |
| localities/x-direct-iom-262144 | tid | 80 | cold | 339.95 | 4 | 94157 | 1 |
| localities/x-direct-iom-262144 | tid | 80 | warm | 1.05 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | bbox-0 | -1 | cold | 2.19 | 0 | 647523 | 4 |
| localities/x-direct-wkb-262144 | bbox-0 | -1 | warm | 1.83 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | bbox-0 | 0 | cold | 5.80 | 10 | 647523 | 4 |
| localities/x-direct-wkb-262144 | bbox-0 | 0 | warm | 1.92 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | bbox-0 | 20 | cold | 266.65 | 10 | 647523 | 4 |
| localities/x-direct-wkb-262144 | bbox-0 | 20 | warm | 5.89 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | bbox-0 | 80 | cold | 866.73 | 10 | 647523 | 4 |
| localities/x-direct-wkb-262144 | bbox-0 | 80 | warm | 8.32 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | bbox-1 | -1 | cold | 17.29 | 0 | 6.07878e+06 | 40 |
| localities/x-direct-wkb-262144 | bbox-1 | -1 | warm | 13.96 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | bbox-1 | 0 | cold | 35.49 | 50 | 6.07878e+06 | 40 |
| localities/x-direct-wkb-262144 | bbox-1 | 0 | warm | 13.17 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | bbox-1 | 20 | cold | 1323.92 | 50 | 6.07878e+06 | 40 |
| localities/x-direct-wkb-262144 | bbox-1 | 20 | warm | 34.23 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | bbox-1 | 80 | cold | 4309.61 | 50 | 6.07878e+06 | 40 |
| localities/x-direct-wkb-262144 | bbox-1 | 80 | warm | 33.40 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | bbox-2 | -1 | cold | 103.92 | 0 | 2.18407e+07 | 143 |
| localities/x-direct-wkb-262144 | bbox-2 | -1 | warm | 96.87 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | bbox-2 | 0 | cold | 171.28 | 183 | 2.18407e+07 | 143 |
| localities/x-direct-wkb-262144 | bbox-2 | 0 | warm | 92.40 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | bbox-2 | 20 | cold | 4985.12 | 183 | 2.18407e+07 | 143 |
| localities/x-direct-wkb-262144 | bbox-2 | 20 | warm | 130.87 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | bbox-2 | 80 | cold | 16023.28 | 183 | 2.18407e+07 | 143 |
| localities/x-direct-wkb-262144 | bbox-2 | 80 | warm | 129.11 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | class | -1 | cold | 59.86 | 0 | 2.12675e+07 | 143 |
| localities/x-direct-wkb-262144 | class | -1 | warm | 50.60 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | class | 0 | cold | 112.92 | 146 | 2.12675e+07 | 143 |
| localities/x-direct-wkb-262144 | class | 0 | warm | 49.53 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | class | 20 | cold | 3910.29 | 146 | 2.12675e+07 | 143 |
| localities/x-direct-wkb-262144 | class | 20 | warm | 87.51 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | class | 80 | cold | 12684.21 | 146 | 2.12675e+07 | 143 |
| localities/x-direct-wkb-262144 | class | 80 | warm | 86.25 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | fid | -1 | cold | 0.65 | 0 | 172086 | 1 |
| localities/x-direct-wkb-262144 | fid | -1 | warm | 0.41 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | fid | 0 | cold | 1.49 | 4 | 172086 | 1 |
| localities/x-direct-wkb-262144 | fid | 0 | warm | 0.39 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | fid | 20 | cold | 106.30 | 4 | 172086 | 1 |
| localities/x-direct-wkb-262144 | fid | 20 | warm | 1.43 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | fid | 80 | cold | 345.22 | 4 | 172086 | 1 |
| localities/x-direct-wkb-262144 | fid | 80 | warm | 1.14 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | tid | -1 | cold | 0.64 | 0 | 172097 | 1 |
| localities/x-direct-wkb-262144 | tid | -1 | warm | 0.46 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | tid | 0 | cold | 1.53 | 4 | 172097 | 1 |
| localities/x-direct-wkb-262144 | tid | 0 | warm | 0.44 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | tid | 20 | cold | 101.51 | 4 | 172097 | 1 |
| localities/x-direct-wkb-262144 | tid | 20 | warm | 1.21 | 0 | 0 | 0 |
| localities/x-direct-wkb-262144 | tid | 80 | cold | 341.96 | 4 | 172097 | 1 |
| localities/x-direct-wkb-262144 | tid | 80 | warm | 1.34 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | bbox-0 | -1 | cold | 8.19 | 0 | 335840 | 4 |
| localities/x-prefetch-iom-262144 | bbox-0 | -1 | warm | 7.97 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | bbox-0 | 0 | cold | 10.74 | 10 | 335840 | 4 |
| localities/x-prefetch-iom-262144 | bbox-0 | 0 | warm | 7.81 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | bbox-0 | 20 | cold | 295.41 | 10 | 335840 | 4 |
| localities/x-prefetch-iom-262144 | bbox-0 | 20 | warm | 15.15 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | bbox-0 | 80 | cold | 901.74 | 10 | 335840 | 4 |
| localities/x-prefetch-iom-262144 | bbox-0 | 80 | warm | 17.22 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | bbox-1 | -1 | cold | 81.07 | 0 | 3.28288e+06 | 45 |
| localities/x-prefetch-iom-262144 | bbox-1 | -1 | warm | 78.16 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | bbox-1 | 0 | cold | 91.03 | 47 | 3.28288e+06 | 45 |
| localities/x-prefetch-iom-262144 | bbox-1 | 0 | warm | 78.48 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | bbox-1 | 20 | cold | 1455.15 | 47 | 3.28288e+06 | 45 |
| localities/x-prefetch-iom-262144 | bbox-1 | 20 | warm | 84.82 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | bbox-1 | 80 | cold | 4278.80 | 47 | 3.28288e+06 | 45 |
| localities/x-prefetch-iom-262144 | bbox-1 | 80 | warm | 101.00 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | bbox-2 | -1 | cold | 1105.28 | 0 | 2.48729e+07 | 349 |
| localities/x-prefetch-iom-262144 | bbox-2 | -1 | warm | 1113.56 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | bbox-2 | 0 | cold | 1217.13 | 163 | 2.48729e+07 | 349 |
| localities/x-prefetch-iom-262144 | bbox-2 | 0 | warm | 1075.38 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | bbox-2 | 20 | cold | 5966.18 | 163 | 2.48729e+07 | 349 |
| localities/x-prefetch-iom-262144 | bbox-2 | 20 | warm | 1086.73 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | bbox-2 | 80 | cold | 16903.84 | 163 | 2.48729e+07 | 349 |
| localities/x-prefetch-iom-262144 | bbox-2 | 80 | warm | 1085.04 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | class | -1 | cold | 1087.92 | 0 | 2.43163e+07 | 349 |
| localities/x-prefetch-iom-262144 | class | -1 | warm | 1083.64 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | class | 0 | cold | 1297.07 | 353 | 2.43163e+07 | 349 |
| localities/x-prefetch-iom-262144 | class | 0 | warm | 1076.80 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | class | 20 | cold | 12066.83 | 353 | 2.43163e+07 | 349 |
| localities/x-prefetch-iom-262144 | class | 20 | warm | 1106.66 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | class | 80 | cold | 33767.87 | 353 | 2.43163e+07 | 349 |
| localities/x-prefetch-iom-262144 | class | 80 | warm | 1118.06 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | fid | -1 | cold | 0.65 | 0 | 94131 | 1 |
| localities/x-prefetch-iom-262144 | fid | -1 | warm | 0.69 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | fid | 0 | cold | 1.54 | 4 | 94131 | 1 |
| localities/x-prefetch-iom-262144 | fid | 0 | warm | 0.54 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | fid | 20 | cold | 118.03 | 4 | 94131 | 1 |
| localities/x-prefetch-iom-262144 | fid | 20 | warm | 1.97 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | fid | 80 | cold | 346.14 | 4 | 94131 | 1 |
| localities/x-prefetch-iom-262144 | fid | 80 | warm | 1.55 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | tid | -1 | cold | 1.14 | 0 | 94157 | 1 |
| localities/x-prefetch-iom-262144 | tid | -1 | warm | 0.50 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | tid | 0 | cold | 1.53 | 4 | 94157 | 1 |
| localities/x-prefetch-iom-262144 | tid | 0 | warm | 0.49 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | tid | 20 | cold | 117.41 | 4 | 94157 | 1 |
| localities/x-prefetch-iom-262144 | tid | 20 | warm | 1.44 | 0 | 0 | 0 |
| localities/x-prefetch-iom-262144 | tid | 80 | cold | 357.02 | 4 | 94157 | 1 |
| localities/x-prefetch-iom-262144 | tid | 80 | warm | 1.29 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | bbox-0 | -1 | cold | 2.64 | 0 | 647523 | 4 |
| localities/x-prefetch-wkb-262144 | bbox-0 | -1 | warm | 2.05 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | bbox-0 | 0 | cold | 5.00 | 10 | 647523 | 4 |
| localities/x-prefetch-wkb-262144 | bbox-0 | 0 | warm | 2.08 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | bbox-0 | 20 | cold | 257.37 | 10 | 647523 | 4 |
| localities/x-prefetch-wkb-262144 | bbox-0 | 20 | warm | 6.13 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | bbox-0 | 80 | cold | 853.33 | 10 | 647523 | 4 |
| localities/x-prefetch-wkb-262144 | bbox-0 | 80 | warm | 7.83 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | bbox-1 | -1 | cold | 17.88 | 0 | 6.07878e+06 | 40 |
| localities/x-prefetch-wkb-262144 | bbox-1 | -1 | warm | 15.24 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | bbox-1 | 0 | cold | 24.31 | 36 | 6.07878e+06 | 40 |
| localities/x-prefetch-wkb-262144 | bbox-1 | 0 | warm | 13.50 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | bbox-1 | 20 | cold | 942.64 | 36 | 6.07878e+06 | 40 |
| localities/x-prefetch-wkb-262144 | bbox-1 | 20 | warm | 23.28 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | bbox-1 | 80 | cold | 3086.79 | 36 | 6.07878e+06 | 40 |
| localities/x-prefetch-wkb-262144 | bbox-1 | 80 | warm | 23.32 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | bbox-2 | -1 | cold | 120.68 | 0 | 2.18407e+07 | 143 |
| localities/x-prefetch-wkb-262144 | bbox-2 | -1 | warm | 104.90 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | bbox-2 | 0 | cold | 164.97 | 161 | 2.18407e+07 | 143 |
| localities/x-prefetch-wkb-262144 | bbox-2 | 0 | warm | 94.20 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | bbox-2 | 20 | cold | 4406.54 | 161 | 2.18407e+07 | 143 |
| localities/x-prefetch-wkb-262144 | bbox-2 | 20 | warm | 128.32 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | bbox-2 | 80 | cold | 14108.66 | 161 | 2.18407e+07 | 143 |
| localities/x-prefetch-wkb-262144 | bbox-2 | 80 | warm | 127.57 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | class | -1 | cold | 60.81 | 0 | 2.12675e+07 | 143 |
| localities/x-prefetch-wkb-262144 | class | -1 | warm | 57.09 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | class | 0 | cold | 120.02 | 146 | 2.12675e+07 | 143 |
| localities/x-prefetch-wkb-262144 | class | 0 | warm | 52.94 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | class | 20 | cold | 3802.76 | 146 | 2.12675e+07 | 143 |
| localities/x-prefetch-wkb-262144 | class | 20 | warm | 88.62 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | class | 80 | cold | 12669.91 | 146 | 2.12675e+07 | 143 |
| localities/x-prefetch-wkb-262144 | class | 80 | warm | 87.65 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | fid | -1 | cold | 0.54 | 0 | 172086 | 1 |
| localities/x-prefetch-wkb-262144 | fid | -1 | warm | 0.42 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | fid | 0 | cold | 1.56 | 4 | 172086 | 1 |
| localities/x-prefetch-wkb-262144 | fid | 0 | warm | 0.41 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | fid | 20 | cold | 102.57 | 4 | 172086 | 1 |
| localities/x-prefetch-wkb-262144 | fid | 20 | warm | 1.15 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | fid | 80 | cold | 340.25 | 4 | 172086 | 1 |
| localities/x-prefetch-wkb-262144 | fid | 80 | warm | 1.52 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | tid | -1 | cold | 0.68 | 0 | 172097 | 1 |
| localities/x-prefetch-wkb-262144 | tid | -1 | warm | 0.46 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | tid | 0 | cold | 1.64 | 4 | 172097 | 1 |
| localities/x-prefetch-wkb-262144 | tid | 0 | warm | 0.41 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | tid | 20 | cold | 101.64 | 4 | 172097 | 1 |
| localities/x-prefetch-wkb-262144 | tid | 20 | warm | 1.66 | 0 | 0 | 0 |
| localities/x-prefetch-wkb-262144 | tid | 80 | cold | 338.98 | 4 | 172097 | 1 |
| localities/x-prefetch-wkb-262144 | tid | 80 | warm | 1.23 | 0 | 0 | 0 |
| million/reference-iom-262144 | tid | -1 | cold | 0.34 | 0 | 32230 | 1 |
| million/reference-iom-262144 | tid | -1 | warm | 0.26 | 0 | 0 | 0 |
| million/reference-iom-262144 | tid | 0 | cold | 4.44 | 10 | 32230 | 1 |
| million/reference-iom-262144 | tid | 0 | warm | 0.27 | 0 | 0 | 0 |
| million/reference-iom-262144 | tid | 20 | cold | 258.63 | 10 | 32230 | 1 |
| million/reference-iom-262144 | tid | 20 | warm | 1.14 | 0 | 0 | 0 |
| million/reference-iom-262144 | tid | 80 | cold | 859.97 | 10 | 32230 | 1 |
| million/reference-iom-262144 | tid | 80 | warm | 2.16 | 0 | 0 | 0 |
| million/reference-wkb-262144 | fid | -1 | cold | 0.41 | 0 | 30632 | 1 |
| million/reference-wkb-262144 | fid | -1 | warm | 0.22 | 0 | 0 | 0 |
| million/reference-wkb-262144 | fid | 0 | cold | 3.84 | 10 | 30632 | 1 |
| million/reference-wkb-262144 | fid | 0 | warm | 0.24 | 0 | 0 | 0 |
| million/reference-wkb-262144 | fid | 20 | cold | 253.09 | 10 | 30632 | 1 |
| million/reference-wkb-262144 | fid | 20 | warm | 1.85 | 0 | 0 | 0 |
| million/reference-wkb-262144 | fid | 80 | cold | 854.50 | 10 | 30632 | 1 |
| million/reference-wkb-262144 | fid | 80 | warm | 1.04 | 0 | 0 | 0 |
| million/reference-wkb-262144 | tid | -1 | cold | 0.29 | 0 | 34671 | 1 |
| million/reference-wkb-262144 | tid | -1 | warm | 0.23 | 0 | 0 | 0 |
| million/reference-wkb-262144 | tid | 0 | cold | 3.85 | 10 | 34671 | 1 |
| million/reference-wkb-262144 | tid | 0 | warm | 0.23 | 0 | 0 | 0 |
| million/reference-wkb-262144 | tid | 20 | cold | 250.00 | 10 | 34671 | 1 |
| million/reference-wkb-262144 | tid | 20 | warm | 0.25 | 0 | 0 | 0 |
| million/reference-wkb-262144 | tid | 80 | cold | 852.59 | 10 | 34671 | 1 |
| million/reference-wkb-262144 | tid | 80 | warm | 0.77 | 0 | 0 | 0 |
| million/x-direct-iom-262144 | fid | -1 | cold | 0.58 | 0 | 41787 | 1 |
| million/x-direct-iom-262144 | fid | -1 | warm | 0.40 | 0 | 0 | 0 |
| million/x-direct-iom-262144 | fid | 0 | cold | 2.34 | 5 | 41787 | 1 |
| million/x-direct-iom-262144 | fid | 0 | warm | 0.40 | 0 | 0 | 0 |
| million/x-direct-iom-262144 | fid | 20 | cold | 120.91 | 5 | 41787 | 1 |
| million/x-direct-iom-262144 | fid | 20 | warm | 0.61 | 0 | 0 | 0 |
| million/x-direct-iom-262144 | fid | 80 | cold | 421.78 | 5 | 41787 | 1 |
| million/x-direct-iom-262144 | fid | 80 | warm | 1.89 | 0 | 0 | 0 |
| million/x-direct-iom-262144 | tid | -1 | cold | 0.49 | 0 | 41787 | 1 |
| million/x-direct-iom-262144 | tid | -1 | warm | 0.39 | 0 | 0 | 0 |
| million/x-direct-iom-262144 | tid | 0 | cold | 2.51 | 5 | 41787 | 1 |
| million/x-direct-iom-262144 | tid | 0 | warm | 0.40 | 0 | 0 | 0 |
| million/x-direct-iom-262144 | tid | 20 | cold | 127.11 | 5 | 41787 | 1 |
| million/x-direct-iom-262144 | tid | 20 | warm | 0.66 | 0 | 0 | 0 |
| million/x-direct-iom-262144 | tid | 80 | cold | 428.02 | 5 | 41787 | 1 |
| million/x-direct-iom-262144 | tid | 80 | warm | 1.00 | 0 | 0 | 0 |
| million/x-direct-wkb-262144 | fid | -1 | cold | 0.44 | 0 | 43144 | 1 |
| million/x-direct-wkb-262144 | fid | -1 | warm | 0.37 | 0 | 0 | 0 |
| million/x-direct-wkb-262144 | fid | 0 | cold | 2.31 | 5 | 43144 | 1 |
| million/x-direct-wkb-262144 | fid | 0 | warm | 0.38 | 0 | 0 | 0 |
| million/x-direct-wkb-262144 | fid | 20 | cold | 127.87 | 5 | 43144 | 1 |
| million/x-direct-wkb-262144 | fid | 20 | warm | 0.65 | 0 | 0 | 0 |
| million/x-direct-wkb-262144 | fid | 80 | cold | 430.57 | 5 | 43144 | 1 |
| million/x-direct-wkb-262144 | fid | 80 | warm | 0.38 | 0 | 0 | 0 |
| million/x-direct-wkb-262144 | tid | -1 | cold | 0.40 | 0 | 43145 | 1 |
| million/x-direct-wkb-262144 | tid | -1 | warm | 0.34 | 0 | 0 | 0 |
| million/x-direct-wkb-262144 | tid | 0 | cold | 2.49 | 5 | 43145 | 1 |
| million/x-direct-wkb-262144 | tid | 0 | warm | 0.35 | 0 | 0 | 0 |
| million/x-direct-wkb-262144 | tid | 20 | cold | 125.45 | 5 | 43145 | 1 |
| million/x-direct-wkb-262144 | tid | 20 | warm | 1.18 | 0 | 0 | 0 |
| million/x-direct-wkb-262144 | tid | 80 | cold | 430.61 | 5 | 43145 | 1 |
| million/x-direct-wkb-262144 | tid | 80 | warm | 1.00 | 0 | 0 | 0 |

## Veränderung gegenüber der Referenz

| Datensatz / Variante | Indexierte Dateigrösse Δ % | TID kalt, HTTP 80 ms: Zeit Δ % | Requests inklusive Öffnen |
|---|---:|---:|---:|
| dmav/hilbert-str-iom-1048576 | +15.51 | -42.65 | 7 vs. 12 |
| dmav/hilbert-str-iom-262144 | +15.51 | -42.24 | 7 vs. 12 |
| dmav/hilbert-str-iom-4194304 | +15.51 | -42.30 | 7 vs. 12 |
| dmav/hilbert-str-iom-65536 | +15.51 | -42.90 | 7 vs. 12 |
| dmav/hilbert-str-wkb-1048576 | -2.48 | -41.43 | 7 vs. 12 |
| dmav/hilbert-str-wkb-262144 | -2.48 | -42.01 | 7 vs. 12 |
| dmav/hilbert-str-wkb-4194304 | -2.48 | -41.81 | 7 vs. 12 |
| dmav/hilbert-str-wkb-65536 | -2.48 | -41.57 | 7 vs. 12 |
| dmav/str-iom-262144 | +15.42 | -41.88 | 7 vs. 12 |
| dmav/str-wkb-262144 | -2.63 | -42.00 | 7 vs. 12 |
| dmav/x-direct-iom-262144 | +15.41 | -42.80 | 7 vs. 12 |
| dmav/x-direct-wkb-262144 | -2.64 | -41.40 | 7 vs. 12 |
| dmav/x-prefetch-iom-262144 | +15.41 | -42.09 | 7 vs. 12 |
| dmav/x-prefetch-wkb-262144 | -2.64 | -41.52 | 7 vs. 12 |
| fixpoints/hilbert-str-iom-1048576 | +2.58 | -42.02 | 8 vs. 14 |
| fixpoints/hilbert-str-iom-262144 | +2.58 | -42.11 | 8 vs. 14 |
| fixpoints/hilbert-str-iom-4194304 | +2.58 | -41.41 | 8 vs. 14 |
| fixpoints/hilbert-str-iom-65536 | +4.61 | -42.09 | 8 vs. 14 |
| fixpoints/hilbert-str-wkb-1048576 | -21.45 | -44.07 | 8 vs. 14 |
| fixpoints/hilbert-str-wkb-262144 | -21.45 | -41.84 | 8 vs. 14 |
| fixpoints/hilbert-str-wkb-4194304 | -21.45 | -44.15 | 8 vs. 14 |
| fixpoints/hilbert-str-wkb-65536 | -21.11 | -43.59 | 8 vs. 14 |
| fixpoints/str-iom-262144 | +2.45 | -42.18 | 8 vs. 14 |
| fixpoints/str-wkb-262144 | -21.56 | -42.35 | 8 vs. 14 |
| fixpoints/x-direct-iom-262144 | +2.45 | -42.45 | 8 vs. 14 |
| fixpoints/x-direct-wkb-262144 | -21.56 | -40.60 | 8 vs. 14 |
| fixpoints/x-prefetch-iom-262144 | +2.45 | -43.05 | 8 vs. 14 |
| fixpoints/x-prefetch-wkb-262144 | -21.56 | -41.20 | 8 vs. 14 |
| localities/hilbert-str-iom-1048576 | -13.29 | -49.55 | 8 vs. 16 |
| localities/hilbert-str-iom-262144 | -8.78 | -47.88 | 8 vs. 16 |
| localities/hilbert-str-iom-4194304 | -13.51 | -43.27 | 8 vs. 16 |
| localities/hilbert-str-iom-65536 | -7.43 | -49.72 | 8 vs. 16 |
| localities/hilbert-str-wkb-1048576 | -17.66 | -49.76 | 8 vs. 16 |
| localities/hilbert-str-wkb-262144 | -12.38 | -50.31 | 8 vs. 16 |
| localities/hilbert-str-wkb-4194304 | -18.56 | -46.59 | 8 vs. 16 |
| localities/hilbert-str-wkb-65536 | -6.91 | -50.11 | 8 vs. 16 |
| localities/str-iom-262144 | -1.03 | -48.97 | 8 vs. 16 |
| localities/str-wkb-262144 | -2.45 | -49.88 | 8 vs. 16 |
| localities/x-direct-iom-262144 | -1.03 | -50.16 | 8 vs. 16 |
| localities/x-direct-wkb-262144 | -2.45 | -50.22 | 8 vs. 16 |
| localities/x-prefetch-iom-262144 | -1.03 | -48.08 | 8 vs. 16 |
| localities/x-prefetch-wkb-262144 | -2.45 | -50.66 | 8 vs. 16 |
| million/x-direct-iom-262144 | -22.90 | -43.42 | 9 vs. 16 |
| million/x-direct-wkb-262144 | -63.61 | -43.11 | 9 vs. 16 |

## Physische Verzeichnisse

| Datensatz / Variante | B+-Baum-Seiten Bytes | Seitenrahmen Bytes | TID-Schlüssel Bytes | TID-Werte Bytes | FID-Schlüssel Bytes | FID-Werte Bytes |
|---|---:|---:|---:|---:|---:|---:|
| dmav/hilbert-str-iom-1048576 | 1521 | 20 | 232 | 285 | 27 | 122 |
| dmav/hilbert-str-iom-262144 | 1521 | 20 | 232 | 285 | 27 | 122 |
| dmav/hilbert-str-iom-4194304 | 1521 | 20 | 232 | 285 | 27 | 122 |
| dmav/hilbert-str-iom-65536 | 1521 | 20 | 232 | 285 | 27 | 122 |
| dmav/hilbert-str-wkb-1048576 | 1521 | 20 | 232 | 285 | 27 | 122 |
| dmav/hilbert-str-wkb-262144 | 1521 | 20 | 232 | 285 | 27 | 122 |
| dmav/hilbert-str-wkb-4194304 | 1521 | 20 | 232 | 285 | 27 | 122 |
| dmav/hilbert-str-wkb-65536 | 1521 | 20 | 232 | 285 | 27 | 122 |
| dmav/reference-iom-262144 | 2446 | 20 | 210 | 355 | 0 | 0 |
| dmav/reference-wkb-262144 | 2951 | 20 | 210 | 355 | 130 | 355 |
| dmav/str-iom-262144 | 1521 | 20 | 232 | 285 | 27 | 122 |
| dmav/str-wkb-262144 | 1521 | 20 | 232 | 285 | 27 | 122 |
| dmav/x-direct-iom-262144 | 1521 | 20 | 232 | 285 | 27 | 122 |
| dmav/x-direct-wkb-262144 | 1521 | 20 | 232 | 285 | 27 | 122 |
| dmav/x-prefetch-iom-262144 | 1521 | 20 | 232 | 285 | 27 | 122 |
| dmav/x-prefetch-wkb-262144 | 1521 | 20 | 232 | 285 | 27 | 122 |
| fixpoints/hilbert-str-iom-1048576 | 52871 | 100 | 22296 | 28614 | 46 | 244 |
| fixpoints/hilbert-str-iom-262144 | 52871 | 100 | 22296 | 28614 | 46 | 244 |
| fixpoints/hilbert-str-iom-4194304 | 52871 | 100 | 22296 | 28614 | 46 | 244 |
| fixpoints/hilbert-str-iom-65536 | 53405 | 100 | 22294 | 28614 | 64 | 366 |
| fixpoints/hilbert-str-wkb-1048576 | 52871 | 100 | 22296 | 28614 | 46 | 244 |
| fixpoints/hilbert-str-wkb-262144 | 52871 | 100 | 22296 | 28614 | 46 | 244 |
| fixpoints/hilbert-str-wkb-4194304 | 52871 | 100 | 22296 | 28614 | 46 | 244 |
| fixpoints/hilbert-str-wkb-65536 | 53140 | 100 | 22297 | 28614 | 55 | 305 |
| fixpoints/reference-iom-262144 | 61484 | 160 | 21084 | 36263 | 0 | 0 |
| fixpoints/reference-wkb-262144 | 112645 | 240 | 21084 | 37045 | 13052 | 37045 |
| fixpoints/str-iom-262144 | 52871 | 100 | 22296 | 28614 | 46 | 244 |
| fixpoints/str-wkb-262144 | 52871 | 100 | 22296 | 28614 | 46 | 244 |
| fixpoints/x-direct-iom-262144 | 52871 | 100 | 22296 | 28614 | 46 | 244 |
| fixpoints/x-direct-wkb-262144 | 52871 | 100 | 22296 | 28614 | 46 | 244 |
| fixpoints/x-prefetch-iom-262144 | 52871 | 100 | 22296 | 28614 | 46 | 244 |
| fixpoints/x-prefetch-wkb-262144 | 52871 | 100 | 22296 | 28614 | 46 | 244 |
| localities/hilbert-str-iom-1048576 | 858733 | 1080 | 349578 | 458679 | 1570 | 10309 |
| localities/hilbert-str-iom-262144 | 1002161 | 1240 | 349585 | 458679 | 6376 | 42761 |
| localities/hilbert-str-iom-4194304 | 824541 | 1040 | 349575 | 458679 | 417 | 2562 |
| localities/hilbert-str-iom-65536 | 1674247 | 2060 | 349584 | 458679 | 28912 | 194834 |
| localities/hilbert-str-wkb-1048576 | 832203 | 1040 | 349582 | 458679 | 679 | 4331 |
| localities/hilbert-str-wkb-262144 | 890961 | 1120 | 349574 | 458679 | 2641 | 17568 |
| localities/hilbert-str-wkb-4194304 | 817897 | 1020 | 349579 | 458679 | 188 | 1098 |
| localities/hilbert-str-wkb-65536 | 1146757 | 1420 | 349579 | 458679 | 11218 | 75457 |
| localities/reference-iom-262144 | 1546047 | 3120 | 337974 | 600334 | 0 | 0 |
| localities/reference-wkb-262144 | 2002186 | 3840 | 337974 | 597005 | 209222 | 597005 |
| localities/str-iom-262144 | 1002428 | 1240 | 349584 | 458679 | 6385 | 42822 |
| localities/str-wkb-262144 | 890961 | 1120 | 349574 | 458679 | 2641 | 17568 |
| localities/x-direct-iom-262144 | 1002428 | 1240 | 349584 | 458679 | 6385 | 42822 |
| localities/x-direct-wkb-262144 | 890961 | 1120 | 349574 | 458679 | 2641 | 17568 |
| localities/x-prefetch-iom-262144 | 1002428 | 1240 | 349584 | 458679 | 6385 | 42822 |
| localities/x-prefetch-wkb-262144 | 890961 | 1120 | 349574 | 458679 | 2641 | 17568 |
| million/reference-iom-262144 | 88970713 | 130100 | 12888890 | 75693819 | 0 | 0 |
| million/reference-wkb-262144 | 191928061 | 308760 | 12888890 | 76012130 | 26000000 | 76012130 |
| million/x-direct-iom-262144 | 68298408 | 83600 | 11032982 | 57000000 | 1613 | 9699 |
| million/x-direct-wkb-262144 | 68345242 | 83660 | 11032990 | 57000000 | 3359 | 20252 |

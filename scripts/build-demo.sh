#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 demo/generate.py
./gradlew installDist --console=plain
build/install/ibx/bin/ibx create demo/quartier.xtf demo/quartier.ibx --overwrite --model-file demo/Quartier.ili --geometry-encoding wkb --geometry-crs Quartier.Unterhalt.Gebaeude.Grundriss=EPSG:2056 --geometry-crs Quartier.Unterhalt.Gebaeude.Beschriftung=EPSG:2056 --geometry-crs Quartier.Unterhalt.Anlage.Position=EPSG:2056 --geometry-crs Quartier.Unterhalt.Spielplatz.Position=EPSG:2056 --geometry-crs Quartier.Unterhalt.Technik.Position=EPSG:2056 --geometry-crs Quartier.Unterhalt.Kontrolle.Standort=EPSG:2056 --spatial Quartier.Unterhalt.Gebaeude:Grundriss --spatial Quartier.Unterhalt.Gebaeude:Beschriftung --spatial Quartier.Unterhalt.Spielplatz:Position --spatial Quartier.Unterhalt.Technik:Position --crs EPSG:2056 --embed-models

#!/bin/sh
set -eu
app=${QGIS_APP:-/Applications/QGIS-final-4_2_2.app}
contents="$app/Contents"
export PYTHONPATH="$contents/Resources/python3.12:$contents/Resources/python3.12/lib-dynload:$contents/Resources/python3.12/site-packages:$(pwd)/qgis${PYTHONPATH:+:$PYTHONPATH}"
export QGIS_PREFIX_PATH="$contents/MacOS"
export PROJ_DATA="$contents/Resources/qgis/proj"
export QT_QPA_PLATFORM=${QT_QPA_PLATFORM:-offscreen}
export QT_PLUGIN_PATH="$contents/PlugIns"
exec "$contents/MacOS/python3.12" "$@"

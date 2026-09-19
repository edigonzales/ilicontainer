#!/usr/bin/env python3
"""Install a link into an explicitly supplied, QGIS-reported profile directory."""
import argparse
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument(
    "--profile",
    required=True,
    type=Path,
    help="QGIS Python console: QgsApplication.qgisSettingsDirPath()",
)
a = p.parse_args()
source = Path(__file__).resolve().parents[1] / "qgis/ibx_browser"
target = a.profile.expanduser().resolve() / "python/plugins/ibx_browser"
target.parent.mkdir(parents=True, exist_ok=True)
if target.is_symlink() and target.resolve() == source:
    print(f"Already installed: {target}")
elif target.exists() or target.is_symlink():
    raise SystemExit(f"Refusing to replace existing plugin: {target}")
else:
    target.symlink_to(source, target_is_directory=True)
    print(f"Installed {target} → {source}")

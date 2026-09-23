#!/usr/bin/env python3
"""Build the platform-independent QGIS plugin ZIP (pure Python, no JVM)."""
import re
import shutil
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
metadata = (root / "qgis/ibx_browser/metadata.txt").read_text()
version = re.search(r"^version=(.+)$", metadata, re.MULTILINE).group(1).strip()
stage = root / "build/qgis-package/ibx_browser"
if stage.exists():
    shutil.rmtree(stage)
shutil.copytree(
    root / "qgis/ibx_browser",
    stage,
    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
)
for file in ["LICENSE", "THIRD_PARTY.md"]:
    shutil.copy2(root / file, stage / file)
shutil.copytree(
    root / "demo", stage / "demo", ignore=shutil.ignore_patterns("__pycache__")
)
output = root / f"build/ibx-qgis-{version}.zip"
with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(stage.rglob("*")):
        if path.is_file():
            archive.write(path, path.relative_to(stage.parent))
print(output)

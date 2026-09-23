#!/usr/bin/env python3
"""Build a standard QGIS plugin ZIP with the pinned Java runtime JARs (not a JRE)."""
import shutil
import subprocess
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
subprocess.run(
    [str(root / "gradlew"), "installDist", "--console=plain"], cwd=root, check=True
)
stage = root / "build/qgis-package/ibx_browser"
if stage.exists():
    shutil.rmtree(stage)
shutil.copytree(
    root / "qgis/ibx_browser",
    stage,
    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
)
shutil.copytree(root / "build/install/ibx/lib", stage / "runtime/lib")
for file in ["LICENSE", "THIRD_PARTY.md"]:
    shutil.copy2(root / file, stage / file)
shutil.copytree(
    root / "demo", stage / "demo", ignore=shutil.ignore_patterns("__pycache__")
)
output = root / "build/ibx-qgis-0.4.2.zip"
with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(stage.rglob("*")):
        if path.is_file():
            archive.write(path, path.relative_to(stage.parent))
print(output)

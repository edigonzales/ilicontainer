#!/usr/bin/env python3
"""Run object-browser acceptance against the plugin extracted from its ZIP."""
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
archive_path = (
    Path(sys.argv[1]).resolve()
    if len(sys.argv) > 1
    else root / "build/ibx-qgis-0.4.3.zip"
)
with tempfile.TemporaryDirectory(prefix="ibx-package-") as temp:
    with zipfile.ZipFile(archive_path) as archive:
        names = set(archive.namelist())
        for path in (
            "ibx_browser/demo/Parkanlage.ili",
            "ibx_browser/demo/parkanlage.xtf",
            "ibx_browser/demo/parkanlage.ibx",
            "ibx_browser/demo/Quartier.ili",
            "ibx_browser/demo/quartier.xtf",
            "ibx_browser/demo/quartier.ibx",
        ):
            assert path in names, f"Missing packaged demo asset: {path}"
        archive.extractall(temp)
    for test in ("test_presentation.py", "test_object_tree.py", "test_ui.py"):
        code = """
import sys, runpy
from pathlib import Path
package, tests, test = sys.argv[1:]
sys.path.insert(0, package)
sys.path.insert(1, tests)
import ibx_browser.object_tree
assert Path(ibx_browser.object_tree.__file__).is_relative_to(Path(package))
sys.argv = [test, '-v']
try:
    runpy.run_path(str(Path(tests) / test), run_name='__main__')
except SystemExit as e:
    if e.code:
        raise
from ibx_browser.client import manager
if manager.process is not None:
    assert str(Path(package) / 'ibx_browser/runtime/lib') in ' '.join(manager.process.arguments())
print('Packaged plugin verified:', test)
"""
        subprocess.run(
            [
                str(root / "scripts/qgis-python.sh"),
                "-c",
                code,
                temp,
                str(root / "qgis/tests"),
                test,
            ],
            cwd=root,
            check=True,
        )
print("Package acceptance passed:", archive_path)

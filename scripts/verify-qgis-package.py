#!/usr/bin/env python3
"""Run object-browser acceptance against the plugin extracted from its ZIP."""
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
metadata = (root / "qgis/ibx_browser/metadata.txt").read_text()
version = re.search(r"^version=(.+)$", metadata, re.MULTILINE).group(1).strip()
archive_path = (
    Path(sys.argv[1]).resolve()
    if len(sys.argv) > 1
    else root / f"build/ibx-qgis-{version}.zip"
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
            "ibx_browser/ibx/cbor.py",
            "ibx_browser/ibx/container.py",
            "ibx_browser/ibx/navigation.py",
        ):
            assert path in names, f"Missing packaged asset: {path}"
        for name in names:
            assert not name.endswith(".jar"), f"Java library packaged: {name}"
            assert "runtime/lib" not in name, f"Bridge runtime packaged: {name}"
        archive.extractall(temp)
    for test in ("test_reader.py", "test_presentation.py", "test_object_tree.py", "test_ui.py"):
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
assert manager.process is None, 'packaged plugin must not spawn a helper process'
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

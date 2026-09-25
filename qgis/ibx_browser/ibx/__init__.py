"""Pure-Python reader for IBX container format 5.

This package implements the read side of the container format documented in
``docs/FORMAT.md``.  It is deliberately free of QGIS and Java dependencies so it
can be tested with a plain CPython interpreter and shipped inside a QGIS plugin
without any binary runtime.

``docs/FORMAT.md`` stays the reference; the Java implementation in
``src/main/java/ch/interlis/ibx`` remains the writer and the export path.
"""

from .container import IbxError

__all__ = ["IbxError"]

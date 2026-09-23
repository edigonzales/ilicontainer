"""ctypes binding to the Zstandard library that QGIS already ships.

Format 4 stores chunk payloads compressed with ``zstd``, ``deflate`` or
``none``.  Zstandard has no built-in Python support before 3.14 and pure Python
cannot decompress it at interactive speed, so the plugin binds the native
library that QGIS itself links (GDAL and Qt depend on it).  Nothing is bundled.

Discovery order:

1. an explicit path passed by the plugin settings,
2. ``IBX_ZSTD_LIB`` / ``IBX_ZSTD_DIR`` environment variables,
3. the QGIS application directories supplied by the caller,
4. the platform library search path.

If no library is found, ``zstd`` chunks report a clear error while ``deflate``
and ``none`` containers keep working.
"""

import ctypes
import ctypes.util
import os
import platform
import sys
import threading


class ZstdUnavailable(RuntimeError):
    """Raised when no usable Zstandard library can be found."""


_LOCK = threading.Lock()
_LIBRARY = None
_LIBRARY_PATH = ""
_LOAD_ERROR = ""
_FAILED_DIRS = set()


def _names():
    system = platform.system()
    if system == "Darwin":
        return ("libzstd.1.dylib", "libzstd.dylib")
    if system == "Windows":
        return ("zstd.dll", "libzstd.dll")
    return ("libzstd.so.1", "libzstd.so")


def _directories(extra_dirs):
    directories = []

    def add(path):
        if path and path not in directories:
            directories.append(path)

    for path in extra_dirs:
        add(path)
    add(os.environ.get("IBX_ZSTD_DIR"))
    add(os.path.dirname(os.environ.get("IBX_ZSTD_LIB", "")))
    executable = os.path.dirname(os.path.abspath(sys.executable)) if sys.executable else ""
    if executable:
        add(executable)
        if sys.platform == "darwin":
            # QGIS.app keeps its frameworks next to MacOS/
            add(os.path.join(os.path.dirname(executable), "Frameworks"))
        else:
            add(os.path.join(executable, "bin"))
            add(os.path.join(executable, "lib"))
            add(os.path.join(executable, "lib64"))
    return directories


def _open(path):
    if sys.platform == "win32" and path:
        directory = os.path.dirname(path)
        if directory and hasattr(os, "add_dll_directory"):
            try:
                os.add_dll_directory(directory)
            except OSError:
                pass
    library = ctypes.CDLL(path)
    library.ZSTD_decompress.restype = ctypes.c_size_t
    library.ZSTD_decompress.argtypes = [
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.c_void_p,
        ctypes.c_size_t,
    ]
    library.ZSTD_isError.restype = ctypes.c_uint
    library.ZSTD_isError.argtypes = [ctypes.c_size_t]
    library.ZSTD_versionNumber.restype = ctypes.c_uint
    library.ZSTD_versionNumber.argtypes = []
    return library


def load(extra_dirs=(), explicit=""):
    """Return the shared library, loading it on first use.

    ``extra_dirs`` should contain the QGIS application directories when the
    caller knows them; the function itself never imports QGIS.
    """

    global _LIBRARY, _LIBRARY_PATH, _LOAD_ERROR
    with _LOCK:
        if _LIBRARY is not None:
            return _LIBRARY
        explicit = explicit or os.environ.get("IBX_ZSTD_LIB", "")
        attempt = tuple(extra_dirs)
        if not explicit and attempt in _FAILED_DIRS:
            raise ZstdUnavailable(_message())
        errors = []
        candidates = []
        if explicit:
            candidates.append(explicit)
        else:
            for directory in _directories(extra_dirs):
                for name in _names():
                    candidates.append(os.path.join(directory, name))
            found = ctypes.util.find_library("zstd")
            if found:
                candidates.append(found)
            candidates.extend(_names())
        seen = set()
        for candidate in candidates:
            if candidate in seen:
                continue
            seen.add(candidate)
            try:
                library = _open(candidate)
            except (OSError, AttributeError) as error:
                errors.append("%s: %s" % (candidate, error))
                continue
            _LIBRARY = library
            _LIBRARY_PATH = candidate
            _LOAD_ERROR = ""
            return library
        _LOAD_ERROR = "; ".join(errors[-3:]) or "no candidate path"
        if not explicit:
            _FAILED_DIRS.add(attempt)
        raise ZstdUnavailable(_message())


def _message():
    return (
        "Zstandard-Bibliothek nicht gefunden. IBX benötigt libzstd zum Lesen "
        "zstd-komprimierter Dateien; unter IBX → Einstellungen kann der Pfad "
        "gesetzt werden. (%s)" % _LOAD_ERROR
    )


def reset():
    """Forget a loaded library; used by settings changes and tests."""

    global _LIBRARY, _LIBRARY_PATH, _LOAD_ERROR, _FAILED_DIRS
    with _LOCK:
        _LIBRARY = None
        _LIBRARY_PATH = ""
        _LOAD_ERROR = ""
        _FAILED_DIRS.clear()


def available():
    try:
        load()
    except ZstdUnavailable:
        return False
    return True


def path():
    return _LIBRARY_PATH


def version():
    library = load()
    return int(library.ZSTD_versionNumber())


def decompress(data, size):
    """Decompress exactly ``size`` bytes or raise :class:`ValueError`."""

    library = load()
    if size < 0:
        raise ValueError("Invalid Zstandard frame size")
    output = ctypes.create_string_buffer(size)
    source = ctypes.c_char_p(bytes(data))
    result = library.ZSTD_decompress(output, size, source, len(data))
    if library.ZSTD_isError(result):
        raise ValueError("Invalid Zstandard chunk")
    if result != size:
        raise ValueError("Zstandard chunk length mismatch")
    return output.raw

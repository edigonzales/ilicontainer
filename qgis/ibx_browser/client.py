"""In-process dataset and workspace manager.

This replaces the former Java bridge client.  The public surface is unchanged
so the provider, the object browser and the access monitor keep working:
``Dataset.call(op, **args)`` carries the same operations the bridge protocol
exposed, and ``manager`` owns the open datasets.

Everything runs in the QGIS Python process; there is no helper process, no
loopback port and no Java runtime.
"""

import json
import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import unquote, urlsplit

from qgis.PyQt.QtCore import (
    QEventLoop,
    QCoreApplication,
    QSettings,
    QThread,
    QTimer,
)

from .ibx import zstd
from .ibx.container import (
    READ_COUNTERS,
    LocalSource,
    Metrics,
)
from .ibx.navigation import FeatureCursor, Navigation
from .ibx.objects import page_item
from .ibx.reader import Container
from .ibx.remote import HttpRangeSource

MAX_CURSORS = 128
CURSOR_IDLE_SECONDS = 60
ZSTD_SETTING = "ibx/zstdLib"


def _qgis_directories():
    """Application directories that may contain the QGIS Zstandard library."""

    directories = []
    try:
        from qgis.core import QgsApplication

        prefix = QgsApplication.prefixPath()
    except Exception:  # pragma: no cover - QGIS always present in the plugin
        prefix = ""
    if prefix:
        directories.extend(
            [
                prefix,
                os.path.join(prefix, "bin"),
                os.path.join(prefix, "lib"),
                os.path.join(prefix, "lib64"),
                os.path.join(prefix, "Frameworks"),
                os.path.join(prefix, os.pardir, "Frameworks"),
            ]
        )
    return directories


_ZSTD_READY = False


def _prepare_zstd():
    """Bind the Zstandard library once, honouring the plugin setting."""

    global _ZSTD_READY
    if _ZSTD_READY:
        return
    try:
        explicit = str(QSettings().value(ZSTD_SETTING, "") or "")
    except Exception:
        explicit = ""
    try:
        zstd.load(_qgis_directories(), explicit=explicit)
    except zstd.ZstdUnavailable:
        # Files with deflate or uncompressed chunks stay readable; zstd
        # chunks report the recorded reason when they are reached.
        pass
    _ZSTD_READY = True


class DatasetError(RuntimeError):
    """User-visible data source error (replaces the former bridge error)."""


class _ActivityEvent:
    __slots__ = (
        "sequence",
        "op",
        "detail",
        "state",
        "started_ns",
        "started_at",
        "finished_at",
        "elapsed_ms",
        "result_count",
        "reads",
        "error",
    )

    def __init__(self, sequence, op, detail, started_ns=None):
        self.sequence = sequence
        self.op = op
        self.detail = detail
        self.state = "queued"
        self.started_ns = started_ns if started_ns is not None else time.perf_counter_ns()
        self.started_at = int(time.time() * 1000) - max(
            0, (time.perf_counter_ns() - self.started_ns) // 1_000_000
        )
        self.finished_at = 0
        self.elapsed_ms = 0
        self.result_count = None
        self.reads = {name: 0 for name in READ_COUNTERS}
        self.error = None

    def to_map(self):
        return {
            "sequence": self.sequence,
            "op": self.op,
            "detail": self.detail,
            "state": self.state,
            "startedAt": self.started_at,
            "finishedAt": self.finished_at or None,
            "elapsedMs": self.elapsed_ms,
            "resultCount": self.result_count,
            "reads": dict(self.reads),
            "error": self.error,
        }


class ActivityLog:
    """Bounded in-memory operation history, mirroring the bridge log."""

    def __init__(self, limit=200):
        self.limit = limit
        self.events = []
        self.totals = {name: 0 for name in READ_COUNTERS}
        self.next_sequence = 1
        self.lock = threading.Lock()

    def begin(self, op, detail):
        with self.lock:
            event = _ActivityEvent(self.next_sequence, op, detail)
            self.next_sequence += 1
            self.events.append(event)
            self._trim()
            return event

    def start(self, event):
        with self.lock:
            event.state = "running"

    def finish(self, event, before, after, result, failure, safe_error):
        with self.lock:
            event.reads = {
                name: max(0, after.get(name, 0) - before.get(name, 0))
                for name in READ_COUNTERS
            }
            event.finished_at = int(time.time() * 1000)
            event.elapsed_ms = max(
                0, (time.perf_counter_ns() - event.started_ns) // 1_000_000
            )
            if failure is None:
                event.state = "success"
                event.result_count = _result_count(result)
            else:
                message = str(failure) if str(failure) else type(failure).__name__
                event.state = "cancelled" if message.lower() == "cancelled" else "failed"
                event.error = safe_error
            for name in READ_COUNTERS:
                self.totals[name] = self.totals.get(name, 0) + event.reads[name]

    def completed(self, op, detail, started_ns, after, result):
        with self.lock:
            event = _ActivityEvent(self.next_sequence, op, detail, started_ns)
            self.next_sequence += 1
            self.events.append(event)
            self._trim()
        self.finish(event, {name: 0 for name in READ_COUNTERS}, after, result, None, None)

    def snapshot(self):
        with self.lock:
            active = sum(
                1
                for event in self.events
                if event.state in ("running", "queued")
            )
            return {
                "events": [event.to_map() for event in self.events],
                "totals": dict(self.totals),
                "active": active,
                "nextSequence": self.next_sequence,
            }

    def _trim(self):
        while len(self.events) > self.limit:
            self.events.pop(0)


def _result_count(result):
    if not isinstance(result, dict):
        return None
    items = result.get("items")
    if isinstance(items, list):
        return len(items)
    count = result.get("count")
    return int(count) if isinstance(count, (int, float)) else None


def source_label(source):
    """Short source name for diagnostics and the activity log."""

    source = str(source or "")
    try:
        if source.startswith(("http://", "https://")):
            parsed = urlsplit(source)
            name = Path(unquote(parsed.path)).name
            return (parsed.hostname or "") + (" / " + name if name else "")
        return Path(source).name or "IBX-Datei"
    except (OSError, ValueError):
        return "IBX-Datei"


def _activity_detail(op, args):
    if op == "query":
        className = args.get("className") or ""
        geometry = args.get("geometry")
        return className + (" · " + geometry if geometry else "")
    if op == "object":
        if "fid" in args:
            return "FID %s" % args["fid"]
        return "Objekt-ID"
    if op == "related":
        return "FID %s" % args.get("fid")
    if op == "next":
        return "Weitere Ergebnisse"
    if op == "catalog":
        return "Klassen und Geometriesichten"
    if op == "baskets":
        return "Baskets"
    return ""


class _Canceller:
    """Cancel handle handed to background tasks; mirrors ``Rpc.call``."""

    def __init__(self, target):
        self.target = target

    def call(self, op, **args):
        if op != "cancel":
            raise DatasetError("Unsupported operation")
        return self.target.call("cancel", **args)


class QueryCursor:
    """One open query with its page projection options."""

    __slots__ = ("cursor", "geometry", "fields", "no_geometry", "accessed")

    def __init__(self, cursor, geometry=None, fields=None, no_geometry=False):
        self.cursor = cursor
        self.geometry = geometry
        self.fields = set(fields) if fields is not None else None
        self.no_geometry = bool(no_geometry)
        self.accessed = time.monotonic()

    def has_next(self):
        return self.cursor.has_next()

    def next(self):
        return self.cursor.next()

    def close(self):
        self.cursor.close()


class Dataset:
    """One open IBX source with catalog, cursors and activity log."""

    def __init__(self, source, options=None, request_id=None, cancelled=None):
        self.source = str(source)
        self.options = dict(options or {})
        self.closed = False
        self.lock = threading.RLock()
        self._cancelled = {}
        self._cursors = {}
        self._closed = False
        self._log = ActivityLog()
        started = time.perf_counter_ns()
        self._metrics = Metrics()
        try:
            reader_source = self._open_source()
            self._container = Container(reader_source, self._metrics)
            self._navigation = Navigation(self._container)
            self.state = self._container.state()
            if request_id and cancelled is not None and cancelled(request_id):
                raise DatasetError("Cancelled")
            self.description = self._navigation.describe()
            self.meta = self.description["metadata"]
            self.catalog = []
            self.baskets = []
            after = None
            while True:
                page = self._navigation.catalog(after=after, limit=256)
                self.catalog.extend(page["items"])
                after = page["next"]
                if not after:
                    break
            after = None
            while True:
                page = self._navigation.baskets(after=after, limit=256)
                self.baskets.extend(page["items"])
                after = page["next"]
                if not after:
                    break
        except Exception as error:
            self._close_container()
            raise DatasetError(str(error)) from error
        self.rpc = _Canceller(self)
        self._log.completed(
            "open",
            source_label(self.source),
            started,
            self._metrics.snapshot(),
            self.description,
        )

    # -- creation -----------------------------------------------------------

    def _open_source(self):
        _prepare_zstd()
        if self.source.startswith(("http://", "https://")):
            return HttpRangeSource(self.source, self.options, self._metrics)
        return LocalSource(self.source, self._metrics)

    def _close_container(self):
        container = getattr(self, "_container", None)
        if container is not None:
            try:
                container.close()
            except Exception:
                pass

    # -- plugin API ---------------------------------------------------------

    def label(self, name):
        return (
            (self.meta.get("definitions", {}).get(name, {}) or {}).get("label")
            or name.rsplit(".", 1)[-1]
        )

    def title(self, obj):
        definition = self.meta.get("definitions", {}).get(obj["className"], {})
        name = definition.get("titleAttribute")
        values = obj.get("fields", {}).get(name, []) if name else []
        title = values[0].get("value") if values else None
        if title:
            return title
        summary = [
            str(value["value"])
            for values in obj.get("fields", {}).values()
            for value in values
            if value.get("kind") == "scalar" and value.get("value") is not None
        ]
        return " · ".join([self.label(obj["className"])] + summary[:2])

    def layer(self, cls, geometry, bids):
        rows = [
            row
            for row in self.catalog
            if row["className"] == cls and (not bids or row["bid"] in bids)
        ]
        count = sum(row["count"] for row in rows)
        boxes = []
        types = set()
        for row in rows:
            descriptor = (row.get("geometries") or {}).get(geometry)
            if descriptor:
                boxes.append(descriptor["extent"])
                types.update(descriptor.get("types", ()))
        extent = (
            None
            if not boxes
            else [
                min(box["minX"] for box in boxes),
                min(box["minY"] for box in boxes),
                max(box["maxX"] for box in boxes),
                max(box["maxY"] for box in boxes),
            ]
        )
        return count, extent, types

    # -- operations ---------------------------------------------------------

    def call(self, op, **args):
        if op == "cancel":
            flag = self._cancelled.get(args.get("target"))
            if flag is not None:
                flag.set()
            return {"ok": True}
        if op == "activity":
            return self._log.snapshot()
        if op == "metrics":
            return self._metrics_snapshot()
        if op == "close":
            self.close()
            return {"ok": True}
        request_id = args.get("requestId")
        if request_id:
            self._cancelled[request_id] = threading.Event()
        event = self._log.begin(op, _activity_detail(op, args))
        try:
            with self.lock:
                before = self._metrics_snapshot()
                self._log.start(event)
                flag = self._cancelled.get(request_id)
                try:
                    result = self._operation(op, args, flag)
                except Exception as error:
                    self._log.finish(
                        event, before, self._metrics_snapshot(), None, error,
                        self._safe_error(error),
                    )
                    raise
                self._log.finish(
                    event, before, self._metrics_snapshot(), result, None, None
                )
                return result
        finally:
            if request_id:
                self._cancelled.pop(request_id, None)

    def _operation(self, op, args, flag):
        if op == "describe":
            return self._navigation.describe()
        if op == "baskets":
            return self._navigation.baskets(
                after=args.get("after"), limit=int(args.get("limit", 256))
            )
        if op == "catalog":
            return self._navigation.catalog(
                after=args.get("after"), limit=int(args.get("limit", 256))
            )
        if op == "object":
            if "fid" in args:
                return self._navigation.object(int(args["fid"]))
            tid = args.get("tid")
            return self._navigation.resolve(
                "" if tid is None else str(tid), args.get("bid")
            )
        if op == "related":
            return self._navigation.related(
                int(args["fid"]), args.get("after"), int(args.get("limit", 50))
            )
        if op == "query":
            return self._query(args, flag)
        if op == "next":
            return self._next(args, flag)
        if op == "closeCursor":
            cursor = self._cursors.pop(args.get("cursor"), None)
            if cursor is not None:
                cursor.close()
            return {"ok": True}
        if op == "export":
            raise DatasetError(
                "XTF-Export steht im Python-Leser nicht zur Verfügung; "
                "dafür die IBX-Kommandozeile verwenden."
            )
        raise DatasetError("Unknown protocol operation")

    # -- query cursors ------------------------------------------------------

    def _query(self, args, flag):
        self._expire_cursors()
        if len(self._cursors) >= MAX_CURSORS:
            raise DatasetError("Too many open iterators")
        className = args.get("className")
        geometry = args.get("geometry")
        bids = args.get("bids") or ()
        if "fids" in args:
            locations = []
            for fid in sorted(set(int(fid) for fid in args["fids"])):
                location = self._container.get_fid(fid)
                if location is not None:
                    locations.append(location)
            cursor = FeatureCursor(
                self._container,
                self._navigation,
                locations,
                className,
                set(bids),
            )
        else:
            box = args.get("bbox")
            cursor = self._navigation.query(className, geometry, box, bids)
        cursor_id = str(uuid.uuid4())
        self._cursors[cursor_id] = QueryCursor(
            cursor,
            geometry=geometry,
            fields=args.get("fields"),
            no_geometry=bool(args.get("noGeometry")),
        )
        return self._page(cursor_id, int(args.get("limit", 256)), flag)

    def _next(self, args, flag):
        return self._page(
            args.get("cursor"), int(args.get("limit", 256)), flag
        )

    def _page(self, cursor_id, limit, flag):
        if limit < 1 or limit > 256:
            raise DatasetError("Page size must be 1..256")
        query = self._cursors.get(cursor_id)
        if query is None:
            raise DatasetError("Iterator expired; repeat query")
        items = []
        try:
            while len(items) < limit and query.has_next():
                if flag is not None and flag.is_set():
                    raise DatasetError("Cancelled")
                obj = query.next()
                items.append(
                    page_item(
                        obj,
                        obj["fid"],
                        obj["bid"],
                        geometry=query.geometry,
                        fields=query.fields,
                        no_geometry=query.no_geometry,
                    )
                )
            more = query.has_next()
            if not more:
                query.close()
                self._cursors.pop(cursor_id, None)
            query.accessed = time.monotonic()
        except Exception:
            query.close()
            self._cursors.pop(cursor_id, None)
            raise
        return {"items": items, "cursor": cursor_id if more else None}

    def _expire_cursors(self):
        now = time.monotonic()
        for cursor_id, query in list(self._cursors.items()):
            if now - query.accessed > CURSOR_IDLE_SECONDS:
                query.close()
                self._cursors.pop(cursor_id, None)

    # -- lifecycle ----------------------------------------------------------

    def _metrics_snapshot(self):
        return self._metrics.snapshot()

    def _safe_error(self, error):
        message = str(error) if str(error) else type(error).__name__
        message = message.replace(self.source, source_label(self.source))
        return message[:397] + "…" if len(message) > 400 else message

    def close(self):
        with self.lock:
            if self._closed:
                return
            self._closed = True
            for query in self._cursors.values():
                query.close()
            self._cursors.clear()
            self._close_container()


class _WorkspaceCanceller:
    """Cancel handle for dataset creation tasks."""

    def __init__(self, manager):
        self.manager = manager

    def call(self, op, **args):
        if op != "cancel":
            raise DatasetError("Unsupported operation")
        target = args.get("target")
        if target:
            self.manager.cancelled.add(target)
        return {"ok": True}


class Manager:
    """Owns open datasets; replaces the former bridge process manager."""

    def __init__(self):
        self.datasets = {}
        self.lock = threading.RLock()
        self.cancelled = set()
        self.process = None  # kept so callers can assert that no helper runs
        self._canceller = _WorkspaceCanceller(self)

    @property
    def rpc(self):
        return self._canceller

    def start(self):
        """Compatibility: there is no helper process to start."""

    def dataset(self, source, options=None, request_id=None, refresh=False):
        key = (str(source), json.dumps(options or {}, sort_keys=True))
        with self.lock:
            if refresh or key not in self.datasets:
                dataset = Dataset(
                    source,
                    options,
                    request_id=request_id,
                    cancelled=self.cancelled.__contains__,
                )
                self.datasets[key] = dataset
            return self.datasets[key]

    def for_provider(self, source, options=None):
        key = (str(source), json.dumps(options or {}, sort_keys=True))
        with self.lock:
            if key in self.datasets:
                return self.datasets[key]
        if QThread.currentThread() != QCoreApplication.instance().thread():
            return self.dataset(source, options)
        # Project restoration may construct providers on the GUI thread. Keep
        # the event loop alive while source discovery runs in a worker.
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(self.dataset, source, options)
            loop = QEventLoop()
            timer = QTimer()
            timer.setInterval(20)
            timer.timeout.connect(lambda: loop.quit() if future.done() else None)
            timer.start()
            if not future.done():
                loop.exec()
            timer.stop()
            return future.result()

    def close(self):
        with self.lock:
            for dataset in self.datasets.values():
                dataset.close()
            self.datasets.clear()
            self.cancelled.clear()


manager = Manager()

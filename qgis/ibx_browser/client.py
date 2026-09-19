"""Plain-data RPC clients are safe in renderer/worker threads. QProcess stays on GUI thread."""

import json
import os
from pathlib import Path
import shutil
import threading
import urllib.request
import urllib.error
import uuid
from qgis.PyQt.QtCore import (
    QProcess,
    QSettings,
    QEventLoop,
    QTimer,
    QThread,
    QCoreApplication,
)
from concurrent.futures import ThreadPoolExecutor


class BridgeError(RuntimeError):
    pass


class Rpc:
    def __init__(self, port, token):
        self.url = f"http://127.0.0.1:{port}/v1"
        self.token = token

    def call(self, op, **args):
        body = json.dumps(dict(op=op, **args)).encode()
        request = urllib.request.Request(
            self.url,
            data=body,
            headers={"Content-Type": "application/json", "X-IBX-Token": self.token},
        )
        try:
            # Never send the private session token to an HTTP proxy.
            with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(
                request, timeout=20
            ) as response:
                return json.load(response)
        except urllib.error.HTTPError as e:
            try:
                message = json.load(e).get("error", str(e))
            except (ValueError, OSError):
                message = str(e)
            raise BridgeError(message) from e
        except (OSError, ValueError) as e:
            raise BridgeError(f"IBX-Hilfsprozess nicht erreichbar: {e}") from e


class Dataset:
    def __init__(self, rpc, source, options=None, request_id=None):
        self.rpc, self.source, self.options = rpc, source, options or {}
        opened = rpc.call(
            "open",
            source=source,
            requestId=request_id or str(uuid.uuid4()),
            **self.options,
        )
        self.session, self.state = opened["session"], opened["state"]
        self.description = opened["description"]
        self.meta = self.description["metadata"]
        self.catalog = []
        self.baskets = []
        try:
            after = None
            while True:
                page = self.call("catalog", after=after)
                self.catalog.extend(page["items"])
                after = page["next"]
                if not after:
                    break
            after = None
            while True:
                page = self.call("baskets", after=after)
                self.baskets.extend(page["items"])
                after = page["next"]
                if not after:
                    break
        except Exception:
            self.call("close")
            raise

    def call(self, op, **args):
        return self.rpc.call(op, session=self.session, **args)

    def label(self, name):
        return (
            self.meta.get("definitions", {}).get(name, {}).get("label")
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
            str(v["value"])
            for vs in obj.get("fields", {}).values()
            for v in vs
            if v.get("kind") == "scalar" and v.get("value") is not None
        ]
        return " · ".join([self.label(obj["className"])] + summary[:2])

    def layer(self, cls, geometry, bids):
        rows = [
            r
            for r in self.catalog
            if r["className"] == cls and (not bids or r["bid"] in bids)
        ]
        count = sum(r["count"] for r in rows)
        boxes, types = [], set()
        for row in rows:
            g = row.get("geometries", {}).get(geometry)
            if g:
                boxes.append(g["extent"])
                types.update(g["types"])
        extent = (
            None
            if not boxes
            else [
                min(b["minX"] for b in boxes),
                min(b["minY"] for b in boxes),
                max(b["maxX"] for b in boxes),
                max(b["maxY"] for b in boxes),
            ]
        )
        return count, extent, types


class BridgeManager:
    def __init__(self):
        self.process = None
        self.rpc = None
        self.datasets = {}
        self.lock = threading.RLock()

    def start(self):
        if (
            self.process
            and self.process.state() == QProcess.ProcessState.Running
            and self.rpc
        ):
            return
        self.datasets.clear()
        settings = QSettings()
        java = settings.value("ibx/java", "") or os.environ.get("JAVA_HOME", "")
        if java and Path(java).is_dir():
            java = str(Path(java) / "bin/java")
        if not java:
            candidates = [
                Path.home() / ".sdkman/candidates/java/21.0.10-tem/bin/java",
                Path.home() / ".sdkman/candidates/java/current/bin/java",
            ]
            java = next(
                (str(p) for p in candidates if p.exists()), shutil.which("java") or ""
            )
        root = Path(__file__).resolve().parents[2]
        libs = Path(
            settings.value("ibx/bridgeLib", "")
            or (Path(__file__).parent / "runtime/lib")
        )
        if not libs.is_dir():
            libs = root / "build/install/ibx/lib"
        if not java or not libs.is_dir():
            raise BridgeError(
                "Java 21 und IBX-Bridge fehlen. Unter IBX → Einstellungen konfigurieren oder das Demo-Paket installieren."
            )
        self.process = QProcess()
        self.process.setProgram(java)
        self.process.setArguments(
            ["-Xmx256m", "-cp", str(libs / "*"), "ch.interlis.ibx.bridge.BridgeMain"]
        )
        loop = QEventLoop()
        self.process.readyReadStandardOutput.connect(loop.quit)
        self.process.errorOccurred.connect(loop.quit)
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        timer.start(8000)
        self.process.start()
        loop.exec()
        timer.stop()
        raw = bytes(self.process.readAllStandardOutput()).decode()
        try:
            hello = json.loads(raw.splitlines()[0])
            if hello["protocol"] != 1:
                raise ValueError("Protocol mismatch")
            self.rpc = Rpc(hello["port"], hello["token"])
        except (ValueError, KeyError, IndexError) as e:
            error = bytes(self.process.readAllStandardError()).decode()
            self.process.kill()
            raise BridgeError(
                "Java-Bridge konnte nicht starten. Java 21 prüfen.\n" + error
            ) from e
        finally:
            self.process.readyReadStandardOutput.disconnect(loop.quit)
            self.process.errorOccurred.disconnect(loop.quit)

    def dataset(self, source, options=None, request_id=None, refresh=False):
        key = (source, json.dumps(options or {}, sort_keys=True))
        with self.lock:
            if refresh or key not in self.datasets:
                if not self.rpc:
                    raise BridgeError("IBX-Bridge ist noch nicht gestartet.")
                self.datasets[key] = Dataset(self.rpc, source, options, request_id)
            return self.datasets[key]

    def for_provider(self, source, options=None):
        key = (source, json.dumps(options or {}, sort_keys=True))
        if key in self.datasets:
            return self.datasets[key]
        if QThread.currentThread() != QCoreApplication.instance().thread():
            return self.dataset(source, options)
        # Project restoration may construct providers on the GUI thread. Keep the
        # event loop alive while plain-data source discovery runs in a worker.
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
        self.datasets.clear()
        if self.process:
            self.process.closeWriteChannel()
            # Asynchronous exit; no GUI waitForFinished.
            process = self.process
            QTimer.singleShot(
                2500,
                lambda: (
                    process.kill()
                    if process.state() != QProcess.ProcessState.NotRunning
                    else None
                ),
            )
        self.rpc = None


manager = BridgeManager()

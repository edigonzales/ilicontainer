from pathlib import Path
from qgis.core import (
    QgsApplication,
    QgsProviderRegistry,
    QgsProject,
    QgsFeatureRequest,
    QgsRectangle,
    QgsCoordinateTransform,
    Qgis,
)
from qgis.gui import QgsMapToolIdentify
from qgis.PyQt.QtCore import Qt, QSettings, QTimer
from qgis.PyQt.QtGui import QAction
from qgis.PyQt.QtWidgets import (
    QInputDialog,
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QLabel,
)
from .provider import Metadata
from .client import manager
from .browser import ObjectBrowser
from .layers import Layers
from .open_dialog import OpenDialog
from .tasks import submit
from .activity import AccessMonitor, source_label

DEMOS = (
    ("Parkanlage", "parkanlage.ibx"),
    ("Quartier und Unterhalt", "quartier.ibx"),
)


class Identify(QgsMapToolIdentify):
    def __init__(self, iface, browser):
        super().__init__(iface.mapCanvas())
        self.iface, self.browser = iface, browser
        self.generation = 0
        self.task = None

    def canvasReleaseEvent(self, event):
        self.generation += 1
        generation = self.generation
        if self.task:
            self.task.cancel()
        canvas = self.iface.mapCanvas()
        point = event.mapPoint()
        radius = canvas.mapUnitsPerPixel() * 5
        box = QgsRectangle(
            point.x() - radius,
            point.y() - radius,
            point.x() + radius,
            point.y() + radius,
        )
        snapshots = []
        for layer in canvas.layers():
            if layer.providerType() != "ibx":
                continue
            transform = QgsCoordinateTransform(
                canvas.mapSettings().destinationCrs(),
                layer.crs(),
                QgsProject.instance(),
            )
            request = (
                QgsFeatureRequest()
                .setFilterRect(transform.transformBoundingBox(box))
                .setFlags(Qgis.FeatureRequestFlag.ExactIntersect)
            )
            snapshots.append(
                (
                    layer.name(),
                    layer.dataProvider().dataset,
                    layer.dataProvider().featureSource(),
                    request,
                )
            )

        def query(_):
            hits = []
            for name, dataset, source, request in snapshots:
                iterator = source.getFeatures(request)
                try:
                    for feature in iterator:
                        hits.append((name, dataset, feature.id()))
                finally:
                    iterator.close()
            return hits

        def ready(hits):
            if generation != self.generation:
                return
            if not hits:
                self.iface.messageBar().pushInfo(
                    "IBX", "An dieser Stelle kein IBX-Objekt gefunden."
                )
                return
            hit = hits[0]
            if len(hits) > 1:
                names = [
                    f"{name} · Treffer {i+1}" for i, (name, _, __) in enumerate(hits)
                ]
                selected, ok = QInputDialog.getItem(
                    self.iface.mainWindow(),
                    "Objekt auswählen",
                    "Mehrere Objekte an dieser Stelle:",
                    names,
                    0,
                    False,
                )
                if not ok:
                    return
                hit = hits[names.index(selected)]
            self.browser.open(hit[1], fid=hit[2])

        self.task = submit(
            "IBX-Objekt identifizieren",
            query,
            ready,
            lambda e: self.iface.messageBar().pushWarning("IBX", e),
        )


class IbxPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.actions = []
        self.dialogs = []

    def initGui(self):
        # Register before project restoration. Keep provider metadata alive for the QGIS session.
        if "ibx" not in QgsProviderRegistry.instance().providerList():
            self.metadata = Metadata()
            QgsProviderRegistry.instance().registerProvider(self.metadata)
        try:
            manager.start()
        except Exception as e:
            self.iface.messageBar().pushWarning("IBX", str(e))
        self.layers = Layers(self.iface)
        self.access_monitor = AccessMonitor(self.iface.mainWindow())
        self.iface.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.access_monitor)
        self.access_monitor.hide()
        self.browser = ObjectBrowser(self.iface, self.layers)
        self.iface.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.browser)
        self.browser.hide()
        self.identify = Identify(self.iface, self.browser)
        for label, callback in [
            ("IBX öffnen …", self.open),
            (
                "IBX-Objekt erkunden",
                lambda: self.iface.mapCanvas().setMapTool(self.identify),
            ),
            ("Ausgewähltes Objekt öffnen", self.selected),
            ("Zugriffsdiagnose", self.metrics),
            ("Demo öffnen", self.demo),
            ("Einstellungen", self.settings),
        ]:
            action = QAction(label, self.iface.mainWindow())
            action.triggered.connect(callback)
            self.iface.addPluginToMenu("IBX", action)
            self.actions.append(action)
        self.actions[0].setIcon(QgsApplication.getThemeIcon("/mActionAddOgrLayer.svg"))
        self.actions[1].setIcon(QgsApplication.getThemeIcon("/mActionIdentify.svg"))
        self.iface.addToolBarIcon(self.actions[0])
        self.iface.addToolBarIcon(self.actions[1])

    def open(self):
        dialog = OpenDialog(self.iface, self.layers)
        self.dialogs.append(dialog)
        dialog.show()

    def demo(self):
        labels = [label for label, _ in DEMOS]
        label, ok = QInputDialog.getItem(
            self.iface.mainWindow(),
            "Demo öffnen",
            "Demo auswählen:",
            labels,
            0,
            False,
        )
        if not ok:
            return
        filename = dict(DEMOS)[label]
        candidates = (
            Path(__file__).parent / "demo" / filename,
            Path(__file__).resolve().parents[2] / "demo" / filename,
        )
        path = next(
            (candidate for candidate in candidates if candidate.is_file()), None
        )
        if path is None:
            self.iface.messageBar().pushWarning(
                "IBX", f"Die Demo-Datei {filename} wurde nicht gefunden."
            )
            return
        dialog = OpenDialog(self.iface, self.layers)
        self.dialogs.append(dialog)
        dialog.source.setText(str(path))
        dialog.show()
        dialog.load()

    def selected(self):
        layer = self.iface.activeLayer()
        if not layer or layer.providerType() != "ibx":
            self.iface.messageBar().pushInfo(
                "IBX", "Bitte einen IBX-Layer und ein Objekt auswählen."
            )
            return
        ids = layer.selectedFeatureIds()
        if not ids:
            self.iface.messageBar().pushInfo(
                "IBX", "Bitte zuerst ein Objekt auswählen."
            )
            return
        self.browser.open(layer.dataProvider().dataset, fid=ids[0])

    def metrics(self):
        self.access_monitor.show_message("IBX-Datenquelle wird ermittelt …")
        QTimer.singleShot(0, self._open_access_monitor)

    def _open_access_monitor(self):
        dataset = self.browser.dataset
        if dataset is not None:
            self.access_monitor.open_dataset(dataset)
            return

        active = self.iface.activeLayer()
        if active is not None and active.providerType() == "ibx":
            self.access_monitor.open_dataset(active.dataProvider().dataset)
            return

        available = []
        seen = set()
        for layer in QgsProject.instance().mapLayers().values():
            if layer.providerType() != "ibx":
                continue
            candidate = layer.dataProvider().dataset
            key = id(candidate)
            if key in seen:
                continue
            seen.add(key)
            available.append((candidate, layer.name()))

        if not available:
            self.access_monitor.show_message(
                "Es ist keine IBX-Datenquelle geladen. Öffne zuerst eine IBX-Datei "
                "oder füge einen IBX-Layer zum Projekt hinzu."
            )
            return
        if len(available) == 1:
            self.access_monitor.open_dataset(available[0][0])
            return

        counts = {}
        for candidate, _ in available:
            label = source_label(candidate.source)
            counts[label] = counts.get(label, 0) + 1
        choices = []
        for index, (candidate, layer_name) in enumerate(available, 1):
            label = source_label(candidate.source)
            if counts[label] > 1:
                label = f"{label} · {layer_name}"
            label = label or f"IBX-Quelle {index}"
            if label in choices:
                label = f"{label} · Quelle {index}"
            choices.append(label)
        selected, ok = QInputDialog.getItem(
            self.iface.mainWindow(),
            "Zugriffsdiagnose",
            "Für welche IBX-Datenquelle soll der Verlauf angezeigt werden?",
            choices,
            0,
            False,
        )
        if not ok:
            self.access_monitor.show_message(
                "Quellauswahl abgebrochen. Wähle einen IBX-Layer und öffne die Diagnose erneut."
            )
            return
        self.access_monitor.open_dataset(available[choices.index(selected)][0])

    def settings(self):
        settings = QSettings()
        dialog = QDialog(self.iface.mainWindow())
        dialog.setWindowTitle("IBX-Einstellungen")
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        library = QLineEdit(settings.value("ibx/zstdLib", ""))
        form.addRow("Zstandard-Bibliothek", library)
        layout.addLayout(form)
        layout.addWidget(
            QLabel(
                "Leer lassen für automatische Erkennung. Die Bibliothek ist nur "
                "für zstd-komprimierte Dateien nötig; QGIS liefert sie normalerweise "
                "mit. Änderungen gelten nach QGIS-Neustart."
            )
        )
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        if dialog.exec():
            settings.setValue("ibx/zstdLib", library.text())

    def unload(self):
        self.identify.generation += 1
        if self.identify.task:
            self.identify.task.cancel()
        self.browser.abort()
        self.access_monitor.shutdown()
        self.iface.removeDockWidget(self.browser)
        self.browser.deleteLater()
        self.iface.removeDockWidget(self.access_monitor)
        self.access_monitor.deleteLater()
        if self.iface.mapCanvas().mapTool() == self.identify:
            self.iface.mapCanvas().unsetMapTool(self.identify)
        for action in self.actions:
            self.iface.removePluginMenu("IBX", action)
            self.iface.removeToolBarIcon(action)
        for dialog in self.dialogs:
            dialog.close()
        if not any(
            l.providerType() == "ibx"
            for l in QgsProject.instance().mapLayers().values()
        ):
            manager.close()

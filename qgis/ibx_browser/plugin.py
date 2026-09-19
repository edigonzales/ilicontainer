import json
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
from qgis.PyQt.QtCore import Qt, QSettings
from qgis.PyQt.QtGui import QAction
from qgis.PyQt.QtWidgets import (
    QInputDialog,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QLabel,
    QPlainTextEdit,
)
from .provider import Metadata
from .client import manager
from .browser import ObjectBrowser
from .layers import Layers
from .open_dialog import OpenDialog
from .tasks import submit


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
        point = canvas.getCoordinateTransform().toMapCoordinates(event.x(), event.y())
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
        path = Path(__file__).parent / "demo/quartier.ibx"
        if not path.exists():
            path = Path(__file__).resolve().parents[2] / "demo/quartier.ibx"
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
        d = self.browser.dataset
        if d is None:
            self.iface.messageBar().pushInfo("IBX", "Zuerst ein Objekt öffnen.")
            return

        def show(data):
            dialog = QDialog(self.iface.mainWindow())
            dialog.setWindowTitle("IBX-Zugriffsdiagnose")
            dialog.resize(580, 400)
            layout = QVBoxLayout(dialog)
            layout.addWidget(
                QLabel(
                    "Kumuliert seit dem Öffnen, inklusive Öffnungskosten. Cachetreffer sind separat ausgewiesen."
                )
            )
            text = QPlainTextEdit(json.dumps(data, indent=2))
            text.setReadOnly(True)
            layout.addWidget(text)
            self.dialogs.append(dialog)
            dialog.show()

        submit(
            "IBX-Zugriffe lesen",
            lambda _: d.call("metrics"),
            show,
            lambda e: self.iface.messageBar().pushWarning("IBX", e),
        )

    def settings(self):
        settings = QSettings()
        dialog = QDialog(self.iface.mainWindow())
        dialog.setWindowTitle("IBX-Einstellungen")
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        java = QLineEdit(settings.value("ibx/java", ""))
        libs = QLineEdit(settings.value("ibx/bridgeLib", ""))
        form.addRow("Java-21-Programm", java)
        form.addRow("Bridge-Verzeichnis (lib)", libs)
        layout.addLayout(form)
        layout.addWidget(
            QLabel(
                "Leere Felder verwenden automatische Erkennung. Änderungen gelten nach QGIS-Neustart."
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
            settings.setValue("ibx/java", java.text())
            settings.setValue("ibx/bridgeLib", libs.text())

    def unload(self):
        self.identify.generation += 1
        if self.identify.task:
            self.identify.task.cancel()
        self.browser.abort()
        self.iface.removeDockWidget(self.browser)
        self.browser.deleteLater()
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

"""Offscreen GUI acceptance in the installed QGIS runtime, including real asynchronous tasks."""

import time
from pathlib import Path
import unittest
from qgis.core import *
from qgis.gui import QgsMapCanvas, QgsMessageBar
from qgis.PyQt.QtWidgets import QMainWindow
from qgis.PyQt.QtCore import Qt, QPoint
from qgis.PyQt.QtTest import QTest
from ibx_browser.client import manager
from ibx_browser.provider import Metadata
from ibx_browser.layers import Layers
from ibx_browser.browser import ObjectBrowser
from ibx_browser.open_dialog import OpenDialog
from ibx_browser.plugin import Identify

app = QgsApplication([], True)
app.initQgis()


class Iface:
    def __init__(self):
        self.window = QMainWindow()
        self.canvas = QgsMapCanvas()
        self.window.setCentralWidget(self.canvas)
        self.window.resize(1250, 800)
        self.bar = QgsMessageBar()

    def mainWindow(self):
        return self.window

    def mapCanvas(self):
        return self.canvas

    def messageBar(self):
        return self.bar

    def setActiveLayer(self, layer):
        self.layer = layer

    def showAttributeTable(self, layer):
        self.table = layer


def wait_until(condition):
    deadline = time.monotonic() + 15
    while not condition() and time.monotonic() < deadline:
        QTest.qWait(25)
    assert condition(), "GUI request did not complete"


class GuiTests(unittest.TestCase):
    def test_user_journey(self):
        iface = Iface()
        manager.start()
        dataset = manager.dataset(str(Path("demo/quartier.ibx").resolve()))
        QgsProviderRegistry.instance().registerProvider(Metadata())
        layers = Layers(iface)
        dialog = OpenDialog(iface, layers)
        dialog.ready(dataset)
        self.assertEqual(3, dialog.baskets.count())
        dialog.add_layers()
        self.assertEqual(1, len(QgsProject.instance().mapLayers()))
        layer = list(QgsProject.instance().mapLayers().values())[0]
        self.assertEqual("Grundriss", layer.dataProvider().spec["geometry"])
        iface.canvas.setLayers([layer])
        iface.canvas.setDestinationCrs(layer.crs())
        iface.canvas.setExtent(layer.extent())
        iface.canvas.refresh()
        browser = ObjectBrowser(iface, layers)
        iface.window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, browser)
        iface.window.show()
        QTest.qWait(150)
        tool = Identify(iface, browser)
        pixel = iface.canvas.getCoordinateTransform().transform(2600010, 1200007)

        class Click:
            def x(self):
                return int(pixel.x())

            def y(self):
                return int(pixel.y())

        tool.canvasReleaseEvent(Click())
        wait_until(
            lambda: browser.obj is not None
            and browser.related.text(1) != "Wird geladen …"
        )
        self.assertEqual("Haus am Park 1", browser.title.text())
        self.assertEqual(1, len(QgsProject.instance().mapLayers()))
        for i in range(browser.tree.topLevelItemCount()):
            item = browser.tree.topLevelItem(i)
            if item.text(0) == "Kontrollen":
                item.setExpanded(True)
                item.child(0).setExpanded(True)
        QTest.qWait(100)
        Path("build/qgis").mkdir(parents=True, exist_ok=True)
        iface.window.grab().save("build/qgis/object-browser.png")
        browser.open(dataset, tid="auftrag0")
        wait_until(
            lambda: browser.obj["tid"] == "auftrag0"
            and browser.related.text(1) != "Wird geladen …"
        )
        self.assertEqual(1, len(QgsProject.instance().mapLayers()))
        self.assertEqual(7, browser.related.childCount())
        browser.open(dataset, tid="anlage0")
        wait_until(lambda: browser.obj["tid"] == "anlage0")
        browser.show_map()
        self.assertEqual(2, len(QgsProject.instance().mapLayers()))
        browser.travel(-1)
        wait_until(lambda: browser.obj["tid"] == "auftrag0")
        browser.open(dataset, tid="missing")
        wait_until(lambda: "nicht enthalten" in browser.status.text())
        self.assertEqual("auftrag0", browser.obj["tid"])
        browser.show_table()
        self.assertEqual(3, len(QgsProject.instance().mapLayers()))
        dialog.show()
        QTest.qWait(100)
        dialog.grab().save("build/qgis/open-dialog.png")
        dialog.close()
        browser.abort()
        iface.window.close()
        QgsProject.instance().clear()
        manager.process.closeWriteChannel()
        manager.process.waitForFinished(3000)


if __name__ == "__main__":
    unittest.main()

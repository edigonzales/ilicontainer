"""Offscreen GUI acceptance in the installed QGIS runtime, including real asynchronous tasks."""

import time
from pathlib import Path
import unittest
from unittest.mock import patch, Mock
from qgis.core import *
from qgis.gui import QgsMapCanvas, QgsMessageBar
from qgis.PyQt.QtWidgets import QMainWindow
from qgis.PyQt.QtCore import Qt, QPoint, QSettings
from qgis.PyQt.QtTest import QTest
from ibx_browser.client import manager
from ibx_browser.provider import Metadata
from ibx_browser.layers import Layers
from ibx_browser.browser import ObjectBrowser
from ibx_browser.open_dialog import (
    OpenDialog,
    Column,
    MODEL_NAMES_SETTING,
    geometry_label,
)
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
    def test_geometry_labels(self):
        for geometry, types, expected in [
            (None, set(), "Ohne Geometrie"),
            ("g", {1, 1004}, "Punkt"),
            ("g", {2, 8, 1009, 11}, "Linie"),
            ("g", {3, 1010, 12}, "Fläche"),
            ("g", {1, 3}, "Gemischt"),
            ("g", {7}, "Gemischt"),
            ("g", {999}, "Geometrie"),
            ("g", set(), "Geometrie"),
        ]:
            with self.subTest(types=types):
                self.assertEqual(expected, geometry_label(geometry, types))

    def test_user_journey(self):
        iface = Iface()
        manager.start()
        dataset = manager.dataset(str(Path("demo/quartier.ibx").resolve()))
        QgsProviderRegistry.instance().registerProvider(Metadata())
        layers = Layers(iface)
        settings = QSettings()
        old_setting = settings.value(MODEL_NAMES_SETTING)
        self.addCleanup(
            lambda: (
                settings.remove(MODEL_NAMES_SETTING)
                if old_setting is None
                else settings.setValue(MODEL_NAMES_SETTING, old_setting)
            )
        )
        settings.remove(MODEL_NAMES_SETTING)
        dialog = OpenDialog(iface, layers)
        dialog.ready(dataset)
        self.assertEqual(3, dialog.baskets.count())
        before = dataset.call("metrics")["chunksRead"]

        def items(parent):
            for i in range(parent.childCount()):
                child = parent.child(i)
                yield child
                yield from items(child)

        entries = list(items(dialog.tree.invisibleRootItem()))
        by_model = {item.text(Column.MODEL): item for item in entries}
        cls = "Quartier.Unterhalt."
        self.assertEqual("Klasse", by_model[cls + "Auftrag"].text(Column.KIND))
        for name in ("Folgeauftrag", "Zustaendigkeit"):
            self.assertEqual("Assoziation", by_model[cls + name].text(Column.KIND))
        building = by_model[cls + "Gebaeude"]
        self.assertEqual("Mehrere Geometrien", building.text(Column.GEOMETRY))
        self.assertEqual("24", building.text(Column.COUNT))
        self.assertEqual("", building.child(0).text(Column.KIND))
        self.assertIn("nicht addiert", building.toolTip(Column.GEOMETRY))
        self.assertTrue(dialog.tree.isColumnHidden(Column.MODEL))
        dialog.model_names.setChecked(True)
        second = OpenDialog(iface, layers)
        self.assertFalse(second.tree.isColumnHidden(Column.MODEL))
        second.close()
        dialog.model_names.setChecked(False)
        dialog.search.setText(cls + "Zustaendigkeit")
        self.assertFalse(by_model[cls + "Zustaendigkeit"].isHidden())
        self.assertTrue(building.isHidden())
        dialog.search.setText(cls + "Gebaeude")
        self.assertFalse(building.isHidden())
        self.assertTrue(
            all(not building.child(i).isHidden() for i in range(building.childCount()))
        )
        dialog.search.clear()
        for i in range(dialog.baskets.count()):
            basket = dialog.baskets.item(i)
            basket.setSelected(True)
            expected = sum(
                r["count"]
                for r in dataset.catalog
                if r["className"] == cls + "Gebaeude" and r["bid"] == basket.text()
            )
            self.assertEqual(str(expected), building.text(Column.COUNT))
            if basket.text() == "leer":
                self.assertEqual("0", building.text(Column.COUNT))
            basket.setSelected(False)
        self.assertEqual("24", building.text(Column.COUNT))
        self.assertEqual(before, dataset.call("metrics")["chunksRead"])
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
        iface.canvas.setMapTool(tool)
        pixel = iface.canvas.getCoordinateTransform().transform(2600010, 1200007)
        QTest.mouseClick(
            iface.canvas.viewport(),
            Qt.MouseButton.LeftButton,
            pos=QPoint(round(pixel.x()), round(pixel.y())),
        )
        wait_until(lambda: browser.obj is not None and browser.tree.relations.complete)
        self.assertEqual("Haus am Park 1", browser.title.text())
        self.assertEqual(1, len(QgsProject.instance().mapLayers()))
        pixel = iface.canvas.getCoordinateTransform().transform(2600035, 1200035)
        QTest.mouseClick(
            iface.canvas.viewport(),
            Qt.MouseButton.LeftButton,
            pos=QPoint(round(pixel.x()), round(pixel.y())),
        )
        wait_until(lambda: iface.bar.currentItem() is not None)
        self.assertEqual(
            "An dieser Stelle kein IBX-Objekt gefunden.",
            iface.bar.currentItem().text(),
        )
        self.assertEqual("Haus am Park 1", browser.title.text())
        for i in range(browser.tree.topLevelItemCount()):
            item = browser.tree.topLevelItem(i)
            if item.text(0) == "Kontrollen":
                item.setExpanded(True)
                item.child(0).setExpanded(True)
        QTest.qWait(100)
        Path("build/qgis").mkdir(parents=True, exist_ok=True)
        iface.window.grab().save("build/qgis/object-browser.png")

        # Real Java-backed inline access: one selected target, no recursive reads.
        def top(name):
            return next(
                browser.tree.topLevelItem(i)
                for i in range(browser.tree.topLevelItemCount())
                if browser.tree.topLevelItem(i).text(0) == name
            )

        order = top("Unterhaltsauftrag")
        before_chunks = dataset.call("metrics")["chunksRead"]
        with patch.object(dataset, "call", wraps=dataset.call) as calls:
            order.setExpanded(True)
            wait_until(lambda: order.state == "loaded")
            self.assertEqual(["object"], [c.args[0] for c in calls.call_args_list])
            order.setExpanded(False)
            order.setExpanded(True)
            self.assertEqual(1, calls.call_count)
        self.assertEqual(0, browser.position)
        self.assertLessEqual(dataset.call("metrics")["chunksRead"] - before_chunks, 1)
        duty = top("Zuständigkeit · Organisation").child(0)
        with patch.object(dataset, "call", wraps=dataset.call) as calls:
            duty.setExpanded(True)
            self.assertEqual(0, calls.call_count)
            details = duty.child(0)
            self.assertEqual("Angaben zur Zuständigkeit", details.text(0))
            self.assertEqual(
                {"Funktion", "Gueltig Ab"},
                {details.child(i).text(0) for i in range(details.childCount())},
            )
            content = duty.child(1)
            content.setExpanded(True)
            wait_until(lambda: content.state == "loaded")
            self.assertEqual(["object"], [c.args[0] for c in calls.call_args_list])
        self.assertEqual(0, browser.position)
        iface.window.grab().save("build/qgis/inline-demo.png")
        browser.open(dataset, tid="auftrag0")
        wait_until(
            lambda: browser.obj["tid"] == "auftrag0" and browser.tree.relations.complete
        )
        self.assertEqual(1, len(QgsProject.instance().mapLayers()))
        self.assertEqual(7, browser.tree.relations.edge_count)
        browser.open(dataset, tid="anlage0")
        wait_until(lambda: browser.obj["tid"] == "anlage0")
        browser.show_map()
        self.assertEqual(2, len(QgsProject.instance().mapLayers()))
        browser.travel(-1)
        wait_until(lambda: browser.obj["tid"] == "auftrag0")
        browser.open(dataset, tid="missing")
        wait_until(lambda: "nicht enthalten" in browser.status.text())
        self.assertEqual("auftrag0", browser.obj["tid"])
        # Returning via a relationship is a new visit, not a hierarchy change.
        browser.open(dataset, tid="anlage0")
        wait_until(lambda: browser.obj["tid"] == "anlage0")
        browser.open(dataset, tid="auftrag0")
        wait_until(lambda: browser.obj["tid"] == "auftrag0")
        browser.open(dataset, tid="anlage0")
        wait_until(lambda: browser.obj["tid"] == "anlage0")
        browser.open(dataset, tid="auftrag0")
        wait_until(lambda: browser.obj["tid"] == "auftrag0")
        self.assertEqual(5, browser.position)
        iface.window.grab().save("build/qgis/history.png")
        self.assertIn("Besuchsverlauf", browser.breadcrumb.text())
        self.assertIn("2 frühere Besuche", browser.breadcrumb.text())
        self.assertIn("(aktuell)", browser.breadcrumb.text())
        browser.breadcrumb.linkActivated.emit("earlier")
        self.assertIn("Haus am Park 1", browser.breadcrumb.text())
        browser.breadcrumb.linkActivated.emit("visit:1")
        wait_until(lambda: browser.position == 1)
        self.assertIn("4 spätere Besuche", browser.breadcrumb.text())
        browser.travel(1)
        wait_until(lambda: browser.position == 2)
        self.assertEqual("anlage0", browser.obj["tid"])

        # Failed, missing, cancelled and stale responses must not move history.
        previous = browser.obj
        with patch("ibx_browser.browser.submit", return_value=Mock()) as submit:
            browser.travel(-1)
            self.assertEqual(2, browser.position)
            success, failure = submit.call_args.args[2:4]
            failure("Testfehler")
            self.assertEqual(2, browser.position)
            self.assertIs(previous, browser.obj)
            browser.travel(-1)
            success = submit.call_args.args[2]
            success(None)
            self.assertEqual(2, browser.position)
            browser.travel(-1)
            success, failure = submit.call_args.args[2:4]
            browser.abort()
            success(previous)
            failure("Verspäteter Fehler")
            self.assertEqual(2, browser.position)
            self.assertIn("Abgebrochen", browser.status.text())
        browser.open(dataset, tid="auftrag0")
        wait_until(lambda: browser.position == 3)
        self.assertEqual(4, len(browser.history))
        self.assertFalse(browser.forward.isEnabled())
        browser.show_table()
        self.assertEqual(3, len(QgsProject.instance().mapLayers()))
        dialog.show()
        QTest.qWait(100)
        dialog.grab().save("build/qgis/open-dialog.png")
        for item in entries:
            if item.data(Column.NAME, Qt.ItemDataRole.UserRole):
                item.setCheckState(Column.NAME, Qt.CheckState.Unchecked)
        for name in ("Auftrag", "Zustaendigkeit"):
            by_model[cls + name].setCheckState(Column.NAME, Qt.CheckState.Checked)
        dialog.add_layers()
        loaded = {
            l.dataProvider().spec["className"]: l
            for l in QgsProject.instance().mapLayers().values()
        }
        self.assertEqual(8, loaded[cls + "Auftrag"].featureCount())
        self.assertEqual(24, loaded[cls + "Zustaendigkeit"].featureCount())
        dialog.close()
        browser.abort()
        iface.window.close()
        QgsProject.instance().clear()
        manager.process.closeWriteChannel()
        manager.process.waitForFinished(3000)


if __name__ == "__main__":
    unittest.main()

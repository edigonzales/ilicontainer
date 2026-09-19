import base64
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsGeometry,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsRectangle,
    QgsEditorWidgetSetup,
)
from qgis.gui import QgsHighlight
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QInputDialog
from .provider import uri


class Layers:
    def __init__(self, iface):
        self.iface = iface
        self.highlight = None

    def ensure(self, dataset, cls, geometry=None, bids=None):
        source = uri(
            dataset.source, dataset.state, cls, geometry, bids, dataset.options
        )
        for layer in QgsProject.instance().mapLayers().values():
            if layer.providerType() == "ibx" and layer.source() == source:
                return layer
        title = dataset.label(cls)
        if geometry:
            title += " – " + dataset.label(cls + "." + geometry)
        layer = QgsVectorLayer(source, title, "ibx")
        if not layer.isValid():
            raise RuntimeError("Die IBX-Sicht konnte nicht geladen werden.")
        for i, field in enumerate(layer.fields()):
            if field.name().startswith("_ibx_"):
                layer.setEditorWidgetSetup(i, QgsEditorWidgetSetup("Hidden", {}))
            else:
                layer.setFieldAlias(i, dataset.label(cls + "." + field.name()))
                if cls + "." + field.name() not in dataset.meta["scalarTypes"]:
                    layer.setEditorWidgetSetup(i, QgsEditorWidgetSetup("JsonEdit", {}))
        title_attr = (
            dataset.meta.get("definitions", {}).get(cls, {}).get("titleAttribute")
        )
        if title_attr:
            layer.setDisplayExpression('"' + title_attr.replace('"', '""') + '"')
        QgsProject.instance().addMapLayer(layer)
        return layer

    def show_object(self, dataset, obj, geometry_name=None):
        geometries = [
            (name, v)
            for name, vs in obj["fields"].items()
            for v in vs
            if v.get("kind") == "geometry"
        ]
        if not geometries:
            return
        if geometry_name:
            geometries = [(n, v) for n, v in geometries if n == geometry_name]
        if len(geometries) > 1:
            names = [dataset.label(obj["className"] + "." + n) for n, _ in geometries]
            choice, ok = QInputDialog.getItem(
                self.iface.mainWindow(),
                "Auf Karte zeigen",
                "Welche Geometrie?",
                names,
                0,
                False,
            )
            if not ok:
                return
            name, value = geometries[names.index(choice)]
        else:
            name, value = geometries[0]
        # Reuse a filtered layer too; highlight does not modify its filter or selection.
        existing = [
            l
            for l in QgsProject.instance().mapLayers().values()
            if l.providerType() == "ibx"
            and l.dataProvider().dataset is dataset
            and l.dataProvider().spec["className"] == obj["className"]
            and l.dataProvider().spec.get("geometry") == name
        ]
        if not existing:
            self.ensure(dataset, obj["className"], name)
        self.show_geometry(dataset, value)

    def show_geometry(self, dataset, value):
        geometry = QgsGeometry()
        geometry.fromWkb(base64.b64decode(value["wkb"]))
        crs = QgsCoordinateReferenceSystem(
            dataset.meta["geometries"][value["descriptor"]]["crs"]
        )
        canvas = self.iface.mapCanvas()
        geometry.transform(
            QgsCoordinateTransform(
                crs, canvas.mapSettings().destinationCrs(), QgsProject.instance()
            )
        )
        if self.highlight:
            self.highlight.hide()
        self.highlight = QgsHighlight(canvas, geometry, None)
        self.highlight.setColor(QColor("#e67e22"))
        self.highlight.setWidth(3)
        self.highlight.show()
        box = geometry.boundingBox()
        if box.width() == 0 or box.height() == 0:
            box = QgsRectangle(
                box.xMinimum() - 15,
                box.yMinimum() - 15,
                box.xMaximum() + 15,
                box.yMaximum() + 15,
            )
        box.scale(1.4)
        canvas.setExtent(box)
        canvas.refresh()

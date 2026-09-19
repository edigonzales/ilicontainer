from pathlib import Path
from enum import IntEnum
from qgis.PyQt.QtCore import Qt, QSettings
from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QDialogButtonBox,
    QListWidget,
    QHeaderView,
    QAbstractItemView,
    QCheckBox,
)
from qgis.core import QgsProject
from .client import manager
from .tasks import submit


class Column(IntEnum):
    NAME = 0
    KIND = 1
    GEOMETRY = 2
    COUNT = 3
    MODEL = 4


COUNT_CLASS_ROLE = int(Qt.ItemDataRole.UserRole) + 1
MODEL_NAMES_SETTING = "ibx/showModelNames"


def geometry_label(geometry, types):
    if geometry is None:
        return "Ohne Geometrie"
    families = set()
    for value in types:
        base = value % 1000
        if base in (1, 4):
            families.add("Punkt")
        elif base in (2, 5, 8, 9, 11, 13):
            families.add("Linie")
        elif base in (3, 6, 10, 12, 14, 15, 16, 17):
            families.add("Fläche")
        elif base == 7:
            return "Gemischt"
        else:
            families.add("Geometrie")
    return (
        next(iter(families))
        if len(families) == 1
        else "Gemischt" if families else "Geometrie"
    )


class OpenDialog(QDialog):
    def __init__(self, iface, layers):
        super().__init__(iface.mainWindow())
        self.iface, self.layers = iface, layers
        self.setWindowTitle("IBX öffnen")
        self.resize(1000, 680)
        self.dataset = None
        self.task = None
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel("Karten und Daten direkt aus einer IBX-Datei erkunden.")
        )
        row = QHBoxLayout()
        self.source = QLineEdit()
        self.source.setPlaceholderText("Datei oder öffentliche https://…/daten.ibx")
        row.addWidget(self.source)
        browse = QPushButton("Datei …")
        browse.clicked.connect(self.browse)
        row.addWidget(browse)
        self.read = QPushButton("Inhalt anzeigen")
        self.read.clicked.connect(self.load)
        row.addWidget(self.read)
        layout.addLayout(row)
        opts = QHBoxLayout()
        self.full = QCheckBox("Vollständigen Download erlauben")
        self.immutable = QCheckBox("URL ist unveränderlich (ohne ETag)")
        self.full.setToolTip(
            "Nur bei fehlender Range-Unterstützung: vollständige lokale Momentaufnahme laden."
        )
        self.immutable.setToolTip("Nur für garantiert unveränderliche URLs verwenden.")
        opts.addWidget(self.full)
        opts.addWidget(self.immutable)
        layout.addLayout(opts)
        self.status = QLabel("Datei oder Adresse wählen.")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Name oder Modellname suchen …")
        self.search.textChanged.connect(self.filter)
        layout.addWidget(self.search)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(
            ["Name", "Modellart", "Geometrie", "Anzahl", "Modellname"]
        )
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tree.header().setStretchLastSection(False)
        for column, width in zip(Column, [310, 130, 180, 90, 350]):
            self.tree.setColumnWidth(column, width)
        self.model_names = QCheckBox("Modellnamen anzeigen")
        self.model_names.setChecked(
            QSettings().value(MODEL_NAMES_SETTING, False, type=bool)
        )
        self.tree.setColumnHidden(Column.MODEL, not self.model_names.isChecked())
        self.model_names.toggled.connect(self.toggle_model_names)
        layout.addWidget(self.model_names)
        layout.addWidget(self.tree, 1)
        layout.addWidget(QLabel("Baskets · keine Auswahl bedeutet alle"))
        self.baskets = QListWidget()
        self.baskets.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.baskets.setMaximumHeight(90)
        self.baskets.itemSelectionChanged.connect(self.update_counts)
        layout.addWidget(self.baskets)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        self.add = self.buttons.addButton(
            "Auswahl hinzufügen", QDialogButtonBox.ButtonRole.AcceptRole
        )
        self.add.setEnabled(False)
        self.buttons.rejected.connect(self.reject)
        self.add.clicked.connect(self.add_layers)
        layout.addWidget(self.buttons)

    def browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "IBX-Datei öffnen", "", "IBX (*.ibx)"
        )
        if path:
            self.source.setText(path)
            self.load()

    def load(self):
        source = self.source.text().strip()
        if not source:
            return
        if not source.startswith(("http://", "https://")):
            source = str(Path(source).expanduser().resolve())
        self.status.setText("Verzeichnis wird gelesen …")
        self.read.setEnabled(False)
        self.add.setEnabled(False)
        try:
            manager.start()
        except Exception as e:
            self.failed(str(e))
            return
        options = dict(
            allowFullDownload=self.full.isChecked(),
            immutableUrl=self.immutable.isChecked(),
        )
        self.task = submit(
            "IBX-Datei öffnen",
            lambda rid: manager.dataset(source, options, rid, refresh=True),
            self.ready,
            self.failed,
            manager.rpc,
        )

    def failed(self, message):
        self.status.setText(message)
        self.read.setEnabled(True)

    def ready(self, dataset):
        self.dataset = dataset
        self.read.setEnabled(True)
        self.tree.clear()
        self.baskets.clear()
        if dataset.meta["geometryEncoding"] != "wkb":
            self.status.setText(
                "Für QGIS bitte mit „ibx create … --geometry-encoding wkb“ neu erstellen und räumliche Indizes ergänzen."
            )
            return
        for bid in sorted({r["bid"] for r in dataset.baskets}):
            self.baskets.addItem(bid)
        classes = sorted({r["className"] for r in dataset.catalog})
        groups = {}
        first = True
        for cls in classes:
            model, topic, _ = cls.split(".", 2)
            group_key = model + "." + topic
            parent = groups.get(group_key)
            if parent is None:
                parent = self.make_item(
                    self.tree, dataset.label(group_key), model_name=group_key
                )
                parent.setExpanded(True)
                groups[group_key] = parent
            geometries = [
                key.rsplit(".", 1)[-1]
                for key in dataset.meta["geometries"]
                if key.rsplit(".", 1)[0] == cls
            ]
            geometries.sort(
                key=lambda name: (
                    "Coord" in dataset.meta["geometries"][cls + "." + name]["type"],
                    name,
                )
            )
            choices = geometries or [None]
            definition = dataset.meta.get("definitions", {}).get(cls, {})
            kind = {"class": "Klasse", "association": "Assoziation"}.get(
                definition.get("kind"), "Unbekannt"
            )
            if len(choices) > 1:
                parent = self.make_item(
                    parent, dataset.label(cls), kind, "Mehrere Geometrien", cls, cls
                )
                parent.setToolTip(
                    Column.GEOMETRY,
                    "Diese Geometriesichten zeigen dieselben Objekte. Die Anzahlen dürfen nicht addiert werden.",
                )
                parent.setExpanded(True)
            for geometry in choices:
                label = (
                    dataset.label(cls + "." + geometry)
                    if len(choices) > 1
                    else dataset.label(cls)
                )
                count, _, types = dataset.layer(cls, geometry, [])
                model_name = cls + "." + geometry if len(choices) > 1 else cls
                item = self.make_item(
                    parent,
                    label,
                    "" if len(choices) > 1 else kind,
                    geometry_label(geometry, types),
                    model_name,
                    cls,
                )
                item.setData(Column.NAME, Qt.ItemDataRole.UserRole, (cls, geometry))
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Column.NAME, Qt.CheckState.Unchecked)
                item.setToolTip(
                    0,
                    label
                    + "\n"
                    + model_name
                    + (
                        "\n" + definition["description"]
                        if definition.get("description")
                        else ""
                    ),
                )
                indexed = geometry is None or any(
                    i["className"] == cls and i["attribute"] == geometry
                    for i in dataset.description["spatial"]["indexes"].values()
                )
                if not indexed:
                    item.setDisabled(True)
                    item.setToolTip(
                        0, "Räumlicher Index fehlt. Mit ibx add-spatial-index ergänzen."
                    )
                elif first and geometry:
                    item.setCheckState(Column.NAME, Qt.CheckState.Checked)
                    first = False
        self.status.setText(
            "Objektarten auswählen. Beziehungen lassen sich später auch ohne geladene Ziellayer öffnen."
        )
        self.update_counts()
        self.add.setEnabled(True)
        self.filter(self.search.text())

    def toggle_model_names(self, visible):
        self.tree.setColumnHidden(Column.MODEL, not visible)
        QSettings().setValue(MODEL_NAMES_SETTING, visible)

    def make_item(
        self, parent, name, kind="", geometry="", model_name="", count_class=None
    ):
        item = QTreeWidgetItem(parent, [name, kind, geometry, "", model_name])
        for column in Column:
            item.setToolTip(column, item.text(column))
        item.setData(Column.NAME, COUNT_CLASS_ROLE, count_class)
        item.setTextAlignment(
            Column.COUNT, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        return item

    def update_counts(self):
        if self.dataset is None:
            return
        bids = {item.text() for item in self.baskets.selectedItems()}
        counts = {}
        for row in self.dataset.catalog:
            if not bids or row["bid"] in bids:
                cls = row["className"]
                counts[cls] = counts.get(cls, 0) + row["count"]

        def visit(item):
            cls = item.data(Column.NAME, COUNT_CLASS_ROLE)
            if cls:
                item.setText(Column.COUNT, str(counts.get(cls, 0)))
                item.setToolTip(
                    Column.COUNT,
                    "Gespeicherte Instanzen in den ausgewählten Baskets; keine Auswahl bedeutet alle.",
                )
            for i in range(item.childCount()):
                visit(item.child(i))

        for i in range(self.tree.topLevelItemCount()):
            visit(self.tree.topLevelItem(i))

    def filter(self, text):
        needle = text.casefold().strip()

        def visit(item, inherited=False):
            own = inherited or any(
                needle in item.text(c).casefold() for c in (Column.NAME, Column.MODEL)
            )
            children = [visit(item.child(i), own) for i in range(item.childCount())]
            visible = own or any(children)
            item.setHidden(not visible)
            if visible and needle and item.childCount():
                item.setExpanded(True)
            return visible

        for i in range(self.tree.topLevelItemCount()):
            visit(self.tree.topLevelItem(i))

    def add_layers(self):
        bids = [item.text() for item in self.baskets.selectedItems()]
        added = []

        def visit(item):
            spec = item.data(Column.NAME, Qt.ItemDataRole.UserRole)
            if spec and item.checkState(Column.NAME) == Qt.CheckState.Checked:
                added.append(self.layers.ensure(self.dataset, *spec, bids))
            for i in range(item.childCount()):
                visit(item.child(i))

        try:
            for i in range(self.tree.topLevelItemCount()):
                visit(self.tree.topLevelItem(i))
            if not added:
                self.status.setText("Bitte mindestens eine Objektart auswählen.")
                return
            first = next((l for l in added if l.isSpatial()), None)
            if first:
                self.iface.setActiveLayer(first)
                self.iface.mapCanvas().setExtent(
                    self.iface.mapCanvas()
                    .mapSettings()
                    .layerExtentToOutputExtent(first, first.extent())
                )
                self.iface.mapCanvas().refresh()
            self.accept()
        except Exception as e:
            self.failed(str(e))

    def reject(self):
        if self.task:
            self.task.cancel()
        super().reject()

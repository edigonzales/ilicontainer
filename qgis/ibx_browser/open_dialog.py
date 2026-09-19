from pathlib import Path
from qgis.PyQt.QtCore import Qt
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
    QListWidgetItem,
    QAbstractItemView,
    QCheckBox,
)
from qgis.core import QgsProject
from .client import manager
from .tasks import submit


class OpenDialog(QDialog):
    def __init__(self, iface, layers):
        super().__init__(iface.mainWindow())
        self.iface, self.layers = iface, layers
        self.setWindowTitle("IBX öffnen")
        self.resize(820, 620)
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
        self.search.setPlaceholderText("Objektart suchen …")
        self.search.textChanged.connect(self.filter)
        layout.addWidget(self.search)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Objektart / Geometrie", "Typ", "Objekte"])
        self.tree.setColumnWidth(0, 420)
        layout.addWidget(self.tree, 1)
        layout.addWidget(QLabel("Datenbereiche · keine Auswahl bedeutet alle"))
        self.baskets = QListWidget()
        self.baskets.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.baskets.setMaximumHeight(90)
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
                parent = QTreeWidgetItem(self.tree, [dataset.label(group_key), "", ""])
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
            if len(choices) > 1:
                parent = QTreeWidgetItem(parent, [dataset.label(cls), "", ""])
                parent.setExpanded(True)
            for geometry in choices:
                label = (
                    dataset.label(cls + "." + geometry)
                    if len(choices) > 1
                    else dataset.label(cls)
                )
                count, _, types = dataset.layer(cls, geometry, [])
                typename = (
                    "Tabelle"
                    if geometry is None
                    else (
                        "Punkt"
                        if types and all(t % 1000 in (1, 4) for t in types)
                        else (
                            "Fläche"
                            if types and all(t % 1000 in (3, 6, 10, 12) for t in types)
                            else "Geometrie"
                        )
                    )
                )
                item = QTreeWidgetItem(parent, [label, typename, str(count)])
                item.setData(0, Qt.ItemDataRole.UserRole, (cls, geometry))
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(0, Qt.CheckState.Unchecked)
                item.setToolTip(
                    0,
                    dataset.meta.get("definitions", {}).get(cls, {}).get("description")
                    or cls,
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
                    item.setCheckState(0, Qt.CheckState.Checked)
                    first = False
        self.status.setText(
            "Objektarten auswählen. Beziehungen lassen sich später auch ohne geladene Ziellayer öffnen."
        )
        self.add.setEnabled(True)
        self.filter(self.search.text())

    def filter(self, text):
        def visit(item):
            own = text.casefold() in item.text(0).casefold()
            children = [visit(item.child(i)) for i in range(item.childCount())]
            visible = own or any(children)
            item.setHidden(not visible)
            if own:
                for i in range(item.childCount()):
                    item.child(i).setHidden(False)
            return visible

        for i in range(self.tree.topLevelItemCount()):
            visit(self.tree.topLevelItem(i))

    def add_layers(self):
        bids = [item.text() for item in self.baskets.selectedItems()]
        added = []

        def visit(item):
            spec = item.data(0, Qt.ItemDataRole.UserRole)
            if spec and item.checkState(0) == Qt.CheckState.Checked:
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

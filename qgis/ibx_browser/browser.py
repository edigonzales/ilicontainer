from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QToolButton,
    QListWidget,
    QListWidgetItem,
)
from .tasks import submit
from .object_tree import ObjectTree


class ObjectBrowser(QDockWidget):
    def __init__(self, iface, layers):
        super().__init__("IBX · Objekte erkunden", iface.mainWindow())
        self.setObjectName("ibxObjectBrowser")
        self.iface, self.layers = iface, layers
        self.dataset, self.obj = None, None
        self.history = []
        self.position = -1
        self.generation = 0
        self.task = None
        root = QWidget()
        layout = QVBoxLayout(root)
        nav = QHBoxLayout()
        self.back = QPushButton("← Zurück")
        self.forward = QPushButton("Vorwärts →")
        self.cancel = QPushButton("Abbrechen")
        self.back.clicked.connect(lambda: self.travel(-1))
        self.forward.clicked.connect(lambda: self.travel(1))
        self.cancel.clicked.connect(self.abort)
        for w in [self.back, self.forward, self.cancel]:
            nav.addWidget(w)
        layout.addLayout(nav)
        self.history_hint = QLabel("Datei öffnen und ein Objekt auf der Karte auswählen.")
        self.history_hint.setWordWrap(True)
        layout.addWidget(self.history_hint)
        self.history_toggle = QToolButton()
        self.history_toggle.setObjectName("ibxHistoryToggle")
        self.history_toggle.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.history_toggle.setArrowType(Qt.ArrowType.RightArrow)
        self.history_toggle.setText("Besuchsverlauf (0)")
        self.history_toggle.setCheckable(True)
        self.history_toggle.setChecked(False)
        self.history_toggle.setToolTip(
            "Besuchsreihenfolge, keine Hierarchie. Beziehungen öffnen einen neuen Besuch."
        )
        self.history_toggle.toggled.connect(self.toggle_history)
        self.history_toggle.hide()
        layout.addWidget(self.history_toggle)
        self.history_list = QListWidget()
        self.history_list.setObjectName("ibxHistoryList")
        self.history_list.setAlternatingRowColors(True)
        self.history_list.setMaximumHeight(130)
        self.history_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.history_list.itemClicked.connect(self.visit_history_item)
        self.history_list.hide()
        layout.addWidget(self.history_list)
        self.title = QLabel("Objekte und ihre Zusammenhänge")
        self.title.setStyleSheet("font-size:18px;font-weight:600;padding:8px 0")
        self.title.setWordWrap(True)
        layout.addWidget(self.title)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.tree = ObjectTree()
        self.tree.openRequested.connect(
            lambda dataset, args: self.open(dataset, **args)
        )
        self.tree.geometryRequested.connect(self.layers.show_geometry)
        layout.addWidget(self.tree)
        actions = QHBoxLayout()
        self.map_button = QPushButton("Auf Karte zeigen")
        self.map_button.clicked.connect(self.show_map)
        self.table_button = QPushButton("Attributtabelle")
        self.table_button.clicked.connect(self.show_table)
        for w in [self.map_button, self.table_button]:
            actions.addWidget(w)
        layout.addLayout(actions)
        self.setWidget(root)
        self.setMinimumWidth(560)
        self.buttons()

    def buttons(self):
        self.back.setEnabled(self.position > 0)
        self.forward.setEnabled(self.position + 1 < len(self.history))
        self.map_button.setEnabled(
            bool(
                self.obj
                and any(
                    v.get("kind") == "geometry"
                    for vs in self.obj["fields"].values()
                    for v in vs
                )
            )
        )
        self.table_button.setEnabled(self.obj is not None)

    def abort(self):
        self.generation += 1
        self.tree.cancel_requests()
        for task in [self.task]:
            if task:
                task.cancel()
        self.status.setText("Abgebrochen. Das bisherige Objekt bleibt geöffnet.")

    def open(self, dataset, fid=None, tid=None, bid=None, history_position=None):
        self.abort()
        generation = self.generation
        self.status.setText("Objekt wird geladen …")
        self.show()
        self.raise_()
        args = dict(fid=fid) if fid is not None else dict(tid=tid, bid=bid)

        def ready(obj):
            if generation != self.generation:
                return
            if obj is None:
                self.status.setText(
                    "Das verknüpfte Objekt ist in dieser Datei nicht enthalten."
                )
                return
            self.dataset, self.obj = dataset, obj
            if history_position is None:
                self.history = self.history[: self.position + 1] + [
                    (dataset, obj["fid"], dataset.title(obj))
                ]
                self.position = len(self.history) - 1
            else:
                self.position = history_position
            self.render()

        self.task = submit(
            "IBX-Objekt lesen",
            lambda rid: dataset.call("object", requestId=rid, **args),
            ready,
            lambda text: self.error(text) if generation == self.generation else None,
            dataset.rpc,
        )

    def error(self, text):
        self.status.setText("Nicht verfügbar: " + text)

    def render(self):
        d, o = self.dataset, self.obj
        self.title.setText(d.title(o))
        self.status.setText("Pfeil: Angaben aufklappen · Öffnen: zum Objekt wechseln")
        self.render_history()
        self.tree.show_object(d, o)
        self.buttons()

    def closeEvent(self, event):
        self.abort()
        super().closeEvent(event)

    def render_history(self):
        self.history_list.clear()
        current = None
        for index, (dataset, _, title) in enumerate(self.history):
            text = f"{index + 1}. {title}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, index)
            item.setToolTip(dataset.source)
            if index == self.position:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setText(text + " (aktuell)")
                current = item
            self.history_list.addItem(item)
        self.history_toggle.setText(f"Besuchsverlauf ({len(self.history)})")
        self.history_hint.hide()
        self.history_toggle.show()
        if self.history_toggle.isChecked() and current:
            self.history_list.scrollToItem(current)

    def toggle_history(self, expanded):
        self.history_toggle.setArrowType(
            Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow
        )
        self.history_list.setVisible(expanded)

    def visit_history_item(self, item):
        position = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(position, int):
            self.visit(position)

    def visit(self, position):
        if 0 <= position < len(self.history) and position != self.position:
            dataset, fid, _ = self.history[position]
            self.open(dataset, fid=fid, history_position=position)

    def travel(self, step):
        self.visit(self.position + step)

    def show_map(self):
        if self.obj:
            self.layers.show_object(self.dataset, self.obj)

    def show_table(self):
        if self.obj:
            self.iface.showAttributeTable(
                self.layers.ensure(self.dataset, self.obj["className"])
            )

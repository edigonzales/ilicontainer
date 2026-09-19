import json
from html import escape
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QFileDialog,
    QMessageBox,
)
from .tasks import submit


class ObjectBrowser(QDockWidget):
    def __init__(self, iface, layers):
        super().__init__("IBX · Objekte erkunden", iface.mainWindow())
        self.setObjectName("ibxObjectBrowser")
        self.iface, self.layers = iface, layers
        self.dataset, self.obj = None, None
        self.history = []
        self.position = -1
        self.show_full_history = False
        self.generation = 0
        self.task = None
        self.related_task = None
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
        self.breadcrumb = QLabel("Datei öffnen und ein Objekt auf der Karte auswählen.")
        self.breadcrumb.setWordWrap(True)
        self.breadcrumb.setTextFormat(Qt.TextFormat.RichText)
        self.breadcrumb.setOpenExternalLinks(False)
        self.breadcrumb.linkActivated.connect(self.history_link)
        self.breadcrumb.setToolTip(
            "Besuchsreihenfolge, keine Hierarchie. Beziehungen öffnen einen neuen Besuch; "
            "Zurück/Vorwärts und die Links wechseln zu einem vorhandenen Besuch."
        )
        layout.addWidget(self.breadcrumb)
        self.title = QLabel("Objekte und ihre Zusammenhänge")
        self.title.setStyleSheet("font-size:18px;font-weight:600;padding:8px 0")
        self.title.setWordWrap(True)
        layout.addWidget(self.title)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Eigenschaft", "Inhalt"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setColumnWidth(0, 185)
        self.tree.itemClicked.connect(self.activate)
        layout.addWidget(self.tree)
        actions = QHBoxLayout()
        self.map_button = QPushButton("Auf Karte zeigen")
        self.map_button.clicked.connect(self.show_map)
        self.table_button = QPushButton("Attributtabelle")
        self.table_button.clicked.connect(self.show_table)
        self.export_button = QPushButton("Originalobjekte exportieren …")
        self.export_button.clicked.connect(self.export)
        for w in [self.map_button, self.table_button, self.export_button]:
            actions.addWidget(w)
        layout.addLayout(actions)
        self.setWidget(root)
        self.setMinimumWidth(420)
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
        self.export_button.setEnabled(self.obj is not None)

    def abort(self):
        self.generation += 1
        for task in [self.task, self.related_task]:
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
            self.load_related()

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
        self.status.setText("Nur lesend · Strukturen aufklappen, Beziehungen anklicken")
        self.render_history()
        self.tree.clear()
        self.fields(self.tree, o)
        self.related = QTreeWidgetItem(
            self.tree, ["Verknüpfte Objekte", "Wird geladen …"]
        )
        self.related.setExpanded(True)
        tech = QTreeWidgetItem(self.tree, ["Technische Details", ""])
        for name, value in [
            ("Klasse", o["className"]),
            ("TID", o.get("tid")),
            ("Basket", o["bid"]),
            ("FID", o["fid"]),
            ("Dateistand", d.state),
        ]:
            QTreeWidgetItem(
                tech, [name, str(value) if value is not None else "Ohne eigene TID"]
            )
        self.buttons()

    def fields(self, parent, obj):
        cls = obj["className"]
        fields = obj.get("fields", {})
        d = self.dataset
        order = [p["name"] for p in d.meta["classes"].get(cls, [])]
        order += [n for n in fields if n not in order]
        for name in order:
            values = fields.get(name)
            label = d.label(cls + "." + name)
            if values is None:
                QTreeWidgetItem(parent, [label, "Nicht angegeben"])
                continue
            if not values:
                QTreeWidgetItem(parent, [label, "Keine Einträge"])
                continue
            group = QTreeWidgetItem(
                parent, [label, f"{len(values)} Einträge" if len(values) > 1 else ""]
            )
            for i, value in enumerate(values):
                item = (
                    QTreeWidgetItem(group, [f"Eintrag {i+1}", ""])
                    if len(values) > 1
                    else group
                )
                kind = value.get("kind")
                if kind == "scalar":
                    shown = value.get("value")
                    definition = d.meta.get("definitions", {}).get(cls + "." + name, {})
                    if value.get("type") == "boolean":
                        shown = (
                            "Ja"
                            if shown == "true"
                            else "Nein" if shown == "false" else shown
                        )
                    item.setText(
                        1,
                        (
                            "Nicht angegeben"
                            if shown is None
                            else str(shown)
                            + (
                                (" " + definition["unit"])
                                if definition.get("unit")
                                else ""
                            )
                        ),
                    )
                elif kind == "reference":
                    item.setText(1, "Verknüpftes Objekt öffnen →")
                    item.setData(0, Qt.ItemDataRole.UserRole, ("reference", value))
                    item.setToolTip(
                        1,
                        "Öffnet das Ziel in diesem Fenster; der Layer muss nicht geladen sein.",
                    )
                    if value.get("fields"):
                        details = QTreeWidgetItem(item, ["Beziehungsdetails", ""])
                        self.fields(details, value)
                elif kind == "geometry":
                    item.setText(1, "Auf Karte zeigen ↗")
                    item.setData(0, Qt.ItemDataRole.UserRole, ("geometry", value))
                else:
                    self.fields(item, value)

    def activate(self, item, column):
        action = item.data(0, Qt.ItemDataRole.UserRole)
        if not action:
            return
        kind, value = action
        if kind == "reference":
            self.open(self.dataset, tid=value["tid"], bid=value.get("bid"))
        elif kind == "object":
            self.open(self.dataset, fid=value)
        elif kind == "geometry":
            self.layers.show_geometry(self.dataset, value)
        elif kind == "more":
            self.related.takeChild(self.related.indexOfChild(item))
            self.load_related(value)

    def load_related(self, after=None):
        d, o, g = self.dataset, self.obj, self.generation

        def ready(page):
            if g != self.generation:
                return
            if not page.get("indexed"):
                self.related.setText(1, "Rückwärtsbeziehungen nicht indexiert")
                return
            self.related.setText(1, "")
            for row in page["items"]:
                obj = row["object"]
                item = QTreeWidgetItem(self.related, [d.title(obj), "Objekt öffnen →"])
                item.setData(0, Qt.ItemDataRole.UserRole, ("object", obj["fid"]))
                path = row["path"].split("/")
                role = path[-2] if len(path) > 1 else "Beziehung"
                item.setToolTip(
                    0, "Verknüpft über " + d.label(obj["className"] + "." + role)
                )
                if (
                    d.meta.get("definitions", {}).get(obj["className"], {}).get("kind")
                    == "association"
                ):
                    details = QTreeWidgetItem(item, ["Beziehungsdetails", ""])
                    self.fields(details, obj)
            if page.get("next"):
                more = QTreeWidgetItem(self.related, ["Weitere anzeigen …", ""])
                more.setData(0, Qt.ItemDataRole.UserRole, ("more", page["next"]))
            if self.related.childCount() == 0:
                self.related.setText(1, "Keine eingehenden Beziehungen")

        self.related_task = submit(
            "IBX-Beziehungen lesen",
            lambda rid: d.call("related", fid=o["fid"], after=after, requestId=rid),
            ready,
            self.error,
            d.rpc,
        )

    def render_history(self):
        start = 0 if self.show_full_history else max(0, self.position - 3)
        visits = []
        if start:
            visits.append(f'<a href="earlier">… {start} frühere Besuche</a>')
        elif self.show_full_history and self.position > 3:
            visits.append('<a href="earlier">Frühere Besuche ausblenden</a>')
        for i in range(start, self.position + 1):
            dataset, _, title = self.history[i]
            label = escape(title)
            if i == self.position:
                visits.append(f"<b>{i + 1}. {label} (aktuell)</b>")
            else:
                visits.append(
                    f'<a href="visit:{i}" title="{escape(dataset.source, quote=True)}">'
                    f"{i + 1}. {label}</a>"
                )
        forward = len(self.history) - self.position - 1
        suffix = (
            f"<br>{forward} spätere Besuche über „Vorwärts“ erreichbar."
            if forward
            else ""
        )
        self.breadcrumb.setText(
            "<b>Besuchsverlauf</b> · Reihenfolge der geöffneten Objekte<br>"
            + " → ".join(visits)
            + suffix
        )

    def history_link(self, link):
        if link == "earlier":
            self.show_full_history = not self.show_full_history
            self.render_history()
        elif link.startswith("visit:") and link[6:].isdigit():
            self.visit(int(link[6:]))

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

    def export(self):
        if not self.obj:
            return
        fids = {self.obj["fid"]}
        from qgis.core import QgsProject

        for layer in QgsProject.instance().mapLayers().values():
            if (
                layer.providerType() == "ibx"
                and layer.dataProvider().dataset is self.dataset
            ):
                fids.update(layer.selectedFeatureIds())
        target, _ = QFileDialog.getSaveFileName(
            self,
            "Originalobjekte als INTERLIS-Fragment exportieren",
            "",
            "INTERLIS (*.xtf)",
        )
        if not target:
            return
        if not target.lower().endswith(".xtf"):
            target += ".xtf"
        d = self.dataset
        self.status.setText(
            f"{len(fids)} vollständige Objekte werden exportiert. Referenzierte Ziele werden nicht automatisch ergänzt."
        )
        self.task = submit(
            "IBX-Originalobjekte exportieren",
            lambda rid: d.call(
                "export", fids=sorted(fids), target=target, requestId=rid
            ),
            lambda result: self.status.setText(
                f"{result['count']} Originalobjekte exportiert. Das XTF ist ein Fragment; Referenzziele können fehlen."
            ),
            self.error,
            d.rpc,
        )

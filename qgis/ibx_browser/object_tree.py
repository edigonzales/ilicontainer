"""Lazy Qt object tree. Every request belongs to one node and one view generation."""

from qgis.PyQt.QtCore import Qt, pyqtSignal, QSize, QEvent
from qgis.PyQt.QtGui import QBrush, QColor, QPalette, QKeySequence
from qgis.PyQt.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QMenu,
    QApplication,
    QHeaderView,
)
from .presentation import Presentation, Entry
from .tasks import submit


class Item(QTreeWidgetItem):
    def __init__(self, parent, texts):
        super().__init__(parent, texts)
        self.entry = None
        self.ancestors = ()
        self.loader = None
        self.state = "unloaded"
        self.ticket = 0
        self.task = None
        self.action = None
        self.technical = False
        self.groups = {}
        self.seen = set()
        self.edge_count = 0
        self.after = None
        self.complete = False
        self.on_cancel = None


class ObjectTree(QTreeWidget):
    openRequested = pyqtSignal(object, object)
    geometryRequested = pyqtSignal(object, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dataset = None
        self.generation = 0
        self.pending = {}
        self.cache = {}
        self.tids = {}
        self.relations = None
        self.setHeaderLabels(["Eigenschaft", "Inhalt", "Aktion"])
        self.setAlternatingRowColors(True)
        self.setIndentation(16)
        self.setColumnWidth(0, 235)
        self.setColumnWidth(1, 245)
        self.setColumnWidth(2, 140)
        self.header().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.setExpandsOnDoubleClick(False)
        self.itemExpanded.connect(self.expand_item)
        self.itemCollapsed.connect(self.collapse_item)
        self.itemClicked.connect(self.activate)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)

    def remember(self, obj):
        address = self.presentation.address(obj)
        if address.fid is not None:
            self.cache[address] = obj
            if address.tid is not None:
                self.tids[(address.source, address.state, address.tid, address.bid)] = (
                    address
                )
                self.tids[(address.source, address.state, address.tid, None)] = address
        return address

    def cached(self, address):
        if address.fid is None:
            address = self.tids.get(
                (address.source, address.state, address.tid, address.bid), address
            )
        return self.cache.get(address)

    @staticmethod
    def identity(address):
        return address.source, address.state, address.fid

    def show_object(self, dataset, obj):
        self.cancel_requests()
        self.clear()
        self.cache, self.tids = {}, {}
        self.dataset = dataset
        self.presentation = Presentation(dataset)
        address = self.remember(obj)
        ancestors = ((self.identity(address), None),)
        self.add_fields(
            self.invisibleRootItem(), self.presentation.fields(obj), ancestors
        )
        self.relations = self.add_relations(self.invisibleRootItem(), obj, ancestors)
        self.add_technical(obj)
        self.relations.loader()

    def add_fields(self, parent, entries, ancestors):
        for entry in entries:
            self.add_entry(parent, entry, ancestors)

    def add_entry(self, parent, entry, ancestors):
        item = Item(parent, [entry.name, entry.value, ""])
        item.entry, item.ancestors = entry, ancestors
        item.setToolTip(0, entry.name)
        if entry.path:
            item.setToolTip(0, entry.name + "\n" + entry.path)
        item.setToolTip(1, entry.value)
        if entry.kind == "group":
            item.state = "loaded"
            self.add_fields(item, entry.children, ancestors)
        elif entry.kind == "geometry":
            self.set_action(
                item,
                "Auf Karte zeigen ↗",
                lambda: self.geometryRequested.emit(self.dataset, entry.geometry),
            )
        elif entry.kind in ("reference", "relationship"):
            self.set_action(
                item,
                "Öffnen →",
                lambda: self.openRequested.emit(
                    self.dataset, entry.address.arguments()
                ),
            )
            item.setChildIndicatorPolicy(
                QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator
            )
            item.loader = lambda: self.expand_reference(item)
            if entry.obj:
                self.remember(entry.obj)
            known = entry.obj or self.cached(entry.address)
            if known:
                item.setText(1, self.dataset.title(known))
                item.setToolTip(1, item.text(1))
        return item

    def set_action(self, item, text, callback):
        item.action = callback
        item.setText(2, text)
        item.setForeground(2, self.palette().brush(QPalette.ColorRole.Link))
        item.setToolTip(2, text + " · auch mit Eingabetaste oder Kontextmenü")

    def expand_item(self, item):
        if (
            isinstance(item, Item)
            and item.loader
            and item.state not in ("loaded", "loading")
        ):
            item.loader()

    def cancel_node(self, item):
        pending = self.pending.pop(id(item), None)
        if pending:
            item.ticket += 1
            if item.task:
                item.task.cancel()
            item.task = None
            item.state = "unloaded"
            item.setText(1, "Abgebrochen · erneut aufklappen oder laden")
            if item.on_cancel:
                item.on_cancel()
        for i in range(item.childCount()):
            self.cancel_node(item.child(i))

    def collapse_item(self, item):
        self.cancel_node(item)

    def cancel_requests(self):
        self.generation += 1
        for item in list(self.pending.values()):
            self.cancel_node(item)

    def request(self, item, operation, arguments, success, failed):
        if item.state == "loading":
            return
        item.ticket += 1
        ticket, generation = item.ticket, self.generation
        item.state = "loading"
        item.setText(1, "Wird geladen …")
        self.pending[id(item)] = item
        dataset = self.dataset

        def current():
            return (
                generation == self.generation
                and self.pending.get(id(item)) is item
                and item.ticket == ticket
            )

        def ready(value):
            if not current():
                return
            self.pending.pop(id(item), None)
            item.task = None
            item.state = "loaded"
            success(value)

        def error(message):
            if not current():
                return
            self.pending.pop(id(item), None)
            item.task = None
            item.state = "error"
            failed(message)

        item.task = submit(
            "IBX-Angaben lesen",
            lambda rid: dataset.call(operation, requestId=rid, **arguments),
            ready,
            error,
            dataset.rpc,
        )

    def retry_child(self, item, message):
        item.state = "error"
        item.setText(1, message)
        item.setToolTip(1, message)
        retry = Item(item, ["Laden fehlgeschlagen", message, ""])
        self.set_action(retry, "Erneut versuchen", item.loader)

    def clear_children(self, item):
        for i in range(item.childCount()):
            self.cancel_node(item.child(i))
        item.takeChildren()

    def expand_reference(self, item):
        entry = item.entry
        self.clear_children(item)
        # Relationship attributes are already available and remain visible even if the target fails.
        for child in entry.children:
            detail = self.add_entry(item, child, item.ancestors)
            detail.setExpanded(True)
        if entry.kind == "relationship" or entry.children:
            content = Item(
                item, ["Angaben zu: " + entry.target_label, "Noch nicht geladen", ""]
            )
            content.setChildIndicatorPolicy(
                QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator
            )
            content.loader = lambda: self.load_target(content, item, entry)
            self.set_action(
                content,
                "Laden",
                lambda: (
                    content.setExpanded(True)
                    if not content.isExpanded()
                    else content.loader()
                ),
            )
            content.on_cancel = lambda: self.set_action(
                content, "Erneut versuchen", content.loader
            )
            item.state = "loaded"
        else:
            self.load_target(item, item, entry)

    def load_target(self, content, title_item, entry):
        if content.state == "loading":
            return
        self.clear_children(content)

        def ready(obj):
            if obj is None:
                self.retry_child(
                    content, "Das Zielobjekt ist in dieser Datei nicht enthalten."
                )
                return
            address = self.remember(obj)
            title_item.setText(1, self.dataset.title(obj))
            title_item.setToolTip(1, title_item.text(1))
            content.state = "loaded"
            if content is not title_item:
                content.setText(1, self.dataset.title(obj))
                self.set_action(content, "", None)
            identity = self.identity(address)
            ancestor = next(
                (anchor for key, anchor in title_item.ancestors if key == identity),
                False,
            )
            if ancestor is not False:
                cycle = Item(
                    content,
                    ["Bereits weiter oben angezeigt", self.dataset.title(obj), ""],
                )

                def jump():
                    if ancestor is None:
                        self.scrollToTop()
                    else:
                        p = ancestor.parent()
                        while p:
                            p.setExpanded(True)
                            p = p.parent()
                        self.setCurrentItem(ancestor)
                        self.scrollToItem(ancestor)

                self.set_action(cycle, "Dorthin springen ↑", jump)
                return
            ancestors = title_item.ancestors + ((identity, title_item),)
            self.add_fields(content, self.presentation.fields(obj), ancestors)
            self.add_relations(content, obj, ancestors)

        cached = entry.obj or self.cached(entry.address)
        if cached:
            ready(cached)
        else:
            self.request(
                content,
                "object",
                entry.address.arguments(),
                ready,
                lambda message: self.retry_child(content, message),
            )

    def add_relations(self, parent, obj, ancestors):
        control = Item(parent, ["Weitere Angaben zum Objekt", "", ""])
        control.ancestors = ancestors
        control.loader = lambda: self.load_relations(control, obj)
        control.on_cancel = lambda: self.set_action(
            control, "Erneut versuchen", control.loader
        )
        self.set_action(control, "Laden", control.loader)
        control.setToolTip(
            0,
            "Zeigt anhand des Rückwärtsindex, welche Objekte auf dieses Objekt verweisen. Es wird nur eine Seite gelesen.",
        )
        return control

    def load_relations(self, control, obj):
        if control.complete or control.state == "loading":
            return

        def failed(message):
            control.setText(1, message)
            control.setToolTip(1, message)
            self.set_action(control, "Erneut versuchen", control.loader)

        def ready(page):
            if not page.get("indexed"):
                control.setText(1, "Rückwärtsbeziehungen nicht indexiert")
                self.set_action(control, "", None)
                control.complete = True
                return
            for row in page["items"]:
                self.remember(row["object"])
                for entry in self.presentation.related(row):
                    if entry.identity in control.seen:
                        continue
                    control.seen.add(entry.identity)
                    group = control.groups.get(entry.group_key)
                    if group is None:
                        parent = control.parent() or self.invisibleRootItem()
                        group = Item(parent, [entry.group, "", ""])
                        # Keep the page control after all its groups, and before technical details.
                        parent.takeChild(parent.indexOfChild(group))
                        parent.insertChild(parent.indexOfChild(control), group)
                        group.setToolTip(0, entry.group)
                        control.groups[entry.group_key] = group
                        group.setExpanded(True)
                    self.add_entry(group, entry, control.ancestors)
            control.edge_count += len(page["items"])
            control.after = page.get("next")
            control.complete = not bool(control.after)
            for group in control.groups.values():
                n = group.childCount()
                group.setText(
                    1,
                    (
                        f"{n} geladen"
                        if not control.complete
                        else ("1 Eintrag" if n == 1 else f"{n} Einträge")
                    ),
                )
            control.setText(1, "")
            self.set_action(control, "Weitere Einträge laden", control.loader)
            control.setHidden(control.complete)

        self.request(
            control,
            "related",
            {"fid": obj["fid"], "after": control.after, "limit": 50},
            ready,
            failed,
        )

    def activate(self, item, column):
        if column == 2 and isinstance(item, Item) and item.action:
            item.action()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.activate(self.currentItem(), 2)
            event.accept()
        elif event.matches(QKeySequence.StandardKey.Copy):
            self.copy_item(self.currentItem())
        else:
            super().keyPressEvent(event)

    def copy_item(self, item):
        if item:
            QApplication.clipboard().setText("\t".join(item.text(i) for i in range(2)))

    def context_menu(self, point):
        item = self.itemAt(point)
        if item is not None:
            self.menu_for_item(item).exec(self.viewport().mapToGlobal(point))

    def menu_for_item(self, item):
        menu = QMenu(self)
        if isinstance(item, Item):
            if item.loader and item.state in ("error", "unloaded"):
                menu.addAction("Angaben laden / erneut versuchen", item.loader)
            if item.action:
                menu.addAction(item.text(2), item.action)
            if item.entry and item.entry.association:
                address = self.presentation.address(item.entry.association)
                menu.addAction(
                    "Assoziation öffnen",
                    lambda: self.openRequested.emit(self.dataset, address.arguments()),
                )
        menu.addAction("Kopieren", lambda: self.copy_item(item))
        return menu

    def add_technical(self, obj):
        tech = Item(self, ["Technische Details", "", ""])
        tech.technical = True
        tech.setSizeHint(0, QSize(0, 34))
        for name, value in [
            ("Klasse", obj["className"]),
            ("TID", obj.get("tid")),
            ("Basket", obj.get("bid")),
            ("FID", obj["fid"]),
            ("Dateistand", self.dataset.state),
        ]:
            Item(
                tech, [name, str(value) if value is not None else "Ohne eigene TID", ""]
            )
        self.style_technical(tech)

    def style_technical(self, tech):
        foreground, background = self.palette().color(
            QPalette.ColorRole.Text
        ), self.palette().color(QPalette.ColorRole.Base)
        color = QColor(
            *[
                round(0.78 * a + 0.22 * b)
                for a, b in zip(foreground.getRgb()[:3], background.getRgb()[:3])
            ]
        )
        for item in [tech] + [tech.child(i) for i in range(tech.childCount())]:
            for column in (0, 1):
                item.setForeground(column, QBrush(color))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        width = self.viewport().width()
        action_width = 140
        remaining = max(200, width - action_width)
        self.setColumnWidth(0, round(remaining * 0.48))
        self.setColumnWidth(1, round(remaining * 0.52))
        self.setColumnWidth(2, action_width)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.PaletteChange:

            def update(parent):
                for i in range(parent.childCount()):
                    child = parent.child(i)
                    if isinstance(child, Item):
                        if child.technical:
                            self.style_technical(child)
                        if child.action:
                            child.setForeground(
                                2, self.palette().brush(QPalette.ColorRole.Link)
                            )
                    update(child)

            update(self.invisibleRootItem())

    def drawRow(self, painter, option, index):
        super().drawRow(painter, option, index)
        item = self.itemFromIndex(index)
        if isinstance(item, Item) and item.technical:
            painter.save()
            painter.setPen(self.palette().color(QPalette.ColorRole.Mid))
            painter.drawLine(option.rect.topLeft(), option.rect.topRight())
            painter.restore()

from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import unittest
from qgis.PyQt.QtCore import Qt, QPoint
from qgis.PyQt.QtGui import QColor, QPalette
from qgis.PyQt.QtTest import QTest
from test_ui import app, Iface, wait_until
from relation_fixtures import FixtureDataset, reference
from ibx_browser.browser import ObjectBrowser
from ibx_browser.layers import Layers
from ibx_browser.object_tree import ObjectTree


def child(parent, name):
    for i in range(parent.childCount()):
        if parent.child(i).text(0) == name:
            return parent.child(i)
    raise AssertionError(
        f"Missing child {name!r}: {[parent.child(i).text(0) for i in range(parent.childCount())]}"
    )


def click(tree, item, column=1):
    tree.scrollToItem(item)
    QTest.qWait(30)
    rect = tree.visualItemRect(item)
    x = tree.header().sectionViewportPosition(column) + min(
        35, tree.columnWidth(column) // 2
    )
    QTest.mouseClick(
        tree.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(x, rect.center().y())
    )


def expand(tree, item):
    tree.setCurrentItem(item, 0)
    tree.scrollToItem(item)
    QTest.keyClick(tree, Qt.Key.Key_Right)


class FakeTask:
    def __init__(self, work, ready, error):
        self.work, self.ready, self.error = work, ready, error
        self.cancelled = False

    def cancel(self):
        self.cancelled = True

    def deliver(self):
        self.ready(self.work("fake"))


class ObjectTreeTests(unittest.TestCase):
    def setUp(self):
        self.d = FixtureDataset()
        self.iface = Iface()
        self.browser = ObjectBrowser(self.iface, Layers(self.iface))
        self.iface.window.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea, self.browser
        )
        self.iface.window.show()
        self.browser.open(self.d, fid=1)
        wait_until(
            lambda: self.browser.obj is not None
            and self.browser.tree.relations.complete
        )
        self.tree = self.browser.tree
        self.root = self.tree.invisibleRootItem()

    def tearDown(self):
        self.browser.close()
        self.iface.window.close()
        QTest.qWait(40)

    def test_inline_clicks_cycle_reuse_and_history(self):
        order = child(self.root, "Unterhaltsauftrag")
        before = len(self.d.calls)
        click(self.tree, order)
        self.assertFalse(order.isExpanded())
        self.assertEqual(0, self.browser.position)
        expand(self.tree, order)
        wait_until(lambda: order.state == "loaded")
        self.assertEqual("Auftrag A", order.text(1))
        self.assertEqual(0, self.browser.position)
        self.assertEqual(["object"], [op for op, _ in self.d.calls[before:]])
        order.setExpanded(False)
        expand(self.tree, order)
        self.assertEqual(before + 1, len(self.d.calls))
        back = child(order, "Return")
        expand(self.tree, back)
        self.assertEqual("Bereits weiter oben angezeigt", back.child(0).text(0))
        self.assertEqual(before + 1, len(self.d.calls))
        click(self.tree, back.child(0), 2)
        self.assertEqual(0, self.browser.position)
        click(self.tree, order, 2)
        wait_until(lambda: self.browser.position == 1)
        self.assertEqual("a", self.browser.obj["tid"])

    def test_nested_control_and_keyboard_navigation(self):
        checks = child(self.root, "Checks")
        expand(self.tree, checks)
        inspector = child(checks, "Kontrollstelle")
        expand(self.tree, inspector)
        wait_until(lambda: inspector.state == "loaded")
        self.assertEqual("Organisation O", inspector.text(1))
        self.assertEqual(0, self.browser.position)
        self.tree.setCurrentItem(inspector)
        QTest.keyClick(self.tree, Qt.Key.Key_Return)
        wait_until(lambda: self.browser.position == 1)
        self.assertEqual("o", self.browser.obj["tid"])

    def test_relationship_attributes_target_and_association_action(self):
        group = child(self.root, "Zuständigkeit · Organisation")
        row = group.child(0)
        before = len(self.d.calls)
        expand(self.tree, row)
        details = child(row, "Angaben zur Zuständigkeit")
        self.assertTrue(details.isExpanded())
        self.assertEqual("verantwortlich", child(details, "Funktion").text(1))
        self.assertEqual(1, details.childCount())
        self.assertEqual(before, len(self.d.calls))
        content = child(row, "Angaben zu: Organisation")
        expand(self.tree, content)
        wait_until(lambda: content.state == "loaded")
        self.assertEqual("Organisation O", row.text(1))
        self.assertEqual("032 000 00 00", child(content, "Telefon").text(1))
        self.assertEqual(before + 1, len(self.d.calls))
        self.assertEqual(0, self.browser.position)
        menu = self.tree.menu_for_item(row)
        next(
            action for action in menu.actions() if action.text() == "Assoziation öffnen"
        ).trigger()
        wait_until(lambda: self.browser.position == 1)
        self.assertEqual(4, self.browser.obj["fid"])
        self.assertIsNone(self.browser.obj["tid"])

    def test_preloaded_reverse_object_does_not_refetch(self):
        self.browser.open(self.d, fid=2)
        wait_until(
            lambda: self.browser.obj["fid"] == 2 and self.tree.relations.complete
        )
        row = child(self.root, "Arbeit · Betroffene Objekte").child(0)
        before = len(self.d.calls)
        expand(self.tree, row)
        self.assertEqual(before, len(self.d.calls))
        self.assertEqual("Haus 1", row.text(1))

    def test_pagination_keeps_distinct_associations_and_does_not_follow_targets(self):
        rows = []
        for i in range(106):
            source = deepcopy(self.d.duty)
            source["fid"] = 100 + i
            rows.append(self.d.edge(source, "/Object/0", "h"))
        self.d.rows[1] = rows
        self.tree.show_object(self.d, self.d.house)
        control = self.tree.relations
        wait_until(lambda: control.state == "loaded")
        group = child(self.root, "Zuständigkeit · Organisation")
        self.assertEqual("50 geladen", group.text(1))
        self.assertEqual(50, group.childCount())
        count = len([c for c in self.d.calls if c[0] == "object"])
        click(self.tree, control, 2)
        wait_until(lambda: control.edge_count == 100)
        self.assertEqual("100 geladen", group.text(1))
        click(self.tree, control, 2)
        wait_until(lambda: control.complete)
        self.assertEqual("106 Einträge", group.text(1))
        self.assertEqual(
            106, len({group.child(i).entry.identity for i in range(group.childCount())})
        )
        self.assertEqual(count, len([c for c in self.d.calls if c[0] == "object"]))

    def test_missing_target_failure_retry_and_unindexed(self):
        self.d.objects.pop(2)
        order = child(self.root, "Unterhaltsauftrag")
        expand(self.tree, order)
        wait_until(lambda: order.state == "error")
        self.assertIn("nicht enthalten", order.text(1))
        self.d.objects[2] = self.d.order
        click(self.tree, order.child(0), 2)
        wait_until(lambda: order.state == "loaded")
        self.assertEqual("Auftrag A", order.text(1))
        real_call = self.d.call
        self.d.call = lambda op, **kw: (
            {"indexed": False, "items": []} if op == "related" else real_call(op, **kw)
        )
        self.tree.show_object(self.d, self.d.house)
        wait_until(lambda: self.tree.relations.complete)
        self.assertEqual(
            "Rückwärtsbeziehungen nicht indexiert", self.tree.relations.text(1)
        )

    def test_concurrent_collapse_abort_and_stale_callbacks(self):
        tasks = []

        def schedule(title, work, ready, error, rpc=None):
            task = FakeTask(work, ready, error)
            tasks.append(task)
            return task

        with patch("ibx_browser.object_tree.submit", schedule):
            order = child(self.root, "Unterhaltsauftrag")
            checks = child(self.root, "Checks")
            checks.setExpanded(True)
            inspector = child(checks, "Kontrollstelle")
            order.setExpanded(True)
            inspector.setExpanded(True)
            self.assertEqual(2, len(tasks))
            self.assertFalse(tasks[0].cancelled)
            checks.setExpanded(False)
            self.assertTrue(tasks[1].cancelled)
            tasks[
                1
            ].deliver()  # A late success must not populate the collapsed subtree.
            self.assertNotEqual("Organisation O", inspector.text(1))
            tasks[0].deliver()
            self.assertEqual("Auftrag A", order.text(1))
            checks.setExpanded(True)
            inspector.setExpanded(False)
            inspector.setExpanded(True)
            current = tasks[-1]
            self.browser.abort()
            current.deliver()
            current.error("late failure")
            self.assertNotEqual("Organisation O", inspector.text(1))
            order.setExpanded(False)
            self.tree.show_object(self.d, self.d.order)
            # New main object invalidates callbacks even if they target deleted Qt items.
            current.deliver()
            self.assertEqual("Auftrag A", child(self.root, "Name").text(1))
            tasks[-1].error("Testfehler")
            self.assertEqual("Testfehler", self.tree.relations.text(1))
            self.tree.relations.action()
            tasks[-1].deliver()
            self.assertTrue(self.tree.relations.complete)

    def test_source_and_file_state_do_not_share_cache(self):
        order = child(self.root, "Unterhaltsauftrag")
        expand(self.tree, order)
        wait_until(lambda: order.state == "loaded")
        other = FixtureDataset("other.ibx", "v2")
        other.order["fields"]["Name"][0]["value"] = "Anderer Auftrag"
        self.tree.show_object(other, other.house)
        row = child(self.root, "Unterhaltsauftrag")
        expand(self.tree, row)
        wait_until(lambda: row.state == "loaded")
        self.assertEqual("Anderer Auftrag", row.text(1))
        self.assertTrue(any(op == "object" for op, _ in other.calls))

    def test_nary_self_and_visual_themes(self):
        self.d.rows[1] += [
            self.d.edge(self.d.triple, "/First/0", "h"),
            self.d.edge(self.d.self_link, "/Before/0", "h"),
        ]
        self.tree.show_object(self.d, self.d.house)
        wait_until(lambda: self.tree.relations.complete)
        nary = child(self.root, "Triple").child(0)
        expand(self.tree, nary)
        self.assertEqual(
            {"First", "Second", "Third", "Anteil", "Weitere Angaben zum Objekt"},
            {nary.child(i).text(0) for i in range(nary.childCount())},
        )
        row = child(self.root, "Successor · After").child(0)
        expand(self.tree, row)
        content = child(row, "Angaben zu: Haus")
        expand(self.tree, content)
        self.assertEqual("Bereits weiter oben angezeigt", content.child(0).text(0))
        group = child(self.root, "Zuständigkeit · Organisation")
        expand(self.tree, group.child(0))
        org = child(group.child(0), "Angaben zu: Organisation")
        expand(self.tree, org)
        wait_until(lambda: org.state == "loaded")
        tech = child(self.root, "Technische Details")
        tech.setExpanded(True)
        Path("build/qgis").mkdir(parents=True, exist_ok=True)
        # Standalone tree screenshots at two widths, including a real dark palette.
        self.tree.setParent(None)
        self.tree.resize(820, 900)
        self.tree.show()
        QTest.qWait(60)
        self.tree.grab().save("build/qgis/relations-light.png")
        dark = QPalette(self.tree.palette())
        for role, color in [
            (QPalette.ColorRole.Base, "#202124"),
            (QPalette.ColorRole.AlternateBase, "#292a2d"),
            (QPalette.ColorRole.Text, "#eeeeee"),
            (QPalette.ColorRole.Window, "#202124"),
            (QPalette.ColorRole.WindowText, "#eeeeee"),
            (QPalette.ColorRole.Link, "#8ab4f8"),
        ]:
            dark.setColor(role, QColor(color))
        self.tree.setPalette(dark)
        self.tree.resize(440, 900)
        self.tree.scrollToItem(tech)
        QTest.qWait(60)
        self.tree.grab().save("build/qgis/relations-dark-narrow.png")
        self.assertNotEqual(
            self.tree.palette().color(QPalette.ColorRole.Text),
            tech.foreground(0).color(),
        )
        self.tree.copy_item(tech.child(0))
        self.assertIn("M.T.House", app.clipboard().text())
        self.tree.close()
        self.tree.setParent(self.browser)


if __name__ == "__main__":
    unittest.main()

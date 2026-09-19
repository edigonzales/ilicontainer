import unittest
from copy import deepcopy
from relation_fixtures import FixtureDataset, obj, reference, scalar
from ibx_browser.presentation import Presentation


class PresentationTests(unittest.TestCase):
    def setUp(self):
        self.d = FixtureDataset()
        self.p = Presentation(self.d)

    def test_binary_attributes_do_not_leak_backlink(self):
        (e,) = self.p.related(self.d.rows[1][0])
        self.assertEqual("Zuständigkeit · Organisation", e.group)
        self.assertEqual("o", e.address.tid)
        self.assertEqual(["Funktion"], [f.name for f in e.children[0].children])
        self.assertIs(self.d.duty, e.association)
        self.assertIsNone(e.association["tid"])
        other = deepcopy(self.d.duty)
        other["fid"] = 40
        (second,) = self.p.related(self.d.edge(other, "/Object/0", "h"))
        self.assertNotEqual(e.identity, second.identity)
        self.assertEqual(e.address, second.address)

    def test_embedded_inverse_and_inherited_roles(self):
        (e,) = self.p.related(self.d.rows[2][0])
        self.assertEqual("Arbeit · Betroffene Objekte", e.group)
        self.assertIs(self.d.house, e.obj)
        self.d.meta["definitions"]["M.T.SubHouse"] = {
            "extends": "M.T.House",
            "kind": "class",
        }
        sub = dict(self.d.house, className="M.T.SubHouse")
        (e,) = self.p.related(self.d.edge(sub, "/Order/0", "a"))
        self.assertEqual("Arbeit · Betroffene Objekte", e.group)
        self.assertEqual("M.T.SubHouse", e.obj["className"])

    def test_nested_reference_resolves_concrete_structure(self):
        (e,) = self.p.related(self.d.edge(self.d.house, "/Checks/0/Inspector/0", "o"))
        self.assertIn("Eintrag 1", e.group)
        self.assertIn("Kontrollstelle", e.group)
        self.assertEqual("/Checks/0/Inspector/0", e.path)

    def test_nary_and_ambiguous_fallback_preserves_all_roles(self):
        (e,) = self.p.related(self.d.edge(self.d.triple, "/First/0", "h"))
        self.assertIs(self.d.triple, e.obj)
        self.assertEqual({"First", "Second", "Third", "Anteil"}, set(e.obj["fields"]))
        del self.d.meta["definitions"]["M.T.Duty.Organisation"]
        (e,) = self.p.related(self.d.rows[1][0])
        self.assertIs(self.d.duty, e.obj)
        (e,) = self.p.related(self.d.edge(self.d.triple, "/does/not/exist/0", "h"))
        self.assertIs(self.d.triple, e.obj)

    def test_self_relation_keeps_opposite_role(self):
        (e,) = self.p.related(self.d.edge(self.d.self_link, "/Before/0", "h"))
        self.assertEqual("h", e.address.tid)
        self.assertIn("After", e.group)
        self.assertEqual([], e.children[0].children)

    def test_repeated_origin_only_removes_proven_occurrence(self):
        source = deepcopy(self.d.duty)
        source["fields"]["Object"].append(reference("h"))
        (a,) = self.p.related(self.d.edge(source, "/Object/0", "h"))
        (b,) = self.p.related(self.d.edge(source, "/Object/1", "h"))
        self.assertNotEqual(a.identity, b.identity)
        self.assertIn("Object", [f.name for f in a.children[0].children])

    def test_unproven_edge_does_not_hide_roles(self):
        (e,) = self.p.related(self.d.edge(self.d.duty, "/Object/0", "wrong"))
        self.assertIs(self.d.duty, e.obj)

    def test_embedded_role_payloads_survive_compact_association(self):
        source = deepcopy(self.d.duty)
        source["fields"]["Object"][0]["fields"] = {
            "OriginNote": [scalar("origin detail")]
        }
        source["fields"]["Organisation"][0]["fields"] = {
            "TargetNote": [scalar("target detail")]
        }
        (entry,) = self.p.related(self.d.edge(source, "/Object/0", "h"))
        details = entry.children[0].children
        self.assertEqual("origin detail", details[-2].children[0].value)
        self.assertEqual("target detail", details[-1].children[0].value)

    def test_sources_and_versions_are_distinct(self):
        a = self.p.address(self.d.house)
        b = Presentation(FixtureDataset("other.ibx")).address(self.d.house)
        c = Presentation(FixtureDataset(state="v2")).address(self.d.house)
        self.assertEqual(3, len({a, b, c}))

    def test_fields_keep_exact_numbers_missing_empty_and_embedded_details(self):
        o = obj(
            "M.T.House",
            90,
            "n",
            Number=[scalar("999999999999.123456789")],
            Empty=[],
            Order=[reference("a", fields={"Reason": [scalar("Test")]})],
        )
        self.d.meta["classes"]["M.T.House"] = [{"name": "Missing"}]
        fields = {e.name: e for e in self.p.fields(o)}
        self.assertEqual("Nicht angegeben", fields["Missing"].value)
        self.assertEqual("Keine Einträge", fields["Empty"].value)
        self.assertEqual("999999999999.123456789", fields["Number"].value)
        self.assertEqual(
            "Test", fields["Unterhaltsauftrag"].children[0].children[0].value
        )


if __name__ == "__main__":
    unittest.main()

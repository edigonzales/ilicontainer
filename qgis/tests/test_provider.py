import concurrent.futures
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from qgis.core import *
from qgis.PyQt.QtCore import QSize
from ibx_browser.client import manager
from ibx_browser.provider import Metadata, uri

app = QgsApplication([], False)
app.initQgis()


class ProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manager.start()
        cls.dataset = manager.dataset(str(Path("demo/quartier.ibx").resolve()))
        cls.hash = hashlib.sha256(Path(cls.dataset.source).read_bytes()).hexdigest()
        QgsProviderRegistry.instance().registerProvider(Metadata())

    @classmethod
    def tearDownClass(cls):
        QgsProject.instance().removeAllMapLayers()
        assert (
            hashlib.sha256(Path(cls.dataset.source).read_bytes()).hexdigest()
            == cls.hash
        )
        manager.process.closeWriteChannel()
        manager.process.waitForFinished(3000)

    def layer(self, geometry="Grundriss", cls="Gebaeude"):
        d = self.dataset
        l = QgsVectorLayer(
            uri(d.source, d.state, "Quartier.Unterhalt." + cls, geometry), "Demo", "ibx"
        )
        self.assertTrue(l.isValid())
        return l

    def test_catalog_count_and_features(self):
        d = self.dataset
        before = d.call("metrics")["chunksRead"]
        l = self.layer()
        self.assertEqual(24, l.featureCount())
        self.assertFalse(l.extent().isNull())
        self.assertEqual(before, d.call("metrics")["chunksRead"])
        features = list(l.getFeatures())
        self.assertEqual(24, len(features))
        self.assertTrue(all(f.hasGeometry() for f in features))
        self.assertFalse(l.startEditing())

    def test_fid_bbox_projection_and_expression(self):
        l = self.layer()
        f = next(l.getFeatures())
        self.assertEqual(f.id(), next(l.getFeatures(QgsFeatureRequest(f.id()))).id())
        self.assertEqual(
            0, len(list(l.getFeatures(QgsFeatureRequest().setFilterFids([]))))
        )
        req = QgsFeatureRequest().setFilterRect(
            QgsRectangle(2600001, 1200001, 2600010, 1200010)
        )
        req.setFlags(Qgis.FeatureRequestFlag.ExactIntersect)
        self.assertEqual(1, len(list(l.getFeatures(req))))
        req = (
            QgsFeatureRequest()
            .setFilterExpression("\"Nummer\" = '1'")
            .setSubsetOfAttributes(["Name"], l.fields())
            .setFlags(
                Qgis.FeatureRequestFlag.NoGeometry
                | Qgis.FeatureRequestFlag.SubsetOfAttributes
            )
        )
        fs = list(l.getFeatures(req))
        self.assertEqual(1, len(fs))
        self.assertFalse(fs[0].hasGeometry())
        self.assertEqual("Haus am Park 1", fs[0]["Name"])
        self.assertEqual(3, len(list(l.getFeatures(QgsFeatureRequest().setLimit(3)))))

    def test_subset_rewind_tables_and_parallel_iterators(self):
        l = self.layer()
        l.setSubsetString("\"Nummer\" = '2'")
        self.assertEqual(1, len(list(l.getFeatures())))
        self.assertEqual(-1, l.featureCount())
        it = l.getFeatures()
        a = next(it)
        self.assertTrue(it.rewind())
        self.assertEqual(a.id(), next(it).id())
        it.close()
        t = self.layer(None, "Auftrag")
        self.assertEqual(8, len(list(t.getFeatures())))
        self.assertFalse(t.isSpatial())
        source = t.dataProvider().featureSource()
        with concurrent.futures.ThreadPoolExecutor(4) as pool:
            results = list(
                pool.map(
                    lambda _: len(list(source.getFeatures(QgsFeatureRequest()))),
                    range(8),
                )
            )
        self.assertEqual([8] * 8, results)

    def test_crs_render_and_project_reload(self):
        l = self.layer()
        QgsProject.instance().addMapLayer(l)
        req = QgsFeatureRequest().setDestinationCrs(
            QgsCoordinateReferenceSystem("EPSG:4326"),
            QgsProject.instance().transformContext(),
        )
        f = next(l.getFeatures(req))
        self.assertLess(f.geometry().boundingBox().xMinimum(), 10)
        settings = QgsMapSettings()
        settings.setLayers([l])
        settings.setExtent(l.extent())
        settings.setOutputSize(QSize(400, 300))
        settings.setDestinationCrs(l.crs())
        job = QgsMapRendererParallelJob(settings)
        job.start()
        job.waitForFinished()
        self.assertFalse(job.renderedImage().isNull())
        self.assertFalse(job.errors())
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "test.qgs")
            self.assertTrue(QgsProject.instance().write(path))
            text = Path(path).read_text()
            self.assertNotIn(manager.rpc.token, text)
            self.assertNotIn(str(manager.rpc.url), text)
            QgsProject.instance().clear()
            self.assertTrue(QgsProject.instance().read(path))
            restored = list(QgsProject.instance().mapLayers().values())[0]
            self.assertTrue(restored.isValid())
            self.assertEqual(24, len(list(restored.getFeatures())))
        QgsProject.instance().clear()

    def test_cancel_and_pinned_state(self):
        l = self.layer()
        feedback = QgsFeedback()
        request = QgsFeatureRequest()
        request.setFeedback(feedback)
        feedback.cancel()
        self.assertEqual([], list(l.getFeatures(request)))
        d = self.dataset
        wrong = QgsVectorLayer(
            uri(d.source, "another-state", "Quartier.Unterhalt.Gebaeude", "Grundriss"),
            "Wrong version",
            "ibx",
        )
        self.assertFalse(wrong.isValid())
        # Reopen using a fresh bridge session (as after application restart).
        manager.datasets.clear()
        restored = QgsVectorLayer(
            uri(d.source, d.state, "Quartier.Unterhalt.Gebaeude", "Grundriss"),
            "Restored",
            "ibx",
        )
        self.assertTrue(restored.isValid())
        self.assertEqual(24, len(list(restored.getFeatures())))

    def test_object_navigation(self):
        d = self.dataset
        g = d.call("object", tid="g0")
        a = d.call("object", tid=g["fields"]["Auftrag"][0]["tid"])
        p = d.call("related", fid=a["fid"], limit=2)
        items = list(p["items"])
        while p["next"]:
            p = d.call("related", fid=a["fid"], after=p["next"], limit=2)
            items.extend(p["items"])
        self.assertEqual(7, len(items))
        self.assertTrue(
            any(r["object"]["className"].endswith("Spielplatz") for r in items)
        )
        self.assertIsNone(d.call("object", tid="not-present"))

    def test_parkanlage_geometry_and_model(self):
        d = manager.dataset(str(Path("demo/parkanlage.ibx").resolve()))
        counts = {}
        for item in d.catalog:
            counts[item["className"]] = counts.get(item["className"], 0) + item["count"]
        self.assertEqual(3, counts["Parkanlage.Park.Spielplatz"])
        self.assertEqual(6, counts["Parkanlage.Park.Spielgeraet"])

        definitions = d.meta["definitions"]
        self.assertFalse(
            any("extends" in definition for definition in definitions.values())
        )
        self.assertFalse(
            any(
                definition.get("kind") == "association"
                for definition in definitions.values()
            )
        )
        reference = definitions["Parkanlage.Park.Spielgeraet.Spielplatz"]
        self.assertEqual("Parkanlage.Park.Spielplatz", reference["target"])

        playgrounds = QgsVectorLayer(
            uri(d.source, d.state, "Parkanlage.Park.Spielplatz", "Flaeche"),
            "Parkanlage",
            "ibx",
        )
        devices = QgsVectorLayer(
            uri(d.source, d.state, "Parkanlage.Park.Spielgeraet", "Position"),
            "Spielgeräte",
            "ibx",
        )
        self.assertTrue(playgrounds.isValid())
        self.assertTrue(devices.isValid())
        self.assertEqual(3, playgrounds.featureCount())
        self.assertEqual(6, devices.featureCount())
        self.assertTrue(
            all(feature.hasGeometry() for feature in playgrounds.getFeatures())
        )
        self.assertTrue(all(feature.hasGeometry() for feature in devices.getFeatures()))

        device = d.call("object", tid="geraet1")
        control = device["fields"]["Kontrollen"][0]
        self.assertEqual("structure", control["kind"])
        self.assertEqual("beobachten", control["fields"]["Ergebnis"][0]["value"])
        measurement = control["fields"]["Messwerte"][0]
        self.assertEqual("Roststelle", measurement["fields"]["Merkmal"][0]["value"])

        playground = d.call("object", tid="park0")
        related = d.call("related", fid=playground["fid"], limit=50)
        self.assertTrue(related["indexed"])
        self.assertEqual(2, len(related["items"]))
        self.assertEqual(
            {"geraet0", "geraet1"},
            {item["object"]["tid"] for item in related["items"]},
        )

    def test_quartier_model_has_no_ibx_label_or_title_metadata(self):
        model = Path("demo/Quartier.ili").read_text(encoding="utf-8")
        self.assertNotIn("!!@ ibx.", model)
        for definition in self.dataset.meta["definitions"].values():
            self.assertFalse(definition.get("titleAttribute"))
        definitions = self.dataset.meta["definitions"]
        self.assertEqual("Gebaeude", definitions["Quartier.Unterhalt.Gebaeude"]["label"])
        self.assertEqual("Auftrag", definitions["Quartier.Unterhalt.Auftrag"]["label"])


if __name__ == "__main__":
    unittest.main()

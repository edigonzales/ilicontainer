"""Streaming read-only provider. No memory layer and no implicit materialization."""

import base64
import json
from decimal import Decimal
from qgis.core import (
    Qgis,
    QgsVectorDataProvider,
    QgsDataProvider,
    QgsProviderMetadata,
    QgsAbstractFeatureSource,
    QgsAbstractFeatureIterator,
    QgsFeatureIterator,
    QgsFeatureRequest,
    QgsFeature,
    QgsFields,
    QgsField,
    QgsGeometry,
    QgsRectangle,
    QgsCoordinateReferenceSystem,
    QgsExpression,
    QgsExpressionContext,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QMetaType
from .client import manager


def uri(source, state, cls, geometry=None, bids=None, options=None):
    return json.dumps(
        dict(
            source=source,
            state=state,
            className=cls,
            geometry=geometry,
            bids=sorted(bids or []),
            options=options or {},
        ),
        ensure_ascii=False,
        sort_keys=True,
    )


class Source(QgsAbstractFeatureSource):
    def __init__(self, provider):
        super().__init__()
        self.dataset = provider.dataset
        self.spec = dict(provider.spec)
        self.fields = QgsFields(provider.fields())
        self.crs = provider.crs()
        self.subset = provider.subsetString()

    def getFeatures(self, request):
        return QgsFeatureIterator(Iterator(self, request))


class Iterator(QgsAbstractFeatureIterator):
    def __init__(self, source, request):
        super().__init__(request)
        self.source, self.req = source, QgsFeatureRequest(request)
        self.cursor, self.buffer, self.done, self.started = None, iter(()), False, False
        self.delivered = 0
        self.transform = request.calculateTransform(source.crs)
        self.rect = self.filterRectToSourceCrs(self.transform)
        self.context = QgsExpressionContext(self.req.expressionContext())
        self.context.setFields(source.fields)
        self.expr = (
            QgsExpression(self.req.filterExpression().expression())
            if self.req.filterType() == QgsFeatureRequest.FilterType.FilterExpression
            else None
        )
        if self.expr:
            self.expr.prepare(self.context)
        self.subset = QgsExpression(source.subset) if source.subset else None
        if self.subset:
            self.subset.prepare(self.context)
        self.engine = None
        if not self.rect.isNull():
            self.rect_geometry = QgsGeometry.fromRect(self.rect)
            self.engine = QgsGeometry.createGeometryEngine(
                self.rect_geometry.constGet()
            )
            self.engine.prepareGeometry()

    def _page(self):
        if not self.started:
            spec = self.source.spec
            args = dict(
                className=spec["className"],
                geometry=spec.get("geometry"),
                bids=spec.get("bids", []),
            )
            ft = self.req.filterType()
            if ft == QgsFeatureRequest.FilterType.FilterFid:
                args["fids"] = [self.req.filterFid()]
            elif ft == QgsFeatureRequest.FilterType.FilterFids:
                args["fids"] = list(self.req.filterFids())
            if not self.rect.isNull():
                args["bbox"] = dict(
                    minX=self.rect.xMinimum(),
                    minY=self.rect.yMinimum(),
                    maxX=self.rect.xMaximum(),
                    maxY=self.rect.yMaximum(),
                )
            # Keep geometry for spatial/expression filtering even under NoGeometry.
            args["noGeometry"] = (
                bool(self.req.flags() & Qgis.FeatureRequestFlag.NoGeometry)
                and self.rect.isNull()
                and not self.expr
                and not self.subset
                and self.req.spatialFilterType()
                != Qgis.SpatialFilterType.DistanceWithin
            )
            if (
                not self.expr
                and not self.subset
                and self.req.flags() & Qgis.FeatureRequestFlag.SubsetOfAttributes
            ):
                args["fields"] = [
                    self.source.fields[i].name() for i in self.req.subsetOfAttributes()
                ]
            result = self.source.dataset.call("query", **args)
            self.started = True
        elif self.cursor:
            result = self.source.dataset.call("next", cursor=self.cursor)
        else:
            return False
        self.cursor = result["cursor"]
        self.buffer = iter(result["items"])
        return bool(result["items"])

    def fetchFeature(self, feature):
        if self.done:
            return False
        if self.req.limit() >= 0 and self.delivered >= self.req.limit():
            self.close()
            return False
        feedback = self.req.feedback()
        try:
            while True:
                if feedback and feedback.isCanceled():
                    self.close()
                    return False
                row = next(self.buffer, None)
                if row is None:
                    if not self._page():
                        self.close()
                        return False
                    continue
                f = QgsFeature(self.source.fields)
                f.setId(row["fid"])
                values = []
                attrs = dict(
                    row["attributes"], _ibx_tid=row["tid"], _ibx_bid=row["bid"]
                )
                for field in self.source.fields:
                    value = attrs.get(field.name())
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value, ensure_ascii=False)
                    if value is not None and field.type() == QMetaType.Type.Bool:
                        value = value == "true"
                    elif value is not None and field.type() == QMetaType.Type.LongLong:
                        value = int(Decimal(value))
                    values.append(value)
                f.setAttributes(values)
                if row["wkb"]:
                    geometry = QgsGeometry()
                    geometry.fromWkb(base64.b64decode(row["wkb"]))
                    f.setGeometry(geometry)
                if not self.rect.isNull():
                    if not f.hasGeometry():
                        continue
                    if self.req.flags() & Qgis.FeatureRequestFlag.ExactIntersect:
                        if not self.engine.intersects(f.geometry().constGet()):
                            continue
                    elif not f.geometry().boundingBox().intersects(self.rect):
                        continue
                self.context.setFeature(f)
                if self.expr and not self.expr.evaluate(self.context):
                    continue
                if self.subset and not self.subset.evaluate(self.context):
                    continue
                if f.hasGeometry():
                    self.geometryToDestinationCrs(f, self.transform)
                if (
                    self.req.spatialFilterType()
                    == Qgis.SpatialFilterType.DistanceWithin
                ):
                    if (
                        not f.hasGeometry()
                        or f.geometry().distance(self.req.referenceGeometry())
                        > self.req.distanceWithin()
                    ):
                        continue
                if self.req.flags() & Qgis.FeatureRequestFlag.NoGeometry:
                    f.clearGeometry()
                if self.req.flags() & Qgis.FeatureRequestFlag.SubsetOfAttributes:
                    keep = set(self.req.subsetOfAttributes())
                    f.setAttributes(
                        [v if i in keep else None for i, v in enumerate(f.attributes())]
                    )
                feature.setFields(self.source.fields)
                feature.setId(f.id())
                feature.setAttributes(f.attributes())
                feature.setGeometry(f.geometry())
                feature.setValid(True)
                self.delivered += 1
                return True
        except Exception:
            self.close()
            raise

    def rewind(self):
        self.close()
        self.done = False
        self.started = False
        self.delivered = 0
        self.buffer = iter(())
        return True

    def close(self):
        if self.cursor:
            try:
                self.source.dataset.call("closeCursor", cursor=self.cursor)
            except Exception:
                pass  # The bridge also expires abandoned cursors.
        self.cursor = None
        self.done = True
        return True


class Provider(QgsVectorDataProvider):
    def __init__(self, source, options=None, flags=None):
        super().__init__(source)
        self.spec = json.loads(source)
        self.dataset = manager.for_provider(
            self.spec["source"], self.spec.get("options")
        )
        if self.spec.get("state") != self.dataset.state:
            self.setError(
                __import__("qgis.core", fromlist=["QgsError"]).QgsError(
                    "Die IBX-Datei wurde ersetzt. Bitte neu öffnen.", "IBX"
                )
            )
            self.valid = False
        else:
            self.valid = True
        self._fields = QgsFields()
        self._subset = ""
        cls, geometry = self.spec["className"], self.spec.get("geometry")
        for prop in self.dataset.meta["classes"][cls]:
            name = prop["name"]
            key = cls + "." + name
            if key in self.dataset.meta["geometries"]:
                continue
            typ = self.dataset.meta["scalarTypes"].get(key)
            field_type = (
                QMetaType.Type.Bool if typ == "boolean" else QMetaType.Type.QString
            )
            definition = self.dataset.meta.get("definitions", {}).get(key, {})
            if (
                typ == "integer"
                and definition.get("minimum") is not None
                and definition.get("maximum") is not None
            ):
                if (
                    -(2**63) <= Decimal(definition["minimum"])
                    and Decimal(definition["maximum"]) < 2**63
                ):
                    field_type = QMetaType.Type.LongLong
            self._fields.append(QgsField(name, field_type))
        for name in ["_ibx_tid", "_ibx_bid"]:
            self._fields.append(QgsField(name, QMetaType.Type.QString))
        self.count, extent, types = self.dataset.layer(
            cls, geometry, self.spec.get("bids")
        )
        self._extent = QgsRectangle(*extent) if extent else QgsRectangle()
        descriptor = self.dataset.meta["geometries"].get(cls + "." + str(geometry), {})
        self._crs = QgsCoordinateReferenceSystem(descriptor.get("crs", ""))
        fallback = (
            1
            if "Coord" in descriptor.get("type", "")
            else (
                10
                if "Surface" in descriptor.get("type", "")
                or "Area" in descriptor.get("type", "")
                else 9
            )
        )
        self._wkb = (
            Qgis.WkbType.NoGeometry
            if not geometry
            else Qgis.WkbType(next(iter(types)) if len(types) == 1 else fallback)
        )

    @classmethod
    def createProvider(cls, source, options, flags=QgsDataProvider.ReadFlags()):
        return cls(source, options, flags)

    def isValid(self):
        return self.valid

    def name(self):
        return "ibx"

    def description(self):
        return "INTERLIS Binary eXchange"

    def storageType(self):
        return "IBX (read-only)"

    def fields(self):
        return self._fields

    def crs(self):
        return self._crs

    def wkbType(self):
        return self._wkb

    def extent(self):
        return self._extent

    def featureCount(self):
        return self.count if not self._subset else -1

    def capabilities(self):
        return Qgis.VectorProviderCapability.SelectAtId

    def featureSource(self):
        return Source(self)

    def getFeatures(self, request=QgsFeatureRequest()):
        return QgsFeatureIterator(Iterator(Source(self), request))

    def supportsSubsetString(self):
        return True

    def subsetString(self):
        return self._subset

    def setSubsetString(self, text, updateFeatureCount=True):
        if text:
            expr = QgsExpression(text)
            if expr.hasParserError():
                return False
        self._subset = text
        self.dataChanged.emit()
        return True


def Metadata():
    return QgsProviderMetadata(
        "ibx", "INTERLIS Binary eXchange", Provider.createProvider
    )

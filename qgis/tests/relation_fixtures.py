"""Typed protocol fixtures for binary/n-ary/self and nested relationship cases."""

from copy import deepcopy
from ibx_browser.client import Dataset


def scalar(value):
    return {"kind": "scalar", "type": "text", "value": value}


def reference(tid, bid=None, fields=None):
    return {
        "kind": "reference",
        "className": "REF",
        "tid": tid,
        "bid": bid,
        "fields": fields or {},
    }


def obj(cls, fid, tid, **fields):
    return {"className": cls, "fid": fid, "tid": tid, "bid": "b", "fields": fields}


class FixtureDataset:
    label = Dataset.label
    title = Dataset.title

    def __init__(self, source="fixture.ibx", state="v1"):
        self.source, self.state = source, state
        self.rpc = None
        self.calls = []
        self.meta = {"definitions": {}, "classes": {}}
        d = self.meta["definitions"]
        for cls, label in [
            ("M.T.House", "Haus"),
            ("M.T.Order", "Auftrag"),
            ("M.T.Org", "Organisation"),
            ("M.T.Structure", "Kontrolle"),
        ]:
            d[cls] = {"kind": "class", "label": label, "titleAttribute": "Name"}
        for association, role_names in [
            ("M.T.Duty", ["Object", "Organisation"]),
            ("M.T.Work", ["Objects", "Order"]),
            ("M.T.Triple", ["First", "Second", "Third"]),
            ("M.T.Successor", ["Before", "After"]),
        ]:
            d[association] = {
                "kind": "association",
                "label": association.rsplit(".", 1)[1],
            }
            for role in role_names:
                target = "M.T.Org" if role == "Organisation" else "M.T.House"
                d[association + "." + role] = {
                    "label": role,
                    "type": "reference",
                    "association": association,
                    "target": target,
                }
        d["M.T.Duty"]["label"] = "Zuständigkeit"
        d["M.T.Work"]["label"] = "Arbeit"
        d["M.T.Work.Objects"]["label"] = "Betroffene Objekte"
        d["M.T.House.Order"] = deepcopy(d["M.T.Work.Order"])
        d["M.T.House.Order"].update(label="Unterhaltsauftrag", target="M.T.Order")
        d["M.T.Structure.Inspector"] = {
            "type": "reference",
            "target": "M.T.Org",
            "label": "Kontrollstelle",
        }
        self.house = obj(
            "M.T.House",
            1,
            "h",
            Name=[scalar("Haus 1")],
            Order=[reference("a")],
            Checks=[
                {
                    "kind": "structure",
                    "className": "M.T.Structure",
                    "fields": {"Inspector": [reference("o")]},
                }
            ],
        )
        self.order = obj(
            "M.T.Order", 2, "a", Name=[scalar("Auftrag A")], Return=[reference("h")]
        )
        self.org = obj(
            "M.T.Org",
            3,
            "o",
            Name=[scalar("Organisation O")],
            Telefon=[scalar("032 000 00 00")],
        )
        self.duty = obj(
            "M.T.Duty",
            4,
            None,
            Object=[reference("h")],
            Organisation=[reference("o")],
            Funktion=[scalar("verantwortlich")],
        )
        self.triple = obj(
            "M.T.Triple",
            5,
            None,
            First=[reference("h")],
            Second=[reference("o")],
            Third=[reference("a")],
            Anteil=[scalar("0.1234567890123456789")],
        )
        self.self_link = obj(
            "M.T.Successor", 6, None, Before=[reference("h")], After=[reference("h")]
        )
        self.objects = {
            o["fid"]: o
            for o in (
                self.house,
                self.order,
                self.org,
                self.duty,
                self.triple,
                self.self_link,
            )
        }
        self.rows = {
            1: [self.edge(self.duty, "/Object/0", "h")],
            2: [self.edge(self.house, "/Order/0", "a")],
        }

    @staticmethod
    def edge(source, path, target, bid=None):
        return {
            "sourceFid": source["fid"],
            "path": path,
            "targetTid": target,
            "targetBid": bid,
            "order": 0,
            "object": source,
        }

    def call(self, op, **args):
        self.calls.append((op, args))
        if op == "object":
            if "fid" in args:
                return self.objects.get(args["fid"])
            return next(
                (
                    o
                    for o in self.objects.values()
                    if o["tid"] == args["tid"]
                    and (args.get("bid") is None or args["bid"] == o["bid"])
                ),
                None,
            )
        if op == "related":
            rows = self.rows.get(args["fid"], [])
            start = int(args.get("after") or 0)
            end = start + args.get("limit", 50)
            return {
                "indexed": True,
                "items": rows[start:end],
                "next": str(end) if end < len(rows) else None,
            }
        raise AssertionError(op)

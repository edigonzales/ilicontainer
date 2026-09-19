"""GUI-independent object/relationship presentation. No I/O and no demo conventions."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Address:
    source: str
    state: str
    fid: int | None = None
    tid: str | None = None
    bid: str | None = None

    def arguments(self):
        return (
            {"fid": self.fid}
            if self.fid is not None
            else {"tid": self.tid, "bid": self.bid}
        )


@dataclass
class Entry:
    name: str
    value: str = ""
    kind: str = "value"
    children: list = field(default_factory=list)
    address: Address | None = None
    obj: dict | None = None
    geometry: dict | None = None
    association: dict | None = None
    group: str = ""
    group_key: tuple = ()
    identity: tuple = ()
    path: str = ""
    target_label: str = "Objekt"


class Presentation:
    def __init__(self, dataset):
        self.dataset = dataset
        self.meta = dataset.meta
        self.definitions = self.meta.get("definitions", {})

    def address(self, obj):
        return Address(
            self.dataset.source,
            self.dataset.state,
            obj.get("fid"),
            obj.get("tid"),
            obj.get("bid"),
        )

    def definition(self, cls, name):
        seen = set()
        while cls and cls not in seen:
            seen.add(cls)
            key = cls + "." + name
            if key in self.definitions:
                return self.definitions[key]
            cls = self.definitions.get(cls, {}).get("extends")
        return {}

    def label(self, cls, name):
        return self.definition(cls, name).get("label") or name

    def roles(self, association):
        result, seen = {}, set()
        cls = association
        while cls and cls not in seen:
            seen.add(cls)
            for key, value in self.definitions.items():
                if (
                    key.rsplit(".", 1)[0] == cls
                    and value.get("association")
                    and value.get("type") == "reference"
                ):
                    result.setdefault(key.rsplit(".", 1)[1], value)
            cls = self.definitions.get(cls, {}).get("extends")
        return result

    def fields(self, obj, omit=(), path=""):
        cls, fields = obj["className"], obj.get("fields", {})
        order = [p["name"] for p in self.meta.get("classes", {}).get(cls, [])]
        order += [name for name in fields if name not in order]
        entries = []
        for name in order:
            if name in omit:
                continue
            label, values = self.label(cls, name), fields.get(name)
            if values is None or not values:
                entries.append(
                    Entry(
                        label, "Nicht angegeben" if values is None else "Keine Einträge"
                    )
                )
                continue
            children = []
            for i, value in enumerate(values):
                entry = Entry(
                    label if len(values) == 1 else f"Eintrag {i+1}",
                    path=f"{path}/{name}/{i}",
                )
                kind = value.get("kind")
                if kind == "scalar":
                    shown = value.get("value")
                    if value.get("type") == "boolean":
                        shown = {"true": "Ja", "false": "Nein"}.get(shown, shown)
                    unit = self.definition(cls, name).get("unit")
                    entry.value = (
                        "Nicht angegeben"
                        if shown is None
                        else str(shown) + (" " + unit if unit else "")
                    )
                elif kind == "geometry":
                    entry.kind, entry.geometry = "geometry", value
                elif kind == "reference":
                    entry.kind, entry.address = "reference", self.address(value)
                    entry.value = "Noch nicht geladen"
                    target = self.definition(cls, name).get("target")
                    entry.target_label = (
                        self.dataset.label(target) if target else "Objekt"
                    )
                    if value.get("fields"):
                        association = self.definition(cls, name).get("association")
                        label_assoc = (
                            self.dataset.label(association)
                            if association
                            else "Beziehung"
                        )
                        entry.children = [
                            Entry(
                                "Angaben zur " + label_assoc,
                                kind="group",
                                children=self.fields(value, path=entry.path),
                            )
                        ]
                else:
                    entry.kind, entry.children = "group", self.fields(
                        value, path=entry.path
                    )
                children.append(entry)
            entries.extend(
                children
                if len(values) == 1
                else [Entry(label, f"{len(values)} Einträge", "group", children)]
            )
        return entries

    def path_context(self, obj, path):
        """Resolve against the actual concrete type at every structure level."""
        parts = path.strip("/").split("/")
        labels, owner = [], obj
        if not parts or len(parts) % 2:
            return None
        try:
            for i in range(0, len(parts), 2):
                name, index = parts[i], int(parts[i + 1])
                values = owner["fields"][name]
                if index < 0:
                    return None
                label = self.label(owner["className"], name)
                if len(values) > 1 or i + 2 < len(parts):
                    label += f" · Eintrag {index+1}"
                labels.append(label)
                value = values[index]
                if i + 2 == len(parts):
                    return owner, name, value, " › ".join(labels)
                owner = value
        except (KeyError, IndexError, TypeError, ValueError):
            return None

    def related(self, row):
        obj, path = row["object"], row["path"]
        cls = obj["className"]
        context = self.path_context(obj, path)
        identity = (self.dataset.source, self.dataset.state, row["sourceFid"], path)
        is_association = self.definitions.get(cls, {}).get("kind") == "association"
        role = context[1] if context else None
        roles = self.roles(cls) if is_association else {}
        # Only compact a proven direct role edge of an unambiguous binary association.
        direct = context and context[0] is obj and context[2].get("kind") == "reference"
        proven = (
            direct
            and context[2].get("tid") == row.get("targetTid")
            and context[2].get("bid") == row.get("targetBid")
        )
        if is_association and proven and len(roles) == 2 and role in roles:
            other = next(name for name in roles if name != role)
            targets = obj.get("fields", {}).get(other, [])
            if targets and all(v.get("kind") == "reference" for v in targets):
                # Retain other occurrences of the originating role, including self-relations.
                remaining = dict(obj, fields=dict(obj.get("fields", {})))
                hit = int(path.rsplit("/", 1)[1])
                remaining["fields"][role] = [
                    v for i, v in enumerate(obj["fields"][role]) if i != hit
                ]
                omit = {other}
                if not remaining["fields"][role]:
                    omit.add(role)
                details = self.fields(remaining, omit)
                if context[2].get("fields"):
                    details.append(
                        Entry(
                            "Angaben zur Rolle · " + self.label(cls, role),
                            kind="group",
                            children=self.fields(context[2]),
                        )
                    )
                target_label = self.dataset.label(
                    roles[other].get("target") or "Objekt"
                )
                return [
                    Entry(
                        self.label(cls, other),
                        "Noch nicht geladen",
                        "relationship",
                        children=[
                            Entry(
                                "Angaben zur " + self.dataset.label(cls),
                                kind="group",
                                children=details
                                + (
                                    [
                                        Entry(
                                            "Angaben zur Rolle · "
                                            + self.label(cls, other),
                                            kind="group",
                                            children=self.fields(target),
                                        )
                                    ]
                                    if target.get("fields")
                                    else []
                                ),
                            )
                        ],
                        address=self.address(target),
                        association=obj,
                        group=self.dataset.label(cls) + " · " + self.label(cls, other),
                        group_key=(cls, other),
                        identity=identity + (other, i),
                        path=path,
                        target_label=target_label,
                    )
                    for i, target in enumerate(targets)
                ]
        group = self.dataset.label(cls)
        group_key = (cls,)
        if context and not is_association:
            owner, name, _, label_path = context
            definition = self.definition(owner["className"], name)
            association = definition.get("association")
            candidates = self.roles(association) if association else {}
            if owner is obj and len(candidates) == 2 and name in candidates:
                other = next(n for n in candidates if n != name)
                group = (
                    self.dataset.label(association)
                    + " · "
                    + (candidates[other].get("label") or other)
                )
                group_key = (association, other)
            else:
                group += " · " + label_path
                group_key = (cls, label_path)
        return [
            Entry(
                self.dataset.label(cls),
                self.dataset.title(obj),
                "reference",
                address=self.address(obj),
                obj=obj,
                association=obj if is_association else None,
                group=group,
                group_key=group_key,
                identity=identity,
                path=path,
            )
        ]

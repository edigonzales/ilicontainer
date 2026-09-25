#!/usr/bin/env python3
"""Write deterministic synthetic INTERLIS 2.4 park playground demo data."""
import argparse
from pathlib import Path
from xml.sax.saxutils import escape

NS = "http://www.interlis.ch/xtf/2.4/Parkanlage"


def field(name, value):
    return f"<p:{name}>{escape(str(value))}</p:{name}>"


def coord(x, y):
    return f"<g:coord><g:c1>{x:.3f}</g:c1><g:c2>{y:.3f}</g:c2></g:coord>"


def role_reference(name, tid):
    return f'<p:{name} ili:ref="{tid}"/>'


def structure(name, value):
    return f"<p:{name}>{value}</p:{name}>"


def object_(name, tid, body):
    return f'<p:{name} ili:tid="{tid}">{body}</p:{name}>\n'


def playground(name, x, y):
    ring = "".join(
        coord(a, b)
        for a, b in [(x, y), (x + 35, y), (x + 35, y + 28), (x, y + 28), (x, y)]
    )
    area = (
        f"<p:Flaeche><g:surface><g:exterior><g:polyline>{ring}</g:polyline>"
        "</g:exterior></g:surface></p:Flaeche>"
    )
    return object_(
        "Spielplatz",
        name[0],
        field("Name", name[1]) + area,
    )


PARKS = [
    ("park0", "Parkanlage am Bach", 2600000, 1200000),
    ("park1", "Wiesenpark", 2600100, 1200000),
    ("park2", "Dorfspielplatz", 2600200, 1200000),
]

DEVICES = [
    {
        "tid": "geraet0",
        "name": "Nestschaukel",
        "typ": "Schaukel",
        "zustand": "gut",
        "park": "park0",
        "xy": (2600010, 1200010),
        "checks": [
            (
                "2026-03-10",
                "inOrdnung",
                "Keine Mängel festgestellt.",
                [("Sitzhoehe", "0.42", "m")],
            )
        ],
    },
    {
        "tid": "geraet1",
        "name": "Rutschbahn",
        "typ": "Rutschbahn",
        "zustand": "pruefen",
        "park": "park0",
        "xy": (2600020, 1200016),
        "checks": [
            (
                "2026-03-11",
                "beobachten",
                "Oberflaeche bei der Leiter kontrollieren.",
                [("Roststelle", "1.00", "Stelle"), ("Rutschflaeche", "2.40", "m")],
            )
        ],
    },
    {
        "tid": "geraet2",
        "name": "Kletterturm",
        "typ": "Kletterturm",
        "zustand": "ersetzen",
        "park": "park1",
        "xy": (2600110, 1200011),
        "checks": [
            (
                "2026-03-12",
                "MassnahmeNoetig",
                "Eine Holzstrebe muss ersetzt werden.",
                [("Holzfeuchte", "21.50", "%")],
            ),
            (
                "2026-06-12",
                "beobachten",
                "Reparatur bei der naechsten Kontrolle nachpruefen.",
                [],
            ),
        ],
    },
    {
        "tid": "geraet3",
        "name": "Federwippe",
        "typ": "Wippe",
        "zustand": "gut",
        "park": "park1",
        "xy": (2600120, 1200018),
        "checks": [],
    },
    {
        "tid": "geraet4",
        "name": "Kleinkindschaukel",
        "typ": "Schaukel",
        "zustand": "pruefen",
        "park": "park2",
        "xy": (2600210, 1200010),
        "checks": [
            (
                "2026-03-14",
                "inOrdnung",
                "Ketten und Aufhaengung sind in Ordnung.",
                [("Kettenlaenge", "1.80", "m")],
            )
        ],
    },
    {
        "tid": "geraet5",
        "name": "Breite Rutsche",
        "typ": "Rutschbahn",
        "zustand": "gut",
        "park": "park2",
        "xy": (2600220, 1200018),
        "checks": [
            (
                "2026-03-15",
                "beobachten",
                "Randbereich auf Abnutzung beobachten.",
                [],
            )
        ],
    },
]


def controls(checks):
    result = []
    for date, outcome, note, measurements in checks:
        values = "".join(
            structure(
                "Messwert",
                field("Merkmal", name)
                + field("Wert", value)
                + field("Einheit", unit),
            )
            for name, value, unit in measurements
        )
        measurement_list = structure("Messwerte", values) if measurements else ""
        result.append(
            structure(
                "Kontrolle",
                field("Datum", date)
                + field("Ergebnis", outcome)
                + field("Bemerkung", note)
                + measurement_list,
            )
        )
    return structure("Kontrollen", "".join(result)) if checks else ""


def write(path):
    with path.open("w", encoding="utf-8", newline="\n") as out:
        out.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<ili:transfer xmlns:ili="http://www.interlis.ch/xtf/2.4/INTERLIS"'
            ' xmlns:g="http://www.interlis.ch/geometry/1.0"'
            f' xmlns:p="{NS}">'
            "<ili:headersection><ili:models><ili:model>Parkanlage</ili:model>"
            "</ili:models><ili:sender>IBX Parkanlage Demo</ili:sender>"
            "</ili:headersection><ili:datasection>"
            '<p:Park ili:bid="demo">\n'
        )
        for park in PARKS:
            out.write(playground(park, park[2], park[3]))
        for device in DEVICES:
            x, y = device["xy"]
            body = (
                field("Name", device["name"])
                + field("Typ", device["typ"])
                + field("Zustand", device["zustand"])
                + f"<p:Position>{coord(x, y)}</p:Position>"
                + role_reference("Spielplatz", device["park"])
                + controls(device["checks"])
            )
            out.write(object_("Spielgeraet", device["tid"], body))
        out.write("</p:Park></ili:datasection></ili:transfer>\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, default=Path(__file__).with_name("parkanlage.xtf")
    )
    args = parser.parse_args()
    write(args.output)

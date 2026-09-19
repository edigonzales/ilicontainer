#!/usr/bin/env python3
"""Deterministic synthetic INTERLIS 2.4 FULL data; no network dependency."""
import argparse
from pathlib import Path
from xml.sax.saxutils import escape

NS = "http://www.interlis.ch/xtf/2.4/Quartier"


def field(name, value):
    return f"<q:{name}>{escape(str(value))}</q:{name}>"


def coord(x, y):
    return f"<g:coord><g:c1>{x:.3f}</g:c1><g:c2>{y:.3f}</g:c2></g:coord>"


def obj(cls, tid, body):
    ident = f' ili:tid="{tid}"' if tid else ""
    return f"<q:{cls}{ident}>{body}</q:{cls}>\n"


def ref(role, tid):
    return f'<q:{role} ili:ref="{tid}"/>'


def write(path, size):
    with path.open("w") as out:
        out.write(
            f'<?xml version="1.0" encoding="UTF-8"?>\n<ili:transfer xmlns:ili="http://www.interlis.ch/xtf/2.4/INTERLIS" xmlns:g="http://www.interlis.ch/geometry/1.0" xmlns:q="{NS}"><ili:headersection><ili:models><ili:model>Quartier</ili:model></ili:models><ili:sender>IBX reproducible demo</ili:sender></ili:headersection><ili:datasection>\n'
        )
        out.write('<q:Unterhalt ili:bid="leer"/>\n<q:Unterhalt ili:bid="nord">\n')
        for i in range(6):
            out.write(
                obj(
                    "Organisation",
                    f"org{i}",
                    field(
                        "Name",
                        [
                            "Werkhof",
                            "Stadtgrün",
                            "Hausdienst",
                            "Tiefbau",
                            "Spielplatzteam",
                            "Beleuchtung",
                        ][i],
                    )
                    + field("Telefon", f"032 555 01 {i:02}"),
                )
            )
        for i in range(8):
            out.write(
                obj(
                    "Auftrag",
                    f"auftrag{i}",
                    field("Name", f"Quartierpflege {2026}-{i+1:03}")
                    + field("Datum", "2026-09-12")
                    + field("Status", "geplant"),
                )
            )
        for i in range(size):
            columns = 6 if size == 24 else 500
            x = 2600000 + (i % columns) * 40
            y = 1200000 + (i // columns) * 50
            body = (
                field("Name", f"Haus am Park {i+1}")
                + field("Nummer", i % 9999 + 1)
                + field("Nutzung", "Wohnen")
            )
            ring = "".join(
                coord(a, b)
                for a, b in [(x, y), (x + 20, y), (x + 20, y + 15), (x, y + 15), (x, y)]
            )
            body += f"<q:Grundriss><g:surface><g:exterior><g:polyline>{ring}</g:polyline></g:exterior></g:surface></q:Grundriss><q:Beschriftung>{coord(x+10,y+7)}</q:Beschriftung>"
            if i % 3 != 2:
                controls = []
                for k in range(2):
                    measurement = (
                        field("Bezeichnung", "Rissbreite")
                        + field("Wert", "0.123456")
                        + field("Einheit", "mm")
                    )
                    control = (
                        field("Datum", f"2026-09-{10+k:02}")
                        + field("Ergebnis", "beobachten")
                        + field("Bemerkung", "Bei der nächsten Begehung prüfen")
                        + f"<q:Messungen><q:Messung>{measurement}</q:Messung></q:Messungen>"
                        + ref("Kontrollstelle", f"org{i%6}")
                        + f"<q:Standort>{coord(x+2,y+2)}</q:Standort>"
                    )
                    controls.append(f"<q:Kontrolle>{control}</q:Kontrolle>")
                body += "<q:Kontrollen>" + "".join(controls) + "</q:Kontrollen>"
            body += ref(
                "Auftrag", f"auftrag{(0 if i<10000 else i%7+1) if size>1000 else i%8}"
            )
            out.write(obj("Gebaeude", f"g{i}", body))
        out.write('</q:Unterhalt><q:Unterhalt ili:bid="sued">\n')
        for i in range(12):
            cls = "Spielplatz" if i < 6 else "Technik"
            body = (
                field("Name", f'{"Spielplatz" if i<6 else "Brunnen"} {i+1}')
                + f"<q:Position>{coord(2600010+i*40,1199960)}</q:Position>"
            )
            body += (
                field("Altersgruppe", "3 bis 12 Jahre")
                if i < 6
                else field("Typ", "Brunnen")
            )
            body += ref("Auftrag", f"auftrag{i%8}")
            out.write(obj(cls, f"anlage{i}", body))
        for i in range(24):
            out.write(
                obj(
                    "Zustaendigkeit",
                    None,
                    ref("Objekt", f"g{i%size}")
                    + ref("Organisation", f"org{i%6}")
                    + field("Funktion", "verantwortlich")
                    + field("GueltigAb", "2026-01-01"),
                )
            )
        for a, b in [(0, 1), (1, 0)]:
            out.write(
                obj(
                    "Folgeauftrag",
                    None,
                    ref("Vorher", f"auftrag{a}") + ref("Nachher", f"auftrag{b}"),
                )
            )
        out.write("</q:Unterhalt></ili:datasection></ili:transfer>\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--size", type=int, default=24)
    p.add_argument(
        "--output", type=Path, default=Path(__file__).with_name("quartier.xtf")
    )
    a = p.parse_args()
    write(a.output, a.size)

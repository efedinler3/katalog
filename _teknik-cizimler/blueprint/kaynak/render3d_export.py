"""CAD modellerini parca parca STL'e aktarir (three.js ustten gercekci gorunus icin).
Cikti: _render3d/<kod>/<parca>.stl + parts.json
"""
import json
import os
import sys

from build123d import export_stl

import families_cad as FC
from urunler import P

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "_render3d")


RAD = {"rubber": 1.2, "marks": 0, "top_marks": 0, "fasteners": 0.6}


def valid(s):
    v = s.is_valid
    return v() if callable(v) else v


def soften(name, shape):
    """Gercek parcadaki gibi kenar radyusu: buyukten kucuge dener, olmazsa parcayi oldugu gibi birakir."""
    r0 = RAD.get(name, 0.9)
    if not r0:
        return shape
    for r in (r0, r0 * 0.6, r0 * 0.35):
        try:
            out = shape.fillet(r, shape.edges())
            if valid(out):
                return out
        except Exception:
            pass
        try:                                   # tum kenarlar olmuyorsa: yalnizca duz kenarlar
            out = shape.fillet(r, [e for e in shape.edges() if e.geom_type.name == "LINE"])
            if valid(out):
                return out
        except Exception:
            pass
    print("  radyus yok:", name)
    return shape


def export(code):
    p = dict(P[code], code=code)
    parts = FC.builder(p["cad_module"])(**p["cad_args"])
    parts.pop("_hatch", None)
    d = os.path.join(OUT, code)
    os.makedirs(d, exist_ok=True)
    names = []
    for name, shape in parts.items():
        fn = f"{name}.stl"
        shape = soften(name, shape)
        export_stl(shape, os.path.join(d, fn), tolerance=0.03, angular_tolerance=0.1)
        names.append(name)
    with open(os.path.join(d, "parts.json"), "w", encoding="utf-8") as fh:
        json.dump(names, fh)
    print(code, names)


if __name__ == "__main__":
    for c in sys.argv[1:]:
        export(c)

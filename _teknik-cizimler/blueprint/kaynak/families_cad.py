"""3B CAD modelinden teknik cizim: on / ust / izometrik projeksiyon + olculer (families3 olcu fonksiyonlari)."""
import hashlib
import os
import pickle

from build123d import Compound

import cad_kit as CK
from families3 import front_dims, plan_dims
from parts import T

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "_cad-onbellek")
BUILDERS = {}


def builder(module):
    import importlib
    name = module.replace(".py", "")
    if name not in BUILDERS:
        BUILDERS[name] = importlib.import_module(name).model
    return BUILDERS[name]


def projections(p):
    os.makedirs(CACHE, exist_ok=True)
    args = p["cad_args"]
    src_sig = "".join(open(os.path.join(HERE, f), encoding="utf-8").read() for f in ("cad_kit.py", p["cad_module"]))
    key = hashlib.md5((repr(sorted(args.items())) + repr(p.get("iso_args")) + src_sig).encode()).hexdigest()[:16]
    cp = os.path.join(CACHE, f"{p['code']}-{key}.pkl")
    if os.path.exists(cp):
        with open(cp, "rb") as fh:
            return pickle.load(fh)
    parts = builder(p["cad_module"])(**args)
    hatch = parts.pop("_hatch", {}) or {}
    comp = Compound(children=list(parts.values()))
    out = {v: CK.project(comp, v) for v in ("front", "top")}
    if p.get("iso_args"):                               # izometrik icin ayri (or. kesitsiz) model
        ip = builder(p["cad_module"])(**dict(args, **p["iso_args"]))
        ip.pop("_hatch", None)
        out["iso"] = CK.project(Compound(children=list(ip.values())), "iso")
    else:
        out["iso"] = CK.project(comp, "iso")
    out["hatch"] = [(loops, pat) for name, pat in hatch.items() for loops in CK.section_loops(parts[name])]
    with open(cp, "wb") as fh:
        pickle.dump(out, fh)
    return out


def bbox(polys):
    xs = [q[0] for pl in polys for q in pl]
    ys = [q[1] for pl in polys for q in pl]
    return min(xs), min(ys), max(xs), max(ys)


def draw_cad(f, pl, iso, p, L):
    pr = projections(p)
    k = 1.0 / f.s
    t = T[p["thread"]]
    tang_v = p.get("tangent", "thin")
    tang_of = (lambda v: tang_v.get(v)) if isinstance(tang_v, dict) else (lambda v: tang_v)
    for loops, pat in pr.get("hatch", []):
        f.hatch_loops(loops, pat)
    for view, V in (("front", f), ("top", pl)):
        tang = tang_of(view)
        vis, _, smooth = pr[view]
        for poly in vis:
            V.poly(poly, "mid", False)
        if tang:
            for poly in smooth:
                V.poly(poly, tang, False)
    # eksenler
    _, ybot, _, ytop = bbox(pr["front"][0])             # eksen: modelin on gorunus sinirlari
    f.line(0, ybot - 3 * k, 0, ytop + 4 * k, "cen")
    Lb, W, C = p["L"], p["W"], p.get("C")
    pl.cline_h(-Lb / 2 - 4 * k, Lb / 2 + 4 * k, 0)
    pl.cline_v(0, -W / 2 - 4 * k, W / 2 + 4 * k)
    if C:
        for sx in (-1, 1):
            pl.cline_v(sx * C / 2, -W / 2 + 4, W / 2 - 4)
    front_dims(f, p, L, k, t)
    plan_dims(pl, p, L, k)
    # izometrik
    vis, _, smooth = pr["iso"]
    x0, y0, x1, y1 = bbox(vis)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for poly in vis:
        iso.poly([(u - cx, v - cy) for (u, v) in poly], "thin", False)
    if tang_of("iso"):
        for poly in smooth:
            iso.poly([(u - cx, v - cy) for (u, v) in poly], "thin", False)
    return (x1 - x0, y1 - y0)

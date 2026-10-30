"""MT ailesi 3B modeli (MT1 / MT2 / MT3): sitedeki dmt1-3 cizim render'larindan.

Kalin taban flansi (uclari duz kesik, ortasi W capli daireye teget capraz kenarli plaka), ustte kesik koni kaucuk
govde (alt cap 0,97 W, ust cap 0,925 W, yukseklik = flans kalinligi; dmt2 yatay olcekle olculdu), uzerinde konik
canak (ust / alt cap = cup), saplama: alt somun + destek pulu (pul alti = destek yuksekligi), bosluk, ust somun.
Olculer urunler.py ile ayni (L, W, C, flans, destek, kanal, cup).
"""
from build123d import Axis, Circle, Pos, Rot, RectangleRounded, SlotCenterToCenter, Solid, extrude, make_hull

import cad_kit as CK
from parts import T

SPEC = {
    "MT1": dict(L=140.0, W=68.0, C=100.0, flange=22.0, support=70.0, upper_gap=10.0, slot=(12.5, 28.0),
                thread="M16", cup=(40.0, 32.0), end_half=17.7),
    "MT2": dict(L=166.0, W=98.0, C=133.0, flange=25.0, support=75.0, upper_gap=10.0, slot=(13.0, 28.0),
                thread="M16", cup=(53.0, 43.0), end_half=25.5),
    "MT3": dict(L=184.0, W=105.0, C=140.0, flange=27.0, support=90.0, upper_gap=12.0, slot=(16.0, 33.0),
                thread="M24", cup=(58.0, 46.0), end_half=27.0),
}


def revolve_z(pts, radii):
    """(r, z) profili Z ekseni etrafinda dondurur."""
    face = CK.rounded_face(pts, radii)
    return Rot(90, 0, 0) * Solid.revolve(face, 360, Axis.Y)


def model(code="MT2"):
    sp = SPEC[code]
    t = T[sp["thread"]]
    d = t["d"]
    L, W, C, fl = sp["L"], sp["W"], sp["C"], sp["flange"]
    parts = {}
    # --- taban flansi
    ex = L / 2 - C / 2
    end = RectangleRounded(2 * ex, 2 * sp["end_half"], 6.0)
    sk = Pos(-C / 2, 0) * end + Pos(C / 2, 0) * end + Circle(W / 2)
    base = extrude(make_hull(sk.edges()), amount=fl)
    sw, sl = sp["slot"]
    for sx in (-1, 1):
        base = base - Pos(sx * C / 2, 0, 0) * extrude(SlotCenterToCenter(sl - sw, sw, rotation=90), amount=80,
                                                      both=True)
    parts["base"] = base
    # --- kesik koni kaucuk govde
    rb, rt, z1 = 0.971 * W / 2, 0.925 * W / 2, 2 * fl
    parts["rubber"] = revolve_z([(0, fl), (rb, fl), (rt, z1), (0, z1)], [0, 0, 0, 0])
    # --- konik canak (ust duz halka + ortada sig cukur)
    ct, cb = sp["cup"][0] / 2, sp["cup"][1] / 2
    hc = 0.38 * fl
    ri = 0.31 * sp["cup"][0]                             # dmt2 ust gorunus ic daire ~ 32,5 / 53
    zc = z1
    parts["cup"] = revolve_z([(d / 2 + 0.5, zc), (cb, zc), (ct, zc + hc), (ri, zc + hc), (d / 2 + 0.5, zc + hc - 3.0)],
                             [0, 0, 0, 0, 0])
    # --- saplama + somunlar
    sup, gap = sp["support"], sp["upper_gap"]
    top = sup + t["wt"] + gap + t["h"] + 1.6 * d
    fast = CK.stud3d(d, z1 - 10.0, top, ch=1.5)
    fast = fast + CK.hex_nut(t["af"], t["h"], d, sup - t["h"])
    fast = fast + CK.washer3d(t["wd"], d + 1.0, t["wt"], sup)
    fast = fast + CK.hex_nut(t["af"], t["h"], d, sup + t["wt"] + gap)
    parts["fasteners"] = fast
    return parts

"""VV ailesi 3B modeli (VV1 = Ellebogen GT-S olculeri, VV2 = GT-M, VV3 = Novibrasyon): sahibin VV cizimlerinden
olculen govde profili (sahibin cizimleri ust uste olculdu), kesitlerden loft edilmis kaucuk govde, celik ust pul,
ic burc + flans + dis kabuk, on yarida eliptik kismi kesit penceresi (celik kesitler taranir, saplama kesilmez).

Govde profili (x yari genislik, z): taban -> bel -> alt cikinti -> kenar ucu (rim) -> ust daire.
y yonu yari boyutlari: kenarda W/2, aradaki kesitler ayni oranla. Butun kesitler ayni topolojide (yuvarlatilmis
dikdortgen) oldugundan loft dikisleri teget-surekli olur; cizimde gorunmez.
"""
import math

from build123d import (Align, Axis, Box, Circle, Cylinder, Ellipse, Plane, Pos, Rot, SlotCenterToCenter, Solid,
                       extrude, loft, make_hull, RectangleRounded)

import cad_kit as CK

SPEC = {
    "VV1": dict(L=120.0, W=60.5, tp=3.0, C=100.0, H=43.0, min_h=68.5, total=125.0, d=16.0, tip=(10.0, 16.0),
                body_top=39.9, top_r=29.3, washer=(54.0, 3.1),
                prof=[(29.6, None), (26.9, 12.5), (32.2, 17.3), (37.0, 17.5), (40.2, 21.4)],
                flange=None, holes=(("slot", 11.0, 14.0, "v"), ("slot", 11.0, 14.0, "v")), ear_flat=27.6,
                nut_af=24.0, nut_h=13.0, jam_h=8.0, wd=30.0, wt=2.5),
    "VV2": dict(L=184.0, W=82.0, tp=4.0, C=140.0, H=55.0, min_h=78.5, total=128.0, d=16.0, tip=(10.0, 10.0),
                body_top=51.4, top_r=36.0, washer=(54.0, 3.6),
                prof=[(37.3, None), (32.1, 18.5), (33.3, 21.0), (50.1, 26.1)],
                flange=(52.4, 37.0, 21.0, 26.1), holes=(("slot", 13.0, 30.0, "v"), ("slot", 13.0, 22.0, "h")),
                ear_flat=32.6, nut_af=24.0, nut_h=13.0, jam_h=8.0, wd=30.0, wt=2.5),
    "VV3": dict(L=228.0, W=112.0, tp=5.0, C=182.0, H=70.0, min_h=100.0, total=170.0, d=20.0, tip=(16.0, 16.0),
                body_top=64.7, top_r=48.0, washer=(88.8, 5.3),
                prof=[(47.9, None), (43.3, 20.6), (52.4, 28.3), (59.3, 28.5), (64.7, 34.1)],
                flange=None, holes=(("slot", 18.0, 34.0, "h"), ("slot", 18.0, 34.0, "v")), ear_flat=44.4,
                nut_af=30.0, nut_h=16.0, jam_h=10.0, wd=37.0, wt=3.0),
}


def barrel_wire(hx, hy, Rb, rc):
    """Fici kesit: on/arka duz (y = +-hy), yanlar Rb yaricapli bombe (x ucu hx), koseler rc yaricapli.
    8 kenar (cizgi, yay, yay, yay, cizgi, yay, yay, yay): butun kesitlerde ayni topoloji."""
    from build123d import Edge, Vector, Wire
    cx = hx - Rb                                         # sag bombe merkezi (cx, 0)
    xf = cx + math.sqrt((Rb - rc) ** 2 - (hy - rc) ** 2)  # kose yayi merkezi (xf, hy - rc)
    ux, uy = xf - cx, hy - rc
    ul = math.hypot(ux, uy)
    tc = (cx + Rb * ux / ul, Rb * uy / ul)               # kose yayi - bombe teget noktasi
    fm = (xf + rc * math.cos(math.atan2(uy, ux) / 2 + math.pi / 4), 0)
    am = math.atan2(uy, ux) / 2 + math.pi / 4            # kose yayi orta acisi (90 ile bombe acisi arasi)
    fm = (xf + rc * math.cos(am), hy - rc + rc * math.sin(am))
    V = lambda x, y: Vector(x, y, 0)
    e = []
    for sy in (1, -1):
        sgn = 1 if sy == 1 else -1
        if sy == 1:
            e.append(Edge.make_line(V(-xf, hy), V(xf, hy)))
            e.append(Edge.make_three_point_arc(V(xf, hy), V(*fm), V(*tc)))
            e.append(Edge.make_three_point_arc(V(*tc), V(hx, 0), V(tc[0], -tc[1])))
            e.append(Edge.make_three_point_arc(V(tc[0], -tc[1]), V(fm[0], -fm[1]), V(xf, -hy)))
        else:
            e.append(Edge.make_line(V(xf, -hy), V(-xf, -hy)))
            e.append(Edge.make_three_point_arc(V(-xf, -hy), V(-fm[0], -fm[1]), V(-tc[0], -tc[1])))
            e.append(Edge.make_three_point_arc(V(-tc[0], -tc[1]), V(-hx, 0), V(-tc[0], tc[1])))
            e.append(Edge.make_three_point_arc(V(-tc[0], tc[1]), V(-fm[0], fm[1]), V(-xf, hy)))
    return Wire(e)


def corner_angle(hx, hy, Rb, rc):
    """Kose yayi ile bombe yayinin teget noktasinin acisi (bombe merkezinden)."""
    cx = hx - Rb
    xf = cx + math.sqrt((Rb - rc) ** 2 - (hy - rc) ** 2)
    return math.atan2(hy - rc, xf - cx)


def section(z, hx, hy, Rb, th):
    """Teget acisi th sabit tutulan fici kesit: butun kesitlerde ayni aci -> loft dikisleri tam G1."""
    from build123d import Face
    rc = (hy - Rb * math.sin(th)) / (1 - math.sin(th))
    return Plane.XY.offset(z) * Face(barrel_wire(hx, hy, Rb, rc))


def hole_cut(spec, cx):
    kind, w, ln, o = spec[:4]
    if kind == "round":
        return Pos(cx, 0, 0) * Cylinder(w / 2, 40)
    rot = 90 if o == "v" else 0
    return Pos(cx, 0, 0) * extrude(SlotCenterToCenter(ln - w, w, rotation=rot), amount=40, both=True)


def model(code="VV1", section_cut=True):
    sp = SPEC[code]
    L, W, tp, C, H, d = sp["L"], sp["W"], sp["tp"], sp["C"], sp["H"], sp["d"]
    parts = {}
    # --- taban plakasi: kulak daireleri + govde alti dikdortgen, gercek yaylarla dis bukey zarf
    re = (L - C) / 2
    sk = Pos(-C / 2, 0) * Circle(re) + Pos(C / 2, 0) * Circle(re) + RectangleRounded(2 * sp["ear_flat"], W, 5.0)
    plate = extrude(make_hull(sk.edges()), amount=tp)
    for spec, cx in ((sp["holes"][0], -C / 2), (sp["holes"][1], C / 2)):
        plate = plate - hole_cut(spec, cx)
    parts["plate"] = plate
    # --- kaucuk govde: ayni topolojide kesitlerden duz (ruled) loft
    prof = sp["prof"]
    rim_x = prof[-1][0]
    ky = (W / 2 - 0.3) / rim_x
    if sp["flange"]:                                    # VV2: lastik, celik cercevenin on/arka kenarinin icinde
        ky = (sp["flange"][1] - 1.5) / rim_x
    th = corner_angle(rim_x, rim_x * ky, 2.31 * rim_x, 0.2 * rim_x)   # sahip cizimi VV1: bombe R 2,31 x, kose 0,2 x
    secs, zs = [], []
    for (x, z) in prof:
        zz = tp if z is None else z
        if zs and zz <= zs[-1] + 0.05:
            zz = zs[-1] + 0.2
        zs.append(zz)
        secs.append(section(zz, x, x * ky, 2.31 * x, th))
    zt, R = sp["body_top"], sp["top_r"]
    secs.append(section(zt - 2.5, R, R - 0.4, R, th))
    secs.append(section(zt, R - 2.2, R - 2.6, R - 2.2, th))
    body = loft(secs, ruled=True)
    # --- 4 capraz kaburga (egim yuzeyinde, ust pul cemberinden kenara): govdenin 1 mm buyutulmus kopyasi ile
    big = []
    for (x, z), zz in zip(prof, zs):
        big.append(section(zz + 0.8, x + 1.0, x * ky + 1.0, 2.31 * x + 1.0, th))
    big.append(section(zt - 2.5 + 0.8, R + 1.0, R - 0.4 + 1.0, R + 1.0, th))
    big.append(section(zt - 0.3, R - 1.2, R - 1.6, R - 1.2, th))
    body_big = loft(big[1:], ruled=True)
    r0, r1, rw = sp["washer"][0] / 2 - 1.0, 0.92 * rim_x, 0.03 * rim_x
    ribs = None
    for a in (45, 135, 225, 315):
        z_rim = zs[-1]
        slab = Rot(0, 0, a) * Pos((r0 + r1) / 2, 0, z_rim + 0.3) * Box(r1 - r0, rw, zt, align=(Align.CENTER, Align.CENTER, Align.MIN))
        rib = (body_big & slab) - body
        ribs = rib if ribs is None else ribs + rib
    body = body + ribs
    # --- ic parcalar (donel): burc + flans, dis kabuk
    rc = 0.855 * d
    core_z0 = 0.26 * zt
    core = Pos(0, 0, core_z0) * Cylinder(rc, zt - core_z0 - 0.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    waist_hy = min(x for (x, z) in prof) * ky             # flans lastik belinin icinde kalmali (VV1 kesit: R ~ 18)
    fl = Pos(0, 0, core_z0) * Cylinder(min(1.32 * d, 0.85 * waist_hy), 0.087 * zt,
                                      align=(Align.CENTER, Align.CENTER, Align.MIN))
    bore = Pos(0, 0, core_z0 + 1.0) * Cylinder(d / 2, zt, align=(Align.CENTER, Align.CENTER, Align.MIN))
    inner = (core + fl) - bore
    sx_, sz_ = rim_x / 64.7, zt / 64.7                  # dis kabuk: VV3 olcumunden normalize
    shell_out = [(22.2, 47.4), (29.9, 45.9), (34.9, 41.3), (38.4, 32.6), (38.6, 24.5)]
    shell_in = [(35.0, 24.5), (34.9, 31.0), (31.9, 39.6), (28.4, 42.2), (22.6, 43.6)]
    prof2 = [(x * sx_, z * sz_) for (x, z) in shell_out + shell_in]
    shell = Rot(90, 0, 0) * Solid.revolve(CK.rounded_face(prof2, [0.8] * len(prof2)), 360, Axis.Y)
    body = body - inner - shell - bore
    flange = None
    if sp["flange"]:
        fx, fy, f0, f1 = sp["flange"]
        flange = Pos(0, 0, f0) * extrude(RectangleRounded(2 * fx, 2 * fy, 6.0), amount=f1 - f0)
        flange = flange - Cylinder(0.62 * rim_x, 200)     # gomulu celik cerceve: ortasi delik (kesitte gorunmez)
        body = body - flange
    wash = Pos(0, 0, zt) * Cylinder(sp["washer"][0] / 2, H - zt, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # --- saplama + somunlar (kesilmez)
    tip = sp["tip"]
    stud = Pos(0, 0, core_z0 + 1.0) * Cylinder(d / 2, sp["total"] - tip[1] - core_z0 - 1.0,
                                             align=(Align.CENTER, Align.CENTER, Align.MIN))
    z_tip = sp["total"] - tip[1]
    tipb = Pos(0, 0, z_tip) * Box(tip[0], tip[0], tip[1], align=(Align.CENTER, Align.CENTER, Align.MIN))
    tipb = tipb & (Pos(0, 0, z_tip) * Cylinder(d / 2, tip[1], align=(Align.CENTER, Align.CENTER, Align.MIN)))
    fast = stud + tipb
    fast = fast + CK.hex_nut(sp["nut_af"], sp["jam_h"], d, H)
    fast = fast + CK.hex_nut(sp["nut_af"], sp["nut_h"], d, sp["min_h"] - sp["wt"] - sp["nut_h"])
    fast = fast + CK.washer3d(sp["wd"], d + 1.0, sp["wt"], sp["min_h"] - sp["wt"])
    top_nut = sp["total"] - tip[1] - 0.45 * d
    fast = fast + CK.hex_nut(sp["nut_af"], sp["nut_h"], d, top_nut - sp["nut_h"])
    fast = fast + CK.washer3d(d * 1.6, d + 0.4, 3.4, top_nut - sp["nut_h"] - 3.4)
    # --- kismi kesit penceresi: on yari (y < 0), elips
    hatch = {}
    if section_cut:
        a, b, zc = 0.609 * rim_x, 0.335 * zt, 0.51 * zt
        win = Pos(0, 0, zc) * Rot(90, 0, 0) * extrude(Ellipse(a, b), amount=W)
        body = body - win
        inner = inner - win
        shell = shell - win
        hatch = {"inner": "h45", "shell": "h135"}
        if flange is not None:
            flange = flange - win
            hatch["flange"] = "h135"
    parts["rubber"] = body
    parts["inner"] = inner
    parts["shell"] = shell
    if flange is not None:
        parts["flange"] = flange
    parts["washer"] = wash
    parts["fasteners"] = fast
    parts["_hatch"] = hatch
    return parts

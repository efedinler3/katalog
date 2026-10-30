"""Blok takoz 3B modeli (400 / 450 / 500 / 600): dokum govde + kulaklar + alt tunel (kaucuk takoz) + ust kaucuk.

Kaynaklar (sitedeki cizimler, assets/src):
  400, 500  d400 / d500 cizim render'i: on gorunus 3x buyutulup olculdu; yatay olcek 93 govde olcusunden,
            dikey olcek H (taban somunu ustu) olcusunden. Govde ustte 93 genis, ortada hafif ice egik duvar, kulak ustune
            ic bukey kavis; ustte V kanalli kaucuk baslik; flansli somun.
  450       d450 fotografi: kutu govde (ust bant bacaklardan genis, ust kenarlar pahli), duz kaucuk yastik.
  600       d600 fotografi (perspektif): yamuk govde, kalin kulaklar, ustte kare kaucuk yastik.
Olculen degerler cizimdeki olculere (L, W, H, min. yukseklik, toplam, kanal) birebir uyar; olcusuz ayrintilar oranla.
"""
from build123d import Align, Cylinder, Plane, Pos, RectangleRounded, SlotCenterToCenter, extrude, loft, make_hull

import cad_kit as CK
from parts import T

SPEC = {
    "400": dict(style="v", L=166.0, W=66.0, C=127.0, thread="M20", H=80.0, min_h=120.0, total=170.0, proj=23.0,
                ear_h=20.2, ear_hw=24.0, slot=(14.0, 28.0), top_hw=46.5, wall=(43.8, 26.4), z_top=57.7, fillet=5.0,
                tun=(33.0, 23.8, 2.6, 3.0), nose=(27.3, 2.4),
                cap=[(35.6, 0.0), (24.4, 5.9), (32.5, 10.2), (33.6, 13.4), (32.8, 13.7)], cap_off=14.9, cap_r=4.0),
    "500": dict(style="v", L=166.0, W=93.0, C=127.0, thread="1in", H=90.0, min_h=130.0, total=190.0, proj=23.0,
                ear_h=22.7, ear_hw=24.6, slot=(14.0, 28.0), top_hw=46.5, wall=(43.4, 29.4), z_top=64.9, fillet=5.5,
                tun=(32.4, 26.8, 2.9, 3.0), nose=(27.3, 2.4),
                cap=[(35.6, 0.0), (24.2, 6.4), (32.2, 10.4), (33.0, 14.7), (32.2, 15.1)], cap_off=3.1, cap_r=4.0),
    "450": dict(style="box", L=165.0, W=85.0, C=127.0, thread="M20", H=72.0, min_h=120.0, total=170.0, proj=3.0,
                ear_h=21.0, ear_hw=29.0, slot=(13.0, 20.0), leg_hw=46.5, box_hw=56.0, box_z0=14.8, z_top=58.3,
                chamfer=4.0, tun=(36.5, 18.9, 2.0, 3.0), nose=None, pad=(40.8, 33.0, 2.0)),
    "600": dict(style="trap", L=166.0, W=93.0, C=127.0, thread="M24", H=95.0, min_h=None, total=190.0, proj=3.0,
                ear_h=20.0, ear_hw=24.0, slot=(14.0, 28.0), base_hw=50.0, top_hw=42.0, z_top=76.0, fillet=4.0,
                tun=(25.0, 24.0, 2.0, 3.0), nose=None, step=(41.0, 3.0), pad=(43.0, 41.0, 2.0)),
}


def plan_clip(sp, hw):
    """Kulaklar + govde tabani: gercek yayli dis bukey zarf (ust gorunusteki capraz kenarlar)."""
    L, W, C = sp["L"], sp["W"], sp["C"]
    ex = L / 2 - C / 2                                   # kanal merkezinden kulak ucuna
    ear = RectangleRounded(2 * ex, 2 * sp["ear_hw"], 7.0)
    sk = Pos(-C / 2, 0) * ear + Pos(C / 2, 0) * ear + RectangleRounded(2 * hw, W, 8.0)
    return make_hull(sk.edges())


def housing_profile(sp):
    """On gorunus govde profili (x, z) + kose yaricaplari."""
    eh, zt = sp["ear_h"], sp["z_top"]
    st = sp["style"]
    if st == "v":
        ht = sp["top_hw"]
        xn, zn = sp["wall"]
        k = (ht - xn) / (zt - zn)                        # duvar egimi (ustte genis)
        xw = xn - k * (zn - eh)
        xb = xw + sp["fillet"] + 3.0
        pts = [(-xb, 0), (-xb, eh), (-xw, eh), (-ht, zt), (ht, zt), (xw, eh), (xb, eh), (xb, 0)]
        rr = [0, 0, sp["fillet"], 0.8, 0.8, sp["fillet"], 0, 0]
    elif st == "box":
        lg, bx, z0, ch = sp["leg_hw"], sp["box_hw"], sp["box_z0"], sp["chamfer"]
        pts = [(-lg, 0), (-lg, z0), (-bx, z0), (-bx, zt - ch), (-bx + ch, zt), (bx - ch, zt), (bx, zt - ch),
               (bx, z0), (lg, z0), (lg, 0)]
        rr = [0, 1.0, 1.0, 0.6, 0.6, 0.6, 0.6, 1.0, 1.0, 0]
    else:                                                # yamuk
        bw, ht = sp["base_hw"], sp["top_hw"]
        xb = bw + sp["fillet"] + 3.0
        pts = [(-xb, 0), (-xb, eh), (-bw, eh), (-ht, zt), (ht, zt), (bw, eh), (xb, eh), (xb, 0)]
        rr = [0, 0, sp["fillet"], 2.0, 2.0, sp["fillet"], 0, 0]
    return pts, rr


def rr_section(z, hx, hy, r):
    r = max(0.6, min(r, hx * 0.95, hy * 0.95))
    return Plane.XY.offset(z) * RectangleRounded(2 * hx, 2 * hy, r)


def model(code="400"):
    sp = SPEC[code]
    t = T[sp["thread"]]
    d = t["d"]
    L, W, C, eh, zt, H = sp["L"], sp["W"], sp["C"], sp["ear_h"], sp["z_top"], sp["H"]
    parts = {}
    # --- dokum govde
    pts, rr = housing_profile(sp)
    if sp["style"] == "box":                             # kutu: ust bant tam derinlikte, kulak plakasi bacak genisliginde
        hw_plan = sp["leg_hw"]
        clip = extrude(RectangleRounded(2 * sp["box_hw"], W, 6.0), amount=zt + 5)
    else:
        hw_plan = max(abs(p[0]) for p in pts)
        clip = extrude(plan_clip(sp, hw_plan), amount=zt + 5)
    house = CK.prism_xz(CK.rounded_face(pts, rr), W) & clip
    plate = extrude(plan_clip(sp, hw_plan), amount=eh)
    body = house + plate
    tw, tz, tz0, tr = sp["tun"]
    tunnel = CK.prism_xz(CK.rounded_face([(-tw, -5), (tw, -5), (tw, tz), (-tw, tz)], [0, 0, tr, tr]), W + 40)
    body = body - tunnel
    sw, sl = sp["slot"]
    for sx in (-1, 1):
        body = body - Pos(sx * C / 2, 0, 0) * extrude(SlotCenterToCenter(sl - sw, sw, rotation=90), amount=80,
                                                      both=True)
    parts["housing"] = body
    # --- tunel kaucugu (+ on/arka cikinti)
    rub = CK.prism_xz(CK.rounded_face([(-tw + 0.3, tz0), (tw - 0.3, tz0), (tw - 0.3, tz - 0.3), (-tw + 0.3, tz - 0.3)],
                                      [tr, tr, tr, tr]), W - 1.0)
    if sp.get("nose"):
        nw, ne = sp["nose"]
        rub = rub + CK.prism_xz(CK.rounded_face([(-nw, tz0 + 2), (nw, tz0 + 2), (nw, tz - 2), (-nw, tz - 2)],
                                                [2.5, 2.5, 2.5, 2.5]), W + 2 * ne)
    parts["tunnel_rubber"] = rub
    # --- ust kaucuk
    st = sp["style"]
    if st == "v":
        secs = []
        hx0 = sp["cap"][0][0]
        for (hx, dz) in sp["cap"]:
            secs.append(rr_section(zt + dz, hx, hx - sp["cap_off"], sp["cap_r"] + hx - hx0))
        cap = loft(secs, ruled=True)
        z_cap = zt + sp["cap"][-1][1]
    else:
        px, py, pc = sp["pad"]
        z0 = zt
        secs = []
        if sp.get("step"):
            s_hx, s_h = sp["step"]
            secs += [rr_section(z0, s_hx, s_hx - (px - py), 5.0), rr_section(z0 + s_h, s_hx, s_hx - (px - py), 5.0)]
            cap0 = loft(secs, ruled=True)
            z0 += s_h
        else:
            cap0 = None
        secs = [rr_section(z0, px, py, 6.0), rr_section(H - pc, px, py, 6.0), rr_section(H, px - pc, py - pc, 6.0 - pc)]
        cap = loft(secs, ruled=True)
        if cap0 is not None:
            cap = cap + cap0
        z_cap = H
    parts["cap"] = cap
    # --- saplama + somunlar
    tot = sp["total"]
    fast = CK.stud3d(d, zt - 12.0, tot, ch=1.2)
    if st == "v":
        fast = fast + CK.hex_nut(t["af"], H - z_cap, d, z_cap)            # flansli taban somunu (ustu = H)
        z = H
    else:
        fast = fast + CK.washer3d(t["wd"], d + 1.0, t["wt"], H)
        fast = fast + CK.hex_nut(t["af"], t["ht"], d, H + t["wt"])
        z = H + t["wt"] + t["ht"]
    if sp["min_h"]:
        mh = sp["min_h"]
        fast = fast + CK.washer3d(t["wd"], d + 1.0, t["wt"], mh - t["wt"])
        fast = fast + CK.hex_nut(t["af"], t["h"], d, mh - t["wt"] - t["h"])
        zu = mh + 8.0
    else:
        zu = tot - sp["proj"] - t["h"] - t["wt"]
        fast = fast + CK.washer3d(t["wd"], d + 1.0, t["wt"], zu - 8.0 - t["wt"])
        fast = fast + CK.hex_nut(t["af"], t["h"], d, zu - 8.0 - t["wt"] - t["h"])
    fast = fast + CK.washer3d(t["wd"], d + 1.0, t["wt"], zu)
    fast = fast + CK.hex_nut(t["af"], t["h"], d, zu + t["wt"])
    parts["fasteners"] = fast
    return parts

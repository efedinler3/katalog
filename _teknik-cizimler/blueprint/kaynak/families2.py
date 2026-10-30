"""Kopru (50/70, 75-200), saildrive (SD 150/230/430), MT ve blok (400/450/500/600) aileleri."""
import math

from bp import arc, fillet_poly, fmt
from parts import T, stack, nut, nordlock, stud, washer
from families import RUBBER, STEEL, convex_hull, hole, plan_hole_dims


# ---------------------------------------------------------------------------
# yardimcilar: cizgi ofseti, Bezier, sac serit
# ---------------------------------------------------------------------------
def bez(p0, p1, p2, p3, n=16):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def offset(pts, dist):
    """Acik cizgiyi sola (ilerleme yonune gore +90 derece) dist kadar kaydirir; koselerde mitre."""
    out = []
    n = len(pts)
    for i in range(n):
        if i == 0:
            dx, dy = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
            m = dist
        elif i == n - 1:
            dx, dy = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
            m = dist
        else:
            ax, ay = pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]
            bx, by = pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]
            la, lb = math.hypot(ax, ay) or 1, math.hypot(bx, by) or 1
            dx, dy = ax / la + bx / lb, ay / la + by / lb
            l0 = math.hypot(dx, dy) or 1
            cos_half = abs((-ay / la) * (-dy / l0) + (ax / la) * (dx / l0))
            m = dist / max(cos_half, 0.35)
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        out.append((pts[i][0] + nx * m, pts[i][1] + ny * m))
    return out


def band(center, th):
    """Acik merkez cizgisinden th kalinliginda kapali serit (bukulmus sac)."""
    a = offset(center, th / 2)
    b = offset(center, -th / 2)
    return a + list(reversed(b))


def model_circles(f, xs, y, r, code):
    """Kopru takozlarindaki kalip yazilari: solda model numarasi, sagda 'no vibrasyon .com'."""
    f.circle(xs[0], y, r, "mid", "#ffffff")
    f.text(xs[0], y, code, size=r * f.s * 0.95, weight=600, dy=r * f.s * 0.33)
    f.circle(xs[1], y, r, "mid", "#ffffff")
    for i, w in enumerate(("no", "vibrasyon", ".com")):
        f.text(xs[1], y + r * (0.42 - 0.42 * i), w, size=r * f.s * 0.30, weight=600, dy=r * f.s * 0.1)


class Flip:
    """On gorunusun y eksenini ters ceviren sarmalayici (alt saplama ve somun icin)."""

    def __init__(self, v):
        self.v, self.s, self.sh = v, v.s, v.sh

    def P(self, x, y):
        return self.v.P(x, -y)

    def poly(self, pts, cls="thick", closed=True, fill=None):
        self.v.poly([(x, -y) for (x, y) in pts], cls, closed, fill)

    def line(self, x1, y1, x2, y2, cls="thick"):
        self.v.line(x1, -y1, x2, -y2, cls)

    def rect(self, x0, y0, x1, y1, cls="thick", fill=None, r=0):
        self.v.rect(x0, -y1, x1, -y0, cls, fill, r)


# ---------------------------------------------------------------------------
# Kopru ailesi
# ---------------------------------------------------------------------------
K200 = 205.0 / 501.0


def _d(x, y):
    return (x - 400.0) * K200, (576.0 - y) * K200


def _mirror_open(half):
    """Sol yaridan (x<=0, soldan merkeze) simetrik acik cizgi."""
    return half + [(-x, y) for (x, y) in reversed(half[:-1])]


def bridge_geom_200():
    """75-200 govdesi (Ellebogen 75/100/150/200 ile ayni): sekilli taban sac, sapka, kaucuk."""
    pl = [(159, 568.5), (322, 568.5)]
    pl += bez((322, 568.5), (338, 568.5), (346, 552), (352, 537))[1:]
    pl += [(380, 470)]
    pl += bez((380, 470), (388, 452), (395, 449.5), (400, 449.5))[1:]
    half = [_d(x, y) for (x, y) in pl]
    half = [(x, 3.0) if abs(y - 3.07) < 0.2 else (x, y) for (x, y) in half]
    half[0] = (-102.5, 3.0)
    plate_c = _mirror_open(half)
    ht = [(240, 509), (296, 399)] + bez((296, 399), (299, 394), (302, 392), (307, 392), 8)[1:] + [(400, 392)]
    hat_c = _mirror_open([_d(x, y) for (x, y) in ht])
    rb = [(246, 503), (299, 398), (501, 398), (554, 503), (458, 546), (448, 537), (436, 505), (422, 470)]
    rb += bez((422, 470), (414, 453), (407, 449), (400, 449), 10)[1:]
    rb += bez((400, 449), (393, 449), (386, 453), (378, 470), 10)[1:]
    rb += [(364, 505), (352, 537), (342, 546)]
    rubber = [_d(x, y) for (x, y) in rb]
    return dict(plate_c=plate_c, plate_t=6.0, hat_c=hat_c, hat_t=3.0, rubber=rubber, flat_plate=False,
                hat_top=76.0, hat_ends=67.0, hat_corner=38.0, circles=((-38.0, 40.0), (38.0, 40.0), 9.5), bean=None)


def bridge_geom_50():
    """50 / 70 govdesi (Ellebogen 50/70): duz taban sac (5 mm) + M kaidesi + sapka."""
    mh = [(-45.5, 6.5), (-24.0, 6.5)] + bez((-24.0, 6.5), (-19.0, 6.5), (-15.0, 14.0), (-12.0, 21.0))[1:]
    mh += [(-5.5, 37.5)] + bez((-5.5, 37.5), (-3.5, 42.0), (-1.8, 44.0), (0.0, 44.0), 8)[1:]
    m_c = _mirror_open(mh)
    hh = [(-53.7, 25.8), (-35.5, 61.8)] + bez((-35.5, 61.8), (-34.3, 64.0), (-33.0, 64.5), (-31.0, 64.5), 8)[1:]
    hh += [(0.0, 64.5)]
    hat_c = _mirror_open(hh)
    hat_in = offset(hat_c, -1.5)
    m_out = offset(m_c, 1.5)
    inner = [pt for pt in m_out if abs(pt[0]) <= 36.0]
    rubber = list(hat_in) + [(37.0, 9.5)] + list(reversed(inner)) + [(-37.0, 9.5)]
    return dict(m_c=m_c, plate_t=5.0, hat_c=hat_c, hat_t=3.0, rubber=rubber, flat_plate=True,
                hat_top=66.0, hat_ends=55.2, hat_corner=36.2, circles=((-27.3, 35.5), (27.3, 35.5), 9.0),
                bean=(12.0, 57.0, 61.0))


def draw_bridge(f, pl, p, L):
    k = 1.0 / f.s
    t = T[p["thread"]]
    g = bridge_geom_50() if p["body"] == "50" else bridge_geom_200()
    Lb, W, C = p["L"], p["W"], p["C"]
    # --- on gorunus
    f.poly(g["rubber"], "thick", True, RUBBER)
    if g["flat_plate"]:
        f.rect(-Lb / 2, 0, Lb / 2, g["plate_t"], "thick", STEEL)
        f.poly(band(g["m_c"], 3.0), "thick", True, STEEL)
    else:
        f.poly(band(g["plate_c"], g["plate_t"]), "thick", True, STEEL)
    f.poly(band(g["hat_c"], g["hat_t"]), "thick", True, STEEL)
    if g["bean"]:
        bw, by0, by1 = g["bean"]
        f.poly(fillet_poly([(-bw, by0), (bw, by0), (bw, by1), (-bw, by1)], 2.0), "mid", True, "#ffffff")
    cx = g["circles"]
    model_circles(f, (cx[0][0], cx[1][0]), cx[0][1], cx[2], p["code"])
    H = g["hat_top"]
    stack(f, t, H, p["minH"], p["total"], lower="grower+jam")
    f.line(0, -4 * k, 0, p["total"] + 4 * k, "cen")
    f.dim_h(-Lb / 2, Lb / 2, 0, 0, -9 * k, fmt(Lb))
    f.dim_v(0, g["plate_t"], Lb / 2, Lb / 2, Lb / 2 + 3.5 * k, fmt(g["plate_t"]), txt_side="top")
    xb = Lb / 2 + 11 * k
    f.dim_v(0, H, g["hat_corner"], g["hat_corner"], xb, fmt(H))
    f.dim_v(0, p["minH"], t["wd"] / 2, t["wd"] / 2, xb + 9 * k, f'{L["minh"]} = {fmt(p["minH"])}')
    f.dim_v(0, p["total"], 0, 0, xb + 18 * k, fmt(p["total"]))
    top = p["total"]
    f.dim_h(-t["d"] / 2, t["d"] / 2, top, top, top + 6 * k, p["thread_txt"], txt_side="right")
    # --- ust gorunus
    pl.rect(-Lb / 2, -W / 2, Lb / 2, W / 2, "thick", STEEL)
    he, hc = g["hat_ends"], g["hat_corner"]
    pl.rect(-he, -W / 2, he, W / 2, "thick", RUBBER)
    for sx in (-1, 1):
        pl.line(sx * hc, -W / 2, sx * hc, W / 2, "mid")
    pl.rect(-hc + 4, -W / 2 + 5, hc - 4, W / 2 - 5, "thin")
    pl.circle(0, 0, t["wd"] / 2, "thick", "#ffffff")
    pl.hexagon(0, 0, t["af"], "thick", 0)
    pl.circle(0, 0, t["d"] / 2, "mid")
    pl.cline_h(-Lb / 2 - 4 * k, Lb / 2 + 4 * k, 0)
    pl.cline_v(0, -W / 2 - 4 * k, W / 2 + 4 * k)
    hole(pl, p["hole_l"], -C / 2)
    hole(pl, p["hole_r"], C / 2)
    pl.dim_h(-C / 2, C / 2, W / 2, W / 2, W / 2 + 9 * k, fmt(C))
    pl.dim_v(-W / 2, W / 2, Lb / 2, Lb / 2, Lb / 2 + 9 * k, fmt(W))
    plan_hole_dims(pl, p["hole_l"], -C / 2, "left", k, W)
    plan_hole_dims(pl, p["hole_r"], C / 2, "right", k, W)


# ---------------------------------------------------------------------------
# Saildrive ailesi (SD 150 / 230 / 430)
# ---------------------------------------------------------------------------
def draw_sd(f, pl, p, L):
    k = 1.0 / f.s
    t = T[p["thread"]]
    H, drop, half = p["H"], p["roof_drop"], p["L"] / 2
    wing_y = H - drop
    tf = p["roof_flat"]
    roof_c = [(-half + 1.5, wing_y + 1.75), (-tf, H - 1.75), (tf, H - 1.75), (half - 1.5, wing_y + 1.75)]
    roof = band(fillet_poly(roof_c, 3.0, closed=False), 3.5)
    tri_w = p["low_w"] / 2
    tri = fillet_poly([(0.0, wing_y), (tri_w, 8.0), (tri_w, 0.0), (-tri_w, 0.0), (-tri_w, 8.0)],
                      [4.0, 3.0, 4.0, 4.0, 3.0])
    rub = [(-half + 10.0, wing_y + 2.0), (-tri_w + 2.0, 7.0), (tri_w - 2.0, 7.0), (half - 10.0, wing_y + 2.0),
           (tf - 1.0, H - 3.5), (-tf + 1.0, H - 3.5)]
    f.poly(fillet_poly(rub, 2.5), "thick", True, RUBBER)
    f.poly(roof, "thick", True, STEEL)
    f.poly(tri, "thick", True, STEEL)
    chev = [(-17.0, H - 10.5), (0.0, wing_y + 8.0), (17.0, H - 10.5)]
    f.poly(fillet_poly(band(chev, 7.0), 2.0), "mid", True, "#ffffff")
    gap = p["bracket_gap"]
    stud(f, H - 0.01, H + p["top_stud"], t["d"])
    nordlock(f, H + gap, t)
    nut(f, H + gap + t["nlt"], t)
    vb = Flip(f)
    stud(vb, 0.01, p["bot_stud"], t["d"])
    nordlock(vb, gap, t)
    nut(vb, gap + t["nlt"], t)
    f.line(0, -p["bot_stud"] - 2 * k, 0, H + p["top_stud"] + 4 * k, "cen")
    f.dim_h(-half, half, wing_y, wing_y, -p["bot_stud"] - 15 * k, fmt(p["L"]))
    f.dim_h(-tri_w, tri_w, 0, 0, -p["bot_stud"] - 6 * k, fmt(p["low_w"]))
    xd = half + 9 * k
    f.dim_v(H, H + p["top_stud"], t["d"] / 2, t["d"] / 2, xd, fmt(p["top_stud"]))
    f.dim_v(wing_y, H, half, tf, xd, fmt(drop))
    f.dim_v(0, wing_y, tri_w, half, xd, fmt(wing_y))
    f.dim_v(0, H, tri_w, tf, xd + 9 * k, fmt(H))
    f.dim_v(-p["bot_stud"], 0, t["d"] / 2, tri_w, xd, fmt(p["bot_stud"]))
    tt = H + p["top_stud"]
    f.dim_h(-t["d"] / 2, t["d"] / 2, tt, tt, tt + 6 * k, p["thread_txt"], txt_side="right")
    yb = -(gap + t["nlt"] + t["h"] + (p["bot_stud"] - gap - t["nlt"] - t["h"]) / 2)
    f.dim_h(-t["d"] / 2, t["d"] / 2, yb, yb, yb, p["thread_txt"], txt_side="left")
    # --- ust gorunus
    W = p["W"]
    pl.rect(-half, -W / 2, half, W / 2, "thick", STEEL)
    for sx in (-1, 1):
        pl.line(sx * tf, -W / 2, sx * tf, W / 2, "mid")
        pl.line(sx * (tf + 3.0), -W / 2, sx * (tf + 3.0), W / 2, "thin")
    pl.rect(-tf + 2.0, -W / 2 + 1.0, tf - 2.0, W / 2 - 1.0, "thin")
    pl.circle(0, 0, t["nl"] / 2, "thick", "#ffffff")
    pl.hexagon(0, 0, t["af"], "thick", 0)
    pl.circle(0, 0, t["d"] / 2, "mid")
    pl.cline_h(-half - 4 * k, half + 4 * k, 0)
    pl.cline_v(0, -W / 2 - 4 * k, W / 2 + 4 * k)
    pl.dim_v(-W / 2, W / 2, half, half, half + 9 * k, fmt(W))


# ---------------------------------------------------------------------------
# MT ailesi: kalin flans taban, silindirik kaucuk, canak pul
# ---------------------------------------------------------------------------
def draw_mt(f, pl, p, L):
    k = 1.0 / f.s
    t = T[p["thread"]]
    Lb, W, C, fl = p["L"], p["W"], p["C"], p["flange"]
    f.rect(-Lb / 2, 0, Lb / 2, fl, "thick", STEEL, r=1.0)
    sw = p["slot"][0]
    for sx in (-1, 1):
        for xx in (sx * C / 2 - sw / 2, sx * C / 2 + sw / 2):
            f.line(xx, 0, xx, fl, "hid")
    rb = W / 2 * 0.98
    rt = rb * 0.95
    bt = fl + p["body"]
    f.poly(fillet_poly([(-rb, fl), (rb, fl), (rt, bt), (-rt, bt)], [0, 0, 4.0, 4.0]), "thick", True, RUBBER)
    cw_top, cw_bot = p["cup"]
    ch = p["cup_h"]
    f.poly([(-cw_bot / 2, bt), (cw_bot / 2, bt), (cw_top / 2, bt + ch), (-cw_top / 2, bt + ch)], "thick", True, STEEL)
    f.line(-cw_top / 2 + 1.5, bt + ch - 1.2, cw_top / 2 - 1.5, bt + ch - 1.2, "thin")
    sup = p["support"]
    top = sup + t["wt"] + p["upper_gap"] + t["h"] + t["d"] * 1.6
    stud(f, bt + ch - 0.01, top, t["d"])
    nut(f, sup - t["h"], t)
    washer(f, sup, t["wd"] + 4, t["wt"])
    nut(f, sup + t["wt"] + p["upper_gap"], t)
    f.line(0, -4 * k, 0, top + 4 * k, "cen")
    f.dim_h(-Lb / 2, Lb / 2, 0, 0, -9 * k, fmt(Lb))
    f.dim_v(0, fl, -Lb / 2, -Lb / 2, -Lb / 2 - 7 * k, fmt(fl))
    f.dim_v(0, sup, t["wd"] / 2 + 2, t["wd"] / 2 + 2, Lb / 2 + 10 * k, fmt(sup))
    f.dim_h(-t["d"] / 2, t["d"] / 2, top, top, top + 6 * k, p["thread_txt"], txt_side="right")
    # --- ust gorunus
    re = p["end_half"]
    pts = [(-Lb / 2, -re), (-Lb / 2, re), (Lb / 2, re), (Lb / 2, -re)] + arc(0, 0, W / 2, 0, 360, 90)
    pl.poly(convex_hull(pts), "thick", True, STEEL)
    pl.circle(0, 0, W / 2 * 0.98, "thick", RUBBER)
    pl.circle(0, 0, cw_top / 2, "mid", "#ffffff")
    pl.circle(0, 0, cw_bot / 2, "thin")
    pl.circle(0, 0, t["d"] / 2, "thick")
    pl.cline_h(-Lb / 2 - 4 * k, Lb / 2 + 4 * k, 0)
    pl.cline_v(0, -W / 2 - 4 * k, W / 2 + 4 * k)
    sl = p["slot"]
    for sx in (-1, 1):
        hole(pl, ("slot", sl[0], sl[1], "v"), sx * C / 2)
    pl.dim_h(-C / 2, C / 2, 0, 0, -W / 2 - 9 * k, fmt(C))
    pl.dim_v(-W / 2, W / 2, 0, 0, Lb / 2 + 9 * k, fmt(W))
    pl.dim_v(-sl[1] / 2, sl[1] / 2, -C / 2, -C / 2, -Lb / 2 - 7 * k, fmt(sl[1]))
    pl.dim_h(-C / 2 - sl[0] / 2, -C / 2 + sl[0] / 2, sl[1] / 2, sl[1] / 2, W / 2 + 7 * k, fmt(sl[0]), txt_side="left")


# ---------------------------------------------------------------------------
# Blok ailesi (400 / 450 / 500 / 600)
# ---------------------------------------------------------------------------
def draw_block(f, pl, p, L):
    k = 1.0 / f.s
    t = T[p["thread"]]
    Lb, W, C = p["L"], p["W"], p["C"]
    hw = p["house_w"] / 2
    ear_h, house_h, H = p["ear_h"], p["house_h"], p["H"]
    clr = p.get("clear", 3.5)
    tun = hw * 0.72
    top_in = hw - p.get("taper", 2.5)
    body = [(-Lb / 2, 0), (-tun - 3.0, 0), (-tun, clr), (tun, clr), (tun + 3.0, 0), (Lb / 2, 0), (Lb / 2, ear_h),
            (hw + 1.0, ear_h), (top_in, house_h), (-top_in, house_h), (-hw - 1.0, ear_h), (-Lb / 2, ear_h)]
    radii = [0.8, 0, 1.5, 1.5, 0, 0.8, 0.8, 4.0, 2.0, 2.0, 4.0, 0.8]
    f.poly(fillet_poly(body, radii), "thick", True, STEEL)
    win = fillet_poly([(-tun + 3, clr + 2.5), (tun - 3, clr + 2.5), (tun - 3, house_h * 0.42),
                       (-tun + 3, house_h * 0.42)], 4.0)
    f.poly(win, "mid", True, RUBBER)
    rw = top_in * 0.78
    groove = [(-rw, house_h), (rw, house_h), (rw * 0.6, house_h + (H - house_h) * 0.45), (rw * 0.92, H - 2.5),
              (rw * 0.74, H), (-rw * 0.74, H), (-rw * 0.92, H - 2.5), (-rw * 0.6, house_h + (H - house_h) * 0.45)]
    f.poly(fillet_poly(groove, 1.2), "thick", True, RUBBER)
    mh = p["minH"] or (H + t["ht"] + t["h"] + t["wt"])
    stack(f, t, H, mh, p["total"], lower="jam")
    f.line(0, -4 * k, 0, p["total"] + 4 * k, "cen")
    f.dim_h(-Lb / 2, Lb / 2, 0, 0, -16 * k, fmt(Lb))
    f.dim_h(-hw, hw, 0, 0, -7 * k, fmt(p["house_w"]))
    xb = Lb / 2 + 11 * k
    f.dim_v(0, H, rw * 0.74, rw * 0.74, xb, fmt(H))
    if p["minH"]:
        f.dim_v(0, p["minH"], -t["wd"] / 2, -t["wd"] / 2, -Lb / 2 - 9 * k, f'{L["minh"]} = {fmt(p["minH"])}')
    f.dim_v(0, p["total"], 0, 0, xb + 9 * k, fmt(p["total"]))
    top = p["total"]
    f.dim_h(-t["d"] / 2, t["d"] / 2, top, top, top + 6 * k, p["thread_txt"], txt_side="right")
    # --- ust gorunus
    eh = p["ear_half"]
    ear_pts = []
    for sx in (-1, 1):
        ear_pts += arc(sx * (Lb / 2 - eh), 0, eh, 0, 360, 48)
    ear_pts += [(-hw, -W / 2), (hw, -W / 2), (hw, W / 2), (-hw, W / 2)]
    pl.poly(convex_hull(ear_pts), "thick", True, STEEL)
    pl.rect(-hw, -W / 2, hw, W / 2, "thick", STEEL, r=4.0)
    pl.rect(-top_in * 0.86, -W / 2 * 0.72, top_in * 0.86, W / 2 * 0.72, "mid", RUBBER, r=4.0)
    pl.hexagon(0, 0, t["af"], "thick", 0)
    pl.circle(0, 0, t["d"] / 2, "mid")
    pl.cline_h(-Lb / 2 - 4 * k, Lb / 2 + 4 * k, 0)
    pl.cline_v(0, -W / 2 - 4 * k, W / 2 + 4 * k)
    sl = p.get("slot")
    if sl:
        for sx in (-1, 1):
            hole(pl, ("slot", sl[0], sl[1], "v"), sx * C / 2)
    pl.dim_h(-C / 2, C / 2, 0, 0, -W / 2 - 9 * k, fmt(C))
    pl.dim_v(-W / 2, W / 2, -hw, -hw, -Lb / 2 - 8 * k, fmt(W))
    if sl and p.get("dim_slot", True):
        pl.dim_v(-sl[1] / 2, sl[1] / 2, C / 2, C / 2, Lb / 2 + 8 * k, fmt(sl[1]))
    if sl and p.get("dim_slot", True) is True:
        pl.dim_h(C / 2 - sl[0] / 2, C / 2 + sl[0] / 2, sl[1] / 2, sl[1] / 2, W / 2 + 8 * k, fmt(sl[0]),
                 txt_side="right")

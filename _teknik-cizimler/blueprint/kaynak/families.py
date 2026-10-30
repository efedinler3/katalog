"""Takoz aileleri: on gorunus + ust gorunus geometrisi ve olculendirme.

Her aile fonksiyonu: draw_<aile>(front: View, plan: View, p: dict, L: dil sozlugu)
Urun koordinati: on gorunuste x yatay, y yukari (0 = taban alti); ust gorunuste x yatay, y = derinlik.
"""
import math

from bp import arc, fillet_poly, fmt, mirror
from parts import T, stack, nut, nordlock, stud, washer

RUBBER = "#f1f1f1"
STEEL = "#ffffff"


def convex_hull(points):
    pts = sorted(set((round(x, 4), round(y, 4)) for x, y in points))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def hole(v, spec, cx):
    """spec: ('round', d) | ('slot', w, length, 'v'|'h')."""
    if spec[0] == "round":
        v.circle(cx, 0, spec[1] / 2)
        v.cross(cx, 0, spec[1] / 2 + 2.5)
    else:
        _, w, ln, o = spec[:4]
        v.slot(cx, 0, w, ln, o == "v")
        if o == "v":
            v.cline_v(cx, -(ln / 2 + 2.5), ln / 2 + 2.5)
            v.cline_h(cx - w / 2 - 2.5, cx + w / 2 + 2.5, 0)
        else:
            v.cline_h(cx - ln / 2 - 2.5, cx + ln / 2 + 2.5, 0)
            v.cline_v(cx, -(w / 2 + 2.5), w / 2 + 2.5)


def hole_dims(v, spec, cx, side, k, base_y):
    """Delik / kanal olculeri (ust gorunus): kanal genisligi altta, boyu yanda."""
    if spec[0] == "round":
        return
    _, w, ln, o = spec
    if o == "v":
        h = (ln - w) / 2
        v.dim_h(cx - w / 2, cx + w / 2, -ln / 2, -ln / 2, base_y, fmt(w), txt_side=None)
        xd = cx + (-1 if side == "left" else 1) * (w / 2 + 8 * k)
        if h > 0:
            v.dim_v(-h, h, cx, cx, xd, fmt(2 * h) if spec_centers(spec) else fmt(ln),
                    txt_side="top" if 2 * h * v.s < 9 else None)
    else:
        h = (ln - w) / 2
        v.dim_v(-w / 2, w / 2, cx + (ln / 2 if side == "right" else -ln / 2), cx + (ln / 2 if side == "right" else -ln / 2),
                cx + (-1 if side == "left" else 1) * (ln / 2 + 7 * k), fmt(w))
        v.dim_h(cx - h, cx + h, -w / 2, -w / 2, base_y, fmt(2 * h) if spec_centers(spec) else fmt(ln))


def spec_centers(spec):
    """Kanal boyu 'merkezler arasi' mi verilecek (Ellebogen tarzi): spec[4] == 'c'."""
    return len(spec) > 4 and spec[4] == "c"


# ---------------------------------------------------------------------------
# VV ailesi (konik takoz): VV1 = Ellebogen GT-S, VV2 = GT-M, VV3 = Novibrasyon
# ---------------------------------------------------------------------------
def vv_profile(p):
    tp, H = p["tp"], p["H"]
    nx = p["neck"]
    wx, wy = p["waist"]
    rx, ry0, ry1 = p["rim"]
    tx = p["top_x"]
    right = [(tx, H), (rx, ry1), (rx, ry0), (wx, wy), (nx, tp)]
    pts = right + [(-x, y) for (x, y) in reversed(right)]
    radii = [1.5, 2.0, 1.2, 6.0, 1.0, 1.0, 6.0, 1.2, 2.0, 1.5]
    return fillet_poly(pts, radii)


def draw_vv(f, pl, p, L):
    k = 1.0 / f.s
    t = T[p["thread"]]
    Lb, W, tp, C, H = p["L"], p["W"], p["tp"], p["C"], p["H"]
    rx = p["rim"][0]
    # --- on gorunus
    f.rect(-Lb / 2, 0, Lb / 2, tp, "thick", STEEL)
    prof = vv_profile(p)
    f.poly(prof, "thick", True, RUBBER)
    # kismi kesit: govde icinde oval pencere; kaucuk, ic metal burc ve alt kap (taramali)
    ry1 = p["rim"][2]
    ew = p["waist"][0] * 0.84
    ecy = tp + (ry1 - tp) * 0.5
    eh = (ry1 - tp) * 0.36
    win = [(ew * math.cos(math.radians(a)), ecy + eh * math.sin(math.radians(a))) for a in range(0, 360, 4)]
    f.poly(win, "thin", True, "#ffffff")
    f.begin_clip(win)
    f.hatch(win, "rub")
    core_r = t["d"] * 0.5 + max(2.2, t["d"] * 0.16)
    cup_y = ecy - eh * 0.5
    cup_t = max(1.5, tp * 0.6)
    cup = [(-ew * 0.8, cup_y), (ew * 0.8, cup_y), (ew * 0.8, cup_y + cup_t), (-ew * 0.8, cup_y + cup_t)]
    f.poly(cup, "mid", True, "#ffffff")
    f.hatch(cup, "h135")
    core = [(-core_r, cup_y + cup_t), (core_r, cup_y + cup_t), (core_r, ecy + eh * 1.2), (-core_r, ecy + eh * 1.2)]
    f.poly(core, "mid", True, "#ffffff")
    f.hatch(core, "h45")
    f.rect(-t["d"] / 2, cup_y + cup_t + 1.2, t["d"] / 2, ecy + eh * 1.2, "mid", "#ffffff")
    f.line(-t["d"] * 0.42, cup_y + cup_t + 1.2, -t["d"] * 0.42, ecy + eh * 1.2, "thin")
    f.line(t["d"] * 0.42, cup_y + cup_t + 1.2, t["d"] * 0.42, ecy + eh * 1.2, "thin")
    f.end_clip()
    f.poly(win, "mid", True)
    # ust pul (Ø54 vb.) govdenin ustunde
    tw = p.get("top_washer")
    if tw:
        f.rect(-tw / 2, H - 1.8, tw / 2, H, "mid", "#ffffff")
    lv = stack(f, t, H, p["minH"], p["total"], lower="jam", tip=p.get("tip"))
    f.line(0, -4 * k, 0, p["total"] + 4 * k, "cen")
    # olculer
    f.dim_h(-Lb / 2, Lb / 2, 0, 0, -9 * k, fmt(Lb))
    xr = Lb / 2
    f.dim_v(0, tp, xr, xr, xr + 3.5 * k, fmt(tp), txt_side="top")
    xb = max(rx, Lb / 2) + 10 * k
    f.dim_v(tp, H, p["top_x"], p["top_x"], xb, fmt(H))
    f.dim_v(0, p["minH"], t["wd"] / 2, t["wd"] / 2, xb + 9 * k, f'{L["minh"]} = {fmt(p["minH"])}')
    f.dim_v(0, p["total"], 0, 0, xb + 18 * k, fmt(p["total"]))
    tip = p.get("tip")
    if tip:
        f.dim_h(-tip[0] / 2, tip[0] / 2, p["total"], p["total"], p["total"] + 6 * k, fmt(tip[0]))
        f.dim_v(p["total"] - tip[1], p["total"], tip[0] / 2, tip[0] / 2, tip[0] / 2 + 7 * k, fmt(tip[1]),
                txt_side="beside" if tip[1] * f.s < 12 else None)
    thread_callout(f, t, lv, p["thread_txt"])
    vv_plan(pl, p, 1.0 / pl.s)


def thread_callout(f, t, lv, txt):
    """Dis olcusu: destek pulu ile ust Nord-Lock arasindaki acik saplamada, oklar saplama kenarinda."""
    gap_bot = lv["support"]
    gap_top = lv["top_nut"] - t["h"] - t["nlt"]
    y = (gap_bot + gap_top) / 2
    f.dim_h(-t["d"] / 2, t["d"] / 2, y, y, y, txt, txt_side="right")


def plan_hole_dims(v, spec, cx, side, k, W):
    """Ust gorunus delik olculeri: genislik altta (W/2 altina), boy / merkez farki yanda."""
    yb = -W / 2 - 8 * k
    sgn = -1 if side == "left" else 1
    if spec[0] == "round":
        d = spec[1]
        v.leader(cx + sgn * d / 2 * 0.7, -d / 2 * 0.7, sgn * 6, 9, f"Ø{fmt(d)}", "start" if side == "right" else "end")
        return
    _, w, ln, o = spec[:4]
    centers = len(spec) > 4 and spec[4] == "c"
    h = (ln - w) / 2
    if o == "v":
        v.dim_h(cx - w / 2, cx + w / 2, -h - w / 2, -h - w / 2, yb, fmt(w), txt_side="left" if side == "left" else "right")
        if h > 0:
            xd = cx + sgn * (w / 2 + 6 * k)
            lab = fmt(2 * h) if centers else fmt(ln)
            y1, y2 = (-h, h) if centers else (-ln / 2, ln / 2)
            xr = cx if centers else cx + sgn * w / 2 * 0.0
            v.dim_v(y1, y2, xr, xr, xd, lab, txt_side="top" if (y2 - y1) * v.s < 9 else None)
    else:
        xd = cx + sgn * (ln / 2 + 6 * k)
        v.dim_v(-w / 2, w / 2, cx + sgn * h, cx + sgn * h, xd, fmt(w), txt_side="top" if w * v.s < 9 else None)
        lab = fmt(2 * h) if centers else fmt(ln)
        x1, x2 = (cx - h, cx + h) if centers else (cx - ln / 2, cx + ln / 2)
        v.dim_h(x1, x2, -w / 2 if centers else 0, -w / 2 if centers else 0, yb, lab,
                txt_side=("left" if side == "left" else "right") if (x2 - x1) * v.s < 12 else None)


def vv_plan(pl, p, k):
    """VV ust gorunus (sahibin cizimlerindeki duzen): kulakli taban, yuvarlak koseli kaucuk, kaburgalar."""
    t = T[p["thread"]]
    Lb, W, C = p["L"], p["W"], p["C"]
    rx = p["rim"][0]
    tip = p.get("tip")
    re = (Lb - C) / 2
    cpts = []
    for sx in (-1, 1):
        cpts += arc(sx * C / 2, 0, re, 0, 360, 48)
    xb_ = p["top_x"]
    cpts += fillet_poly([(-xb_, -W / 2), (xb_, -W / 2), (xb_, W / 2), (-xb_, W / 2)], 5)
    pl.poly(convex_hull(cpts), "thick", True, STEEL)
    bz = W / 2 - 0.4
    body = fillet_poly([(-rx, -bz), (rx, -bz), (rx, bz), (-rx, bz)], min(rx, bz) * p.get("corner_k", 0.34))
    pl.poly(body, "thick", True, RUBBER)
    rt = p.get("top_washer", 2 * p["top_x"]) / 2
    rib_end = rt * p.get("rib_k", 1.36)
    rw = 1.1 + 0.004 * Lb
    for a in (45, 135, 225, 315):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        nx, ny = -sa, ca
        r1 = rt * 1.03
        pts = [(r1 * ca + nx * rw, r1 * sa + ny * rw), (rib_end * ca + nx * rw, rib_end * sa + ny * rw),
               (rib_end * ca - nx * rw, rib_end * sa - ny * rw), (r1 * ca - nx * rw, r1 * sa - ny * rw)]
        pl.poly(pts, "mid", True, "#ffffff")
    fp = p.get("flange_plan")
    if fp:
        for sz in (-1, 1):
            pl.line(-fp[0], sz * fp[1], fp[0], sz * fp[1], "mid")
    pl.circle(0, 0, rt, "thick", "#ffffff")
    pl.circle(0, 0, rt * 0.6, "mid")
    pl.hexagon(0, 0, t["af"], "thick", 0)
    pl.circle(0, 0, t["af"] * 0.42, "thin")
    pl.circle(0, 0, t["d"] / 2, "mid")
    if tip:
        pl.rect(-tip[0] / 2, -tip[0] / 2, tip[0] / 2, tip[0] / 2, "mid")
    pl.cline_h(-Lb / 2 - 4 * k, Lb / 2 + 4 * k, 0)
    pl.cline_v(0, -W / 2 - 4 * k, W / 2 + 4 * k)
    hole(pl, p["hole_l"], -C / 2)
    hole(pl, p["hole_r"], C / 2)
    pl.dim_h(-C / 2, C / 2, W / 2, W / 2, W / 2 + 9 * k, fmt(C))
    pl.dim_v(-W / 2, W / 2, 0, 0, Lb / 2 + 9 * k, fmt(W))
    plan_hole_dims(pl, p["hole_l"], -C / 2, "left", k, W)
    plan_hole_dims(pl, p["hole_r"], C / 2, "right", k, W)

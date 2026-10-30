"""Izlenmis gorunuslerle cizim: urun hatlari gercek fotograftan / hazir cizimden, saplama + olculer vektor.

draw_photo(front, plan, p, L): p['kind'] in bridge | sd | block | mt | vv ; p['trace'] = dict(front=..., plan=...)
"""
import math

from bp import fmt, arc
from parts import T, stack, nut, nordlock, stud, washer
from families import hole, plan_hole_dims, convex_hull, RUBBER
from families2 import Flip
from foto_aile import trace_view, front_map, plan_map, draw_trace
import families as F


def draw_photo(f, pl, p, L):
    kind = p["kind"]
    tr = p["trace"]
    k = 1.0 / f.s
    t = T[p["thread"]]
    code = p["code"]
    tf = trace_view(tr["front"], f"{code}-on")
    Lb = p["L"]
    if kind == "bridge":
        fm, top = front_map(tf, Lb, p["H"])
    elif kind == "sd":
        fm, top = front_map(tf, Lb, p["H"])
    elif kind == "block":
        fm, top = front_map(tf, Lb, p["H"])
    elif kind == "mt":
        fm, top = front_map(tf, Lb, None, uniform=True)
    else:
        fm, top = front_map(tf, Lb, p["H"])
    drop = None
    if p.get("relabel"):
        cx_, cy_, r_ = p["relabel"]
        drop = lambda x, y: (x - cx_) ** 2 + (y - cy_) ** 2 < (r_ * 0.86) ** 2
    draw_trace(f, tf, fm, drop=drop)
    if p.get("relabel"):
        cx_, cy_, r_ = p["relabel"]
        f.text(cx_, cy_, code, size=r_ * f.s * 1.0, weight=600, dy=r_ * f.s * 0.35)
    # --- saplama / somunlar
    H = top
    if kind in ("bridge",):
        lv = stack(f, t, H, p["minH"], p["total"], lower="grower+jam")
    elif kind == "block":
        mh = p["minH"] or (H + t["ht"] + t["h"] + t["wt"])
        lv = stack(f, t, H, mh, p["total"], lower="jam")
    elif kind == "vv":
        lv = stack(f, t, H, p["minH"], p["total"], lower="jam", tip=p.get("tip"))
    elif kind == "mt":
        sup = p["support"]
        tot = sup + t["wt"] + p["upper_gap"] + t["h"] + t["d"] * 1.6
        stud(f, H - 0.01, tot, t["d"])
        nut(f, sup - t["h"], t)
        washer(f, sup, t["wd"] + 4, t["wt"])
        nut(f, sup + t["wt"] + p["upper_gap"], t)
        p = dict(p, total=tot)
    elif kind == "sd":
        gap = p["bracket_gap"]
        stud(f, H - 0.01, H + p["top_stud"], t["d"])
        nordlock(f, H + gap, t)
        nut(f, H + gap + t["nlt"], t)
        vb = Flip(f)
        stud(vb, 0.01, p["bot_stud"], t["d"])
        nordlock(vb, gap, t)
        nut(vb, gap + t["nlt"], t)
    ybot = -p.get("bot_stud", 0)
    ytop = p["total"] if "total" in p else p["H"] + p.get("top_stud", 0)
    f.line(0, ybot - 3 * k, 0, ytop + 4 * k, "cen")
    front_dims(f, p, L, k, t)
    # --- ust gorunus
    if "plan" not in tr:
        if kind == "mt":
            mt_plan(pl, p, k)
        else:
            F.vv_plan(pl, p, k)
        return
    tp_ = trace_view(tr["plan"], f"{code}-ust")
    W = p["W"]
    pm = plan_map(tp_, Lb, W)
    C = p.get("C")
    pdrop = None
    hl = p.get("hole_l") or (("slot", p["slot"][0], p["slot"][1], "v") if p.get("slot") else None)
    hr = p.get("hole_r") or hl
    if p.get("redraw_holes") and C:
        hw = max(hl[1] if hl[0] != "round" else hl[1], 8.0) / 2
        pdrop = lambda x, y: abs(x) > C / 2 - hw - 3.0
    draw_trace(pl, tp_, pm, drop=pdrop)
    if p.get("redraw_holes") and C:
        hole(pl, hl, -C / 2)
        hole(pl, hr, C / 2)
    pl.cline_h(-Lb / 2 - 4 * k, Lb / 2 + 4 * k, 0)
    pl.cline_v(0, -W / 2 - 4 * k, W / 2 + 4 * k)
    if C and not p.get("redraw_holes"):
        for sx in (-1, 1):
            pl.cross(sx * C / 2, 0, 6)
    plan_dims(pl, p, L, k)


def front_dims(f, p, L, k, t):
    kind = p["kind"]
    Lb = p["L"]
    if kind == "sd":
        H, drop, half = p["H"], p["roof_drop"], Lb / 2
        wing_y = H - drop
        tri_w = p["low_w"] / 2
        tf = p["roof_flat"]
        f.dim_h(-half, half, wing_y, wing_y, -p["bot_stud"] - 15 * k, fmt(Lb))
        f.dim_h(-tri_w, tri_w, 0, 0, -p["bot_stud"] - 6 * k, fmt(p["low_w"]))
        xd = half + 9 * k
        f.dim_v(H, H + p["top_stud"], t["d"] / 2, t["d"] / 2, xd, fmt(p["top_stud"]))
        f.dim_v(wing_y, H, half, tf, xd, fmt(drop))
        f.dim_v(0, wing_y, tri_w, half, xd, fmt(wing_y))
        f.dim_v(0, H, tri_w, tf, xd + 9 * k, fmt(H))
        f.dim_v(-p["bot_stud"], 0, t["d"] / 2, tri_w, xd, fmt(p["bot_stud"]))
        tt = H + p["top_stud"]
        f.dim_h(-t["d"] / 2, t["d"] / 2, tt, tt, tt + 6 * k, p["thread_txt"], txt_side="right")
        gap = p["bracket_gap"]
        yb = -(gap + t["nlt"] + t["h"] + (p["bot_stud"] - gap - t["nlt"] - t["h"]) / 2)
        f.dim_h(-t["d"] / 2, t["d"] / 2, yb, yb, yb, p["thread_txt"], txt_side="left")
        return
    f.dim_h(-Lb / 2, Lb / 2, 0, 0, -(16 if kind == "block" else 9) * k, fmt(Lb))
    if kind == "block" and p.get("house_w"):
        hw = p["house_w"] / 2
        f.dim_h(-hw, hw, 0, 0, -7 * k, fmt(p["house_w"]))
    if p.get("tp"):
        f.dim_v(0, p["tp"], Lb / 2, Lb / 2, Lb / 2 + 3.5 * k, fmt(p["tp"]), txt_side="top")
    if kind == "mt":
        fl = p["flange"]
        f.dim_v(0, fl, -Lb / 2, -Lb / 2, -Lb / 2 - 7 * k, fmt(fl))
        f.dim_v(0, p["support"], t["wd"] / 2 + 2, t["wd"] / 2 + 2, Lb / 2 + 10 * k, fmt(p["support"]))
    else:
        xb = Lb / 2 + 11 * k
        H = p["H"]
        f.dim_v(0, H, p.get("h_x", 20), p.get("h_x", 20), xb, fmt(H))
        if p.get("minH"):
            if kind == "block":
                f.dim_v(0, p["minH"], -t["wd"] / 2, -t["wd"] / 2, -Lb / 2 - 9 * k, f'{L["minh"]} = {fmt(p["minH"])}')
            else:
                f.dim_v(0, p["minH"], t["wd"] / 2, t["wd"] / 2, xb + 9 * k, f'{L["minh"]} = {fmt(p["minH"])}')
        f.dim_v(0, p["total"], 0, 0, xb + (18 if kind != "block" else 9) * k, fmt(p["total"]))
    top = p.get("total") or 0
    tip = p.get("tip")
    if tip:
        f.dim_h(-tip[0] / 2, tip[0] / 2, top, top, top + 6 * k, fmt(tip[0]))
        f.dim_v(top - tip[1], top, tip[0] / 2, tip[0] / 2, tip[0] / 2 + 7 * k, fmt(tip[1]),
                txt_side="beside" if tip[1] * f.s < 12 else None)
        # dis olcusu: destek pulu ile ust Nord-Lock arasinda
        sup = p["minH"]
        gt = top - (tip[1] + t["d"] * 0.45) - t["h"] - t["nlt"]
        y = (sup + gt) / 2
        f.dim_h(-t["d"] / 2, t["d"] / 2, y, y, y, p["thread_txt"], txt_side="right")
    elif kind == "mt":
        tot = p["support"] + t["wt"] + p["upper_gap"] + t["h"] + t["d"] * 1.6
        f.dim_h(-t["d"] / 2, t["d"] / 2, tot, tot, tot + 6 * k, p["thread_txt"], txt_side="right")
    else:
        f.dim_h(-t["d"] / 2, t["d"] / 2, top, top, top + 6 * k, p["thread_txt"], txt_side="right")


def plan_dims(pl, p, L, k):
    kind = p["kind"]
    Lb, W, C = p["L"], p["W"], p.get("C")
    if kind == "sd":
        pl.dim_v(-W / 2, W / 2, Lb / 2, Lb / 2, Lb / 2 + 9 * k, fmt(W))
        return
    if kind in ("bridge", "vv"):
        pl.dim_h(-C / 2, C / 2, W / 2, W / 2, W / 2 + 9 * k, fmt(C))
        import bp as _bp                              # kanal olcusu yazisi genislik olcusune binmesin
        pl.dim_v(-W / 2, W / 2, Lb / 2, Lb / 2, Lb / 2 + (6.5 + 2.4 * _bp.TXT) * k, fmt(W))
        plan_hole_dims(pl, p["hole_l"], -C / 2, "left", k, W)
        plan_hole_dims(pl, p["hole_r"], C / 2, "right", k, W)
        return
    # blok / mt: kanallar
    pl.dim_h(-C / 2, C / 2, 0, 0, -W / 2 - 9 * k, fmt(C))
    pl.dim_v(-W / 2, W / 2, -Lb / 2, -Lb / 2, -Lb / 2 - 8 * k, fmt(W))
    sl = p.get("slot")
    if sl and p.get("dim_slot", True):
        pl.dim_v(-sl[1] / 2, sl[1] / 2, C / 2, C / 2, Lb / 2 + 8 * k, fmt(sl[1]))
        if p.get("dim_slot", True) is True:
            pl.dim_h(C / 2 - sl[0] / 2, C / 2 + sl[0] / 2, sl[1] / 2, sl[1] / 2, W / 2 + 8 * k, fmt(sl[0]),
                     txt_side="right")


def mt_plan(pl, p, k):
    """MT ust gorunus (sitedeki cizimin duzeni): uclari duz kesik flans, ortada tam genislikte kaucuk daire."""
    t = T[p["thread"]]
    Lb, W, C = p["L"], p["W"], p["C"]
    re_ = p["end_half"]
    pts = [(-Lb / 2, -re_), (-Lb / 2, re_), (Lb / 2, re_), (Lb / 2, -re_)] + arc(0, 0, W / 2, 0, 360, 120)
    pl.poly(convex_hull(pts), "thick", True, "#ffffff")
    pl.circle(0, 0, W / 2 * 0.99, "thick", RUBBER)
    cw_top, cw_bot = p["cup"]
    pl.circle(0, 0, cw_top / 2, "mid", "#ffffff")
    pl.circle(0, 0, cw_bot / 2 * 0.62, "thin")
    pl.circle(0, 0, t["d"] / 2, "thick")
    pl.cline_h(-Lb / 2 - 4 * k, Lb / 2 + 4 * k, 0)
    pl.cline_v(0, -W / 2 - 4 * k, W / 2 + 4 * k)
    sl = p["slot"]
    for sx in (-1, 1):
        hole(pl, ("slot", sl[0], sl[1], "v"), sx * C / 2)
    plan_dims(pl, p, None, k)

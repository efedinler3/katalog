"""Izlenmis (gercek fotograf / hazir cizim) gorunusleri sayfaya yerlestirir.

Her urunun 'trace' ayari:
  front / plan: dict(src, box=(x0,y0,x1,y1) kaynak px, mode='photo'|'lines', thr, cut='auto'|satir|None,
                     cut_frac, cut_bottom=satir|None, erase=[(x0,y0,x1,y1)...], up)
Kalibrasyon: on gorunus  x: maske siniri -> +-L/2,  y: alt -> y_bot (0), kesim satiri -> H (ya da esit olcek)
             ust gorunus x: +-L/2, y: +-W/2
"""
import os
import pickle

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import measure, morphology

import foto_cizim as FC

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(HERE, "_iz-onbellek")


def _lines_mask(gray, thr, close_r=2, min_area=3000, thick_open=0):
    """Cizgi cizimde nesne bolgesi: koyu cizgiler kapatilir, delikler doldurulur, en buyuk bolgeler.
    thick_open: ince cizgileri (isaret / olcu) dolgu oncesi atmak icin acma yaricapi."""
    m = gray < thr
    if thick_open:
        m = morphology.opening(m, morphology.disk(thick_open))
    m = morphology.closing(m, morphology.disk(close_r))
    f = ndimage.binary_fill_holes(m)
    lab = measure.label(f)
    keep = np.zeros_like(f)
    regs = sorted(measure.regionprops(lab), key=lambda r: r.area, reverse=True)
    for r in regs[:3]:
        if r.area >= min_area:
            keep[lab == r.label] = True
    return keep


def trace_view(cfg, key):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cp = os.path.join(CACHE_DIR, key + ".pkl")
    sig = repr(sorted(cfg.items()))
    if os.path.exists(cp):
        with open(cp, "rb") as fh:
            d = pickle.load(fh)
        if d.get("sig") == sig:
            return d
    up = cfg.get("up", 2)
    box = cfg["box"]
    rgb = FC.load(cfg["src"], box, up)
    gray = rgb.mean(axis=2)
    thr = cfg.get("thr", 0.86)
    er = [(int((y0 - box[1]) * up), int((x0 - box[0]) * up), int((y1 - box[1]) * up), int((x1 - box[0]) * up))
          for (x0, y0, x1, y1) in cfg.get("erase", [])]
    if cfg.get("mode", "photo") == "photo":
        base = FC._mask(gray, thr, 6, 16000)
    else:
        base = _lines_mask(gray, thr, thick_open=cfg.get('thick_open', 0))
    for (y0, x0, y1, x1) in er:
        base[y0:y1, x0:x1] = False
    cut = cfg.get("cut")
    cut_px = 0
    if cut == "auto":
        widths = base.sum(axis=1)
        rows = np.nonzero(widths > cfg.get("cut_frac", 0.30) * widths.max())[0]
        cut_px = int(rows[0])
    elif isinstance(cut, (int, float)):
        cut_px = int((cut - box[1]) * up)
    cb = cfg.get("cut_bottom")
    if cb == "auto":
        widths = base.sum(axis=1)
        rows = np.nonzero(widths > cfg.get("cut_frac", 0.30) * widths.max())[0]
        cutb_px = int(rows[-1]) + 1
    else:
        cutb_px = int((cb - box[1]) * up) if cb else None
    if cfg.get("mode", "photo") == "photo":
        t = FC.trace_photo(rgb, thr=thr, tv=cfg.get("tv", 0.12), cut_top=cut_px, erase=er,
                           min_len=cfg.get("min_len", 60))
        if cutb_px:
            t["mask"][cutb_px:, :] = False
    else:
        base = _lines_mask(gray, thr, thick_open=cfg.get('thick_open', 0))   # silme yalniz ic cizgilere
        m = base.copy()
        if cut_px:
            m[:cut_px, :] = False
        if cutb_px:
            m[cutb_px:, :] = False
        m = morphology.opening(m, morphology.disk(2))
        lines = (gray < cfg.get("line_thr", thr)) & m
        for (y0, x0, y1, x1) in er:
            lines[y0:y1, x0:x1] = False
        dist = ndimage.distance_transform_edt(m)
        lines &= dist > cfg.get("edge_gap", 4)
        sk = morphology.skeletonize(lines)
        inner = [FC._smooth(c, 0.7, 1) for c in FC.chains(sk, cfg.get("min_len", 30))]
        sm = ndimage.gaussian_filter(m.astype(np.float32), 1.2)
        outline = [FC._smooth(c, 0.9, 1) for c in measure.find_contours(sm, 0.5) if len(c) > 80]
        t = dict(outline=outline, inner=inner, mask=m)
    ys, xs = np.nonzero(t["mask"])
    t["bb"] = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
    t["cut_px"] = cut_px
    t["cutb_px"] = cutb_px
    t["sig"] = sig
    del t["mask"]
    with open(cp, "wb") as fh:
        pickle.dump(t, fh)
    return t


def front_map(t, L, H=None, y_bot=0.0, uniform=False, x_extent=None):
    """Kalibrasyon: piksel (y, x) -> mm (x, y)."""
    xa, ya, xb, yb = t["bb"]
    if x_extent:                                   # maskenin yatay sinirlari L degilse (ornegin cikinti)
        xa, xb = x_extent
    sx = (xb - xa) / L
    cx = (xa + xb) / 2
    bot = t["cutb_px"] if t.get("cutb_px") else yb
    if uniform or not H:
        sy = sx
    else:
        top = t["cut_px"] if t["cut_px"] else ya
        sy = (bot - top) / (H - y_bot)

    def f(y, x):
        return (x - cx) / sx, y_bot + (bot - y) / sy
    top_mm = y_bot + (bot - (t["cut_px"] if t["cut_px"] else ya)) / sy
    return f, top_mm


def plan_map(t, L, W):
    xa, ya, xb, yb = t["bb"]
    sx = (xb - xa) / L
    sy = (yb - ya) / W
    cx, cy = (xa + xb) / 2, (ya + yb) / 2

    def f(y, x):
        return (x - cx) / sx, (cy - y) / sy
    return f


def draw_trace(v, t, f, outline_cls="thick", inner_cls="thin", drop=None):
    """drop(x_mm, y_mm) True ise o noktayi iceren zincir parcasi atilir."""
    for c in t["outline"]:
        pts = [f(y, x) for (y, x) in c]
        v.poly(pts, outline_cls, True)
    for c in t["inner"]:
        pts = [f(y, x) for (y, x) in c]
        if drop:
            seg = []
            for p in pts:
                if drop(*p):
                    if len(seg) > 1:
                        v.poly(seg, inner_cls, False)
                    seg = []
                else:
                    seg.append(p)
            if len(seg) > 1:
                v.poly(seg, inner_cls, False)
        else:
            v.poly(pts, inner_cls, False)

"""Fotografli cizimden on ve ust gorunusu otomatik bul, saplamayi kes, vektor cizgiye cevir.

auto(src, thr, ...) -> dict(front=dict(outline, inner, bbox, cut), plan=dict(...)) ; koordinatlar kaynak px * up.
"""
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import measure, morphology

import foto_cizim as FC


def components(gray, thr=0.86, open_r=4, min_area=6000):
    m = gray < thr
    m = morphology.opening(m, morphology.disk(open_r))
    lab = measure.label(m)
    regs = [r for r in measure.regionprops(lab) if r.area >= min_area]
    return lab, regs


def auto(src, thr=0.86, up=2, cut_frac=0.30, tv=0.12, front_pad=6, plan_pad=6, cut_override=None, erase=(),
         min_area=6000, open_r=4):
    im = Image.open(src).convert("RGB")
    g = np.asarray(im.convert("L")).astype(np.float32) / 255
    lab, regs = components(g, thr, open_r, min_area)
    regs.sort(key=lambda r: r.area, reverse=True)
    two = sorted(regs[:2], key=lambda r: r.bbox[0])           # ustteki = on gorunus
    out = {}
    for name, r, pad in (("front", two[0], front_pad), ("plan", two[1], plan_pad)):
        y0, x0, y1, x1 = r.bbox
        box = (max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad))
        rgb = FC.load(src, box, up)
        cut = 0
        if name == "front":
            reg_mask = (lab[box[1]:box[3], box[0]:box[2]] == r.label)
            widths = reg_mask.sum(axis=1)
            full = widths.max()
            rows = np.nonzero(widths > cut_frac * full)[0]
            cut_src = rows[0] if cut_override is None else cut_override - box[1]
            cut = int(cut_src * up)
        er = []
        for (ex0, ey0, ex1, ey1) in erase:
            er.append((int((ey0 - box[1]) * up), int((ex0 - box[0]) * up), int((ey1 - box[1]) * up),
                       int((ex1 - box[0]) * up)))
        t = FC.trace_photo(rgb, thr=thr, tv=tv, cut_top=cut, erase=er)
        xb0, yb0, xb1, yb1 = FC.bbox(t["mask"])
        t.update(box=box, up=up, cut=cut, bb=(xb0, yb0, xb1, yb1))
        out[name] = t
    return out


def preview(res, path, S=1.0):
    from PIL import ImageDraw
    ims = []
    for k in ("front", "plan"):
        t = res[k]
        h, w = t["mask"].shape
        can = Image.new("RGB", (w, h), "white")
        dr = ImageDraw.Draw(can)
        for c in t["outline"]:
            pts = [(x, y) for (y, x) in c]
            dr.line(pts + [pts[0]], fill="black", width=4)
        for c in t["inner"]:
            dr.line([(x, y) for (y, x) in c], fill="black", width=2)
        ims.append(can)
    W = max(i.width for i in ims)
    Hh = sum(i.height for i in ims) + 20
    c = Image.new("RGB", (W, Hh), "white")
    y = 0
    for i in ims:
        c.paste(i, ((W - i.width) // 2, y))
        y += i.height + 20
    c.thumbnail((1600, 1600))
    c.save(path, quality=88)

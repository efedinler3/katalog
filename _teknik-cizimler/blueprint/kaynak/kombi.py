"""Karsidan olculu fotograf (ustte, buyuk) + ustten render (altta) tek gorselde:
iki urunun sol ve sag uclari ayni hizada (taban boyu olcu cizgileri ust uste denk gelir).
Cikti: assets/img/olcu-kombi-<pid>[-tr].png   Calistirma: python kombi.py [pid ...]
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
KAT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
IMG = os.path.join(KAT, "assets", "img")
TOP = {"mt": "mt2"}
PIDS = ["50", "70", "75", "100", "150", "200", "400", "450", "500", "600", "vv1", "vv2", "vv3", "sd", "mt"]


def base_line(im):
    """Taban boyu olcu cizgisi: alt yarida en uzun yatay koyu-gri (INK) cizgi -> (x0, x1, y)."""
    a = np.asarray(im.convert("RGBA")).astype(int)
    ink = (a[..., 3] > 150) & (np.abs(a[..., 0] - 60) < 28) & (np.abs(a[..., 1] - 64) < 28) & (np.abs(a[..., 2] - 68) < 28)
    h = a.shape[0]
    best = (0, 0, 0, 0)
    for y in range(h // 2, h):
        row = ink[y]
        if row.sum() < 20:
            continue
        xs = np.where(row)[0]
        # en uzun kesintisiz (kucuk bosluklara izin vererek) parca
        gaps = np.where(np.diff(xs) > 6)[0]
        starts = np.r_[xs[0], xs[gaps + 1]]
        ends = np.r_[xs[gaps], xs[-1]]
        i = np.argmax(ends - starts)
        if ends[i] - starts[i] > best[0]:
            best = (ends[i] - starts[i], starts[i], ends[i], y)
    return best[1], best[2], best[3]


def product_span(im):
    al = np.asarray(im.convert("RGBA"))[..., 3]
    cols = np.where((al > 200).any(0))[0]
    return cols.min(), cols.max()


def combine(pid, suf):
    if pid in SIDE:
        return combine_side(pid, suf)
    fp = os.path.join(IMG, f"olcu-{pid}{suf}.png")
    tp = os.path.join(IMG, f"olcu-ust-{TOP.get(pid, pid)}{suf}.png")
    if not (os.path.exists(fp) and os.path.exists(tp)):
        return False
    fr, tp_ = Image.open(fp).convert("RGBA"), Image.open(tp).convert("RGBA")
    fx0, fx1, _ = base_line(fr)
    tx0, tx1, _ = base_line(tp_)
    if fx1 - fx0 < fr.width * 0.25:                  # olcusuz on gorsel (MT): urun genisligi
        fx0, fx1 = product_span(fr)
    s = (fx1 - fx0) / (tx1 - tx0)
    tp_ = tp_.resize((round(tp_.width * s), round(tp_.height * s)), Image.LANCZOS)
    tx0 = round(tx0 * s)
    off_t = fx0 - tx0                                 # ust gorselin sola kaydirma miktari
    left = min(0, off_t)
    W = max(fr.width, off_t + tp_.width) - left
    gap = round(fr.height * 0.03)
    H = fr.height + gap + tp_.height
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(fr, (-left, 0))
    out.alpha_composite(tp_, (off_t - left, fr.height + gap))
    # yatayda ortala: urun merkezi gorselin merkezinde
    cx = (fx0 + fx1) / 2 - left
    half = max(cx, W - cx)
    can = Image.new("RGBA", (round(2 * half), H), (0, 0, 0, 0))
    can.alpha_composite(out, (round(half - cx), 0))
    can.thumbnail((1600, 2200))
    can.save(os.path.join(IMG, f"olcu-kombi-{pid}{suf}.png"), optimize=True)
    return True


SIDE = {"400", "450", "500", "600"}      # tekli urunler: karsidan ve ustten yan yana


def combine_side(pid, suf):
    fp = os.path.join(IMG, f"olcu-{pid}{suf}.png")
    tp = os.path.join(IMG, f"olcu-ust-{TOP.get(pid, pid)}{suf}.png")
    if not (os.path.exists(fp) and os.path.exists(tp)):
        return False
    fr, tp_ = Image.open(fp).convert("RGBA"), Image.open(tp).convert("RGBA")
    fx0, fx1, _ = base_line(fr)
    tx0, tx1, _ = base_line(tp_)
    s = (fx1 - fx0) / (tx1 - tx0)                   # ustten gorunus, karsidan ile ayni olcekte
    tp_ = tp_.resize((round(tp_.width * s), round(tp_.height * s)), Image.LANCZOS)
    gap = round(fr.width * 0.06)
    H = max(fr.height, tp_.height)
    out = Image.new("RGBA", (fr.width + gap + tp_.width, H), (0, 0, 0, 0))
    out.alpha_composite(fr, (0, (H - fr.height) // 2))
    out.alpha_composite(tp_, (fr.width + gap, (H - tp_.height) // 2))
    out.thumbnail((1800, 1100))
    out.save(os.path.join(IMG, f"olcu-kombi-{pid}{suf}.png"), optimize=True)
    return True

if __name__ == "__main__":
    for p in sys.argv[1:] or PIDS:
        print(p, [combine(p, s) for s in ("-tr", "")])

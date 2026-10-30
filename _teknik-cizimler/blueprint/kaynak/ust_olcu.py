"""Blender ustten render (_render3d/ust-<KOD>.png) -> golgeli, ortalanmis, olculu PNG (assets/img/olcu-ust-<pid>[-tr].png).
Olcu degerleri CAD verisinden (urunler.P); cizgiler render'daki urunun gercek kenarlarina oturur.
Calistirma: python ust_olcu.py [KOD ...]
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from urunler import P

HERE = os.path.dirname(os.path.abspath(__file__))
KAT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
IMG = os.path.join(KAT, "assets", "img")
R3 = os.path.join(HERE, "_render3d")
INK = (60, 64, 68, 255)
_WIN_FONT = r"C:\Windows\Fonts\segoeui.ttf"
FONT = _WIN_FONT if os.path.exists(_WIN_FONT) else os.path.join(KAT, "assets", "fonts", "ttf", "segoeui.ttf")
PID = {"50": "50", "70": "70", "75": "75", "100": "100", "150": "150", "200": "200", "400": "400", "450": "450",
       "500": "500", "600": "600", "VV1": "vv1", "VV2": "vv2", "VV3": "vv3", "SD150": "sd",
       "MT1": "mt1", "MT2": "mt2", "MT3": "mt3"}
MT = {"MT1": (140, 68, 100, "12,5 × 28"), "MT2": (166, 98, 133, "13 × 28"), "MT3": (184, 105, 140, "16 × 33")}


def num(v):
    return f"{v:g}".replace(".", ",")


def neutral_cool(im):
    """HDRI'nin metale verdigi mavi kaymayi temizler (pirinc / sicak renkler kalir)."""
    rgba = np.asarray(im).copy()
    hsv = np.asarray(im.convert("RGB").convert("HSV")).astype(np.float64)
    h = hsv[..., 0] * 360 / 255
    cool = (h > 170) & (h < 270)
    hsv[..., 1] = np.where(cool, hsv[..., 1] * 0.15, hsv[..., 1])
    rgb = np.asarray(Image.fromarray(hsv.round().astype(np.uint8), "HSV").convert("RGB"))
    rgba[..., :3] = rgb
    return Image.fromarray(rgba, "RGBA")


def shadowed(im):
    im = neutral_cool(im)
    a = np.asarray(im).astype(np.uint8)
    prod = a[..., 3] >= 250
    m = Image.fromarray((prod * 255).astype(np.uint8))
    bb = m.getbbox()
    im, m = im.crop(bb), m.crop(bb)
    pad = int(0.08 * max(im.size))
    W, H = im.width + 2 * pad, im.height + 2 * pad
    sh = Image.new("L", (W, H), 0)
    sh.paste(m, (pad + int(0.010 * W), pad + int(0.018 * W)))
    sh = sh.filter(ImageFilter.GaussianBlur(0.014 * W)).point(lambda v: int(v * 0.42))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.putalpha(sh)
    p = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    p.paste(im, (pad, pad), m)
    return Image.alpha_composite(out, p), (pad, pad, pad + im.width, pad + im.height)


def hole_text(code, lang):
    sys.path.insert(0, KAT)
    from olcu_foto import hole_labels  # noqa: E402
    if code in MT:
        s = MT[code][3]
        return s, s
    return hole_labels(dict(P[code], code=code), lang)


def draw(code, lang):
    src = os.path.join(R3, f"ust-{code}.png")
    if not os.path.exists(src):
        return False
    img, (x0, y0, x1, y1) = shadowed(Image.open(src).convert("RGBA"))
    if code in MT:
        Lmm, Wmm, Cmm, _ = MT[code]
    else:
        q = P[code]
        Lmm, Wmm, Cmm = q["L"], q.get("W"), q.get("C")
    W0 = img.width
    k = W0 / 1500
    pl, pr, pt, pb = int(140 * k), int(260 * k), int(60 * k), int(300 * k)
    can = Image.new("RGBA", (img.width + pl + pr, img.height + pt + pb), (0, 0, 0, 0))
    can.alpha_composite(img, (pl, pt))
    d = ImageDraw.Draw(can)
    f = ImageFont.truetype(FONT, int(46 * k))
    lw = max(2, int(2.2 * k))
    L, R, T, B = x0 + pl, x1 + pl, y0 + pt, y1 + pt
    cx, cy = (L + R) / 2, (T + B) / 2
    sx = (R - L) / Lmm

    def ext(p, q):
        d.line([p, q], fill=INK, width=max(1, lw // 2))

    def arrow(p, q):
        d.line([p, q], fill=INK, width=lw)
        for a1, b1 in ((p, q), (q, p)):
            v = np.subtract(b1, a1).astype(float)
            v /= np.hypot(*v)
            n = np.array([-v[1], v[0]])
            t = np.array(a1, float)
            d.polygon([tuple(t), tuple(t + 17 * k * v + 6 * k * n), tuple(t + 17 * k * v - 6 * k * n)], fill=INK)

    def vtext(x, y, s):
        t = Image.new("RGBA", (int(len(s) * 26 * k + 40), int(56 * k)), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((t.width / 2, t.height / 2), s, fill=INK, font=f, anchor="mm")
        t = t.rotate(90, expand=True)
        can.alpha_composite(t, (int(x - t.width / 2), int(y - t.height / 2)))

    # boy (alt) ve delik araligi
    yb = B + 170 * k
    ext((L, B + 12 * k), (L, yb + 16 * k)); ext((R, B + 12 * k), (R, yb + 16 * k))
    arrow((L, yb), (R, yb)); d.text((cx, yb - 10 * k), num(Lmm), fill=INK, font=f, anchor="mb")
    if Cmm:
        hl, hr = cx - Cmm / 2 * sx, cx + Cmm / 2 * sx
        yc = B + 90 * k
        ext((hl, cy), (hl, yc + 16 * k)); ext((hr, cy), (hr, yc + 16 * k))
        arrow((hl, yc), (hr, yc)); d.text((cx, yc - 10 * k), num(Cmm), fill=INK, font=f, anchor="mb")
        lt, rt = hole_text(code, lang)
        yt = B + 250 * k
        for hx, txt in ((hl, lt), (hr, rt)):
            if txt:
                ext((hx, yc + 22 * k), (hx, yt - 30 * k))
                d.text((hx, yt), txt, fill=INK, font=f, anchor="mm")
    # genislik (sag)
    if Wmm:
        xw = R + 110 * k
        ext((R + 12 * k, T), (xw + 16 * k, T)); ext((R + 12 * k, B), (xw + 16 * k, B))
        arrow((xw, T), (xw, B)); vtext(xw - 32 * k, cy, num(Wmm))
    bb = can.split()[3].point(lambda v: 255 if v > 6 else 0).getbbox()
    m = int(20 * k)
    can = can.crop((max(bb[0] - m, 0), max(bb[1] - m, 0), min(bb[2] + m, can.width), min(bb[3] + m, can.height)))
    # yatayda tam ortalama: urun merkezi gorselin merkezine gelsin
    ucx = cx - max(bb[0] - m, 0)
    left, right = ucx, can.width - ucx
    if left < right:
        can2 = Image.new("RGBA", (int(2 * right), can.height), (0, 0, 0, 0)); can2.alpha_composite(can, (int(right - left), 0))
    else:
        can2 = Image.new("RGBA", (int(2 * left), can.height), (0, 0, 0, 0)); can2.alpha_composite(can, (0, 0))
    can2.thumbnail((1800, 1800))
    suf = "-tr" if lang == "tr" else ""
    can2.save(os.path.join(IMG, f"olcu-ust-{PID[code]}{suf}.png"), optimize=True)
    return True


if __name__ == "__main__":
    for c in sys.argv[1:] or list(PID):
        ok = [draw(c, lg) for lg in ("tr", "en")]
        print(c, "ok" if all(ok) else "render yok")

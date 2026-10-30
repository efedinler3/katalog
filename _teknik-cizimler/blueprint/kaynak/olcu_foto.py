"""Karsidan urun fotograflari (Masaustu *kar.jpg) -> arka plansiz, olculu PNG (assets/img/olcu-<pid>[-tr].png).

Olcu degerleri bizim CAD verisinden (urunler.P) gelir; cizgiler fotograftaki urunun gercek kenarlarina oturur.
Calistirma: python olcu_foto.py [pid ...]
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

from urunler import P

HERE = os.path.dirname(os.path.abspath(__file__))
KAT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
IMG = os.path.join(KAT, "assets", "img")
_LOCAL_M = os.path.join(HERE, "karsidan-fotolar")
M = _LOCAL_M if os.path.isdir(_LOCAL_M) else r"C:\Users\sefed\OneDrive\Masaüstü"

# pid -> (fotograf, CAD kodu, tur)
SRC = {"50": ("50kar.jpg", "50", "base"), "70": ("70kar.jpg", "70", "base"), "75": ("75kar.jpg", "75", "base"),
       "100": ("100kar.jpg", "100", "base"), "150": ("150kar.jpg", "150", "base"), "200": ("200kar.jpg", "200", "base"),
       "400": ("400kar.jpg", "400", "base"), "450": ("450kar.jpg", "450", "base"), "500": ("500kar.jpg", "500", "base"),
       "600": ("600kar.jpg", "600", "base"), "vv1": ("vv1kar.jpg", "VV1", "base"), "vv3": ("vv3kar.jpg", "VV3", "base"), "vv2": ("vv2kar.jpg", "VV2", "base"),
       "sd": ("sd150kar.jpg", "SD150", "sd"), "sd230": ("sd230kar.jpg", "SD230", "sd"),
       "sd430": ("sd430kar.jpg", "SD430", "sd"), "mt": ("mtkar.jpg", None, "plain")}

INK = (60, 64, 68, 255)
_WIN_FONT = r"C:\Windows\Fonts\segoeui.ttf"
FONT = _WIN_FONT if os.path.exists(_WIN_FONT) else os.path.join(KAT, "assets", "fonts", "ttf", "segoeui.ttf")


def num(v):
    s = f"{v:g}"
    return s.replace(".", ",")


def cutout(im):
    """Beyaz zemini saydam yapar; zemine bagli gri golge yumusak, saydam koyu golgeye doner."""
    a = np.asarray(im.convert("RGB"), dtype=np.float64)
    lum = a.mean(2)
    mn = a.min(2)
    light = mn >= 232
    lab, _ = ndi.label(light)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, border[border > 0])
    solid = ~bg & (lum < 215)
    solid = ndi.binary_opening(solid, iterations=2)
    lab2, n = ndi.label(solid)
    if n:
        sizes = ndi.sum(solid, lab2, range(1, n + 1))
        solid = np.isin(lab2, 1 + np.where(sizes > sizes.max() * 0.02)[0])
    prod = ndi.binary_fill_holes(ndi.binary_closing(solid | (~bg & ~(lum > 225)), iterations=2))
    prod &= ~bg
    lab3, n3 = ndi.label(prod)
    if n3:
        sizes = ndi.sum(prod, lab3, range(1, n3 + 1))
        prod = np.isin(lab3, 1 + np.where(sizes > sizes.max() * 0.02)[0])
    # golge: urun disinda kalan acik-gri pikseller
    shadow = ~prod
    sh_a = np.clip((248 - lum) / 248, 0, 1) * shadow
    alpha = np.where(prod, 1.0, sh_a * 0.9)
    soft = ndi.gaussian_filter(prod.astype(float), 0.8)
    alpha = np.maximum(alpha, soft)
    rgb = np.where(prod[..., None], a, 40)
    out = np.dstack([rgb, alpha * 255]).round().clip(0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA"), prod


def edges(prod):
    ys, xs = np.where(prod)
    top, bottom = ys.min(), ys.max()
    width = prod.sum(1)
    big = np.where(width > width.max() * 0.55)[0]
    base_bot = big.max()
    rows = prod[max(base_bot - 25, 0):base_bot + 1]
    cs = np.where(rows.any(0))[0]
    return dict(top=top, bottom=bottom, base_bot=base_bot, left=cs.min(), right=cs.max(), xs=xs, ys=ys)


class Dim:
    def __init__(self, canvas, scale):
        self.c = canvas
        self.d = ImageDraw.Draw(canvas)
        self.k = scale
        self.f = ImageFont.truetype(FONT, int(44 * scale))
        self.lw = max(2, int(2 * scale))

    def arrow(self, p, q):
        d, k = self.d, self.k
        d.line([p, q], fill=INK, width=self.lw)
        for a1, b1 in ((p, q), (q, p)):
            v = np.subtract(b1, a1).astype(float)
            v /= np.hypot(*v)
            n = np.array([-v[1], v[0]])
            t = np.array(a1, float)
            d.polygon([tuple(t), tuple(t + 16 * k * v + 6 * k * n), tuple(t + 16 * k * v - 6 * k * n)], fill=INK)

    def ext(self, p, q):
        self.d.line([p, q], fill=INK, width=max(1, self.lw // 2))

    def htext(self, x, y, s, anchor="mb"):
        self.d.text((x, y), s, fill=INK, font=self.f, anchor=anchor)

    def vtext(self, x, y, s):
        t = Image.new("RGBA", (int(len(s) * 22 * self.k + 40), int(48 * self.k)), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((t.width / 2, t.height / 2), s, fill=INK, font=self.f, anchor="mm")
        t = t.rotate(90, expand=True)
        self.c.alpha_composite(t, (int(x - t.width / 2), int(y - t.height / 2)))


def right_edge(prod, y, x0):
    row = np.where(prod[int(y), :])[0]
    return (row.max() + x0) if len(row) else None


def draw_base(img, prod, q, lang):
    e = edges(prod)
    H, W = prod.shape
    k = W / 1400
    pad_l, pad_r, pad_t, pad_b = int(100 * k), int(380 * k), int(130 * k), int(190 * k)
    can = Image.new("RGBA", (W + pad_l + pad_r, H + pad_t + pad_b), (0, 0, 0, 0))
    can.alpha_composite(img, (pad_l, pad_t))
    D = Dim(can, k)
    L, R, B, T = e["left"] + pad_l, e["right"] + pad_l, e["base_bot"] + pad_t, e["top"] + pad_t
    cxp = (e["left"] + e["right"]) // 2
    band = prod[:, max(cxp - (e["right"] - e["left"]) // 6, 0):cxp + (e["right"] - e["left"]) // 6]
    rows_c = np.where(band.sum(1) >= 6)[0]
    T = rows_c.min() + pad_t
    sx = (R - L) / q["L"]
    sv = (B - T) / q["total"]
    cx = (L + R) / 2
    # taban boyu
    yb = B + 150 * k
    D.ext((L, B + 10 * k), (L, yb + 14 * k))
    D.ext((R, B + 10 * k), (R, yb + 14 * k))
    D.arrow((L, yb), (R, yb))
    D.htext(cx, yb - 8 * k, num(q["L"]))
    # delik araligi
    if q.get("C"):
        hl, hr = cx - q["C"] / 2 * sx, cx + q["C"] / 2 * sx
        yc = B + 80 * k
        D.ext((hl, B - 6 * k), (hl, yc + 14 * k))
        D.ext((hr, B - 6 * k), (hr, yc + 14 * k))
        D.arrow((hl, yc), (hr, yc))
        D.htext(cx, yc - 8 * k, num(q["C"]))
    # sag dikey olculer (icten disa)
    thr = 0.17 if q.get("code", "").startswith("VV") else 0.33
    wrow = prod.sum(1)
    body_top = np.where(wrow > thr * (e["right"] - e["left"]))[0].min() + pad_t
    if q["code"] not in ("400", "500"):              # siyah gövde: koyu kaucuk/braket satirlari (somunlar acik metal)
        rgb = np.asarray(img.convert("RGB"), dtype=np.float64).mean(2)
        dk = (rgb < 95) & prod
        body_top = np.where(dk.sum(1) > 0.15 * (e["right"] - e["left"]))[0].min() + pad_t
    sb = (B - body_top) / q["H"]
    items = [(q["H"], num(q["H"]))]
    if q.get("minH"):
        items.append((q["minH"], ("MİN. = " if lang == "tr" else "MIN. = ") + num(q["minH"])))
    items.append((q["total"], num(q["total"])))
    for i, (mm, label) in enumerate(items):
        x = R + (80 + 100 * i) * k
        y = body_top if i == 0 else (T if i == len(items) - 1 else min(max(B - mm * sv, T + 30 * k), body_top - 30 * k))
        xe = right_edge(prod, min(max(y - pad_t, 0), H - 1), pad_l) or cx
        D.ext((xe + 8 * k, y), (x + 14 * k, y))
        D.arrow((x, y), (x, B))
        D.vtext(x - 28 * k, (y + B) / 2, label)
    D.ext((R + 8 * k, B), (R + (80 + 100 * (len(items) - 1)) * k + 14 * k, B))
    # saplama
    ys = np.where(prod[:, :].any(1))[0]
    toprow = prod[T - pad_t:T - pad_t + int(30 * k)]
    cols = np.where(toprow.any(0))[0]
    sl, sr = cols.min() + pad_l, cols.max() + pad_l
    yt = T - 50 * k
    D.ext((sl, T - 6 * k), (sl, yt - 14 * k))
    D.ext((sr, T - 6 * k), (sr, yt - 14 * k))
    D.arrow((sl - 40 * k, yt), (sl, yt))
    D.arrow((sr + 40 * k, yt), (sr, yt))
    D.htext(sr + 50 * k, yt, q["thread_txt"], anchor="lm")
    # delikler / kanallar (katalog tablosundaki deger) ve taban genisligi
    lt, rt = hole_labels(q, lang)
    if FRONT_HOLES and q.get("C"):
        hl, hr = cx - q["C"] / 2 * sx, cx + q["C"] / 2 * sx
        yh = B - 10 * k
        ty = B + 215 * k                          # olcu cizgilerinin altinda, urunun disinda
        for hx, txt, side in ((hl, lt, -1), (hr, rt, 1)):
            if not txt:
                continue
            D.d.ellipse((hx - 5 * k, yh - 5 * k, hx + 5 * k, yh + 5 * k), outline=INK, width=max(1, D.lw // 2))
            D.ext((hx, yh + 6 * k), (hx, ty - 22 * k))
            D.htext(hx, ty + 14 * k, txt, anchor="mm")
    if FRONT_HOLES and q.get("W"):
        wtxt = ("Taban genişliği " if lang == "tr" else "Base width ") + num(q["W"])
        D.htext(cx, B + 215 * k + 14 * k, wtxt, anchor="mm")
    return can


FRONT_HOLES = False      # delik / kanal / genislik artik ustten render'da


def hole_labels(q, lang):
    """Sol delik ve sag kanal etiketi; degerler katalog tablosundan (data.py 'Holes')."""
    import re
    sys.path.insert(0, KAT)
    from data import PRODUCTS
    pid = {"VV1": "vv1", "VV2": "vv2", "VV3": "vv3"}.get(q["code"], q["code"])
    if pid not in PRODUCTS:
        return "", ""
    rows = dict(PRODUCTS[pid].get("dimrows", []))
    h = rows.get("Holes", "")
    slot_w = "kanal" if lang == "tr" else "slot"
    if not h:
        s = q.get("slot")
        return (f"{num(s[0])} × {num(s[1])}", f"{num(s[0])} × {num(s[1])}") if s else ("", "")
    h = h.replace(" mm", "").replace(".", ",")
    m = re.match(r"Ø([\d,]+) \+ ([\d,]+ )?slot", h)
    if m:
        return f"Ø{m.group(1)}", (f"{slot_w} {m.group(2).strip()}" if m.group(2) else slot_w)
    m = re.match(r"2 slots, ([\d,]+ × [\d,]+)", h)
    if m:
        return m.group(1), m.group(1)
    m = re.match(r"([\d,]+ × [\d,]+) slots", h)
    if m:
        return m.group(1), m.group(1)
    m = re.match(r"Ø([\d,]+)$", h)
    if m:
        return f"Ø{m.group(1)}", f"Ø{m.group(1)}"
    return h, ""


def draw_sd(img, prod, q, lang):
    H, W = prod.shape
    k = W / 1400
    pad_l, pad_r, pad_t, pad_b = int(80 * k), int(300 * k), int(90 * k), int(200 * k)
    can = Image.new("RGBA", (W + pad_l + pad_r, H + pad_t + pad_b), (0, 0, 0, 0))
    can.alpha_composite(img, (pad_l, pad_t))
    D = Dim(can, k)
    width = prod.sum(1)
    body = np.where(width > width.max() * 0.35)[0]
    bt, bb = body.min() + pad_t, body.max() + pad_t
    cs = np.where(prod[body].any(0))[0]
    L, R = cs.min() + pad_l, cs.max() + pad_l
    ys = np.where(prod.any(1))[0]
    T, Bt = ys.min() + pad_t, ys.max() + pad_t
    # gövde genisligi (alt)
    yb = Bt + 90 * k
    D.ext((L, bb - 40 * k), (L, yb + 14 * k))
    D.ext((R, bb - 40 * k), (R, yb + 14 * k))
    D.arrow((L, yb), (R, yb))
    D.htext((L + R) / 2, yb - 8 * k, num(q["L"]))
    # gövde yuksekligi (sag)
    x = R + 70 * k
    D.ext((R + 8 * k, bt), (x + 14 * k, bt))
    D.ext((R + 8 * k, bb), (x + 14 * k, bb))
    D.arrow((x, bt), (x, bb))
    D.vtext(x - 22 * k, (bt + bb) / 2, num(q["H"]))
    # saplamalar
    for yy, lbl in ((T + 40 * k, q["thread_txt"]), (Bt - 40 * k, q["thread_txt"])):
        D.ext(((L + R) / 2 + 70 * k, yy), ((L + R) / 2 + 190 * k, yy))
        D.htext((L + R) / 2 + 200 * k, yy, lbl, anchor="lm")
    return can


def trim(im, m=20):
    bb = im.split()[3].point(lambda v: 255 if v > 8 else 0).getbbox()
    return im.crop((max(bb[0] - m, 0), max(bb[1] - m, 0), min(bb[2] + m, im.width), min(bb[3] + m, im.height)))


def main(pids):
    for pid in pids:
        fn, code, kind = SRC[pid]
        img, prod = cutout(Image.open(os.path.join(M, fn)))
        q = dict(P[code], code=code) if code else None
        ys, xs = np.where(prod)                      # urune kirp: olcu yazilari urun boyuna gore olceklensin
        m = int(0.06 * max(xs.max() - xs.min(), ys.max() - ys.min()))
        box = (max(xs.min() - m, 0), max(ys.min() - m, 0), min(xs.max() + m, prod.shape[1]), min(ys.max() + m, prod.shape[0]))
        img, prod = img.crop(box), prod[box[1]:box[3], box[0]:box[2]]
        for lang, suf in (("tr", "-tr"), ("en", "")):
            if kind == "base":
                out = draw_base(img, prod, q, lang)
            elif kind == "sd":
                out = draw_sd(img, prod, q, lang)
            else:
                out = img
            out = trim(out)
            out.thumbnail((1800, 1800))
            out.save(os.path.join(IMG, f"olcu-{pid}{suf}.png"), optimize=True)
        print(pid)


if __name__ == "__main__":
    main(sys.argv[1:] or list(SRC))

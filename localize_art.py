"""Cizimlerdeki yazilari duzeltir / Turkcelestirir.

- assets/img/<ad>-tr.jpg : Turkce katalog icin etiketleri Turkce cizimler
  (saildrive yerlesim semalari, 200 parca adlari, VV 'MIN. HEIGHT' yazilari)
- assets/img/d450.jpg     : govdedeki 'NoVibrasyon' -> 'Novibrasyon' (iki dil icin)

Orijinaller assets/img/_orig/ klasorunde saklanir; betik her calistiginda oradan uretir.
prepare_assets.py yeniden calistirilirsa bu betigi de calistirin:  python localize_art.py
"""
import os
import shutil

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "assets", "img")
ORIG = os.path.join(IMG, "_orig")
FONTS = os.path.join(HERE, "assets", "fonts", "static")
TTF = os.path.join(HERE, "assets", "fonts", "ttf")
CAP = 0.727            # Inter buyuk harf yuksekligi / em


# ------------------------------------------------------------------ yazi tipi
def ttf_pair(weight):
    """Inter latin + latin-ext woff2 -> ttf (PIL icin)."""
    os.makedirs(TTF, exist_ok=True)
    out = []
    for sub in ("latin", "latin-ext"):
        dst = os.path.join(TTF, f"Inter-{weight}-{sub}.ttf")
        if not os.path.exists(dst):
            f = TTFont(os.path.join(FONTS, f"Inter-{weight}-{sub}.woff2"))
            f.flavor = None
            f.save(dst)
        out.append(dst)
    return out


class MixedFont:
    """Iki alt kume dosyasini (latin / latin-ext) karakter bazinda birlestirir."""

    def __init__(self, weight, size):
        a, b = ttf_pair(weight)
        self.fonts = [ImageFont.truetype(a, size), ImageFont.truetype(b, size)]
        self.cmaps = [set(TTFont(a).getBestCmap()), set(TTFont(b).getBestCmap())]

    def pick(self, ch):
        return self.fonts[0] if ord(ch) in self.cmaps[0] else self.fonts[1]

    def width(self, s):
        return sum(self.pick(c).getlength(c) for c in s)

    def draw(self, dr, x, baseline, s, fill):
        for c in s:
            f = self.pick(c)
            dr.text((x, baseline), c, font=f, fill=fill, anchor="ls")
            x += f.getlength(c)


# ------------------------------------------------------------------ yardimcilar
def dist(p, q):
    return abs(p[0] - q[0]) + abs(p[1] - q[1]) + abs(p[2] - q[2])


def ink_bbox(im, box, bg, thr=90, vertical=False):
    """Kutu icindeki yazinin siki sinirlari (alt cizgi / kilavuz cizgileri haric)."""
    x0, y0, x1, y1 = box
    px = im.load()
    rows = {}
    for y in range(y0, y1):
        xs = [x for x in range(x0, x1) if dist(px[x, y], bg) > thr]
        if xs:
            rows[y] = xs
    if not vertical:          # neredeyse tam genislikte tek cizgi = kilavuz, yazi degil
        rows = {y: xs for y, xs in rows.items() if len(xs) < 0.6 * (x1 - x0)}
    cols = {}
    for y, xs in rows.items():
        for x in xs:
            cols[x] = cols.get(x, 0) + 1
    if vertical:              # dikey olcu cizgisi
        cols = {x: n for x, n in cols.items() if n < 0.6 * (y1 - y0)}
    if not rows or not cols:
        raise SystemExit(f"yazi bulunamadi: {box}")
    ys = [y for y, xs in rows.items() if any(x in cols for x in xs)]
    return min(cols), min(ys), max(cols) + 1, max(ys) + 1


def ink_color(im, bb, bg, thr=90):
    px = im.load()
    cs = [px[x, y] for y in range(bb[1], bb[3]) for x in range(bb[0], bb[2]) if dist(px[x, y], bg) > thr * 1.6]
    if not cs:
        cs = [(40, 40, 40)]
    cs.sort(key=lambda c: sum(c))
    mid = cs[len(cs) // 3]
    return tuple(mid)


def local_bg(im, bb, bg, thr=90, ring=8):
    px = im.load()
    x0, y0, x1, y1 = bb[0] - ring, bb[1] - ring, bb[2] + ring, bb[3] + ring
    cs = []
    for y in range(max(0, y0), min(im.height, y1)):
        for x in range(max(0, x0), min(im.width, x1)):
            if bb[0] - 2 <= x < bb[2] + 2 and bb[1] - 2 <= y < bb[3] + 2:
                continue
            c = px[x, y]
            if dist(c, bg) <= thr:
                cs.append(c)
    if not cs:
        return bg
    return tuple(sorted(ch)[len(ch) // 2] for ch in zip(*cs))


def erase(im, bb, fill, pad=3):
    dr = ImageDraw.Draw(im)
    dr.rectangle((bb[0] - pad, bb[1] - pad, bb[2] + pad - 1, bb[3] + pad - 1), fill=fill)


def put_text(im, bb, text, color, weight=600, align="left", max_w=None, rotate=0):
    """Eski yazinin yerine ayni buyuk harf yuksekliginde yeni yazi (rotate: 90 = asagidan yukari)."""
    if rotate:
        cap = bb[2] - bb[0]
        length = bb[3] - bb[1]
    else:
        cap = bb[3] - bb[1]
        length = bb[2] - bb[0]
    size = max(8, round(cap / CAP))
    font = MixedFont(weight, size)
    w = font.width(text)
    limit = max_w or length * 1.25
    while w > limit and size > 8:
        size -= 1
        font = MixedFont(weight, size)
        w = font.width(text)
    capn = size * CAP
    if not rotate:
        dr = ImageDraw.Draw(im)
        x = bb[0] if align == "left" else (bb[0] + bb[2]) / 2 - w / 2
        font.draw(dr, x, bb[3], text, color)
        return
    tile = Image.new("RGBA", (int(w) + 8, int(capn * 1.6) + 8), (0, 0, 0, 0))
    font.draw(ImageDraw.Draw(tile), 4, 4 + capn * 1.3, text, color + (255,))
    tile = tile.rotate(rotate, expand=True, resample=Image.BICUBIC)
    cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
    im.paste(tile, (int(cx - tile.width / 2), int(cy - tile.height / 2)), tile)


def load(key):
    os.makedirs(ORIG, exist_ok=True)
    src = os.path.join(ORIG, key + ".jpg")
    if not os.path.exists(src):
        shutil.copy2(os.path.join(IMG, key + ".jpg"), src)
    return Image.open(src).convert("RGB")


def relabel(key, jobs, out_key):
    im = load(key)
    bg = im.getpixel((6, 6))
    for job in jobs:
        box, text = job["box"], job["text"]
        bb = ink_bbox(im, box, bg, job.get("thr", 90), vertical=bool(job.get("rotate")))
        col = job.get("color") or ink_color(im, bb, bg, job.get("thr", 90))
        fill = local_bg(im, bb, bg, job.get("thr", 90))
        pad = job.get("pad", 3)
        # alt kenarda pay yok: yazinin hemen altindaki kilavuz cizgisi silinmesin
        ImageDraw.Draw(im).rectangle((bb[0] - pad, bb[1] - pad, bb[2] + pad - 1,
                                      bb[3] + (pad if job.get("rotate") else 0) - 1), fill=fill)
        if "x" in job:
            bb = (job["x"], bb[1], job["x"] + (bb[2] - bb[0]), bb[3])
        if "cap" in job:                  # buyuk harf yuksekligini komsu satirla esitle
            bb = (bb[0], bb[3] - job["cap"], bb[2], bb[3])
        if "like" in job:                 # rengi komsu etiketten al
            col = job["like"]
        put_text(im, bb, text, col, job.get("weight", 600), job.get("align", "left"),
                 job.get("max_w"), job.get("rotate", 0))
    im.save(os.path.join(IMG, out_key + ".jpg"), "JPEG", quality=92)
    print("yazildi:", out_key)


# ------------------------------------------------------------------ is listesi
SAILDRIVE = [
    {"box": (700, 95, 960, 175), "text": "İSKELE", "align": "center", "weight": 700},
    {"box": (640, 628, 1010, 700), "text": "SANCAK", "align": "center", "weight": 700},
    {"box": (288, 270, 356, 530), "text": "ARKA TARAF", "rotate": -90, "weight": 600},
    {"box": (1186, 262, 1262, 540), "text": "ÖN TARAF", "rotate": -90, "weight": 600},
]

D200 = [
    {"box": (12, 55, 200, 92), "text": "SABİT", "x": 21},
    {"box": (12, 93, 300, 128), "text": "SAPLAMA", "x": 21},
    {"box": (12, 180, 330, 221), "text": "DIN 934 SOMUN", "x": 21},
    {"box": (12, 276, 330, 312), "text": "NORD-LOCK", "x": 21},
    {"box": (12, 313, 260, 350), "text": "RONDELA", "x": 21},
    {"box": (12, 383, 360, 423), "text": "DÜZ PUL", "x": 21},
    {"box": (12, 447, 330, 489), "text": "DIN 934 SOMUN", "x": 21},
    {"box": (12, 518, 450, 561), "text": "DIN 936 KONTRA SOMUN", "max_w": 505, "x": 21},
    {"box": (12, 593, 460, 636), "text": "GROWER RONDELA", "max_w": 470, "x": 21},
    {"box": (12, 664, 210, 699), "text": "MODEL", "x": 21, "cap": 33, "like": (58, 58, 58)},
    {"box": (12, 700, 250, 741), "text": "NUMARASI", "x": 21},
    {"box": (1318, 560, 1378, 990), "text": "MİN. YÜKSEKLİK = 103", "rotate": 90, "weight": 500, "max_w": 470},
]

VV = {
    "dvv1": [{"box": (1630, 860, 1706, 1270), "text": "MİN. YÜKSEKLİK = 68.5", "rotate": 90, "weight": 400,
              "max_w": 470}],
    "dvv2": [{"box": (1896, 860, 1970, 1240), "text": "78.5 (MİN. YÜKSEKLİK)", "rotate": 90, "weight": 400,
              "max_w": 440}],
    "dvv3": [{"box": (1866, 850, 1925, 1230), "text": "MİN. YÜKSEKLİK = 100", "rotate": 90, "weight": 400,
              "max_w": 450}],
}


def fix_d450():
    """Govdedeki kabartma 'NoVibrasyon' -> 'Novibrasyon' (siyah kaucuk uzerinde acik gri)."""
    im = load("d450")
    box = (455, 855, 900, 945)
    px = im.load()
    light = [(x, y) for y in range(box[1], box[3]) for x in range(box[0], box[2]) if sum(px[x, y]) > 300]
    xs, ys = [p[0] for p in light], [p[1] for p in light]
    bb = (min(xs), min(ys), max(xs) + 1, max(ys) + 1)
    col = sorted((px[x, y] for x, y in light), key=sum)[len(light) * 2 // 3]
    # yazi piksellerini cevredeki koyu kaucuk pikselleriyle doldur (dokulu, ek yeri yok)
    import random
    random.seed(450)
    dark = [px[x, y] for y in range(bb[1] - 14, bb[3] + 14) for x in range(bb[0] - 14, bb[2] + 14)
            if sum(px[x, y]) < 170]
    mask = Image.new("L", im.size, 0)
    md = mask.load()
    for x, y in light:
        md[x, y] = 255
    mask = mask.filter(ImageFilter.MaxFilter(7))
    fill = Image.new("RGB", im.size)
    fp = fill.load()
    for y in range(bb[1] - 6, bb[3] + 6):
        for x in range(bb[0] - 6, bb[2] + 6):
            fp[x, y] = random.choice(dark)
    fill = fill.filter(ImageFilter.GaussianBlur(0.7))
    im.paste(fill, (0, 0), mask)
    # 'N' buyuk harfi ile olc: buyuk harf yuksekligi ~ 'N' yuksekligi (bb yuksekligi 'y' kuyrugu icerir)
    cap = (bb[3] - bb[1]) * 0.78
    size = round(cap / CAP)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    f = MixedFont(500, size)
    w = f.width("Novibrasyon")
    x = (bb[0] + bb[2]) / 2 - w / 2
    f.draw(ImageDraw.Draw(layer), x, bb[1] + cap, "Novibrasyon", col + (255,))
    layer = layer.filter(ImageFilter.GaussianBlur(0.8))
    im.paste(layer, (0, 0), layer)
    im.save(os.path.join(IMG, "d450.jpg"), "JPEG", quality=92)
    print("yazildi: d450 (Novibrasyon)")


def main():
    for key in ("lsd150", "lsd230", "lsd430"):
        relabel(key, SAILDRIVE, key + "-tr")
    relabel("d200", D200, "d200-tr")
    for key, jobs in VV.items():
        relabel(key, jobs, key + "-tr")
    fix_d450()


if __name__ == "__main__":
    main()

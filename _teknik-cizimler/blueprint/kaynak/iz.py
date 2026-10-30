"""Iz araclari: orijinal cizimi milimetrik izgarayla buyutur ve kendi geometrimi kirmizi olarak ustune bindirir.

Kalibrasyon: ref goruntude cx (simetri ekseni px), by (y=0 seviyesi px), sx / sy (px / mm).
mm -> px:  X = cx + x * sx,  Y = by - y * sy
"""
import sys

from PIL import Image, ImageDraw, ImageFont

FONT = ImageFont.truetype("arial.ttf", 13)


class Ref:
    def __init__(self, path, cx, by, sx, sy=None):
        self.im = Image.open(path).convert("RGB")
        self.cx, self.by, self.sx, self.sy = cx, by, sx, sy or sx

    def px(self, x, y):
        return self.cx + x * self.sx, self.by - y * self.sy

    def mm(self, X, Y):
        return (X - self.cx) / self.sx, (self.by - Y) / self.sy


def grid(ref, xr, yr, zoom, out, step=1.0, major=5.0):
    """xr, yr: mm araliklari; zoom: buyutme. Ince izgara step, kalin major, etiket her major."""
    x0, y1 = ref.px(xr[0], yr[1])
    x1, y0 = ref.px(xr[1], yr[0])
    crop = ref.im.crop((int(x0), int(y1), int(x1) + 1, int(y0) + 1))
    crop = crop.resize((int(crop.width * zoom), int(crop.height * zoom)), Image.LANCZOS)
    dr = ImageDraw.Draw(crop, "RGBA")
    ox, oy = int(x0), int(y1)

    def P(x, y):
        X, Y = ref.px(x, y)
        return (X - ox) * zoom, (Y - oy) * zoom
    k = 0
    v = xr[0] - (xr[0] % step)
    while v <= xr[1] + 1e-6:
        a, _ = P(v, 0)
        is_major = abs((v / major) - round(v / major)) < 1e-6
        dr.line([(a, 0), (a, crop.height)], fill=(0, 120, 255, 150 if is_major else 55), width=2 if is_major else 1)
        if is_major:
            dr.text((a + 2, 2), f"{v:g}", fill=(0, 80, 220, 255), font=FONT)
        v += step
    v = yr[0] - (yr[0] % step)
    while v <= yr[1] + 1e-6:
        _, b = P(0, v)
        is_major = abs((v / major) - round(v / major)) < 1e-6
        dr.line([(0, b), (crop.width, b)], fill=(255, 60, 0, 150 if is_major else 55), width=2 if is_major else 1)
        if is_major:
            dr.text((2, b + 1), f"{v:g}", fill=(220, 40, 0, 255), font=FONT)
        v += step
    crop.save(out, quality=92)


def overlay(ref, polys, out, crop_mm=None, zoom=1.0, color=(230, 0, 0)):
    im = ref.im.copy()
    dr = ImageDraw.Draw(im, "RGBA")
    for pts, closed in polys:
        q = [ref.px(x, y) for (x, y) in pts]
        if closed:
            q = q + [q[0]]
        dr.line(q, fill=color + (210,), width=2)
    if crop_mm:
        (xa, xb), (ya, yb) = crop_mm
        x0, y1 = ref.px(xa, yb)
        x1, y0 = ref.px(xb, ya)
        im = im.crop((int(x0), int(y1), int(x1), int(y0)))
    if zoom != 1.0:
        im = im.resize((int(im.width * zoom), int(im.height * zoom)), Image.LANCZOS)
    im.save(out, quality=92)


def pxgrid(path, box, zoom, out, step=10):
    """Ham piksel izgarasi (kalibrasyon noktalarini okumak icin)."""
    im = Image.open(path).convert("RGB").crop(box)
    im = im.resize((int(im.width * zoom), int(im.height * zoom)), Image.LANCZOS)
    dr = ImageDraw.Draw(im, "RGBA")
    x = box[0] - box[0] % step
    while x <= box[2]:
        a = (x - box[0]) * zoom
        major = x % (step * 5) == 0
        dr.line([(a, 0), (a, im.height)], fill=(0, 120, 255, 150 if major else 50), width=1)
        if major:
            dr.text((a + 2, 2), str(x), fill=(0, 80, 220, 255), font=FONT)
        x += step
    y = box[1] - box[1] % step
    while y <= box[3]:
        b = (y - box[1]) * zoom
        major = y % (step * 5) == 0
        dr.line([(0, b), (im.width, b)], fill=(255, 60, 0, 150 if major else 50), width=1)
        if major:
            dr.text((2, b + 1), str(y), fill=(220, 40, 0, 255), font=FONT)
        y += step
    im.save(out, quality=92)


if __name__ == "__main__":
    pxgrid(sys.argv[1], tuple(int(v) for v in sys.argv[2].split(",")), float(sys.argv[3]), sys.argv[4])

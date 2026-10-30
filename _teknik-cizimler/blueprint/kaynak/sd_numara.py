"""SD urun fotografina (assets/img/psd.jpg) sol kanada halka icinde model numarasi: kalip baskisi gibi hafif kabartma.

Cikti (onizleme, katalogda kullanilmaz): <katalog>/_foto-onerisi-sd/psd150.jpg, psd230.jpg, psd430.jpg
"""
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
KAT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(KAT, "assets", "img", "psd.jpg")
OUT = os.path.join(KAT, "_foto-onerisi-sd")
FONT = r"C:\Windows\Fonts\segoeuib.ttf" if os.path.exists(r"C:\Windows\Fonts\segoeuib.ttf") else os.path.join(KAT, "assets", "fonts", "ttf", "segoeuib.ttf")

CX, CY, R = 505, 1045, 124          # sol kanat yuzeyi (tam boy piksel)
ANGLE = 38                          # yazi egimi (derece, saat yonu tersine)


def mark(code, size=520):
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    c = size / 2
    d.ellipse((c - R, c - R, c + R, c + R), outline=255, width=14)
    f = ImageFont.truetype(FONT, 116)
    d.text((c, c + 4), code, font=f, fill=255, anchor="mm")
    return m.rotate(ANGLE, resample=Image.BICUBIC)


def emboss(img, m, x, y):
    """Kalip kabartmasi: ust-sol isik kenari, alt-sag golge (yumusak), hafif acik yuz."""
    size = m.size[0]
    box = (x - size // 2, y - size // 2, x + size // 2, y + size // 2)
    region = img.crop(box)
    soft = m.filter(ImageFilter.GaussianBlur(1.0))
    shadow = ImageChops.offset(m, 5, 6).filter(ImageFilter.GaussianBlur(4)).point(lambda v: int(v * 0.85))
    rim_lo = ImageChops.offset(soft, 2, 3).point(lambda v: int(v * 0.9))
    rim_hi = ImageChops.offset(soft, -2, -2).point(lambda v: int(v * 0.7))
    region = Image.composite(Image.new("RGB", region.size, (0, 0, 0)), region, shadow)
    region = Image.composite(Image.new("RGB", region.size, (8, 8, 8)), region, rim_lo)
    region = Image.composite(Image.new("RGB", region.size, (150, 150, 150)), region, rim_hi)
    # yuz: yukaridan asagi hafif koyulasan gri (yuvarlak kabartma hissi)
    grad = Image.linear_gradient("L").resize(region.size).point(lambda v: 70 - int(v * 0.12))
    face = Image.merge("RGB", (grad, grad, grad))
    inner = ImageChops.offset(soft, 1, 1)
    region = Image.composite(face, region, inner.point(lambda v: int(v * 0.95)))
    img.paste(region, box)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    for code in ("150", "230", "430"):
        img = Image.open(SRC).convert("RGB")
        img = emboss(img, mark(code), CX, CY)
        img.save(os.path.join(OUT, f"psd{code}.jpg"), quality=92)
        print(code)


if __name__ == "__main__":
    main()

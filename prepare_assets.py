"""Katalog gorsellerini hazirlar: indirir / kopyalar, kirpar, baski icin buyutur.

Calistirma:  python prepare_assets.py
Cikti:       assets/img/<anahtar>.jpg
"""
import os
import sys
import urllib.request
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "assets", "src")
OUT = os.path.join(HERE, "assets", "img")
E = "E:/03 Novibrasyon Marin/"
SHOP = "https://cdn.shopify.com/s/files/1/0698/5328/2531/files/"

# Renkler styles.css ile ayni olmali: --panel (urun zemini) ve --paper (kirik beyaz sayfa)
PANEL = (236, 235, 230)
PAPER = (247, 246, 242)
# Kaynak gorselin kenarindan kirpilacak oran (gorselin icinde cerceve varsa)
INSET = {"bronze": 0.07}
# Kaynakta once uygulanan kirpma kutusu (x0, y0, x1, y1) — piksel
CROP = {
    "ship": (0, 0, 2752, 1352),        # sag alttaki yapay zeka filigranini disarida birak
    "d200": (66, 26, 792, 1035),       # teknik foyden sadece olcu gorunusleri (egriler vektor cizilir)
}
# Kaynakta beyazla kapatilacak alanlar: saildrive semalarindaki on takoz numaralari
# (on takoz modeli motora gore degisir; katalog metni dogru modeli verir)
LAYOUT_MASK = [(600, 40, 910, 212), (600, 728, 910, 943)]
MASK = {"lsd150": LAYOUT_MASK, "lsd230": LAYOUT_MASK, "lsd430": LAYOUT_MASK}
# Gri studyo fonlu cizimler: kirpmada kenar gurultusu asindirilir
GREY_BG = {"dvv1", "dvv2", "dvv3"}
# Bu gorseller elle / ayri betikle uretilir, prepare_assets.py uzerine yazmaz
KEEP = {"psd"}

# anahtar: (kaynak, islem)   islem: prod = urun fotografi (panel rengine oturtulur)
#                                    draw = teknik cizim (beyaz kalir)
#                                    photo = ortam fotografi (sadece boyut)
ASSETS = {
    # --- Urun fotograflari
    "p50": (SHOP + "novibrasyon-marin-yanmar-1gm-engine-mount-50kg-front-a1b2c3d4.jpg", "prod"),
    "p70": (SHOP + "novibrasyon-marin-yanmar-1gm-engine-mount-70kg-rear-gearbox-oem-replacement-a1b2c3d4_f5608fe1-71ec-4fa8-a073-82a1d327c4bd.jpg", "prod"),
    "p75": (SHOP + "novibrasyon-marin-yanmar-engine-mount-75-a1b2c3d4_1a243d8e-e91c-4db7-860c-3c4862d7b53d.jpg", "prod"),
    "p75s": (SHOP + "novibrasyon-marin-yanmar-engine-mount-stainless-steel-75a3b1c2.jpg", "prod"),
    "p100": (SHOP + "novibrasyon-marin-engine-mount-100-3ym-3gm-3jh-3fm-128270-08341-a1b2c3.jpg", "prod"),
    "p100s": (SHOP + "novibrasyon-marin-yanmar-engine-mount-stainless-steel-rubber-100-3ym-3gm-3jh-128270-08341-a1b2c3_25e24766-fc32-4d6c-97bc-ba748d64b990.jpg", "prod"),
    "p150": (SHOP + "novibrasyon-marin-engine-mount-121370-08351-a1b2c3_a14af204-ba68-49df-95af-887213b0756a.jpg", "prod"),
    "p150s": (SHOP + "novibrasyon-marin-yanmar-engine-mount-stainless-steel-121370-08351-a1b2c3.jpg", "prod"),
    "p200": (SHOP + "novibrasyon-marin-yanmar-engine-mount-200-4jh-a1b2c3d4.jpg", "prod"),
    "p200s": (SHOP + "novibrasyon-marin-yanmar-engine-mount-stainless-steel-200kg-a1b2c3d4.jpg", "prod"),
    # Dogru "no / vibrasyon / .com" kabartmali X tipi saildrive takozu (SD40/SD50 196440-02380 ilani).
    # Not: E: arsivindeki "Saildrive On Takoz (X Tipi).jpg" farkli markali bir urun, kullanmayin.
    "psd": (SHOP + "novibrasyon-marin-yanmar-engine-mount-196440-02380-a1b2c3.jpg", "prod"),
    "p400": (SHOP + "novibrasyon-marin-yanmar-engine-mount-a1b2c3d4_10e2420e-43fc-48e6-ba89-22231561b916.jpg", "prod"),
    "p450": (SHOP + "novibrasyon-marin-cummins-engine-mount-m20-3349230-a1b2c3_ef752400-9a97-4a71-b9d6-8319828d890c.jpg", "prod"),
    "p500": (SHOP + "novibrasyon-marin-yanmar-engine-mount-119773-08310-a1b2c3.jpg", "prod"),
    "p600": (SHOP + "novibrasyon-marine-engine-mount-3964883-4931364-a1b2c3.jpg", "prod"),
    "pvv1": (SHOP + "novibrasyon-marin-engine-mount-100kg-16mm-stud-vibration-isolator-a1b2c3_c056c6da-8bfe-4846-bc05-769f07d21acc.jpg", "prod"),
    "pvv1s": (SHOP + "novibrasyon-marin-vv1-stainless-engine-mount-a1b2c3.jpg", "prod"),
    "pvv2": (SHOP + "novibrasyon-marin-engine-mount-300kg-rubber-vibration-isolator-a1b2c3_92d53926-b0c0-4b33-a21c-c1ea01c1b9f6.jpg", "prod"),
    "pvv2s": (SHOP + "novibrasyon-marin-stainless-engine-mount-300kg-65shore-a1b2c3d4.jpg", "prod"),
    "pvv3": (SHOP + "novibrasyon-marin-engine-mount-500kg-20mm-stud-a1b2c3.jpg", "prod"),
    "pmt1": (SHOP + "novibrasyon-marin-mt1-engine-mount-vibration-isolator-a1b2c3d4.jpg", "prod"),
    "pmt2": (SHOP + "novibrasyon-marin-engine-mount-mt2-vibration-dampener-a1b2c3.jpg", "prod"),
    "pmt3": (SHOP + "novibrasyon-marin-engine-mount-mt3-vibration-isolator-a1b2c3_3300939c-c259-4322-8afd-3ff4db854b54.jpg", "prod"),
    # --- Teknik cizimler
    "d50": (SHOP + "novibrasyon-marin-yanmar-1gm-motor-mount-50kg-front-oem-replacement-128170-08340-a1b2c3d4_cba9a8cb-28f2-40df-a393-fa10076ad8a0.jpg", "draw"),
    "d70": (SHOP + "novibrasyon-marin-yanmar-1gm-motor-mount-70kg-rear-gearbox-oem-replacement-128170-08350-a1b2c3d4_cde64ff1-40a4-4606-b099-a7f3d89e56ab.jpg", "draw"),
    "d75": (SHOP + "novibrasyon-marin-yanmar-engine-mount-75-a1b2c3d4_dd88234f-6bcc-48f5-abe8-ecf19016b900.jpg", "draw"),
    "d100": (SHOP + "novibrasyon-marin-engine-mount-128270-08341-a1b2c3d4.jpg", "draw"),
    "d150": (SHOP + "novibrasyon-marin-engine-mount-121370-08351-a1b2c3.jpg", "draw"),
    "d200": (E + "02 Teknik Çizimler/Saildrive Takoz 200 - Teknik Veri Föyü.png", "draw"),
    "d400": (SHOP + "novibrasyon-marin-yanmar-engine-mount-519175-08300-a1b2c3.jpg", "draw"),
    "d450": (SHOP + "novibrasyon-marin-cummins-engine-mount-m20-3349230-a1b2c3d4.jpg", "draw"),
    "d500": (SHOP + "novibrasyon-marin-yanmar-engine-mount-vibration-isolator-a1b2c3d4.jpg", "draw"),
    "d600": (SHOP + "novibrasyon-marine-engine-mount-cummins-3964883-4931364-a1b2c3_cdfca2a6-5661-47b1-9a97-577458712428.jpg", "draw"),
    "dvv1": (E + "02 Teknik Çizimler/Konik Takoz M16 - 120 mm/Konik M16-120 - Çizim Logolu (4000px).png", "draw"),
    "dvv2": (E + "02 Teknik Çizimler/Konik Takoz M16 - 184 mm/Konik M16-184 - Çizim Logolu (4000px).png", "draw"),
    "dvv3": (E + "02 Teknik Çizimler/Konik Takoz M20 - 228 mm/Konik M20-228 - Çizim Logolu (4000px).png", "draw"),
    "dmt1": (SHOP + "novibrasyon-marin-mt1-engine-mount-drawing-a1b2c3d4.jpg", "draw"),
    "dmt2": (SHOP + "novibrasyon-marin-mt2-engine-mount-drawing-a1b2c3d4.jpg", "draw"),
    "dmt3": (SHOP + "novibrasyon-marin-mt3-engine-mount-drawing-a1b2c3d4_240537dc-6e25-45ee-8b91-8ea9e419e5db.jpg", "draw"),
    # --- Egriler
    "c75a": (SHOP + "novibrasyon-marin-engine-mount-frequency-curve-a1b2c3d4_a03b950d-312d-4d46-8a93-fa3fd3aa77aa.jpg", "draw"),
    "c75b": (SHOP + "novibrasyon-marin-engine-mount-load-deflection-curve-a1b2c3d4_16791e9a-7c0d-4a8c-ac5d-8c06071c0d1b.jpg", "draw"),
    "c100a": (SHOP + "novibrasyon-marin-engine-mount-frequency-curve-a1b2c3d4_a207dad9-8599-4d7d-9c94-1c4cc6b2386b.jpg", "draw"),
    "c100b": (SHOP + "novibrasyon-marin-engine-mount-load-deflection-curve-graph-a1b2c3.jpg", "draw"),
    "c150a": (SHOP + "novibrasyon-marin-150-engine-mount-frequency-curve-a1b2c3.jpg", "draw"),
    "c150b": (SHOP + "novibrasyon-marin-150-engine-mount-load-deflection-curve-a1b2c3.jpg", "draw"),
    "cvv1": (SHOP + "novibrasyon-marin-engine-mount-load-chart-a1b2c3d4_f9e32e16-9437-44e1-94e3-4a27e3c8e032.jpg", "draw"),
    "cvv2": (SHOP + "novibrasyon-marin-engine-mount-load-chart-a1b2c3_b0b90bef-01d0-4575-bdf8-f871c5dc8843.jpg", "draw"),
    "cvv3": (SHOP + "novibrasyon-marin-engine-mount-load-chart-a1b2c3d4_2d0c932e-a624-451d-b413-85a1d1918f15.jpg", "draw"),
    # --- Saildrive yerlesim semalari
    "lsd150": (E + "03 Saildrive Yerleşim Şemaları/SD150 - Takoz 100.png", "draw"),
    "lsd230": (E + "03 Saildrive Yerleşim Şemaları/SD230 - Takoz 100.png", "draw"),
    "lsd430": (E + "03 Saildrive Yerleşim Şemaları/SD430 - Takoz 200.png", "draw"),
    # --- Ortam / bolum gorselleri
    "cover": (SHOP + "novibrasyon-marin-yanmar-engine-mount-196440-02380-a1b2c3_ca34f97e-be79-4548-8804-58a9a8b86443.jpg", "prod"),
    "welcome": (E + "04 Yapay Zeka Görselleri/Ürün ve Atölye Sahneleri/Atölye - Koli ve Dört Takoz (filigransız).png", "photo"),
    "div1": (E + "08 Sunum ve Tasarımlar/Deck Görselleri/deck.png", "photo"),
    "div2": (E + "01 Ürün Fotoğrafları/Saildrive Üçlü Setler/Saildrive Üçlü Set 100.png", "prod"),
    "div3": (E + "04 Yapay Zeka Görselleri/Ürün ve Atölye Sahneleri/Blok Takoz Dörtlü Set (AI) 1.png", "prod"),
    "div4": (SHOP + "novibrasyon-marin-stainless-steel-engine-mounts-55kg-a1b2c3.jpg", "prod"),
    "ship": (E + "04 Yapay Zeka Görselleri/Kargo ve Teslimat/Novibrasyon Logolu Araç - Koliler.png", "photo"),
    "boxes": (E + "08 Sunum ve Tasarımlar/Canva Tasarımları/2026-05-13 Canva Tasarım - Novibrasyon Kutuları.png", "photo"),
    "bronze": (SHOP + "novibrasyon-marin-bronze-shaft-bearings-a1b2c3d4_34312d73-6590-4731-9ae9-ede02793d526.jpg", "prod"),
    "fiber": (SHOP + "novibrasyon-marin-fiber-shaft-bearing-a1b2c3d4.jpg", "prod"),
}


def fetch(key, src):
    """Kaynagi assets/src altina kopyalar; yerel dosya yolunu dondurur."""
    ext = os.path.splitext(src.split("?")[0])[1].lower() or ".jpg"
    local = os.path.join(SRC, key + ext)
    if os.path.exists(local):
        return local
    if src.startswith("http"):
        req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=120).read()
    else:
        with open(src, "rb") as f:
            data = f.read()
    with open(local, "wb") as f:
        f.write(data)
    return local


def flatten(im):
    im = ImageOps.exif_transpose(im)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        return bg.convert("RGB")
    return im.convert("RGB")


def white_point(im):
    """Kose yamalarindan arka plan beyazini tahmin eder."""
    w, h = im.size
    s = max(6, min(w, h) // 40)
    vals = []
    for box in ((0, 0, s, s), (w - s, 0, w, s), (0, h - s, s, h), (w - s, h - s, w, h)):
        g = im.crop(box).convert("L")
        px = sorted(g.tobytes())
        vals.append(px[len(px) // 2])
    return max(200, min(vals))


def autocrop(im, thr, pad, erode=True):
    g = im.convert("L")
    mask = g.point(lambda v: 255 if v < thr else 0)
    if erode:
        mask = mask.filter(ImageFilter.MinFilter(3))
    bbox = mask.getbbox()
    if not bbox:
        return im
    x0, y0, x1, y1 = bbox
    p = int(max(x1 - x0, y1 - y0) * pad)
    x0, y0 = max(0, x0 - p), max(0, y0 - p)
    x1, y1 = min(im.width, x1 + p), min(im.height, y1 + p)
    return im.crop((x0, y0, x1, y1))


def upscale(im, min_long):
    long = max(im.size)
    if long >= min_long:
        return im
    f = min_long / long
    im = im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=2))


def downscale(im, max_long):
    if max(im.size) <= max_long:
        return im
    im = im.copy()
    im.thumbnail((max_long, max_long), Image.LANCZOS)
    return im


def edge_fade(im):
    """Kenarlari beyaza yumusatir ki panelle birlesim cizgisi gorunmesin."""
    w, h = im.size
    m = max(8, int(min(w, h) * 0.035))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rectangle((m, m, w - m, h - m), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(m / 2))
    return Image.composite(im, Image.new("RGB", (w, h), (255, 255, 255)), mask)


def crop_inside_frame(im, bottom):
    """Teknik foyun dis cercevesini ve alttaki tork / logo bandini atar."""
    g = im.convert("L")
    w, h = g.size
    px = g.load()

    def dark_ratio_col(x):
        return sum(1 for y in range(100, bottom - 20, 4) if px[x, y] < 110) / len(range(100, bottom - 20, 4))

    def dark_ratio_row(y):
        return sum(1 for x in range(100, w - 100, 4) if px[x, y] < 110) / len(range(100, w - 100, 4))

    left = next(x for x in range(0, w // 4) if dark_ratio_col(x) > 0.6)
    right = next(x for x in range(w - 1, 3 * w // 4, -1) if dark_ratio_col(x) > 0.6)
    top = next(y for y in range(0, h // 4) if dark_ratio_row(y) > 0.6)
    return im.crop((left + 8, top + 8, right - 7, bottom))


def process(key, path, mode):
    im = flatten(Image.open(path))
    if key in INSET:
        f = INSET[key]
        im = im.crop((int(im.width * f), int(im.height * f), int(im.width * (1 - f)), int(im.height * (1 - f))))
    if key in CROP:
        im = im.crop(CROP[key])
    if key in MASK:
        d = ImageDraw.Draw(im)
        for box in MASK[key]:
            d.rectangle(box, fill=(255, 255, 255))
    if mode == "prod":
        wp = white_point(im)
        if wp < 254:
            im = im.point(lambda v: min(255, round(v * 255 / wp)))
        im = autocrop(im, 236, 0.06)
        im = upscale(im, 2200)
        im = downscale(im, 3000)
        im = edge_fade(im)
        im = ImageChops.multiply(im, Image.new("RGB", im.size, PANEL))
        q = 90
    elif mode == "draw":
        wp = white_point(im)
        if wp < 254:
            im = im.point(lambda v: min(255, round(v * 255 / wp)))
        im = autocrop(im, 225, 0.03, erode=key in GREY_BG)   # gri fonlu cizimlerde kenar gurultusunu at
        im = upscale(im, 2000)
        im = downscale(im, 2800)
        im = ImageChops.multiply(im, Image.new("RGB", im.size, PAPER))
        q = 90
    else:
        im = upscale(im, 2600)            # tam sayfa fotograflar icin en az ~300 ppi
        im = downscale(im, 3000)
        q = 88
    out = os.path.join(OUT, key + ".jpg")
    im.save(out, "JPEG", quality=q, optimize=True, progressive=True)
    return im.size


def main():
    os.makedirs(SRC, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    only = set(sys.argv[1:])
    for key, (src, mode) in ASSETS.items():
        if only and key not in only:
            continue
        if key in KEEP and not only and os.path.exists(os.path.join(OUT, key + ".jpg")):
            print(f"{key:8s} (elle uretilen gorsel, atlandi)")
            continue
        path = fetch(key, src)
        size = process(key, path, mode)
        print(f"{key:8s} {mode:5s} {size[0]}x{size[1]}")


if __name__ == "__main__":
    main()

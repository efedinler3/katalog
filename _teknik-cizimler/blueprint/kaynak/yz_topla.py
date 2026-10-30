"""Tum yapay zeka urun fotograflarini tek klasorde urun urun toplar (kopyalar, kaynaklara dokunmaz).

Hedef: <katalog>/_yapay-zeka-fotograflar/<urun>/<kaynak>__<dosya>   + her klasorde _genel-bakis.jpg
Ayni goruntu (icerik ozeti ayni) bir kez alinir.
"""
import hashlib
import os
import re
import shutil

from PIL import Image, ImageDraw, ImageFont

KAT = r"C:\Users\sefed\Documents\Novibrasyon Katalog"
E = r"E:\03 Novibrasyon Marin"
OUT = os.path.join(KAT, "_yapay-zeka-fotograflar")
EXT = (".png", ".jpg", ".jpeg", ".webp")
PRODUCTS = ["50", "70", "75", "100", "150", "200", "400", "450", "500", "600", "sd", "vv1", "vv2", "vv3", "mt"]
ALIAS = {"sd150-sd230-sd430": "sd", "mt1-mt2-mt3": "mt"}


def norm(pid):
    pid = pid.lower()
    return ALIAS.get(pid, pid)


def images(folder):
    for root, _, files in os.walk(folder):
        for f in sorted(files):
            if f.lower().endswith(EXT) and not f.startswith("_onizleme"):
                yield os.path.join(root, f)


def main():
    seen = {}
    plan = []                                            # (hedef klasor, kaynak etiketi, dosya)
    # 1) E: 00 Yeni Yapay Zeka: dosya adi "<urun>-<sahne>.png"
    for sub in sorted(os.listdir(os.path.join(E, "00 Yeni Yapay Zeka"))):
        d = os.path.join(E, "00 Yeni Yapay Zeka", sub)
        if not os.path.isdir(d):
            continue
        for p in images(d):
            pid = norm(re.split(r"[-_ ]", os.path.basename(p))[0])
            plan.append((pid if pid in PRODUCTS else "_genel/" + sub, sub, p))
    # 2) katalog _foto-secim/<urun>/yapay-zeka
    fs = os.path.join(KAT, "_foto-secim")
    for sub in sorted(os.listdir(fs)):
        d = os.path.join(fs, sub, "yapay-zeka")
        if os.path.isdir(d):
            for p in images(d):
                plan.append((norm(sub), "foto-secim", p))
    # 3) katalog _ai-fotograf-adaylari/<urun>
    ad = os.path.join(KAT, "_ai-fotograf-adaylari")
    for sub in sorted(os.listdir(ad)):
        d = os.path.join(ad, sub)
        if os.path.isdir(d) and not sub.startswith("_"):
            for p in images(d):
                plan.append((norm(sub), "ai-adaylari", p))
    # 4) E: 04 Yapay Zeka Gorselleri: urun adi yok -> _genel/<kaynak>
    g = os.path.join(E, "04 Yapay Zeka Görselleri")
    for sub in sorted(os.listdir(g)):
        d = os.path.join(g, sub)
        if os.path.isdir(d):
            for p in images(d):
                plan.append(("_genel/" + sub, sub, p))

    counts = {}
    for target, label, src in plan:
        h = hashlib.md5(open(src, "rb").read()).hexdigest()
        if h in seen:
            continue
        seen[h] = src
        dst_dir = os.path.join(OUT, target)
        os.makedirs(dst_dir, exist_ok=True)
        name = f"{label}__{os.path.basename(src)}".replace(" ", "-")
        shutil.copy2(src, os.path.join(dst_dir, name))
        counts[target] = counts.get(target, 0) + 1
    for t in sorted(counts):
        overview(os.path.join(OUT, t))
        print(f"{counts[t]:4d}  {t}")
    print("toplam", sum(counts.values()), "farkli gorsel")


def overview(folder, tw=360):
    files = [f for f in sorted(os.listdir(folder)) if f.lower().endswith(EXT)]
    if not files:
        return
    cols = 5
    rows = (len(files) + cols - 1) // cols
    th = tw + 34
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * 10, rows * th + (rows + 1) * 10), "#e6e6e2")
    font = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 15)
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(files):
        x, y = 10 + (i % cols) * (tw + 10), 10 + (i // cols) * (th + 10)
        try:
            im = Image.open(os.path.join(folder, f)).convert("RGB")
            im.thumbnail((tw, tw))
            sheet.paste(im, (x + (tw - im.width) // 2, y + (tw - im.height) // 2))
        except OSError:
            pass
        d.text((x + 2, y + tw + 6), f"{i + 1}. {f[:44]}", fill="#222", font=font)
    sheet.save(os.path.join(folder, "_genel-bakis.jpg"), quality=85)


if __name__ == "__main__":
    main()

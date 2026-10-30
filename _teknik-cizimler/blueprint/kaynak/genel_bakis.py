"""Tum cizim sayfalarinin kucuk resimli genel bakisi: ../genel-bakis-<dil>.jpg (ya da verilen kodlar)."""
import os
import sys

from PIL import Image

from urunler import ORDER

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)


def main():
    lang = "tr"
    args = [a for a in sys.argv[1:]]
    if "--lang" in args:
        lang = args[args.index("--lang") + 1]
        args = [a for a in args if a not in ("--lang", lang)]
    out = None
    if "--out" in args:
        out = args[args.index("--out") + 1]
        args = [a for a in args if a not in ("--out", out)]
    codes = args or ORDER
    cols = 4 if len(codes) > 6 else min(3, len(codes))
    tw = 1000 if len(codes) > 6 else 1400
    th = int(tw * 0.8)
    rows = (len(codes) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * 16, rows * th + (rows + 1) * 16), "#d9dde0")
    for i, c in enumerate(codes):
        im = Image.open(os.path.join(OUT, lang, f"{c}.png")).convert("RGB")
        im.thumbnail((tw, th), Image.LANCZOS)
        sheet.paste(im, (16 + (i % cols) * (tw + 16), 16 + (i // cols) * (th + 16)))
    path = out or os.path.join(OUT, f"genel-bakis-{lang}.jpg")
    sheet.save(path, quality=86)
    print(path, sheet.size)


if __name__ == "__main__":
    main()

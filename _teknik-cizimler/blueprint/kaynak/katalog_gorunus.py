"""Katalog icin ayri on / ust gorunus gorselleri: cercevesiz, antetsiz, olcu yazilari buyuk.

Cikti: assets/img/<anahtar>-on[-tr].png ve <anahtar>-ust[-tr].png (beyaz kenarlar kirpilir).
Calistirma: python katalog_gorunus.py [kod ...] [--lang tr|en]
"""
import os
import subprocess
import sys

import pymupdf
from PIL import Image, ImageChops

import bp
from bp import Sheet, View

TXT_K = 5.3                     # olcu yazisi yuksekligi (mm, cizim sayfasinda 3,1)
bp.TXT = TXT_K
bp.AL, bp.AW = 4.0, 1.4
View.text.__defaults__ = (TXT_K,) + View.text.__defaults__[1:]
Sheet.text.__defaults__ = (TXT_K,) + Sheet.text.__defaults__[1:]
bp.LW.update({"thick": 0.6, "mid": 0.48, "thin": 0.28})

import families_cad as FCAD          # noqa: E402  (bp yamasindan sonra)
import make_blueprints as MB         # noqa: E402
from urunler import P                # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
KAT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
IMG = os.path.join(KAT, "assets", "img")
KEY = {"50": "d50", "70": "d70", "75": "d75", "100": "d100", "150": "d150", "200": "d200", "400": "d400",
       "450": "d450", "500": "d500", "600": "d600", "SD150": "dsd150", "SD230": "dsd230", "SD430": "dsd430",
       "VV1": "dvv1", "VV2": "dvv2", "VV3": "dvv3", "MT1": "dmt1", "MT2": "dmt2", "MT3": "dmt3"}


def white_to_alpha(im):
    """Beyaz zemini saydam yapar (renk-alfa): cizim katalogda sayfa zemininin rengini alir."""
    import numpy as np
    a = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
    alpha = np.clip((1.0 - a).max(axis=2), 0, 1)
    rgb = np.where(alpha[..., None] > 0, (a - (1.0 - alpha[..., None])) / np.maximum(alpha[..., None], 1e-6), 0)
    out = np.dstack([np.clip(rgb, 0, 1), alpha]) * 255.0
    return Image.fromarray(out.round().astype(np.uint8), "RGBA")


def trim(im, m=24):
    bg = Image.new("RGB", im.size, (255, 255, 255))
    box = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > 25 else 0).getbbox()
    return im.crop((max(0, box[0] - m), max(0, box[1] - m), min(im.width, box[2] + m), min(im.height, box[3] + m)))


FAMILY = [["50", "70", "75", "100", "150", "200"], ["SD150", "SD230", "SD430"], ["400", "450", "500", "600"],
          ["VV1", "VV2", "VV3"], ["MT1", "MT2", "MT3"]]


def family_scale(code):
    """Ayni ailede tek olcek: urunler katalogda birbirine gore gercek boyda gorunur."""
    fam = next(f for f in FAMILY if code in f)
    return min(MB.layout_cad(dict(P[c], code=c))[0] for c in fam)


def render(code, lang):
    p = dict(P[code], code=code)
    L = dict(MB.LANG[lang], minh="MİN." if lang == "tr" else "MIN.")
    _, fo, po = MB.layout_cad(p)
    s = family_scale(code)
    shF, shP, shI = Sheet(400, 300), Sheet(400, 300), Sheet(400, 300)
    f = View(shF, fo[0] + 40, fo[1] + 20, s)
    pl = View(shP, po[0] + 40, po[1] - 60, s)
    FCAD.draw_cad(f, pl, View(shI, 200, 150, 1.0), p, L)
    tmp = os.path.join(HERE, "_gorunus")
    os.makedirs(tmp, exist_ok=True)
    html = os.path.join(tmp, f"{code}-{lang}.html")
    pages = "".join(f"<div class='pg'>{sh.svg()}</div>" for sh in (shF, shP))
    with open(html, "w", encoding="utf-8") as fh:
        fh.write("<!doctype html><html><head><meta charset='utf-8'><style>@page{size:400mm 300mm;margin:0}"
                 "html,body{margin:0}.pg{width:400mm;height:300mm;page-break-after:always;overflow:hidden}"
                 "svg{display:block}</style></head><body>" + pages + "</body></html>")
    pdf = html[:-5] + ".pdf"
    exe = next(c for c in MB.CHROME if os.path.exists(c))
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                    f"--print-to-pdf={pdf}", "file:///" + html.replace("\\", "/")], check=True, capture_output=True)
    doc = pymupdf.open(pdf)
    suf = "-tr" if lang == "tr" else ""
    for i, part in enumerate(("on", "ust")):
        pix = doc[i].get_pixmap(dpi=260)
        im = trim(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
        white_to_alpha(im).save(os.path.join(IMG, f"{KEY[code]}-{part}{suf}.png"), optimize=True)
    doc.close()
    print(code, lang)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    langs = [sys.argv[sys.argv.index("--lang") + 1]] if "--lang" in sys.argv else ["tr", "en"]
    if "--lang" in sys.argv:
        args = [a for a in args if a not in langs]
    for c in args or list(KEY):
        for lg in langs:
            render(c, lg)

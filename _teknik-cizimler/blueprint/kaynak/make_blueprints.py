"""Novibrasyon takozlari: tek tip teknik cizim (blueprint) sayfalari.

Olculer: Ellebogen teknik foyleri (50, 70, 75, 100, 150, 200, SD 150/230/430, GT-S = VV1, GT-M = VV2),
VV3 Novibrasyon cizimi, Ellebogen karsiligi olmayanlar (400, 450, 500, 600, MT1-3) sitedeki / katalogdaki cizimler.
Calistirma:  python make_blueprints.py [kod ...] [--lang tr|en]
Cikti:       ../<dil>/<kod>.svg, .png (3000 x 2400), ../novibrasyon-teknik-cizimler-<dil>.pdf
"""
import base64
import math
import os
import subprocess
import sys

import pymupdf

from bp import Sheet, View, fmt, LW, INK
import families as F
import families2 as F2
import families3 as F3

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
KAT = os.path.dirname(os.path.dirname(OUT))
CHROME = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
          r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
          "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"]

LANG = {
    "tr": dict(minh="MİN. YÜKSEKLİK", front="ÖN GÖRÜNÜŞ", top="ÜST GÖRÜNÜŞ", iso="İZOMETRİK GÖRÜNÜŞ", model="MODEL", desc="TANIM",
               stud="SAPLAMA", refs="MUADİL / REFERANS", units="BİRİM / İZDÜŞÜM", date="TARİH",
               mount="Deniz motoru takozu", code="tr", load="MAKS. YÜK", sheet="SAYFA"),
    "en": dict(minh="MIN. HEIGHT", front="FRONT VIEW", top="TOP VIEW", iso="ISOMETRIC VIEW", model="MODEL", desc="DESCRIPTION",
               stud="STUD", refs="REPLACES / REFERENCE", units="UNITS / PROJECTION", date="DATE",
               mount="Marine engine mount", code="en", load="MAX. LOAD", sheet="SHEET"),
}

from urunler import P, ORDER


def logo_data():
    with open(os.path.join(KAT, "assets", "logo-ink.png"), "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode()


LOGO = logo_data()


def extents(p):
    """On gorunus dikey kapsam (y_min, y_max) ve ust gorunus derinligi, genislik."""
    fam = p.get("kind", p["family"])
    if fam == "sd":
        return -p["bot_stud"], p["H"] + p["top_stud"], p["W"], p["L"]
    if fam == "mt":
        from parts import T as TT
        t = TT[p["thread"]]
        return 0.0, p["support"] + t["wt"] + p["upper_gap"] + t["h"] + t["d"] * 1.6, p["W"], p["L"]
    return 0.0, p["total"], p["W"], p["L"]


def layout(p):
    y0, y1, W, Lb = extents(p)
    avail_h = 205.0 - 16 - 20 - 12 - 22
    s = min(avail_h / ((y1 - y0) + W), 222.0 / Lb, 1.6)
    s = math.floor(s * 20) / 20
    fx = 140.0
    fy = 18 + (y1) * s + 6
    py = fy - y0 * s + 22 + W / 2 * s + 10
    return s, (fx, fy), (fx, py)


def layout_cad(p):
    """Sol sutun: on + ust gorunus (genislik ~170 mm), sag sutun izometrik."""
    y0, y1, W, Lb = extents(p)
    s = min((203.0 - 66.0) / ((y1 - y0) + W), 128.0 / Lb, 1.6)
    s = math.floor(s * 20) / 20
    fx = 18 + Lb / 2 * s + 4
    fy = 18 + y1 * s + 6
    py = fy - y0 * s + 22 + W / 2 * s + 10
    return s, (fx, fy), (fx, py)


def title_block(sh, code, p, L):
    x0, y0, x1, y1 = 150.0, 207.0, 294.0, 234.0
    sh.rect(x0, y0, x1 - x0, y1 - y0, "thick", "#ffffff")
    r1, r2 = y0 + 10.0, y0 + 18.5
    xa, xb = x0 + 50.0, x0 + 95.0
    for (a, b, c, d) in ((x0, r1, x1, r1), (x0, r2, x1, r2), (xa, y0, xa, r1), (xb, y0, xb, y1)):
        sh.line(a, b, c, d, "mid")
    sh.add(f'<image href="{LOGO}" x="{x0 + 2.5}" y="{y0 + 2.2}" width="45" height="{45 * 290 / 1492:.2f}"/>')
    lab = lambda x, y, s: sh.text(x, y, s, 1.75, "start", 400, ls=0.25)
    lab(xa + 1.5, y0 + 2.6, L["model"])
    sh.text(xa + 1.5, r1 - 1.3, f"NOVIBRASYON {code}", 4.2, "start", 600)
    lab(xb + 1.5, y0 + 2.6, L["stud"])
    sh.text(xb + 1.5, y0 + 6.6, p["thread_txt"], 3.0, "start", 600)
    lab(x0 + 1.5, r1 + 2.6, L["desc"])
    desc = p.get("desc", "")
    desc = desc[L["code"]] if isinstance(desc, dict) else desc
    sh.text(x0 + 1.5, r2 - 1.3, f'{L["mount"]} · {desc}'.rstrip(" ·"), 2.6, "start")
    lab(xb + 1.5, r1 + 2.6, L["units"])
    sh.text(xb + 1.5, r2 - 1.3, "mm · 1. açı (ISO E)" if L is LANG["tr"] else "mm · 1st angle (ISO E)", 2.4, "start")
    proj_symbol(sh, x1 - 11.5, (r1 + r2) / 2 + 0.6)
    lab(x0 + 1.5, r2 + 2.6, L["refs"])
    sh.text(x0 + 1.5, y1 - 1.5, p.get("refs", "-"), 2.3, "start")
    lab(xb + 1.5, r2 + 2.6, L["date"])
    sh.text(xb + 1.5, y1 - 1.5, "2026-10-20 · novibrasyon.com", 2.3, "start")


def proj_symbol(sh, cx, cy):
    """1. aci izdusum sembolu: kesik koni (sag) + ic ice iki daire (sol)."""
    sh.add(f'<path class="mid" d="M{cx + 1.2:.2f},{cy - 1.6:.2f} L{cx + 6.2:.2f},{cy - 2.8:.2f} L{cx + 6.2:.2f},{cy + 2.8:.2f} '
           f'L{cx + 1.2:.2f},{cy + 1.6:.2f} Z"/>')
    sh.add(f'<circle class="mid" cx="{cx - 3.4:.2f}" cy="{cy:.2f}" r="2.8"/><circle class="mid" cx="{cx - 3.4:.2f}" '
           f'cy="{cy:.2f}" r="1.6"/>')
    sh.line(cx - 7.2, cy, cx + 7.4, cy, "cen")


def sheet_for(code, lang):
    p = dict(P[code], code=code)
    L = LANG[lang]
    sh = Sheet()
    sh.rect(5, 5, 290, 230, "thick")
    y0, y1, W, Lb = extents(p)
    if p["family"] == "cad":
        import families_cad as FCAD
        s, fo, po = layout_cad(p)
        front = View(sh, fo[0], fo[1], s)
        plan = View(sh, po[0], po[1], s)
        pr = FCAD.projections(p)
        ix0, iy0, ix1, iy1 = FCAD.bbox(pr["iso"][0])
        import charts as CHT
        if CHT.draw_charts(sh, code, lang):              # sag ust: yuk-cokme + dogal frekans, altinda izometrik
            si = min(100.0 / (ix1 - ix0), 98.0 / (iy1 - iy0))
            iso = View(sh, 241.0, 148.0, si)
            sh.text(188, 88, L["iso"], 2.4, "start", 600, ls=0.4)
        else:
            si = min(92.0 / (ix1 - ix0), 120.0 / (iy1 - iy0))
            iso = View(sh, 244.0, 92.0, si)
            sh.text(198, 14, L["iso"], 2.4, "start", 600, ls=0.4)
        FCAD.draw_cad(front, plan, iso, p, L)
    else:
        s, fo, po = layout(p)
        front = View(sh, fo[0], fo[1], s)
        plan = View(sh, po[0], po[1], s)
        fn = getattr(F3, "draw_" + p["family"], None) or getattr(F2, "draw_" + p["family"], None) or getattr(F, "draw_" + p["family"])
        fn(front, plan, p, L)
    sh.text(12, 14, L["front"], 2.4, "start", 600, ls=0.4)
    sh.text(12, po[1] - W / 2 * s - 12, L["top"], 2.4, "start", 600, ls=0.4)
    title_block(sh, code, p, L)
    return sh


def render(codes, lang):
    od = os.path.join(OUT, lang)
    os.makedirs(od, exist_ok=True)
    pages = []
    for c in codes:
        svg = sheet_for(c, lang).svg()
        with open(os.path.join(od, f"{c}.svg"), "w", encoding="utf-8") as fh:
            fh.write(svg)
        pages.append(svg)
    font = "file:///C:/Windows/Fonts/bahnschrift.ttf"
    html = ("<!doctype html><html><head><meta charset='utf-8'><style>"
            f"@font-face{{font-family:Bahnschrift;src:url('{font}')}}"
            "@page{size:300mm 240mm;margin:0} html,body{margin:0;padding:0} "
            ".pg{width:300mm;height:240mm;page-break-after:always;overflow:hidden} svg{display:block}"
            "</style></head><body>" + "".join(f"<div class='pg'>{s}</div>" for s in pages) + "</body></html>")
    hp = os.path.join(HERE, f"_sayfalar-{lang}.html")
    with open(hp, "w", encoding="utf-8") as fh:
        fh.write(html)
    pdf = os.path.join(OUT, f"novibrasyon-teknik-cizimler-{lang}.pdf")
    exe = next(c for c in CHROME if os.path.exists(c))
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                    "--virtual-time-budget=15000", f"--print-to-pdf={pdf}", "file:///" + hp.replace("\\", "/")],
                   check=True, capture_output=True)
    doc = pymupdf.open(pdf)
    for i, c in enumerate(codes):
        pix = doc[i].get_pixmap(dpi=254)
        pix.save(os.path.join(od, f"{c}.png"))
    print(lang, len(codes), "sayfa ->", pdf)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    lang = "tr"
    if "--lang" in sys.argv:
        lang = sys.argv[sys.argv.index("--lang") + 1]
        args = [a for a in args if a != lang]
    codes = args or ORDER
    render(codes, lang)


if __name__ == "__main__":
    main()

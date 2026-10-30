"""Novibrasyon katalogunu uretir: HTML -> PDF (Chrome ile).

Kullanim:
    python build.py                # Turkce + Ingilizce: A4, baski (3 mm tasma) ve e-posta PDF'leri
    python build.py --lang tr      # yalnizca Turkce
    python build.py --lang en      # yalnizca Ingilizce
    python build.py --lang tr --html   # sadece HTML (onizleme icin)

Fotograf slotlari: fotograflar/<urun>/1.jpg, 2.jpg, 3.jpg  (jpg / jpeg / png / webp)
Turkce metinler: ceviri-tr.json
"""
import base64
import html
import json
import math
import os
import re
import subprocess
import sys

from PIL import Image

from data import COMPANY, FINDER, FINDER_2, FINDER_3, PRODUCTS, SECTIONS, SHIPPING, FINISHES
from i18n import COLLECT, LANG, MISSING, SEEN, T, Tf, where

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = "assets/img/"
PHOTOS = "fotograflar"
CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
]
NB = "\u00a0"

# ---------------------------------------------------------------------------
# Yardimcilar
# ---------------------------------------------------------------------------
ICONS = {
    "check": '<circle cx="12" cy="12" r="10"/><path d="m8 12.5 2.8 2.8L16.5 9.5"/>',
    "camera": '<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/>',
    "chat": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/><path d="M9 10h.01M12 10h.01M15 10h.01"/>',
    "mail": '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
    "truck": '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
    "waves": '<path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "insta": '<rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><path d="M17.5 6.5h.01"/>',
    "pin": '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
    "arrow": '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>',
}
MOBILE = False          # mobil surum: sayfa numarasi yerine dokunulabilir baglanti


def e(text):
    """HTML kacisi + ' · ' ayiraclarinin satir basina dusmemesi.
    Turkcede buyuk harfe cevrilen yerlerde marka logodaki gibi NOVIBRASYON kalsin (NOVİBRASYON degil)."""
    out = html.escape(str(text)).replace(" · ", NB + "· ")
    if LANG == "tr":
        out = re.sub(r"\b(Novibrasyon|[Ss]aildrive|Cummins)\b", r'<span lang="en">\1</span>', out)
    return out


def em(text):
    """Model listeleri: her kod bir butun ('4JH-TE', 'QSB 5.9' satir sonunda bolunmez)."""
    out = e(text)
    out = re.sub(r"\b([0-9A-Z][0-9A-Za-z]*) (\d[\d.]*)\b", "\\1" + NB + "\\2", out)
    return re.sub(r"(?<![\w-])([0-9A-Za-z]+(?:[-/][0-9A-Za-z]+)+)", r'<span class="nw">\1</span>', out)


def icon(name, cls=""):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')


def img_size(key):
    with Image.open(os.path.join(HERE, IMG, key + ".jpg")) as im:
        return im.size


def aspect(key):
    w, h = img_size(key)
    return w / h


def pname(pid):
    p = PRODUCTS[pid]
    return p.get("name") or f"Novibrasyon {p['code']}"


def short_code(pid):
    return PRODUCTS[pid]["code"]


def logo_variants():
    """logo.png (siyah, seffaf) -> renkli logolar; 'head' = sloganisiz (ust bilgi icin)."""
    base = Image.open(os.path.join(HERE, "assets", "logo.png")).convert("RGBA")
    alpha = base.getchannel("A")
    head_alpha = alpha.copy()
    head_alpha.paste(0, (440, 200, base.width, base.height))       # "MARINE ENGINE MOUNTS" satiri
    out = {}
    for name, rgb in {"ink": (14, 26, 29), "teal": (18, 56, 63), "white": (255, 255, 255)}.items():
        for variant, a in (("", alpha), ("-head", head_alpha)):
            path = os.path.join(HERE, "assets", f"logo-{name}{variant}.png")
            if not os.path.exists(path):
                im = Image.new("RGBA", base.size, rgb + (0,))
                im.putalpha(a)
                im = im.crop(im.getbbox())
                im.save(path)
            out[name + variant] = f"assets/logo-{name}{variant}.png"
    return out


def font_css():
    """Statik Inter fontlari varsa onlari (PDF'te gercek font olarak gomulur), yoksa degisken fontu gomer."""
    static_dir = os.path.join(HERE, "assets", "fonts", "static")
    static_css = os.path.join(static_dir, "fonts-static.css")
    if os.path.exists(static_css):
        css = open(static_css, encoding="utf-8").read()
        base_dir = static_dir
    else:
        css = open(os.path.join(HERE, "assets", "fonts", "fonts.css"), encoding="utf-8").read()
        base_dir = os.path.join(HERE, "assets", "fonts")

    def embed(m):
        fn = m.group(1)
        data = base64.b64encode(open(os.path.join(base_dir, fn), "rb").read()).decode()
        return f"url(data:font/woff2;base64,{data})"
    return re.sub(r"url\(['\"]?([^'\")]+\.woff2)['\"]?\)", embed, css)


def localize_data():
    """Urun, bolum ve ortak metinleri secili dile cevirir (motor bulucu cizim aninda cevrilir)."""
    global SHIPPING, FINISHES
    where("sections")
    for sec in SECTIONS:
        sec["title"], sec["intro"] = T(sec["title"]), T(sec["intro"])
    SHIPPING[:] = [T(s) for s in SHIPPING]
    FINISHES[:] = [(k, T(t), T(d)) for k, t, d in FINISHES]
    for pid, p in PRODUCTS.items():
        where(pid)
        for k in ("name", "title", "tagline", "intro", "fits_note", "refs_head", "refs_note", "note",
                  "variants_note", "load"):
            if p.get(k):
                p[k] = T(p[k])
        p["hero"] = [(k, T(c)) for k, c in p["hero"]]
        for g in p.get("fits", []):
            g["label"] = T(g.get("label", ""))
            g["models"] = [T(m) for m in g["models"]]
            if g.get("tag"):
                g["tag"] = T(g["tag"])
        p["features"] = [T(f) for f in p.get("features", [])]
        p["dimrows"] = [(T(k), T(v)) for k, v in p.get("dimrows", [])]
        for key in ("variants", "mounting"):
            if p.get(key):
                heads, rows = p[key]
                if len(heads) != 2:              # 2 sutunlu Shore / yuk karolari cizimde cevrilir
                    rows = [[T(c) for c in r] for r in rows]
                p[key] = ([T(h) for h in heads], rows)
        d = p["dims"]
        if d.get("caption"):
            d["caption"] = T(d["caption"])
        if d.get("labels"):
            d["labels"] = [T(x) for x in d["labels"]]
    where("ui")


localize_data()


def find_photo(pid, n):
    for ext in ("jpg", "jpeg", "png", "webp", "JPG", "JPEG", "PNG"):
        path = os.path.join(HERE, PHOTOS, pid, f"{n}.{ext}")
        if os.path.exists(path):
            return f"{PHOTOS}/{pid}/{n}.{ext}"
    return None


def load_curves(cid):
    if not cid:
        return None
    path = os.path.join(HERE, "assets", "curves", cid + ".json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Sayfa plani ve numaralar
# ---------------------------------------------------------------------------
PAGES = []
PAGE_OF = {}
MIN_TAIL_PHOTOS = 2        # arka sayfalardan once en az bu kadar tam sayfa fotograf (sahibinin secimleri dusmesin)
FINDER_PAGES = []


def full_page_photos():
    d = os.path.join(HERE, PHOTOS, "tam-sayfa")
    return sorted(f for f in os.listdir(d) if re.fullmatch(r"\d+\.(jpe?g|png|webp)", f, re.I)) if os.path.isdir(d) else []


def plan():
    """Sayfa plani. Her urun iki sayfalik bir acilim: sol (cift) sayfa + sag (tek) sayfa.
    Bolum ayraci saga duser; gerekirse soluna tam sayfa fotograf sayfasi konur.
    Toplam sayfa 4'un kati olsun diye arka sayfalardan once fotograf sayfalari eklenir."""
    pages = [("cover", None)] + ([("about", None), ("aboutR", None)] if ABOUT else []) + [("welcome", None), ("tech", None)]
    pages += [("finderT", k) for k in range(len(FINDER_PAGES))]
    pages += [("partnos", None), ("layout", 0), ("layout", 1)]
    for sec in SECTIONS:
        if (len(pages) + 1) % 2 == 0:                 # siradaki sayfa sol: yorumlu fotograf + ayrac acilimi
            pages.append(("photo", sec))
        pages.append(("divider", sec))
        for k, pid in enumerate(sec["products"]):
            if k and k == sec.get("mid_photos"):        # uzun bolumun ortasinda iki sayfalik fotograf acilimi
                pages += [("photo", sec), ("photo", sec)]
            pages += [("prodL", pid), ("prodR", pid)]
    tail = [("bearings", None), ("back", None)]
    used = sum(1 for kd, _ in pages if kd == "photo")
    while used < len(full_page_photos()):             # kalan tam sayfa fotograflar arka sayfalardan once (sayi sarti yok)
        pages.append(("photo", None))
        used += 1
    return pages + tail


def setup():
    """Motor bulucuyu olcup sayfalar, sonra sayfa planini ve numaralari kurar."""
    FINDER_PAGES[:] = paginate_finder()
    PAGES[:] = plan()
    PAGE_OF.clear()
    PHOTO_NO.clear()
    for i, (kind, arg) in enumerate(PAGES, start=1):
        if kind == "prodL":
            PAGE_OF[arg] = i
        elif kind == "divider":
            PAGE_OF["sec-" + arg["id"]] = i
        elif kind == "finderT":
            PAGE_OF[f"finder{arg + 1}"] = i
            PAGE_OF.setdefault("finder0", i)
        elif kind == "photo":
            PHOTO_NO[i] = len(PHOTO_NO) + 1
        elif kind == "layout":
            PAGE_OF.setdefault("layout", i)
        elif kind != "prodR":
            PAGE_OF[kind] = i
    PAGE_OF.update({m: PAGE_OF[s] for m, s in SERIES_OF.items() if s in PAGE_OF})


PHOTO_NO = {}              # sayfa no -> tam sayfa fotograf sira no (fotograflar/tam-sayfa/<no>.jpg)
SECTION_OF = {pid: sec for sec in SECTIONS for pid in sec["products"]}
SERIES_OF = {"sd150": "sd", "sd230": "sd", "sd430": "sd"}      # katalogda seri acilimina gosterilen modeller
SECTION_OF.update({m: SECTION_OF[s] for m, s in SERIES_OF.items() if s in SECTION_OF})
PRODUCT_ORDER = [pid for sec in SECTIONS for pid in sec["products"]]

LOGO = logo_variants()

# Urun renkleri: her bolum tek renk ailesi; seri icinde kucukten buyuge acik -> koyu
# (Yanmar 50 en acik turkuaz, 500 en koyu turkuaz). (acik, koyu) uclari:
PALETTE = {"yanmar": ("#7fd0d4", "#0a3f45"), "saildrive": ("#92b8e2", "#163e6e"),
           "cummins": ("#d6aa7c", "#6a3c17"), "universal": ("#aab6bf", "#2b3740")}
TAB_TOP, TAB_STEP = 20.0, 13.2        # kenar sekmesi: ilk urun ust kenari ve urun basina kayma (mm)


def _rgb(h):
    return [int(h[i:i + 2], 16) for i in (1, 3, 5)]


def _hex(c):
    return "#" + "".join(f"{max(0, min(255, round(v))):02x}" for v in c)


def _mix(a, b, t):
    return [x + (y - x) * t for x, y in zip(a, b)]


def _lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def shade_vars(pid=None, sec=None):
    """Urun rengi (CSS degiskenleri): --sh zemin, --sht yazi, --shk yuk degeri, --shd ailenin koyusu."""
    sec = sec or SECTION_OF[pid]
    lo, hi = (_rgb(x) for x in PALETTE[sec["id"]])
    prods = sec["products"]
    t = prods.index(pid) / max(1, len(prods) - 1) if pid else 0.6
    c = _mix(lo, hi, t)
    if _lum(c) > 0.2:                                   # acik zemin: koyu yazi
        text, key = _mix(hi, [0, 0, 0], .5), _mix(hi, [0, 0, 0], .25)
    else:
        text, key = [255, 255, 255], _mix(lo, [255, 255, 255], .45)
    return f"--sh:{_hex(c)};--sht:{_hex(text)};--shk:{_hex(key)};--shd:{_hex(hi)}"


def sec_short(sec):
    """Kenar sekmesindeki bolum adi, buyuk harf (Turkcede i -> İ; marka adlari oldugu gibi)."""
    if sec["id"] == "universal":
        s = T("Universal")
        return (s.replace("i", "İ") if LANG == "tr" else s).upper()
    return {"yanmar": "YANMAR", "saildrive": "SAILDRIVE", "cummins": "CUMMINS"}[sec["id"]]


def pg(n):
    """Sayfa numarasi: 's. 12' / 'p. 12'."""
    return f"{e(T('p.'))}{NB}{n}"


def run_header(title, sec=None):
    """Ust bant: koyu zemin, logo ve bolum adi (tam tasma)."""
    acc = f' style="--acc:{sec["accent"]}"' if sec else ""
    return (f'<div class="band"{acc}><div class="band-in"><img src="{LOGO["white-head"]}" alt="">'
            f'<span>{e(title)}</span></div></div>')


def folio(n):
    return (f'<div class="folio"><span>{e(COMPANY["name"])} · {e(T("Marine Engine Mounts"))} · '
            f'{e(Tf("Catalogue {year}", year=COMPANY["year"]))}</span><b>{n}</b></div>')


def thumb_tab(n, sec, pid=None):
    """Kenar sekmesi: dis kenarda (tek sayfa sagda, cift sayfa solda) urun renginde 'YANMAR 01';
    her urunde biraz asagi kayar, kapali katalogun kenarinda merdiven gibi gorunur."""
    side = "r" if n % 2 else "l"
    i = PRODUCT_ORDER.index(pid or sec["products"][0])
    num = f'<b>{sec["products"].index(pid) + 1:02d}</b>' if pid else ""
    return (f'<div class="ttab {side}" style="top:{TAB_TOP + i * TAB_STEP:.1f}mm;{shade_vars(pid, sec)}">'
            f'<span><small>{e(sec_short(sec))}</small>{num}</span></div>')


def page(inner, n, cls="", sec=None, pid=None):
    tab = thumb_tab(n, sec, pid) if sec else ""
    style = f' style="{shade_vars(pid)}"' if pid else ""
    return f'<section class="page {cls}" data-n="{n}"{style}><div class="trim">{inner}{tab}</div></section>'


def mount_pill(pid, pos=""):
    pos_html = f"<i>{e(T(pos))}</i>" if pos else ""
    if MOBILE:
        return (f'<a class="mp" href="#prod-{SERIES_OF.get(pid, pid)}"><b>{e(short_code(pid))}</b>{pos_html}'
                f'<em>{icon("arrow")}</em></a>')
    return (f'<span class="mp"><b>{e(short_code(pid))}</b>{pos_html}'
            f'<em>{pg(PAGE_OF.get(pid, 99))}</em></span>')


# ---------------------------------------------------------------------------
# Teknik cizimler (assets/art/*.svg, satir ici; renk = currentColor)
# ---------------------------------------------------------------------------
def art_svg(name, cls="", style="", viewbox=None):
    path = os.path.join(HERE, "assets", "art", name + ".svg")
    if not os.path.exists(path):
        return ""
    svg = open(path, encoding="utf-8").read()
    svg = re.sub(r"<\?xml[^>]*\?>|<!DOCTYPE[^>]*>|<!--.*?-->", "", svg, flags=re.S).strip()
    # id'ler sayfada tekil olsun (ayni cizim birden cok sayfada kullanilabilir; tanimlar ayni)
    svg = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{name}-{m.group(1)}"', svg)
    svg = re.sub(r"url\(#([^)]+)\)", lambda m: f"url(#{name}-{m.group(1)})", svg)
    svg = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{name}-{m.group(1)}"', svg)
    if viewbox:
        svg = re.sub(r'viewBox="[^"]*"', f'viewBox="{viewbox}"', svg, count=1)
    svg = re.sub(r"<svg\b", f'<svg class="art {cls}" style="{style}"', svg, count=1)
    for _ in range(2):
        svg = re.sub(r'(<svg[^>]*?)\s(width|height)="[^"]*"', r"\1", svg, count=1)
    return svg


def art_anchors(name):
    path = os.path.join(HERE, "assets", "art", name + ".anchors.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def art_viewbox(name):
    path = os.path.join(HERE, "assets", "art", name + ".svg")
    if not os.path.exists(path):
        return None
    m = re.search(r'viewBox="([^"]+)"', open(path, encoding="utf-8").read())
    return [float(v) for v in m.group(1).replace(",", " ").split()] if m else None


def qr_svg(data, cls="qr"):
    """QR kodu (segno) -> satir ici SVG, koyu moduller currentColor."""
    import segno
    q = segno.make(data, error="m", micro=False)
    rows = list(q.matrix)
    n = len(rows)
    d = []
    for y, row in enumerate(rows):
        x = 0
        while x < n:
            if row[x]:
                x0 = x
                while x < n and row[x]:
                    x += 1
                d.append(f"M{x0} {y}h{x - x0}v1h-{x - x0}z")
            else:
                x += 1
    return (f'<svg class="{cls}" viewBox="-2 -2 {n + 4} {n + 4}" shape-rendering="crispEdges">'
            f'<path d="{"".join(d)}" fill="currentColor"/></svg>')


# ---------------------------------------------------------------------------
# Kapak ve karsilama
# ---------------------------------------------------------------------------
def wave_path(x0=16.0, x1=194.0, calm_at=118.0, amp=7.5):
    """Ufuk cizgisi motifi: soldan titresen, saga dogru durulup duz cizgiye donen dalga (mm)."""
    pts = []
    x = x0
    while x <= x1 + 1e-6:
        t = min(max((x - x0) / (calm_at - x0), 0.0), 1.0)
        env = (1 - t * t * (3 - 2 * t)) ** 1.6
        y = env * amp * (0.74 * math.sin(x * 1.35) + 0.26 * math.sin(x * 3.3 + 1.3))
        pts.append(f"{x:.2f},{15 - y:.2f}")
        x += 0.35
    return "M" + " L".join(pts)


COVER_HORIZON = 178.5      # kapak fotografinda ufuk cizgisi (mm, sayfa ustunden)
COVER_ENGINE_X, COVER_ENGINE_W = 22.0, 176.0


def p_cover(n):
    hazir = os.path.join(HERE, "assets", "img", f"kapak-{LANG}.jpg")
    if os.path.exists(hazir):                    # sahibinin hazir kapagi (logo ve yazilar gorselin icinde)
        return page(f'<div class="bleed-top fullphoto"><img src="{IMG}kapak-{LANG}.jpg" alt=""></div>', n, "photo")
    vb = art_viewbox("engine-side")
    engine, calm_at = "", 118.0
    if vb:
        a = art_anchors("engine-side")
        sc = COVER_ENGINE_W / vb[2]
        bed = a.get("bed_top_y", vb[3] * 0.9)
        top = COVER_HORIZON - (bed - vb[1]) * sc
        h = vb[3] * sc
        pos = f"left:{COVER_ENGINE_X:.1f}mm;top:{top:.1f}mm;width:{COVER_ENGINE_W:.1f}mm;height:{h:.1f}mm"
        # alttaki koyu kopya: parlak ufukta da cizgiler okunsun (vektor 'hale')
        engine = art_svg("engine-side", "cover-engine halo", pos) + art_svg("engine-side", "cover-engine", pos)
        mf = a.get("m-front")
        if mf:                       # dalga on takozda soner: motorun alti sessiz
            calm_at = COVER_ENGINE_X + (mf[0] - vb[0]) * sc
    d = wave_path(x0=-4.0, x1=214.0, calm_at=calm_at) if vb else wave_path()
    inner = f"""
    <div class="bleed-top cover-photo"><img src="{IMG}cover-sea.jpg" alt=""></div>
    <img class="cover-logo" src="{LOGO['white']}" alt="Novibrasyon">
    <div class="cover-kicker">{T("Product Catalogue")}<br>{COMPANY['year']}</div>
    <div class="cover-title">{T("Marine engine<br>mounts.")}</div>
    <div class="cover-sub">{e(T("Feel the quality. Enjoy the silence."))}</div>
    {engine}
    <svg class="cover-wave" viewBox="0 0 210 30" preserveAspectRatio="none">
      <defs><filter id="glow" x="-5%" y="-50%" width="110%" height="200%"><feGaussianBlur stdDeviation="0.7"/></filter></defs>
      <path d="{d}" fill="none" stroke="#bfeef2" stroke-width="1.8" stroke-opacity=".35" filter="url(#glow)"/>
      <path d="{d}" fill="none" stroke="#ffffff" stroke-width=".42" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    <div class="cover-brands">{e(T("Engine mounts for Yanmar · Cummins · Caterpillar · Volvo Penta · MAN · Perkins"))}</div>
    <div class="cover-foot"><span>{COMPANY['web']}</span><span>WhatsApp {COMPANY['whatsapp']}</span>
      <span>{COMPANY['email']}</span></div>"""
    return page(inner, n, "dark cover")


def p_welcome(n):
    """Karsilama + icindekiler tek sayfada."""
    def row(label, n, sub="", num=""):
        sub_html = f"<span>{e(T(sub))}</span>" if sub else ""
        num_html = f"<i>{e(num)}</i>" if num is not None else ""
        return f'<div class="irow">{num_html}<b>{e(T(label))}</b>{sub_html}<em>{pg(n)}</em></div>'
    fast = "".join([
        row("How a mount works", PAGE_OF["tech"], "Technical introduction", None),
        row("Engine finder", PAGE_OF["finder0"], "Look up your engine", None),
        row("Part number finder", PAGE_OF["partnos"], "Your old mount", None),
        row("Mount positions", PAGE_OF["layout"], "Which mount goes where", None),
        row("How to order", PAGE_OF["back"], "Three simple steps", None),
    ])
    secs = "".join(row(s["title"], PAGE_OF["sec-" + s["id"]], num=s["num"]) for s in SECTIONS)
    secs += row("Shaft bearings", PAGE_OF["bearings"], num="")
    inner = f"""
    <div class="bleed-top photo-top" style="height:calc(118mm + var(--b))"><img src="{IMG}welcome.jpg" alt=""></div>
    <div class="head" style="top:127mm">
      <div class="eyebrow">{e(Tf("Welcome to {name}", name=COMPANY['name']))}</div>
      <div class="h1">{e(T("Feel the quality. Enjoy the silence."))}</div>
      <p class="lead">{e(T("Novibrasyon Marin produces marine engine mounts and shaft bearings in Istanbul and ships them worldwide. Every mount in this catalogue is made to reduce engine vibration and noise, help keep the engine in line, and stand up to salt water and long hours at sea."))}</p>
      <div class="cindex">
        <div><h3>{e(T("Find it fast"))}</h3>{fast}</div>
        <div><h3>{e(T("In this catalogue"))}</h3>{secs}</div>
      </div>
    </div>
    <div class="values">
      <div>{icon('waves')}<b>{e(T("Less vibration"))}</b><span>{em(T("Bonded rubber elements absorb engine vibration before it reaches the hull."))}</span></div>
      <div>{icon('shield')}<b>{e(T("Built for salt water"))}</b><span>{em(T("Galvanized steel, 316 stainless steel and marine-grade aluminum bodies."))}</span></div>
      <div>{icon('truck')}<b>{e(T("2–4 business days"))}</b><span>{em(T("FedEx or UPS Express, insured and tracked. Depends on destination and customs."))}</span></div>
    </div>
    {folio(n)}"""
    return page(inner, n)


# ---------------------------------------------------------------------------
# Hakkimizda (iki sayfalik acilim, kapaktan hemen sonra)
# ---------------------------------------------------------------------------
ABOUT = os.environ.get("NOVI_HAKKIMIZDA", "1") == "1"    # sahibi onayladi (2026-10-27); 0 = kapali
ABOUT_FIGS = []
ABOUT_COLS = [
    ("What we make", "We produce professional vibration mounts for your engines. Engine mounts for Yanmar, Cummins, Caterpillar, Volvo Penta, MAN, Perkins, Beta Marine and Mercruiser, plus shaft bearings."),
    ("How we work", "Send us your engine model or a photo of your old mount. We confirm the right part before you order."),
    ("Delivery", "FedEx or UPS Express, insured and tracked, 2–4 business days."),
]


# Hakkimizda: novibrasyon.com/pages/about ile ayni 5 bolum, ayni gorseller; metinler kisaltildi.
# Bolumler sirayla: solda foto / sagda yazi, sonra solda yazi / sagda foto.
ABOUT_SECTIONS = [
    ("about-s1", "About us", "Five decades of rubber expertise.",
     "Novibrasyon is a marine brand built on our family's rubber manufacturing experience since 1970. We make professional vibration mounts for boat owners, service centres and shipyards around the world.",
     ["Yanmar", "Volvo Penta", "Cummins", "Caterpillar", "MAN", "Perkins", "Beta Marine", "Mercruiser", "John Deere"]),
    ("about-s2", "Manufacturing & quality", "Quality built into every product.",
     "Rubber compounds developed for marine use and corrosion-resistant metal parts. Every mount passes a multi-stage inspection: dimensions, rubber-to-metal bonding and load tolerance.",
     ["Marine-grade materials", "Multi-stage inspection", "45–65 Shore options"]),
    ("about-s3", "Packaging & dispatch", "Carefully packed. Quickly shipped.",
     "Most orders leave within 24 hours, packed for international transport and checked one last time. Tracking is sent as soon as the parcel ships.",
     ["FedEx Express Priority", "Dispatch within 24 hours", "Worldwide shipping"]),
    ("about-s4", "Delivery & support", "Fast delivery. Reliable support.",
     "Europe in 1–2, North America in 2–3 and other regions usually in 3–5 business days. Our team helps you choose the right mount and checks compatibility before you order.",
     ["Support on WhatsApp and e-mail"]),
    ("about-s5", "Business solutions", "Solutions for professionals.",
     "Custom manufacturing and wholesale for shipyards, boat builders, service centres, engine rebuilders and distributors. Contact us for partnerships and special projects.",
     ["Shipyards", "Boat builders", "Distributors"]),
]


def p_about(n):
    """Hakkimizda: tek sayfa, sitedeki gibi 5 bolum (foto / yazi sirayla yer degistirir)."""
    rows = []
    for i, (img, kick, title, text, tags) in enumerate(ABOUT_SECTIONS):
        chips = "".join(f"<span>{e(T(x))}</span>" for x in tags)
        rows.append(f'<div class="ab-row{" rev" if i % 2 else ""}"><div class="ab-ph"><img src="{IMG}{img}.jpg" alt=""></div>'
                    f'<div class="ab-tx"><div class="ab-k"><i>0{i + 1}</i>{e(T(kick))}</div><h3>{e(T(title))}</h3>'
                    f'<p>{e(T(text))}</p><div class="ab-tags">{chips}</div></div></div>')
    inner = f"""
    {run_header(T("About us"))}
    <div class="about2">
      <div class="ab-head">
        <div class="eyebrow">{e(T("About us"))}</div>
        <div class="h1">{e(T("Built to Perform. Engineered to Last."))}</div>
        <p class="lead">{e(T("Our mission is simple: the right product, with exceptional quality, delivered as quickly as possible."))}</p>
      </div>
      {"".join(rows)}
    </div>
    {folio(n)}"""
    return page(inner, n, "about-page")


def p_about_l(n):
    inner = f"""
    <div class="bleed-top about-hero"><img src="{IMG}about-hero.jpg" alt=""></div>
    <div class="about-shade"></div>
    <div class="about-title">
      <div class="eyebrow">{e(T("About us"))}</div>
      <div class="h1">{e(T("Quiet engines, from Istanbul."))}</div>
      <p class="lead">{e(T("Novibrasyon Marin is a marine engine mount brand from Tuzla, Istanbul. We supply engine mounts and shaft bearings for Yanmar, Cummins, Volvo Penta, Perkins and many other marine diesels, and ship them to boat owners and workshops around the world."))}</p>
    </div>
    {folio(n)}"""
    return page(inner, n, "dark about")


ABOUT_R_TEXT = [
    "We manufacture professional vibration mounts for the marine engines of Yanmar, Volvo Penta, Cummins, "
    "Caterpillar, MAN, Perkins, Beta Marine, Mercruiser, John Deere and many other brands, together with bronze "
    "and fiber shaft bearings.",
    "Working with us is simple. Tell us your engine model, or send a photo of your old mount if you are not sure. "
    "We check the part number, stud thread and mounting dimensions, and confirm the right mount before you order.",
    "Your order is packed for international transport and leaves within 24 hours with FedEx or UPS Express, "
    "insured and tracked. It usually reaches you in 2–4 business days, depending on destination and customs.",
]
ABOUT_R_BRANDS = ["Yanmar", "Volvo Penta", "Cummins", "Caterpillar", "MAN", "Perkins", "Beta Marine",
                  "Mercruiser", "John Deere"]


def p_about_r(n):
    """Ne yapiyoruz / nasil calisiyoruz / teslimat: tek akici metin, markalar ve uc fotograf."""
    shots = ["about-r0", "about-r1", "about-2"]
    mosaic = "".join(f'<figure class="am{i}"><img src="{IMG}{k}.jpg" alt=""></figure>' for i, k in enumerate(shots))
    paras = "".join(f"<p>{e(T(x))}</p>" for x in ABOUT_R_TEXT)
    brands = "".join(f"<span>{e(b)}</span>" for b in ABOUT_R_BRANDS)
    addr = " · ".join(e(a) for a in COMPANY["address"])
    inner = f"""
    {run_header(T("What we do"))}
    <div class="flow about-r">
      <div>
        <div class="eyebrow">{e(T("What we do"))}</div>
        <div class="h1">{e(T("Professional vibration mounts for every marine engine."))}</div>
      </div>
      <div class="about-mosaic">{mosaic}</div>
      <div class="ar-text">{paras}</div>
      <div class="ar-brands"><h3>{e(T("Engines we make mounts for"))}</h3><div>{brands}</div></div>
      <div class="about-addr">{icon('pin')}<span>{addr}</span><em>{e(COMPANY['web'])}</em></div>
    </div>
    {folio(n)}"""
    return page(inner, n)


# ---------------------------------------------------------------------------
# Teknik giris (tek sayfa)
# ---------------------------------------------------------------------------
TECH_PARTS = [
    ("Stud", "Carries the engine foot."),
    ("Adjusting nuts", "Set the engine height for shaft alignment."),
    ("Rubber element", "Absorbs the vibration. Its hardness is given in Shore."),
    ("Metal housing", "Holds the rubber and takes the load."),
    ("Base flange", "Bolted to the engine bed."),
    ("Centre core", "The raised centre of the base plate, bonded into the rubber."),
]
TECH_SHORE = [("45", "Soft", "Best isolation, for lighter loads."),
              ("55", "Medium", "Balanced isolation and load capacity."),
              ("65", "Hard", "Firm support for the heaviest loads.")]
TECH_SIGNS = ["Cracked, split or crumbling rubber",
              "Rubber coming away from the metal",
              "The engine sits lower than before or the mount has collapsed",
              "Soft, swollen rubber from oil or diesel",
              "More vibration or noise, knocking when shifting gear",
              "Shaft seal or shaft bearing wearing fast, shaft out of line"]
FINDER_STEP_TEXT = "Find your engine in the engine finder (page {p}). It shows the right mount for your engine."


def tech_steps(finder_page):
    return [
        ("Engine model", Tf(FINDER_STEP_TEXT, p=finder_page)),
        ("Load at each mount", T("Engine and gearbox weight, shared between the mounts. The rear mounts often carry more, because the gearbox sits there.")),
        ("Fit", T("Stud thread, mounting hole centers and height must match your engine feet and engine bed.")),
        ("Rubber hardness", T("Chosen by the load at each mount: softer for light loads, harder for heavy ones.")),
    ]


def p_tech(n):
    lis = "".join(f'<li><i>{k + 1}</i><div><b>{e(T(a))}</b><span>{e(T(b))}</span></div></li>'
                  for k, (a, b) in enumerate(TECH_PARTS))
    drawing = art_svg("mount-anatomy", "anat", viewbox="10 175 990 685")
    cards = "".join(f'<div class="kcard"><i>{k + 1}</i><b>{e(T(a))}</b><span>{e(b)}</span></div>'
                    for k, (a, b) in enumerate(tech_steps(PAGE_OF["finder0"])))
    shore_html = "".join(f'<div class="sh s{v}"><em>{v}</em><small>Shore</small><b>{e(T(a))}</b>'
                         f'<span>{e(T(b))}</span></div>' for v, a, b in TECH_SHORE)
    signs_html = "".join(f"<li>{icon('check')}<span>{e(T(s))}</span></li>" for s in TECH_SIGNS)
    inner = f"""
    {run_header(T("Technical introduction"))}
    <div class="head">
      <div class="eyebrow">{e(T("Technical introduction"))}</div>
      <div class="h1">{e(T("From vibration to silence."))}</div>
      <p class="lead">{e(T("A diesel engine shakes with every firing stroke. An engine mount is a rubber spring between the engine and the hull: it carries the weight of the engine and gearbox, keeps the shaft in line and stops most of the vibration before it reaches the boat."))}</p>
      <div class="tech-anat">
        <div class="anat-card">{drawing}</div>
        <div class="anat-list"><h3>{e(T("Inside a Novibrasyon mount"))}</h3><ol class="parts">{lis}</ol></div>
      </div>
      <h3 class="sect">{e(T("Choosing the right mount"))}</h3>
      <div class="kcards">{cards}</div>
      <h3 class="sect">{e(T("Rubber hardness in Shore"))}</h3>
      <div class="shore">
        <div class="shlab"><span>{e(T("softer"))}</span><span>{e(T("harder"))}</span></div>
        <div class="shbar"></div>
        <div class="shs">{shore_html}</div>
      </div>
      <h3 class="sect">{e(T("When is it time to replace?"))}</h3>
      <ul class="feat signs">{signs_html}</ul>
      <p class="tipline">{e(T("Mounts age together: when one has failed, check all of them. After fitting new mounts, check the shaft alignment at the coupling and tighten the nuts to the recommended torque."))}</p>
    </div>
    {folio(n)}"""
    return page(inner, n)


# ---------------------------------------------------------------------------
# Motor bulucu: olculup sayfalara bolunen tablolar (ilk sayfada kisa giris)
# ---------------------------------------------------------------------------
THUMB_DIR = os.path.join(HERE, "assets", "img", "thumbs")


def thumb(pid):
    """Urun kucuk gorseli (kare, panel rengi zemin), assets/img/thumbs/<pid>.jpg."""
    key = PRODUCTS[pid]["hero"][0][0]
    src = os.path.join(HERE, "assets", "img", key + ".jpg")
    dst = os.path.join(THUMB_DIR, pid + ".jpg")
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
        os.makedirs(THUMB_DIR, exist_ok=True)
        with Image.open(src) as im:
            im = im.convert("RGB")
            bg = (236, 235, 230)
            px = im.load()
            w, h = im.size
            step = max(1, min(w, h) // 400)
            xs, ys = [], []
            for y in range(0, h, step):
                for x in range(0, w, step):
                    r, g, b = px[x, y]
                    if abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2]) > 40:
                        xs.append(x)
                        ys.append(y)
            if xs:
                im = im.crop((min(xs), min(ys), max(xs) + 1, max(ys) + 1))
            side = int(max(im.size) * 1.14)
            canvas = Image.new("RGB", (side, side), bg)
            canvas.paste(im, ((side - im.width) // 2, (side - im.height) // 2))
            canvas.thumbnail((360, 360), Image.LANCZOS)
            canvas.save(dst, "JPEG", quality=86)
    return f"assets/img/thumbs/{pid}.jpg"


def pos_tag(note):
    """Takoz kutusundaki kisa not: Shore onerisi ('55 Shore, 6LP') veya saildrive tipi ('with SD20')."""
    if not note:
        return ""
    main, _, rest = note.partition(", ")
    cls = "shore" if "Shore" in main else "note"
    extra = f'<span class="pn2">{em(T(rest))}</span>' if rest else ""
    return f'<span class="pt {cls}">{em(T(main))}</span>{extra}'


def mount_chip(pid, note):
    if MOBILE:
        return (f'<a class="mc" href="#prod-{pid}"><div class="th"><img src="{thumb(pid)}" alt=""></div>'
                f'<div class="mi"><b>{e(short_code(pid))}</b>{pos_tag(note)}</div>'
                f'<div class="pg go">{icon("arrow")}</div></a>')
    return (f'<div class="mc"><div class="th"><img src="{thumb(pid)}" alt=""></div>'
            f'<div class="mi"><b>{e(short_code(pid))}</b>{pos_tag(note)}</div>'
            f'<div class="pg">{pg(PAGE_OF.get(pid, 99))}</div></div>')


def finder_row(series, models, mounts, alt):
    """Motor satiri: solda motor adi (+ kisa model listesi), sagda takoz kutulari;
    uzun model listeleri satirin altinda tam genislikte."""
    models = T(models) if models and models != series else ""
    short = f"<span>{em(models)}</span>" if models and len(models) <= 50 else ""
    wide = f'<div class="ml">{em(models)}</div>' if models and len(models) > 50 else ""
    chips = "".join(mount_chip(pid, note) for pid, note in mounts)
    return (f'<div class="fr2{" alt" if alt else ""}"><div class="en"><b>{em(T(series))}</b>{short}</div>'
            f'<div class="mcs">{chips}</div>{wide}</div>')


def brand_band(brand, cont=False):
    extra = f'<em>{e(T("continued"))}</em>' if cont else ""
    return f'<div class="bband"><span>{e(T(brand))}</span>{extra}</div>'


FINDER_ALL = FINDER + FINDER_2 + FINDER_3


def finder_blocks():
    """[(tur, marka, html_fn)]  tur: 'brand' | 'row'."""
    out = []
    for brand, rows in FINDER_ALL:
        out.append(("brand", brand, lambda b=brand: brand_band(b)))
        for k, (series, models, mounts) in enumerate(rows):
            out.append(("row", brand, lambda s=series, m=models, mo=mounts, a=k % 2 == 1: finder_row(s, m, mo, a)))
    return out


def measure_html(frags, width_mm=178.0):
    """Chrome ile her HTML parcasinin yuksekligini (mm) olcer."""
    body = "".join(f'<div class="mz" style="width:{width_mm}mm;display:flow-root">{h}</div>' for h in frags)
    js = """
    document.fonts.ready.then(function () {
      var MM = 96 / 25.4, out = [];
      document.querySelectorAll('.mz').forEach(function (el) { out.push(el.getBoundingClientRect().height / MM); });
      document.getElementById('out').textContent = JSON.stringify(out);
    });"""
    doc = (f'<!doctype html><html lang="{LANG}"><head><meta charset="utf-8"><style>{font_css()}</style>'
           f'<link rel="stylesheet" href="styles.css"></head><body class="measure">{body}'
           f'<pre id="out"></pre><script>{js}</script></body></html>')
    path = os.path.join(HERE, f"_olcum-{LANG}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    src = "file:///" + path.replace("\\", "/")
    res = subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--allow-file-access-from-files",
                          "--virtual-time-budget=20000", "--dump-dom", src],
                         check=True, capture_output=True, text=True, encoding="utf-8")
    m = re.search(r'<pre id="out">([^<]*)</pre>', res.stdout)
    os.remove(path)
    if not m or not m.group(1):
        sys.exit("Olcum basarisiz (motor bulucu).")
    return json.loads(m.group(1))


FINDER_CAP = 251.0      # tablo alani: 261 mm akis - 4.2 mm aralik - ~5 mm ust baslik (mm)


def finder_intro():
    """Motor bulucunun ilk sayfasindaki kisa giris."""
    return (f'<div class="fintro"><div class="eyebrow">{e(T("Engine finder"))}</div>'
            f'<div class="h1">{e(T("Find your mount."))}</div>'
            f'<p class="lead">{e(T("Find your engine brand and model in the table: each box shows the mount code and its page. The engine model is on the name plate or in the engine manual."))}</p></div>')


def paginate_finder():
    """Motor bulucu tablolarini olcup sayfalara boler: [[(tur, marka, html_fn, devam_mi)]]."""
    blocks = finder_blocks()
    eyebrow = f'<div class="eyebrow">{e(T("Engine finder"))}</div>'
    heights = measure_html([fn() for _, _, fn in blocks] + [brand_band("Yanmar", True), finder_intro(), eyebrow])
    eyebrow_h = heights.pop()
    intro_h = heights.pop()
    cont_h = heights.pop()
    pages, cur, used = [], [], intro_h - eyebrow_h
    for i, ((kind, brand, fn), h) in enumerate(zip(blocks, heights)):
        need = h
        if kind == "brand" and i + 1 < len(heights):
            need += heights[i + 1]                       # marka basligi en az bir satirla kalsin
        if cur and used + need > FINDER_CAP:
            pages.append(cur)
            cur, used = [], 0.0
            if kind == "row" and brand:
                cur.append(("brand", brand, lambda b=brand: brand_band(b, True), True))
                used += cont_h
        cur.append((kind, brand, fn, False))
        used += h
    if cur:
        pages.append(cur)
    return pages


def p_finder_table(n, k):
    blocks = FINDER_PAGES[k]
    body = "".join(fn() for _, _, fn, _ in blocks)
    head = finder_intro() if k == 0 else (
        f'<div class="eyebrow">{e(Tf("Engine finder · {i} of {n}", i=k + 1, n=len(FINDER_PAGES)))}</div>')
    inner = f"""
    {run_header(T("Engine finder"))}
    <div class="flow index">
      <div>{head}</div>
      <div class="fit" data-max="1.0"><div class="finder2">{body}</div></div>
    </div>
    {folio(n)}"""
    return page(inner, n)


# ---------------------------------------------------------------------------
# Takoz yerlesimi (iki sayfa): tekne ustten, hangi takoz nereye.
#   Yanmar ve saildrive: Ellebogen yerlesim tablolari / setleri ile ayni (2026-10-30).
#   konum: bp arka-iskele, bs arka-sancak, fp on-iskele, fs on-sancak, sd saildrive (arka, ortada)
#   deger: urun kimligi; "?" = bilgi yok (bize sorun); ("VV · MT", None) = serbest etiket
# ---------------------------------------------------------------------------
LAYOUT_PAGES = [
    ("Shaft-drive engines", [
        ("Yanmar 1GM · 1GM10", "Back: 50 × 2 · Front: 70 × 2", {"bp": "50", "bs": "50", "fp": "70", "fs": "70"}),
        ("Yanmar 2GM · 3GM · 2YM15 · 3YM", "Back: 75 × 2 · Front: 100 × 2", {"bp": "75", "bs": "75", "fp": "100", "fs": "100"}),
        ("Yanmar 2GM20V · 3GM30V (V-drive) · 3HM · 3HM35", "100 × 4", {"bp": "100", "bs": "100", "fp": "100", "fs": "100"}),
        ("Yanmar 3JH series", "Port: 150 × 2 · Starboard: 100 × 2", {"bp": "150", "bs": "100", "fp": "150", "fs": "100"}),
        ("Yanmar 4JH series", "Port: 200 × 2 · Starboard: 150 × 2", {"bp": "200", "bs": "150", "fp": "200", "fs": "150"}),
        ("Yanmar 4JH3 · 4JH4 turbo · 4JH80 · 4JH110", "200 × 4", {"bp": "200", "bs": "200", "fp": "200", "fs": "200"}),
        ("Yanmar 4LHA series", "400 × 4", {"bp": "400", "bs": "400", "fp": "400", "fs": "400"}),
        ("Yanmar 6LP · 6LY · 6LF", "500 × 4", {"bp": "500", "bs": "500", "fp": "500", "fs": "500"}),
        ("Cummins 6B · 6BT · 6BTA 5.9", "450 × 4", {"bp": "450", "bs": "450", "fp": "450", "fs": "450"}),
    ]),
    ("Saildrive and other engines", [
        ("Yanmar 1GM10 with saildrive", "Front: 50 × 2 · Saildrive: SD150", {"fp": "50", "fs": "50", "sd": "sd150"}),
        ("Yanmar 2GM20 with SD20", "Front: 75 × 2 · Saildrive: SD150", {"fp": "75", "fs": "75", "sd": "sd150"}),
        ("Yanmar 2YM15 with saildrive", "Front: 100 × 2 · Saildrive: SD150", {"fp": "100", "fs": "100", "sd": "sd150"}),
        ("Yanmar 3YM · 3GM30 · 3HM35 with SD20 · SD25 · SD30", "Front: 100 × 2 · Saildrive: SD230", {"fp": "100", "fs": "100", "sd": "sd230"}),
        ("Yanmar 3JH with SD31 · SD40 · SD50", "Front: 200 × 2 · Saildrive: SD230", {"fp": "200", "fs": "200", "sd": "sd230"}),
        ("Yanmar 4JH with SD40 · SD50", "Saildrive: SD430 · Front mounts: ask us", {"fp": "?", "fs": "?", "sd": "sd430"}),
        ("Cummins QSB 5.9 · 6CTA 8.3 · QSC 8.3 · QSL9 · QSM11", "600 × 4 (6CTA 8.3, QSC 8.3 and QSL9 also 500)", {"bp": "600", "bs": "600", "fp": "600", "fs": "600"}),
        ("Cummins QSB 6.7 · Caterpillar 3116 · 3126 · C7", "500 × 4", {"bp": "500", "bs": "500", "fp": "500", "fs": "500"}),
        ("Volvo Penta · Perkins · MAN and other engines", "Universal mounts: the same model at all four positions; the Shore hardness is chosen by the load at each mount",
         {"bp": ("VV · MT", None), "bs": ("VV · MT", None), "fp": ("VV · MT", None), "fs": ("VV · MT", None)}),
    ]),
]


def prod_color(pid):
    """Urunun katalog rengi (bolum paletinde acik -> koyu) ve okunur yazi rengi."""
    sec = SECTION_OF[pid]
    lo, hi = (_rgb(x) for x in PALETTE[sec["id"]])
    prods = sec["products"]
    c = _mix(lo, hi, prods.index(SERIES_OF.get(pid, pid)) / max(1, len(prods) - 1)) if len(prods) > 1 else _mix(lo, hi, .6)
    return _hex(c), ("#10262b" if _lum(c) > 0.2 else "#ffffff")


def boat_svg(pos):
    """Tekne ustten: kic solda, bas sagda; iskele ustte, sancak altta. Takoz kutulari urun renginde."""
    sd = "sd" in pos
    o = ['<svg class="boat" viewBox="0 0 300 150">',
         '<path d="M34 28 L170 22 Q252 32 294 75 Q252 118 170 128 L34 122 Q10 120 10 75 Q10 30 34 28 Z" '
         'fill="#f4f6f6" stroke="#9aa9ad" stroke-width="1.6"/>',
         '<path d="M180 30 Q250 42 282 75 Q250 108 180 120" fill="none" stroke="#d3dcde" stroke-width="1"/>']
    if not sd:
        o.append('<line x1="14" y1="75" x2="58" y2="75" stroke="#7d8d91" stroke-width="2.2"/>')
    o.append('<rect x="56" y="62" width="22" height="26" rx="3" fill="#c9d3d5" stroke="#7d8d91"/>'
             '<rect x="78" y="52" width="82" height="46" rx="5" fill="#dfe6e7" stroke="#7d8d91"/>'
             '<line x1="88" y1="66" x2="150" y2="66" stroke="#b5c2c5"/><line x1="88" y1="75" x2="150" y2="75" stroke="#b5c2c5"/>'
             '<line x1="88" y1="84" x2="150" y2="84" stroke="#b5c2c5"/>')
    xy = {"bp": (86, 36), "fp": (152, 36), "bs": (86, 114), "fs": (152, 114), "sd": (50, 75)}
    for k, v in pos.items():
        x, y = xy[k]
        if isinstance(v, tuple):
            label, bg, fg = v[0], "#4a5a64", "#ffffff"
        elif v == "?":
            label, bg, fg = "?", "#c3cccf", "#4a5a64"
        else:
            label = PRODUCTS[v]["code"]
            bg, fg = prod_color(v)
        w = max(40, 9.2 * len(label) + 8)
        fs = 15 if len(label) <= 4 else 12.5
        o.append(f'<rect x="{x - w / 2:.1f}" y="{y - 11}" width="{w:.1f}" height="22" rx="4" fill="{bg}" stroke="#ffffff" stroke-width="1.4"/>'
                 f'<text x="{x}" y="{y + fs / 3:.1f}" text-anchor="middle" font-size="{fs}" font-weight="800" fill="{fg}">{e(label)}</text>')
    lab = 'font-size="8.5" font-weight="700" fill="#6b7c80" letter-spacing=".8"'
    o.append(f'<text x="12" y="14" {lab}>{e(T("BACK"))}</text>'
             f'<text x="292" y="14" text-anchor="end" {lab}>{e(T("FRONT"))}</text>'
             f'<text x="119" y="14" text-anchor="middle" {lab}>{e(T("PORT"))}</text>'
             f'<text x="119" y="146" text-anchor="middle" {lab}>{e(T("STARBOARD"))}</text>')
    o.append("</svg>")
    return "".join(o)


def p_layout(n, k=0):
    title, items = LAYOUT_PAGES[k]
    cards = []
    for engines, summary, pos in items:
        pids = sorted({v for v in pos.values() if isinstance(v, str) and v != "?"}, key=code_rank)
        if not pids:                                          # universal: VV1 ... MT
            pids = ["vv1", "vv2", "vv3", "mt"]
        pills = "".join(mount_pill(x) for x in pids)
        cards.append(f'<div class="lycard"><b class="lyeng">{em(T(engines))}</b>{boat_svg(pos)}'
                     f'<div class="lysum">{e(T(summary))}</div><div class="mps">{pills}</div></div>')
    head = (f'<div class="eyebrow">{e(T("Mount positions"))} · {e(T(title))}</div>'
            f'<div class="h1">{e(T("Which mount goes where?"))}</div>'
            f'<p class="lead">{e(T("Seen from above: the back is the stern side, where the gearbox and shaft are; the front is the bow side. On some engines the port and starboard mounts are different models."))}</p>'
            if k == 0 else
            f'<div class="eyebrow">{e(T("Mount positions"))} · {e(T(title))}</div>'
            f'<div class="h1">{e(T("Saildrive and other engines."))}</div>'
            f'<p class="lead">{e(T("With a saildrive, one saildrive mount carries the back of the engine and two engine mounts carry the front."))}</p>')
    note = ("Positions follow the original Yanmar mount arrangement. Port is the left side and starboard the right side when looking forward. If your engine is not listed, send us a photo of your old mounts."
            if k == 0 else
            "For larger engines the same model is used at all four positions; please confirm with the part number of your old mount. Not sure? Send us your engine model or a photo.")
    inner = f"""
    {run_header(T("Mount positions"))}
    <div class="flow lay">
      <div>{head}</div>
      <div class="lygrid">{"".join(cards)}</div>
      <p class="lynote">{e(T(note))}</p>
    </div>
    {folio(n)}"""
    return page(inner, n)


def code_rank(pid):
    """Urun kodu sirasi: once sayisal kodlar (50 ... 600), sonra SD, VV ve MT."""
    code = PRODUCTS[pid]["code"]
    if code.isdigit():
        return int(code)
    m = re.match(r"([A-Z]+)(\d*)", code)
    group = {"SD": 10000, "VV": 20000, "MT": 30000}.get(m.group(1), 40000)
    return group + int(m.group(2) or 0)


def p_partnos(n):
    """Parca numaralari: marka gruplari icinde Novibrasyon urun sirasina gore (50, 70, 75 ...)."""
    rows = {}
    for pid, p in PRODUCTS.items():
        for label, nums in p.get("refs", []):
            brand = "Cummins" if label.startswith("Cummins") else label
            for num in nums:
                rows.setdefault((brand, num), []).append(pid)
    rank = {pid: code_rank(pid) for pid in PRODUCTS}
    order = ["Yanmar", "Cummins", "Caterpillar", "MAN", "Barry Controls", "Trelleborg / Metalastik"]
    entries = []                                  # (marka, ilk_mi, satir html)
    for brand in order:
        items = sorted(((num, pids) for (b, num), pids in rows.items() if b == brand),
                       key=lambda it: (min(rank[p] for p in it[1]), it[0]))
        for k, (num, pids) in enumerate(items):
            pids = sorted(pids, key=rank.get)
            entries.append((brand, k == 0, f'<div class="pnrow"><div class="mps">'
                                          f'{"".join(mount_pill(p) for p in pids)}</div>'
                                          f'<span class="pn">{e(num)}</span></div>'))
    half = (len(entries) + len(order) + 1) // 2
    cols, cur, count, last_brand = [], [], 0, None
    for brand, first, html_row in entries:
        if len(cols) == 0 and count >= half and not first and brand == last_brand:
            cols.append(cur)
            cur, count = [f'<div class="brandhead">{e(Tf("{brand}, continued", brand=brand))}</div>'], 1
        elif len(cols) == 0 and count >= half and first:
            cols.append(cur)
            cur, count = [], 0
        if first:
            cur.append(f'<div class="brandhead">{e(brand)}</div>')
            count += 1
        cur.append(html_row)
        count += 1
        last_brand = brand
    cols.append(cur)
    body = "".join(f'<div class="pncol">{"".join(c)}</div>' for c in cols)
    inner = f"""
    {run_header(T('Part number finder'))}
    <div class="flow index">
      <div>
        <div class="eyebrow">{e(T("Part number finder"))}</div>
        <div class="h1">{e(T("Have a part number?"))}</div>
        <p class="lead">{e(T("Find the original part number on your old mount or in your engine manual, then look it up here."))}</p>
      </div>
      <div class="fit" data-max="1.0"><div class="pnc">{body}</div></div>
    </div>
    {folio(n)}"""
    return page(inner, n)


def p_divider(n, sec):
    pids = sec.get("div_products", sec["products"])
    rows = "".join(
        f'<div><b>{e(pname(pid))}</b><span>{e(PRODUCTS[pid]["tagline"])}</span><em>{pg(PAGE_OF[pid])}</em></div>'
        for pid in pids)
    extra = ""
    if sec.get("div_products"):                  # tek urunlu bolum: modeller gorselleriyle, kisa montaj notu
        cards = "".join(f'<figure><img src="{IMG}{PRODUCTS[pid]["hero"][0][0]}.jpg" alt="">'
                        f'<figcaption>{e(PRODUCTS[pid]["code"])}</figcaption></figure>' for pid in pids)
        extra = f'<div class="div-models">{cards}</div><p class="div-note">{e(T(sec["div_note"]))}</p>'
    mode = "product" if sec["image_mode"] == "product" else ""
    inner = f"""
    <div class="bleed-x div-img {mode}"><img src="{IMG}{sec['image']}.jpg" alt=""></div>
    <div class="div-text">
      <div class="div-num"><i style="background:{sec['accent']}"></i>{sec['num']}</div>
      <div class="div-title">{e(sec['title'])}</div>
      <p class="div-intro">{e(sec['intro'])}</p>
      <div class="div-list">{rows}</div>
      {extra}
    </div>
    {folio(n)}"""
    return page(inner, n, "dark", sec)


REVIEW_PAGES = {1: (0, 4), 2: (4, 7), 3: (7, 10), 4: (10, 13), 5: (13, 16), 6: (16, 19)}   # 19 yorum, 6 tam sayfa fotograf


def review_overlay(no):
    """Fotograf altinda petek dizilimli radyuslu kartlar: puan karti + 4-5 eBay yorumu (ulke bayragi ile)."""
    if MOBILE or no not in REVIEW_PAGES:
        return ""
    from yorumlar import COUNTRY, REVIEWS, flag_svg
    a, b = REVIEW_PAGES[no]

    def short(t, n=125):
        return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + " …"

    def card(code, txt):
        c = COUNTRY.get(code)
        who = (f'<span class="cty">{flag_svg(code)}{e(c[0] if LANG == "tr" else c[1])}</span>' if c else "")
        return (f'<div class="rvc"><div class="st">★★★★★</div><q>“{e(short(txt))}”</q>'
                f'<div class="by">{who}<span>{e(T("eBay User"))}</span></div></div>')

    score = (f'<div class="rvc score"><b>5,0</b><div class="st">★★★★★</div>'
             f'<small>{e(T("100% Positive Ratings"))}</small><span>eBay · Novibrasyon Marin</span></div>')
    cards = [score] + [card(c, t) for c, t in REVIEWS[a:b]]
    tag = f'<div class="rv-tag"><span>★ 5,0</span>{e(T("Customer reviews"))} · eBay</div>'
    return tag + '<div class="rv-hc">' + "".join(f'<div class="cell c{i}">{x}</div>' for i, x in enumerate(cards)) + "</div>"


def p_photo(n, sec):
    """Tam sayfa fotograf sayfasi: fotograflar/tam-sayfa/<no>.jpg varsa tasmali basilir, yoksa yer tutucu."""
    no = PHOTO_NO.get(n, 0)
    path = None
    for ext in ("jpg", "jpeg", "png", "webp", "JPG", "JPEG", "PNG"):
        cand = os.path.join(HERE, PHOTOS, "tam-sayfa", f"{no}.{ext}")
        if os.path.exists(cand):
            path = f"{PHOTOS}/tam-sayfa/{no}.{ext}"
            break
    if path:
        inner = f'<div class="bleed-top fullphoto"><img src="{html.escape(path)}" alt=""></div>' + review_overlay(no)
    else:
        inner = (f'<div class="bleed-top fullphoto empty">{icon("camera")}'
                 f'<b>{e(T("Full-page photo"))}</b><span>{PHOTOS}/tam-sayfa/{no}.jpg</span></div>')
    return page(inner, n, "photo")


# ---------------------------------------------------------------------------
# Urun sayfalari: iki sayfalik acilim
#   sol  (prodL): kod, slogan, urun gorseli, one cikan degerler, uyumlu motorlar, parca no
#   sag  (prodR): olcu cizimi + olcu tablosu, yuk / Shore, egriler, fotograflar, iletisim
# ---------------------------------------------------------------------------
def brandline(pid):
    if pid.startswith("sd"):
        return "Novibrasyon Saildrive"
    if SECTION_OF[pid]["id"] == "universal":
        return "Novibrasyon " + T("Universal")
    return "Novibrasyon"


def keyfig_items(p):
    """One cikan degerler: [(deger, etiket)]; yuk (varsa) en basta."""
    if p.get("keyfigs"):
        return [(T(v), T(lbl)) for v, lbl in p["keyfigs"]]
    dr = dict(p.get("dimrows", []))
    items = []
    if p.get("load"):
        items.append((p["load"], T("Max. load per mount")))
    for lbl in ("Stud thread", "Base (L × W)", "Base length", "Hole centers", "Body height"):
        v = dr.get(T(lbl))
        if v and len(items) < 4:
            items.append((v, T(lbl)))
    return items


def keyfigs(p):
    """One cikan degerler bandi: yuk (varsa) en basta ve buyuk."""
    items = keyfig_items(p)
    cells = "".join(f'<div class="{"kload" if k == 0 and p.get("load") else ""}"><b>{e(v)}</b><span>{e(lbl)}</span></div>'
                    for k, (v, lbl) in enumerate(items))
    return f'<div class="kfig n{len(items)}">{cells}</div>'


def fits_block(p):
    if not p.get("fits"):
        return ""
    note = f'<p class="fnote">{e(p["fits_note"])}</p>' if p.get("fits_note") else ""
    if p["fits"][0].get("label") == T("Typical applications"):
        chips = "".join(f'<span class="chip">{e(m)}</span>' for m in p["fits"][0]["models"])
        return (f'<div class="blk"><h3>{e(T("Typical applications"))}</h3><div class="chips">{chips}</div>'
                f'{note}</div>')
    groups = []
    for g in p["fits"]:
        label = e(g.get("label", ""))
        if g.get("tag"):                                    # yalnizca saildrive tipi
            gl = f'<div class="gl"><span class="tag">{e(g["tag"])}</span><small>{label}</small></div>'
        else:
            gl = f'<div class="gl">{label}</div>'
        chips = "".join(
            f'<span class="chip{" text" if len(m) > 20 else ""}">{e(m)}</span>' for m in g["models"])
        groups.append(f'<div class="group">{gl}<div class="chips">{chips}</div></div>')
    return f'<div class="blk"><h3>{e(T("Fits these engines"))}</h3>{"".join(groups)}{note}</div>'


def refs_block(p):
    if not p.get("refs") or p.get("refs_on_page") is False:
        return ""
    head = p.get("refs_head")
    cells = "".join(
        f'<div class="refcell"><small>{e(b)}</small><div class="nums">'
        + "".join(f'<span class="pn">{e(x)}</span>' for x in nums) + "</div></div>"
        for b, nums in p["refs"])
    note = f'<p class="rnote">{e(p["refs_note"])}</p>' if p.get("refs_note") else ""
    title = e(T("Replaces part numbers · by engine application" if head else "Replaces part numbers"))
    return f'<div class="blk"><h3>{title}</h3><div class="refgrid">{cells}</div>{note}</div>'


def tiles_html(items, cls="tiles"):
    return f'<div class="{cls}">' + "".join(
        f'<div><b>{e(v)}</b><span>{e(k).replace(chr(10), "<br>")}</span></div>' for k, v in items) + "</div>"


def dims_table(p):
    """Olcu tablosu: tek urunde etiket / deger; MT'de model sutunlari."""
    if p.get("mounting"):
        heads, rows = p["mounting"]
        th = "<th></th>" + "".join(f"<th>{e(r[0])}</th>" for r in rows)
        trs = "".join(f'<tr><td class="lbl">{e(heads[i])}</td>'
                      + "".join(f'<td class="val">{em(r[i])}</td>' for r in rows) + "</tr>"
                      for i in range(1, len(heads)))
        return f'<table class="dt multi"><tr>{th}</tr>{trs}</table>'
    if not p.get("dimrows"):
        return ""
    trs = "".join(f'<tr><td class="lbl">{e(k)}</td><td class="val">{em(v)}</td></tr>' for k, v in p["dimrows"])
    return f'<table class="dt">{trs}</table>'


def variants_block(p):
    """Shore / yuk: kg degerleri buyuk."""
    if not p.get("variants"):
        return ""
    heads, rows = p["variants"]
    note = f'<p class="fnote">{e(p["variants_note"])}</p>' if p.get("variants_note") else ""
    if len(heads) == 2:
        tiles = []
        for hard, load in rows:
            val, sub = (load[:-10], "per mount") if load.endswith(" per mount") else (load, "")
            tiles.append(f'<div><span>{e(T(hard))}</span><b>{e(T(val))}</b><small>{e(T(sub))}</small></div>')
        return (f'<div class="blk"><h3>{e(T("Rubber hardness & maximum load"))}</h3>'
                f'<div class="ltiles">{"".join(tiles)}</div>{note}</div>')
    th = "".join(f"<th>{e(h)}</th>" for h in heads)
    trs = []
    for r in rows:
        tds = []
        for i, c in enumerate(r):
            if i == 0:
                cls = "k"
            elif (len(heads) == 3 and i == 1) or (len(heads) == 5 and i in (1, 2, 3)):
                cls = "big"
            else:
                cls = "txt"
            tds.append(f'<td class="{cls}">{em(c)}</td>')
        trs.append("<tr>" + "".join(tds) + "</tr>")
    title = e(T("Maximum static load per mount" if p["code"] == "MT" else "Available variants"))
    return f'<div class="blk"><h3>{title}</h3><table class="vt"><tr>{th}</tr>{"".join(trs)}</table>{note}</div>'


def finish_line(p):
    if not p.get("finishes"):
        return ""
    items = "".join(f'<span><i class="swatch {"ss" if k == "ss" else ""}"></i>{e(t)}</span>'
                    for k, t, _ in FINISHES)
    return f'<div class="finline"><b>{e(T("Available body options"))}</b>{items}</div>'


def features_block(p):
    if not p.get("features"):
        return ""
    lis = "".join(f"<li>{icon('check')}<span>{e(f)}</span></li>" for f in p["features"])
    return f'<div class="blk"><h3>{e(T("Key features"))}</h3><ul class="feat">{lis}</ul></div>'


def callout(p):
    return f"""
    <div class="callout">
      <div class="cq"><h4>{e(T("Not sure it fits?"))}</h4><p>{e(p['note'])}</p></div>
      <div class="cbar">
        <span>{icon('chat')}WhatsApp {e(COMPANY['whatsapp'])}</span>
        <span>{icon('mail')}{e(COMPANY['email'])}</span>
        <span class="soft">{icon('truck')}{e(T("FedEx or UPS Express · 2–4 business days · insured and tracked"))}</span>
      </div>
    </div>"""


HERO_SCALE = {"pmt1": 140 / 184, "pmt2": 166 / 184}     # taban boylari 140 / 166 / 184 mm


def p_prodL(n, pid):
    p = PRODUCTS[pid]
    sec = SECTION_OF[pid]
    figs = []
    for key, cap in p["hero"]:
        sw = ""
        if cap and ("Galvani" in cap):
            sw = '<span class="swatch"></span>'
        elif cap and ("stainless" in cap or "paslanmaz" in cap):
            sw = '<span class="swatch ss"></span>'
        capt = f"<figcaption>{sw}{e(cap)}</figcaption>" if cap else ""
        sc = HERO_SCALE.get(key)                  # ayni seride boylar gercek oranda (MT1 < MT2 < MT3)
        st = f' style="transform:scale({sc});transform-origin:50% 100%"' if sc else ""
        figs.append(f'<figure><img src="{IMG}{key}.jpg" alt=""{st}>{capt}</figure>')
    stage_cls = "solo" if len(figs) == 1 else ("trio" if len(figs) == 3 else "")
    code_cls = "long" if len(p["code"]) >= 5 else ""
    inner = f"""
    <div class="sea">{art_svg("sea-scene").replace("sea-scene-", f"sea{n}-")}</div>
    {run_header(sec['title'], sec)}
    <div class="flow prod">
      <div class="ptop">
        <div class="pcode"><div class="brandline">{e(brandline(pid))}</div>
          <div class="code {code_cls}">{e(p['code'])}</div></div>
        <div class="ptext"><div class="tagline">{e(p['tagline'])}</div><p class="lead">{e(p['intro'])}</p></div>
      </div>
      <div class="stage {stage_cls}">{''.join(figs)}</div>
      {keyfigs(p)}
      <div class="fit" data-max="1.0">{variants_block(p)}{fits_block(p)}{refs_block(p)}{features_block(p)}</div>
    </div>
    {folio(n)}"""
    return page(inner, n, "", sec, pid)


def card_img(key):
    if LANG != "en" and os.path.exists(os.path.join(HERE, "assets", "img", f"{key}-{LANG}.jpg")):
        key = f"{key}-{LANG}"                   # etiketleri cevrilmis cizim (localize_art.py)
    return f"{IMG}{key}.jpg"


CONTAIN_PHOTOS = {("vv3", 2)}     # (urun, fotograf no): kirpilmaz, tamami gorunur


def photo_slot(pid, num):
    path = find_photo(pid, num)
    if path:
        src = html.escape(path)
        contain = " contain" if (pid, num) in CONTAIN_PHOTOS else ""
        return (f'<div class="pslot filled{contain}"><img class="pbg" src="{src}" alt="">'
                f'<img class="pfg" src="{src}" alt=""></div>')
    return (f'<div class="pslot">{icon("camera")}<b>{e(Tf("Photo {n}", n=num))}</b>'
            f'<span>{PHOTOS}/{pid}/{num}.jpg</span></div>')


def charts_row(d, h=44):
    curves = load_curves(d.get("curves"))
    if not curves:
        return ""
    cells = "".join(f'<div class="card chartcard">{chart_svg(pan, 84, h, d.get("series"))}</div>'
                    for pan in curves["panels"])
    return f'<div class="charts">{cells}</div>'


V2_ALL = True              # yeni sag sayfa duzeni tum urunlerde (False: eski duzen)
V2_PIDS = set()            # yeni sag sayfa duzeni (on / ust gorunus kutulari, 2 fotograf) uygulanan urunler


VIEW_FAMILY = [["d50", "d70", "d75", "d100", "d150", "d200"], ["dsd150", "dsd230", "dsd430"],
               ["d400", "d450", "d500", "d600"], ["dvv1", "dvv2", "dvv3"], ["dmt1", "dmt2", "dmt3"]]
VIEW_BOX = {"on": (80.0, 57.0), "ust": (80.0, 57.0)}           # kutu ici kullanilabilir alan (mm)
VIEW_BOX_TRI = {"on": (48.0, 38.0), "ust": (48.0, 36.0)}       # MT: uc kutu
VIEW_BOX_TRI_BIG = {"on": (53.0, 50.0), "ust": (53.0, 44.0)}   # uc kutu, fotograf satiri yok (SD)


def _view_file(key, part):
    for k in ([f"{key}-{part}-{LANG}.png"] if LANG != "en" else []) + [f"{key}-{part}.png"]:
        if os.path.exists(os.path.join(HERE, "assets", "img", k)):
            return k
    return f"{key}-{part}.png"


def view_img(key, part, tri=False, big=False):
    """Ayri on / ust gorunus; ailede ortak olcek: genislik mm olarak verilir (gercek oranli)."""
    fn = _view_file(key, part)
    fam = next((f for f in VIEW_FAMILY if key in f), [key])
    sizes = []
    for k in fam:
        try:
            with Image.open(os.path.join(HERE, "assets", "img", _view_file(k, part))) as im:
                sizes.append(im.size)
        except OSError:
            pass
    with Image.open(os.path.join(HERE, "assets", "img", fn)) as im:
        w, h = im.size
    bw, bh = (VIEW_BOX_TRI_BIG if big else VIEW_BOX_TRI if tri else VIEW_BOX)[part]
    if not tri:                                  # tek urun: her gorunus kendi kutusunu doldurur
        return f'{IMG}{fn}" style="width:{w * min(bw / w, bh / h):.1f}mm;max-width:none;max-height:none'
    c = min(bw / max(x for x, _ in sizes), bh / max(y for _, y in sizes))
    return f'{IMG}{fn}" style="width:{w * c:.1f}mm;max-width:none;max-height:none'


def dims_strip(p):
    if not p.get("dimrows"):
        return dims_table(p)
    rows = list(p["dimrows"])
    rows += [("", "")] * (-len(rows) % 3)                 # son satir da tam (cizgili bos hucreler)
    trs = "".join("<tr>" + "".join(f'<td class="lbl">{e(k)}</td><td class="val">{em(v) if v else ""}</td>'
                                   for k, v in rows[i:i + 3]) + "</tr>" for i in range(0, len(rows), 3))
    return f'<table class="dgrid3">{trs}</table>'


SHOW_TOPVIEW = False


def olcu_file(pid):
    for k in ([f"olcu-{pid}-{LANG}.png"] if LANG != "en" else []) + [f"olcu-{pid}.png"]:
        if os.path.exists(os.path.join(HERE, "assets", "img", k)):
            return k
    return None


def p_prodR_v3(n, pid, ofile):
    """Tek olculu fotograf duzeni: sol ustte buyuk olculu urun, sagda iki egri, olcu tablosu, iki buyuk fotograf."""
    p = PRODUCTS[pid]
    sec = SECTION_OF[pid]
    d = p["dims"]
    curves = load_curves(d.get("curves"))
    charts = "".join(f'<div class="c3 ch{i}">{chart_svg(pan, 84, 40, d.get("series"))}</div>'
                     for i, pan in enumerate(curves["panels"])) if curves else ""
    cap = d.get("caption", "")
    capline = f'<p class="capline">{e(cap)}</p>' if cap else ""
    top_html = ""
    ust = None if "kombi" in ofile else olcu_file(f"ust-{ {'mt': 'mt2'}.get(pid, pid)}")                     # Blender ustten render + delik / kanal / genislik olculeri
    if ust:
        top_html = f'<img class="tv" src="{IMG}{ust}" alt="">'
    elif SHOW_TOPVIEW and len(d["images"]) == 1:   # ustten gorunus (kapali: delik/kanal/genislik artik olculu fotografta)
        top_html = f'<img class="tv" src="{IMG}{_view_file(d["images"][0], "ust")}" alt="">'
    elif SHOW_TOPVIEW and pid == "sd":
        top_html = f'<img class="tv" src="{IMG}{_view_file("dsd150", "ust")}" alt="">'
    inner = f"""
    {run_header(sec['title'], sec)}
    <div class="d3{'' if charts else ' nocharts'}">
      <div class="hd"><div class="eyebrow" style="color:{sec['accent']}">{e(pname(pid))}</div>
        <div class="h2">{e(T("Dimensions & technical data"))}</div></div>
      <div class="c3 front"><img class="fo" src="{IMG}{ofile}" alt="">{top_html}</div>
      {charts}
      <div class="tbl"><h3 class="dth">{e(T("Dimensions"))}</h3>{dims_strip(p)}{capline}{finish_line(p)}</div>
      <div class="ph">{photo_slot(pid, 1)}</div>
      <div class="ph">{photo_slot(pid, 2)}</div>
      <div class="cl">{callout(p)}</div>
    </div>
    {folio(n)}"""
    return page(inner, n, "", sec, pid)


def p_prodR_v2(n, pid):
    ofile = olcu_file(f"kombi-{pid}") or olcu_file(pid)
    if ofile:
        return p_prodR_v3(n, pid, ofile)
    p = PRODUCTS[pid]
    sec = SECTION_OF[pid]
    d = p["dims"]
    imgs = d["images"]
    big = not d.get("photos", True)                      # fotograf satiri yoksa cizimler ve grafikler buyur
    if len(imgs) == 3:                                  # MT: her boy icin on + ust gorunus ust uste
        cards = "".join(f'<div class="vcard tri"><span class="lbl">{e(d["labels"][k])}</span>'
                        f'<img src="{view_img(key, "on", True, big)}" alt=""><img src="{view_img(key, "ust", True, big)}" alt=""></div>'
                        for k, key in enumerate(imgs))
        views = f'<div class="v2views tri">{cards}</div>'
    else:
        key = imgs[0]
        views = (f'<div class="v2views">'
                 f'<div class="vcard"><span class="lbl">{e(T("Front view"))}</span><img src="{view_img(key, "on")}" alt=""></div>'
                 f'<div class="vcard"><span class="lbl">{e(T("Top view"))}</span><img src="{view_img(key, "ust")}" alt=""></div></div>')
    cap = d.get("caption", "")
    capline = f'<p class="capline">{e(cap)}</p>' if cap else ""
    photos = "".join(photo_slot(pid, k) for k in (1, 2))
    photo_row = (f'<div class="photos"><h3>{e(T("Photos"))}</h3><div class="prow two">{photos}</div></div>'
                 if d.get("photos", True) else "")
    inner = f"""
    {run_header(sec['title'], sec)}
    <div class="flow prodr prodr2{'' if photo_row else ' nophoto'}">
      <div>
        <div class="eyebrow" style="color:{sec['accent']}">{e(pname(pid))}</div>
        <div class="h2">{e(T("Dimensions & technical data"))}</div>
      </div>
      <div class="fit" data-max="1.0">{views}{charts_row(d, 44 if photo_row else 74)}
        <div class="dblk"><h3 class="dth">{e(T("Dimensions"))}</h3>{dims_strip(p)}
          <p class="capline">{e(T("All dimensions in mm."))}</p></div>{capline}{finish_line(p)}</div>
      {photo_row}
      {callout(p)}
    </div>
    {folio(n)}"""
    return page(inner, n, "", sec, pid)


def p_prodR(n, pid):
    if not MOBILE and (V2_ALL or pid in V2_PIDS):
        return p_prodR_v2(n, pid)
    p = PRODUCTS[pid]
    sec = SECTION_OF[pid]
    d = p["dims"]
    imgs = d.get("images", [])
    cap = d.get("caption", "")
    if len(imgs) == 3:                                   # MT: uc boy yan yana, tablo altta
        cards = "".join(f'<div class="dcard tri"><span class="lbl">{e(d["labels"][k])}</span>'
                        f'<img src="{card_img(key)}" alt=""></div>' for k, key in enumerate(imgs))
        drawing = f'<div class="dtri">{cards}</div><div class="blk">{dims_table(p)}</div>'
    elif d.get("kind") == "layout":                      # saildrive: montaj duzeni + kisa tablo
        drawing = (f'<div class="dcard wide"><img src="{card_img(imgs[0])}" alt=""></div>'
                   f'<p class="capline">{e(cap)}</p>'
                   f'<div class="dgrid sd"><div>{dims_table(p)}</div>'
                   f'<p class="capline">{e(T("Dimension drawing on request."))}</p></div>')
        cap = ""
    else:
        tall = "" if load_curves(d.get("curves")) else " tall"
        drawing = (f'<div class="dgrid{tall}"><div class="dcard"><img src="{card_img(imgs[0])}" alt=""></div>'
                   f'<div><h3 class="dth">{e(T("Dimensions"))}</h3>{dims_table(p)}'
                   f'<p class="capline">{e(T("All dimensions in mm."))}</p></div></div>')
    capline = f'<p class="capline">{e(cap)}</p>' if cap else ""
    photos = "".join(photo_slot(pid, k) for k in (1, 2, 3))
    inner = f"""
    {run_header(sec['title'], sec)}
    <div class="flow prodr">
      <div>
        <div class="eyebrow" style="color:{sec['accent']}">{e(pname(pid))}</div>
        <div class="h2">{e(T("Dimensions & technical data"))}</div>
      </div>
      <div class="fit" data-max="1.0">{drawing}{capline}{charts_row(d)}{finish_line(p)}</div>
      <div class="photos"><h3>{e(T("Photos"))}</h3><div class="prow">{photos}</div></div>
      {callout(p)}
    </div>
    {folio(n)}"""
    return page(inner, n, "", sec, pid)


CHART_COLORS = ["#12383f", "#17737d", "#5fb3bd"]
SHORE_COLOR = {"45": "#5fb3bd", "55": "#17737d", "65": "#12383f"}


def _axis_label(text):
    """'Load (Kg)' -> 'Load (kg)', 'Natural Frequency (Hz)' -> 'Natural frequency (Hz)'."""
    words = text.replace("(Kg)", "(kg)").split(" ")
    return " ".join([words[0]] + [w if w.startswith("(") else w.lower() for w in words[1:]])


def _log_fit(points):
    """Log-log dogru uydurma: orijinal grafikteki duz cizgiler duz cizilsin."""
    xs = [math.log10(x) for x, _ in points]
    ys = [math.log10(y) for _, y in points]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return points
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    x0, x1 = points[0][0], points[-1][0]
    return [[x0, 10 ** (a + b * math.log10(x0))], [x1, 10 ** (a + b * math.log10(x1))]]


def chart_svg(panel, w, h, only=None):
    """Sayisallastirilmis egriyi buyuk etiketli vektor grafik olarak cizer.

    Koordinatlar 0.1 mm biriminde (x10) yazilir; kucuk font boyutlarinda Chrome'un
    harf araliklarini yuvarlayip bozmasini onler. w, h: mm.
    """
    K = 10.0
    ml, mr, mt, mb = 13.5, 3.0, 9.0, 11.5
    pw, ph = w - ml - mr, h - mt - mb
    X, Y = dict(panel["x"]), dict(panel["y"])
    series = [s for s in panel["series"] if not only or s["label"].startswith(only)]
    if only and series:
        # eksen araligini bu urunun egrilerine gore daralt
        ymax = max(p[1] for s in series for p in s["points"]) * 1.3
        cands = [t for t in Y["ticks"] if t >= ymax]
        if cands and cands[0] < Y["max"]:
            Y["max"] = cands[0]
            Y["ticks"] = [t for t in Y["ticks"] if t <= Y["max"]]

    def norm(ax, v):
        if ax.get("scale") == "log":
            return (math.log10(v) - math.log10(ax["min"])) / (math.log10(ax["max"]) - math.log10(ax["min"]))
        return (v - ax["min"]) / (ax["max"] - ax["min"])

    def sx(v):
        return (ml + norm(X, v) * pw) * K

    def sy(v):
        return (mt + (1 - norm(Y, v)) * ph) * K

    def fmt(v):
        return f"{v:g}"

    def is125(v):
        m = v / 10 ** math.floor(math.log10(v))
        return any(abs(m - c) < 1e-6 for c in (1, 2, 5))

    def labelled(ticks, ax, pos, min_gap_mm):
        """Etiketlenecek tikler: log eksende 1-2-5; ust uctan baslayip cakismayanlar."""
        cand = [t for t in ticks if ax.get("scale") != "log" or is125(t)]
        out, last = set(), None
        for t in reversed(cand):
            p = pos(t) / K
            if last is None or abs(last - p) >= min_gap_mm:
                out.add(t)
                last = p
        return out

    fs_tick, fs_ax, fs_title = 2.8 * K, 3.2 * K, 3.4 * K           # ~7.9 / 9.1 / 9.6 pt
    o = [f'<svg class="chart" viewBox="0 0 {w * K:.0f} {h * K:.0f}" width="{w:.1f}mm" height="{h:.1f}mm">']
    cid = f"clip{abs(hash((panel.get('title'), w, h, only))) % 10**8}"
    o.append(f'<defs><clipPath id="{cid}"><rect x="{ml * K:.1f}" y="{mt * K:.1f}" '
             f'width="{pw * K:.1f}" height="{ph * K:.1f}"/></clipPath></defs>')
    xt, yt = X["ticks"], Y["ticks"]
    xl = labelled(xt, X, sx, 5.6)
    yl = labelled(yt, Y, sy, 3.9)
    for t in xt:
        x = sx(t)
        o.append(f'<line x1="{x:.1f}" y1="{mt * K:.1f}" x2="{x:.1f}" y2="{(mt + ph) * K:.1f}" class="gr"/>')
        if t in xl:
            o.append(f'<text x="{x:.1f}" y="{(mt + ph + 3.8) * K:.1f}" font-size="{fs_tick:.0f}" '
                     f'text-anchor="middle">{fmt(t)}</text>')
    for t in yt:
        y = sy(t)
        o.append(f'<line x1="{ml * K:.1f}" y1="{y:.1f}" x2="{(ml + pw) * K:.1f}" y2="{y:.1f}" class="gr"/>')
        if t in yl:
            o.append(f'<text x="{(ml - 1.4) * K:.1f}" y="{y + 0.95 * K:.1f}" font-size="{fs_tick:.0f}" '
                     f'text-anchor="end">{fmt(t)}</text>')
    o.append(f'<rect x="{ml * K:.1f}" y="{mt * K:.1f}" width="{pw * K:.1f}" height="{ph * K:.1f}" class="fr"/>')
    o.append(f'<text x="{(ml + pw / 2) * K:.1f}" y="{(h - 1.2) * K:.1f}" font-size="{fs_ax:.0f}" '
             f'text-anchor="middle" class="ax">{e(T(_axis_label(X["label"])))}</text>')
    o.append(f'<text transform="translate({3.2 * K:.1f} {(mt + ph / 2) * K:.1f}) rotate(-90)" '
             f'font-size="{fs_ax:.0f}" text-anchor="middle" class="ax">{e(T(_axis_label(Y["label"])))}</text>')
    o.append(f'<text x="{0.4 * K:.1f}" y="{4.4 * K:.1f}" font-size="{fs_title:.0f}" class="ti">'
             f'{e(T(panel.get("title", "")))}</text>')
    legend, all_pts = [], []
    for i, s in enumerate(series):
        m = re.search(r"(45|55|65) Shore", s["label"])
        col = SHORE_COLOR[m.group(1)] if m else CHART_COLORS[i % len(CHART_COLORS)]
        pts = s["points"]
        if X.get("scale") == "log" and Y.get("scale") == "log" and len(pts) > 2:
            pts = _log_fit(pts)
        dense = pts if len(pts) > 2 else [
            [pts[0][0] + (pts[1][0] - pts[0][0]) * k / 20, pts[0][1] + (pts[1][1] - pts[0][1]) * k / 20]
            for k in range(21)]
        all_pts += [(sx(px) / K, sy(py) / K) for px, py in dense
                    if X["min"] <= px <= X["max"] and Y["min"] <= py <= Y["max"]]
        d = " L".join(f"{sx(px):.1f},{sy(py):.1f}" for px, py in pts)
        o.append(f'<path d="M{d}" fill="none" stroke="{col}" stroke-width="6" '
                 f'stroke-linejoin="round" stroke-linecap="round" clip-path="url(#{cid})"/>')
        legend.append((col, m.group(0) if m else T(s["label"])))
    legend = list(dict.fromkeys(legend))            # ayni sertlik tek satir
    if len(legend) > 1:
        lw = 24.0
        lh = 1.8 + 3.9 * len(legend)
        corners = [(ml + pw - lw - 1.2, mt + 1.2), (ml + 1.2, mt + 1.2),
                   (ml + pw - lw - 1.2, mt + ph - lh - 1.2), (ml + 1.2, mt + ph - lh - 1.2)]

        def hits(c):
            x0, y0 = c
            return sum(1 for px, py in all_pts if x0 - 1 <= px <= x0 + lw + 1 and y0 - 1 <= py <= y0 + lh + 1)
        x0, y0 = min(corners, key=hits)
        o.append(f'<rect x="{x0 * K:.1f}" y="{y0 * K:.1f}" width="{lw * K:.1f}" height="{lh * K:.1f}" '
                 f'rx="8" class="lgbg"/>')
        for i, (col, lab) in enumerate(legend):
            yy = y0 + 1.2 + 3.9 * (i + 1) - 0.6
            o.append(f'<line x1="{(x0 + 1.6) * K:.1f}" y1="{(yy - 1.0) * K:.1f}" x2="{(x0 + 6.4) * K:.1f}" '
                     f'y2="{(yy - 1.0) * K:.1f}" stroke="{col}" stroke-width="9" stroke-linecap="round"/>')
            o.append(f'<text x="{(x0 + 8.0) * K:.1f}" y="{yy * K:.1f}" font-size="{fs_tick:.0f}" '
                     f'class="lg">{e(lab)}</text>')
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------------------
# Arka sayfalar
# ---------------------------------------------------------------------------
def bearing_val(v):
    """'1-1/4 in' -> 1-1/4 + kucuk birim; '3-1/4 ?' (kaynakta birim yok) -> isaretli."""
    num, _, unit = v.partition(" ")
    if unit == "?":
        return f'{e(num)}<sup>†</sup>'
    return f'{e(num)}<small>{e(unit)}</small>'


def bearing_table(title, rows):
    head = "".join(f"<th>{x}</th>" for x in "ABC")
    trs = "".join("<tr>" + "".join(f"<td>{bearing_val(v)}</td>" for v in r) + "</tr>" for r in rows)
    return (f'<div class="btab"><h3>{e(T(title))}<span>{len(rows)}</span></h3>'
            f'<table class="bt"><tr>{head}</tr>{trs}</table></div>')


def p_bearings_v2(n):
    """Saft yataklari: urun gorselleri + tum olcu listesi (bronz mm, bronz inc, fiber)."""
    with open(os.path.join(HERE, "assets", "bearings.json"), encoding="utf-8") as f:
        b = json.load(f)
    side = (f'{bearing_table("Fiber · mm", b["fiber_mm"])}'
            f'<div class="bimg"><img src="{IMG}bronze.jpg" alt=""><span>{e(T("Bronze shaft bearings"))}</span></div>'
            f'<div class="bimg"><img src="{IMG}fiber.jpg" alt=""><span>{e(T("Fiber shaft bearings"))}</span></div>'
            f'<p class="bnote">† {e(T("Unit not stated in the source listing. Please confirm before ordering."))}</p>')
    inner = f"""
    {run_header(T('Also from Novibrasyon'))}
    <div class="flow brg">
      <div>
        <div class="eyebrow">{e(T("Also from Novibrasyon"))}</div>
        <div class="h1">{e(T("Shaft bearings."))}</div>
        <p class="lead">{e(T("Bronze and fiber shaft bearings for smooth, efficient shaft rotation, available in metric and inch sizes."))}</p>
        <p class="bkey"><b>A</b> {e(T("Shaft / internal diameter"))}<b>B</b> {e(T("Outer diameter"))}<b>C</b> {e(T("Length"))}</p>
      </div>
      <div class="bgrid">
        {bearing_table("Bronze · mm", b["bronze_mm"])}
        {bearing_table("Bronze · inch", b["bronze_inch"])}
        <div class="bside">{side}
          <div class="bcontact"><div class="lbl">{e(T("Size not listed? · WhatsApp"))}</div>
            <div class="big">{e(COMPANY['whatsapp'])}</div>
            <div>{icon('mail')}{e(COMPANY['email'])}</div><div>{icon('globe')}{e(COMPANY['web'])}</div></div>
        </div>
      </div>
    </div>
    {folio(n)}"""
    return page(inner, n)


def p_bearings(n):
    if not MOBILE:
        return p_bearings_v2(n)

    def card(key, title, items):
        lis = "".join(f"<li>{icon('check')}<span>{e(T(t))}</span></li>" for t in items)
        return (f'<div class="bcard"><div class="im"><img src="{IMG}{key}.jpg" alt=""></div>'
                f'<h2>{e(T(title))}</h2><ul class="feat" style="grid-template-columns:1fr">{lis}</ul></div>')
    inner = f"""
    {run_header(T('Also from Novibrasyon'))}
    <div class="head">
      <div class="eyebrow">{e(T("Also from Novibrasyon"))}</div>
      <div class="h1">{e(T("Shaft bearings."))}</div>
      <p class="lead">{e(T("Bronze and fiber shaft bearings for smooth, efficient shaft rotation, available in metric and inch sizes."))}</p>
      <div class="bcards">
        {card('bronze', 'Bronze shaft bearings', [
            'Marine-grade bronze (CuSn12, CuSn10Pb10, etc.)',
            'High resistance to saltwater and chemicals',
            'Precision-engineered for low-friction shaft rotation',
            f'Operating temperature: −40{NB}°C to +150{NB}°C'])}
        {card('fiber', 'Fiber shaft bearings', [
            'High-performance fiber composite material',
            'Lighter than traditional metal bearings',
            'High resistance to seawater and chemicals',
            f'Operating temperature: −30{NB}°C to +120{NB}°C'])}
      </div>
    </div>
    <div class="contact-strip bottom">
      <div><div class="lbl">{e(T("Full size list · WhatsApp"))}</div><div class="big">{e(COMPANY['whatsapp'])}</div></div>
      <div class="ct">
        <div>{icon('mail')}{e(COMPANY['email'])}</div>
        <div>{icon('globe')}{e(COMPANY['web'])}</div>
      </div>
    </div>
    {folio(n)}"""
    return page(inner, n)


def p_order(n):
    inner = f"""
    {run_header(T('How to order'))}
    <div class="head">
      <div class="eyebrow">{e(T("How to order"))}</div>
      <div class="h1">{e(T("Ordering is simple."))}</div>
      <div class="steps">
        <div><em>1</em><b>{e(T("Tell us your engine"))}</b><span>{e(T("Engine make and model, and the position you need: front, rear, left, right or saildrive."))}</span></div>
        <div><em>2</em><b>{e(T("Send a photo"))}</b><span>{e(T("A photo of your current mount, its part number, or its stud thread, mounting centers and height."))}</span></div>
        <div><em>3</em><b>{e(T("We confirm and ship"))}</b><span>{e(T("FedEx Express or UPS Express. Insured and tracked, in 2–4 business days depending on destination and customs."))}</span></div>
      </div>
      <div class="order-ch"><b>{e(T("Easy ways to order"))}</b><span>{e(T("eBay, WhatsApp, our website or e-mail"))}</span><span class="emin">{e(T("Not sure which mount fits? Contact us before you order."))}</span></div>
      <div class="ship-img"><img src="{IMG}ship.jpg" alt=""></div>
    </div>
    <div class="contact-strip bottom">
      <div><div class="lbl">WhatsApp</div><div class="big">{e(COMPANY['whatsapp'])}</div></div>
      <div class="ct">
        <div>{icon('mail')}{e(COMPANY['email'])}</div>
        <div>{icon('globe')}{e(COMPANY['web'])}</div>
      </div>
    </div>
    {folio(n)}"""
    return page(inner, n)


EBAY_URL = "https://www.ebay.com/str/novibrasyonmarin"
BACK_LINEUP = [("100", "Yanmar"), ("sd230", "Saildrive"), ("450", "Cummins"), ("vv3", "Universal"),
               ("mt", "MT series")]


def p_back(n):
    addr = "<br>".join(e(a) for a in COMPANY["address"])
    wa = "https://wa.me/" + re.sub(r"\D", "", COMPANY["whatsapp"])
    mail = "mailto:" + COMPANY["email"]
    web = "https://" + COMPANY["web"]
    ebay = EBAY_URL
    qrs = [(wa, T("Ask on WhatsApp"), T("Scan and send us a photo of your mount. We reply with the right part.")),
           (mail, T("E-mail"), T("Scan to e-mail us a question or an order.")),
           (web, T("Website"), T("Scan to see every product online and order.")),
           (ebay, T("eBay store"), T("Scan to see our eBay store and reviews."))]
    qr_html = "".join(f'<div class="bq"><div class="bqr">{qr_svg(u)}</div><b>{e(h)}</b><span>{e(d)}</span></div>' for u, h, d in qrs)
    shots = {1: ("step-motor", ""), 2: ("eski-yeni", "Left: a new Novibrasyon mount. Right: a worn mount."),
             3: ("ship", "")}

    def shot(i):
        img, cap = shots[i]
        capt = f"<figcaption>{e(T(cap))}</figcaption>" if cap else ""
        return f'<figure class="bk-on s{i}"><img src="{IMG}{img}.jpg" alt="">{capt}</figure>'
    steps = "".join(f'<div>{shot(i)}<em>{i}</em><b>{e(T(h))}</b><span>{e(T(d))}</span></div>'
                    for i, (h, d) in enumerate([
        ("Tell us your engine", "Engine make and model, and the position you need: front, rear, left, right or saildrive."),
        ("Not sure? Send a photo", "If you don't know the model, a photo of your old mount is enough. We find the right part for you."),
        ("We confirm and ship", "FedEx Express or UPS Express. Insured and tracked, in 2–4 business days depending on destination and customs."),
    ], 1))
    inner = f"""
    <img class="back-logo" src="{LOGO['white']}" alt="Novibrasyon">
    <div class="back-tag">{e(T("Feel the quality. Enjoy the silence."))}</div>
    <div class="bk-h first">{e(T("Ordering in 3 steps"))}</div>
    <div class="bk-steps">{steps}</div>
    <div class="bk-h">{e(T("Easy ways to order"))}</div>
    <p class="bk-lead">{e(T("Order on eBay, by WhatsApp or on our website. You can also ask us anything by e-mail."))}</p>
    <div class="bk-qr">{qr_html}</div>
    <div class="bk-addr">{icon('pin')}<span>{addr}</span></div>
    <div class="bk-addr">{icon('chat')}<span>WhatsApp {e(COMPANY['whatsapp'])} · {e(COMPANY['email'])} · {e(COMPANY['web'])}</span></div>
    <div class="back-foot">{e(Tf("Thank you for choosing {name}.", name=COMPANY['name']))}<br>
      {e(T("Engine brand names are used only to show compatibility. Specifications and images may change without notice. Please confirm fitment before ordering."))}</div>"""
    return page(inner, n, "dark back")


RENDER = {
    "cover": lambda n, a: p_cover(n), "welcome": lambda n, a: p_welcome(n),
    "about": lambda n, a: p_about(n), "aboutR": lambda n, a: p_about_r(n),
    "tech": lambda n, a: p_tech(n), "finderT": p_finder_table,
    "partnos": lambda n, a: p_partnos(n), "layout": lambda n, a: p_layout(n, a),
    "divider": p_divider, "photo": p_photo, "prodL": p_prodL, "prodR": p_prodR,
    "bearings": lambda n, a: p_bearings(n), "order": lambda n, a: p_order(n),
    "back": lambda n, a: p_back(n),
}


def build_html(bleed_mm, img_dir="assets/img/"):
    global IMG
    IMG = img_dir
    body = "\n".join(RENDER[k](i, a) for i, (k, a) in enumerate(PAGES, start=1))
    IMG = "assets/img/"
    # tasmali surumde Chrome sayfa genisligini tam puana yuvarlar; 0.2 mm pay birakilir
    extra = 0.2 if bleed_mm else 0
    w, h = 210 + 2 * bleed_mm + extra, 297 + 2 * bleed_mm + extra
    title = Tf("Novibrasyon Marin — Product Catalogue {year}", year=COMPANY["year"])
    return f"""<!doctype html>
<html lang="{LANG}"><head><meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>{font_css()}</style>
<link rel="stylesheet" href="styles.css">
<style>@page {{ size: {w}mm {h}mm; margin: 0; }} :root {{ --b: {bleed_mm}mm; }}</style>
</head><body>
{body}
<script>{AUTOFIT_JS}</script>
</body></html>"""


# Her .fit blogunu sayfaya sigacak sekilde buyutur / kucultur (zoom).
AUTOFIT_JS = """
(function () {
  var MM = 96 / 25.4;
  function run() {
    document.querySelectorAll('.flow').forEach(function (flow) {
      var fit = flow.querySelector('.fit');
      if (!fit) return;
      var call = flow.querySelector('.callout');
      var max = parseFloat(fit.dataset.max || '1.2');
      function limit() {
        return call ? call.getBoundingClientRect().top : flow.getBoundingClientRect().bottom;
      }
      function slack() { return limit() - fit.getBoundingClientRect().bottom; }
      function over() { return flow.scrollHeight > flow.clientHeight + 1 || slack() < 5 * MM; }
      var z = 1;
      while (over() && z > 0.7) { z -= 0.02; fit.style.zoom = z; }
      while (!over() && slack() > 12 * MM && z < max) {
        z += 0.02; fit.style.zoom = z;
        if (over()) { z -= 0.02; fit.style.zoom = z; break; }
      }
      fit.dataset.zoom = z.toFixed(2);
    });
    // deniz cizimi: icerigin bittigi yerden sayfa altina kadar; yer azsa gizlenir
    document.querySelectorAll('.sea').forEach(function (sea) {
      var trim = sea.parentNode, flow = trim.querySelector('.flow');
      var tr = trim.getBoundingClientRect(), bottom = tr.top;
      Array.prototype.forEach.call(flow.children, function (c) {
        bottom = Math.max(bottom, c.getBoundingClientRect().bottom);
      });
      var h = tr.bottom - bottom - 5 * MM;
      if (h < 24 * MM) { sea.style.display = 'none'; return; }
      sea.style.height = 'calc(' + Math.min(h, 100 * MM).toFixed(1) + 'px + var(--b))';
    });
    document.body.dataset.fitted = '1';
  }
  if (document.fonts && document.fonts.ready) { document.fonts.ready.then(run); } else { run(); }
})();
"""


def chrome():
    for c in CHROME_CANDIDATES:
        if os.path.exists(c):
            return c
    sys.exit("Chrome / Edge bulunamadi.")


def to_pdf(html_name, pdf_name):
    src = "file:///" + os.path.join(HERE, html_name).replace("\\", "/")
    out = os.path.join(HERE, pdf_name)
    subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--allow-file-access-from-files", "--run-all-compositor-stages-before-draw",
                    "--virtual-time-budget=30000", f"--print-to-pdf={out}", src],
                   check=True, capture_output=True)
    return out


def set_print_boxes(path, bleed_mm=3):
    """Baski PDF'ine TrimBox / BleedBox yazar (kesim olcusu: tam A4, 3 mm tasma)."""
    import pymupdf
    mm = 72 / 25.4
    doc = pymupdf.open(path)
    for pg in doc:
        r = pg.mediabox
        pg.set_bleedbox(r)
        pg.set_trimbox(pymupdf.Rect(bleed_mm * mm, bleed_mm * mm, (bleed_mm + 210) * mm, (bleed_mm + 297) * mm))
    tmp = path + ".tmp"
    doc.save(tmp, garbage=3, deflate=True)
    doc.close()
    os.replace(tmp, path)


def make_mail_images(max_long=1300, quality=74):
    """E-posta surumu icin kucultulmus JPEG kopyalari (assets/img-mail/)."""
    src_dir = os.path.join(HERE, "assets", "img")
    dst_dir = os.path.join(HERE, "assets", "img-mail")
    os.makedirs(dst_dir, exist_ok=True)
    for fn in os.listdir(src_dir):
        if not fn.lower().endswith(".jpg"):
            continue
        src, dst = os.path.join(src_dir, fn), os.path.join(dst_dir, fn)
        if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
            continue
        with Image.open(src) as im:
            im = im.convert("RGB")
            im.thumbnail((max_long, max_long), Image.LANCZOS)
            im.save(dst, "JPEG", quality=quality, optimize=True, progressive=True)


def check_pdf(path):
    """Her sayfayi cizer; eksik kaynak uyarisi varsa hata verir."""
    import pymupdf
    pymupdf.TOOLS.reset_mupdf_warnings()
    doc = pymupdf.open(path)
    for pg in doc:
        pg.get_pixmap(dpi=20)
    warnings = pymupdf.TOOLS.mupdf_warnings()
    doc.close()
    if "cannot find" in warnings or "error" in warnings.lower():
        raise SystemExit(f"PDF kontrolu basarisiz: {path}\n{warnings}")


def ensure_photo_dirs():
    for pid in PRODUCTS:
        os.makedirs(os.path.join(HERE, PHOTOS, pid), exist_ok=True)


OUT_NAMES = {
    "tr": ("Novibrasyon-Katalog-{y}-TR.pdf", "Novibrasyon-Katalog-{y}-TR-BASKI-3mm-tasma.pdf",
           "Novibrasyon-Katalog-{y}-TR-eposta.pdf"),
    "en": ("Novibrasyon-Catalogue-{y}-EN.pdf", "Novibrasyon-Catalogue-{y}-EN-PRINT-3mm-bleed.pdf",
           "Novibrasyon-Catalogue-{y}-EN-email.pdf"),
}


MOBILE_NAMES = {"tr": "Novibrasyon-Katalog-{y}-TR-mobil.pdf", "en": "Novibrasyon-Catalogue-{y}-EN-mobile.pdf"}


def build_mobile():
    """Telefon icin 9:16 sayfali katalog (mobile.py)."""
    import mobile
    make_mail_images()
    html_m = mobile.build_mobile_html(sys.modules[__name__])
    name = f"katalog-{LANG}-mobil.html"
    with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
        f.write(html_m)
    if LANG == "tr" and MISSING:
        print(f"[tr] UYARI (mobil): cevirisi olmayan metinler: {MISSING}")
    pdf = to_pdf(name, MOBILE_NAMES[LANG].format(y=COMPANY["year"]))
    check_pdf(pdf)
    import pymupdf
    with pymupdf.open(pdf) as d:
        n = len(d)
    print(f"PDF: {pdf}  ({os.path.getsize(pdf) / 1e6:.1f} MB, {n} sayfa, mobil)")


def main():
    if "--lang" not in sys.argv:                  # iki dil, ayri ayri
        for lang in ("tr", "en"):
            subprocess.run([sys.executable, os.path.abspath(__file__), "--lang", lang] + sys.argv[1:], check=True)
        return
    ensure_photo_dirs()
    setup()
    if "--mobile" in sys.argv:                    # yalnizca mobil surum
        build_mobile()
        return
    only_html = "--html" in sys.argv or COLLECT
    names = {k: f"katalog-{LANG}{k}.html" for k in ("", "-baski", "-eposta")}
    with open(os.path.join(HERE, names[""]), "w", encoding="utf-8") as f:
        f.write(build_html(0))
    if COLLECT:
        with open(os.path.join(HERE, "_metinler.json"), "w", encoding="utf-8") as f:
            json.dump(SEEN, f, ensure_ascii=False, indent=1)
        print(f"{len(SEEN)} metin toplandi -> _metinler.json")
        return
    with open(os.path.join(HERE, names["-baski"]), "w", encoding="utf-8") as f:
        f.write(build_html(3))
    print(f"[{LANG}] HTML hazir: {len(PAGES)} sayfa")
    if len(PAGES) % 4:
        print(f"[{LANG}] UYARI: sayfa sayisi 4'un kati degil ({len(PAGES)})")
    if LANG == "tr":
        miss = os.path.join(HERE, "ceviri-eksik.txt")
        if MISSING:
            with open(miss, "w", encoding="utf-8") as f:
                f.write("\n".join(MISSING))
            print(f"[tr] UYARI: {len(MISSING)} metnin cevirisi yok -> ceviri-eksik.txt")
        elif os.path.exists(miss):
            os.remove(miss)
    if only_html:
        return
    make_mail_images()
    with open(os.path.join(HERE, names["-eposta"]), "w", encoding="utf-8") as f:
        f.write(build_html(0, "assets/img-mail/"))
    y = COMPANY["year"]
    pa, pb, pc = (n.format(y=y) for n in OUT_NAMES[LANG])
    a = to_pdf(names[""], pa)
    b = to_pdf(names["-baski"], pb)
    set_print_boxes(b)
    c = to_pdf(names["-eposta"], pc)
    for f in (a, b, c):
        check_pdf(f)
        print(f"PDF: {f}  ({os.path.getsize(f) / 1e6:.1f} MB)")
    build_mobile()


if __name__ == "__main__":
    main()

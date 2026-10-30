"""Mobil katalog: telefon ekrani icin 108 x 192 mm (9:16) sayfalar, tek sutun, dokunulabilir baglantilar.

build.py tarafindan cagrilir (ayni icerik ve ceviriler):  build_mobile_html(B)  -> HTML metni
"""
import os

W, H = 108.0, 192.0          # sayfa (mm)
PAD = 7.0                    # yan bosluk (mm)


def build_mobile_html(B):
    B.MOBILE = True
    B.IMG = "assets/img-mail/"
    T, Tf, e, em, icon = B.T, B.Tf, B.e, B.em, B.icon
    C = B.COMPANY
    IMG = B.IMG

    def img_key(key):
        if B.LANG != "en" and os.path.exists(os.path.join(B.HERE, "assets", "img", f"{key}-{B.LANG}.jpg")):
            return f"{key}-{B.LANG}"
        return key

    def mcard(key, label="", cls=""):
        lbl = f'<span class="lbl">{e(label)}</span>' if label else ""
        return f'<div class="mcard {cls}">{lbl}<img src="{IMG}{img_key(key)}.jpg" alt=""></div>'

    def eyebrow(t):
        return f'<div class="eyebrow">{e(t)}</div>'

    def h1(t):
        return f'<div class="h1">{e(t)}</div>'

    def lead(t):
        return f'<p class="lead">{e(t)}</p>'

    def sect(inner, sid="", cls=""):
        sid = f' id="{sid}"' if sid else ""
        return f'<section class="ms {cls}"{sid}>{inner}</section>'

    def contact_box():
        return f"""
        <div class="mcontact">
          <b>{e(T("Not sure it fits?"))}</b>
          <div>{icon('chat')}WhatsApp {e(C['whatsapp'])}</div>
          <div>{icon('mail')}{e(C['email'])}</div>
          <div class="soft">{icon('truck')}{e(T("FedEx or UPS Express · 2–4 business days · insured and tracked"))}</div>
        </div>"""

    out = []

    # ------------------------------------------------------------------ kapak
    vb = B.art_viewbox("engine-side")
    engine, calm = "", 30.0
    if vb:
        a = B.art_anchors("engine-side")
        ew, ex, horizon = 100.0, 6.0, H * 0.60
        sc = ew / vb[2]
        top = horizon - (a.get("bed_top_y", 700) - vb[1]) * sc
        pos = f"left:{ex:.1f}mm;top:{top:.1f}mm;width:{ew:.1f}mm;height:{vb[3] * sc:.1f}mm"
        engine = B.art_svg("engine-side", "cover-engine halo", pos) + B.art_svg("engine-side", "cover-engine", pos)
        if a.get("m-front"):
            calm = ex + (a["m-front"][0] - vb[0]) * sc
    wave = B.wave_path(x0=-3.0, x1=W + 3, calm_at=calm, amp=5.0)
    out.append(sect(f"""
      <img class="mc-bg" src="{IMG}cover-sea.jpg" alt="">
      <img class="mc-logo" src="{B.LOGO['white']}" alt="Novibrasyon">
      <div class="mc-kicker">{T("Product Catalogue")}<br>{C['year']}</div>
      <div class="mc-title">{T("Marine engine<br>mounts.")}</div>
      <div class="mc-sub">{e(T("Feel the quality. Enjoy the silence."))}</div>
      {engine}
      <svg class="mc-wave" viewBox="0 0 {W:g} 30" preserveAspectRatio="none">
        <path d="{wave}" fill="none" stroke="#bfeef2" stroke-width="1.4" stroke-opacity=".35"/>
        <path d="{wave}" fill="none" stroke="#ffffff" stroke-width=".35" stroke-linecap="round"/>
      </svg>
      <div class="mc-brands">{e(T("Engine mounts for Yanmar · Cummins · Caterpillar · Volvo Penta · MAN · Perkins"))}</div>
      <div class="mc-foot"><span>{C['web']}</span><span>WhatsApp {C['whatsapp']}</span></div>""",
                    "cover", "dark full mcover"))

    # ------------------------------------------------------------------ karsilama + icindekiler
    def irow(label, href, sub="", num=""):
        sub_html = f"<span>{e(T(sub))}</span>" if sub else ""
        num_html = f"<i>{e(num)}</i>" if num else ""
        return (f'<a class="irow" href="#{href}">{num_html}<b>{e(T(label))}</b>{sub_html}'
                f'<em>{icon("arrow")}</em></a>')
    fast = "".join([
        irow("How a mount works", "tech1", "Technical introduction"),
        irow("Engine finder", "finder", "Look up your engine"),
        irow("Part number finder", "partnos", "Your old mount"),
        irow("How to order", "order", "Three simple steps"),
    ])
    secs = "".join(irow(s["title"], "sec-" + s["id"], num=s["num"]) for s in B.SECTIONS)
    secs += irow("Shaft bearings", "bearings")
    out.append(sect(f"""
      <div class="m-photo"><img src="{IMG}welcome.jpg" alt=""></div>
      {eyebrow(Tf("Welcome to {name}", name=C['name']))}
      {h1(T("Feel the quality. Enjoy the silence."))}
      {lead(T("Novibrasyon Marin produces marine engine mounts and shaft bearings in Istanbul and ships them worldwide. Every mount in this catalogue is made to reduce engine vibration and noise, help keep the engine in line, and stand up to salt water and long hours at sea."))}
      <div class="mvalues">
        <div>{icon('waves')}<b>{e(T("Less vibration"))}</b><span>{em(T("Bonded rubber elements absorb engine vibration before it reaches the hull."))}</span></div>
        <div>{icon('shield')}<b>{e(T("Built for salt water"))}</b><span>{em(T("Galvanized steel, 316 stainless steel and marine-grade aluminum bodies."))}</span></div>
        <div>{icon('truck')}<b>{e(T("2–4 business days"))}</b><span>{em(T("FedEx or UPS Express, insured and tracked. Depends on destination and customs."))}</span></div>
      </div>
      <h3 class="sect">{e(T("Find it fast"))}</h3><div class="mindex">{fast}</div>
      <h3 class="sect">{e(T("In this catalogue"))}</h3><div class="mindex">{secs}</div>""", "welcome"))

    # ------------------------------------------------------------------ teknik giris
    parts = [("Stud", "Carries the engine foot."),
             ("Adjusting nuts", "Set the engine height for shaft alignment."),
             ("Rubber element", "Absorbs the vibration. Its hardness is given in Shore."),
             ("Metal housing", "Holds the rubber and takes the load."),
             ("Base flange", "Bolted to the engine bed."),
             ("Centre core", "The raised centre of the base plate, bonded into the rubber.")]
    lis = "".join(f'<li><i>{k + 1}</i><div><b>{e(T(a))}</b><span>{e(T(b))}</span></div></li>'
                  for k, (a, b) in enumerate(parts))
    out.append(sect(f"""
      {eyebrow(T("Technical introduction"))}
      {h1(T("From vibration to silence."))}
      {lead(T("A diesel engine shakes with every firing stroke. An engine mount is a rubber spring between the engine and the hull: it carries the weight of the engine and gearbox, keeps the shaft in line and stops most of the vibration before it reaches the boat."))}
      <div class="anat-card m">{B.art_svg("mount-anatomy", "anat", viewbox="10 175 990 685")}</div>
      <h3 class="sect">{e(T("Inside a Novibrasyon mount"))}</h3>
      <ol class="parts">{lis}</ol>
""", "tech1"))

    steps = [("Engine model", _finder_text(B)),
             ("Load at each mount", T("Engine and gearbox weight, shared between the mounts. The rear mounts often carry more, because the gearbox sits there.")),
             ("Fit", T("Stud thread, mounting hole centers and height must match your engine feet and engine bed.")),
             ("Rubber hardness", T("Chosen by the load at each mount: softer for light loads, harder for heavy ones."))]
    cards = "".join(f'<div class="kcard"><i>{k + 1}</i><b>{e(T(a))}</b><span>{e(b)}</span></div>'
                    for k, (a, b) in enumerate(steps))
    shore = [("45", "Soft", "Best isolation, for lighter loads."),
             ("55", "Medium", "Balanced isolation and load capacity."),
             ("65", "Hard", "Firm support for the heaviest loads.")]
    shore_html = "".join(f'<div class="sh s{v}"><em>{v}</em><small>Shore</small><b>{e(T(a))}</b>'
                         f'<span>{e(T(b))}</span></div>' for v, a, b in shore)
    signs = ["Cracked, split or crumbling rubber", "Rubber coming away from the metal",
             "The engine sits lower than before or the mount has collapsed",
             "Soft, swollen rubber from oil or diesel",
             "More vibration or noise, knocking when shifting gear",
             "Shaft seal or shaft bearing wearing fast, shaft out of line"]
    signs_html = "".join(f"<li>{icon('check')}<span>{e(T(s))}</span></li>" for s in signs)
    out.append(sect(f"""
      {eyebrow(T("Technical introduction"))}
      {h1(T("Choosing the right mount."))}
      {lead(T("Four things decide which mount is right for your engine."))}
      <div class="kcards m">{cards}</div>
      <div class="keep">
        <h3 class="sect">{e(T("Rubber hardness in Shore"))}</h3>
        <div class="shlab"><span>{e(T("softer"))}</span><span>{e(T("harder"))}</span></div>
        <div class="shbar"></div>
        <div class="shs">{shore_html}</div>
      </div>
      <h3 class="sect">{e(T("When is it time to replace?"))}</h3>
      <ul class="feat signs m">{signs_html}</ul>
      <p class="tipline">{e(T("Mounts age together: when one has failed, check all of them. After fitting new mounts, check the shaft alignment at the coupling and tighten the nuts to the recommended torque."))}</p>""",
                    "tech2"))

    # ------------------------------------------------------------------ motor bulucu
    fsteps = [("Find your engine brand", "Tap your brand in the list below."),
              ("Find your engine model", "The model is on the engine's name plate or in its manual."),
              ("Tap the mount", "Each box shows the mount code. Tap it to open the mount.")]
    fsteps_html = "".join(f'<div><em>{k + 1}</em><div><b>{e(T(a))}</b><span>{e(T(b))}</span></div></div>'
                          for k, (a, b) in enumerate(fsteps))
    brands = []
    for brand, _ in B.FINDER_ALL:
        if brand not in brands:
            brands.append(brand)
    bidx = "".join(f'<a href="#brand-{_slug(b)}"><b>{e(T(b))}</b><em>{icon("arrow")}</em></a>' for b in brands)
    out.append(sect(f"""
      {eyebrow(T("Engine finder"))}
      {h1(T("Find your mount in three steps."))}
      <div class="msteps">{fsteps_html}</div>
      <div class="keep"><h3 class="sect">{e(T("How to read a box"))}</h3>
        <div class="keychip">{B.mount_chip("100", "")}</div></div>
      <h3 class="sect">{e(T("Engine brands"))}</h3>
      <div class="mbidx">{bidx}</div>""", "finder"))

    rows = []
    for brand, brows in B.FINDER_ALL:
        rows.append(f'<div class="bband" id="brand-{_slug(brand)}"><span>{e(T(brand))}</span></div>')
        for k, (series, models, mounts) in enumerate(brows):
            models = T(models) if models and models != series else ""
            mhtml = f"<span>{em(models)}</span>" if models else ""
            chips = "".join(B.mount_chip(pid, pos) for pid, pos in mounts)
            rows.append(f'<div class="mfr{" alt" if k % 2 else ""}"><div class="en"><b>{em(T(series))}</b>{mhtml}</div>'
                        f'<div class="mcs">{chips}</div></div>')
    out.append(sect(f'{eyebrow(T("Engine finder"))}<div class="mfinder">{"".join(rows)}</div>', "finder-table"))

    # ------------------------------------------------------------------ parca numarasi
    pn = {}
    for pid, p in B.PRODUCTS.items():
        for label, nums in p.get("refs", []):
            brand = "Cummins" if label.startswith("Cummins") else label
            for num in nums:
                pn.setdefault((brand, num), []).append(pid)
    pn_html = []
    for brand in ["Yanmar", "Cummins", "Caterpillar", "Barry Controls"]:
        rank = {x: i for i, x in enumerate(B.PRODUCT_ORDER)}
        rank.update({x: rank[s] for x, s in B.SERIES_OF.items() if s in rank})
        items = sorted(((num, pids) for (b, num), pids in pn.items() if b == brand),
                       key=lambda it: (min(rank[x] for x in it[1]), it[0]))
        if not items:
            continue
        pn_html.append(f'<div class="brandhead">{e(brand)}</div>')
        for num, pids in items:
            pn_html.append(f'<div class="pnrow"><span class="pn">{e(num)}</span>'
                           f'<div class="mps">{"".join(B.mount_pill(x) for x in pids)}</div></div>')
    out.append(sect(f"""
      {eyebrow(T("Part number finder"))}
      {h1(T("Have a part number?"))}
      {lead(T("Find the original part number on your old mount or in your engine manual, then look it up here."))}
      <div class="mpn">{"".join(pn_html)}</div>""", "partnos"))

    # ------------------------------------------------------------------ bolumler ve urunler
    for sec in B.SECTIONS:
        lst = "".join(f'<a href="#prod-{pid}"><b>{e(B.pname(pid))}</b><span>{e(B.PRODUCTS[pid]["tagline"])}</span>'
                      f'<em>{icon("arrow")}</em></a>' for pid in sec["products"])
        mode = "product" if sec["image_mode"] == "product" else ""
        out.append(sect(f"""
          <div class="mdiv-img {mode}"><img src="{IMG}{sec['image']}.jpg" alt=""></div>
          <div class="mdiv-text">
            <div class="div-num">{sec['num']}</div>
            <div class="div-title">{e(sec['title'])}</div>
            <p class="div-intro">{e(sec['intro'])}</p>
            <div class="mdiv-list">{lst}</div>
          </div>""", "sec-" + sec["id"], "dark full"))
        for pid in sec["products"]:
            out.append(product_pages(B, pid, sec, mcard, contact_box, eyebrow, h1, lead, sect))

    # ------------------------------------------------------------------ yataklar, siparis, arka kapak
    def bcard(key, title, items):
        li = "".join(f"<li>{icon('check')}<span>{e(T(t))}</span></li>" for t in items)
        return (f'<div class="mbcard keep"><div class="im"><img src="{IMG}{key}.jpg" alt=""></div>'
                f'<h2>{e(T(title))}</h2><ul class="feat m">{li}</ul></div>')
    NB = B.NB
    out.append(sect(f"""
      {eyebrow(T("Also from Novibrasyon"))}
      {h1(T("Shaft bearings."))}
      {lead(T("Bronze and fiber shaft bearings for smooth, efficient shaft rotation, available in metric and inch sizes."))}
      {bcard('bronze', 'Bronze shaft bearings', ['Marine-grade bronze (CuSn12, CuSn10Pb10, etc.)',
            'High resistance to saltwater and chemicals', 'Precision-engineered for low-friction shaft rotation',
            f'Operating temperature: −40{NB}°C to +150{NB}°C'])}
      {bcard('fiber', 'Fiber shaft bearings', ['High-performance fiber composite material',
            'Lighter than traditional metal bearings', 'High resistance to seawater and chemicals',
            f'Operating temperature: −30{NB}°C to +120{NB}°C'])}
      <div class="mstrip keep"><small>{e(T("Full size list · WhatsApp"))}</small><b>{e(C['whatsapp'])}</b></div>""",
                    "bearings"))
    out.append(sect(f"""
      {eyebrow(T("How to order"))}
      {h1(T("Ordering is simple."))}
      <div class="msteps big">
        <div><em>1</em><div><b>{e(T("Tell us your engine"))}</b><span>{e(T("Engine make and model, and the position you need: front, rear, left, right or saildrive."))}</span></div></div>
        <div><em>2</em><div><b>{e(T("Send a photo"))}</b><span>{e(T("A photo of your current mount, its part number, or its stud thread, mounting centers and height."))}</span></div></div>
        <div><em>3</em><div><b>{e(T("We confirm and ship"))}</b><span>{e(T("FedEx Express or UPS Express. Insured and tracked, in 2–4 business days depending on destination and customs."))}</span></div></div>
      </div>
      <div class="m-photo2 keep"><img src="{IMG}ship.jpg" alt=""></div>
      <div class="mstrip keep"><small>WhatsApp</small><b>{e(C['whatsapp'])}</b></div>""", "order"))

    import re as _re
    wa = "https://wa.me/" + _re.sub(r"\D", "", C["whatsapp"])
    web = "https://" + C["web"]
    addr = "<br>".join(e(x) for x in C["address"])
    out.append(sect(f"""
      <img class="mc-bg" src="{IMG}cover-sea.jpg" alt="">
      <div class="mback">
        <img class="mb-logo" src="{B.LOGO['white']}" alt="Novibrasyon">
        <div class="mb-tag">{e(T("Feel the quality. Enjoy the silence."))}</div>
        <div class="mb-qr">
          <div>{B.qr_svg(wa)}<b>{e(T("Ask on WhatsApp"))}</b></div>
          <div>{B.qr_svg(web)}<b>{e(C['web'])}</b></div>
        </div>
        <div class="mb-ct">
          <a href="{wa}">{icon('chat')}<span><small>WhatsApp</small>{e(C['whatsapp'])}</span></a>
          <a href="mailto:{C['email']}">{icon('mail')}<span><small>{e(T("E-mail"))}</small>{e(C['email'])}</span></a>
          <a href="{web}">{icon('globe')}<span><small>Web</small>{e(C['web'])}</span></a>
          <div>{icon('insta')}<span><small>Instagram</small>{e(C['instagram'])}</span></div>
          <div>{icon('pin')}<span><small>{e(T("Address"))}</small>{addr}</span></div>
        </div>
        <div class="mb-foot">{e(T("Engine brand names are used only to show compatibility. Specifications and images may change without notice. Please confirm fitment before ordering."))}</div>
      </div>""", "back", "dark full mcover"))

    B.MOBILE = False
    B.IMG = "assets/img/"
    title = Tf("Novibrasyon Marin — Product Catalogue {year}", year=C["year"])
    import html as _h
    return f"""<!doctype html>
<html lang="{B.LANG}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_h.escape(title)}</title>
<style>{B.font_css()}</style>
<link rel="stylesheet" href="styles.css">
<link rel="stylesheet" href="styles-mobile.css">
<style>@page {{ size: {W:g}mm {H:g}mm; margin: 0; }}</style>
</head><body class="m">
{"".join(out)}
<script>
(function () {{   /* telefonda web sayfasi olarak acilirsa ekrana sigdir */
  if (!window.matchMedia || !matchMedia('screen').matches) return;
  var px = {W:g} * 96 / 25.4, z = Math.min(1, window.innerWidth / px);
  if (z < 1) document.documentElement.style.zoom = z;
}})();
</script>
</body></html>"""


def _slug(s):
    import re
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _finder_text(B):
    """'Motorunuzu motor rehberinde bulun (sayfa N)...' -> mobilde sayfa numarasiz."""
    import re
    t = B.Tf(B.FINDER_STEP_TEXT, p="§")
    return re.sub(r"\s*\([^)]*§[^)]*\)", "", t)


def product_pages(B, pid, sec, mcard, contact_box, eyebrow, h1, lead, sect):
    T, e, em, icon = B.T, B.e, B.em, B.icon
    p = B.PRODUCTS[pid]
    IMG = B.IMG
    # --- 1. sayfa: vitrin
    figs = []
    for key, cap in p["hero"]:
        sw = ""
        if cap and "Galvani" in cap:
            sw = '<span class="swatch"></span>'
        elif cap and ("stainless" in cap or "paslanmaz" in cap):
            sw = '<span class="swatch ss"></span>'
        capt = f"<figcaption>{sw}{e(cap)}</figcaption>" if cap else ""
        figs.append(f'<figure><img src="{IMG}{key}.jpg" alt="">{capt}</figure>')
    n = len(figs)
    glance = "".join(f"<div><b>{e(v)}</b><span>{e(lbl)}</span></div>" for v, lbl in B.keyfig_items(p))
    code_cls = "long" if len(p["code"]) >= 5 else ("mid" if len(p["code"]) >= 3 else "")
    brandline = B.brandline(pid)
    html = [sect(f"""
      {eyebrow(sec['title'])}
      <div class="brandline">{brandline}</div>
      <div class="code {code_cls}">{e(p['code'])}</div>
      <div class="tagline">{e(p['tagline'])}</div>
      <div class="mstage n{n}">{''.join(figs)}</div>
      <div class="mglance" style="{B.shade_vars(pid)}">{glance}</div>""", "prod-" + pid, "full mhero")]

    # --- 2. sayfa ve sonrasi: uyum, ozellikler, olculer
    d = p["dims"]
    blocks = [B.fits_block(p), m_variants(B, p)]
    blocks.append(m_mounting(B, p))
    blocks.append(B.refs_block(p))
    if p.get("dimrows"):
        blocks.append(f'<div class="blk"><h3>{e(T("Dimensions"))}</h3>{B.tiles_html(p["dimrows"])}</div>')
    blocks += [B.finish_line(p), B.features_block(p)]
    body = "".join(f'<div class="keep">{b}</div>' for b in blocks if b)

    dims = []
    imgs = d.get("images", [])
    lay = "triple" if len(imgs) == 3 else ("layout" if d.get("kind") == "layout" else "pair")
    curves = B.load_curves(d.get("curves"))
    if lay == "triple":
        cards = "".join(mcard(k, d["labels"][i], "tri") for i, k in enumerate(imgs))
        dims.append(f'<div class="mtri">{cards}</div>')
    else:
        for k in imgs:
            dims.append(mcard(k))
    cap = ""
    if lay in ("pair", "triple") and imgs:
        cap = T("All dimensions in mm.")
    if d.get("caption"):
        cap = (cap + " " + d["caption"]).strip()
    if cap:
        dims.append(f'<p class="cap-in">{e(cap)}</p>')
    if curves and lay == "pair":
        cw = 108.0 - 2 * 7.0 - 4
        for pan in curves["panels"]:
            dims.append(f'<div class="mchart keep">{B.chart_svg(pan, cw, 62, d.get("series"))}</div>')
    if d.get("tiles"):
        dims.append(f'<div class="blk keep"><h3>{e(d.get("tiles_title", ""))}</h3>'
                    f'{B.tiles_html(d["tiles"], "tiles wide")}</div>')
    photos = [B.find_photo(pid, k) for k in (1, 2, 3)]
    photos = [x for x in photos if x]
    if photos:
        dims.append(f'<h3 class="sect">{e(T("Photos"))}</h3><div class="mphotos">'
                    + "".join(f'<img src="{x}" alt="">' for x in photos) + "</div>")
    dims_title = d.get("title") or T("Dimensions")
    dims_html = "".join(dims)
    dims_block = (f'<div class="mdims"><div class="h2m">{e(dims_title)}</div>{dims_html}</div>'
                  if (imgs or photos or d.get("caption")) else "")
    html.append(sect(f"""
      {eyebrow(B.pname(pid))}
      <div class="h2m">{e(T("Fit & specifications"))}</div>
      {lead(p['intro'])}
      {body}
      {dims_block}
      <div class="keep"><div class="mnote">{e(p['note'])}</div>{contact_box()}</div>""", "", "mdetail"))
    return "".join(html)


def m_variants(B, p):
    T, e, em = B.T, B.e, B.em
    if not p.get("variants"):
        return ""
    heads, rows = p["variants"]
    note = f'<p class="fnote">{e(p["variants_note"])}</p>' if p.get("variants_note") else ""
    if len(heads) == 2:                        # Shore -> yuk karolari
        items = [(f"{T(h)} · {T('per mount')}", load[:-10] if load.endswith(" per mount") else T(load))
                 for h, load in rows]
        return (f'<div class="blk"><h3>{e(T("Rubber hardness & maximum load"))}</h3>'
                f'{B.tiles_html(items, "tiles vtiles")}{note}</div>')
    if len(heads) == 3:                        # VV3: secenek, yuk, uygulamalar
        cards = "".join(f'<div class="vcard"><div class="vh"><b>{e(r[0])}</b><em>{e(r[1])}</em></div>'
                        f'<p>{em(r[2])}</p></div>' for r in rows)
        return f'<div class="blk"><h3>{e(T("Available variants"))}</h3>{cards}{note}</div>'
    # MT: model x Shore yuk tablosu -> kart
    cards = []
    for r in rows:
        cells = "".join(f'<div><small>{e(heads[i])}</small><strong>{e(r[i])}</strong></div>' for i in range(1, len(r) - 1))
        cards.append(f'<div class="vcard"><div class="vh"><b>{e(r[0])}</b><span>{e(r[-1])}</span></div>'
                     f'<div class="vgrid">{cells}</div></div>')
    return f'<div class="blk"><h3>{e(T("Maximum static load per mount"))}</h3>{"".join(cards)}{note}</div>'


def m_mounting(B, p):
    T, e, em = B.T, B.e, B.em
    if not p.get("mounting"):
        return ""
    heads, rows = p["mounting"]
    cards = []
    for r in rows:
        dl = "".join(f"<dt>{e(heads[i])}</dt><dd>{em(r[i])}</dd>" for i in range(1, len(r)))
        cards.append(f'<div class="vcard"><div class="vh"><b>{e(r[0])}</b></div><dl>{dl}</dl></div>')
    return f'<div class="blk"><h3>{e(T("Mounting details"))}</h3>{"".join(cards)}</div>'

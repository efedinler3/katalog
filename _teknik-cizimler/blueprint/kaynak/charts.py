"""Yuk-cokme ve dogal frekans egrileri (cizim sayfasinin sag ustu), Novibrasyon cizim tarzinda.

Kaynaklar (piksel olcumu, 2026-10-20):
  75, 100, 150     sitedeki Novibrasyon grafikleri (75/100/150-yuk-cokme / -dogal-frekans-egrisi.jpg)
  200              Novibrasyon 200 teknik veri foyu
  VV1, VV2, VV3    sitedeki ortak VV grafigi (log-log; her cizginin iki ucu olculdu)
  50, 70, SD150, SD230, SD430   Ellebogen teknik foyleri (bizde grafik yok; 75 / 100 / 150 / 200'de Ellebogen
                   egrileri bizimkilerle uyumlu: frekans egrileri %2 icinde ayni, yuk-cokme egimi 75 ve 200'de ayni,
                   100 ve 150'de %7-10 fark)
Dogrusal yuk-cokme: W = k d (k kg/mm). Dogal frekans: W = A / f^2 (A kg Hz^2; olculen egrilere oturuyor).
VV: iki uc nokta arasinda log-log dogru (W = Wa (x / xa)^m).
400, 450, 500, 600, MT1-3: kaynak yok -> grafik cizilmez.
"""
import math

CH = {
    "50": dict(src="ELL", ld=dict(x=(0, 5, 1), y=(0, 40, 5), k=[(None, 8.46)]),
               nf=dict(x=(10, 20, 1), y=(0, 40, 5), A=[(None, 4620.0)])),
    "70": dict(src="ELL", ld=dict(x=(0, 5, 1), y=(0, 40, 5), k=[(None, 8.45)]),
               nf=dict(x=(9, 20, 1), y=(0, 40, 5), A=[(None, 3370.0)])),
    "75": dict(src="NV", ld=dict(x=(0, 6, 1), y=(0, 40, 5), k=[(None, 7.6)]),
               nf=dict(x=(7, 20, 1), y=(0, 40, 5), A=[(None, 2230.0)])),
    "100": dict(src="NV", ld=dict(x=(0, 6, 1), y=(0, 80, 10), k=[(None, 13.4)]),
                nf=dict(x=(7, 20, 1), y=(0, 80, 10), A=[(None, 4360.0)])),
    "150": dict(src="NV", ld=dict(x=(0, 6, 1), y=(0, 100, 20), k=[(None, 15.1)]),
                nf=dict(x=(7, 20, 1), y=(0, 100, 20), A=[(None, 6780.0)])),
    "200": dict(src="NV", ld=dict(x=(0, 5, 1), y=(0, 150, 25), k=[(None, 30.0)]),
                nf=dict(x=(7, 20, 1), y=(0, 150, 25), A=[(None, 13700.0)])),
    "SD150": dict(src="ELL", ld=dict(x=(0, 7, 1), y=(0, 100, 20), k=[(None, 15.0)]),
                  nf=dict(x=(6, 20, 1), y=(0, 100, 20), A=[(None, 4545.0)])),
    "SD230": dict(src="ELL", ld=dict(x=(0, 5, 1), y=(0, 150, 25), k=[(None, 30.1)]),
                  nf=dict(x=(6, 20, 1), y=(0, 150, 25), A=[(None, 12940.0)])),
    "SD430": dict(src="ELL", ld=dict(x=(0, 5, 1), y=(0, 175, 25), k=[(None, 38.9)]),
                  nf=dict(x=(6, 20, 1), y=(0, 175, 25), A=[(None, 17375.0)])),
    "VV1": dict(src="NV",
                ld=dict(x=(0, 5, 1), y=(0, 100, 10),
                        seg=[("45", (1.014, 12.2), (3.936, 46.1)), ("55", (1.014, 20.4), (3.688, 69.0)),
                             ("65", (1.014, 28.4), (3.648, 93.9))]),
                nf=dict(x=(7, 20, 1), y=(0, 100, 10),
                        seg=[("45", (8.688, 46.3), (17.106, 12.2)), ("55", (9.655, 68.7), (19.289, 18.6)),
                             ("65", (10.741, 82.8), (19.803, 26.9))])),
    "VV2": dict(src="NV",
                ld=dict(x=(0, 6, 1), y=(0, 300, 50),
                        seg=[("45", (1.019, 23.1), (5.482, 119.6)), ("55", (1.024, 37.2), (5.371, 190.4)),
                             ("65", (1.019, 51.0), (5.426, 279.0))]),
                nf=dict(x=(7, 20, 1), y=(0, 300, 50),
                        seg=[("45", (7.266, 108.8), (17.436, 20.9)), ("55", (8.095, 163.0), (18.541, 33.2)),
                             ("65", (8.386, 267.9), (19.225, 52.3))])),
    "VV3": dict(src="NV",
                ld=dict(x=(0, 6, 1), y=(0, 900, 100),
                        seg=[("55", (1.014, 88.9), (5.979, 545.2)), ("65", (1.019, 162.7), (4.724, 781.7))]),
                nf=dict(x=(7, 20, 1), y=(0, 900, 100),
                        seg=[("55", (7.334, 518.6), (18.541, 84.8)), ("65", (8.312, 775.0), (19.673, 174.7))])),
}

# MT1-3 (2026-10-20, sahibin onayi: olcum gelene kadar HESAPLANMIS egri): katalogdaki takoz basina maks. yuk
# (45 / 55 / 65 Shore) ve bilinen 12 modelin tasarim noktasi: maks. yukte ~5 mm cokme (VV1 3,6-3,9 / VV2 5,4 /
# VV3 4,7-6,0 / 200 5,0 / SD150 6,7 mm). Dogrusal: k = Wmaks / 5 mm. Dogal frekans statik: W = 248,4 k / f^2.
D_MAX = 5.0


def _calc(loads, ymax, ystep):
    k = [(str(sh), w / D_MAX, w) for sh, w in loads]
    return dict(src="CALC", ld=dict(x=(0, 6, 1), y=(0, ymax, ystep), k=k),
                nf=dict(x=(6, 20, 1), y=(0, ymax, ystep), A=[(lab, 248.4 * kk, w) for lab, kk, w in k]))


CH["MT1"] = _calc([(45, 80), (55, 140), (65, 200)], 200, 25)
CH["MT2"] = _calc([(45, 140), (55, 220), (65, 350)], 350, 50)
CH["MT3"] = _calc([(45, 200), (55, 400), (65, 550)], 600, 100)

TXT = {
    "tr": dict(ld="YÜK-ÇÖKME EĞRİSİ", nf="DOĞAL FREKANS EĞRİSİ", load="Yük (kg)", defl="Çökme (mm)",
               freq="Doğal frekans (Hz)", shore="Shore",
               calc="Hesaplanmış eğri: maksimum yükte 5 mm çökme varsayımı · ölçümle doğrulanacak"),
    "en": dict(ld="LOAD-DEFLECTION CURVE", nf="NATURAL FREQUENCY CURVE", load="Load (kg)", defl="Deflection (mm)",
               freq="Natural frequency (Hz)", shore="Shore",
               calc="Calculated curves: 5 mm deflection assumed at maximum load · to be verified by measurement"),
}


def _seg_fn(a, b):
    """Log-log dogru: W = Wa (x / xa)^m."""
    m = math.log(b[1] / a[1]) / math.log(b[0] / a[0])
    return lambda x: a[1] * (x / a[0]) ** m


def series(spec, kind):
    """[(etiket, [(x, W), ...])] egri noktalari (cerceveye kirpilmis)."""
    x0, x1, _ = spec["x"]
    y0, y1, _ = spec["y"]
    out = []
    if "k" in spec:
        for lab, k, *wm in spec["k"]:
            xe = min(x1, min([y1, *wm]) / k)
            out.append((lab, [(x0 + (xe - x0) * i / 40, k * (x0 + (xe - x0) * i / 40)) for i in range(41)]))
    elif "A" in spec:
        for lab, A, *wm in spec["A"]:
            fs = max(x0, math.sqrt(A / min([y1, *wm])))
            pts = [(f, A / f / f) for f in (fs + (x1 - fs) * i / 120 for i in range(121))]
            out.append((lab, pts))
    elif "pts" in spec:                                  # kendi olcumumuz: [(etiket, [(x, W), ...])]
        for lab, pts in spec["pts"]:
            out.append((lab, sorted(pts)))
    else:
        for lab, a, b in spec["seg"]:
            fn = _seg_fn(a, b)
            if kind == "ld":
                xs = [b[0] * i / 120 for i in range(121)]
            else:
                xs = [a[0] + (b[0] - a[0]) * i / 120 for i in range(121)]
            pts = [(x, fn(x) if x > 0 else 0.0) for x in xs]
            pts = [(x, w) for (x, w) in pts if w <= y1 * 1.0001]
            out.append((lab, pts))
    return out


def draw_chart(sh, x, y, w, spec, kind, title, xlab, ylab, curve_label):
    """Tek grafik blogu: (x, y) sol ust kose, w genislik (mm)."""
    from bp import esc
    px0, py0 = x + 7.5, y + 5.0
    pw = w - 9.5
    ph = pw
    X0, X1, XS = spec["x"]
    Y0, Y1, YS = spec["y"]
    sx = lambda v: px0 + (v - X0) / (X1 - X0) * pw
    sy = lambda v: py0 + ph - (v - Y0) / (Y1 - Y0) * ph
    sh.text(x + w / 2 + 2.5, y + 2.2, title, 1.9, "middle", 600, ls=0.25)
    v = X0
    while v <= X1 + 1e-9:
        sh.line(sx(v), py0, sx(v), py0 + ph, "grid")
        sh.text(sx(v), py0 + ph + 2.4, f"{v:g}", 1.45, "middle")
        v += XS
    v = Y0
    while v <= Y1 + 1e-9:
        sh.line(px0, sy(v), px0 + pw, sy(v), "grid")
        sh.text(px0 - 0.9, sy(v) + 0.5, f"{v:g}", 1.45, "end")
        v += YS
    sh.rect(px0, py0, pw, ph, "mid")
    sh.text(px0 + pw / 2, py0 + ph + 5.4, xlab, 1.6, "middle", 600)
    sh.text(x + 1.4, py0 + ph / 2, ylab, 1.6, "middle", 600, rot=-90)
    sers = series(spec, kind)
    for i, (lab, pts) in enumerate(sers):
        d = "M" + " L".join(f"{sx(a):.3f},{sy(b):.3f}" for a, b in pts)
        sh.add(f'<path class="curve" d="{d}"/>')
        # etiket: egrinin ortasina yakin, egime paralel, ustte
        j = int(len(pts) * (0.55 if kind == "ld" else 0.42))
        j = max(1, min(len(pts) - 2, j))
        (ax, ay), (bx, by) = (sx(pts[j - 1][0]), sy(pts[j - 1][1])), (sx(pts[j + 1][0]), sy(pts[j + 1][1]))
        ang = math.degrees(math.atan2(by - ay, bx - ax))
        cx, cy = sx(pts[j][0]), sy(pts[j][1])
        nx, ny = math.sin(math.radians(ang)), -math.cos(math.radians(ang))
        txt = curve_label if lab is None else f"{lab} Shore"
        tx, ty = cx + nx * 0.9, cy + ny * 0.9
        sh.add(f'<text x="{tx:.3f}" y="{ty:.3f}" font-size="1.45" font-weight="600" text-anchor="middle" '
               f'letter-spacing="0.1" transform="rotate({ang:.2f} {tx:.3f} {ty:.3f})">{esc(txt)}</text>')


def draw_charts(sh, code, lang, x=187.0, y=11.0, w=53.0, gap=1.5):
    c = CH.get(code)
    if not c:
        return False
    t = TXT[lang]
    name = f"NOVIBRASYON {code}"
    draw_chart(sh, x, y, w, c["ld"], "ld", t["ld"], t["defl"], t["load"], name)
    draw_chart(sh, x + w + gap, y, w, c["nf"], "nf", t["nf"], t["freq"], t["load"], name)
    if c.get("src") == "CALC":
        sh.text(x + 7.5, y + w + 5.5, t["calc"], 1.6, "start", 600)
    return True


def _nice(v):
    p = 10 ** math.floor(math.log10(v))
    for k in (1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if k * p >= v:
            return k * p
    return 10 * p


def _step(vmax, n=8):
    p = 10 ** math.floor(math.log10(vmax))
    for k in (0.1, 0.2, 0.25, 0.5, 1, 2, 2.5, 5):
        if vmax / (k * p) <= n:
            return k * p
    return p


def load_measurements(folder):
    """Olcum formunun kayitlari (ArtifactData list out_dir: <folder>/olcumler/<id>.json) -> CH girdileri.
    Bloklar (400-600): tek egri; MT1-3: sertlik basina bir egri. Dogal frekans f = 15,76 / sqrt(cokme mm)."""
    import glob
    import json
    import os
    groups = {}
    for fp in glob.glob(os.path.join(folder, "olcumler", "*.json")):
        d = json.load(open(fp, encoding="utf-8"))
        d = d.get("data", d)
        pts = [(float(q["mm"]), float(q["kg"])) for q in d.get("points", []) if q.get("mm") is not None]
        if sum(1 for x, w in pts if x > 0) < 2:
            continue
        model = str(d.get("model"))
        lab = None if d.get("shore") in (None, "") else str(int(d["shore"]))
        groups.setdefault(model, []).append((lab, pts))
    out = {}
    for model, sers in groups.items():
        sers.sort(key=lambda t: t[0] or "")
        xm = _nice(max(x for _, p in sers for x, w in p) * 1.1)
        wm = _nice(max(w for _, p in sers for x, w in p) * 1.05)
        nf = [(lab, [(15.76 / math.sqrt(x), w) for x, w in p if x > 0]) for lab, p in sers]
        fmin = math.floor(min(f for _, p in nf for f, w in p))
        fmax = math.ceil(max(f for _, p in nf for f, w in p))
        fmin, fmax = max(1, min(fmin, 7)), max(fmax, 20)
        out[model] = dict(src="OLCUM",
                          ld=dict(x=(0, xm, _step(xm, 8)), y=(0, wm, _step(wm, 8)), pts=sers),
                          nf=dict(x=(fmin, fmax, 1 if fmax - fmin <= 16 else 2), y=(0, wm, _step(wm, 8)), pts=nf))
    return out

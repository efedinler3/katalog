"""Yeni teknik cizimleri ve egrileri kataloga aktarir.

1. ../tr/<kod>.png ve ../en/<kod>.png sayfalarinin sol sutunu (on + ust gorunus) -> assets/img/<anahtar>[-tr].jpg
2. charts.CH verisi -> assets/curves/<id>.json (katalogun egri formati)
Calistirma: python katalog_aktar.py   (sonra katalogda: python build.py)
"""
import json
import math
import os

from PIL import Image, ImageChops

import charts as BC

HERE = os.path.dirname(os.path.abspath(__file__))
BP = os.path.dirname(HERE)
KAT = os.path.dirname(os.path.dirname(BP))
IMG = os.path.join(KAT, "assets", "img")
CUR = os.path.join(KAT, "assets", "curves")

# katalog gorsel anahtari -> cizim sayfasi kodu
DRAW = {"d50": "50", "d70": "70", "d75": "75", "d100": "100", "d150": "150", "d200": "200",
        "d400": "400", "d450": "450", "d500": "500", "d600": "600",
        "dsd150": "SD150", "dsd230": "SD230", "dsd430": "SD430",
        "dvv1": "VV1", "dvv2": "VV2", "dvv3": "VV3", "dmt1": "MT1", "dmt2": "MT2", "dmt3": "MT3"}


def crop_drawing(src):
    im = Image.open(src).convert("RGB")
    im = im.crop((40, 40, 1862, 2062))                   # sol sutun; grafikler (x >= 187 mm) ve antet disarida
    bg = Image.new("RGB", im.size, (255, 255, 255))
    box = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > 30 else 0).getbbox()
    if box:
        m = 30
        im = im.crop((max(0, box[0] - m), max(0, box[1] - m), min(im.width, box[2] + m), min(im.height, box[3] + m)))
    return im


def export_drawings():
    for key, code in DRAW.items():
        for lang, suffix in (("en", ""), ("tr", "-tr")):
            im = crop_drawing(os.path.join(BP, lang, f"{code}.png"))
            im.save(os.path.join(IMG, f"{key}{suffix}.jpg"), quality=92)
        print("cizim", key)


def ticks(a, b, s):
    out, v = [], a
    while v <= b + 1e-9:
        out.append(int(v) if float(v).is_integer() else round(v, 3))
        v += s
    return out


def axis(label, rng, scale="linear", tk=None):
    a, b, s = rng
    return {"label": label, "scale": scale, "min": a, "max": b, "ticks": tk or ticks(a, b, s)}


def single(code, cid):
    c = BC.CH[code]
    nf, ld = c["nf"], c["ld"]
    A, k = nf["A"][0][1], ld["k"][0][1]
    x0, x1, _ = nf["x"]
    y1 = nf["y"][1]
    fs = max(x0, math.sqrt(A / y1))
    npt = 40
    nf_pts = [[round(f, 3), round(A / f / f, 2)] for f in (fs + (x1 - fs) * i / (npt - 1) for i in range(npt))]
    xe = min(ld["x"][1], ld["y"][1] / k)
    name = f"Novibrasyon {code}"
    return {"id": cid, "panels": [
        {"title": "Natural frequency curve", "x": axis("Natural Frequency (Hz)", nf["x"]),
         "y": axis("Load (Kg)", nf["y"]), "series": [{"label": name, "points": nf_pts}]},
        {"title": "Load-deflection curve", "x": axis("Deflection (mm)", ld["x"]),
         "y": axis("Load (Kg)", ld["y"]), "series": [{"label": name, "points": [[0, 0], [round(xe, 3), round(k * xe, 2)]]}]},
    ]}


NF_X = {"label": "Natural frequency (Hz)", "scale": "log", "min": 5, "max": 20,
        "ticks": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 20]}
LD_X = {"label": "Compression (mm)", "scale": "log", "min": 1, "max": 10, "ticks": [1, 1.5, 2, 3, 4, 5, 6, 8, 10]}
LOG_Y = [10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 100, 150, 200, 250, 300, 400, 500, 600, 700, 800, 1000, 1500,
         2000, 2500, 3000]


def logy(mx):
    return {"label": "Load (kg)", "scale": "log", "min": 10, "max": mx, "ticks": [t for t in LOG_Y if t <= mx]}


def logseg(a, b, n=32):
    fn = BC._seg_fn(a, b)
    la, lb = math.log10(a[0]), math.log10(b[0])
    return [[round(10 ** (la + (lb - la) * i / (n - 1)), 3), round(fn(10 ** (la + (lb - la) * i / (n - 1))), 2)]
            for i in range(n)]


def vv():
    nf_s, ld_s = [], []
    for code in ("VV1", "VV2", "VV3"):
        c = BC.CH[code]
        for lab, a, b in c["nf"]["seg"]:
            nf_s.append({"label": f"{code} · {lab} Shore", "points": logseg(a, b)})
        for lab, a, b in c["ld"]["seg"]:
            ld_s.append({"label": f"{code} · {lab} Shore", "points": logseg(a, b)})
    return {"id": "cvv", "panels": [
        {"title": "Natural frequency curve", "x": NF_X, "y": logy(1500), "series": nf_s},
        {"title": "Load-deflection curve", "x": LD_X, "y": logy(3000), "series": ld_s}]}


def mt():
    """Hesaplanmis MT egrileri (charts._calc): W = k d, d = 1 ... 5 mm; f = 15,76 / sqrt(d)."""
    nf_s, ld_s = [], []
    for code in ("MT1", "MT2", "MT3"):
        for lab, k, wmax in BC.CH[code]["ld"]["k"]:
            dmax = wmax / k
            ds = [1 + (dmax - 1) * i / 19 for i in range(20)]
            ld_s.append({"label": f"{code} · {lab} Shore", "points": [[round(d, 3), round(k * d, 2)] for d in ds]})
            nf_s.append({"label": f"{code} · {lab} Shore",
                         "points": [[round(15.76 / math.sqrt(d), 3), round(k * d, 2)] for d in reversed(ds)]})
    return {"id": "cmt", "panels": [
        {"title": "Natural frequency curve", "x": NF_X, "y": logy(1000), "series": nf_s},
        {"title": "Load-deflection curve", "x": LD_X, "y": logy(1000), "series": ld_s}]}


def sd_series():
    """SD150 / SD230 / SD430 tek grafikte (katalogda saildrive seri acilimi)."""
    parts = [single(c, "") for c in ("SD150", "SD230", "SD430")]
    out = {"id": "csd", "panels": []}
    for k in range(2):
        pans = [p["panels"][k] for p in parts]
        pan = json.loads(json.dumps(pans[-1]))                 # en genis eksen (SD430)
        pan["x"] = axis(pan["x"]["label"], (min(p["x"]["min"] for p in pans), max(p["x"]["max"] for p in pans), 1))
        pan["series"] = [{"label": s["label"].replace("Novibrasyon ", ""), "points": s["points"]}
                         for p in pans for s in p["series"]]
        out["panels"].append(pan)
    return out


def export_curves():
    files = {"c50": single("50", "c50"), "c70": single("70", "c70"), "c75": single("75", "c75"),
             "c100": single("100", "c100"), "c150": single("150", "c150"), "c200": single("200", "c200"),
             "csd150": single("SD150", "csd150"), "csd230": single("SD230", "csd230"),
             "csd430": single("SD430", "csd430"), "csd": sd_series(), "cvv": vv(), "cmt": mt()}
    for cid, d in files.items():
        with open(os.path.join(CUR, cid + ".json"), "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=1)
        print("egri", cid)


if __name__ == "__main__":
    export_drawings()
    export_curves()

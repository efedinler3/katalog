"""Baglanti elemanlari (on gorunus): saplama, DIN 934 / 936 somun, pul, Nord-Lock pul, grower pul.

Olculer standart tablolardan (DIN 934 / 936, ISO 7089); takoz olculeri degil, gorunus icin.
"""
import math

from bp import fillet_poly

T = {
    "M12": dict(d=12.0, af=18.0, h=10.0, ht=7.0, wd=24.0, wt=2.5, nl=19.5, nlt=3.4),
    "M14": dict(d=14.0, af=22.0, h=11.0, ht=8.0, wd=28.0, wt=2.5, nl=23.0, nlt=3.4),
    "M16": dict(d=16.0, af=24.0, h=13.0, ht=8.0, wd=30.0, wt=3.0, nl=25.4, nlt=3.4),
    "M18": dict(d=18.0, af=27.0, h=15.0, ht=9.0, wd=34.0, wt=3.0, nl=27.5, nlt=3.4),
    "M20": dict(d=20.0, af=30.0, h=16.0, ht=10.0, wd=37.0, wt=3.0, nl=30.7, nlt=3.4),
    "M24": dict(d=24.0, af=36.0, h=19.0, ht=12.0, wd=44.0, wt=4.0, nl=38.0, nlt=3.4),
    "1in": dict(d=25.4, af=38.1, h=22.0, ht=14.0, wd=50.0, wt=4.0, nl=40.0, nlt=3.4),
}
WHITE = "#ffffff"


def stud(v, y0, y1, d, tip=None):
    """Saplama: y0 -> y1; tip=(anahtar agzi, boy) varsa ustte daraltilmis uc."""
    r = d / 2
    ch = min(1.2, d * 0.08)
    if tip:
        fw, fh = tip
        top = y1 - fh
        v.poly([(-r, y0), (-r, top - 1.0), (-fw / 2, top), (-fw / 2, y1 - 0.8), (-fw / 2 + 0.8, y1),
                (fw / 2 - 0.8, y1), (fw / 2, y1 - 0.8), (fw / 2, top), (r, top - 1.0), (r, y0)], "thick", False)
        v.line(-r * 0.84, y0, -r * 0.84, top - 1.5, "thin")
        v.line(r * 0.84, y0, r * 0.84, top - 1.5, "thin")
    else:
        v.poly([(-r, y0), (-r, y1 - ch), (-r + ch, y1), (r - ch, y1), (r, y1 - ch), (r, y0)], "thick", False)
        v.line(-r + ch, y1 - ch, r - ch, y1 - ch, "thin")
        v.line(-r * 0.84, y0, -r * 0.84, y1 - ch, "thin")
        v.line(r * 0.84, y0, r * 0.84, y1 - ch, "thin")


def nut(v, y0, t, thin=False, x=0.0):
    """Altigen somun on gorunusu (kose olcusu genislik): uc yuz, pah yaylari."""
    h = t["ht"] if thin else t["h"]
    ac = t["af"] * 2 / math.sqrt(3)
    a = ac / 2
    c = min(0.9, h * 0.12)
    pts = [(x - a, y0 + c), (x - a + c, y0), (x + a - c, y0), (x + a, y0 + c),
           (x + a, y0 + h - c), (x + a - c, y0 + h), (x - a + c, y0 + h), (x - a, y0 + h - c)]
    v.poly(pts, "thick", True, WHITE)
    for k in (-1, 1):
        v.line(x + k * a / 2, y0 + c * 0.6, x + k * a / 2, y0 + h - c * 0.6, "mid")
    # pah yaylari (yuzlerin ust / alt kenarinda)
    for (xa, xb) in ((-a, -a / 2), (-a / 2, a / 2), (a / 2, a)):
        for (yy, sgn) in ((y0 + h, -1), (y0, 1)):
            depth = c * (1.0 if abs(xb - xa) > a * 0.9 else 0.8)
            q0 = v.P(x + xa + 0.15, yy)
            q1 = v.P(x + (xa + xb) / 2, yy + sgn * depth)
            q2 = v.P(x + xb - 0.15, yy)
            v.sh.add(f'<path class="thin" d="M{q0[0]:.3f},{q0[1]:.3f} Q{q1[0]:.3f},{q1[1]:.3f} '
                     f'{q2[0]:.3f},{q2[1]:.3f}"/>')
    return y0 + h


def washer(v, y0, od, th, x=0.0):
    v.rect(x - od / 2, y0, x + od / 2, y0 + th, "thick", WHITE)
    return y0 + th


def nordlock(v, y0, t, x=0.0):
    """Nord-Lock pul cifti (ortada ince ayrim cizgisi)."""
    od, th = t["nl"], t["nlt"]
    v.rect(x - od / 2, y0, x + od / 2, y0 + th, "thick", WHITE)
    v.line(x - od / 2, y0 + th / 2, x + od / 2, y0 + th / 2, "thin")
    return y0 + th


def grower(v, y0, t, x=0.0):
    """Yaylı (grower) pul: yarik izi egik ince cizgi."""
    od = t["d"] * 1.75
    th = t["d"] * 0.22
    v.rect(x - od / 2, y0, x + od / 2, y0 + th, "thick", WHITE)
    v.line(x + od * 0.1, y0, x + od * 0.22, y0 + th, "thin")
    return y0 + th


def stack(v, t, y_body, min_h, total, lower="jam", tip=None, prot=None, lower_washer=None):
    """Saplama + somun dizisi. Destek pulunun ustu = min_h, saplama ucu = total.

    lower: 'jam' (ince kontra somun), 'grower+jam', 'none'
    lower_washer: govde ustunde ayri pul cap/kalinlik (od, t) ya da None
    Donus: onemli seviyeler sozlugu.
    """
    stud(v, y_body - 0.01, total, t["d"], tip)
    y = y_body
    if lower_washer:
        y = washer(v, y, lower_washer[0], lower_washer[1])
    if "grower" in lower:
        y = grower(v, y, t)
    if "jam" in lower:
        y = nut(v, y, t, thin=True)
    sw_bot = min_h - t["wt"]
    n_bot = sw_bot - t["h"]
    if n_bot < y - 0.01:                 # yer yok: alt somun ince somunun ustune oturur
        n_bot = y
    nut(v, n_bot, t)
    washer(v, sw_bot, t["wd"], t["wt"])
    p = prot if prot is not None else (tip[1] + t["d"] * 0.45 if tip else t["d"] * 1.05)
    top_nut_top = total - p
    tn_bot = top_nut_top - t["h"]
    nl_bot = tn_bot - t["nlt"]
    nordlock(v, nl_bot, t)
    nut(v, tn_bot, t)
    return dict(support=min_h, top_nut=top_nut_top, body=y_body)

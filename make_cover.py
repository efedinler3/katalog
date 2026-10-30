"""Kapak gorseli: prosedurel olarak uretilmis alacakaranlik denizi + paslanmaz takoz ve yansimasi.

Calistirma:  python make_cover.py
Cikti:       assets/img/cover-sea.jpg  (216 x 303 mm, ~305 dpi; 3 mm tasma payi dahil)
"""
import os

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 2600, 3648                 # 216 x 303 mm @ ~305 dpi
HORIZON = 0.600                   # ufuk cizgisi (yukseklik orani)
SUN_X = 0.50                      # gunes yatay konumu
PRODUCT = os.path.join(HERE, "assets", "src", "p200.jpg")


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# Renkler (0..1, sRGB)
ZENITH = np.array([0.018, 0.050, 0.075])
HIGH = np.array([0.045, 0.170, 0.215])
LOW = np.array([0.200, 0.470, 0.500])
HORIZ = np.array([0.640, 0.820, 0.800])
WARM = np.array([1.000, 0.780, 0.560])
DEEP = np.array([0.008, 0.045, 0.055])


def sky(elev, azi):
    """Yukseklik acisi (rad) ve gunese olan yatay aci farkina gore gokyuzu rengi."""
    e = np.clip(elev, 0, None)[..., None]
    c = lerp(HORIZ, LOW, smooth(0.0, 0.05, e))
    c = lerp(c, HIGH, smooth(0.03, 0.22, e))
    c = lerp(c, ZENITH, smooth(0.20, 0.70, e))
    # gunes cevresindeki sicak parlama (ufka yakin)
    d = np.sqrt((azi[..., None] * 0.9) ** 2 + (e * 2.2) ** 2)
    glow = np.exp(-d / 0.22) * 0.55 + np.exp(-d / 0.07) * 0.6 + np.exp(-d / 0.025) * 0.9
    c = lerp(c, WARM, np.clip(glow, 0, 1) * 0.8)
    c = c + np.exp(-d / 0.010)[...] * 0.6
    return c


def render(ss=1.25):
    """Deniz ve gokyuzunu ss kat buyuk hesaplar, sonra kucultur (kenar yumusatma)."""
    RW, RH = int(W * ss), int(H * ss)
    ys, xs = np.mgrid[0:RH, 0:RW].astype(np.float32)
    f = 1.05 * RW
    yh = HORIZON * RH
    cx, sx = RW / 2, SUN_X * RW
    img = np.zeros((RH, RW, 3), np.float32)

    above = ys < yh
    elev = np.arctan((yh - ys) / f)
    azi = np.arctan((xs - sx) / f)
    img[above] = sky(elev[above], azi[above])

    below = ~above
    yb, xb = ys[below], xs[below]
    cam_h = 4.0
    dy = np.maximum(yb - yh, 0.35)
    z = cam_h * f / dy
    xw = (xb - cx) * z / f
    footprint = z / f
    hx = np.zeros_like(z)
    hz = np.zeros_like(z)
    rng = np.random.default_rng(11)
    for lam in np.geomspace(0.05, 16.0, 60):
        th = np.radians(rng.normal(0, 38))
        ph = rng.uniform(0, 2 * np.pi)
        slope = 0.020 * (0.75 + 0.5 * rng.random())
        k = 2 * np.pi / lam
        dx, dz = np.sin(th), np.cos(th)
        lod = 1 - smooth(0.35, 1.6, footprint * 4 / lam)
        c = np.cos(k * (xw * dx + z * dz) + ph) * slope * lod
        hx += c * dx
        hz += c * dz
    n = np.stack([-hx, np.ones_like(z), -hz], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    v = np.stack([xw, -np.full_like(z, cam_h), z], -1)
    v /= np.linalg.norm(v, axis=-1, keepdims=True)
    vn = np.sum(v * n, -1, keepdims=True)
    r = v - 2 * vn * n
    sun_az = np.arctan((sx - cx) / f)
    r_el = np.arcsin(np.clip(r[..., 1], -1, 1))
    r_az = np.arctan2(r[..., 0], r[..., 2]) - sun_az
    refl = sky(np.maximum(r_el, 0.001), r_az)
    cos_t = np.clip(-vn[..., 0], 0, 1)
    fres = (0.02 + 0.98 * (1 - cos_t) ** 5)[..., None]
    sun = np.array([np.sin(sun_az), 0.022, np.cos(sun_az)])
    sun /= np.linalg.norm(sun)
    spec = np.clip(np.sum(r * sun, -1), 0, 1)
    glint = (spec ** 2400 * 5.0 + spec ** 300 * 0.55 + spec ** 60 * 0.10)[..., None] * WARM
    water = DEEP + LOW * 0.10 * np.exp(-z / 80)[..., None]
    sea = fres * refl + (1 - fres) * water + glint
    haze = np.exp(-z / 260)[..., None]
    horizon_col = sky(np.full_like(z, 0.0005), np.arctan((xb - sx) / f))
    sea = lerp(horizon_col, sea, haze)
    img[below] = sea
    img = np.clip(img, 0, 1)
    out = Image.fromarray((img * 255).astype(np.uint8), "RGB").resize((W, H), Image.LANCZOS)
    return np.asarray(out).astype(np.float32) / 255


def cutout(path):
    """Beyaz fonlu urun fotografindan seffaf RGBA: kenardan taşkın dolgu ile fon, kalan urun."""
    im = np.asarray(Image.open(path).convert("RGB")).astype(np.float32) / 255
    light = im.min(-1) >= 0.93
    lab, _ = ndimage.label(light)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, border[border > 0])
    prod = ndimage.binary_fill_holes(~bg)
    prod = ndimage.binary_opening(prod, iterations=2)
    lab2, n2 = ndimage.label(prod)
    if n2 > 1:
        sizes = ndimage.sum(prod, lab2, range(1, n2 + 1))
        prod = lab2 == (1 + int(np.argmax(sizes)))
    # golge kalintisi: urunun altinda, notr ve acik gri olan pikselleri at
    sat = im.max(-1) - im.min(-1)
    shadowish = (im.min(-1) > 0.62) & (sat < 0.04)
    rows = np.nonzero(prod.any(1))[0]
    y_cut = rows.min() + int((rows.max() - rows.min()) * 0.80)
    sh = shadowish.copy()
    sh[:y_cut] = False
    prod &= ~sh
    prod = ndimage.binary_opening(prod, iterations=1)
    alpha = ndimage.gaussian_filter(prod.astype(np.float32), 0.9)
    ys, xs = np.nonzero(alpha > 0.02)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgba = np.dstack([im, alpha])[y0:y1, x0:x1]
    return Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), "RGBA")


def compose(bg):
    base = Image.fromarray((bg * 255).astype(np.uint8), "RGB").convert("RGBA")
    prod = cutout(PRODUCT)
    if os.environ.get("NO_PRODUCT"):
        return base.convert("RGB")
    pw = int(W * 0.50)
    ph = int(prod.height * pw / prod.width)
    prod = prod.resize((pw, ph), Image.LANCZOS)
    px = (W - pw) // 2
    base_y = int(HORIZON * H + H * 0.075)       # urunun tabani (ufkun biraz altinda)
    py = base_y - ph

    # arkadan gelen gunes: urun cevresinde sicak hale
    a = np.asarray(prod.getchannel("A")).astype(np.float32) / 255
    pad = 220
    big = np.zeros((ph + 2 * pad, pw + 2 * pad), np.float32)
    big[pad:pad + ph, pad:pad + pw] = a
    halo = ndimage.gaussian_filter(big, 60) * 1.4 + ndimage.gaussian_filter(big, 14) * 0.5
    halo = np.clip(halo, 0, 1)
    hcol = np.dstack([np.full_like(halo, WARM[0]), np.full_like(halo, WARM[1]), np.full_like(halo, WARM[2])])
    himg = Image.fromarray((np.dstack([hcol, halo * 0.55]) * 255).astype(np.uint8), "RGBA")
    base.alpha_composite(himg, (px - pad, py - pad))

    # yansima: cevrilmis, dalgalanmis, soluk
    refl = prod.transpose(Image.FLIP_TOP_BOTTOM)
    ra = np.asarray(refl).astype(np.float32)
    rows = np.arange(ra.shape[0])
    fade = np.clip(1 - rows / (ra.shape[0] * 0.85), 0, 1) ** 1.8 * 0.38
    ra[..., 3] *= fade[:, None]
    ra[..., :3] *= 0.75
    shift = (np.sin(rows / 7.0) * 6 + np.sin(rows / 2.9) * 2.5).astype(int)
    for i in range(ra.shape[0]):
        ra[i] = np.roll(ra[i], shift[i], axis=0)
    refl = Image.fromarray(ra.astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(3.0))
    base.alpha_composite(refl, (px, base_y - 4))

    # urunun altindaki temas golgesi
    sh_h = 120
    yy, xx = np.mgrid[0:sh_h, 0:pw].astype(np.float32)
    sa = np.exp(-((xx - pw / 2) / (pw * 0.40)) ** 2 - ((yy - sh_h / 2) / 18) ** 2) * 0.6
    shadow = Image.fromarray(np.dstack([np.zeros((sh_h, pw, 3)), sa * 255]).astype(np.uint8), "RGBA")
    base.alpha_composite(shadow, (px, base_y - sh_h // 2))

    # urunu hafif sahneye uydur: biraz koyulastir, kenarlarina sicak isik
    pa = np.asarray(prod).astype(np.float32)
    rim = ndimage.gaussian_filter(a, 6)
    edge = np.clip((a - rim) * 3.0, 0, 1)[..., None]
    pa[..., :3] = pa[..., :3] * 0.92 + edge * np.array(WARM) * 255 * 0.55
    prod = Image.fromarray(np.clip(pa, 0, 255).astype(np.uint8), "RGBA")
    base.alpha_composite(prod, (px, py))

    # metin okunurlugu icin ust ve alt koyulasma
    yy = np.arange(H, dtype=np.float32)[:, None] / H
    g = smooth(0.84, 1.0, yy) * 0.55 + (1 - smooth(0.0, 0.34, yy)) * 0.30
    g = np.broadcast_to(g, (H, W))
    dark = Image.fromarray(np.dstack([np.zeros((H, W, 3)), g * 255]).astype(np.uint8), "RGBA")
    base.alpha_composite(dark)
    return base.convert("RGB")


def main():
    bg = render()
    if os.environ.get("SEA_ONLY"):
        Image.fromarray((bg * 255).astype(np.uint8)).save(os.path.join(HERE, "assets", "img", "sea-only.jpg"), quality=92)
        return
    out = compose(bg)
    path = os.path.join(HERE, "assets", "img", "cover-sea.jpg")
    out.save(path, "JPEG", quality=92, optimize=True, progressive=True)
    print("kapak:", path, out.size)


if __name__ == "__main__":
    main()

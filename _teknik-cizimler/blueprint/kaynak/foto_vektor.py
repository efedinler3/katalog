"""Gercek urun fotografindan vektor cizgi: maske siniri (dis hat) + ton esik egrileri (ic hatlar).

trace(img_rgb, box, thr, levels, ...) -> dict(outline=[poly...], inner=[poly...]) piksel koordinatinda (kirpma ici).
Polilineler Douglas-Peucker ile sadelestirilir ve hafif yumusatilir.
"""
import numpy as np
from scipy import ndimage
from skimage import measure, morphology


def _mask(gray, thr, open_r, min_area, extra=None):
    m = gray < thr
    if extra is not None:
        m |= extra
    m = morphology.opening(m, morphology.disk(open_r))
    lab = measure.label(m)
    keep = np.zeros_like(m, dtype=bool)
    for r in measure.regionprops(lab):
        if r.area >= min_area:
            keep[lab == r.label] = True
    keep = ndimage.binary_fill_holes(keep)
    keep = morphology.closing(keep, morphology.disk(2))
    return keep


def _chaikin(p, n=1, closed=False):
    p = np.asarray(p)
    for _ in range(n):
        if len(p) < 3:
            break
        q = 0.75 * p[:-1] + 0.25 * p[1:]
        r = 0.25 * p[:-1] + 0.75 * p[1:]
        mid = np.empty((2 * len(q), 2))
        mid[0::2], mid[1::2] = q, r
        p = np.vstack([p[:1], mid, p[-1:]]) if not closed else mid
    return p


def _simplify(c, tol, smooth, closed):
    c = measure.approximate_polygon(c, tolerance=tol)
    if smooth:
        c = _chaikin(c, smooth, closed)
    return c


def trace(rgb, thr=0.86, open_r=4, min_area=4000, levels=(0.30,), sigma=1.2, min_len=30, tol=0.7, smooth=1,
          exclude=None, boundary_gap=3.5, keep_mask=None):
    """rgb: HxWx3 float 0..1. exclude: maske disinda tutulacak bolge (saplama vb.) bool dizisi.
    Donus: outline (liste, kapali), inner (liste, acik), mask."""
    gray = rgb.mean(axis=2)
    mask = keep_mask if keep_mask is not None else _mask(gray, thr, open_r, min_area)
    if exclude is not None:
        mask = mask & ~exclude
    sm = ndimage.gaussian_filter(mask.astype(np.float32), 1.0)
    outline = []
    for c in measure.find_contours(sm, 0.5):
        if len(c) > 40:
            outline.append(_simplify(c, tol, smooth, True))
    g = ndimage.gaussian_filter(gray, sigma)
    g = np.where(mask, g, 1.0)
    dist = ndimage.distance_transform_edt(mask)
    inner = []
    for lv in levels:
        for c in measure.find_contours(g, lv):
            if len(c) < min_len:
                continue
            ci = np.clip(np.round(c).astype(int), 0, np.array(mask.shape) - 1)
            dd = dist[ci[:, 0], ci[:, 1]]
            ok = dd > boundary_gap                   # dis hatta yapisik parcalari at
            # ardisik 'ok' parcalarini ayri cizgiler olarak al
            start = None
            for i, v in enumerate(list(ok) + [False]):
                if v and start is None:
                    start = i
                elif not v and start is not None:
                    seg = c[start:i]
                    if len(seg) >= min_len:
                        inner.append(_simplify(seg, tol, smooth, False))
                    start = None
    return dict(outline=outline, inner=inner, mask=mask)

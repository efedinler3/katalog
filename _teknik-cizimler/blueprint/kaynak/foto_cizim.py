"""Gercek fotograf / render / cizgi cizim -> vektor cizgi (urun hatlari).

Iki yol:
- photo:  urun maskesi (koyu bolge) + TV gurultu silme + Canny kenar -> iskelet -> zincirler (polilineler)
- lines:  hazir cizgi cizim (koyu ince cizgiler) -> esik -> iskelet -> zincirler
Koordinatlar: kirpilmis ve 'up' kat buyutulmus piksel; mm donusumu calibrate() ile.
"""
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import feature, measure, morphology, restoration

N8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def _mask(gray, thr, open_r, min_area):
    m = gray < thr
    m = morphology.opening(m, morphology.disk(open_r))
    lab = measure.label(m)
    keep = np.zeros_like(m, dtype=bool)
    for r in measure.regionprops(lab):
        if r.area >= min_area:
            keep[lab == r.label] = True
    keep = ndimage.binary_fill_holes(keep)
    return morphology.closing(keep, morphology.disk(2))


def chains(skel, min_len=12):
    """Iskelet pikselleri -> acik / kapali zincirler (y, x listeleri)."""
    sk = skel.copy()
    H, W = sk.shape
    pts = set(zip(*np.nonzero(sk)))

    def nbrs(p):
        y, x = p
        return [(y + dy, x + dx) for dy, dx in N8 if (y + dy, x + dx) in pts]
    deg = {p: len(nbrs(p)) for p in pts}
    visited = set()
    out = []

    def walk(start, nxt):
        path = [start, nxt]
        visited.add(frozenset((start, nxt)))
        prev, cur = start, nxt
        while True:
            if deg[cur] != 2:
                break
            cand = [q for q in nbrs(cur) if q != prev and frozenset((cur, q)) not in visited]
            if not cand:
                break
            q = cand[0]
            visited.add(frozenset((cur, q)))
            path.append(q)
            prev, cur = cur, q
            if cur == start:
                break
        return path
    nodes = [p for p in pts if deg[p] != 2]
    for p in nodes:
        for q in nbrs(p):
            if frozenset((p, q)) not in visited:
                out.append(walk(p, q))
    for p in pts:                                    # yalniz kalan donguler
        if deg[p] == 2:
            for q in nbrs(p):
                if frozenset((p, q)) not in visited:
                    out.append(walk(p, q))
    res = []
    for c in out:
        if len(c) >= min_len:
            res.append(np.array(c, dtype=np.float32))
    return res


def _smooth(c, tol=0.9, n=2):
    c = measure.approximate_polygon(c, tolerance=tol)
    for _ in range(n):
        if len(c) < 3:
            break
        q = 0.75 * c[:-1] + 0.25 * c[1:]
        r = 0.25 * c[:-1] + 0.75 * c[1:]
        mid = np.empty((2 * len(q), 2), np.float32)
        mid[0::2], mid[1::2] = q, r
        c = np.vstack([c[:1], mid, c[-1:]])
    return c


def load(path, box, up=2):
    im = Image.open(path).convert("RGB").crop(box)
    if up != 1:
        im = im.resize((im.width * up, im.height * up), Image.LANCZOS)
    return np.asarray(im).astype(np.float32) / 255


def trace_photo(rgb, thr=0.86, open_r=6, min_area=16000, tv=0.12, sigma=2.2, lo=0.03, hi=0.07, min_len=60,
                erase=(), cut_top=0, inner_gap=5, mask_extra=None, mask_cut=None):
    """erase: [(y0, x0, y1, x1), ...] maske ve kenarlardan silinecek dikdortgenler (olcu kalintilari).
    cut_top: bu satirin ustu atilir (saplama ayri cizilecek)."""
    gray = rgb.mean(axis=2)
    mask = _mask(gray, thr, open_r, min_area)
    if mask_extra is not None:
        mask |= mask_extra
    if mask_cut is not None:
        mask &= ~mask_cut
    for (y0, x0, y1, x1) in erase:
        mask[y0:y1, x0:x1] = False
    if cut_top:
        mask[:cut_top, :] = False
    mask = morphology.opening(mask, morphology.disk(2))
    t = restoration.denoise_tv_chambolle(gray, weight=tv)
    t = np.where(mask, t, 1.0)
    e = feature.canny(t, sigma=sigma, low_threshold=lo, high_threshold=hi)
    e &= morphology.erosion(mask, morphology.disk(inner_gap))
    sk = morphology.skeletonize(morphology.dilation(e, morphology.disk(1)))
    inner = [_smooth(c) for c in chains(sk, min_len)]
    sm = ndimage.gaussian_filter(mask.astype(np.float32), 1.6)
    outline = [_smooth(c, 1.0, 2) for c in measure.find_contours(sm, 0.5) if len(c) > 80]
    return dict(outline=outline, inner=inner, mask=mask)


def trace_lines(rgb, thr=0.45, min_len=25, erase=(), keep_box=None):
    """Hazir cizgi cizim: koyu cizgiler -> iskelet -> zincir. erase: silinecek dikdortgenler."""
    gray = rgb.mean(axis=2)
    m = gray < thr
    for (y0, x0, y1, x1) in erase:
        m[y0:y1, x0:x1] = False
    if keep_box is not None:
        y0, x0, y1, x1 = keep_box
        k = np.zeros_like(m)
        k[y0:y1, x0:x1] = True
        m &= k
    sk = morphology.skeletonize(m)
    lines = [_smooth(c, 0.7, 1) for c in chains(sk, min_len)]
    return dict(outline=[], inner=lines, mask=m)


def bbox(mask):
    ys, xs = np.nonzero(mask)
    return xs.min(), ys.min(), xs.max(), ys.max()

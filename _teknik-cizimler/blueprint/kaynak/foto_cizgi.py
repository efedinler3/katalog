"""Gercek urun fotografli cizimden temiz cizgi cizim: urunu beyaz zeminden ayirir, hatlarini cikarir.

1) Urun maskesi: koyu / gri pikseller, ince olcu cizgileri ve yazilar morfolojik acma ile atilir,
   buyuk bilesenler kalir.
2) Dis hat: maskenin siniri (kalin cizgi).
3) Ic hatlar: maske icinde Canny kenarlari (ince cizgi), kisa parcalar atilir.
Cikti: beyaz zemin + siyah cizgi PNG (ve maske).
Calistirma:  python foto_cizgi.py <giris.jpg> <cikis.png> [x0,y0,x1,y1 kirpma]
"""
import sys

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import feature, morphology, measure


def product_mask(gray, thr=0.86, open_r=4, min_area=4000):
    m = gray < thr
    m = morphology.binary_opening(m, morphology.disk(open_r))
    lab = measure.label(m)
    keep = np.zeros_like(m)
    for r in measure.regionprops(lab):
        if r.area >= min_area:
            keep[lab == r.label] = True
    keep = ndimage.binary_fill_holes(keep)
    keep = morphology.binary_closing(keep, morphology.disk(2))
    return keep


def line_art(rgb, sigma=1.6, lo=0.04, hi=0.11, min_len=18, thr=0.86):
    gray = np.asarray(rgb.convert("L")).astype(np.float32) / 255
    mask = product_mask(gray, thr)
    # dis hat
    edge_out = mask ^ morphology.binary_erosion(mask, morphology.disk(1))
    edge_out = morphology.binary_dilation(edge_out, morphology.disk(1))
    # ic hatlar: maskenin biraz icinde
    inner = morphology.binary_erosion(mask, morphology.disk(3))
    e = feature.canny(gray, sigma=sigma, low_threshold=lo, high_threshold=hi) & inner
    lab = measure.label(e, connectivity=2)
    sizes = np.bincount(lab.ravel())
    small = sizes < min_len
    small[0] = False
    e[small[lab]] = False
    out = np.ones(gray.shape, np.float32)
    out[edge_out] = 0.0
    e_d = morphology.binary_dilation(e, morphology.disk(0.6)) if False else e
    out[e_d] = np.minimum(out[e_d], 0.15)
    return out, mask


def main():
    src, dst = sys.argv[1], sys.argv[2]
    im = Image.open(src).convert("RGB")
    if len(sys.argv) > 3:
        im = im.crop(tuple(int(v) for v in sys.argv[3].split(",")))
    out, mask = line_art(im)
    Image.fromarray((out * 255).astype(np.uint8)).save(dst)
    Image.fromarray((mask * 255).astype(np.uint8)).save(dst.replace(".png", "-maske.png"))
    print("ok", out.shape)


if __name__ == "__main__":
    main()

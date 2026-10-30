"""Kopru ailesi 3B modeli (75 / 100 / 150 / 200): Ellebogen 75 CAD foyunden olculen profil + Novibrasyon isaretleri.

Olculer (mm): taban 205 x 60 x 6, ortasi 63 derece Lambda bukum (dis tepe ~51); sapka 6 mm, bacak 66 derece,
dis ust yuzey 76; delik araligi 174, sol O12,2, sag 12,5 kanal (merkezler arasi 17,5); M16 x 1,5 saplama,
min yukseklik 103, toplam 145. Kaucuk: iki lob + tepe kapagi + ayak kamalari; sapka altinda pencere.
"""
import math

from build123d import (Align, Cylinder, Pos, Rot, Text, extrude, Box, SlotCenterToCenter, Circle, Compound,
                       Solid, Face, Sketch)

import cad_kit as CK

import os
FONT = r"C:\Windows\Fonts\segoeui.ttf" if os.path.exists(r"C:\Windows\Fonts\segoeui.ttf") else os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "assets", "fonts", "ttf", "segoeui.ttf")
FONT_B = r"C:\Windows\Fonts\segoeuib.ttf" if os.path.exists(r"C:\Windows\Fonts\segoeuib.ttf") else os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "assets", "fonts", "ttf", "segoeuib.ttf")


def emboss_front(sk, x, z, y_face, h=0.6):
    """XY'de cizilmis 2B sekli on yuze (y = y_face, -Y yonune bakan) h kadar kabartir."""
    s = extrude(sk, amount=h)
    s = Rot(90, 0, 0) * s
    return Pos(x, y_face, z) * s


def emboss_top(sk, x, y, z_face, h=0.5):
    s = extrude(sk, amount=h)
    return Pos(x, y, z_face) * s


def model(code="75", L=205.0, W=60.0, C=174.0, H=76.0, min_h=103.0, total=145.0, d=16.0, slot=17.5):
    parts = {}
    # --- taban saci (6 mm) ortasi Lambda
    center = [(-L / 2, 3.0), (-27.29, 3.0), (0.0, 57.04), (27.29, 3.0), (L / 2, 3.0)]
    plate = CK.prism_xz(CK.band_face(center, [0, 11.0, 7.4, 11.0, 0], 6.0), W)
    hole_l = Pos(-C / 2, 0, 0) * Cylinder(12.2 / 2, 40)
    slot = extrude(SlotCenterToCenter(slot, 12.5, rotation=90), amount=40, both=True)
    plate = plate - hole_l - Pos(C / 2, 0, 0) * slot
    parts["plate"] = plate
    # --- ayak altliklari (2 mm, kaucuk bag saci)
    shims = []
    for sx in (-1, 1):
        f = CK.rounded_face([(sx * 74.5, 6.0), (sx * 35.0, 6.0), (sx * 35.0, 8.0), (sx * 74.5, 8.0)], [0, 0, 0, 0])
        shims.append(CK.prism_xz(f, 54.0))
    parts["shim"] = shims[0] + shims[1]
    # --- sapka (6 mm): dis ust yuzey H
    hat_c = [(-69.74, 24.78), (-48.2, H - 3.0), (48.2, H - 3.0), (69.74, 24.78)]
    parts["hat"] = CK.prism_xz(CK.band_face(hat_c, [0, 5.0, 5.0, 0], 6.0), W)
    # --- kaucuk
    rub = [(-48.84, 64.24), (-11.1, 46.7), (0.0, 54.0), (11.1, 46.7), (48.84, 64.24), (63.9, 30.5),
           (32.7, 16.3), (46.4, 8.0), (35.0, 8.0), (35.0, 6.0), (29.3, 6.0), (0.0, 63.9), (-29.3, 6.0),
           (-35.0, 6.0), (-35.0, 8.0), (-46.4, 8.0), (-32.7, 16.3), (-63.9, 30.5)]
    rr = [1.5, 2.5, 6.0, 2.5, 1.5, 1.2, 1.5, 0.8, 0, 0, 8.0, 10.4, 8.0, 0, 0, 0.8, 1.5, 1.2]
    parts["rubber"] = CK.prism_xz(CK.rounded_face(rub, rr), 54.0)
    # --- on yuz isaretleri: solda model numarasi halkasi, sagda 'novibrasyon'
    yf = -27.0
    ring = Circle(13.0) - Circle(11.9)
    marks = emboss_front(ring, -37.7, 40.0, yf)
    num = Text(code, font_size=12.5, font_path=FONT_B, align=(Align.CENTER, Align.CENTER))
    marks = marks + emboss_front(num, -37.7, 40.0, yf)
    word = Text("novibrasyon", font_size=6.2, font_path=FONT, align=(Align.CENTER, Align.CENTER))
    marks = marks + emboss_front(word, 38.5, 37.0, yf)
    parts["marks"] = marks
    # --- sapka ustu: 4 serit + yazi
    top = None
    for sz in (-1, 1):
        for x0, x1 in ((-40.0, -6.0), (6.0, 40.0)):
            s = emboss_top(SlotCenterToCenter(x1 - x0 - 3.0, 3.0), (x0 + x1) / 2, sz * 19.0, H, 0.5)
            top = s if top is None else top + s
    tword = Text("novibrasyon", font_size=9.0, font_path=FONT, align=(Align.CENTER, Align.CENTER))
    parts["top_marks"] = top + emboss_top(tword, 0, 0, H, 0.4)
    # --- saplama ve somunlar (DIN 936 kontra, DIN 934, pul, Nord-Lock, grower)
    fast = CK.stud3d(d, H - 6.0, total, ch=1.2)
    z = H
    fast = fast + CK.washer3d(27.0, 16.4, 3.0, z)              # grower
    z += 3.0
    fast = fast + CK.hex_nut(24.0, 8.0, d, z)                  # DIN 936
    z += 8.0
    fast = fast + CK.hex_nut(24.0, 13.0, d, min_h - 3.0 - 13.0)
    fast = fast + CK.washer3d(30.0, 17.0, 3.0, min_h - 3.0)    # destek pulu
    top_nut = total - 13.6
    fast = fast + CK.hex_nut(24.0, 13.0, d, top_nut - 13.0)
    fast = fast + CK.washer3d(25.4, 16.4, 3.4, top_nut - 13.0 - 3.4)   # Nord-Lock
    parts["fasteners"] = fast
    return parts


if __name__ == "__main__":
    import time
    t0 = time.time()
    p = model()
    print({k: type(v).__name__ for k, v in p.items()}, f"{time.time() - t0:.1f}s")

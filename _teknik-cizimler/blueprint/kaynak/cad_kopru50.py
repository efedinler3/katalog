"""50 / 70 gövdesi 3B modeli: Ellebogen 50 CAD foyunden olculen profil (8,874 px/mm), Novibrasyon isaretleri.

Olculer (mm): taban 159 x 49 x 5, ortasi 63 derece Lambda bukum; sapka 4 mm, bacak 66 derece, dis ust 66;
delik araligi 127,5; sol O12,5, sag 12,5 kanal (merkezler arasi 18); M14 x 1,5; min yukseklik 96,5; toplam 147.
Kaucuk: paralelkenar loblar + Lambda ustu ince kaplama + tepe kapagi; sapka altinda saplama basligi.
"""
from build123d import Align, Circle, Cylinder, Pos, SlotCenterToCenter, Text, extrude

import cad_kit as CK
from cad_kopru import FONT, FONT_B, emboss_front, emboss_top


def model(code="50", L=159.0, W=49.0, C=127.5, H=66.0, min_h=96.5, total=147.0, d=14.0):
    parts = {}
    center = [(-L / 2, 2.5), (-21.9, 2.5), (0.0, 46.08), (21.9, 2.5), (L / 2, 2.5)]
    plate = CK.prism_xz(CK.band_face(center, [0, 11.5, 4.6, 11.5, 0], 5.0), W)
    plate = plate - Pos(-C / 2, 0, 0) * Cylinder(12.5 / 2, 40)
    plate = plate - Pos(C / 2, 0, 0) * extrude(SlotCenterToCenter(18.0, 12.5, rotation=90), amount=40, both=True)
    parts["plate"] = plate
    sh = []
    for sx in (-1, 1):
        sh.append(CK.prism_xz(CK.rounded_face([(sx * 45.2, 5.0), (sx * 26.5, 5.0), (sx * 26.5, 6.5), (sx * 45.2, 6.5)],
                                              [0, 0, 0, 0]), 44.0))
    parts["shim"] = sh[0] + sh[1]
    hat_c = [(-51.87, 21.19), (-33.0, H - 2.0), (33.0, H - 2.0), (51.87, 21.19)]
    parts["hat"] = CK.prism_xz(CK.band_face(hat_c, [0, 3.0, 3.0, 0], 4.0), W)
    rub = [(-35.56, 53.27), (-6.46, 40.64), (0.0, 47.0), (6.46, 40.64), (35.56, 53.27), (46.4, 28.66),
           (18.34, 17.01), (23.6, 6.5), (22.64, 6.5), (0.0, 51.55), (-22.64, 6.5), (-23.6, 6.5), (-18.34, 17.01),
           (-46.4, 28.66)]
    rr = [1.5, 1.8, 5.0, 1.8, 1.5, 1.5, 1.8, 0, 0, 7.1, 0, 0, 1.8, 1.5]
    parts["rubber"] = CK.prism_xz(CK.rounded_face(rub, rr), 44.0)
    head = Cylinder(13.4, 3.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    head = head.chamfer(1.4, None, head.edges().group_by()[0])
    parts["head"] = Pos(0, 0, 56.4) * head
    yf = -22.0
    marks = emboss_front(Circle(10.0) - Circle(9.0), -26.6, 35.4, yf)
    marks = marks + emboss_front(Text(code, font_size=10.0, font_path=FONT_B, align=(Align.CENTER, Align.CENTER)),
                                 -26.6, 35.4, yf)
    marks = marks + emboss_front(Text("NoVibrasyon", font_size=4.8, font_path=FONT,
                                      align=(Align.CENTER, Align.CENTER)), 27.0, 33.0, yf)
    parts["marks"] = marks
    top = None
    for sz in (-1, 1):
        s = emboss_top(SlotCenterToCenter(44.0, 2.6), 0, sz * 17.5, H, 0.45)
        top = s if top is None else top + s
    parts["top_marks"] = top
    fast = CK.stud3d(d, H - 4.0, total, ch=1.1)
    fast = fast + CK.washer3d(24.0, 14.4, 2.6, H)                      # grower
    fast = fast + CK.hex_nut(22.0, 14.0, d, H + 2.6)                   # DIN 985 kilitli somun
    fast = fast + CK.hex_nut(22.0, 11.0, d, min_h - 2.5 - 11.0)        # DIN 934
    fast = fast + CK.washer3d(28.0, 15.0, 2.5, min_h - 2.5)            # destek pulu
    top_nut = total - 19.8
    fast = fast + CK.hex_nut(22.0, 11.0, d, top_nut - 11.0)
    fast = fast + CK.washer3d(23.0, 14.4, 3.4, top_nut - 11.0 - 3.4)   # Nord-Lock
    parts["fasteners"] = fast
    return parts

"""Saildrive takozu 3B modeli (SD 150 / 230 / 430): Ellebogen SD 150 CAD foyunden (8,874 px/mm) olculen profil.

Olculer (mm): kanat ucu genisligi 130, derinlik 61; cati sac 7 mm, ust yuzey 64, kanatlar 45 derece, uclar z=30'da
yatay kesik; X kaucuk (ortasinda V bosluk); ucgen alt parca (taban 52, tepe 34); M12 alt + ust saplama
(ust 34, alt 35,5 cikinti), Nord-Lock + somun.
"""
from build123d import Align, Circle, Cylinder, Pos, Text

import cad_kit as CK
from cad_kopru import FONT, FONT_B, emboss_front


def model(code="150", H=64.0, top_stud=34.0, bot_stud=35.5, d=12.0, depth=61.0):
    parts = {}
    roof = [(-64.8, 30.0), (-31.0, H), (31.0, H), (64.8, 30.0), (53.4, 30.0), (26.4, H - 7.0), (-26.4, H - 7.0),
            (-53.4, 30.0)]
    parts["roof"] = CK.prism_xz(CK.rounded_face(roof, [0, 4.0, 4.0, 0, 0, 2.0, 2.0, 0]), depth)
    tri = [(0.0, 34.2), (26.0, 8.2), (26.0, 0.0), (-26.0, 0.0), (-26.0, 8.2)]
    parts["tri"] = CK.prism_xz(CK.rounded_face(tri, [6.8, 3.0, 4.4, 4.4, 3.0]), 57.0)
    rub = [(-26.4, H - 7.0), (26.4, H - 7.0), (47.9, 35.5), (23.1, 11.1), (0.0, 34.2), (-23.1, 11.1), (-47.9, 35.5)]
    rubber = CK.prism_xz(CK.rounded_face(rub, [1.0, 1.0, 1.2, 1.5, 6.8, 1.5, 1.2]), 57.0)
    chev = [(0.0, 31.5), (21.2, 53.6), (19.0, 55.6), (0.0, 44.4), (-19.0, 55.6), (-21.2, 53.6)]
    rubber = rubber - CK.prism_xz(CK.rounded_face(chev, [4.0, 1.8, 1.8, 3.0, 1.8, 1.8]), 70.0)
    parts["rubber"] = rubber
    yf = -28.5
    w = Text("novibrasyon", font_size=4.6, font_path=FONT, align=(Align.CENTER, Align.CENTER), rotation=45)
    marks = emboss_front(w, 33.5, 25.5, yf, 0.5)
    # sol kanat: kopru takozlarindaki gibi halka icinde model numarasi
    rx, rz, rr = -36.0, 31.0, 8.6
    marks = marks + emboss_front(Circle(rr) - Circle(rr - 1.0), rx, rz, yf, 0.5)
    n = Text(code, font_size=7.4, font_path=FONT_B, align=(Align.CENTER, Align.CENTER))
    marks = marks + emboss_front(n, rx, rz, yf, 0.5)
    parts["marks"] = marks
    fast = CK.stud3d(d, H - 7.0, H + top_stud, ch=1.0)
    fast = fast + CK.washer3d(19.5, 12.4, 3.4, H + 10.0)
    fast = fast + CK.hex_nut(18.0, 10.0, d, H + 13.4)
    bot = CK.stud3d(d, -bot_stud, 6.0, ch=0)
    bot = bot.chamfer(1.0, None, bot.edges().group_by()[0]) if False else bot
    fast = fast + bot
    fast = fast + CK.washer3d(19.5, 12.4, 3.4, -13.4)
    fast = fast + CK.hex_nut(18.0, 10.0, d, -23.4)
    parts["fasteners"] = fast
    return parts

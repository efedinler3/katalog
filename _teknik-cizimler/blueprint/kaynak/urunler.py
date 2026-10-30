"""Cizim verisi: olculer (mm), kaynaklar ve iz (trace) ayarlari.

Urun hatlari: gercek urun fotograflari / hazir cizimler (Novibrasyon sitesi; VV icin sahibin cizimleri;
SD icin Ellebogen SD 150 foyu) vektor cizgiye cevrilir. Olculendirilen degerler:
- ELL = Ellebogen teknik foyu: 50, 70, 75, 100, 150, 200, SD 150/230/430, GT-S (= VV1), GT-M (= VV2)
- NV  = Novibrasyon cizimi / katalog: VV3, 400, 450, 500, 600, MT1-3
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
KAT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SRC = os.path.join(KAT, "assets", "src")
ELL = os.path.join(os.path.dirname(HERE), "referans-ellebogen")
OWN = os.path.join(os.path.dirname(HERE), "referans-sahip")
UNI = {"tr": "Üniversal", "en": "Universal"}


def ph(name, box, thr=0.86, cut="auto", frac=0.30, mode="photo", **kw):
    d = dict(src=os.path.join(SRC, name + ".jpg"), box=box, thr=thr, cut=cut, cut_frac=frac, mode=mode, up=2)
    d.update(kw)
    return d


BRIDGE = dict(family="photo", kind="bridge", thread_txt="M16 × 1,5", thread="M16")

P = {
    "50": dict(family="cad", cad_module="cad_kopru50.py", cad_args=dict(code="50"), kind="bridge", L=159.0, W=49.0, C=127.5, H=66.0, tp=5.0, h_x=34.0, minH=96.5,
               total=147.0, thread="M14", thread_txt="M14 × 1,5", hole_l=("round", 12.5),
               hole_r=("slot", 12.5, 30.5, "v", "c"), redraw_holes=True,
               trace=dict(front=ph("d50", (95, 398, 866, 643)),
                          plan=ph("d50", (872, 745, 1442, 925), thr=0.5, cut=None, mode="lines")),
               desc="Yanmar 1GM", refs="Yanmar 128170-08340", src="ELL"),
    "70": dict(family="cad", cad_module="cad_kopru50.py", cad_args=dict(code="70"), kind="bridge", L=159.0, W=49.0, C=127.5, H=66.0, tp=5.0, h_x=34.0, minH=96.5,
               total=147.0, thread="M14", thread_txt="M14 × 1,5", hole_l=("round", 12.5),
               hole_r=("slot", 12.5, 30.5, "v", "c"), redraw_holes=True,
               trace=dict(front=ph("d70", (95, 398, 866, 643)),
                          plan=ph("d70", (872, 745, 1442, 925), thr=0.5, cut=None, mode="lines")),
               desc="Yanmar 1GM", refs="Yanmar 128170-08350", src="ELL"),
    "75": dict(BRIDGE, family="cad", cad_module="cad_kopru.py", cad_args=dict(code="75", L=200.0, C=173.0, H=75.0, slot=17.2), L=200.0, W=60.0, C=173.0, H=75.0, tp=6.0, h_x=40.0, minH=None, total=145.0,
               hole_l=("round", 12.2), hole_r=("slot", 12.5, 29.7, "v", "c"),
               trace=dict(front=ph("d75", thr=0.80, box=(375, 266, 1161, 580)), plan=ph("d75", (399, 729, 1127, 952), cut=None)),
               desc="Yanmar 2GM · 2YM · 3GM · 3YM", refs="Yanmar 128270-08341, 128377-08340, 128377-08341", src="ELL"),
    "100": dict(BRIDGE, family="cad", cad_module="cad_kopru.py", cad_args=dict(code="100", L=200.0, C=173.0, H=75.0, slot=17.3), L=200.0, W=60.0, C=173.0, H=75.0, tp=6.0, h_x=40.0, minH=None, total=145.0,
                hole_l=("round", 12.2), hole_r=("slot", 12.5, 29.8, "v", "c"),
                trace=dict(front=ph("d100", thr=0.80, box=(374, 273, 1164, 583)), plan=ph("d100", (400, 736, 1127, 954), cut=None)),
                desc="Yanmar 2GM · 3GM · 3HM · 3JH", refs="Yanmar 124772-08341, 128377-08351", src="ELL"),
    "150": dict(BRIDGE, family="cad", cad_module="cad_kopru.py", cad_args=dict(code="150", L=200.0, C=173.0, H=75.0, slot=17.2), L=200.0, W=60.0, C=173.0, H=75.0, tp=6.0, h_x=40.0, minH=None, total=145.0,
                hole_l=("round", 12.2), hole_r=("slot", 12.5, 29.7, "v", "c"),
                trace=dict(front=ph("d150", thr=0.80, box=(374, 267, 1159, 580)), plan=ph("d150", (399, 729, 1128, 952), cut=None)),
                desc="Yanmar 3JH · 4JH", refs="Yanmar 121370-08351", src="ELL"),
    "200": dict(BRIDGE, family="cad", cad_module="cad_kopru.py", cad_args=dict(code="200"), L=205.0, W=60.0, C=174.0, H=76.0, tp=6.0, h_x=40.0, minH=103.0, total=145.0,
                hole_l=("round", 12.2), hole_r=("slot", 12.5, 30.0, "v", "c"), relabel=(-38.5, 34.0, 12.0),
                trace=dict(front=ph("d150", thr=0.80, box=(374, 267, 1159, 580)), plan=ph("d150", (399, 729, 1128, 952), cut=None)),
                desc="Yanmar 4JH", refs="Yanmar 129470-08350, 129670-08351", src="ELL"),
    "SD150": dict(family="cad", cad_module="cad_sd.py", cad_args=dict(code="150"), kind="sd", L=130.0, W=61.0, H=64.0, roof_drop=34.0, roof_flat=31.0, low_w=52.0,
                  top_stud=34.0, bot_stud=35.5, bracket_gap=10.0, thread="M12", thread_txt="M12",
                  trace=dict(front=dict(src=os.path.join(ELL, "technical-data-sheet-ellebogen-sd-150.png"),
                                        box=(500, 330, 1720, 1600), mode="lines", thr=0.45, cut="auto",
                                        cut_bottom="auto", cut_frac=0.30, up=1, thick_open=1),
                             plan=dict(src=os.path.join(ELL, "technical-data-sheet-ellebogen-sd-150.png"),
                                       box=(500, 2060, 1720, 2650), mode="lines", thr=0.45, cut=None, up=1, thick_open=1,
                                       erase=[(640, 2110, 800, 2600)])),
                  desc="Yanmar saildrive SD20 · SD25", refs="Yanmar 129795-08340", src="ELL"),
}
P["SD230"] = dict(P["SD150"], cad_args=dict(code="230"), desc="Yanmar saildrive SD20 · SD25 · SD30", refs="Yanmar 196420-02310")
P["SD430"] = dict(P["SD150"], cad_args=dict(code="430"), desc="Yanmar saildrive SD40 · SD50", refs="Yanmar 196440-02380")

P.update({
    "400": dict(family="cad", cad_module="cad_blok.py", cad_args=dict(code="400"), tangent=None, kind="block", L=166.0, W=66.0, C=127.0, house_w=93.0, H=80.0, h_x=22.0,
                minH=120.0, total=170.0, thread="M20", thread_txt="M20", slot=(14.0, 28.0), redraw_holes=True,
                hole_l=("slot", 14.0, 28.0, "v"), hole_r=("slot", 14.0, 28.0, "v"),
                trace=dict(front=ph("d400", (523, 128, 1028, 580), thr=0.965),
                           plan=ph("d400", (522, 858, 1032, 1098), thr=0.5, cut=None, mode="lines")),
                desc="Yanmar 4LHA", refs="519175-08300 · Yanmar 119175-08440", src="NV"),
    "450": dict(family="cad", cad_module="cad_blok.py", cad_args=dict(code="450"), tangent=None, kind="block", L=165.0, W=85.0, C=127.0, house_w=93.0, H=72.0, h_x=30.0,
                minH=120.0, total=170.0, thread="M20", thread_txt="M20", slot=(13.0, 20.0), dim_slot="len",
                trace=dict(front=ph("d450", (467, 205, 1006, 591)), plan=ph("d450", (467, 686, 1014, 908), cut=None)),
                desc="Cummins 6B · 6BT · 6BTA 5.9", refs="Cummins 3349230 · Barry Controls 27655-2", src="NV"),
    "500": dict(family="cad", cad_module="cad_blok.py", cad_args=dict(code="500"), tangent=None, kind="block", L=166.0, W=93.0, C=127.0, house_w=93.0, H=90.0, h_x=22.0,
                minH=130.0, total=190.0, thread="1in", thread_txt="1″ × 14 TPI", slot=(14.0, 28.0),
                redraw_holes=True, hole_l=("slot", 14.0, 28.0, "v"), hole_r=("slot", 14.0, 28.0, "v"),
                trace=dict(front=ph("d500", (554, 219, 1033, 598), thr=0.965),
                           plan=ph("d500", (552, 842, 1033, 1125), thr=0.5, cut=None, mode="lines")),
                desc="Yanmar 6LY · 6LP · Cummins 6CTA",
                refs="Yanmar 119773-08300, 119773-08310 · Cummins 3968021, 3393853", src="NV"),
    "600": dict(family="cad", cad_module="cad_blok.py", cad_args=dict(code="600"), tangent=None, kind="block", L=166.0, W=93.0, C=127.0, house_w=None, H=95.0, h_x=30.0,
                minH=None, total=190.0, thread="M24", thread_txt="M24", slot=(14.0, 28.0), dim_slot=False,
                trace=dict(front=ph("d600", (494, 111, 1041, 555)), plan=ph("d600", (484, 624, 1049, 889), cut=None)),
                desc="Cummins QSM11 · QSB 5.9 · 6CTA", refs="Cummins 3964883, 4931364, 5301975", src="NV"),
    # --- VV: on gorunus sahibin cizimlerinden, ust gorunus vektor
    "VV1": dict(family="cad", cad_module="cad_vv.py", cad_args=dict(code="VV1"), iso_args=dict(section_cut=False),
                tangent=None, kind="vv", L=120.0, W=60.5, tp=3.0, C=100.0, H=43.0, h_x=27.6, minH=68.5,
                total=125.0, thread="M16", thread_txt="M16 × 1,5", tip=(10.0, 16.0),
                neck=29.4, waist=(26.8, 12.0), rim=(40.3, 18.4, 22.2), top_x=27.6, top_washer=54.0,
                hole_l=("slot", 11.0, 14.0, "v", "c"), hole_r=("slot", 11.0, 14.0, "v", "c"),
                trace=dict(front=dict(src=os.path.join(OWN, "vv1.jpg"), box=(330, 330, 812, 524), mode="lines",
                                      erase=[(686, 340, 812, 350)], thr=0.6, cut="auto", cut_frac=0.30, up=2)),
                desc=UNI, refs="-", src="ELL"),
    "VV2": dict(family="cad", cad_module="cad_vv.py", cad_args=dict(code="VV2"), iso_args=dict(section_cut=False),
                tangent=None, kind="vv", L=184.0, W=82.0, tp=4.0, C=140.0, H=55.0, h_x=33.0, minH=78.5,
                total=128.0, thread="M16", thread_txt="M16 × 1,5", tip=(10.0, 10.0),
                neck=36.5, waist=(34.0, 12.0), rim=(53.8, 20.0, 26.4), top_x=32.6, top_washer=54.0,
                hole_l=("slot", 13.0, 30.0, "v", "c"), hole_r=("slot", 13.0, 22.0, "h", "c"),
                trace=dict(front=dict(src=os.path.join(OWN, "vv2.jpg"), box=(274, 300, 860, 515), mode="lines",
                                      erase=[(678, 324, 860, 334)], thr=0.6, cut="auto", cut_frac=0.30, up=2)),
                desc=UNI, refs="-", src="ELL"),
    "VV3": dict(family="cad", cad_module="cad_vv.py", cad_args=dict(code="VV3"), iso_args=dict(section_cut=False),
                tangent=None, kind="vv", L=228.0, W=112.0, tp=5.0, C=182.0, H=70.0, h_x=44.4, minH=100.0,
                total=170.0, thread="M20", thread_txt="M20 × 1,5", tip=(16.0, 16.0),
                neck=44.8, waist=(40.8, 18.9), rim=(61.7, 29.0, 35.0), top_x=44.4, top_washer=88.0,
                hole_l=("slot", 18.0, 34.0, "h"), hole_r=("slot", 18.0, 34.0, "v"),
                trace=dict(front=dict(src=os.path.join(OWN, "vv3.jpg"), box=(282, 330, 858, 523), mode="lines",
                                      erase=[(686, 341, 858, 351)], thr=0.6, cut="auto", cut_frac=0.30, up=2)),
                desc=UNI, refs="MAN 51.96210-7001 … 7037 · Trelleborg 17-1657", src="NV"),
    # --- MT: render cizimlerden
    "MT1": dict(family="cad", cad_module="cad_mt.py", cad_args=dict(code="MT1"), tangent=None, kind="mt", cup=(40.0, 32.0), end_half=17.7, redraw_holes=True, L=140.0, W=68.0, C=100.0, flange=22.0, support=70.0, upper_gap=10.0,
                slot=(12.5, 28.0), thread="M16", thread_txt="M16 × 1,5",
                trace=dict(front=ph("dmt1", mode="lines", box=(463, 475, 1066, 659), thr=0.5, frac=0.27)),
                desc=UNI, refs="-", src="NV"),
    "MT2": dict(family="cad", cad_module="cad_mt.py", cad_args=dict(code="MT2"), tangent=None, kind="mt", cup=(53.0, 43.0), end_half=25.5, redraw_holes=True, L=166.0, W=98.0, C=133.0, flange=25.0, support=75.0, upper_gap=10.0,
                slot=(13.0, 28.0), thread="M16", thread_txt="M16 × 1,5 / M18 × 1,5",
                trace=dict(front=ph("dmt2", mode="lines", box=(487, 459, 1079, 638), thr=0.5, frac=0.27)),
                desc=UNI, refs="-", src="NV"),
    "MT3": dict(family="cad", cad_module="cad_mt.py", cad_args=dict(code="MT3"), tangent=None, kind="mt", cup=(58.0, 46.0), end_half=27.0, redraw_holes=True, L=184.0, W=105.0, C=140.0, flange=27.0, support=90.0, upper_gap=12.0,
                slot=(16.0, 33.0), thread="M24", thread_txt="M24 × 1,5",
                trace=dict(front=ph("dmt3", mode="lines", box=(494, 457, 1094, 641), thr=0.5, frac=0.27)),
                desc=UNI, refs="-", src="NV"),
})

ORDER = ["50", "70", "75", "100", "150", "200", "SD150", "SD230", "SD430", "400", "450", "500", "600",
         "VV1", "VV2", "VV3", "MT1", "MT2", "MT3"]

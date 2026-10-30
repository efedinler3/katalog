"""Katalog icerigi. Urun metinleri Word dosyalarindan alinmistir (marka yazimi: Novibrasyon)."""

COMPANY = {
    "name": "Novibrasyon Marin",
    "whatsapp": "+90 530 780 19 95",
    "email": "info@novibrasyonmarin.com",
    "web": "www.novibrasyon.com",
    "instagram": "@novibrasyon",
    "address": ["Evliya Çelebi Mah. Mavi Sokak No: 25", "Tuzla / İstanbul, Türkiye"],
    "year": "2026",
}

SHIPPING = [
    "FedEx Express or UPS Express",
    "Estimated delivery in 2–4 business days, depending on destination and customs processing",
    "Insured packaging and shipment tracking",
]

FINISHES = [
    ("galv", "Galvanized steel", "Durable construction with corrosion protection for marine use."),
    ("ss", "316 stainless steel", "Enhanced corrosion resistance for demanding saltwater environments."),
]

NOTE_STD = ("To help us confirm compatibility, please send us a photo or the dimensions "
            "of your current mount before ordering.")
SD_CAPTION = ("Typical saildrive layout: the saildrive mount supports the gearbox / saildrive side at "
              "the back and two engine mounts carry the front. The front mount model depends on the "
              "engine — see the engine finder or ask us.")

# Bolumler. "accent": kenar sekmesi ve bolum vurgusu rengi.
SECTIONS = [
    {
        "id": "yanmar",
        "num": "01",
        "title": "Yanmar Engine Mounts",
        "intro": "Replacement mounts for Yanmar 1GM, 2GM, 3GM, 2YM, 3YM, 3JH, 4JH, 4LHA and "
                 "6LP / 6LY engines. The 75, 100, 150 and 200 come in galvanized steel or 316 "
                 "stainless steel.",
        "image": "div1",
        "image_mode": "photo",
        "accent": "#17737d",
        "products": ["50", "70", "75", "100", "150", "200", "400", "500"],
        "mid_photos": 4,          # 100'den sonra iki sayfalik yorumlu fotograf acilimi
    },
    {
        "id": "saildrive",
        "num": "02",
        "title": "Saildrive Mounts",
        "intro": "Rear mounts for the gearbox / saildrive side of Yanmar saildrive "
                 "installations, from SD20 to SD50.",
        "image": "div2",
        "image_mode": "photo",
        "accent": "#2c5d86",
        "products": ["sd"],
        "div_products": ["sd150", "sd230", "sd430"],     # bolum kapaginda uc model ayri satir + gorsel
        "div_note": SD_CAPTION,
    },
    {
        "id": "cummins",
        "num": "03",
        "title": "Cummins Engine Mounts",
        "intro": "Block mounts for Cummins 5.9, 6CTA 8.3, QSC 8.3, QSL9, QSB and QSM11 marine "
                 "diesels.",
        "image": "div3-motor",
        "image_mode": "photo",
        "accent": "#8c5a2b",
        "products": ["450", "600"],
    },
    {
        "id": "universal",
        "num": "04",
        "title": "Universal Mounts",
        "intro": "Flexible mounts chosen by load and rubber hardness, for Volvo Penta, Perkins, "
                 "Mercruiser, Beta, MAN, Cummins, Caterpillar and similar engines.",
        "image": "div4-vv",
        "image_mode": "photo",
        "accent": "#4a5a64",
        "products": ["vv1", "vv2", "vv3", "mt"],
    },
]

# ---------------------------------------------------------------------------
# Urunler
#   code      : buyuk yazilan model kodu
#   title     : tam urun adi (Word basligi)
#   tagline   : kisa slogan
#   intro     : kisa aciklama
#   hero      : [(gorsel, alt yazi)]
#   load      : takoz basina maks. yuk (one cikan deger), yoksa yazilmaz
#   fits      : [{"label", "models", "tag"}]   (tag yalnizca saildrive tipi icin)
#   fits_note : uyum notu
#   refs_head : parca no tablosu ilk sutun basligi
#   refs      : [(marka / uygulama, [parca no])]
#   finishes  : govde secenekleri gosterilsin mi
#   features  : ozellikler
#   dimrows   : olcu tablosu [(etiket, deger)]
#   variants  : (basliklar, satirlar)  - Shore / yuk tablolari
#   mounting  : MT olcu tablosu (model x olcu)
#   note      : siparis oncesi not
#   dims      : olcu gorseli (images), egriler (curves), aciklama (caption)
# ---------------------------------------------------------------------------
DIM_50_70 = [("Stud thread", "M14 × 1.5"), ("Base length", "159 mm"), ("Hole centers", "127.5 mm"),
             ("Holes", "Ø12.5 mm + slot"), ("Body height", "66 mm"), ("Min. height", "96.5 mm"),
             ("Total height", "147 mm")]
DIM_75_150 = [("Stud thread", "M16 × 1.5"), ("Base length", "200 mm"), ("Hole centers", "173 mm"),
              ("Holes", "Ø12.2 mm + 17.2 mm slot"), ("Body height", "75 mm"), ("Total height", "145 mm")]

# Govde secenekli Yanmar takozlari (75, 100, 150, 200): Word dosyalarindaki "Available Body Options"
FEAT_BODY = ["Bonded rubber element designed to reduce engine vibration and movement",
             "Helps support stable engine alignment",
             "Galvanized steel body with corrosion protection for marine use",
             "316 stainless steel option for demanding saltwater environments"]
FEAT_150 = ["Designed for higher engine loads",
            "Bonded rubber element designed to reduce vibration and engine movement",
            "Galvanized steel body with corrosion protection for marine use",
            "316 stainless steel option for demanding saltwater environments"]

PRODUCTS = {
    "50": {
        "code": "50",
        "title": "Novibrasyon 50 Marine Engine Mount — Yanmar 1GM",
        "tagline": "Used together with the 70 on the Yanmar 1GM.",
        "intro": "A marine engine mount designed to reduce vibration and support stable engine "
                 "alignment on Yanmar 1GM engines.",
        "hero": [("p50", None)],
        "load": "50 kg",
        "fits": [{"label": "Yanmar", "models": ["1GM"]}],
        "refs": [("Yanmar", ["128170-08340"])],
        "features": ["Bonded rubber element designed to reduce engine vibration and noise",
                     "Helps support stable engine alignment",
                     "Durable construction for marine environments"],
        "dimrows": DIM_50_70,
        "note": NOTE_STD,
        "dims": {"images": ["d50"], "curves": "c50"},
    },
    "70": {
        "code": "70",
        "title": "Novibrasyon 70 Marine Engine Mount — Yanmar 1GM",
        "tagline": "Used together with the 50 on the Yanmar 1GM.",
        "intro": "A marine engine mount designed to reduce vibration and support stable engine "
                 "alignment on Yanmar 1GM engines.",
        "hero": [("p70", None)],
        "load": "70 kg",
        "fits": [{"label": "Yanmar", "models": ["1GM"]}],
        "refs": [("Yanmar", ["128170-08350"])],
        "features": ["Bonded rubber element designed to reduce engine vibration",
                     "Helps support stable engine alignment",
                     "Designed for use in marine environments"],
        "dimrows": DIM_50_70,
        "note": NOTE_STD,
        "dims": {"images": ["d70"], "curves": "c70"},
    },
    "75": {
        "code": "75",
        "title": "Novibrasyon 75 Marine Engine Mount — Yanmar Series",
        "tagline": "For Yanmar 2GM, 3GM, 2YM and 3YM.",
        "intro": "A marine engine mount designed to reduce vibration and support stable engine "
                 "alignment in the Yanmar applications listed below.",
        "hero": [("p75", "Galvanized steel"), ("p75s", "316 stainless steel")],
        "fits": [
            {"label": "2GM series", "models": ["2GM", "2GM20", "2GM20B", "2GM20F", "2GMF"]},
            {"label": "2YM series", "models": ["2YM15"]},
            {"label": "3GM series", "models": ["3GM", "3GM30", "3GM30B", "3GM30F", "3GMD", "3GMDF", "3GMF"]},
            {"label": "3YM series", "models": ["3YM20", "3YM30", "3YM30AE"]},
        ],
        "refs": [("Yanmar", ["128270-08341", "128270-08340", "128377-08340", "128377-08341"])],
        "features": FEAT_BODY,
        "finishes": True,
        "dimrows": DIM_75_150,
        "note": NOTE_STD,
        "dims": {"images": ["d75"], "curves": "c75"},
    },
    "100": {
        "code": "100",
        "title": "Novibrasyon 100 Marine Engine Mount — Yanmar Series",
        "tagline": "For Yanmar 2GM, 3GM, 2YM, 3YM and 3JH.",
        "intro": "A marine engine mount designed to reduce vibration and support stable engine "
                 "alignment in the Yanmar applications listed below.",
        "hero": [("p100", "Galvanized steel"), ("p100s", "316 stainless steel")],
        "fits": [
            {"label": "2GM · 3GM · 2YM · 3YM",
             "models": ["2GM", "2GMF", "2GM20", "2GM20B", "2GM20F", "3GM", "3GMF", "3GMD", "3GMDF",
                        "3GM30", "3GM30B", "3GM30F", "2YM15", "3YM20", "3YM30", "3YM30AE"]},
            {"label": "3JH engines",
             "models": ["3JH2", "3JH2BE", "3JH2TBE", "3JH2E", "3JH2TE", "3JH3E", "3JH4E", "3JH5E",
                        "3JH5AE", "3JH40"]},
            {"label": "V-drive · 3HM",
             "models": ["2GM20V", "2GM20FV", "3GM30V", "3GM30FV", "3HM", "3HMF", "3HM35", "3HM35F"]},
        ],
        "refs": [("Yanmar", ["124772-08341", "128377-08351"])],
        "features": FEAT_BODY,
        "finishes": True,
        "dimrows": [("Stud thread", "M16 × 1.5"), ("Base length", "200 mm"), ("Hole centers", "173 mm"),
                    ("Holes", "Ø12.2 mm + 17.3 mm slot"), ("Body height", "75 mm"),
                    ("Total height", "145 mm")],
        "note": NOTE_STD,
        "dims": {"images": ["d100"], "curves": "c100"},
    },
    "150": {
        "code": "150",
        "title": "Novibrasyon 150 Marine Engine Mount — Yanmar Series",
        "tagline": "Made for higher engine loads.",
        "intro": "A marine engine mount designed for higher engine loads, vibration reduction and "
                 "stable engine alignment on Yanmar 3JH and 4JH engines.",
        "hero": [("p150", "Galvanized steel"), ("p150s", "316 stainless steel")],
        "fits": [
            {"label": "3JH series",
             "models": ["3JH2", "3JH2BE", "3JH2TBE", "3JH2E", "3JH2TE", "3JH3E", "3JH4E", "3JH5E",
                        "3JH5AE", "3JH40"]},
            {"label": "4JH series",
             "models": ["4JH-E", "4JH-TE", "4JH-HTE", "4JH-DTE", "4JH2", "4JH2E", "4JH2TE", "4JH2BE",
                        "4JH2TBE", "4JH2HTE", "4JH2DTE", "4JH2UTBE", "4JH2UTE", "4JH3E", "4JH4",
                        "4JH4-E", "4JH4-AE", "4JH5E", "4JH45", "4JH57"]},
        ],
        "refs": [("Yanmar", ["121370-08351"])],
        "features": FEAT_150,
        "finishes": True,
        "dimrows": DIM_75_150,
        "note": NOTE_STD,
        "dims": {"images": ["d150"], "curves": "c150"},
    },
    "200": {
        "code": "200",
        "title": "Novibrasyon 200 Marine Engine Mount — Yanmar 4JH Series",
        "tagline": "For the Yanmar 4JH series, turbo 4JH3 / 4JH4, 4JH80 and 4JH110.",
        "intro": "A marine engine mount designed to reduce vibration and support stable engine "
                 "alignment in Yanmar 4JH applications.",
        "hero": [("p200", "Galvanized steel"), ("p200s", "316 stainless steel")],
        "fits": [
            {"label": "4JH series", "models": ["4JH-E", "4JH-TE", "4JH-HTE", "4JH-DTE", "4JH2", "4JH3E", "4JH4-E",
                                               "4JH4-AE", "4JH5E", "4JH45", "4JH57"]},
            {"label": "4JH3 series", "models": ["4JH3-TE", "4JH3-HTE", "4JH3-DTE"]},
            {"label": "4JH4 series", "models": ["4JH4-TE", "4JH4-HTE"]},
            {"label": "4JH80 / 4JH110", "models": ["4JH80", "4JH110"]},
        ],
        "refs": [("Yanmar", ["129470-08350", "129670-08341"])],
        "features": FEAT_BODY,
        "finishes": True,
        "dimrows": [("Stud thread", "M16 × 1.5"), ("Base (L × W)", "205 × 60 mm"), ("Hole centers", "174 mm"),
                    ("Holes", "Ø12.2 mm + 17.5 mm slot"), ("Body height", "76 mm"),
                    ("Min. height", "103 mm"), ("Total height", "145 mm")],
        "note": NOTE_STD,
        "dims": {"images": ["d200"], "curves": "c200"},
    },
    "sd150": {
        "code": "SD150",
        "name": "Novibrasyon SD150 Saildrive",
        "title": "Novibrasyon 150 Saildrive Engine Mount — Yanmar SD20 / SD25",
        "tagline": "For Yanmar 2GM and 2YM15 with SD20 / SD25.",
        "intro": "A saildrive mount for selected Yanmar Saildrive installations. It helps reduce "
                 "vibration and support stable engine alignment.",
        "hero": [("psd150", None)],
        "fits": [
            {"label": "Yanmar engines", "models": ["2GM", "2GM20", "2GM20F", "2YM15"]},
            {"label": "Saildrive systems", "models": ["SD20", "SD25"]},
        ],
        "refs": [("Yanmar", ["129795-08340"])],
        "keyfigs": [("M12", "Studs, top and bottom"), ("SD20 · SD25", "Yanmar saildrive"), ("1", "Mount per saildrive")],
        "features": ["Bonded rubber element designed to reduce vibration and noise",
                     "Supports the engine at the gearbox / saildrive side",
                     "Durable construction for marine environments"],
        "dimrows": [("Studs", "M12, top and bottom"), ("Per saildrive", "1 mount")],
        "note": NOTE_STD,
        "dims": {"images": ["dsd150"], "curves": "csd150", "caption": SD_CAPTION},
    },
    "sd230": {
        "code": "SD230",
        "name": "Novibrasyon SD230 Saildrive",
        "title": "Novibrasyon 230 Saildrive Engine Mount — Yanmar Series",
        "tagline": "For Yanmar 3YM, 3GM, 3HM and 3JH with SD20 to SD50.",
        "intro": "A saildrive mount for selected Yanmar Saildrive installations. It helps reduce "
                 "vibration and support stable engine alignment.",
        "hero": [("psd230", None)],
        "fits": [
            {"tag": "SD20 · SD25 · SD30", "label": "Yanmar engines",
             "models": ["3YM20", "3YM30", "3GM30", "3HM35"]},
            {"tag": "SD31 · SD40 · SD50", "label": "Yanmar engines",
             "models": ["3JH2E", "3JH2TE", "3JH3E", "3JH4E", "3JH5E", "3JH5AE"]},
        ],
        "refs": [("Yanmar", ["196420-02310"])],
        "keyfigs": [("M12", "Studs, top and bottom"), ("SD20–SD50", "Yanmar saildrive"), ("1", "Mount per saildrive")],
        "features": ["Bonded rubber element designed to reduce vibration and noise",
                     "Supports the engine at the gearbox / saildrive side",
                     "Durable construction for marine environments"],
        "dimrows": [("Studs", "M12, top and bottom"), ("Per saildrive", "1 mount")],
        "note": NOTE_STD,
        "dims": {"images": ["dsd230"], "curves": "csd230", "caption": SD_CAPTION},
    },
    "sd430": {
        "code": "SD430",
        "name": "Novibrasyon SD430 Saildrive",
        "title": "Novibrasyon 430 Saildrive Engine Mount — Yanmar 4JH Series",
        "tagline": "For Yanmar 4JH with SD40 / SD50.",
        "intro": "A saildrive mount for selected Yanmar 4JH installations. It helps reduce "
                 "vibration and support stable engine alignment.",
        "hero": [("psd430", None)],
        "fits": [
            {"label": "Yanmar engines", "models": ["4JH3E", "4JH3TE", "4JH4E", "4JH4AE", "4JH4TE"]},
            {"label": "Saildrive systems", "models": ["SD40", "SD50"]},
        ],
        "refs": [("Yanmar", ["196440-02380"])],
        "keyfigs": [("M12", "Studs, top and bottom"), ("SD40 · SD50", "Yanmar saildrive"), ("1", "Mount per saildrive")],
        "features": ["Bonded rubber element designed to reduce vibration and noise",
                     "Supports the engine at the gearbox / saildrive side",
                     "Durable construction for marine environments"],
        "dimrows": [("Studs", "M12, top and bottom"), ("Per saildrive", "1 mount")],
        "note": NOTE_STD,
        "dims": {"images": ["dsd430"], "curves": "csd430", "caption": SD_CAPTION},
    },
    # Katalogda saildrive tek acilim (MT gibi): sd150 / sd230 / sd430 motor ve parca no bulucuda kalir.
    "sd": {
        "code": "SD",
        "name": "Novibrasyon SD Saildrive Series",
        "title": "Novibrasyon SD Series — Yanmar Saildrive Mounts",
        "tagline": "Three saildrive mounts, SD20 to SD50.",
        "intro": "Saildrive mounts for Yanmar saildrive installations. The SD150, SD230 and SD430 share "
                 "the same mounting dimensions and differ in load capacity; choose by engine and saildrive.",
        "hero": [("psd150", "SD150"), ("psd230", "SD230"), ("psd430", "SD430")],
        "keyfigs": [("SD20–SD50", "Yanmar saildrive"), ("SD150 · SD230 · SD430", "Three models"),
                    ("M12", "Studs, top and bottom")],
        "fits": [
            {"tag": "SD150", "label": "SD20 · SD25", "models": ["2GM", "2GM20", "2GM20F", "2YM15"]},
            {"tag": "SD230", "label": "SD20 · SD25 · SD30", "models": ["3YM20", "3YM30", "3GM30", "3HM35"]},
            {"tag": "SD230", "label": "SD31 · SD40 · SD50",
             "models": ["3JH2E", "3JH2TE", "3JH3E", "3JH4E", "3JH5E", "3JH5AE"]},
            {"tag": "SD430", "label": "SD40 · SD50", "models": ["4JH3E", "4JH3TE", "4JH4E", "4JH4AE", "4JH4TE"]},
        ],
        "features": ["Bonded rubber element designed to reduce vibration and noise",
                     "Supports the engine at the gearbox / saildrive side",
                     "One mount per saildrive"],
        "mounting": (["Model", "Yanmar part no.", "Studs", "Base (L × W)", "Height"],
                     [["SD150", "129795-08340", "M12, top and bottom", "130 × 61 mm", "64 mm"],
                      ["SD230", "196420-02310", "M12, top and bottom", "130 × 61 mm", "64 mm"],
                      ["SD430", "196440-02380", "M12, top and bottom", "130 × 61 mm", "64 mm"]]),
        "note": NOTE_STD,
        "dims": {"images": ["dsd150", "dsd230", "dsd430"], "labels": ["SD150", "SD230", "SD430"],
                 "curves": "csd", "caption": SD_CAPTION},
    },
    "400": {
        "code": "400",
        "title": "Novibrasyon 400 Marine Engine Mount — Yanmar 4LHA Series",
        "tagline": "Aluminum strength for the Yanmar 4LHA.",
        "intro": "A marine engine mount designed to reduce vibration and help maintain stable "
                 "engine alignment.",
        "hero": [("p400", None)],
        "fits": [{"label": "Yanmar", "models": ["4LHA-HTP", "4LHA-DTP", "4LHA-STP"]}],
        "refs": [("Yanmar", ["519175-08300", "119175-08440"])],
        "refs_note": "Novibrasyon 400 is our product model designation.",
        "features": ["Marine-grade aluminum body with corrosion-resistant construction",
                     "Bonded rubber element designed to reduce engine vibration and noise",
                     "Helps support stable engine alignment",
                     "Designed for the demanding conditions of marine use"],
        "dimrows": [("Stud thread", "M20"), ("Base (L × W)", "166 × 66 mm"), ("Hole centers", "127 mm"),
                    ("Holes", "2 slots, 14 × 28 mm"), ("Body height", "80 mm"), ("Min. height", "120 mm"),
                    ("Total height", "170 mm")],
        "note": NOTE_STD,
        "dims": {"images": ["d400"]},
    },
    "450": {
        "code": "450",
        "title": "Novibrasyon 450 Marine Engine Mount — Cummins 5.9 Series",
        "tagline": "Heavy-duty support for the Cummins 5.9.",
        "intro": "A marine engine mount designed to reduce vibration and help maintain stable "
                 "engine and drivetrain alignment.",
        "hero": [("p450", None)],
        "fits": [{"label": "Cummins", "models": ["6B 5.9", "6BT 5.9", "6BTA 5.9"]}],
        "refs": [("Cummins", ["3349230"]), ("Barry Controls", ["27655-2"])],
        "features": ["Durable construction for marine diesel applications",
                     "Bonded rubber element designed to reduce engine vibration and noise",
                     "Helps reduce vibration transfer to the hull and drivetrain",
                     "Designed for use in demanding marine environments"],
        "dimrows": [("Stud thread", "M20"), ("Base (L × W)", "165 × 85 mm"), ("Hole centers", "127 mm"),
                    ("Body height", "72 mm"), ("Min. height", "120 mm"), ("Total height", "170 mm")],
        "note": NOTE_STD,
        "dims": {"images": ["d450"]},
    },
    "500": {
        "code": "500",
        "title": "Novibrasyon 500 Marine Engine Mount",
        "tagline": "For Yanmar 6LP / 6LY, Cummins and Caterpillar.",
        "intro": "A marine engine mount designed to reduce vibration and support stable engine "
                 "alignment.",
        "hero": [("p500", None)],
        "fits": [
            {"label": "Yanmar", "models": ["6LPA-STP2", "6LPA-STC", "6LY2M-WDT", "6LY2A-UTP",
                                           "6LY2M-WST", "6LY400", "6LY440", "6LY2A-STP", "6LF550"]},
            {"label": "Cummins", "models": ["6CTA 8.3", "QSC 8.3", "QSL9", "QSB 6.7"]},
            {"label": "Caterpillar", "models": ["3116", "3126", "C7"]},
            {"label": "John Deere", "models": ["Selected marine engine applications"]},
        ],
        "fits_note": "The mount may also suit other marine engines when the mounting dimensions "
                     "and load requirements match.",
        "refs": [("Yanmar", ["119773-08300", "119773-08310"]), ("Cummins", ["3968021", "3393853"]),
                 ("Caterpillar", ["139-1502"]), ("Barry Controls", ["27391-8", "27391-9", "28717-2"])],
        "features": ["Marine-grade aluminum body with corrosion-resistant construction",
                     "Bonded rubber element designed to reduce vibration transfer",
                     "Helps support stable engine alignment",
                     "Designed for use in humid and saltwater marine environments"],
        "dimrows": [("Stud thread", "1″ × 14 TPI"), ("Base (L × W)", "166 × 93 mm"), ("Hole centers", "127 mm"),
                    ("Holes", "2 slots, 14 × 28 mm"), ("Body height", "90 mm"), ("Min. height", "130 mm"),
                    ("Total height", "190 mm")],
        "note": "Please confirm the existing mount part number, stud thread and engine load before "
                "ordering. Yanmar installations may use a different stud specification. For help "
                "confirming fitment, please send us your engine model and the part number or a photo "
                "of your current mount.",
        "dims": {"images": ["d500"],
                 "caption": "The drawing shows an M24 stud; the stud thread can differ by installation. "
                            "Please confirm before ordering."},
    },
    "600": {
        "code": "600",
        "title": "Novibrasyon 600 Marine Engine Mount — Cummins Series",
        "tagline": "Engine and gearbox, held in line.",
        "intro": "A marine engine mount designed to reduce vibration and support stable engine and "
                 "gearbox alignment.",
        "hero": [("p600", None)],
        "fits": [{"label": "Cummins", "models": ["QSM11", "QSB 5.9", "6CTA 8.3", "QSL9", "QSC 8.3"]}],
        "refs_head": "Engine application",
        "refs": [("Cummins QSM11", ["3964883"]), ("Cummins QSB 5.9", ["4931364", "5301975"]),
                 ("Cummins 6CTA 8.3 / QSL9 / QSC 8.3", ["3968021", "3393853"])],
        "features": ["Marine-grade aluminum body with corrosion-resistant construction",
                     "Bonded rubber element designed to reduce engine vibration and noise",
                     "Helps support stable engine and gearbox alignment",
                     "Suitable for leisure and commercial marine applications"],
        "dimrows": [("Stud thread", "M24"), ("Base (L × W)", "166 × 93 mm"), ("Hole centers", "127 mm"),
                    ("Body height", "95 mm"), ("Total height", "190 mm")],
        "note": "Mount specifications can vary between engine and gearbox configurations. Please "
                "confirm the existing mount part number, stud size and load requirements before "
                "ordering. Send us a photo of your current mount if you need help checking "
                "compatibility.",
        "dims": {"images": ["d600"]},
    },
    "vv1": {
        "code": "VV1",
        "title": "Novibrasyon VV1 Universal Engine Mount",
        "tagline": "Flexible support for smaller engines.",
        "intro": "A flexible marine engine mount designed to reduce vibration and support stable "
                 "engine alignment. Available in three rubber hardness options, with a choice of "
                 "galvanized steel or 316 stainless steel body.",
        "hero": [("pvv1", "Galvanized steel"), ("pvv1s", "316 stainless steel")],
        "load": "45–100 kg",
        "fits": [{"label": "Typical applications",
                  "models": ["Volvo Penta", "Perkins", "Mercruiser", "Beta Marine", "and similar engines"]}],
        "fits_note": "Selected installations, subject to checking the mounting dimensions and "
                     "engine load.",
        "variants": (["Rubber hardness", "Load capacity"],
                     [["45 Shore", "45 kg per mount"], ["55 Shore", "55 kg per mount"],
                      ["65 Shore", "100 kg per mount"]]),
        "finishes": True,
        "features": ["Bonded rubber element designed to reduce vibration and noise",
                     "Helps support stable engine alignment"],
        "dimrows": [("Stud thread", "M16 × 1.5"), ("Base (L × W)", "120 × 60.5 mm"), ("Hole centers", "100 mm"),
                    ("Holes", "Ø11 mm"), ("Body height", "43 mm"), ("Min. height", "68.5 mm"),
                    ("Total height", "125 mm")],
        "note": "To help us select the correct variant, please send us your engine model and a "
                "photo or the dimensions of your current mount before ordering.",
        "dims": {"images": ["dvv1"], "curves": "cvv", "series": "VV1"},
    },
    "vv2": {
        "code": "VV2",
        "title": "Novibrasyon VV2 Universal Engine Mount — M16 Stud",
        "tagline": "Flexible support for mid-size engines.",
        "intro": "A flexible marine engine mount designed to reduce vibration and support stable "
                 "engine alignment. Available in three rubber hardness options, with a choice of "
                 "galvanized steel or 316 stainless steel body.",
        "hero": [("pvv2", "Galvanized steel"), ("pvv2s", "316 stainless steel")],
        "load": "120–300 kg",
        "fits": [{"label": "Volvo Penta",
                  "models": ["D2-40", "D2-55", "D2-75", "D3-110", "D3-130", "D3-160", "D3-190",
                             "TAMD30", "TAMD31", "TAMD41", "KAD32", "KAMD42", "KAMD43", "KAMD44", "KAD300"]},
                 {"label": "Other engines",
                  "models": ["Yanmar", "Caterpillar", "MAN", "Perkins", "Cummins", "and similar engines"]}],
        "fits_note": "Selected marine engines, subject to checking the mounting dimensions and "
                     "load distribution.",
        "variants": (["Rubber hardness", "Load capacity"],
                     [["45 Shore", "120 kg per mount"], ["55 Shore", "200 kg per mount"],
                      ["65 Shore", "300 kg per mount"]]),
        "finishes": True,
        "features": ["Flexible rubber element designed to reduce vibration and noise",
                     "Helps support stable engine alignment"],
        "dimrows": [("Stud thread", "M16 × 1.5"), ("Base (L × W)", "184 × 82 mm"), ("Hole centers", "140 mm"),
                    ("Holes", "Ø13 mm + 17 mm slot"), ("Body height", "55 mm"), ("Min. height", "78.5 mm"),
                    ("Total height", "128 mm")],
        "note": "To help us select the correct variant, please send us your engine model and a "
                "photo or the dimensions of your current mount before ordering.",
        "dims": {"images": ["dvv2"], "curves": "cvv", "series": "VV2"},
    },
    "vv3": {
        "code": "VV3",
        "title": "Novibrasyon VV3 Universal Engine Mount — M20 Stud",
        "tagline": "Flexible support for large marine diesels.",
        "intro": "A large flexible marine engine mount designed to reduce vibration and support "
                 "stable engine alignment. Available in two rubber hardness and load capacity options.",
        "hero": [("pvv3", None)],
        "load": "500 / 800 kg",
        "variants": (["Variant", "Max. load", "Typical engine applications"],
                     [["55 Shore", "500 kg per mount",
                       "Volvo Penta D4 and D6 series; Yanmar 4LH and 6LP series; "
                       "Cummins 4BT, 6BT, 6BTA 5.9 and QSB 5.9; Perkins/Sabre M92, M115 and M130; "
                       "Caterpillar 3056 and C4.4; selected MAN applications"],
                      ["65 Shore", "800 kg per mount",
                       "Volvo Penta TAMD 63/71/72/73/74/75 and D9 series; MAN D0836, D0826, D2848 (V8), "
                       "D2840 (V10) and D2842 (V12); Cummins 6CTA 8.3, QSC 8.3, QSL9 and QSM11; Caterpillar "
                       "3116, 3126, C7 and C9"]]),
        "fits": [{"label": "Volvo Penta",
                  "models": ["D4 · D6", "TAMD63L-A · 63P-A", "TAMD71B", "TAMD73P-A · 73WJ-A",
                             "TAMD74A-A · A-B · C-A", "TAMD74L-A · L-B · P-A · P-B", "TAMD75P-A"]},
                 {"label": "MAN",
                  "models": ["D2866 LE201", "D2866 LE202", "D2866 LE203", "D2866 LE4 Series", "D2876 LE301",
                             "D2876 LE401", "D2876 LE402", "D2876 LE403", "D2876 LE404", "D2876 LE405",
                             "D2848 LE4 Series", "D2840 LE4 Series", "D2842 LE4 Series"]}],
        "refs": [("MAN", ["51.96210-7001", "51.96210-7002", "51.96210-7003", "51.96210-7004", "51.96210-7031",
                          "51.96210-7032", "51.96210-7033", "51.96210-7035", "51.96210-7037"]),
                 ("Trelleborg / Metalastik", ["17-1657-00", "17-1657-01", "17-1657-02", "17-1657-03"])],
        "refs_on_page": False,          # yalniz parca numarasi rehberinde (urun sayfasina sigmiyor)
        "fits_note": "MAN and Trelleborg / Metalastik reference numbers are listed in the part number finder.",
        "features": ["Bonded rubber element designed to reduce vibration and noise",
                     "Load options for different engine and gearbox installations",
                     "Helps support stable engine alignment"],
        "dimrows": [("Stud thread", "M20 × 1.5"), ("Base (L × W)", "228 × 112 mm"), ("Hole centers", "182 mm"),
                    ("Holes", "18 × 34 mm slots"), ("Body height", "70 mm"), ("Min. height", "100 mm"),
                    ("Total height", "170 mm")],
        "note": "The engine models and part numbers listed are potential replacement references; exact "
                "compatibility has not been verified for every model. To select the correct variant, please "
                "send us your engine model, engine and gearbox weight, and a photo or the dimensions of your "
                "current mount before ordering.",
        "dims": {"images": ["dvv3"], "curves": "cvv", "series": "VV3"},
    },
    "mt": {
        "code": "MT",
        "name": "Novibrasyon MT Series",
        "title": "Novibrasyon MT Series — Universal Marine Engine Mounts",
        "tagline": "Three sizes. Three hardness options.",
        "intro": "The Novibrasyon MT series offers three mount sizes for a wide range of marine "
                 "engines. Each model is available in 45, 55 and 65 Shore rubber hardness options, "
                 "allowing the mount to be selected according to the load at each mounting point.",
        "hero": [("pmt1", "MT1"), ("pmt2", "MT2"), ("pmt3", "MT3")],
        "load": "80–550 kg",
        "keyfigs": [("80–550 kg", "Max. load per mount"), ("MT1 · MT2 · MT3", "Three sizes"),
                    ("45 · 55 · 65", "Shore hardness options")],
        "variants": (["Model", "45 Shore", "55 Shore", "65 Shore", "Application guide"],
                     [["MT1", "80 kg", "140 kg", "200 kg", "approx. 9–130 hp"],
                      ["MT2", "140 kg", "220 kg", "350 kg", "approx. 100–240 hp"],
                      ["MT3", "200 kg", "400 kg", "550 kg", "approx. 200–650 hp"]]),
        "variants_note": "Loads shown are maximum static loads per mount. Horsepower ranges are "
                         "guides; engine weight and load distribution determine the correct model.",
        "mounting": (["Model", "Stud thread", "Base (L × W)", "Hole centers", "Slots", "Height"],
                     [["MT1", "M16 × 1.5", "140 × 68 mm", "100 mm", "12.5 × 28 mm", "70 mm"],
                      ["MT2", "M16 × 1.5 or M18 × 1.5", "166 × 98 mm", "133 mm", "13 × 28 mm", "75 mm"],
                      ["MT3", "M24 × 1.5", "184 × 105 mm", "140 mm", "16 × 33 mm", "90 mm"]]),
        "features": ["Three sizes covering a broad range of marine engine installations",
                     "Bonded rubber element designed to reduce vibration and noise",
                     "Choice of rubber hardness to suit different mounting loads"],
        "note": "To help us select the correct MT model and Shore hardness, please send your engine "
                "model, engine and gearbox weight, and a photo or measurements of your current "
                "mounts before ordering.",
        "dims": {"images": ["dmt1", "dmt2", "dmt3"], "labels": ["MT1", "MT2", "MT3"], "curves": "cmt",
                 "caption": "MT curves are calculated (5 mm deflection assumed at maximum load) and will be confirmed by measurement."},
    },
}

# ---------------------------------------------------------------------------
# Motor bulucu:  (marka, [(seri / motorlar, alt satir, [(urun, not)])])
#   not: yalnizca Shore onerisi veya saildrive tipi (montaj konumu yazilmaz)
# ---------------------------------------------------------------------------
FINDER = [
    ("Yanmar", [
        ("1GM", "", [("50", ""), ("70", "")]),
        ("2GM series", "2GM · 2GMF · 2GM20 · 2GM20B · 2GM20F", [("75", ""), ("100", "")]),
        ("2YM15", "", [("75", ""), ("100", "")]),
        ("3GM series", "3GM · 3GMF · 3GMD · 3GMDF · 3GM30 · 3GM30B · 3GM30F", [("75", ""), ("100", "")]),
        ("3YM series", "3YM20 · 3YM30 · 3YM30AE", [("75", ""), ("100", "")]),
        ("3JH series", "3JH2 · 3JH2BE · 3JH2TBE · 3JH2E · 3JH2TE · 3JH3E · 3JH4E · 3JH5E · 3JH5AE · 3JH40",
         [("100", ""), ("150", "")]),
        ("4JH series", "4JH-E · 4JH-TE · 4JH-HTE · 4JH-DTE · 4JH2 · 4JH2E · 4JH2TE · 4JH2BE · 4JH2TBE · "
                       "4JH2HTE · 4JH2DTE · 4JH2UTBE · 4JH2UTE · 4JH3E · 4JH4 · 4JH4-E · 4JH4-AE · "
                       "4JH5E · 4JH45 · 4JH57",
         [("150", ""), ("200", "")]),
        ("4JH3 / 4JH4 turbo · 4JH80 · 4JH110", "4JH3-TE · 4JH3-HTE · 4JH3-DTE · 4JH4-TE · 4JH4-HTE · 4JH80 · 4JH110",
         [("200", "")]),
        ("4LHA series", "4LHA-HTP · 4LHA-DTP · 4LHA-STP", [("400", ""), ("vv3", "55 Shore")]),
        ("4LH series", "", [("vv3", "55 Shore")]),
        ("6LP · 6LY · 6LF", "6LPA-STP2 · 6LPA-STC · 6LY2M-WDT · 6LY2A-UTP · 6LY2M-WST · 6LY400 · "
                            "6LY440 · 6LY2A-STP · 6LF550", [("500", ""), ("vv3", "55 Shore, 6LP")]),
    ]),
]

FINDER_2 = [
    ("Yanmar saildrive", [
        ("2GM · 2GM20 · 2GM20F · 2YM15", "with SD20 · SD25", [("sd150", "")]),
        ("3YM20 · 3YM30 · 3GM30 · 3HM35", "with SD20 · SD25 · SD30", [("sd230", "")]),
        ("3JH2E · 3JH2TE · 3JH3E · 3JH4E · 3JH5E · 3JH5AE", "with SD31 · SD40 · SD50", [("sd230", "")]),
        ("4JH3E · 4JH3TE · 4JH4E · 4JH4AE · 4JH4TE", "with SD40 · SD50", [("sd430", "")]),
    ]),
    ("Cummins", [
        ("6B 5.9", "", [("450", "")]),
        ("6BT · 6BTA 5.9", "", [("450", ""), ("vv3", "55 Shore")]),
        ("QSB 5.9", "", [("600", ""), ("vv3", "55 Shore")]),
        ("QSB 6.7", "", [("500", "")]),
        ("6CTA 8.3 · QSC 8.3 · QSL9", "", [("500", ""), ("600", ""), ("vv3", "65 Shore")]),
        ("QSM11", "", [("600", ""), ("vv3", "65 Shore")]),
        ("4BT", "", [("vv3", "55 Shore")]),
    ]),
    ("Caterpillar", [
        ("3116 · 3126 · C7", "", [("500", ""), ("vv3", "65 Shore")]),
        ("C9", "", [("vv3", "65 Shore")]),
        ("3056 · C4.4", "", [("vv3", "55 Shore")]),
    ]),
    ("John Deere", [
        ("Selected marine engines", "", [("500", "")]),
    ]),
]

FINDER_3 = [
    ("Volvo Penta", [
        ("D2 · D3 · TAMD30 · 31 · 41 · KAD · KAMD", "", [("vv2", "")]),
        ("D4 · D6 · TAMD 63 · 71–75 · D9", "", [("vv3", "55 Shore, D4 · D6"), ("vv3", "65 Shore, TAMD · D9")]),
        ("Selected installations", "", [("vv1", "")]),
    ]),
    ("MAN", [
        ("D2866 · D2876", "", [("vv3", "")]),
        ("D2848 · D2840 · D2842 · D0836 · D0826", "", [("vv3", "65 Shore")]),
        ("Selected installations", "", [("vv2", ""), ("vv3", "55 Shore")]),
    ]),
    ("Perkins / Sabre", [
        ("M92 · M115 · M130", "", [("vv3", "55 Shore")]),
        ("Selected installations", "", [("vv1", ""), ("vv2", "")]),
    ]),
    ("Universal Mounts", [
        ("Mercruiser · Beta Marine", "Selected installations", [("vv1", "")]),
        ("Yanmar · Cummins · Caterpillar", "Selected installations", [("vv2", "")]),
        ("Any marine engine", "Chosen by the load at each mount", [("vv1", ""), ("vv2", ""), ("vv3", ""), ("mt", "")]),
    ]),
]

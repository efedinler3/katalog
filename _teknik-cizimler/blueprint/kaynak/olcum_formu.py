"""Takoz yuk-cokme olcum formu (A4, kalemle doldurulur): ../../olcum-formu/takoz-cokme-olcum-formu.pdf

Grafigi olmayan 7 model: 400, 450, 500, 600 (bloklar) ve MT1, MT2, MT3 (45 / 55 / 65 Shore).
MT yuk adimlari katalogdaki maksimum yukun %25'lik dilimleri; bloklarda maksimum yuk bilinmiyor.
"""
import base64
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
KAT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "olcum-formu")
CHROME = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
          r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
          "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"]

BLOK = [
    ("400", "Yanmar 4LHA", [0, 50, 100, 150, 200, 250, 300]),
    ("450", "Cummins 6B · 6BT · 6BTA 5.9", [0, 50, 100, 150, 200, 250, 300, 350]),
    ("500", "Yanmar 6LY · Cummins 6CTA", [0, 75, 150, 225, 300, 375, 450]),
    ("600", "Cummins QSM11 · QSB 5.9", [0, 100, 200, 300, 400, 500]),
]
MT = [
    ("MT1", "140 × 68 mm · M16", [(45, 80), (55, 140), (65, 200)]),
    ("MT2", "166 × 98 mm · M16 / M18", [(45, 140), (55, 220), (65, 350)]),
    ("MT3", "184 × 105 mm · M24", [(45, 200), (55, 400), (65, 550)]),
]


def logo():
    with open(os.path.join(KAT, "assets", "logo-ink.png"), "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode()


def quarter(mx):
    out = []
    for f in (0, 0.25, 0.5, 0.75, 1.0):
        v = mx * f
        out.append(int(round(v / 5.0) * 5) if f not in (0, 1.0) else int(v))
    return out


def table(steps, extra=3, note_col=True):
    rows = []
    for i, kg in enumerate(steps):
        zero = kg == 0
        rows.append(f"<tr><td class='n'>{i + 1}</td><td class='kg'>{kg}</td>"
                    f"<td class='mm'>{'0,00' if zero else ''}</td>" + ("<td></td>" if note_col else "") + "</tr>")
    for j in range(extra):
        rows.append(f"<tr class='ex'><td class='n'>{len(steps) + j + 1}</td><td class='kg'></td><td class='mm'></td>"
                    + ("<td></td>" if note_col else "") + "</tr>")
    head = ("<tr><th class='n'>#</th><th>Yük (kg)</th><th>Çökme (mm)</th>" + ("<th>Not</th>" if note_col else "")
            + "</tr>")
    return f"<table><thead>{head}</thead><tbody>{''.join(rows)}</tbody></table>"


META = ("<div class='meta'><span>Tarih: <i></i></span><span>Ölçen: <i></i></span><span>Sıcaklık: <i class='s'></i> °C</span>"
        "<span class='cb'>☐ Ön yükleme (2 kez) yapıldı</span><span class='cb'>Yük: ☐ ağırlık ☐ baskül ☐ yük hücresi</span></div>")


def page(body, n, total, title):
    return (f"<section class='pg'><header><img src='{LOGO}' alt=''><div class='ht'><b>{title}</b>"
            f"<span>Takoz yük–çökme ölçüm formu</span></div></header>{body}"
            f"<footer><span>Novibrasyon · teknik çizim eğrileri için ölçüm</span><span>Sayfa {n} / {total}</span></footer></section>")


def build():
    pages = []
    intro = """
<h1>Takoz Yük–Çökme Ölçümü</h1>
<p class='lead'>Grafiği olmayan 7 modelin (400, 450, 500, 600, MT1, MT2, MT3) eğrileri bu ölçümlerden çizilecek.
Her takoz için tablodaki yük adımlarında komparatörde okunan çökmeyi mm olarak yazın. MT'lerde elde olan her sertlik
(45 / 55 / 65 Shore) ayrı ölçülür; olmayan sertliğin tablosu boş kalabilir.</p>
<div class='two'>
<div>
<h2>Gerekenler</h2>
<ul>
<li>Komparatör (0,01 mm hassasiyet) ve manyetik ayak</li>
<li>İki düz, kalın çelik plaka (alt ve üst)</li>
<li>Küçük yükler için ağırlık plakaları</li>
<li>Büyük yükler için hidrolik pres veya sağlam kiriş + kriko; altına 500 kg'lık dijital baskül ya da yük hücresi</li>
</ul>
<h2>Güvenlik</h2>
<ul>
<li>Yükü takozun tam ortasına verin, yandan kaymasın.</li>
<li>Kriko veya pres altındayken elinizi yükün altına sokmayın.</li>
<li>Bloklarda (400–600) çökme yaklaşık 8 mm'ye ulaşınca veya yük 500 kg'ı geçince durun.</li>
</ul>
</div>
<div>
<h2>Adımlar</h2>
<ol>
<li>Takozu alt plakaya koyun. Somun ve pulları minimum yükseklik konumuna getirin; yük, motor ayağı gibi üst pula otursun.</li>
<li><b>Ön yükleme:</b> takozu tablodaki en yüksek yüke kadar 2 kez yükleyip boşaltın, sonra 5 dakika bekletin.</li>
<li>Komparatörü üst plakaya dayayıp sıfırlayın: 0 kg = 0,00 mm.</li>
<li>Yükü tablodaki adımlarla artırın. Her adımda <b>1 dakika</b> bekleyip çökmeyi okuyun ve yazın.</li>
<li>Gerekirse boş satırlara ara veya ek yük adımları yazabilirsiniz.</li>
<li>Ortam 15–25 °C olsun; sıcaklığı her tablonun üstüne yazın.</li>
</ol>
</div>
</div>
<h2>Dolduran için not</h2>
<p>Doğal frekans ayrıca ölçülmez; çökmeden hesaplanır: <span class='f'>f = 15,76 / √çökme(mm)</span> Hz.
Formu doldurduktan sonra sayfaların net fotoğrafını göndermeniz yeterli; eğriler çizim sayfalarına eklenecek.</p>
<h2>Ölçülecek takozlar</h2>
<table class='list'><thead><tr><th>Model</th><th>Motor / ölçü</th><th>Ölçülecek</th><th>Sayfa</th></tr></thead><tbody>
<tr><td>400</td><td>Yanmar 4LHA</td><td>1 takoz</td><td>2</td></tr>
<tr><td>450</td><td>Cummins 6B · 6BT · 6BTA 5.9</td><td>1 takoz</td><td>2</td></tr>
<tr><td>500</td><td>Yanmar 6LY · Cummins 6CTA</td><td>1 takoz</td><td>3</td></tr>
<tr><td>600</td><td>Cummins QSM11 · QSB 5.9</td><td>1 takoz</td><td>3</td></tr>
<tr><td>MT1</td><td>140 × 68 mm · M16</td><td>45 / 55 / 65 Shore</td><td>4</td></tr>
<tr><td>MT2</td><td>166 × 98 mm · M16 / M18</td><td>45 / 55 / 65 Shore</td><td>5</td></tr>
<tr><td>MT3</td><td>184 × 105 mm · M24</td><td>45 / 55 / 65 Shore</td><td>6</td></tr>
</tbody></table>"""
    bodies = [("Ölçüm yöntemi", intro)]
    for i in range(0, len(BLOK), 2):
        blocks = []
        for code, desc, steps in BLOK[i:i + 2]:
            blocks.append(f"<div class='blk'><div class='bh'><h2>Novibrasyon {code}</h2><span>{desc} · maksimum yük "
                          f"bilinmiyor, ~8 mm çökmede durun</span></div>{META}{table(steps, extra=3)}</div>")
        bodies.append((f"Blok takozlar · {BLOK[i][0]} / {BLOK[i + 1][0]}", "".join(blocks)))
    for code, desc, shores in MT:
        cols = []
        for sh, mx in shores:
            cols.append(f"<div class='col'><h3>{sh} Shore</h3><p class='mx'>Maks. {mx} kg</p>"
                        f"<div class='meta v'><span>Sıcaklık: <i class='s'></i> °C</span>"
                        f"<span class='cb'>☐ Ön yükleme yapıldı</span><span class='cb'>☐ Bu sertlik elde yok</span></div>"
                        f"{table(quarter(mx), extra=3, note_col=False)}</div>")
        body = (f"<div class='bh'><h2>Novibrasyon {code}</h2><span>{desc} · yük adımları katalogdaki maksimum yükün "
                f"%25'lik dilimleri</span></div><div class='meta'><span>Tarih: <i></i></span><span>Ölçen: <i></i></span>"
                f"<span class='cb'>Yük: ☐ ağırlık ☐ baskül ☐ yük hücresi</span></div><div class='three'>{''.join(cols)}</div>"
                f"<div class='notes'><b>Notlar</b></div>")
        bodies.append((f"{code} · 45 / 55 / 65 Shore", body))
    total = len(bodies)
    pages = [page(b, i + 1, total, t) for i, (t, b) in enumerate(bodies)]
    css = """
@page { size: A4; margin: 0 }
* { box-sizing: border-box }
html, body { margin: 0; padding: 0; background: #fff; color: #14283a; font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5pt }
.pg { width: 210mm; height: 297mm; padding: 13mm 14mm 12mm; page-break-after: always; display: flex; flex-direction: column; gap: 4mm; overflow: hidden }
header { display: flex; align-items: center; justify-content: space-between; border-bottom: 0.6mm solid #14283a; padding-bottom: 3mm }
header img { height: 9mm }
.ht { text-align: right; display: grid }
.ht b { font-size: 12pt; letter-spacing: .02em }
.ht span { font-size: 8.5pt; color: #5a6b7b; letter-spacing: .12em; text-transform: uppercase }
footer { margin-top: auto; display: flex; justify-content: space-between; font-size: 8pt; color: #5a6b7b; border-top: 0.2mm solid #b8c4ce; padding-top: 2mm }
h1 { font-size: 22pt; margin: 2mm 0 0; line-height: 1.1 }
h2 { font-size: 12.5pt; margin: 3mm 0 1.5mm }
h3 { font-size: 12pt; margin: 0 }
p { margin: 0 0 2mm; line-height: 1.45 }
.lead { color: #33495c; max-width: 165mm }
ul, ol { margin: 0 0 2mm; padding-left: 5mm; line-height: 1.45 }
li { margin-bottom: 1mm }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 8mm }
.f { font-family: Consolas, monospace; border: 0.2mm solid #b8c4ce; padding: 0.3mm 1.5mm; border-radius: 1mm; white-space: nowrap }
table { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums }
th { font-size: 8.5pt; text-transform: uppercase; letter-spacing: .08em; color: #5a6b7b; text-align: left; padding: 1.5mm 2mm; border-bottom: 0.4mm solid #14283a }
td { border-bottom: 0.2mm solid #b8c4ce; padding: 0 2mm; height: 9.2mm; font-size: 11pt }
td.n, th.n { width: 9mm; color: #5a6b7b; font-size: 9pt }
td.kg { width: 28mm; font-weight: 600 }
td.mm { width: 38mm; border-left: 0.2mm solid #b8c4ce; border-right: 0.2mm solid #b8c4ce; background: #f4f7f9 }
tr.ex td.kg { font-weight: 400 }
table.list td { height: 7mm; font-size: 10pt }
.blk { display: grid; gap: 2mm; margin-bottom: 4mm }
.bh { display: flex; align-items: baseline; justify-content: space-between; gap: 4mm; flex-wrap: wrap }
.bh h2 { margin: 0; font-size: 15pt }
.bh span { color: #5a6b7b; font-size: 9pt }
.meta { display: flex; flex-wrap: wrap; gap: 2mm 6mm; font-size: 9.5pt; align-items: baseline }
.meta i { display: inline-block; width: 32mm; border-bottom: 0.2mm solid #14283a; height: 4mm }
.meta i.s { width: 12mm }
.meta.v { flex-direction: column; gap: 1.5mm }
.cb { white-space: nowrap }
.three { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5mm }
.col { display: grid; gap: 1.5mm; align-content: start }
.col .mx { margin: 0; color: #5a6b7b; font-size: 9pt }
.col td.kg { width: auto } .col td.mm { width: 26mm }
.notes { flex: 1; border: 0.2mm solid #b8c4ce; border-radius: 1.5mm; padding: 2mm 3mm; min-height: 30mm; font-size: 9.5pt; color: #5a6b7b }
"""
    html = ("<!doctype html><html lang='tr'><head><meta charset='utf-8'><title>Takoz Yük–Çökme Ölçüm Formu</title><style>"
            + css + "</style></head><body>" + "".join(pages) + "</body></html>")
    os.makedirs(OUT, exist_ok=True)
    hp = os.path.join(HERE, "_olcum-formu.html")
    with open(hp, "w", encoding="utf-8") as fh:
        fh.write(html)
    pdf = os.path.join(OUT, "takoz-cokme-olcum-formu.pdf")
    exe = next(c for c in CHROME if os.path.exists(c))
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                    f"--print-to-pdf={pdf}", "file:///" + hp.replace("\\", "/")], check=True, capture_output=True)
    import pymupdf
    doc = pymupdf.open(pdf)
    for i, pg in enumerate(doc):
        pg.get_pixmap(dpi=70).save(os.path.join(HERE, f"_olcum-onizleme-{i + 1}.png"))
    print(pdf, len(doc), "sayfa")


LOGO = logo()

if __name__ == "__main__":
    build()

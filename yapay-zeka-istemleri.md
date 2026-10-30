# Novibrasyon katalog — fotoğraf slotları için ChatGPT / Gemini istemleri

Her ürünün katalogda 3 boş fotoğraf slotu var:
- **Slot 1 (büyük, dikey):** takoz motora takılı hâlde
- **Slot 2 (küçük):** yakın çekim detay
- **Slot 3 (küçük):** elde veya set hâlinde

**Nasıl kullanılır**
1. ChatGPT'de yeni bir sohbet açın.
2. Aşağıdaki "referans fotoğraf" dosyasını sohbete ekleyin. Dosyalar `assets\img\` klasöründe.
3. "Ortak kurallar" metnini, ardından slotun istemini yapıştırın.
4. Sonucu `fotograflar\<ürün>\1.jpg`, `2.jpg` veya `3.jpg` olarak kaydedin ve `KATALOGU-OLUSTUR.bat` dosyasını çalıştırın.
5. Görseli kataloğa koymadan önce saplama, somun sayısı, delik sayısı ve gövde şeklinin gerçek ürünle aynı olduğunu kontrol edin. Yapay zekâ bazen parça ekler ya da çıkarır.

## Ortak kurallar (her istemin başına ekleyin)

> Use the attached photo as the exact product reference. Keep the product's shape, proportions, colours, stud, nuts, washers, base plate and bolt holes exactly as in the reference — do not add, remove or redesign any part. Photorealistic product photography for a premium printed catalogue, natural soft light, realistic materials, sharp focus on the mount, shallow depth of field. No text, no logos, no brand names, no watermarks, no people's faces.

## İstemler

Her ürünün istemleri aynı kalıbı izler; sadece referans ve motor adı değişir.

- **S1 (dikey 2:3):** "Show this exact engine mount installed under the {POSITION} engine foot of a {ENGINE} marine diesel engine in a clean boat engine room, bolted to a GRP engine bed, the adjusting nuts visible. Vertical 2:3 image."
- **S2 (kare):** "Close-up detail of this exact mount: the threaded stud, the adjusting nuts and the {MATERIAL} body with the bonded black rubber element, on a neutral light-grey surface. Square image."
- **S3 (kare):** "A mechanic's hand in a work glove holding this exact mount to show its size, workshop background softly out of focus. Square image." *(Alternatif: "A set of four of these exact mounts neatly arranged on a clean workbench.")*

| Ürün | Referans fotoğraf | {ENGINE} | {POSITION} | {MATERIAL} |
|---|---|---|---|---|
| 50 | p50.jpg | Yanmar 1GM | front | black-coated steel |
| 70 | p70.jpg | Yanmar 1GM | rear (gearbox side) | black-coated steel |
| 75 | p75.jpg | Yanmar 3GM | rear (gearbox side) | galvanized steel |
| 100 | p100.jpg | Yanmar 3YM | front | galvanized steel |
| 150 | p150.jpg | Yanmar 4JH | right side | galvanized steel |
| 200 | p200.jpg | Yanmar 4JH turbo | right side | galvanized steel |
| SD150 / SD230 / SD430 | psd.jpg | Yanmar saildrive engine | rear saildrive leg | black rubber-and-steel saildrive |
| 400 | p400.jpg | Yanmar 4LHA | front | aluminium |
| 450 | p450.jpg | Cummins 6BT 5.9 | front | black steel |
| 500 | p500.jpg | Cummins 6CTA 8.3 | rear | steel |
| 600 | p600.jpg | Cummins QSM11 | front | black |
| VV1 | pvv1.jpg | Volvo Penta D2-40 | front | galvanized steel |
| VV2 | pvv2.jpg | Perkins M92 | front | galvanized steel |
| VV3 | pvv3.jpg | Volvo Penta TAMD 63 | front | black rubber-coated steel |
| MT | pmt2.jpg | 6-cylinder marine diesel | front | grey cast body |

**Not:** Saildrive (SD) ürünleri için S1 şöyle olmalı: "Show this exact mount fitted between the saildrive leg and the hull, under the engine's gearbox end, as in a Yanmar saildrive installation." Doğru olmayan bir kurulum görüntüsü müşteriyi yanıltabilir. Emin değilseniz S2 ve S3 ile yetinin.

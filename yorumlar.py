"""eBay alici yorumlari (sahibin sectigi 19 yorum, metin aynen) ve kucuk bayraklar.
Tam sayfa fotograflarin altinda petek dizilimli radyuslu kartlar olarak basilir (build.p_photo)."""

# (ulke kodu ya da "", metin)
REVIEWS = [
    ("CA", "I ordered four engine mounts to replace the old ones on my Yanmar 4 JH2-DTE. Two days later, I received those from Istanbul, Turkey to Montreal, Canada. The price including shipping was really good, it was well packaged , in perfect condition and the quality is comparable even better than the original. I’m really happy and recommend this supplier to anyone."),
    ("GB", "Could not ask for better service to the UK - fantastic quality and speed of service first rate, wouldnt hesitate to order again, exceptional value for money, both condition and appearance first rate"),
    ("GB", "Excellent service and great communication. The order was shipped the same day and received a few days earlier than originally estimated. The engine mounts arrived well packaged, look well-built, and have the appearance of a high quality product. I highly recommend this seller."),
    ("US", "I purchased these on a Monday with a 7 day delivery promise. (Istanbul Turkey to San Diego US) The package arrived in 3 days in perfect condition. I also was informed I may have to pay duty when the motor mounts reached the US but I did not have to pay anything. THANK YOU NOVIBRASYYON! I will be replacing the motor mounts on my sailboat with a Yanmar 3jh2e motor. These are the exact size and look to be top quality. The value is unmatched. By far the best price I could find."),
    ("ES", "Vendedor súper recomendable. Se le ha preguntado por los soportes y la respuesta ha sido inmediata. El producto llegó en perfectas condiciones y muy muy rápido. Increíble el embalaje y envío. Recomendado 100x100."),
    ("IT", "Persona gentilissima ha risolto tutti i miei dubbi e problemi per poter acquistare il prodotto 5 stelle sono veramente poche 100% positivo super raccomando se avrei di nuovo bisogno non esiterei ad acquistare da lei grazie mille di tutto"),
    ("FI", "Thank you for a very fast delivery and high-grade products well packed in high quality sealed packings. We are very pleased with you! Keep up the good work! Best regards from Finland, EU"),
    ("US", "First class service email acknowledged in 2 minutes problem resolved within 10 minutes would not hesitate in recommending this company"),
    ("GB", "Very impressed with the seller. Packaging and postage was absolutely spot on! No problems receiving updates etc! My engine mounts are perfect for my needs."),
    ("US", "Good price. Very helpful. I ordered them and put the wrong address in immediately canceled it and ordered it again and they refunded the original without any issue. I would definitely do business with them again!"),
    ("DE", "Super Service, Samstags bestellt, Sonntag früh die Bestellung geändert, Sonntag Mittag wurde die Bestellung mit der Änderung bestätigt, Mittwoch waren die Teile da!"),
    ("DE", "Die Lieferung war zu schnell für mich, ich war von einer längeren Lieferzeit ausgegangen. Die Motorfüße sind genau richtig. Vielen Dank mit Ihnen mache ich gerne wieder Geschäfte."),
    ("US", "Beautiful engine mounts. The polished stainless steel look fantastic. Fast shipping to USA. Highly recommend."),
    ("GB", "Fantastic product, excellent customer service, highly recommended! Fast delivery, Excellent condition."),
    ("US", "Excellent experience. The shipping was faster than most of the vendors in the USA. Will buy again! A++"),
    ("US", "Unbelievable fast delivery, the items even beter quality then original one.Thank you"),
    ("GB", "Mounts look amazing quality, really pleased, great service, highly recommend"),
    ("US", "All good regarding product packing and shipping. Fedex tracking great. Arrived 5 days earlier than expected. Still have to fit into yacht."),
    ("GB", "I have not tested the engine mounts yet, but package arrived quickly, well packaged and without any sign of damage. Looks promising!"),
]

COUNTRY = {"CA": ("Kanada", "Canada"), "GB": ("Birleşik Krallık", "United Kingdom"),
           "US": ("ABD", "USA"), "FI": ("Finlandiya", "Finland"), "ES": ("İspanya", "Spain"),
           "IT": ("İtalya", "Italy"), "DE": ("Almanya", "Germany")}

# 3:2 basit bayraklar (SVG)
_W, _H = 30, 20
FLAGS = {
    "ES": f'<rect width="{_W}" height="{_H}" fill="#c60b1e"/><rect y="5" width="{_W}" height="10" fill="#ffc400"/>',
    "IT": f'<rect width="10" height="{_H}" fill="#009246"/><rect x="10" width="10" height="{_H}" fill="#fff"/><rect x="20" width="10" height="{_H}" fill="#ce2b21"/>',
    "DE": f'<rect width="{_W}" height="{_H / 3:.3f}" fill="#000"/><rect y="{_H / 3:.3f}" width="{_W}" height="{_H / 3:.3f}" fill="#dd0000"/><rect y="{2 * _H / 3:.3f}" width="{_W}" height="{_H / 3:.3f}" fill="#ffce00"/>',
    "FI": f'<rect width="{_W}" height="{_H}" fill="#fff"/><rect x="8" width="5" height="{_H}" fill="#003580"/>'
          f'<rect y="7.5" width="{_W}" height="5" fill="#003580"/>',
    "CA": f'<rect width="{_W}" height="{_H}" fill="#fff"/><rect width="7.5" height="{_H}" fill="#d52b1e"/>'
          f'<rect x="22.5" width="7.5" height="{_H}" fill="#d52b1e"/>'
          '<path d="M15 4l1.2 2.6 2-1-.6 3.4 2.2-1.4.4 1.6 2-.4-1 2.2.8.6-3.4 2.4.4 1.4-3.2-.4V18h-.6v-2.9l-3.2.4.4-1.4'
          '-3.4-2.4.8-.6-1-2.2 2 .4.4-1.6 2.2 1.4-.6-3.4 2 1z" fill="#d52b1e"/>',
    "US": "".join(f'<rect y="{i * _H / 13:.3f}" width="{_W}" height="{_H / 13:.3f}" fill="{"#b22234" if i % 2 == 0 else "#fff"}"/>'
                  for i in range(13)) + f'<rect width="12" height="{_H * 7 / 13:.3f}" fill="#3c3b6e"/>',
    "GB": f'<rect width="{_W}" height="{_H}" fill="#012169"/>'
          f'<path d="M0 0L{_W} {_H}M{_W} 0L0 {_H}" stroke="#fff" stroke-width="4"/>'
          f'<path d="M0 0L{_W} {_H}M{_W} 0L0 {_H}" stroke="#c8102e" stroke-width="1.6"/>'
          f'<path d="M{_W / 2} 0V{_H}M0 {_H / 2}H{_W}" stroke="#fff" stroke-width="6"/>'
          f'<path d="M{_W / 2} 0V{_H}M0 {_H / 2}H{_W}" stroke="#c8102e" stroke-width="3.6"/>',
}


def flag_svg(code):
    if code not in FLAGS:
        return ""
    return (f'<svg class="flag" viewBox="0 0 {_W} {_H}" xmlns="http://www.w3.org/2000/svg">'
            f'<clipPath id="fc{code}"><rect width="{_W}" height="{_H}" rx="2"/></clipPath>'
            f'<g clip-path="url(#fc{code})">{FLAGS[code]}</g></svg>')

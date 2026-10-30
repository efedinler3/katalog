"""Novibrasyon teknik cizim kiti: SVG uzerinde olcekli gorunus, cizgi tipleri, tarama, olcu oklari, yazilar.

Sayfa birimi mm (SVG viewBox), y asagi. Urun koordinatlari mm, y yukari; View donusturur.
Cizgi tipleri (ISO 128 benzeri): kalin gorunur kenar, ince olcu / tarama, kesikli gizli kenar, zincir eksen.
"""
import math

FONT = "'Segoe UI', Arial, sans-serif"
INK = "#111418"
LW = {"thick": 0.42, "mid": 0.28, "thin": 0.17, "hatch": 0.13}
TXT = 3.1            # olcu yazisi yuksekligi (mm)
AL, AW = 2.5, 0.9    # ok boyu / yarim genislik (mm)
GAP = 0.9            # uzatma cizgisinin cisimden boslugu (mm)
OVER = 1.6           # uzatma cizgisinin olcu cizgisini asmasi (mm)


def fmt(v):
    """12.5 -> '12,5'; 12.0 -> '12'."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s.replace(".", ",")


def arc(cx, cy, r, a0, a1, n=None):
    """Derece cinsinden a0 -> a1 yayi (urun koordinatlari, saat yonu tersine pozitif)."""
    n = n or max(6, int(abs(a1 - a0) / 6))
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def fillet_poly(pts, r, closed=True, n=8):
    """Kose yuvarlatma: her kosede r yaricapli yay (r sayi ya da kose basina liste)."""
    out = []
    m = len(pts)
    rr = r if isinstance(r, (list, tuple)) else [r] * m
    rng = range(m) if closed else range(1, m - 1)
    if not closed:
        out.append(pts[0])
    for i in rng:
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % m]
        ri = rr[i]
        if ri <= 0:
            out.append(p1)
            continue
        v1 = (p0[0] - p1[0], p0[1] - p1[1])
        v2 = (p2[0] - p1[0], p2[1] - p1[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        if l1 == 0 or l2 == 0:
            out.append(p1)
            continue
        u1, u2 = (v1[0] / l1, v1[1] / l1), (v2[0] / l2, v2[1] / l2)
        cosang = max(-1.0, min(1.0, u1[0] * u2[0] + u1[1] * u2[1]))
        ang = math.acos(cosang)
        if ang < 1e-3 or abs(ang - math.pi) < 1e-3:
            out.append(p1)
            continue
        t = ri / math.tan(ang / 2)
        t = min(t, l1 * 0.49, l2 * 0.49)
        ri = t * math.tan(ang / 2)
        a = (p1[0] + u1[0] * t, p1[1] + u1[1] * t)
        b = (p1[0] + u2[0] * t, p1[1] + u2[1] * t)
        bis = (u1[0] + u2[0], u1[1] + u2[1])
        bl = math.hypot(*bis)
        d = ri / math.sin(ang / 2)
        c = (p1[0] + bis[0] / bl * d, p1[1] + bis[1] / bl * d)
        a0 = math.degrees(math.atan2(a[1] - c[1], a[0] - c[0]))
        a1 = math.degrees(math.atan2(b[1] - c[1], b[0] - c[0]))
        da = (a1 - a0 + 540) % 360 - 180
        out += [(c[0] + ri * math.cos(math.radians(a0 + da * k / n)),
                 c[1] + ri * math.sin(math.radians(a0 + da * k / n))) for k in range(n + 1)]
    if not closed:
        out.append(pts[-1])
    return out


def mirror(pts):
    """Sag yari profili (x>=0, yukaridan asagi ya da asagidan yukari) -> tam simetrik kapali profil."""
    return pts + [(-x, y) for (x, y) in reversed(pts)]


class Sheet:
    def __init__(self, w=300.0, h=240.0):
        self.w, self.h = w, h
        self.items = []

    def add(self, s):
        self.items.append(s)

    def svg(self, extra_css=""):
        defs = (f'<defs><pattern id="h45" patternUnits="userSpaceOnUse" width="1.3" height="1.3" '
                f'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="1.3" stroke="{INK}" '
                f'stroke-width="{LW["hatch"]}"/></pattern>'
                f'<pattern id="h135" patternUnits="userSpaceOnUse" width="1.3" height="1.3" '
                f'patternTransform="rotate(-45)"><line x1="0" y1="0" x2="0" y2="1.3" stroke="{INK}" '
                f'stroke-width="{LW["hatch"]}"/></pattern>'
                f'<pattern id="rub" patternUnits="userSpaceOnUse" width="2.2" height="2.2" '
                f'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="2.2" stroke="{INK}" '
                f'stroke-width="0.11" stroke-dasharray="0.5 0.6"/></pattern></defs>')
        css = (f'<style>text{{font-family:{FONT};fill:{INK}}} .thick{{stroke:{INK};stroke-width:{LW["thick"]};fill:none;'
               f'stroke-linejoin:round;stroke-linecap:round}} .mid{{stroke:{INK};stroke-width:{LW["mid"]};fill:none;'
               f'stroke-linejoin:round}} .thin{{stroke:{INK};stroke-width:{LW["thin"]};fill:none}} '
               f'.hid{{stroke:{INK};stroke-width:{LW["thin"]};fill:none;stroke-dasharray:1.6 0.9}} '
               f'.cen{{stroke:{INK};stroke-width:{LW["thin"]};fill:none;stroke-dasharray:7 1.1 1 1.1}} '
               f'.grid{{stroke:{INK};stroke-width:0.1;fill:none}} .curve{{stroke:{INK};stroke-width:0.34;fill:none;stroke-linejoin:round;stroke-linecap:round}} '
               f'{extra_css}</style>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}mm" height="{self.h}mm" '
                f'viewBox="0 0 {self.w} {self.h}">{defs}{css}<rect width="{self.w}" height="{self.h}" fill="#fff"/>'
                + "".join(self.items) + "</svg>")

    # --- sayfa koordinatinda yardimcilar
    def text(self, x, y, s, size=TXT, anchor="middle", weight=400, rot=0, ls=0):
        tr = f' transform="rotate({rot} {x:.3f} {y:.3f})"' if rot else ""
        lsp = f' letter-spacing="{ls}"' if ls else ""
        self.add(f'<text x="{x:.3f}" y="{y:.3f}" font-size="{size}" text-anchor="{anchor}" '
                 f'font-weight="{weight}"{lsp}{tr}>{esc(s)}</text>')

    def line(self, x1, y1, x2, y2, cls="thin"):
        self.add(f'<line class="{cls}" x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}"/>')

    def rect(self, x, y, w, h, cls="thin", fill=None, rx=0):
        f = f' style="fill:{fill}"' if fill else ""
        self.add(f'<rect class="{cls}" x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" rx="{rx}"{f}/>')

    def arrow(self, x, y, dx, dy):
        """(x, y) ucunda, (dx, dy) yonunu gosteren dolu ok."""
        l = math.hypot(dx, dy)
        ux, uy = dx / l, dy / l
        bx, by = x - ux * AL, y - uy * AL
        self.add(f'<path d="M{x:.3f},{y:.3f} L{bx - uy * AW:.3f},{by + ux * AW:.3f} '
                 f'L{bx + uy * AW:.3f},{by - ux * AW:.3f} Z" fill="{INK}"/>')


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class View:
    """Urun koordinati (mm, y yukari) -> sayfa (mm, y asagi)."""

    def __init__(self, sh, ox, oy, s):
        self.sh, self.ox, self.oy, self.s = sh, ox, oy, s

    def P(self, x, y):
        return self.ox + x * self.s, self.oy - y * self.s

    def d(self, pts, closed=True):
        q = [self.P(x, y) for (x, y) in pts]
        return "M" + " L".join(f"{a:.3f},{b:.3f}" for a, b in q) + (" Z" if closed else "")

    def poly(self, pts, cls="thick", closed=True, fill=None):
        f = f' style="fill:{fill}"' if fill else ""
        self.sh.add(f'<path class="{cls}" d="{self.d(pts, closed)}"{f}/>')

    def fillpoly(self, pts, fill):
        self.sh.add(f'<path d="{self.d(pts)}" fill="{fill}" stroke="none"/>')

    _clip_n = [0]

    def begin_clip(self, pts):
        View._clip_n[0] += 1
        cid = f"cl{View._clip_n[0]}"
        self.sh.add(f'<clipPath id="{cid}"><path d="{self.d(pts)}"/></clipPath><g clip-path="url(#{cid})">')

    def end_clip(self):
        self.sh.add("</g>")

    def hatch(self, pts, pat="h45"):
        self.sh.add(f'<path d="{self.d(pts)}" fill="url(#{pat})" stroke="none"/>')

    def hatch_loops(self, loops, pat="h45"):
        """Delikli bolge taramasi (dis halka + ic halkalar, evenodd)."""
        d = " ".join(self.d(l) for l in loops)
        self.sh.add(f'<path d="{d}" fill="url(#{pat})" fill-rule="evenodd" stroke="none"/>')

    def line(self, x1, y1, x2, y2, cls="thick"):
        a, b = self.P(x1, y1)
        c, d = self.P(x2, y2)
        self.sh.line(a, b, c, d, cls)

    def rect(self, x0, y0, x1, y1, cls="thick", fill=None, r=0):
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        if r:
            pts = fillet_poly(pts, r)
        self.poly(pts, cls, True, fill)

    def circle(self, x, y, r, cls="thick", fill=None):
        cx, cy = self.P(x, y)
        f = f' style="fill:{fill}"' if fill else ""
        self.sh.add(f'<circle class="{cls}" cx="{cx:.3f}" cy="{cy:.3f}" r="{r * self.s:.3f}"{f}/>')

    def text(self, x, y, s, size=TXT, anchor="middle", weight=400, rot=0, dy=0):
        a, b = self.P(x, y)
        self.sh.text(a, b + dy, s, size, anchor, weight, rot)

    def slot(self, cx, cy, w, length, vertical, cls="thick"):
        """Kanal: w genislik, length toplam boy; vertical=True ise boy y yonunde."""
        r = w / 2
        h = max(0.0, length - w) / 2
        if vertical:
            pts = arc(cx, cy + h, r, 0, 180, 18) + arc(cx, cy - h, r, 180, 360, 18)
        else:
            pts = arc(cx + h, cy, r, -90, 90, 18) + arc(cx - h, cy, r, 90, 270, 18)
        self.poly(pts, cls)

    def hexagon(self, cx, cy, af, cls="thick", rot=0):
        r = af / math.sqrt(3)
        pts = [(cx + r * math.cos(math.radians(60 * i + rot)), cy + r * math.sin(math.radians(60 * i + rot)))
               for i in range(6)]
        self.poly(pts, cls)

    def cline_h(self, x0, x1, y):
        self.line(x0, y, x1, y, "cen")

    def cline_v(self, x, y0, y1):
        self.line(x, y0, x, y1, "cen")

    def cross(self, x, y, r):
        """Delik merkezi: zincir eksen artisi."""
        self.cline_h(x - r, x + r, y)
        self.cline_v(x, y - r, y + r)

    # --- olculer (urun koordinati; konumlar mm)
    def dim_h(self, x1, x2, y1, y2, yd, txt, below=False, txt_side=None):
        """Yatay olcu: (x1, y1) ve (x2, y2) noktalarindan yd seviyesine uzatma, ok ve yazi."""
        sh = self.sh
        X1, Y1 = self.P(x1, y1)
        X2, Y2 = self.P(x2, y2)
        _, YD = self.P(0, yd)
        for X, Y in ((X1, Y1), (X2, Y2)):
            sgn = 1 if YD > Y else -1
            if abs(YD - Y) > GAP:
                sh.line(X, Y + sgn * GAP, X, YD + sgn * OVER)
        span = abs(X2 - X1)
        tw = len(txt) * TXT * 0.52
        xa, xb = min(X1, X2), max(X1, X2)
        ty = YD + (TXT + 1.0 if below else -0.9)
        if span > 2 * AL + 1.0:
            sh.line(xa, YD, xb, YD)
            sh.arrow(xa, YD, -1, 0)
            sh.arrow(xb, YD, 1, 0)
        else:                                             # dar: oklar disarida
            sh.line(xa - AL - 3, YD, xb + AL + 3, YD)
            sh.arrow(xa, YD, 1, 0)
            sh.arrow(xb, YD, -1, 0)
        if span > tw + 2 * AL and txt_side is None:
            sh.text((xa + xb) / 2, ty, txt)
        else:
            side = txt_side or "right"
            if side == "right":
                sh.text(xb + AL + 1.2, ty, txt, anchor="start")
            else:
                sh.text(xa - AL - 1.2, ty, txt, anchor="end")

    def dim_v(self, y1, y2, x1, x2, xd, txt, left=False, txt_side=None):
        """Dikey olcu: (x1, y1) ve (x2, y2) noktalarindan xd konumuna; yazi saga okunur (-90)."""
        sh = self.sh
        X1, Y1 = self.P(x1, y1)
        X2, Y2 = self.P(x2, y2)
        XD, _ = self.P(xd, 0)
        for X, Y in ((X1, Y1), (X2, Y2)):
            sgn = 1 if XD > X else -1
            if abs(XD - X) > GAP:
                sh.line(X + sgn * GAP, Y, XD + sgn * OVER, Y)
        ya, yb = min(Y1, Y2), max(Y1, Y2)
        span = yb - ya
        tw = len(txt) * TXT * 0.52
        tx = XD - 0.9 if not left else XD - 0.9
        if span > 2 * AL + 1.0:
            sh.line(XD, ya, XD, yb)
            sh.arrow(XD, ya, 0, -1)
            sh.arrow(XD, yb, 0, 1)
        else:
            sh.line(XD, ya - AL - 3, XD, yb + AL + 3)
            sh.arrow(XD, ya, 0, 1)
            sh.arrow(XD, yb, 0, -1)
        if txt_side == "beside":
            sh.text(XD + 0.9 + TXT * 0.78, (ya + yb) / 2, txt, rot=-90)
        elif span > tw + 2 * AL and txt_side is None:
            sh.text(tx, (ya + yb) / 2, txt, rot=-90)
        else:
            side = txt_side or "top"
            if side == "top":
                sh.text(tx, ya - AL - 1.2, txt, anchor="start", rot=-90)
            else:
                sh.text(tx, yb + AL + 1.2, txt, anchor="end", rot=-90)

    def leader(self, x, y, tx, ty, txt, anchor="start", shoulder=None):
        """Isaret cizgisi: (x, y) noktasindan (tx, ty) sayfa ofsetine, omuz + yazi (urun noktasi, sayfa ofseti)."""
        sh = self.sh
        X, Y = self.P(x, y)
        TX, TY = X + tx, Y + ty
        sh.line(X, Y, TX, TY)
        tw = len(txt) * TXT * 0.53 + 1.5
        sw = shoulder if shoulder is not None else tw
        if anchor == "start":
            sh.line(TX, TY, TX + sw, TY)
            sh.text(TX + 0.8, TY - 0.9, txt, anchor="start")
        else:
            sh.line(TX - sw, TY, TX, TY)
            sh.text(TX - 0.8, TY - 0.9, txt, anchor="end")

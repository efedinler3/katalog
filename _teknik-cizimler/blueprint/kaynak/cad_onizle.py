"""3B modelden hizli onizleme: on / ust / izometrik projeksiyon (gorunur kalin, gizli kesik)."""
import sys
import time

from build123d import Compound
from PIL import Image, ImageDraw

import cad_kit as CK


def render(parts, out, views=("front", "top", "iso"), S=6.0, hidden=True, show_smooth=False):
    comp = Compound(children=[v for k, v in parts.items() if not k.startswith('_')])
    ims = []
    for v in views:
        t0 = time.time()
        vis, hid, smooth = CK.project(comp, v)
        vis = vis + (smooth if show_smooth else [])
        pts = [p for pl in vis + hid for p in pl]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        W, H = int((x1 - x0) * S) + 40, int((y1 - y0) * S) + 40
        im = Image.new("RGB", (W, H), "white")
        dr = ImageDraw.Draw(im)
        P = lambda p: (20 + (p[0] - x0) * S, 20 + (y1 - p[1]) * S)
        if hidden:
            for pl in hid:
                q = [P(p) for p in pl]
                for i in range(len(q) - 1):
                    if i % 2 == 0:
                        dr.line([q[i], q[i + 1]], fill=(150, 150, 150), width=1)
        for pl in vis:
            dr.line([P(p) for p in pl], fill="black", width=2)
        ims.append(im)
        print(v, len(vis), len(hid), f"{time.time() - t0:.1f}s")
    Wt = sum(i.width for i in ims) + 20 * len(ims)
    Ht = max(i.height for i in ims)
    c = Image.new("RGB", (Wt, Ht), "white")
    x = 0
    for i in ims:
        c.paste(i, (x, 0))
        x += i.width + 20
    c.thumbnail((2600, 2600))
    c.save(out, quality=90)


if __name__ == "__main__":
    import cad_kopru
    render(cad_kopru.model(), sys.argv[1])

"""CAD kiti (build123d / OpenCASCADE): yuvarlatilmis profiller, bukulmus sac, baglanti elemanlari, projeksiyon.

Profil koordinatlari (u, v) = (x, z) mm; prism_xz profili XZ duzleminde Y boyunca ortalanmis olarak uzatir.
"""
import math

from build123d import (Axis, Edge, Face, Location, Plane, Pos, Rot, Solid, Vector, Wire, extrude, Cylinder,
                       Box, RegularPolygon, Text, Align, Compound, Sketch, Circle, SlotCenterToCenter)


def _fillet_geom(p0, p1, p2, r):
    """p1 kosesinde r yaricapli yay: (teget1, orta, teget2) ya da None."""
    v1 = (p0[0] - p1[0], p0[1] - p1[1])
    v2 = (p2[0] - p1[0], p2[1] - p1[1])
    l1, l2 = math.hypot(*v1), math.hypot(*v2)
    u1, u2 = (v1[0] / l1, v1[1] / l1), (v2[0] / l2, v2[1] / l2)
    cosang = max(-1.0, min(1.0, u1[0] * u2[0] + u1[1] * u2[1]))
    ang = math.acos(cosang)
    if r <= 0 or ang < 1e-4 or abs(ang - math.pi) < 1e-4:
        return None
    t = r / math.tan(ang / 2)
    t = min(t, l1 * 0.999, l2 * 0.999)
    r = t * math.tan(ang / 2)
    a = (p1[0] + u1[0] * t, p1[1] + u1[1] * t)
    b = (p1[0] + u2[0] * t, p1[1] + u2[1] * t)
    bis = (u1[0] + u2[0], u1[1] + u2[1])
    bl = math.hypot(*bis)
    d = r / math.sin(ang / 2)
    c = (p1[0] + bis[0] / bl * d, p1[1] + bis[1] / bl * d)
    m = (c[0] - bis[0] / bl * r, c[1] - bis[1] / bl * r)
    return a, m, b


def rounded_wire(pts, radii, closed=True):
    """Kose yaricapli cokgen -> Line + ThreePointArc kenarli Wire (XY duzleminde)."""
    n = len(pts)
    radii = radii if isinstance(radii, (list, tuple)) else [radii] * n
    segs = []                                   # (baslangic, bitis) veya yay
    corners = []
    for i in range(n):
        if not closed and (i == 0 or i == n - 1):
            corners.append(None)
            continue
        corners.append(_fillet_geom(pts[i - 1], pts[i], pts[(i + 1) % n], radii[i]))
    edges = []
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        j = (i + 1) % n
        start = corners[i][2] if corners[i] else pts[i]
        end = corners[j][0] if corners[j] else pts[j]
        if math.hypot(end[0] - start[0], end[1] - start[1]) > 1e-6:
            edges.append(Edge.make_line(Vector(*start, 0), Vector(*end, 0)))
        if corners[j] and (closed or j != n - 1):
            a, m, b = corners[j]
            edges.append(Edge.make_three_point_arc(Vector(*a, 0), Vector(*m, 0), Vector(*b, 0)))
    return Wire(edges)


def rounded_face(pts, radii):
    return Face(rounded_wire(pts, radii, True))


def _isect(p, d, q, e):
    den = d[0] * e[1] - d[1] * e[0]
    if abs(den) < 1e-12:
        return None
    t = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den
    return (p[0] + d[0] * t, p[1] + d[1] * t)


def band_pts(center, radii, t):
    """Acik merkez cizgisi + kose yaricaplari -> kalinlik t'lik kapali sac profili (noktalar, yaricaplar)."""
    n = len(center)
    dirs = []
    for i in range(n - 1):
        dx, dy = center[i + 1][0] - center[i][0], center[i + 1][1] - center[i][1]
        l = math.hypot(dx, dy)
        dirs.append((dx / l, dy / l))
    sides = {}
    for side in (1, -1):
        pts, rr = [], []
        for i in range(n):
            if i == 0:
                d = dirs[0]
                nx, ny = -d[1] * side, d[0] * side
                pts.append((center[0][0] + nx * t / 2, center[0][1] + ny * t / 2))
                rr.append(0)
            elif i == n - 1:
                d = dirs[-1]
                nx, ny = -d[1] * side, d[0] * side
                pts.append((center[-1][0] + nx * t / 2, center[-1][1] + ny * t / 2))
                rr.append(0)
            else:
                d0, d1 = dirs[i - 1], dirs[i]
                n0 = (-d0[1] * side, d0[0] * side)
                n1 = (-d1[1] * side, d1[0] * side)
                p0 = (center[i][0] + n0[0] * t / 2, center[i][1] + n0[1] * t / 2)
                p1 = (center[i][0] + n1[0] * t / 2, center[i][1] + n1[1] * t / 2)
                x = _isect(p0, d0, p1, d1) or p0
                pts.append(x)
                turn = d0[0] * d1[1] - d0[1] * d1[0]           # >0 sola donus
                inside = (turn > 0) == (side > 0)
                rr.append(max(0.3, radii[i] - t / 2) if inside else radii[i] + t / 2)
        sides[side] = (pts, rr)
    a_pts, a_r = sides[1]
    b_pts, b_r = sides[-1]
    return a_pts + list(reversed(b_pts)), a_r + list(reversed(b_r))


def band_face(center, radii, t):
    pts, rr = band_pts(center, radii, t)
    return rounded_face(pts, rr)


def prism_xz(face, depth, y0=None):
    """XY'de cizilmis profili (x, y=z) dunya XZ'sine cevirip Y boyunca depth kadar (ortali) uzatir."""
    sol = extrude(face, amount=depth)
    sol = Rot(90, 0, 0) * sol                 # profil y -> dunya z, uzatma -> dunya Y
    bb = sol.bounding_box()
    off = -(bb.min.Y + bb.max.Y) / 2 if y0 is None else y0 - bb.min.Y
    return Pos(0, off, 0) * sol


def hex_nut(af, h, d, z0=0.0, x=0.0, y=0.0):
    """Pahli altigen somun (30 derece pah, koni kesisimi): eksen Z, alti z0."""
    rc = af / math.sqrt(3)
    hexp = extrude(RegularPolygon(rc, 6, rotation=0), amount=h)
    ch = (rc - af / 2) * 1.05
    prof = rounded_face([(0, 0), (rc + ch * 0.2 - ch, 0), (rc + 0.01, ch * math.tan(math.radians(30))),
                         (rc + 0.01, h - ch * math.tan(math.radians(30))), (rc + ch * 0.2 - ch, h), (0, h)], 0)
    cone = Solid.revolve(prof, 360, Axis.Y)
    cone = Rot(90, 0, 0) * cone
    cone = Rot(0, 0, 0) * cone
    nut = hexp & cone
    hole = Cylinder(d / 2, h * 3)
    nut = nut - hole
    return Pos(x, y, z0) * nut


def washer3d(od, idd, t, z0=0.0):
    w = Cylinder(od / 2, t, align=(Align.CENTER, Align.CENTER, Align.MIN)) - Cylinder(idd / 2, t * 3)
    return Pos(0, 0, z0) * w


def stud3d(d, z0, z1, ch=1.0, tip=None):
    L = z1 - z0
    s = Cylinder(d / 2, L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    s = s.chamfer(ch, None, s.edges().group_by(Axis.Z)[-1]) if ch else s
    return Pos(0, 0, z0) * s


def project(shape, view, n_curve=40):
    """view: 'front' (-Y'den bakis, x sag, z yukari), 'top' (+Z'den, x sag, y yukari), 'iso'.
    Donus: (gorunur, gizli) polilineler [[(u, v), ...], ...]."""
    if view == "front":
        org, up = (0, -1000, 0), (0, 0, 1)
    elif view == "top":
        org, up = (0, 0, 1000), (0, 1, 0)
    elif view == "right":
        org, up = (1000, 0, 0), (0, 0, 1)
    else:
        org, up = (700, -1000, 650), (0, 0, 1)
    vis, hid, smooth = hlr(shape, org, up)

    def pl(edges):
        out = []
        for e in edges:
            gt = str(e.geom_type)
            m = 2 if "LINE" in gt else max(6, int(e.length / 1.2))
            m = min(m, 160)
            try:
                pts = [e.position_at(i / (m - 1)) for i in range(m)]
            except Exception:                         # bozuk/cok kisa HLR kenari: parametreyle ornekle
                try:
                    from build123d import PositionMode
                    pts = [e.position_at(i / (m - 1), PositionMode.PARAMETER) for i in range(m)]
                except Exception:
                    continue
            out.append([(p.X, p.Y) for p in pts])
        return out
    return pl(vis), pl(hid), pl(smooth)


def hlr(shape, viewport_origin, viewport_up, look_at=(0, 0, 0), ang_tol=0.12):
    """Gizli cizgi kaldirma: (gorunur keskin + dis hat, gizli, gorunur teget/yumusak) kenarlar ayri."""
    from OCP.BRepLib import BRepLib
    from OCP.gp import gp_Ax1, gp_Ax2
    from OCP.HLRAlgo import HLRAlgo_Projector
    from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
    from OCP.TopAbs import TopAbs_ShapeEnum
    from OCP.TopExp import TopExp_Explorer
    from build123d.topology import Edge as BEdge
    from build123d.topology.shape_core import downcast

    def ext(c):
        out = []
        if c.IsNull():
            return out
        ex = TopExp_Explorer(c, TopAbs_ShapeEnum.TopAbs_EDGE)
        while ex.More():
            e = downcast(ex.Current())
            BRepLib.BuildCurves3d_s(e, 1e-5)
            out.append(BEdge(e))
            ex.Next()
        return out
    BRepLib.EncodeRegularity_s(shape.wrapped, ang_tol)    # teget-surekli dikisler -> Rg1 (yumusak) kenar
    algo = HLRBRep_Algo()
    algo.Add(shape.wrapped)
    o, la, upv = Vector(viewport_origin), Vector(look_at), Vector(viewport_up).normalized()
    d = (o - la).normalized()
    ax = gp_Ax2()
    ax.SetAxis(gp_Ax1(o.to_pnt(), d.to_dir()))
    ax.SetYDirection(upv.to_dir())
    algo.Projector(HLRAlgo_Projector(ax))
    algo.Update()
    algo.Hide()
    h = HLRBRep_HLRToShape(algo)
    vis = ext(h.VCompound()) + ext(h.OutLineVCompound())
    smooth = ext(h.Rg1LineVCompound())
    hid = ext(h.HCompound()) + ext(h.OutLineHCompound())
    return vis, hid, smooth


def _wire_pts(w):
    """Kapali teli sirali kenarlarla (yonleri dikkate alarak) (x, z) noktalarina cevirir."""
    from OCP.BRepTools import BRepTools_WireExplorer
    from OCP.TopAbs import TopAbs_REVERSED
    from build123d.topology import Edge as BEdge
    pts = []
    ex = BRepTools_WireExplorer(w.wrapped)
    while ex.More():
        e = BEdge(ex.Current())
        m = 2 if "LINE" in str(e.geom_type) else max(6, min(120, int(e.length / 0.6)))
        ts = [i / (m - 1) for i in range(m)]
        if ex.Current().Orientation() == TopAbs_REVERSED:
            ts = ts[::-1]
        pts += [(q.X, q.Z) for q in (e.position_at(t) for t in ts)]
        ex.Next()
    return pts


def section_loops(part, y=0.0, n=160):
    """Parcanin y duzlemindeki kesit yuzleri (normal +-Y): [[dis halka, ic halkalar...], ...] (x, z) polilineleri."""
    out = []
    for fc in part.faces():
        try:
            nrm, c = fc.normal_at(), fc.center()
        except Exception:
            continue
        if abs(abs(nrm.Y) - 1) > 1e-6 or abs(c.Y - y) > 1e-3:
            continue
        loops = []
        for w in [fc.outer_wire()] + list(fc.inner_wires()):
            loops.append(_wire_pts(w))
        out.append(loops)
    return out

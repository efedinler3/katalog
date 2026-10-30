"""Blender Cycles: CAD STL parcalari -> fotogercekci, arka plansiz PNG.
blender -b -P render_blender.py -- <kod> <finish: black|cast|alu|stainless> <stud: zinc|brass> <view: top|front> <cikti.png> [ornek]
Dokular: ambientCG (CC0), HDRI: Poly Haven studio_small_09 (CC0).
"""
import json
import math
import os
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
code, finish, stud, view, out = argv[:5]
samples = int(argv[5]) if len(argv) > 5 else 160
HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "tex")

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = samples
sc.cycles.use_denoising = True
sc.cycles.use_adaptive_sampling = True
sc.cycles.adaptive_threshold = 0.008
sc.cycles.max_bounces = 10
sc.cycles.glossy_bounces = 6
sc.cycles.caustics_reflective = False
sc.cycles.denoiser = "OPENIMAGEDENOISE"
sc.render.film_transparent = True
sc.render.resolution_x, sc.render.resolution_y = 2200, 1350
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGBA"
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Medium High Contrast"

# --- dunya: stüdyo HDRI
w = bpy.data.worlds.new("W")
sc.world = w
w.use_nodes = True
nt = w.node_tree
env = nt.nodes.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(os.path.join(TEX, "studio.hdr"))
mp = nt.nodes.new("ShaderNodeMapping")
tc = nt.nodes.new("ShaderNodeTexCoord")
mp.inputs["Rotation"].default_value = (0, 0, math.radians(35))
nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
bg = nt.nodes["Background"]
bg.inputs["Strength"].default_value = 1.0
nt.links.new(env.outputs["Color"], bg.inputs["Color"])


def img(name, kind, colorspace):
    p = os.path.join(TEX, name, f"{name}_1K-JPG_{kind}.jpg")
    im = bpy.data.images.load(p, check_existing=True)
    im.colorspace_settings.name = colorspace
    return im


def material(mname, texset, base, rough, metal, coat=0.0, coat_r=0.3, scale=0.02, bump=0.4, bevel=0.6, peel=0.08, smudge=0.12, aniso=0.0):
    m = bpy.data.materials.new(mname)
    m.use_nodes = True
    n = m.node_tree.nodes
    L = m.node_tree.links
    bs = n["Principled BSDF"]
    tco = n.new("ShaderNodeTexCoord")
    mp_ = n.new("ShaderNodeMapping")
    mp_.inputs["Scale"].default_value = (scale, scale, scale)
    L.new(tco.outputs["Object"], mp_.inputs["Vector"])

    def tex(kind, cs):
        t = n.new("ShaderNodeTexImage")
        t.image = img(texset, kind, cs)
        t.projection = "BOX"
        t.projection_blend = 0.3
        L.new(mp_.outputs["Vector"], t.inputs["Vector"])
        return t

    col = tex("Color", "sRGB")
    mix = n.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 1.0
    mix.inputs[7].default_value = (*base, 1)
    L.new(col.outputs["Color"], mix.inputs[6])
    L.new(mix.outputs[2], bs.inputs["Base Color"])
    rt = tex("Roughness", "Non-Color")
    rm = n.new("ShaderNodeMapRange")
    rm.inputs["To Min"].default_value = rough * 0.75
    rm.inputs["To Max"].default_value = min(1.0, rough * 1.25)
    L.new(rt.outputs["Color"], rm.inputs["Value"])
    L.new(rm.outputs["Result"], bs.inputs["Roughness"])
    bs.inputs["Metallic"].default_value = metal
    nm = tex("NormalGL", "Non-Color")
    nmap = n.new("ShaderNodeNormalMap")
    nmap.inputs["Strength"].default_value = bump
    L.new(nm.outputs["Color"], nmap.inputs["Color"])
    # portakal kabugu (ince kabarti) + leke/parmak izi (purtuzluluk dalgalanmasi)
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900.0; nz.inputs["Detail"].default_value = 4.0
    L.new(tco.outputs["Object"], nz.inputs["Vector"])
    bmp = n.new("ShaderNodeBump"); bmp.inputs["Strength"].default_value = peel; bmp.inputs["Distance"].default_value = 0.02
    L.new(nz.outputs["Fac"], bmp.inputs["Height"])
    sm = n.new("ShaderNodeTexNoise"); sm.inputs["Scale"].default_value = 18.0; sm.inputs["Detail"].default_value = 6.0
    sm.inputs["Roughness"].default_value = 0.7
    L.new(tco.outputs["Object"], sm.inputs["Vector"])
    smr = n.new("ShaderNodeMapRange"); smr.inputs["From Min"].default_value = 0.45; smr.inputs["From Max"].default_value = 0.75
    smr.inputs["To Min"].default_value = 0.0; smr.inputs["To Max"].default_value = smudge
    L.new(sm.outputs["Fac"], smr.inputs["Value"])
    add = n.new("ShaderNodeMath"); add.operation = "ADD"; add.use_clamp = True
    L.new(rm.outputs["Result"], add.inputs[0]); L.new(smr.outputs["Result"], add.inputs[1])
    L.new(add.outputs["Value"], bs.inputs["Roughness"])
    bev = n.new("ShaderNodeBevel")                  # ince kenar parlamasi (gercek pah etkisi)
    bev.inputs["Radius"].default_value = bevel
    L.new(nmap.outputs["Normal"], bmp.inputs["Normal"])
    L.new(bmp.outputs["Normal"], bev.inputs["Normal"])
    L.new(bev.outputs["Normal"], bs.inputs["Normal"])
    if aniso:
        bs.inputs["Anisotropic"].default_value = aniso
    if coat:
        bs.inputs["Coat Weight"].default_value = coat
        bs.inputs["Coat Roughness"].default_value = coat_r
    return m


MAT = {
    "black": lambda: material("black", "Rubber004", (0.16, 0.16, 0.17), 0.55, 0.0, coat=0.6, coat_r=0.35, bump=0.25),
    "cast": lambda: material("cast", "Rubber004", (0.17, 0.17, 0.18), 0.75, 0.05, coat=0.2, coat_r=0.6, bump=0.9),
    "alu": lambda: material("alu", "Metal032", (0.85, 0.86, 0.87), 0.55, 0.9, bump=0.9, scale=0.03),
    "stainless": lambda: material("stainless", "Metal009", (1, 1, 1), 0.28, 1.0, bump=0.25, scale=0.02),
}
M_FIN = MAT[finish]()
M_RUB = material("rubber", "Rubber004", (0.11, 0.11, 0.115), 0.85, 0.0, bump=0.7, bevel=0.8, peel=0.15, smudge=0.05)
M_ZINC = material("zinc", "Metal032", (0.93, 0.94, 0.95), 0.26, 1.0, bump=0.3, scale=0.05, bevel=0.35, peel=0.02, smudge=0.18, aniso=0.5)
M_BRASS = material("brass", "Metal009", (0.85, 0.62, 0.38), 0.35, 1.0, bump=0.2, scale=0.05, bevel=0.3)


def mat_for(name):
    import re
    if re.search(r"rubber|marks|core|pad|block|body_r|dome", name, re.I):
        return M_RUB
    if name == "washer" and code.startswith("VV"):          # VV: buyuk ust pul govdenin siyah kapagi
        return M_FIN
    if re.search(r"fasten|nut|stud|washer|bolt|thread", name, re.I):
        return M_BRASS if stud == "brass" else M_ZINC
    return M_FIN


# --- parcalar
d = os.path.join(HERE, code)
names = json.load(open(os.path.join(d, "parts.json"), encoding="utf-8"))
objs = []
for nm in names:
    bpy.ops.wm.stl_import(filepath=os.path.join(d, f"{nm}.stl"))
    o = bpy.context.selected_objects[0]
    o.name = nm
    o.data.materials.append(mat_for(nm))
    bpy.ops.object.shade_auto_smooth(angle=math.radians(30))
    objs.append(o)

import mathutils  # noqa: E402

mn = mathutils.Vector((1e9, 1e9, 1e9))
mx = -mn
for o in objs:
    for v in o.bound_box:
        p = o.matrix_world @ mathutils.Vector(v)
        mn = mathutils.Vector(map(min, mn, p))
        mx = mathutils.Vector(map(max, mx, p))
ctr = (mn + mx) / 2
size = mx - mn
for o in objs:
    o.location -= ctr
zmin = mn.z - ctr.z

# --- golge yakalayici zemin
bpy.ops.mesh.primitive_plane_add(size=4000, location=(0, 0, zmin - 0.05))
gp = bpy.context.active_object
gp.is_shadow_catcher = True
gp.hide_render = True

# --- isiklar: buyuk yumusak ust kutu isik + yan dolgu
bpy.ops.object.light_add(type="AREA", location=(-0.35 * size.x, 0.25 * size.y, size.z + 3 * max(size.x, size.y)))
k = bpy.context.active_object
k.data.shape = "RECTANGLE"; k.data.size = 1.2 * max(size.x, size.y); k.data.size_y = 0.6 * max(size.x, size.y)
k.data.energy = 9.0e5
k.rotation_euler = (math.radians(8), math.radians(-6), 0)
bpy.ops.object.light_add(type="AREA", location=(1.2 * size.x, -1.0 * size.y, size.z + max(size.x, size.y)))
f = bpy.context.active_object
f.data.size = max(size.x, size.y)
f.data.energy = 2.5e5
f.rotation_euler = (math.radians(45), math.radians(35), 0)

# --- kamera: uzun odak, tam tepeden (ya da tam karsidan)
cam_data = bpy.data.cameras.new("C")
cam_data.lens = 135
cam = bpy.data.objects.new("C", cam_data)
sc.collection.objects.link(cam)
sc.camera = cam
aspect = sc.render.resolution_x / sc.render.resolution_y
fov = 2 * math.atan(36 / 2 / cam_data.lens)
if view == "top":
    span = max(size.x / aspect, size.y) * 1.12
    dist = span / 2 / math.tan(fov / 2) * aspect ** 0 + size.z
    cam.location = (0, 0, dist)
    cam.rotation_euler = (0, 0, 0)
else:
    span = max(size.x / aspect, size.z) * 1.12
    dist = span / 2 / math.tan(fov / 2) + size.y
    cam.location = (0, -dist, 0)
    cam.rotation_euler = (math.radians(90), 0, 0)
cam_data.clip_end = dist * 4
cam_data.sensor_fit = "VERTICAL"
cam_data.sensor_width = 36 * aspect

sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print("YAZILDI", out)

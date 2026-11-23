"""The installed NVC face (design §5, maqueta v4 + 2026-11-23 changes) rendered in 3D.

  python art/blender/make_prints.py
  blender -b -P art/blender/current.py -- <out.png> [samples] [hands]

Without "hands" it renders the background only (what the watch face draws under its dynamic
layers); with "hands" it adds 3D hands at 10:08:32 to judge the overall look.
Geometry follows art/render_bg.py (watch px, origin at the centre, y down).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import watchkit as wk  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = Path(argv[0]) if argv else wk.ROOT / "docs/mockup/propuestas/actual_3d.png"
SAMPLES = int(argv[1]) if len(argv) > 1 else 192
HANDS = len(argv) > 2 and argv[2] == "hands"

wk.setup(SAMPLES, world_strength=0.8, key_energy=16000)

GOLD = wk.simple("gold", **{"Base Color": (0.95, 0.77, 0.46, 1), "Metallic": 1.0, "Roughness": 0.34})
GOLD_POL = wk.simple("gold_pol", **{"Base Color": (0.97, 0.79, 0.48, 1), "Metallic": 1.0, "Roughness": 0.24})
BLACK = wk.simple("black", **{"Base Color": (0.01, 0.01, 0.012, 1), "Roughness": 0.4})
WIN_FLOOR = wk.simple("win_floor", **{"Base Color": (0.018, 0.018, 0.02, 1), "Roughness": 0.45})
WHITE = wk.simple("white", **{"Base Color": (0.90, 0.89, 0.86, 1), "Metallic": 0.6, "Roughness": 0.25})

BEZEL = wk.finish_material("bezel", {"Base Color": (0.42, 0.42, 0.44, 1), "Metallic": 1.0, "Roughness": 0.32,
                                     "Anisotropic": 0.85}, radial_tangent=True)
# ---- dial: one dense grid displaced by the height map (real milled walls, sunk sub-dials and
# windows), materials split by projected masks
import bpy  # noqa: E402


def dial_material():
    mat = bpy.data.materials.new("dial")
    n, l = wk.nodes_of(mat)
    out = n.new("ShaderNodeOutputMaterial")
    satin = wk.principled(n, **{"Base Color": (0.028, 0.028, 0.032, 1), "Metallic": 0.5, "Roughness": 0.27,
                                "Coat Weight": 0.3, "Coat Roughness": 0.08})
    # milled floor: bead-blasted, lighter than the satin ocean (2026-11-23: the map must read)
    blast = wk.principled(n, **{"Base Color": (0.10, 0.10, 0.105, 1), "Metallic": 0.55, "Roughness": 0.6})
    snail = wk.principled(n, **{"Base Color": (0.075, 0.075, 0.08, 1), "Metallic": 0.85, "Roughness": 0.22})
    hole = wk.principled(n, **{"Base Color": (0.015, 0.015, 0.017, 1), "Roughness": 0.5})
    sn = wk.projected(n, l, wk.BUILD / "current_snail.png", "Non-Color")
    bump = n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.8
    bump.inputs["Distance"].default_value = 0.02
    l.new(sn.outputs["Color"], bump.inputs["Height"])
    l.new(bump.outputs["Normal"], snail.inputs["Normal"])
    shader = satin.outputs["BSDF"]
    for mask, other in (("current_land.png", blast), ("current_wells.png", snail), ("current_windows.png", hole)):
        m = wk.projected(n, l, wk.BUILD / mask, "Non-Color")
        mx = n.new("ShaderNodeMixShader")
        l.new(m.outputs["Color"], mx.inputs["Fac"])
        l.new(shader, mx.inputs[1])
        l.new(other.outputs["BSDF"], mx.inputs[2])
        shader = mx.outputs["Shader"]
    l.new(shader, out.inputs["Surface"])
    return mat


bpy.ops.mesh.primitive_grid_add(x_subdivisions=1400, y_subdivisions=1400, size=wk.SIZE, location=(0, 0, 0))
dial = bpy.context.active_object
dial.name = "dial"
tex = bpy.data.textures.new("height", "IMAGE")
tex.image = bpy.data.images.load(str(wk.BUILD / "current_height.png"))
tex.image.colorspace_settings.name = "Non-Color"
tex.extension = "EXTEND"
disp = dial.modifiers.new("milling", "DISPLACE")
disp.texture = tex
disp.texture_coords = "UV"
disp.direction = "Z"
disp.mid_level = 1.0
disp.strength = 0.6
bpy.ops.object.shade_smooth()
dial.data.materials.append(dial_material())

# bezel
wk.lathe("bezel", [(220.6, 0.05), (221.3, 0.45), (223.5, 0.70), (229.5, 0.66), (232.6, 0.35), (233, 0.0),
                   (233, -1.0)], BEZEL)

CENTER = (0.0, 112.0, 50.0, 52.4)   # must match art/render_bg.py
SIDES = [(-82.0, 86.0, 41.0, 43.2), (82.0, 86.0, 41.0, 43.2)]
# gold rims. The centre dial sits on top (design §5.3): its rim is whole and the side rims stop
# against it, so nothing of the side dials shows inside the centre one (user, 2026-11-23).
cx_, cy_, r_, ro_ = CENTER
for i, (x, y, r, ro) in enumerate(SIDES):
    rim = wk.torus(f"rim{i}", x, y, (r + ro) / 2, (ro - r) / 20 + 0.03, 0.0, GOLD_POL)
    wk.boolean_cut(rim, wk.cylinder(f"rim_cut{i}", cx_, cy_, ro_ + 0.6, -2, 2, BLACK))
wk.torus("rim_centre", cx_, cy_, (r_ + ro_) / 2, (ro_ - r_) / 20 + 0.03, 0.05, GOLD_POL)

for i, (x, y) in enumerate([(138.0, 0.0), (-138.0, 0.0)]):
    fr = wk.box(f"win_frame{i}", x, y, 69.2, 31.2, -0.02, 0.08, 0, GOLD, bevel=0.04)  # window 66x28 + 1.6 frame
    wk.boolean_cut(fr, wk.box(f"cut_frame{i}", x, y, 66, 28, -1, 1, 0, BLACK, bevel=0))

# gold indices: double bars at 12, 3, 6 and 9; single bars elsewhere
for h in range(12):
    deg = h * 30
    if h % 3 == 0:
        for off in (-1.9, 1.9):
            a = math.radians(deg)
            ox, oy = off * math.cos(a), off * math.sin(a)
            rm = 203
            wk.box(f"idx{h}{off}", rm * math.sin(a) + ox, -rm * math.cos(a) + oy, 2.3, 18, 0.0, 0.22, deg, GOLD,
                   bevel=0.025)
    else:
        wk.radial_box(f"idx{h}", deg, 197, 212, 2.6, 0.0, 0.22, GOLD, bevel=0.025)

wk.logo(0, -123, 72, 0.05, wk.logo_material(gold=(0.95, 0.77, 0.46, 1), roughness=0.18))

if HANDS:
    hd, md, sd = wk.hand_angles((10, 8, 32))
    wk.hand("hour", hd, 11.7, 1.6, 1.1, 0.25, 0.45, 0.10, GOLD_POL)
    wk.hand("minute", md, 17.7, 2.0, 0.8, 0.18, 0.60, 0.09, GOLD_POL)
    wk.hand("second", sd, 18.9, 2.9, 0.16, 0.10, 0.78, 0.02, WHITE)
    a = math.radians(sd + 180)
    wk.torus("sec_ring", 33 * math.sin(a), -33 * math.cos(a), 4.2, 0.06, 0.79, WHITE)
    wk.cylinder("cap", 0, 0, 7.0, 0.80, 0.92, GOLD_POL, verts=64)
    wk.cylinder("cap_in", 0, 0, 5.2, 0.92, 0.95, BLACK, verts=64)

wk.render(OUT)

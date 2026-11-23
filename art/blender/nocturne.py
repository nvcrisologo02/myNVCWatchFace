"""NVC Nocturne: dress watch designed from scratch around the "NVC zZz" (sleep) logo.

Gold case, midnight-blue clous de Paris dial, moon phase, Breguet hands, retrograde glucose fan.

  python art/blender/make_prints.py
  blender -b -P art/blender/nocturne.py -- <out.png> [samples] [bg]

With "bg" it renders the production background (design 2026-11-23-nocturne §6): transparent film,
so the moon aperture is a hole (alpha 0) through which the watch face shows the turning moon disc;
no hands, no crystal and none of the dynamic content.
"""
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import watchkit as wk  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = Path(argv[0]) if argv else wk.ROOT / "docs/mockup/propuestas/nocturne_3d.png"
SAMPLES = int(argv[1]) if len(argv) > 1 else 192
BG = len(argv) > 2 and argv[2] == "bg"
TIME, GLUCOSE, BATTERY, DAY = (10, 8, 32), 112, 76, 23
PRINT = wk.BUILD / ("nocturne_print_bg.png" if BG else "nocturne_print.png")

wk.setup(SAMPLES, world_strength=0.8, key_energy=16000)
if BG:
    wk.scene.render.film_transparent = True

GOLD_POL = wk.simple("gold_polished", **{"Base Color": (1.0, 0.78, 0.42, 1), "Metallic": 1.0, "Roughness": 0.14})
GOLD_HAND = wk.simple("gold_hand", **{"Base Color": (1.0, 0.82, 0.50, 1), "Metallic": 1.0, "Roughness": 0.32})
GOLD_MOON = wk.simple("gold_moon", **{"Base Color": (1.0, 0.80, 0.45, 1), "Metallic": 1.0, "Roughness": 0.45})
BLUED = wk.simple("blued_steel", **{"Base Color": (0.10, 0.20, 0.75, 1), "Metallic": 1.0, "Roughness": 0.18})
DATE_DISC = wk.simple("date_disc", **{"Base Color": (0.93, 0.91, 0.85, 1), "Roughness": 0.5,
                                      "Emission Color": (1, 0.98, 0.94, 1), "Emission Strength": 0.35})
NAVY_INK = wk.simple("navy_ink", **{"Base Color": (0.02, 0.04, 0.12, 1), "Roughness": 0.4})
GLUC_TXT = wk.simple("gluc_txt", **{"Base Color": (0.85, 0.70, 0.42, 1), "Roughness": 0.4,
                                    "Emission Color": (0.85, 0.70, 0.42, 1), "Emission Strength": 0.18})
GLASS = wk.simple("crystal", **{"Roughness": 0.0, "Transmission Weight": 1.0, "IOR": 1.77})
NAVY = (0.015, 0.045, 0.20, 1)

DIAL = wk.finish_material("dial", {"Base Color": NAVY, "Metallic": 0.35, "Roughness": 0.35, "Coat Weight": 0.5,
                                   "Coat Roughness": 0.05}, PRINT,
                          height=wk.BUILD / "nocturne_guilloche.png", height_strength=1.0, height_distance=0.08)
SKY = wk.projected_color_material("sky", wk.BUILD / "nocturne_sky.png", {"Roughness": 0.35, "Coat Weight": 0.5})

# polished gold case: rounded bezel
wk.lathe("bezel", [(212.6, 0.25), (213.4, 0.9), (216, 1.35), (222, 1.55), (229, 1.35), (232.4, 0.8), (233, 0.2),
                   (233, -1.0)], GOLD_POL)

dial = wk.cylinder("dial", 0, 0, 212.8, -0.3, 0.0, DIAL, verts=256)
wk.torus("chapter_edge", 0, 0, 150, 0.06, 0.0, GOLD_POL)

# moon phase at 12: semicircular aperture (r 34) with the two classic "humps" that hide the moons
# at new moon. Moons ride the disc at r 20 from its centre, which is the aperture centre.
MX, MY, MR = 0, -92, 34
HUMP_X, HUMP_R = 20, 12.5
cut = wk.cylinder("cut_moon", MX, MY, MR, -1, 1, NAVY_INK)
for nm, obj in [("half", wk.box("cut_moon_half", MX, MY + 20, 80, 40, -2, 2, 0, NAVY_INK, bevel=0)),
                ("hump_l", wk.cylinder("hump_l", MX - HUMP_X, MY, HUMP_R, -2, 2, NAVY_INK)),
                ("hump_r", wk.cylinder("hump_r", MX + HUMP_X, MY, HUMP_R, -2, 2, NAVY_INK))]:
    md = cut.modifiers.new(nm, "BOOLEAN")
    md.operation = "DIFFERENCE"
    md.object = obj
    md.solver = "EXACT"
    obj.hide_render = True
wk.boolean_cut(dial, cut)
arch = wk.torus("moon_rim", MX, MY, MR + 0.8, 0.08, 0.0, GOLD_POL)
wk.boolean_cut(arch, wk.box("rim_cut", MX, MY + 20, 80, 40, -2, 2, 0, NAVY_INK, bevel=0))
for side in (-1, 1):  # gold edge on each hump
    hr = wk.torus(f"hump_rim{side}", MX + side * HUMP_X, MY, HUMP_R + 0.6, 0.06, 0.0, GOLD_POL)
    wk.boolean_cut(hr, wk.box(f"hump_rim_cut{side}", MX + side * HUMP_X, MY + 20, 40, 40, -2, 2, 0, NAVY_INK,
                              bevel=0))
if not BG:  # sketch only: in the watch face the disc is a separate, turning layer under the dial
    wk.cylinder("sky", MX, MY, 40, -0.9, -0.6, SKY)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.1, location=(*wk.W(MX, MY - 20), -0.6))
    moon = bpy.context.active_object
    moon.scale = (1, 1, 0.35)
    moon.data.materials.append(GOLD_MOON)
    for p in moon.data.polygons:
        p.use_smooth = True

wk.logo(0, -42, 54, 0.04, wk.logo_material(gold=(0.95, 0.76, 0.44, 1), roughness=0.2))

# sub-dials 9 (activity + reserve) and 3 (weather): recessed, snailed, gold rims
for x, nm in [(-90, "activity"), (90, "weather")]:
    wk.boolean_cut(dial, wk.cylinder("cut_" + nm, x, 8, 36, -1, 1, NAVY_INK))
    wk.cylinder("floor_" + nm, x, 8, 36.5, -0.45, -0.25, wk.snail_material(
        "floor_" + nm, {"Base Color": (0.01, 0.022, 0.07, 1), "Metallic": 0.5, "Roughness": 0.3}, PRINT, scale=22))
    wk.torus("rim_" + nm, x, 8, 36.8, 0.08, 0.0, GOLD_POL)

# date at 6 in the chapter ring
wk.boolean_cut(dial, wk.box("cut_date", 0, 178, 22, 16, -1, 1, 0, NAVY_INK, bevel=0))
df = wk.box("date_frame", 0, 178, 25, 19, -0.02, 0.05, 0, GOLD_POL, bevel=0.02)
wk.boolean_cut(df, wk.box("cut_date_frame", 0, 178, 22, 16, -1, 1, 0, NAVY_INK, bevel=0))
wk.cylinder("date_disc", 0, 178, 16, -0.7, -0.6, DATE_DISC)


def f2deg(v):
    return 240 - 120 * (min(max(v, 40), 300) - 40) / 260


if not BG:
    wk.text_obj("date_num", str(DAY), wk.BODONI, 13, 0, 178, -0.585, NAVY_INK)
    wk.text_obj("gval", str(GLUCOSE), wk.BODONI, 20, 0, 132, 0.01, GLUC_TXT)
    wk.text_obj("gtrend", "→", wk.SYMBOLS, 14, 26, 133, 0.01, GLUC_TXT)
    wk.hand("reserve", -60 + 1.2 * BATTERY, 2.5, 0.4, 0.18, 0.06, -0.2, 0.04, GOLD_HAND, pivot=(-90, 8))
    wk.cylinder("rcap", -90, 8, 2.2, -0.2, -0.1, GOLD_HAND, verts=48)
    wk.hand("gneedle", f2deg(GLUCOSE), 7.1, 0.8, 0.22, 0.06, 0.05, 0.04, BLUED, pivot=(0, 40))
    wk.cylinder("gcap", 0, 40, 3.2, 0.05, 0.14, BLUED, verts=48)
    hd, md_, sd = wk.hand_angles(TIME)
    wk.breguet_hand("hour", hd, 11.2, 0.42, 8.2, 0.75, 0.16, 0.45, 0.08, GOLD_HAND)
    wk.breguet_hand("minute", md_, 17.2, 0.32, 14.0, 0.65, 0.15, 0.62, 0.07, GOLD_HAND)
    wk.hand("second", sd, 18.6, 3.0, 0.10, 0.06, 0.80, 0.02, GOLD_HAND)
    wk.cylinder("cap", 0, 0, 5.0, 0.80, 0.93, GOLD_POL, verts=64)
    wk.cylinder("crystal", 0, 0, 212.6, 1.6, 1.75, GLASS, verts=256)

wk.render(OUT)

"""NVC Navigator: pilot chronograph inspired by the user's Citizen Promaster (BY3006-53E).

  python art/blender/make_prints.py
  blender -b -P art/blender/navigator.py -- <out.png> [samples] [bg]

With "bg" it renders the production background for the watch face: no hands, no crystal and none
of the dynamic content (complication icons, temperature, glucose number, date number).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import watchkit as wk  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = Path(argv[0]) if argv else wk.ROOT / "docs/mockup/propuestas/navigator_3d.png"
SAMPLES = int(argv[1]) if len(argv) > 1 else 192
TIME, GLUCOSE, BATTERY, DAY = (10, 8, 32), 112, 76, 23
BG = len(argv) > 2 and argv[2] == "bg"
PRINT = wk.BUILD / ("navigator_print_bg.png" if BG else "navigator_print.png")

wk.setup(SAMPLES, world_strength=0.5, key_energy=14000)

STEEL_POL = wk.simple("steel_polished", **{"Base Color": (0.80, 0.80, 0.82, 1), "Metallic": 1.0, "Roughness": 0.08})
STEEL_HAND = wk.simple("steel_hand", **{"Base Color": (0.86, 0.86, 0.88, 1), "Metallic": 1.0, "Roughness": 0.20})
STEEL_IDX = wk.simple("steel_index", **{"Base Color": (0.84, 0.84, 0.86, 1), "Metallic": 1.0, "Roughness": 0.15})
LUME = wk.simple("lume", **{"Base Color": (0.80, 0.92, 0.82, 1), "Roughness": 0.55,
                            "Emission Color": (0.55, 1.0, 0.65, 1), "Emission Strength": 0.08})
RED = wk.simple("red", **{"Base Color": (0.75, 0.06, 0.04, 1), "Roughness": 0.3})
DATE_DISC = wk.simple("date_disc", **{"Base Color": (0.92, 0.91, 0.87, 1), "Roughness": 0.5,
                                      "Emission Color": (1, 1, 0.97, 1), "Emission Strength": 0.12})
BLACK = wk.simple("black", **{"Base Color": (0.01, 0.01, 0.012, 1), "Roughness": 0.35})
GOLD_TXT = wk.simple("gold_txt", **{"Base Color": (0.83, 0.67, 0.38, 1), "Roughness": 0.4,
                                    "Emission Color": (0.83, 0.67, 0.38, 1), "Emission Strength": 0.15})
GLASS = wk.simple("crystal", **{"Roughness": 0.0, "Transmission Weight": 1.0, "IOR": 1.77})

BEZEL = wk.finish_material("bezel", {"Base Color": (0.70, 0.71, 0.73, 1), "Metallic": 1.0, "Roughness": 0.28,
                                     "Anisotropic": 0.85}, PRINT, radial_tangent=True)
REHAUT = wk.finish_material("rehaut", {"Base Color": (0.035, 0.036, 0.04, 1), "Roughness": 0.55}, PRINT)
DIAL = wk.finish_material(
    "dial", {"Base Color": (0.075, 0.08, 0.088, 1), "Metallic": 1.0, "Roughness": 0.24, "Anisotropic": 1.0,
             "Anisotropic Rotation": 0.25, "Coat Weight": 0.35, "Coat Roughness": 0.03},
    PRINT, radial_tangent=True,
    inlay=(wk.BUILD / "navigator_map.png", {"Base Color": (0.40, 0.41, 0.43, 1), "Metallic": 1.0, "Roughness": 0.42}))

# bezel (24 h, brushed) and rehaut
wk.lathe("bezel", [(211.8, 0.55), (212.6, 1.05), (214.5, 1.30), (224, 1.42), (231.5, 1.25), (233, 0.9),
                   (233, -1.0)], BEZEL)
wk.lathe("rehaut", [(195.6, -0.02), (211.8, 0.62)], REHAUT)

# dial with holes for the sub-dials and the date window
dial = wk.cylinder("dial", 0, 0, 196.2, -0.3, 0.0, DIAL, verts=256)
for x, y, r, nm in [(-95, 0, 42, "activity"), (95, 0, 42, "weather"), (0, 95, 48, "glucose")]:
    wk.boolean_cut(dial, wk.cylinder("cut_" + nm, x, y, r, -1, 1, BLACK))
    wk.cylinder("floor_" + nm, x, y, r + 0.5, -0.45, -0.25, wk.snail_material(
        "floor_" + nm, {"Base Color": (0.06, 0.062, 0.068, 1), "Metallic": 0.7, "Roughness": 0.32}, PRINT))
    wk.torus("rim_" + nm, x, y, r + 1.2, 0.12, 0.02, STEEL_POL)

dx, dy = 160 * math.sin(math.radians(135)), -160 * math.cos(math.radians(135))
wk.boolean_cut(dial, wk.box("cut_date", dx, dy, 24, 16, -1, 1, 45, BLACK, bevel=0))
frame = wk.box("date_frame", dx, dy, 27, 19, -0.02, 0.06, 45, STEEL_POL, bevel=0.02)
wk.boolean_cut(frame, wk.box("cut_frame", dx, dy, 24, 16, -1, 1, 45, BLACK, bevel=0))
wk.cylinder("date_disc", dx, dy, 20, -0.7, -0.6, DATE_DISC)
if not BG:
    wk.text_obj("date_num", str(DAY), wk.BARLOW, 12, dx, dy, -0.585, BLACK, rot=45)

# applied indices: polished steel with lume inserts
for h in range(12):
    deg = h * 30
    if h in (3, 9):
        wk.radial_box(f"idx{h}", deg, 184, 193, 6.0, 0.0, 0.35, STEEL_IDX)
    elif h == 0:
        for o in (-1.8, 1.8):
            wk.radial_box(f"idx0{o}", deg + o, 170, 193, 4.4, 0.0, 0.35, STEEL_IDX)
            wk.radial_box(f"lume0{o}", deg + o, 173, 190, 1.8, 0.35, 0.37, LUME, bevel=0)
    else:
        r0 = 182 if h == 6 else 176
        wk.radial_box(f"idx{h}", deg, r0, 193, 6.2, 0.0, 0.35, STEEL_IDX)
        wk.radial_box(f"lume{h}", deg, r0 + 3, 190, 2.4, 0.35, 0.37, LUME, bevel=0)

wk.logo(0, -122, 60, 0.08, wk.logo_material())

# glucose value window
gcx, gcy = 0, 95
wk.box("gwin", gcx, gcy + 26, 34, 16, -0.01, 0.03, 0, BLACK, bevel=0.02)
gf = wk.box("gwin_frame", gcx, gcy + 26, 37, 19, -0.02, 0.05, 0, STEEL_POL, bevel=0.02)
wk.boolean_cut(gf, wk.box("cut_gwin", gcx, gcy + 26, 34, 16, -1, 1, 0, BLACK, bevel=0))
if not BG:
    wk.text_obj("gval", str(GLUCOSE), wk.BARLOW, 13, gcx - 4, gcy + 26, 0.04, GOLD_TXT)
    wk.text_obj("gtrend", "→", wk.SYMBOLS, 10, gcx + 11, gcy + 26, 0.04, GOLD_TXT)


    def g2deg(v):
        return -135 + 270 * (min(max(v, 40), 300) - 40) / 260


    wk.hand("gneedle", g2deg(GLUCOSE), 3.9, 0.8, 0.26, 0.10, 0.05, 0.05, STEEL_POL, pivot=(gcx, gcy))
    wk.cylinder("gcap", gcx, gcy, 3.4, 0.05, 0.16, STEEL_POL, verts=48)
    wk.hand("reserve", -50 + BATTERY, 2.6, 0.5, 0.22, 0.08, 0.05, 0.04, STEEL_POL, pivot=(0, -30))
    wk.cylinder("rcap", 0, -30, 2.4, 0.05, 0.13, STEEL_POL, verts=48)

    hd, md, sd = wk.hand_angles(TIME)
    wk.hand("hour", hd, 11.8, 1.8, 1.0, 0.6, 0.45, 0.12, STEEL_HAND, lume=(0.25, 0.78, 0.45), lume_mat=LUME)
    wk.hand("minute", md, 17.6, 2.2, 0.8, 0.45, 0.62, 0.11, STEEL_HAND, lume=(0.22, 0.86, 0.36), lume_mat=LUME)
    wk.hand("second", sd, 19.0, 4.2, 0.12, 0.08, 0.80, 0.02, RED)
    a = math.radians(sd)
    wk.cylinder("sec_dot", 150 * math.sin(a), -150 * math.cos(a), 3.0, 0.80, 0.83, RED, verts=32)
    wk.cylinder("cap", 0, 0, 6.5, 0.80, 0.95, STEEL_HAND, verts=64)
    wk.cylinder("crystal", 0, 0, 212, 1.6, 1.75, GLASS, verts=256)


wk.render(OUT)

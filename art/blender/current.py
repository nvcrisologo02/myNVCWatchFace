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
# satin black dial; milled continents are lighter, bead-blasted (2026-11-23: map must read on the watch)
DIAL = wk.finish_material(
    "dial", {"Base Color": (0.03, 0.03, 0.034, 1), "Metallic": 0.5, "Roughness": 0.28, "Coat Weight": 0.3,
             "Coat Roughness": 0.08},
    height=wk.BUILD / "current_height.png", height_strength=1.0, height_distance=0.35,
    inlay=(wk.BUILD / "current_land.png", {"Base Color": (0.11, 0.11, 0.115, 1), "Metallic": 0.5,
                                            "Roughness": 0.62}))

# bezel
wk.lathe("bezel", [(220.6, 0.05), (221.3, 0.45), (223.5, 0.70), (229.5, 0.66), (232.6, 0.35), (233, 0.0),
                   (233, -1.0)], BEZEL)

# dial with the sub-dials and windows cut out
dial = wk.cylinder("dial", 0, 0, 220.6, -0.3, 0.0, DIAL, verts=256)
CENTER = (0.0, 100.0, 50.0, 52.4)
SIDES = [(-82.0, 74.0, 41.0, 43.2), (82.0, 74.0, 41.0, 43.2)]
for i, (x, y, r, ro) in enumerate(SIDES + [CENTER]):
    nm = f"sub{i}"
    wk.boolean_cut(dial, wk.cylinder("cut_" + nm, x, y, r, -1, 1, BLACK))
    z = -0.45 if i < 2 else -0.40
    wk.cylinder("floor_" + nm, x, y, r + 0.5, z - 0.2, z, wk.snail_material(
        "floor_" + nm, {"Base Color": (0.035, 0.035, 0.04, 1), "Metallic": 0.6, "Roughness": 0.3},
        wk.BUILD / "empty.png", scale=20))
    # gold rims; the centre one sits higher so it crosses over the side ones (design §5.3)
    wk.torus("rim_" + nm, x, y, (r + ro) / 2, (ro - r) / 20 + 0.03, 0.22 if i == 2 else 0.0, GOLD_POL)

for i, (x, y) in enumerate([(138.0, 0.0), (-138.0, 0.0)]):
    wk.boolean_cut(dial, wk.box(f"cut_win{i}", x, y, 58, 24, -1, 1, 0, BLACK, bevel=0))
    fr = wk.box(f"win_frame{i}", x, y, 61.2, 27.2, -0.02, 0.08, 0, GOLD, bevel=0.04)
    wk.boolean_cut(fr, wk.box(f"cut_frame{i}", x, y, 58, 24, -1, 1, 0, BLACK, bevel=0))
    wk.box(f"win_floor{i}", x, y, 60, 26, -0.5, -0.4, 0, WIN_FLOOR, bevel=0)

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

"""Render the gold hands of the installed face in 3D, one by one, pointing at 12 on a transparent film.

  blender -b -P art/blender/hands.py -- <out_dir> [samples]

Writes <out_dir>/raw_<name>.png (932x932, 2 px per watch px, pivot at the image centre).
art/blender/cut_hands.py then crops them into watch face sprites.
"""
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import watchkit as wk  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = Path(argv[0]) if argv else wk.BUILD / "hands"
SAMPLES = int(argv[1]) if len(argv) > 1 else 128

# hand geometry (units: 10 watch px). Reach from the design (§5.4): hour 117, minute 177, second 189
SPECS = {
    "hour": dict(length=11.7, tail=1.6, w_base=1.25, w_tip=0.30, z=0.45, thick=0.12),
    "minute": dict(length=17.7, tail=2.0, w_base=0.95, w_tip=0.22, z=0.60, thick=0.10),
    "second": dict(length=18.9, tail=2.9, w_base=0.18, w_tip=0.10, z=0.78, thick=0.02),
}

for name, g in SPECS.items():
    wk.setup(SAMPLES, world_strength=0.8, key_energy=16000)
    wk.scene.render.film_transparent = True
    gold = wk.simple("gold_pol", **{"Base Color": (0.97, 0.79, 0.48, 1), "Metallic": 1.0, "Roughness": 0.24})
    white = wk.simple("white", **{"Base Color": (0.90, 0.89, 0.86, 1), "Metallic": 0.6, "Roughness": 0.25})
    mat = white if name == "second" else gold
    wk.hand(name, 0.0, g["length"], g["tail"], g["w_base"], g["w_tip"], g["z"], g["thick"], mat)
    if name == "second":
        wk.torus("sec_ring", 0, 33, 4.2, 0.06, g["z"] + 0.01, white)  # counterweight ring, 33 px behind
    wk.render(OUT / f"raw_{name}.png")

# centre cap: gold ring with a dark centre
wk.setup(SAMPLES, world_strength=0.8, key_energy=16000)
wk.scene.render.film_transparent = True
gold = wk.simple("gold_pol", **{"Base Color": (0.97, 0.79, 0.48, 1), "Metallic": 1.0, "Roughness": 0.24})
black = wk.simple("black", **{"Base Color": (0.01, 0.01, 0.012, 1), "Roughness": 0.4})
wk.cylinder("cap", 0, 0, 7.0, 0.80, 0.92, gold, verts=64)
wk.cylinder("cap_in", 0, 0, 5.2, 0.92, 0.95, black, verts=64)
wk.render(OUT / "raw_cap.png")

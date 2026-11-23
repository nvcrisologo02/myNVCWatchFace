"""Render the hands of a watch face in 3D, one by one, pointing at 12 on a transparent film.

  blender -b -P art/blender/hands.py -- <out_dir> [samples] [face]     face: nvc (default) | navigator

Writes <out_dir>/raw_<name>.png (932x932, 2 px per watch px, pivot at the image centre).
art/blender/cut_hands.py then crops them into watch face sprites.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import watchkit as wk  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = Path(argv[0]) if argv else wk.BUILD / "hands"
SAMPLES = int(argv[1]) if len(argv) > 1 else 128
FACE = argv[2] if len(argv) > 2 else "nvc"


def materials():
    return dict(
        gold=wk.simple("gold_pol", **{"Base Color": (0.97, 0.79, 0.48, 1), "Metallic": 1.0, "Roughness": 0.24}),
        white=wk.simple("white", **{"Base Color": (0.90, 0.89, 0.86, 1), "Metallic": 0.6, "Roughness": 0.25}),
        black=wk.simple("black", **{"Base Color": (0.01, 0.01, 0.012, 1), "Roughness": 0.4}),
        steel=wk.simple("steel_hand", **{"Base Color": (0.86, 0.86, 0.88, 1), "Metallic": 1.0, "Roughness": 0.20}),
        steel_pol=wk.simple("steel_pol", **{"Base Color": (0.80, 0.80, 0.82, 1), "Metallic": 1.0, "Roughness": 0.08}),
        red=wk.simple("red", **{"Base Color": (0.75, 0.06, 0.04, 1), "Roughness": 0.3}),
        red_metal=wk.simple("red_metal", **{"Base Color": (0.85, 0.10, 0.06, 1), "Metallic": 0.6, "Roughness": 0.3}),
        lume=wk.simple("lume", **{"Base Color": (0.80, 0.92, 0.82, 1), "Roughness": 0.55,
                                  "Emission Color": (0.55, 1.0, 0.65, 1), "Emission Strength": 0.08}),
    )


def nvc(name, m):
    """Gold hands of the installed NVC face. Reach (design §5.4): hour 117, minute 177, second 189."""
    if name == "hour":
        wk.hand(name, 0, 11.7, 1.6, 1.25, 0.30, 0.45, 0.12, m["gold"])
    elif name == "minute":
        wk.hand(name, 0, 17.7, 2.0, 0.95, 0.22, 0.60, 0.10, m["gold"])
    elif name == "second":
        wk.hand(name, 0, 18.9, 2.9, 0.18, 0.10, 0.78, 0.02, m["white"])
        wk.torus("sec_ring", 0, 33, 4.2, 0.06, 0.79, m["white"])  # counterweight ring, 33 px behind
    elif name == "cap":
        wk.cylinder("cap", 0, 0, 7.0, 0.80, 0.92, m["gold"], verts=64)
        wk.cylinder("cap_in", 0, 0, 5.2, 0.92, 0.95, m["black"], verts=64)


def navigator(name, m):
    """Steel sword hands with lume, red seconds, small needles (design 2026-11-23-navigator §5)."""
    if name == "hour":
        wk.hand(name, 0, 11.8, 1.8, 1.0, 0.6, 0.45, 0.12, m["steel"], lume=(0.25, 0.78, 0.45), lume_mat=m["lume"])
    elif name == "minute":
        wk.hand(name, 0, 17.6, 2.2, 0.8, 0.45, 0.62, 0.11, m["steel"], lume=(0.22, 0.86, 0.36), lume_mat=m["lume"])
    elif name == "second":
        wk.hand(name, 0, 19.0, 4.2, 0.12, 0.08, 0.80, 0.02, m["red"])
        wk.cylinder("sec_dot", 0, -150, 3.0, 0.80, 0.83, m["red"], verts=32)
    elif name == "cap":
        wk.cylinder("cap", 0, 0, 6.5, 0.80, 0.95, m["steel"], verts=64)
    elif name == "gauge":       # glucose gauge needle, pivot at the gauge centre
        # white lacquer like an aircraft gauge: polished steel got lost on the dial (watch, 2026-11-23)
        wk.hand(name, 0, 4.6, 0.9, 0.34, 0.13, 0.05, 0.05, m["white"])
        wk.cylinder("gcap", 0, 0, 4.0, 0.05, 0.16, m["steel"], verts=48)
    elif name in ("reserve", "reserve_low"):   # battery power-reserve needle; red when low
        mat = m["red_metal"] if name == "reserve_low" else m["white"]
        wk.hand(name, 0, 3.6, 0.6, 0.32, 0.12, 0.05, 0.04, mat)
        wk.cylinder("rcap", 0, 0, 3.0, 0.05, 0.13, m["steel"], verts=48)


FACES = {
    "nvc": (nvc, ["hour", "minute", "second", "cap"]),
    "navigator": (navigator, ["hour", "minute", "second", "cap", "gauge", "reserve", "reserve_low"]),
}

build, names = FACES[FACE]
for nm in names:
    wk.setup(SAMPLES, world_strength=0.8, key_energy=16000)
    wk.scene.render.film_transparent = True
    build(nm, materials())
    wk.render(OUT / f"raw_{nm}.png")

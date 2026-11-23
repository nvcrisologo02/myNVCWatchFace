"""Always-On art of NVC Nocturne (design 2026-11-23-nocturne §5).

  python art/blender/nocturne_aod.py <art_dir> <prints_dir>

Writes in <art_dir>:
  ambient_dial.png    932x932, opaque black with the moon aperture left transparent (the moon disc,
                      drawn underneath, shows through, as on the active face); Roman numerals,
                      railroad track, aperture rim and the glucose scale in dim gold
  hand3d_<n>_aod.png  hour / minute: the Breguet silhouette in dim gold (same size and pivot)
Deterministic.
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

N = 932
K = 2.0
C = N / 2
DIM = 0.42
R_IN, R_OUT, HALF, HUMP_R = 100, 140, 40, 22   # moon window, as art/blender/nocturne.py
R_MID = (R_IN + R_OUT) / 2


def P(x, y):
    return C + x * K, C + y * K


def aperture_mask():
    m = Image.new("L", (N, N), 0)
    d = ImageDraw.Draw(m)
    d.pieslice([*P(-R_OUT, -R_OUT), *P(R_OUT, R_OUT)], -90 - HALF, -90 + HALF, fill=255)
    d.ellipse([*P(-R_IN, -R_IN), *P(R_IN, R_IN)], fill=0)
    for s in (-1, 1):
        a = math.radians(s * HALF)
        hx, hy = R_MID * math.sin(a), -R_MID * math.cos(a)
        d.ellipse([*P(hx - HUMP_R, hy - HUMP_R), *P(hx + HUMP_R, hy + HUMP_R)], fill=0)
    return m


def dial(art: Path, prints: Path):
    out = Image.new("RGBA", (N, N), (0, 0, 0, 255))
    pr = Image.open(prints / "nocturne_print_bg.png").convert("RGBA").resize((N, N), Image.LANCZOS)
    # keep numerals, track and glucose fan; drop the sub-dial scales (hidden in ambient)
    keep = Image.new("L", (N, N), 255)
    kd = ImageDraw.Draw(keep)
    for x in (-92, 92):
        kd.ellipse([*P(x - 46, 10 - 46), *P(x + 46, 10 + 46)], fill=0)
    a = ImageChops.multiply(pr.getchannel("A"), keep).point(lambda v: round(v * DIM))
    ink = pr.copy()
    ink.putalpha(a)
    out = Image.alpha_composite(out, ink)
    d = ImageDraw.Draw(out)
    gold = (int(214 * DIM), int(180 * DIM), int(112 * DIM), 255)
    for r in (R_OUT + 0.7, R_IN - 0.7):
        d.arc([*P(-r, -r), *P(r, r)], -90 - HALF + 9, -90 + HALF - 9, fill=gold, width=2)
    hole = aperture_mask()
    out.putalpha(ImageChops.subtract(out.getchannel("A"), hole))
    out.save(art / "ambient_dial.png", optimize=True)


def hand_aod(art: Path, name: str):
    im = Image.open(art / f"hand3d_{name}.png").convert("RGBA")
    sil = Image.new("RGBA", im.size, (110, 90, 51, 0))
    sil.putalpha(im.getchannel("A"))
    sil.save(art / f"hand3d_{name}_aod.png", optimize=True)


if __name__ == "__main__":
    art, prints = Path(sys.argv[1]), Path(sys.argv[2])
    dial(art, prints)
    for n in ("hour", "minute", "gauge"):
        hand_aod(art, n)
    print(art)

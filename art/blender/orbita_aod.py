"""Always-On art of NVC Orbita (design 2026-11-26-orbita §5).

  python art/blender/orbita_aod.py <art_dir> <prints_dir>

Writes in <art_dir>:
  ambient_dial.png    932x932, opaque black: ring numerals and hour ticks dimmed, the globe window
                      outline and the continents at 30 %. No band, step bars, marker or satellite.
  hand3d_<n>_aod.png  hour / minute: the hand silhouette in dim white (same size and pivot)
Deterministic.
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

N = 932
K = 2.0
C = N / 2
DIM = 0.45
LAND = 0.30
WINDOW = 170.0
TEXT_R = 213.0


def P(x, y):
    return C + x * K, C + y * K


def ring_mask(r0, r1):
    m = Image.new("L", (N, N), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([*P(-r1, -r1), *P(r1, r1)], fill=255)
    d.ellipse([*P(-r0, -r0), *P(r0, r0)], fill=0)
    return m


def dial(art: Path, prints: Path):
    out = Image.new("RGBA", (N, N), (0, 0, 0, 255))
    pr = Image.open(prints / "orbita_print_bg.png").convert("RGBA").resize((N, N), Image.LANCZOS)
    # keep the numerals (r 200..226 minus the step bars and the shoe at the top) and the hour ticks
    numerals = ring_mask(TEXT_R - 13, TEXT_R + 12)  # stops short of the knurled rim (r 226)
    ImageDraw.Draw(numerals).pieslice([*P(-230, -230), *P(230, 230)], -90 - 56, -90 + 56, fill=0)  # bars, shoe
    keep = ImageChops.lighter(numerals, ring_mask(176, 197))  # + hour ticks
    ImageDraw.Draw(keep).ellipse([*P(-64, 134 - 64), *P(64, 134 + 64)], fill=0)  # glucose sub-dial ticks
    white = Image.new("RGBA", (N, N), (236, 236, 230, 255))
    white.putalpha(ImageChops.multiply(pr.getchannel("A"), keep).point(lambda v: round(v * DIM)))
    out = Image.alpha_composite(out, white)
    # continents and the window outline
    land = Image.open(prints / "orbita_map.png").convert("RGBA").resize((N, N), Image.LANCZOS).getchannel("A")
    grey = Image.new("RGBA", (N, N), (236, 236, 230, 255))
    grey.putalpha(land.point(lambda v: round(v * LAND)))
    out = Image.alpha_composite(out, grey)
    d = ImageDraw.Draw(out)
    c = round(236 * DIM)
    d.ellipse([*P(-WINDOW, -WINDOW), *P(WINDOW, WINDOW)], outline=(c, c, c, 255), width=2)
    out.save(art / "ambient_dial.png", optimize=True)


def hand_aod(art: Path, name: str):
    im = Image.open(art / f"hand3d_{name}.png").convert("RGBA")
    c = round(236 * 0.6)
    sil = Image.new("RGBA", im.size, (c, c, c, 0))
    sil.putalpha(im.getchannel("A"))
    sil.save(art / f"hand3d_{name}_aod.png", optimize=True)


if __name__ == "__main__":
    art, prints = Path(sys.argv[1]), Path(sys.argv[2])
    dial(art, prints)
    for n in ("hour", "minute"):
        hand_aod(art, n)
    print(art)

"""Always-On art of NVC Navigator ("like a watch in the dark", design 2026-11-23-navigator §5).

  python art/blender/navigator_aod.py <art_dir> <prints_dir>

Reads the 3D hand sprites in <art_dir> (hand3d_*.png) and writes there:
  ambient_dial.png     932x932: lume of the indices + the glucose scale, dimmed; transparent elsewhere
  hand3d_<n>_aod.png   hour / minute: dark body, glowing lume strip (same size and pivot as the 3D sprite)
Deterministic.
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

N = 932
K = 2.0  # px per watch px
C = N / 2
LUME = (110, 255, 150)


def P(x, y):
    return C + x * K, C + y * K


def bar(d, deg, r0, r1, w, fill):
    a = math.radians(deg)
    ux, uy, tx, ty = math.sin(a), -math.cos(a), math.cos(a), math.sin(a)
    pts = [(ux * r0 - tx * w / 2, uy * r0 - ty * w / 2), (ux * r1 - tx * w / 2, uy * r1 - ty * w / 2),
           (ux * r1 + tx * w / 2, uy * r1 + ty * w / 2), (ux * r0 + tx * w / 2, uy * r0 + ty * w / 2)]
    d.polygon([P(*p) for p in pts], fill=fill)


def glow(layer, radius=3.0, gain=0.7):
    a = layer.getchannel("A").filter(ImageFilter.GaussianBlur(radius)).point(lambda v: round(v * gain))
    halo = Image.new("RGBA", layer.size, LUME + (0,))
    halo.putalpha(a)
    return Image.alpha_composite(halo, layer)


def dial(art: Path, prints: Path):
    lume = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(lume)
    # lume inserts of the applied indices (same geometry as art/blender/navigator.py)
    for h in range(12):
        deg = h * 30
        if h in (3, 9):
            continue
        if h == 0:
            for o in (-1.8, 1.8):
                bar(d, deg + o, 173, 190, 1.8, LUME + (235,))
        else:
            r0 = 182 if h == 6 else 176
            bar(d, deg, r0 + 3, 190, 2.4, LUME + (235,))
    out = glow(lume)
    # glucose scale, dimmed: the printed gauge (zones and ticks) around (233, 328), r 56
    pr = Image.open(prints / "navigator_print_bg.png").convert("RGBA").resize((N, N), Image.LANCZOS)
    m = Image.new("L", (N, N), 0)
    ImageDraw.Draw(m).ellipse([*P(-56, 95 - 56), *P(56, 95 + 56)], fill=255)
    gauge = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    gauge.paste(pr, (0, 0), ImageChops.multiply(m, pr.getchannel("A")))
    gauge.putalpha(gauge.getchannel("A").point(lambda v: round(v * 0.55)))
    out = Image.alpha_composite(out, gauge)
    out.save(art / "ambient_dial.png", optimize=True)


def hand_aod(art: Path, name: str):
    im = Image.open(art / f"hand3d_{name}.png").convert("RGBA")
    px = im.load()
    body = Image.new("RGBA", im.size, (0, 0, 0, 0))
    lume = Image.new("RGBA", im.size, (0, 0, 0, 0))
    bp, lp = body.load(), lume.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a < 8:
                continue
            if g - r >= 3 and g - b >= 3 and g > 160:   # pale-green lume strip (steel leans blue)
                lp[x, y] = LUME + (a,)
            else:
                bp[x, y] = (38, 40, 42, round(a * 0.9))
    Image.alpha_composite(body, glow(lume, 2.0, 0.6)).save(art / f"hand3d_{name}_aod.png", optimize=True)


if __name__ == "__main__":
    art, prints = Path(sys.argv[1]), Path(sys.argv[2])
    dial(art, prints)
    for n in ("hour", "minute"):
        hand_aod(art, n)
    print(art)

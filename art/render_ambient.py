"""Generate the ambient (Always-On) dial: thin dim-gold indices and the logo at 32 % (design §5.4).

Output: <out_dir>/ambient_dial.png, 932x932 (2x), transparent except indices and logo.
Deterministic. Usage: python art/render_ambient.py <logo.png> <out_dir>
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

SCALE = 2
SS = 4
SIZE = 466
GOLD_DIM = (110, 90, 51, 255)   # #6E5A33
LOGO_CENTER = (233, 110)   # must match LOGO_CY in render_bg.py (233 - 123)
LOGO_WIDTH = 72
LOGO_OPACITY = 0.32


def _indices(draw: ImageDraw.ImageDraw, k: float) -> None:
    c = SIZE / 2 * k
    for hour in range(12):
        a = math.radians(hour * 30)
        sx, sy = math.sin(a), -math.cos(a)
        px, py = math.cos(a), math.sin(a)  # perpendicular
        offsets = (-1.9, 1.9) if hour % 3 == 0 else (0.0,)
        r0, r1 = (194, 212) if hour % 3 == 0 else (197, 212)
        for o in offsets:
            x0, y0 = c + (sx * r0 + px * o) * k, c + (sy * r0 + py * o) * k
            x1, y1 = c + (sx * r1 + px * o) * k, c + (sy * r1 + py * o) * k
            draw.line([(x0, y0), (x1, y1)], fill=GOLD_DIM, width=round(1.0 * k))


def render_ambient(logo_path: Path, out_dir: Path) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    k = SCALE * SS
    big = Image.new("RGBA", (SIZE * k, SIZE * k), (0, 0, 0, 0))
    _indices(ImageDraw.Draw(big), k)
    im = big.resize((SIZE * SCALE, SIZE * SCALE), Image.LANCZOS)

    logo = Image.open(logo_path).convert("RGBA")
    w = LOGO_WIDTH * SCALE
    logo = logo.resize((w, round(logo.height * w / logo.width)), Image.LANCZOS)
    alpha = logo.getchannel("A").point(lambda v: round(v * LOGO_OPACITY))
    logo.putalpha(alpha)
    im.alpha_composite(logo, (LOGO_CENTER[0] * SCALE - logo.width // 2,
                              LOGO_CENTER[1] * SCALE - logo.height // 2))
    path = out_dir / "ambient_dial.png"
    im.save(path, optimize=False, compress_level=9)
    return path


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    print(render_ambient(Path(sys.argv[1]), Path(sys.argv[2])))

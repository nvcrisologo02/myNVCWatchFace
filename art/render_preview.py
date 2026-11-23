"""Compose the watch face picker preview (466x466): 3D background, 3D hands with shadows at 10:08:32.

Usage: python art/render_preview.py <art_out_dir> <preview.png>
Uses bg_3d.png and hand3d_*.png from scripts/render_3d.sh (placement in hand3d_placement.json).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

CENTER = 466  # 2x px
ANGLES = {"hour": (10 + 8 / 60) * 30, "minute": (8 + 32 / 60) * 6, "second": 32 * 6}
SHADOW_OFFSET = (2, 3)  # watch px, same as the shadow clock in watchface.xml


def render_preview(art: Path, out: Path) -> Path:
    im = Image.open(art / "bg_3d.png").convert("RGBA")
    placement = json.loads((art / "hand3d_placement.json").read_text())

    def put(name, angle, suffix="", dx=0, dy=0):
        hand = Image.open(art / f"hand3d_{name}{suffix}.png").convert("RGBA")
        w, h = hand.size
        pivot = round(placement[name]["pivot_y"] * h)
        canvas = Image.new("RGBA", (2 * h, 2 * h), (0, 0, 0, 0))
        canvas.paste(hand, (h - w // 2, h - pivot))
        canvas = canvas.rotate(-angle, resample=Image.BICUBIC)
        im.alpha_composite(canvas, (CENTER - h + dx * 2, CENTER - h + dy * 2))

    for name, angle in ANGLES.items():
        put(name, angle, "_shadow", *SHADOW_OFFSET)
    for name, angle in ANGLES.items():
        put(name, angle)
    cap = Image.open(art / "hand3d_cap.png").convert("RGBA")
    im.alpha_composite(cap, (CENTER - cap.width // 2, CENTER - cap.height // 2))
    im.resize((466, 466), Image.LANCZOS).convert("RGB").save(out, compress_level=9)
    return out


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    print(render_preview(Path(sys.argv[1]), Path(sys.argv[2])))

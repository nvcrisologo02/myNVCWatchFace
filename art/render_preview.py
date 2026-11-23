"""Compose the watch face picker preview (466x466): background plus hands at 10:08:32.

Usage: python art/render_preview.py <art_out_dir> <preview.png>
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_hands import HANDS  # noqa: E402

CENTER = 466  # 2x px
ANGLES = {"hand_hour": (10 + 8 / 60) * 30, "hand_minute": (8 + 32 / 60) * 6, "hand_second": 32 * 6}


def render_preview(art: Path, out: Path) -> Path:
    im = Image.open(art / "bg_bajo.png").convert("RGBA")
    for name, angle in ANGLES.items():
        hand = Image.open(art / f"{name}.png").convert("RGBA")
        g = HANDS[name]
        w, h = hand.size
        canvas = Image.new("RGBA", (2 * h, 2 * h), (0, 0, 0, 0))
        canvas.paste(hand, (h - w // 2, h - g["pivot_px"]))
        canvas = canvas.rotate(-angle, resample=Image.BICUBIC)
        im.alpha_composite(canvas, (CENTER - h, CENTER - h))
    cap = Image.open(art / "hand_cap.png").convert("RGBA")
    im.alpha_composite(cap, (CENTER - cap.width // 2, CENTER - cap.height // 2))
    im.resize((466, 466), Image.LANCZOS).convert("RGB").save(out, compress_level=9)
    return out


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    print(render_preview(Path(sys.argv[1]), Path(sys.argv[2])))

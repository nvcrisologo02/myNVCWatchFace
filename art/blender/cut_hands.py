"""Crop the 3D hand renders into watch face sprites and make their drop shadows.

  python art/blender/cut_hands.py <raw_dir> <out_dir>      (every raw_<name>.png in raw_dir)

For each hand writes hand3d_<name>.png and hand3d_<name>_shadow.png (2x, pointing up, pivot on
the vertical centre line) and prints the WFF placement: x, y, width, height, pivotY.
Width is an even integer so x lands on a pixel (WFF hand x/y are integers).
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageFilter

SCALE = 2
CENTRE = 466  # pivot in the 932 px raw render
SHADOW_BLUR = 3.0  # 2x px
SHADOW_ALPHA = 0.55


def cut(raw: Path, out: Path, name: str) -> dict:
    im = Image.open(raw / f"raw_{name}.png").convert("RGBA")
    a = im.getchannel("A")
    l, t, r, b = a.point(lambda v: 255 if v > 4 else 0).getbbox()
    pad = 8  # room for the shadow blur
    half = max(CENTRE - l, r - CENTRE) + pad
    half += half % 2  # even
    top, bottom = max(t - pad, 0), min(b + pad, im.height)
    box = (CENTRE - half, top, CENTRE + half, bottom)
    sprite = im.crop(box)
    if (sprite.height % 2):
        sprite = im.crop((box[0], box[1], box[2], box[3] + 1))
    sprite.save(out / f"hand3d_{name}.png", optimize=True)
    alpha = sprite.getchannel("A").filter(ImageFilter.GaussianBlur(SHADOW_BLUR))
    shadow = Image.new("RGBA", sprite.size, (0, 0, 0, 0))
    shadow.putalpha(alpha.point(lambda v: round(v * SHADOW_ALPHA)))
    shadow.save(out / f"hand3d_{name}_shadow.png", optimize=True)
    w, h = sprite.size[0] // SCALE, sprite.size[1] // SCALE
    pivot_px = CENTRE - top
    return dict(x=233 - w // 2, y=233 - pivot_px // SCALE, width=w, height=h,
                pivot_y=round(pivot_px / sprite.size[1], 6))


if __name__ == "__main__":
    raw, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    names = sorted(p.stem[4:] for p in raw.glob("raw_*.png"))
    placement = {n: cut(raw, out, n) for n in names}
    (raw / "placement.json").write_text(json.dumps(placement, indent=2))
    print(json.dumps(placement, indent=2))

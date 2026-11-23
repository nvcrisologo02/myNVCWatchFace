"""Generate the watch hands and centre cap for the NVC watch face (design §5.4).

Each hand is a narrow PNG at 2x (SCALE) pointing up, with the pivot on the vertical centre line at
row HANDS[name]["pivot_px"]. The watch face places it centred on (233, 233) using pivotX = 0.5 and
pivotY = HANDS[name]["pivot_y"]. Deterministic: same code, same bytes.

Usage: python art/render_hands.py <out_dir>
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

SCALE = 2          # export scale (watch px -> image px)
SS = 4             # supersampling factor for anti-aliasing

GOLD = (201, 168, 106)        # #C9A86A
GOLD_LIGHT = (230, 205, 149)  # #E6CD95
GOLD_DIM = (110, 90, 51)      # #6E5A33
WHITE = (239, 237, 231)       # #EFEDE7
DARK_EDGE = (20, 16, 10)

# Geometry in watch px: reach from pivot to tip, tail behind the pivot, maximum half-width.
_SPEC = {
    "hand_hour":   dict(reach=117, tail=16, half=5.6, tip=1.4),
    "hand_minute": dict(reach=177, tail=20, half=3.6, tip=0.9),
    "hand_second": dict(reach=189, tail=37, half=0.8, tip=0.6, ring=4.2),
}
_PAD = 2  # watch px of transparent margin around each hand

HANDS: dict[str, dict] = {}
for _name, _s in _SPEC.items():
    _w = 2 * math.ceil(max(_s["half"], _s.get("ring", 0) + 1) + _PAD)  # even integer: x lands on a pixel
    _h = _s["reach"] + _s["tail"] + 2 * _PAD
    _pivot_px = (_PAD + _s["reach"]) * SCALE
    for _suffix in ("", "_aod"):
        if _name == "hand_second" and _suffix:
            continue  # no second hand in ambient (design §5.4)
        HANDS[_name + _suffix] = dict(
            width=_w, height=_h, pivot_px=_pivot_px,
            pivot_y=round(_pivot_px / (_h * SCALE), 6),
        )

CAP = dict(radius=7, ring=1.6)


def _taper(s: dict, ss: float, cx: float, py: float) -> tuple[list, list]:
    """Left and right outline of a tapered hand, tip up, in supersampled px."""
    top = py - s["reach"] * ss
    bot = py + s["tail"] * ss
    shoulder = py - s["reach"] * 0.28 * ss
    left = [(cx - s["tip"] * ss, top), (cx - s["half"] * ss, shoulder),
            (cx - s["half"] * 0.8 * ss, py), (cx - s["half"] * 0.5 * ss, bot)]
    right = [(cx + s["half"] * 0.5 * ss, bot), (cx + s["half"] * 0.8 * ss, py),
             (cx + s["half"] * ss, shoulder), (cx + s["tip"] * ss, top)]
    return left, right


def _draw_hand(name: str, ambient: bool) -> Image.Image:
    s = _SPEC[name]
    g = HANDS[name + ("_aod" if ambient else "")]
    k = SCALE * SS
    W, H = round(g["width"] * k), round(g["height"] * k)
    cx, py = W / 2, g["pivot_px"] * SS
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    if name == "hand_second":
        # thin needle, ring counterweight at the end of the tail
        d.rectangle([cx - s["half"] * k, py - s["reach"] * k, cx + s["half"] * k,
                     py + (s["tail"] - 2 * s["ring"]) * k], fill=WHITE + (255,))
        rc = py + (s["tail"] - s["ring"]) * k
        r = s["ring"] * k
        d.ellipse([cx - r, rc - r, cx + r, rc + r], outline=WHITE + (255,), width=round(1.4 * k))
    else:
        left, right = _taper(s, k, cx, py)
        outline = left + right
        if ambient:
            d.polygon(outline, outline=GOLD_DIM + (255,), width=round(1.2 * k))
        else:
            d.polygon(outline, fill=DARK_EDGE + (255,))
            inner_l, inner_r = _taper(dict(s, half=s["half"] - 0.6, tip=s["tip"] * 0.6,
                                           reach=s["reach"] - 0.8, tail=s["tail"] - 0.8),
                                      k, cx, py)
            # two facets: the left one catches the light (design §5.2: light from top left)
            d.polygon(inner_l + [(cx, py + (s["tail"] - 0.8) * k), (cx, py - (s["reach"] - 0.8) * k)],
                      fill=GOLD_LIGHT + (255,))
            d.polygon([(cx, py - (s["reach"] - 0.8) * k), (cx, py + (s["tail"] - 0.8) * k)] + inner_r,
                      fill=GOLD + (255,))
    return im.resize((round(g["width"] * SCALE), round(g["height"] * SCALE)), Image.LANCZOS)


def _draw_cap() -> Image.Image:
    r, ring = CAP["radius"], CAP["ring"]
    k = SCALE * SS
    size = round(2 * (r + 1) * k)
    c = size / 2
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([c - r * k, c - r * k, c + r * k, c + r * k], fill=GOLD + (255,))
    d.ellipse([c - (r - ring) * k, c - (r - ring) * k, c + (r - ring) * k, c + (r - ring) * k],
              fill=(14, 14, 16, 255))
    d.ellipse([c - 1.6 * k, c - 1.6 * k, c + 1.6 * k, c + 1.6 * k], fill=GOLD_LIGHT + (255,))
    return im.resize((size // SS, size // SS), Image.LANCZOS)


def render_hands(out_dir: Path) -> list[Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for name in HANDS:
        base = name.removesuffix("_aod")
        im = _draw_hand(base, ambient=name.endswith("_aod"))
        p = out_dir / f"{name}.png"
        im.save(p, optimize=False, compress_level=9)
        paths.append(p)
    p = out_dir / "hand_cap.png"
    _draw_cap().save(p, optimize=False, compress_level=9)
    paths.append(p)
    return paths


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    for path in render_hands(Path(sys.argv[1])):
        print(path)
    for name, g in HANDS.items():
        print(f"{name}: {g['width']}x{g['height']} pivotY={g['pivot_y']}")

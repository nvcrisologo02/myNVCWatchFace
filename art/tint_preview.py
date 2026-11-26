"""Preview the watch's tint of the Orbita ring and fit each colour to its Blender render (plan task 4).

  python -I art/tint_preview.py <art_dir> <renders_dir> <out.png>

<art_dir> holds bg_3d.png and ring_tint.png (scripts/render_3d.sh 256 orbita); <renders_dir> holds
orbita_<colour>.png, the sketch rendered with the ring really in that colour (art/blender/orbita.py).
The watch draws ring_tint.png with tintColor: each channel multiplied by the colour (sRGB). For each
colour the tint is fitted so that the mean of the tinted sectors equals the mean of the same sectors
in the Blender render. Prints the ARGB values and writes a sheet: tinted on top, Blender below.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

COLOURS = ("verde", "naranja", "rojo", "amarillo", "azul")


def tinted(bg, ring, rgb):
    r = np.asarray(ring).astype(float)
    r[..., :3] *= np.asarray(rgb, float) / 255
    layer = Image.fromarray(np.clip(r, 0, 255).astype(np.uint8), "RGBA")
    return Image.alpha_composite(bg, layer)


def fit(ring, ref):
    """sRGB colour that makes the mean of the tinted sector pixels equal the reference's."""
    r = np.asarray(ring).astype(float)
    sel = r[..., 3] > 250
    ring_mean = r[sel][:, :3].mean(axis=0)
    ref_mean = np.asarray(ref.convert("RGB")).astype(float)[sel].mean(axis=0)
    return tuple(int(v) for v in np.clip(np.round(ref_mean / ring_mean * 255), 0, 255)), sel


def main(art, renders, out):
    bg = Image.open(art / "bg_3d.png").convert("RGBA")
    ring = Image.open(art / "ring_tint.png").convert("RGBA")
    S = 420
    sheet = Image.new("RGB", (S * len(COLOURS), S * 2), (20, 20, 22))
    mask = Image.new("L", (S - 20, S - 20), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, S - 21, S - 21], fill=255)
    for i, c in enumerate(COLOURS):
        ref = Image.open(renders / f"orbita_{c}.png").convert("RGBA")
        rgb, sel = fit(ring, ref)
        t = tinted(bg, ring, rgb)
        err = np.abs(np.asarray(t.convert("RGB")).astype(float)[sel].mean(axis=0)
                     - np.asarray(ref.convert("RGB")).astype(float)[sel].mean(axis=0)).max()
        print(f'"{c}": "#ff{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}",  # mean error {err:.1f}')
        for row, im in enumerate((t, ref)):
            sheet.paste(im.convert("RGB").resize((S - 20, S - 20), Image.LANCZOS), (i * S + 10, row * S + 10), mask)
    sheet.save(out)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))

"""Turn the user's satellite PNG into the white sprite of the Orbita face (user, 2026-11-26).

  python -I art/satellite_sprite.py <satellite.png> art/blender/build/orbita_satellite.png [rot] [longest] [cx] [cy]

The picture is cut from its white background, made monochrome and lifted to white (the blue solar
panels become light grey, their grid a little darker), rotated so the dish points at the globe,
scaled and placed in the 932 px render frame (2 px per watch px, dial centre in the middle).
Defaults: rotation 202 deg counter-clockwise, longest side 250 watch px, centre at (112, 0).
"""
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC, DST = sys.argv[1], sys.argv[2]
ROT = float(sys.argv[3]) if len(sys.argv) > 3 else 202.0
LONGEST = float(sys.argv[4]) if len(sys.argv) > 4 else 250.0
CX = float(sys.argv[5]) if len(sys.argv) > 5 else 112.0
CY = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0
OUT = 932

im = Image.open(SRC).convert("RGBA")
if im.getextrema()[3][0] < 255:  # it already has transparency
    alpha = im.getchannel("A")
else:  # flood the white background from the corners
    fill = im.convert("RGB")
    for corner in ((0, 0), (fill.width - 1, 0), (0, fill.height - 1), (fill.width - 1, fill.height - 1)):
        ImageDraw.floodfill(fill, corner, (255, 0, 255), thresh=28)
    arr = np.asarray(fill).astype(int)
    bg = (arr[:, :, 0] == 255) & (arr[:, :, 1] == 0) & (arr[:, :, 2] == 255)
    alpha = Image.fromarray(((~bg) * 255).astype("uint8"), "L").filter(ImageFilter.MinFilter(3))
alpha = alpha.filter(ImageFilter.GaussianBlur(0.7))

# monochrome lifted to white: the brightest of (luminance, blue) keeps the blue panels light, then
# v -> 255 - (255 - v) / 2 so the grid lines stay a little darker than the panels
rgb = np.asarray(im.convert("RGB")).astype(float)
lum = rgb @ (0.299, 0.587, 0.114)
white = 255 - (255 - np.maximum(lum, rgb[:, :, 2])) * 0.5
mono = Image.fromarray(white.astype("uint8"), "L")
sprite = Image.merge("RGBA", (mono, mono, mono, alpha))
sprite = sprite.crop(sprite.getbbox())
sprite = sprite.rotate(ROT, resample=Image.BICUBIC, expand=True)
sprite = sprite.crop(sprite.getbbox())
k = 2 * LONGEST / max(sprite.size)
sprite = sprite.resize((round(sprite.width * k), round(sprite.height * k)), Image.LANCZOS)
frame = Image.new("RGBA", (OUT, OUT), (0, 0, 0, 0))
frame.alpha_composite(sprite, (round(OUT / 2 + 2 * CX - sprite.width / 2), round(OUT / 2 + 2 * CY - sprite.height / 2)))
frame.save(DST)
# drop shadow (the reference's satellite is dark-edged over the land): blurred alpha, offset (3, 4) px
shadow = Image.new("RGBA", (OUT, OUT), (0, 0, 0, 0))
sh_alpha = frame.getchannel("A").filter(ImageFilter.GaussianBlur(4)).point(lambda v: int(v * 0.6))
shadow.putalpha(sh_alpha)
shadow = shadow.transform(shadow.size, Image.AFFINE, (1, 0, -6, 0, 1, -8))
shadow.save(DST.replace(".png", "_shadow.png"))
bb = frame.getbbox()
print("sprite bbox (watch px):", [round((bb[0] - OUT / 2) / 2), round((bb[1] - OUT / 2) / 2),
                                  round((bb[2] - OUT / 2) / 2), round((bb[3] - OUT / 2) / 2)])

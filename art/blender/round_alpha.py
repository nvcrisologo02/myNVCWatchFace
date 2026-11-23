"""Crop a transparent-film render to the round screen, keeping its alpha (holes stay holes).

  python art/blender/round_alpha.py <src.png> <dst.png>
"""
import sys

from PIL import Image, ImageChops, ImageDraw

src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGBA")
m = Image.new("L", (im.width * 4, im.height * 4), 0)
ImageDraw.Draw(m).ellipse([0, 0, m.width - 1, m.height - 1], fill=255)
m = m.resize(im.size, Image.LANCZOS)
im.putalpha(ImageChops.multiply(im.getchannel("A"), m))
im.save(dst, optimize=True)

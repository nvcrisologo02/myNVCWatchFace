"""Printed layers for the 3D sketches: everything that is ink on the dial, rehaut or bezel.

Blender projects these images straight down onto the 3D parts (orthographic top view), so
prints stay exactly where the watch face expects them. Run with the system Python (needs PIL):

  python art/blender/make_prints.py <out_dir>

Outputs (1864x1864, 4 px per watch px, image centre = dial centre):
  navigator_print.png  RGBA ink (white, gold, red, amber) on transparent
  navigator_map.png    L mask of the world map (steel inlay on the dial)
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ART = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ART))
import render_bg as rb  # noqa: E402  (reuses the map projection and land polygons)

N = 1864
K = N / 466.0
C = N / 2
BARLOW = ART.parent / "watchface/src/main/res/font/barlow_condensed_semibold.ttf"
BARLOW_M = ART.parent / "watchface/src/main/res/font/barlow_condensed_medium.ttf"

WHITE = (236, 236, 230, 255)
BLACK = (12, 12, 14, 255)
GOLD = (214, 178, 112, 255)
RED = (214, 64, 52, 255)
AMBER = (226, 160, 56, 255)
GREY = (170, 170, 166, 255)

# glucose gauge geometry (watch px, centre of the dial = 0,0; y down)
GAUGE = (0.0, 95.0, 56.0)  # enlarged on the user's request (2026-11-23; was r 48)
RESERVE = (0.0, -30.0)


def P(x, y):
    return C + x * K, C + y * K


def polar(r, deg, cx=0.0, cy=0.0):
    a = math.radians(deg)
    return cx + r * math.sin(a), cy - r * math.cos(a)


def tick(d, deg, r0, r1, w, fill, cx=0.0, cy=0.0):
    a = math.radians(deg)
    ux, uy, tx, ty = math.sin(a), -math.cos(a), math.cos(a), math.sin(a)
    pts = [(cx + ux * r0 - tx * w / 2, cy + uy * r0 - ty * w / 2), (cx + ux * r1 - tx * w / 2, cy + uy * r1 - ty * w / 2),
           (cx + ux * r1 + tx * w / 2, cy + uy * r1 + ty * w / 2), (cx + ux * r0 + tx * w / 2, cy + uy * r0 + ty * w / 2)]
    d.polygon([P(*p) for p in pts], fill=fill)


def label(img, txt, font, size, x, y, fill, rot=0.0, stroke=0.0):
    f = ImageFont.truetype(str(font), max(4, round(size * K)))
    sw = round(stroke * K)
    l, t, r, b = f.getbbox(txt, stroke_width=sw)
    tile = Image.new("RGBA", (r - l + 8, b - t + 8), (0, 0, 0, 0))
    ImageDraw.Draw(tile).text((4 - l, 4 - t), txt, font=f, fill=fill, stroke_width=sw, stroke_fill=fill)
    if rot:
        tile = tile.rotate(-rot, resample=Image.BICUBIC, expand=True)
    px, py = P(x, y)
    img.alpha_composite(tile, (round(px - tile.width / 2), round(py - tile.height / 2)))


def arc(d, cx, cy, r, w, a0, a1, fill):
    # PIL angles: 0 = 3 o'clock, clockwise; ours: 0 = 12 o'clock
    box = [*P(cx - r, cy - r), *P(cx + r, cy + r)]
    d.arc(box, a0 - 90, a1 - 90, fill=fill, width=max(1, round(w * K)))


def sun(d, cx, cy, r, fill):
    d.ellipse([*P(cx - r * 0.45, cy - r * 0.45), *P(cx + r * 0.45, cy + r * 0.45)], fill=fill)
    for i in range(8):
        tick(d, i * 45, r * 0.62, r, r * 0.16, fill, cx, cy)


def runner(d, cx, cy, s, fill):
    """Stand-in for the OHealth activity icon."""
    w = max(1, round(0.15 * s * K))
    segs = [(0.1, -0.55, -0.05, 0.05), (-0.05, 0.05, 0.3, 0.45), (-0.05, 0.05, -0.4, 0.38),
            (0.3, 0.45, 0.2, 0.85), (0.05, -0.4, 0.5, -0.15), (0.05, -0.4, -0.45, -0.25)]
    for x0, y0, x1, y1 in segs:
        d.line([P(cx + x0 * s, cy + y0 * s), P(cx + x1 * s, cy + y1 * s)], fill=fill, width=w, joint="curve")
    hr = 0.17 * s
    d.ellipse([*P(cx + 0.15 * s - hr, cy - 0.78 * s - hr), *P(cx + 0.15 * s + hr, cy - 0.78 * s + hr)], fill=fill)


def g2deg(v):
    return -135 + 270 * (min(max(v, 40), 300) - 40) / 260


def navigator(out: Path):
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # bezel: 24 h scale, engraved and filled black
    for h in range(24):
        deg = h * 15
        if h % 2 == 0:
            label(img, str(h if h else 24), BARLOW, 11, *polar(222.5, deg), BLACK, rot=deg)
        else:
            tick(d, deg, 218.5, 226.5, 1.6, BLACK)
    # rehaut minute track
    for m in range(60):
        tick(d, m * 6, 198 if m % 5 == 0 else 203, 210.5, 1.8 if m % 5 == 0 else 0.9, WHITE)
    # sub-dial ticks (activity at 9, weather at 3)
    for cx in (-95.0, 95.0):
        for i in range(30):
            tick(d, i * 12, 42 - (6 if i % 5 == 0 else 3.5), 40.8, 1.0, WHITE, cx, 0.0)
    label(img, "ACTIVIDAD", BARLOW_M, 6.5, -95, 27, GREY)
    # glucose gauge: coloured zones, ticks, thresholds
    gcx, gcy, gr = GAUGE
    for lo, hi, c in [(40, 70, RED), (70, 180, GOLD), (180, 300, AMBER)]:
        arc(d, gcx, gcy, gr - 6, 3.2, g2deg(lo), g2deg(hi), c)
    for v in range(40, 301, 20):
        tick(d, g2deg(v), gr - 13, gr - 8, 1.0, WHITE, gcx, gcy)
    for v in (70, 180):
        label(img, str(v), BARLOW_M, 9, *polar(gr - 22, g2deg(v), gcx, gcy), GREY)
    label(img, "mg/dL", BARLOW_M, 8, gcx, gcy - 18, GREY)
    # power reserve (battery)
    pcx, pcy = RESERVE
    for i in range(11):
        tick(d, -50 + i * 10, 34, 39 if i % 5 else 43, 1.2 if i % 5 else 1.8, WHITE, pcx, pcy)  # enlarged 2026-11-23
    label(img, "0", BARLOW_M, 8.5, *polar(49, -50, pcx, pcy), GREY)
    label(img, "100", BARLOW_M, 8.5, *polar(51, 50, pcx, pcy), GREY)
    label(img, "RESERVA", BARLOW_M, 7, pcx, pcy - 16, GREY)
    label(img, "NAVIGATOR", BARLOW_M, 8, 0, -84, (210, 210, 204, 255))
    img.save(out / "navigator_print_bg.png")  # production: no sample content
    # sample complication content (in the real face these come from the providers)
    sun(d, 95, -14, 11, GOLD)
    label(img, "8°", BARLOW, 22, 97, 13, WHITE)
    runner(d, -95, -3, 19, GOLD)
    img.save(out / "navigator_print.png")

    # map inlay mask
    polys = rb.load_land(str(ART / "data/ne_50m_land.geojson"))
    m = Image.new("L", (N * 2, N * 2), 0)
    rb.draw_land(ImageDraw.Draw(m), K * 2, C * 2, polys)
    m = m.reduce(2)
    # keep the map off the sub-dials and inside the dial
    cut = Image.new("L", (N, N), 0)
    cd = ImageDraw.Draw(cut)
    cd.ellipse([*P(-190, -190), *P(190, 190)], fill=255)
    for cx, cy, r in [(-95, 0, 46), (95, 0, 46), (0, 95, 52)]:
        cd.ellipse([*P(cx - r, cy - r), *P(cx + r, cy + r)], fill=0)
    from PIL import ImageChops
    ImageChops.multiply(m, cut).save(out / "navigator_map.png")


BODONI = Path(__file__).resolve().parents[2] / "nocturne/src/main/res/font/bodoni_moda.ttf"  # SIL OFL
NGOLD = (214, 180, 112, 255)
FAN = (0.0, 32.0, 62.0)  # pivot x, y and radius of the glucose fan (2026-11-23: was (0, 40, 74), clashed with the 30 px value)


def f2deg(v):
    return 240 - 120 * (min(max(v, 40), 300) - 40) / 260


def nocturne(out: Path):
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    romans = ["XII", "I", "II", "III", "IIII", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
    for h, rn in enumerate(romans):
        if h == 4:  # the date window sits at 4 (moved from 6, user 2026-11-23); III and IX fit
            continue
        label(img, rn, BODONI, 24 if h else 26, *polar(178, h * 30), NGOLD, rot=h * 30)
    # railroad minute track
    for r in (202.6, 209.0):
        d.ellipse([*P(-r, -r), *P(r, r)], outline=NGOLD, width=round(0.8 * K))
    for m in range(60):
        tick(d, m * 6, 202.6, 209.0, 1.6 if m % 5 == 0 else 0.7, NGOLD)
    # sub-dial ticks: reserve scale on the 9 o'clock dial, plain ticks on the 3 o'clock dial
    for i in range(6):
        tick(d, -60 + i * 24, 30, 36, 1.1, NGOLD, -92, 10)
    for i in range(12):
        tick(d, i * 30, 38.5, 42.5, 0.9, NGOLD, 92, 10)
    # glucose fan
    fx, fy, fr = FAN
    for lo, hi, c in [(40, 70, RED), (70, 180, NGOLD), (180, 300, AMBER)]:
        a0, a1 = sorted((f2deg(lo), f2deg(hi)))
        arc(d, fx, fy, fr, 2.6, a0, a1, c)
    for v in range(40, 301, 20):
        tick(d, f2deg(v), fr - 7, fr - 2, 0.8, NGOLD, fx, fy)
    for v in (70, 180):
        label(img, str(v), BODONI, 8, *polar(fr - 14, f2deg(v), fx, fy), NGOLD)
    label(img, "mg/dL", BODONI, 7, 0, 146, (170, 170, 176, 255))
    img.save(out / "nocturne_print_bg.png")  # production: no sample content
    runner(d, -90, 15, 14, NGOLD)
    sun(d, 90, -5, 10, NGOLD)
    label(img, "8°", BODONI, 17, 92, 18, (236, 230, 214, 255))
    img.save(out / "nocturne_print.png")

    # moon-phase sky (projected on the disc under the aperture)
    sky = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sky)
    mx, my = 0.0, 0.0
    sd.ellipse([*P(mx - 146, my - 146), *P(mx + 146, my + 146)], fill=(16, 34, 104, 255))
    for sx, sy, sr in [(-22, -16, 1.3), (-12, -26, 0.9), (6, -28, 1.1), (19, -18, 1.4), (25, -6, 0.9),
                       (-27, -4, 1.0), (13, -8, 0.8), (-4, -18, 0.6)]:
        sd.ellipse([*P(mx + sx - sr, my + sy - sr), *P(mx + sx + sr, my + sy + sr)], fill=(244, 214, 140, 255))
    sky.save(out / "nocturne_sky.png")

    # moon disc of the watch face (turns under the aperture): lapis sky with stars all round,
    # centred on the image centre because the disc is rendered at the origin
    disc = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    dd = ImageDraw.Draw(disc)
    dd.ellipse([*P(-146, -146), *P(146, 146)], fill=(16, 34, 104, 255))
    import random
    rnd = random.Random(29)
    for _ in range(170):
        r = 100 + 42 * rnd.random()  # the band seen through the window
        a = rnd.random() * 2 * math.pi
        sx, sy, sr = r * math.cos(a), r * math.sin(a), 0.5 + 0.8 * rnd.random()
        dd.ellipse([*P(sx - sr, sy - sr), *P(sx + sr, sy + sr)], fill=(244, 214, 140, 255))
    disc.save(out / "nocturne_moon_disc.png")

    # clous de Paris height map (centre of the dial, r < 150)
    import numpy as np
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    xx = (xx + 0.5 - C) / K
    yy = (yy + 0.5 - C) / K
    u = (xx + yy) / math.sqrt(2) / 3.0
    v = (xx - yy) / math.sqrt(2) / 3.0
    hob = np.minimum(1 - np.abs((u % 1) * 2 - 1), 1 - np.abs((v % 1) * 2 - 1))
    hob = hob * (np.hypot(xx, yy) < 149.5)
    Image.fromarray((hob * 255).astype(np.uint8), "L").save(out / "nocturne_guilloche.png")


# ------------------------------------------------------------------ Orbita (sketch, 2026-11-26)
# Geometry measured on the user's own design, docs/referencias/orbita-referencia.png, scaled to the
# 466 px screen (grid in art/blender/build/orbita_ref_grid.png): knurled grey rim r 226..233, ring
# r 200..226 with coloured sectors 1:40-4:20 and 7:40-10:20, dark zone with the hour ticks r 152..200,
# globe window r 152, glucose sub-dial at (0, 134) r 62/46.
OB_RIM_IN = 226.0
OB_RING_IN = 200.0
OB_TEXT_R = 213.0                  # numerals and curved texts, centred in the ring
OB_SECTORS = ((50, 130), (230, 310))
OB_SHOE_DEG = -45.0        # steps icon (fixed)
OB_STEPS_START = -40.0     # steps value starts here, clockwise (TextCircular align START)
OB_BATT_ICON = 221.0       # battery icon (dynamic: red when low)
OB_BATT_START = 214.0      # battery value starts here, reading counter-clockwise
OB_HR_CENTRE = 149.0       # heart rate centred on 5 o'clock
OB_SUB = (0.0, 134.0, 62.0, 46.0)  # sub-dial centre, outer (tick ring) and inner (dark disc) radii
OB_ACCENT = (232, 92, 36, 255)
INK = (40, 40, 42, 255)
TICK_GREY = (104, 104, 102, 255)
OB_WINDOW = 170.0  # globe window: the dark band to the ring is narrow, as in the reference
OB_MAP = (2.75, 2.6, -12.0, -55.0, 190.0)  # px/deg lon, px/deg Mercator lat, (lon 32.5, lat 30) at, bulge R


def arc_text(img, txt, font, size, r, deg, fill, track=1.0, stroke=0.0):
    """Text bent along a circle, centred on deg. Upper half reads clockwise, lower half counter-clockwise.
    Returns the angles it spans."""
    f = ImageFont.truetype(str(font), max(4, round(size * K)))
    widths = [f.getlength(ch) / K * track for ch in txt]
    span = math.degrees(sum(widths) / r)
    lower = 90 < deg % 360 < 270
    a = deg + span / 2 if lower else deg - span / 2
    for ch, w in zip(txt, widths):
        step = math.degrees(w / r)
        mid = a - step / 2 if lower else a + step / 2
        if ch != " ":
            label(img, ch, font, size, *polar(r, mid), fill, rot=mid + 180 if lower else mid, stroke=stroke)
        a = a - step if lower else a + step
    return deg - span / 2, deg + span / 2


def icon(img, draw_fn, w, h, x, y, rot=0.0):
    """Icon drawn by draw_fn(d, k, ox, oy) on a w x h (watch px) tile, rotated and pasted at (x, y)."""
    tile = Image.new("RGBA", (round(w * K) + 8, round(h * K) + 8), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(tile), K, 4, 4)
    if rot:
        tile = tile.rotate(-rot, resample=Image.BICUBIC, expand=True)
    px, py = P(x, y)
    img.alpha_composite(tile, (round(px - tile.width / 2), round(py - tile.height / 2)))


def battery(d, k, ox, oy, w=22.0, h=11.0, level=0.8, fill=INK):
    d.rounded_rectangle([ox, oy, ox + w * k, oy + h * k], radius=2 * k, outline=fill, width=max(1, round(1.5 * k)))
    d.rounded_rectangle([ox + w * k, oy + h * 0.3 * k, ox + (w + 2.2) * k, oy + h * 0.7 * k], radius=k, fill=fill)
    d.rounded_rectangle([ox + 2.8 * k, oy + 2.8 * k, ox + (2.8 + (w - 5.6) * level) * k, oy + (h - 2.8) * k],
                        radius=k, fill=fill)


def shoe(d, k, ox, oy, s=18.0, fill=INK):
    """Steps icon: a running shoe seen from the side, toe to the right (unit box 1 x 0.6)."""
    up = [(0.00, 0.30), (0.05, 0.12), (0.13, 0.04), (0.22, 0.10), (0.30, 0.24), (0.42, 0.22), (0.55, 0.28),
          (0.70, 0.34), (0.84, 0.38), (0.95, 0.44), (1.00, 0.50), (0.98, 0.56)]
    sole = [(0.96, 0.60), (0.10, 0.60), (0.02, 0.56), (0.0, 0.46)]
    d.polygon([(ox + x * s * k, oy + y * s * k) for x, y in up + sole], fill=fill)
    # sole line and laces, cut out
    d.line([(ox + 0.03 * s * k, oy + 0.48 * s * k), (ox + 0.97 * s * k, oy + 0.52 * s * k)], fill=(0, 0, 0, 0),
           width=max(1, round(0.05 * s * k)))
    for x0 in (0.36, 0.46, 0.56):
        d.line([(ox + x0 * s * k, oy + 0.30 * s * k), (ox + (x0 + 0.05) * s * k, oy + 0.40 * s * k)],
               fill=(0, 0, 0, 0), width=max(1, round(0.04 * s * k)))


def text_span(txt, size, r):
    """Angle (deg) that arc_text uses for txt at radius r."""
    f = ImageFont.truetype(str(BARLOW), max(4, round(size * K)))
    return math.degrees(sum(f.getlength(ch) / K for ch in txt) / r)


def battery_icon(fill):
    """Full-frame layer with the battery icon at OB_BATT_ICON on the band, upright towards the centre."""
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    icon(im, lambda dd, k, ox, oy: battery(dd, k, ox, oy, 24, 12, fill=fill), 26.2, 12,
         *polar(OB_TEXT_R, OB_BATT_ICON), rot=OB_BATT_ICON + 180)
    return im


def orbita_map(out: Path):
    """The globe's map as in the reference: a flat Mercator map (not a true sphere: the reference's
    Europe and Africa are bigger), fitted on the reference by overlaying the coastlines
    (art/blender/build/fit_flat.png), then bulged towards the window edge (planar distance s ->
    R sin(s / R)). Writes orbita_map.png (white land with hammered grain, alpha = land, clipped to the
    window) and orbita_map_height.png (raised land with soft edges, for the bump)."""
    import json
    import numpy as np
    from PIL import ImageFilter
    kx, ky, ox, oy, bulge = OB_MAP
    merc = lambda lat: math.degrees(math.log(math.tan(math.pi / 4 + math.radians(max(-80.0, min(80.0, lat))) / 2)))  # noqa: E731
    m30 = merc(30)

    def pr(lon, lat):
        x, y = ox + kx * (lon - 32.5), oy - ky * (merc(lat) - m30)
        r = math.hypot(x, y)
        if r > 0:
            f = bulge * math.sin(min(r, bulge * math.pi / 2) / bulge) / r
            x, y = x * f, y * f
        return P(x, y)

    ss = 2  # supersampling
    m = Image.new("L", (N * ss, N * ss), 0)
    md = ImageDraw.Draw(m)
    with open(ART / "data/ne_50m_land.geojson", encoding="utf-8") as fh:
        geo = json.load(fh)
    for f in geo["features"]:
        g = f["geometry"]
        for rings in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            for i, ring in enumerate(rings):
                pts = [pr(lo, la) for lo, la in ring if la > -60]
                if len(pts) > 2:
                    md.polygon([(x * ss, y * ss) for x, y in pts], fill=255 if i == 0 else 0)
    m = m.resize((N, N), Image.LANCZOS)
    clip = Image.new("L", (N, N), 0)
    ImageDraw.Draw(clip).ellipse([*P(-OB_WINDOW, -OB_WINDOW), *P(OB_WINDOW, OB_WINDOW)], fill=255)
    from PIL import ImageChops
    m = ImageChops.multiply(m, clip)
    # hammered grain (deterministic) and a slightly darker band just inside the coast
    rng = np.random.default_rng(7)
    grain = Image.fromarray((rng.random((N // 4, N // 4)) * 255).astype(np.uint8), "L").resize((N, N), Image.BICUBIC)
    grain = np.asarray(grain.filter(ImageFilter.GaussianBlur(2))).astype(float) / 255
    inner = np.asarray(m.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(4))).astype(float) / 255
    val = 255 * (0.80 + 0.14 * grain) * (0.86 + 0.14 * inner)
    tone = Image.fromarray(np.clip(val, 0, 255).astype(np.uint8), "L")
    Image.merge("RGBA", (tone, tone, tone, m)).save(out / "orbita_map.png")
    h = np.asarray(m.filter(ImageFilter.GaussianBlur(3))).astype(float) / 255 * (0.85 + 0.15 * grain)
    Image.fromarray((h * 255).astype(np.uint8), "L").save(out / "orbita_map_height.png")


def orbita(out: Path):
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rt = OB_TEXT_R
    # ring: white numerals on the coloured sectors, a dark upright 6 on the white bottom one
    from PIL import ImageFilter
    sh = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    for h in (2, 3, 4, 8, 9, 10):
        label(sh, str(h), BARLOW, 28, *polar(rt, h * 30), (0, 0, 0, 170), rot=h * 30, stroke=1.0)
    label(sh, "6", BARLOW, 28, *polar(rt - 1, 180), (0, 0, 0, 120), stroke=1.0)
    sh = sh.filter(ImageFilter.GaussianBlur(1.2 * K)).transform(sh.size, Image.AFFINE, (1, 0, -1.5 * K, 0, 1, -2 * K))
    img.alpha_composite(sh)
    for h in (2, 3, 4, 8, 9, 10):
        label(img, str(h), BARLOW, 28, *polar(rt, h * 30), WHITE, rot=h * 30, stroke=0.6)
    label(img, "6", BARLOW, 28, *polar(rt - 1, 180), INK, stroke=0.6)
    # step bars centred in the band, from the steps text to the coloured sector (the orange progress
    # marker is a separate turning sprite, orbita_step_marker.png)
    for i in range(-7, 28):
        tick(d, i * 2, 204, 223, 1.6, TICK_GREY)
    # steps icon: fixed, left of the steps value (which starts at OB_STEPS_START)
    icon(img, lambda dd, k, ox, oy: shoe(dd, k, ox, oy, 24), 24, 15, *polar(rt, OB_SHOE_DEG), rot=OB_SHOE_DEG)
    # knurled rim: a fine dark line every degree
    for i in range(360):
        tick(d, i, OB_RIM_IN + 0.8, 232.6, 0.9, (58, 58, 60, 255))
    # hour ticks on the dark zone between the ring and the globe window
    for h in range(12):
        tick(d, h * 30, 177 if h == 0 else 180, 196 if h == 0 else 193, 4.0 if h == 0 else 3.0, WHITE)
    # glucose sub-dial: dark ticks across its silver ring
    sx, sy, so, si = OB_SUB
    for i in range(36):
        tick(d, i * 10, si + 1.5, so - 1.5, 1.8, INK, sx, sy)
    img.save(out / "orbita_print_bg.png")  # production: no sample content
    # sample dynamic content (the watch face draws these): steps, battery, heart rate, glucose
    arc_text(img, "8000", BARLOW, 28, rt, OB_STEPS_START + text_span("8000", 28, rt) / 2, INK, stroke=0.4)
    arc_text(img, "80%", BARLOW, 28, rt, OB_BATT_START - text_span("80%", 28, rt) / 2, INK, stroke=0.4)
    img.alpha_composite(battery_icon(INK))
    arc_text(img, "89 BPM", BARLOW, 28, rt, OB_HR_CENTRE, INK, stroke=0.4)
    label(img, "112", BARLOW, 48, sx, sy, WHITE, stroke=0.5)
    img.save(out / "orbita_print.png")

    # dynamic sprites, full frame (932 px, pivot = dial centre): progress marker at 0 deg, battery icons
    mk = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    tick(ImageDraw.Draw(mk), 0, 201, 226, 5.0, OB_ACCENT)
    mk.save(out / "orbita_step_marker.png")
    battery_icon(INK).save(out / "orbita_icon_battery.png")
    battery_icon(RED).save(out / "orbita_icon_battery_low.png")

    orbita_map(out)

    # coloured sectors of the ring; white elsewhere
    sm = Image.new("L", (N, N), 0)
    sd = ImageDraw.Draw(sm)
    for a0, a1 in OB_SECTORS:
        sd.pieslice([*P(-OB_RIM_IN, -OB_RIM_IN), *P(OB_RIM_IN, OB_RIM_IN)], a0 - 90, a1 - 90, fill=255)
    sd.ellipse([*P(-OB_RING_IN, -OB_RING_IN), *P(OB_RING_IN, OB_RING_IN)], fill=0)
    sm.save(out / "orbita_ring_mask.png")


def current(out: Path):
    """Displacement and material masks of the installed face (geometry of art/render_bg.py).

    current_height.png (16 bit): displacement in Blender units, encoded as 1 + H / 0.6
      (1.0 = dial surface). Continents milled 0.10, rays 0.025, minute dots 0.04, sub-dials and
      windows sunk 0.40, outside the dial 0.6.
    current_land.png, current_wells.png, current_windows.png: material masks.
    current_snail.png: concentric snailing of each sub-dial floor (bump).
    """
    import numpy as np
    S = rb.S
    assert S == N
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    xx = (xx + 0.5 - C) / K
    yy = (yy + 0.5 - C) / K
    rr = np.hypot(xx, yy)
    polys = rb.load_land(str(ART / "data/ne_50m_land.geojson"))
    land = rb.raster(lambda d, k, c: rb.draw_land(d, k, c, polys))
    land = np.clip((rb.gauss(land, rb.COAST_SMOOTH * K) - 0.5) / 0.10 + 0.5, 0, 1)
    land *= np.clip((216.0 - rr) / 1.0 + 0.5, 0, 1)
    _, y_cut = rb.proj(0.0, rb.LAT_CUT)
    land *= np.clip((float(y_cut) - yy) / 0.5, 0, 1)

    def soft(mask, px=0.35):
        return np.clip(mask, 0, 1)

    wells = np.zeros_like(land)
    for cx, cy, r, ro in rb.WELLS:
        wells = np.maximum(wells, np.clip((r - np.hypot(xx - cx, yy - cy)) * K / 2 + 0.5, 0, 1))
    covers = np.zeros_like(land)
    for cx, cy, r, ro in rb.WELLS:
        covers = np.maximum(covers, np.clip((ro + 1.0 - np.hypot(xx - cx, yy - cy)) * K / 2 + 0.5, 0, 1))
    wins = np.zeros_like(land)
    for cx, cy in rb.WINDOWS:
        dx = np.abs(xx - cx) - rb.WIN_W / 2
        dy = np.abs(yy - cy) - rb.WIN_H / 2
        wins = np.maximum(wins, np.clip(-np.maximum(dx, dy) * K / 2 + 0.5, 0, 1))
        covers = np.maximum(covers, np.clip(-np.maximum(dx - 3, dy - 3) * K / 2 + 0.5, 0, 1))
    land_v = land * (1 - covers)
    rays = rb.raster(rb.draw_rays)
    fade = np.clip((rr - 24.0) / 40.0, 0, 1) * np.clip((203.0 - rr) / 2.0, 0, 1)
    rays_v = rays * fade * (1 - np.clip(land * 1.5, 0, 1)) * (1 - covers)
    dots = rb.raster(rb.draw_dots)
    inside = np.clip((220.6 - rr) * K / 2 + 0.5, 0, 1)

    H = (-0.10 * rb.gauss(land_v, 0.35 * K) - 0.025 * rays_v - 0.04 * rb.gauss(dots, 0.15 * K)
         - 0.40 * np.maximum(wells, wins))
    H = H * inside - 0.6 * (1 - inside)
    enc = np.clip(1 + H / 0.6, 0, 1)
    Image.fromarray((enc * 65535).astype(np.uint16)).save(out / "current_height.png")
    Image.fromarray((np.clip(land_v, 0, 1) * 255).astype(np.uint8), "L").save(out / "current_land.png")
    Image.fromarray((np.clip(wells, 0, 1) * 255).astype(np.uint8), "L").save(out / "current_wells.png")
    Image.fromarray((np.clip(wins, 0, 1) * 255).astype(np.uint8), "L").save(out / "current_windows.png")
    snail = np.zeros_like(land)
    # side dials first, centre last: the centre dial sits on top and its snailing wins (design §5.3)
    for cx, cy, r, ro in list(rb.SIDE_WELLS) + [rb.CENTER_WELL]:
        d = np.hypot(xx - cx, yy - cy)
        snail = np.where(d < r + 1, 0.5 + 0.5 * np.sin(2 * math.pi * d / 1.0), snail)
    Image.fromarray((snail * 255).astype(np.uint8), "L").save(out / "current_snail.png")


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ART / "blender/build"
    out.mkdir(parents=True, exist_ok=True)
    navigator(out)
    nocturne(out)
    orbita(out)
    current(out)
    print(out)

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


def label(img, txt, font, size, x, y, fill, rot=0.0):
    f = ImageFont.truetype(str(font), max(4, round(size * K)))
    l, t, r, b = f.getbbox(txt)
    tile = Image.new("RGBA", (r - l + 8, b - t + 8), (0, 0, 0, 0))
    ImageDraw.Draw(tile).text((4 - l, 4 - t), txt, font=f, fill=fill)
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
FAN = (0.0, 40.0, 74.0)  # pivot x, y and radius of the retrograde glucose fan


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
    current(out)
    print(out)

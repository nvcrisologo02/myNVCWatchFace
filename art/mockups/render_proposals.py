"""Sketches (bocetos) of two new watch face proposals, rendered like a product photo.

Throwaway design spike: not part of the watch face build. Reuses the lighting helpers of
art/render_bg.py so light comes from the top left as on the current face.

  navigator  - pilot chronograph inspired by the user's Citizen Promaster (BY3006-53E)
  nocturne   - dress watch designed from scratch around the "NVC zZz" (sleep) logo

Usage: python art/mockups/render_proposals.py <out_dir>
Writes <name>.png (active) and <name>_aod.png (Always-On) at 932x932.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ART = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ART))
import render_bg as rb  # noqa: E402

S, K, C = rb.S, rb.K, rb.C
FONTS = Path("C:/Windows/Fonts")
BARLOW = ART.parent / "watchface/src/main/res/font/barlow_condensed_semibold.ttf"
BARLOW_M = ART.parent / "watchface/src/main/res/font/barlow_condensed_medium.ttf"
BODONI = FONTS / "BOD_R.TTF"
SYMBOLS = FONTS / "seguisym.ttf"
LOGO = ART / "src/logo-nvc.jpg"
GEO = ART / "data/ne_50m_land.geojson"

yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
xx = (xx + 0.5 - C) / K
yy = (yy + 0.5 - C) / K
rr = np.hypot(xx, yy)
ang = np.arctan2(xx, -yy)  # 0 at 12 o'clock, clockwise
RNG = np.random.default_rng(11)

LIGHT = np.array([-0.55, -0.62, 0.56]); LIGHT /= np.linalg.norm(LIGHT)
HALF = LIGHT + np.array([0, 0, 1.0]); HALF /= np.linalg.norm(HALF)


# ----------------------------------------------------------------- masks
def mask(fn):
    return rb.raster(fn)


def disk(cx, cy, r):
    return mask(lambda d, k, c: d.ellipse(rb.bbox(cx, cy, r, k, c), fill=255))


def ring(cx, cy, r0, r1):
    return np.clip(disk(cx, cy, r1) - disk(cx, cy, r0), 0, 1)


def poly(pts):
    return mask(lambda d, k, c: d.polygon([(c + x * k, c + y * k) for x, y in pts], fill=255))


def polar(r, deg, cx=0.0, cy=0.0):
    a = math.radians(deg)
    return cx + r * math.sin(a), cy - r * math.cos(a)


def baton(deg, r0, r1, w0, w1=None, cx=0.0, cy=0.0):
    """Radial bar from r0 to r1, width w0 at r0 and w1 at r1 (wedge if they differ)."""
    w1 = w0 if w1 is None else w1
    a = math.radians(deg)
    ux, uy, tx, ty = math.sin(a), -math.cos(a), math.cos(a), math.sin(a)
    pts = [(cx + ux * r0 - tx * w0 / 2, cy + uy * r0 - ty * w0 / 2),
           (cx + ux * r1 - tx * w1 / 2, cy + uy * r1 - ty * w1 / 2),
           (cx + ux * r1 + tx * w1 / 2, cy + uy * r1 + ty * w1 / 2),
           (cx + ux * r0 + tx * w0 / 2, cy + uy * r0 + ty * w0 / 2)]
    return poly(pts)


def text(txt, font, size, cx, cy, rot=0.0):
    """Text mask centred on (cx, cy) in design units, rotated rot degrees clockwise."""
    f = ImageFont.truetype(str(font), max(4, int(round(size * K * 2))))
    l, t, r, b = f.getbbox(txt)
    im = Image.new("L", (r - l + 8, b - t + 8), 0)
    ImageDraw.Draw(im).text((4 - l, 4 - t), txt, font=f, fill=255)
    if rot:
        im = im.rotate(-rot, resample=Image.BICUBIC, expand=True)
    im = im.resize((max(1, im.width // 2), max(1, im.height // 2)), Image.LANCZOS)
    out = np.zeros((S, S), np.float32)
    x0 = int(round(C + cx * K - im.width / 2)); y0 = int(round(C + cy * K - im.height / 2))
    a = np.asarray(im, np.float32) / 255
    out[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a
    return out


def arc_mask(cx, cy, r, w, a0, a1):
    """Annular sector between angles a0..a1 (degrees, 0 = 12 o'clock, clockwise)."""
    ar = np.degrees(np.arctan2(xx - cx, -(yy - cy))) % 360
    lo, hi = a0 % 360, a1 % 360
    inside = (ar >= lo) & (ar <= hi) if lo <= hi else (ar >= lo) | (ar <= hi)
    d = np.hypot(xx - cx, yy - cy)
    return (np.clip((w / 2 - np.abs(d - r)) * K / 1.5 + 0.5, 0, 1) * inside).astype(np.float32)


# ----------------------------------------------------------------- shading
def normals(H, slope):
    gy, gx = np.gradient(H)
    nx, ny, nz = -gx * slope, -gy * slope, np.ones_like(H)
    n = np.sqrt(nx * nx + ny * ny + nz * nz)
    return nx / n, ny / n, nz / n


def _unit(*v):
    v = np.array(v, dtype=np.float64)
    return v / np.linalg.norm(v)


BOX = _unit(-0.45, -0.55, 0.70)     # large softbox, top left (the key light of the whole face)
STRIP = _unit(0.80, -0.05, 0.60)    # narrow strip light on the right
BOUNCE = _unit(0.05, 0.75, 0.66)    # weak bounce from below


def studio(rx, ry, rz, ceiling=0.22):
    """Brightness of a photo studio seen along reflection vector R (view straight down)."""
    def lobe(d, width):
        t = np.clip((rx * d[0] + ry * d[1] + rz * d[2] - (1 - width)) / width, 0, 1)
        return t * t * (3 - 2 * t)
    horizon = np.clip(1 - rz, 0, 1)
    return (ceiling + 0.10 * np.clip(-ry, 0, 1) - 0.12 * horizon
            + 1.55 * lobe(BOX, 0.10) + 1.10 * lobe(STRIP, 0.035) + 0.30 * lobe(BOUNCE, 0.12))


def reflect(nx, ny, nz, parallax=0.0011):
    """Reflection of the view ray; parallax lets flat parts see a slightly different studio
    depending on where they are on the dial, as in a photo."""
    rx, ry, rz = 2 * nz * nx, 2 * nz * ny, 2 * nz * nz - 1
    rx = rx + xx * parallax; ry = ry + yy * parallax
    n = np.sqrt(rx * rx + ry * ry + rz * rz)
    return rx / n, ry / n, rz / n


def env_metal(nx, ny, nz, base, ceiling=0.42, spec=0.5, polish=120):
    rx, ry, rz = reflect(nx, ny, nz)
    e = studio(rx, ry, rz, ceiling)
    ndh = np.clip(nx * HALF[0] + ny * HALF[1] + nz * HALF[2], 0, 1)
    return np.clip(e, 0, 2)[..., None] * np.array(base) + (spec * ndh ** polish)[..., None]


def metal(m, base, height=1.0, bevel=0.5, polish=120, env=0.55, slope=5.0, ceiling=0.42):
    """Raised polished metal part: flat top mirrors the studio ceiling, bevels catch the lights."""
    H = np.clip(rb.gauss(m, bevel * K) * 1.25, 0, 1) * height
    nx, ny, nz = normals(H, slope)
    return env_metal(nx, ny, nz, base, ceiling=ceiling, polish=polish)


def over(col, rgb, a):
    a = np.clip(a, 0, 1)[..., None]
    return col * (1 - a) + rgb * a


def shadow(col, m, dx=1.4, dy=1.8, blur=1.4, strength=0.6):
    sh = rb.gauss(rb.shift(m, dx, dy), blur * K)
    return col * (1 - strength * np.clip(sh - m, 0, 1))[..., None]


def lume_glow(m, color, blur=2.2):
    g = rb.gauss(m, blur * K)
    return np.array(color) * np.clip(m + 0.6 * g, 0, 1.2)[..., None]


# ----------------------------------------------------------------- shared parts
def hand_poly(deg, length, tail, w_base, w_tip, kind="sword"):
    """Outline of a hand pointing at deg, pivot at the centre."""
    if kind == "sword":
        prof = [(-tail, w_base * 0.5), (0, w_base), (length * 0.82, w_tip), (length, 0)]
    elif kind == "dauphine":
        prof = [(-tail, w_base * 0.4), (0, w_base * 0.7), (length * 0.25, w_base), (length, 0)]
    elif kind == "needle":
        prof = [(-tail, w_base), (length, w_tip)]
    a = math.radians(deg)
    ux, uy, tx, ty = math.sin(a), -math.cos(a), math.cos(a), math.sin(a)
    left = [(ux * s - tx * w / 2, uy * s - ty * w / 2) for s, w in prof]
    right = [(ux * s + tx * w / 2, uy * s + ty * w / 2) for s, w in reversed(prof)]
    return left + right, (ux, uy, tx, ty)


def faceted_hand(col, deg, length, tail, wb, wt, base, kind="sword", lume=None, lume_len=(0.25, 0.78),
                 shadow_off=(2.6, 3.4)):
    pts, (ux, uy, tx, ty) = hand_poly(deg, length, tail, wb, wt, kind)
    m = poly(pts)
    col = shadow(col, m, *shadow_off, blur=2.2, strength=0.7)
    # two facets either side of a central ridge, each tilted ~30 deg: one faces the softbox,
    # the other the dark studio, as on a real faceted hand
    half = poly([(0 - ux * tail, 0 - uy * tail), (ux * length, uy * length)] +
                [(ux * length - tx * wb, uy * length - ty * wb), (-ux * tail - tx * wb, -uy * tail - ty * wb)])
    f1 = np.clip(m * half, 0, 1); f2 = np.clip(m - f1, 0, 1)
    for f, sgn in ((f1, -1), (f2, 1)):
        nvec = _unit(sgn * tx * 0.32, sgn * ty * 0.32, 1.0)
        one = np.ones((S, S), np.float32)
        rgb = env_metal(one * nvec[0], one * nvec[1], one * nvec[2], base, ceiling=0.40)
        col = over(col, rgb, f)
    ridge = np.clip(rb.gauss(f1, 0.25 * K) * rb.gauss(f2, 0.25 * K) * 4, 0, 1) * m
    col = over(col, np.array((1.0, 1.0, 1.0)), ridge * 0.35)
    lm = None
    if lume:
        s0, s1 = lume_len[0] * length, lume_len[1] * length
        w = wb * 0.45
        lm = poly([(ux * s0 - tx * w / 2, uy * s0 - ty * w / 2), (ux * s1 - tx * w / 4, uy * s1 - ty * w / 4),
                   (ux * s1 + tx * w / 4, uy * s1 + ty * w / 4), (ux * s0 + tx * w / 2, uy * s0 + ty * w / 2)])
        col = over(col, np.array(lume) * (0.85 + 0.15 * rb.gauss(lm, 0.4 * K))[..., None], lm * 0.95)
    return col, m, lm


def logo_layer(cx, cy, width):
    rgb, a = rb.prep_logo(str(LOGO))
    w = int(round(width * K)); h = int(round(w * a.shape[0] / a.shape[1]))
    rgb_s, a_s = rb.resize_premult(rgb, a, w, h)
    full_a = np.zeros((S, S), np.float32); full_rgb = np.zeros((S, S, 3), np.float32)
    x0 = int(round(C + cx * K - w / 2)); y0 = int(round(C + cy * K - h / 2))
    full_a[y0:y0 + h, x0:x0 + w] = a_s; full_rgb[y0:y0 + h, x0:x0 + w] = rgb_s
    return full_rgb, full_a


def crystal(col):
    """Sapphire crystal: faint diagonal reflection and darkening near the rim."""
    refl = np.clip(1 - np.abs((xx + yy * 0.8) + 120) / 70.0, 0, 1) * np.clip((150 - rr) / 150, 0, 1)
    col = col + (refl * 0.035)[..., None]
    col = col * (1 - 0.25 * np.clip((rr - 205) / 15, 0, 1) * (rr < 213))[..., None]
    return col


def finish(col, out):
    col = col * np.clip((233 - rr) / 0.6 + 0.5, 0, 1)[..., None]
    col = col + RNG.normal(0, 0.003, col.shape).astype(np.float32)
    img = Image.fromarray(np.clip(col * 255 + 0.5, 0, 255).astype(np.uint8), "RGB").resize((932, 932), Image.LANCZOS)
    img.save(out, optimize=True)
    print(out)


def brushed_ring(r0, r1, base, radial=False):
    m = ring(0, 0, r0, r1)
    n = rb.gauss(RNG.normal(0, 1, (S, S)).astype(np.float32), 0.5)
    rbin = np.clip((rr * K * 1.6).astype(np.int32), 0, int(S * 1.2))
    streak = rb.gauss(RNG.normal(0, 1, (1, int(S * 1.2) + 1)).astype(np.float32), 0.7)[0][rbin]
    # domed profile with a bevel on the inner edge; brushing smears the reflection along the ring
    t = np.clip((rr - r0) / (r1 - r0), 0, 1)
    slope_r = np.where(t < 0.15, -1.6, 0.9 * np.cos(t * math.pi))
    inv = 1.0 / np.maximum(rr, 1e-3)
    nx, ny, nz = slope_r * xx * inv * -1, slope_r * yy * inv * -1, np.ones_like(rr)
    nn = np.sqrt(nx * nx + ny * ny + nz * nz)
    rgb = env_metal(nx / nn, ny / nn, nz / nn, base, ceiling=0.30, spec=0.25, polish=40)
    return m, rgb * (1 + 0.06 * streak + 0.015 * n)[..., None]


# ----------------------------------------------------------------- data shown in the sketches
TIME = (10, 8, 32)
GLUCOSE, TREND = 112, "→"
BATTERY = 76
DAY, WEEKDAY = 23, "LUN"
TEMP = "8°"
GOLD = (0.80, 0.66, 0.40)
STEEL = (0.78, 0.79, 0.81)
LUME = (0.86, 0.98, 0.88)
LUME_GLOW = (0.45, 1.0, 0.62)
RED, AMBER, OK_GOLD = (0.86, 0.26, 0.22), (0.89, 0.62, 0.20), (0.85, 0.72, 0.45)


def hand_angles():
    h, m, s = TIME
    return (h % 12 + m / 60) * 30, (m + s / 60) * 6, s * 6


def glucose_color(v):
    return RED if v < 70 else AMBER if v > 180 else OK_GOLD


def sun_icon(cx, cy, r):
    m = disk(cx, cy, r * 0.45)
    for i in range(8):
        m = np.maximum(m, baton(i * 45, r * 0.62, r, r * 0.16, cx=cx, cy=cy))
    return m


def runner_icon(cx, cy, s):
    """Simple stick figure (stand-in for the OHealth activity icon)."""
    def seg(x0, y0, x1, y1, w):
        dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy); nx, ny = -dy / L * w / 2, dx / L * w / 2
        return poly([(cx + (x0 + nx) * s, cy + (y0 + ny) * s), (cx + (x1 + nx) * s, cy + (y1 + ny) * s),
                     (cx + (x1 - nx) * s, cy + (y1 - ny) * s), (cx + (x0 - nx) * s, cy + (y0 - ny) * s)])
    m = disk(cx + 0.15 * s, cy - 0.78 * s, 0.17 * s)
    for args in [(0.1, -0.55, -0.05, 0.05, 0.16), (-0.05, 0.05, 0.3, 0.45, 0.15), (-0.05, 0.05, -0.4, 0.38, 0.15),
                 (0.3, 0.45, 0.2, 0.85, 0.14), (0.05, -0.4, 0.5, -0.15, 0.13), (0.05, -0.4, -0.45, -0.25, 0.13)]:
        m = np.maximum(m, seg(*args))
    return m


# ================================================================= NAVIGATOR
def navigator(out_dir: Path):
    col = np.zeros((S, S, 3), np.float32)
    # bezel: brushed steel 24 h ring with engraved numerals
    bm, brgb = brushed_ring(212.5, 233, (0.62, 0.63, 0.66))
    col = over(col, brgb, bm)
    eng = np.zeros((S, S), np.float32)
    for h in range(24):
        deg = h * 15
        if h % 2 == 0:
            eng = np.maximum(eng, text(str(h if h else 24), BARLOW, 10, *polar(222.5, deg), rot=deg))
        else:
            eng = np.maximum(eng, baton(deg, 219, 226, 1.4))
    col = over(col, np.array((0.06, 0.06, 0.07)), eng * 0.92)
    col = shadow(col, eng, -0.4, -0.5, 0.3, 0.0)  # engraving catches light on the lower edge
    col = over(col, np.array((0.02, 0.02, 0.02)), ring(0, 0, 211.5, 212.8))

    # rehaut (inclined minute ring) and dial
    reh = ring(0, 0, 196, 211.5)
    inv = 1.0 / np.maximum(rr, 1e-3)
    rnx, rny = -xx * inv * 0.55, -yy * inv * 0.55
    rn = np.sqrt(rnx ** 2 + rny ** 2 + 1)
    rndl = np.clip((rnx * LIGHT[0] + rny * LIGHT[1] + LIGHT[2]) / rn, 0, 1)
    col = over(col, np.array((0.13, 0.135, 0.145)) * (0.35 + 1.0 * rndl)[..., None], reh)
    ticks = np.zeros((S, S), np.float32)
    for m in range(60):
        ticks = np.maximum(ticks, baton(m * 6, 203 if m % 5 else 198, 210, 1.6 if m % 5 == 0 else 0.8))
    col = over(col, np.array((0.92, 0.92, 0.9)), ticks)

    dial = disk(0, 0, 196)
    streak = rb.gauss(RNG.normal(0, 1, (1, 4096)).astype(np.float32), 0.6)[0]
    abin = ((ang / (2 * math.pi) + 0.5) * 4095).astype(np.int32)
    sun = 0.5 + 0.5 * np.cos(2 * (ang - math.radians(315)))
    base = np.array((0.155, 0.165, 0.18))
    tone = (0.55 + 0.75 * sun ** 3 + 0.08 * streak[abin] * np.clip(rr / 40, 0, 1))
    col = over(col, base * tone[..., None], dial)
    # the dial sits below the rehaut: soft shadow along its edge, deeper at the top left
    col = col * (1 - 0.65 * rb.gauss(rb.shift(1 - dial, 1.8, 2.4), 2.6 * K) * dial)[..., None]
    # faint engraved world map under the sunburst
    polys = rb.load_land(str(GEO))
    land = mask(lambda d, k, c: rb.draw_land(d, k, c, polys))
    coast = np.clip(rb.gauss(land, 0.5 * K) * (1 - rb.gauss(land, 0.5 * K)) * 4, 0, 1)
    col = col * (1 - 0.35 * coast * dial)[..., None]

    # sub-dials: activity (9), weather (3), glucose gauge (6)
    subs = [(-95, 0, 42), (95, 0, 42), (0, 95, 48)]
    for cx, cy, r in subs:
        d = np.hypot(xx - cx, yy - cy)
        well = disk(cx, cy, r)
        snail = 0.5 + 0.5 * np.sin(2 * math.pi * d / 1.1)
        col = over(col, np.array((0.11, 0.115, 0.125)) * (0.9 + 0.18 * snail)[..., None], well)
        inner_sh = rb.gauss(rb.shift(1 - well, 1.2, 1.6), 1.2 * K) * well
        col = col * (1 - 0.6 * inner_sh)[..., None]
        rim = ring(cx, cy, r, r + 2.4)
        col = shadow(col, rim, 0.8, 1.0, 0.8, 0.5)
        col = over(col, metal(rim, STEEL, bevel=0.6, polish=70), rim)
        if (cx, cy) != (0, 95):
            t = np.zeros((S, S), np.float32)
            for i in range(30):
                t = np.maximum(t, baton(i * 12, r - (6 if i % 5 == 0 else 3.5), r - 1.2, 1.0, cx=cx, cy=cy))
            col = over(col, np.array((0.85, 0.85, 0.83)), t * 0.9)

    # activity icon and label
    col = over(col, np.array(GOLD) * 1.05, runner_icon(-95, -2, 19))
    col = over(col, np.array((0.7, 0.7, 0.68)), text("ACTIVIDAD", BARLOW_M, 6.5, -95, 26))
    # weather
    col = over(col, np.array(GOLD) * 1.1, sun_icon(95, -14, 11))
    col = over(col, np.array((0.95, 0.95, 0.93)), text(TEMP, BARLOW, 22, 96, 13))

    # glucose gauge: 40..300 over 270 deg, red / gold / amber zones
    gcx, gcy, gr = 0, 95, 48
    def g2deg(v):
        return -135 + 270 * (np.clip(v, 40, 300) - 40) / 260
    for lo, hi, c in [(40, 70, RED), (70, 180, OK_GOLD), (180, 300, AMBER)]:
        col = over(col, np.array(c), arc_mask(gcx, gcy, gr - 6, 3.2, g2deg(lo), g2deg(hi)))
    t = np.zeros((S, S), np.float32)
    for v in range(40, 301, 20):
        t = np.maximum(t, baton(g2deg(v), gr - 13, gr - 8, 1.0, cx=gcx, cy=gcy))
    col = over(col, np.array((0.85, 0.85, 0.83)), t)
    for v in (70, 180):
        col = over(col, np.array((0.8, 0.8, 0.78)), text(str(v), BARLOW_M, 7, *polar(gr - 20, g2deg(v), gcx, gcy)))
    # value window at the bottom of the gauge
    win = mask(lambda d, k, c: d.rounded_rectangle([c + (gcx - 17) * k, c + (gcy + 18) * k, c + (gcx + 17) * k,
                                                    c + (gcy + 34) * k], radius=3 * k, fill=255))
    frame = np.clip(mask(lambda d, k, c: d.rounded_rectangle([c + (gcx - 18.6) * k, c + (gcy + 16.4) * k,
                                                              c + (gcx + 18.6) * k, c + (gcy + 35.6) * k],
                                                             radius=4 * k, fill=255)) - win, 0, 1)
    col = over(col, np.array((0.03, 0.03, 0.035)), win)
    col = over(col, metal(frame, STEEL, bevel=0.4), frame)
    col = over(col, np.array(glucose_color(GLUCOSE)), text(f"{GLUCOSE}", BARLOW, 13, gcx - 4, gcy + 26))
    col = over(col, np.array(glucose_color(GLUCOSE)), text(TREND, SYMBOLS, 10, gcx + 10, gcy + 26))
    col = over(col, np.array((0.6, 0.6, 0.58)), text("mg/dL", BARLOW_M, 6, gcx, gcy - 16))
    col, gm, _ = faceted_hand_at(col, g2deg(GLUCOSE), gr - 8, gcx, gcy)
    cap = disk(gcx, gcy, 3.4)
    col = over(col, metal(cap, STEEL, bevel=0.6), cap)

    # applied indices (polished steel with lume insert)
    idx_lume = np.zeros((S, S), np.float32)
    for h in range(12):
        deg = h * 30
        if h in (3, 9):
            continue
        r0 = 176 if h != 6 else 182
        if h == 0:  # double baton at 12, each with its own lume strip
            parts = [(baton(deg + o, 170, 193, 4.6, 4.0), baton(deg + o, 173, 190, 1.6)) for o in (-1.8, 1.8)]
        else:
            parts = [(baton(deg, r0, 193, 6.5, 5.5), baton(deg, r0 + 3, 190, 2.2))]
        for p, ins in parts:
            col = shadow(col, p, 1.3, 1.7, 1.2, 0.65)
            col = over(col, metal(p, STEEL, bevel=0.7, polish=80), p)
            idx_lume = np.maximum(idx_lume, ins)
    col = over(col, np.array(LUME) * 0.92, idx_lume)
    for h in (3, 9):
        p = baton(h * 30, 184, 193, 6.5, 5.5)
        col = shadow(col, p, 1.3, 1.7, 1.2, 0.65)
        col = over(col, metal(p, STEEL, bevel=0.7, polish=80), p)

    # logo (applied) and power reserve (battery)
    lrgb, la = logo_layer(0, -122, 60)
    col = col * (1 - 0.6 * rb.gauss(rb.shift(la, 0.9, 1.2), 1.0 * K) * (1 - la))[..., None]
    col = over(col, lrgb, la)
    col = over(col, np.array((0.78, 0.78, 0.76)), text("NAVIGATOR", BARLOW_M, 8, 0, -84))
    pcx, pcy = 0, -30
    pr = np.zeros((S, S), np.float32)
    for i in range(11):
        pr = np.maximum(pr, baton(-50 + i * 10, 26, 30 if i % 5 else 33, 0.9 if i % 5 else 1.4, cx=pcx, cy=pcy))
    col = over(col, np.array((0.85, 0.85, 0.83)), pr)
    col = over(col, np.array((0.7, 0.7, 0.68)), text("0", BARLOW_M, 6.5, *polar(38, -50, pcx, pcy)))
    col = over(col, np.array((0.7, 0.7, 0.68)), text("100", BARLOW_M, 6.5, *polar(39, 50, pcx, pcy)))
    col = over(col, np.array((0.6, 0.6, 0.58)), text("RESERVA", BARLOW_M, 5.5, pcx, pcy - 13))
    col, _, _ = faceted_hand_at(col, -50 + BATTERY, 27, pcx, pcy)

    # date window at 4:30
    dx, dy = polar(160, 135)
    a = math.radians(135 - 90)
    def rot(px, py):
        return dx + px * math.cos(a) - py * math.sin(a), dy + px * math.sin(a) + py * math.cos(a)
    win = poly([rot(-12, -8), rot(12, -8), rot(12, 8), rot(-12, 8)])
    fr = np.clip(poly([rot(-13.6, -9.6), rot(13.6, -9.6), rot(13.6, 9.6), rot(-13.6, 9.6)]) - win, 0, 1)
    col = col * (1 - 0.5 * rb.gauss(rb.shift(win, 0.0, 0.0), 0.1))[..., None]
    col = over(col, np.array((0.93, 0.92, 0.88)), win)
    col = over(col, metal(fr, STEEL, bevel=0.4), fr)
    col = over(col, np.array((0.05, 0.05, 0.05)), text(str(DAY), BARLOW, 12, dx, dy, rot=135 - 90))

    # hands
    hd, md, sd = hand_angles()
    col, hm, hl = faceted_hand(col, hd, 118, 18, 10, 6, STEEL, lume=LUME)
    col, mm, ml = faceted_hand(col, md, 176, 22, 8, 4.5, STEEL, lume=LUME, lume_len=(0.22, 0.86))
    pts, (ux, uy, tx, ty) = hand_poly(sd, 190, 42, 1.2, 0.8, "needle")
    sm = poly(pts)
    col = shadow(col, sm, 3.2, 4.2, 2.2, 0.55)
    col = over(col, np.array((0.88, 0.2, 0.15)), sm)
    tip = disk(ux * 150, uy * 150, 3.0)
    col = over(col, np.array((0.88, 0.2, 0.15)), tip)
    cap = disk(0, 0, 6.5)
    col = shadow(col, cap, 1.2, 1.6, 1.0, 0.6)
    col = over(col, metal(cap, STEEL, bevel=1.0, polish=90), cap)
    col = crystal(col)
    finish(col, out_dir / "navigator.png")

    # Always-On: only the lume glows, as a real watch in the dark
    aod = np.zeros((S, S, 3), np.float32)
    aod = aod + lume_glow(np.maximum.reduce([idx_lume, hl, ml]), LUME_GLOW) * 0.75
    aod = over(aod, np.array((0.22, 0.22, 0.22)), ticks * 0.6)
    aod = over(aod, np.array(glucose_color(GLUCOSE)) * 0.7, text(f"{GLUCOSE}", BARLOW, 13, gcx - 4, gcy + 26))
    aod = over(aod, np.array(glucose_color(GLUCOSE)) * 0.7, text(TREND, SYMBOLS, 10, gcx + 10, gcy + 26))
    aod = over(aod, np.array((0.35, 0.35, 0.35)), gm * 0.8)
    for lo, hi, c in [(40, 70, RED), (70, 180, OK_GOLD), (180, 300, AMBER)]:
        aod = over(aod, np.array(c) * 0.45, arc_mask(gcx, gcy, gr - 6, 2.0, g2deg(lo), g2deg(hi)))
    finish(aod, out_dir / "navigator_aod.png")


def faceted_hand_at(col, deg, length, cx, cy):
    a = math.radians(deg)
    ux, uy, tx, ty = math.sin(a), -math.cos(a), math.cos(a), math.sin(a)
    pts = [(cx - tx * 1.2, cy - ty * 1.2), (cx + ux * length, cy + uy * length), (cx + tx * 1.2, cy + ty * 1.2)]
    m = poly(pts)
    col = shadow(col, m, 1.0, 1.3, 0.9, 0.6)
    col = over(col, metal(m, STEEL, bevel=0.2), m)
    cap = disk(cx, cy, 2.6)
    col = over(col, metal(cap, STEEL, bevel=0.5), cap)
    return col, m, None


# ================================================================= NOCTURNE
def nocturne(out_dir: Path):
    col = np.zeros((S, S, 3), np.float32)
    # thin polished gold bezel with a step
    bez = ring(0, 0, 214, 233)
    t = np.clip((rr - 214) / 19, 0, 1)
    H = np.sin(t * math.pi) * 6 + (rr > 222) * 0.8
    nx, ny, nz = normals(rb.gauss(H.astype(np.float32), 0.6 * K), 1.5)
    gold_b = env_metal(nx, ny, nz, (0.95, 0.76, 0.45), ceiling=0.34, spec=0.6)
    col = over(col, gold_b, bez)
    col = over(col, np.array((0.02, 0.02, 0.03)), ring(0, 0, 212.8, 214.2))

    # dial: midnight blue. Clous de Paris centre, flat chapter ring
    navy = np.array((0.035, 0.065, 0.14))
    dial = disk(0, 0, 212.8)
    u = (xx + yy) / math.sqrt(2); v = (xx - yy) / math.sqrt(2)
    p = 3.0
    hob = np.minimum(1 - np.abs(((u / p) % 1) * 2 - 1), 1 - np.abs(((v / p) % 1) * 2 - 1))
    centre = disk(0, 0, 150)
    Hc = (hob * centre).astype(np.float32)
    nx, ny, nz = normals(rb.gauss(Hc, 0.15 * K), 1.6)
    ndl = np.clip(nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2], 0, 1)
    ndh = np.clip(nx * HALF[0] + ny * HALF[1] + nz * HALF[2], 0, 1)
    sheen = np.clip(1 - np.hypot(xx + 60, yy + 70) / 260, 0, 1)
    gu = navy * (0.6 + 1.1 * ndl + 0.6 * sheen)[..., None] + (ndh ** 30 * 0.25)[..., None] * np.array((0.6, 0.7, 1.0))
    col = over(col, navy * (0.8 + 0.6 * sheen)[..., None], dial)
    col = over(col, gu, centre)
    col = col * (1 - 0.7 * rb.gauss(rb.shift(1 - dial, 1.8, 2.4), 2.6 * K) * dial)[..., None]
    # chapter ring edge (slightly raised)
    edge = ring(0, 0, 149.4, 151.2)
    col = over(col, metal(edge, (0.86, 0.70, 0.42), bevel=0.3), edge)

    # printed gold Roman numerals and railroad track
    gold_print = np.zeros((S, S), np.float32)
    romans = ["XII", "I", "II", "III", "IIII", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
    for h, rn in enumerate(romans):
        if h in (3, 6, 9):
            continue
        deg = h * 30
        gold_print = np.maximum(gold_print, text(rn, BODONI, 24 if h else 26, *polar(178, deg), rot=deg))
    gold_print = np.maximum(gold_print, ring(0, 0, 202.2, 203.0))
    gold_print = np.maximum(gold_print, ring(0, 0, 208.6, 209.4))
    for m in range(60):
        gold_print = np.maximum(gold_print, baton(m * 6, 203, 208.6, 0.7 if m % 5 else 1.6))
    col = over(col, np.array((0.84, 0.70, 0.44)), gold_print)

    # moon phase at 12
    mx, my = 0, -92
    sky_disk = disk(mx, my, 34)
    aperture = sky_disk * (yy < my + 4)
    col = col * (1 - 0.6 * rb.gauss(rb.shift(aperture, 1.0, 1.4), 1.0 * K) * (1 - aperture))[..., None]
    lapis = np.array((0.06, 0.12, 0.36)) * (0.8 + 0.4 * np.clip(-(yy - my) / 34, 0, 1))[..., None]
    col = over(col, lapis, aperture)
    stars = np.zeros((S, S), np.float32)
    for sx, sy, sr in [(-22, -16, 1.2), (-12, -26, 0.8), (6, -28, 1.0), (19, -18, 1.3), (25, -6, 0.8),
                       (-27, -4, 0.9), (13, -8, 0.7)]:
        stars = np.maximum(stars, disk(mx + sx, my + sy, sr))
    col = over(col, np.array((0.95, 0.82, 0.52)), stars * aperture)
    moon = disk(mx - 6, my - 10, 12) * aperture
    mnx, mny, mnz = normals(rb.gauss(moon, 3.0 * K), 3.0)
    mdl = np.clip(mnx * LIGHT[0] + mny * LIGHT[1] + mnz * LIGHT[2], 0, 1)
    col = over(col, np.array((0.93, 0.79, 0.50)) * (0.35 + 0.85 * mdl)[..., None], moon)
    # the two humps of a classic moon-phase aperture
    humps = (disk(mx - 30, my + 4, 15) + disk(mx + 30, my + 4, 15)) * aperture
    col = over(col, navy * 0.9, np.clip(humps, 0, 1))
    arch = np.clip(ring(mx, my, 34, 35.6) * (yy < my + 4), 0, 1)
    col = over(col, metal(arch, (0.86, 0.70, 0.42), bevel=0.3), arch)

    # logo printed in gold under the moon
    lrgb, la = logo_layer(0, -42, 54)
    col = over(col, lrgb, la)

    # sub-dials 9 (activity + battery reserve) and 3 (weather), recessed with snailing
    for cx in (-90, 90):
        cy, r = 8, 36
        d = np.hypot(xx - cx, yy - cy)
        well = disk(cx, cy, r)
        snail = 0.5 + 0.5 * np.sin(2 * math.pi * d / 0.9)
        col = over(col, navy * (0.75 + 0.35 * snail)[..., None], well)
        col = col * (1 - 0.55 * rb.gauss(rb.shift(1 - well, 1.2, 1.6), 1.1 * K) * well)[..., None]
        rr_ = ring(cx, cy, r, r + 1.6)
        col = over(col, metal(rr_, (0.86, 0.70, 0.42), bevel=0.3), rr_)
    # 9: activity, small reserve scale on top
    col = over(col, np.array((0.86, 0.72, 0.46)), runner_icon(-90, 14, 15))
    pr = np.zeros((S, S), np.float32)
    for i in range(6):
        pr = np.maximum(pr, baton(-60 + i * 24, 24, 29, 0.9, cx=-90, cy=8))
    col = over(col, np.array((0.84, 0.70, 0.44)), pr)
    col, _, _ = faceted_hand_at(col, -60 + 1.2 * BATTERY, 25, -90, 8)
    # 3: weather and the date under it
    col = over(col, np.array((0.9, 0.76, 0.48)), sun_icon(90, -6, 10))
    col = over(col, np.array((0.92, 0.90, 0.84)), text(TEMP, BODONI, 18, 92, 18))

    # glucose: retrograde fan at 6 (40..300 over 120 deg), blued-steel hand
    fx, fy, fr = 0, 40, 74
    def f2deg(v):
        return 240 - 120 * (np.clip(v, 40, 300) - 40) / 260 + 0
    for lo, hi, c in [(40, 70, RED), (70, 180, (0.84, 0.70, 0.44)), (180, 300, AMBER)]:
        a0, a1 = sorted((f2deg(lo), f2deg(hi)))
        col = over(col, np.array(c), arc_mask(fx, fy, fr, 2.6, a0, a1))
    t = np.zeros((S, S), np.float32)
    for v in range(40, 301, 20):
        t = np.maximum(t, baton(f2deg(v), fr - 7, fr - 2, 0.8, cx=fx, cy=fy))
    col = over(col, np.array((0.84, 0.70, 0.44)), t)
    for v in (70, 180):
        col = over(col, np.array((0.84, 0.70, 0.44)), text(str(v), BODONI, 8, *polar(fr - 14, f2deg(v), fx, fy)))
    col = over(col, np.array(glucose_color(GLUCOSE)), text(f"{GLUCOSE}", BODONI, 20, 0, 132))
    col = over(col, np.array((0.84, 0.70, 0.44)), text(TREND, SYMBOLS, 14, 26, 133))
    col = over(col, np.array((0.6, 0.6, 0.62)), text("mg/dL", BODONI, 7, 0, 146))
    # date at 6 in the chapter ring
    dwin = mask(lambda d, k, c: d.rectangle([c - 11 * k, c + 170 * k, c + 11 * k, c + 186 * k], fill=255))
    dfr = np.clip(mask(lambda d, k, c: d.rectangle([c - 12.6 * k, c + 168.4 * k, c + 12.6 * k, c + 187.6 * k],
                                                   fill=255)) - dwin, 0, 1)
    col = over(col, np.array((0.94, 0.92, 0.86)), dwin)
    col = over(col, metal(dfr, (0.86, 0.70, 0.42), bevel=0.3), dfr)
    col = over(col, np.array((0.05, 0.07, 0.14)), text(str(DAY), BODONI, 13, 0, 178))
    # glucose hand (blued steel, thin, with a small counterweight)
    a = math.radians(f2deg(GLUCOSE))
    ux, uy, tx, ty = math.sin(a), -math.cos(a), math.cos(a), math.sin(a)
    gm = poly([(fx - tx * 1.1 - ux * 8, fy - ty * 1.1 - uy * 8), (fx + ux * (fr - 3), fy + uy * (fr - 3)),
               (fx + tx * 1.1 - ux * 8, fy + ty * 1.1 - uy * 8)])
    col = shadow(col, gm, 1.4, 1.8, 1.2, 0.6)
    col = over(col, metal(gm, (0.18, 0.28, 0.75), bevel=0.2, polish=50), gm)
    gcap = disk(fx, fy, 3.2)
    col = over(col, metal(gcap, (0.18, 0.28, 0.75), bevel=0.6), gcap)

    # Breguet-style gold hands: hollow "pomme" near the tip
    hd, md, sd = hand_angles()
    def breguet(deg, length, w, ring_at, ring_r):
        a = math.radians(deg)
        ux, uy, tx, ty = math.sin(a), -math.cos(a), math.cos(a), math.sin(a)
        shaft = poly([(-ux * 16 - tx * w / 2, -uy * 16 - ty * w / 2), (ux * length - tx * 0.6, uy * length - ty * 0.6),
                      (ux * length + tx * 0.6, uy * length + ty * 0.6), (-ux * 16 + tx * w / 2, -uy * 16 + ty * w / 2)])
        o = ring(ux * ring_at, uy * ring_at, ring_r - 1.6, ring_r)
        hole = disk(ux * ring_at, uy * ring_at, ring_r - 1.6)
        return np.clip(np.maximum(shaft * (1 - hole), o), 0, 1)
    for deg, L, w, ra, rr_ in [(hd, 112, 4.2, 82, 7.5), (md, 172, 3.2, 140, 6.5)]:
        m = breguet(deg, L, w, ra, rr_)
        col = shadow(col, m, 2.6, 3.4, 2.0, 0.7)
        col = over(col, metal(m, (0.88, 0.72, 0.44), bevel=0.3, polish=80), m)
    pts, (ux, uy, tx, ty) = hand_poly(sd, 186, 30, 1.0, 0.6, "needle")
    sm = poly(pts)
    col = shadow(col, sm, 3.0, 4.0, 2.0, 0.5)
    col = over(col, metal(sm, (0.88, 0.72, 0.44), bevel=0.1), sm)
    cap = disk(0, 0, 5)
    col = shadow(col, cap, 1.2, 1.6, 1.0, 0.6)
    col = over(col, metal(cap, (0.88, 0.72, 0.44), bevel=1.0, polish=90), cap)
    col = crystal(col)
    finish(col, out_dir / "nocturne.png")

    # Always-On: moon, numerals and hands in dim gold, glucose in its colour
    aod = np.zeros((S, S, 3), np.float32)
    dim = np.array((0.42, 0.34, 0.20))
    aod = over(aod, dim, gold_print * 0.8)
    aod = over(aod, dim * 1.2, moon)
    aod = over(aod, dim, arch)
    for deg, L, w, ra, rr_ in [(hd, 112, 4.2, 82, 7.5), (md, 172, 3.2, 140, 6.5)]:
        aod = over(aod, dim * 1.5, breguet(deg, L, w, ra, rr_))
    aod = over(aod, np.array(glucose_color(GLUCOSE)) * 0.7, text(f"{GLUCOSE}", BODONI, 20, 0, 132))
    aod = over(aod, np.array((0.25, 0.32, 0.65)), gm)
    finish(aod, out_dir / "nocturne_aod.png")


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ART.parent / "docs/mockup/propuestas")
    out.mkdir(parents=True, exist_ok=True)
    navigator(out)
    nocturne(out)

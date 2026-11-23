"""Fondo de la esfera NVC para el OnePlus Watch 3.

Un unico mapa de alturas y una unica luz (arriba a la izquierda) para todo el
relieve, para que ninguna pieza contradiga a otra:
  - continentes: en relieve, meseta mate con bisel brillante
  - rayos y minuteria: grabados
  - sub-esferas y ventanas: hundidas, con aro dorado en relieve
  - indices: dorados en relieve
El logo se superpone con su propia sombra.

Uso: python -I render_bg.py <ne_50m_land.geojson> <logo.jpg> <carpeta_salida>
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

U = 466.0                 # unidades de diseno = pixeles reales del reloj
S = 1864                  # resolucion de trabajo (4x)
K = S / U
OUT = 932                 # exportacion (2x) para Watch Face Studio
C = S / 2.0

# ---------------- geometria (unidades de diseno, origen en el centro) -------
DIAL_R = 219.6
BEZEL_IN, BEZEL_OUT = 221.0, 233.0
# sub-esferas: x, y, radio del fondo, radio exterior del aro.
# La central es mayor y queda por encima: su aro corta los de las laterales.
CENTER_WELL = (0.0, 112.0, 50.0, 52.4)   # 12 mas abajo a peticion del usuario (2026-11-23); antes (0, 100) y (0, 88, 44, 46.4)
SIDE_WELLS = [(-82.0, 86.0, 41.0, 43.2), (82.0, 86.0, 41.0, 43.2)]   # antes (+-82, 74) y (+-72, 62, 36, 38.2)
WELLS = [CENTER_WELL] + SIDE_WELLS
WIN_W, WIN_H, WIN_RAD, WIN_FRAME = 66.0, 28.0, 5.5, 1.6   # agrandadas a peticion del usuario (2026-11-23; antes 58x24 y 46x19)
WINDOWS = [(138.0, 0.0), (-138.0, 0.0)]               # 3 h: fecha | 9 h: bateria
LOGO_CX, LOGO_CY, LOGO_W = 0.0, -123.0, 72.0   # subido 17 a peticion del usuario (2026-11-23); era -106

# ---------------- proyeccion del mapa (Mercator) ----------------------------
LON0 = 10.0               # meridiano central
XS = 1.04                 # unidades por grado
LAT_TOP, LAT_BOT, LAT_CUT = 84.0, -57.0, -58.0
YMID = -11.0              # sube un poco el mapa, como en la referencia
MIN_ISLAND = 6.0          # area minima de una isla, en unidades^2 (1 unidad = 1 px del reloj)
COAST_SMOOTH = 0.85       # suavizado de costa: cierra canales y redondea a escala de reloj


def merc(lat):
    lat = np.clip(lat, -85.0, 85.0)
    return np.degrees(np.log(np.tan(np.pi / 4 + np.radians(lat) / 2)))


M_MID = float((merc(LAT_TOP) + merc(LAT_BOT)) / 2)


def proj(lon, lat):
    x = (np.asarray(lon) - LON0) * XS
    y = -(merc(np.asarray(lat)) - M_MID) * XS + YMID
    return x, y


# ---------------- utilidades ------------------------------------------------
def box_blur(a, r):
    r = int(r)
    if r < 1:
        return a

    def one(x, axis):
        pad = [(0, 0)] * x.ndim
        pad[axis] = (r + 1, r)
        cs = np.cumsum(np.pad(x, pad, mode="edge"), axis=axis, dtype=np.float64)
        n = x.shape[axis]
        hi = np.take(cs, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
        lo = np.take(cs, np.arange(0, n), axis=axis)
        return ((hi - lo) / (2 * r + 1)).astype(np.float32)

    return one(one(a, 0), 1)


def gauss(a, sigma_px):
    """Aproximacion gaussiana con tres pasadas de caja."""
    if sigma_px <= 0.3:
        return a
    w = math.sqrt(4 * sigma_px * sigma_px + 1)
    r = max(1, int(round((w - 1) / 2)))
    for _ in range(3):
        a = box_blur(a, r)
    return a


def shift(a, dx, dy):
    """Desplaza en unidades de diseno."""
    return np.roll(np.roll(a, int(round(dy * K)), 0), int(round(dx * K)), 1)


def raster(draw_fn, ss=2):
    """Rasteriza con antialias (supermuestreo ss) y devuelve float 0..1."""
    im = Image.new("L", (S * ss, S * ss), 0)
    draw_fn(ImageDraw.Draw(im), K * ss, C * ss)
    im = im.reduce(ss)
    return np.asarray(im, dtype=np.float32) / 255.0


def bbox(cx, cy, r, k, c):
    return [c + (cx - r) * k, c + (cy - r) * k, c + (cx + r) * k, c + (cy + r) * k]


# ---------------- dibujo de mascaras ----------------------------------------
def load_land(path):
    with open(path, encoding="utf-8") as fh:
        geo = json.load(fh)
    polys = []
    for f in geo["features"]:
        g = f["geometry"]
        sets = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for rings in sets:
            ext = np.asarray(rings[0], dtype=np.float64)
            if ext[:, 1].max() < -50:          # Antartida y subantarticas fuera
                continue
            px, py = proj(ext[:, 0], ext[:, 1])
            area = 0.5 * abs(np.dot(px, np.roll(py, 1)) - np.dot(py, np.roll(px, 1)))
            if area < MIN_ISLAND:              # islas por debajo de lo que el reloj puede pintar
                continue
            polys.append([np.asarray(r, dtype=np.float64) for r in rings])
    return polys


def draw_land(d, k, c, polys):
    for rings in polys:
        for i, ring in enumerate(rings):
            if len(ring) < 3:
                continue
            x, y = proj(ring[:, 0], ring[:, 1])
            pts = list(zip((c + x * k).tolist(), (c + y * k).tolist()))
            d.polygon(pts, fill=255 if i == 0 else 0)


def draw_rays(d, k, c):
    w = max(1, int(round(0.55 * k)))
    for i in range(72):
        a = math.radians(i * 5)
        sx, sy = math.sin(a), -math.cos(a)
        d.line([(c + sx * 24 * k, c + sy * 24 * k), (c + sx * 200 * k, c + sy * 200 * k)],
               fill=255, width=w)


def draw_dots(d, k, c):
    for m in range(60):
        if m % 5 == 0:
            continue
        a = math.radians(m * 6)
        d.ellipse(bbox(math.sin(a) * 207, -math.cos(a) * 207, 1.30, k, c), fill=255)


def bar(d, k, c, ang_deg, r0, r1, w, off):
    a = math.radians(ang_deg)
    ux, uy = math.sin(a), -math.cos(a)      # radial
    tx, ty = math.cos(a), math.sin(a)       # tangencial
    pts = []
    for rr_, tt in ((r0, off - w / 2), (r1, off - w / 2), (r1, off + w / 2), (r0, off + w / 2)):
        pts.append((c + (ux * rr_ + tx * tt) * k, c + (uy * rr_ + ty * tt) * k))
    d.polygon(pts, fill=255)


def draw_idx(d, k, c):
    for h in range(12):
        if h % 3 == 0:
            for off in (-1.9, 1.9):
                bar(d, k, c, h * 30, 194, 212, 2.3, off)
        else:
            bar(d, k, c, h * 30, 197, 212, 2.6, 0)


def draw_disk(cx, cy, r):
    def fn(d, k, c):
        d.ellipse(bbox(cx, cy, r, k, c), fill=255)
    return fn


def draw_windows(grow):
    def fn(d, k, c):
        for cx, cy in WINDOWS:
            w, h = WIN_W / 2 + grow, WIN_H / 2 + grow
            d.rounded_rectangle([c + (cx - w) * k, c + (cy - h) * k, c + (cx + w) * k, c + (cy + h) * k],
                                radius=(WIN_RAD + grow) * k, fill=255)
    return fn


# ---------------- logo -------------------------------------------------------
def prep_logo(path):
    im = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    r, b = im[..., 0], im[..., 2]
    lum = im.max(-1)
    # el fondo de la imagen es gris neutro oscuro; el oro es claro o calido
    a = np.clip(np.maximum((lum - 0.15) / 0.22, (r - b - 0.045) / 0.10), 0, 1)
    ys, xs = np.where(a > 0.35)
    pad = 6
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, im.shape[0] - 1)
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, im.shape[1] - 1)
    return im[y0:y1 + 1, x0:x1 + 1], a[y0:y1 + 1, x0:x1 + 1]


def resize_premult(rgb, a, w, h):
    pre = np.dstack([rgb * a[..., None], a])
    img = Image.fromarray(np.clip(pre * 255 + 0.5, 0, 255).astype(np.uint8), "RGBA")
    # PIL trata RGBA como no premultiplicado: redimensionamos canal a canal
    chans = [np.asarray(Image.fromarray(np.asarray(img)[..., i]).resize((w, h), Image.LANCZOS),
                        dtype=np.float32) / 255.0 for i in range(4)]
    pa = np.clip(chans[3], 0, 1)
    out = np.dstack(chans[:3]) / np.maximum(pa[..., None], 1e-4)
    return np.clip(out, 0, 1), pa


# ---------------- programa principal ----------------------------------------
def main():
    geo_path, logo_path, outdir = sys.argv[1:4]
    mode = sys.argv[4] if len(sys.argv) > 4 else "alto"     # alto = relieve | bajo = bajo relieve
    sign = 1.0 if mode == "alto" else -1.0
    os.makedirs(outdir, exist_ok=True)

    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    xx = (xx + 0.5 - C) / K
    yy = (yy + 0.5 - C) / K
    rr = np.hypot(xx, yy)
    ang = np.arctan2(xx, -yy)                       # 0 = 12 h, sentido horario

    def circ(r, soft=0.35):
        return np.clip((r - rr) / soft + 0.5, 0, 1).astype(np.float32)

    print("mascaras...")
    polys = load_land(geo_path)
    land = raster(lambda d, k, c: draw_land(d, k, c, polys))
    land = np.clip((gauss(land, COAST_SMOOTH * K) - 0.5) / 0.10 + 0.5, 0, 1)
    land *= circ(216.0, 1.0)
    _, y_cut = proj(0.0, LAT_CUT)
    land *= np.clip((float(y_cut) - yy) / 0.5, 0, 1)

    rays = raster(draw_rays)
    dots = raster(draw_dots)
    idx = raster(draw_idx)
    cx_, cy_, cr_, co_ = CENTER_WELL
    c_floor = raster(draw_disk(cx_, cy_, cr_))
    c_outer = raster(draw_disk(cx_, cy_, co_))
    wells_floor = c_floor.copy()
    wells_outer = c_outer.copy()
    rims = c_outer - c_floor
    for sx_, sy_, sr_, so_ in SIDE_WELLS:
        s_floor = raster(draw_disk(sx_, sy_, sr_))
        s_outer = raster(draw_disk(sx_, sy_, so_))
        wells_floor = np.maximum(wells_floor, s_floor * (1 - c_outer))
        wells_outer = np.maximum(wells_outer, s_outer)
        rims = rims + (s_outer - s_floor) * (1 - c_outer)
    rims = np.clip(rims, 0, 1)
    win_floor = raster(draw_windows(0.0))
    win_outer = raster(draw_windows(WIN_FRAME))

    covers = np.clip(wells_outer + win_outer, 0, 1)
    land_v = land * (1 - covers)
    fade = np.clip((rr - 24.0) / 40.0, 0, 1) * np.clip((203.0 - rr) / 2.0, 0, 1)
    rays_v = rays * fade * (1 - np.clip(land * 1.5, 0, 1)) * (1 - covers)
    gold = np.clip(idx + rims + (win_outer - win_floor), 0, 1)
    recess = np.clip(wells_floor + win_floor, 0, 1)

    print("relieve...")
    H = (sign * (1.45 if sign > 0 else 1.15) * gauss(land_v, (0.70 if sign > 0 else 0.90) * K)
         - 1.10 * gauss(rays_v, 0.18 * K)
         - 1.40 * gauss(dots, 0.30 * K)
         + 1.30 * gauss(gold, 0.30 * K)
         - 1.60 * gauss(recess, 0.45 * K))
    gy, gx = np.gradient(H)
    SL = 7.0
    nx, ny, nz = -gx * SL, -gy * SL, np.ones_like(H)

    # bisel exterior: aro abombado
    bezel = circ(BEZEL_OUT, 0.6) - circ(BEZEL_IN, 0.6)
    t = np.clip((rr - BEZEL_IN) / (BEZEL_OUT - BEZEL_IN), 0, 1)
    nr = -0.85 * np.cos(np.pi * t)
    inv = 1.0 / np.maximum(rr, 1e-3)
    nx = nx * (1 - bezel) + nr * xx * inv * bezel
    ny = ny * (1 - bezel) + nr * yy * inv * bezel
    nn = np.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx / nn, ny / nn, nz / nn

    L = np.array([-0.55, -0.62, 0.56])
    L /= np.linalg.norm(L)
    Hv = L + np.array([0.0, 0.0, 1.0])
    Hv /= np.linalg.norm(Hv)
    ndl = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    ndh = np.clip(nx * Hv[0] + ny * Hv[1] + nz * Hv[2], 0, 1)

    print("materiales...")
    rng = np.random.default_rng(7)
    sheen = np.clip(1 - np.hypot(xx + 60, yy + 80) / 320.0, 0, 1)
    grain = gauss(rng.normal(0, 1, (S, S)).astype(np.float32), 0.6)

    ocean = 0.060 + 0.020 * sheen - 0.028 * rays_v - 0.032 * dots
    if sign > 0:
        land_alb = 0.112 + 0.022 * sheen + 0.008 * grain
    else:
        land_alb = 0.135 + 0.030 * sheen + 0.022 * grain     # fondo fresado y granallado, mas claro que el oceano para que el mapa se lea en el reloj (2026-11-23)
    alb = ocean * (1 - land_v) + land_alb * land_v

    d_c = np.hypot(xx - CENTER_WELL[0], yy - CENTER_WELL[1])
    d_s = np.min(np.stack([np.hypot(xx - w[0], yy - w[1]) for w in SIDE_WELLS]), axis=0)
    rl = np.where(c_outer > 0.5, d_c, d_s)
    azur = 0.5 + 0.5 * np.sin(2 * np.pi * rl / 0.95)       # caracoleado de las sub-esferas
    alb = alb * (1 - wells_floor) + (0.050 + 0.011 * azur) * wells_floor
    alb = alb * (1 - win_floor) + 0.046 * win_floor

    alb_rgb = np.dstack([alb * 0.985, alb, alb * 1.03])
    gold_rgb = np.array([0.66, 0.54, 0.33], dtype=np.float32)
    alb_rgb = alb_rgb * (1 - gold[..., None]) + gold_rgb * gold[..., None]

    rbin = np.clip((rr * K * 1.5).astype(np.int32), 0, int(S * 1.2))
    noise1d = gauss(rng.normal(0, 1, (1, int(S * 1.2) + 1)).astype(np.float32), 0.8)[0]
    bez_alb = 0.185 + 0.030 * noise1d[rbin]
    alb_rgb = alb_rgb * (1 - bezel[..., None]) + np.dstack([bez_alb, bez_alb, bez_alb * 1.03]) * bezel[..., None]

    print("sombras...")
    if sign > 0:
        land_sh = gauss(shift(land_v, 1.0, 1.3), 1.1 * K) * (1 - land_v)
    else:   # en bajo relieve la sombra cae dentro del continente, junto al borde de arriba-izquierda
        land_sh = gauss(shift(1 - land_v, 1.0, 1.3), 1.1 * K) * land_v
    gold_sh = gauss(shift(gold, 0.6, 0.8), 0.7 * K) * (1 - gold)
    rec_sh = gauss(shift(1 - recess, 0.9, 1.1), 1.1 * K) * recess
    occl = (1 - 0.68 * land_sh) * (1 - 0.55 * gold_sh) * (1 - 0.65 * rec_sh)

    print("iluminacion...")
    col = alb_rgb * ((0.30 + 1.25 * ndl) * occl)[..., None]
    spec_g = ndh ** 28
    spec_m = ndh ** 12
    if sign > 0:
        gloss_w = 0.07 + 1.10 * np.clip(gauss(land_v, 1.2 * K) * 1.6, 0, 1)
    else:   # solo brillan las paredes del fresado, no el fondo
        lb = gauss(land_v, 1.0 * K)
        gloss_w = 0.07 + 0.80 * np.clip(lb * (1 - lb) * 4.0, 0, 1)
    col += (gloss_w * spec_g * (1 - gold) * (1 - bezel) * 0.85)[..., None]
    col += (gold * spec_m)[..., None] * np.array([1.0, 0.90, 0.68], dtype=np.float32) * 0.55

    a_l = math.radians(315)
    aniso = (np.clip(np.cos(ang - a_l), 0, 1) ** 3 * 0.20
             + np.clip(np.cos(ang - a_l - math.pi), 0, 1) ** 3 * 0.06)
    col += (bezel * (aniso + 0.18 * spec_m))[..., None] * np.array([0.85, 0.85, 0.88], dtype=np.float32)

    gap = np.exp(-((rr - 220.3) / 0.5) ** 2) + np.exp(-((rr - 232.6) / 0.45) ** 2)
    col *= (1 - 0.85 * np.clip(gap, 0, 1))[..., None]

    print("logo...")
    lrgb, la = prep_logo(logo_path)
    lw = int(round(LOGO_W * K))
    lh = int(round(lw * la.shape[0] / la.shape[1]))
    lrgb_s, la_s = resize_premult(lrgb, la, lw, lh)
    x0 = int(round(C + (LOGO_CX * K) - lw / 2))
    y0 = int(round(C + (LOGO_CY * K) - lh / 2))
    full_a = np.zeros((S, S), np.float32)
    full_a[y0:y0 + lh, x0:x0 + lw] = la_s
    full_rgb = np.zeros((S, S, 3), np.float32)
    full_rgb[y0:y0 + lh, x0:x0 + lw] = lrgb_s
    lsh = gauss(shift(full_a, 0.8, 1.0), 0.9 * K)
    col *= (1 - 0.6 * lsh * (1 - full_a))[..., None]
    col = col * (1 - full_a[..., None]) + full_rgb * full_a[..., None]

    col *= circ(BEZEL_OUT, 0.6)[..., None]
    col += rng.normal(0, 0.0035, col.shape).astype(np.float32)   # tramado anti-bandas

    img = Image.fromarray(np.clip(col * 255 + 0.5, 0, 255).astype(np.uint8), "RGB")
    img = img.resize((OUT, OUT), Image.LANCZOS)
    p_bg = os.path.join(outdir, "bg_%s.png" % mode)
    img.save(p_bg, optimize=True)

    lw2 = int(round(LOGO_W * 2))
    lh2 = int(round(lw2 * la.shape[0] / la.shape[1]))
    lr2, la2 = resize_premult(lrgb, la, lw2, lh2)
    logo_img = Image.fromarray(np.clip(np.dstack([lr2, la2]) * 255 + 0.5, 0, 255).astype(np.uint8), "RGBA")
    p_logo = os.path.join(outdir, "logo.png")
    logo_img.save(p_logo, optimize=True)

    print("ok:", p_bg, os.path.getsize(p_bg), "bytes |", p_logo, logo_img.size)


if __name__ == "__main__":
    main()

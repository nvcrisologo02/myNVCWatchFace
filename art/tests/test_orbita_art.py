"""Tests for the Orbita prints (plan 2026-11-26-orbita-build, task 3). Run: python -m pytest art/tests -v"""
import math
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "blender"))
import make_prints as mp  # noqa: E402

N, K, C = mp.N, mp.K, mp.C


def px(r, deg):
    a = math.radians(deg)
    return round(C + r * math.sin(a) * K), round(C - r * math.cos(a) * K)


@pytest.fixture(scope="module")
def out(tmp_path_factory):
    d = tmp_path_factory.mktemp("orbita")
    mp.orbita(d)
    return d


def test_prints_deterministic(out, tmp_path):
    mp.orbita(tmp_path)
    for name in ("orbita_print_bg.png", "orbita_map.png", "orbita_ring_mask.png", "orbita_step_marker.png"):
        assert (out / name).read_bytes() == (tmp_path / name).read_bytes(), name


def test_bg_print_has_no_dynamic_content(out):
    im = Image.open(out / "orbita_print_bg.png").convert("RGBA")
    for deg in range(-20, 61):
        for r in range(200, 228):
            p = im.getpixel(px(r, deg))
            assert not (p[3] > 128 and p[0] > 200 and p[1] < 120 and p[2] < 80), (r, deg)  # no orange marker
    for centre in (206, 149):  # battery and heart-rate text zones: transparent
        for deg in range(centre - 12, centre + 13, 2):
            for r in range(205, 222, 2):
                assert im.getpixel(px(r, deg))[3] == 0, (centre, r, deg)


def test_ring_mask_sectors(out):
    m = Image.open(out / "orbita_ring_mask.png").convert("L")
    assert m.getpixel(px(213, 90)) == 255
    assert m.getpixel(px(213, 270)) == 255
    for r, deg in ((213, 0), (213, 180), (190, 90)):
        assert m.getpixel(px(r, deg)) == 0, (r, deg)


def test_step_marker_geometry(out):
    a = Image.open(out / "orbita_step_marker.png").getchannel("A")
    x0, y0, x1, y1 = a.getbbox()
    assert C - 6 * K <= x0 and x1 <= C + 6 * K
    assert C - 227 * K <= y0 and y1 <= C - 200 * K


def test_band_icons_stay_off_the_coloured_sectors(out):
    """Dark band ink (the shoe) must not land on the coloured sectors: the watch tints them (user, 2026-11-26)."""
    im = Image.open(out / "orbita_print_bg.png").convert("RGBA")
    m = Image.open(out / "orbita_ring_mask.png").convert("L")
    for deg in range(-55, -40):  # between the 10 (whose shadow belongs on the sector) and the steps
        for r in range(203, 224):
            x, y = px(r, deg)
            p = im.getpixel((x, y))
            dark = p[3] > 64 and max(p[:3]) < 120
            assert not (dark and m.getpixel((x, y)) > 0), (r, deg)

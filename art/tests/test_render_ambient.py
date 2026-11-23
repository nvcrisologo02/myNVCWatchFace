"""Tests for the ambient dial generator. Run: python -m pytest art/tests -v"""
import sys
from pathlib import Path

from PIL import Image

ART = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ART))
from render_ambient import render_ambient  # noqa: E402

LOGO = ART / "out" / "logo.png"


def test_ambient_dial_is_deterministic(tmp_path):
    a = render_ambient(LOGO, tmp_path / "a")
    b = render_ambient(LOGO, tmp_path / "b")
    assert a.read_bytes() == b.read_bytes()


def test_ambient_dial_size_and_low_pixel_count(tmp_path):
    im = Image.open(render_ambient(LOGO, tmp_path)).convert("RGBA")
    assert im.size == (932, 932)
    lit = sum(1 for a in im.getchannel("A").getdata() if a > 16)
    assert lit / (932 * 932) < 0.03  # Always-On: very few lit pixels


def test_index_at_twelve_is_lit_and_centre_is_dark(tmp_path):
    im = Image.open(render_ambient(LOGO, tmp_path)).convert("RGBA")
    # 12 o'clock double bar at x = 233 +/- 1.9, r 194..212 -> y = 233-203 = 30 (x2 = 60)
    assert max(im.getpixel((466 + dx, 60))[3] for dx in range(-6, 7)) > 128
    assert im.getpixel((466, 466))[3] == 0

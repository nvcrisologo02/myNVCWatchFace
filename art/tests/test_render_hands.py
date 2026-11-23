"""Tests for the hand generator (plan, task 4). Run: python -I -m pytest art/tests -v"""
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from render_hands import HANDS, SCALE, render_hands  # noqa: E402


def opaque_rows(path):
    im = Image.open(path).convert("RGBA")
    alpha = im.getchannel("A")
    w, h = im.size
    rows = [y for y in range(h) if any(alpha.getpixel((x, y)) > 8 for x in range(w))]
    return rows[0], rows[-1], h


def test_hands_are_deterministic(tmp_path):
    a = render_hands(tmp_path / "a")
    b = render_hands(tmp_path / "b")
    assert [p.name for p in a] == [p.name for p in b]
    assert [p.read_bytes() for p in a] == [p.read_bytes() for p in b]


@pytest.mark.parametrize("name,reach,tail", [
    ("hand_hour", 117, None),
    ("hand_minute", 177, None),
    ("hand_second", 189, 37),
])
def test_hand_lengths_match_spec(tmp_path, name, reach, tail):
    paths = {p.stem: p for p in render_hands(tmp_path)}
    top, bottom, _ = opaque_rows(paths[name])
    pivot = HANDS[name]["pivot_px"]
    assert (pivot - top) / SCALE == pytest.approx(reach, abs=1)
    if tail is not None:
        assert (bottom - pivot) / SCALE == pytest.approx(tail, abs=1)


@pytest.mark.parametrize("name", ["hand_hour", "hand_minute", "hand_second"])
def test_pivot_ratio_matches_image(tmp_path, name):
    paths = {p.stem: p for p in render_hands(tmp_path)}
    h = Image.open(paths[name]).size[1]
    assert HANDS[name]["pivot_y"] == pytest.approx(HANDS[name]["pivot_px"] / h, abs=1e-4)


def test_ambient_hands_have_hollow_centre(tmp_path):
    paths = {p.stem: p for p in render_hands(tmp_path)}
    im = Image.open(paths["hand_minute_aod"]).convert("RGBA")
    w, _ = im.size
    y = HANDS["hand_minute_aod"]["pivot_px"] - 80 * SCALE
    assert im.getpixel((w // 2, y))[3] == 0  # outline only: the middle is transparent

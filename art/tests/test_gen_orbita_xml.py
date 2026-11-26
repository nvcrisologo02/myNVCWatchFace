"""Tests for scripts/gen_orbita_xml.py (plan 2026-11-26-orbita-build, task 5).
Run: python -m pytest art/tests -v"""
import importlib.util
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("gen_orbita_xml", ROOT / "scripts/gen_orbita_xml.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

WHITE, RED, AMBER, GREY = "#fff0f0ec", "#ffe5483c", "#ffe3a63a", "#ff8c8a84"


@pytest.fixture(scope="module")
def xml():
    return gen.build_xml()


@pytest.fixture(scope="module")
def tree(xml):
    return ET.fromstring(xml.encode("utf-8"))


def slot(tree, sid):
    return next(s for s in tree.iter("ComplicationSlot") if s.get("slotId") == str(sid))


def test_marker_angle_is_clamped():
    expr = gen.MARKER_ANGLE.replace(" ", "")
    assert "clamp([STEP_PERCENT],0,100)" in expr
    assert expr.startswith("-14+68*")


def test_glucose_thresholds(tree):
    g = slot(tree, gen.GLUCOSE_SLOT)
    text = ET.tostring(g, encoding="unicode")
    v = "round([COMPLICATION.RANGED_VALUE_VALUE])"  # colour follows the number shown: 180.4 is "180", white
    for cond in (f"{v} &lt; 70", f"{v} &gt; 180"):
        assert cond in text or cond.replace("&lt;", "<").replace("&gt;", ">") in text, cond
    for colour in (WHITE, RED, AMBER):
        assert colour in text
    nodata = [f for f in g.iter("Font") if f.get("color") == GREY]
    assert nodata and "--" in "".join(nodata[0].itertext())


def test_glucose_value_size_and_no_trend(tree):
    g = slot(tree, gen.GLUCOSE_SLOT)
    sizes = {f.get("size") for f in g.iter("Font")}
    assert sizes == {"48"}
    assert "subText" not in ET.tostring(g, encoding="unicode")  # no trend arrow


def test_glucose_slot_ranged_only(tree):
    assert slot(tree, gen.GLUCOSE_SLOT).get("supportedTypes") == "RANGED_VALUE EMPTY"


def test_workout_slot_invisible(tree):
    s = slot(tree, gen.WORKOUT_SLOT)
    x, y, w, h = (int(s.get(k)) for k in ("x", "y", "width", "height"))
    a = math.radians(-33)
    cx, cy = 233 + 213 * math.sin(a), 233 - 213 * math.cos(a)
    assert x <= cx <= x + w and y <= cy <= y + h
    for c in s.iter("Complication"):
        assert not list(c.iter("PartText")) and not list(c.iter("PartImage"))


def test_colour_config(tree):
    cfg = tree.find("UserConfigurations/ColorConfiguration")
    assert cfg.get("id") == "colorAnillo"
    opts = cfg.findall("ColorOption")
    assert len(opts) == 5
    green = next(o for o in opts if o.get("displayName") == "verde")
    assert cfg.get("defaultValue") == green.get("id")
    rings = [p for p in tree.iter("PartImage") if p.get("tintColor") == "[CONFIGURATION.colorAnillo]"]
    assert len(rings) == 1


def test_heart_rate_no_reading(xml):
    hr = xml[xml.index("<!-- heart rate"):]
    hr = hr[:hr.index("<!-- end heart rate")]
    assert "[HEART_RATE]" in hr and "--" in hr and "BPM" in hr


def test_integer_geometry(tree):
    for el in tree.iter():
        for k in ("x", "y", "width", "height", "size", "centerX", "centerY"):
            v = el.get(k)
            if v is not None and not v.startswith("["):
                assert re.fullmatch(r"-?\d+", v), (el.tag, k, v)


def test_fixed_font_text_is_inline(xml):
    """A fixed text with newlines/indent round it is not drawn by the watch inside TextCircular (watch, 2026-11-26)."""
    for m in re.finditer(r"<Font [^>]*>(.*?)</Font>", xml, re.S):
        inner = m.group(1)
        if "<Template>" not in inner:
            assert inner == inner.strip() and "\n" not in inner, repr(inner)

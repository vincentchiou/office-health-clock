# tests/test_utils.py — ui/utils 共用工具測試

import pytest
from ui.utils import hex_to_rgb, rgb_to_hex, brighten, lerp_color


class TestHexToRgb:
    def test_white(self):
        assert hex_to_rgb("#ffffff") == (255, 255, 255)

    def test_black(self):
        assert hex_to_rgb("#000000") == (0, 0, 0)

    def test_without_hash(self):
        assert hex_to_rgb("ff8800") == (255, 136, 0)

    def test_mixed(self):
        assert hex_to_rgb("#3b82f6") == (59, 130, 246)


class TestRgbToHex:
    def test_white(self):
        assert rgb_to_hex(255, 255, 255) == "#ffffff"

    def test_black(self):
        assert rgb_to_hex(0, 0, 0) == "#000000"


class TestBrighten:
    def test_no_change(self):
        result = brighten("#808080", 0.0)
        assert result == "#808080"

    def test_full_brighten(self):
        result = brighten("#000000", 1.0)
        assert result == "#ffffff"

    def test_partial_brighten(self):
        result = brighten("#000000", 0.5)
        r, g, b = hex_to_rgb(result)
        assert r == 127  # ~127.5
        assert g == 127
        assert b == 127


class TestLerpColor:
    def test_same_color(self):
        result = lerp_color("#000000", "#ffffff", 0.5)
        r, g, b = hex_to_rgb(result)
        assert r == 127  # ~127.5
        assert g == 127
        assert b == 127

    def test_start(self):
        result = lerp_color("#ff0000", "#0000ff", 0.0)
        assert hex_to_rgb(result) == (255, 0, 0)

    def test_end(self):
        result = lerp_color("#ff0000", "#0000ff", 1.0)
        assert hex_to_rgb(result) == (0, 0, 255)

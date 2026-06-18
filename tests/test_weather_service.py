# tests/test_weather_service.py — WeatherService 單元測試

import pytest
from urllib.error import URLError
from core.weather_service import WeatherService, WeatherSnapshot


class TestWeatherService:
    def test_initial_state(self):
        svc = WeatherService()
        # No snapshot yet
        assert svc._snapshot is None

    def test_weather_code_to_icon(self):
        assert WeatherService._weather_code_to_icon(0) == ("☀", "晴朗")
        assert WeatherService._weather_code_to_icon(1) == ("🌤", "多雲")
        assert WeatherService._weather_code_to_icon(3) == ("☁", "陰天")
        assert WeatherService._weather_code_to_icon(61) == ("🌧", "下雨")
        assert WeatherService._weather_code_to_icon(95) == ("⛈", "雷雨")

    def test_offset_hours(self):
        offset = WeatherService._offset_hours()
        assert isinstance(offset, int)
        # Taiwan should be UTC+8
        assert offset == 8

    def test_timezone_map_has_taipei(self):
        tz_map = WeatherService._timezone_map()
        assert "Taipei Standard Time" in tz_map
        assert tz_map["Taipei Standard Time"]["name"] == "台北"

    def test_offset_map_has_taiwan(self):
        offset_map = WeatherService._offset_map()
        assert 8 in offset_map
        assert offset_map[8]["name"] == "台北"

    def test_manual_location(self):
        svc = WeatherService()
        loc = {"name": "測試", "lat": 25.0, "lon": 121.5, "timezone": "Asia/Taipei"}
        svc.set_manual_location(loc)
        assert svc._manual_location == loc
        # Snapshot should be reset
        assert svc._snapshot is None

    def test_http_get_json_invalid_url(self):
        with pytest.raises((URLError, OSError)):
            WeatherService._http_get_json("https://invalid.example.com/json", timeout=2)

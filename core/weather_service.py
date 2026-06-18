# core/weather_service.py — 當地天氣資料抓取與快取

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging
import os
import threading
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WeatherSnapshot:
    location: str
    icon: str
    temperature_c: float | None
    wind_kmh: float | None
    rain_mm: float | None
    description: str
    updated_at: datetime


class WeatherService:
    """Fetches local weather from Open-Meteo without an API key."""

    def __init__(self, refresh_ttl_minutes: int = 120):
        self._refresh_ttl = timedelta(minutes=refresh_ttl_minutes)
        self._lock = threading.Lock()
        self._snapshot: WeatherSnapshot | None = None
        self._last_refresh: datetime | None = None
        self._location_cache: dict[str, object] | None = None
        self._manual_location: dict[str, object] | None = None

    def set_manual_location(self, location: dict[str, object] | None) -> None:
        with self._lock:
            self._manual_location = location
            self._snapshot = None
            self._last_refresh = None

    def get_snapshot(self, force: bool = False) -> WeatherSnapshot:
        now = datetime.now()
        with self._lock:
            if not force and self._snapshot and self._last_refresh:
                if now - self._last_refresh < self._refresh_ttl:
                    return self._snapshot

        snapshot = self._refresh()
        with self._lock:
            self._snapshot = snapshot
            self._last_refresh = now
        return snapshot

    def refresh_async(self, callback=None) -> None:
        def worker():
            snapshot = self.get_snapshot(force=True)
            if callback:
                callback(snapshot)

        threading.Thread(target=worker, daemon=True).start()

    def _refresh(self) -> WeatherSnapshot:
        with self._lock:
            manual = self._manual_location
        if manual:
            location = manual
        else:
            location = self._detect_location()
        if location is None:
            return WeatherSnapshot(
                location="--",
                icon="⛅",
                temperature_c=None,
                wind_kmh=None,
                rain_mm=None,
                description="無法取得",
                updated_at=datetime.now(),
            )

        try:
            return self._fetch_weather(location)
        except Exception as ex:
            logger.warning("Failed to fetch weather: %s", ex)
            return WeatherSnapshot(
                location=str(location.get("name") or "--"),
                icon="⛅",
                temperature_c=None,
                wind_kmh=None,
                rain_mm=None,
                description="無法取得",
                updated_at=datetime.now(),
            )

    def _detect_location(self) -> dict[str, object] | None:
        location = self._detect_location_via_ip()
        if location:
            with self._lock:
                self._location_cache = location
            return location

        location = self._detect_location_via_timezone()
        if location:
            with self._lock:
                self._location_cache = location
            return location

        with self._lock:
            return self._location_cache

    def _detect_location_via_ip(self) -> dict[str, object] | None:
        urls = [
            "https://ipapi.co/json/",
            "https://ipwho.is/",
        ]
        for url in urls:
            try:
                payload = self._http_get_json(url, timeout=5)
                if not payload:
                    continue

                if payload.get("success") is False:
                    continue

                lat = payload.get("latitude") or payload.get("lat")
                lon = payload.get("longitude") or payload.get("lon") or payload.get("lng")
                if lat is None or lon is None:
                    continue

                city = payload.get("region") or payload.get("city") or "當地"
                name = str(city)

                timezone = payload.get("timezone") or "auto"
                if isinstance(timezone, dict):
                    timezone = timezone.get("id") or "auto"

                return {
                    "name": name,
                    "lat": float(lat),
                    "lon": float(lon),
                    "timezone": timezone,
                }
            except Exception as ex:
                logger.debug("IP location detection failed for %s: %s", url, ex)
                continue
        return None

    def _detect_location_via_timezone(self) -> dict[str, object] | None:
        tz_name = None
        try:
            tz_name = datetime.now().astimezone().tzname()
        except Exception:
            tz_name = None

        if not tz_name:
            return None

        mapped = self._timezone_map().get(tz_name)
        if mapped:
            return mapped

        offset_hours = self._offset_hours()
        return self._offset_map().get(offset_hours)

    @staticmethod
    def _offset_hours() -> int | None:
        try:
            offset = datetime.now().astimezone().utcoffset()
            if offset is None:
                return None
            return int(offset.total_seconds() // 3600)
        except Exception:
            return None

    @staticmethod
    def _timezone_map() -> dict[str, dict[str, object]]:
        return {
            "Taipei Standard Time": {"name": "台北", "lat": 25.0330, "lon": 121.5654, "timezone": "Asia/Taipei"},
            "China Standard Time": {"name": "上海", "lat": 31.2304, "lon": 121.4737, "timezone": "Asia/Shanghai"},
            "Tokyo Standard Time": {"name": "東京", "lat": 35.6762, "lon": 139.6503, "timezone": "Asia/Tokyo"},
            "Korea Standard Time": {"name": "首爾", "lat": 37.5665, "lon": 126.9780, "timezone": "Asia/Seoul"},
            "Singapore Standard Time": {"name": "新加坡", "lat": 1.3521, "lon": 103.8198, "timezone": "Asia/Singapore"},
            "SE Asia Standard Time": {"name": "曼谷", "lat": 13.7563, "lon": 100.5018, "timezone": "Asia/Bangkok"},
            "UTC": {"name": "UTC", "lat": 0.0, "lon": 0.0, "timezone": "UTC"},
        }

    @staticmethod
    def _offset_map() -> dict[int, dict[str, object]]:
        return {
            8: {"name": "台北", "lat": 25.0330, "lon": 121.5654, "timezone": "Asia/Taipei"},
            9: {"name": "東京", "lat": 35.6762, "lon": 139.6503, "timezone": "Asia/Tokyo"},
            7: {"name": "曼谷", "lat": 13.7563, "lon": 100.5018, "timezone": "Asia/Bangkok"},
            1: {"name": "倫敦", "lat": 51.5072, "lon": -0.1276, "timezone": "Europe/London"},
            -5: {"name": "紐約", "lat": 40.7128, "lon": -74.0060, "timezone": "America/New_York"},
            -8: {"name": "洛杉磯", "lat": 34.0522, "lon": -118.2437, "timezone": "America/Los_Angeles"},
        }

    @staticmethod
    def _http_get_json(url: str, timeout: int = 5) -> dict | None:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read().decode("utf-8")
        return json.loads(data)

    def _fetch_weather(self, location: dict[str, object]) -> WeatherSnapshot:
        lat = float(location["lat"])
        lon = float(location["lon"])
        timezone = str(location.get("timezone") or "auto")
        params = {
            "latitude": f"{lat:.4f}",
            "longitude": f"{lon:.4f}",
            "current": "temperature_2m,weather_code,wind_speed_10m,precipitation",
            "timezone": timezone,
            "temperature_unit": "celsius",
        }
        url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)
        payload = self._http_get_json(url, timeout=8)
        current = payload.get("current", {}) if payload else {}

        temp = current.get("temperature_2m")
        wind = current.get("wind_speed_10m")
        rain = current.get("precipitation")
        code = int(current.get("weather_code", 0) or 0)
        icon, desc = self._weather_code_to_icon(code)

        return WeatherSnapshot(
            location=str(location.get("name") or "當地"),
            icon=icon,
            temperature_c=float(temp) if temp is not None else None,
            wind_kmh=float(wind) if wind is not None else None,
            rain_mm=float(rain) if rain is not None else None,
            description=desc,
            updated_at=datetime.now(),
        )

    @staticmethod
    def _weather_code_to_icon(code: int) -> tuple[str, str]:
        if code == 0:
            return "☀", "晴朗"
        if code in (1, 2):
            return "🌤", "多雲"
        if code == 3:
            return "☁", "陰天"
        if code in (45, 48):
            return "🌫", "霧"
        if code in (51, 53, 55, 56, 57):
            return "🌦", "毛毛雨"
        if code in (61, 63, 65, 66, 67):
            return "🌧", "下雨"
        if code in (71, 73, 75, 77):
            return "❄", "下雪"
        if code in (80, 81, 82):
            return "🌦", "陣雨"
        if code in (95, 96, 99):
            return "⛈", "雷雨"
        return "⛅", "天氣"

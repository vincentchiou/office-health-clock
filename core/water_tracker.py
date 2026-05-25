# core/water_tracker.py — 喝水記錄與持久化

import json
import os
from datetime import date, datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
LOG_FILE = os.path.join(DATA_DIR, "water_log.json")
TMP_FILE = LOG_FILE + ".tmp"


class WaterTracker:
    def __init__(self, target_ml: int = 2000):
        self._target_ml = target_ml
        self._today_key = ""
        self._today_total = 0
        self._today_records = []
        self._log = {}
        os.makedirs(DATA_DIR, exist_ok=True)
        self._load()
        self._ensure_today()

    # ── 公開 API ──────────────────────────────────────────

    def add_water(self, ml: int) -> int:
        self._ensure_today()
        now = datetime.now().strftime("%H:%M:%S")
        self._today_records.append({"time": now, "ml": ml})
        self._today_total += ml
        self._save()
        return self._today_total

    def get_today_total(self) -> int:
        self._ensure_today()
        return self._today_total

    def get_target(self) -> int:
        return self._target_ml

    def set_target(self, ml: int):
        self._target_ml = ml
        self._ensure_today()
        self._log[self._today_key]["target_ml"] = ml
        self._save()

    def is_goal_reached(self) -> bool:
        return self.get_today_total() >= self._target_ml

    def get_remaining(self) -> int:
        return max(0, self._target_ml - self.get_today_total())

    def get_today_records(self) -> list:
        self._ensure_today()
        return list(self._today_records)

    def check_and_reset_if_new_day(self):
        """每秒 tick 中呼叫，跨日自動重置。"""
        today = date.today().isoformat()
        if today != self._today_key:
            self._ensure_today()

    # ── 用藥追蹤 ──────────────────────────────────────────

    def is_med_taken(self) -> bool:
        self._ensure_today()
        return self._log[self._today_key].get("med_taken", False)

    def set_med_taken(self):
        self._ensure_today()
        self._log[self._today_key]["med_taken"] = True
        self._save()

    # ── 內部 ──────────────────────────────────────────────

    def _ensure_today(self):
        today = date.today().isoformat()
        if today == self._today_key:
            return
        self._today_key = today
        if today not in self._log:
            self._log[today] = {
                "target_ml": self._target_ml,
                "total_ml": 0,
                "records": [],
                "med_taken": False,
            }
        entry = self._log[today]
        self._today_total = entry.get("total_ml", 0)
        self._today_records = entry.get("records", [])

    def _load(self):
        if not os.path.exists(LOG_FILE):
            self._log = {}
            return
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                self._log = json.load(f)
        except (json.JSONDecodeError, OSError):
            self._log = {}

    def _save(self):
        key = self._today_key
        self._log[key]["total_ml"] = self._today_total
        self._log[key]["records"] = self._today_records
        try:
            with open(TMP_FILE, "w", encoding="utf-8") as f:
                json.dump(self._log, f, ensure_ascii=False, indent=2)
            os.replace(TMP_FILE, LOG_FILE)
        except OSError:
            pass

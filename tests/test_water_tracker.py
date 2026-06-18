# tests/test_water_tracker.py — WaterTracker 單元測試

import json
import os
import tempfile
from datetime import date, datetime
from unittest import mock

import pytest


@pytest.fixture
def tracker(tmp_path):
    """Create a fresh WaterTracker with a temp log file per test."""
    log_file = str(tmp_path / "water_log.json")
    
    with mock.patch("core.water_tracker.DATA_DIR", str(tmp_path)), \
         mock.patch("core.water_tracker.LOG_FILE", log_file), \
         mock.patch("core.water_tracker.TMP_FILE", log_file + ".tmp"):
        from core.water_tracker import WaterTracker
        return WaterTracker(target_ml=2000)


class TestWaterTracker:
    def test_initial_state(self, tracker):
        assert tracker.get_today_total() == 0
        assert tracker.get_target() == 2000
        assert not tracker.is_goal_reached()
        assert tracker.get_remaining() == 2000

    def test_add_water(self, tracker):
        total = tracker.add_water(500)
        assert total == 500
        assert tracker.get_today_total() == 500
        assert tracker.get_remaining() == 1500

    def test_add_water_multiple(self, tracker):
        tracker.add_water(300)
        tracker.add_water(200)
        tracker.add_water(100)
        assert tracker.get_today_total() == 600

    def test_goal_reached(self, tracker):
        tracker.add_water(2000)
        assert tracker.is_goal_reached()
        assert tracker.get_remaining() == 0

    def test_set_target(self, tracker):
        tracker.set_target(3000)
        assert tracker.get_target() == 3000
        assert tracker.get_remaining() == 3000

    def test_med_taken(self, tracker):
        assert not tracker.is_med_taken()
        tracker.set_med_taken()
        assert tracker.is_med_taken()

    def test_today_records(self, tracker):
        records = tracker.get_today_records()
        assert len(records) == 0

        tracker.add_water(250)
        records = tracker.get_today_records()
        assert len(records) == 1
        assert records[0]["ml"] == 250

    def test_day_rollover(self, tracker):
        tracker.add_water(500)
        # Simulate tomorrow by patching date
        import core.water_tracker as wt_mod
        original_date = wt_mod.date
        
        class FakeDate:
            @staticmethod
            def today():
                return original_date(2099, 1, 1)
            @staticmethod
            def isoformat():
                return "2099-01-01"
        
        with mock.patch.object(wt_mod, "date", FakeDate):
            tracker.check_and_reset_if_new_day()
            # Should have reset for the new day
            assert tracker.get_today_total() == 0

# tests/test_scheduler.py — Scheduler 單元測試

from unittest import mock

import pytest


class FakeRoot:
    """Mock tkinter root for testing Scheduler."""
    
    def __init__(self):
        self._counter = 0
        self._callbacks = {}
    
    def after(self, ms, callback):
        self._counter += 1
        self._callbacks[self._counter] = (ms, callback)
        return str(self._counter)
    
    def after_cancel(self, after_id):
        self._callbacks.pop(int(after_id), None)


@pytest.fixture
def root():
    return FakeRoot()


@pytest.fixture
def scheduler(root):
    from core.scheduler import Scheduler
    return Scheduler(root)


class TestScheduler:
    def test_schedule_and_fire(self, scheduler, root):
        called = []
        scheduler.schedule("test", 1000, lambda: called.append(True))
        
        # Simulate timer firing
        assert 1 in root._callbacks
        ms, cb = root._callbacks[1]
        assert ms == 1000
        cb()
        assert called == [True]

    def test_cancel(self, scheduler, root):
        scheduler.schedule("test", 1000, lambda: None)
        scheduler.cancel("test")
        assert "test" not in scheduler._after_ids

    def test_cancel_all(self, scheduler, root):
        scheduler.schedule("a", 1000, lambda: None)
        scheduler.schedule("b", 2000, lambda: None)
        scheduler.cancel_all()
        assert len(scheduler._after_ids) == 0

    def test_duplicate_schedule_cancels_first(self, scheduler, root):
        called = []
        scheduler.schedule("test", 1000, lambda: called.append("first"))
        scheduler.schedule("test", 2000, lambda: called.append("second"))
        
        # Only the second callback should be registered
        assert len(root._callbacks) == 1
        ms, cb = list(root._callbacks.values())[0]
        assert ms == 2000
        cb()
        assert called == ["second"]

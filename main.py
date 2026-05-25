# main.py — 辦公室健康時鐘 進入點

import ctypes
import json
import os
import random
import sys
import tkinter as tk
from datetime import datetime, time as dtime

# ── DPI 適配（必須在 tk.Tk() 之前）─────────────────────
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

import config
from core.scheduler import Scheduler
from core.water_tracker import WaterTracker
from ui.clock_window import ClockWindow
from ui.reminder_window import ReminderWindow

# ── 設定檔路徑 ────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")


def load_settings() -> dict:
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            s = dict(config.DEFAULT_SETTINGS)
            s.update(loaded)
            return s
        except Exception:
            pass
    return dict(config.DEFAULT_SETTINGS)


def save_settings(s: dict):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ── 設定對話框 ────────────────────────────────────────

def show_settings_dialog(root: tk.Tk, settings: dict, on_save):
    dlg = tk.Toplevel(root)
    dlg.title("設定")
    dlg.configure(bg=config.BG_COLOR)
    dlg.attributes("-topmost", True)
    dlg.resizable(False, False)
    dlg.grab_set()

    fields = [
        ("每日喝水目標 (ml)", "water_target_ml", int),
        ("下班小時 (0-23)", "end_of_work_hour", int),
        ("下班分鐘 (0-59)", "end_of_work_minute", int),
        ("久坐提醒間隔 (分鐘)", "exercise_interval_minutes", int),
        ("喝水提醒最短間隔 (分鐘)", "water_reminder_min_minutes", int),
        ("喝水提醒最長間隔 (分鐘)", "water_reminder_max_minutes", int),
        ("用藥提醒小時 (0-23)", "med_hour", int),
        ("用藥提醒分鐘 (0-59)", "med_minute", int),
    ]

    vars_ = {}
    for label, key, _ in fields:
        row = tk.Frame(dlg, bg=config.BG_COLOR)
        row.pack(fill="x", padx=16, pady=4)
        tk.Label(row, text=label, width=22, anchor="w",
                 font=config.FONT_SMALL, fg=config.DATE_COLOR,
                 bg=config.BG_COLOR).pack(side="left")
        var = tk.StringVar(value=str(settings.get(key, "")))
        vars_[key] = var
        tk.Entry(row, textvariable=var, width=8,
                 bg=config.BTN_BG, fg=config.CLOCK_COLOR,
                 insertbackground=config.CLOCK_COLOR,
                 relief="flat").pack(side="left", padx=4)

    def _save():
        for label, key, typ in fields:
            try:
                settings[key] = typ(vars_[key].get())
            except ValueError:
                pass
        on_save(settings)
        dlg.destroy()

    btn_row = tk.Frame(dlg, bg=config.BG_COLOR)
    btn_row.pack(pady=10)
    tk.Button(btn_row, text="儲存", command=_save,
              bg=config.WATER_COLOR, fg="white",
              font=config.FONT_BTN, relief="flat",
              padx=14, pady=4, cursor="hand2").pack(side="left", padx=6)
    tk.Button(btn_row, text="取消", command=dlg.destroy,
              bg=config.BTN_BG, fg=config.DATE_COLOR,
              font=config.FONT_BTN, relief="flat",
              padx=14, pady=4, cursor="hand2").pack(side="left", padx=6)

    dlg.bind("<Escape>", lambda e: dlg.destroy())
    # 置中
    dlg.update_idletasks()
    w, h = dlg.winfo_width(), dlg.winfo_height()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    dlg.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")


# ── 主應用邏輯 ────────────────────────────────────────

class App:
    def __init__(self):
        self._settings = load_settings()
        self._root = tk.Tk()
        self._root.withdraw()   # 先隱藏，建好視窗再顯示

        self._scheduler = Scheduler(self._root)
        self._tracker = WaterTracker(self._settings["water_target_ml"])
        self._reminder = ReminderWindow(self._root)

        self._exercise_elapsed = 0   # 已坐秒數
        self._exercise_interval_s = self._settings["exercise_interval_minutes"] * 60
        self._exercise_showing = False

        self._water_showing = False
        self._last_water_remind_time = None   # datetime

        self._med_showing = False

        self._clock = ClockWindow(
            self._root,
            self._settings,
            on_close=self._on_close,
            on_settings=self._on_settings,
        )

        self._root.deiconify()
        self._sync_water_display()
        self._sync_med_display()
        self._start_tick()
        self._schedule_water_reminder()
        self._schedule_eow_reminder()
        self._schedule_med_reminder()

    # ── 主計時 tick ───────────────────────────────────

    def _start_tick(self):
        self._scheduler.schedule("tick", 1000, self._tick)

    def _tick(self):
        # 跨日檢查
        self._tracker.check_and_reset_if_new_day()

        # 更新時鐘顯示
        self._clock.tick()
        self._sync_water_display()

        # 久坐計時
        if not self._exercise_showing:
            self._exercise_elapsed += 1
            remaining = self._exercise_interval_s - self._exercise_elapsed
            self._clock.set_exercise_remaining(remaining)
            if remaining <= 0:
                self._show_exercise()

        self._scheduler.schedule("tick", 1000, self._tick)

    # ── 久坐提醒 ─────────────────────────────────────

    def _show_exercise(self):
        self._exercise_showing = True
        elapsed_min = self._exercise_elapsed // 60
        self._reminder.show_exercise(
            elapsed_minutes=elapsed_min,
            on_close=self._after_exercise,
        )

    def _after_exercise(self):
        self._exercise_elapsed = 0
        self._exercise_showing = False

    # ── 喝水提醒 ─────────────────────────────────────

    def _schedule_water_reminder(self):
        if self._is_after_work():
            return
        min_m = self._settings.get("water_reminder_min_minutes", 30)
        max_m = self._settings.get("water_reminder_max_minutes", 90)
        delay_s = random.randint(min_m * 60, max_m * 60)
        self._scheduler.schedule("water_remind", delay_s * 1000,
                                 self._show_water_reminder)

    def _show_water_reminder(self):
        if self._tracker.is_goal_reached() or self._is_after_work():
            self._schedule_water_reminder()
            return
        self._water_showing = True
        self._last_water_remind_time = datetime.now()
        self._reminder.show_water(
            total_ml=self._tracker.get_today_total(),
            target_ml=self._tracker.get_target(),
            on_drink=self._record_water,
            on_skip=self._after_water_remind,
        )

    def _after_water_remind(self):
        self._water_showing = False
        self._schedule_water_reminder()

    def _record_water(self, ml: int):
        self._tracker.add_water(ml)
        self._sync_water_display()
        self._water_showing = False
        self._schedule_water_reminder()

    def _sync_water_display(self):
        self._clock.set_water(
            self._tracker.get_today_total(),
            self._tracker.get_target(),
        )

    # ── 用藥提醒 ─────────────────────────────────────

    def _schedule_med_reminder(self):
        if self._tracker.is_med_taken():
            return
        now = datetime.now()
        med_h = self._settings.get("med_hour", 13)
        med_m = self._settings.get("med_minute", 40)
        target = now.replace(hour=med_h, minute=med_m, second=0, microsecond=0)
        delay_s = target.timestamp() - now.timestamp()
        if delay_s > 0:
            self._scheduler.schedule("med_remind", int(delay_s * 1000),
                                     self._show_med_reminder)

    def _show_med_reminder(self):
        if self._tracker.is_med_taken() or self._med_showing:
            return
        self._med_showing = True
        taken = [False]

        def _on_taken():
            taken[0] = True
            self._tracker.set_med_taken()
            self._clock.set_med_taken(True)

        def _on_close():
            self._med_showing = False
            if not taken[0]:
                # 15 分鐘後再次提醒
                self._scheduler.schedule("med_remind", 15 * 60 * 1000,
                                         self._show_med_reminder)

        self._reminder.show_medicine(on_taken=_on_taken, on_close=_on_close)

    def _sync_med_display(self):
        taken = self._tracker.is_med_taken()
        self._clock.set_med_taken(taken)
        med_h = self._settings.get("med_hour", 13)
        med_m = self._settings.get("med_minute", 40)
        self._clock.set_med_time(med_h, med_m)

    # ── 下班前提醒 ────────────────────────────────────

    def _schedule_eow_reminder(self):
        now = datetime.now()
        eow_h = self._settings.get("end_of_work_hour", 17)
        eow_m = self._settings.get("end_of_work_minute", 30)
        target = now.replace(hour=eow_h, minute=eow_m, second=0, microsecond=0)
        remind_at = target.timestamp() - 30 * 60   # 下班前 30 分鐘
        delay_s = remind_at - now.timestamp()
        if delay_s > 0:
            self._scheduler.schedule("eow_remind", int(delay_s * 1000),
                                     self._show_eow_reminder)

    def _show_eow_reminder(self):
        if self._tracker.is_goal_reached():
            return
        self._reminder.show_eow_water(
            total_ml=self._tracker.get_today_total(),
            target_ml=self._tracker.get_target(),
            on_drink=self._record_water_eow,
            on_close=None,
        )

    def _record_water_eow(self, ml: int):
        self._tracker.add_water(ml)
        self._sync_water_display()

    # ── 工具 ──────────────────────────────────────────

    def _is_after_work(self) -> bool:
        now = datetime.now().time()
        eow = dtime(
            self._settings.get("end_of_work_hour", 17),
            self._settings.get("end_of_work_minute", 30),
        )
        return now >= eow

    # ── 關閉與設定 ────────────────────────────────────

    def _on_close(self):
        x, y = self._clock.get_position()
        self._settings["window_x"] = x
        self._settings["window_y"] = y
        save_settings(self._settings)
        self._scheduler.cancel_all()
        self._root.destroy()

    def _on_settings(self):
        def _save(new_settings):
            self._settings.update(new_settings)
            save_settings(self._settings)
            # 更新 tracker 目標
            self._tracker.set_target(new_settings["water_target_ml"])
            # 更新久坐間隔
            self._exercise_interval_s = new_settings["exercise_interval_minutes"] * 60
            # 重排喝水提醒
            self._scheduler.cancel("water_remind")
            self._schedule_water_reminder()
            # 重排下班提醒
            self._scheduler.cancel("eow_remind")
            self._schedule_eow_reminder()
            # 重排用藥提醒
            self._scheduler.cancel("med_remind")
            self._schedule_med_reminder()
            self._sync_med_display()
            self._sync_water_display()

        show_settings_dialog(self._root, self._settings, on_save=_save)

    # ── 啟動 ──────────────────────────────────────────

    def run(self):
        self._root.mainloop()


if __name__ == "__main__":
    App().run()

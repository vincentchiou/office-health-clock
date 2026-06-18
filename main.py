# main.py — 辦公室健康時鐘 進入點

import ctypes
import json
import logging
import os
import random
import sys
import tkinter as tk
from datetime import datetime, time as dtime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr),
    ],
)
logger = logging.getLogger(__name__)

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
from core.system_monitor import SystemMonitor
from core.weather_service import WeatherService
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
        except (json.JSONDecodeError, OSError) as ex:
            logger.warning("Failed to load settings, using defaults: %s", ex)
    return dict(config.DEFAULT_SETTINGS)


def save_settings(s: dict):
    tmp = SETTINGS_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=2)
        os.replace(tmp, SETTINGS_FILE)
    except OSError as ex:
        logger.error("Failed to save settings: %s", ex)


# ── 設定對話框（優化版）────────────────────────────────

def show_settings_dialog(root: tk.Tk, settings: dict, on_save):
    dlg = tk.Toplevel(root)
    dlg.title("設定")
    dlg.configure(bg=config.BG_COLOR)
    dlg.attributes("-topmost", True)
    dlg.resizable(False, False)
    dlg.grab_set()

    # 標題區域
    title_frame = tk.Frame(dlg, bg=config.BG_SECONDARY, height=40)
    title_frame.pack(fill="x")
    title_frame.pack_propagate(False)
    
    tk.Label(title_frame, text="⚙ 設定", 
             font=config.FONT_REMIND,
             fg=config.TEXT_PRIMARY, bg=config.BG_SECONDARY).pack(side="left", padx=16, pady=8)

    # 內容區域
    content_frame = tk.Frame(dlg, bg=config.BG_COLOR, padx=20, pady=16)
    content_frame.pack(fill="both", expand=True)

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
    for i, (label, key, _) in enumerate(fields):
        # 每個欄位一個容器
        field_frame = tk.Frame(content_frame, bg=config.BG_COLOR)
        field_frame.pack(fill="x", pady=4)
        
        # 標籤
        tk.Label(field_frame, text=label, width=22, anchor="w",
                 font=config.FONT_SMALL, fg=config.TEXT_SECONDARY,
                 bg=config.BG_COLOR).pack(side="left")
        
        # 輸入框（帶邊框效果）
        input_frame = tk.Frame(field_frame, bg=config.BORDER_COLOR, padx=1, pady=1)
        input_frame.pack(side="left", padx=(8, 0))
        
        var = tk.StringVar(value=str(settings.get(key, "")))
        vars_[key] = var
        
        entry = tk.Entry(input_frame, textvariable=var, width=10,
                         bg=config.BG_ELEVATED, fg=config.CLOCK_COLOR,
                         insertbackground=config.CLOCK_COLOR,
                         font=config.FONT_VALUE,
                         relief="flat", bd=0)
        entry.pack(padx=2, pady=2)
        
        # 輸入框focus效果
        def on_focus_in(e, frame=input_frame, ent=entry):
            frame.config(bg=config.BTN_PRIMARY)
            ent.config(bg=config.BG_TERTIARY)
        
        def on_focus_out(e, frame=input_frame, ent=entry):
            frame.config(bg=config.BORDER_COLOR)
            ent.config(bg=config.BG_ELEVATED)
        
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    # ── 天氣地區下拉選單 ──
    loc_frame = tk.Frame(content_frame, bg=config.BG_COLOR)
    loc_frame.pack(fill="x", pady=4)

    tk.Label(loc_frame, text="天氣地區", width=22, anchor="w",
             font=config.FONT_SMALL, fg=config.TEXT_SECONDARY,
             bg=config.BG_COLOR).pack(side="left")

    loc_names = list(config.TAIWAN_LOCATIONS.keys())
    current_loc = settings.get("weather_location", "auto")
    # 找到目前設定對應的顯示名稱
    current_label = "自動偵測"
    for label, val in config.TAIWAN_LOCATIONS.items():
        if isinstance(val, dict) and val.get("name") == current_loc:
            current_label = label
            break
        elif val == current_loc:
            current_label = label
            break

    loc_var = tk.StringVar(value=current_label)
    vars_["weather_location_label"] = loc_var

    loc_option = tk.OptionMenu(content_frame, loc_var, *loc_names)
    loc_option.config(
        font=config.FONT_SMALL,
        bg=config.BG_ELEVATED, fg=config.CLOCK_COLOR,
        activebackground=config.BG_TERTIARY,
        activeforeground=config.CLOCK_COLOR,
        highlightthickness=0, relief="flat", bd=0,
        width=18,
    )
    loc_option.pack(fill="x", pady=(0, 4))

    # 分隔線
    tk.Frame(content_frame, bg=config.DIVIDER_COLOR, height=1).pack(fill="x", pady=(12, 12))

    # 按鈕區域
    btn_frame = tk.Frame(content_frame, bg=config.BG_COLOR)
    btn_frame.pack()

    def _save():
        for label, key, typ in fields:
            try:
                settings[key] = typ(vars_[key].get())
            except ValueError:
                pass
        # 處理天氣地區
        selected_label = vars_["weather_location_label"].get()
        loc_val = config.TAIWAN_LOCATIONS.get(selected_label, "auto")
        if isinstance(loc_val, dict):
            settings["weather_location"] = loc_val["name"]
        else:
            settings["weather_location"] = loc_val
        on_save(settings)
        dlg.destroy()

    # 儲存按鈕
    save_btn = tk.Button(btn_frame, text="儲存", command=_save,
              bg=config.BTN_PRIMARY, fg="white",
              font=config.FONT_BTN_LARGE, relief="flat",
              padx=20, pady=8, cursor="hand2")
    save_btn.pack(side="left", padx=8)
    
    # 儲存按鈕hover效果
    def on_save_enter(e):
        save_btn.config(bg=config.BTN_PRIMARY_HOVER)
    def on_save_leave(e):
        save_btn.config(bg=config.BTN_PRIMARY)
    def on_save_press(e):
        save_btn.config(bg=config.BTN_PRIMARY_ACTIVE)
    def on_save_release(e):
        save_btn.config(bg=config.BTN_PRIMARY_HOVER)
    
    save_btn.bind("<Enter>", on_save_enter)
    save_btn.bind("<Leave>", on_save_leave)
    save_btn.bind("<ButtonPress-1>", on_save_press)
    save_btn.bind("<ButtonRelease-1>", on_save_release)

    # 取消按鈕
    cancel_btn = tk.Button(btn_frame, text="取消", command=dlg.destroy,
              bg=config.BTN_BG, fg=config.TEXT_SECONDARY,
              font=config.FONT_BTN, relief="flat",
              padx=20, pady=8, cursor="hand2")
    cancel_btn.pack(side="left", padx=8)
    
    # 取消按鈕hover效果
    def on_cancel_enter(e):
        cancel_btn.config(fg=config.TEXT_PRIMARY, bg=config.BG_TERTIARY)
    def on_cancel_leave(e):
        cancel_btn.config(fg=config.TEXT_SECONDARY, bg=config.BG_COLOR)
    
    cancel_btn.bind("<Enter>", on_cancel_enter)
    cancel_btn.bind("<Leave>", on_cancel_leave)

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
        self._sys_monitor = SystemMonitor()
        self._weather_service = WeatherService()
        self._apply_weather_location()

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
            on_drink=self._record_water,
        )

        self._root.deiconify()
        self._sync_water_display()
        self._sync_med_display()
        self._start_tick()
        self._start_sys_tick()
        self._start_weather_tick()
        self._schedule_water_reminder()
        self._schedule_eow_reminder()
        self._schedule_med_reminder()

    # ── 主計時 tick ───────────────────────────────────

    def _start_tick(self):
        self._scheduler.schedule("tick", 1000, self._tick)

    def _start_sys_tick(self):
        self._scheduler.schedule("sys_tick", 3000, self._sys_tick)

    def _start_weather_tick(self):
        self._scheduler.schedule("weather_tick", 100, self._refresh_weather)

    def _refresh_weather(self):
        def _apply(snapshot):
            try:
                self._root.after(0, lambda s=snapshot: self._clock.set_weather(s))
            except Exception as ex:
                print(f"[weather] UI update error: {ex}", file=sys.stderr)

        try:
            self._weather_service.refresh_async(_apply)
        except Exception as ex:
            print(f"[weather] refresh error: {ex}", file=sys.stderr)
        self._scheduler.schedule("weather_tick", 2 * 60 * 60 * 1000, self._refresh_weather)

    def _sys_tick(self):
        self._sys_monitor.update()
        self._clock.set_system_monitor(self._sys_monitor)
        self._scheduler.schedule("sys_tick", 3000, self._sys_tick)

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
        self._sys_monitor.shutdown()
        self._root.destroy()

    def _apply_weather_location(self):
        loc = self._settings.get("weather_location", "auto")
        if loc == "auto":
            self._weather_service.set_manual_location(None)
        else:
            for label, val in config.TAIWAN_LOCATIONS.items():
                if isinstance(val, dict) and val.get("name") == loc:
                    self._weather_service.set_manual_location(val)
                    return
            self._weather_service.set_manual_location(None)

    def _on_settings(self):
        def _save(new_settings):
            self._settings.update(new_settings)
            save_settings(self._settings)
            # 更新 tracker 目標
            self._tracker.set_target(new_settings["water_target_ml"])
            # 更新久坐間隔
            self._exercise_interval_s = new_settings["exercise_interval_minutes"] * 60
            # 更新天氣地區
            self._apply_weather_location()
            self._refresh_weather()
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

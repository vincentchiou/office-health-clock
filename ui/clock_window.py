# ui/clock_window.py — 主時鐘視窗（可愛大版）

import tkinter as tk
from datetime import datetime
import config

WEEKDAYS = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
BAR_WIDTH = 130   # 進度條寬度


class ClockWindow:
    """
    溫暖紫色系可愛時鐘視窗：
    - overrideredirect（無標準邊框）
    - topmost 始終置頂
    - 可拖曳，關閉時儲存位置
    - 每秒由外部 tick() 呼叫更新顯示
    """

    def __init__(self, root: tk.Tk, settings: dict, on_close, on_settings):
        self._root = root
        self._settings = settings
        self._on_close = on_close
        self._on_settings = on_settings

        self._exercise_remaining = settings.get("exercise_interval_minutes", 50) * 60
        self._water_total = 0
        self._water_target = settings.get("water_target_ml", 2000)
        self._med_taken = False
        self._med_hour = settings.get("med_hour", 13)
        self._med_minute = settings.get("med_minute", 40)

        self._drag_x = 0
        self._drag_y = 0

        self._build()
        self._place_window()

    # ── 公開 API ──────────────────────────────────────────

    def tick(self):
        """每秒呼叫一次，更新所有顯示。"""
        now = datetime.now()
        self._var_time.set(now.strftime("%H:%M:%S"))
        wd = WEEKDAYS[now.weekday()]
        self._var_date.set(f"{now.strftime('%Y-%m-%d')}  {wd}")
        self._update_exercise_display()
        self._update_water_display()
        self._update_med_display()

    def set_exercise_remaining(self, seconds: int):
        self._exercise_remaining = seconds

    def set_water(self, total_ml: int, target_ml: int):
        self._water_total = total_ml
        self._water_target = target_ml

    def set_med_taken(self, taken: bool):
        self._med_taken = taken

    def set_med_time(self, hour: int, minute: int):
        self._med_hour = hour
        self._med_minute = minute

    def get_position(self) -> tuple[int, int]:
        return self._root.winfo_x(), self._root.winfo_y()

    # ── 建構 UI ───────────────────────────────────────────

    def _build(self):
        root = self._root
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.configure(bg=config.BORDER_COLOR)
        root.resizable(False, False)

        # 薰衣草外框
        outer = tk.Frame(root, bg=config.BORDER_COLOR,
                         padx=config.WINDOW_BORDER, pady=config.WINDOW_BORDER)
        outer.pack(fill="both", expand=True)

        # 主背景
        self._main = tk.Frame(outer, bg=config.BG_COLOR,
                               width=config.WINDOW_WIDTH,
                               height=config.WINDOW_HEIGHT)
        self._main.pack(fill="both", expand=True)
        self._main.pack_propagate(False)

        self._build_titlebar()
        self._build_clock_area()
        self._build_divider()
        self._build_info_area()
        self._setup_drag()

    def _build_titlebar(self):
        bar = tk.Frame(self._main, bg=config.BG_COLOR, height=28)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # 關閉鈕
        close_btn = tk.Label(bar, text=" ✕ ", font=("Segoe UI", 10, "bold"),
                             fg=config.CLOSE_COLOR, bg=config.BG_COLOR,
                             cursor="hand2")
        close_btn.pack(side="left", padx=(4, 0))
        close_btn.bind("<Button-1>", lambda e: self._on_close())

        # 中間標題
        tk.Label(bar, text="💝 健康小幫手",
                 font=config.FONT_TITLE,
                 fg=config.BORDER_COLOR, bg=config.BG_COLOR).pack(side="left", padx=8)

        # 設定鈕
        cfg_btn = tk.Label(bar, text="⚙ 設定 ", font=("Segoe UI", 9),
                           fg=config.DATE_COLOR, bg=config.BG_COLOR,
                           cursor="hand2")
        cfg_btn.pack(side="right", padx=(0, 4))
        cfg_btn.bind("<Button-1>", lambda e: self._on_settings())

        # 整列可拖曳
        bar.bind("<ButtonPress-1>", self._start_drag)
        bar.bind("<B1-Motion>", self._do_drag)

    def _build_clock_area(self):
        self._var_time = tk.StringVar(value="--:--:--")
        self._var_date = tk.StringVar(value="")

        tk.Label(self._main, textvariable=self._var_time,
                 font=config.FONT_CLOCK,
                 fg=config.CLOCK_COLOR, bg=config.BG_COLOR).pack(pady=(2, 0))

        tk.Label(self._main, textvariable=self._var_date,
                 font=config.FONT_DATE,
                 fg=config.DATE_COLOR, bg=config.BG_COLOR).pack(pady=(0, 4))

    def _build_divider(self):
        tk.Frame(self._main, bg=config.DIVIDER_COLOR, height=1).pack(
            fill="x", padx=12, pady=(0, 6))

    def _build_info_area(self):
        # ── 喝水列 ──
        water_frm = tk.Frame(self._main, bg=config.BG_COLOR)
        water_frm.pack(fill="x", padx=14, pady=(0, 3))

        tk.Label(water_frm, text="💧", font=("Segoe UI", 12),
                 fg=config.WATER_COLOR, bg=config.BG_COLOR).pack(side="left")

        self._bar_canvas = tk.Canvas(water_frm, width=BAR_WIDTH, height=12,
                                     bg=config.BTN_BG, highlightthickness=0,
                                     bd=0)
        self._bar_canvas.pack(side="left", padx=(5, 7))
        self._bar_fill = self._bar_canvas.create_rectangle(
            0, 0, 0, 12, fill=config.WATER_COLOR, outline="")

        self._var_water = tk.StringVar(value="0/2000ml")
        self._lbl_water = tk.Label(water_frm, textvariable=self._var_water,
                                   font=config.FONT_SMALL,
                                   fg=config.WATER_COLOR, bg=config.BG_COLOR)
        self._lbl_water.pack(side="left")

        # ── 久坐倒數列 ──
        ex_frm = tk.Frame(self._main, bg=config.BG_COLOR)
        ex_frm.pack(fill="x", padx=14, pady=(0, 3))

        tk.Label(ex_frm, text="⏱", font=("Segoe UI", 12),
                 fg=config.TIMER_COLOR, bg=config.BG_COLOR).pack(side="left")

        self._var_exercise = tk.StringVar(value="下次起身：--:--")
        self._lbl_exercise = tk.Label(ex_frm, textvariable=self._var_exercise,
                                      font=config.FONT_SMALL,
                                      fg=config.TIMER_COLOR, bg=config.BG_COLOR)
        self._lbl_exercise.pack(side="left", padx=(5, 0))

        # ── 用藥列 ──
        med_frm = tk.Frame(self._main, bg=config.BG_COLOR)
        med_frm.pack(fill="x", padx=14, pady=(0, 4))

        tk.Label(med_frm, text="💊", font=("Segoe UI", 12),
                 fg=config.MED_COLOR, bg=config.BG_COLOR).pack(side="left")

        self._var_med = tk.StringVar(value="今日用藥：13:40")
        self._lbl_med = tk.Label(med_frm, textvariable=self._var_med,
                                 font=config.FONT_SMALL,
                                 fg=config.MED_COLOR, bg=config.BG_COLOR)
        self._lbl_med.pack(side="left", padx=(5, 0))

    # ── 更新顯示 ──────────────────────────────────────────

    def _update_exercise_display(self):
        s = max(0, self._exercise_remaining)
        m = (s % 3600) // 60
        sec = s % 60
        h = s // 3600
        if h:
            txt = f"下次起身：{h:02d}:{m:02d}:{sec:02d}"
        else:
            txt = f"下次起身：{m:02d}:{sec:02d}"
        color = config.WARN_COLOR if s < 120 else config.TIMER_COLOR
        self._var_exercise.set(txt)
        self._lbl_exercise.config(fg=color)

    def _update_water_display(self):
        total = self._water_total
        target = self._water_target
        self._var_water.set(f"{total}/{target}ml")
        done = total >= target
        color = config.WATER_DONE_COLOR if done else config.WATER_COLOR
        pct = min(1.0, total / target) if target else 0
        bar_w = int(BAR_WIDTH * pct)
        self._bar_canvas.itemconfig(self._bar_fill, fill=color)
        self._bar_canvas.coords(self._bar_fill, 0, 0, bar_w, 12)
        self._lbl_water.config(fg=color)

    def _update_med_display(self):
        if self._med_taken:
            self._var_med.set("今日用藥：已服 ✓")
            self._lbl_med.config(fg=config.MED_DONE_COLOR)
        else:
            self._var_med.set(f"今日用藥：{self._med_hour:02d}:{self._med_minute:02d}")
            self._lbl_med.config(fg=config.MED_COLOR)

    # ── 拖曳 ──────────────────────────────────────────────

    def _setup_drag(self):
        self._main.bind("<ButtonPress-1>", self._start_drag)
        self._main.bind("<B1-Motion>", self._do_drag)

    def _start_drag(self, event):
        self._drag_x = event.x_root - self._root.winfo_x()
        self._drag_y = event.y_root - self._root.winfo_y()

    def _do_drag(self, event):
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        x = max(0, min(x, sw - config.WINDOW_WIDTH))
        y = max(0, min(y, sh - config.WINDOW_HEIGHT))
        self._root.geometry(f"+{x}+{y}")

    # ── 位置 ──────────────────────────────────────────────

    def _place_window(self):
        x = self._settings.get("window_x", -1)
        y = self._settings.get("window_y", -1)
        self._root.update_idletasks()
        if x < 0 or y < 0:
            sw = self._root.winfo_screenwidth()
            sh = self._root.winfo_screenheight()
            x = sw - config.WINDOW_WIDTH - 20
            y = sh - config.WINDOW_HEIGHT - 50
        self._root.geometry(
            f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}+{x}+{y}")

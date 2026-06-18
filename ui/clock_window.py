# ui/clock_window.py — 主時鐘視窗（圖形化版）

import tkinter as tk
import math
from datetime import datetime
import config
from ui.water_panel import WaterPanel
from ui.utils import hex_to_rgb, brighten

WEEKDAYS = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]


class CircleIndicator:
    """Enhanced circular progress indicator with glowing arcs"""
    
    def __init__(self, parent, size=80, color=config.COLOR_WATER, bg_color=config.SYS_BAR_BG):
        self.size = size
        self.color = color
        self.bg_color = bg_color
        self.canvas = tk.Canvas(parent, width=size, height=size, 
                               bg=config.SYS_BAR_BG, highlightthickness=0, bd=0)
        self.progress = 0
        self.target_progress = 0
        self.animation_id = None
        
    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)
        
    def update(self, progress, text="", sub_text=""):
        self.target_progress = min(1.0, max(0.0, progress))
        if self.animation_id is None:
            self._animate_progress()
            
    def _animate_progress(self):
        diff = self.target_progress - self.progress
        if abs(diff) < 0.005:
            self.progress = self.target_progress
            self._draw()
            self.animation_id = None
            return
        self.progress += diff * 0.15
        self._draw()
        self.animation_id = self.canvas.after(30, self._animate_progress)
        
    def _draw(self):
        self.canvas.delete("all")
        cx, cy = self.size // 2, self.size // 2
        radius = self.size // 2 - 12
        main_w = config.ARC_WIDTH_MAIN
        glow_w = config.ARC_WIDTH_GLOW

        # Background circle (track)
        self._draw_arc(cx, cy, radius, 1.0, self.bg_color, width=main_w)

        if self.progress > 0:
            # Glow layers (larger radius, lower opacity via stipple)
            for i in range(config.ARC_GLOW_LAYERS, 0, -1):
                r = radius + i * 3
                w = max(1, glow_w - i)
                self._draw_arc(cx, cy, r, self.progress, self.color, width=w)

            # Inner glow
            if config.INDICATOR_INNER_GLOW:
                self._draw_arc(cx, cy, radius - 2, self.progress,
                               self._brighten(self.color, 0.4), width=3)

            # Main progress arc
            self._draw_arc(cx, cy, radius, self.progress, self.color, width=main_w)

            # Bright tip at end of arc
            self._draw_tip(cx, cy, radius, self.progress, self.color)

        # Center text
        text = f"{int(self.progress * 100)}%"
        self.canvas.create_text(cx, cy, text=text,
                               font=config.FONT_CIRCLE, fill=config.TEXT_PRIMARY)
        
    def _draw_arc(self, cx, cy, radius, progress, color, width=8):
        start_angle = 90
        extent = 360 * progress
        points = []
        steps = max(3, int(40 * progress))
        for i in range(steps + 1):
            angle = math.radians(start_angle - (extent * i / steps))
            x = cx + radius * math.cos(angle)
            y = cy - radius * math.sin(angle)
            points.append((x, y))
        for i in range(len(points) - 1):
            self.canvas.create_line(points[i], points[i+1],
                                   fill=color, width=width, capstyle=tk.ROUND)

    def _draw_tip(self, cx, cy, radius, progress, color):
        """Draw a bright dot at the arc tip"""
        angle = math.radians(90 - 360 * progress)
        x = cx + radius * math.cos(angle)
        y = cy - radius * math.sin(angle)
        bright = self._brighten(color, 0.6)
        r = config.ARC_WIDTH_MAIN // 2 + 2
        self.canvas.create_oval(x - r, y - r, x + r, y + r,
                               fill=bright, outline="", tags="tip")
        # Glow around tip
        self.canvas.create_oval(x - r - 3, y - r - 3, x + r + 3, y + r + 3,
                               fill="", outline=color, width=1, tags="tip")

    @staticmethod
    def _brighten(hex_color, amount):
        return brighten(hex_color, amount)


class GaugeIndicator:
    """Enhanced gauge indicator with glowing semicircle and animated needle"""
    
    def __init__(self, parent, size=100, color=config.COLOR_TIMER):
        self.size = size
        self.color = color
        self.canvas = tk.Canvas(parent, width=size, height=size,
                               bg=config.SYS_BAR_BG, highlightthickness=0, bd=0)
        self.progress = 0
        self.target_progress = 0
        self.current_needle_angle = 180
        self.animation_id = None
        
    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)
        
    def update(self, progress, text="", color=None):
        if color is None:
            color = self.color
        self.target_progress = min(1.0, max(0.0, progress))
        self.color = color
        if self.animation_id is None:
            self._animate_gauge()
            
    def _animate_gauge(self):
        diff = self.target_progress - self.progress
        if abs(diff) < 0.005:
            self.progress = self.target_progress
            self._draw()
            self.animation_id = None
            return
        self.progress += diff * 0.15
        self._draw()
        self.animation_id = self.canvas.after(30, self._animate_gauge)
        
    def _draw(self):
        self.canvas.delete("all")
        cx, cy = self.size // 2, self.size // 2 + 8
        radius = self.size // 2 - 16
        main_w = config.ARC_WIDTH_MAIN
        glow_w = config.ARC_WIDTH_GLOW

        # Background semicircle
        self._draw_semicircle(cx, cy, radius, 1.0, config.SYS_BAR_BG, width=main_w)

        if self.progress > 0:
            # Glow layers
            for i in range(config.ARC_GLOW_LAYERS, 0, -1):
                r = radius + i * 3
                w = max(1, glow_w - i)
                self._draw_semicircle(cx, cy, r, self.progress, self.color, width=w)

            # Inner glow
            self._draw_semicircle(cx, cy, radius - 2, self.progress,
                                  CircleIndicator._brighten(self.color, 0.4), width=3)

            # Main arc
            self._draw_semicircle(cx, cy, radius, self.progress, self.color, width=main_w)

        # Needle with smooth rotation
        target_angle = 180 + 180 * self.progress
        self.current_needle_angle += (target_angle - self.current_needle_angle) * 0.12
        self._draw_needle(cx, cy, radius - 10, self.current_needle_angle, self.color)
        
        # Center text
        text = f"{int(self.progress * 100)}%"
        self.canvas.create_text(cx, cy - 8, text=text,
                               font=config.FONT_CIRCLE, fill=config.TEXT_PRIMARY)
        
    def _draw_semicircle(self, cx, cy, radius, progress, color, width=10):
        start_angle = 180
        extent = 180 * progress
        points = []
        steps = max(3, int(36 * progress))
        for i in range(steps + 1):
            angle = math.radians(start_angle + (extent * i / steps))
            x = cx + radius * math.cos(angle)
            y = cy - radius * math.sin(angle)
            points.append((x, y))
        for i in range(len(points) - 1):
            self.canvas.create_line(points[i], points[i+1],
                                   fill=color, width=width, capstyle=tk.ROUND)
    
    def _draw_needle(self, cx, cy, length, angle_degrees, color):
        angle = math.radians(angle_degrees)
        x = cx + length * math.cos(angle)
        y = cy - length * math.sin(angle)
        
        # Needle shadow
        self.canvas.create_line(cx + 1, cy + 1, x + 1, y + 1,
                               fill="#000000", width=4, capstyle=tk.ROUND)
        # Needle body
        self.canvas.create_line(cx, cy, x, y, fill=color, width=3, capstyle=tk.ROUND)
        # Needle center dot
        self.canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5,
                               fill=color, outline="", width=0)
        bright = CircleIndicator._brighten(color, 0.5)
        self.canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3,
                               fill=bright, outline="", width=0)


class SystemMetricCard:
    """Compact icon card with a progress bar for system metrics."""

    def __init__(self, parent, title: str, icon: str, accent_color: str):
        self._title = title
        self._icon = icon
        self._accent_color = accent_color
        self._ratio = 0.0
        self._value_text = "--"

        self.frame = tk.Frame(
            parent,
            bg=config.SYS_CARD_BG,
            highlightbackground=config.BORDER_LIGHT,
            highlightthickness=1,
        )

        header = tk.Frame(self.frame, bg=config.SYS_CARD_BG)
        header.pack(fill="x", padx=8, pady=(5, 1))

        tk.Label(
            header,
            text=f"{icon} {title}",
            font=config.FONT_SYS_CARD_TITLE,
            fg=config.TEXT_SECONDARY,
            bg=config.SYS_CARD_BG,
        ).pack(side="left")

        self._value_var = tk.StringVar(value="--")
        tk.Label(
            header,
            textvariable=self._value_var,
            font=config.FONT_SYS_CARD_VALUE,
            fg=config.TEXT_PRIMARY,
            bg=config.SYS_CARD_BG,
        ).pack(side="right")

        self._bar = tk.Canvas(
            self.frame,
            height=7,
            bg=config.SYS_CARD_BG,
            highlightthickness=0,
            bd=0,
        )
        self._bar.pack(fill="x", padx=8, pady=(1, 6))
        self._bar.bind("<Configure>", lambda e: self._draw_bar())

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def update(self, value_text: str, ratio: float | None, accent_color: str | None = None):
        self._value_var.set(value_text)
        self._value_text = value_text
        self._ratio = 0.0 if ratio is None else max(0.0, min(1.0, ratio))
        if accent_color is not None:
            self._accent_color = accent_color
        self._draw_bar()

    def _draw_bar(self):
        self._bar.delete("all")
        w = self._bar.winfo_width()
        h = self._bar.winfo_height()
        if w <= 2 or h <= 2:
            return

        bg = config.SYS_BAR_EMPTY
        fg = self._accent_color

        self._bar.create_rectangle(2, 1, w - 2, h - 1, fill=bg, outline="")
        fill_w = int((w - 4) * self._ratio)
        if fill_w > 0:
            self._bar.create_rectangle(2, 1, 2 + fill_w, h - 1, fill=fg, outline="")

        # End cap for a more polished look
        cap_x = min(w - 3, 2 + fill_w)
        if fill_w > 0:
            self._bar.create_oval(cap_x - 3, 0, cap_x + 3, h, fill=fg, outline="")


class ClockWindow:
    """
    圖形化時鐘視窗：
    - overrideredirect（無標準邊框）
    - topmost 始終置頂
    - 可拖曳，關閉時儲存位置
    - 圓形喝水進度指示器
    - 儀表盤式久坐計時器
    - 圖標化系統監控
    """

    def __init__(self, root: tk.Tk, settings: dict, on_close, on_settings, on_drink=None):
        self._root = root
        self._settings = settings
        self._on_close = on_close
        self._on_settings = on_settings
        self._on_drink = on_drink

        self._exercise_remaining = settings.get("exercise_interval_minutes", 50) * 60
        self._exercise_interval = settings.get("exercise_interval_minutes", 50) * 60
        self._water_total = 0
        self._water_target = settings.get("water_target_ml", 2000)
        self._med_taken = False
        self._med_hour = settings.get("med_hour", 13)
        self._med_minute = settings.get("med_minute", 40)

        self._sys_cpu_temp = None
        self._sys_cpu_util = 0.0
        self._sys_gpu_temp = None
        self._sys_vram_used = 0.0
        self._sys_vram_total = 0.0
        self._sys_vram_pct = 0.0
        self._sys_ram_used = 0.0
        self._sys_ram_total = 0.0
        self._sys_ram_pct = 0.0
        self._sys_gpu_util = 0.0

        self._weather_location = "--"
        self._weather_icon = "⛅"
        self._weather_temp = None
        self._weather_wind = None
        self._weather_rain = None
        self._weather_description = "--"
        self._var_weather_main = tk.StringVar(value="⏳ 載入中...")

        self._drag_x = 0
        self._drag_y = 0
        self._resize_edge = None

        self._particle_system = None
        self._water_goal_celebrated = False

        self._build()
        self._setup_particles()
        self._place_window()

    # ── 公開 API ──────────────────────────────────────────

    def tick(self):
        now = datetime.now()
        self._var_time.set(now.strftime("%H:%M:%S"))
        wd = WEEKDAYS[now.weekday()]
        self._var_date.set(f"{now.strftime('%Y-%m-%d')}  {wd}")
        self._update_exercise_display()
        self._update_water_display()
        self._update_med_display()
        self._update_sys_display()

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

    def set_system_monitor(self, monitor):
        self._sys_cpu_temp = monitor.cpu_temp
        self._sys_cpu_util = monitor.cpu_util
        self._sys_gpu_temp = monitor.gpu_temp
        self._sys_vram_used = monitor.vram_used
        self._sys_vram_total = monitor.vram_total
        self._sys_vram_pct = monitor.vram_pct
        self._sys_ram_used = monitor.ram_used
        self._sys_ram_total = monitor.ram_total
        self._sys_ram_pct = monitor.ram_pct
        self._sys_gpu_util = monitor.gpu_util

    def set_weather(self, snapshot):
        self._weather_location = getattr(snapshot, "location", "--") or "--"
        self._weather_icon = getattr(snapshot, "icon", "⛅") or "⛅"
        self._weather_temp = getattr(snapshot, "temperature_c", None)
        self._weather_wind = getattr(snapshot, "wind_kmh", None)
        self._weather_rain = getattr(snapshot, "rain_mm", None)
        self._weather_description = getattr(snapshot, "description", "--") or "--"
        self._update_weather_display()

    def get_position(self) -> tuple[int, int]:
        return self._root.winfo_x(), self._root.winfo_y()

    # ── 建構 UI ───────────────────────────────────────────

    def _build(self):
        root = self._root
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.configure(bg=config.BORDER_COLOR)
        root.resizable(False, False)

        # 外層脈衝邊框
        self._border_frame = tk.Frame(root, bg=config.BORDER_PULSE_1,
                                      padx=config.WINDOW_BORDER, pady=config.WINDOW_BORDER)
        self._border_frame.pack(fill="both", expand=True)
        self._pulse_phase = 0.0

        # 主內容區
        self._main = tk.Frame(self._border_frame, bg=config.BG_GRADIENT_TOP)
        self._main.pack(fill="both", expand=True)

        self._build_titlebar()
        self._build_clock_area()
        self._build_info_area()
        self._build_water_panel()
        self._build_sys_area()
        self._setup_drag()
        self._start_pulse_border()

    def _start_pulse_border(self):
        """Start pulsing border color animation"""
        self._pulse_border()

    def _pulse_border(self):
        """Animate border color through gradient palette"""
        import math
        self._pulse_phase += config.PULSE_BORDER_SPEED
        if self._pulse_phase > 2 * math.pi:
            self._pulse_phase -= 2 * math.pi

        p = self._pulse_phase
        c1 = self._hex_to_rgb(config.BORDER_PULSE_1)
        c2 = self._hex_to_rgb(config.BORDER_PULSE_2)
        c3 = self._hex_to_rgb(config.BORDER_PULSE_3)

        t = (math.sin(p) + 1) / 2
        if t < 0.5:
            t2 = t * 2
            r = int(c1[0] + (c2[0] - c1[0]) * t2)
            g = int(c1[1] + (c2[1] - c1[1]) * t2)
            b = int(c1[2] + (c2[2] - c1[2]) * t2)
        else:
            t2 = (t - 0.5) * 2
            r = int(c2[0] + (c3[0] - c2[0]) * t2)
            g = int(c2[1] + (c3[1] - c2[1]) * t2)
            b = int(c2[2] + (c3[2] - c2[2]) * t2)

        color = f"#{r:02x}{g:02x}{b:02x}"
        self._border_frame.config(bg=color)
        self._root.after(80, self._pulse_border)

    @staticmethod
    def _hex_to_rgb(hex_color):
        return hex_to_rgb(hex_color)

    def _build_titlebar(self):
        bar = tk.Frame(self._main, bg=config.BG_SECONDARY, height=32)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # 關閉按鈕
        close_btn = tk.Label(bar, text="✕", font=("Segoe UI", 10, "bold"),
                             fg=config.CLOSE_COLOR, bg=config.BG_SECONDARY,
                             cursor="hand2", padx=8, pady=2)
        close_btn.pack(side="left", padx=(8, 0))
        close_btn.bind("<Button-1>", lambda e: (self.destroy(), self._on_close()))
        close_btn.bind("<Enter>", lambda e: close_btn.config(fg=config.CLOSE_HOVER, bg=config.BG_TERTIARY))
        close_btn.bind("<Leave>", lambda e: close_btn.config(fg=config.CLOSE_COLOR, bg=config.BG_SECONDARY))

        # 標題
        tk.Label(bar, text="💝 健康小幫手",
                 font=config.FONT_TITLE,
                 fg=config.TEXT_PRIMARY, bg=config.BG_SECONDARY).pack(side="left", padx=6)

        # 時鐘（放在標題與設定之間）
        self._var_time = tk.StringVar(value="--:--:--")
        self._lbl_time = tk.Label(bar, textvariable=self._var_time,
                                  font=("Consolas", 11, "bold"),
                                  fg=config.CLOCK_COLOR, bg=config.BG_SECONDARY)
        self._lbl_time.pack(side="left", padx=6)

        # 設定按鈕
        cfg_btn = tk.Label(bar, text="⚙ 設定", font=config.FONT_LABEL,
                           fg=config.TEXT_SECONDARY, bg=config.BG_SECONDARY,
                           cursor="hand2", padx=8, pady=2)
        cfg_btn.pack(side="right", padx=(0, 8))
        cfg_btn.bind("<Button-1>", lambda e: self._on_settings())
        cfg_btn.bind("<Enter>", lambda e: cfg_btn.config(fg=config.TEXT_PRIMARY, bg=config.BG_TERTIARY))
        cfg_btn.bind("<Leave>", lambda e: cfg_btn.config(fg=config.TEXT_SECONDARY, bg=config.BG_SECONDARY))

        bar.bind("<ButtonPress-1>", self._start_drag)
        bar.bind("<B1-Motion>", self._do_drag)

    def _build_clock_area(self):
        # 左右並排：左邊指示器，右邊天氣+日期
        row1 = tk.Frame(self._main, bg=config.BG_COLOR)
        row1.pack(fill="x", padx=16, pady=(8, 4))
        row1.columnconfigure(0, weight=1)
        row1.columnconfigure(1, weight=0)

        # ── 左側：指示器 ──
        left = tk.Frame(row1, bg=config.BG_COLOR)
        left.grid(row=0, column=0, sticky="w")

        water_f = tk.Frame(left, bg=config.BG_COLOR)
        water_f.pack(side="left", padx=(0, 12))
        self._water_indicator = CircleIndicator(water_f, size=64, color=config.COLOR_WATER, bg_color=config.SYS_BAR_BG)
        self._water_indicator.pack()
        tk.Label(water_f, text="💧 喝水", font=config.FONT_SMALL, fg=config.TEXT_SECONDARY, bg=config.BG_COLOR).pack(pady=(2, 0))

        timer_f = tk.Frame(left, bg=config.BG_COLOR)
        timer_f.pack(side="left", padx=(0, 12))
        self._timer_indicator = GaugeIndicator(timer_f, size=64, color=config.COLOR_TIMER)
        self._timer_indicator.pack()
        tk.Label(timer_f, text="⏱ 久坐", font=config.FONT_SMALL, fg=config.TEXT_SECONDARY, bg=config.BG_COLOR).pack(pady=(2, 0))

        med_f = tk.Frame(left, bg=config.BG_COLOR)
        med_f.pack(side="left")
        self._med_indicator = CircleIndicator(med_f, size=64, color=config.COLOR_MED, bg_color=config.SYS_BAR_BG)
        self._med_indicator.pack()
        tk.Label(med_f, text="💊 用藥", font=config.FONT_SMALL, fg=config.TEXT_SECONDARY, bg=config.BG_COLOR).pack(pady=(2, 0))

        # ── 右側：天氣+日期 ──
        right = tk.Frame(row1, bg=config.BG_COLOR)
        right.grid(row=0, column=1, sticky="ne", padx=(8, 0))

        self._var_weather_location = tk.StringVar(value="天氣")
        self._var_weather_main = tk.StringVar(value="⏳ 載入中...")
        self._var_date = tk.StringVar(value="")

        tk.Label(right, textvariable=self._var_weather_location,
                 font=("Segoe UI", 9, "bold"), fg="#60a5fa", bg=config.BG_COLOR).pack(anchor="e")
        tk.Label(right, textvariable=self._var_weather_main,
                 font=("Segoe UI", 10), fg="#f8fafc", bg=config.BG_COLOR,
                 justify="right").pack(anchor="e", pady=(2, 0))
        tk.Label(right, textvariable=self._var_date,
                 font=("Segoe UI", 8), fg=config.DATE_COLOR, bg=config.BG_COLOR).pack(anchor="e", pady=(4, 0))

    def _build_info_area(self):
        # 資訊顯示區
        info_frame = tk.Frame(self._main, bg=config.BG_COLOR)
        info_frame.pack(fill="x", padx=16, pady=(0, 8))

        # 水量文字
        self._var_water = tk.StringVar(value="0/2000ml")
        self._lbl_water = tk.Label(info_frame, textvariable=self._var_water,
                                   font=config.FONT_VALUE,
                                   fg=config.COLOR_WATER, bg=config.BG_COLOR)
        self._lbl_water.pack(side="left")

        # 久坐倒數文字
        self._var_exercise = tk.StringVar(value="起身：--:--")
        self._lbl_exercise = tk.Label(info_frame, textvariable=self._var_exercise,
                                      font=config.FONT_VALUE,
                                      fg=config.COLOR_TIMER, bg=config.BG_COLOR)
        self._lbl_exercise.pack(side="left", padx=(20, 0))

        # 用藥文字
        self._var_med = tk.StringVar(value="用藥：13:40")
        self._lbl_med = tk.Label(info_frame, textvariable=self._var_med,
                                 font=config.FONT_VALUE,
                                 fg=config.COLOR_MED, bg=config.BG_COLOR)
        self._lbl_med.pack(side="right")

    def _build_water_panel(self):
        if self._on_drink is not None:
            panel = WaterPanel(self._main, on_drink=self._on_drink)
            panel.pack(fill="x", padx=16, pady=(0, 8))

    def _build_sys_area(self):
        # 分隔線
        tk.Frame(self._main, bg=config.DIVIDER_LIGHT, height=1).pack(fill="x", padx=16, pady=(0, 6))

        # 系統監控標題
        sys_header = tk.Frame(self._main, bg=config.BG_COLOR)
        sys_header.pack(fill="x", padx=16, pady=(0, 4))
        
        tk.Label(sys_header, text="📊 系統監控", font=config.FONT_SYS_CARD_TITLE,
                  fg=config.TEXT_SECONDARY, bg=config.BG_COLOR).pack(side="left")

        grid = tk.Frame(self._main, bg=config.BG_COLOR)
        grid.pack(fill="x", padx=16, pady=(0, 6))
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        self._cpu_card = SystemMetricCard(grid, "CPU", "🧠", config.SYS_TEMP_OK)
        self._cpu_util_card = SystemMetricCard(grid, "CPU%", "📊", config.SYS_BAR_CPU)
        self._gpu_card = SystemMetricCard(grid, "GPU", "🎮", config.SYS_TEMP_OK)
        self._ram_card = SystemMetricCard(grid, "RAM", "🧩", config.SYS_BAR_RAM)
        self._vram_card = SystemMetricCard(grid, "VRAM", "🖼", config.SYS_BAR_VRAM)
        self._cuda_card = SystemMetricCard(grid, "CUDA", "⚡", config.SYS_BAR_CUDA)

        self._cpu_card.grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=(0, 4))
        self._cpu_util_card.grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=(0, 4))
        self._gpu_card.grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=(0, 4))
        self._ram_card.grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=(0, 4))
        self._vram_card.grid(row=2, column=0, sticky="ew", padx=(0, 4), pady=(0, 4))
        self._cuda_card.grid(row=2, column=1, sticky="ew", padx=(4, 0), pady=(0, 4))

    # ── 更新顯示 ──────────────────────────────────────────

    def _update_exercise_display(self):
        s = max(0, self._exercise_remaining)
        total = self._exercise_interval
        m = (s % 3600) // 60
        sec = s % 60
        h = s // 3600
        
        if h:
            txt = f"起身：{h:02d}:{m:02d}:{sec:02d}"
        else:
            txt = f"起身：{m:02d}:{sec:02d}"
        
        # 顏色變化
        if s < 60:
            color = config.COLOR_WARN
        elif s < 120:
            color = config.COLOR_TIMER_HOVER
        else:
            color = config.COLOR_TIMER
        
        self._var_exercise.set(txt)
        self._lbl_exercise.config(fg=color)
        
        # 更新計時器指示器
        progress = 1.0 - (s / total) if total > 0 else 0
        self._timer_indicator.update(progress, f"{m:02d}:{sec:02d}", color)

    def _update_water_display(self):
        total = self._water_total
        target = self._water_target
        self._var_water.set(f"{total}/{target}ml")
        done = total >= target
        color = config.COLOR_WATER_DONE if done else config.COLOR_WATER
        pct = min(1.0, total / target) if target else 0

        self._lbl_water.config(fg=color)

        # 更新喝水指示器
        self._water_indicator.update(pct, f"{int(pct*100)}%", color)

        # 達標慶祝（僅觸發一次）
        if done and not self._water_goal_celebrated:
            self._water_goal_celebrated = True
            self._celebrate_water_goal()
        elif not done:
            self._water_goal_celebrated = False

    def _update_med_display(self):
        if self._med_taken:
            self._var_med.set("用藥：已服 ✓")
            self._lbl_med.config(fg=config.COLOR_MED_DONE)
            self._med_indicator.update(1.0, "✓", config.COLOR_MED_DONE)
        else:
            self._var_med.set(f"用藥：{self._med_hour:02d}:{self._med_minute:02d}")
            self._lbl_med.config(fg=config.COLOR_MED)
            self._med_indicator.update(0.0, "未服", config.COLOR_MED)

    def _update_sys_display(self):
        # CPU 溫度
        if self._sys_cpu_temp is not None:
            t = self._sys_cpu_temp
            color = self._temp_color(t)
            self._cpu_card.update(f"{t:.0f}°C", t / 100.0, color)
        else:
            self._cpu_card.update("--", None, config.SYS_TEMP_OK)

        # CPU 使用率
        self._cpu_util_card.update(f"{self._sys_cpu_util:.0f}%", self._sys_cpu_util / 100.0, config.SYS_BAR_CPU)

        # GPU 溫度
        if self._sys_gpu_temp is not None:
            t = self._sys_gpu_temp
            color = self._temp_color(t)
            self._gpu_card.update(f"{t:.0f}°C", t / 100.0, color)
        else:
            self._gpu_card.update("--", None, config.SYS_TEMP_OK)

        # RAM
        if self._sys_ram_total > 0:
            self._ram_card.update(
                f"{self._sys_ram_used:.1f}/{self._sys_ram_total:.1f}G",
                self._sys_ram_pct / 100.0,
                config.SYS_BAR_RAM,
            )
        else:
            self._ram_card.update("--", None, config.SYS_BAR_RAM)

        # VRAM
        if self._sys_vram_total > 0:
            self._vram_card.update(
                f"{self._sys_vram_used:.1f}/{self._sys_vram_total:.1f}G",
                self._sys_vram_pct / 100.0,
                config.SYS_BAR_VRAM,
            )
        else:
            self._vram_card.update("--", None, config.SYS_BAR_VRAM)

        # CUDA
        self._cuda_card.update(f"{self._sys_gpu_util:.0f}%", self._sys_gpu_util / 100.0, config.SYS_BAR_CUDA)

    def _update_weather_display(self):
        temp_text = "--°C"
        if self._weather_temp is not None:
            temp_text = f"{self._weather_temp:.0f}°C"

        wind_text = "--"
        if self._weather_wind is not None:
            wind_text = f"{self._weather_wind:.0f} km/h"

        rain_text = "--"
        if self._weather_rain is not None:
            rain_text = f"{self._weather_rain:.1f} mm"

        self._var_weather_location.set(f"📍 {self._weather_location}")
        self._var_weather_main.set(f"{self._weather_icon} {temp_text}\n💨 {wind_text}\n🌧 {rain_text}")

    @staticmethod
    def _temp_color(temp: float) -> str:
        if temp >= 80:
            return config.SYS_TEMP_HOT
        elif temp >= 65:
            return config.SYS_TEMP_WARM
        return config.SYS_TEMP_OK

    # ── 粒子效果 ──────────────────────────────────────────

    def _setup_particles(self) -> None:
        """Setup particle system for visual effects.

        Note: Particle canvas overlay was removed because ``place()`` with
        full coverage blocked all underlying UI widgets.  Particles are
        currently disabled; re-enable by creating a dedicated canvas that
        does not occlude the main frame.
        """
        self._particle_system = None

    def _celebrate_water_goal(self) -> None:
        """Emit confetti once when water goal is reached.

        This is a one-shot effect: ``_water_goal_celebrated`` is set to
        ``True`` by ``_update_water_display`` before calling this method,
        so subsequent ticks will not re-trigger the celebration unless the
        user drops below the target and reaches it again.
        """
        if self._particle_system:
            x = config.WINDOW_WIDTH // 2
            y = config.WINDOW_HEIGHT // 2
            self._particle_system.emit_confetti(x, y, config.PARTICLE_CONFETTI_COUNT)

    def destroy(self) -> None:
        """Clean up particle system callbacks before the root window is destroyed.

        Must be called *before* ``root.destroy()`` to prevent ``TclError``
        from pending ``after`` callbacks firing on a dead widget.
        """
        if self._particle_system is not None:
            self._particle_system.clear()
            self._particle_system = None

    # ── 拖曳與縮放 ──────────────────────────────────────

    _EDGE = 6  # 邊緣感應寬度

    def _setup_drag(self):
        self._main.bind("<ButtonPress-1>", self._start_drag)
        self._main.bind("<B1-Motion>", self._do_drag)
        self._root.bind("<Motion>", self._edge_cursor)
        self._root.bind("<ButtonRelease-1>", self._end_resize)

    def _edge_cursor(self, event):
        """靠近邊緣時改變游標"""
        w = self._root.winfo_width()
        h = self._root.winfo_height()
        e = self._EDGE
        x, y = event.x, event.y

        on_right = x >= w - e
        on_left = x <= e
        on_bottom = y >= h - e
        on_top = y <= e

        if on_right and on_bottom:
            self._root.config(cursor="size_nw_se")
        elif on_left and on_top:
            self._root.config(cursor="size_nw_se")
        elif on_right and on_top:
            self._root.config(cursor="size_ne_sw")
        elif on_left and on_bottom:
            self._root.config(cursor="size_ne_sw")
        elif on_right:
            self._root.config(cursor="sb_h_double_arrow")
        elif on_left:
            self._root.config(cursor="sb_h_double_arrow")
        elif on_bottom:
            self._root.config(cursor="sb_v_double_arrow")
        elif on_top:
            self._root.config(cursor="sb_v_double_arrow")
        else:
            self._root.config(cursor="")

    def _start_drag(self, event):
        w = self._root.winfo_width()
        h = self._root.winfo_height()
        e = self._EDGE
        x, y = event.x, event.y

        # 判斷是否在邊緣（縮放模式）
        on_right = x >= w - e
        on_left = x <= e
        on_bottom = y >= h - e
        on_top = y <= e

        self._resize_edge = None
        if on_right and on_bottom:
            self._resize_edge = "se"
        elif on_left and on_top:
            self._resize_edge = "nw"
        elif on_right and on_top:
            self._resize_edge = "ne"
        elif on_left and on_bottom:
            self._resize_edge = "sw"
        elif on_right:
            self._resize_edge = "e"
        elif on_left:
            self._resize_edge = "w"
        elif on_bottom:
            self._resize_edge = "s"
        elif on_top:
            self._resize_edge = "n"

        if self._resize_edge:
            self._resize_start_x = event.x_root
            self._resize_start_y = event.y_root
            self._resize_start_geo = self._root.geometry()
            return

        # 拖曳模式
        self._drag_x = event.x_root - self._root.winfo_x()
        self._drag_y = event.y_root - self._root.winfo_y()

    def _do_drag(self, event):
        if self._resize_edge:
            dx = event.x_root - self._resize_start_x
            dy = event.y_root - self._resize_start_y
            geo = self._resize_start_geo
            # 解析目前幾何 "WxH+X+Y"
            parts = geo.replace("x", "+").split("+")
            cur_w, cur_h, cur_x, cur_y = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
            min_w, min_h = 200, 200
            edge = self._resize_edge

            new_x, new_y = cur_x, cur_y
            new_w, new_h = cur_w, cur_h

            if "e" in edge:
                new_w = max(min_w, cur_w + dx)
            if "w" in edge:
                new_w = max(min_w, cur_w - dx)
                new_x = cur_x + (cur_w - new_w)
            if "s" in edge:
                new_h = max(min_h, cur_h + dy)
            if "n" in edge:
                new_h = max(min_h, cur_h - dy)
                new_y = cur_y + (cur_h - new_h)

            self._root.geometry(f"{new_w}x{new_h}+{new_x}+{new_y}")
        else:
            x = event.x_root - self._drag_x
            y = event.y_root - self._drag_y
            sw = self._root.winfo_screenwidth()
            sh = self._root.winfo_screenheight()
            geo = self._root.geometry()
            parts = geo.replace("x", "+").split("+")
            w, h = int(parts[0]), int(parts[1])
            x = max(0, min(x, sw - w))
            y = max(0, min(y, sh - h))
            self._root.geometry(f"+{x}+{y}")

    def _end_resize(self, event):
        self._resize_edge = None

    # ── 位置 ──────────────────────────────────────────────

    def _place_window(self):
        self._root.update_idletasks()
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()

        # 根據螢幕大小動態計算視窗尺寸（取螢幕短邊的 30%～40%）
        short_side = min(sw, sh)
        scale = 0.35
        win_w = max(config.WINDOW_MIN_WIDTH, min(config.WINDOW_MAX_WIDTH, int(short_side * scale)))
        win_h = max(config.WINDOW_MIN_HEIGHT, min(config.WINDOW_MAX_HEIGHT, int(win_w * 1.15)))

        x = self._settings.get("window_x", -1)
        y = self._settings.get("window_y", -1)
        if x < 0 or y < 0:
            x = sw - win_w - 20
            y = sh - win_h - 50
        self._root.geometry(f"{win_w}x{win_h}+{x}+{y}")

# ui/clock_window.py — 主時鐘視窗（圖形化版）

import tkinter as tk
import math
from datetime import datetime
import config

WEEKDAYS = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]


class CircleIndicator:
    """Enhanced circular progress indicator with animations"""
    
    def __init__(self, parent, size=80, color=config.COLOR_WATER, bg_color=config.SYS_BAR_BG):
        self.size = size
        self.color = color
        self.bg_color = bg_color
        self.canvas = tk.Canvas(parent, width=size, height=size, 
                               bg=config.BG_COLOR, highlightthickness=0, bd=0)
        self.progress = 0
        self.target_progress = 0
        self.animation_id = None
        self.pulse_effect = None
        
    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)
        
    def update(self, progress, text="", sub_text=""):
        """Update with smooth animation"""
        self.target_progress = min(1.0, max(0.0, progress))
        
        # Start animation if not already running
        if self.animation_id is None:
            self._animate_progress()
            
    def _animate_progress(self):
        """Animate progress change"""
        diff = self.target_progress - self.progress
        
        if abs(diff) < 0.01:
            self.progress = self.target_progress
            self._draw()
            return
            
        # Smooth interpolation
        self.progress += diff * 0.1
        self._draw()
        self.animation_id = self.canvas.after(16, self._animate_progress)
        
    def _draw(self):
        """Draw the indicator"""
        self.canvas.delete("all")
        
        cx, cy = self.size // 2, self.size // 2
        radius = self.size // 2 - 8
        
        # Draw background arc
        self._draw_arc(cx, cy, radius, 1.0, self.bg_color, width=8)
        
        # Draw progress arc with glow effect
        if self.progress > 0:
            # Draw glow
            for i in range(3):
                r = radius + i * 2
                alpha = 0.3 * (1 - i / 3)
                self._draw_arc(cx, cy, r, self.progress, self.color, width=2)
                
            # Draw main arc
            self._draw_arc(cx, cy, radius, self.progress, self.color, width=8)
        
        # Draw center text
        text = f"{int(self.progress * 100)}%"
        self.canvas.create_text(cx, cy - 5, text=text, 
                               font=config.FONT_CIRCLE, fill=config.TEXT_PRIMARY)
        
    def _draw_arc(self, cx, cy, radius, progress, color, width=8):
        """Draw an arc"""
        start_angle = 90  # Start from top
        extent = 360 * progress
        
        # Use multiple line segments to simulate arc
        points = []
        steps = max(2, int(36 * progress))
        for i in range(steps + 1):
            angle = math.radians(start_angle - (extent * i / steps))
            x = cx + radius * math.cos(angle)
            y = cy - radius * math.sin(angle)
            points.append((x, y))
        
        # Draw line segments
        for i in range(len(points) - 1):
            self.canvas.create_line(points[i], points[i+1], 
                                   fill=color, width=width, capstyle=tk.ROUND)


class GaugeIndicator:
    """Enhanced gauge indicator with animated needle"""
    
    def __init__(self, parent, size=100, color=config.COLOR_TIMER):
        self.size = size
        self.color = color
        self.canvas = tk.Canvas(parent, width=size, height=size,
                               bg=config.BG_COLOR, highlightthickness=0, bd=0)
        self.progress = 0
        self.target_progress = 0
        self.current_needle_angle = 180  # Start position
        self.animation_id = None
        
    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)
        
    def update(self, progress, text="", color=None):
        """Update with smooth needle animation"""
        if color is None:
            color = self.color
            
        self.target_progress = min(1.0, max(0.0, progress))
        self.color = color
        
        # Start animation if not already running
        if self.animation_id is None:
            self._animate_gauge()
            
    def _animate_gauge(self):
        """Animate gauge needle"""
        diff = self.target_progress - self.progress
        
        if abs(diff) < 0.01:
            self.progress = self.target_progress
            self._draw()
            return
            
        # Smooth interpolation
        self.progress += diff * 0.1
        self._draw()
        self.animation_id = self.canvas.after(16, self._animate_gauge)
        
    def _draw(self):
        """Draw the gauge"""
        self.canvas.delete("all")
        
        cx, cy = self.size // 2, self.size // 2 + 10
        radius = self.size // 2 - 15
        
        # Draw background arc (semicircle)
        self._draw_semicircle(cx, cy, radius, 1.0, config.SYS_BAR_BG, width=10)
        
        # Draw progress arc with glow
        if self.progress > 0:
            # Glow effect
            for i in range(2):
                r = radius + i * 3
                self._draw_semicircle(cx, cy, r, self.progress, self.color, width=2)
                
            # Main arc
            self._draw_semicircle(cx, cy, radius, self.progress, self.color, width=10)
        
        # Draw needle with smooth rotation
        target_angle = 180 + 180 * self.progress
        self.current_needle_angle += (target_angle - self.current_needle_angle) * 0.1
        self._draw_needle(cx, cy, radius - 15, self.current_needle_angle, self.color)
        
        # Draw center text
        text = f"{int(self.progress * 100)}%"
        self.canvas.create_text(cx, cy - 10, text=text,
                               font=config.FONT_CIRCLE, fill=config.TEXT_PRIMARY)
        
    def _draw_semicircle(self, cx, cy, radius, progress, color, width=10):
        """Draw a semicircle"""
        start_angle = 180
        extent = 180 * progress
        
        points = []
        steps = max(2, int(36 * progress))
        for i in range(steps + 1):
            angle = math.radians(start_angle + (extent * i / steps))
            x = cx + radius * math.cos(angle)
            y = cy - radius * math.sin(angle)
            points.append((x, y))
        
        for i in range(len(points) - 1):
            self.canvas.create_line(points[i], points[i+1],
                                   fill=color, width=width, capstyle=tk.ROUND)
    
    def _draw_needle(self, cx, cy, length, angle_degrees, color):
        """Draw the needle"""
        angle = math.radians(angle_degrees)
        x = cx + length * math.cos(angle)
        y = cy - length * math.sin(angle)
        
        # Needle root
        self.canvas.create_oval(cx-4, cy-4, cx+4, cy+4, 
                               fill=color, outline="")
        # Needle line
        self.canvas.create_line(cx, cy, x, y, fill=color, width=3, capstyle=tk.ROUND)


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

    def __init__(self, root: tk.Tk, settings: dict, on_close, on_settings):
        self._root = root
        self._settings = settings
        self._on_close = on_close
        self._on_settings = on_settings

        self._exercise_remaining = settings.get("exercise_interval_minutes", 50) * 60
        self._exercise_interval = settings.get("exercise_interval_minutes", 50) * 60
        self._water_total = 0
        self._water_target = settings.get("water_target_ml", 2000)
        self._med_taken = False
        self._med_hour = settings.get("med_hour", 13)
        self._med_minute = settings.get("med_minute", 40)

        self._sys_cpu_temp = None
        self._sys_gpu_temp = None
        self._sys_vram_used = 0.0
        self._sys_vram_total = 0.0
        self._sys_vram_pct = 0.0
        self._sys_ram_used = 0.0
        self._sys_ram_total = 0.0
        self._sys_ram_pct = 0.0
        self._sys_gpu_util = 0.0

        self._drag_x = 0
        self._drag_y = 0

        self._build()
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
        self._sys_gpu_temp = monitor.gpu_temp
        self._sys_vram_used = monitor.vram_used
        self._sys_vram_total = monitor.vram_total
        self._sys_vram_pct = monitor.vram_pct
        self._sys_ram_used = monitor.ram_used
        self._sys_ram_total = monitor.ram_total
        self._sys_ram_pct = monitor.ram_pct
        self._sys_gpu_util = monitor.gpu_util

    def get_position(self) -> tuple[int, int]:
        return self._root.winfo_x(), self._root.winfo_y()

    # ── 建構 UI ───────────────────────────────────────────

    def _build(self):
        root = self._root
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.configure(bg=config.BORDER_COLOR)
        root.resizable(False, False)

        # 外層邊框
        outer = tk.Frame(root, bg=config.BORDER_COLOR,
                         padx=config.WINDOW_BORDER, pady=config.WINDOW_BORDER)
        outer.pack(fill="both", expand=True)

        # 主內容區
        self._main = tk.Frame(outer, bg=config.BG_COLOR,
                              width=config.WINDOW_WIDTH,
                              height=config.WINDOW_HEIGHT)
        self._main.pack(fill="both", expand=True)
        self._main.pack_propagate(False)

        self._build_titlebar()
        self._build_clock_area()
        self._build_indicators_area()
        self._build_info_area()
        self._build_sys_area()
        self._setup_drag()

    def _build_titlebar(self):
        bar = tk.Frame(self._main, bg=config.BG_SECONDARY, height=32)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # 關閉按鈕
        close_btn = tk.Label(bar, text="✕", font=("Segoe UI", 10, "bold"),
                             fg=config.CLOSE_COLOR, bg=config.BG_SECONDARY,
                             cursor="hand2", padx=8, pady=2)
        close_btn.pack(side="left", padx=(8, 0))
        close_btn.bind("<Button-1>", lambda e: self._on_close())
        close_btn.bind("<Enter>", lambda e: close_btn.config(fg=config.CLOSE_HOVER, bg=config.BG_TERTIARY))
        close_btn.bind("<Leave>", lambda e: close_btn.config(fg=config.CLOSE_COLOR, bg=config.BG_SECONDARY))

        # 標題
        tk.Label(bar, text="💝 健康小幫手",
                 font=config.FONT_TITLE,
                 fg=config.TEXT_PRIMARY, bg=config.BG_SECONDARY).pack(side="left", padx=6)

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
        clock_frame = tk.Frame(self._main, bg=config.BG_COLOR)
        clock_frame.pack(fill="x", padx=16, pady=(8, 0))

        self._var_time = tk.StringVar(value="--:--:--")
        self._var_date = tk.StringVar(value="")

        tk.Label(clock_frame, textvariable=self._var_time,
                 font=config.FONT_CLOCK,
                 fg=config.CLOCK_COLOR, bg=config.BG_COLOR).pack(anchor="w")

        tk.Label(clock_frame, textvariable=self._var_date,
                 font=config.FONT_DATE,
                 fg=config.DATE_COLOR, bg=config.BG_COLOR).pack(anchor="w", pady=(0, 4))

    def _build_indicators_area(self):
        """建構圖形化指示器區域"""
        indicators_frame = tk.Frame(self._main, bg=config.BG_COLOR)
        indicators_frame.pack(fill="x", padx=16, pady=(8, 8))

        # 喝水圓形指示器
        water_frame = tk.Frame(indicators_frame, bg=config.BG_COLOR)
        water_frame.pack(side="left", padx=(0, 16))
        
        self._water_indicator = CircleIndicator(water_frame, size=70, 
                                               color=config.COLOR_WATER,
                                               bg_color=config.SYS_BAR_BG)
        self._water_indicator.pack()
        
        tk.Label(water_frame, text="💧 喝水", font=config.FONT_SMALL,
                 fg=config.TEXT_SECONDARY, bg=config.BG_COLOR).pack(pady=(4, 0))

        # 久坐計時器
        timer_frame = tk.Frame(indicators_frame, bg=config.BG_COLOR)
        timer_frame.pack(side="left", padx=(0, 16))
        
        self._timer_indicator = GaugeIndicator(timer_frame, size=70,
                                              color=config.COLOR_TIMER)
        self._timer_indicator.pack()
        
        tk.Label(timer_frame, text="⏱ 久坐", font=config.FONT_SMALL,
                 fg=config.TEXT_SECONDARY, bg=config.BG_COLOR).pack(pady=(4, 0))

        # 用藥狀態
        med_frame = tk.Frame(indicators_frame, bg=config.BG_COLOR)
        med_frame.pack(side="left")
        
        self._med_indicator = CircleIndicator(med_frame, size=70,
                                             color=config.COLOR_MED,
                                             bg_color=config.SYS_BAR_BG)
        self._med_indicator.pack()
        
        tk.Label(med_frame, text="💊 用藥", font=config.FONT_SMALL,
                 fg=config.TEXT_SECONDARY, bg=config.BG_COLOR).pack(pady=(4, 0))

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

    def _build_sys_area(self):
        # 分隔線
        tk.Frame(self._main, bg=config.DIVIDER_LIGHT, height=1).pack(fill="x", padx=16, pady=(0, 6))

        # 系統監控標題
        sys_header = tk.Frame(self._main, bg=config.BG_COLOR)
        sys_header.pack(fill="x", padx=16, pady=(0, 4))
        
        tk.Label(sys_header, text="📊 系統監控", font=config.FONT_SMALL,
                 fg=config.TEXT_SECONDARY, bg=config.BG_COLOR).pack(side="left")

        # CPU/GPU 溫度
        row1 = tk.Frame(self._main, bg=config.BG_COLOR)
        row1.pack(fill="x", padx=16, pady=(0, 3))

        self._var_cpu_temp = tk.StringVar(value="CPU: --°C")
        self._lbl_cpu_temp = tk.Label(row1, textvariable=self._var_cpu_temp,
                                      font=config.FONT_SYS, fg=config.SYS_COLOR, bg=config.BG_COLOR)
        self._lbl_cpu_temp.pack(side="left")

        self._var_gpu_temp = tk.StringVar(value="GPU: --°C")
        self._lbl_gpu_temp = tk.Label(row1, textvariable=self._var_gpu_temp,
                                      font=config.FONT_SYS, fg=config.SYS_COLOR, bg=config.BG_COLOR)
        self._lbl_gpu_temp.pack(side="right")

        # VRAM/RAM
        row2 = tk.Frame(self._main, bg=config.BG_COLOR)
        row2.pack(fill="x", padx=16, pady=(0, 3))

        self._var_ram = tk.StringVar(value="RAM: --/--G")
        self._lbl_ram = tk.Label(row2, textvariable=self._var_ram,
                                 font=config.FONT_SYS, fg=config.SYS_COLOR, bg=config.BG_COLOR)
        self._lbl_ram.pack(side="left")

        self._var_vram = tk.StringVar(value="VRAM: --/--G")
        self._lbl_vram = tk.Label(row2, textvariable=self._var_vram,
                                  font=config.FONT_SYS, fg=config.SYS_COLOR, bg=config.BG_COLOR)
        self._lbl_vram.pack(side="right")

        # CUDA
        row3 = tk.Frame(self._main, bg=config.BG_COLOR)
        row3.pack(fill="x", padx=16, pady=(0, 6))

        self._var_cuda = tk.StringVar(value="CUDA: --%")
        self._lbl_cuda = tk.Label(row3, textvariable=self._var_cuda,
                                  font=config.FONT_SYS, fg=config.SYS_COLOR, bg=config.BG_COLOR)
        self._lbl_cuda.pack(side="left")

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
            self._var_cpu_temp.set(f"CPU: {t:.0f}°C")
            color = self._temp_color(t)
            self._lbl_cpu_temp.config(fg=color)
        else:
            self._var_cpu_temp.set("CPU: --°C")

        # GPU 溫度
        if self._sys_gpu_temp is not None:
            t = self._sys_gpu_temp
            self._var_gpu_temp.set(f"GPU: {t:.0f}°C")
            color = self._temp_color(t)
            self._lbl_gpu_temp.config(fg=color)
        else:
            self._var_gpu_temp.set("GPU: --°C")

        # RAM
        if self._sys_ram_total > 0:
            self._var_ram.set(f"RAM: {self._sys_ram_used:.1f}/{self._sys_ram_total:.1f}G")
        else:
            self._var_ram.set("RAM: --/--G")

        # VRAM
        if self._sys_vram_total > 0:
            self._var_vram.set(f"VRAM: {self._sys_vram_used:.1f}/{self._sys_vram_total:.1f}G")
        else:
            self._var_vram.set("VRAM: --/--G")

        # CUDA
        self._var_cuda.set(f"CUDA: {self._sys_gpu_util:.0f}%")

    @staticmethod
    def _temp_color(temp: float) -> str:
        if temp >= 80:
            return config.SYS_TEMP_HOT
        elif temp >= 65:
            return config.SYS_TEMP_WARM
        return config.SYS_TEMP_OK

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
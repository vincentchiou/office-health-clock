# ui/reminder_window.py — 強制確認提醒視窗（圖形化版）

import tkinter as tk
import math
import winsound
import config


def _play_alert():
    try:
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    except Exception:
        pass


class AnimatedIcon:
    """Enhanced animated icon with particle effects"""
    
    def __init__(self, parent, icon, size=80, color=config.BTN_PRIMARY):
        self.icon = icon
        self.size = size
        self.color = color
        self.canvas = tk.Canvas(parent, width=size, height=size,
                               bg=config.BG_COLOR, highlightthickness=0, bd=0)
        self.frame = 0
        self.pulse_phase = 0
        self.glow_phase = 0
        self.animation_id = None
        
    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)
        
    def start_animation(self):
        """Start continuous animation"""
        self.animation_id = self.canvas.after(50, self._animate)
        
    def _animate(self):
        """Animate the icon"""
        self.frame += 1
        self.pulse_phase += 0.1
        self.glow_phase += 0.05
        
        self.draw()
        self.animation_id = self.canvas.after(50, self._animate)
        
    def draw(self):
        """Draw the animated icon"""
        self.canvas.delete("all")
        cx, cy = self.size // 2, self.size // 2
        
        # Pulsing glow effect
        pulse_scale = 1.0 + 0.1 * math.sin(self.pulse_phase)
        
        # Draw multiple glow layers
        for i in range(4):
            r = 35 + i * 3 * pulse_scale
            alpha = 0.4 * (1 - i / 4)
            self.canvas.create_oval(cx - r, cy - r, 
                                   cx + r, cy + r,
                                   fill="", outline=self.color, width=1)
        
        # Main circle with dynamic border
        border_width = 3 + int(2 * math.sin(self.glow_phase))
        self.canvas.create_oval(cx - 32, cy - 32, cx + 32, cy + 32,
                               fill=config.BG_ELEVATED, outline=self.color, width=border_width)
        
        # Icon text with shadow effect
        self.canvas.create_text(cx + 1, cy + 1, text=self.icon,
                               font=("Segoe UI", 32), fill=config.SHADOW_DARK)
        self.canvas.create_text(cx, cy, text=self.icon,
                               font=("Segoe UI", 32), fill=self.color)
        
    def stop_animation(self):
        """Stop animation"""
        if self.animation_id:
            self.canvas.after_cancel(self.animation_id)
            self.animation_id = None


class ProgressBar:
    """進度條"""
    
    def __init__(self, parent, width=250, height=20, color=config.COLOR_WATER):
        self.width = width
        self.height = height
        self.color = color
        self.canvas = tk.Canvas(parent, width=width, height=height,
                               bg=config.BG_COLOR, highlightthickness=0, bd=0)
        
    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)
        
    def update(self, progress, text=""):
        """更新進度條 0-1"""
        self.canvas.delete("all")
        
        # 背景
        self.canvas.create_rectangle(0, 0, self.width, self.height,
                                    fill=config.SYS_BAR_BG, outline="", width=0)
        
        # 進度（圓角效果）
        if progress > 0:
            bar_width = int(self.width * progress)
            self.canvas.create_rectangle(2, 2, bar_width - 2, self.height - 2,
                                        fill=self.color, outline="", width=0)
        
        # 文字
        if text:
            self.canvas.create_text(self.width // 2, self.height // 2,
                                   text=text, font=config.FONT_SMALL,
                                   fill=config.TEXT_PRIMARY)


class ReminderWindow:
    """
    圖形化強制確認視窗：
    - 全螢幕半透明遮罩
    - 動畫圖標
    - 視覺化進度條
    - 增強的按鈕效果
    """

    def __init__(self, root: tk.Tk):
        self._root = root

    def show_exercise(self, elapsed_minutes: int, on_close=None):
        _play_alert()
        self._show(
            title="起來動一動！",
            icon="🏃",
            icon_color=config.COLOR_TIMER,
            lines=[
                f"你已坐了約 {elapsed_minutes} 分鐘",
                "請做 5 分鐘伸展或起身走動",
            ],
            buttons=[("✓  已完成，繼續工作", None)],
            on_close=on_close,
            accent_color=config.COLOR_TIMER,
            progress=elapsed_minutes / 50,  # 假設50分鐘為目標
            progress_text=f"{elapsed_minutes}/50 分鐘",
        )

    def show_water(self, total_ml: int, target_ml: int, on_drink=None, on_skip=None):
        _play_alert()
        remaining = max(0, target_ml - total_ml)
        pct = min(1.0, total_ml / target_ml) if target_ml else 0

        def _drink(ml):
            if on_drink:
                on_drink(ml)

        def _skip():
            if on_skip:
                on_skip()

        self._show(
            title="記得喝水！",
            icon="💧",
            icon_color=config.COLOR_WATER,
            lines=[
                f"今日：{total_ml} / {target_ml} ml",
                f"還差 {remaining} ml 達標",
            ],
            buttons=[
                ("+200 ml", lambda: _drink(200)),
                ("+350 ml", lambda: _drink(350)),
                ("+500 ml", lambda: _drink(500)),
            ],
            skip_text="跳過，稍後提醒",
            on_close=_skip,
            accent_color=config.COLOR_WATER,
            progress=pct,
            progress_text=f"{int(pct*100)}%",
        )

    def show_medicine(self, on_taken=None, on_close=None):
        _play_alert()
        self._show(
            title="吃藥時間到囉！",
            icon="💊",
            icon_color=config.COLOR_MED,
            lines=[
                "記得服用今日藥物 🌿",
                "健康的身體從按時吃藥開始 ♥",
            ],
            buttons=[("✓  已服藥完成", on_taken)],
            skip_text="稍後提醒我",
            on_close=on_close,
            accent_color=config.COLOR_MED,
            progress=0,
            progress_text="待服藥",
        )

    def show_eow_water(self, total_ml: int, target_ml: int, on_drink=None, on_close=None):
        _play_alert()
        remaining = max(0, target_ml - total_ml)
        pct = min(1.0, total_ml / target_ml) if target_ml else 0

        def _drink(ml):
            if on_drink:
                on_drink(ml)

        self._show(
            title="快下班了！補足水分",
            icon="⏰",
            icon_color=config.COLOR_WARN,
            lines=[
                f"今日：{total_ml} / {target_ml} ml",
                f"還差 {remaining} ml，把握時間補充！",
            ],
            buttons=[
                ("+200 ml", lambda: _drink(200)),
                ("+350 ml", lambda: _drink(350)),
                ("+500 ml", lambda: _drink(500)),
            ],
            skip_text="確認，待會再喝",
            on_close=on_close,
            accent_color=config.COLOR_WARN,
            progress=pct,
            progress_text=f"{int(pct*100)}%",
        )

    def _animate_dialog_entrance(self, dialog):
        """Animate dialog entrance with scale and fade"""
        # Start small and scale up
        dialog.scale = 0.1
        dialog.alpha = 0.0
        
        def animate_step():
            dialog.scale += 0.05
            dialog.alpha += 0.05
            
            if dialog.scale >= 1.0:
                dialog.scale = 1.0
                dialog.alpha = 1.0
                return
                
            # Apply scale effect (simulated with geometry)
            width = int(440 * dialog.scale)
            height = int(380 * dialog.scale)
            x = (dialog.winfo_screenwidth() - width) // 2
            y = (dialog.winfo_screenheight() - height) // 2
            
            dialog.geometry(f"{width}x{height}+{x}+{y}")
            dialog.attributes("-alpha", dialog.alpha)
            
            dialog.after(16, animate_step)
            
        animate_step()

    def _animate_dialog_exit(self, dialog, overlay, callback=None):
        """Animate dialog exit"""
        def animate_step():
            dialog.scale -= 0.1
            dialog.alpha -= 0.1
            
            if dialog.scale <= 0.0:
                dialog.destroy()
                overlay.destroy()
                if callback:
                    callback()
                return
                
            # Apply exit effect
            width = int(440 * dialog.scale)
            height = int(380 * dialog.scale)
            x = (dialog.winfo_screenwidth() - width) // 2
            y = (dialog.winfo_screenheight() - height) // 2
            
            dialog.geometry(f"{width}x{height}+{x}+{y}")
            dialog.attributes("-alpha", dialog.alpha)
            
            dialog.after(16, animate_step)
            
        animate_step()

    def _show(self, title, icon, lines, buttons,
              skip_text=None, on_close=None, accent_color=None,
              icon_color=None, progress=0, progress_text=""):
        if accent_color is None:
            accent_color = config.BTN_PRIMARY
        if icon_color is None:
            icon_color = accent_color

        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()

        # ── 遮罩層 ──────────────────────────────────────
        overlay = tk.Toplevel(self._root)
        overlay.geometry(f"{sw}x{sh}+0+0")
        overlay.overrideredirect(True)
        overlay.attributes("-topmost", True)
        overlay.attributes("-alpha", 0.65)
        overlay.configure(bg=config.OVERLAY_COLOR)
        overlay.update()

        # ── 對話框 ──────────────────────────────────────
        dw, dh = 440, 380
        dx = (sw - dw) // 2
        dy = (sh - dh) // 2

        dlg = tk.Toplevel(self._root)
        dlg.geometry(f"{dw}x{dh}+{dx}+{dy}")
        dlg.overrideredirect(True)
        dlg.attributes("-topmost", True)
        dlg.configure(bg=config.BG_COLOR)
        dlg.update()

        # 外層邊框（強調色）
        border = tk.Frame(dlg, bg=accent_color, padx=3, pady=3)
        border.pack(fill="both", expand=True)

        # 內層內容
        inner = tk.Frame(border, bg=config.BG_COLOR, padx=28, pady=24)
        inner.pack(fill="both", expand=True)

        # 動畫圖標
        icon_widget = AnimatedIcon(inner, icon, size=80, color=icon_color)
        icon_widget.pack(pady=(0, 12))
        icon_widget.draw()
        icon_widget.start_animation()

        # 標題
        tk.Label(inner, text=title,
                 font=config.FONT_REMIND,
                 fg=config.TEXT_PRIMARY, bg=config.BG_COLOR).pack(pady=(0, 8))

        # 分隔線
        tk.Frame(inner, bg=accent_color, height=2).pack(fill="x", pady=(0, 12))

        # 內容文字
        for line in lines:
            tk.Label(inner, text=line,
                     font=config.FONT_REMIND_SUB,
                     fg=config.TEXT_SECONDARY, bg=config.BG_COLOR,
                     anchor="w").pack(fill="x", pady=2)

        # 進度條
        if progress_text:
            progress_bar = ProgressBar(inner, width=280, height=24, color=accent_color)
            progress_bar.pack(pady=(12, 8))
            progress_bar.update(progress, progress_text)

        tk.Frame(inner, bg=config.DIVIDER_COLOR, height=1).pack(fill="x", pady=(8, 12))

        # 按鈕區域
        btn_frame = tk.Frame(inner, bg=config.BG_COLOR)
        btn_frame.pack()

        closed = [False]

        def _close(extra_cb=None):
            if closed[0]:
                return
            closed[0] = True
            guard_id[0] and dlg.after_cancel(guard_id[0])
            icon_widget.stop_animation()
            dlg.grab_release()
            
            def on_animation_done():
                if extra_cb:
                    extra_cb()
                if on_close:
                    on_close()
            
            self._animate_dialog_exit(dlg, overlay, on_animation_done)

        # 建立按鈕
        for i, (label, cb) in enumerate(buttons):
            btn = tk.Button(
                btn_frame, text=label,
                font=config.FONT_BTN_LARGE,
                bg=accent_color, fg="white",
                activebackground=config.BTN_PRIMARY_HOVER,
                activeforeground="white",
                relief="flat", padx=18, pady=10, cursor="hand2",
                command=lambda c=cb: _close(c),
            )
            btn.pack(side="left", padx=8, pady=4)

            def on_enter(e, b=btn, color=accent_color):
                b.config(bg=config.BTN_PRIMARY_HOVER)
            def on_leave(e, b=btn, color=accent_color):
                b.config(bg=color)
            def on_press(e, b=btn):
                b.config(bg=config.BTN_PRIMARY_ACTIVE)
            def on_release(e, b=btn, color=accent_color):
                b.config(bg=color)

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            btn.bind("<ButtonPress-1>", on_press)
            btn.bind("<ButtonRelease-1>", on_release)

        if skip_text:
            skip_btn = tk.Button(
                inner, text=skip_text,
                font=config.FONT_BTN,
                bg=config.BTN_BG, fg=config.TEXT_SECONDARY,
                activebackground=config.BTN_HOVER,
                activeforeground=config.TEXT_PRIMARY,
                relief="flat", padx=14, pady=8, cursor="hand2",
                command=lambda: _close(None),
            )
            skip_btn.pack(pady=(10, 0))

            def on_skip_enter(e):
                skip_btn.config(fg=config.TEXT_PRIMARY, bg=config.BG_TERTIARY)
            def on_skip_leave(e):
                skip_btn.config(fg=config.TEXT_SECONDARY, bg=config.BG_COLOR)

            skip_btn.bind("<Enter>", on_skip_enter)
            skip_btn.bind("<Leave>", on_skip_leave)

        # 提示文字
        tk.Label(inner, text="按 ESC 或 Enter 確認",
                 font=config.FONT_SMALL,
                 fg=config.TEXT_MUTED, bg=config.BG_COLOR).pack(pady=(14, 0))

        # ── 輸入鎖定 ──────────────────────────────────────
        dlg.grab_set()
        dlg.focus_force()
        dlg.bind("<Escape>", lambda e: _close())
        dlg.bind("<Return>", lambda e: _close())
        
        # Start entrance animation
        self._animate_dialog_entrance(dlg)

        guard_id = [None]

        def _guard():
            if not closed[0] and dlg.winfo_exists():
                dlg.focus_force()
                guard_id[0] = dlg.after(200, _guard)

        guard_id[0] = dlg.after(200, _guard)
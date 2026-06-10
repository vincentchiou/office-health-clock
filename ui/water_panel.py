# ui/water_panel.py — 主視窗底部喝水快選按鈕列（增強視覺版）

import tkinter as tk
import config


class WaterPanel(tk.Frame):
    """
    Enhanced water panel with animated color transitions, glow, and press effects.
    """

    def __init__(self, parent, on_drink, **kwargs):
        super().__init__(parent, bg=config.BG_COLOR, **kwargs)
        self._on_drink = on_drink
        self._build()

    def _build(self):
        for i, ml in enumerate(config.WATER_QUICK_AMOUNTS):
            btn_canvas = tk.Canvas(self, width=64, height=34, bg=config.BG_COLOR,
                                   highlightthickness=0, bd=0)
            btn_canvas.pack(side="left", padx=4, pady=2)

            # Draw initial background
            self._draw_btn_bg(btn_canvas, config.BTN_BG, config.COLOR_WATER)

            btn = tk.Button(
                btn_canvas,
                text=f"+{ml}ml",
                font=config.FONT_BTN,
                bg=config.BTN_BG,
                fg=config.COLOR_WATER,
                activebackground=config.BTN_BG,
                activeforeground=config.COLOR_WATER,
                relief="flat",
                bd=0,
                padx=8, pady=4,
                cursor="hand2",
                command=lambda m=ml, c=btn_canvas: self._on_drink_with_effect(m, c),
            )
            btn.place(relx=0.5, rely=0.5, anchor="center")

            self._setup_button_effects(btn, btn_canvas, ml)

    def _draw_btn_bg(self, canvas, bg_color, border_color):
        """Draw rounded button background with colored border"""
        canvas.delete("all")
        w, h = 64, 34
        r = 6  # corner radius
        # Border
        canvas.create_arc(2, 2, 2 + r * 2, 2 + r * 2, start=90, extent=90,
                          outline=border_color, style="arc", width=2)
        canvas.create_arc(w - r * 2 - 2, 2, w - 2, 2 + r * 2, start=0, extent=90,
                          outline=border_color, style="arc", width=2)
        canvas.create_arc(2, h - r * 2 - 2, 2 + r * 2, h - 2, start=180, extent=90,
                          outline=border_color, style="arc", width=2)
        canvas.create_arc(w - r * 2 - 2, h - r * 2 - 2, w - 2, h - 2, start=270, extent=90,
                          outline=border_color, style="arc", width=2)
        # Border lines
        canvas.create_line(r + 2, 2, w - r - 2, 2, fill=border_color, width=2)
        canvas.create_line(r + 2, h - 2, w - r - 2, h - 2, fill=border_color, width=2)
        canvas.create_line(2, r + 2, 2, h - r - 2, fill=border_color, width=2)
        canvas.create_line(w - 2, r + 2, w - 2, h - r - 2, fill=border_color, width=2)
        # Fill
        canvas.create_rectangle(r + 2, 2, w - r - 2, h - 2, fill=bg_color, outline="")
        canvas.create_rectangle(2, r + 2, w - 2, h - r - 2, fill=bg_color, outline="")
        canvas.create_rectangle(r + 2, r + 2, w - r - 2, h - r - 2, fill=bg_color, outline="")

    def _setup_button_effects(self, btn, canvas, ml):
        """Set up hover/press effects with animated color transitions"""
        original_bg = config.BTN_BG
        original_fg = config.COLOR_WATER
        hover_bg = config.COLOR_WATER_HOVER
        hover_border = config.COLOR_WATER_DONE
        press_bg = config.COLOR_WATER_DONE
        press_border = "#ffffff"

        btn._original_bg = original_bg
        btn._original_fg = original_fg
        btn._canvas = canvas
        btn.is_hovered = False
        btn.is_pressed = False

        def on_enter(e):
            btn.is_hovered = True
            self._animate_transition(btn, hover_bg, original_fg, hover_border)

        def on_leave(e):
            btn.is_hovered = False
            if not btn.is_pressed:
                self._animate_transition(btn, original_bg, original_fg, original_fg)

        def on_press(e):
            btn.is_pressed = True
            self._animate_transition(btn, press_bg, "#ffffff", press_border)

        def on_release(e):
            btn.is_pressed = False
            if btn.is_hovered:
                self._animate_transition(btn, hover_bg, original_fg, hover_border)
            else:
                self._animate_transition(btn, original_bg, original_fg, original_fg)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<ButtonPress-1>", on_press)
        btn.bind("<ButtonRelease-1>", on_release)

    def _animate_transition(self, btn, target_bg, target_fg, border_color):
        """Smoothly transition button colors and redraw border"""
        btn.config(bg=target_bg, fg=target_fg, activebackground=target_bg)
        canvas = btn._canvas
        if canvas:
            self._draw_btn_bg(canvas, target_bg, border_color)

    def _on_drink_with_effect(self, ml, canvas):
        """Flash effect on press"""
        # Flash to done color
        self._draw_btn_bg(canvas, config.COLOR_WATER_DONE, "#ffffff")
        self.after(120, lambda: self._draw_btn_bg(canvas, config.BTN_BG, config.COLOR_WATER))
        self.after(120, lambda: self._on_drink(ml))

# ui/water_panel.py — 主視窗底部喝水快選按鈕列（優化版）

import tkinter as tk
import config


class WaterPanel(tk.Frame):
    """
    Enhanced water panel with animated buttons and visual feedback.
    Displays quick-select water amount buttons with hover/press effects.
    """

    def __init__(self, parent, on_drink, **kwargs):
        super().__init__(parent, bg=config.BG_COLOR, **kwargs)
        self._on_drink = on_drink
        self._build()

    def _build(self):
        for i, ml in enumerate(config.WATER_QUICK_AMOUNTS):
            btn_frame = tk.Frame(self, bg=config.BG_COLOR)
            btn_frame.pack(side="left", padx=3, pady=2)

            btn = tk.Button(
                btn_frame,
                text=f"+{ml}ml",
                font=config.FONT_BTN,
                bg=config.BTN_BG,
                fg=config.COLOR_WATER,
                activebackground=config.BTN_HOVER,
                activeforeground=config.COLOR_WATER_DONE,
                relief="flat",
                padx=8, pady=4,
                cursor="hand2",
                command=lambda m=ml: self._on_drink_with_effect(m, btn),
            )
            btn.pack()

            self._setup_button_effects(btn, ml)

    def _setup_button_effects(self, btn, ml):
        """
        Configure mouse event handlers for hover, press, and release effects.
        Stores original and target colors as button attributes for reliable access.
        """
        original_bg = config.BTN_BG
        original_fg = config.COLOR_WATER
        hover_bg = config.BG_TERTIARY
        hover_fg = config.COLOR_WATER_HOVER
        press_bg = config.BORDER_COLOR
        press_fg = config.COLOR_WATER_DONE

        btn._original_bg = original_bg
        btn._original_fg = original_fg
        btn.is_hovered = False
        btn.is_pressed = False
        btn._anim_job = None

        def on_enter(e):
            btn.is_hovered = True
            self._animate_button_hover(btn, hover_bg, hover_fg)

        def on_leave(e):
            btn.is_hovered = False
            if not btn.is_pressed:
                self._animate_button_hover(btn, original_bg, original_fg)

        def on_press(e):
            btn.is_pressed = True
            btn.config(bg=press_bg, fg=press_fg)

        def on_release(e):
            btn.is_pressed = False
            if btn.is_hovered:
                btn.config(bg=hover_bg, fg=hover_fg)
            else:
                btn.config(bg=original_bg, fg=original_fg)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<ButtonPress-1>", on_press)
        btn.bind("<ButtonRelease-1>", on_release)

    def _animate_button_hover(self, btn, target_bg, target_fg):
        """
        Apply immediate color transition to target bg/fg.
        Cancels any in-flight animation to prevent queued updates.
        """
        if btn._anim_job is not None:
            btn.after_cancel(btn._anim_job)
            btn._anim_job = None
        btn.config(bg=target_bg, fg=target_fg)

    def _on_drink_with_effect(self, ml, btn):
        """Handle drink button press with flash effect and callback."""
        original_bg = btn._original_bg
        btn.config(bg=config.COLOR_WATER_DONE)
        btn.after(100, lambda: btn.config(bg=original_bg))

        self._on_drink(ml)
# ui/water_panel.py — 主視窗底部喝水快選按鈕列

import tkinter as tk
import config


class WaterPanel(tk.Frame):
    """
    嵌入主視窗的喝水快選列：
    [+200ml]  [+350ml]  [+500ml]
    點擊後呼叫 on_drink(ml)。
    """

    def __init__(self, parent, on_drink, **kwargs):
        super().__init__(parent, bg=config.BG_COLOR, **kwargs)
        self._on_drink = on_drink
        self._build()

    def _build(self):
        for ml in config.WATER_QUICK_AMOUNTS:
            btn = tk.Button(
                self,
                text=f"+{ml}ml",
                font=config.FONT_BTN,
                bg=config.BTN_BG,
                fg=config.WATER_COLOR,
                activebackground=config.BTN_HOVER,
                activeforeground=config.WATER_DONE_COLOR,
                relief="flat",
                padx=6, pady=2,
                cursor="hand2",
                command=lambda m=ml: self._on_drink(m),
            )
            btn.pack(side="left", padx=2)

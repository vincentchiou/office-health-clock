# ui/reminder_window.py — 強制確認提醒視窗

import tkinter as tk
import winsound
import config


def _play_alert():
    try:
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    except Exception:
        pass


class ReminderWindow:
    """
    彈出強制確認視窗：
    - 全螢幕半透明遮罩（阻止視覺上操作其他視窗）
    - 置中對話框 + grab_set() 鎖定輸入
    - 每 200ms focus_force() 守衛
    - ESC / Enter / 確認按鈕 → 關閉
    """

    def __init__(self, root: tk.Tk):
        self._root = root

    # ── 運動提醒 ─────────────────────────────────────────

    def show_exercise(self, elapsed_minutes: int, on_close=None):
        _play_alert()
        self._show(
            title="起來動一動！",
            icon="🏃",
            lines=[
                f"你已坐了約 {elapsed_minutes} 分鐘",
                "請做 5 分鐘伸展或起身走動",
            ],
            buttons=[("✓  已完成，繼續工作", None)],
            on_close=on_close,
        )

    # ── 喝水提醒 ─────────────────────────────────────────

    def show_water(self, total_ml: int, target_ml: int, on_drink=None, on_skip=None):
        _play_alert()
        remaining = max(0, target_ml - total_ml)
        pct = min(100, int(total_ml / target_ml * 100)) if target_ml else 0

        def _drink(ml):
            if on_drink:
                on_drink(ml)

        def _skip():
            if on_skip:
                on_skip()

        self._show(
            title="記得喝水！",
            icon="💧",
            lines=[
                f"今日：{total_ml} / {target_ml} ml  ({pct}%)",
                f"還差 {remaining} ml 達標",
            ],
            buttons=[
                ("+200 ml", lambda: _drink(200)),
                ("+350 ml", lambda: _drink(350)),
                ("+500 ml", lambda: _drink(500)),
            ],
            skip_text="跳過，稍後提醒",
            on_close=_skip,
        )

    # ── 用藥提醒 ─────────────────────────────────────────

    def show_medicine(self, on_taken=None, on_close=None):
        """
        on_taken : 點「已服藥完成」後呼叫（額外 callback）
        on_close : 無論確認或跳過都呼叫（用來決定是否重排提醒）
        """
        _play_alert()
        self._show(
            title="吃藥時間到囉！",
            icon="💊",
            lines=[
                "記得服用今日藥物 🌿",
                "健康的身體從按時吃藥開始 ♥",
            ],
            buttons=[("✓  已服藥完成", on_taken)],
            skip_text="稍後提醒我",
            on_close=on_close,
        )

    # ── 下班前最後提醒 ────────────────────────────────────

    def show_eow_water(self, total_ml: int, target_ml: int, on_drink=None, on_close=None):
        _play_alert()
        remaining = max(0, target_ml - total_ml)

        def _drink(ml):
            if on_drink:
                on_drink(ml)

        self._show(
            title="快下班了！補足水分",
            icon="⏰",
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
        )

    # ── 核心顯示邏輯 ──────────────────────────────────────

    def _show(self, title, icon, lines, buttons,
              skip_text=None, on_close=None):
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()

        # ── 遮罩層 ──────────────────────────────────────
        overlay = tk.Toplevel(self._root)
        overlay.geometry(f"{sw}x{sh}+0+0")
        overlay.overrideredirect(True)
        overlay.attributes("-topmost", True)
        overlay.attributes("-alpha", 0.55)
        overlay.configure(bg=config.OVERLAY_COLOR)
        overlay.update()

        # ── 對話框 ──────────────────────────────────────
        dw, dh = 400, 300
        dx = (sw - dw) // 2
        dy = (sh - dh) // 2

        dlg = tk.Toplevel(self._root)
        dlg.geometry(f"{dw}x{dh}+{dx}+{dy}")
        dlg.overrideredirect(True)
        dlg.attributes("-topmost", True)
        dlg.configure(bg=config.BG_COLOR)
        dlg.update()

        # 藍色外框效果（用 Frame 包覆）
        border = tk.Frame(dlg, bg=config.BORDER_COLOR, padx=2, pady=2)
        border.pack(fill="both", expand=True)
        inner = tk.Frame(border, bg=config.BG_COLOR, padx=18, pady=14)
        inner.pack(fill="both", expand=True)

        # icon + 標題
        tk.Label(inner, text=f"{icon}  {title}",
                 font=config.FONT_REMIND,
                 fg=config.CLOCK_COLOR, bg=config.BG_COLOR).pack(pady=(4, 8))

        for line in lines:
            tk.Label(inner, text=line,
                     font=config.FONT_REMIND_SUB,
                     fg=config.DATE_COLOR, bg=config.BG_COLOR).pack()

        tk.Frame(inner, bg=config.BORDER_COLOR, height=1).pack(fill="x", pady=10)

        # 行動按鈕列（水量或確認）
        btn_frame = tk.Frame(inner, bg=config.BG_COLOR)
        btn_frame.pack()

        closed = [False]

        def _close(extra_cb=None):
            if closed[0]:
                return
            closed[0] = True
            guard_id[0] and dlg.after_cancel(guard_id[0])
            dlg.grab_release()
            dlg.destroy()
            overlay.destroy()
            if extra_cb:
                extra_cb()
            if on_close:
                on_close()

        for label, cb in buttons:
            btn = tk.Button(
                btn_frame, text=label,
                font=config.FONT_BTN,
                bg=config.WATER_COLOR, fg="white",
                activebackground=config.WATER_DONE_COLOR,
                relief="flat", padx=10, pady=5, cursor="hand2",
                command=lambda c=cb: _close(c),
            )
            btn.pack(side="left", padx=4)

        if skip_text:
            tk.Button(
                inner, text=skip_text,
                font=("Segoe UI", 9),
                bg=config.BTN_BG, fg=config.DATE_COLOR,
                activebackground=config.BTN_HOVER,
                relief="flat", padx=8, pady=3, cursor="hand2",
                command=lambda: _close(None),
            ).pack(pady=(8, 0))

        tk.Label(inner, text="按 ESC 或 Enter 確認",
                 font=("Segoe UI", 8),
                 fg="#556677", bg=config.BG_COLOR).pack(pady=(6, 0))

        # ── 輸入鎖定 ──────────────────────────────────────
        dlg.grab_set()
        dlg.focus_force()
        dlg.bind("<Escape>", lambda e: _close())
        dlg.bind("<Return>", lambda e: _close())

        guard_id = [None]

        def _guard():
            if not closed[0] and dlg.winfo_exists():
                dlg.focus_force()
                guard_id[0] = dlg.after(200, _guard)

        guard_id[0] = dlg.after(200, _guard)

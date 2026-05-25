# config.py — 全域顏色、字體、常數

# 視窗尺寸
WINDOW_WIDTH  = 340
WINDOW_HEIGHT = 252
WINDOW_BORDER = 2

# 顏色（溫暖紫色系，可愛風）
BG_COLOR         = "#1e1b4b"   # 深紫藍
BORDER_COLOR     = "#a78bfa"   # 薰衣草紫
CLOCK_COLOR      = "#fef9ee"   # 暖奶油白
DATE_COLOR       = "#a5b4fc"   # 淡紫灰
WATER_COLOR      = "#38bdf8"   # 天空藍（未達標）
WATER_DONE_COLOR = "#34d399"   # 薄荷綠（達標）
TIMER_COLOR      = "#fb923c"   # 橘色
WARN_COLOR       = "#f87171"   # 柔紅
MED_COLOR        = "#f472b6"   # 粉紅（用藥）
MED_DONE_COLOR   = "#86efac"   # 淡綠（已服藥）
BTN_BG           = "#312e81"   # 深紫按鈕底
BTN_FG           = "#e0e7ff"
BTN_HOVER        = "#4338ca"
CLOSE_COLOR      = "#f87171"
OVERLAY_COLOR    = "black"
DIVIDER_COLOR    = "#3730a3"   # 分隔線

# 字體
FONT_CLOCK      = ("Consolas", 52, "bold")
FONT_DATE       = ("Segoe UI", 12)
FONT_SMALL      = ("Segoe UI", 11)
FONT_BTN        = ("Segoe UI", 10)
FONT_REMIND     = ("Segoe UI", 15, "bold")
FONT_REMIND_SUB = ("Segoe UI", 12)
FONT_TITLE      = ("Segoe UI", 9)

# 預設設定（若 settings.json 不存在時使用）
DEFAULT_SETTINGS = {
    "water_target_ml": 2000,
    "end_of_work_hour": 17,
    "end_of_work_minute": 30,
    "exercise_interval_minutes": 50,
    "water_reminder_min_minutes": 30,
    "water_reminder_max_minutes": 90,
    "med_hour": 13,
    "med_minute": 40,
    "window_x": -1,
    "window_y": -1,
}

# 喝水快選量（ml）
WATER_QUICK_AMOUNTS = [200, 350, 500]

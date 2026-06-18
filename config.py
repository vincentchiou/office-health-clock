# config.py — 全域顏色、字體、常數

# 視窗尺寸（自適應）
WINDOW_WIDTH  = 420
WINDOW_HEIGHT = 480
WINDOW_MIN_WIDTH  = 360
WINDOW_MIN_HEIGHT = 400
WINDOW_MAX_WIDTH  = 560
WINDOW_MAX_HEIGHT = 700
WINDOW_BORDER = 2

# 設計系統 — 現代專業風格
# ──────────────────────────────────────────────────────

# 背景色系（深色主題）
BG_COLOR         = "#0f172a"   # 深藍黑（主背景）
BG_SECONDARY     = "#1e293b"   # 次要背景
BG_TERTIARY      = "#334155"   # 第三層背景
BG_ELEVATED      = "#1a2332"   # 抬高背景（卡片效果）
BG_GRADIENT_TOP  = "#0c1929"   # 漸變頂部
BG_GRADIENT_BOT  = "#162032"   # 漸變底部

# 脈衝邊框色系
BORDER_PULSE_1   = "#3b82f6"   # 藍色脈衝
BORDER_PULSE_2   = "#8b5cf6"   # 紫色脈衝
BORDER_PULSE_3   = "#06b6d4"   # 青色脈衝

# 邊框與分割線
BORDER_COLOR     = "#475569"   # 中性灰藍邊框
BORDER_LIGHT     = "#374151"   # 輕淡邊框
DIVIDER_COLOR    = "#334155"   # 分隔線
DIVIDER_LIGHT    = "#2d3748"   # 輕淡分隔線

# 主要文字
TEXT_PRIMARY      = "#f8fafc"   # 主要文字（亮白）
TEXT_SECONDARY    = "#94a3b8"   # 次要文字（灰藍）
TEXT_TERTIARY     = "#64748b"   # 第三層文字（暗灰）
TEXT_MUTED       = "#475569"   # 極淡文字

# 語義色系
COLOR_WATER      = "#38bdf8"   # 天空藍（喝水）
COLOR_WATER_HOVER = "#7dd3fc"  # 喝水懸停
COLOR_WATER_DONE = "#34d399"   # 薄荷綠（達標）
COLOR_TIMER      = "#fbbf24"   # 琥珀色（計時器）
COLOR_TIMER_HOVER = "#fcd34d"  # 計時器懸停
COLOR_WARN       = "#f87171"   # 柔紅（警告）
COLOR_WARN_HOVER = "#fca5a5"   # 警告懸停
COLOR_MED        = "#f472b6"   # 粉紅（用藥）
COLOR_MED_HOVER  = "#f9a8d4"   # 用藥懸停
COLOR_MED_DONE   = "#86efac"   # 淡綠（已服藥）
COLOR_SUCCESS    = "#10b981"   # 翡翠綠（成功）
COLOR_INFO       = "#60a5fa"   # 藍色（資訊）

# 系統監控色系
SYS_COLOR        = "#94a3b8"   # 系統監控文字
SYS_TEMP_HOT     = "#f87171"   # 高溫警告
SYS_TEMP_WARM    = "#fb923c"   # 溫熱
SYS_TEMP_OK      = "#34d399"   # 正常溫度
SYS_LABEL_COLOR  = "#64748b"   # 標籤文字
SYS_BAR_BG       = "#1e293b"   # 進度條底色
SYS_BAR_CPU      = "#f472b6"   # CPU 溫度條
SYS_BAR_GPU      = "#a78bfa"   # GPU 溫度條
SYS_BAR_VRAM     = "#38bdf8"   # VRAM 用量條
SYS_BAR_RAM      = "#34d399"   # RAM 用量條
SYS_BAR_CUDA     = "#fbbf24"   # CUDA 使用率條

# 按鈕色系
BTN_BG           = "#1e293b"   # 按鈕背景
BTN_FG           = "#f8fafc"   # 按鈕文字
BTN_HOVER        = "#334155"   # 按鈕懸停
BTN_ACTIVE       = "#475569"   # 按鈕按下
BTN_PRIMARY      = "#3b82f6"   # 主要按鈕
BTN_PRIMARY_HOVER = "#2563eb"  # 主要按鈕懸停
BTN_PRIMARY_ACTIVE = "#1d4ed8" # 主要按鈕按下
BTN_SECONDARY    = "#6366f1"   # 次要按鈕
BTN_SECONDARY_HOVER = "#4f46e5" # 次要按鈕懸停

# 特殊元素
CLOSE_COLOR      = "#f87171"   # 關閉按鈕
CLOSE_HOVER      = "#fca5a5"   # 關閉按鈕懸停
OVERLAY_COLOR    = "#0f172a"   # 遮罩層
CLOCK_COLOR      = "#f8fafc"   # 時鐘文字
DATE_COLOR       = "#94a3b8"   # 日期文字

# 動畫與過渡
ANIM_FAST        = 100        # 快速動畫（毫秒）
ANIM_NORMAL      = 200        # 普通動畫
ANIM_SLOW        = 300        # 慢速動畫

# Animation durations (seconds)
ANIM_DURATION_FAST = 0.1
ANIM_DURATION_NORMAL = 0.2
ANIM_DURATION_SLOW = 0.3
ANIM_DURATION_VERY_SLOW = 0.5

# Particle settings
PARTICLE_WATER_DROP_COUNT = 8
PARTICLE_SPARKLE_COUNT = 12
PARTICLE_CONFETTI_COUNT = 30
PARTICLE_LIFETIME = 1.0

# Glow effects
GLOW_INTENSITY = 0.3
GLOW_RADIUS = 10

# Bounce effects
BOUNCE_SCALE = 1.1
BOUNCE_DURATION = 0.2

# 陰影效果（模擬）
SHADOW_LIGHT     = "#1a2332"   # 淺陰影
SHADOW_MEDIUM    = "#0d1117"   # 中等陰影
SHADOW_DARK      = "#080c12"   # 深陰影

# 圖形化元素尺寸
CIRCLE_SIZE      = 80         # 圓形指示器大小
GAUGE_SIZE       = 100        # 儀表盤大小
INDICATOR_SIZE   = 60         # 小型指示器大小
ICON_FONT_SIZE   = 32         # 動畫圖標字體大小

# 指示器視覺增強
ARC_WIDTH_MAIN   = 12         # 主弧線寬度
ARC_WIDTH_GLOW   = 4          # 發光弧線寬度
ARC_GLOW_LAYERS  = 3          # 發光層數
INDICATOR_INNER_GLOW = True   # 內圈發光

# 脈衝邊框
PULSE_BORDER_SPEED   = 0.03   # 脈衝速度
PULSE_BORDER_WIDTH   = 3      # 脈衝邊框寬度

# AnimatedIcon 動畫參數
SPARKLE_INTERVAL       = 6    # 粒子發射間隔（幀數）
BORDER_WIDTH_BASE      = 3    # 圓形邊框基礎寬度
BORDER_WIDTH_AMPLITUDE = 2    # 圓形邊框脈衝振幅
CIRCLE_INSET           = 8    # 圓形內縮像素
PULSE_AMPLITUDE        = 0.1  # 脈衝縮放振幅

# ReminderWindow 參數
OVERLAY_ALPHA          = 0.65 # 遮罩層透明度
DIALOG_START_SCALE     = 0.1  # 入場動畫起始縮放

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
    "weather_location": "auto",
}

# 台灣縣市對照表（縣市名稱 → 緯度、經度）
TAIWAN_LOCATIONS = {
    "自動偵測": "auto",
    "基隆市": {"lat": 25.1276, "lon": 121.7392, "name": "基隆市"},
    "台北市": {"lat": 25.0330, "lon": 121.5654, "name": "台北市"},
    "新北市": {"lat": 25.0143, "lon": 121.4673, "name": "新北市"},
    "桃園市": {"lat": 24.9928, "lon": 121.3010, "name": "桃園市"},
    "新竹市": {"lat": 24.8016, "lon": 120.9714, "name": "新竹市"},
    "新竹縣": {"lat": 24.8390, "lon": 120.9980, "name": "新竹縣"},
    "苗栗縣": {"lat": 24.5600, "lon": 120.8200, "name": "苗栗縣"},
    "台中市": {"lat": 24.1477, "lon": 120.6736, "name": "台中市"},
    "彰化縣": {"lat": 24.0758, "lon": 120.5438, "name": "彰化縣"},
    "南投縣": {"lat": 23.9113, "lon": 120.6774, "name": "南投縣"},
    "雲林縣": {"lat": 23.7083, "lon": 120.5366, "name": "雲林縣"},
    "嘉義市": {"lat": 23.4800, "lon": 120.4490, "name": "嘉義市"},
    "嘉義縣": {"lat": 23.4588, "lon": 120.2960, "name": "嘉義縣"},
    "台南市": {"lat": 22.9999, "lon": 120.2269, "name": "台南市"},
    "高雄市": {"lat": 22.6273, "lon": 120.3014, "name": "高雄市"},
    "屏東縣": {"lat": 22.6685, "lon": 120.4882, "name": "屏東縣"},
    "宜蘭縣": {"lat": 24.7597, "lon": 121.7430, "name": "宜蘭縣"},
    "花蓮縣": {"lat": 23.9750, "lon": 121.6113, "name": "花蓮縣"},
    "台東縣": {"lat": 22.7613, "lon": 121.1133, "name": "台東縣"},
    "澎湖縣": {"lat": 23.5730, "lon": 119.5836, "name": "澎湖縣"},
    "金門縣": {"lat": 24.4365, "lon": 118.3184, "name": "金門縣"},
    "連江縣": {"lat": 26.1500, "lon": 119.9500, "name": "連江縣"},
}

# 喝水快選量（ml）
WATER_QUICK_AMOUNTS = [200, 350, 500]

# 字體系統
FONT_CLOCK      = ("Segoe UI", 42, "bold")
FONT_DATE       = ("Segoe UI", 10)
FONT_SMALL      = ("Segoe UI", 9)
FONT_BTN        = ("Segoe UI", 9)
FONT_BTN_LARGE  = ("Segoe UI", 10, "bold")
FONT_REMIND     = ("Segoe UI", 14, "bold")
FONT_REMIND_SUB = ("Segoe UI", 11)
FONT_TITLE      = ("Segoe UI", 8, "bold")
FONT_LABEL      = ("Segoe UI", 8)
FONT_VALUE      = ("Consolas", 9)
FONT_SYS        = ("Consolas", 8)
FONT_SYS_LABEL  = ("Segoe UI", 8)
FONT_ICON       = ("Segoe UI", 12)
FONT_ICON_LARGE = ("Segoe UI", 16)
FONT_CIRCLE     = ("Segoe UI", 14, "bold")
FONT_CIRCLE_SM  = ("Segoe UI", 10)
FONT_SYS_CARD_TITLE = ("Segoe UI", 8, "bold")
FONT_SYS_CARD_VALUE = ("Segoe UI", 10, "bold")
FONT_SYS_CARD_SMALL = ("Segoe UI", 8)

# 系統監控卡片
SYS_CARD_BG      = "#172033"
SYS_BAR_EMPTY    = "#243149"

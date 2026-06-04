# 💝 辦公室健康時鐘

一款常駐於桌面角落的辦公室健康小幫手，幫助久坐上班族養成運動、喝水、按時服藥的好習慣。

![Python](https://img.shields.io/badge/Python-3.12-blue) ![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey) ![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ 功能特色

| 功能 | 說明 |
|------|------|
| 🕐 **桌面時鐘** | 大字體時鐘常駐螢幕角落，始終置頂，可自由拖曳 |
| 🏃 **久坐提醒** | 每 50 分鐘強制彈出提醒，必須按 OK 或 ESC 才能繼續操作 |
| 💧 **喝水追蹤** | 記錄每日飲水量，顯示進度條，不定期提醒補水 |
| ⏰ **下班前提醒** | 下班前 30 分鐘，若未達喝水目標自動提醒 |
| 💊 **用藥提醒** | 每日 13:40 提醒服藥，服藥後顯示「已服 ✓」，跨重開機保留記錄 |
| ⚙️ **彈性設定** | 下班時間、喝水目標、提醒間隔、用藥時間均可調整 |
| 🚀 **開機自動啟動** | 登入後自動在背景啟動，無需手動開啟 |

---

## 🖥️ 介面預覽

```
┌──────────────────────────────────────┐
│ ✕  💝 健康小幫手              ⚙ 設定 │
│                                      │
│           15:30:22                   │
│        2026-05-25  週一               │
│  ─────────────────────────────────  │
│  💧 ████████░░  1400/2000ml          │
│  ⏱ 下次起身：23:15                   │
│  💊 今日用藥：13:40                   │
└──────────────────────────────────────┘
```

深紫色系可愛風格，薰衣草紫邊框，支援高 DPI 螢幕。

---

## 🚀 快速開始

### 系統需求

- Windows 10 / 11
- Python 3.10+（[下載 Python](https://www.python.org/downloads/)）

### 安裝與啟動

1. 下載或 Clone 此專案
2. 雙擊 `start.bat`（第一次執行會自動建立虛擬環境，約 10 秒）
3. 時鐘視窗出現於螢幕右下角，可拖曳到任意位置

```bash
git clone https://github.com/vincentchiou/office-health-clock.git
cd office-health-clock
start.bat
```

> **零額外套件**：純 Python 標準函式庫，無需 `pip install` 任何第三方套件。

### 設定開機自動啟動

1. 將 `startup.vbs` 放在專案資料夾（已包含）
2. 建立本機啟動器 `C:\Users\<你的帳號>\HealthClock_launcher.vbs`，內容如下：

```vbscript
Dim WShell, vbsPath, fso
WShell  = CreateObject("WScript.Shell")
vbsPath = "C:\<你的專案路徑>\startup.vbs"   ' ← 改成你的實際路徑
Set fso = CreateObject("Scripting.FileSystemObject")

' 等待路徑就緒（最多 60 秒，適合 Google Drive 等雲端磁碟）
Dim waited : waited = 0
Do While Not fso.FileExists(vbsPath)
    WScript.Sleep 2000 : waited = waited + 2
    If waited >= 60 Then WScript.Quit
Loop

WShell.Run "wscript.exe """ & vbsPath & """", 0, False
```

3. 在 Windows **啟動資料夾** 建立捷徑指向此 VBS：
   - 按 `Win + R` → 輸入 `shell:startup` → Enter
   - 在開啟的資料夾中建立 `HealthClock_launcher.vbs` 的捷徑

> **提示**：啟動器會等待雲端硬碟掛載完成再啟動，適合程式放在 Google Drive / OneDrive 的使用者。

**取消自動啟動：** 刪除啟動資料夾中的捷徑即可。

---

## ⚙️ 個人化設定

點擊視窗右上角「⚙ 設定」開啟設定對話框：

| 設定項目 | 預設值 | 說明 |
|---------|--------|------|
| 每日喝水目標 | 2000 ml | 每日建議飲水量 |
| 下班時間 | 17:30 | 超過此時間停止喝水提醒 |
| 久坐提醒間隔 | 50 分鐘 | 運動提醒頻率 |
| 喝水提醒間隔 | 30～90 分鐘（隨機）| 喝水提醒頻率範圍 |
| 用藥提醒時間 | 13:40 | 每日用藥提醒時間 |

設定檔存放於 `data/settings.json`，可直接編輯。

---

## 📁 專案結構

```
office-health-clock/
├── start.bat              # 一鍵啟動
├── startup.vbs            # 無聲啟動器（供開機自動啟動使用）
├── main.py                # 主程式入口
├── config.py              # 顏色、字體、常數
├── requirements.txt       # 無第三方套件
├── ui/
│   ├── clock_window.py    # 主時鐘視窗
│   ├── reminder_window.py # 強制確認提醒視窗
│   └── water_panel.py     # 喝水快選面板
├── core/
│   ├── scheduler.py       # 計時器管理
│   └── water_tracker.py   # 喝水/用藥記錄與持久化
└── data/                  # 自動建立
    ├── settings.json      # 使用者設定
    └── water_log.json     # 每日喝水與用藥記錄
```

---

## 🔧 提醒機制說明

### 強制確認
每次提醒彈出時，視窗會搶佔輸入焦點，**必須按確認按鈕或 ESC 鍵**才能繼續操作滑鼠，確保提醒被真正注意到。

### 喝水提醒邏輯
- 工作時間內，每隔 30～90 分鐘（隨機）提醒一次
- 下班前 30 分鐘若未達標，觸發最終提醒
- 達到目標後停止提醒

### 用藥提醒邏輯
- 每日固定時間提醒
- 若跳過，15 分鐘後重新提醒
- 點選「已服藥完成」後，當日不再提醒，並記錄於 `water_log.json`

---

## 📊 資料格式

`data/water_log.json` 每日記錄範例：

```json
{
  "2026-05-25": {
    "target_ml": 2000,
    "total_ml": 1750,
    "records": [
      {"time": "09:15:00", "ml": 350},
      {"time": "11:30:00", "ml": 500},
      {"time": "14:00:00", "ml": 200}
    ],
    "med_taken": true
  }
}
```

---

## 📝 License

MIT License — 自由使用、修改、分享。

---

*由 Claude Code 協助開發 🤖*

# 打字 Whack-a-Mole 遊戲 - 項目重構說明

## 📁 新的項目結構

```
my_frist_game/
├── main_refactored.py      # ⭐ 新的主入口（推薦使用）
├── main.py                 # （舊版本，可刪除）
├── main-2.py               # （舊版本，可刪除）
│
├── config/
│   └── settings.py         # 🎮 遊戲配置（顏色、尺寸、常數）
│
├── assets/
│   ├── __init__.py
│   └── loader.py           # 📦 資源加載（圖片、字體、動畫）
│
├── data/
│   ├── words.csv           # 📚 詞彙數據
│   └── loader.py           # 📖 CSV 詞彙讀取
│
├── core/
│   ├── __init__.py
│   ├── game.py             # 🎯 遊戲引擎（邏輯）
│   ├── mole.py             # 🐭 地鼠管理（位置、動畫）
│   └── state.py            # 📊 遊戲狀態管理
│
├── ui/
│   ├── __init__.py
│   ├── buttons.py          # 🔘 按鈕管理
│   └── renderer.py         # 🎨 UI 繪製函數
│
├── images/                 # 遊戲圖片資源
├── fonts/                  # 遊戲字體
├── resources/              # 聲音等其他資源
└── README.md               # 原始說明
```

## 🔄 功能模組說明

### 1️⃣ **config/settings.py** - 配置管理

- 定義所有遊戲常數（尺寸、顏色、位置等）
- 集中管理配置，方便修改難度、大小等參數

### 2️⃣ **assets/loader.py** - 資源加載

- 加載遊戲圖片和動畫幀
- 加載字體
- 統一管理資源，避免重複加載

### 3️⃣ **data/loader.py** - 數據加載

- 從 CSV 讀取詞彙
- 根據難度和類別篩選詞彙

### 4️⃣ **core/mole.py** - 地鼠類

- 管理地鼠位置、當前單字、動畫幀
- `reset()` - 生成新地鼠
- `update_animation()` - 更新動畫
- `get_current_frame()` - 獲取當前幀

### 5️⃣ **core/state.py** - 遊戲狀態類

- 管理得分、生命、輸入文本
- 狀態管理：menu → category → game → over
- 提供狀態轉換方法

### 6️⃣ **core/game.py** - 遊戲引擎類

- `start_game()` - 初始化遊戲
- `update_game()` - 每幀更新邏輯
- `handle_key_press()` - 處理玩家輸入
- `check_answer()` - 檢查答案是否正確

### 7️⃣ **ui/buttons.py** - 按鈕管理

- 建立和管理所有按鈕（難度、類別）
- 檢測按鈕點擊

### 8️⃣ **ui/renderer.py** - UI 渲染器

- `draw_menu()` - 繪製主選單
- `draw_category()` - 繪製類別選擇
- `draw_game()` - 繪製遊戲畫面
- `draw_game_over()` - 繪製遊戲結束畫面

## ✨ 改進優勢

| 原始版本          | 重構版本                       |
| ----------------- | ------------------------------ |
| 單個 700+ 行檔案  | 分模組，每個檔案 50-150 行     |
| 混雜所有邏輯和 UI | 邏輯、UI、配置分離             |
| 難以修改配置      | 所有常數集中在 `settings.py`   |
| 難以測試          | 易於單元測試各模組             |
| 難以擴展          | 易於添加新功能（音效、動畫等） |

## 🚀 使用方式

```bash
# 在 my_frist_game 目錄執行
python main_refactored.py
```

## 📝 如何擴展

### 添加新的難度等級

修改 `config/settings.py` 和 `words.csv`

### 添加音效

1. 在 `assets/loader.py` 添加 `load_sounds()` 函數
2. 在 `core/game.py` 調用播放音效

### 添加新狀態

1. 在 `core/state.py` 添加狀態
2. 在 `main_refactored.py` 的事件處理和繪製函數中添加對應邏輯

### 修改顏色方案

在 `config/settings.py` 修改顏色定義，所有 UI 會自動更新

## 🎮 遊戲流程

```
START → 選難度 → 選類別 → 遊戲進行 → 檢查答案 →
  ↓                                     ↓
失命 ← ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┘
  ↓
(生命 = 0) → 遊戲結束 → 點擊返回選難度
```

## 💡 代碼質量

- ✅ 清晰的命名約定
- ✅ 函數和類有說明文檔
- ✅ 單一職責原則（每個模組做一件事）
- ✅ 易於測試和維護
- ✅ 配置集中管理

---

祝遊戲開發愉快！🎮

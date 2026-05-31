# my_first_game

## 缺少功能

1. 登入(?)
1. 封面
1. 顯示倒數秒數
1. 排行榜
1. 修改選類別，改成一個level三個關卡，比如說1-1、1-2、1-3
1. 切換輸入法為英文
1. 打遊戲時出現游標

my_frist_game/
│
├── main.py # 只負責啟動
├── config.py # 常數（畫面、時間、顏色）
│
├── core/
│ ├── game.py # 主遊戲流程（state machine）
│ ├── mole.py # 地鼠邏輯
│ ├── words.py # CSV 載入
│
├── ui/
│ ├── menu.py # 選 level UI
│ ├── category.py # 選分類 UI
│ ├── game_ui.py # 遊戲畫面 UI
│ ├── game_over.py # 結束畫面 UI
│
├── assets/
│ ├── images/
│ ├── fonts/
│ └── words.csv
│
└── utils/
└── button.py # 按鈕工具（可選）

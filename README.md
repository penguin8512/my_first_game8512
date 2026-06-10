
# ∫•⬬•ʅ 打字地鼠大作戰

一個結合 **打字練習 + 打地鼠遊戲 + 劇情引導機器人** 的 Python Pygame 專案。

玩家需要在時間內正確輸入英文單字，擊退地鼠並挑戰關卡！

---

## 遊戲特色

- 打地鼠 + 英文打字訓練結合
- 互動式 AI 引導機器人（開場劇情）
- 敲擊動畫與特效系統
- WPM / CPM / 正確率統計
- 背景音樂與音效
- 多關卡與階段系統
<!-- - 可透過 GitHub Pages 網頁遊玩 -->
- 使用7000單字作為題庫

---

## 遊玩方式

### 本地執行（Python）

請先安裝 pygame：

```bash
pip install pygame
```
執行：

```bash
python main.py
```


---
### Windows 免安裝版本
如果你不想安裝 Python，可以直接從 GitHub 下載 ZIP 檔：

1. 點選「Code」→「Download ZIP」
2. 解壓縮檔案
3. 進入資料夾
4. 雙擊執行 `main.exe`

即可開始遊玩

⚠️ 請確保 `images / music / words.csv` 與 `main.exe` 在同一資料夾


<!-- ### 網頁版（GitHub Pages）

直接開啟：

```
https://你的帳號.github.io/你的repo/
```

（部署完成後即可使用）

--- -->

## 遊戲規則

1. 地鼠會隨機出現在洞口
2. 每隻地鼠會顯示一個英文單字
3. 在時間內輸入正確單字並按 ENTER
4. 成功擊中即可獲得分數
5. 關卡越後面難度越高

---

## 關卡說明（動態隨機難度曲線）
### 地鼠停留時間會隨著關卡推進而增加難度

- 🟢 Level 1：固定 7.0 秒 

- 🟡 Level 2：6.0 ~ 7.0 秒隨機

- 🟡 Level 3：5.0 ~ 7.0 秒隨機 

- 🟠 Level 4：4.0 ~ 6.0 秒隨機 

- 🔴 Level 5：3.0 ~ 6.0 秒隨機

- ☠️ Level 6：3.0 ~ 5.0 秒隨機 ——【魔王極速關】
---
## 遊戲系統

### 計分系統

* 正確輸入 +2 分
* 錯誤輸入 -1 分
* 最後計算：

  * WPM（每分鐘單字數）
  * CPM（每分鐘字元數）
  * Accuracy（正確率）
* 每關累積 10 分過關

---

### 動畫系統

* 地鼠出現動畫
* 被擊中縮回動畫
* 鎚子打擊特效
* 粒子爆炸效果

---

### 劇情系統

* 開場 AI 機器人引導
* 玩家輸入名字
* 教學模式
* 根據結果鼓勵、安慰玩家

---

## 專案結構

```
project/
│── main.py
│── words.csv
│── main.exe
│
├── images/
│   ├── mice1.png ~ mice8.png
│   ├── mice_hit1.png ~ mice_hit4.png
│   ├── hammer1.png ~ hammer4.png
│   └── robot.png / robot_happy.png / robot_sad.png
│
├── music/
│   ├── bgm.wav
│   ├── hit.wav
│   ├── wrong.wav
│   └── clear.wav
│
├── fonts/
│   └── msjh.ttf
```

---

## 使用技術

* Python 3
* Pygame
* auto-py-to-exe (圖形化打包工具，用於將遊戲編譯為 Windows 獨立的 `.exe` 執行檔)
* CSV 資料讀取
<!-- * GitHub Pages（網頁部署）
* pygbag（Pygame Web 轉換） -->

---

## 未來更新計畫

*  加入排行榜系統
*  多人競速模式
*  製作網頁版
*  過關分數隨難度增加

---

## 資料來源
- [單字庫](https://drive.google.com/file/d/1SvWyswCK-w4xmR5aOYIPXmBE5eax3KxM/view)
- [音效-wrong](https://sc.chinaz.com/tag_yinxiao/cuowu.html)
- [音效-hit](https://youtu.be/SpWW74WrmZg?si=mj84YmBExHNUdy6f)
- [音效-clear](https://youtu.be/5-gG-59gQpU?si=zqGCrudRCWGzK4yA)
- [音樂-bgm](https://youtu.be/XpIpJ64QDSc?si=_FjwlF_fKcgM-4pb)

###### 在本專題開發過程中，使用 AI 工具協助學習與開發，提升程式完成效率與除錯能力。(協作AI：ChatGPT、Gemini)






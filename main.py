import pygame
import random
import csv
import sys

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("打字地鼠大作戰")

clock = pygame.time.Clock()

# =========================
# CSV
# =========================
def load_words(level, stage):
    result = []
    try:
        with open("words.csv", newline='', encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["level"] == str(level) and row["stage"] == stage:
                    result.append({"word": row["english"]})
    except FileNotFoundError:
        # 預防找不到 CSV 檔案時崩潰
        pass
    return result if result else [{"word": "cat"}]


# =========================
# 圖片
# =========================
mole_frames = []
for i in range(8, 0, -1):
    # 這裡預防測試時沒有圖片，正式跑時請確保路徑正確
    try:
        img = pygame.image.load(f"images/mice{i}.png").convert_alpha()
    except:
        img = pygame.Surface((120, 120))
        img.fill((200, i*25, 0))
    img = pygame.transform.scale(img, (120, 120))
    mole_frames.append(img)

# 載入 4 張鎚子與 4 張地鼠被打的動畫幀
hammer_frames = []
hit_mole_frames = []
for i in range(1, 5):
    try:
        h_img = pygame.image.load(f"images/hammer{i}.png").convert_alpha()
        hammer_frames.append(pygame.transform.scale(h_img, (120, 120)))
    except:
        h_err = pygame.Surface((120, 120)); h_err.fill((255, 0, 0))
        hammer_frames.append(h_err)
        
    try:
        m_img = pygame.image.load(f"images/mice_hit{i}.png").convert_alpha()
        hit_mole_frames.append(pygame.transform.scale(m_img, (120, 120)))
    except:
        m_err = pygame.Surface((120, 120)); m_err.fill((200, 0, 0))
        hit_mole_frames.append(m_err)

try:
    hole_img = pygame.image.load("images/mice8.png").convert_alpha()
    bg_img = pygame.image.load("images/black.png").convert()
except:
    hole_img = pygame.Surface((140, 80))
    hole_img.fill((50, 50, 50))
    bg_img = pygame.Surface((WIDTH, HEIGHT))
    bg_img.fill((0, 0, 0))

hole_img = pygame.transform.scale(hole_img, (140, 80))
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

font = pygame.font.Font("fonts/msjh.ttf", 30) if pygame.font.get_init() else pygame.font.SysFont("Arial", 30)
big_font = pygame.font.Font(None, 60)
# =========================
# 按鈕圖片 
# =========================
# ==========================================
# 載入主選單與 6 關獨立的三態圖片
# ==========================================
try:
    # 【主選單按鈕圖片】
    btn1_normal  = pygame.transform.scale(pygame.image.load("images/button/btn1-1.png").convert_alpha(), (600, 300))
    btn1_hover   = pygame.transform.scale(pygame.image.load("images/button/btn1-2.png").convert_alpha(), (600, 300))
    btn1_pressed = pygame.transform.scale(pygame.image.load("images/button/btn1-3.png").convert_alpha(), (600, 300))
    
    btn2_normal  = pygame.transform.scale(pygame.image.load("images/button/btn2-1.png").convert_alpha(), (600, 300))
    btn2_hover   = pygame.transform.scale(pygame.image.load("images/button/btn2-2.png").convert_alpha(), (600, 300))
    btn2_pressed = pygame.transform.scale(pygame.image.load("images/button/btn2-3.png").convert_alpha(), (600, 300))
    
    btn3_normal  = pygame.transform.scale(pygame.image.load("images/button/btn3-1.png").convert_alpha(), (600, 300))
    btn3_hover   = pygame.transform.scale(pygame.image.load("images/button/btn3-2.png").convert_alpha(), (600, 300))
    btn3_pressed = pygame.transform.scale(pygame.image.load("images/button/btn3-3.png").convert_alpha(), (600, 300))

    # 三個列表，分別存放6個關卡的常態、懸停、按壓圖片
    lvl_normals = []
    lvl_hovers = []
    lvl_presseds = []

    for i in range(1, 7):
        img_n = pygame.image.load(f"images/button/Lv{i}-1.png").convert_alpha()
        img_h = pygame.image.load(f"images/button/Lv{i}-2.png").convert_alpha()
        img_p = pygame.image.load(f"images/button/Lv{i}-3.png").convert_alpha()
        
        lvl_normals.append(pygame.transform.scale(img_n, (450, 250)))
        lvl_hovers.append(pygame.transform.scale(img_h, (450, 250)))
        lvl_presseds.append(pygame.transform.scale(img_p, (450, 250)))

except Exception as e:
    print(f"按鈕圖片載入失敗，將使用純色代替。錯誤原因: {e}")
    # 防禦機制：萬一沒圖片，就建立替代畫布
    btn1_normal = btn1_hover = btn1_pressed = pygame.Surface((500, 250))
    lvl_normals = [pygame.Surface((450, 250)) for _ in range(6)]
    lvl_hovers = [pygame.Surface((450, 250)) for _ in range(6)]
    lvl_presseds = [pygame.Surface((450, 250)) for _ in range(6)]
# =========================
# 音效
# =========================
# 這裡加 try-except 避免測試時沒音效檔案報錯
try:
    hit_sound = pygame.mixer.Sound("music/hit.wav")
    wrong_sound = pygame.mixer.Sound("music/wrong.wav")
    clear_sound = pygame.mixer.Sound("music/clear.wav")
    hit_sound.set_volume(1)
    wrong_sound.set_volume(1)
    clear_sound.set_volume(0.7)
    pygame.mixer.music.load("music/bgm.wav")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
except:
    pass

# =========================
# 狀態
# =========================
#  將初始狀態改為 "chatbot"，讓遊戲一打開先進入聊天流程
game_state = "chatbot" 
chatbot_step = 0        # 控制機器人對話走到哪一步
player_name = "玩家"     # 儲存玩家輸入的名字

# 記錄哪一個按鈕被按下去、以及按下的時間點
pressed_button_name = None   # 記錄主選單哪個被按
pressed_level_index = None   # 記錄關卡選單哪個被按
button_flash_timer = 0       # 記錄按下時的時間戳記
FLASH_DURATION = 150         # 強制有動畫的時間（150 毫秒）

level = 1
stages = ["first", "second", "third"]
stage_index = 0

typed_chars = 0
correct_words = 0
wrong_words = 0
score = 0
total_score = 0
TARGET_SCORE = 10 #通關分數

MAX_NAME_LEN = 12
input_val = ""  
user_text = ""
words = [{"word": "cat"}]
current_word = random.choice(words)

mole_positions = [
    (150, 250), (350, 250), (550, 250), (750, 250),
    (150, 480), (350, 480), (550, 480), (750, 480),
]

current_pos = random.choice(mole_positions)

# 地鼠消失時間
MOLE_DURATION = 7000
stage_start_time = pygame.time.get_ticks()
mole_timer = pygame.time.get_ticks()
mole_index = 0
mole_speed = 0.2

clear_timer = 0
particles = []

# 真正用於計算打字速度的有效遊戲總秒數
total_game_time = 0.0

# 最後結算用的暫存數據，避免在結束畫面裡反覆計算導致數字浮動
final_cpm = 0.0
final_wpm = 0.0
final_accuracy = 0.0

# 用來存放當前畫面上正在播放的敲擊動畫列表
active_hit_animations = []

# =========================
#  動畫管理類別
# =========================
class HitAnimation:
    def __init__(self, pos):
        self.pos = pos
        self.current_frame = 0
        self.timer = 0.0
        self.frame_duration = 0.08  # 每一幀播放速度（秒）
        self.is_finished = False

    def update(self, dt):
        if self.is_finished: return
        self.timer += dt
        if self.timer >= self.frame_duration:
            self.timer = 0.0
            self.current_frame += 1
            if self.current_frame >= 4:
                self.is_finished = True
                self.current_frame = 3

    def draw(self):
        if self.is_finished: return
        x, y = self.pos
        # 1. 畫被打縮進去的地鼠
        screen.blit(hit_mole_frames[self.current_frame], (x - 60, y - 30))
        # 2. 畫上層砸下來的鎚子
        screen.blit(hammer_frames[self.current_frame], (x - 60, y - 80))

# =========================
# UI
# =========================
menu_buttons = {
    "開始遊戲": pygame.Rect(350, 250, 300, 60),
    "遊戲說明": pygame.Rect(350, 400, 300, 60),
    "結束遊戲": pygame.Rect(350, 550, 300, 60)
}

# ==========================================
# 關卡按鈕2*3
# ==========================================
level_buttons = []
btn_w, btn_h = 450, 250 # 圖片尺寸
hit_w, hit_h = 200, 90  # 判定方格尺寸

for i in range(6):
    col = i % 2   # 第幾欄 (0, 1)
    row = i // 2  # 第幾列 (0, 1, 2)
    
    # 1. 基礎 X, Y 座標計算
    img_x = 110 + col * (btn_w + 0)
    img_y = 120 + row * (btn_h + 20)
    
    # 2. 微調位移
    if row == 0:      # 第 1、2 關（第 0 列）
        img_y += 0    # 維持原樣
    elif row == 1:    # 第 3、4 關（第 1 列）
        img_y -= 80   # 往上移動 80
    elif row == 2:    # 第 5、6 關（第 2 列）
        img_y -= 160  # 往上移動 160
 
    # 3. 計算判定方格（Rect）的位置，確保它永遠在該列圖片的正中央
    hit_x = img_x + 65
    hit_y = img_y + 47
    
    # 將跟著圖片一起移動後的感應區存進清單
    level_buttons.append(pygame.Rect(hit_x, hit_y, hit_w, hit_h))
# =========================
# 工具
# =========================
def new_mole():
    global current_word, current_pos, mole_index, mole_timer, CURRENT_MOLE_DURATION
     #記住這隻地鼠原本的位置
    old_pos = current_pos if 'current_pos' in globals() else None
    # 1. 隨機選一個洞和單字
    current_pos = random.choice(mole_positions)
    if words: 
        current_word = random.choice(words)
    else:
        current_word = {"word": "test", "chinese": "測試"}
        
    # 2. 如果抽到一樣的洞，就強制重新抽，直到抽到不同的洞為止
    while True:
        next_pos = random.choice(mole_positions)
        if next_pos != old_pos:
            current_pos = next_pos
            break # 抽到不同的洞了，跳出迴圈
            
    # 3. 重置動畫幀與時間計時器
    mole_index = 0
    mole_timer = pygame.time.get_ticks()

    try:
        current_lvl = level
    except NameError:
        current_lvl = 1 # 保險機制

    # 4. 根據關卡決定這隻新地鼠的隨機壽命
    if current_lvl == 1:     min_s, max_s = 7.0, 7.0
    elif current_lvl == 2:   min_s, max_s = 6.0, 7.0
    elif current_lvl == 3:   min_s, max_s = 5.0, 7.0
    elif current_lvl == 4:   min_s, max_s = 4.0, 6.0
    elif current_lvl == 5:   min_s, max_s = 3.0, 6.0
    else:                    min_s, max_s = 3.0, 5.0

    # 抽一個隨機秒數並轉成毫秒
    CURRENT_MOLE_DURATION = random.uniform(min_s, max_s) * 1000

def draw_mole():
    x, y = current_pos
    frame = mole_frames[int(mole_index)]
    screen.blit(frame, (x - 60, y - 30))
    text = font.render(current_word["word"], True, (255, 255, 255))
    text_rect = text.get_rect(center=(x, y - 60))
    screen.blit(text, text_rect)

def draw_holes():
    for pos in mole_positions:
        screen.blit(hole_img, (pos[0] - 70, pos[1]))

def spawn_particles():
    global particles
    particles.clear()
    for _ in range(50):
        particles.append([
            WIDTH // 2,
            HEIGHT // 2,
            random.uniform(-6, 6),
            random.uniform(-8, -2),
            random.randint(3, 8)
        ])

def update_particles():
    for p in particles:
        p[0] += p[2]
        p[1] += p[3]
        p[3] += 0.2

def draw_particles():
    for p in particles:
        pygame.draw.circle(screen, (255, 255, 0), (int(p[0]), int(p[1])), int(p[4]))

def start_clear():
    global game_state, clear_timer
    try: clear_sound.play()
    except: pass
    spawn_particles()
    game_state = "clear"
    clear_timer = pygame.time.get_ticks()

# 統一計算打字效率的函式
def calculate_stats():
    global final_cpm, final_wpm, final_accuracy
    # 確保分母不為 0，改用分鐘制 (秒數 / 60)
    minutes = max(total_game_time / 60.0, 0.01)
    
    final_cpm = typed_chars / minutes
    final_wpm = final_cpm / 5.0  # 傳統 WPM 定義為 CPM / 5
    
    total_words = correct_words + wrong_words
    final_accuracy = (correct_words / max(1, total_words)) * 100
# 繪製機器人外觀與對話框的共用函式
def draw_robot_ui(bot_text, show_input=False, input_val=""):
    screen.fill((40, 45, 50)) # 深色科技感背景
    
    # 1. 機器人圖片
    # 繪製引導機器人（圖片版）
    robot_img = pygame.image.load("images/robot.png").convert_alpha()
    robot_img = pygame.transform.scale(robot_img, (150, 150))
    screen.blit(robot_img, (50, 150))
    # 名字標籤
    name_tag = font.render("小幫手喵喵", True, (0, 255, 200))
    screen.blit(name_tag, (50, 300))
    
    # 2. 繪製對話氣泡框
    bubble_rect = pygame.Rect(220, 150, 720, 250)
    pygame.draw.rect(screen, (30, 30, 35), bubble_rect, border_radius=15)
    pygame.draw.rect(screen, (0, 180, 255), bubble_rect, 3, border_radius=15)
    
    # 渲染對話文字 (支援多行 \n 換行)
    lines = bot_text.split('\n')
    for idx, line in enumerate(lines):
        rendered_line = font.render(line, True, (255, 255, 255))
        screen.blit(rendered_line, (250, 180 + idx * 40))
        
    # 3. 如果需要玩家輸入（填名字階段）
    if show_input:
        box_width = 400
        box_height = 50
        box_x = (WIDTH - box_width) // 2
        box_y = 450
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        
        pygame.draw.rect(screen, (20, 20, 25), box_rect)
        box_color = (0, 220, 100) if input_val else (150, 150, 150)
        pygame.draw.rect(screen, box_color, box_rect, 3, border_radius=8)
        
        text_surf = font.render(input_val, True, (255, 255, 255))
        screen.blit(text_surf, (box_rect.x + 15, box_rect.centery - text_surf.get_height() // 2))
        
        hint = font.render("請輸入您的英文名字，完成後請按 ENTER", True, (150, 150, 150))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 520))
        counter = font.render(f"{len(input_val)}/12", True, (150,150,150))
        screen.blit(counter, (box_rect.right - 60, box_rect.y - 40))
    else:
        # 提示按 Enter 繼續
        hint = font.render("[ 按 ENTER 繼續 ]", True, (0, 255, 200))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 550))



new_mole()

# =========================
# LOOP
# =========================
running = True

while running:
    # 取得每影格實際經過的毫秒數，並換算成秒
    dt = clock.tick(60) / 1000.0  
    current_time = pygame.time.get_ticks()
    mole_index += mole_speed
    if mole_index >= len(mole_frames):
        mole_index = len(mole_frames) - 1

    # 在每影格更新並剔除已播完的打地鼠動畫
    for anim in active_hit_animations[:]:
        anim.update(dt)
        if anim.is_finished:
            active_hit_animations.remove(anim)


    # ================= CHATBOT 機器人互動狀態 =================
    if game_state == "chatbot":
        if chatbot_step == 0:
            draw_robot_ui("嗨！歡迎來到打字地鼠世界！\n我是你的引導小幫手。\n在開始之前，能告訴我你的名字嗎？")
        elif chatbot_step == 1:
            draw_robot_ui("請在下方輸入框寫下名字吧：", show_input=True, input_val=user_text)
        elif chatbot_step == 2:
            draw_robot_ui(f"{player_name}，你好呀！很高興認識你！\n接下來，請讓我為你說明一下遊戲規則。\n準備好了就按 Enter 吧！")
        elif chatbot_step == 3:
            draw_robot_ui("【 遊戲規則說明 】\n1. 地鼠出現時，牠頭上會顯示一個英文單字。\n2. 在時間內正確打出單字並按下 ENTER 敲擊！\n3. 每關有3個小階段，必須達到5分才能過關喔。\n祝你好運！記得輸入法要切成英文喔！")
#============================================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if chatbot_step == 1:
                    # 名字輸入階段
                    if event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if user_text.strip() != "":
                            player_name = user_text.strip()
                        user_text = "" # 清空，留給後面遊戲打字用
                        chatbot_step = 2
                    else:
                        # 只有當按下的是英文字母或空格時才接收
                        if event.unicode.isalpha() or event.unicode == " ":
                            # 限制名字最長12 個字（直接寫數字，免去未定義變數的崩潰）
                            if len( user_text ) < 12:
                                user_text += event.unicode # 將字串加到正確的user_text 變數中
  
#============================================
                else:
                    # 其他步驟點 Enter 進入下一步
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        chatbot_step += 1
                        if chatbot_step > 3:
                            game_state = "menu" # 對話結束，跳轉至主畫面

    # ================= MENU =================
    elif game_state == "menu":
        screen.fill((20, 20, 20))
        big_font = pygame.font.Font("fonts/msjh.ttf", 60)
        title = big_font.render("打字地鼠大作戰", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        current_time = pygame.time.get_ticks()

        for name, btn in menu_buttons.items():
            if name == "開始遊戲":
                img_n, img_h, img_p = btn1_normal, btn1_hover, btn1_pressed
            elif name == "遊戲說明":
                img_n, img_h, img_p = btn2_normal, btn2_hover, btn2_pressed
            else:
                img_n, img_h, img_p = btn3_normal, btn3_hover, btn3_pressed

            # 如果這個按鈕剛被點擊，且 150 毫秒還沒到，強制顯示「按下去的圖（img_p）」
            if pressed_button_name == name and (current_time - button_flash_timer < FLASH_DURATION):
                current_img = img_p
            # 否則，維持原本的滑鼠懸停判定
            elif btn.collidepoint(mouse_pos):
                current_img = img_p if mouse_click else img_h
            else:
                current_img = img_n

            img_rect = current_img.get_rect(center=btn.center)
            screen.blit(current_img, img_rect.topleft)
            

        # 延遲切換狀態的邏輯
        if pressed_button_name and (current_time - button_flash_timer >= FLASH_DURATION):
            if pressed_button_name == "開始遊戲":
                score = 0; total_score = 0; stage_index = 0; user_text = ""; typed_chars = 0
                correct_words = 0; wrong_words = 0; total_game_time = 0.0; active_hit_animations = []
                stage_start_time = pygame.time.get_ticks(); mole_timer = pygame.time.get_ticks()
                game_state = "level"
            elif pressed_button_name == "遊戲說明":
                game_state = "how"
            pressed_button_name = None # 觸發完後重置

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 點擊時不立刻換關卡，而是先啟動動畫
                for name, btn in menu_buttons.items():
                    if btn.collidepoint(event.pos):
                        pressed_button_name = name
                        button_flash_timer = pygame.time.get_ticks()
                        if name == "結束遊戲": # 結束遊戲可以立刻退出
                            running = False

    # ================= 選擇關卡 =================
    elif game_state == "level":
        screen.fill((0, 0, 0))
        title = big_font.render("關卡選擇", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 40)) # 置中一下比較美

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, btn in enumerate(level_buttons):
                    if btn.collidepoint(event.pos):
                        pressed_level_index = i
                        button_flash_timer = pygame.time.get_ticks()

        # 延遲切換進入遊戲關卡
        if pressed_level_index is not None and (current_time - button_flash_timer >= FLASH_DURATION):
            level = pressed_level_index + 1
            # 重置所有遊戲數值
            stage_index = 0; score = 0; total_score = 0; user_text = ""; typed_chars = 0
            correct_words = 0; wrong_words = 0; total_game_time = 0.0; active_hit_animations = []
            stage_start_time = pygame.time.get_ticks(); mole_timer = pygame.time.get_ticks()
            words = load_words(level, stages[0])
            new_mole()
            game_state = "game"
            pressed_level_index = None # 重置，非常重要！

        # 繪製 6 個大關卡按鈕
        # ==========================================
        # 邏輯：大圖片置中蓋在小感應區上
        # ==========================================
        for i, hit_rect in enumerate(level_buttons):
            # 1. 偵測小感應區 (hit_rect) 是否被碰觸
            if pressed_level_index == i and (current_time - button_flash_timer < FLASH_DURATION):
                current_lvl_img = lvl_presseds[i]
            elif hit_rect.collidepoint(mouse_pos):
                current_lvl_img = lvl_presseds[i] if mouse_click else lvl_hovers[i]
            else:
                current_lvl_img = lvl_normals[i]

            # 2. 計算大圖片的置中位置
            # 讓圖片中心對準感應區的中心
            img_render_rect = current_lvl_img.get_rect(center=hit_rect.center)
            
            # 3. 畫出圖片
            screen.blit(current_lvl_img, img_render_rect.topleft)

            # --------------------------------------------------
            # 除錯:感應區
            # pygame.draw.rect(screen, (255, 0, 0), hit_rect, 2) 
            # --------------------------------------------------
    # ================= HOW =================
    elif game_state == "how":
        screen.fill((30, 30, 30))
        texts = [
            "遊戲說明", "這是一個打地鼠遊戲", "當地鼠出現時，打字框會顯示一個英文單字",
            "你需要在地鼠消失前，正確輸入單字並按下ENTER", "每關有三個階段，每個階段需要達到十分才能過關",
            "總共有六關，記得輸入法要切成英文喔！","祝各位好運~", "", "按下ENTER返回選單"
        ]
        for i, t in enumerate(texts):
            screen.blit(font.render(t, True, (255, 255, 255)), (150, 150 + i * 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    game_state = "menu"

    # ================= GAME =================
    elif game_state == "game":
        screen.blit(bg_img, (0, 0))
        # 只有在真正的遊戲關卡狀態下，才累加有效打字時間
        total_game_time += dt

        elapsed = (current_time - stage_start_time) / 1000

        # 時間到，換下一隻地鼠
        if current_time - mole_timer >= CURRENT_MOLE_DURATION:
            new_mole()
            

        # =====================
        # 時間到 (60秒一關)
        # =====================
        if elapsed >= 60:
            # 分數達標
            user_text = ""
            if score >= TARGET_SCORE:
                try: clear_sound.play()
                except: pass
                
                # 不管到第幾階段過關，只要過關時間到就應該立刻噴發粒子
                spawn_particles()

                if stage_index < 2:
                    stage_index += 1
                    game_state = "clear"
                    clear_timer = pygame.time.get_ticks()
                else:
                    calculate_stats() # 破關，先算好分數數據存起來
                    game_state = "result"
                    clear_timer = pygame.time.get_ticks()
            # 分數不足
            else:
                calculate_stats() # 輸了，先算好分數數據存起來
                game_state = "over"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = "menu"
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                     
                    if user_text.lower() == current_word["word"].lower():
                        score += 2
                        total_score += 2
                        correct_words += 1
                        typed_chars += len(user_text)  
                        
                        # 打對單字時，在當前地鼠座標建立敲擊動畫物件
                        active_hit_animations.append(HitAnimation(current_pos))

                        try: hit_sound.play()
                        except: pass
                    else:
                        score -= 1
                        total_score -= 1
                        wrong_words += 1
                        try: wrong_sound.play()
                        except: pass
                    user_text = ""
                    new_mole()
                else:
                    if event.unicode:
                        try:
                            event.unicode.encode('ascii')
                            user_text += event.unicode
                        except UnicodeEncodeError:
                            # 如果包含中文或中文符號，會觸發此錯誤，直接忽略不存入
                            pass

    
        draw_holes()
        draw_mole()

        # 在畫面上印出所有正在播放的打地鼠特效
        for anim in active_hit_animations:
            anim.draw()

        # ==========================================
        # 動態輸入框
        # ==========================================
        # 設定輸入框的尺寸與位置 (X, Y, 寬, 高)
        box_width = 500
        box_height = 50
        box_x = (WIDTH - box_width) // 2  # 居中對齊 (300)
        box_y = 580
        
        input_box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        
        # 1. 畫輸入框的背景（深灰色，帶點透明感）
        pygame.draw.rect(screen, (30, 30, 35), input_box_rect)
        
        # 2. 畫輸入框的邊框（有文字時亮綠色，沒文字時灰白色）
        box_color = (0, 220, 100) if user_text else (150, 150, 150)
        pygame.draw.rect(screen, box_color, input_box_rect, 3, border_radius=8) # 3像素寬，圓角8
        
        # 3. 渲染玩家輸入的文字
        text_surface = font.render(user_text, True, (255, 255, 255))
        
        # 讓文字在輸入框內保持垂直居中，稍微往右靠 15 像素
        text_rect = text_surface.get_rect()
        text_rect.midleft = (box_x + 15, box_y + box_height // 2)
        
        # 4. 把文字貼到畫面上
        screen.blit(text_surface, text_rect)
        # ==========================================
        # screen.blit(font.render(user_text, True, (255, 255, 255)), (270, 590))
        screen.blit(font.render(f"Level {level}-{stage_index+1}", True, (255,255,255)), (50, 20))
        screen.blit(font.render(f"得分：{score}", True, (255,255,255)), (50, 60))
        screen.blit(font.render(f"剩餘時間：{max(0, int(60 - elapsed))}秒", True, (255,255,0)), (750, 20)) # 顯示時間(倒數)
        
    # ================= GAME OVER =================
    elif game_state == "over":
        screen.blit(bg_img, (0, 0)) 
        # 引導機器人
        robot_img = pygame.image.load("images/robot_sad.png").convert_alpha()
        robot_img = pygame.transform.scale(robot_img, (150, 150))
        screen.blit(robot_img, (100, 150))
        # 名字標籤
        name_tag = font.render("小幫手喵喵", True, (0, 235, 200))
        screen.blit(name_tag, (100, 320))
        

        # 這裡直接讀取剛剛算好的 final_wpm 和 final_cpm，不會再隨著時間遞減了！
        stats1 = font.render(f"每分鐘所打的單字數(WPM): {final_wpm:.1f}", True, (255,255,255))
        stats2 = font.render(f"每分鐘所打的字元數(CPM): {final_cpm:.1f}", True, (255,255,255))
        stats3 = font.render(f"正確率: {final_accuracy:.1f}%", True, (255,255,255))
        stats4 = font.render(f"總分: {total_score}", True, (255,255,255))

        screen.blit(stats1,(450,300))
        screen.blit(stats2,(450,340))
        screen.blit(stats3,(450,380))
        screen.blit(stats4,(450,420))
        
        hint = font.render("按下空白鍵返回主畫面", True, (255,255,255))
        screen.blit(hint,(420,520))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    chatbot_step = 2 # 回到選單前，下次玩直接從步驟2(打過招呼)開始
                    game_state = "menu"

        # 機器人的難過對話框
        bubble_rect = pygame.Rect(320, 80, 600, 120)
        pygame.draw.rect(screen, (30, 30, 35), bubble_rect, border_radius=15)
        pygame.draw.rect(screen, (255, 50, 50), bubble_rect, 3, border_radius=15) # 紅色邊框
        line1 = font.render(
            f"別灰心，{player_name}！再接再厲！",
            True,
            (255, 255, 255)
        )

        line2 = font.render(
            "以下是你的本次成績：",
            True,
            (255, 255, 255)
        )

        screen.blit(line1, (350, 100))
        screen.blit(line2, (350, 140))

        # 成績板
        text = big_font.render("GAME OVER", True, (255,50,50))
        screen.blit(text,(420, 220))

    # ================= result =================
    elif game_state == "result":
        screen.fill((40, 45, 50)) 
        
        # 讓最後的通關大畫面的過關粒子也能持續更新繪製
        update_particles()
        draw_particles()

        # 引導機器人
        robot_img = pygame.image.load("images/robot_happy.png").convert_alpha()
        robot_img = pygame.transform.scale(robot_img, (150, 150))
        screen.blit(robot_img, (100, 150))
        # 名字標籤
        name_tag = font.render("小幫手喵喵", True, (0, 235, 200))
        screen.blit(name_tag, (100, 320))
        

        # 機器人的恭喜對話框
        bubble_rect = pygame.Rect(320, 80, 600, 120)
        pygame.draw.rect(screen, (30, 30, 35), bubble_rect, border_radius=15)
        pygame.draw.rect(screen, (0, 255, 100), bubble_rect, 3, border_radius=15) # 綠色邊框

        line1 = font.render(f"太棒了，{player_name}！你成功通關了！", True, (255, 255, 255))
        line2 = font.render("來看看你驚人的表現吧：", True, (255, 255, 255))

        screen.blit(line1, (350, 100))
        screen.blit(line2, (350, 140))

        over_text = big_font.render("恭喜通關！", True, (255, 255, 0))
        screen.blit(over_text, (400, 220))

        # 讀取算好的靜態數據
        wpm_text = font.render(f"每分鐘所打的單字數(WPM): {final_wpm:.1f}", True, (255, 255, 255))
        cpm_text = font.render(f"每分鐘所打的字元數(CPM): {final_cpm:.1f}", True, (255, 255, 255))
        acc_text = font.render(f"正確率: {final_accuracy:.1f}%", True, (255, 255, 255))
        score_text = font.render(f"總分: {total_score}", True, (255, 255, 255))

        screen.blit(wpm_text, (450, 300))
        screen.blit(cpm_text, (450, 340))
        screen.blit(acc_text, (450, 380))
        screen.blit(score_text, (450, 420))

        hint = font.render("按下空白鍵返回主畫面", True, (180, 180, 180))
        screen.blit(hint, (400, 520))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    chatbot_step = 2
                    game_state = "menu"

    # ================= FIREWORK =================
    # elif game_state == "firework":
    #     screen.fill((0,0,0))
    #     update_particles()
    #     draw_particles()

    #     title = big_font.render("關卡完成！", True, (255,255,0))
    #     screen.blit(title,(220,150))

    #     if pygame.time.get_ticks() - clear_timer > 3000:
    #         level += 1
    #         if level > 6:
    #             game_state = "menu"
    #         else:
    #             stage_index = 0
    #             score = 0
    #             user_text = ""
    #             active_hit_animations = [] # 重置動畫
    #             words = load_words(level,"first")
    #             stage_start_time = pygame.time.get_ticks()
    #             new_mole()
    #             game_state = "game"
    
    # ================= CLEAR =================
    elif game_state == "clear":
        screen.fill((0, 0, 0))
        update_particles()
        draw_particles()

        elapsed_clear = pygame.time.get_ticks() - clear_timer
        flash = (pygame.time.get_ticks() // 200) % 2
        color = (255, 255, 0) if flash else (255, 180, 0)

        scale = min(1.8, 0.5 + elapsed_clear / 500)
        clear_font = pygame.font.Font("fonts/msjh.ttf", int(80 * scale))
        text = clear_font.render("過關！", True, color)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(text, text_rect)

        sub = font.render("準備好迎接下一關了嗎？", True, (255, 255, 255))
        sub_rect = sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        screen.blit(sub, sub_rect)

        next_text = font.render("按 ENTER 繼續", True, (255, 255, 255))
        next_rect = next_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        screen.blit(next_text, next_rect)

        # 按下 ENTER 進入下一關
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    score = 0
                    user_text = ""
                    active_hit_animations = [] # 進入下一關時，把殘留沒播完的特效清空
                    stage_name = stages[min(stage_index, len(stages)-1)]
                    words = load_words(level, stage_name)
                    stage_start_time = pygame.time.get_ticks()
                    new_mole()
                    game_state = "game"

    pygame.display.flip()

pygame.quit()
sys.exit()

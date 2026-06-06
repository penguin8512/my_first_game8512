import pygame
import random
import csv
import sys

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Typing Whack-a-Mole")

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
        pass
    return result if result else [{"word": "cat"}]


# =========================
# 圖片
# =========================
mole_frames = []
for i in range(8, 0, -1):
    try:
        img = pygame.image.load(f"images/mice{i}.png").convert_alpha()
    except:
        img = pygame.Surface((120, 120))
        img.fill((200, i*25, 0))
    img = pygame.transform.scale(img, (120, 120))
    mole_frames.append(img)

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
# 音效
# =========================
try:
    hit_sound = pygame.mixer.Sound("music/hit.wav")
    wrong_sound = pygame.mixer.Sound("music/wrong.wav")
    clear_sound = pygame.mixer.Sound("music/clear.wav")
    hit_sound.set_volume(0.5)
    wrong_sound.set_volume(0.5)
    clear_sound.set_volume(0.7)
    pygame.mixer.music.load("music/bgm.wav")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
except:
    pass

# =========================
# 狀態變數
# =========================
# 🌟 將初始狀態改為 "chatbot"，讓遊戲一打開先進入聊天流程
game_state = "chatbot" 
chatbot_step = 0        # 🌟 控制機器人對話走到哪一步
player_name = "玩家"     # 🌟 用來儲存玩家輸入的名字

level = 1
stages = ["first", "second", "third"]
stage_index = 0

typed_chars = 0
correct_words = 0
wrong_words = 0
score = 0
total_score = 0
TARGET_SCORE = 1

user_text = ""
words = [{"word": "cat"}]
current_word = random.choice(words)

mole_positions = [
    (150, 250), (350, 250), (550, 250), (750, 250),
    (150, 480), (350, 480), (550, 480), (750, 480),
]

current_pos = random.choice(mole_positions)

MOLE_DURATION = 7000
stage_start_time = pygame.time.get_ticks()
mole_timer = pygame.time.get_ticks()
mole_index = 0
mole_speed = 0.2

clear_timer = 0
particles = []

total_game_time = 0.0
final_cpm = 0.0
final_wpm = 0.0
final_accuracy = 0.0

active_hit_animations = []

# =========================
# 動畫管理類別
# =========================
class HitAnimation:
    def __init__(self, pos):
        self.pos = pos
        self.current_frame = 0
        self.timer = 0.0
        self.frame_duration = 0.08
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
        screen.blit(hit_mole_frames[self.current_frame], (x - 60, y - 30))
        screen.blit(hammer_frames[self.current_frame], (x - 60, y - 80))

# =========================
# UI
# =========================
menu_buttons = {
    "開始遊戲": pygame.Rect(350, 250, 300, 60),
    "遊戲說明": pygame.Rect(350, 350, 300, 60),
    "結束遊戲": pygame.Rect(350, 450, 300, 60)
}

level_buttons = [
    pygame.Rect(120 + i * 140, 250, 120, 60)
    for i in range(6)
]

# =========================
# 工具
# =========================
def new_mole():
    global current_word, current_pos, mole_index, mole_timer
    if words: current_word = random.choice(words)
    old_pos = current_pos
    while True:
        next_pos = random.choice(mole_positions)
        if next_pos != old_pos:
            current_pos = next_pos
            break
    mole_index = 0
    mole_timer = pygame.time.get_ticks()

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

def calculate_stats():
    global final_cpm, final_wpm, final_accuracy
    minutes = max(total_game_time / 60.0, 0.01)
    final_cpm = typed_chars / minutes
    final_wpm = final_cpm / 5.0
    total_words = correct_words + wrong_words
    final_accuracy = (correct_words / max(1, total_words)) * 100

# 🌟 新增：繪製機器人外觀與對話框的共用函式
def draw_robot_ui(bot_text, show_input=False, input_val=""):
    screen.fill((40, 45, 50)) # 深色科技感背景
    
    # 1. 繪製機器人頭像 (用漂亮的圓形加圖案暫代，未來可換圖)
    pygame.draw.circle(screen, (0, 180, 255), (200, 250), 70)
    pygame.draw.circle(screen, (255, 255, 255), (175, 240), 10) # 眼睛
    pygame.draw.circle(screen, (255, 255, 255), (225, 240), 10)
    pygame.draw.rect(screen, (255, 255, 255), (175, 270, 50, 10), border_radius=3) # 微笑
    
    # 名字標籤
    name_tag = font.render("引導員 茉莉", True, (0, 255, 200))
    screen.blit(name_tag, (145, 340))
    
    # 2. 繪製對話氣泡框
    bubble_rect = pygame.Rect(320, 150, 550, 220)
    pygame.draw.rect(screen, (30, 30, 35), bubble_rect, border_radius=15)
    pygame.draw.rect(screen, (0, 180, 255), bubble_rect, 3, border_radius=15)
    
    # 渲染對話文字 (支援多行 \n 換行)
    lines = bot_text.split('\n')
    for idx, line in enumerate(lines):
        rendered_line = font.render(line, True, (255, 255, 255))
        screen.blit(rendered_line, (350, 180 + idx * 40))
        
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
    dt = clock.tick(60) / 1000.0  

    mole_index += mole_speed
    if mole_index >= len(mole_frames):
        mole_index = len(mole_frames) - 1

    for anim in active_hit_animations[:]:
        anim.update(dt)
        if anim.is_finished:
            active_hit_animations.remove(anim)

    # ================= 🌟 新增：CHATBOT 機器人互動狀態 =================
    if game_state == "chatbot":
        if chatbot_step == 0:
            draw_robot_ui("嗨！歡迎來到打字地鼠世界！\n我是你的引導機器人。\n在開始之前，能告訴我你的名字嗎？")
        elif chatbot_step == 1:
            draw_robot_ui("請在下方輸入框寫下名字吧：", show_input=True, input_val=user_text)
        elif chatbot_step == 2:
            draw_robot_ui(f"{player_name}，你好呀！很高興認識你！\n接下來，請讓我為你說明一下遊戲規則。\n準備好了就按 Enter 吧！")
        elif chatbot_step == 3:
            draw_robot_ui("【 遊戲規則說明 】\n1. 地鼠出現時，牠頭上會顯示一個英文單字。\n2. 在時間內正確打出單字並按下 ENTER 敲擊！\n3. 每關有3個小階段，必須達到指定分數才能過關。\n祝你好運！點擊 Enter 進入主畫面！")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if chatbot_step == 1:
                    # 名字輸入階段，此處不阻擋中文，方便玩家命名
                    if event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    elif event.key == pygame.K_RETURN:
                        if user_text.strip() != "":
                            player_name = user_text.strip()
                        user_text = "" # 清空，留給後面遊戲打字用
                        chatbot_step = 2
                    else:
                        if event.unicode and event.unicode.isprintable():
                            user_text += event.unicode
                else:
                    # 其他步驟點 Enter 進入下一步
                    if event.key == pygame.K_RETURN:
                        chatbot_step += 1
                        if chatbot_step > 3:
                            game_state = "menu" # 對話結束，跳轉至主畫面

    # ================= MENU =================
    elif game_state == "menu":
        screen.fill((20, 20, 20))
        title = big_font.render("TYPING WHACK-A-MOLE", True, (255, 255, 255))
        screen.blit(title, (180, 120))

        for name, btn in menu_buttons.items():
            pygame.draw.rect(screen, (0, 200, 0), btn)
            screen.blit(font.render(name.upper(), True, (0, 0, 0)), (btn.x + 85, btn.y + 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_buttons["開始遊戲"].collidepoint(event.pos):
                    score = 0
                    total_score = 0
                    stage_index = 0
                    user_text = ""
                    typed_chars = 0
                    correct_words = 0
                    wrong_words = 0
                    total_game_time = 0.0 
                    active_hit_animations = [] 
                    stage_start_time = pygame.time.get_ticks()
                    mole_timer = pygame.time.get_ticks()
                    game_state = "level"
                if menu_buttons["遊戲說明"].collidepoint(event.pos):
                    game_state = "how"
                if menu_buttons["結束遊戲"].collidepoint(event.pos):
                    running = False

    # ================= LEVEL SELECT =================
    elif game_state == "level":
        screen.fill((0, 0, 0))
        title = big_font.render("SELECT LEVEL", True, (255, 255, 255))
        screen.blit(title, (350, 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, btn in enumerate(level_buttons):
                    if btn.collidepoint(event.pos):
                        level = i + 1
                        stage_index = 0
                        score = 0
                        total_score = 0
                        user_text = ""
                        typed_chars = 0
                        correct_words = 0
                        wrong_words = 0
                        total_game_time = 0.0 
                        active_hit_animations = [] 
                        stage_start_time = pygame.time.get_ticks()
                        mole_timer = pygame.time.get_ticks()
                        words = load_words(level, stages[0])
                        new_mole()
                        game_state = "game"

        for i, btn in enumerate(level_buttons):
            pygame.draw.rect(screen, (0, 200, 0), btn)
            screen.blit(font.render(f"L{i+1}", True, (0, 0, 0)), (btn.x + 35, btn.y + 15))

    # ================= HOW =================
    elif game_state == "how":
        screen.fill((30, 30, 30))
        texts = [
            "遊戲說明", "這是一個打地鼠遊戲", "當地鼠出現時，打字框會顯示一個英文單字",
            "你需要在地鼠消失前，正確輸入單字並按下ENTER", "每關有三個階段，每個階段需要達到一定分數才能過關",
            "總共有六關，祝各位好運~", "", "按下ENTER返回選單"
        ]
        for i, t in enumerate(texts):
            screen.blit(font.render(t, True, (255, 255, 255)), (150, 150 + i * 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = "menu"

    # ================= GAME =================
    elif game_state == "game":
        screen.blit(bg_img, (0, 0))
        total_game_time += dt

        elapsed = (pygame.time.get_ticks() - stage_start_time) / 1000
        current_time = pygame.time.get_ticks()

        if current_time - mole_timer >= MOLE_DURATION:
            new_mole()

        if elapsed >= 10:
            user_text = ""
            if score >= TARGET_SCORE:
                try: clear_sound.play()
                except: pass
                
                spawn_particles()

                if stage_index < 2:
                    stage_index += 1
                    game_state = "clear"
                    clear_timer = pygame.time.get_ticks()
                else:
                    calculate_stats() 
                    game_state = "result"
                    clear_timer = pygame.time.get_ticks()
            else:
                calculate_stats() 
                game_state = "over"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = "menu"
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                elif event.key == pygame.K_RETURN:
                     
                    if user_text.lower() == current_word["word"].lower():
                        score += 1
                        total_score += 1
                        correct_words += 1
                        typed_chars += len(user_text)  
                        
                        active_hit_animations.append(HitAnimation(current_pos))

                        try: hit_sound.play()
                        except: pass
                    else:
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
                            pass

        draw_holes()
        draw_mole()

        for anim in active_hit_animations:
            anim.draw()

        # 輸入框
        box_width = 500
        box_height = 50
        box_x = (WIDTH - box_width) // 2  
        box_y = 580
        input_box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        
        pygame.draw.rect(screen, (30, 30, 35), input_box_rect)
        box_color = (0, 220, 100) if user_text else (150, 150, 150)
        pygame.draw.rect(screen, box_color, input_box_rect, 3, border_radius=8) 
        
        text_surface = font.render(user_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.midleft = (box_x + 15, box_y + box_height // 2)
        screen.blit(text_surface, text_rect)

        screen.blit(font.render(f"L{level}-{stages[stage_index]}", True, (255,255,255)), (50, 20))
        screen.blit(font.render(f"Score:{total_score}", True, (255,255,255)), (50, 60))
        screen.blit(font.render(f"Time:{max(0, int(10 - elapsed))}", True, (255,255,0)), (820, 20)) 
        
    # ================= GAME OVER (🌟 機器人失敗結算) =================
    elif game_state == "over":
        screen.fill((40, 45, 50)) # 使用機器人底色
        
        # 繪製引導機器人
        pygame.draw.circle(screen, (0, 180, 255), (200, 250), 70)
        pygame.draw.circle(screen, (255, 255, 255), (175, 240), 10) 
        pygame.draw.circle(screen, (255, 255, 255), (225, 240), 10)
        pygame.draw.rect(screen, (255, 255, 255), (185, 270, 30, 5), border_radius=2) # 變成一條直線癟嘴，代表難過
        name_tag = font.render("引導員 茉莉", True, (0, 255, 200))
        screen.blit(name_tag, (145, 340))

        # 機器人的難過對話框
        bubble_rect = pygame.Rect(320, 80, 550, 120)
        pygame.draw.rect(screen, (30, 30, 35), bubble_rect, border_radius=15)
        pygame.draw.rect(screen, (255, 50, 50), bubble_rect, 3, border_radius=15) # 紅色邊框
        bot_msg = font.render(f"別灰心，{player_name}！再接再厲！\n以下是你的本次成績：", True, (255, 255, 255))
        screen.blit(bot_msg, (350, 100))

        # 成績板
        text = big_font.render("GAME OVER", True, (255,50,50))
        screen.blit(text,(420, 220))

        stats1 = font.render(f"WPM: {final_wpm:.1f}", True, (255,255,255))
        stats2 = font.render(f"CPM: {final_cpm:.1f}", True, (255,255,255))
        stats3 = font.render(f"Accuracy: {final_accuracy:.1f}%", True, (255,255,255))
        stats4 = font.render(f"Total Score: {total_score}/{TARGET_SCORE}", True, (255,255,255))

        screen.blit(stats1,(450,300))
        screen.blit(stats2,(450,340))
        screen.blit(stats3,(450,380))
        screen.blit(stats4,(450,420))
        
        hint = font.render("Press SPACE to Menu", True, (255,255,255))
        screen.blit(hint,(420,520))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    chatbot_step = 2 # 回到選單前，下次玩直接從步驟2(打過招呼)開始
                    game_state = "menu"

    # ================= result (🌟 機器人成功結算) =================
    elif game_state == "result":
        screen.fill((40, 45, 50)) 
        update_particles()
        draw_particles()

        # 繪製引導機器人
        pygame.draw.circle(screen, (0, 180, 255), (200, 250), 70)
        pygame.draw.circle(screen, (255, 255, 255), (175, 240), 10) 
        pygame.draw.circle(screen, (255, 255, 255), (225, 240), 10)
        pygame.draw.rect(screen, (255, 255, 255), (175, 270, 50, 10), border_radius=3) # 開心微笑
        name_tag = font.render("引導員 茉莉", True, (0, 255, 200))
        screen.blit(name_tag, (145, 340))

        # 機器人的恭喜對話框
        bubble_rect = pygame.Rect(320, 80, 550, 120)
        pygame.draw.rect(screen, (30, 30, 35), bubble_rect, border_radius=15)
        pygame.draw.rect(screen, (0, 255, 100), bubble_rect, 3, border_radius=15) # 綠色邊框
        bot_msg = font.render(f"太強了，{player_name}！你成功通關了！\n來看看你驚人的表現吧：", True, (255, 255, 255))
        screen.blit(bot_msg, (350, 100))

        over_text = big_font.render("STAGE COMPLETE!", True, (255, 255, 0))
        screen.blit(over_text, (400, 220))

        wpm_text = font.render(f"WPM: {final_wpm:.1f}", True, (255, 255, 255))
        cpm_text = font.render(f"CPM: {final_cpm:.1f}", True, (255, 255, 255))
        acc_text = font.render(f"Accuracy: {final_accuracy:.1f}%", True, (255, 255, 255))
        score_text = font.render(f"Score: {total_score}", True, (255, 255, 255))

        screen.blit(wpm_text, (450, 300))
        screen.blit(cpm_text, (450, 340))
        screen.blit(acc_text, (450, 380))
        screen.blit(score_text, (450, 420))

        hint = font.render("Press SPACE to return menu", True, (180, 180, 180))
        screen.blit(hint, (400, 520))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    chatbot_step = 2
                    game_state = "menu"

    # ================= FIREWORK =================
    elif game_state == "firework":
        screen.fill((0,0,0))
        update_particles()
        draw_particles()

        title = big_font.render("LEVEL COMPLETE!", True, (255,255,0))
        screen.blit(title,(220,150))

        if pygame.time.get_ticks() - clear_timer > 3000:
            level += 1
            if level > 6:
                game_state = "menu"
            else:
                stage_index = 0
                score = 0
                user_text = ""
                active_hit_animations = [] 
                words = load_words(level,"first")
                stage_start_time = pygame.time.get_ticks()
                new_mole()
                game_state = "game"

    # ================= CLEAR =================
    elif game_state == "clear":
        screen.fill((0, 0, 0))
        update_particles()
        draw_particles()

        elapsed_clear = pygame.time.get_ticks() - clear_timer
        flash = (pygame.time.get_ticks() // 200) % 2
        color = (255, 255, 0) if flash else (255, 180, 0)

        scale = min(1.8, 0.5 + elapsed_clear / 500)
        clear_font = pygame.font.Font(None, int(80 * scale))
        text = clear_font.render("LEVEL CLEAR!", True, color)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(text, text_rect)

        sub = font.render("GET READY FOR NEXT LEVEL", True, (255, 255, 255))
        sub_rect = sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        screen.blit(sub, sub_rect)

        if elapsed_clear > 2000:
            score = 0
            user_text = ""
            active_hit_animations = [] 
            stage_name = stages[min(stage_index, len(stages)-1)]
            words = load_words(level, stage_name)
            stage_start_time = pygame.time.get_ticks()
            new_mole()
            game_state = "game"

    pygame.display.flip()

pygame.quit()
sys.exit()
import pygame
import random
import csv
import sys
from robot_screen import RobotScreen

# =========================
# 初始化
# =========================
pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Typing Whack-a-Mole")
clock = pygame.time.Clock()

# =========================
# 字體
# =========================
def load_font(path, size, fallback_size=None):
    try:
        return pygame.font.Font(path, size)
    except Exception:
        return pygame.font.Font(None, fallback_size or size)

fonts = {
    'small':  load_font("fonts/msjh.ttf", 22, 24),
    'normal': load_font("fonts/msjh.ttf", 30, 32),
    'big':    load_font("fonts/msjh.ttf", 44, 48),
    'title':  load_font("fonts/msjh.ttf", 60, 64),
}

# =========================
# 讀 CSV
# =========================
def load_words(level, category):
    result = []
    try:
        with open("words.csv", newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["level"] == str(level) and row["category"] == category:
                    result.append({"en": row["english"], "zh": row["chinese"]})
    except FileNotFoundError:
        pass
    return result or [{"en": "cat", "zh": "貓"}, {"en": "dog", "zh": "狗"},
                      {"en": "bird", "zh": "鳥"}, {"en": "fish", "zh": "魚"}]

# =========================
# 動畫圖片
# =========================
mole_frames = []
try:
    for i in range(8, 0, -1):
        img = pygame.image.load(f"images/mice{i}.png").convert_alpha()
        img = pygame.transform.scale(img, (120, 120))
        mole_frames.append(img)
except Exception:
    # fallback: draw a circle
    surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.circle(surf, (180, 100, 60), (60, 60), 50)
    pygame.draw.circle(surf, (220, 150, 100), (60, 60), 50, 3)
    mole_frames = [surf]

try:
    hole_img = pygame.image.load("images/mice8.png").convert_alpha()
    hole_img = pygame.transform.scale(hole_img, (140, 80))
except Exception:
    hole_img = pygame.Surface((140, 80), pygame.SRCALPHA)
    pygame.draw.ellipse(hole_img, (40, 30, 20), (0, 0, 140, 80))

try:
    bg_img = pygame.image.load("images/black.png").convert()
    bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
except Exception:
    bg_img = pygame.Surface((WIDTH, HEIGHT))
    bg_img.fill((18, 28, 18))

# =========================
# 顏色
# =========================
WHITE  = (255, 255, 255)
BLACK  = (20,  20,  20)
GREEN  = (0,   200, 0)
RED    = (220, 60,  60)
YELLOW = (255, 220, 0)

# =========================
# 地鼠位置
# =========================
mole_positions = [
    (150, 180), (350, 180), (550, 180), (750, 180),
    (150, 420), (350, 420), (550, 420), (750, 420),
]

# =========================
# Level / Category 按鈕
# =========================
level_buttons = [
    pygame.Rect(120 + (i % 3)*250, 180 + (i//3)*120, 180, 70)
    for i in range(7)
]
animal_button = pygame.Rect(350, 220, 300, 70)
food_button   = pygame.Rect(350, 340, 300, 70)
school_button = pygame.Rect(350, 460, 300, 70)

# =========================
# 遊戲狀態
# =========================
game_state       = "robot_intro"   # robot_intro/robot_story/hub/menu/category/game/over/review/exit
selected_level   = None
selected_category= None
player_name      = "玩家"
words            = []
wrong_words      = []

# 遊戲資料
current_word     = {"en": "cat", "zh": "貓"}
current_pos      = random.choice(mole_positions)
user_text        = ""
score            = 0
lives            = 5
MOLE_DURATION    = 3000
mole_timer       = pygame.time.get_ticks()
mole_frame_index = 0.0
mole_anim_speed  = 0.2

# =========================
# 機器人畫面
# =========================
robot_screen = RobotScreen(screen, fonts)
robot_screen.show_intro()

# =========================
# 遊戲工具函式
# =========================
def new_mole():
    global current_word, current_pos, mole_timer, mole_frame_index
    current_word     = random.choice(words)
    current_pos      = random.choice(mole_positions)
    mole_timer       = pygame.time.get_ticks()
    mole_frame_index = 0.0

def draw_holes():
    for pos in mole_positions:
        x, y = pos
        screen.blit(hole_img, (x - 70, y))

def draw_mole():
    x, y  = current_pos
    frame = mole_frames[int(mole_frame_index) % len(mole_frames)]
    screen.blit(frame, (x - 60, y - 30))
    txt_str = f'{current_word["en"]} {current_word["zh"]}'
    txt     = fonts['normal'].render(txt_str, True, WHITE)
    screen.blit(txt, (x - 80, y - 130))

def draw_rounded_rect(surface, color, rect, radius=12):
    pygame.draw.rect(surface, color, pygame.Rect(rect), border_radius=radius)

# =========================
# 主迴圈
# =========================
running = True

while running:

    clock.tick(60)
    robot_screen.update()

    mole_frame_index += mole_anim_speed
    if mole_frame_index >= len(mole_frames):
        mole_frame_index = len(mole_frames) - 1

    # ── 事件 ───────────────────────────────────────────────────────
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            if game_state in ("robot_intro", "robot_story", "hub"):
                # show exit dialog
                prev_state  = game_state
                game_state  = "exit_confirm"
                robot_screen.show_exit()
            else:
                game_state = "exit_confirm"
                robot_screen.show_exit()

        # ── 機器人畫面事件 ────────────────────────────────────────
        if game_state in ("robot_intro", "robot_story", "hub", "exit_confirm", "review_screen"):
            result = robot_screen.handle_event(event)
            if result:
                action = result.get("action")

                if action == "name_confirmed":
                    player_name = result["name"]
                    robot_screen.player_name = player_name
                    # modify first story message to include name
                    RobotScreen.STORY_MSGS[0] = f"太好了，{player_name}！歡迎來到「打字打地鼠」！🎮"
                    game_state = "robot_story"
                    robot_screen.show_story()

                elif action == "start_game":
                    game_state = "hub"
                    robot_screen.show_hub()

                elif action == "goto_menu":
                    game_state = "menu"
                    score      = 0
                    lives      = 5
                    wrong_words= []

                elif action == "quit":
                    running = False

                elif action == "cancel_exit":
                    game_state = "menu"

                elif action == "review_wrong":
                    # start game with only wrong words
                    words = wrong_words[:]
                    if words:
                        score      = 0
                        lives      = 5
                        user_text  = ""
                        wrong_words= []
                        new_mole()
                        game_state = "game"

        # ── MENU ─────────────────────────────────────────────────
        elif game_state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, btn in enumerate(level_buttons):
                    if btn.collidepoint(event.pos):
                        selected_level = i + 1
                        game_state     = "category"

        # ── CATEGORY ─────────────────────────────────────────────
        elif game_state == "category":
            if event.type == pygame.MOUSEBUTTONDOWN:
                cat = None
                if animal_button.collidepoint(event.pos):  cat = "animals"
                elif food_button.collidepoint(event.pos):  cat = "food"
                elif school_button.collidepoint(event.pos):cat = "school"
                if cat:
                    selected_category = cat
                    words = load_words(selected_level, selected_category)
                    score      = 0
                    lives      = 5
                    user_text  = ""
                    wrong_words= []
                    new_mole()
                    game_state = "game"

        # ── GAME ─────────────────────────────────────────────────
        elif game_state == "game":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = "menu"
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                elif event.key == pygame.K_RETURN:
                    if user_text.lower() == current_word["en"].lower():
                        score += 1
                    else:
                        lives -= 1
                        wrong_words.append(current_word)
                    user_text = ""
                    new_mole()
                else:
                    if event.unicode.isalpha():
                        user_text += event.unicode

        # ── GAME OVER ─────────────────────────────────────────────
        elif game_state == "over":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # show review screen
                game_state = "review_screen"
                robot_screen.show_review(wrong_words, None, None)

    # ── 繪製 ───────────────────────────────────────────────────────

    if game_state in ("robot_intro", "robot_story", "hub"):
        robot_screen.draw()

    elif game_state == "exit_confirm":
        robot_screen.draw()

    elif game_state == "review_screen":
        robot_screen.draw()

    elif game_state == "menu":
        screen.fill(BLACK)
        title = fonts['title'].render(f"SELECT LEVEL", True, WHITE)
        screen.blit(title, (220, 50))
        hi = fonts['normal'].render(f"歡迎回來，{player_name}！", True, YELLOW)
        screen.blit(hi, (340, 115))
        for i, btn in enumerate(level_buttons):
            draw_rounded_rect(screen, GREEN, btn, 10)
            t = fonts['normal'].render(f"LEVEL {i+1}", True, BLACK)
            screen.blit(t, (btn.x + 25, btn.y + 20))

    elif game_state == "category":
        screen.fill(BLACK)
        t = fonts['big'].render(f"LEVEL {selected_level}", True, WHITE)
        screen.blit(t, (330, 100))
        draw_rounded_rect(screen, GREEN,  animal_button, 12)
        draw_rounded_rect(screen, YELLOW, food_button,   12)
        draw_rounded_rect(screen, RED,    school_button, 12)
        screen.blit(fonts['normal'].render("ANIMALS", True, BLACK), (410, 240))
        screen.blit(fonts['normal'].render("FOOD",    True, BLACK), (450, 360))
        screen.blit(fonts['normal'].render("SCHOOL",  True, BLACK), (420, 480))

    elif game_state == "game":
        screen.blit(bg_img, (0, 0))

        if pygame.time.get_ticks() - mole_timer > MOLE_DURATION:
            lives -= 1
            wrong_words.append(current_word)
            new_mole()

        if lives <= 0:
            game_state = "over"

        draw_holes()
        draw_mole()

        draw_rounded_rect(screen, (40, 40, 60), (250, 575, 500, 66), 12)
        pygame.draw.rect(screen, WHITE, (250, 575, 500, 66), 2, border_radius=12)
        screen.blit(fonts['normal'].render(user_text, True, WHITE), (270, 590))
        screen.blit(fonts['normal'].render(f"Score: {score}", True, WHITE), (50, 50))
        screen.blit(fonts['normal'].render(f"Lives: {lives}", True, RED),   (50, 100))
        screen.blit(fonts['small'].render(f"Hi {player_name}！加油！", True, YELLOW), (50, 150))

    elif game_state == "over":
        screen.fill(BLACK)
        screen.blit(fonts['title'].render("GAME OVER", True, RED),   (260, 220))
        screen.blit(fonts['normal'].render(f"Score: {score}", True, WHITE), (420, 330))
        screen.blit(fonts['normal'].render(f"答錯 {len(wrong_words)} 題", True, YELLOW), (400, 380))
        screen.blit(fonts['normal'].render("按 SPACE 查看統計 →", True, WHITE), (300, 450))

    pygame.display.flip()

pygame.quit()
sys.exit()
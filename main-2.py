import pygame
import random
import csv

# =========================
# 初始化
# =========================
pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Typing Whack-a-Mole")

clock = pygame.time.Clock()

# =========================
# 讀 CSV（level + category）
# =========================
def load_words(level, category):

    result = []

    with open("words.csv", newline='', encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["level"] == str(level) and row["category"] == category:
                result.append({
                    "en": row["english"],
                    "zh": row["chinese"]
                })

    return result

# =========================
# 動畫
# =========================
mole_frames = []

for i in range(8, 0, -1):
    img = pygame.image.load(f"images/mice{i}.png").convert_alpha()
    img = pygame.transform.scale(img, (120, 120))
    mole_frames.append(img)

mole_frame_index = 0
mole_anim_speed = 0.2

# =========================
# 顏色
# =========================
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GREEN = (0, 200, 0)
RED = (220, 60, 60)
YELLOW = (255, 220, 0)

# =========================
# 圖片
# =========================
hole_img = pygame.image.load("images/mice8.png").convert_alpha()
bg_img = pygame.image.load("images/black.png").convert()

hole_img = pygame.transform.scale(hole_img, (140, 80))
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

# =========================
# 字體
# =========================
font = pygame.font.Font("fonts/msjh.ttf", 30)
big_font = pygame.font.Font(None,60)

# =========================
# 遊戲狀態
# =========================
game_state = "menu"
selected_level = None
selected_category = None

# =========================
# Level 按鈕（7個）
# =========================
level_buttons = []

for i in range(7):
    btn = pygame.Rect(
        120 + (i % 3) * 250,
        180 + (i // 3) * 120,
        180,
        70
    )
    level_buttons.append(btn)

# =========================
# Category 按鈕
# =========================
animal_button = pygame.Rect(350, 220, 300, 70)
food_button = pygame.Rect(350, 340, 300, 70)
school_button = pygame.Rect(350, 460, 300, 70)

# =========================
# 地鼠位置
# =========================
mole_positions = [
    (150, 180), (350, 180), (550, 180), (750, 180),
    (150, 420), (350, 420), (550, 420), (750, 420),
]

# =========================
# 遊戲資料
# =========================
words = [{"en": "cat", "zh": "貓"}]

current_word = random.choice(words)
current_pos = random.choice(mole_positions)

user_text = ""
score = 0
lives = 5

MOLE_DURATION = 3000
mole_timer = pygame.time.get_ticks()

# =========================
# 換地鼠
# =========================
def new_mole():
    global current_word, current_pos, mole_timer, mole_frame_index

    current_word = random.choice(words)
    current_pos = random.choice(mole_positions)
    mole_timer = pygame.time.get_ticks()
    mole_frame_index = 0

# =========================
# 畫洞
# =========================
def draw_holes():
    for pos in mole_positions:
        x, y = pos
        screen.blit(hole_img, (x - 70, y))

# =========================
# 畫地鼠（中英）
# =========================
def draw_mole():
    x, y = current_pos

    frame = mole_frames[int(mole_frame_index)]
    screen.blit(frame, (x - 60, y - 30))

    # ⭐ 顯示 英文 + 中文
    text_str = f'{current_word["en"]} {current_word["zh"]}'
    text = font.render(text_str, True, WHITE)

    screen.blit(text, (x - 80, y - 130))

# =========================
# 初始化
# =========================
new_mole()

# =========================
# 主迴圈
# =========================
running = True

while running:

    clock.tick(60)

    mole_frame_index += mole_anim_speed
    if mole_frame_index >= len(mole_frames):
        mole_frame_index = len(mole_frames) - 1

    # =========================
    # MENU（選 Level）
    # =========================
    if game_state == "menu":

        screen.fill(BLACK)

        title = big_font.render("SELECT LEVEL", True, WHITE)
        screen.blit(title, (280, 70))

        for i, btn in enumerate(level_buttons):
            pygame.draw.rect(screen, GREEN, btn)
            text = font.render(f"LEVEL {i+1}", True, BLACK)
            screen.blit(text, (btn.x + 25, btn.y + 20))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, btn in enumerate(level_buttons):
                    if btn.collidepoint(event.pos):
                        selected_level = i + 1
                        game_state = "category"

    # =========================
    # CATEGORY（選類型）
    # =========================
    elif game_state == "category":

        screen.fill(BLACK)

        title = big_font.render(f"LEVEL {selected_level}", True, WHITE)
        screen.blit(title, (330, 100))

        pygame.draw.rect(screen, GREEN, animal_button)
        pygame.draw.rect(screen, YELLOW, food_button)
        pygame.draw.rect(screen, RED, school_button)

        screen.blit(font.render("ANIMALS", True, BLACK), (410, 240))
        screen.blit(font.render("FOOD", True, BLACK), (450, 360))
        screen.blit(font.render("SCHOOL", True, BLACK), (420, 480))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:

                if animal_button.collidepoint(event.pos):
                    selected_category = "animals"

                elif food_button.collidepoint(event.pos):
                    selected_category = "food"

                elif school_button.collidepoint(event.pos):
                    selected_category = "school"

                if selected_category:

                    words = load_words(selected_level, selected_category)

                    if len(words) == 0:
                        words = [{"en": "empty", "zh": "空"}]

                    score = 0
                    lives = 5
                    user_text = ""

                    new_mole()
                    game_state = "game"

    # =========================
    # GAME
    # =========================
    elif game_state == "game":

        screen.blit(bg_img, (0, 0))

        if pygame.time.get_ticks() - mole_timer > MOLE_DURATION:
            lives -= 1
            new_mole()

        if lives <= 0:
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

                    if user_text.lower() == current_word["en"].lower():
                        score += 1
                    else:
                        lives -= 1

                    user_text = ""
                    new_mole()

                else:
                    if event.unicode.isalpha():
                        user_text += event.unicode

        draw_holes()
        draw_mole()

        pygame.draw.rect(screen, WHITE, (250, 580, 500, 60), 2)
        screen.blit(font.render(user_text, True, WHITE), (270, 590))

        screen.blit(font.render(f"得分: {score}", True, WHITE), (50, 50))
        screen.blit(font.render(f"生命: {lives}", True, RED), (50, 100))

    # =========================
    # GAME OVER
    # =========================
    elif game_state == "over":

        screen.fill(BLACK)

        screen.blit(big_font.render("GAME OVER", True, RED), (300, 230))
        screen.blit(font.render(f"得分: {score}", True, WHITE), (420, 340))
        screen.blit(font.render("按空白鍵回到選單", True, WHITE), (320, 450))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_state = "menu"

    pygame.display.flip()

pygame.quit()
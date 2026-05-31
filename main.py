import pygame

import random

# =========================
# 初始化
# =========================
pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Typing Whack-a-Mole")

clock = pygame.time.Clock()

mole_frames = []

#動畫
for i in range(8, 0, -1):
    img = pygame.image.load(f"images/mice{i}.png").convert_alpha()
    img = pygame.transform.scale(img, (120, 120))
    mole_frames.append(img)
mole_frame_index = 0
mole_anim_speed = 0.2   # 控制動畫速度（越大越快）





# =========================
# 顏色
# =========================
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GREEN = (0, 200, 0)
RED = (220, 60, 60)

# =========================
# 載入圖片
# =========================
mole_img = pygame.image.load("images/mice1.png").convert_alpha()
hole_img = pygame.image.load("images/mice8.png").convert_alpha()
bg_img = pygame.image.load("images/black.png").convert()

mole_img = pygame.transform.scale(mole_img, (120, 120))
hole_img = pygame.transform.scale(hole_img, (140, 80))
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

# =========================
# 字體
# =========================
font = pygame.font.Font(None, 48)
big_font = pygame.font.Font(None, 80)

# =========================
# 遊戲狀態
# =========================
game_state = "menu"   # menu / game / over

selected_level = None
selected_category = None

# =========================
# 按鈕
level_buttons = []

for i in range(7):

    btn = pygame.Rect(120 + (i % 3) * 250,
                      180 + (i // 3) * 120,
                      180,
                      70)

    level_buttons.append(btn)
# =========================
# 遊戲資料
# =========================
mole_positions = [
    (150, 180), (350, 180), (550, 180), (750, 180),
    (150, 420), (350, 420), (550, 420), (750, 420),
]


#單字庫
word_levels = {

    "level1": {
        "animals": ["cat", "dog", "pig"],
        "food": ["cake", "rice", "milk"],
        "school": ["pen", "book", "desk"]
    },

    "level2": {
        "animals": ["rabbit", "tiger", "panda"],
        "food": ["banana", "burger", "noodle"],
        "school": ["eraser", "teacher", "student"]
    },

    "level3": {
        "animals": [a],
        "food": [a],
        "school": [a]
    },

    "level4": {
        "animals": [a],
        "food": [a],
        "school": [a]
    },

    "level5": {
        "animals": [a],
        "food": [a],
        "school": [a]
    },

    "level6": {
        "animals": [a],
        "food": [a],
        "school": [a]
    },

    "level7": {
        "animals": [a],
        "food": [a],
        "school": [a]
    }
}

current_word = random.choice(words)
current_pos = random.choice(mole_positions)

user_text = ""
score = 0
lives = 5

MOLE_DURATION = 3000
mole_timer = pygame.time.get_ticks()

# =========================
# 換地鼠
def new_mole():
    global current_word, current_pos, mole_timer
    global mole_frame_index

    current_word = random.choice(words)
    current_pos = random.choice(mole_positions)
    mole_timer = pygame.time.get_ticks()

    mole_frame_index = 0   # 每次重置動畫
# =========================
# 畫洞
# =========================
def draw_holes():
    for pos in mole_positions:
        x, y = pos
        
        screen.blit(hole_img, (x - 70, y))

# =========================
# 畫地鼠
# =========================
def draw_mole():
    x, y = current_pos

    frame = mole_frames[int(mole_frame_index)]

    screen.blit(frame, (x - 60, y - 30))

    text = font.render(current_word, True, WHITE)
    screen.blit(text, (x - 40, y - 130))

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
    # MENU 畫面
    # =========================
    if game_state == "menu":

        screen.fill(BLACK)

        title = big_font.render("Typing Whack-a-Mole", True, WHITE)
        screen.blit(title, (250, 200))

        pygame.draw.rect(screen, GREEN, button)
        btn_text = font.render("START GAME", True, BLACK)
        screen.blit(btn_text, (385, 370))

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if button.collidepoint(event.pos):
                    game_state = "game"
                    score = 0
                    lives = 5
                    user_text = ""
                    new_mole()

    # =========================
    # GAME 畫面
    # =========================
    elif game_state == "game":

        screen.blit(bg_img, (0, 0))

        # 遊戲時間
        if pygame.time.get_ticks() - mole_timer > MOLE_DURATION:
            lives -= 1
            new_mole()

        if lives <= 0:
            game_state = "over"

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]

                elif event.key == pygame.K_RETURN:

                    if user_text.lower() == current_word.lower():
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

        screen.blit(font.render(f"Score: {score}", True, WHITE), (50, 50))
        screen.blit(font.render(f"Lives: {lives}", True, RED), (50, 100))

    # =========================
    # GAME OVER 畫面
    # =========================
    elif game_state == "over":

        screen.fill(BLACK)

        text = big_font.render("GAME OVER", True, RED)
        screen.blit(text, (330, 250))

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (420, 350))

        restart_text = font.render("Click to Return Menu", True, WHITE)
        screen.blit(restart_text, (350, 450))

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                game_state = "menu"

    pygame.display.flip()

pygame.quit()
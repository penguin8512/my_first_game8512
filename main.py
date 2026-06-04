import pygame
import random
import csv



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

    with open("words.csv", newline='', encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["level"] == str(level) and row["stage"] == stage:
                result.append({"word": row["english"]})

    return result


# =========================
# 圖片
# =========================
mole_frames = []
for i in range(8, 0, -1):
    img = pygame.image.load(f"images/mice{i}.png").convert_alpha()
    img = pygame.transform.scale(img, (120, 120))
    mole_frames.append(img)

hole_img = pygame.image.load("images/mice8.png").convert_alpha()
bg_img = pygame.image.load("images/black.png").convert()

hole_img = pygame.transform.scale(hole_img, (140, 80))
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

font = pygame.font.Font("fonts/msjh.ttf", 30)
big_font = pygame.font.Font(None, 60)

# =========================
# 音效
# =========================
hit_sound = pygame.mixer.Sound("music/hit.wav")
wrong_sound = pygame.mixer.Sound("music/wrong.wav")
clear_sound = pygame.mixer.Sound("music/clear.wav")

hit_sound.set_volume(0.5)
wrong_sound.set_volume(0.5)
clear_sound.set_volume(0.7)

pygame.mixer.music.load("music/bgm.wav")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)
# =========================
# 狀態
# =========================
game_state = "menu"

level = 1
stages = ["first", "second", "third"]
stage_index = 0
start_time = pygame.time.get_ticks()
typed_chars = 0
correct_words = 0
wrong_words = 0
score = 0
#過關分數
TARGET_SCORE = 1

user_text = ""

words = [{"word": "cat"}]
current_word = random.choice(words)

mole_positions = [
    (150, 250), (350, 250), (550, 250), (750, 250),
    (150, 480), (350, 480), (550, 480), (750, 480),
]

current_pos = random.choice(mole_positions)

#地鼠消失時間
MOLE_DURATION = 7000
stage_start_time = pygame.time.get_ticks()
mole_timer = pygame.time.get_ticks()
mole_index = 0
mole_speed = 0.2

clear_timer = 0

particles = []

# =========================
# UI
# =========================
menu_buttons = {
    "開始遊戲": pygame.Rect(350, 250, 300, 60),
    "遊戲說明": pygame.Rect(350, 350, 300, 60),
    "結束遊戲": pygame.Rect(350, 450, 300, 60)
    # pygame.Rect(x, y, width, height)
    # pygame.Rect(左上角 X 座標（水平位置）, 左上角 Y 座標（垂直位置）, 寬度（橫向大小）, 高度（縱向大小）)
}

level_buttons = [
    pygame.Rect(120 + i * 140, 250, 120, 60)
    for i in range(6)
]


# =========================
# 工具
# =========================
def new_mole():
    global current_word,current_pos,mole_index,mole_timer

    current_word=random.choice(words)
    current_pos=random.choice(mole_positions)

    mole_index=0
    mole_timer=pygame.time.get_ticks()


def draw_mole():
    x, y = current_pos

    frame = mole_frames[int(mole_index)]
    screen.blit(frame, (x - 60, y - 30))

    text = font.render(current_word["word"], True, (255, 255, 255))

    text_rect = text.get_rect(
        center=(x, y - 60)
    )

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
        pygame.draw.circle(
            screen,
            (255, 255, 0),
            (int(p[0]), int(p[1])),
            int(p[4])
        )

def start_clear():
    global game_state, clear_timer

    clear_sound.play()
    spawn_particles()

    game_state = "clear"
    clear_timer = pygame.time.get_ticks()


new_mole()

# =========================
# LOOP
# =========================
running = True

while running:
    clock.tick(60)

    mole_index += mole_speed
    if mole_index >= len(mole_frames):
        mole_index = len(mole_frames) - 1

    # ================= MENU =================
    if game_state == "menu":
        screen.fill((20, 20, 20))

        title = big_font.render("TYPING WHACK-A-MOLE", True, (255, 255, 255))
        screen.blit(title, (180, 120))

        for name, btn in menu_buttons.items():
            pygame.draw.rect(screen, (0, 200, 0), btn)
            screen.blit(font.render(name.upper(), True, (0, 0, 0)),(btn.x + 85, btn.y + 10)) # 主選單按鈕的文字設定

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_buttons["開始遊戲"].collidepoint(event.pos):

                    score = 0
                    stage_index = 0
                    user_text = ""

                    start_time = pygame.time.get_ticks()
                    typed_chars = 0
                    correct_words = 0
                    wrong_words = 0

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
                        user_text = ""

                        start_time = pygame.time.get_ticks()
                        typed_chars = 0
                        correct_words = 0
                        wrong_words = 0

                        stage_start_time = pygame.time.get_ticks()
                        mole_timer = pygame.time.get_ticks()

                        words = load_words(level, stages[0])

                        new_mole()

                        game_state = "game"

        for i, btn in enumerate(level_buttons):
            pygame.draw.rect(screen, (0, 200, 0), btn)
            screen.blit(font.render(f"L{i+1}", True, (0, 0, 0)),
                        (btn.x + 35, btn.y + 15))

    # ================= HOW =================
    elif game_state == "how":
        screen.fill((30, 30, 30))

        texts = [
            "遊戲說明",
            "這是一個打地鼠遊戲",
            "當地鼠出現時，打字框會顯示一個英文單字",
            "你需要在地鼠消失前，正確輸入單字並按下ENTER",
            "每關有三個階段，每個階段需要達到一定分數才能過關",
            "總共有六關，祝各位好運~",
            "",
            "按下ENTER返回選單"
        ]

        for i, t in enumerate(texts):
            screen.blit(font.render(t, True, (255, 255, 255)), (150, 150 + i * 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: # 按下ENTER返回選單
                    game_state = "menu"

    # ================= GAME =================
    elif game_state == "game":
        screen.blit(bg_img, (0, 0))
        elapsed = (pygame.time.get_ticks() - stage_start_time) / 1000
        current_time = pygame.time.get_ticks()

        # 地鼠5秒換位置
        if current_time - mole_timer >= MOLE_DURATION:

            new_mole()
        # =====================
        # 時間到
        # =====================
        if elapsed >= 10:#一關時間(s)

            total_time = (pygame.time.get_ticks() - start_time) / 1000

            cpm = typed_chars / max(total_time, 1)
            wpm = (typed_chars / 5) / max(total_time / 60, 1)
            accuracy = (correct_words / max(1, correct_words + wrong_words)) * 100

            # 分數達標
            if score >= TARGET_SCORE:

                clear_sound.play()

                

                
                # 第一、二關過關
                if stage_index < 2:
                    stage_index += 1
                    game_state = "clear"
                    clear_timer = pygame.time.get_ticks()

                # 第三關過關
                else:

                    spawn_particles()
                    game_state = "result"
                    clear_timer = pygame.time.get_ticks()

            # 分數不足
            else:

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
                        correct_words += 1
                        hit_sound.play()

                        typed_chars += len(current_word["word"])
                    else:
                        wrong_words += 1
                        wrong_sound.play()

                    user_text = ""
                    new_mole()

                    

                else:
                    if event.unicode.isalpha():
                        user_text += event.unicode

        draw_holes()
        draw_mole()

        screen.blit(font.render(user_text, True, (255, 255, 255)), (270, 590))

        screen.blit(font.render(f"L{level}-{stages[stage_index]}", True, (255,255,255)), (50, 20))
        screen.blit(font.render(f"Score:{score}", True, (255,255,255)), (50, 60))
        screen.blit(
            font.render(f"Time:{int(30 - elapsed)}", True, (255,255,0)),
            (820, 20)
        )
        
    # ================= GAME OVER =================
    elif game_state == "over":

        screen.fill((0,0,0))

        text = big_font.render(
            "GAME OVER",
            True,
            (255,0,0)
        )

        screen.blit(text,(300,250))

        score_text = font.render(
            f"Score : {score}/{TARGET_SCORE}",
            True,
            (255,255,255)
        )

        screen.blit(score_text,(400,350))

        hint = font.render(
            "Press SPACE to Menu",
            True,
            (255,255,255)
        )

        screen.blit(hint,(350,450))

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:

                    score = 0
                    stage_index = 0
                    user_text = ""

                    stage_start_time = pygame.time.get_ticks()
                    mole_timer = pygame.time.get_ticks()


                    game_state = "menu"


# ================= result =================
    elif game_state == "result":

        screen.fill((0, 0, 0))

        # GAME OVER
        over_text = big_font.render("GAME OVER", True, (255, 80, 80))
        screen.blit(over_text, (350, 80))

        # RESULT
        result_title = big_font.render("RESULT", True, (255, 255, 0))
        screen.blit(result_title, (390, 160))

        # 計算（保險重算一次）
        total_time = max((pygame.time.get_ticks() - start_time) / 1000, 1)

        cpm = typed_chars / total_time
        wpm = (typed_chars / 5) / (total_time / 60)
        accuracy = (correct_words / max(1, correct_words + wrong_words)) * 100

        # 顯示數據
        wpm_text = font.render(f"WPM: {wpm:.1f}", True, (255, 255, 255))
        cpm_text = font.render(f"CPM: {cpm:.1f}", True, (255, 255, 255))
        acc_text = font.render(f"Accuracy: {accuracy:.1f}%", True, (255, 255, 255))
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))

        screen.blit(wpm_text, (400, 280))
        screen.blit(cpm_text, (400, 330))
        screen.blit(acc_text, (400, 380))
        screen.blit(score_text, (400, 430))

        hint = font.render("Press SPACE to return menu", True, (180, 180, 180))
        screen.blit(hint, (330, 520))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_state = "menu"
# ================= FIREWORK =================
    elif game_state == "firework":

        screen.fill((0,0,0))

        update_particles()
        draw_particles()

        title = big_font.render(
            "LEVEL COMPLETE!",
            True,
            (255,255,0)
        )

        screen.blit(title,(220,150))

        if pygame.time.get_ticks() - clear_timer > 3000:

            level += 1

            if level > 6:

                game_state = "menu"

            else:

                stage_index = 0
                score = 0

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

        if flash:
            color = (255, 255, 0)
        else:
            color = (255, 180, 0)

        scale = min(1.8, 0.5 + elapsed_clear / 500)

        clear_font = pygame.font.Font(
            None,
            int(80 * scale)
        )

        text = clear_font.render(
            "LEVEL CLEAR!",
            True,
            color
        )

        text_rect = text.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 - 50)
        )

        screen.blit(text, text_rect)

        sub = font.render(
            "GET READY FOR NEXT LEVEL",
            True,
            (255, 255, 255)
        )

        sub_rect = sub.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 + 60)
        )

        screen.blit(sub, sub_rect)

        if elapsed_clear > 2000:

            score = 0

            stage_name = stages[min(stage_index, len(stages)-1)]
            words = load_words(level, stage_name)

            stage_start_time = pygame.time.get_ticks()

            new_mole()

            game_state = "game"

    pygame.display.flip()

pygame.quit()
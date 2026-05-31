import pygame
from config import WIDTH, HEIGHT
from core.game import Game

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# ===== load assets =====
mole_frames = []
for i in range(8, 0, -1):
    img = pygame.image.load(f"assets/images/mice{i}.png").convert_alpha()
    img = pygame.transform.scale(img, (120, 120))
    mole_frames.append(img)

bg = pygame.image.load("assets/images/black.png").convert()
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

font = pygame.font.Font("assets/fonts/msjh.ttf", 30)
big_font = pygame.font.Font(None, 60)

positions = [
    (150, 180), (350, 180), (550, 180), (750, 180),
    (150, 420), (350, 420), (550, 420), (750, 420),
]

assets = {
    "mole_frames": mole_frames,
    "positions": positions,
    "bg": bg
}

game = Game(assets)

running = True

while running:
    clock.tick(60)

    # ================= UPDATE =================
    if game.state == "game":
        game.update_game()

    # ================= EVENTS =================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game.state == "menu":
            game.handle_menu(event)

        elif game.state == "category":
            game.handle_category(event)

        elif game.state == "game":
            game.handle_game(event)

        elif game.state == "over":
            game.handle_over(event)

    # ================= DRAW =================
    if game.state == "menu":
        game.draw_menu(screen, font, big_font)

    elif game.state == "category":
        game.draw_category(screen, font, big_font)

    elif game.state == "game":
        game.draw_game(screen, font)

    elif game.state == "over":
        game.draw_over(screen, font, big_font)

    pygame.display.flip()

pygame.quit()
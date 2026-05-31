import pygame
import random
from core.words import load_words
from core.mole import Mole
from config import MOLE_DURATION, BLACK, WHITE, GREEN, RED, YELLOW

class Game:
    def __init__(self, assets):
        self.assets = assets

        self.state = "menu"

        self.level = None
        self.category = None

        self.words = []
        self.mole = None

        self.score = 0
        self.lives = 5
        self.user_text = ""

        # buttons
        self.level_buttons = [
            pygame.Rect(120 + (i % 3) * 250, 180 + (i // 3) * 120, 180, 70)
            for i in range(7)
        ]

        self.animal_btn = pygame.Rect(350, 220, 300, 70)
        self.food_btn = pygame.Rect(350, 340, 300, 70)
        self.school_btn = pygame.Rect(350, 460, 300, 70)

    # ================= MENU =================
    def draw_menu(self, screen, font, big_font):
        screen.fill(BLACK)

        screen.blit(big_font.render("SELECT LEVEL", True, WHITE), (280, 70))

        for i, btn in enumerate(self.level_buttons):
            pygame.draw.rect(screen, GREEN, btn)
            screen.blit(font.render(f"LEVEL {i+1}", True, BLACK),
                        (btn.x + 25, btn.y + 20))

    def handle_menu(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, btn in enumerate(self.level_buttons):
                if btn.collidepoint(event.pos):
                    self.level = i + 1
                    self.state = "category"

    # ================= CATEGORY =================
    def draw_category(self, screen, font, big_font):
        screen.fill(BLACK)

        screen.blit(big_font.render(f"LEVEL {self.level}", True, WHITE), (330, 100))

        pygame.draw.rect(screen, GREEN, self.animal_btn)
        pygame.draw.rect(screen, YELLOW, self.food_btn)
        pygame.draw.rect(screen, RED, self.school_btn)

        screen.blit(font.render("ANIMALS", True, BLACK), (410, 240))
        screen.blit(font.render("FOOD", True, BLACK), (450, 360))
        screen.blit(font.render("SCHOOL", True, BLACK), (420, 480))

    def handle_category(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:

            if self.animal_btn.collidepoint(event.pos):
                self.category = "animals"
            elif self.food_btn.collidepoint(event.pos):
                self.category = "food"
            elif self.school_btn.collidepoint(event.pos):
                self.category = "school"

            if self.category:
                self.start_game()

    # ================= GAME =================
    def start_game(self):
        self.words = load_words(self.level, self.category)

        if not self.words:
            self.words = [{"en": "empty", "zh": "空"}]

        self.score = 0
        self.lives = 5
        self.user_text = ""

        self.mole = Mole(
            self.words,
            self.assets["positions"],
            self.assets["mole_frames"]
        )

        self.state = "game"

    def update_game(self):
        self.mole.update()

        if pygame.time.get_ticks() - self.mole.timer > MOLE_DURATION:
            self.lives -= 1
            self.mole.new()

        if self.lives <= 0:
            self.state = "over"

    def draw_game(self, screen, font):
        screen.blit(self.assets["bg"], (0, 0))

        self.mole.draw(screen, font)

        screen.blit(font.render(self.user_text, True, WHITE), (300, 600))
        screen.blit(font.render(f"score: {self.score}", True, WHITE), (50, 50))
        screen.blit(font.render(f"life: {self.lives}", True, RED), (50, 100))

        pygame.draw.rect(screen, WHITE, (250, 580, 500, 60), 2)

    def handle_game(self, event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_BACKSPACE:
                self.user_text = self.user_text[:-1]

            elif event.key == pygame.K_RETURN:
                self.check_answer()

            elif event.key == pygame.K_ESCAPE:
                self.state = "menu"

            else:
                if event.unicode.isalpha():
                    self.user_text += event.unicode

    def check_answer(self):
        if self.user_text.lower() == self.mole.current_word["en"].lower():
            self.score += 1
        else:
            self.lives -= 1

        self.user_text = ""
        self.mole.new()

    # ================= OVER =================
    def draw_over(self, screen, font, big_font):
        screen.fill(BLACK)

        screen.blit(big_font.render("GAME OVER", True, RED), (300, 230))
        screen.blit(font.render(f"score: {self.score}", True, WHITE), (420, 340))
        screen.blit(font.render("SPACE 回主選單", True, WHITE), (360, 450))

    def handle_over(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.state = "menu"
import random
import pygame

class Mole:
    def __init__(self, words, positions, frames):
        self.words = words
        self.positions = positions
        self.frames = frames

        self.current_word = None
        self.current_pos = None
        self.frame_index = 0
        self.timer = pygame.time.get_ticks()

        self.new()

    def new(self):
        self.current_word = random.choice(self.words)
        self.current_pos = random.choice(self.positions)
        self.timer = pygame.time.get_ticks()
        self.frame_index = 0

    def update(self):
        self.frame_index += 0.2
        if self.frame_index >= len(self.frames):
            self.frame_index = len(self.frames) - 1

    def draw(self, screen, font):
        x, y = self.current_pos

        frame = self.frames[int(self.frame_index)]
        screen.blit(frame, (x - 60, y - 30))

        text = font.render(
            f'{self.current_word["en"]} {self.current_word["zh"]}',
            True,
            (255, 255, 255)
        )
        screen.blit(text, (x - 80, y - 130))
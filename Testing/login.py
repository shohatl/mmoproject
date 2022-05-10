import pygame
import time


class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        self.rect = pygame.Rect((x, y), (width, height))
        self.is_pressed = False
        self.text = text

    def check_pressed(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0] == 1:
            self.is_pressed = True

    def reset(self):
        self.is_pressed = False

class TextField:
    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        self.rect = pygame.Rect((x, y), (width, height))
        self.is_pressed = False
        self.text = text
        self.current_text = text
        self.last_deleted = 0

    def check_pressed(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0] == 1:
            self.is_pressed = True
            self.current_text = ""

    def get_input(self):
        for event in pygame.event.get():
            if 'Z' >= event.unicode >= '0' or 'z' >= event.unicode >= 'a' and len(self.current_text) <= 12:
                self.current_text += event.unicode
        keys = pygame.key.get_pressed()
        if keys[pygame.K_BACKSPACE] and keys[pygame.K_LCTRL]:
            self.current_text = ''
        if keys[pygame.K_BACKSPACE] and self.current_text and time.time() - self.last_deleted > 0.2:
            self.last_deleted = time.time()
            self.current_text = self.current_text[:-1]

    def reset(self):
        self.is_pressed = False
        self.current_text = self.text

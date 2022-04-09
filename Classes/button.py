import pygame
from Classes import item


class Button:
    def __init__(self, x, y, button_image):
        self.x = x
        self.y = y
        self.button_image = button_image
        self.pressed = False

    def show_button(self, screen):
        tmp = self.button_image.get_rect()
        tmp.center = self.x, self.y
        screen.blit(self.button_image, tmp)

    def check_press(self):
        rect = self.button_image.get_rect()
        rect.center = self.x, self.y
        if pygame.mouse.get_pressed()[0] == 1 and not self.pressed and rect.collidepoint(pygame.mouse.get_pos()):
            self.pressed = True
            return True
        elif not pygame.mouse.get_pressed()[0]:
            self.pressed = False
        return False

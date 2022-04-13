import pygame


class Button:
    def __init__(self, x, y, button_image):
        self.x = x
        self.y = y
        self.button_image = button_image
        self.pressed = False

    def show_button(self, screen):
        screen.blit(self.button_image, (self.x, self.y))

    def check_press(self):
        rect = self.button_image.get_rect()
        rect.topleft = self.x, self.y
        if pygame.mouse.get_pressed()[0] == 1 and not self.pressed and rect.collidepoint(pygame.mouse.get_pos()):
            self.pressed = True
        if not pygame.mouse.get_pressed()[0]:
            self.pressed = False
        return False

import pygame


class Dropped_item:
    def __init__(self, x, y, lvl, name, time_dropped):
        self.x = x
        self.y = y
        self.lvl = lvl
        self.image = pygame.image.load(f'../Assets/icons/icon-{name}.png')
        self.image = pygame.transform.scale(self.image, (70, 70))
        self.time_dropped = time_dropped

    def show_item_on_surface(self, screen):
        screen.blit(self.image, (self.x - 35, self.y - 35))

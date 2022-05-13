import pygame


class Dropped_item:
    id = 0

    def __init__(self, x, y, lvl, name, time_dropped):
        self.id = Dropped_item.id
        Dropped_item.id += 1
        self.x = x
        self.y = y
        self.lvl = lvl
        self.name = name
        self.image = pygame.image.load(f'../Assets/icons/icon-{name}.png')
        self.image = pygame.transform.scale(self.image, (70, 70))
        self.time_dropped = time_dropped

    def check_pick_up(self, p):
        item_rect = self.image.get_rect()
        item_rect.center = self.x, self.y
        P_rect = pygame.Rect((0, 0), (100, 100))
        P_rect.center = p.x, p.y
        return item_rect.colliderect(P_rect)

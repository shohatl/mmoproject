import random
import time
import pygame

spears = []


class Mob:
    def __init__(self, x, y, lvl):
        self.x = x
        self.y = y
        self.dir_x = 0
        self.dir_y = 0
        self.lvl = lvl
        self.is_alive = True
        self.is_melee = bool(random.randint(0, 1))
        self.HP = 100 * self.lvl
        self.death_time = 0
        self.worth = 300 * self.lvl
        self.last_time_moved = 0
        self.last_attacked = 0
        self.has_target = False
        self.target_x = 0
        self.target_y = 0
        self.home_x = self.x
        self.home_y = self.y
        self.trigger_range = 1200 + 600 * int(self.is_melee)
        self.home_range = 1000 + 1000 * int(self.is_melee)

    def move(self, players):
        if time.time() - self.last_time_moved < 10 ** -3:
            return
        # criteria for movement
        home_rect = pygame.Rect((0, 0), (self.home_range, self.home_range))
        home_rect.center = self.home_x, self.home_y
        mob_rect = pygame.Rect((0, 0), (80, 120))
        mob_rect.center = self.x, self.y
        if mob_rect.colliderect(home_rect):
            trigger_rect = pygame.Rect((0, 0), (self.trigger_range, self.trigger_range))
            trigger_rect.center = mob_rect.center
            for player in players:
                player_rect = pygame.Rect((0, 0), (66, 92))
                player_rect.center = player.x, player.y
                if player_rect.colliderect(trigger_rect):
                    if self.has_target:
                        if (player.x - self.x) ** 2 + (player.y - self.y) ** 2 < (self.target_x - self.x) ** 2 + (self.target_y - self.y) ** 2:
                            self.target_x = player.x
                            self.target_y = player.y
                    else:
                        self.target_x = player.x
                        self.target_y = player.y
                        self.has_target = True
        else:
            self.target_x = self.home_x
            self.target_y = self.home_y
        # Actual procedure of movement
        if bool(random.randint(0, 1)):
            self.x += (self.target_x - self.x) / abs(self.target_x - self.x)
        else:
            self.y += (self.target_y - self.y) / abs(self.target_y - self.y)
        if self.has_target and time.time() - self.last_attacked > 2:
            spears.append(particle(self.x, self.y, self.target_x, self.target_y, "spear"))

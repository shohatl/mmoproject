import time
from item import Item

# GLOBAL VARIABLES
collide_list = [4, 5, 22, 23, 26, 39, 40, 41, 43, 57, 59, 60, 75, 76, 77, 78, 92, 93, 94, 95, 96]


class Player:
    def __init__(self, nickname, ip, key):
        self.x = 1000
        self.y = 1000
        self.dir_x = 0
        self.dir_y = 0
        self.Class = "Mage"
        self.last_time_used_ability = 0
        self.is_ability_active = False
        self.last_time_moved = 0
        self.speed = 8
        self.armour = 0
        self.other_players_list = []
        self.projectiles = []
        self.picked = 0
        self.inventory = [Item("bow", 1), False, False, False, False, False]  # to add items later
        self.gold = 0
        self.health = 100
        self.nickname = nickname
        self.ip = ip
        self.key = key

    def check_collision(self, map):
        return int(map[self.y // 64][self.x // 64]) in collide_list

    def move(self):
        if time.time() - self.last_time_moved > 10 ** -3:
            self.x += self.dir_x
            if self.check_collision():
                self.x -= self.dir_x
            self.y += self.dir_y
            if self.check_collision():
                self.y -= self.dir_y

    def attack(self, mouseX, mouseY):
        self.projectiles.append(particle(self.x, self.y, mouseX, mouseY, self.inventory[self.picked].name))

    def use_ability(self):
        if time.time() - self.last_time_used_ability > self.Class.cooldown:
            self.last_time_used_ability = time.time()
            self.is_ability_active = True

    def ability(self):
        if self.is_ability_active:
            if time.time() - self.last_time_used_ability > 2:
                self.is_ability_active = False
                self.speed = 8
                self.armour = 0
        else:
            if self.Class == "Mage":
                self.health += 10
                self.health -= self.health // 100 * self.health % 100
                self.is_ability_active = False
            elif self.Class == "Scout":
                self.speed = 16
            else:
                self.armour = 0.9

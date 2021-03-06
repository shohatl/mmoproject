import secrets
import time
from Classes import item, particle
import socket

# GLOBAL VARIABLES
collide_list = [4, 5, 22, 23, 26, 39, 40, 41, 43, 57, 59, 60, 75, 76, 77, 78, 92, 93, 94, 95, 96]


class Player:
    def __init__(self, nickname, ip, key, Class):
        self.socket_server = 0
        self.socket_send = ip
        self.socket_location = ip
        self.socket_particles = ip
        self.socket_mobs = ip
        self.socket_chat = ip
        self.x = 100
        self.y = 100
        self.dir_x = 0
        self.dir_y = 0
        self.last_dir = 1
        self.Class = Class
        self.last_time_used_ability = time.time()
        self.is_ability_active = False
        self.last_time_send_connection_alive_packet = time.time()
        self.last_time_moved = 0
        self.last_time_attack = 0
        self.speed = 8
        self.income_dmg_multiplier = 1
        self.other_players_list = []
        self.mobs_on_screen = []
        self.particles_on_screen = []
        self.projectiles = []
        self.has_moved = False
        self.picked = 0
        self.inventory = [item.Item("bow", 1), item.Item('cumball', 90), item.Item('cumball', 69), False, False,
                          item.Item('dagger', 3)]  # to add items later
        self.gold = 0
        self.health = 100
        self.nickname = nickname
        self.key = key
        self.expected_syn = secrets.randbelow(1000)
        if self.expected_syn < 100:
            self.expected_syn += 420

    def check_collision(self, map):
        return int(map[self.y // 64][self.x // 64]) in collide_list

    def move(self):
        self.has_moved = False
        if time.time() - self.last_time_moved > 10 ** -3:
            self.last_time_moved = time.time()
            if self.dir_x:
                self.last_dir = self.dir_x
            self.has_moved = True
            self.x += self.speed * self.dir_x
            # if self.check_collision():
            #     self.x -= self.dir_x
            self.y += self.speed * self.dir_y
            # if self.check_collision():
            #     self.y -= self.dir_y
            return self.dir_x != 0 or self.dir_y != 0
        return False

    def attack(self, mouseX, mouseY):
        if self.inventory[self.picked] and time.time() - self.last_time_attack > self.inventory[self.picked].cool_down:
            self.last_time_attack = time.time()
            self.projectiles.append(particle.Particle(self.x, self.y, mouseX, mouseY, self.inventory[self.picked].speed,
                                                      self.inventory[self.picked].range,
                                                      self.inventory[self.picked].dmg,
                                                      self.inventory[self.picked].name))

    def use_ability(self):
        if time.time() - self.last_time_used_ability > 10:
            self.last_time_used_ability = time.time()
            self.is_ability_active = True

    def get_cd_left(self):
        return time.time() - self.last_time_used_ability

    def ability(self):
        if self.is_ability_active:
            if time.time() - self.last_time_used_ability > 3:
                self.is_ability_active = False
                self.income_dmg_multiplier = 1
                self.last_time_used_ability = time.time()
            if time.time() - self.last_time_used_ability > 2 and self.Class == 'Scout':
                self.is_ability_active = False
                self.speed = 8
                self.last_time_used_ability = time.time()
            if self.Class == "Mage":
                self.health = 100
                self.is_ability_active = False
            elif self.Class == "Scout":
                self.speed = 16
            else:
                self.income_dmg_multiplier = 0
        else:
            self.is_ability_active = False
            self.speed = 8
            self.income_dmg_multiplier = 1

    def use_potion(self):
        if self.gold >= 1000:
            self.health += 10
            self.gold -= 1000
            self.health -= self.health // 100 * self.health % 100
            return True
        return False

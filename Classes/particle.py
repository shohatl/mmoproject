import math
import time


class Particle:
    def __init__(self, x, y, target_x, target_y, speed, range, dmg, hit_box):
        self.x = x
        self.y = y
        self.angle = math.atan2(float(self.y - target_y), float(self.x - target_x))
        self.speed = speed
        self.range = range
        self.dmg = dmg
        self.hit_box = hit_box
        self.hit_box.center = self.x, self.y
        self.last_moved = 0
        self.xVelocity = float(self.speed * math.cos(self.angle))
        self.yVelocity = float(self.speed * math.sin(self.angle))
        self.angle *= 180 / math.pi  # converted to degrees

    def move(self):
        if time.time() - self.last_moved > 10 ** -3:
            self.last_moved = time.time()
            self.x -= self.xVelocity
            self.y -= self.yVelocity
            self.hit_box.center = int(self.x), int(self.y)
            self.range -= self.speed

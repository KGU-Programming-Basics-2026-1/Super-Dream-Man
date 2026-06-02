# projectile.py

class Projectile:
    def __init__(self, x, y, dx, dy):
        self.pos = (x, y)
        self.velocity = (dx, dy)
        self.alive = True

    def update(self, delta_time):
        if not self.alive:
            return
        self.pos = (self.pos[0] + self.velocity[0] * delta_time, self.pos[1] + self.velocity[1] * delta_time)
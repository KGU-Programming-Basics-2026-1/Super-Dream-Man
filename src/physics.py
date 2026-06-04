# physics.py
from settings import *

class Physics:
    def __init__(self, mass, aerodynamic_shape=(1, 1)):
        self.mass = mass
        self.velocity = (0, 0)
        self.acceleration = (0, 0)
        self.on_ground = False
        self.aerodynamic_shape = aerodynamic_shape
    
    def apply_force(self, force):
        ax = force[0] / self.mass
        ay = force[1] / self.mass
        self.acceleration = (self.acceleration[0] + ax, self.acceleration[1] + ay)
    
    def update(self, delta_time) -> tuple:
        ax = self.acceleration[0] + GRAVITY[0]
        ax = ax * (1 - AIR_RESISTANCE * self.aerodynamic_shape[0] * 10)

        ay = self.acceleration[1] + GRAVITY[1]
        ay = ay * (1 - AIR_RESISTANCE * self.aerodynamic_shape[1] * 10)
        
        dax = 1 - AIR_RESISTANCE * self.aerodynamic_shape[0] * 10
        day = 1 - AIR_RESISTANCE * self.aerodynamic_shape[1] * 10
        
        self.acceleration = (dax, day)

        self.velocity = (self.velocity[0] + ax * delta_time, self.velocity[1] + ay * delta_time)

        return self.velocity
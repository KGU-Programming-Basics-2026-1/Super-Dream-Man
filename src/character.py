# character.py

import render
from physics import * 
from settings  import *
from collision import *

class Character(Collision):
    def __init__(self, name
                 , x = 0, y = 0
                 , weapon=None, speed = 5
                 , alive=True
                 , width = 20, height = 40):
        self.super.__init__(x + width / 2, y, width, height)
        self.name = name
        self.pos = (x, y)
        self.alive = alive
        self.speed = speed
        self.on_ground = False
        self.weapon = weapon

        self.physical = False
        self.physical_values = None
        self.layer = Layer.LAYER_CHRACTER
    
    def set_physical(self, mass, aerodynamic_shape=(1, 1)):
        """
        Configure physical properties for the character.

        Parameters:
            mass (float): Positive mass value.
            aerodynamic_shape (tuple): Two-element tuple with values between 0 and 1.
        """
        self.physical = True
        self.physical_values = Physics(mass, aerodynamic_shape)
    
    def move(self, dx, dy, delta_time):
        if self.physical:
            self.physical_values.apply_force((dx * self.speed, dy * self.speed))
        else:
            displacement = (dx * self.speed * delta_time
                            , dy * self.speed * delta_time)
            self.pos = (self.pos[0] + displacement[0]
                        , self.pos[1] + displacement[1])
            super().move(displacement[0], displacement[1])
            

    def jump(self):
        if self.physical:
            self.physical_values.apply_force((UP[0] * self.speed, UP[1] * self.speed))
        else:
            self.pos = (self.pos[0] + UP[0] * self.speed
                            , UP[1] * self.speed)
        self.on_ground = False
    
    def update_physics(self, delta_time):
        if self.physical:
            velocity = self.physical_values.update(delta_time)
            self.pos = (self.pos[0] + velocity[0], self.pos[1] + velocity[1])
    
    def attack(self):
        if self.weapon == None:
            return 0
    
    
    def die(self):
        self.alive = False
    
    def revive(self):
        self.alive = True
    
    def update(self, delta_time):
        self.update_physics(delta_time = delta_time)

    def __str__(self):
        return f'{self.name} at {self.pos}'
    
    def draw(self):
        render.drawer.up()
        render.drawer.goto(self.pos[0], self.pos[1])
        render.drawer.down()
        
        for i in range(4):
            if i % 2 == 0:
                render.drawer.forward(self.width)
            else:
                render.drawer.forward(self.height)
            render.drawer.left()
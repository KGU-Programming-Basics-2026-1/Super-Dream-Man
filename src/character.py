# character.py

from physics import Physics
import settings

class Character:
    def __init__(self, name
                 , x = 0, y = 0
                 , weapon=None, speed = 5
                 , alive=True):
        self.name = name
        self.pos = (x, y)
        self.alive = alive
        self.speed = speed
        self.on_ground = False
        self.weapon = weapon

        self.physical = False
        self.physical_values = None
    
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

    def jump(self):
        if self.physical:
            self.physical_values.apply_force((settings.UP[0] * self.speed, settings.UP[1] * self.speed))
        else:
            self.pos = (self.pos[0] + settings.UP[0] * self.speed
                            , settings.UP[1] * self.speed)
        self.on_ground = False
    
    def update_physics(self, delta_time):
        if self.physical:
            velocity = self.physical_values.update(delta_time)
            self.pos = (self.pos[0] + velocity[0], self.pos[1] + velocity[1])
    
    def attack(self):
        assert(False, "Character.attack() is not implemented yet")
    
    def die(self):
        self.alive = False
    
    def revive(self):
        self.alive = True
    
    def update(self, delta_time):
        self.update_physics(delta_time = delta_time)

    def __str__(self):
        return f'{self.name} at {self.pos}'
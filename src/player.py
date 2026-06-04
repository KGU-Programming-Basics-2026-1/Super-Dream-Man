# player.py
from character import *
from physics import *

class Player(Character):
    def __init__(self, x, y, input_handler):
        super().__init__(name = 'Player', x = x, y = y, alive = True, physical = True)
        self.layer = LAYER_PLAYER

        
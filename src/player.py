# player.py
from character import Character
from physics import Physics

class Player(Character):
    def __init__(self, x, y, input_handler):
        super().__init__(name = 'Player', x = x, y = y, alive = True, physical = True)

        
# tile.py
import render
from settings import *
from collision import Collision


class Tile(Collision):
    def __init__(self, x, y, type):
        super().__init__(x + TILE_SIZE / 2, y, TILE_SIZE, TILE_SIZE)
        self.grid_pos = (x * TILE_SIZE, y * TILE_SIZE)
        self.type = type
        self.layer = Layer.LAYER_GAME_OBJECT

    def get_bounding_box(self):
        x, y = self.grid_pos
        return (x * TILE_SIZE
                , y * TILE_SIZE
                , (x + 1) * TILE_SIZE
                , (y + 1) * TILE_SIZE)
    
    def draw(self):
        render.drawer.up()
        render.drawer.goto(self.grid_pos)
        render.drawer.down()
        render.drawer.color(0x9e080f)
        for i in range(4):
            render.drawer.forward(TILE_SIZE)
            render.drawer.left()
        
        # Draw sprite

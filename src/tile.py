# tile.py
from render import *
from settings import *
from collision import Collision
import turtle

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
    
    def draw(self, drawer : turtle.Turtle):
        drawer.up()
        drawer.right(90)
        drawer.penup()
        drawer.goto(self.grid_pos[0], self.grid_pos[1])
        drawer.pendown()
        drawer.color('red')
        for i in range(4):
            drawer.begin_fill()
            drawer.forward(TILE_SIZE)
            drawer.left(90)
            drawer.end_fill()
            
        
        # Draw sprite

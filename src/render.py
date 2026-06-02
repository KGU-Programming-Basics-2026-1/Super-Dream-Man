# render.py
import turtle
import character

class Renderer:
    def __init__(self, width, height):
        self.screen = turtle.Screen()
        self.screen.setup(width, height)
        self.screen.tracer(0)
    
    def draw_character(self, character):
        turtle.goto(character.pos)
        turtle.circle(20, 'blue' if character.alive else 'red')

    def draw_tile(self, tile):
        turtle.goto(tile.pos)
        turtle.begin_fill()
        turtle.square(40, 'green' if tile.breakable else 'black')
        turtle.end_fill()


    def release(self):
        turtle.bye()
    
    def clear(self):
        turtle.clear()
    
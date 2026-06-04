# render.py
import turtle
from settings import *
from character import *
from queue import PriorityQueue

drawer = turtle.Turtle()


class RenderQueue:
    def __init__(self, width, height):
        drawer.screen = turtle.Screen()
        drawer.screen.setup(width, height)
        drawer.screen.tracer(0)
        self.queue = PriorityQueue()
        self.counter = 0
        drawer.screen.setworldcoordinates(0, 0, width, height)
    
    def enqueue(self, obj):        
        self.queue.put((obj.layer, self.counter, obj))
        self.counter += 1

    def render(self):    
        drawer.screen.clear()
        while not self.queue.empty():
            layer, counter, obj = self.queue.get()
            obj.draw()

    def release(self):
        drawer.bye()
    
    def clear(self):
        drawer.clear()
    

    
# main.py
from asyncio import sleep

from settings import *
from character import *
from render import * 
from tile import *
from map import *

def init():
    global render_queue
    render_queue = RenderQueue(SCREEN_WIDTH, SCREEN_HEIGHT)
    global map
    map = load_map1_1()
    
    
    
    global shouldRun
    shouldRun = True
    
def input():
    assert(False, "input() is not implemented yet")

def update(delta_time):
    assert(False)

def render():
    for row in map:
        for tile in row:
            render_queue.enqueue(tile)
    
    render_queue.render()
    
    

    

def shutdown():
    assert(False, "shutdown() is not implemented yet")

def main():
    init()
    
    while shouldRun:
        #input()
        #update(1)
        render()
    shutdown()

if __name__ == "__main__":
    main()

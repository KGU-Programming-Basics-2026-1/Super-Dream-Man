# main.py
from asyncio import sleep

import settings
from character import Character

def init():
    global shouldRun
    shouldRun = True
    global ball
    ball = Character(name = 'Ball', x = 0, y = 0, weapon=None, speed=40, alive = True)
    ball.set_physical(mass = 0.1, aerodynamic_shape=(0.1, 0.1))
    
    global feather
    feather = Character(name = 'Feather', x = 0, y = 0, weapon=None, speed=0, alive = True)
    feather.set_physical(mass = 0.01, aerodynamic_shape=(0.99, 0.99))

def input():
    assert(False, "input() is not implemented yet")

def update(delta_time):
    ball.jump()
    ball.update(delta_time)
    feather.jump()
    feather.update(delta_time)
    if feather.pos[1] < -10 or ball.pos[1] < -100:
        global shouldRun
        shouldRun = False

def render():
    print(ball)
    print(feather)

def shutdown():
    assert(False, "shutdown() is not implemented yet")

def main():
    init()
    while shouldRun:
        #input()
        update(1)
        render()
    shutdown()

if __name__ == "__main__":
    main()

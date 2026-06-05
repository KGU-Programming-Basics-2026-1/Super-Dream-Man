# settings.py
from enum import *

# Debug settings
DEBUG = True

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# If FPS is 0, the game will run as fast as possible
FPS = 120

# Tile settings
TILE_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH / TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT / TILE_SIZE

class TileTypes(IntEnum):
    TILE_BREAKABLE = 0
    TILE_UNBREAKABLE = 1
    TILE_INTERACTIVE = 2

# Painter's algorithms
class Layer(IntEnum):
    LAYER_BACKGROUND = 0
    LAYER_GAME_OBJECT = 1
    LAYER_CHRACTER = 2
    LAYER_PLAYER = 3
    LAYER_UI = 4

# Physics settings
GRAVITY = (0, -9.81)
UP = (0, 1)
DOWN = (0, -1)
LEFT = (-1, 0)
RIGHT = (1, 0)
AIR_RESISTANCE = 0.1

# Camera settings
CAMERA_SPEED_MAX = 10
CAMERA_SPEED_ACCELERATION = 0.5
CAMERA_SPEED_DECELERATION = 0.7


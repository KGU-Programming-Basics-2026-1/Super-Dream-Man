# settings.py
import enum

# Debug settings
DEBUG = True

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# If FPS is 0, the game will run as fast as possible
FPS = 120

# Tile settings
TILE_SIZE = 40
GRID_WIDTH = SCREEN_WIDTH / TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT / TILE_SIZE
class TileType(enum):
    BREAKABLE = 0
    UNBREAKABLE = 1
    BACKGROUND = 2




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


# render.py
import tkinter as tk
import numpy as np
from enum import *
from settings import *

# RGB color array of 16-bit colors (5-6-5 format)
# Each color is stored as a tuple (R, G, B) with 16-bit depth
rgb_colors = np.array([
    (31, 0, 0),      # Red
    (0, 63, 0),      # Green
    (0, 0, 31),      # Blue
    (31, 63, 0),     # Yellow
    (31, 0, 31),     # Magenta
    (0, 63, 31),     # Cyan
    (31, 63, 31),    # White
    (0, 0, 0),       # Black
], dtype=np.uint16)

class Colors(IntEnum):
    RED = 0
    GREEN = 1
    BLUE = 2
    YELLOW = 3
    MAGENTA = 4
    CYAN = 5
    WHITE = 6
    BLACK = 7

class Renderer:
    def __init__(self, root : tk.Tk):
        self.root = root
        self.root.geometry(f'{SCREEN_WIDTH}x{SCREEN_HEIGHT}')

        self.label = tk.Label(self.root)
        self.label.pack()

        self.frame = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, 3), dtype=np.uint8)

        
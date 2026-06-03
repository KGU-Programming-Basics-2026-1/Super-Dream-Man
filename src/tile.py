# tile.py
import settings

class Tile:
    def __init__(self, x, y, type):
        self.grid_pos = (x * settings.TILE_SIZE, y * settings.TILE_SIZE)
        self.type = type

    def get_bounding_box(self):
        x, y = self.grid_pos
        return (x * settings.TILE_SIZE
                , y * settings.TILE_SIZE
                , (x + 1) * settings.TILE_SIZE
                , (y + 1) * settings.TILE_SIZE)
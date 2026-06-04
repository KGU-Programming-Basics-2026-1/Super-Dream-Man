# collision.py

class Collision:
    def __init__(self, x, y, width, height):
        self.width = width
        self.height = height
        self.left = x - width / 2
        self.top = y + height
        self.right = x + width / 2
        self.bottom = y
        
        self.pos = [x, y]
    
    def move(self, dx, dy):
        self.pos[0] = self.pos[0] + dx
        self.pos[1] = self.pos[1] + dy

        self.left = self.pos[0] - self.width / 2
        self.top = self.pos[1] + self.height
        self.right = self.pos[0] + self.width / 2
        self.bottom = self.pos[1]

    def detect(self, other) -> bool:
        return not (
            self.right < other.left or
            self.left > other.right or
            self.top < other.bottom or
            self.bottom > other.top
        )

    def set_pos(self, x, y):
        self.left = x - self.width / 2
        self.top = y + self.height
        self.right = x + self.width / 2
        self.bottom = y
    
    def get_bounding_box(self) -> tuple:
        return (
            self.left, self.top
            , self.right, self.bottom
        )


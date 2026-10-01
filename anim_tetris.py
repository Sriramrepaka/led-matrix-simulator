import random

# Standard Tetromino definitions: block coordinate offsets relative to center, and RGB colors
TETROMINOES = {
    'I': ([(0, -1), (0, 0), (0, 1), (0, 2)], (0, 255, 255)),   # Cyan
    'J': ([(0, -1), (0, 0), (0, 1), (-1, 1)], (0, 0, 255)),    # Blue
    'L': ([(0, -1), (0, 0), (0, 1), (1, 1)], (255, 165, 0)),   # Orange
    'O': ([(0, 0), (1, 0), (0, 1), (1, 1)], (255, 255, 0)),    # Yellow
    'S': ([(0, 0), (1, 0), (0, 1), (-1, 1)], (0, 255, 0)),     # Green
    'T': ([(0, 0), (-1, 0), (1, 0), (0, 1)], (128, 0, 128)),   # Purple
    'Z': ([(-1, 0), (0, 0), (0, 1), (1, 1)], (255, 0, 0))     # Red
}

def rotate_offsets(offsets, rotation_count):
    """Rotate relative block coordinates 90 degrees clockwise rotation_count times."""
    current = offsets
    for _ in range(rotation_count):
        current = [(-dy, dx) for dx, dy in current]
    return current

class Animation:
    def __init__(self, size):
        self.size = size
        self.fps = 8
        self.board = [[(0, 0, 0) for _ in range(size)] for _ in range(size)]
        self.spawn_piece()

    def spawn_piece(self):
        shape_name = random.choice(list(TETROMINOES.keys()))
        base_offsets, self.color = TETROMINOES[shape_name]
        
        # Select random orientation (0°, 90°, 180°, or 270°)
        rotations = random.randint(0, 3)
        self.piece_offsets = rotate_offsets(base_offsets, rotations)

        # Calculate bounding limits so pieces spawn strictly within horizontal borders
        min_dx = min(dx for dx, dy in self.piece_offsets)
        max_dx = max(dx for dx, dy in self.piece_offsets)
        min_dy = min(dy for dx, dy in self.piece_offsets)

        self.piece_x = random.randint(-min_dx, self.size - 1 - max_dx)
        self.piece_y = -min_dy

    def get_blocks(self, px, py):
        """Return global grid coordinates for all 4 blocks of the current piece."""
        return [(px + dx, py + dy) for dx, dy in self.piece_offsets]

    def check_collision(self, px, py):
        """Return True if any block collides with walls, floor, or fixed grid tiles."""
        for x, y in self.get_blocks(px, py):
            if x < 0 or x >= self.size or y >= self.size:
                return True
            if y >= 0 and self.board[y][x] != (0, 0, 0):
                return True
        return False

    def get_next_frame(self):
        next_y = self.piece_y + 1

        if self.check_collision(self.piece_x, next_y):
            # Lock piece blocks into fixed board state
            for x, y in self.get_blocks(self.piece_x, self.piece_y):
                if 0 <= x < self.size and 0 <= y < self.size:
                    self.board[y][x] = self.color

            # Check and clear completed horizontal lines
            row = self.size - 1
            while row >= 0:
                if all(self.board[row][col] != (0, 0, 0) for col in range(self.size)):
                    del self.board[row]
                    self.board.insert(0, [(0, 0, 0) for _ in range(self.size)])
                else:
                    row -= 1

            # Spawn next piece
            self.spawn_piece()

            # If newly spawned piece collides immediately, clear board (game over reset)
            if self.check_collision(self.piece_x, self.piece_y):
                self.board = [[(0, 0, 0) for _ in range(self.size)] for _ in range(self.size)]
        else:
            self.piece_y = next_y

        # Render combined frame (board + falling piece)
        frame = [row[:] for row in self.board]
        for x, y in self.get_blocks(self.piece_x, self.piece_y):
            if 0 <= x < self.size and 0 <= y < self.size:
                frame[y][x] = self.color

        return frame
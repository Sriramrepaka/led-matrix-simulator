import random

TETROMINOES = {
    'I': ([(0, -1), (0, 0), (0, 1), (0, 2)], (0, 240, 240)),   # Cyan
    'J': ([(0, -1), (0, 0), (0, 1), (-1, 1)], (0, 32, 240)),   # Blue
    'L': ([(0, -1), (0, 0), (0, 1), (1, 1)], (240, 160, 0)),   # Orange
    'O': ([(0, 0), (1, 0), (0, 1), (1, 1)], (240, 240, 0)),    # Yellow
    'S': ([(0, 0), (1, 0), (0, 1), (-1, 1)], (0, 240, 32)),    # Green
    'T': ([(0, 0), (-1, 0), (1, 0), (0, 1)], (160, 0, 240)),   # Purple
    'Z': ([(-1, 0), (0, 0), (0, 1), (1, 1)], (240, 0, 0))     # Red
}

def rotate_offsets(offsets, rotation_count):
    current = offsets
    for _ in range(rotation_count % 4):
        current = [(-dy, dx) for dx, dy in current]
    return current

class Animation:
    def __init__(self, size):
        self.size = size
        self.fps = 8
        # Start with a completely blank LED matrix
        self.board = [[(0, 0, 0) for _ in range(size)] for _ in range(size)]
        self.spawn_piece()

    def spawn_piece(self):
        shape_name = random.choice(list(TETROMINOES.keys()))
        self.base_offsets, self.color = TETROMINOES[shape_name]
        
        self.current_rot = 0
        self.piece_offsets = list(self.base_offsets)

        min_dy = min(dy for dx, dy in self.piece_offsets)
        self.piece_x = self.size // 2
        self.piece_y = -min_dy

        # Calculate optimal placement target for intelligent gameplay simulation
        self.target_x, self.target_rot = self.find_best_move()

    def check_collision_custom(self, px, py, offsets):
        for dx, dy in offsets:
            x, y = px + dx, py + dy
            if x < 0 or x >= self.size or y >= self.size:
                return True
            if y >= 0 and self.board[y][x] != (0, 0, 0):
                return True
        return False

    def evaluate_placement(self, px, py, offsets):
        temp_board = [row[:] for row in self.board]
        for dx, dy in offsets:
            x, y = px + dx, py + dy
            if 0 <= x < self.size and 0 <= y < self.size:
                temp_board[y][x] = self.color

        lines_cleared = sum(1 for r in range(self.size) if all(temp_board[r][c] != (0, 0, 0) for c in range(self.size)))

        col_heights = [0] * self.size
        holes = 0
        for c in range(self.size):
            found_block = False
            for r in range(self.size):
                if temp_board[r][c] != (0, 0, 0):
                    if not found_block:
                        col_heights[c] = self.size - r
                        found_block = True
                elif found_block:
                    holes += 1

        agg_height = sum(col_heights)
        max_height = max(col_heights)
        bumpiness = sum(abs(col_heights[i] - col_heights[i+1]) for i in range(self.size - 1))

        # Score formula favoring completed lines and minimizing holes/height
        return (lines_cleared ** 2) * 1000 - holes * 150 - agg_height * 5 - bumpiness * 10 - max_height * 20 + py * 2

    def find_best_move(self):
        best_score = -float('inf')
        best_x = self.piece_x
        best_rot = 0

        for rot in range(4):
            offsets = rotate_offsets(self.base_offsets, rot)
            min_dx = min(dx for dx, dy in offsets)
            max_dx = max(dx for dx, dy in offsets)

            for target_x in range(-min_dx, self.size - max_dx):
                drop_y = self.piece_y
                while not self.check_collision_custom(target_x, drop_y + 1, offsets):
                    drop_y += 1

                if self.check_collision_custom(target_x, drop_y, offsets):
                    continue

                score = self.evaluate_placement(target_x, drop_y, offsets)
                if score > best_score:
                    best_score = score
                    best_x = target_x
                    best_rot = rot

        return best_x, best_rot

    def get_blocks(self, px, py):
        return [(px + dx, py + dy) for dx, dy in self.piece_offsets]

    def get_next_frame(self):
        # 1. Rotate piece towards target orientation frame-by-frame
        if self.current_rot != self.target_rot:
            next_rot = (self.current_rot + 1) % 4
            test_offsets = rotate_offsets(self.base_offsets, next_rot)
            if not self.check_collision_custom(self.piece_x, self.piece_y, test_offsets):
                self.current_rot = next_rot
                self.piece_offsets = test_offsets

        # 2. Shift piece sideways towards target column frame-by-frame
        if self.piece_x < self.target_x:
            if not self.check_collision_custom(self.piece_x + 1, self.piece_y, self.piece_offsets):
                self.piece_x += 1
        elif self.piece_x > self.target_x:
            if not self.check_collision_custom(self.piece_x - 1, self.piece_y, self.piece_offsets):
                self.piece_x -= 1

        # 3. Advance piece down
        next_y = self.piece_y + 1
        if self.check_collision_custom(self.piece_x, next_y, self.piece_offsets):
            # Lock piece
            for x, y in self.get_blocks(self.piece_x, self.piece_y):
                if 0 <= x < self.size and 0 <= y < self.size:
                    self.board[y][x] = self.color

            # Clear lines
            row = self.size - 1
            while row >= 0:
                if all(self.board[row][col] != (0, 0, 0) for col in range(self.size)):
                    del self.board[row]
                    self.board.insert(0, [(0, 0, 0) for _ in range(self.size)])
                else:
                    row -= 1

            self.spawn_piece()

            # Reset to clean empty matrix on game over
            if self.check_collision_custom(self.piece_x, self.piece_y, self.piece_offsets):
                self.board = [[(0, 0, 0) for _ in range(self.size)] for _ in range(self.size)]
                self.spawn_piece()
        else:
            self.piece_y = next_y

        # Render frame
        frame = [row[:] for row in self.board]
        for x, y in self.get_blocks(self.piece_x, self.piece_y):
            if 0 <= x < self.size and 0 <= y < self.size:
                frame[y][x] = self.color

        return frame
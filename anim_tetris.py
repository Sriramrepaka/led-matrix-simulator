import random

class Animation:
    def __init__(self, size):
        self.size = size
        self.fps = 8
        self.board = [[(0, 0, 0) for _ in range(size)] for _ in range(size)]
        self.spawn_piece()

    def spawn_piece(self):
        self.piece_x = random.randint(1, self.size - 2)
        self.piece_y = 0
        self.color = random.choice([
            (255, 0, 0), (0, 255, 255), (255, 165, 0), 
            (255, 255, 0), (0, 255, 0), (128, 0, 128)
        ])

    def get_next_frame(self):
        # Clear piece from previous step
        next_y = self.piece_y + 1
        
        # Check collision with bottom or fixed blocks
        if next_y >= self.size or self.board[next_y][self.piece_x] != (0, 0, 0):
            # Lock current piece
            self.board[self.piece_y][self.piece_x] = self.color
            
            # Check line clears
            for row in range(self.size - 1, -1, -1):
                if all(self.board[row][col] != (0, 0, 0) for col in range(self.size)):
                    del self.board[row]
                    self.board.insert(0, [(0, 0, 0) for _ in range(self.size)])
            
            self.spawn_piece()
        else:
            self.piece_y = next_y

        # Build composite frame
        frame = [row[:] for row in self.board]
        frame[self.piece_y][self.piece_x] = self.color
        return frame
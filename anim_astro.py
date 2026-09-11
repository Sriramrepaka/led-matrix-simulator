import random

class Animation:
    def __init__(self, size):
        self.size = size
        self.fps = 12
        self.player_x = size // 2
        self.bullets = []
        self.enemies = []
        self.tick_count = 0

    def get_next_frame(self):
        self.tick_count += 1
        buffer = [[(0, 0, 0) for _ in range(self.size)] for _ in range(self.size)]

        # Move player side-to-side
        if self.tick_count % 3 == 0:
            self.player_x += random.choice([-1, 0, 1])
            self.player_x = max(1, min(self.size - 2, self.player_x))

        # Auto-shoot
        if self.tick_count % 2 == 0:
            self.bullets.append([self.player_x, self.size - 2])

        # Spawn enemies
        if random.random() < 0.3:
            self.enemies.append([random.randint(0, self.size - 1), 0])

        # Move bullets & enemies
        self.bullets = [[bx, by - 1] for bx, by in self.bullets if by > 0]
        self.enemies = [[ex, ey + 1] for ex, ey in self.enemies if ey < self.size]

        # Check hits
        for b in self.bullets[:]:
            for e in self.enemies[:]:
                if b[0] == e[0] and b[1] == e[1]:
                    self.bullets.remove(b)
                    self.enemies.remove(e)
                    break

        # Render elements
        for ex, ey in self.enemies:
            buffer[ey][ex] = (255, 40, 40)
        for bx, by in self.bullets:
            buffer[by][bx] = (255, 255, 0)
            
        # Draw player ship (triangle)
        px, py = self.player_x, self.size - 1
        buffer[py][px] = (0, 150, 255)
        buffer[py][px - 1] = (0, 80, 200)
        buffer[py][px + 1] = (0, 80, 200)

        return buffer
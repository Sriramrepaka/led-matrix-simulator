import math

class Animation:
    def __init__(self, size):
        self.size = size
        self.fps = 10
        self.radius = 0
        self.growing = True

    def get_next_frame(self):
        buffer = [[(10, 25, 10) for _ in range(self.size)] for _ in range(self.size)]
        cx, cy = self.size // 2, self.size // 2
        
        # Stem
        for y in range(cy, self.size):
            buffer[y][cx] = (30, 180, 30)

        # Pulse radius
        if self.growing:
            self.radius += 0.25
            if self.radius >= 4.5:
                self.growing = False
        else:
            self.radius -= 0.25
            if self.radius <= 0.5:
                self.growing = True

        # Render Petals
        for y in range(self.size):
            for x in range(self.size):
                dx = x - cx
                dy = y - cy
                dist = math.sqrt(dx*dx + dy*dy)
                
                if 0 < dist <= self.radius:
                    angle = math.atan2(dy, dx)
                    petal_factor = math.sin(angle * 5)  # 5-petal pattern
                    if dist <= (self.radius * (0.6 + 0.4 * petal_factor)):
                        buffer[y][x] = (255, 50, 150)
                        
        # Yellow Center
        buffer[cy][cx] = (255, 220, 0)

        return buffer
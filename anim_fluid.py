import math
import colorsys

class Animation:
    def __init__(self, size):
        self.size = size
        self.fps = 30
        self.t = 0

    def get_next_frame(self):
        buffer = [[(0, 0, 0) for _ in range(self.size)] for _ in range(self.size)]
        self.t += 0.05
        
        for y in range(self.size):
            for x in range(self.size):
                # Calculate wave disturbance
                v1 = math.sin(x * 0.5 + self.t)
                v2 = math.sin(y * 0.5 + self.t)
                v3 = math.sin((x + y) * 0.3 + self.t)
                val = (v1 + v2 + v3 + 3) / 6.0  # Normalize to 0..1
                
                # Convert hue to RGB
                r, g, b = colorsys.hsv_to_rgb((val + self.t * 0.1) % 1.0, 0.9, val)
                buffer[y][x] = (int(r * 255), int(g * 255), int(b * 255))
                
        return buffer
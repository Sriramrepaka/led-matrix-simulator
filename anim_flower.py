import math

class Animation:
    def __init__(self, size):
        self.size = size
        self.fps = 12
        self.frame_count = 0
        
        # Stem Toggle (Set to True if you want a green stem at the bottom)
        self.show_stem = False

    def get_next_frame(self):
        # Dark panel background
        buffer = [[(5, 5, 12) for _ in range(self.size)] for _ in range(self.size)]
        
        # Matrix center at (5, 5)
        cx, cy = self.size // 2, self.size // 2
        
        self.frame_count += 1
        t = self.frame_count * 0.1

        # Blooming expansion cycle (grows outward, breathes, then contracts)
        bloom = (math.sin(t * 0.6) + 1.0) / 2.0  # Range 0.0 to 1.0
        max_r = 1.2 + bloom * 3.4                # Maximum reach across the 11x11 grid

        petal_count = 4
        rotation_angle = t * 0.08  # Gentle organic rotation

        # 1. Render 4-Petal Flower Body
        for y in range(self.size):
            for x in range(self.size):
                dx = x - cx
                dy = y - cy
                dist = math.sqrt(dx * dx + dy * dy)

                if 0.5 < dist <= max_r + 0.5:
                    angle = math.atan2(dy, dx) + rotation_angle
                    
                    # 4-petal mathematical wave function (peaks at 4 primary axes)
                    petal_factor = 0.5 + 0.5 * math.cos(petal_count * angle)
                    allowed_r = max_r * (0.30 + 0.70 * petal_factor)

                    if dist <= allowed_r:
                        # Color gradient: vibrant ruby red at core to bright orchid pink at tips
                        norm_dist = dist / max_r
                        r_col = min(255, int(220 + norm_dist * 35))
                        g_col = min(255, int(25 + norm_dist * 80))
                        b_col = min(255, int(110 + norm_dist * 100))

                        buffer[y][x] = (r_col, g_col, b_col)

        # 2. Central Pistil (Gold Center)
        buffer[cy][cx] = (255, 215, 0)

        # Pulsing center glow
        halo_pulse = (math.sin(t * 1.5) + 1.0) / 2.0
        glow_intensity = int(130 + 80 * halo_pulse)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                if buffer[ny][nx] == (5, 5, 12):  # Fill surrounding background
                    buffer[ny][nx] = (glow_intensity, int(glow_intensity * 0.6), 0)

        # 3. Optional Stem
        if self.show_stem:
            for y in range(cy + 2, self.size):
                buffer[y][cx] = (20, 160, 30)

        return buffer
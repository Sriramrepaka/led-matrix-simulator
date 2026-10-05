import math

class Animation:
    def __init__(self, size):
        self.size = size
        self.fps = 12
        self.frame_count = 0

    def get_next_frame(self):
        # Dark ambient panel background
        buffer = [[(5, 10, 8) for _ in range(self.size)] for _ in range(self.size)]
        
        # Position flower center near top-middle (column 5, row 4)
        cx, cy = self.size // 2, 4
        
        # 120 frames per lifecycle (~10 seconds at 12 FPS)
        cycle_length = 120
        progress = (self.frame_count % cycle_length) / cycle_length
        self.frame_count += 1

        # Phase timeline parameters
        stem_start_y = self.size - 1
        stem_target_y = cy + 1

        if progress < 0.25:
            # Phase 1: Stem grows upward
            stem_growth = progress / 0.25
            current_stem_top = int(stem_start_y - stem_growth * (stem_start_y - stem_target_y))
            bloom_ratio = 0.0
        elif progress < 0.40:
            # Phase 2: Flower bud forms & begins opening
            current_stem_top = stem_target_y
            bloom_ratio = (progress - 0.25) / 0.15
        elif progress < 0.80:
            # Phase 3: Full bloom & breathing pulse
            current_stem_top = stem_target_y
            bloom_ratio = 1.0
        else:
            # Phase 4: Soft fade-out reset
            current_stem_top = stem_target_y
            bloom_ratio = max(0.0, 1.0 - (progress - 0.80) / 0.20)

        # Smooth overall fade factor near cycle reset
        fade_factor = 1.0
        if progress > 0.85:
            fade_factor = max(0.0, (1.0 - progress) / 0.15)

        # 1. Render Stem
        for y in range(stem_start_y, current_stem_top - 1, -1):
            if 0 <= y < self.size:
                green_val = int(180 * fade_factor)
                buffer[y][cx] = (20, green_val, 30)

        # 2. Render Side Leaves
        if current_stem_top <= 7 and fade_factor > 0:
            leaf_fade = min(1.0, fade_factor)
            leaf_color = (15, int(150 * leaf_fade), 25)
            # Left & right leaves branching outward
            if 0 <= cx - 2 < self.size:
                buffer[7][cx - 1] = leaf_color
                buffer[6][cx - 2] = leaf_color
            if 0 <= cx + 2 < self.size:
                buffer[7][cx + 1] = leaf_color
                buffer[6][cx + 2] = leaf_color

        # 3. Render Flower Petals & Center Pistil
        if bloom_ratio > 0.0 and fade_factor > 0:
            # Gentle radial pulse and dynamic rotation
            pulse = math.sin(self.frame_count * 0.15) * 0.18 if bloom_ratio == 1.0 else 0.0
            radius = (1.2 + 2.2 * bloom_ratio + pulse) * fade_factor

            # Soft color oscillation (magenta to warm rose)
            color_shift = (math.sin(self.frame_count * 0.1) + 1.0) / 2.0
            r_petal = int((240 + 15 * color_shift) * fade_factor)
            g_petal = int((30 + 40 * color_shift) * fade_factor)
            b_petal = int((140 - 50 * color_shift) * fade_factor)

            petal_count = 6
            angle_offset = self.frame_count * 0.03  # Subtle rotation

            for y in range(self.size):
                for x in range(self.size):
                    dx = x - cx
                    dy = y - cy
                    dist = math.sqrt(dx * dx + dy * dy)

                    if 0.5 < dist <= radius + 0.5:
                        angle = math.atan2(dy, dx) + angle_offset
                        petal_shape = 0.5 + 0.5 * math.cos(angle * petal_count)
                        max_allowed_dist = radius * (0.55 + 0.45 * petal_shape)

                        if dist <= max_allowed_dist:
                            intensity = max(0.4, 1.0 - (dist / (radius + 0.5)) * 0.5)
                            buffer[y][x] = (
                                int(r_petal * intensity),
                                int(g_petal * intensity),
                                int(b_petal * intensity)
                            )

            # Center Pistil (Bright Golden Yellow)
            center_r = int(255 * fade_factor)
            center_g = int(210 * fade_factor)
            buffer[cy][cx] = (center_r, center_g, 0)

            # Soft glow surrounding pistil
            if bloom_ratio > 0.5:
                glow_color = (int(160 * fade_factor), int(120 * fade_factor), 0)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size and buffer[ny][nx] == (5, 10, 8):
                        buffer[ny][nx] = glow_color

        return buffer
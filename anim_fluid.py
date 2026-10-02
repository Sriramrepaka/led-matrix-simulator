import math
import random

class Animation:
    def __init__(self, size):
        self.size = size
        self.fps = 30
        
        # Tilt control parameters (-1.0 to +1.0)
        self.tilt_x = 0.0
        self.tilt_y = 1.0  # Default downward gravity
        
        # Fill exactly 50% of the matrix (60 LEDs for an 11x11 grid)
        self.num_particles = (size * size) // 2
        self.particles = []
        
        # Initialize bottom half of the matrix grid
        count = 0
        for y in range(size - 1, -1, -1):
            for x in range(size):
                if count < self.num_particles:
                    # [x_pos, y_pos, x_vel, y_vel]
                    self.particles.append([float(x), float(y), 0.0, 0.0])
                    count += 1

    def update_tilt(self, tilt_x, tilt_y):
        """Receives tilt control values from simulator sliders."""
        self.tilt_x = tilt_x
        self.tilt_y = tilt_y

    def get_next_frame(self):
        # 1. Physics force step based on X/Y matrix tilt angles
        gx = self.tilt_x * 0.45
        gy = self.tilt_y * 0.45

        for p in self.particles:
            p[2] += gx
            p[3] += gy
            
            # Fluid viscosity damping
            p[2] *= 0.85
            p[3] *= 0.85
            
            p[0] += p[2]
            p[1] += p[3]

        # 2. Iterative collision & boundary handling
        for _ in range(4):
            for i in range(self.num_particles):
                p1 = self.particles[i]
                
                # Matrix wall boundary constraints
                if p1[0] < 0:
                    p1[0] = 0; p1[2] = -p1[2] * 0.2
                elif p1[0] > self.size - 1:
                    p1[0] = self.size - 1; p1[2] = -p1[2] * 0.2
                
                if p1[1] < 0:
                    p1[1] = 0; p1[3] = -p1[3] * 0.2
                elif p1[1] > self.size - 1:
                    p1[1] = self.size - 1; p1[3] = -p1[3] * 0.2

                # Inter-particle repulsion forces
                for j in range(i + 1, self.num_particles):
                    p2 = self.particles[j]
                    dx = p2[0] - p1[0]
                    dy = p2[1] - p1[1]
                    dist_sq = dx * dx + dy * dy
                    min_dist = 0.92
                    
                    if dist_sq < min_dist * min_dist:
                        dist = math.sqrt(dist_sq)
                        if dist < 0.0001:
                            dx, dy, dist = 0.1, 0.1, 0.14
                        overlap = (min_dist - dist) / dist * 0.4
                        p1[0] -= dx * overlap
                        p1[1] -= dy * overlap
                        p2[0] += dx * overlap
                        p2[1] += dy * overlap

        # 3. Grid Slot Assignment (Guarantees exactly 60 distinct LEDs light up)
        occupied_cells = set()
        grid = [[(10, 10, 20) for _ in range(self.size)] for _ in range(self.size)]

        for p in self.particles:
            gx_idx = max(0, min(self.size - 1, int(round(p[0]))))
            gy_idx = max(0, min(self.size - 1, int(round(p[1]))))
            
            # If slot is already taken, spiral outward to find the nearest open slot
            if (gx_idx, gy_idx) in occupied_cells:
                found_slot = False
                for radius in range(1, self.size):
                    for dx in range(-radius, radius + 1):
                        for dy in range(-radius, radius + 1):
                            nx, ny = gx_idx + dx, gy_idx + dy
                            if 0 <= nx < self.size and 0 <= ny < self.size:
                                if (nx, ny) not in occupied_cells:
                                    gx_idx, gy_idx = nx, ny
                                    found_slot = True
                                    break
                        if found_slot: break
                    if found_slot: break

            occupied_cells.add((gx_idx, gy_idx))

        # 4. Render liquid gradient onto grid
        for (x, y) in occupied_cells:
            # Liquid cyan-to-deep blue depth color gradient
            blue = min(255, 150 + y * 9)
            green = min(220, 60 + (10 - y) * 12)
            grid[y][x] = (0, green, blue)

        return grid
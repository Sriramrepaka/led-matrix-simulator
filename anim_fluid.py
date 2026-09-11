import math
import random

class Animation:
    def __init__(self, size):
        self.size = size
        self.fps = 30
        
        # IMU Angles (Degrees)
        self.pitch = 0.0  # X-axis tilt (-45 to 45)
        self.roll = 0.0   # Y-axis tilt (-45 to 45)
        
        # Initialize grid with half volume filled (bottom half filled by default)
        self.particles = []
        total_pixels = size * size
        target_particles = total_pixels // 2  # 50% full matrix
        
        # Fill from bottom up
        count = 0
        for y in range(size - 1, -1, -1):
            for x in range(size):
                if count < target_particles:
                    self.particles.append([float(x), float(y), 0.0, 0.0]) # x, y, vx, vy
                    count += 1

    def update_imu(self, pitch, roll):
        self.pitch = pitch
        self.roll = roll

    def get_next_frame(self):
        buffer = [[(10, 10, 20) for _ in range(self.size)] for _ in range(self.size)]
        
        # Calculate gravity vector from IMU pitch/roll
        rad_pitch = math.radians(self.pitch)
        rad_roll = math.radians(self.roll)
        
        gx = math.sin(rad_roll) * 0.4
        gy = math.cos(rad_pitch) * math.cos(rad_roll) * 0.4 + math.sin(rad_pitch) * 0.4

        # Grid occupancy map for simple collisions
        occupied = set()

        # Update particle physics
        for p in self.particles:
            # Apply gravity
            p[2] += gx  # Velocity X
            p[3] += gy  # Velocity Y

            # Apply slight damping (viscosity)
            p[2] *= 0.85
            p[3] *= 0.85

            # Proposed new position
            nx = p[0] + p[2]
            ny = p[1] + p[3]

            # Boundary constraints (Keep inside 11x11 matrix)
            if nx < 0:
                nx, p[2] = 0, -p[2] * 0.3
            elif nx >= self.size - 0.5:
                nx, p[2] = self.size - 1, -p[2] * 0.3

            if ny < 0:
                ny, p[3] = 0, -p[3] * 0.3
            elif ny >= self.size - 0.5:
                ny, p[3] = self.size - 1, -p[3] * 0.3

            p[0], p[1] = nx, ny

            # Map to grid integers
            gx_idx = int(round(p[0]))
            gy_idx = int(round(p[1]))
            
            # Constrain array indexing limits
            gx_idx = max(0, min(self.size - 1, gx_idx))
            gy_idx = max(0, min(self.size - 1, gy_idx))

            occupied.add((gx_idx, gy_idx))

        # Render fluid onto grid
        for (x, y) in occupied:
            # Liquid gradient color based on depth
            blue_intensity = min(255, 120 + y * 12)
            buffer[y][x] = (0, 180, blue_intensity)

        return buffer
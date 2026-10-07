import random
import math

class Animation:
    def __init__(self, size):
        self.size = size
        self.fps = 12
        self.player_x = float(size // 2)
        self.tilt_x = 0.0
        self.bullets = []
        self.enemies = []
        self.explosions = []
        self.stars = []
        self.tick_count = 0
        
        # Initialize background starfield
        for _ in range(8):
            self.stars.append([
                random.randint(0, size - 1),
                random.uniform(0, size - 1),
                random.uniform(0.3, 0.9)
            ])

    def update_tilt(self, tilt_x, tilt_y):
        """Receives interactive X-tilt slider updates from simulator_3.py"""
        self.tilt_x = tilt_x

    def get_next_frame(self):
        self.tick_count += 1
        # Deep space dark background
        buffer = [[(5, 5, 15) for _ in range(self.size)] for _ in range(self.size)]

        # 1. Update & Render Scrolling Starfield
        for star in self.stars:
            star[1] += star[2] * 0.35  # Scroll speed proportional to depth
            if star[1] >= self.size:
                star[1] = 0
                star[0] = random.randint(0, self.size - 1)
            
            sx, sy = int(star[0]), int(star[1])
            brightness = int(110 * star[2])
            buffer[sy][sx] = (brightness, brightness, brightness + 45)

        # 2. Player Controls (Interactive Tilt + Autonomous AI Fallback)
        if abs(self.tilt_x) > 0.05:
            # Move ship based on slider input
            self.player_x += self.tilt_x * 0.75
        else:
            # Autonomous AI auto-dodge & target tracking when slider is centered
            nearest_enemy_x = None
            lowest_y = -1
            for e in self.enemies:
                if e['y'] > lowest_y:
                    lowest_y = e['y']
                    nearest_enemy_x = e['x']
            
            if nearest_enemy_x is not None:
                if nearest_enemy_x > self.player_x:
                    self.player_x += 0.3
                elif nearest_enemy_x < self.player_x:
                    self.player_x -= 0.3
            else:
                # Gentle breathing float
                self.player_x += math.sin(self.tick_count * 0.2) * 0.2

        # Keep player ship within matrix boundaries
        self.player_x = max(1.0, min(float(self.size - 2), self.player_x))
        px = int(round(self.player_x))

        # 3. Auto-Fire Lasers
        if self.tick_count % 3 == 0:
            self.bullets.append([px, self.size - 3])

        # 4. Enemy Spawning (Standard Invaders & Armored Bosses)
        if random.random() < 0.28 and len(self.enemies) < 4:
            is_boss = random.random() < 0.2
            self.enemies.append({
                'x': float(random.randint(0, self.size - 1)),
                'y': 0.0,
                'hp': 2 if is_boss else 1,
                'is_boss': is_boss,
                'speed': random.uniform(0.18, 0.32)
            })

        # 5. Move Bullets & Enemies
        self.bullets = [[bx, by - 1] for bx, by in self.bullets if by > 0]
        for e in self.enemies:
            e['y'] += e['speed']

        # 6. Safe Bullet-Enemy Collision Detection
        hit_bullet_indices = set()
        hit_enemy_indices = set()

        for b_idx, (bx, by) in enumerate(self.bullets):
            for e_idx, e in enumerate(self.enemies):
                ex, ey = int(round(e['x'])), int(round(e['y']))
                # Check direct overlap or fast-movement passing
                if abs(bx - ex) == 0 and (by == ey or by == ey - 1):
                    hit_bullet_indices.add(b_idx)
                    e['hp'] -= 1
                    if e['hp'] <= 0:
                        hit_enemy_indices.add(e_idx)
                        # Spawn particle explosion burst
                        for _ in range(6):
                            self.explosions.append({
                                'x': float(ex), 'y': float(ey),
                                'vx': random.uniform(-0.5, 0.5),
                                'vy': random.uniform(-0.5, 0.5),
                                'life': 1.0,
                                'color': (255, 210, 30) if e['is_boss'] else (255, 60, 20)
                            })
                    break

        # Remove destroyed elements
        self.bullets = [b for idx, b in enumerate(self.bullets) if idx not in hit_bullet_indices]
        self.enemies = [e for idx, e in enumerate(self.enemies) if idx not in hit_enemy_indices and e['y'] < self.size]

        # 7. Render Particle Explosions
        active_explosions = []
        for p in self.explosions:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 0.25
            if p['life'] > 0:
                ex, ey = int(round(p['x'])), int(round(p['y']))
                if 0 <= ex < self.size and 0 <= ey < self.size:
                    r = int(p['color'][0] * p['life'])
                    g = int(p['color'][1] * p['life'])
                    b = int(p['color'][2] * p['life'])
                    buffer[ey][ex] = (r, g, b)
                active_explosions.append(p)
        self.explosions = active_explosions

        # 8. Render Enemies
        for e in self.enemies:
            ex, ey = int(round(e['x'])), int(round(e['y']))
            if 0 <= ex < self.size and 0 <= ey < self.size:
                if e['is_boss']:
                    buffer[ey][ex] = (255, 200, 0)
                    if ey > 0:
                        buffer[ey - 1][ex] = (220, 100, 0)
                else:
                    pulse = int(200 + 55 * math.sin(self.tick_count * 0.6))
                    buffer[ey][ex] = (pulse, 30, 70)

        # 9. Render Glowing Cyan Laser Bolts
        for bx, by in self.bullets:
            if 0 <= bx < self.size and 0 <= by < self.size:
                buffer[by][bx] = (0, 255, 240)

        # 10. Render Solid Navy Blue Astro Vehicle
        py = self.size - 2
        navy_blue = (0, 35, 140)
        
        # Nose cone, center chassis, and side wings all use uniform Navy Blue
        buffer[py - 1][px] = navy_blue
        buffer[py][px] = navy_blue
        buffer[py][px - 1] = navy_blue
        buffer[py][px + 1] = navy_blue

        # Flickering Thruster Fire
        if py + 1 < self.size:
            flame_g = random.randint(100, 180)
            buffer[py + 1][px] = (255, flame_g, 0)

        return buffer
import random
import math

class Animation:
    def __init__(self, size):
        self.size = size
        self.fps = 12
        self.player_x = float(size // 2)
        self.tilt_x = 0.0
        self.bullets = []
        self.asteroids = []
        self.explosions = []
        self.stars = []
        self.tick_count = 0
        
        # AI decision state ("hit" vs "dodge")
        self.ai_mode = "hit"
        self.ai_timer = 0
        
        # Scrolling starfield background
        for _ in range(8):
            self.stars.append([
                random.randint(0, size - 1),
                random.uniform(0, size - 1),
                random.uniform(0.3, 0.8)
            ])

    def update_tilt(self, tilt_x, tilt_y):
        """Receives interactive X-tilt slider updates from simulator_3.py"""
        self.tilt_x = tilt_x

    def get_next_frame(self):
        self.tick_count += 1
        # Deep space dark background
        buffer = [[(5, 5, 15) for _ in range(self.size)] for _ in range(self.size)]

        # 1. Update Starfield
        for star in self.stars:
            star[1] += star[2] * 0.3
            if star[1] >= self.size:
                star[1] = 0
                star[0] = random.randint(0, self.size - 1)
            
            sx, sy = int(star[0]), int(star[1])
            brightness = int(100 * star[2])
            buffer[sy][sx] = (brightness, brightness, brightness + 40)

        # 2. Spawn White & Orange Asteroids
        if random.random() < 0.32 and len(self.asteroids) < 4:
            is_orange = random.random() < 0.5
            self.asteroids.append({
                'x': float(random.randint(0, self.size - 1)),
                'y': 0.0,
                'is_orange': is_orange,
                'speed': random.uniform(0.2, 0.35)
            })

        # 3. AI Movement Logic (Dodging a few & hitting a few)
        if abs(self.tilt_x) > 0.05:
            # Interactive manual slider override
            self.player_x += self.tilt_x * 0.75
        else:
            # Autonomous AI routine
            self.ai_timer += 1
            if self.ai_timer > 14:
                # Cycle state between destroying asteroids and dodging them
                self.ai_mode = "dodge" if self.ai_mode == "hit" else "hit"
                self.ai_timer = 0

            # Identify closest incoming threat
            threat = None
            closest_y = -1
            for ast in self.asteroids:
                if ast['y'] > closest_y:
                    closest_y = ast['y']
                    threat = ast

            if threat is not None:
                tx = threat['x']
                if self.ai_mode == "hit":
                    # Align with target to blast it
                    if tx > self.player_x:
                        self.player_x += 0.35
                    elif tx < self.player_x:
                        self.player_x -= 0.35
                else:
                    # Sidestep to dodge incoming path
                    if abs(tx - self.player_x) < 1.6:
                        dodge_dir = 1.0 if self.player_x < (self.size / 2) else -1.0
                        self.player_x += dodge_dir * 0.4
            else:
                # Gentle breathing float when space is clear
                self.player_x += math.sin(self.tick_count * 0.2) * 0.15

        # Keep ship inside grid bounds
        self.player_x = max(1.0, min(float(self.size - 2), self.player_x))
        px = int(round(self.player_x))

        # 4. Auto-Fire Defense Lasers
        if self.ai_mode == "hit" and self.tick_count % 3 == 0:
            self.bullets.append([px, self.size - 3])
        elif abs(self.tilt_x) > 0.05 and self.tick_count % 4 == 0:
            self.bullets.append([px, self.size - 3])

        # 5. Move Bullets & Asteroids
        self.bullets = [[bx, by - 1] for bx, by in self.bullets if by > 0]
        for ast in self.asteroids:
            ast['y'] += ast['speed']

        # 6. Bullet-Asteroid Collision Detection
        hit_bullets = set()
        hit_asteroids = set()

        for b_idx, (bx, by) in enumerate(self.bullets):
            for a_idx, ast in enumerate(self.asteroids):
                ax, ay = int(round(ast['x'])), int(round(ast['y']))
                if abs(bx - ax) == 0 and (by == ay or by == ay - 1):
                    hit_bullets.add(b_idx)
                    hit_asteroids.add(a_idx)
                    
                    # Particle explosion burst
                    p_color = (255, 130, 20) if ast['is_orange'] else (240, 240, 255)
                    for _ in range(5):
                        self.explosions.append({
                            'x': float(ax), 'y': float(ay),
                            'vx': random.uniform(-0.4, 0.4),
                            'vy': random.uniform(-0.4, 0.4),
                            'life': 1.0,
                            'color': p_color
                        })
                    break

        self.bullets = [b for i, b in enumerate(self.bullets) if i not in hit_bullets]
        self.asteroids = [a for i, a in enumerate(self.asteroids) if i not in hit_asteroids and a['y'] < self.size]

        # 7. Render Particle Explosions
        active_exp = []
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
                active_exp.append(p)
        self.explosions = active_exp

        # 8. Render White and Orange Asteroids
        for ast in self.asteroids:
            ax, ay = int(round(ast['x'])), int(round(ast['y']))
            if 0 <= ax < self.size and 0 <= ay < self.size:
                if ast['is_orange']:
                    buffer[ay][ax] = (255, 120, 20)  # Burning Orange Asteroid
                else:
                    buffer[ay][ax] = (235, 235, 245)  # Crisp White Asteroid

        # 9. Render Cyan Defense Lasers
        for bx, by in self.bullets:
            if 0 <= bx < self.size and 0 <= by < self.size:
                buffer[by][bx] = (0, 240, 255)

        # 10. Render AstroBot Shape ".:." (Navy Blue Triangle)
        py = self.size - 1  # Base row
        navy_dark = (0, 35, 140)
        navy_core = (0, 110, 240)

        # Top Tip '.'
        buffer[py - 1][px] = navy_dark

        # Base Row '.:.'
        buffer[py][px - 1] = navy_dark  # Left wing '.'
        buffer[py][px]     = navy_core  # Center core ':'
        buffer[py][px + 1] = navy_dark  # Right wing '.'

        return buffer
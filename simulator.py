import pygame
import sys
import importlib

# Configuration
GRID_SIZE = 11
LED_SIZE = 40
GAP = 10
MARGIN = 20

# Window dimensions with extra space at the bottom for UI sliders
MATRIX_WIDTH = GRID_SIZE * (LED_SIZE + GAP) - GAP + (MARGIN * 2)
PANEL_HEIGHT = 140
WIDTH = MATRIX_WIDTH
HEIGHT = MATRIX_WIDTH + PANEL_HEIGHT

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.dragging = False
        self.handle_radius = 10

    def draw(self, screen, font):
        # Draw label and value
        txt = font.render(f"{self.label}: {self.val:+.2f}", True, (200, 200, 200))
        screen.blit(txt, (self.rect.x, self.rect.y - 22))
        
        # Track line
        pygame.draw.rect(screen, (50, 50, 50), self.rect, border_radius=4)
        
        # Center tick mark (0.0 position)
        center_x = self.rect.x + self.rect.width // 2
        pygame.draw.line(screen, (100, 100, 100), (center_x, self.rect.y - 3), (center_x, self.rect.bottom + 3), 2)

        # Active fill track
        handle_x = self.val_to_x()
        fill_left = min(center_x, handle_x)
        fill_width = abs(handle_x - center_x)
        if fill_width > 0:
            pygame.draw.rect(screen, (0, 160, 230), (fill_left, self.rect.y, fill_width, self.rect.height))

        # Knob handle
        pygame.draw.circle(screen, (240, 240, 240), (handle_x, self.rect.centery), self.handle_radius)

    def val_to_x(self):
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        return int(self.rect.x + ratio * self.rect.width)

    def x_to_val(self, x):
        ratio = max(0.0, min(1.0, (x - self.rect.x) / self.rect.width))
        return self.min_val + ratio * (self.max_val - self.min_val)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.inflate(20, 20).collidepoint(event.pos):
                self.dragging = True
                self.val = self.x_to_val(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.val = self.x_to_val(event.pos[0])

class LEDMatrixSimulator:
    def __init__(self, mode="fluid"):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(f"11x11 LED Matrix Simulator - [{mode.upper()}]")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 14)
        self.mode = mode
        
        # Load animation module
        try:
            self.anim_module = importlib.import_module(f"anim_{mode}")
            self.anim = self.anim_module.Animation(GRID_SIZE)
        except ModuleNotFoundError:
            print(f"Error: anim_{mode}.py not found.")
            sys.exit(1)

        # Initialize interactive X and Y tilt sliders
        slider_w = WIDTH - 100
        self.slider_x = Slider(50, MATRIX_WIDTH + 35, slider_w, 12, -1.0, 1.0, 0.0, "X-Tilt (Left / Right)")
        self.slider_y = Slider(50, MATRIX_WIDTH + 85, slider_w, 12, -1.0, 1.0, 1.0, "Y-Tilt (Up / Down)")

    def draw_matrix(self, frame_buffer):
        self.screen.fill((15, 15, 15))  # Dark panel background
        
        # Render LED Matrix
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                color = frame_buffer[y][x]
                cx = MARGIN + x * (LED_SIZE + GAP) + LED_SIZE // 2
                cy = MARGIN + y * (LED_SIZE + GAP) + LED_SIZE // 2
                
                if max(color) > 50:
                    glow_color = (color[0]//3, color[1]//3, color[2]//3)
                    pygame.draw.circle(self.screen, glow_color, (cx, cy), (LED_SIZE // 2) + 4)
                
                pygame.draw.circle(self.screen, color, (cx, cy), LED_SIZE // 2)
                pygame.draw.circle(self.screen, (255, 255, 255, 30), (cx - 3, cy - 3), LED_SIZE // 6)

        # Render UI Control Panel divider & sliders
        pygame.draw.line(self.screen, (35, 35, 35), (0, MATRIX_WIDTH), (WIDTH, MATRIX_WIDTH), 2)
        self.slider_x.draw(self.screen, self.font)
        self.slider_y.draw(self.screen, self.font)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Pass input events to UI sliders
                self.slider_x.handle_event(event)
                self.slider_y.handle_event(event)

            # Pass slider tilt parameters to animation class
            if hasattr(self.anim, 'update_tilt'):
                self.anim.update_tilt(self.slider_x.val, self.slider_y.val)

            # Get next frame and draw
            frame_buffer = self.anim.get_next_frame()
            self.draw_matrix(frame_buffer)
            self.clock.tick(self.anim.fps)

        pygame.quit()

if __name__ == "__main__":
    mode_to_run = "fluid"
    if len(sys.argv) > 1:
        mode_to_run = sys.argv[1]
        
    sim = LEDMatrixSimulator(mode=mode_to_run)
    sim.run()
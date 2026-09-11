import pygame
import sys
import importlib

# Configuration
GRID_SIZE = 11
LED_SIZE = 40
GAP = 10
MARGIN = 20

WIDTH = GRID_SIZE * (LED_SIZE + GAP) - GAP + (MARGIN * 2)
HEIGHT = WIDTH

class LEDMatrixSimulator:
    def __init__(self, mode="fluid"):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(f"11x11 LED Matrix Simulator - [{mode.upper()}]")
        self.clock = pygame.time.Clock()
        self.mode = mode
        
        # Load the module dynamically based on mode
        try:
            self.anim_module = importlib.import_module(f"anim_{mode}")
            self.anim = self.anim_module.Animation(GRID_SIZE)
        except ModuleNotFoundError:
            print(f"Error: anim_{mode}.py not found.")
            sys.exit(1)

    def draw_matrix(self, frame_buffer):
        self.screen.fill((15, 15, 15))  # Dark panel background
        
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                color = frame_buffer[y][x]
                cx = MARGIN + x * (LED_SIZE + GAP) + LED_SIZE // 2
                cy = MARGIN + y * (LED_SIZE + GAP) + LED_SIZE // 2
                
                # Glow effect for bright pixels
                if max(color) > 50:
                    glow_color = (color[0]//3, color[1]//3, color[2]//3)
                    pygame.draw.circle(self.screen, glow_color, (cx, cy), (LED_SIZE // 2) + 4)
                
                # LED Diode
                pygame.draw.circle(self.screen, color, (cx, cy), LED_SIZE // 2)
                
                # Inner highlight/bevel
                pygame.draw.circle(self.screen, (255, 255, 255, 30), (cx - 3, cy - 3), LED_SIZE // 6)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Get next frame from subfile
            frame_buffer = self.anim.get_next_frame()
            self.draw_matrix(frame_buffer)
            self.clock.tick(self.anim.fps)

        pygame.quit()

if __name__ == "__main__":
    # Modes available: "fluid", "tetris", "astro", "flower"
    mode_to_run = "tetris"
    if len(sys.argv) > 1:
        mode_to_run = sys.argv[1]
        
    sim = LEDMatrixSimulator(mode=mode_to_run)
    sim.run()
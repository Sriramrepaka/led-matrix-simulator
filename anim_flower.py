import math

# 11x11 Pixel Art Frames: Rose/Tulip on a Stem with Leaves
# ' ' = Dark background
# 'G' = Stem / Leaf Green
# 'd' = Dark Leaf Shadow
# 'R' = Ruby Red Petal Base
# 'P' = Vibrant Rose/Pink Petal
# 'Y' = Petal Highlight

FRAME_CENTER = [
    "           ",
    "   P P P   ",
    "  RPPYPPR  ",
    "  RPPPPRR  ",
    "   RPPRR   ",
    "     G     ",
    "     Gg    ",
    "  GGGGGGG  ",
    "   dGGGd   ",
    "     G     ",
    "     G     "
]

FRAME_SWAY_RIGHT = [
    "           ",
    "    P P P  ",
    "   RPPYPPR ",
    "   RPPPPRR ",
    "    RPPRR  ",
    "     GG    ",
    "     Gg    ",
    "  GGGGGGG  ",
    "   dGGGd   ",
    "     G     ",
    "     G     "
]

FRAME_SWAY_LEFT = [
    "           ",
    "  P P P    ",
    " RPPYPPR   ",
    " RPPPPRR   ",
    "  RPPRR    ",
    "    GG     ",
    "     Gg    ",
    "  GGGGGGG  ",
    "   dGGGd   ",
    "     G     ",
    "     G     "
]

FRAMES = [FRAME_CENTER, FRAME_SWAY_RIGHT, FRAME_CENTER, FRAME_SWAY_LEFT]

class Animation:
    def __init__(self, size):
        self.size = size
        self.fps = 8
        self.tick_count = 0

    def get_next_frame(self):
        # Advance sway animation frame every 5 clock cycles
        self.tick_count += 1
        frame_idx = (self.tick_count // 5) % len(FRAMES)
        art = FRAMES[frame_idx]

        # Subtle dynamic shimmer for petal highlights
        shimmer = (math.sin(self.tick_count * 0.2) + 1.0) / 2.0

        # Color palette definition
        bg_color = (8, 12, 22)
        green_stem = (35, 185, 60)
        green_dark = (18, 110, 35)
        petal_ruby = (200, 20, 65)
        petal_pink = (255, 60 + int(30 * shimmer), 135)
        petal_high = (255, 180 + int(40 * shimmer), 195)

        color_map = {
            ' ': bg_color,
            'G': green_stem,
            'g': green_stem,
            'd': green_dark,
            'R': petal_ruby,
            'P': petal_pink,
            'Y': petal_high
        }

        # Build matrix buffer
        buffer = [[bg_color for _ in range(self.size)] for _ in range(self.size)]

        for y in range(self.size):
            for x in range(self.size):
                char = art[y][x]
                buffer[y][x] = color_map.get(char, bg_color)

        return buffer
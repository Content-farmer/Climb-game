# settings.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES_DIR = os.path.join(BASE_DIR, "Sprites")
MUSIC_DIR = os.path.join(BASE_DIR, "Music")
HIGHSCORES_PATH = os.path.join(BASE_DIR, "highscores.txt")
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE      = (255, 255, 255)
GRAY       = (100, 100, 100)
DARK_GRAY  = (50, 50, 50)
YELLOW     = (200, 200, 50)
BLACK      = (0, 0, 0)
LIGHT_GREY = (130, 130, 130) 

# Conversion: pixels per meter (for score)
PIXELS_PER_METER = 40  # 40 pixels = 1 meter

# Collectible definitions (for random collectibles)
collectible_defs = [
    ("Red", (255, 0, 0, 200)),
    ("Green", (0, 255, 0, 200)),
    ("Blue", (0, 0, 255, 200)),
    ("Yellow", (255, 255, 0, 200)),
    ("Cyan", (0, 255, 255, 200)),
    ("Magenta", (255, 0, 255, 200)),
    ("Orange", (255, 165, 0, 200)),
    ("Purple", (128, 0, 128, 200)),
    ("Pink", (255, 192, 203, 200)),
    ("Brown", (165, 42, 42, 200)),
    ("Teal", (0, 128, 128, 200)),
    ("Gold", (255, 215, 0, 200)),
    ("Silver", (192, 192, 192, 200)),
    ("Maroon", (128, 0, 0, 200)),
    ("Olive", (128, 128, 0, 200)),
    ("Turquoise", (64, 224, 208, 200))
]

# Achievement definitions for the Achievements page (16 items)
achievement_defs = [
    ("violet",          (148, 0, 211, 200)),
    ("chartreuse",      (127, 255, 0, 200)),
    ("vermillion",      (227, 66, 52, 200)),
    ("teal",            (0, 128, 128, 200)),
    ("navy",            (0, 0, 128, 200)),
    ("onix",            (40, 40, 40, 200)),
    ("midnight blue",   (25, 25, 112, 200)),
    ("pink",            (255, 105, 180, 200)),
    ("salmon",          (250, 128, 114, 200)),
    ("bronze",          (205, 127, 50, 200)),
    ("seafoam green",   (159, 226, 191, 200)),
    ("grey",            (50, 50, 50)),
    ("white",           (255, 255, 255, 200)),
    ("black",           (0, 0, 0, 200)),
    ("peuter",          (210, 180, 140, 200)),
    ("flesh",           (255, 204, 153, 200))
]

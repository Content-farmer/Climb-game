

# settings.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES_DIR = os.path.join(BASE_DIR, "Sprites")
MUSIC_DIR = os.path.join(BASE_DIR, "Music")
HIGHSCORES_PATH = os.path.join(BASE_DIR, "highscores.txt")
 SCREEN_WIDTH = 800
 SCREEN_HEIGHT = 600

+FPS = 60
 
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
 

)


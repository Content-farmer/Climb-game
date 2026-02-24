import pygame, sys, random, os, textwrap

# ---------------- Constants ----------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE     = (255, 255, 255)
GRAY      = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
YELLOW    = (200, 200, 50)
BLACK     = (0, 0, 0)
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

# Achievement definitions for the Achievements page (4x4 grid)
achievement_defs = [
    ("500m Normal", (255, 200, 200, 200)),
    ("1000m Normal", (255, 180, 180, 200)),
    ("1500m Normal", (255, 160, 160, 200)),
    ("2000m Normal", (255, 140, 140, 200)),
    ("2500m Normal", (255, 120, 120, 200)),
    ("3000m Normal", (255, 100, 100, 200)),
    ("3500m Normal", (255, 80, 80, 200)),
    ("4000m Normal", (255, 60, 60, 200)),
    ("500m Hard", (200, 200, 255, 200)),
    ("1000m Hard", (180, 180, 255, 200)),
    ("1500m Hard", (160, 160, 255, 200)),
    ("2000m Hard", (140, 140, 255, 200)),
    ("2500m Hard", (120, 120, 255, 200)),
    ("3000m Hard", (100, 100, 255, 200)),
    ("3500m Hard", (80, 80, 255, 200)),
    ("4000m Hard", (60, 60, 255, 200))
]

# ---------------- Helper Function for Word Wrapping ----------------
def wrap_text(text, font, max_width):
    # Use textwrap to break paragraphs into lines; adjust width as needed.
    lines = []
    for paragraph in text.splitlines():
        lines.extend(textwrap.wrap(paragraph, width=40))
    return lines

# ---------------- Collectible Class ----------------
class Collectible:
    def __init__(self, x, y, size, name, color):
        self.rect = pygame.Rect(x, y, size, size)
        self.name = name
        self.color = color
    def draw(self, surface, camera_offset_y):
        adj_rect = pygame.Rect(self.rect.x, self.rect.y - camera_offset_y, self.rect.width, self.rect.height)
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        s.fill(self.color)
        surface.blit(s, (adj_rect.x, adj_rect.y))

# ---------------- Platform Class ----------------
class Platform:
    def __init__(self, x, y, width, height, ptype="regular", symbol="",
                 is_moving=False, moving_speed=0,
                 is_conveyor=False, conveyor_speed=0,
                 is_icy=False, is_crumble=False, crumble_duration=None,
                 image=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.ptype = ptype
        self.symbol = symbol
        self.is_moving = is_moving
        self.moving_speed = moving_speed
        self.is_conveyor = is_conveyor
        self.conveyor_speed = conveyor_speed
        self.is_icy = is_icy
        self.is_crumble = is_crumble
        self.crumble_duration = crumble_duration
        self.crumble_start_time = None
        self.expired = False
        self.image = None  # Removed PNG code; always use symbol

    def update(self):
        if self.is_moving:
            self.rect.x += self.moving_speed
            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                self.moving_speed = -self.moving_speed
        if self.is_crumble:
            current_time = pygame.time.get_ticks()
            if self.crumble_start_time is not None:
                if not self.expired and (current_time - self.crumble_start_time >= self.crumble_duration):
                    self.expired = True
                elif self.expired and (current_time - self.crumble_start_time >= self.crumble_duration + 5000):
                    self.expired = False
                    self.crumble_start_time = None

    def draw(self, surface, font, camera_offset_y):
        if self.is_crumble and self.expired:
            return
        if self.ptype == "regular":
            color = GRAY
        elif self.ptype == "moving":
            color = (150, 150, 250)
        elif self.ptype == "conveyor":
            color = YELLOW
        elif self.ptype == "icy":
            color = (180, 255, 255)
        elif self.ptype.startswith("crumble"):
            color = (255, 100, 100)
        else:
            color = GRAY
        adj_rect = pygame.Rect(self.rect.x, self.rect.y - camera_offset_y, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, color, adj_rect)
        if self.symbol:
            text = font.render(self.symbol, True, BLACK)
            text_rect = text.get_rect(center=adj_rect.center)
            surface.blit(text, text_rect)

# ---------------- Tower (World) Class ----------------
class Tower:
    def __init__(self, start_y, special_mode=False):
        self.platforms = []
        self.start_y = start_y
        self.highest_platform_y = start_y
        self.special_mode = special_mode
        self.generate_initial_platforms()

    def generate_initial_platforms(self):
        ground = Platform(0, self.start_y, SCREEN_WIDTH, 40, ptype="regular")
        self.platforms.append(ground)
        self.highest_platform_y = self.start_y
        last_center_x = SCREEN_WIDTH // 2
        last_y = self.start_y
        while last_y > self.start_y - SCREEN_HEIGHT * 2:
            new_plat = self.generate_next_platform(last_center_x, last_y)
            self.platforms.append(new_plat)
            last_center_x = new_plat.rect.x + new_plat.rect.width // 2
            last_y = new_plat.rect.y
            self.highest_platform_y = new_plat.rect.y

    def generate_next_platform(self, prev_center_x, prev_y):
        gap = random.randint(60, 110)
        new_y = prev_y - gap
        diff = self.start_y - new_y
        diff_meters = diff / PIXELS_PER_METER
        base_width = 250
        min_width = 30
        # Slow platform shrinking: divisor increased to 80 for a longer shrink duration.
        if diff < 100 * PIXELS_PER_METER:
            width = base_width
        else:
            width = max(min_width, base_width - ((diff - (100 * PIXELS_PER_METER)) // 80))
        offset = random.randint(-150, 150)
        center_x = prev_center_x + offset
        center_x = max(width // 2, min(SCREEN_WIDTH - width // 2, center_x))
        new_x = center_x - width // 2
        height = 20
        if self.special_mode:
            width = min_width
            if random.random() < 0.9:
                ptype = "crumble_1"
            else:
                r = random.random()
                if r < 0.1:
                    ptype = "moving"
                elif r < 0.2:
                    ptype = "conveyor"
                else:
                    ptype = "regular"
        else:
            if diff_meters < 500:
                ptype = "regular"
            elif diff_meters < 1000:
                ptype = "moving" if random.random() < 0.1 else "regular"
            elif diff_meters < 1500:
                r = random.random()
                if r < 0.1:
                    ptype = "moving"
                elif r < 0.2:
                    ptype = "conveyor"
                else:
                    ptype = "regular"
            elif diff_meters < 2000:
                r = random.random()
                if r < 0.15:
                    ptype = "moving"
                elif r < 0.30:
                    ptype = "conveyor"
                elif r < 0.45:
                    ptype = "icy"
                else:
                    ptype = "regular"
            elif diff_meters < 2500:
                r = random.random()
                if r < 0.15:
                    ptype = "moving"
                elif r < 0.30:
                    ptype = "conveyor"
                elif r < 0.45:
                    ptype = "icy"
                elif r < 0.60:
                    ptype = "crumble_3"
                else:
                    ptype = "regular"
            else:
                if random.random() < 0.2:
                    ptype = "regular"
                else:
                    ptype = random.choice(["moving", "conveyor", "icy", "crumble_3", "crumble_1"])
        symbol = ""
        is_moving = False
        moving_speed = 0
        is_conveyor = False
        conveyor_speed = 0
        is_icy = False
        is_crumble = False
        crumble_duration = None
        if ptype == "moving":
            symbol = "~"
            is_moving = True
            moving_speed = random.choice([1, -1])
        elif ptype == "conveyor":
            is_conveyor = True
            conveyor_speed = random.choice([1, -1, 2, -2])
            symbol = "<-" if conveyor_speed < 0 else "->"
        elif ptype == "icy":
            is_icy = True
            symbol = "*"  # Using "*" as placeholder for ice
        elif ptype == "crumble_3":
            is_crumble = True
            crumble_duration = 2000
            symbol = "!"
        elif ptype == "crumble_1":
            is_crumble = True
            crumble_duration = 500
            symbol = "!!"
        return Platform(new_x, new_y, width, height, ptype=ptype, symbol=symbol,
                        is_moving=is_moving, moving_speed=moving_speed,
                        is_conveyor=is_conveyor, conveyor_speed=conveyor_speed,
                        is_icy=is_icy, is_crumble=is_crumble, crumble_duration=crumble_duration)

    def update(self, camera_offset_y):
        for plat in self.platforms:
            plat.update()
        buffer = SCREEN_HEIGHT
        self.platforms = [p for p in self.platforms if (p.rect.y - camera_offset_y < SCREEN_HEIGHT + buffer or p.rect.y == self.start_y)]
        while self.highest_platform_y > camera_offset_y - 100:
            highest = min(self.platforms, key=lambda p: p.rect.y)
            new_plat = self.generate_next_platform(highest.rect.x + highest.rect.width // 2, highest.rect.y)
            self.platforms.append(new_plat)
            self.highest_platform_y = new_plat.rect.y

# ---------------- Player (and Demo Bot) Class ----------------
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color=WHITE, is_bot=False):
        super().__init__()
        self.width = 37
        self.height = 40
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_y = 0
        self.vel_x = 0
        self.speed = 5
        self.jump_strength = -15   # Jump strength set back to -15
        self.on_ground = False
        self.on_icy = False
        self.fall_start_y = None
        self.coyote_time = 150
        self.last_on_ground_time = 0
        self.jump_buffer_time = None
        self.jump_buffer_duration = 150
        self.is_bot = is_bot
        self.bot_timer = 0

    def handle_input(self):
        if self.is_bot:
            now = pygame.time.get_ticks()
            if now - self.bot_timer > random.randint(1000, 3000):
                self.vel_x = random.choice([-self.speed, self.speed])
                self.bot_timer = now
            if self.rect.right > SCREEN_WIDTH - 10:
                self.vel_x = -self.speed
            elif self.rect.left < 10:
                self.vel_x = self.speed
            if self.on_ground and random.random() < 0.03:
                self.jump()
            return
        keys = pygame.key.get_pressed()
        effective_speed = self.speed
        if not self.on_ground and self.fall_start_y is not None and (self.rect.y - self.fall_start_y > 500):
            effective_speed = self.speed * 0.5
        if not self.on_icy:
            if keys[pygame.K_LEFT]:
                self.vel_x = -effective_speed
            elif keys[pygame.K_RIGHT]:
                self.vel_x = effective_speed
            else:
                self.vel_x = 0
        else:
            if keys[pygame.K_LEFT]:
                self.vel_x -= 1.0
            elif keys[pygame.K_RIGHT]:
                self.vel_x += 1.0
            else:
                self.vel_x *= 0.999
            max_ice_speed = self.speed * 3
            if self.vel_x > max_ice_speed:
                self.vel_x = max_ice_speed
            if self.vel_x < -max_ice_speed:
                self.vel_x = -max_ice_speed

    def jump(self):
        self.vel_y = self.jump_strength
        self.on_ground = False
        self.last_on_ground_time = 0
        self.vel_x = 0
        self.on_icy = False
        self.fall_start_y = None

    def update(self, platforms):
        current_time = pygame.time.get_ticks()
        self.handle_input()
        self.rect.x += int(self.vel_x)
        self.vel_y += 0.8
        if self.vel_y > 10:
            self.vel_y = 10
        self.rect.y += int(self.vel_y)
        if self.on_ground:
            self.fall_start_y = self.rect.y
        else:
            if self.fall_start_y is None:
                self.fall_start_y = self.rect.y
        collided_platform = None
        for plat in platforms:
            if plat.is_crumble and plat.expired:
                continue
            if self.rect.colliderect(plat.rect):
                if self.vel_y > 0 and (self.rect.bottom - plat.rect.top) < 20:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    collided_platform = plat
                    self.last_on_ground_time = current_time
                    if plat.is_icy:
                        self.on_icy = True
                    else:
                        self.on_icy = False
                    if plat.is_crumble and plat.crumble_start_time is None:
                        plat.crumble_start_time = current_time
                elif self.vel_y < 0 and (plat.rect.bottom - self.rect.top) < 20:
                    self.rect.top = plat.rect.bottom
                    self.vel_y = 0
        if not collided_platform:
            self.on_icy = False
        if collided_platform and collided_platform.is_conveyor:
            self.rect.x += collided_platform.conveyor_speed
        if self.jump_buffer_time is not None:
            if current_time - self.jump_buffer_time <= self.jump_buffer_duration:
                if self.on_ground or (current_time - self.last_on_ground_time <= self.coyote_time):
                    self.jump()
                    self.jump_buffer_time = None
            else:
                self.jump_buffer_time = None

# ---------------- Game Class ----------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("A Needed Climb")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.state = "MENU"
        self.menu_options = ["A Normal Climb", "A Harder Climb", "High Scores", "Music", "Credits", "Collectibles"]
        self.menu_index = 0
        self.all_music = ["Music 1", "Music 2", "Music 3", "Music 4", "Music 5",
                          "Music 6", "Music 7", "Music 8", "Music 9", "Music 10", "Off"]
        self.current_music = None
        self.high_scores = self.load_high_scores()
        self.collected_collectibles = set()   # random collectibles (indices 0-15)
        self.unlocked_achievements = set()      # achievements (indices 0-15)
        self.player_color = WHITE
        self.special_mode = False  # False = Normal; True = Harder
        self.checkpoints = []      # list of checkpoint scores (in m)
        self.current_checkpoint = 0  # highest checkpoint reached (in m)
        self.collectibles_page = "Random"  # "Random" or "Achievements"
        # Demo bot for menu background
        self.demo_tower = Tower(SCREEN_HEIGHT - 50, special_mode=False)
        self.demo_bot = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100, color=self.player_color, is_bot=True)

    @property
    def all_music(self):
        return self._all_music
    @all_music.setter
    def all_music(self, value):
        self._all_music = value

    def load_high_scores(self):
        if os.path.exists("highscores.txt"):
            with open("highscores.txt", "r") as f:
                scores = [float(line.strip()) for line in f.readlines()]
            scores.sort(reverse=True)
            return scores[:5]
        else:
            return []

    def save_high_scores(self):
        with open("highscores.txt", "w") as f:
            for score in self.high_scores:
                f.write(f"{score}\n")

    def run(self):
        while True:
            if self.state == "MENU":
                self.menu_loop()
            elif self.state == "CHECKPOINT":
                self.checkpoint_menu_loop()
            elif self.state == "HIGH_SCORES":
                self.high_scores_loop()
            elif self.state == "MUSIC":
                self.music_menu_loop()
            elif self.state == "CREDITS":
                self.credits_loop()
            elif self.state == "COLLECTIBLES":
                self.collectibles_loop()
            elif self.state == "NARRATIVE":
                self.narrative_loop()
            elif self.state == "GAMEPLAY":
                self.gameplay_loop()
            elif self.state == "GAME_OVER":
                self.game_over_loop()
            else:
                break

    # ----- Menu Loop with Background Bot -----
    def menu_loop(self):
        running = True
        while running and self.state == "MENU":
            # Update demo bot and its tower
            self.demo_bot.update(self.demo_tower.platforms)
            camera_offset = self.demo_bot.rect.y - SCREEN_HEIGHT//2
            self.screen.fill(DARK_GRAY)
            for plat in self.demo_tower.platforms:
                plat.draw(self.screen, self.font, camera_offset)
            pygame.draw.rect(self.screen, self.player_color, self.demo_bot.rect.move(0, -camera_offset))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.menu_index = (self.menu_index - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.menu_index = (self.menu_index + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN:
                        sel = self.menu_options[self.menu_index]
                        if sel == "A Normal Climb":
                            self.special_mode = False
                            if self.checkpoints:
                                # Go to checkpoint selection menu
                                self.state = "CHECKPOINT"
                            else:
                                self.state = "NARRATIVE"
                            running = False
                        elif sel == "A Harder Climb":
                            self.special_mode = True
                            self.state = "NARRATIVE"
                            running = False
                        elif sel == "High Scores":
                            self.state = "HIGH_SCORES"
                            running = False
                        elif sel == "Music":
                            self.state = "MUSIC"
                            running = False
                        elif sel == "Credits":
                            self.state = "CREDITS"
                            running = False
                        elif sel == "Collectibles":
                            self.collectibles_page = "Random"
                            self.state = "COLLECTIBLES"
                            running = False
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            for i, option in enumerate(self.menu_options):
                text = self.font.render(option, True, WHITE)
                self.screen.blit(text, (80, 100 + i * 50))
                if i == self.menu_index:
                    selector = self.font.render(">", True, WHITE)
                    self.screen.blit(selector, (40, 100 + i * 50))
            # Also, if in normal mode and checkpoints exist, display them on the side.
            if not self.special_mode and self.checkpoints:
                cp_text = self.font.render("Checkpoints:", True, WHITE)
                self.screen.blit(cp_text, (SCREEN_WIDTH - 300, 100))
                for i, cp in enumerate(self.checkpoints):
                    cp_option = self.font.render(f"{i+1}: {cp:.1f} m", True, WHITE)
                    self.screen.blit(cp_option, (SCREEN_WIDTH - 300, 140 + i*40))
            pygame.display.flip()
            self.clock.tick(FPS)

    # ----- Checkpoint Menu (only for Normal mode) -----
    def checkpoint_menu_loop(self):
        options = ["Start from Bottom"] + [f"{cp:.1f} m" for cp in self.checkpoints]
        selected = 0
        running = True
        while running and self.state == "CHECKPOINT":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        self.start_checkpoint = 0 if selected == 0 else options[selected]
                        # Convert selected option to a score (if not bottom)
                        if selected > 0:
                            self.start_checkpoint = float(options[selected].split()[0])
                        else:
                            self.start_checkpoint = 0
                        self.state = "NARRATIVE"
                        running = False
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "MENU"
                        running = False
            self.screen.fill(BLACK)
            title = self.font.render("Select Checkpoint", True, WHITE)
            self.screen.blit(title, (50, 50))
            for i, option in enumerate(options):
                text = self.font.render(option, True, WHITE)
                self.screen.blit(text, (50, 100 + i*40))
                if i == selected:
                    selector = self.font.render(">", True, WHITE)
                    self.screen.blit(selector, (20, 100 + i*40))
            pygame.display.flip()
            self.clock.tick(FPS)

    # ----- High Scores Loop -----
    def high_scores_loop(self):
        running = True
        while running and self.state == "HIGH_SCORES":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        self.state = "MENU"
                        running = False
            self.screen.fill(BLACK)
            title = self.font.render("High Scores", True, WHITE)
            self.screen.blit(title, (50, 50))
            for i, score in enumerate(self.high_scores):
                score_text = self.font.render(f"{i+1}. {score:.1f} m", True, WHITE)
                self.screen.blit(score_text, (50, 100 + i * 40))
            info = self.font.render("Press ESC or Enter to return", True, WHITE)
            self.screen.blit(info, (50, 300))
            pygame.display.flip()
            self.clock.tick(FPS)

    # ----- Music Menu with Paging -----
    def music_menu_loop(self):
        page_size = 5
        current_page = 0
        selected = 0
        active = True
        while active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % page_size
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % page_size
                    elif event.key == pygame.K_LEFT:
                        current_page = max(0, current_page - 1)
                        selected = 0
                    elif event.key == pygame.K_RIGHT:
                        if (current_page+1)*page_size < len(self.all_music):
                            current_page += 1
                            selected = 0
                    elif event.key == pygame.K_RETURN:
                        choice = self.all_music[current_page * page_size + selected]
                        if choice == "Off":
                            pygame.mixer.music.stop()
                            self.current_music = None
                        else:
                            track_num = choice.split()[-1]
                            filename = f"music_{track_num}.mp3"
                            try:
                                pygame.mixer.music.load(filename)
                                pygame.mixer.music.play(-1)
                                self.current_music = filename
                            except Exception as e:
                                print("Failed to load", filename, e)
                        active = False
                    elif event.key == pygame.K_ESCAPE:
                        active = False
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,150))
            self.screen.blit(overlay, (0,0))
            menu_width, menu_height = 300, 300
            menu_x = (SCREEN_WIDTH - menu_width) // 2
            menu_y = (SCREEN_HEIGHT - menu_height) // 2
            pygame.draw.rect(self.screen, DARK_GRAY, (menu_x, menu_y, menu_width, menu_height))
            title = self.font.render("Select Music", True, WHITE)
            title_rect = title.get_rect(center=(menu_x + menu_width//2, menu_y + 30))
            self.screen.blit(title, title_rect)
            for i in range(page_size):
                idx = current_page * page_size + i
                if idx < len(self.all_music):
                    option = self.all_music[idx]
                    text = self.font.render(option, True, WHITE)
                    text_rect = text.get_rect(center=(menu_x + menu_width//2, menu_y + 70 + i*40))
                    self.screen.blit(text, text_rect)
                    if i == selected:
                        selector = self.font.render(">", True, WHITE)
                        sel_rect = selector.get_rect(center=(menu_x + 30, menu_y + 70 + i*40))
                        self.screen.blit(selector, sel_rect)
            page_text = self.font.render(f"Page {current_page+1} of {((len(self.all_music)-1)//page_size)+1}", True, WHITE)
            page_rect = page_text.get_rect(center=(menu_x + menu_width//2, menu_y + menu_height - 30))
            self.screen.blit(page_text, page_rect)
            pygame.display.flip()
            self.clock.tick(FPS)
        self.state = "MENU"

    # ----- Credits Loop with Word Wrapping -----
    def credits_loop(self):
        credits_text = ("A Needed Climb\nDeveloped by Kohen Johnston\nArt, Music & Code by the internet/Kohen\n"
                        "Special Thanks to my brain and all the people who helped")
        wrapped_lines = wrap_text(credits_text, self.font, SCREEN_WIDTH - 100)
        footer = "Press ESC or Enter to return."
        record = max(self.high_scores) if self.high_scores else 0
        milestone = 500
        if record >= 10000:
            record_msg = "You Win... I could never make it to the top, I'm glad you could"
        else:
            while record >= milestone and milestone < 10000:
                milestone += 500
            record_msg = f"My record is {milestone}m, can you beat it?"
        running = True
        while running and self.state == "CREDITS":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self.state = "MENU"
                    running = False
            self.screen.fill(BLACK)
            y = 50
            for line in wrapped_lines:
                text = self.font.render(line, True, WHITE)
                self.screen.blit(text, (50, y))
                y += 40
            footer_text = self.font.render(footer, True, WHITE)
            self.screen.blit(footer_text, (50, SCREEN_HEIGHT - 90))
            record_text = self.font.render(record_msg, True, WHITE)
            self.screen.blit(record_text, (50, SCREEN_HEIGHT - 50))
            pygame.display.flip()
            self.clock.tick(FPS)

    # ----- Collectibles Loop (Two Pages: Random and Achievements) -----
    def collectibles_loop(self):
        page = self.collectibles_page  # "Random" or "Achievements"
        grid_rows = 4
        grid_cols = 4
        cell_size = 50
        padding = 60   # changed padding to 60
        grid_width = grid_cols * cell_size + (grid_cols+1) * padding
        grid_height = grid_rows * cell_size + (grid_rows+1) * padding
        start_x = (SCREEN_WIDTH - grid_width) // 2
        start_y = (SCREEN_HEIGHT - grid_height) // 2
        sel_row = 0
        sel_col = 0
        show_tab_info = True
        tab_info_timer = 0
        message = ""
        message_timer = 0
        running = True
        while running and self.state == "COLLECTIBLES":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        page = "Achievements" if page == "Random" else "Random"
                        show_tab_info = False  # hide info after TAB is pressed
                    elif event.key == pygame.K_UP:
                        sel_row = (sel_row - 1) % grid_rows
                    elif event.key == pygame.K_DOWN:
                        sel_row = (sel_row + 1) % grid_rows
                    elif event.key == pygame.K_LEFT:
                        sel_col = (sel_col - 1) % grid_cols
                    elif event.key == pygame.K_RIGHT:
                        sel_col = (sel_col + 1) % grid_cols
                    elif event.key == pygame.K_RETURN:
                        idx = sel_row * grid_cols + sel_col
                        if page == "Random":
                            if idx in self.collected_collectibles:
                                self.player_color = collectible_defs[idx][1]
                                message = f"Player color changed to {collectible_defs[idx][0]}"
                            else:
                                message = "You don't have that collectible yet!"
                        else:
                            if idx in self.unlocked_achievements:
                                self.player_color = achievement_defs[idx][1]
                                message = f"Player color changed to {achievement_defs[idx][0]}"
                            else:
                                message = "You haven't unlocked that achievement yet!"
                        message_timer = pygame.time.get_ticks()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                        self.state = "MENU"
            self.screen.fill(BLACK)
            header = self.font.render(f"{page} Collectibles", True, WHITE)
            self.screen.blit(header, (50, 20))
            for row in range(grid_rows):
                for col in range(grid_cols):
                    idx = row * grid_cols + col
                    if page == "Random":
                        if idx in self.collected_collectibles:
                            color = collectible_defs[idx][1]
                            name = collectible_defs[idx][0]
                        else:
                            color = LIGHT_GREY
                            name = "???"
                    else:
                        if idx in self.unlocked_achievements:
                            color = achievement_defs[idx][1]
                            name = achievement_defs[idx][0]
                        else:
                            color = LIGHT_GREY
                            name = "???"
                    cell_x = start_x + padding + col * (cell_size + padding)
                    cell_y = start_y + padding + row * (cell_size + padding)
                    cell_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)
                    s = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                    s.fill(color)
                    self.screen.blit(s, (cell_x, cell_y))
                    name_text = self.font.render(name, True, WHITE)
                    text_rect = name_text.get_rect(center=(cell_x+cell_size//2, cell_y+cell_size+15))
                    self.screen.blit(name_text, text_rect)
            sel_x = start_x + padding + sel_col * (cell_size + padding)
            sel_y = start_y + padding + sel_row * (cell_size + padding)
            selector_rect = pygame.Rect(sel_x-2, sel_y-2, cell_size+4, cell_size+4)
            pygame.draw.rect(self.screen, YELLOW, selector_rect, 3)
            if show_tab_info:
                info = self.font.render("Press TAB to toggle page", True, WHITE)
                self.screen.blit(info, (50, SCREEN_HEIGHT - 550))
            if message and pygame.time.get_ticks() - message_timer < 2000:
                msg_text = self.font.render(message, True, WHITE)
                self.screen.blit(msg_text, (50, SCREEN_HEIGHT - 50))
            pygame.display.flip()
            self.clock.tick(FPS)
        self.collectibles_page = page

    # ----- Narrative Loop (Blank, wait one key) -----
    def narrative_loop(self):
        self.screen.fill(BLACK)
        prompt = self.font.render("Press any key to start", True, WHITE)
        self.screen.blit(prompt, (50, SCREEN_HEIGHT//2))
        pygame.display.flip()
        waiting = True
        while waiting and self.state == "NARRATIVE":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    waiting = False
                    self.state = "GAMEPLAY"
            self.clock.tick(FPS)

    # ----- Gameplay Loop with Checkpoints -----
    def gameplay_loop(self):
        # Use checkpoint if in normal mode and selected from menu; otherwise start from bottom.
        start_score = 0
        if not self.special_mode and hasattr(self, "start_checkpoint"):
            start_score = self.start_checkpoint
        start_y = SCREEN_HEIGHT - 100
        player_start_y = start_y - start_score * PIXELS_PER_METER
        player = Player(SCREEN_WIDTH//2, start_y - 37, color=self.player_color)
        tower = Tower(start_y, special_mode=self.special_mode)
        score = start_score
        max_height = player.rect.y
        # For checkpoints: update current checkpoint when score increases by 200m
        checkpoint_message = ""
        checkpoint_timer = 0
        spawned_collectibles = []
        last_collectible_spawn = start_score
        running = True
        while running and self.state == "GAMEPLAY":
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.jump_buffer_time = pygame.time.get_ticks()
                    elif event.key == pygame.K_ESCAPE:
                        pause_choice = self.pause_loop()
                        if pause_choice == "quit":
                            self.state = "MENU"
                            return
            player.update(tower.platforms)
            if player.rect.y < max_height:
                max_height = player.rect.y
            # If player falls more than 1000 pixels below highest reached, they die.
            if player.rect.y > max_height + 1000:
                running = False
                self.state = "GAME_OVER"
            score = start_score + (start_y - player.rect.y) / PIXELS_PER_METER
            # Checkpoint: if score increases by at least 200 from last checkpoint, update.
            if not self.special_mode and score >= self.current_checkpoint + 200:
                self.current_checkpoint = score
                self.checkpoints.append(score)
                checkpoint_message = "Checkpoint reached!"
                checkpoint_timer = pygame.time.get_ticks()
            # Spawn random collectibles every 200m
            if score - last_collectible_spawn >= 200:
                last_collectible_spawn = score
                if random.random() < 1/8:
                    candidate = random.randint(0, 15)
                    if candidate not in self.collected_collectibles:
                        camera_offset_y = player.rect.y - SCREEN_HEIGHT//2
                        x = random.randint(50, SCREEN_WIDTH-50)
                        y = camera_offset_y + random.randint(50, SCREEN_HEIGHT//2)
                        spawned_collectibles.append(Collectible(x, y, 20, collectible_defs[candidate][0], collectible_defs[candidate][1]))
            camera_offset_y = player.rect.y - SCREEN_HEIGHT//2
            for col in spawned_collectibles[:]:
                if player.rect.colliderect(col.rect):
                    for idx, (name, color) in enumerate(collectible_defs):
                        if name == col.name:
                            self.collected_collectibles.add(idx)
                            break
                    spawned_collectibles.remove(col)
            tower.update(camera_offset_y)
            self.screen.fill(DARK_GRAY)
            for plat in tower.platforms:
                plat.draw(self.screen, self.font, camera_offset_y)
            # Draw checkpoint line
            if not self.special_mode and self.current_checkpoint > 0:
                cp_y = start_y - self.current_checkpoint * PIXELS_PER_METER - camera_offset_y
                for x in range(0, SCREEN_WIDTH, 15):
                    pygame.draw.line(self.screen, WHITE, (x, cp_y), (x+7, cp_y), 2)
                if pygame.time.get_ticks() - checkpoint_timer < 2000:
                    cp_msg = self.font.render("Checkpoint reached!", True, WHITE)
                    self.screen.blit(cp_msg, (SCREEN_WIDTH//2 - cp_msg.get_width()//2, cp_y - 30))
            for col in spawned_collectibles:
                col.draw(self.screen, camera_offset_y)
            adj_player = pygame.Rect(player.rect.x, player.rect.y - camera_offset_y, player.width, player.height)
            pygame.draw.rect(self.screen, self.player_color, adj_player)
            score_text = self.font.render(f"Height: {score:.1f} m", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            pygame.display.flip()
        if self.state == "GAME_OVER":
            self.game_over_screen(score)
            if not self.special_mode:
                # Unlock achievements based on thresholds for normal mode (first 8)
                for i in range(8):
                    threshold = 500 * (i+1)
                    if score >= threshold:
                        self.unlocked_achievements.add(i)
            else:
                for i in range(8):
                    threshold = 500 * (i+1)
                    if score >= threshold:
                        self.unlocked_achievements.add(8+i)
            self.high_scores.append(score)
            self.high_scores.sort(reverse=True)
            self.high_scores = self.high_scores[:5]
            self.save_high_scores()
            self.state = "MENU"

    # ----- Game Over Screen -----
    def game_over_screen(self, score):
        running = True
        title = self.font.render("You have died", True, WHITE)
        subtitle = pygame.font.SysFont(None, 28).render("But your soul persists and finds another body so you may try again", True, WHITE)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    running = False
            self.screen.fill(BLACK)
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 40))
            self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, SCREEN_HEIGHT//2 + 10))
            pygame.display.flip()
            self.clock.tick(FPS)

    # ----- Pause Loop -----
    def pause_loop(self):
        options = ["Resume", "Music Options", "High Scores", "Quit to Menu"]
        selected = 0
        paused = True
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        choice = options[selected]
                        if choice == "Resume":
                            paused = False
                        elif choice == "Music Options":
                            self.music_menu_loop()
                        elif choice == "High Scores":
                            self.high_scores_loop()
                        elif choice == "Quit to Menu":
                            return "quit"
                    elif event.key == pygame.K_ESCAPE:
                        paused = False
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            menu_width, menu_height = 300, 200
            menu_x = (SCREEN_WIDTH - menu_width) // 2
            menu_y = (SCREEN_HEIGHT - menu_height) // 2
            pygame.draw.rect(self.screen, DARK_GRAY, (menu_x, menu_y, menu_width, menu_height))
            for i, option in enumerate(options):
                text = self.font.render(option, True, WHITE)
                text_rect = text.get_rect(center=(menu_x + menu_width//2, menu_y + 40 + i*40))
                self.screen.blit(text, text_rect)
                if i == selected:
                    selector = self.font.render(">", True, WHITE)
                    sel_rect = selector.get_rect(center=(menu_x + 30, menu_y + 40 + i*40))
                    self.screen.blit(selector, sel_rect)
            pygame.display.flip()
            self.clock.tick(FPS)
        return "resume"

    def pause_music_loop(self):
        self.music_menu_loop()

    def pause_high_scores_loop(self):
        active = True
        while active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        active = False
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            menu_width, menu_height = 300, 300
            menu_x = (SCREEN_WIDTH - menu_width) // 2
            menu_y = (SCREEN_HEIGHT - menu_height) // 2
            pygame.draw.rect(self.screen, DARK_GRAY, (menu_x, menu_y, menu_width, menu_height))
            title = self.font.render("High Scores", True, WHITE)
            self.screen.blit(title, (menu_x + 20, menu_y + 20))
            for i, score in enumerate(self.high_scores):
                score_text = self.font.render(f"{i+1}. {score:.1f} m", True, WHITE)
                self.screen.blit(score_text, (menu_x + 20, menu_y + 60 + i*40))
            info = self.font.render("Press ESC or Enter to return", True, WHITE)
            self.screen.blit(info, (menu_x + 20, menu_y + menu_height - 40))
            pygame.display.flip()
            self.clock.tick(FPS)

    def game_over_loop(self):
        self.state = "MENU"

# ---------------- Main Execution ----------------
if __name__ == "__main__":
    game = Game()
    game.unlocked_achievements = set()
    game.run()

import os
import pygame
import random
from settings import SCREEN_WIDTH, WHITE, GRAY, YELLOW, BLACK, SPRITES_DIR


class Collectible:
    def __init__(self, x, y, size, name, color):
        self.rect = pygame.Rect(x, y, size, size)
        self.name = name
        self.color = color

    def draw(self, surface, camera_offset_y):
        adj_rect = pygame.Rect(self.rect.x, self.rect.y - camera_offset_y, self.rect.width, self.rect.height)
        swatch = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        swatch.fill(self.color)
        surface.blit(swatch, (adj_rect.x, adj_rect.y))


class Platform:
    def __init__(self, x, y, width, height, ptype="regular", symbol="",
                 is_moving=False, moving_speed=0,
                 is_conveyor=False, conveyor_speed=0,
                 is_icy=False, is_crumble=False, crumble_duration=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.original_y = y
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

    def update(self):
        if self.is_moving:
            self.rect.x += self.moving_speed
            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                self.moving_speed = -self.moving_speed
        if self.is_crumble and self.crumble_start_time is not None:
            current_time = pygame.time.get_ticks()
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
        elif self.ptype == "slope":
            color = (0, 255, 0)
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


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color=WHITE, is_bot=False):
        super().__init__()
        self.width = 40
        self.height = 40
        self.color = color
        self.is_bot = is_bot

        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump_strength = -15
        self.on_ground = False

        self.dashing = False
        self.dash_duration_ms = 160
        self.dash_start_time = 0
        self.dash_boost_multiplier = 3
        self.invulnerable = False

        self.facing_right = True
        self.bot_timer = 0

        self.sprite_sheet = self._load_sprite_sheet()
        self.image = self._extract_frame(0)
        self.rect = self.image.get_rect(center=(x, y))

    def _load_sprite_sheet(self):
        sprite_sheet_path = os.path.join(SPRITES_DIR, "original-49f68d37388b9b1ae5d98fc6fb02c1a5-911357247.jpg")
        return pygame.image.load(sprite_sheet_path).convert_alpha()

    def _extract_frame(self, frame_index):
        frame_count = 4
        frame_width = self.sprite_sheet.get_width() // frame_count
        frame_height = self.sprite_sheet.get_height()
        src_rect = pygame.Rect(frame_index * frame_width, 0, frame_width, frame_height)
        frame = self.sprite_sheet.subsurface(src_rect)
        frame = pygame.transform.smoothscale(frame, (self.width, self.height))
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        return frame

    def apply_gravity(self):
        self.vel_y += 0.8
        if self.vel_y > 10:
            self.vel_y = 10

    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_strength
            self.on_ground = False

    def dash(self):
        if not self.dashing:
            self.dashing = True
            self.dash_start_time = pygame.time.get_ticks()
            self.invulnerable = True
            if self.facing_right:
                self.vel_x += self.speed * (self.dash_boost_multiplier - 1)
            else:
                self.vel_x -= self.speed * (self.dash_boost_multiplier - 1)

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
        if keys[pygame.K_k] and not self.dashing:
            self.dash()

        if keys[pygame.K_a]:
            self.vel_x = -self.speed
            self.facing_right = False
        elif keys[pygame.K_d]:
            self.vel_x = self.speed
            self.facing_right = True
        elif not self.dashing:
            self.vel_x = 0

        if keys[pygame.K_SPACE]:
            self.jump()

    def update(self, platforms, keys=None):
        self.handle_input()

        if self.dashing and (pygame.time.get_ticks() - self.dash_start_time >= self.dash_duration_ms):
            self.dashing = False
            self.invulnerable = False
            if self.vel_x > 0:
                self.vel_x = self.speed
            elif self.vel_x < 0:
                self.vel_x = -self.speed

        self.apply_gravity()
        self.rect.x += int(self.vel_x)
        self.rect.y += int(self.vel_y)
        self.on_ground = False

        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_y > 0 and (self.rect.bottom - plat.rect.top) < 20:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0 and (plat.rect.bottom - self.rect.top) < 20:
                    self.rect.top = plat.rect.bottom
                    self.vel_y = 0

        frame_index = (pygame.time.get_ticks() // 120) % 4
        self.image = self._extract_frame(frame_index)

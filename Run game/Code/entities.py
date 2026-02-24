-import pygame
-import random
-from settings import SCREEN_WIDTH, SCREEN_HEIGHT, PIXELS_PER_METER, WHITE, GRAY, YELLOW, BLACK, LIGHT_GREY
-
-# ---------------- Collectible Class ----------------
-class Collectible:
-    def __init__(self, x, y, size, name, color):
-        self.rect = pygame.Rect(x, y, size, size)
-        self.name = name
-        self.color = color  # Expected as an RGBA tuple
-
-    def draw(self, surface, camera_offset_y):
-        adj_rect = pygame.Rect(self.rect.x, self.rect.y - camera_offset_y, self.rect.width, self.rect.height)
-        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
-        s.fill(self.color)
-        surface.blit(s, (adj_rect.x, adj_rect.y))
-
-# ---------------- Platform Class ----------------
-class Platform:
-    def __init__(self, x, y, width, height, ptype="regular", symbol="",
-                 is_moving=False, moving_speed=0,
-                 is_conveyor=False, conveyor_speed=0,
-                 is_icy=False, is_crumble=False, crumble_duration=None):
-        self.rect = pygame.Rect(x, y, width, height)
-        self.original_y = y  # For slope platforms to return to original position.
-        self.ptype = ptype
-        self.symbol = symbol
-        self.is_moving = is_moving
-        self.moving_speed = moving_speed
-        self.is_conveyor = is_conveyor
-        self.conveyor_speed = conveyor_speed
-        self.is_icy = is_icy
-        self.is_crumble = is_crumble
-        self.crumble_duration = crumble_duration  # in milliseconds
-        self.crumble_start_time = None
-        self.expired = False
-
-    def update(self):
-        if self.is_moving:
-            self.rect.x += self.moving_speed
-            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
-                self.moving_speed = -self.moving_speed
-        if self.is_crumble:
-            current_time = pygame.time.get_ticks()
-            if self.crumble_start_time is not None:
-                if not self.expired and (current_time - self.crumble_start_time >= self.crumble_duration):
-                    self.expired = True
-                elif self.expired and (current_time - self.crumble_start_time >= self.crumble_duration + 5000):
-                    self.expired = False
-                    self.crumble_start_time = None
-
-    def draw(self, surface, font, camera_offset_y):
-        if self.is_crumble and self.expired:
-            return
-        if self.ptype == "regular":
-            color = GRAY
-        elif self.ptype == "moving":
-            color = (150, 150, 250)
-        elif self.ptype == "conveyor":
-            color = YELLOW
-        elif self.ptype == "icy":
-            color = (180, 255, 255)
-        elif self.ptype == "slope":
-            color = (0, 255, 0)  # Green for slope platforms.
-        elif self.ptype.startswith("crumble"):
-            color = (255, 100, 100)
-        else:
-            color = GRAY
-
-        adj_rect = pygame.Rect(self.rect.x, self.rect.y - camera_offset_y, self.rect.width, self.rect.height)
-        pygame.draw.rect(surface, color, adj_rect)
-        if self.symbol:
-            text = font.render(self.symbol, True, BLACK)
-            text_rect = text.get_rect(center=adj_rect.center)
-            surface.blit(text, text_rect)
-
-# ---------------- Player Class ----------------
-class Player(pygame.sprite.Sprite):
-    def __init__(self, x, y, color=WHITE, is_bot=False):
-        super().__init__()
-        self.width = 40
-        self.height = 40
-        self.image = pygame.Surface((self.width, self.height))
-        self.image.fill(color)
-        self.rect = self.image.get_rect(center=(x, y))
-        self.color = color
-        self.vel_x = 0
-        self.vel_y = 0
-        self.speed = 5
-        self.jump_strength = -15
-        self.on_ground = False
-        self.dashing = False
-        self.dash_duration = 10  # Duration in frames
-        self.dash_timer = 0
-        self.dash_speed = 15
-        self.facing_right = True
-        self.invulnerable = False
-        self.dash_boost_multiplier = 3  # Multiplier applied to current speed when dashing
-        self.hp = 1
-        self.is_bot = is_bot
-        self.bot_timer = 0
-
-        # Sprite animations: load sprite sheets from the "Sprites" folder.
-        # Expected frame counts: idle=6, run=8, jump=8, dash=8. Each frame is scaled to 40x40.
-        self.sprites = {}
-        self.sprites['idle'] = pygame.image.load("Sprites/idle.png").convert_alpha()
-        self.sprites['run'] = pygame.image.load("Sprites/run.png").convert_alpha()
-        self.sprites['dash'] = pygame.image.load("Sprites/dash.png").convert_alpha()
-        self.sprites['jump'] = pygame.image.load("Sprites/jump.png").convert_alpha()
-        self.current_state = "idle"
-        self.frame_counts = {"idle": 6, "run": 8, "jump": 8, "dash": 8}
-        self.current_sprite = self.sprites['idle']
-        self.animation_frame = 0
-        self.animation_speed = 0.15
-        self.last_update = pygame.time.get_ticks()
-
-    def apply_gravity(self):
-        self.vel_y += 0.8
-        if self.vel_y > 10:
-            self.vel_y = 10
-
-    def jump(self):
-        if self.on_ground:
-            self.vel_y = self.jump_strength
-            self.on_ground = False
-            self.current_state = "jump"
-            self.current_sprite = self.sprites['jump']
-
-    def dash(self):
-        if not self.dashing:
-            self.dashing = True
-            self.dash_timer = self.dash_duration
-            self.invulnerable = True
-            # Add boost to current x velocity (dash adds to movement rather than overriding it)
-            if self.facing_right:
-                self.vel_x += self.speed * (self.dash_boost_multiplier - 1)
-            else:
-                self.vel_x -= self.speed * (self.dash_boost_multiplier - 1)
-            self.current_state = "dash"
-            self.current_sprite = self.sprites['dash']
-
-    def handle_input(self):
-        if self.is_bot:
-            now = pygame.time.get_ticks()
-            if now - self.bot_timer > random.randint(1000, 3000):
-                self.vel_x = random.choice([-self.speed, self.speed])
-                self.bot_timer = now
-            if self.rect.right > SCREEN_WIDTH - 10:
-                self.vel_x = -self.speed
-            elif self.rect.left < 10:
-                self.vel_x = self.speed
-            if self.on_ground and random.random() < 0.03:
-                self.jump()
-            return
-        keys = pygame.key.get_pressed()
-        current_time = pygame.time.get_ticks()
-        # Dash: press K key to dash (affects x velocity) and allow dashing while moving.
-        if keys[pygame.K_k] and not self.dashing and (current_time - self.last_update >= 16):
-            self.dash()
-            self.last_update = current_time
-        # WASD controls: A/D for left/right, SPACE for jump.
-        if keys[pygame.K_a]:
-            self.vel_x = -self.speed
-            self.facing_right = False
-            if not self.dashing:
-                self.current_state = "run"
-                self.current_sprite = self.sprites['run']
-        elif keys[pygame.K_d]:
-            self.vel_x = self.speed
-            self.facing_right = True
-            if not self.dashing:
-                self.current_state = "run"
-                self.current_sprite = self.sprites['run']
-        else:
-            if not self.dashing:
-                self.vel_x = 0
-                self.current_state = "idle"
-                self.current_sprite = self.sprites['idle']
-        if keys[pygame.K_SPACE]:
-            self.jump()
-
-    def update(self, platforms, keys=None):
-        current_time = pygame.time.get_ticks()
-        if keys is not None:
-            self.handle_input()
-        # End dash if duration expired (using frame-based timing approximation)
-        if self.dashing and (current_time - self.last_update >= self.dash_duration * 16):
-            self.dashing = False
-            self.invulnerable = False
-            # Resume normal speed in the current direction after dash\n            if self.vel_x > 0:\n                self.vel_x = self.speed\n            elif self.vel_x < 0:\n                self.vel_x = -self.speed\n            self.current_state = \"idle\"\n            self.current_sprite = self.sprites['idle']\n        self.apply_gravity()\n        self.rect.x += int(self.vel_x)\n        self.rect.y += int(self.vel_y)\n        for plat in platforms:\n            if self.rect.colliderect(plat.rect):\n                if self.vel_y > 0 and (self.rect.bottom - plat.rect.top) < 20:\n                    self.rect.bottom = plat.rect.top\n                    self.vel_y = 0\n                    self.on_ground = True\n                elif self.vel_y < 0 and (plat.rect.bottom - self.rect.top) < 20:\n                    self.rect.top = plat.rect.bottom\n                    self.vel_y = 0\n        self.update_animation()\n\n    def update_animation(self):\n        frame_count = self.frame_counts.get(self.current_state, 4)\n        self.animation_frame += self.animation_speed\n        if self.animation_frame >= frame_count:\n            self.animation_frame = 0\n        frame_width = self.current_sprite.get_width() // frame_count\n        frame_rect = pygame.Rect(int(self.animation_frame) * frame_width, 0, frame_width, self.current_sprite.get_height())\n        frame_image = self.current_sprite.subsurface(frame_rect)\n        frame_image = pygame.transform.scale(frame_image, (40, 40))\n        if not self.facing_right:\n            frame_image = pygame.transform.flip(frame_image, True, False)\n        self.image = frame_image\n\n    # Class attributes for animation\n    animation_frame = 0\n    animation_speed = 0.15\n    frame_counts = {\"idle\": 6, \"run\": 8, \"jump\": 8, \"dash\": 8}\n```
-
-
+import os
+import pygame
+import random
+from settings import SCREEN_WIDTH, WHITE, GRAY, YELLOW, BLACK, SPRITES_DIR
+
+
+class Collectible:
+    def __init__(self, x, y, size, name, color):
+        self.rect = pygame.Rect(x, y, size, size)
+        self.name = name
+        self.color = color
+
+    def draw(self, surface, camera_offset_y):
+        adj_rect = pygame.Rect(self.rect.x, self.rect.y - camera_offset_y, self.rect.width, self.rect.height)
+        swatch = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
+        swatch.fill(self.color)
+        surface.blit(swatch, (adj_rect.x, adj_rect.y))
+
+
+class Platform:
+    def __init__(self, x, y, width, height, ptype="regular", symbol="",
+                 is_moving=False, moving_speed=0,
+                 is_conveyor=False, conveyor_speed=0,
+                 is_icy=False, is_crumble=False, crumble_duration=None):
+        self.rect = pygame.Rect(x, y, width, height)
+        self.original_y = y
+        self.ptype = ptype
+        self.symbol = symbol
+        self.is_moving = is_moving
+        self.moving_speed = moving_speed
+        self.is_conveyor = is_conveyor
+        self.conveyor_speed = conveyor_speed
+        self.is_icy = is_icy
+        self.is_crumble = is_crumble
+        self.crumble_duration = crumble_duration
+        self.crumble_start_time = None
+        self.expired = False
+
+    def update(self):
+        if self.is_moving:
+            self.rect.x += self.moving_speed
+            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
+                self.moving_speed = -self.moving_speed
+        if self.is_crumble and self.crumble_start_time is not None:
+            current_time = pygame.time.get_ticks()
+            if not self.expired and (current_time - self.crumble_start_time >= self.crumble_duration):
+                self.expired = True
+            elif self.expired and (current_time - self.crumble_start_time >= self.crumble_duration + 5000):
+                self.expired = False
+                self.crumble_start_time = None
+
+    def draw(self, surface, font, camera_offset_y):
+        if self.is_crumble and self.expired:
+            return
+
+        if self.ptype == "regular":
+            color = GRAY
+        elif self.ptype == "moving":
+            color = (150, 150, 250)
+        elif self.ptype == "conveyor":
+            color = YELLOW
+        elif self.ptype == "icy":
+            color = (180, 255, 255)
+        elif self.ptype == "slope":
+            color = (0, 255, 0)
+        elif self.ptype.startswith("crumble"):
+            color = (255, 100, 100)
+        else:
+            color = GRAY
+
+        adj_rect = pygame.Rect(self.rect.x, self.rect.y - camera_offset_y, self.rect.width, self.rect.height)
+        pygame.draw.rect(surface, color, adj_rect)
+        if self.symbol:
+            text = font.render(self.symbol, True, BLACK)
+            text_rect = text.get_rect(center=adj_rect.center)
+            surface.blit(text, text_rect)
+
+
+class Player(pygame.sprite.Sprite):
+    def __init__(self, x, y, color=WHITE, is_bot=False):
+        super().__init__()
+        self.width = 40
+        self.height = 40
+        self.color = color
+        self.is_bot = is_bot
+
+        self.vel_x = 0
+        self.vel_y = 0
+        self.speed = 5
+        self.jump_strength = -15
+        self.on_ground = False
+
+        self.dashing = False
+        self.dash_duration_ms = 160
+        self.dash_start_time = 0
+        self.dash_boost_multiplier = 3
+        self.invulnerable = False
+
+        self.facing_right = True
+        self.bot_timer = 0
+
+        self.sprite_sheet = self._load_sprite_sheet()
+        self.image = self._extract_frame(0)
+        self.rect = self.image.get_rect(center=(x, y))
+
+    def _load_sprite_sheet(self):
+        sprite_sheet_path = os.path.join(SPRITES_DIR, "original-49f68d37388b9b1ae5d98fc6fb02c1a5-911357247.jpg")
+        return pygame.image.load(sprite_sheet_path).convert_alpha()
+
+    def _extract_frame(self, frame_index):
+        frame_count = 4
+        frame_width = self.sprite_sheet.get_width() // frame_count
+        frame_height = self.sprite_sheet.get_height()
+        src_rect = pygame.Rect(frame_index * frame_width, 0, frame_width, frame_height)
+        frame = self.sprite_sheet.subsurface(src_rect)
+        frame = pygame.transform.smoothscale(frame, (self.width, self.height))
+        if not self.facing_right:
+            frame = pygame.transform.flip(frame, True, False)
+        return frame
+
+    def apply_gravity(self):
+        self.vel_y += 0.8
+        if self.vel_y > 10:
+            self.vel_y = 10
+
+    def jump(self):
+        if self.on_ground:
+            self.vel_y = self.jump_strength
+            self.on_ground = False
+
+    def dash(self):
+        if not self.dashing:
+            self.dashing = True
+            self.dash_start_time = pygame.time.get_ticks()
+            self.invulnerable = True
+            if self.facing_right:
+                self.vel_x += self.speed * (self.dash_boost_multiplier - 1)
+            else:
+                self.vel_x -= self.speed * (self.dash_boost_multiplier - 1)
+
+    def handle_input(self):
+        if self.is_bot:
+            now = pygame.time.get_ticks()
+            if now - self.bot_timer > random.randint(1000, 3000):
+                self.vel_x = random.choice([-self.speed, self.speed])
+                self.bot_timer = now
+            if self.rect.right > SCREEN_WIDTH - 10:
+                self.vel_x = -self.speed
+            elif self.rect.left < 10:
+                self.vel_x = self.speed
+            if self.on_ground and random.random() < 0.03:
+                self.jump()
+            return
+
+        keys = pygame.key.get_pressed()
+        if keys[pygame.K_k] and not self.dashing:
+            self.dash()
+
+        if keys[pygame.K_a]:
+            self.vel_x = -self.speed
+            self.facing_right = False
+        elif keys[pygame.K_d]:
+            self.vel_x = self.speed
+            self.facing_right = True
+        elif not self.dashing:
+            self.vel_x = 0
+
+        if keys[pygame.K_SPACE]:
+            self.jump()
+
+    def update(self, platforms, keys=None):
+        self.handle_input()
+
+        if self.dashing and (pygame.time.get_ticks() - self.dash_start_time >= self.dash_duration_ms):
+            self.dashing = False
+            self.invulnerable = False
+            if self.vel_x > 0:
+                self.vel_x = self.speed
+            elif self.vel_x < 0:
+                self.vel_x = -self.speed
+
+        self.apply_gravity()
+        self.rect.x += int(self.vel_x)
+        self.rect.y += int(self.vel_y)
+        self.on_ground = False
+
+        for plat in platforms:
+            if self.rect.colliderect(plat.rect):
+                if self.vel_y > 0 and (self.rect.bottom - plat.rect.top) < 20:
+                    self.rect.bottom = plat.rect.top
+                    self.vel_y = 0
+                    self.on_ground = True
+                elif self.vel_y < 0 and (plat.rect.bottom - self.rect.top) < 20:
+                    self.rect.top = plat.rect.bottom
+                    self.vel_y = 0
+
+        frame_index = (pygame.time.get_ticks() // 120) % 4
+        self.image = self._extract_frame(frame_index)
 

)


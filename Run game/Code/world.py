import pygame
import random
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, PIXELS_PER_METER

from entities import Platform  # Make sure this import exists if using world.py

class Tower:
    def __init__(self, start_y, special_mode=False):
        self.platforms = []
        self.start_y = start_y
        self.highest_platform_y = start_y
        self.special_mode = special_mode
        self.generate_initial_platforms()
    # ... rest of Tower class ...


    def generate_initial_platforms(self):
        # Create the ground
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

        base_width = 200
        min_width = 50  # Adjusted to prevent unfair jumps
        width = max(min_width, base_width - ((diff - (500 * PIXELS_PER_METER)) // 50))

        offset = random.randint(-150, 150)
        center_x = prev_center_x + offset
        center_x = max(width // 2, min(SCREEN_WIDTH - width // 2, center_x))
        new_x = center_x - width // 2

        height = 20
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

        return Platform(new_x, new_y, width, height, ptype=ptype)

    def update(self, camera_offset_y):
        # Remove platforms too far below
        self.platforms = [p for p in self.platforms if p.rect.y - camera_offset_y < SCREEN_HEIGHT + 200]

        # Generate new platforms
        while self.highest_platform_y > camera_offset_y - 100:
            highest = min(self.platforms, key=lambda p: p.rect.y)
            new_plat = self.generate_next_platform(highest.rect.x + highest.rect.width // 2, highest.rect.y)
            self.platforms.append(new_plat)
            self.highest_platform_y = new_plat.rect.y

        # Update platforms (like moving platforms)
        for plat in self.platforms:
            plat.update()

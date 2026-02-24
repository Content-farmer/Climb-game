# game.py
import pygame, sys, random, os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, PIXELS_PER_METER, collectible_defs, achievement_defs, WHITE, DARK_GRAY, BLACK, YELLOW, LIGHT_GREY, HIGHSCORES_PATH, MUSIC_DIR
from utils import wrap_text
from entities import Collectible, Player
# game.py
from world import Tower  # Instead of importing from entities


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
        # Keep player color fixed (for the player body) and use crown_color to show the chosen color.
        self.player_color = WHITE
        self.crown_color = None
        self.special_mode = False  # False = Normal; True = Harder
        self.collectibles_page = "Random"  # "Random" or "Achievements"
        # Dialog triggers (score thresholds in m mapped to dialog MP3 file names)
        self.dialog_triggers = {1000: "up1.mp3",
                                3000: "up2.mp3",
                                5000: "up3.mp3",
                                7000: "up4.mp3",
                                9000: "up5.mp3"}
        self.death_dialog = "death.mp3"
        # Demo bot for menu background:
        self.demo_tower = Tower(SCREEN_HEIGHT - 50, special_mode=False)
        self.demo_bot = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100, color=self.player_color, is_bot=True)

    @property
    def all_music(self):
        return self._all_music
    @all_music.setter
    def all_music(self, value):
        self._all_music = value

    def load_high_scores(self):
        if os.path.exists(HIGHSCORES_PATH):
            with open(HIGHSCORES_PATH, "r") as f:
                scores = [float(line.strip()) for line in f.readlines()]
            scores.sort(reverse=True)
            return scores[:5]
        else:
            return []
    def save_high_scores(self):
        with open(HIGHSCORES_PATH, "w") as f:
            for score in self.high_scores:
                f.write(f"{score}\n")
    def run(self):
        while True:
            if self.state == "MENU":
                self.menu_loop()
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

    # ---------------- Menu Loop with Demo Bot Background ----------------
    def menu_loop(self):
        running = True
        while running and self.state == "MENU":
            self.demo_bot.update(self.demo_tower.platforms)
            camera_offset = self.demo_bot.rect.y - SCREEN_HEIGHT//2
            self.screen.fill(DARK_GRAY)
            for plat in self.demo_tower.platforms:
                plat.draw(self.screen, self.font, camera_offset)
            self.screen.blit(self.demo_bot.image, self.demo_bot.rect.move(0, -camera_offset))
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
            overlay.fill((0,0,0,200))
            self.screen.blit(overlay, (0,0))
            for i, option in enumerate(self.menu_options):
                text = self.font.render(option, True, WHITE)
                self.screen.blit(text, (80, 100 + i*50))
                if i == self.menu_index:
                    selector = self.font.render(">", True, WHITE)
                    self.screen.blit(selector, (40, 100 + i*50))
            pygame.display.flip()
            self.clock.tick(FPS)

    # ---------------- High Scores Loop ----------------
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
            self.screen.blit(title, (50,50))
            for i, score in enumerate(self.high_scores):
                score_text = self.font.render(f"{i+1}. {score:.1f} m", True, WHITE)
                self.screen.blit(score_text, (50, 100 + i*40))
            info = self.font.render("Press ESC or Enter to return", True, WHITE)
            self.screen.blit(info, (50,300))
            pygame.display.flip()
            self.clock.tick(FPS)

    # ---------------- Music Menu with Paging (loads from "Music" folder) ----------------
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
                        choice = self.all_music[current_page*page_size + selected]
                        if choice == "Off":
                            pygame.mixer.music.stop()
                            self.current_music = None
                        else:
                            track_num = choice.split()[-1]
                            filename = os.path.join(MUSIC_DIR, f"music_{track_num}.mp3")
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
            menu_width, menu_height = 300,300
            menu_x = (SCREEN_WIDTH-menu_width)//2
            menu_y = (SCREEN_HEIGHT-menu_height)//2
            pygame.draw.rect(self.screen, DARK_GRAY, (menu_x, menu_y, menu_width, menu_height))
            title = self.font.render("Select Music", True, WHITE)
            title_rect = title.get_rect(center=(menu_x+menu_width//2, menu_y+30))
            self.screen.blit(title, title_rect)
            for i in range(page_size):
                idx = current_page*page_size + i
                if idx < len(self.all_music):
                    option = self.all_music[idx]
                    text = self.font.render(option, True, WHITE)
                    text_rect = text.get_rect(center=(menu_x+menu_width//2, menu_y+70+i*40))
                    self.screen.blit(text, text_rect)
                    if i == selected:
                        selector = self.font.render(">", True, WHITE)
                        sel_rect = selector.get_rect(center=(menu_x+30, menu_y+70+i*40))
                        self.screen.blit(selector, sel_rect)
            page_text = self.font.render(f"Page {current_page+1} of {((len(self.all_music)-1)//page_size)+1}", True, WHITE)
            page_rect = page_text.get_rect(center=(menu_x+menu_width//2, menu_y+menu_height-30))
            self.screen.blit(page_text, page_rect)
            pygame.display.flip()
            self.clock.tick(FPS)
        self.state = "MENU"

    # ---------------- Credits Loop with Word Wrapping ----------------
    def credits_loop(self):
        credits_text = ("A Needed Climb\nDeveloped by Kohen Johnston\nArt, Music & Code by the internet/Kohen\n"
                        "Special Thanks to my brain and all the people who helped")
        wrapped_lines = wrap_text(credits_text, self.font, SCREEN_WIDTH-100)
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
            self.screen.blit(footer_text, (50, SCREEN_HEIGHT-90))
            record_text = self.font.render(record_msg, True, WHITE)
            self.screen.blit(record_text, (50, SCREEN_HEIGHT-50))
            pygame.display.flip()
            self.clock.tick(FPS)

    # ---------------- Collectibles Loop (Two Pages: Random and Achievements) ----------------
    def collectibles_loop(self):
        page = self.collectibles_page  # "Random" or "Achievements"
        grid_rows = 4
        grid_cols = 4
        cell_size = 50
        padding = 60
        grid_width = grid_cols * cell_size + (grid_cols+1) * padding
        grid_height = grid_rows * cell_size + (grid_rows+1) * padding
        start_x = (SCREEN_WIDTH - grid_width) // 2
        start_y = (SCREEN_HEIGHT - grid_height) // 2
        sel_row = 0
        sel_col = 0
        show_tab_info = True
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
                        show_tab_info = False
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
                                self.crown_color = collectible_defs[idx][1]
                                message = f"Crown color set to {collectible_defs[idx][0]}"
                            else:
                                message = "You don't have that collectible yet!"
                        else:
                            if idx in self.unlocked_achievements:
                                self.crown_color = achievement_defs[idx][1]
                                message = f"Crown color set to {achievement_defs[idx][0]}"
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
                self.screen.blit(info, (50, SCREEN_HEIGHT-550))
            if message and pygame.time.get_ticks() - message_timer < 2000:
                msg_text = self.font.render(message, True, WHITE)
                self.screen.blit(msg_text, (50, SCREEN_HEIGHT-50))
            pygame.display.flip()
            self.clock.tick(FPS)
        self.collectibles_page = page

    # ---------------- Narrative Loop (Blank, wait one key) ----------------
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

    # ---------------- Gameplay Loop with Dialog and Slope Platforms ----------------
    def gameplay_loop(self):
        start_y = SCREEN_HEIGHT - 50
        new_start_y = start_y  # No checkpoints now.
        player = Player(SCREEN_WIDTH//2, new_start_y - (37//2), color=self.player_color)
        tower = Tower(new_start_y, special_mode=self.special_mode)
        score = 0.0
        max_height = player.rect.y
        spawned_collectibles = []
        last_collectible_spawn = 0
        dialog_played = set()
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
            if player.rect.y > max_height + 1000:
                running = False
                self.state = "GAME_OVER"
                if "death" not in dialog_played:
                    try:
                        death_sound = pygame.mixer.Sound(os.path.join("Dialog", self.death_dialog))
                        death_sound.play()
                    except Exception as e:
                        print("Failed to play death dialog:", e)
                    dialog_played.add("death")
            score = (new_start_y - player.rect.y) / PIXELS_PER_METER
            for thresh, dlg_file in self.dialog_triggers.items():
                if score >= thresh and thresh not in dialog_played:
                    try:
                        dlg_sound = pygame.mixer.Sound(os.path.join("Dialog", dlg_file))
                        dlg_sound.play()
                    except Exception as e:
                        print("Failed to play dialog", dlg_file, e)
                    dialog_played.add(thresh)
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
            # Update slope platforms:
            for plat in tower.platforms:
                if plat.ptype == "slope":
                    if player.rect.colliderect(plat.rect):
                        if plat.rect.y < plat.original_y + 30:
                            plat.rect.y += 1
                    else:
                        if plat.rect.y > plat.original_y:
                            plat.rect.y -= 1
            self.screen.fill(DARK_GRAY)
            for plat in tower.platforms:
                plat.draw(self.screen, self.font, camera_offset_y)
            for col in spawned_collectibles:
                col.draw(self.screen, camera_offset_y)
            # Draw player (fixed color) then crown above:
            adj_player = player.rect.move(0, -camera_offset_y)
            self.screen.blit(player.image, adj_player)
            if self.crown_color:
                crown_height = 10
                crown_points = [(adj_player.centerx, adj_player.top - crown_height),
                                (adj_player.left, adj_player.top),
                                (adj_player.right, adj_player.top)]
                pygame.draw.polygon(self.screen, self.crown_color, crown_points)
            score_text = self.font.render(f"Height: {score:.1f} m", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            pygame.display.flip()
        if self.state == "GAME_OVER":
            self.game_over_screen(score)
            if not self.special_mode:
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

    # ---------------- Game Over Screen ----------------
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

    # ---------------- Pause Loop ----------------
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
            overlay.fill((0,0,0,150))
            self.screen.blit(overlay, (0,0))
            menu_width, menu_height = 300,200
            menu_x = (SCREEN_WIDTH - menu_width) // 2
            menu_y = (SCREEN_HEIGHT - menu_height) // 2
            pygame.draw.rect(self.screen, DARK_GRAY, (menu_x, menu_y, menu_width, menu_height))
            for i, option in enumerate(options):
                text = self.font.render(option, True, WHITE)
                text_rect = text.get_rect(center=(menu_x+menu_width//2, menu_y+40+i*40))
                self.screen.blit(text, text_rect)
                if i == selected:
                    selector = self.font.render(">", True, WHITE)
                    sel_rect = selector.get_rect(center=(menu_x+30, menu_y+40+i*40))
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
            overlay.fill((0,0,0,150))
            self.screen.blit(overlay, (0,0))
            menu_width, menu_height = 300,300
            menu_x = (SCREEN_WIDTH-menu_width)//2
            menu_y = (SCREEN_HEIGHT-menu_height)//2
            pygame.draw.rect(self.screen, DARK_GRAY, (menu_x, menu_y, menu_width, menu_height))
            title = self.font.render("High Scores", True, WHITE)
            self.screen.blit(title, (menu_x+20, menu_y+20))
            for i, score in enumerate(self.high_scores):
                score_text = self.font.render(f"{i+1}. {score:.1f} m", True, WHITE)
                self.screen.blit(score_text, (menu_x+20, menu_y+60+i*40))
            info = self.font.render("Press ESC or Enter to return", True, WHITE)
            self.screen.blit(info, (menu_x+20, menu_y+menu_height-40))
            pygame.display.flip()
            self.clock.tick(FPS)
    def game_over_loop(self):
        self.state = "MENU"

if __name__ == "__main__":
    game = Game()
    game.unlocked_achievements = set()
    game.run()

import pygame
import sys
import json
import os
from .audio_manager import AudioManager
from .transition import Transition
from .font_renderer import CustomFontRenderer
from .sprite_loader import SpriteLoader, Animation

class FreeplayMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.clock = pygame.time.Clock()
        self.running = True

        self.audio = AudioManager()
        self.transition = Transition(screen)
        self.game_font = CustomFontRenderer("assets/fonts/bold.xml", "assets/fonts/bold.png")

        self.system_font = pygame.font.Font("assets/fonts/Weight.ttf", 24)
        self.sprites = SpriteLoader()

        self.setup_menu()
        self.load_week_data()
        self.load_assets()
        self.audio_setup()

    def setup_menu(self):
        try:
            self.background = pygame.image.load("assets/menuBG.png").convert()
            self.background = pygame.transform.scale(self.background, (self.width, self.height))
        except:
            print("Error: No se pudo cargar el fondo menuBG")
            self.background = None
        
        self.title_color = (255, 255, 255)
        self.text_color = (200, 200, 200)
        self.selected_color = (255, 255, 0)
        self.panel_color = (0, 0, 0, 150)
        
        self.weeks = []
        self.week_index = 0

    def load_week_data(self):
        try:
            with open("data/week_data.json", "r", encoding="utf-8") as f:
                self.week_data = json.load(f)
            
            self.weeks = list(self.week_data.keys())
            print(f"Semanas cargadas: {self.weeks}")
            
        except Exception as e:
            print(f"Error cargando week_data.json: {e}")
            self.week_data = {
                "week1": {
                    "id": "week1",
                    "name": "Tutorial",
                    "display_name": "WEEK 1",
                    "description": "Learn the basics of the game",
                    "difficulty": "NORMAL",
                    "length": "1:30",
                    "composer": "Kawai Sprite",
                    "script": "scripts/week1_script.lua",
                    "songs": ["tutorial"],
                    "locked": False
                }
            }
            self.weeks = ["week1"]

    def get_current_week_info(self):
        if self.weeks and self.week_index < len(self.weeks):
            week_id = self.weeks[self.week_index]
            return self.week_data.get(week_id, {})
        return {}

    def load_assets(self):
        try:
            gf_frames = self.sprites.load_sprite_sheet("assets/gfDanceTitle.xml", "assets/gfDanceTitle.png")
            if gf_frames:
                self.gf_anim = Animation(list(gf_frames.values()), fps=24)
                print("GF animation cargada")
            else:
                self.gf_anim = None
        except Exception as e:
            self.gf_anim = None
            print(f"Error cargando GF: {e}")

    def audio_setup(self):
        self.audio.preload_sounds({
            "scroll": "audio/sfx/scroll.ogg",
            "confirm": "audio/sfx/confirm.ogg",
            "back": "audio/sfx/back.ogg"
        })

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.audio.cleanup()
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and not self.transition.is_active():
                    self.audio.play_sound("confirm", volume=0.8)
                    week_id = self.weeks[self.week_index]
                    
                    if week_id == "week1":
                        return "start_week1"
                    elif week_id == "week2":
                        return "start_week2"
                    elif week_id == "week3":
                        return "start_week3"
                    else:
                        return f"start_{week_id}"
                    
                elif event.key == pygame.K_ESCAPE and not self.transition.is_active():
                    self.audio.play_sound("back", volume=0.8)
                    self.transition.start_fade_out(self.transition_callback, ("song_selection",))
            
                elif event.key == pygame.K_DOWN and not self.transition.is_active():
                    self.audio.play_sound("scroll", volume=0.7)
                    self.week_index = (self.week_index + 1) % len(self.weeks)
                
                elif event.key == pygame.K_UP and not self.transition.is_active():
                    self.audio.play_sound("scroll", volume=0.7)
                    self.week_index = (self.week_index - 1) % len(self.weeks)
                    
        return None

    def transition_callback(self, next_screen):
        self.running = False
        self.next_screen = next_screen

    def update(self, dt):
        if hasattr(self, "gf_anim") and self.gf_anim:
            self.gf_anim.update(dt)
        self.transition.update()

    def create_panel(self, width, height, alpha=150):
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        panel.fill((0, 0, 0, alpha))
        return panel

    def draw_system_text(self, text, x, y, color=(255, 255, 255), font_size=20):
        try:
            font = pygame.font.Font("assets/fonts/Weight.ttf", font_size)
            text_surface = font.render(text, True, color)
            self.screen.blit(text_surface, (x, y))
            return text_surface.get_rect(topleft=(x, y))
        except:
            font = pygame.font.SysFont("Arial", font_size)
            text_surface = font.render(text, True, color)
            self.screen.blit(text_surface, (x, y))
            return text_surface.get_rect(topleft=(x, y))

    def draw_wrapped_system_text(self, text, x, y, max_width, color=(255, 255, 255), font_size=18):
        try:
            font = pygame.font.Font("assets/fonts/Weight.ttf", font_size)
        except:
            font = pygame.font.SysFont("Arial", font_size)
            
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        current_y = y
        for line in lines:
            text_surface = font.render(line, True, color)
            self.screen.blit(text_surface, (x, current_y))
            current_y += font_size + 5  # Espacio entre líneas

    def draw(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((0, 0, 0))

        title_text = "FREE PLAY"
        title_width = self.game_font.get_text_width(title_text, scale=1.0)
        title_x = (self.width - title_width) // 2
        title_y = 30
        self.game_font.render_text(title_text, title_x, title_y, self.screen, scale=1.0, color=self.title_color)

        panel_width = self.width * 0.42
        panel_height = self.height * 0.65
        left_panel_x = 25
        left_panel_y = 70
        
        left_panel = self.create_panel(int(panel_width), int(panel_height))
        self.screen.blit(left_panel, (left_panel_x, left_panel_y))

        info_title = "WEEK INFO"
        info_title_width = self.game_font.get_text_width(info_title, scale=1.0)
        info_title_x = left_panel_x + (panel_width - info_title_width) // 2
        self.game_font.render_text(info_title, info_title_x, left_panel_y + 25, self.screen, scale=1.0, color=self.title_color)

        week_info = self.get_current_week_info()
        content_x = left_panel_x + 25
        content_start_y = left_panel_y + 70

        if week_info:
            self.game_font.render_text("ID:", content_x, content_start_y, self.screen, scale=0.8, color=self.selected_color)
            self.draw_system_text(week_info.get("id", "N/A"), content_x + 60, content_start_y, self.text_color, 18)

            self.game_font.render_text("NAME:", content_x, content_start_y + 35, self.screen, scale=0.8, color=self.selected_color)
            self.draw_system_text(week_info.get("name", "N/A"), content_x + 100, content_start_y + 35, self.text_color, 18)

            self.game_font.render_text("DIFFICULTY:", content_x, content_start_y + 70, self.screen, scale=0.8, color=self.selected_color)
            self.draw_system_text(week_info.get("difficulty", "NORMAL"), content_x + 150, content_start_y + 70, self.text_color, 18)

            self.game_font.render_text("LENGTH:", content_x, content_start_y + 105, self.screen, scale=0.8, color=self.selected_color)
            self.draw_system_text(week_info.get("length", "?:??"), content_x + 110, content_start_y + 105, self.text_color, 18)

            self.game_font.render_text("COMPOSER:", content_x, content_start_y + 140, self.screen, scale=0.8, color=self.selected_color)
            self.draw_system_text(week_info.get("composer", "Unknown"), content_x + 130, content_start_y + 140, self.text_color, 18)

            songs = week_info.get("songs", [])
            self.game_font.render_text("SONGS:", content_x, content_start_y + 185, self.screen, scale=0.8, color=self.selected_color)
            for i, song in enumerate(songs):
                song_y = content_start_y + 215 + (i * 25)
                self.draw_system_text(f"- {song}", content_x + 20, song_y, self.text_color, 16)

            description = week_info.get("description", "")
            if description:
                self.game_font.render_text("DESCRIPTION:", content_x, content_start_y + 260, self.screen, scale=0.8, color=self.selected_color)
                self.draw_wrapped_system_text(description, content_x, content_start_y + 285, 
                                            panel_width - 50, self.text_color, 16)

        right_panel_x = self.width - panel_width - 25
        right_panel_y = 70
        
        right_panel = self.create_panel(int(panel_width), int(panel_height))
        self.screen.blit(right_panel, (right_panel_x, right_panel_y))
        weeks_title = "WEEK SELECT"
        weeks_title_width = self.game_font.get_text_width(weeks_title, scale=1.0)
        weeks_title_x = right_panel_x + (panel_width - weeks_title_width) // 2
        self.game_font.render_text(weeks_title, weeks_title_x, right_panel_y + 25, self.screen, scale=1.0, color=self.title_color)

        week_start_y = right_panel_y + 70
        week_spacing = 55

        for i, week_id in enumerate(self.weeks):
            week_data = self.week_data.get(week_id, {})
            color = self.selected_color if i == self.week_index else self.text_color
            
            week_display = week_data.get("display_name", f"WEEK {i+1}")
            week_width = self.game_font.get_text_width(week_display, scale=0.9)
            week_x = right_panel_x + (panel_width - week_width) // 2
            week_y = week_start_y + i * week_spacing
            
            self.game_font.render_text(week_display, week_x, week_y, self.screen, scale=0.9, color=color)
            
            if i == self.week_index:
                selector = ">"
                self.game_font.render_text(selector, week_x - 35, week_y, self.screen, scale=0.9, color=self.selected_color)

        if hasattr(self, "gf_anim") and self.gf_anim:
            frame = self.gf_anim.get_current_frame()
            if frame:
                gf_surface = frame["surface"]
                gf_scale = 0.3
                gf_scaled = pygame.transform.scale(
                    gf_surface,
                    (int(gf_surface.get_width() * gf_scale), int(gf_surface.get_height() * gf_scale))
                )
                gf_x = (self.width - gf_scaled.get_width()) // 2
                gf_y = self.height - gf_scaled.get_height() - 30
                self.screen.blit(gf_scaled, (gf_x, gf_y))

        instructions_text = "ENTER: SELECT WEEK   ESC: BACK TO MENU"
        instructions_rect = self.draw_system_text(instructions_text, 0, 0, self.text_color, 18)
        instructions_x = (self.width - instructions_rect.width) // 2
        instructions_y = self.height - 35
        self.draw_system_text(instructions_text, instructions_x, instructions_y, self.text_color, 18)

        self.transition.draw()
        pygame.display.flip()

    def run(self):
        last_time = pygame.time.get_ticks()
        self.transition.start_fade_in()

        while self.running:
            now = pygame.time.get_ticks()
            dt = now - last_time
            last_time = now

            result = self.handle_input()
            if result:
                return result

            self.update(dt)
            self.draw()
            self.clock.tick(60)

        return getattr(self, "next_screen", "song_selection")
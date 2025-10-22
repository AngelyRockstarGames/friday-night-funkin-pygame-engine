import pygame
import sys
import os
from .sprite_loader import SpriteLoader, ButtonAnimation
from .audio_manager import AudioManager
from .transition import Transition

class SongSelection:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.sprite_loader = SpriteLoader()
        self.clock = pygame.time.Clock()
        self.running = True
        self.audio_manager = AudioManager()
        self.transition = Transition(screen)
        
        self.load_assets()
        self.setup_animations()
        self.setup_elements()
        self.setup_audio()
    
    def load_assets(self):
        self.freeplay_frames = self.sprite_loader.load_sprite_sheet(
            "assets/freeplay.xml", 
            "assets/freeplay.png"
        )
        self.credits_frames = self.sprite_loader.load_sprite_sheet(
            "assets/credits.xml", 
            "assets/credits.png"
        )
        
        try:
            self.background = pygame.image.load("assets/menuBG.png").convert()
            self.background = pygame.transform.scale(self.background, (self.width, self.height))
        except:
            print("Error: No se pudo cargar el fondo menuBG")
            self.background = None
    
    def setup_animations(self):
        if self.freeplay_frames:
            self.freeplay_animation = ButtonAnimation(self.freeplay_frames, fps=12)
        if self.credits_frames:
            self.credits_animation = ButtonAnimation(self.credits_frames, fps=12)
    
    def setup_elements(self):
        self.buttons = [
            {"name": "freeplay", "x": 0, "y": 0, "width": 0, "height": 0, "selected": False},
            {"name": "credits", "x": 0, "y": 0, "width": 0, "height": 0, "selected": False}
        ]
        self.selected_button = 0
        
        try:
            self.font = pygame.font.Font("fonts/vcr_osd_mono.ttf", 24)
        except:
            self.font = pygame.font.SysFont("Arial", 24)
            print("Info: Usando fuente por defecto")
    
    def setup_audio(self):

        nav_sounds = {
            "scroll": "audio/sfx/scroll.ogg",
            "confirm": "audio/sfx/confirm.ogg",
            "back": "audio/sfx/back.ogg"
        }
        self.audio_manager.preload_sounds(nav_sounds)
        
        self.audio_manager.play_music("songs/menu_theme.ogg")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.audio_manager.cleanup()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and not self.transition.is_active():
                    self.audio_manager.play_sound("confirm", volume=0.7)
                    if self.selected_button == 0:
                        self.transition.start_fade_out(self.transition_callback, ("freeplay",))
                    else:

                        return "credits"
                elif event.key == pygame.K_ESCAPE and not self.transition.is_active():
                    self.audio_manager.play_sound("back", volume=0.7)
                    self.transition.start_fade_out(self.transition_callback, ("main_menu",))
                elif event.key == pygame.K_UP and not self.transition.is_active():
                    self.audio_manager.play_sound("scroll", volume=0.5)
                    self.selected_button = (self.selected_button - 1) % len(self.buttons)
                elif event.key == pygame.K_DOWN and not self.transition.is_active():
                    self.audio_manager.play_sound("scroll", volume=0.5)
                    self.selected_button = (self.selected_button + 1) % len(self.buttons)
        return None
    
    def transition_callback(self, next_screen):
        self.running = False
        self.next_screen = next_screen
    
    def update(self, dt):
        if hasattr(self, 'freeplay_animation'):
            if self.selected_button == 0:
                self.freeplay_animation.set_state("selected")
            else:
                self.freeplay_animation.set_state("idle")
            self.freeplay_animation.update(dt)
        
        if hasattr(self, 'credits_animation'):
            if self.selected_button == 1:
                self.credits_animation.set_state("selected")
            else:
                self.credits_animation.set_state("idle")
            self.credits_animation.update(dt)
        
        for i, button in enumerate(self.buttons):
            button["selected"] = (i == self.selected_button)
        
        self.transition.update()
    
    def draw(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((0, 0, 0))
        
        button_y_start = self.height // 2 - 100
        
        if hasattr(self, 'freeplay_animation'):
            freeplay_frame = self.freeplay_animation.get_current_frame()
            if freeplay_frame:
                freeplay_surface = freeplay_frame['surface']
                freeplay_scale = 0.8
                freeplay_scaled = pygame.transform.scale(freeplay_surface, 
                    (int(freeplay_surface.get_width() * freeplay_scale), 
                     int(freeplay_surface.get_height() * freeplay_scale)))
                freeplay_x = (self.width - freeplay_scaled.get_width()) // 2
                freeplay_y = button_y_start
                self.screen.blit(freeplay_scaled, (freeplay_x, freeplay_y))
                self.buttons[0]["x"] = freeplay_x
                self.buttons[0]["y"] = freeplay_y
                self.buttons[0]["width"] = freeplay_scaled.get_width()
                self.buttons[0]["height"] = freeplay_scaled.get_height()
        
        if hasattr(self, 'credits_animation'):
            credits_frame = self.credits_animation.get_current_frame()
            if credits_frame:
                credits_surface = credits_frame['surface']
                credits_scale = 0.8
                credits_scaled = pygame.transform.scale(credits_surface, 
                    (int(credits_surface.get_width() * credits_scale), 
                     int(credits_surface.get_height() * credits_scale)))
                credits_x = (self.width - credits_scaled.get_width()) // 2
                credits_y = button_y_start + 150
                self.screen.blit(credits_scaled, (credits_x, credits_y))
                self.buttons[1]["x"] = credits_x
                self.buttons[1]["y"] = credits_y
                self.buttons[1]["width"] = credits_scaled.get_width()
                self.buttons[1]["height"] = credits_scaled.get_height()
        
        if self.selected_button == 1:
            debug_text = self.font.render("(credits script missing here)", True, (255, 0, 0))
            debug_x = 50
            debug_y = 200
            self.screen.blit(debug_text, (debug_x, debug_y))
        
        instructions_text = self.font.render("USE ARROWS TO SELECT - ENTER TO CONFIRM - ESC TO BACK", True, (255, 255, 255))
        instructions_x = (self.width - instructions_text.get_width()) // 2
        instructions_y = self.height - 100
        self.screen.blit(instructions_text, (instructions_x, instructions_y))
        
        self.transition.draw()
        
        pygame.display.flip()
    
    def run(self):
        last_time = pygame.time.get_ticks()
        self.transition.start_fade_in()
        
        while self.running:
            current_time = pygame.time.get_ticks()
            dt = current_time - last_time
            last_time = current_time
            
            result = self.handle_events()
            if result:
                return result
            
            self.update(dt)
            self.draw()
            self.clock.tick(60)
        
        return getattr(self, 'next_screen', 'main_menu')
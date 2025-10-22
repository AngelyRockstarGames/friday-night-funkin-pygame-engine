import pygame
import sys
from .sprite_loader import SpriteLoader, Animation
from .audio_manager import AudioManager
from .transition import Transition

class MainMenu:
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
        self.gf_frames = self.sprite_loader.load_sprite_sheet(
            "assets/gfDanceTitle.xml", 
            "assets/gfDanceTitle.png"
        )
        self.logo_frames = self.sprite_loader.load_sprite_sheet(
            "assets/logoBumpin.xml", 
            "assets/logoBumpin.png"
        )
        self.enter_frames = self.sprite_loader.load_sprite_sheet(
            "assets/titleEnter.xml", 
            "assets/titleEnter.png"
        )
        
        if not self.gf_frames:
            print("Error: No se pudieron cargar los sprites de GF")
        if not self.logo_frames:
            print("Error: No se pudieron cargar los sprites del logo")
        if not self.enter_frames:
            print("Error: No se pudieron cargar los sprites de titleEnter")
    
    def setup_animations(self):
        if self.gf_frames:
            self.gf_animation = Animation(self.gf_frames, fps=25)
        if self.logo_frames:
            self.logo_animation = Animation(self.logo_frames, fps=25)
        if self.enter_frames:
            self.enter_animation = Animation(self.enter_frames, fps=25)
    
    def setup_elements(self):
        self.background_color = (0, 0, 0)
        self.press_enter_alpha = 255
        self.press_enter_fading = True
    
    def setup_audio(self):
        menu_sounds = {
            "scroll": "audio/sfx/scroll.ogg",
            "confirm": "audio/sfx/confirm.ogg"
        }
        self.audio_manager.preload_sounds(menu_sounds)
        
        self.audio_manager.play_music("audio/music/menu_theme.ogg", fade_in=1500)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.audio_manager.cleanup()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and not self.transition.is_active():

                    self.audio_manager.play_sound("confirm", volume=0.7)
                    self.transition.start_fade_out(self.transition_callback, ("song_selection",))
                elif event.key == pygame.K_ESCAPE:
                    self.audio_manager.cleanup()
                    pygame.quit()
                    sys.exit()
                elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    self.audio_manager.play_sound("scroll", volume=0.5)
        return None
    
    def transition_callback(self, next_screen):
        self.running = False
        self.next_screen = next_screen
    
    def update(self, dt):
        if hasattr(self, 'gf_animation'):
            self.gf_animation.update(dt)
        if hasattr(self, 'logo_animation'):
            self.logo_animation.update(dt)
        if hasattr(self, 'enter_animation'):
            self.enter_animation.update(dt)
        
        if self.press_enter_fading:
            self.press_enter_alpha -= 3
            if self.press_enter_alpha <= 50:
                self.press_enter_fading = False
        else:
            self.press_enter_alpha += 3
            if self.press_enter_alpha >= 255:
                self.press_enter_fading = True
        
        self.transition.update()
    
    def draw(self):
        self.screen.fill(self.background_color)
        
        if hasattr(self, 'logo_animation'):
            logo_frame = self.logo_animation.get_current_frame()
            logo_surface = logo_frame['surface']
            logo_scale = 0.9
            logo_scaled = pygame.transform.scale(logo_surface, 
                (int(logo_surface.get_width() * logo_scale), 
                 int(logo_surface.get_height() * logo_scale)))
            logo_x = 30
            logo_y = (self.height - logo_scaled.get_height()) // 2
            self.screen.blit(logo_scaled, (logo_x, logo_y))
        
        if hasattr(self, 'gf_animation'):
            gf_frame = self.gf_animation.get_current_frame()
            gf_surface = gf_frame['surface']
            gf_scale = 0.6
            gf_scaled = pygame.transform.scale(gf_surface, 
                (int(gf_surface.get_width() * gf_scale), 
                 int(gf_surface.get_height() * gf_scale)))
            gf_x = self.width - gf_scaled.get_width() - 30
            gf_y = (self.height - gf_scaled.get_height()) // 2
            self.screen.blit(gf_scaled, (gf_x, gf_y))
        
        if hasattr(self, 'enter_animation'):
            enter_frame = self.enter_animation.get_current_frame()
            enter_surface = enter_frame['surface']
            enter_scale = 0.4
            enter_scaled = pygame.transform.scale(enter_surface, 
                (int(enter_surface.get_width() * enter_scale), 
                 int(enter_surface.get_height() * enter_scale)))
            enter_x = (self.width - enter_scaled.get_width()) // 2
            enter_y = self.height - 150
            enter_scaled.set_alpha(self.press_enter_alpha)
            self.screen.blit(enter_scaled, (enter_x, enter_y))
        
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
        
        return getattr(self, 'next_screen', 'exit')
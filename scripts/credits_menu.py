import pygame
import sys
from .audio_manager import AudioManager
from .transition import Transition
from .font_renderer import CustomFontRenderer 

class CreditsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.clock = pygame.time.Clock()
        self.running = True
        self.audio_manager = AudioManager()
        self.transition = Transition(screen)
        
        self.font_renderer = CustomFontRenderer("assets/fonts/bold.xml", "assets/fonts/bold.png")
        
        self.setup_elements()
        self.setup_audio()
    
    def setup_elements(self):
        try:
            self.background = pygame.image.load("assets/menuBGBlue.png").convert()
            self.background = pygame.transform.scale(self.background, (self.width, self.height))
        except:
            print("Error: No se pudo cargar el fondo menuBGBlue")
            self.background = None
        
        self.text_color = (255, 255, 255)
        self.debug_color = (255, 0, 0)
    
    def setup_audio(self):
        self.audio_manager.preload_sounds({"back": "audio/sfx/back.ogg"})
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.audio_manager.cleanup()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_RETURN] and not self.transition.is_active():
                    self.audio_manager.play_sound("back", volume=0.7)
                    return "song_selection"
        return None
    
    def update(self, dt):
        self.transition.update()
    
    def draw(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((0, 0, 0))
        

        title = "CREDITS"
        title_width = self.font_renderer.get_text_width(title, scale=1.2)
        title_x = (self.width - title_width) // 2
        title_y = 100
        self.font_renderer.render_text(title, title_x, title_y, self.screen, scale=1.2, color=self.text_color)
        
        debug_text = "(no credits render)"
        debug_x = 50
        debug_y = 200
        self.font_renderer.render_text(debug_text, debug_x, debug_y, self.screen, color=self.debug_color)
        
        instructions_text = "PRESS ESC OR ENTER TO BACK"
        instructions_width = self.font_renderer.get_text_width(instructions_text, scale=0.8)
        instructions_x = (self.width - instructions_width) // 2
        instructions_y = self.height - 100
        self.font_renderer.render_text(instructions_text, instructions_x, instructions_y, self.screen, scale=0.8, color=self.text_color)
        
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
        
        return "song_selection"
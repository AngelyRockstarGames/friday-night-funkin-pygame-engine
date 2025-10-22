import pygame

class Transition:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.transition_surface = pygame.Surface((self.width, self.height))
        self.transition_surface.fill((0, 0, 0))
        self.alpha = 0
        self.speed = 8
        self.state = "none"  # "none", "fade_out", "fade_in"
        self.callback = None
        self.callback_args = None
    
    def start_fade_out(self, callback=None, callback_args=None):
        self.state = "fade_out"
        self.alpha = 0
        self.callback = callback
        self.callback_args = callback_args
    
    def start_fade_in(self):
        self.state = "fade_in"
        self.alpha = 255
    
    def update(self):
        if self.state == "fade_out":
            self.alpha += self.speed
            if self.alpha >= 255:
                self.alpha = 255
                if self.callback:
                    if self.callback_args:
                        self.callback(*self.callback_args)
                    else:
                        self.callback()
                self.state = "fade_in"
        
        elif self.state == "fade_in":
            self.alpha -= self.speed
            if self.alpha <= 0:
                self.alpha = 0
                self.state = "none"
    
    def draw(self):
        if self.state != "none":
            self.transition_surface.set_alpha(self.alpha)
            self.screen.blit(self.transition_surface, (0, 0))
    
    def is_active(self):
        return self.state != "none"
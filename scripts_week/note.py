import pygame
from .note_renderer import note_renderer

class Note:
    def __init__(self, direction, time, must_hit=True, length=0):
        self.direction = direction  # 0: left, 1: down, 2: up, 3: right
        self.time = time  
        self.must_hit = must_hit  
        self.length = length  
        self.active = True
        self.hit = False
        self.missed = False
        self.perfect = False
        self.good = False
        self.bad = False
        
        self.x = 0
        self.y = 0
        self.speed = 1.0
        

        self.confirm_animation_frame = 0
        self.confirm_animation_timer = 0
        self.showing_confirm = False
        
     
        self.alpha = 255
        self.scale = 1.0
    
    def update(self, dt, target_y, current_time):
    
        if not self.active:

            if self.showing_confirm:
                self.confirm_animation_timer += dt
                if self.confirm_animation_timer > 0.05:
                    self.confirm_animation_timer = 0
                    self.confirm_animation_frame += 1
                    if self.confirm_animation_frame >= 4: 
                        self.showing_confirm = False
            return
            

        time_until_hit = self.time - current_time
        
        if time_until_hit > 0:
            self.y = target_y - (time_until_hit * 500 * self.speed)
            
            distance_ratio = time_until_hit / 2.0  
            self.alpha = min(255, int(255 * (1.0 - distance_ratio * 0.5)))
            self.scale = 0.8 + (0.2 * distance_ratio)
        else:

            if not self.hit and not self.missed:
                self.missed = True
                self.active = False
    
    def check_hit(self, input_time, perfect_threshold=0.05, good_threshold=0.1, bad_threshold=0.15):
        if not self.active or self.hit or self.missed:
            return False
            
        time_diff = abs(input_time - self.time)
        
        if time_diff <= perfect_threshold:
            self.hit = True
            self.perfect = True
            self.active = False
            self.show_confirm_animation()
            return "perfect"
        elif time_diff <= good_threshold:
            self.hit = True  
            self.good = True
            self.active = False
            self.show_confirm_animation()
            return "good"
        elif time_diff <= bad_threshold:
            self.hit = True
            self.bad = True
            self.active = False
            self.show_confirm_animation()
            return "bad"
            
        return False
    
    def show_confirm_animation(self):
        self.showing_confirm = True
        self.confirm_animation_frame = 0
        self.confirm_animation_timer = 0
    
    def draw(self, screen, target_x, target_y):

        if self.showing_confirm:
            note_renderer.draw_confirm_effect(
                screen, 
                self.direction, 
                target_x, 
                target_y,
                animation_frame=self.confirm_animation_frame
            )
        elif self.active:
            width = int(100 * self.scale)
            height = int(100 * self.scale)
            x = target_x - width // 2
            y = self.y - height // 2
            
            note_renderer.draw_note(
                screen, 
                self.direction, 
                x, 
                y, 
                width, 
                height, 
                self.alpha
            )
            
            if self.length > 0:
                self.draw_sustain_note(screen, target_x, target_y)
    
    def draw_sustain_note(self, screen, target_x, target_y):
        length_height = (self.length / 1000.0) * 500 * self.speed
        sustain_rect = pygame.Rect(target_x - 15, self.y, 30, length_height)
        
        sustain_color = note_renderer.arrow_colors[self.direction]
        pygame.draw.rect(screen, sustain_color, sustain_rect)
        
        pygame.draw.rect(screen, (255, 255, 255), sustain_rect, 1)
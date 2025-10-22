import pygame
from .sprite_loader import SpriteLoader, Animation

class Character:
    def __init__(self, xml_path=None, image_path=None):
        self.sprite_loader = SpriteLoader()
        self.animations = {}
        self.current_animation = ""
        self.current_frame_index = 0
        self.animation_timer = 0
        self.animation_fps = 24
        self.current_frame = None
        
        self.x = 0
        self.y = 0
        self.scale = 1.0
        self.flip_x = False
        self.flip_y = False
        self.alpha = 255
        
        self.is_idle = True
        self.is_singing = False
        self.sing_direction = 0  # 0: left, 1: down, 2: up, 3: right
        
        if xml_path and image_path:
            self.load_character(xml_path, image_path)
    
    def load_character(self, xml_path, image_path):
        try:
            frames = self.sprite_loader.load_sprite_sheet(xml_path, image_path)
            if frames:
                self.setup_animations(frames)
                print(f"Personaje cargado: {len(self.animations)} animaciones")
                return True
            else:
                print(f"No se pudieron cargar los sprites del personaje: {xml_path}")
                return False
        except Exception as e:
            print(f"Error cargando personaje {xml_path}: {e}")
            return False
    
    def setup_animations(self, frames):
        animation_groups = {}
        
        for frame_name, frame_data in frames.items():
            base_name = frame_name.rstrip('0123456789')
            
            if base_name not in animation_groups:
                animation_groups[base_name] = []
            
            animation_groups[base_name].append(frame_data)
        
        for anim_name, anim_frames in animation_groups.items():
            anim_frames.sort(key=lambda frame: frame.get('name', ''))
            self.animations[anim_name] = Animation(anim_frames, fps=self.animation_fps)
        
        if self.animations:
            default_anims = ["idle", "BF idle dance", "Dad idle", "GF Dancing Beat"]
            for anim_name in default_anims:
                if anim_name in self.animations:
                    self.set_animation(anim_name)
                    break
            else:
                first_anim = list(self.animations.keys())[0]
                self.set_animation(first_anim)
    
    def set_animation(self, animation_name, force_reset=False):
        if animation_name in self.animations:
            if self.current_animation != animation_name or force_reset:
                self.current_animation = animation_name
                self.current_frame_index = 0
                self.animation_timer = 0
                self.animations[animation_name].reset()
                

                self.is_idle = any(idle_keyword in animation_name.lower() 
                                 for idle_keyword in ['idle', 'dance', 'beat'])
                self.is_singing = any(sing_keyword in animation_name.lower() 
                                    for sing_keyword in ['sing', 'note', 'left', 'right', 'up', 'down'])
                
                if 'left' in animation_name.lower():
                    self.sing_direction = 0
                elif 'down' in animation_name.lower():
                    self.sing_direction = 1
                elif 'up' in animation_name.lower():
                    self.sing_direction = 2
                elif 'right' in animation_name.lower():
                    self.sing_direction = 3
                
                return True
        else:
            print(f"Animación no encontrada: {animation_name}")
            return False
    
    def set_sing_animation(self, direction):
        direction_names = ["LEFT", "DOWN", "UP", "RIGHT"]
        direction_name = direction_names[direction]
        
        sing_anims = [
            f"sing{direction_name}",
            f"BF NOTE {direction_name}",
            f"Dad Sing {direction_name}",
            f"sing {direction_name.lower()}",
            f"note {direction_name.lower()}"
        ]
        
        for anim_name in sing_anims:
            if anim_name in self.animations:
                self.set_animation(anim_name)
                return True
        
        if "sing" in self.animations:
            self.set_animation("sing")
            return True
        
        return False
    
    def update(self, dt):
        if self.current_animation in self.animations:
            self.animations[self.current_animation].update(dt)
            current_frame_data = self.animations[self.current_animation].get_current_frame()
            
            if current_frame_data:
                self.current_frame = current_frame_data["surface"]
                
                if self.flip_x or self.flip_y:
                    self.current_frame = pygame.transform.flip(self.current_frame, self.flip_x, self.flip_y)
                
                if self.scale != 1.0:
                    original_size = self.current_frame.get_size()
                    new_size = (int(original_size[0] * self.scale), int(original_size[1] * self.scale))
                    self.current_frame = pygame.transform.scale(self.current_frame, new_size)
                
                if self.alpha < 255:
                    self.current_frame.set_alpha(self.alpha)
    
    def draw(self, screen, x=None, y=None):
        if self.current_frame:
            draw_x = x if x is not None else self.x
            draw_y = y if y is not None else self.y
            
            # Centrar el sprite
            rect = self.current_frame.get_rect()
            draw_x -= rect.width // 2
            draw_y -= rect.height // 2
            
            screen.blit(self.current_frame, (draw_x, draw_y))
    
    def get_animation_names(self):
        return list(self.animations.keys())
    
    def has_animation(self, animation_name):
        return animation_name in self.animations
    
    def reset_to_idle(self):
        idle_anims = ["idle", "BF idle dance", "Dad idle", "GF Dancing Beat"]
        for anim_name in idle_anims:
            if anim_name in self.animations:
                self.set_animation(anim_name)
                return True
        return False
    
    def set_position(self, x, y):
        self.x = x
        self.y = y
    
    def set_scale(self, scale):
        self.scale = scale
    
    def set_flip(self, flip_x=False, flip_y=False):
        self.flip_x = flip_x
        self.flip_y = flip_y
    
    def set_alpha(self, alpha):
        self.alpha = max(0, min(255, alpha))
    
    def get_size(self):
        if self.current_frame:
            return self.current_frame.get_size()
        return (0, 0)
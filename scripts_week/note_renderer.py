import pygame
from .sprite_loader import SpriteLoader

class NoteRenderer:
    def __init__(self):
        self.sprite_loader = SpriteLoader()
        self.note_frames = {}
        self.arrow_frames = {}
        self.press_animations = {}
        self.confirm_animations = {}
        
        self.load_note_assets()
    
    def load_note_assets(self):

        try:
            self.note_frames = self.sprite_loader.load_sprite_sheet(
                "assets/NOTE_assets.xml", 
                "assets/NOTE_assets.png"
            )
            
            if self.note_frames:
                print(f"✅ Cargados {len(self.note_frames)} sprites de notas")
                self.setup_animations()
            else:
                print("No se pudieron cargar los sprites de notas")
                
        except Exception as e:
            print(f"Error cargando assets de notas: {e}")
    
    def setup_animations(self):
        self.arrow_frames = {
            0: self.get_frame("arrowLEFT0000"),    # Izquierda
            1: self.get_frame("arrowDOWN0000"),    # Abajo
            2: self.get_frame("arrowUP0000"),      # Arriba
            3: self.get_frame("arrowRIGHT0000")    # Derecha
        }
        
        self.press_animations = {
            0: self.create_animation(["left press0000", "left press0001", "left press0002", "left press0003"]),
            1: self.create_animation(["down press0000", "down press0001", "down press0002", "down press0003"]),
            2: self.create_animation(["up press0000", "up press0001", "up press0002", "up press0003"]),
            3: self.create_animation(["right press0000", "right press0001", "right press0002", "right press0003"])
        }
        
        self.confirm_animations = {
            0: self.create_animation(["left confirm0000", "left confirm0001", "left confirm0002", "left confirm0003"]),
            1: self.create_animation(["down confirm0000", "down confirm0001", "down confirm0002", "down confirm0003"]),
            2: self.create_animation(["up confirm0000", "up confirm0001", "up confirm0002", "up confirm0003"]),
            3: self.create_animation(["right confirm0000", "right confirm0001", "right confirm0002", "right confirm0003"])
        }
        
        self.arrow_colors = [
            (255, 0, 0),    # Rojo - Izquierda
            (0, 255, 0),    # Verde - Abajo  
            (0, 0, 255),    # Azul - Arriba
            (255, 255, 0)   # Amarillo - Derecha
        ]
    
    def get_frame(self, frame_name):
        return self.note_frames.get(frame_name)
    
    def create_animation(self, frame_names):
        frames = []
        for name in frame_names:
            frame = self.get_frame(name)
            if frame:
                frames.append(frame)
        return frames if frames else None
    
    def draw_note(self, screen, direction, x, y, width=100, height=100, alpha=255):
        frame = self.arrow_frames.get(direction)
        
        if frame and frame["surface"]:
            scaled_surface = pygame.transform.scale(frame["surface"], (width, height))
            
            if alpha < 255:
                scaled_surface.set_alpha(alpha)
                
            screen.blit(scaled_surface, (x, y))
        else:
            color = self.arrow_colors[direction]
            note_rect = pygame.Rect(x, y, width, height)
            pygame.draw.rect(screen, color, note_rect)
            pygame.draw.rect(screen, (255, 255, 255), note_rect, 2)
    
    def draw_arrow(self, screen, direction, x, y, width=100, height=100, pressed=False, animation_frame=0):
        if pressed and self.press_animations.get(direction):
            animation = self.press_animations[direction]
            if animation_frame < len(animation):
                frame = animation[animation_frame]
                if frame and frame["surface"]:
                    scaled_surface = pygame.transform.scale(frame["surface"], (width, height))
                    screen.blit(scaled_surface, (x, y))
                    return
        else:
            self.draw_note(screen, direction, x, y, width, height)
    
    def draw_confirm_effect(self, screen, direction, x, y, width=150, height=150, animation_frame=0):
        if self.confirm_animations.get(direction):
            animation = self.confirm_animations[direction]
            if animation_frame < len(animation):
                frame = animation[animation_frame]
                if frame and frame["surface"]:
                    scaled_surface = pygame.transform.scale(frame["surface"], (width, height))
                    screen.blit(scaled_surface, (x - (width - 100) // 2, y - (height - 100) // 2))
                    return True
        return False
    
    def get_note_size(self, direction):
        frame = self.arrow_frames.get(direction)
        if frame and frame["surface"]:
            return frame["surface"].get_size()
        return (100, 100)

note_renderer = NoteRenderer()
import pygame
import xml.etree.ElementTree as ET
import os

class SpriteLoader:
    def __init__(self):
        self.sprites = {}
    
    def load_sprite_sheet(self, xml_path, image_path):
        try:
            if not os.path.exists(image_path):
                print(f"Error: No se encuentra la imagen {image_path}")
                return None
                
            sheet_image = pygame.image.load(image_path).convert_alpha()
            
            if not os.path.exists(xml_path):
                print(f"Error: No se encuentra el XML {xml_path}")
                return None
                
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            frames = []
            for subtexture in root.findall('SubTexture'):
                frame_data = {
                    'name': subtexture.get('name'),
                    'x': int(subtexture.get('x')),
                    'y': int(subtexture.get('y')),
                    'width': int(subtexture.get('width')),
                    'height': int(subtexture.get('height')),
                    'frameX': int(subtexture.get('frameX', 0)),
                    'frameY': int(subtexture.get('frameY', 0)),
                    'frameWidth': int(subtexture.get('frameWidth', int(subtexture.get('width')))),
                    'frameHeight': int(subtexture.get('frameHeight', int(subtexture.get('height'))))
                }
                
                frame_surface = pygame.Surface((frame_data['width'], frame_data['height']), pygame.SRCALPHA)
                frame_surface.blit(sheet_image, (0, 0), 
                                 (frame_data['x'], frame_data['y'], 
                                  frame_data['width'], frame_data['height']))
                
                frame_data['surface'] = frame_surface
                frames.append(frame_data)
            
            return frames
            
        except Exception as e:
            print(f"Error cargando spritesheet: {e}")
            return None
class Animation:
    def __init__(self, frames, fps=12):
        self.frames = frames
        self.fps = fps
        self.current_frame = 0
        self.animation_time = 0
        self.frame_duration = 1000 / fps
    
    def update(self, dt):
        self.animation_time += dt
        if self.animation_time >= self.frame_duration:
            self.animation_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
    
    def get_current_frame(self):
        return self.frames[self.current_frame]

class ButtonAnimation:
    def __init__(self, frames, fps=12):
        self.all_frames = frames
        self.idle_frames = [f for f in frames if 'idle' in f['name']]
        self.selected_frames = [f for f in frames if 'selected' in f['name']]
        self.fps = fps
        self.current_frame = 0
        self.animation_time = 0
        self.frame_duration = 1000 / fps
        self.state = "idle"
    
    def set_state(self, state):
        if state != self.state:
            self.state = state
            self.current_frame = 0
            self.animation_time = 0
    
    def update(self, dt):
        self.animation_time += dt
        
        current_frames = self.idle_frames if self.state == "idle" else self.selected_frames
        
        if not current_frames:
            return
            
        if self.animation_time >= self.frame_duration:
            self.animation_time = 0
            self.current_frame = (self.current_frame + 1) % len(current_frames)
    
    def get_current_frame(self):
        current_frames = self.idle_frames if self.state == "idle" else self.selected_frames
        
        if not current_frames:
            if self.all_frames:
                return self.all_frames[0]
            return None
            
        return current_frames[self.current_frame]
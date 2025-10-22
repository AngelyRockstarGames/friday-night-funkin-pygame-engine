import pygame
import xml.etree.ElementTree as ET
from typing import Dict, Tuple

class CustomFontRenderer:
    def __init__(self, xml_path: str, image_path: str):
        self.characters: Dict[str, Dict] = {}
        self.load_font(xml_path, image_path)
    
    def load_font(self, xml_path: str, image_path: str):
        try:
            self.font_sheet = pygame.image.load(image_path).convert_alpha()
            
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            for char in root.findall('SubTexture'):
                name = char.get('name')
                x = int(char.get('x'))
                y = int(char.get('y'))
                width = int(char.get('width'))
                height = int(char.get('height'))
                
                base_char = name.rstrip('0123')
                
                if base_char.startswith('-') and base_char.endswith('-'):
                    special_chars = {
                        '-andpersand-': '&',
                        '-angry faic-': '☹',
                        '-apostraphie-': "'",
                        '-back slash-': '\\',
                        '-comma-': ',',
                        '-dash-': '-',
                        '-down arrow-': '↓',
                        '-end quote-': '"',
                        '-exclamation point-': '!',
                        '-forward slash-': '/',
                        '-greater than-': '>',
                        '-heart-': '♥',
                        '-left arrow-': '←',
                        '-less than-': '<',
                        '-multiply x-': '×',
                        '-period-': '.',
                        '-question mark-': '?',
                        '-right arrow-': '→',
                        '-start quote-': '"',
                        '-up arrow-': '↑'
                    }
                    base_char = special_chars.get(base_char, base_char)
                
                if base_char not in self.characters:
                    self.characters[base_char] = []
                
                self.characters[base_char].append({
                    'rect': pygame.Rect(x, y, width, height),
                    'width': width,
                    'height': height
                })
                
        except Exception as e:
            print(f"Error loading font: {e}")
    
    def render_text(self, text: str, x: int, y: int, surface: pygame.Surface, 
                   scale: float = 1.0, color: Tuple[int, int, int] = (255, 255, 255),
                   spacing: int = 0):

        current_x = x
        
        for char in text:
            if char == ' ':
                current_x += 20 * scale 
                continue
                
            if char in self.characters:
                char_data = self.characters[char][0]
                char_surface = pygame.Surface((char_data['width'], char_data['height']), pygame.SRCALPHA)
                char_surface.blit(self.font_sheet, (0, 0), char_data['rect'])
                
                if scale != 1.0:
                    new_width = int(char_data['width'] * scale)
                    new_height = int(char_data['height'] * scale)
                    char_surface = pygame.transform.scale(char_surface, (new_width, new_height))
                
                if color != (255, 255, 255):
                    char_surface.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
                
                # Dibujar en la superficie principal
                surface.blit(char_surface, (current_x, y))
                current_x += char_data['width'] * scale + spacing
            else:
                current_x += 20 * scale
    
    def get_text_width(self, text: str, scale: float = 1.0, spacing: int = 0) -> int:
        width = 0
        
        for char in text:
            if char == ' ':
                width += 20 * scale
            elif char in self.characters:
                char_data = self.characters[char][0]
                width += char_data['width'] * scale + spacing
            else:
                width += 20 * scale
        
        return width
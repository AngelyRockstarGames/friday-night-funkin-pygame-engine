# scripts/week_manager.py
import pygame
from .sprite_loader import SpriteLoader, Animation

class WeekManager:
    def __init__(self):
        self.sprite_loader = SpriteLoader()
        self.week_frames = {}
        self.week_animations = {}
        
    def load_weeks(self):
        print("Cargando sprites de semanas...")
        self.week_frames = self.sprite_loader.load_sprite_sheet(
            "assets/fonts/campaign_menu_UI_assets.xml", 
            "assets/fonts/campaign_menu_UI_assets.png"
        )
        
        if self.week_frames is None:
            print("Error: No se pudieron cargar los sprites de las semanas")
            self.week_frames = {}
            return False
        
        print(f"WeekManager: {len(self.week_frames)} sprites cargados")
        return True
    
    def setup_week_animations(self):
        self.week_animations = {}
        
        if not self.week_frames:
            print("Error: No hay frames disponibles para crear animaciones")
            return False
        
        week_sprites = {
            "tutorial": ["tutorial selected0000", "tutorial selected0001"],
            "week1": ["WEEK1 select0000", "WEEK1 select0001"],
            "week2": ["week2 select0000", "week2 select0001"], 
            "week3": ["Week 3 press0000", "Week 3 press0001"],
            "week4": ["Week 4 press0000", "Week 4 press0001"],
            "week5": ["week 50000", "week 50001"],
            "week6": ["Week 60000", "Week 60001"]
        }
        
        successful_weeks = 0
        for week_name, sprite_names in week_sprites.items():
            frames = []
            missing_sprites = []
            
            for sprite_name in sprite_names:
                if sprite_name in self.week_frames:
                    frames.append(self.week_frames[sprite_name])
                else:
                    missing_sprites.append(sprite_name)
            
            if frames:
                self.week_animations[week_name] = Animation(frames, fps=12)
                successful_weeks += 1
                print(f"Animación creada para: {week_name}")
            else:
                print(f"No se pudo crear animación para {week_name}")
                if missing_sprites:
                    print(f"   Sprites faltantes: {missing_sprites}")
        
        print(f"Animaciones creadas: {successful_weeks}/{len(week_sprites)} semanas")
        return successful_weeks > 0
    
    def get_week_animation(self, week_name):
        return self.week_animations.get(week_name)
    
    def get_available_weeks(self):
        return list(self.week_animations.keys())
    
    def update_animations(self, dt):
        for animation in self.week_animations.values():
            animation.update(dt)
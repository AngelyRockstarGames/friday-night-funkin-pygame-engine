import pygame
import sys
import time
import psutil
import os
from scripts.main_page import MainMenu
from scripts.song_selection import SongSelection
from scripts.WeekSelectorMenu import FreeplayMenu
from scripts.credits_menu import CreditsMenu
from scripts.audio_manager import AudioManager

class DebugInfo:
    def __init__(self):
        self.show_debug = False
        self.font = None
        self.fps_history = []
        self.max_history = 60
        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0
        
    def setup_font(self):
        try:
            self.font = pygame.font.Font("fonts/vcr_osd_mono.ttf", 16)
        except:
            self.font = pygame.font.SysFont("Courier New", 16)
    
    def update_fps(self):
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_time = current_time
            
            self.fps_history.append(self.fps)
            if len(self.fps_history) > self.max_history:
                self.fps_history.pop(0)
    
    def get_cpu_usage(self):
        return psutil.cpu_percent(interval=None)
    
    def get_memory_usage(self):
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def get_avg_fps(self):
        if not self.fps_history:
            return 0
        return sum(self.fps_history) / len(self.fps_history)
    
    def draw(self, screen):
        if not self.show_debug or not self.font:
            return
        
        audio_mgr = AudioManager()
        
        cpu_usage = self.get_cpu_usage()
        memory_usage = self.get_memory_usage()
        avg_fps = self.get_avg_fps()
        
        debug_lines = [
            f"FPS: {self.fps}",
            f"Avg FPS: {avg_fps:.1f}",
            f"CPU: {cpu_usage:.1f}%",
            f"RAM: {memory_usage:.1f} MB",
            f"Music: {audio_mgr.get_current_music() or 'None'}",
            f"Music State: {audio_mgr.music_state.value}",
            "",
            "F12: Toggle Debug",
            "ESC: Exit"
        ]
        
        y_offset = 10
        for line in debug_lines:
            if line:
                text_surface = self.font.render(line, True, (0, 255, 0))
                screen.blit(text_surface, (10, y_offset))
            y_offset += 20

class Game:
    def __init__(self):
        pygame.init()
        
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("fukin")
        
        self.debug_info = DebugInfo()
        self.debug_info.setup_font()
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.in_background = False
        
        self.current_screen = "main_menu"
        self.screens = {
            "main_menu": MainMenu,
            "song_selection": SongSelection,
            "freeplay": FreeplayMenu,
            "credits": CreditsMenu
        }
        
        self.audio_manager = AudioManager()
        
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.ACTIVEEVENT])
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.ACTIVEEVENT:
                if event.gain == 0:
                    self.in_background = True
                    self.pause_game()
                else:
                    self.in_background = False
                    self.resume_game()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F12:
                    self.debug_info.show_debug = not self.debug_info.show_debug
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def pause_game(self):
        self.audio_manager.pause_music()
    
    def resume_game(self):
        self.audio_manager.resume_music()
    
    def run_screen(self, screen_name):
        screen_class = self.screens.get(screen_name)
        if screen_class:
            screen_instance = screen_class(self.screen)
            return screen_instance.run()
        return "exit"
    
    def run(self):
        last_time = time.time()
        
        try:
            while self.running:
                current_time = time.time()
                dt = (current_time - last_time) * 1000
                last_time = current_time
                
                self.handle_events()
                
                if self.in_background:
                    self.clock.tick(10)
                    pygame.time.wait(50)
                    continue
                
                self.debug_info.update_fps()
                
                result = self.run_screen(self.current_screen)
                
                if result == "exit":
                    self.running = False
                elif result in self.screens:
                    self.current_screen = result
                elif result == "main_menu":
                    self.current_screen = "main_menu"
                elif result == "song_selection":
                    self.current_screen = "song_selection"
                elif result == "freeplay":
                    self.current_screen = "freeplay"
                elif result == "credits":
                    self.current_screen = "credits"
                elif result.startswith("start_song:"):
                    song_name = result.split(":")[1]
                    print(f"Iniciando canción: {song_name}")
                    self.current_screen = "song_selection"
                    self.audio_manager.play_music("songs/menu_theme.ogg", fade_in=1000)
                elif result.startswith("start_week"):
                    week_id = result.replace("start_", "")
                    print(f"Iniciando semana: {week_id}")
                    
                    if week_id == "week1":
                        from scripts_week.Week1Tutorial import Week1Tutorial
                        week_game = Week1Tutorial(self.screen)
                        week_result = week_game.run()
                    
                        self.current_screen = "main_menu"
                        self.audio_manager.play_music("songs/menu_theme.ogg", fade_in=1000)
                    else:
                        print(f"Semana {week_id} no implementada aún")
                        self.current_screen = "freeplay"
                
                if self.debug_info.show_debug:
                    self.debug_info.draw(self.screen)
                
                pygame.display.flip()
                self.clock.tick(60)
                
        except Exception as e:
            print(f"Error en el juego: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.audio_manager.cleanup()
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
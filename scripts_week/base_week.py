import pygame
import os
from .audio_manager import week_audio_manager
from .note_renderer import note_renderer

class BaseWeek:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.running = True
        self.score = 0
        self.health = 100
        self.combo = 0
        self.max_combo = 0
        self.notes_hit = 0
        self.notes_missed = 0
        self.accuracy = 100.0
        
        self.audio_manager = week_audio_manager
        
        self.note_renderer = note_renderer
        self.notes = []
        self.active_notes = []
        
        self.song_start_time = 0
        self.current_song_time = 0
        self.song_playing = False
        
        self.game_state = "playing"  # playing, paused, game_over, completed
        self.pause_menu = None
        
    def load_assets(self):
        raise NotImplementedError("Cada semana debe implementar load_assets()")
    
    def setup_audio(self):
        raise NotImplementedError("Cada semana debe implementar setup_audio()")
    
    def setup_stage(self):
        """Configurar stage y posiciones - debe ser implementado por cada semana"""
        raise NotImplementedError("Cada semana debe implementar setup_stage()")
    
    def load_song_data(self):
        raise NotImplementedError("Cada semana debe implementar load_song_data()")
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.toggle_pause()
                elif self.game_state == "playing":
                    # Manejar flechas del jugador
                    if event.key == pygame.K_LEFT:
                        self.handle_note_input(0)
                    elif event.key == pygame.K_DOWN:
                        self.handle_note_input(1)
                    elif event.key == pygame.K_UP:
                        self.handle_note_input(2)
                    elif event.key == pygame.K_RIGHT:
                        self.handle_note_input(3)
        
        return None
    
    def handle_note_input(self, direction):
        current_time = self.get_current_song_time()
        
        best_note = None
        best_time_diff = 0.2 
        
        for note in self.active_notes:
            if note.direction == direction and note.must_hit and note.active:
                time_diff = abs(note.time - current_time)
                if time_diff < best_time_diff:
                    best_time_diff = time_diff
                    best_note = note
        
        if best_note:
            result = best_note.check_hit(current_time)
            if result:
                self.on_note_hit(best_note, result)
                self.audio_manager.play_sound("hit", volume=0.7)
        else:
            self.on_note_miss(direction)
            self.audio_manager.play_sound("miss", volume=0.5)
    
    def on_note_hit(self, note, result):
        note.hit = True
        note.active = False
        
        if result == "perfect":
            self.score += 350
            self.combo += 1
            self.health = min(100, self.health + 2)
        elif result == "good":
            self.score += 200
            self.combo += 1
            self.health = min(100, self.health + 1)
        elif result == "bad":
            self.score += 100
            self.combo = 0
            self.health = max(0, self.health - 5)
        
        self.notes_hit += 1
        self.max_combo = max(self.max_combo, self.combo)
        self.calculate_accuracy()
        
        self.on_note_hit_animation(note.direction)
    
    def on_note_miss(self, direction):
        self.combo = 0
        self.notes_missed += 1
        self.health = max(0, self.health - 10)
        self.calculate_accuracy()
        
        self.on_note_miss_animation(direction)
    
    def calculate_accuracy(self):
        total_notes = self.notes_hit + self.notes_missed
        if total_notes > 0:
            self.accuracy = (self.notes_hit / total_notes) * 100
        else:
            self.accuracy = 100.0
    
    def on_note_hit_animation(self, direction):
        pass
    
    def on_note_miss_animation(self, direction):
        pass
    
    def toggle_pause(self):
        if self.game_state == "playing":
            self.game_state = "paused"
            self.audio_manager.pause_music()
        elif self.game_state == "paused":
            self.game_state = "playing"
            self.audio_manager.resume_music()
    
    def get_current_song_time(self):
        if self.song_playing:
            return self.current_song_time
        return 0
    
    def start_song(self):
        self.song_start_time = pygame.time.get_ticks() / 1000.0
        self.song_playing = True
        self.audio_manager.resume_music()
    
    def stop_song(self):
        self.song_playing = False
        self.audio_manager.stop_music()
    
    def update(self, dt):
        if self.game_state != "playing":
            return
        
        if self.song_playing:
            self.current_song_time = (pygame.time.get_ticks() / 1000.0) - self.song_start_time
        
        self.update_notes(dt)
        
        self.check_game_conditions()
        
        self.update_animations(dt)
    
    def update_notes(self, dt):
        current_time = self.get_current_song_time()
        
        for note in self.active_notes[:]:
            note.update(dt, self.get_note_target_y(), current_time)

            if not note.active and not note.showing_confirm:
                self.active_notes.remove(note)
        
        self.spawn_notes(current_time)
    
    def spawn_notes(self, current_time):
        pass
    
    def get_note_target_y(self):
        return self.height - 200
    
    def check_game_conditions(self):
        if self.health <= 0:
            self.game_state = "game_over"
        elif self.is_song_completed():
            self.game_state = "completed"
    
    def is_song_completed(self):
        return False
    
        pass
    

        pass
    
    def draw_hud(self):

        score_font = pygame.font.Font(None, 36)
        score_text = score_font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (20, 20))
        
        combo_text = score_font.render(f"Combo: {self.combo}", True, (255, 255, 255))
        self.screen.blit(combo_text, (20, 60))
        
        accuracy_text = score_font.render(f"Accuracy: {self.accuracy:.1f}%", True, (255, 255, 255))
        self.screen.blit(accuracy_text, (20, 100))
        
        self.draw_health_bar()
        
    
        if self.game_state == "paused":
            self.draw_pause_screen()
        elif self.game_state == "game_over":
            self.draw_game_over_screen()
        elif self.game_state == "completed":
            self.draw_completed_screen()
    
    def draw_health_bar(self):
        health_width = 300 * (self.health / 100)
        health_color = (0, 255, 0) if self.health > 50 else (255, 255, 0) if self.health > 25 else (255, 0, 0)
        
        health_rect = pygame.Rect(self.width // 2 - 150, 30, health_width, 20)
        health_border = pygame.Rect(self.width // 2 - 150, 30, 300, 20)
        
        pygame.draw.rect(self.screen, health_color, health_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), health_border, 2)
    
        health_font = pygame.font.Font(None, 24)
        health_text = health_font.render(f"Health: {int(self.health)}%", True, (255, 255, 255))
        self.screen.blit(health_text, (self.width // 2 - 40, 35))
    
    def draw_pause_screen(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        pause_font = pygame.font.Font(None, 72)
        pause_text = pause_font.render("PAUSED", True, (255, 255, 255))
        text_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(pause_text, text_rect)
        
        instruction_font = pygame.font.Font(None, 36)
        instruction_text = instruction_font.render("Press ESC to resume", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(self.width // 2, self.height // 2 + 60))
        self.screen.blit(instruction_text, instruction_rect)
    
    def draw_game_over_screen(self):

        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        game_over_font = pygame.font.Font(None, 72)
        game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(game_over_text, text_rect)
        
        stats_font = pygame.font.Font(None, 36)
        stats_text = stats_font.render(f"Final Score: {self.score} | Max Combo: {self.max_combo}", True, (255, 255, 255))
        stats_rect = stats_text.get_rect(center=(self.width // 2, self.height // 2 + 20))
        self.screen.blit(stats_text, stats_rect)
        
        instruction_font = pygame.font.Font(None, 24)
        instruction_text = instruction_font.render("Press ESC to return to menu", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(self.width // 2, self.height // 2 + 80))
        self.screen.blit(instruction_text, instruction_rect)
    
    def draw_completed_screen(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        complete_font = pygame.font.Font(None, 72)
        complete_text = complete_font.render("SONG COMPLETED!", True, (0, 255, 0))
        text_rect = complete_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(complete_text, text_rect)
        
        stats_font = pygame.font.Font(None, 36)
        stats_text = stats_font.render(f"Score: {self.score} | Accuracy: {self.accuracy:.1f}% | Max Combo: {self.max_combo}", True, (255, 255, 255))
        stats_rect = stats_text.get_rect(center=(self.width // 2, self.height // 2 + 20))
        self.screen.blit(stats_text, stats_rect)
        
        rating = self.calculate_rating()
        rating_font = pygame.font.Font(None, 48)
        rating_text = rating_font.render(f"Rating: {rating}", True, (255, 215, 0))
        rating_rect = rating_text.get_rect(center=(self.width // 2, self.height // 2 + 70))
        self.screen.blit(rating_text, rating_rect)
    
    def calculate_rating(self):
        if self.accuracy >= 95:
            return "S"
        elif self.accuracy >= 90:
            return "A"
        elif self.accuracy >= 80:
            return "B"
        elif self.accuracy >= 70:
            return "C"
        else:
            return "D"
    
    def cleanup(self):
        self.audio_manager.stop_music()
        self.audio_manager.cleanup()
    
    def run(self):
        raise NotImplementedError("Cada semana debe implementar run()")
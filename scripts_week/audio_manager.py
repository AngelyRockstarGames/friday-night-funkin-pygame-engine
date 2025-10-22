import pygame
import os
from enum import Enum

class MusicState(Enum):
    STOPPED = 0
    PLAYING = 1
    PAUSED = 2

class AudioManager:
    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        self.current_music = None
        self.music_volume = 0.7
        self.sound_volume = 0.8
        self.music_state = MusicState.STOPPED
        self.loaded_sounds = {}
        
        pygame.mixer.music.set_volume(self.music_volume)
        
    def play_music(self, filepath, loop=-1, fade_in=0):
        try:
            if os.path.exists(filepath):
                if self.current_music != filepath:
                    pygame.mixer.music.load(filepath)
                    self.current_music = filepath
                
                if fade_in > 0:
                    pygame.mixer.music.play(loop, fade_ms=fade_in)
                else:
                    pygame.mixer.music.play(loop)
                
                self.music_state = MusicState.PLAYING
                print(f"Reproduciendo música: {filepath}")
                return True
            else:
                print(f"Archivo de música no encontrado: {filepath}")
                return False
                
        except Exception as e:
            print(f"Error reproduciendo música {filepath}: {e}")
            return False
    
    def stop_music(self, fade_out=0):
        try:
            if fade_out > 0:
                pygame.mixer.music.fadeout(fade_out)
            else:
                pygame.mixer.music.stop()
            
            self.music_state = MusicState.STOPPED
            self.current_music = None
            print("Música detenida")
            
        except Exception as e:
            print(f"Error deteniendo música: {e}")
    
    def pause_music(self):
        try:
            pygame.mixer.music.pause()
            self.music_state = MusicState.PAUSED
        except Exception as e:
            print(f"Error pausando música: {e}")
    
    def resume_music(self):
        try:
            pygame.mixer.music.unpause()
            self.music_state = MusicState.PLAYING
        except Exception as e:
            print(f"Error reanudando música: {e}")
    
    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sound_volume(self, volume):
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.loaded_sounds.values():
            sound.set_volume(self.sound_volume)
    
    def preload_sounds(self, sound_dict):
        for key, filepath in sound_dict.items():
            try:
                if os.path.exists(filepath):
                    sound = pygame.mixer.Sound(filepath)
                    sound.set_volume(self.sound_volume)
                    self.loaded_sounds[key] = sound
                    print(f"Sonido preload: {key} -> {filepath}")
                else:
                    print(f"Archivo de sonido no encontrado: {filepath}")
                    
            except Exception as e:
                print(f"Error cargando sonido {filepath}: {e}")
    
    def play_sound(self, sound_key, volume=None):
        try:
            if sound_key in self.loaded_sounds:
                sound = self.loaded_sounds[sound_key]
                if volume is not None:
                    original_volume = sound.get_volume()
                    sound.set_volume(min(volume, self.sound_volume))
                    sound.play()
                    sound.set_volume(original_volume)
                else:
                    sound.play()
                return True
            else:
                print(f"Sonido no encontrado: {sound_key}")
                return False
                
        except Exception as e:
            print(f"Error reproduciendo sonido {sound_key}: {e}")
            return False
    
    def get_current_music(self):

        return self.current_music
    
    def is_music_playing(self):
        return self.music_state == MusicState.PLAYING
    
    def is_music_paused(self):
        return self.music_state == MusicState.PAUSED
    
    def cleanup(self):
        try:
            self.stop_music()
            for sound in self.loaded_sounds.values():
                sound.stop()
            self.loaded_sounds.clear()
        except Exception as e:
            print(f"Error en cleanup: {e}")

week_audio_manager = AudioManager()
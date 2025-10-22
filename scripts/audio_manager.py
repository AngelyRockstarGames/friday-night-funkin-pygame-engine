import pygame
import os
import json
import time
import threading
from typing import Dict, List, Optional, Callable, Tuple
from enum import Enum
from dataclasses import dataclass

class AudioState(Enum):
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    FADING = "fading"

@dataclass
class SoundInstance:
    sound: pygame.mixer.Sound
    channel: Optional[pygame.mixer.Channel]
    volume: float
    pan: float
    loop: bool
    start_time: float

class AudioManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AudioManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        try:
            pygame.mixer.init(
                frequency=44100,
                size=-16,
                channels=2,
                buffer=1024
            )
            pygame.mixer.set_num_channels(16)
        except pygame.error as e:
            print(f"AudioManager Error: {e}")
            try:
                pygame.mixer.init()
            except pygame.error as e2:
                print(f"AudioManager Critical Error: {e2}")
                return
        
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.master_volume = 1.0
        
        self.current_music = None
        self.music_state = AudioState.STOPPED
        self.music_fade_thread = None
        self.music_start_time = 0
        
        self.sound_instances: Dict[str, SoundInstance] = {}
        self.loaded_sounds: Dict[str, pygame.mixer.Sound] = {}
        
        self.config = self.load_config()
        self._initialized = True
    
    def load_config(self) -> Dict:
        config_path = "config/audio_config.json"
        default_config = {
            "music_volume": 0.7,
            "sfx_volume": 0.8,
            "master_volume": 1.0,
            "preload_sounds": True,
            "audio_latency": 100,
            "max_simultaneous_sounds": 8,
            "default_fade_duration": 1000
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    return {**default_config, **loaded_config}
        except Exception as e:
            print(f"AudioManager Config Error: {e}")
        
        return default_config
    
    def _find_sound_file(self, sound_name: str) -> Optional[str]:
        possible_paths = [
            f"audio/sfx/{sound_name}.ogg",
            f"assets/sounds/{sound_name}.ogg",
            f"sounds/{sound_name}.ogg",
            f"{sound_name}.ogg"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def load_sound(self, sound_name: str) -> Optional[pygame.mixer.Sound]:
        if sound_name in self.loaded_sounds:
            return self.loaded_sounds[sound_name]
        
        sound_path = self._find_sound_file(sound_name)
        if not sound_path:
            print(f"AudioManager: Sound file not found: {sound_name}")
            return None
        
        try:
            sound = pygame.mixer.Sound(sound_path)
            self.loaded_sounds[sound_name] = sound
            return sound
        except pygame.error as e:
            print(f"AudioManager: Error loading sound {sound_name}: {e}")
            return None
    
    def preload_sounds(self, sound_dict: Dict[str, str]):
        if not self.config.get("preload_sounds", True):
            return
            
        for name, path in sound_dict.items():
            if os.path.exists(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    self.loaded_sounds[name] = sound
                except Exception as e:
                    print(f"AudioManager: Error loading sound {name}: {e}")
            else:
                print(f"AudioManager: File not found: {path}")
    
    def play_music(self, music_path: str, fade_in: int = 0, loop: bool = True):
        if not os.path.exists(music_path):
            print(f"AudioManager: Music file not found: {music_path}")
            return
        
        if self.current_music == music_path and self.music_state == AudioState.PLAYING:
            return
        
        try:
            if self.music_fade_thread and self.music_fade_thread.is_alive():
                self.music_fade_thread.join(timeout=0.1)
            
            if self.music_state != AudioState.STOPPED:
                pygame.mixer.music.stop()
            
            pygame.mixer.music.load(music_path)
            
            if fade_in > 0:
                self.music_state = AudioState.FADING
                pygame.mixer.music.set_volume(0.0)
                pygame.mixer.music.play(-1 if loop else 0)
                
                self.music_fade_thread = threading.Thread(
                    target=self._fade_music_volume, 
                    args=(0.0, self.music_volume * self.master_volume, fade_in, False)
                )
                self.music_fade_thread.daemon = True
                self.music_fade_thread.start()
            else:
                pygame.mixer.music.play(-1 if loop else 0)
                pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
                self.music_state = AudioState.PLAYING
            
            self.current_music = music_path
            self.music_start_time = time.time()
            
        except pygame.error as e:
            print(f"AudioManager: Error playing music: {e}")
        except Exception as e:
            print(f"AudioManager: Unexpected error: {e}")
    
    def stop_music(self, fade_out: int = 0):
        if self.music_state == AudioState.STOPPED:
            return
            
        fade_duration = fade_out if fade_out > 0 else self.config.get("default_fade_duration", 1000)
        
        if fade_duration > 0:
            self.music_state = AudioState.FADING
            current_volume = pygame.mixer.music.get_volume()
            self.music_fade_thread = threading.Thread(
                target=self._fade_music_volume,
                args=(current_volume, 0.0, fade_duration, True)
            )
            self.music_fade_thread.daemon = True
            self.music_fade_thread.start()
        else:
            pygame.mixer.music.stop()
            self.music_state = AudioState.STOPPED
            self.current_music = None
    
    def pause_music(self):
        if self.music_state == AudioState.PLAYING:
            pygame.mixer.music.pause()
            self.music_state = AudioState.PAUSED
    
    def resume_music(self):
        if self.music_state == AudioState.PAUSED:
            pygame.mixer.music.unpause()
            self.music_state = AudioState.PLAYING
    
    def play_sound(self, sound_name: str, volume: float = 1.0, pan: float = 0.0, loop: bool = False) -> Optional[str]:
        instance_id = f"{sound_name}_{int(time.time() * 1000)}"
        
        sound = self.load_sound(sound_name)
        if sound is None:
            return None
        
        channel = pygame.mixer.find_channel()
        if channel is None:
            channel = self._find_stoppable_channel()
            if channel is None:
                return None
        
        final_volume = volume * self.sfx_volume * self.master_volume
        sound.set_volume(final_volume)
        
        self._set_channel_pan(channel, pan, final_volume)
        
        if loop:
            channel.play(sound, loops=-1)
        else:
            channel.play(sound)
        
        self.sound_instances[instance_id] = SoundInstance(
            sound=sound,
            channel=channel,
            volume=final_volume,
            pan=pan,
            loop=loop,
            start_time=time.time()
        )
        
        return instance_id
    
    def _find_stoppable_channel(self) -> Optional[pygame.mixer.Channel]:
        for instance in self.sound_instances.values():
            if (instance.channel and instance.channel.get_busy() and 
                not instance.loop and 
                (time.time() - instance.start_time) > 2.0):
                instance.channel.stop()
                return instance.channel
        return None
    
    def _set_channel_pan(self, channel: pygame.mixer.Channel, pan: float, volume: float):
        left_volume = volume * (1.0 - max(0, pan))
        right_volume = volume * (1.0 - max(0, -pan))
        
        try:
            channel.set_volume(left_volume, right_volume)
        except TypeError:
            channel.set_volume((left_volume + right_volume) / 2)
    
    def stop_sound(self, instance_id: str):
        if instance_id in self.sound_instances:
            instance = self.sound_instances[instance_id]
            if instance.channel and instance.channel.get_busy():
                instance.channel.stop()
            del self.sound_instances[instance_id]
    
    def stop_all_sounds(self):
        for instance_id in list(self.sound_instances.keys()):
            self.stop_sound(instance_id)
    
    def set_music_volume(self, volume: float):
        self.music_volume = max(0.0, min(1.0, volume))
        self.config["music_volume"] = self.music_volume
        
        if self.music_state == AudioState.PLAYING:
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
    
    def set_sfx_volume(self, volume: float):
        self.sfx_volume = max(0.0, min(1.0, volume))
        self.config["sfx_volume"] = self.sfx_volume
        
        for instance in self.sound_instances.values():
            if instance.channel and instance.channel.get_busy():
                final_volume = instance.volume * (self.sfx_volume / 0.8) * self.master_volume
                instance.sound.set_volume(final_volume)
                self._set_channel_pan(instance.channel, instance.pan, final_volume)
    
    def set_master_volume(self, volume: float):
        self.master_volume = max(0.0, min(1.0, volume))
        self.config["master_volume"] = self.master_volume
        self.set_music_volume(self.music_volume)
        self.set_sfx_volume(self.sfx_volume)
    
    def _fade_music_volume(self, start_vol: float, end_vol: float, duration: int, stop_after: bool = False):
        steps = max(1, int(duration / 50))
        step_duration = duration / steps
        
        for i in range(steps + 1):
            progress = i / steps
            current_vol = start_vol + (end_vol - start_vol) * progress
            try:
                pygame.mixer.music.set_volume(current_vol)
                time.sleep(step_duration / 1000)
            except Exception as e:
                break
        
        if stop_after:
            try:
                pygame.mixer.music.stop()
                self.music_state = AudioState.STOPPED
                self.current_music = None
            except Exception as e:
                print(f"AudioManager: Error stopping music: {e}")
        else:
            self.music_state = AudioState.PLAYING
    
    def get_music_position(self) -> float:
        if self.music_state == AudioState.PLAYING:
            return pygame.mixer.music.get_pos() / 1000.0
        return 0.0
    
    def get_audio_levels(self) -> Tuple[float, float]:
        if self.music_state == AudioState.PLAYING:
            t = time.time() - self.music_start_time
            left = abs((t * 2) % 1 - 0.5) * 2
            right = abs((t * 2.3) % 1 - 0.5) * 2
            return min(1.0, left * 0.8), min(1.0, right * 0.8)
        return 0.0, 0.0
    
    def is_music_playing(self) -> bool:
        return self.music_state == AudioState.PLAYING
    
    def is_music_paused(self) -> bool:
        return self.music_state == AudioState.PAUSED
    
    def get_current_music(self) -> Optional[str]:
        return self.current_music
    
    def cleanup(self):
        try:
            pygame.mixer.music.stop()
            for instance in self.sound_instances.values():
                if instance.channel and instance.channel.get_busy():
                    instance.channel.stop()
            self.sound_instances.clear()
            self.loaded_sounds.clear()
            if self.music_fade_thread and self.music_fade_thread.is_alive():
                self.music_fade_thread.join(timeout=0.5)
            self.save_config()
        except Exception as e:
            print(f"AudioManager: Cleanup error: {e}")
    
    def save_config(self):
        config_path = "config/audio_config.json"
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"AudioManager: Error saving config: {e}")
    
    def __del__(self):
        self.cleanup()
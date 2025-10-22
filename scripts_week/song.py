import pygame
import json
import os
from .note import Note

class Song:
    def __init__(self, name, bpm, notes_data, speed=1.0, needs_voicing=False):
        self.name = name
        self.bpm = bpm
        self.speed = speed
        self.notes_data = notes_data
        self.needs_voicing = needs_voicing
        

        self.current_time = 0
        self.playing = False
        self.completed = False
        
        self.beat_duration = 60.0 / bpm 
        self.step_duration = self.beat_duration / 4  # 16th notes
        self.measures = []
        
        self.all_notes = []
        self.processed_notes = set()
        
        self.total_notes = 0
        self.duration = 0

        self.process_song_data()
    
    def process_song_data(self):
        self.all_notes = []
        max_time = 0
        
        for section_index, section in enumerate(self.notes_data):
            must_hit_section = section.get("mustHitSection", True)
            section_notes = section.get("sectionNotes", [])
            section_bpm = section.get("bpm", self.bpm)
            section_change_bpm = section.get("changeBPM", False)
            
            for note_data in section_notes:
                time_ms = note_data[0]
                direction = note_data[1]
                length_ms = note_data[2] if len(note_data) > 2 else 0
                
                time_seconds = time_ms / 1000.0
                
                note = Note(
                    direction=direction,
                    time=time_seconds,
                    must_hit=must_hit_section,
                    length=length_ms
                )
                
                note.speed = self.speed
                self.all_notes.append(note)
                
                note_end_time = time_seconds + (length_ms / 1000.0) if length_ms > 0 else time_seconds
                max_time = max(max_time, note_end_time)
        
        self.all_notes.sort(key=lambda note: note.time)
        self.total_notes = len(self.all_notes)
        self.duration = max_time
        
        print(f"Canción '{self.name}' procesada: {self.total_notes} notas, duración: {self.duration:.2f}s")
    
    def start(self):
        self.current_time = 0
        self.playing = True
        self.completed = False
        self.processed_notes.clear()
        
        for note in self.all_notes:
            note.active = True
            note.hit = False
            note.missed = False
            note.showing_confirm = False
    
    def update(self, dt):
        if self.playing:
            self.current_time += dt
            
            if self.current_time >= self.duration + 2.0:  
                self.completed = True
                self.playing = False
    
    def get_current_notes(self, lookahead_time=2.0):
        current_notes = []
        

            if (note.time >= self.current_time and 
                note.time <= self.current_time + lookahead_time and
                note.active and not note.hit and not note.missed):
                current_notes.append(note)
        
        return current_notes
    
    def get_notes_for_spawning(self, lookahead_time=2.0):
        notes_to_spawn = []
        
        for note in self.all_notes:
            note_id = f"{note.time}_{note.direction}_{note.must_hit}"
            
            if (note.time >= self.current_time and 
                note.time <= self.current_time + lookahead_time and
                note_id not in self.processed_notes):
                
                notes_to_spawn.append(note)
                self.processed_notes.add(note_id)
        
        return notes_to_spawn
    
    def get_beat_time(self, beat_number):

        return beat_number * self.beat_duration
    
    def get_measure_time(self, measure_number):
        return measure_number * self.beat_duration * 4
    

        return int(self.current_time / self.beat_duration)
    
    def get_current_measure(self):

        return int(self.current_time / (self.beat_duration * 4))
    
    def get_beat_progress(self):

        current_beat = self.current_time / self.beat_duration
        return current_beat - int(current_beat)
    
    def get_measure_progress(self):

        current_measure = self.current_time / (self.beat_duration * 4)
        return current_measure - int(current_measure)
    
    def get_progress(self):

        if self.duration == 0:
            return 0
        return min(self.current_time / self.duration, 1.0)
    
    def get_notes_count(self):
 
        total = len(self.all_notes)
        player_notes = sum(1 for note in self.all_notes if note.must_hit)
        opponent_notes = total - player_notes
        
        return {
            "total": total,
            "player": player_notes,
            "opponent": opponent_notes,
            "duration": self.duration
        }
    
    def get_section_at_time(self, time):
        accumulated_time = 0
        for section in self.notes_data:
            section_notes = section.get("sectionNotes", [])
            if section_notes:
                section_duration = (max(note[0] for note in section_notes) - min(note[0] for note in section_notes)) / 1000.0
            else:
                section_duration = 4 * self.beat_duration  
            
            if accumulated_time <= time < accumulated_time + section_duration:
                return section
            
            accumulated_time += section_duration
        
        return None
    
    def stop(self):

        self.playing = False
    
    def pause(self):

        self.playing = False
    
    def resume(self):

        self.playing = True
    
    def is_playing(self):
        return self.playing
    
    def is_completed(self):
        return self.completed
    
    @classmethod
    def from_json_file(cls, json_path, speed=1.0):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                song_data = json.load(f)
            
            song_info = song_data["song"]
            return cls(
                name=song_info.get("song", "Unknown"),
                bpm=song_info.get("bpm", 100),
                notes_data=song_info.get("notes", []),
                speed=speed,
                needs_voicing=song_info.get("needsVoicing", False)
            )
        except Exception as e:
            print(f"Error cargando canción desde {json_path}: {e}")
            return cls.create_default_song()
    
    @classmethod
    def create_default_song(cls):
        default_notes = [
            {
                "mustHitSection": True, 
                "sectionNotes": [
                    [480, 0, 0], [720, 1, 0], [960, 2, 0], [1200, 3, 0],
                    [1440, 0, 0], [1680, 1, 0], [1920, 2, 0], [2160, 3, 0]
                ]
            },
            {
                "mustHitSection": False, 
                "sectionNotes": [
                    [2640, 0, 0], [2880, 1, 0], [3120, 2, 0], [3360, 3, 0],
                    [3600, 0, 0], [3840, 1, 0], [4080, 2, 0], [4320, 3, 0]
                ]
            }
        ]
        
        return cls(
            name="Default Song",
            bpm=100,
            notes_data=default_notes,
            speed=1.0
        )
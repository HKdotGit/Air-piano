import os
import pygame

class AudioEngine:
    def __init__(self):
        # We use pygame.mixer exclusively to avoid C++ build errors 
        # from older miniaudio/sounddevice modules on Python 3.14+
        if not pygame.mixer.get_init():
            # Init with low buffer for minimal latency
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            
        self.sounds = {}
        self.master_volume = 0.5
        
        print("Loading samples via Pygame API...")
        self.load_samples()
        
    def load_samples(self):
        notes = [
            "C3", "Cs3", "D3", "Ds3", "E3", "F3", 
            "Fs3", "G3", "Gs3", "A3", "As3", "B3",
            "C4", "Cs4", "D4", "Ds4", "E4", "F4", 
            "Fs4", "G4", "Gs4", "A4", "As4", "B4",
            "C5", "Cs5", "D5", "Ds5", "E5", "F5", 
            "Fs5", "G5", "Gs5", "A5", "As5", "B5"
        ]
        
        for i, note in enumerate(notes):
            path = f"assets/{note}.mp3"
            if os.path.exists(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    sound.set_volume(self.master_volume)
                    self.sounds[i] = sound
                    print(f"Loaded {note}")
                except Exception as e:
                    print(f"Failed to load {path}: {e}")
            else:
                pass # Silent ignore for missing assets to avoid huge logs

    def play_note(self, index):
        if index in self.sounds:
            # Play the cached Sound object
            self.sounds[index].play()

    def close(self):
        pygame.mixer.quit()

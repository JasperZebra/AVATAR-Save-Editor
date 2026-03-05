"""
Sound Manager for Avatar Save Editor
Handles background music and sound effects throughout the application
"""
import os
import logging
from pathlib import Path
from typing import Optional, Dict
import threading

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: pygame not installed. Sound features will be disabled.")
    print("Install with: pip install pygame")


class SoundManager:
    """Manages all sound playback for the application"""
    
    def __init__(self, enabled: bool = True, volume: float = 0.5):
        self.logger = logging.getLogger('SoundManager')
        self.enabled = enabled and PYGAME_AVAILABLE
        self._volume = volume
        self._bg_music_volume = volume * 0.6  # Background music quieter
        self._sfx_volume = volume
        
        # Sound effects cache
        self._sound_effects: Dict[str, any] = {}
        self._current_bg_music: Optional[str] = None
        
        # Initialize pygame mixer if available
        if self.enabled:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                pygame.mixer.music.set_volume(self._bg_music_volume)
                self.logger.info("Sound system initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize sound system: {e}")
                self.enabled = False
        
        # Define sound paths
        self.sounds_dir = Path("sounds")
        self.music_dir = self.sounds_dir / "music"
        self.sfx_dir = self.sounds_dir / "sfx"
        
        # Create directories if they don't exist
        self._create_sound_directories()
    
    def _create_sound_directories(self):
        """Create sound directories structure"""
        try:
            self.sounds_dir.mkdir(exist_ok=True)
            self.music_dir.mkdir(exist_ok=True)
            self.sfx_dir.mkdir(exist_ok=True)
            
            # Create a README
            readme_path = self.sounds_dir / "README.txt"
            if not readme_path.exists():
                with open(readme_path, 'w') as f:
                    f.write("Avatar Save Editor - Sound Files\n")
                    f.write("=" * 40 + "\n\n")
                    f.write("Place your sound files in these folders:\n\n")
                    f.write("music/\n")
                    f.write("  - version_selector.mp3/.ogg/.wav (version select screen music)\n")
                    f.write("  - main_editor.mp3/.ogg/.wav (main editor background music)\n\n")
                    f.write("sfx/\n")
                    f.write("  - click.wav or click.ogg (button click sound)\n")
                    f.write("  - hover.wav or hover.ogg (button hover sound)\n")
                    f.write("  - tab_switch.wav or tab_switch.ogg (tab change sound)\n")
                    f.write("  - success.wav or success.ogg (success notification)\n")
                    f.write("  - error.wav or error.ogg (error notification)\n\n")
                    f.write("Supported formats: .mp3, .ogg, .wav\n")
                    f.write("Recommended: Use .ogg for best compatibility\n")

        except Exception as e:
            self.logger.warning(f"Could not create sound directories: {e}")
    
    def _find_sound_file(self, base_name: str, directory: Path) -> Optional[Path]:
        """Find a sound file with various extensions"""
        extensions = ['.ogg', '.wav', '.mp3']
        for ext in extensions:
            sound_path = directory / f"{base_name}{ext}"
            if sound_path.exists():
                return sound_path
        return None
    
    def load_sound_effect(self, name: str) -> bool:
        """Load a sound effect into memory"""
        if not self.enabled:
            return False
        
        try:
            sound_path = self._find_sound_file(name, self.sfx_dir)
            if sound_path is None:
                self.logger.debug(f"Sound effect not found: {name}")
                return False
            
            sound = pygame.mixer.Sound(str(sound_path))
            sound.set_volume(self._sfx_volume)
            self._sound_effects[name] = sound
            self.logger.debug(f"Loaded sound effect: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load sound effect {name}: {e}")
            return False
    
    def play_sound_effect(self, name: str):
        """Play a sound effect"""
        if not self.enabled:
            return
        
        try:
            # Load if not already loaded
            if name not in self._sound_effects:
                if not self.load_sound_effect(name):
                    return
            
            # Play the sound
            sound = self._sound_effects.get(name)
            if sound:
                sound.play()
                
        except Exception as e:
            self.logger.error(f"Failed to play sound effect {name}: {e}")
    
    def play_background_music(self, music_name: str = "background", loop: bool = True):
        """Play background music"""
        if not self.enabled:
            return
        
        try:
            music_path = self._find_sound_file(music_name, self.music_dir)
            if music_path is None:
                self.logger.debug(f"Background music not found: {music_name}")
                return
            
            # Stop current music if playing
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            
            # Load and play new music
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.play(-1 if loop else 0)
            self._current_bg_music = music_name
            self.logger.info(f"Playing background music: {music_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to play background music: {e}")
    
    def stop_background_music(self):
        """Stop background music"""
        if not self.enabled:
            return
        
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(1000)  # 1 second fade out
                self._current_bg_music = None
                
        except Exception as e:
            self.logger.error(f"Failed to stop background music: {e}")
    
    def pause_background_music(self):
        """Pause background music"""
        if not self.enabled:
            return
        
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                
        except Exception as e:
            self.logger.error(f"Failed to pause background music: {e}")
    
    def resume_background_music(self):
        """Resume background music"""
        if not self.enabled:
            return
        
        try:
            pygame.mixer.music.unpause()
            
        except Exception as e:
            self.logger.error(f"Failed to resume background music: {e}")
    
    def set_volume(self, volume: float):
        """Set overall volume (0.0 to 1.0)"""
        self._volume = max(0.0, min(1.0, volume))
        self._bg_music_volume = self._volume * 0.6
        self._sfx_volume = self._volume
        
        if self.enabled:
            # Update music volume
            pygame.mixer.music.set_volume(self._bg_music_volume)
            
            # Update all loaded sound effects
            for sound in self._sound_effects.values():
                sound.set_volume(self._sfx_volume)
    
    def set_background_volume(self, volume: float):
        """Set background music volume specifically (0.0 to 1.0)"""
        self._bg_music_volume = max(0.0, min(1.0, volume))
        
        if self.enabled:
            pygame.mixer.music.set_volume(self._bg_music_volume)
    
    def set_sfx_volume(self, volume: float):
        """Set sound effects volume specifically (0.0 to 1.0)"""
        self._sfx_volume = max(0.0, min(1.0, volume))
        
        if self.enabled:
            for sound in self._sound_effects.values():
                sound.set_volume(self._sfx_volume)
    
    def toggle_enabled(self):
        """Toggle sound system on/off"""
        if not PYGAME_AVAILABLE:
            return False
        
        self.enabled = not self.enabled
        
        if not self.enabled:
            self.stop_background_music()
        else:
            # Restart background music if it was playing
            if self._current_bg_music:
                self.play_background_music(self._current_bg_music)
        
        return self.enabled
    
    def is_enabled(self) -> bool:
        """Check if sound system is enabled"""
        return self.enabled
    
    def cleanup(self):
        """Clean up sound resources"""
        if self.enabled:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                self.logger.info("Sound system cleaned up")
            except Exception as e:
                self.logger.error(f"Error during sound cleanup: {e}")


class SoundMixin:
    """Mixin class to add sound capabilities to widgets"""
    
    def __init__(self, *args, sound_manager: Optional[SoundManager] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.sound_manager = sound_manager
    
    def add_click_sound(self):
        """Add click sound to this widget"""
        if self.sound_manager:
            original_command = self.cget('command')
            
            def with_sound():
                self.sound_manager.play_sound_effect('click')
                if original_command:
                    original_command()
            
            self.configure(command=with_sound)
    
    def add_hover_sound(self):
        """Add hover sound to this widget"""
        if self.sound_manager:
            def on_enter(event):
                self.sound_manager.play_sound_effect('hover')
            
            self.bind('<Enter>', on_enter)
    
    def add_all_sounds(self):
        """Add both click and hover sounds"""
        self.add_click_sound()
        self.add_hover_sound()

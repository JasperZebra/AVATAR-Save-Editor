"""
Updated Settings Window with Sound Controls
"""
import os
import tkinter as tk
from tkinter import ttk
from custom_messagebox import show_success, show_error
import logging

class SettingsWindow:
    """Settings configuration window with sound controls"""
    
    def __init__(self, parent, config, save_callback, sound_manager=None):
        self.logger = logging.getLogger('SettingsWindow')
        self.parent = parent
        self.config = config
        self.save_callback = save_callback
        self.sound_manager = sound_manager
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("650x600")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()

        # Set icon
        icon_path = os.path.join("icon", "avatar_icon.ico")
        if os.path.exists(icon_path):
            try:
                self.window.iconbitmap(icon_path)
            except Exception as e:
                self.logger.warning(f"Failed to set window icon: {e}")

        # Apply dark theme
        self.window.configure(bg='#1e1e1e')
        
        # Center window
        self._center_window()
        
        # Create UI
        self._create_ui()
    
    def _center_window(self):
        """Center window on parent"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
    
    def _wrap_button_with_sound(self, button, command=None):
        """Wrap a button with click and hover sounds"""
        if command is None:
            command = button.cget('command')
        
        def sound_command():
            if self.sound_manager and hasattr(self.config, 'play_click_sounds'):
                if self.config.play_click_sounds:
                    self.sound_manager.play_sound_effect('click')
            if command:
                if callable(command):
                    command()
                else:
                    try:
                        button.tk.call(command)
                    except:
                        pass
        
        button.config(command=sound_command)
        
        # Add hover sound
        if self.sound_manager and hasattr(self.config, 'play_hover_sounds'):
            if self.config.play_hover_sounds:
                button.bind('<Enter>', lambda e: self.sound_manager.play_sound_effect('hover'))
        
        return button
    
    def _create_ui(self):
        """Create settings UI"""
        # Main container
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Settings", 
                                font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create notebook for categories
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # ADD TAB HOVER SOUND (only once per tab)
        self._last_hovered_settings_tab = None
        
        def on_settings_tab_hover(event):
            """Play hover sound when mouse enters a NEW tab"""
            if self.sound_manager and hasattr(self.config, 'play_hover_sounds'):
                if self.config.play_hover_sounds:
                    try:
                        tab_id = notebook.identify(event.x, event.y)
                        if tab_id and tab_id != self._last_hovered_settings_tab:
                            self._last_hovered_settings_tab = tab_id
                            self.sound_manager.play_sound_effect('hover')
                        elif not tab_id:
                            self._last_hovered_settings_tab = None
                    except:
                        pass
        
        notebook.bind('<Motion>', on_settings_tab_hover)
        
        # Sound tab (first priority!)
        sound_tab = ttk.Frame(notebook, padding=15)
        notebook.add(sound_tab, text="Sound")
        self._create_sound_settings(sound_tab)
        
        # Logging tab
        logging_tab = ttk.Frame(notebook, padding=15)
        notebook.add(logging_tab, text="Logging")
        self._create_logging_settings(logging_tab)
        
        # Backup tab
        backup_tab = ttk.Frame(notebook, padding=15)
        notebook.add(backup_tab, text="Backups")
        self._create_backup_settings(backup_tab)
        
        # Window tab
        window_tab = ttk.Frame(notebook, padding=15)
        notebook.add(window_tab, text="Window")
        self._create_window_settings(window_tab)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        save_btn = ttk.Button(button_frame, text="Save", width=15)
        self._wrap_button_with_sound(save_btn, self._save_settings)
        save_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", width=15)
        self._wrap_button_with_sound(cancel_btn, self.window.destroy)
        cancel_btn.pack(side=tk.LEFT)
        
        reset_btn = ttk.Button(button_frame, text="Reset to Defaults", width=20)
        self._wrap_button_with_sound(reset_btn, self._reset_defaults)
        reset_btn.pack(side=tk.RIGHT)
    
    def _create_sound_settings(self, parent):
        """Create sound settings section"""
        # Sound enabled checkbox
        self.sound_enabled_var = tk.BooleanVar(
            value=getattr(self.config, 'sound_enabled', True)
        )
        
        enable_check = ttk.Checkbutton(
            parent, 
            text="Enable sound effects and music", 
            variable=self.sound_enabled_var,
            command=self._on_sound_toggle
        )
        enable_check.pack(anchor=tk.W, pady=(0, 20))
        
        # Volume controls frame
        volume_frame = ttk.LabelFrame(parent, text="Volume Controls", padding=10)
        volume_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Master volume
        master_frame = ttk.Frame(volume_frame)
        master_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(master_frame, text="Master Volume:", 
                  font=('Segoe UI', 9, 'bold'), width=20).pack(side=tk.LEFT)
        
        self.master_volume_var = tk.DoubleVar(
            value=getattr(self.config, 'master_volume', 0.5) * 100
        )
        
        master_scale = ttk.Scale(
            master_frame, 
            from_=0, 
            to=100, 
            orient=tk.HORIZONTAL,
            variable=self.master_volume_var,
            command=self._on_master_volume_change
        )
        master_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.master_volume_label = ttk.Label(master_frame, text="50%", width=5)
        self.master_volume_label.pack(side=tk.LEFT)
        
        # Background music volume
        bg_frame = ttk.Frame(volume_frame)
        bg_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(bg_frame, text="Background Music:", 
                  font=('Segoe UI', 9, 'bold'), width=20).pack(side=tk.LEFT)
        
        self.bg_volume_var = tk.DoubleVar(
            value=getattr(self.config, 'bg_music_volume', 0.3) * 100
        )
        
        bg_scale = ttk.Scale(
            bg_frame, 
            from_=0, 
            to=100, 
            orient=tk.HORIZONTAL,
            variable=self.bg_volume_var,
            command=self._on_bg_volume_change
        )
        bg_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.bg_volume_label = ttk.Label(bg_frame, text="30%", width=5)
        self.bg_volume_label.pack(side=tk.LEFT)
        
        # Sound effects volume
        sfx_frame = ttk.Frame(volume_frame)
        sfx_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(sfx_frame, text="Sound Effects:", 
                  font=('Segoe UI', 9, 'bold'), width=20).pack(side=tk.LEFT)
        
        self.sfx_volume_var = tk.DoubleVar(
            value=getattr(self.config, 'sfx_volume', 0.5) * 100
        )
        
        sfx_scale = ttk.Scale(
            sfx_frame, 
            from_=0, 
            to=100, 
            orient=tk.HORIZONTAL,
            variable=self.sfx_volume_var,
            command=self._on_sfx_volume_change
        )
        sfx_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.sfx_volume_label = ttk.Label(sfx_frame, text="50%", width=5)
        self.sfx_volume_label.pack(side=tk.LEFT)
        
        # Sound options frame
        options_frame = ttk.LabelFrame(parent, text="Sound Options", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Background music checkbox
        self.bg_music_var = tk.BooleanVar(
            value=getattr(self.config, 'play_background_music', True)
        )
        ttk.Checkbutton(
            options_frame, 
            text="Play background music", 
            variable=self.bg_music_var
        ).pack(anchor=tk.W, pady=2)
        
        # Click sounds checkbox
        self.click_sounds_var = tk.BooleanVar(
            value=getattr(self.config, 'play_click_sounds', True)
        )
        ttk.Checkbutton(
            options_frame, 
            text="Button click sounds", 
            variable=self.click_sounds_var
        ).pack(anchor=tk.W, pady=2)
        
        # Hover sounds checkbox
        self.hover_sounds_var = tk.BooleanVar(
            value=getattr(self.config, 'play_hover_sounds', False)
        )
        ttk.Checkbutton(
            options_frame, 
            text="Button hover sounds", 
            variable=self.hover_sounds_var
        ).pack(anchor=tk.W, pady=2)
        
        # Tab switch sounds checkbox
        self.tab_sounds_var = tk.BooleanVar(
            value=getattr(self.config, 'play_tab_sounds', True)
        )
        ttk.Checkbutton(
            options_frame, 
            text="Tab switch sounds", 
            variable=self.tab_sounds_var
        ).pack(anchor=tk.W, pady=2)
        
        # Test sound button
        test_frame = ttk.Frame(parent)
        test_frame.pack(fill=tk.X, pady=(10, 0))
        
        test_click_btn = ttk.Button(test_frame, text="Test Click Sound")
        self._wrap_button_with_sound(test_click_btn, self._test_click_sound)
        test_click_btn.pack(side=tk.LEFT, padx=5)
        
        test_tab_btn = ttk.Button(test_frame, text="Test Tab Sound")
        self._wrap_button_with_sound(test_tab_btn, self._test_tab_sound)
        test_tab_btn.pack(side=tk.LEFT, padx=5)
        
        # Update initial label values
        self._update_volume_labels()
    
    def _on_sound_toggle(self):
        """Handle sound enable/disable toggle"""
        if self.sound_manager:
            if self.sound_enabled_var.get():
                self.sound_manager.enabled = True
                # Start background music if enabled
                if self.bg_music_var.get():
                    self.sound_manager.play_background_music("main_editor", loop=True)
            else:
                self.sound_manager.enabled = False
                self.sound_manager.stop_background_music()
    
    def _on_master_volume_change(self, value):
        """Handle master volume change"""
        volume = float(value) / 100.0
        if self.sound_manager:
            self.sound_manager.set_volume(volume)
        self._update_volume_labels()
    
    def _on_bg_volume_change(self, value):
        """Handle background music volume change"""
        volume = float(value) / 100.0
        if self.sound_manager:
            self.sound_manager.set_background_volume(volume)
        self._update_volume_labels()
    
    def _on_sfx_volume_change(self, value):
        """Handle sound effects volume change"""
        volume = float(value) / 100.0
        if self.sound_manager:
            self.sound_manager.set_sfx_volume(volume)
        self._update_volume_labels()
    
    def _update_volume_labels(self):
        """Update volume percentage labels"""
        self.master_volume_label.config(
            text=f"{int(self.master_volume_var.get())}%"
        )
        self.bg_volume_label.config(
            text=f"{int(self.bg_volume_var.get())}%"
        )
        self.sfx_volume_label.config(
            text=f"{int(self.sfx_volume_var.get())}%"
        )
    
    def _test_click_sound(self):
        """Test click sound"""
        if self.sound_manager:
            self.sound_manager.play_sound_effect('click')
    
    def _test_tab_sound(self):
        """Test tab switch sound"""
        if self.sound_manager:
            self.sound_manager.play_sound_effect('tab_switch')
    
    def _create_logging_settings(self, parent):
        """Create logging settings section"""
        # File logging
        self.file_logging_var = tk.BooleanVar(value=self.config.enable_file_logging)
        file_check = ttk.Checkbutton(parent, text="Enable file logging (save_editor.log)", 
                                      variable=self.file_logging_var)
        file_check.pack(anchor=tk.W, pady=5)
        
        # Console logging
        self.console_logging_var = tk.BooleanVar(value=self.config.enable_console_logging)
        console_check = ttk.Checkbutton(parent, text="Enable console logging", 
                                        variable=self.console_logging_var)
        console_check.pack(anchor=tk.W, pady=5)
        
        # Log level
        level_frame = ttk.Frame(parent)
        level_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(level_frame, text="Log Level:", 
                  font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        self.log_level_var = tk.StringVar(value=self.config.log_level)
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        level_combo = ttk.Combobox(level_frame, textvariable=self.log_level_var, 
                                    values=log_levels, state="readonly", width=15)
        level_combo.pack(side=tk.LEFT)
        
        # Help text
        help_text = ttk.Label(parent, text="Changes to logging settings require restart", 
                              foreground="orange", font=('Segoe UI', 8))
        help_text.pack(pady=(20, 0))
    
    def _create_backup_settings(self, parent):
        """Create backup settings section"""
        # Max backups
        max_frame = ttk.Frame(parent)
        max_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(max_frame, text="Max backups per character:", 
                  font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        self.max_backups_var = tk.StringVar(value=str(self.config.max_backups_per_character))
        max_entry = ttk.Entry(max_frame, textvariable=self.max_backups_var, width=10)
        max_entry.pack(side=tk.LEFT)
        
        # Backup folder
        folder_frame = ttk.Frame(parent)
        folder_frame.pack(fill=tk.X, pady=(15, 5))
        
        ttk.Label(folder_frame, text="Backup folder name:", 
                  font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        self.backup_folder_var = tk.StringVar(value=self.config.backup_root_folder)
        folder_entry = ttk.Entry(folder_frame, textvariable=self.backup_folder_var, width=30)
        folder_entry.pack(side=tk.LEFT)
        
        # Backup suffix
        suffix_frame = ttk.Frame(parent)
        suffix_frame.pack(fill=tk.X, pady=(15, 5))
        
        ttk.Label(suffix_frame, text="Simple backup suffix:", 
                  font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        self.backup_suffix_var = tk.StringVar(value=self.config.backup_suffix)
        suffix_entry = ttk.Entry(suffix_frame, textvariable=self.backup_suffix_var, width=15)
        suffix_entry.pack(side=tk.LEFT)
    
    def _create_window_settings(self, parent):
        """Create window settings section"""
        # Default geometry
        geom_frame = ttk.Frame(parent)
        geom_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(geom_frame, text="Default window size:", 
                  font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        self.geometry_var = tk.StringVar(value=self.config.window_geometry)
        geom_entry = ttk.Entry(geom_frame, textvariable=self.geometry_var, width=15)
        geom_entry.pack(side=tk.LEFT)
        
        ttk.Label(geom_frame, text="(e.g., 1366x768)", 
                  foreground="gray", font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=(10, 0))
        
        # Min size
        min_frame = ttk.Frame(parent)
        min_frame.pack(fill=tk.X, pady=(15, 5))
        
        ttk.Label(min_frame, text="Minimum window size:", 
                  font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        current_min = f"{self.config.min_window_size[0]},{self.config.min_window_size[1]}"
        self.min_size_var = tk.StringVar(value=current_min)
        min_entry = ttk.Entry(min_frame, textvariable=self.min_size_var, width=15)
        min_entry.pack(side=tk.LEFT)
        
        ttk.Label(min_frame, text="(e.g., 1366,768)", 
                  foreground="gray", font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=(10, 0))
        
        # Help text
        help_text = ttk.Label(parent, text="Window size changes require restart", 
                              foreground="orange", font=('Segoe UI', 8))
        help_text.pack(pady=(20, 0))
    
    def _save_settings(self):
        """Save settings and close window"""
        try:
            # Save sound settings
            self.config.sound_enabled = self.sound_enabled_var.get()
            self.config.master_volume = self.master_volume_var.get() / 100.0
            self.config.bg_music_volume = self.bg_volume_var.get() / 100.0
            self.config.sfx_volume = self.sfx_volume_var.get() / 100.0
            self.config.play_background_music = self.bg_music_var.get()
            self.config.play_click_sounds = self.click_sounds_var.get()
            self.config.play_hover_sounds = self.hover_sounds_var.get()
            self.config.play_tab_sounds = self.tab_sounds_var.get()
            
            # Validate and update other config
            self.config.enable_file_logging = self.file_logging_var.get()
            self.config.enable_console_logging = self.console_logging_var.get()
            self.config.log_level = self.log_level_var.get()
            
            # Validate max backups
            try:
                max_backups = int(self.max_backups_var.get())
                if max_backups < 1:
                    show_error("Invalid Value", "Max backups must be at least 1")
                    return
                self.config.max_backups_per_character = max_backups
            except ValueError:
                show_error("Invalid Value", "Max backups must be a number")
                return
            
            self.config.backup_root_folder = self.backup_folder_var.get()
            self.config.backup_suffix = self.backup_suffix_var.get()
            
            # Validate geometry
            geometry = self.geometry_var.get()
            if 'x' not in geometry:
                show_error("Invalid Format", "Window size must be in format: WIDTHxHEIGHT")
                return
            self.config.window_geometry = geometry
            
            # Validate min size
            try:
                min_size_parts = self.min_size_var.get().split(',')
                if len(min_size_parts) != 2:
                    raise ValueError()
                width, height = int(min_size_parts[0]), int(min_size_parts[1])
                if width < 800 or height < 600:
                    show_error("Invalid Size", "Minimum window size must be at least 800x600")
                    return
                self.config.min_window_size = (width, height)
            except ValueError:
                show_error("Invalid Format", "Minimum size must be in format: WIDTH,HEIGHT")
                return
            
            # Save to file
            self.config.save_to_file()
            
            # Call callback
            self.save_callback(self.config)
            
            # Close window
            self.window.destroy()
            
            show_success("Settings Saved", "Settings have been saved successfully!")
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}", exc_info=True)
            show_error("Error", f"Failed to save settings: {e}")
    
    def _reset_defaults(self):
        """Reset all settings to defaults"""
        self.window.grab_release()
        
        try:
            from custom_messagebox import ask_ok_cancel
            
            result = ask_ok_cancel("Reset Settings", "Are you sure you want to reset all settings to defaults?")
            
            if result:
                from main import SaveEditorConfig
                default_config = SaveEditorConfig()
                
                # Update sound UI
                self.sound_enabled_var.set(getattr(default_config, 'sound_enabled', True))
                self.master_volume_var.set(getattr(default_config, 'master_volume', 0.5) * 100)
                self.bg_volume_var.set(getattr(default_config, 'bg_music_volume', 0.3) * 100)
                self.sfx_volume_var.set(getattr(default_config, 'sfx_volume', 0.5) * 100)
                self.bg_music_var.set(getattr(default_config, 'play_background_music', True))
                self.click_sounds_var.set(getattr(default_config, 'play_click_sounds', True))
                self.hover_sounds_var.set(getattr(default_config, 'play_hover_sounds', False))
                self.tab_sounds_var.set(getattr(default_config, 'play_tab_sounds', True))
                
                # Update other UI
                self.file_logging_var.set(default_config.enable_file_logging)
                self.console_logging_var.set(default_config.enable_console_logging)
                self.log_level_var.set(default_config.log_level)
                self.max_backups_var.set(str(default_config.max_backups_per_character))
                self.backup_folder_var.set(default_config.backup_root_folder)
                self.backup_suffix_var.set(default_config.backup_suffix)
                self.geometry_var.set(default_config.window_geometry)
                self.min_size_var.set(f"{default_config.min_window_size[0]},{default_config.min_window_size[1]}")
                
                self._update_volume_labels()
        
        finally:
            if self.window.winfo_exists():
                self.window.grab_set()
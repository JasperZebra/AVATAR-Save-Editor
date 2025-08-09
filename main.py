"""
Avatar: The Game Save Editor
Made by: Jasper_Zebra
Version: 2.0

A modern, feature-rich save editor for Avatar: The Game across multiple platforms.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from typing import Optional, Dict, Any
import xml.etree.ElementTree as ET
import logging
from dataclasses import dataclass
from custom_messagebox import MessageBoxManager, show_info, show_error, show_warning, ask_question, ask_ok_cancel, show_success


# Import handlers and managers
from xml_handler import XMLHandler
from pc_xml_handler import PCXMLHandler
from ps3_xml_handler import PS3XMLHandler
from xml_viewer import XMLViewerWindow
from version_selector import VersionSelector

# Import all manager classes
from territory_manager import TerritoryManager
from stats_manager import StatsManager
from achievements_manager import AchievementsManager
from maps_manager import MapsManager
from checkpoints_manager import CheckpointsManager
from pandora_pedia_manager import PandoraPediaManager
from missions_manager import MissionsManager
from pins_manager import PinsManager
from sounds_manager import SoundsManager
from tutorial_manager import TutorialManager
from vehicle_manager import VehicleManager
from skills_manager import SkillsManager


@dataclass
class SaveEditorConfig:
    """Configuration settings for the Save Editor"""
    app_title: str = "Avatar: The Game Save Editor | Made by: Jasper_Zebra | Version 2.0"
    window_geometry: str = "1800x1100"
    icon_path: str = os.path.join("icon", "avatar_icon.ico")
    backup_suffix: str = ".backup"


class ThemeManager:
    """Manages the dark theme styling for the application"""
    
    @staticmethod
    def setup_dark_theme(root: tk.Tk) -> ttk.Style:
        """Configure comprehensive dark theme styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Color palette
        colors = {
            'background': '#1e1e1e',
            'foreground': '#ffffff', 
            'selected': '#1e1e1e',
            'active': '#2a7fff',
            'border': '#2a7fff',
            'input_bg': '#2c2c2c',
            'button_bg': "#252525",
            'button_pressed': '#1e1e1e',
            'error': '#ff6b6b',
            'tooltip_bg': '#4a4a4a',
        }
        
        # Global styles
        style.configure('.', **{
            'background': colors['background'],
            'foreground': colors['foreground'],
            'fieldbackground': colors['input_bg'],
            'troughcolor': colors['background'],
            'borderwidth': 1,
            'bordercolor': colors['border']
        })
        
        # Widget-specific styles
        widget_styles = {
            'TFrame': {'background': colors['background']},
            'TLabelframe': {'background': colors['background'], 'bordercolor': colors['border']},
            'TLabelframe.Label': {'background': colors['background'], 'foreground': colors['foreground']},
            'TLabel': {'background': colors['background'], 'foreground': colors['foreground']},
            'TCheckbutton': {'background': colors['background'], 'foreground': colors['foreground'], 'focuscolor': colors['active']},
            'TButton': {'background': colors['button_bg'], 'foreground': colors['foreground'], 'bordercolor': colors['border'], 'focuscolor': colors['active']},
            'TEntry': {'fieldbackground': colors['input_bg'], 'foreground': colors['foreground'], 'bordercolor': colors['border']},
            'TCombobox': {'fieldbackground': colors['input_bg'], 'background': colors['input_bg'], 'foreground': colors['foreground'], 'arrowcolor': colors['foreground'], 'bordercolor': colors['border']},
            'TNotebook': {'background': colors['background'], 'bordercolor': colors['border']},
            'TNotebook.Tab': {'background': colors['button_bg'], 'foreground': colors['foreground'], 'bordercolor': colors['border']},
            'Treeview': {'background': colors['input_bg'], 'foreground': colors['foreground'], 'fieldbackground': colors['input_bg']},
            'Treeview.Heading': {'background': colors['button_bg'], 'foreground': colors['foreground'], 'borderwidth': 1, 'bordercolor': colors['border']},
            'TScrollbar': {'background': colors['button_bg'], 'bordercolor': colors['border'], 'arrowcolor': colors['foreground'], 'troughcolor': colors['background']}
        }
        
        for widget, style_config in widget_styles.items():
            style.configure(widget, **style_config)
        
        # State-based styling
        style.map('TCheckbutton', background=[('active', colors['button_bg'])])
        style.map('TButton', background=[('pressed', colors['button_pressed']), ('active', colors['active'])])
        style.map('TCombobox', fieldbackground=[('readonly', colors['input_bg'])], background=[('active', colors['active']), ('pressed', colors['button_pressed']), ('readonly', colors['input_bg'])])
        style.map('TNotebook.Tab', background=[('selected', colors['active']), ('active', colors['active']), ('!selected', colors['button_bg'])])
        style.map('Treeview', background=[('selected', colors['active']), ('!selected', colors['input_bg']), ('active', colors['button_bg'])], foreground=[('selected', colors['foreground']), ('active', colors['foreground'])])
        style.map('Treeview.Heading', background=[('active', colors['active']), ('pressed', colors['button_pressed'])])
        style.map('TScrollbar', background=[('pressed', colors['button_pressed']), ('active', colors['active'])])
        
        # Root and text widget styling
        root.configure(bg=colors['background'])
        root.option_add('*TCombobox*Listbox.background', colors['input_bg'])
        root.option_add('*TCombobox*Listbox.foreground', colors['foreground'])
        root.option_add('*TCombobox*Listbox.selectBackground', colors['selected'])
        root.option_add('*TCombobox*Listbox.selectForeground', colors['foreground'])
        root.option_add('*Text*background', colors['input_bg'])
        root.option_add('*Text*foreground', colors['foreground'])
        root.option_add('*Text*selectBackground', colors['active'])
        root.option_add('*Text*selectForeground', colors['foreground'])
        
        return style


class FileOperations:
    """Handles file loading and saving operations"""
    
    def __init__(self, game_version: str):
        self.game_version = game_version
        self.logger = logging.getLogger(f'FileOperations.{game_version}')
        
        # Platform-specific handlers
        self.handlers = {
            'xbox': XMLHandler,
            'pc': PCXMLHandler, 
            'ps3': PS3XMLHandler
        }
    
    def get_file_types(self) -> list:
        """Get appropriate file types for file dialog"""
        base_types = [("All Save Files", "*.sav SAVEDATA.*")]
        
        if self.game_version in ['xbox', 'pc']:
            base_types.append(("Save Files", "*.sav"))
        elif self.game_version == 'ps3':
            base_types.append(("PS3 Save Files", "SAVEDATA.*"))
            
        return base_types
    
    def load_file(self, file_path: Path) -> tuple:
        """Load file using appropriate handler"""
        handler = self.handlers[self.game_version]
        
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Verify integrity
        is_valid = handler.verify_checksum(file_data)
        self.logger.debug(f"{self.game_version.upper()} integrity check: {is_valid}")
        
        # Load XML
        tree, xml_start, original_size = handler.load_xml_tree(file_path)
        
        return tree, xml_start, original_size, is_valid
    
    def save_file(self, tree: ET.ElementTree, file_path: Path) -> None:
        """Save file using appropriate handler"""
        handler = self.handlers[self.game_version]
        handler.save_xml_tree(tree, file_path)


class SaveEditor:
    """Main Save Editor application class"""
    
    def __init__(self, root: tk.Tk, game_version: str = "xbox"):
        self.logger = logging.getLogger('SaveEditor')
        self.config = SaveEditorConfig()
        
        # Core properties
        self.root = root
        self.game_version = game_version
        self.file_ops = FileOperations(game_version)
        
        # File state
        self.tree: Optional[ET.ElementTree] = None
        self.file_path: Optional[Path] = None
        self.original_size: Optional[int] = None
        self.xml_start: Optional[int] = None
        
        # UI components
        self.managers: Dict[str, Any] = {}
        
        self._initialize_application()
    
    def _initialize_application(self):
        """Initialize the complete application"""
        self.logger.debug("Initializing Save Editor application")
        
        try:
            self._setup_window()
            self._setup_theme()
            self._setup_ui()
            self._setup_event_handlers()
            
            self.logger.debug("Application initialization completed")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize application: {e}", exc_info=True)
            raise
    
    def _setup_window(self):
        """Configure main window properties"""
        self.root.title(self.config.app_title)
        self.root.geometry(self.config.window_geometry)
        
        # Set application icon
        try:
            if os.path.exists(self.config.icon_path):
                self.root.iconbitmap(self.config.icon_path)
                self.logger.debug(f"Icon set: {self.config.icon_path}")
        except Exception as e:
            self.logger.warning(f"Failed to set icon: {e}")
    
    def _setup_theme(self):
        """Setup application theme"""
        self.style = ThemeManager.setup_dark_theme(self.root)
    
    def _setup_ui(self):
        """Setup the user interface"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self._create_file_operations_section()
        self._create_tabbed_interface()
    
    def _setup_event_handlers(self):
        """Setup application event handlers"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_file_operations_section(self):
        """Create the file operations toolbar"""
        file_frame = ttk.LabelFrame(self.main_frame, text="File Operations", padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Left section - Action buttons
        self._create_action_buttons(file_frame)
        
        # Center section - File info
        self._create_file_info_section(file_frame)
        
        # Right section - Statistics and status
        self._create_status_section(file_frame)
    
    def _create_action_buttons(self, parent):
        """Create action buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(side=tk.LEFT)
        
        # Main action buttons
        buttons_config = [
            ("Load Save File", self.load_save_file, None),
            ("View XML", self.open_xml_viewer, None),
            ("Save Changes", self.save_changes, "disabled")
        ]
        
        self.action_buttons = {}
        for text, command, state in buttons_config:
            btn = ttk.Button(button_frame, text=text, command=command)
            if state:
                btn.config(state=state)
            btn.pack(side=tk.LEFT, padx=5)
            self.action_buttons[text.lower().replace(' ', '_')] = btn
    
    def _create_file_info_section(self, parent):
        """Create file information display section"""
        info_frame = ttk.Frame(parent)
        info_frame.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        
        self.file_label = ttk.Label(info_frame, text="No file loaded", wraplength=300)
        self.file_label.pack(side=tk.LEFT)
        
        self.unsaved_label = ttk.Label(info_frame, text="", foreground="red")
        self.unsaved_label.pack(side=tk.LEFT, padx=(10, 0))
    
    def _create_status_section(self, parent):
        """Create status and statistics section"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(side=tk.RIGHT)
        
        # Time statistics
        self._create_time_display(status_frame)
        
        # Checksum status
        self.checksum_label = ttk.Label(status_frame, text="Checksum: None", font=("", 9))
        self.checksum_label.pack(side=tk.RIGHT, padx=(20, 0))
    
    def _create_time_display(self, parent):
        """Create time statistics display"""
        time_frame = ttk.Frame(parent)
        time_frame.pack(side=tk.LEFT)
        
        time_row = ttk.Frame(time_frame)
        time_row.pack()
        
        self.time_labels = {}
        time_stats = ["Game Time", "Played Time", "Environment Time"]
        
        for i, stat in enumerate(time_stats):
            if i > 0:
                ttk.Label(time_row, text=" | ", font=("", 8)).pack(side=tk.LEFT)
            
            ttk.Label(time_row, text=f"{stat}:", font=("", 8)).pack(side=tk.LEFT)
            self.time_labels[stat] = ttk.Label(time_row, text="0h 00m 00s", font=("", 8))
            self.time_labels[stat].pack(side=tk.LEFT)
    
    def _create_tabbed_interface(self):
        """Create the main tabbed interface with all managers"""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab configuration: (tab_name, display_name, manager_class)
        tab_configs = [
            ("stats", "Player Stats", StatsManager),
            ("territory", "Territory Control", TerritoryManager),
            ("achievements", "Achievements", AchievementsManager),
            ("maps", "Maps", MapsManager),
            ("checkpoints", "Checkpoints", CheckpointsManager),
            ("pandora_pedia", "Pandora-Pedia", PandoraPediaManager),
            ("missions", "Missions", MissionsManager),
            ("pins", "Map Pins", PinsManager),
            ("sounds", "Sounds", SoundsManager),
            ("tutorial", "Tutorial Database", TutorialManager),
            ("vehicle", "Vehicle Knowledge", VehicleManager),
            ("skills", "Skills", SkillsManager)
        ]
        
        # Create tabs and managers
        for tab_key, display_name, manager_class in tab_configs:
            frame = ttk.Frame(self.notebook, padding=10)
            self.notebook.add(frame, text=display_name)
            
            # Initialize manager
            if manager_class in [StatsManager, TerritoryManager]:
                manager = manager_class(frame, main_window=self)
            else:
                manager = manager_class(frame, self)
            
            self.managers[tab_key] = manager
        
        self.logger.debug(f"Created {len(tab_configs)} tabs with managers")
    
    def update_time_display(self, time_values):
        """Update the time display in the main window"""
        try:
            self.logger.debug(f"Updating time display with values: {time_values}")
            
            # Format time values for display
            game_time = self._format_time_value(time_values.get("GameTime", "0"))
            played_time = self._format_time_value(time_values.get("PlayedTime", "0")) 
            env_time = self._format_time_value(time_values.get("EnvTime", "0"))
            
            # Update time labels (adjust these based on your actual UI structure)
            if hasattr(self, 'game_time_label'):
                self.game_time_label.config(text=game_time)
                
            if hasattr(self, 'played_time_label'):
                self.played_time_label.config(text=played_time)
                
            if hasattr(self, 'env_time_label'):
                self.env_time_label.config(text=env_time)
                
            # If you have a stats manager with time entries, update those too
            if hasattr(self, 'stats_manager') and self.stats_manager:
                stats_entries = self.stats_manager.entries
                
                if "GameTime" in stats_entries:
                    widget = stats_entries["GameTime"]
                    if hasattr(widget, 'config'):
                        widget.config(text=game_time)
                    else:
                        widget.delete(0, tk.END)
                        widget.insert(0, game_time)
                        
                if "PlayedTime" in stats_entries:
                    widget = stats_entries["PlayedTime"]
                    if hasattr(widget, 'config'):
                        widget.config(text=played_time)
                    else:
                        widget.delete(0, tk.END)
                        widget.insert(0, played_time)
                        
                if "EnvTime" in stats_entries:
                    widget = stats_entries["EnvTime"]
                    if hasattr(widget, 'config'):
                        widget.config(text=env_time)
                    else:
                        widget.delete(0, tk.END)
                        widget.insert(0, env_time)
            
            self.logger.debug("Time display updated successfully")
            
        except Exception as e:
            self.logger.error(f"Error updating time display: {str(e)}", exc_info=True)

    def _format_time_value(self, time_str):
        """Format time value for display"""
        try:
            # Convert to float first, then to int to handle decimal values
            time_seconds = int(float(time_str))
            
            # Convert seconds to hours, minutes, seconds
            hours = time_seconds // 3600
            minutes = (time_seconds % 3600) // 60
            seconds = time_seconds % 60
            
            if hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                return f"{minutes}m {seconds}s" 
            else:
                return f"{seconds}s"
                
        except (ValueError, TypeError):
            return time_str  # Return original if conversion fails
        
    
    
    def _update_checksum_display(self, is_valid: bool):
        """Update checksum verification display"""
        self.checksum_label.config(
            text=f"Checksum: {'Valid' if is_valid else 'Invalid'}",
            foreground="dark green" if is_valid else "red"
        )
    
    def _load_data_into_managers(self):
        """Load data into all managers"""
        manager_methods = {
            'stats': 'load_stats',
            'territory': 'load_territory_data',
            'achievements': 'load_achievements',
            'maps': 'load_maps_data',
            'checkpoints': 'load_checkpoints_data',
            'pandora_pedia': 'load_pandora_pedia',
            'missions': 'load_missions',
            'pins': 'load_pins',
            'sounds': 'load_sounds',
            'tutorial': 'load_tutorials',
            'vehicle': 'load_vehicles',
            'skills': 'load_skills'
        }
        
        for manager_key, method_name in manager_methods.items():
            try:
                manager = self.managers.get(manager_key)
                if manager and hasattr(manager, method_name):
                    method = getattr(manager, method_name)
                    method(self.tree)
            except Exception as e:
                self.logger.error(f"Error loading data for {manager_key}: {e}")
    
    def load_save_file(self):
        """Load a save file with comprehensive error handling"""
        self.logger.debug(f"Loading save file for {self.game_version}")
        
        # Check for unsaved changes
        if self._check_unsaved_changes():
            return
        
        try:
            # File selection
            file_path = filedialog.askopenfilename(filetypes=self.file_ops.get_file_types())
            if not file_path:
                return
            
            self.file_path = Path(file_path)
            self.file_label.config(text=self.file_path.name)
            
            # Load file
            self.tree, self.xml_start, self.original_size, is_valid = self.file_ops.load_file(self.file_path)
            
            # Update UI
            self._update_checksum_display(is_valid)
            self._load_data_into_managers()
            
            # Enable save functionality
            self.action_buttons['save_changes'].config(state="normal")
            self.unsaved_label.config(text="")
            
            self.logger.debug("Save file loaded successfully")
            show_success("Success", "Save file loaded successfully!")
            
        except Exception as e:
            self.logger.error(f"Failed to load save file: {e}", exc_info=True)
            show_error("Error", f"Failed to load save file: {e}")

    def _check_unsaved_changes(self) -> bool:
        """Check for unsaved changes and prompt user"""
        if self.unsaved_label.cget("text") == "Unsaved Changes":
            response = ask_question(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before loading a new file?"
            )
            
            if response is None:  # This won't happen with ask_question, but keeping for compatibility
                return True
            elif response:  # Yes, save changes
                self.save_changes()
        
        return False

    def open_xml_viewer(self):
        """Open XML viewer window"""
        if not self.tree:
            show_error("Error", "No save file loaded. Please load a save file first.")
            return
        
        try:
            xml_text = XMLHandler.get_pretty_xml(self.tree)
            XMLViewerWindow(self.root, xml_text=xml_text)
            self.logger.debug("XML viewer opened")
        except Exception as e:
            self.logger.error(f"Error opening XML viewer: {e}", exc_info=True)
            show_error("Error", f"Failed to open XML viewer: {e}")

    def save_changes(self):
        """Save all changes to file"""
        if not self.tree or not self.file_path:
            show_error("Error", "No save file loaded!")
            return
        
        try:
            # Create backup
            self._create_backup()
            
            # Process all manager updates
            self._process_manager_updates()
            
            # Save file
            self.file_ops.save_file(self.tree, self.file_path)
            
            # Update UI
            self.unsaved_label.config(text="")
            
            self.logger.debug("Changes saved successfully")
            show_success("Success", "Save file modified successfully!\nA backup has been created.")
            
        except ValueError as ve:
            self.logger.error(f"Save failed - size error: {ve}")
            show_error("Error", "Failed to save: The modified save data is too large.")
        except Exception as e:
            self.logger.error(f"Failed to save changes: {e}", exc_info=True)
            show_error("Error", f"Failed to save changes: {e}")

    def _on_close(self):
        """Handle application close event"""
        try:
            if self.unsaved_label.cget("text") == "Unsaved Changes":
                response = ask_question(
                    "Unsaved Changes",
                    "You have unsaved changes. Would you like to save before closing?"
                )
                
                if response is True:
                    self.save_changes()
                    self.root.destroy()
                else:  # False - don't save, just close
                    self.root.destroy()
                
            else:
                self.root.destroy()
                
        except Exception as e:
            self.logger.error(f"Error during close: {e}", exc_info=True)
            self.root.destroy()    
    
    def _create_backup(self):
        """Create backup of original file"""
        backup_path = self.file_path.with_suffix(self.file_path.suffix + self.config.backup_suffix)
        if not backup_path.exists():
            with open(self.file_path, 'rb') as src, open(backup_path, 'wb') as dst:
                dst.write(src.read())
            self.logger.debug(f"Backup created: {backup_path}")
    
    def _process_manager_updates(self):
        """Process updates from all managers"""
        # Get stats updates and apply to XML
        if 'stats' in self.managers:
            self._apply_stats_updates()
        
        # Save changes from all other managers
        save_methods = {
            'territory': 'save_territory_changes',
            'pandora_pedia': 'save_pandora_pedia_changes', 
            'achievements': 'save_achievement_changes',
            'missions': 'save_mission_changes',
            'pins': 'save_pin_changes',
            'sounds': 'save_sound_changes',
            'tutorial': 'save_tutorial_changes',
            'vehicle': 'save_vehicle_changes',
            'skills': 'save_skill_changes',
            'maps': 'save_maps_changes',
            'checkpoints': 'save_checkpoints_changes'
        }
        
        for manager_key, method_name in save_methods.items():
            try:
                manager = self.managers.get(manager_key)
                if manager and hasattr(manager, method_name):
                    method = getattr(manager, method_name)
                    result = method(self.tree)
                    if result is not None:  # Some methods return updated tree
                        self.tree = result
            except Exception as e:
                self.logger.error(f"Error saving {manager_key} changes: {e}")
    
    def _apply_stats_updates(self):
        """Apply statistics updates to XML tree - FIXED VERSION"""
        stats_manager = self.managers.get('stats')
        if not stats_manager:
            return
        
        try:
            root = self.tree.getroot()
            stats_updates = stats_manager.get_stats_updates()
            
            # Update PlayerProfile sections
            profile = root.find("PlayerProfile")
            if profile is None:
                profile = ET.SubElement(root, "PlayerProfile")
            
            # Update profile sections
            profile_sections = ["BaseInfo", "XpInfo", "OptionsInfo", "TimeInfo"]
            for section_name in profile_sections:
                if section_name in stats_updates and stats_updates[section_name]:
                    section = profile.find(section_name)
                    if section is None:
                        section = ET.SubElement(profile, section_name)
                    
                    for key, value in stats_updates[section_name].items():
                        section.set(key, str(value))
                        self.logger.debug(f"Updated {section_name}.{key} = {value}")
            
            # Update Metagame section (outside PlayerProfile)
            if "Metagame" in stats_updates and stats_updates["Metagame"]:
                metagame = root.find("Metagame")
                if metagame is None:
                    metagame = ET.SubElement(root, "Metagame")
                
                for key, value in stats_updates["Metagame"].items():
                    metagame.set(key, str(value))
                    self.logger.debug(f"Updated Metagame.{key} = {value}")
            
            # Update Player sections within Metagame
            metagame = root.find("Metagame")
            if metagame is not None:
                for player_section in ["Player0", "Player1"]:
                    if player_section in stats_updates and stats_updates[player_section]:
                        player = metagame.find(player_section)
                        if player is None:
                            player = ET.SubElement(metagame, player_section)
                        
                        for key, value in stats_updates[player_section].items():
                            player.set(key, str(value))
                            self.logger.debug(f"Updated {player_section}.{key} = {value}")
            
            # Update RecoveryBits in the correct location
            if "BaseInfo" in stats_updates and "RecoveryBits" in stats_updates["BaseInfo"]:
                # Also check if it should be in Possessions_Recovery
                recovery = profile.find("Possessions_Recovery")
                if recovery is not None:
                    recovery.set("RecoveryBits", stats_updates["BaseInfo"]["RecoveryBits"])
                    self.logger.debug(f"Updated Possessions_Recovery.RecoveryBits")
            
            self.logger.debug("Stats updates applied successfully")
            
        except Exception as e:
            self.logger.error(f"Error applying stats updates: {e}", exc_info=True)    

def setup_logging():
    """Configure application logging"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('save_editor.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


def main():
    """Main application entry point"""
    setup_logging()
    main_logger = logging.getLogger('Main')
    
    try:
        # Show version selection
        selector = VersionSelector()
        selector.show_selection_screen()
        selected_version = selector.selected_version
        
        # Clean up selector
        try:
            if selector.root and selector.root.winfo_exists():
                selector.root.destroy()
        except:
            pass
        
        # Check if version was selected
        if selected_version is None:
            main_logger.debug("No version selected, exiting")
            return
        
        main_logger.debug(f"Starting Save Editor for {selected_version}")
        
        # Create and run main application
        root = tk.Tk()
        app = SaveEditor(root, game_version=selected_version)
        root.mainloop()
        
    except Exception as e:
        main_logger.error(f"Application error: {e}", exc_info=True)
        if 'root' in locals():
            try:
                show_error("Critical Error", f"Application encountered a critical error:\n{e}")
            except:
                pass

if __name__ == "__main__":
    main()
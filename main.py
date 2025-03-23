import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
from pathlib import Path
from typing import Optional, Dict
import xml.etree.ElementTree as ET
import logging

from xml_handler import XMLHandler
from territory_manager import TerritoryManager
from stats_manager import StatsManager
from xml_viewer import XMLViewerWindow
from achievements_manager import AchievementsManager
from navigation_manager import NavigationManager
from pandora_pedia_manager import PandoraPediaManager
from version_selector import VersionSelector  
from pc_xml_handler import PCXMLHandler
from missions_manager import MissionsManager
from pins_manager import PinsManager
from sounds_manager import SoundsManager
from tutorial_manager import TutorialManager
from vehicle_manager import VehicleManager
from skills_manager import SkillsManager



# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('save_editor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def setup_dark_theme(root):
    """Configure dark theme styling for the application"""
    # Create a style object to manage themed widget appearances
    style = ttk.Style()
    
    # Use clam theme as base - this helps with styling control
    style.theme_use('clam')
    
    # Define a color palette for consistent dark mode theming
    colors = {
        'background': '#1e1e1e',       # Main background color (darkest grey)
        'foreground': '#ffffff',       # Primary text color (white)
        'selected': '#1e1e1e',         # Background color for selected items
        'active': '#2a7fff',           # Highlight color for active elements
        'border': '#2a7fff',           # Border color (nearly black)
        'input_bg': '#2c2c2c',         # Background for input fields (dark grey)
        'button_bg': '#3c3f41',        # Button background color
        'button_pressed': '#1e1e1e',   # Color when button is pressed
        'error': '#ff6b6b',            # Error/warning color (soft red)
        'tooltip_bg': '#4a4a4a',       # Tooltip background color
    }

    # CHECKBUTTON STYLING
    # Configure checkbox appearance
    style.configure('TCheckbutton',
        background=colors['background'],
        foreground=colors['foreground'],
        focuscolor=colors['active']
    )
    # Checkbutton state-based styling
    style.map('TCheckbutton',
        background=[('active', colors['button_bg'])],
        foreground=[('active', colors['foreground'])]
    )

    # GLOBAL STYLE CONFIGURATION
    # Set default styles for all ttk widgets
    style.configure('.',
        background=colors['background'],     # Default background
        foreground=colors['foreground'],     # Default text color
        fieldbackground=colors['input_bg'],  # Default field background
        troughcolor=colors['background'],    # Color for progress/scroll troughs
        borderwidth=1,                       # Default border width
        bordercolor=colors['border']         # Default border color
    )

    # FRAME STYLING
    # Configure standard frames
    style.configure('TFrame',
        background=colors['background']
    )

    # LABEL FRAME STYLING
    # Style for framed labels and their containers
    style.configure('TLabelframe',
        background=colors['background'],
        bordercolor=colors['border']
    )
    style.configure('TLabelframe.Label',
        background=colors['background'],
        foreground=colors['foreground']
    )

    # BUTTON STYLING
    # Configure button appearance and interaction states
    style.configure('TButton',
        background=colors['button_bg'],      # Button background
        foreground=colors['foreground'],     # Button text color
        bordercolor=colors['border'],        # Button border
        lightcolor=colors['button_bg'],      # Light shade of button
        darkcolor=colors['button_bg'],       # Dark shade of button
        focuscolor=colors['active']          # Color when button is focused
    )
    # Button state-based styling
    style.map('TButton',
        background=[('pressed', colors['button_pressed']), ('active', colors['active'])],
        foreground=[('pressed', colors['foreground']), ('active', colors['foreground'])]
    )

    # ENTRY FIELD STYLING
    # Configure text input fields
    style.configure('TEntry',
        fieldbackground=colors['input_bg'],  # Input field background
        foreground=colors['foreground'],     # Input text color
        bordercolor=colors['border']         # Input field border
    )

    # COMBOBOX (DROPDOWN) STYLING
    # Configure dropdown/select input fields
    style.configure('TCombobox',
        fieldbackground=colors['input_bg'],  # Dropdown background
        background=colors['input_bg'],       # Dropdown arrow background
        foreground=colors['foreground'],     # Dropdown text color
        arrowcolor=colors['foreground'],     # Dropdown arrow color
        bordercolor=colors['border']         # Dropdown border
    )
    # Combobox state-based styling
    style.map('TCombobox',
        fieldbackground=[('readonly', colors['input_bg'])],      # Background when read-only
        selectbackground=[('readonly', colors['selected'])],     # Selection background
        background=[
            ('active', colors['active']),                     # Arrow box background when hovered
            ('pressed', colors['button_pressed']),               # Arrow box background when pressed
            ('readonly', colors['input_bg'])                     # Arrow box background when readonly
        ]
    )

    # Additional styling to force dark background
    root.option_add('*TCombobox*Listbox.background', colors['input_bg'])
    root.option_add('*TCombobox*Listbox.foreground', colors['foreground'])
    root.option_add('*TCombobox*Listbox.selectBackground', colors['selected'])
    root.option_add('*TCombobox*Listbox.selectForeground', colors['foreground'])

    # LABEL STYLING
    # Configure standard labels
    style.configure('TLabel',
        background=colors['background'],
        foreground=colors['foreground']
    )

    # NOTEBOOK (TAB) STYLING
    # Configure notebook/tabbed interfaces
    style.configure('TNotebook',
        background=colors['background'],
        bordercolor=colors['border']
    )
    style.configure('TNotebook.Tab',
        background=colors['button_bg'],      # Tab background
        foreground=colors['foreground'],     # Tab text color
        lightcolor=colors['border'],         # Tab light border
        bordercolor=colors['border']         # Tab border
    )
    # Tab state-based styling
    style.map('TNotebook.Tab',
        background=[
            ('selected', colors['active']),      # Selected tab background
            ('active', colors['active']),     # Hover tab background
            ('!selected', colors['button_bg'])   # Normal tab background
        ],
        foreground=[
            ('selected', colors['foreground']),  # Selected tab text
            ('active', colors['foreground']),    # Hover tab text
            ('!selected', colors['foreground'])  # Normal tab text
        ]
    )

    # TREEVIEW STYLING
    # Configure list/tree view widgets
    style.configure('Treeview',
        background=colors['input_bg'],        # Treeview background
        foreground=colors['foreground'],      # Treeview text
        fieldbackground=colors['input_bg']    # Treeview field background
    )
    style.configure('Treeview.Heading',
        background=colors['button_bg'],       # Column headers background
        foreground=colors['foreground'],      # Column headers text
        borderwidth=1,
        bordercolor=colors['border']          # Column headers border
    )
    # Treeview state-based styling
    style.map('Treeview',
        background=[
            ('selected', colors['active']),      # Selected item background
            ('!selected', colors['input_bg']),   # Normal background
            ('active', colors['button_bg'])      # Hovered item background
        ],
        foreground=[
            ('selected', colors['foreground']),  # Selected item text
            ('active', colors['foreground'])     # Hovered item text
        ]
    )
    # Treeview Heading (column headers) state-based styling
    style.map('Treeview.Heading',
        background=[
            ('active', colors['active']),     # Header hover background
            ('pressed', colors['button_pressed']) # Header click background
        ]
    )

    # SCROLLBAR STYLING
    # Configure scrollbar appearance
    style.configure('TScrollbar',
        background=colors['button_bg'],       # Scrollbar background
        bordercolor=colors['border'],         # Scrollbar border
        arrowcolor=colors['foreground'],      # Scrollbar arrow color
        troughcolor=colors['background']      # Scrollbar trough color
    )
    # Scrollbar state-based styling
    style.map('TScrollbar',
        background=[('pressed', colors['button_pressed']), ('active', colors['active'])]
    )

    # ROOT WINDOW BACKGROUND
    # Set the overall application background
    root.configure(bg=colors['background'])

    # TEXT WIDGET SPECIFIC STYLING
    # Configure colors for text widgets (like XML viewer)
    root.option_add('*Text*background', colors['input_bg'])          # Text background
    root.option_add('*Text*foreground', colors['foreground'])        # Text color
    root.option_add('*Text*selectBackground', colors['active'])      # Text selection background
    root.option_add('*Text*selectForeground', colors['foreground'])  # Text selection foreground

    # Return the configured style object
    return style

class SaveEditor:
    def __init__(self, root: tk.Tk, game_version: str = "xbox") -> None:
        self.logger = logging.getLogger('SaveEditor')
        self.logger.debug("Initializing Save Editor")
        self.root = root
        self.game_version = game_version
        self.root.title("Avatar: The Game Save Editor | Version 1.1")
        self.root.geometry("1130x680")

        # Set the window icon
        try:
            icon_path = os.path.join("icon", "avatar_icon.ico")
            self.root.iconbitmap(icon_path)
            self.logger.debug(f"Application icon set successfully from path: {icon_path}")
        except Exception as e:
            self.logger.error(f"Failed to set application icon: {str(e)}")

        # Setup dark theme
        self.style = setup_dark_theme(self.root)
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.tree: Optional[ET.ElementTree] = None
        self.file_path: Optional[Path] = None
        self.original_size: Optional[int] = None
        self.xml_start: Optional[int] = None
        
        self.setup_ui()
        self.logger.debug("Save Editor initialization complete")
        
    def setup_ui(self):
        self.logger.debug("Setting up UI components")
        try:
            self.main_frame = ttk.Frame(self.root)
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            self._create_file_section()
            self._create_notebook()
            self.logger.debug("UI setup completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error setting up UI: {str(e)}", exc_info=True)
            raise

    def _create_file_section(self) -> None:
        self.logger.debug("Creating file operations section")
        try:
            file_frame = ttk.LabelFrame(self.main_frame, text="File Operations", padding=10)
            file_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Left side buttons
            button_frame = ttk.Frame(file_frame)
            button_frame.pack(side=tk.LEFT, padx=0)
            
            self.load_button = ttk.Button(
                button_frame, 
                text="Load Save File", 
                command=self.load_save
            )
            self.load_button.pack(side=tk.LEFT, padx=5)
            
            self.xml_viewer_button = ttk.Button(
                button_frame,
                text="View XML",
                command=self.open_xml_viewer
            )
            self.xml_viewer_button.pack(side=tk.LEFT, padx=5)
            
            self.save_button = ttk.Button(
                button_frame,
                text="Save Changes",
                command=self.save_changes,
                state="disabled"
            )
            self.save_button.pack(side=tk.LEFT, padx=5)
            
            # Middle frame for file labels
            label_frame = ttk.Frame(file_frame)
            label_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

            self.file_label = ttk.Label(
                label_frame, 
                text="No file loaded", 
                wraplength=300
            )
            self.file_label.pack(side=tk.LEFT, padx=2)

            self.unsaved_label = ttk.Label(
                label_frame,
                text="",
                foreground="red"
            )
            self.unsaved_label.pack(side=tk.LEFT, padx=2)
            
            # Right side frame for time stats and checksum
            right_frame = ttk.Frame(file_frame)
            right_frame.pack(side=tk.RIGHT, padx=5)
            
            # Time stats frame - now horizontal
            time_stats_frame = ttk.Frame(right_frame)
            time_stats_frame.pack(side=tk.LEFT, padx=(0, 20))
            
            # Create time stat labels horizontally with smaller font
            self.time_labels = {}
            time_font = ("", 8)  # Smaller font size
            
            # Single frame for all time stats
            time_row = ttk.Frame(time_stats_frame)
            time_row.pack(fill=tk.X)
            
            # Add each time stat horizontally
            for i, stat in enumerate(["Game Time", "Played Time", "Environment Time"]):
                if i > 0:  # Add separator except for first item
                    ttk.Label(time_row, text=" | ", font=time_font).pack(side=tk.LEFT)
                    
                ttk.Label(time_row, text=f"{stat}:", font=time_font).pack(side=tk.LEFT)
                self.time_labels[stat] = ttk.Label(time_row, text="0h 00m 00s", font=time_font)
                self.time_labels[stat].pack(side=tk.LEFT)

            # Checksum label
            self.checksum_label = ttk.Label(
                right_frame,
                text="Checksum: None",
                font=("", 9)
            )
            self.checksum_label.pack(side=tk.RIGHT)

        except Exception as e:
            self.logger.error(f"Error creating file section: {str(e)}", exc_info=True)
            raise

    def open_xml_viewer(self):
        self.logger.debug("Opening XML viewer")
        try:
            if not self.tree:
                self.logger.warning("Attempted to open XML viewer with no file loaded")
                messagebox.showerror("Error", "No save file loaded. Please load a save file first.")
                return
            
            xml_text = XMLHandler.get_pretty_xml(self.tree)
            XMLViewerWindow(self.root, xml_text=xml_text)
            self.logger.debug("XML viewer opened successfully")
            
        except Exception as e:
            self.logger.error(f"Error opening XML viewer: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to open XML viewer: {str(e)}")

    def _create_notebook(self) -> None:
        self.logger.debug("Creating notebook tabs")
        try:
            self.notebook = ttk.Notebook(self.main_frame)
            self.notebook.pack(fill=tk.BOTH, expand=True)
            
            self.stats_frame = ttk.Frame(self.notebook, padding=10)
            self.territory_frame = ttk.Frame(self.notebook, padding=10)
            self.achievements_frame = ttk.Frame(self.notebook, padding=10)
            self.navigation_frame = ttk.Frame(self.notebook, padding=10)
            self.pandora_pedia_frame = ttk.Frame(self.notebook, padding=10) 
            self.missions_frame = ttk.Frame(self.notebook, padding=10) 
            self.pins_frame = ttk.Frame(self.notebook, padding=10)
            self.sounds_frame = ttk.Frame(self.notebook, padding=10)
            self.tutorial_frame = ttk.Frame(self.notebook, padding=10)
            self.vehicle_frame = ttk.Frame(self.notebook, padding=10)
            self.skills_frame = ttk.Frame(self.notebook, padding=10)

            self.notebook.add(self.stats_frame, text="Player Stats")
            self.notebook.add(self.territory_frame, text="Territory Control")
            self.notebook.add(self.achievements_frame, text="Achievements")
            self.notebook.add(self.navigation_frame, text="Navigation")
            self.notebook.add(self.pandora_pedia_frame, text="Pandora-Pedia") 
            self.notebook.add(self.missions_frame, text="Missions") 
            self.notebook.add(self.pins_frame, text="Map Pins")
            self.notebook.add(self.sounds_frame, text="Sounds")
            self.notebook.add(self.tutorial_frame, text="Tutorial Database")
            self.notebook.add(self.vehicle_frame, text="Vehicle Knowledge")
            self.notebook.add(self.skills_frame, text="Skills")

            self.stats_manager = StatsManager(self.stats_frame, self)
            self.territory_manager = TerritoryManager(self.territory_frame, main_window=self)
            self.achievements_manager = AchievementsManager(self.achievements_frame, self)
            self.navigation_manager = NavigationManager(self.navigation_frame, self)
            self.pandora_pedia_manager = PandoraPediaManager(self.pandora_pedia_frame, self)
            self.missions_manager = MissionsManager(self.missions_frame, self) 
            self.pins_manager = PinsManager(self.pins_frame, self)
            self.sounds_manager = SoundsManager(self.sounds_frame, self)
            self.tutorial_manager = TutorialManager(self.tutorial_frame, self)
            self.vehicle_manager = VehicleManager(self.vehicle_frame, self)
            self.skills_manager = SkillsManager(self.skills_frame, self)

            self.logger.debug("Notebook and manager instances created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating notebook: {str(e)}", exc_info=True)
            raise
        
    def load_save(self) -> None:
        """Load a save file with version-specific handling."""
        self.logger.debug(f"Loading save file for {self.game_version} version")
        
        # Check for unsaved changes
        if self.unsaved_label.cget("text") == "Unsaved Changes":
            response = messagebox.askyesnocancel(
                "Unsaved Changes", 
                "You have unsaved changes. Do you want to save before loading a new file?",
                icon="warning"
            )
            
            if response is None:  # Cancel
                return
            elif response is True:  # Yes, save changes
                self.save_changes()
        
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("Save Files", "*.sav")],
            )
            if not file_path:
                self.logger.debug("File selection cancelled")
                return
            
            self.file_path = Path(file_path)
            self.logger.debug(f"Selected file: {self.file_path}")
            self.file_label.config(text=self.file_path.name)

            # Read file and verify checksum before loading XML
            with open(self.file_path, 'rb') as f:
                file_data = f.read()
            
            # Select the appropriate handler based on game version
            if self.game_version == "xbox":
                # Xbox 360 version - use original handler
                self.logger.debug("Using Xbox 360 XML handler")
                is_valid = XMLHandler.verify_checksum(file_data)
                self.logger.debug(f"Xbox checksum verification result: {is_valid}")
                
                # Load XML using Xbox handler
                self.tree, self.xml_start, self.original_size = XMLHandler.load_xml_tree(self.file_path)
            else:
                # PC version - use PC-specific handler
                self.logger.debug("Using PC XML handler")
                # For PC version, we skip checksum verification
                is_valid = PCXMLHandler.verify_checksum(file_data)
                self.logger.debug("PC version - skipping checksum verification")
                
                # Load XML using PC handler
                try:
                    self.logger.debug("Attempting to load with PC handler")
                    self.tree, self.xml_start, self.original_size = PCXMLHandler.load_xml_tree(self.file_path)
                    self.logger.debug("PC save file parsed successfully")
                except Exception as pc_error:
                    self.logger.error(f"Failed to parse PC save file: {str(pc_error)}", exc_info=True)
                    # Fallback to Xbox loading method if PC parsing fails
                    self.logger.debug("Attempting fallback to Xbox loading method")
                    self.tree, self.xml_start, self.original_size = XMLHandler.load_xml_tree(self.file_path)
            
            # Update checksum verification display
            self.checksum_label.config(
                text=f"Checksum: {'Valid' if is_valid else 'Invalid'}", 
                foreground="dark green" if is_valid else "red"
            )
            
            # Load data into managers
            self.stats_manager.load_stats(self.tree)
            self.territory_manager.load_territory_data(self.tree)
            self.achievements_manager.load_achievements(self.tree)
            self.navigation_manager.load_navigation_data(self.tree)
            self.pandora_pedia_manager.load_pandora_pedia(self.tree)
            self.missions_manager.load_missions(self.tree)
            self.pins_manager.load_pins(self.tree)
            self.sounds_manager.load_sounds(self.tree)
            self.tutorial_manager.load_tutorials(self.tree)
            self.vehicle_manager.load_vehicles(self.tree)
            self.skills_manager.load_skills(self.tree)

            self.save_button.config(state="normal")
            self.unsaved_label.config(text="")
            self.logger.debug("Save file loaded successfully")
            messagebox.showinfo("Success", "Save file loaded successfully!")
        
        except Exception as e:
            self.logger.error(f"Failed to load save file: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to load save file: {str(e)}")

    def save_changes(self) -> None:
        """Save changes to file with version-specific handling."""
        self.logger.debug(f"Starting save changes operation for {self.game_version} version")
        if not self.tree or not self.file_path:
            self.logger.warning("Attempted to save with no file loaded")
            messagebox.showerror("Error", "No save file loaded!")
            return
                    
        try:            
            # Create a backup regardless of version
            backup_path = self.file_path.with_suffix(self.file_path.suffix + ".backup")
            if not backup_path.exists():
                with open(self.file_path, 'rb') as src, open(backup_path, 'wb') as dst:
                    dst.write(src.read())
                self.logger.debug(f"Created backup at {backup_path}")
            
            # Ensure the root element exists
            root = self.tree.getroot()
            if root is None:
                self.logger.error("XML tree root is None")
                raise ValueError("Invalid XML structure")

            # Create profile if it doesn't exist
            profile = root.find("PlayerProfile")
            if profile is None:
                profile = ET.SubElement(root, "PlayerProfile")
            
            # Get updates from each manager
            stats_updates = self.stats_manager.get_stats_updates()
            
            # Debug print for faction value
            if "Metagame" in stats_updates and "PlayerFaction" in stats_updates["Metagame"]:
                self.logger.debug(f"Faction value from stats_updates: {stats_updates['Metagame']['PlayerFaction']}")
            
            # Update sections with fallback creation
            sections = {
                "BaseInfo": stats_updates.get("BaseInfo", {}),
                "XpInfo": stats_updates.get("XpInfo", {}),
                "OptionsInfo": stats_updates.get("OptionsInfo", {}),
                "TimeInfo": stats_updates.get("TimeInfo", {})
            }
            
            for section_name, updates in sections.items():
                # Find or create the section
                section = profile.find(section_name)
                if section is None:
                    section = ET.SubElement(profile, section_name)
                
                # Update section attributes
                for key, value in updates.items():
                    section.set(key, str(value))
            
            # Process Equipment section specifically for PC version
            if self.game_version != "xbox":
                # Find or create Equipment section
                equipment = profile.find("Equipment")
                if equipment is None:
                    equipment = ET.SubElement(profile, "Equipment")
                
                # Make sure armor updates from stats_manager are applied
                if "Equipment" in stats_updates:
                    for key, value in stats_updates.get("Equipment", {}).items():
                        self.logger.debug(f"Setting equipment attribute: {key}={value}")
                        equipment.set(key, str(value))
                        
            # Update territories, Pandora-pedia entries, and achievements (unchanged)
            try:
                self.territory_manager.save_territory_changes(self.tree)
            except Exception as territory_error:
                self.logger.error(f"Error saving territory changes: {str(territory_error)}")
            
            try:
                self.pandora_pedia_manager.save_pandora_pedia_changes(self.tree)
            except Exception as pandora_pedia_error:
                self.logger.error(f"Error saving Pandora-Pedia changes: {str(pandora_pedia_error)}")
            
            try:
                self.achievements_manager.save_achievement_changes(self.tree)
            except Exception as achievement_error:
                self.logger.error(f"Error saving achievement changes: {str(achievement_error)}")

            try:
                self.missions_manager.save_mission_changes(self.tree)
            except Exception as missions_error:
                self.logger.error(f"Error saving missions changes: {str(missions_error)}")

            try:
                self.pins_manager.save_pin_changes(self.tree)
            except Exception as pins_error:
                self.logger.error(f"Error saving pins changes: {str(pins_error)}")

            try:
                self.sounds_manager.save_sound_changes(self.tree)
            except Exception as sounds_error:
                self.logger.error(f"Error saving sounds changes: {str(sounds_error)}")

            try:
                self.tutorial_manager.save_tutorial_changes(self.tree)
            except Exception as tutorial_error:
                self.logger.error(f"Error saving tutorial changes: {str(tutorial_error)}")

            try:
                self.tree = self.vehicle_manager.save_vehicle_changes(self.tree)
            except Exception as vehicle_error:
                self.logger.error(f"Error saving vehicle knowledge changes: {str(vehicle_error)}")

            try:
                self.tree = self.skills_manager.save_skill_changes(self.tree)
            except Exception as skills_error:
                self.logger.error(f"Error saving skills data: {str(skills_error)}")

            # Ensure faction is preserved
            self.stats_manager._ensure_faction_preserved()

            # Save file using the appropriate method based on version
            if self.game_version == "xbox":
                # Xbox 360 save format - with checksum handling
                self.logger.debug("Saving file using Xbox 360 format handler")
                XMLHandler.save_xml_tree(self.tree, self.file_path)
            else:
                # PC save format - direct XML save, but using XMLHandler for saving
                # This is the key change - use the Xbox handler's save method but with PC specifics
                self.logger.debug("Saving file using hybrid XML handler for PC saves")
                XMLHandler.save_xml_tree(self.tree, self.file_path)  # Use the Xbox handler here
            
            self.logger.debug("XML tree saved successfully")
            
            # Set the status to "Unsaved Changes" initially, then clear it if save succeeded
            self.unsaved_label.config(text="")
            
            self.logger.debug("Changes saved successfully")
            messagebox.showinfo("Success", "Save file modified successfully!\nA backup has been created.")
            
        except ValueError as ve:
            self.logger.error(f"Failed to save changes - size error: {str(ve)}")
            messagebox.showerror("Error", 
                "Failed to save changes: The modified save data is too large.\n"
                "Try removing some modifications to reduce the size.")
        except Exception as e:
            self.logger.error(f"Failed to save changes: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to save changes: {str(e)}")

    def _on_close(self):
        self.logger.debug("Application closing")
        try:
            if self.unsaved_label.cget("text") == "Unsaved Changes":
                self.logger.debug("Unsaved changes detected")
                response = messagebox.askyesnocancel(
                    "Unsaved Changes",
                    "You have unsaved changes. Would you like to save before closing?",
                    icon="warning"
                )
                
                if response is True:  # Yes, save changes
                    self.logger.debug("Saving changes before exit")
                    self.save_changes()
                    self.root.destroy()
                elif response is False:  # No, close without saving
                    self.logger.debug("Closing without saving changes")
                    self.root.destroy()
                # If response is None (Cancel), do nothing and keep window open
                else:
                    self.logger.debug("Cancel closing, keeping window open")
                
            else:  # No unsaved changes
                self.logger.debug("Closing application (no unsaved changes)")
                self.root.destroy()
                
        except Exception as e:
            self.logger.error(f"Error during application close: {str(e)}", exc_info=True)
            self.root.destroy()  # Ensure application closes even if there's an error          


    def update_time_display(self, time_info: Dict[str, str]) -> None:
        """Update the time display labels with new values."""
        mapping = {
            "Game Time": "GameTime",
            "Played Time": "PlayedTime",
            "Environment Time": "EnvTime"
        }
        
        # Import format_game_time from stats_manager if needed or create standalone function
        from stats_manager import StatsManager
        
        for display_name, xml_name in mapping.items():
            if display_name in self.time_labels:
                value = time_info.get(xml_name, "0")
                # Use StatsManager's formatting method
                formatted_time = StatsManager._format_game_time(None, value)
                self.time_labels[display_name].config(text=formatted_time)


if __name__ == "__main__":
    # Create a logger for the main module
    main_logger = logging.getLogger('Main')
    
    # Create the version selector
    selector = VersionSelector()
    
    # Show the selection screen
    selector.show_selection_screen()
    
    # After mainloop exits, get the selected version
    selected_version = selector.selected_version
    
    # Destroy the selector window to be safe
    try:
        if selector.root and selector.root.winfo_exists():
            selector.root.destroy()
    except:
        pass
    
    # Check if a version was selected (should be handled by _on_window_close, but just in case)
    if selected_version is None:
        main_logger.debug("No version selected, exiting program")
        sys.exit(0)
    
    main_logger.debug(f"User selected version: {selected_version}")
    
    # Create the main application with the selected version
    root = tk.Tk()
    app = SaveEditor(root, game_version=selected_version)
    root.mainloop()
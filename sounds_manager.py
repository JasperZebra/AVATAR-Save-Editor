import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
from typing import Dict, Optional
import logging

class SoundsManager:
    def __init__(self, parent: ttk.Frame, main_window):
        self.logger = logging.getLogger('SoundsManager')
        self.logger.debug("Initializing SoundsManager")
        self.parent = parent
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self) -> None:
        # Create Sounds Treeview that fills the entire parent space
        tree_frame = ttk.Frame(self.parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(tree_frame, text="Sound Knowledge").pack()

        # Create Treeview with columns
        columns = ("ID", "Sound Name", "Description")
        self.sounds_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="extended"
        )

        # Configure columns
        self.sounds_tree.heading("ID", text="Sound ID")
        self.sounds_tree.heading("Sound Name", text="Sound Name")
        self.sounds_tree.heading("Description", text="Description")

        # Set column widths and alignment
        self.sounds_tree.column("ID", width=120, anchor="w")
        self.sounds_tree.column("Sound Name", width=300, anchor="w")
        self.sounds_tree.column("Description", width=400, anchor="w")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.sounds_tree.yview)
        self.sounds_tree.configure(yscrollcommand=scrollbar.set)

        self.sounds_tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        # Statistics frame
        stats_frame = ttk.Frame(tree_frame)
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.sound_count_label = ttk.Label(stats_frame, text="Total sounds discovered: 0")
        self.sound_count_label.pack(side=tk.LEFT, padx=10)

    def load_sounds(self, tree: ET.ElementTree) -> None:
        self.logger.debug("Loading sounds")
        try:
            # Clear existing items
            for item in self.sounds_tree.get_children():
                self.sounds_tree.delete(item)
            
            # Find all sound elements in XML
            sounds = tree.findall(".//SoundKnowledge/Sound")
            
            self.logger.debug(f"Found {len(sounds)} sounds")
            
            # Sort sounds by ID for consistent display
            sounds_sorted = sorted(sounds, key=lambda x: x.get("ID", "0"))
            
            # Process each sound
            for sound in sounds_sorted:
                try:
                    sound_id = sound.get("ID", "")
                    
                    # Get the sound name and description
                    sound_name, description = self._get_sound_info(sound_id)
                    
                    self.sounds_tree.insert("", tk.END, values=(
                        sound_id,
                        sound_name,
                        description
                    ))
                    
                except Exception as e:
                    self.logger.error(f"Error processing sound {sound_id}: {str(e)}", exc_info=True)

            # Update statistics
            self.sound_count_label.config(text=f"Total sounds discovered: {len(sounds)}")
            
            self.logger.debug("Sounds loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading sounds: {str(e)}", exc_info=True)
            raise

    def save_sound_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        self.logger.debug("Sound data is view-only, no changes to save")
        # Since this is just a view-only tab, simply return the tree unchanged
        return tree
    
    def _get_sound_info(self, sound_id):
        """Map sound ID to a name and description"""
        
        # Map of sound IDs to names and descriptions
        # This is a best guess since the actual mapping is not available
        sound_info = {
            # Environmental sounds
            "759101": ("Forest Ambience", "Natural forest sounds of Pandora"),
            "759321": ("Water Flowing", "Sound of water running in streams or rivers"),
            "758777": ("Wind Through Trees", "Wind blowing through Pandoran flora"),
            "758744": ("Rain Sounds", "Rainfall on Pandora's forest canopy"),
            "758969": ("Cave Echo", "Ambient echo sounds in cave systems"),
            "759305": ("Thunder", "Sound of thunderstorms on Pandora"),
            "758961": ("Bioluminescent Activation", "Sound of plants lighting up at night"),
            "759329": ("Waterfall", "Sound of water falling from height"),
            
            # Creature sounds
            "759269": ("Viperwolf Call", "Hunting call of the viperwolf pack"),
            "758861": ("Hammerhead Stampede", "Sound of stampeding hammerhead titanotheres"),
            "758681": ("Thanator Roar", "Threatening roar of a thanator"),
            "759285": ("Banshee Screech", "Distinctive call of a mountain banshee"),
            "758773": ("Hexapede Movement", "Sounds of hexapede herds moving through foliage"),
            "758829": ("Stingbat Wings", "Sound of stingbat wings flapping"),
            "759141": ("Prolemuris Call", "Call of the prolemuris in the trees"),
            "758733": ("Sturmbeest Grunt", "Low grunting sound of a sturmbeest"),
            "758785": ("Direhorse Gallop", "Sound of a direhorse running"),
            "758805": ("Small Creature Movement", "Sounds of small Pandoran creatures"),
            
            # Technology sounds
            "758385": ("AMP Suit Activation", "Startup sequence of an AMP suit"),
            "759085": ("RDA Gunfire", "Sound of RDA weapons fire"),
            "759301": ("Aircraft Engine", "Sound of Samson or Scorpion engines"),
            "759081": ("Door Mechanism", "Sound of RDA facility doors opening/closing"),
            "759005": ("Computer Terminal", "Interface sounds from computer terminals"),
            "759261": ("Airlock Cycling", "Sound of an airlock pressurizing/depressurizing"),
            "759113": ("Radio Chatter", "RDA radio communications"),
            "758498": ("Vehicle Movement", "Sound of ground vehicles moving"),
            "758494": ("Machinery Operation", "Sound of mining or construction equipment"),
            "4294967295": ("System Sound", "Generic system or interface sound"),
            
            # Na'vi sounds
            "758925": ("Na'vi Language", "Phrases or words in the Na'vi language"),
            "759393": ("Na'vi Song", "Traditional Na'vi singing or chanting"),
            "758901": ("Bow String", "Sound of a Na'vi bow being fired"),
            "759389": ("Ceremonial Drums", "Na'vi ceremonial drumming"),
            "759357": ("Tsaheylu Connection", "Sound of forming neural connection"),
            "758993": ("Na'vi Hunting Call", "Hunting signals between Na'vi"),
            "759001": ("Pa'li Whistle", "Whistle to call a direhorse"),
            "758884": ("Ikran Call", "Sound used to call a banshee"),
            "759025": ("Tribal Celebration", "Sounds of Na'vi celebration"),
            "759377": ("Prayer Chant", "Eywa prayer chanting"),
            "759253": ("Fighting Stance", "Sound of Na'vi preparing for combat"),
            
            # Special mission sounds
            "1159811": ("Mission Objective", "Sound indicating a mission objective"),
            "1159825": ("Mission Complete", "Sound of mission completion"),
            "1159852": ("Mission Failed", "Sound indicating mission failure"),
        }
        
        # Return name and description if found, otherwise provide generic information
        if sound_id in sound_info:
            return sound_info[sound_id]
        else:
            return (f"Unknown Sound ({sound_id})", "No description available")
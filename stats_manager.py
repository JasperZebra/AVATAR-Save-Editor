import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
from typing import Dict, Optional
from ui_components import LabeledInput, block_combobox_mousewheel
import os
from PIL import Image, ImageTk
from Face_Image_Window import FaceImageWindow
import logging

class StatsManager:
    def __init__(self, parent: ttk.Frame, main_window):
        self.logger = logging.getLogger('StatsManager')
        self.logger.debug("Initializing StatsManager")
        self.parent = parent
        self.main_window = main_window
        self.entries = {}
        self.face_image_frame = None
        self.face_image_label = None
        self.label_frames = {}  # Store frames for label displays

        # Create item mappings FIRST
        self._create_item_mappings()
        
        # Initialize face values mapping - this is the first change
        self.face_values = {}
        # Create separate mappings for male and female faces
        for i in range(12):  # 12 pairs (00-11)
            face_num = str(i).zfill(2)
            # Both male and female of the same number share the same face value
            self.face_values[str(i)] = {
                "male": f"Male {face_num}",
                "female": f"Female {face_num}"
            }
        
        self.setup_ui()

    def _create_item_mappings(self):
        """Create mappings for item IDs to their actual names"""
        self.item_mappings = {

            #############################################

            # RDA Weapons

            # Dual Wasp Pistol
            "1042188764": "Dual Wasp Pistol I",
            "815885611": "Dual Wasp Pistol II",
            "760079057": "Dual Wasp Pistol III",
            "999316102": "Dual Wasp Pistol IV",

            # Standard Issue Rifle
            "1130814347": "Standard Issue Rifle TERRA I",
            "1306083196": "Standard Issue Rifle EURYS II",
            "3628031700": "Standard Issue Rifle SOLARIS III",
            "1146928137": "Standard Issue Rifle SOLARIS IV",

            # Combat Shotgun PHALANX
            "2313824646": "Combat Shotgun PHALANX I",
            "2270547313": "Combat Shotgun PHALANX II",
            "2789519003": "Combat Shotgun PHALANX III",
            "1919695864": "Combat Shotgun PHALANX IV",

            # Assault Rifle
            "2397981034": "Assault Rifle TERRA I",
            "2152836509": "Assault Rifle EURYS II",
            "268371112": "Assault Rifle SOLARIS III",
            "466145020": "Assault Rifle SOLARIS IV",

            # BANISHER M60 Machine Gun
            "85991974": "BANISHER M60 Machine Gun I",
            "195020497": "BANISHER M60 Machine Gun II",
            "1881065336": "BANISHER M60 Machine Gun III",
            "1796958374": "BANISHER M60 Machine Gun IV",

            # Grenade Launcher M222
            "94681171": "Grenade Launcher M222 - I",
            "186342564": "Grenade Launcher M222 - II",
            "1349633617": "Grenade Launcher M222 - III",
            "4018216358": "Grenade Launcher M222 - IV",

            # Flamethrower
            "2529862352": "Flamethrower VESUPYRE I",
            "2557822503": "Flamethrower STERILATOR II",
            "609450705": "Flamethrower BUSHBOSS III",
            "2288255787": "Flamethrower BUSHBOSS IV",

            # Nail Gun HAMMER
            "2548581230": "Nail Gun HAMMER I",
            "2572658585": "Nail Gun HAMMER II",
            "143378107": "Nail Gun HAMMER III",
            "1911864170": "Nail Gun HAMMER IV",

            # RDA Ammo
            "4029490973": "Rifle Ammo",
            "2220072441": "Shotgun Ammo",
            "3183424835": "SMG Ammo",
            "3227899887": "Grenade Ammo",
            "4198025789": "Rocket Ammo",
            "2442117335": "LMG Ammo",
            "3819023512": "Heavy Ammo",

            #############################################

            # RDA Armor Sets

            # Titan Armor Set
            "4082430736": "Titan Head",
            "205852157":  "Titan Torso",
            "1052486966": "Titan Legs",
        
            # Militum Armor Set
            "149499402":  "Militum Head",  
            "4160278759": "Militum Torso",    
            "3305533484": "Militum Legs",   

            # Kodiak Armor Set
            "1593826001": "Kodiak Head",          
            "2716738620": "Kodiak Torso",        
            "2467333367": "Kodiak Legs",      

            # Exotant Armor Set
            "3527939275": "Exotant Head",     
            "1193780569": "Exotant Torso",       
            "1379870057": "Exotant Legs",         

            # Centauri Armor Set
            "403319592":  "Centauri Head",     
            "3877361093": "Centauri Torso",   
            "3588584718": "Centauri Legs",        

            # Hydra Armor Set
            "3753317026": "Hydra Head",      
            "1851965193": "Hydra Torso",        
            "2428117146": "Hydra Legs",   

            # Warthog Armor Set
            "2823901304": "Warthog Head",         
            "1981144899": "Warthog Torso",          
            "2056338139": "Warthog Legs",    

            # Viper Armor Set
            "3980056687": "Viper Head",
            "3574042272": "Viper Torso",
            "1417888964": "Viper Legs",

            # Default RDA Aromor Set
            "433486271": "Default RDA Head",

            #############################################

            # Na'vi Weapons
            "1304439874": "Staff",
            "1132447925": "Na'vi Bow",  
            "172062103": "Great Bow",   
            "982090295": "War Bow",      
            "1048019290": "Hunter Bow",  
            "2092736556": "Na'vi Spear", 
            "535013914": "Battle Staff", 
            "1662469074": "Poison Dart", 
            "1839769381": "Stinger",     
            "2986118748": "Spirit Staff",
            "2813685095": "War Club",    

            # Additional Na'vi weapons/items from XML
            "3400058396": "Unknown Na'vi Item 1",
            "371977402": "Unknown Na'vi Item 2",
            "1519513878": "Unknown Na'vi Item 3",
            "2232927470": "Unknown Na'vi Item 4",
            "1865419077": "Unknown Na'vi Item 5",
            "958613249": "Unknown Na'vi Item 6",
            "2948460035": "Unknown Na'vi Item 7",
            "985254384": "Unknown Na'vi Item 8",
            "386149755": "Unknown Na'vi Item 9",
            "216177023": "Unknown Na'vi Item 10",
            "3960574385": "Unknown Na'vi Item 11",
            "2070955956": "Unknown Na'vi Item 12",
            "1711646853": "Unknown Na'vi Item 13",
            "2024863229": "Unknown Na'vi Item 14",
            "240531571": "Unknown Na'vi Item 15",
            "921966990": "Unknown Na'vi Item 16",
            "25166328": "Unknown Na'vi Item 17",
            "3724948480": "Unknown Na'vi Item 18",
            "874641835": "Unknown Na'vi Item 19",
            "3932154789": "Unknown Na'vi Item 20",
            "884530381": "Unknown Na'vi Item 21",
            "3480671099": "Unknown Na'vi Item 22",

            # Na'vi Ammo
            "1042656528": "Arrow Ammo",  
            "435601722": "Spear Ammo",   
            "3069972540": "Poison Ammo", 

           #############################################

            # Na'vi Armor
            "753645081": "Na'vi Light Armor",
            "236713729": "Na'vi Medium Armor",
            "2228061969": "Na'vi Heavy Armor",

            "3363478556": "Hunter Armor",    
            "1118628876": "Warrior Armor",   
            "3934969092": "Elite Armor", 

            "291262189": "Spirit Stone",     
            "2255793432": "Healing Herb",    
            "2740507591": "War Paint",    

            "3529616870": "Stealth Cloak",   
            "1641566717": "Hunter's Mark",   
            "540413008": "Sacred Totem",   

            "4093397293": "Spirit Charm",    
            "2295024111": "War Horn",        
            "2917611312": "Sacred Feathers", 

            "4249071066": "Hunter's Eye",    
            "3879387803": "Battle Paint",        
        }

    def _get_item_name(self, item_id: str) -> str:
        """Convert an item ID to its readable name"""
        return self.item_mappings.get(item_id, f"Unknown Item ({item_id})")    

    def _format_weapon_text(self, weapon_info: dict) -> str:
        """Format weapon info for display"""
        if not weapon_info:
            return "-Empty-"
            
        text = f"{weapon_info['name']}"
        
        # Special cases - update to match new names
        if weapon_info['id'] == "1042188764":  # Dual Wasp Pistol I
            text += " (∞)"
        elif weapon_info['id'] in ["1304439874", "2813685095"]:  # Staff and War Club
            text += " (Melee)"
        else:
            # For all other weapons, show ammo count if they have ammo
            if weapon_info['ammo'] != "0" and not weapon_info.get('infinite_ammo', False):
                total_ammo = weapon_info.get('total_ammo', '0')
                text += f" ({weapon_info['ammo']}/{total_ammo})"
            elif weapon_info.get('infinite_ammo', False):
                text += " (∞)"
        
        return text

    def setup_ui(self) -> None:
        self._create_stat_fields()

    def _create_stat_fields(self) -> None:
        """Create all stat fields and UI elements"""
        self.logger.debug("Creating stat fields")
        try:
            # Create list of all face values for combobox
            face_values = {}
            for i in range(12):  # 12 pairs (00-11)
                face_num = str(i).zfill(2)
                face_values[f"male_{i}"] = f"Male {face_num}"
                face_values[f"female_{i}"] = f"Female {face_num}"

            # List of fields to display as labels
            label_fields = {"isfemale", "face", "YouAreHere_LatitudeLongitude", "TotalEP", "namevec"}

            # Define positions for top row groups
            x_positions_row1 = [0, 230, 460, 690]  # Four positions
            
            # Define field groups - added Max Out button as a special field
            field_groups = {
                "Character Info": [
                    ("Character Name", "namevec", None),
                    ("Is Female", "isfemale", {"0": "No", "1": "Yes"}),
                    ("Face", "face", self.face_values),
                    ("Side", "side", {"1": "Navi", "2": "RDA"}),
                    ("Pawn", "pawn", {"1": "Navi", "2": "RDA"}),
                    ("Location", "YouAreHere_LatitudeLongitude")
                ],
                "Progress": [
                    ("Player Faction", "PlayerFaction", {"0": "Undecided", "1": "Na'vi", "2": "RDA"}),
                    ("Total EP", "TotalEP"),
                    ("Max Out EP", "max_out_button", "button"),
                    ("Recovery Bits", "RecoveryBits"),
                ],
                "Faction Settings": [
                    ("Na'vi Cost Reduction", "NaviCostReduction"),
                    ("RDA Cost Reduction", "CorpCostReduction"),
                    ("EPs", "EPs"),        
                    ("newEPs", "newEPs") 
                ],
                "Gameplay Settings": [
                    ("Entity Scanning", "bEntityScanningEnabled", {"0": "No", "1": "Yes"}),
                    ("First Person Mode", "FirstPersonMode", {"0": "No", "1": "Yes"}),
                    ("Rumble Enabled", "RumbleEnabled", {"0": "No", "1": "Yes"})
                ]
            }
            
            # Create level options based on faction
            rda_levels = {"max": "Max Level"}  # Only max level option
            navi_levels = {"max": "Max Level"}  # Only max level option
            
            # Store level options for later use
            self.level_options = {
                "Na'vi": navi_levels,
                "RDA": rda_levels
            }

            # Create top row groups
            first_row_groups = list(field_groups.items())[:4]
            for i, (group_name, fields) in enumerate(first_row_groups):
                group_frame = ttk.LabelFrame(self.parent, text=group_name)
                group_frame.place(x=x_positions_row1[i], y=0, width=230, height=185)  # Back to original width
                
                for field_info in fields:
                    label_text = field_info[0]
                    key = field_info[1]
                    field_type = field_info[2] if len(field_info) > 2 else None

                    # Special handling for button type
                    if field_type == "button":
                        field_frame = ttk.Frame(group_frame)
                        field_frame.pack(fill=tk.X, padx=5, pady=2)
                        ttk.Label(field_frame, text=f"{label_text}:").pack(side=tk.LEFT, padx=5)
                        button = ttk.Button(field_frame, text="Max Out", command=self._max_out_level)
                        button.pack(side=tk.LEFT, padx=5)
                        self.entries[key] = button
                        continue

                    if key in label_fields:
                        # Create frame for label layout
                        field_frame = ttk.Frame(group_frame)
                        field_frame.pack(fill=tk.X, padx=5, pady=2)
                        
                        # Label with field name
                        ttk.Label(field_frame, text=f"{label_text}:").pack(side=tk.LEFT, padx=5)
                        
                        # Label for value
                        value_label = ttk.Label(field_frame, text="-")
                        value_label.pack(side=tk.LEFT, padx=5)
                        
                        self.entries[key] = value_label
                        
                        if key == "face":
                            value_label.bind('<Button-1>', lambda e: self._on_face_selected())
                    else:
                        input_widget = LabeledInput(
                            group_frame,
                            label_text,
                            "combobox" if field_type else "entry",
                            field_type
                        )
                        input_widget.pack(fill=tk.X, padx=5, pady=2)
                        self.entries[key] = input_widget.input

                        # Special bindings for different fields
                        if key == "PlayerFaction":
                            # When faction changes, update the level dropdown options
                            input_widget.input.bind('<<ComboboxSelected>>', self._on_faction_selected)
                        elif key == "TotalEP":
                            # Custom binding for TotalEP input to update level
                            input_widget.input.bind('<KeyRelease>', lambda e: self._update_level_from_ep())
                            
                        if isinstance(input_widget.input, (ttk.Entry, ttk.Combobox)):
                            if hasattr(input_widget.input, 'bind'):
                                input_widget.input.bind('<KeyRelease>', self._mark_unsaved_changes)
                                if key not in ["TotalEP"]:  # Don't double-bind
                                    input_widget.input.bind('<<ComboboxSelected>>', self._mark_unsaved_changes)

            # RDA Loadout frame
            rda_frame = ttk.LabelFrame(self.parent, text="RDA Loadout")
            rda_frame.place(x=0, y=190, width=545, height=350)

            # Define custom slot names for RDA
            rda_slot_names = [
                "Right Weapon",    # Slot 1
                "Down Weapon",  # Slot 2
                "Left Weapon",    # Slot 3
                "Top Weapon"         # Slot 4
            ]

            # Define custom slot names and positions for RDA
            rda_slot_names = [
                {"name": "Right Weapon", "x": 5, "y": 0},    # Slot 1
                {"name": "Down Weapon", "x": 5, "y": 50},     # Slot 2
                {"name": "Left Weapon", "x": 5, "y": 100},    # Slot 3
                {"name": "Top Weapon", "x": 5, "y": 150}      # Slot 4
            ]

            # Initialize weapon slots array
            self.weapon_slots = []

            # Add reset ammo button to RDA loadout frame
            reset_frame = ttk.Frame(rda_frame)
            reset_frame.place(x=350, y=200)  # Adjust position as needed

            reset_button = ttk.Button(
                reset_frame,
                text="Reset Weapon Ammo Types",
                command=self._reset_weapon_ammo
            )
            reset_button.pack(pady=5)
            
            # Create RDA weapon slots with dropdowns
            for i, slot_info in enumerate(rda_slot_names):
                self._create_weapon_dropdown(rda_frame, slot_info["name"], i, is_navi=False, 
                                            x=slot_info["x"], y=slot_info["y"])
    
            # Create RDA armor mappings
            self._create_rda_armor_mappings()

            # Add armor slot
            armor_frame = ttk.Frame(rda_frame)
            armor_frame.place(x=10, y=200)  # Adjust y and x position as needed

            # Store labels in a dictionary for easy updating
            self.armor_dropdowns = {}

            # Create labels for each armor slot
            armor_slots = [
                ("headwear", "Headwear"),
                ("torso", "Torso"),
                ("legs", "Legs")
            ]

            for slot_id, slot_name in armor_slots:
                slot_frame = ttk.Frame(armor_frame)
                slot_frame.pack(fill=tk.X, pady=10)
                
                ttk.Label(slot_frame, text=f"{slot_name}:").pack(side=tk.LEFT, padx=5)
                
                # Create combobox with armor options for this slot
                values = list(self.rda_armor_sets[slot_id].values())
                combo = ttk.Combobox(slot_frame, values=values, state="readonly", width=30)
                combo.set("-Empty-")  # Default value
                combo.pack(side=tk.LEFT, padx=5)
                block_combobox_mousewheel(combo)
                
                # Bind the combobox to update function
                combo.bind('<<ComboboxSelected>>', 
                    lambda e, slot=slot_id: self._on_armor_selected(e, slot))
                
                self.armor_dropdowns[slot_id] = combo

            # Na'vi Loadout frame
            navi_frame = ttk.LabelFrame(self.parent, text="Na'vi Loadout")
            navi_frame.place(x=545, y=190, width=555, height=350)

            # Define custom slot names for Na'vi
            navi_slot_names = [
                "Right Weapon",    # Slot 1
                "Down Weapon",     # Slot 2
                "Left Weapon",    # Slot 3
                "Top Weapon"        # Slot 4
            ]

            # Define custom slot names and positions for Na'vi
            navi_slot_names = [
                {"name": "Right Weapon", "x": 5, "y": 0},    # Slot 1
                {"name": "Down Weapon", "x": 5, "y": 50},     # Slot 2
                {"name": "Left Weapon", "x": 5, "y": 100},    # Slot 3
                {"name": "Top Weapon", "x": 5, "y": 150}      # Slot 4
            ]

            # Initialize Na'vi weapon slots array
            self.navi_weapon_slots = []
            
            # Add reset ammo button to RDA loadout frame
            reset_frame = ttk.Frame(navi_frame)
            reset_frame.place(x=350, y=200)  # Adjust position as needed

            reset_button = ttk.Button(
                reset_frame,
                text="Reset Weapon Ammo Types",
                command=self._reset_weapon_ammo
            )
            reset_button.pack(pady=5)

            # Create Na'vi weapon slots with dropdowns
            for i, slot_info in enumerate(navi_slot_names):
                self._create_weapon_dropdown(navi_frame, slot_info["name"], i, is_navi=True,
                                            x=slot_info["x"], y=slot_info["y"])
    
            # Create Na'vi armor mappings
            self._create_navi_armor_mappings()

            # Create Na'vi armor section with individual slots
            navi_armor_frame = ttk.Frame(navi_frame)
            navi_armor_frame.place(x=10, y=200)  # Adjust y position as needed

            # Store labels in a dictionary for easy updating
            self.navi_armor_dropdowns = {}

            # Create labels for each Na'vi armor slot
            armor_slots = [
                ("headwear", "Headwear"),
                ("torso", "Torso"),
                ("legs", "Legs")
            ]

            for slot_id, slot_name in armor_slots:
                slot_frame = ttk.Frame(navi_armor_frame)
                slot_frame.pack(fill=tk.X, pady=10)
                
                ttk.Label(slot_frame, text=f"{slot_name}:").pack(side=tk.LEFT, padx=5)
                
                # Create combobox with armor options for this slot
                values = list(self.navi_armor_sets[slot_id].values())
                combo = ttk.Combobox(slot_frame, values=values, state="readonly", width=30)
                combo.set("-Empty-")  # Default value
                combo.pack(side=tk.LEFT, padx=5)
                block_combobox_mousewheel(combo)
                
                # Bind the combobox to update function
                combo.bind('<<ComboboxSelected>>', 
                    lambda e, slot=slot_id: self._on_navi_armor_selected(e, slot))
                
                self.navi_armor_dropdowns[slot_id] = combo

            # Create the face image frame
            self.face_image_frame = ttk.LabelFrame(self.parent, text="Character Face")
            self.face_image_frame.place(
                x=920,
                y=0,
                width=182,
                height=185
            )

            # Create a label inside the frame to display the image
            self.face_image_label = ttk.Label(self.face_image_frame)
            self.face_image_label.pack(
                expand=True,
                fill='both',
                padx=12,
                pady=5
            )

        except Exception as e:
            self.logger.error(f"Error creating stat fields: {str(e)}", exc_info=True)
            raise


    def _create_readonly_entry(self, parent, initial_value="0", width=8):
        """Create an entry field that cannot be edited by typing but can be programmatically updated"""
        entry = ttk.Entry(parent, width=width)
        entry.insert(0, initial_value)
        
        # Disable direct user editing
        def disable_editing(event):
            return "break"
        
        # Bind all events that could modify the entry content
        entry.bind("<Key>", disable_editing)
        entry.bind("<KeyPress>", disable_editing)
        entry.bind("<KeyRelease>", disable_editing)
        
        # Still allow selection and copying
        entry.bind("<Control-c>", lambda e: None)  # Allow copying
        
        return entry

    def _create_weapon_dropdown(self, parent_frame, slot_name, slot_index, is_navi=False, x=0, y=0):
            """Create a dropdown for weapon selection and an entry for ammo count"""
            # Create a frame to hold the controls
            slot_frame = ttk.Frame(parent_frame)
            slot_frame.place(x=x, y=y, width=535, height=30)  # Use place instead of pack
            
            # Label for the slot
            ttk.Label(slot_frame, text=f"{slot_name}:").pack(side=tk.LEFT, padx=2)
            
            # Create the weapon dropdown
            all_weapons = {}
            
            # Add RDA and Na'vi weapons
            for item_id, item_name in self.item_mappings.items():
                # Add only weapons (filter out armor and other items)
                if any(weapon_keyword in item_name.lower() for weapon_keyword in 
                    ["pistol", "rifle", "shotgun", "machine gun", "launcher", "thrower", "nail gun", "bow", "staff", "spear", "club", "dart"]):
                    all_weapons[item_id] = f"[RDA] {item_name}" if any(rda_keyword in item_name.lower() for rda_keyword in 
                                        ["pistol", "rifle", "shotgun", "machine gun", "launcher", "thrower", "nail gun"]) else f"[Na'vi] {item_name}"
            
            # Create the dropdown with weapon names
            combo = ttk.Combobox(slot_frame, values=list(all_weapons.values()), width=34, state="readonly")
            combo.pack(side=tk.LEFT, padx=2)
            combo.set("-Empty-")
            block_combobox_mousewheel(combo)
            
            # Create a frame for ammo control
            ammo_frame = ttk.Frame(slot_frame)
            ammo_frame.pack(side=tk.LEFT, padx=2)
            
            # Label and entry for ammo - use a regular entry that can be disabled later if needed
            ttk.Label(ammo_frame, text="Ammo:").pack(side=tk.LEFT)
            ammo_entry = ttk.Entry(ammo_frame, width=8)
            ammo_entry.insert(0, "0")
            ammo_entry.pack(side=tk.LEFT, padx=2)
            
            # Add infinite ammo checkbox
            infinite_var = tk.BooleanVar()
            infinite_check = ttk.Checkbutton(
                ammo_frame, 
                text="∞", 
                variable=infinite_var,
                style="TCheckbutton"
            )
            infinite_check.pack(side=tk.LEFT, padx=2)
            
            # Add clip size control - CHANGED: Using a label instead of an entry
            clip_frame = ttk.Frame(slot_frame)
            clip_frame.pack(side=tk.LEFT, padx=5)
            
            ttk.Label(clip_frame, text="Clip:").pack(side=tk.LEFT)
            
            # Use a label instead of entry for clip size
            clip_label = ttk.Label(clip_frame, text="0", width=5)
            clip_label.pack(side=tk.LEFT, padx=2)
            
            # Create slot data
            weapon_slot_data = {
                "dropdown": combo,
                "ammo_entry": ammo_entry,
                "clip_entry": clip_label,  # Now this is a label, not an entry
                "infinite_var": infinite_var,
                "infinite_check": infinite_check,
                "all_weapons": all_weapons  # Store mapping of IDs to names
            }
            
            # Choose the right list to modify
            weapons_array = self.navi_weapon_slots if is_navi else self.weapon_slots
            
            # Ensure the list has enough elements
            while len(weapons_array) <= slot_index:
                weapons_array.append(None)
            
            # Now we can safely assign to the index
            weapons_array[slot_index] = weapon_slot_data
            
            # Bind events - use the appropriate event handler
            if is_navi:
                combo.bind('<<ComboboxSelected>>', lambda e, idx=slot_index: self._on_navi_weapon_selected(e, idx))
            else:
                combo.bind('<<ComboboxSelected>>', lambda e, idx=slot_index: self._on_weapon_selected(e, idx))
            
            # Bind the infinite ammo checkbox
            infinite_check.bind('<ButtonRelease-1>', lambda e, idx=slot_index, navi=is_navi: 
                            self._toggle_infinite_ammo(e, idx, navi))
            
            # No need for bindings on the clip label since it's read-only now
            
            return weapon_slot_data

    # Also add a method to programmatically update entry values
    def _update_entry_value(self, entry, value):
        """Update an entry value programmatically, bypassing the read-only restriction"""
        entry.configure(state="normal")  # Temporarily enable
        entry.delete(0, tk.END)
        entry.insert(0, str(value))
        entry.configure(state="readonly")  # Set back to readonly

    def _update_clip_value(self, event, slot_index, is_navi=False):
        """Update the clip size value in the XML when changed in the UI"""
        try:
            # Get the new clip value - we no longer get it from UI since it's now read-only
            # Instead, get it from the weapon data
            # This method is now only called programmatically, not from user interaction
            
            clip_label = self.navi_weapon_slots[slot_index]["clip_entry"] if is_navi else self.weapon_slots[slot_index]["clip_entry"]
            new_clip = clip_label.cget("text")
            
            # Validate as integer
            try:
                new_clip = int(new_clip)
            except ValueError:
                # Not a valid number, ignore
                return
                            
            # Update the XML if valid
            if self.main_window.tree is not None:
                profile = self.main_window.tree.getroot().find("PlayerProfile")
                if profile is not None:
                    if is_navi:
                        # Find the Na'vi weapon we're updating
                        avatar = profile.find("Possessions_Avatar")
                        if avatar is None:
                            return
                                        
                        equipped = avatar.find("EquippedWeapons")
                        if equipped is None:
                            return
                                        
                        slots = equipped.findall("Slot")
                        if slot_index >= len(slots):
                            return
                                    
                        # Get the possession index
                        poss_idx = slots[slot_index].get("MainHand_PossIdx", "-1")
                        if poss_idx == "-1":
                            return
                                        
                        # Find the weapon possession
                        possessions = avatar.find("Posessions")
                        if possessions is None:
                            return
                                        
                        # First get the weapon to determine its ammo type
                        weapon_poss = None
                        for poss in possessions.findall("Poss"):
                            if poss.get("Index") == poss_idx:
                                weapon_poss = poss
                                break
                                
                        if weapon_poss is None:
                            return
                        
                        # Only update NbInClip in the corresponding ammo item
                        ammo_type = weapon_poss.get("crc_AmmoType", "4294967295")
                        if ammo_type != "4294967295":  # Skip for infinite ammo weapons
                            ammo_updated = False
                            for ammo_poss in possessions.findall("Poss"):
                                if ammo_poss.get("crc_ItemID") == ammo_type:
                                    ammo_poss.set("NbInClip", str(new_clip))
                                    self.logger.debug(f"Updated Na'vi ammo clip to {new_clip}")
                                    ammo_updated = True
                                    break
                            
                            # If ammo item not found, create it
                            if not ammo_updated:
                                self._ensure_ammo_exists(possessions, ammo_type, "100")
                                # Find the newly created ammo and set its clip
                                for ammo_poss in possessions.findall("Poss"):
                                    if ammo_poss.get("crc_ItemID") == ammo_type:
                                        ammo_poss.set("NbInClip", str(new_clip))
                                        self.logger.debug(f"Created and updated Na'vi ammo clip to {new_clip}")
                                        break
                    else:
                        # RDA weapon update - same logic as above
                        # [rest of the method unchanged]
                        soldier = profile.find("Possessions_Soldier")
                        if soldier is None:
                            return
                                        
                        equipped = soldier.find("EquippedWeapons")
                        if equipped is None:
                            return
                                        
                        slots = equipped.findall("Slot")
                        if slot_index >= len(slots):
                            return
                                    
                        # Get the possession index
                        poss_idx = slots[slot_index].get("MainHand_PossIdx", "-1")
                        if poss_idx == "-1":
                            return
                                        
                        # Find the weapon possession
                        possessions = soldier.find("Posessions")
                        if possessions is None:
                            return
                                
                        # First get the weapon to determine its ammo type
                        weapon_poss = None
                        for poss in possessions.findall("Poss"):
                            if poss.get("Index") == poss_idx:
                                weapon_poss = poss
                                break
                                
                        if weapon_poss is None:
                            return
                        
                        # Only update NbInClip in the corresponding ammo item
                        ammo_type = weapon_poss.get("crc_AmmoType", "4294967295")
                        if ammo_type != "4294967295":  # Skip for infinite ammo weapons
                            ammo_updated = False
                            for ammo_poss in possessions.findall("Poss"):
                                if ammo_poss.get("crc_ItemID") == ammo_type:
                                    ammo_poss.set("NbInClip", str(new_clip))
                                    self.logger.debug(f"Updated RDA ammo clip to {new_clip}")
                                    ammo_updated = True
                                    break
                            
                            # If ammo item not found, create it
                            if not ammo_updated:
                                self._ensure_ammo_exists(possessions, ammo_type, "100")
                                # Find the newly created ammo and set its clip
                                for ammo_poss in possessions.findall("Poss"):
                                    if ammo_poss.get("crc_ItemID") == ammo_type:
                                        ammo_poss.set("NbInClip", str(new_clip))
                                        self.logger.debug(f"Created and updated RDA ammo clip to {new_clip}")
                                        break
                    
                    # Mark as unsaved
                    self.main_window.unsaved_label.config(text="Unsaved Changes")
        except Exception as e:
            self.logger.error(f"Error updating clip value: {str(e)}")

    def _toggle_infinite_ammo(self, event, slot_index, is_navi=False):
        """Handle toggling infinite ammo for a weapon"""
        try:
            # Get the slot data
            slot_data = self.navi_weapon_slots[slot_index] if is_navi else self.weapon_slots[slot_index]
            
            # Get the current weapon from the dropdown
            weapon_name = slot_data["dropdown"].get()
            if weapon_name == "-Empty-":
                return
                
            # Find weapon ID from name
            weapon_id = None
            for id, name in slot_data["all_weapons"].items():
                if name == weapon_name:
                    weapon_id = id
                    break
                    
            if weapon_id is None:
                return
                
            # Get the infinite ammo state (note: need to get the new value after toggle)
            # We need to wait a moment for the checkbox to update
            self.parent.after(50, lambda: self._apply_infinite_ammo(slot_index, is_navi, weapon_id))
                
        except Exception as e:
            self.logger.error(f"Error toggling infinite ammo: {str(e)}")

    def _apply_infinite_ammo(self, slot_index, is_navi, weapon_id):
        """Apply the infinite ammo setting after checkbox toggle"""
        try:
            # Get the slot data
            slot_data = self.navi_weapon_slots[slot_index] if is_navi else self.weapon_slots[slot_index]
            
            # Get the state of the checkbox
            infinite_enabled = slot_data["infinite_var"].get()
            self.logger.debug(f"Toggling infinite ammo to {infinite_enabled} for weapon ID {weapon_id}")
            
            # Update the XML if a save file is loaded
            if self.main_window.tree is not None:
                profile = self.main_window.tree.getroot().find("PlayerProfile")
                if profile is not None:
                    if is_navi:
                        # Find the Na'vi weapon we're updating
                        avatar = profile.find("Possessions_Avatar")
                        if avatar is None:
                            self.logger.error("Possessions_Avatar not found")
                            return
                                    
                        equipped = avatar.find("EquippedWeapons")
                        if equipped is None:
                            self.logger.error("EquippedWeapons not found")
                            return
                                    
                        slots = equipped.findall("Slot")
                        if slot_index >= len(slots):
                            self.logger.error(f"Slot index {slot_index} out of range")
                            return
                                    
                        # Get the possession index
                        poss_idx = slots[slot_index].get("MainHand_PossIdx", "-1")
                        if poss_idx == "-1":
                            self.logger.error("No weapon equipped in this slot")
                            return
                                    
                        # Find the possession
                        possessions = avatar.find("Posessions")
                        if possessions is None:
                            self.logger.error("Posessions not found")
                            return
                            
                        # Get the weapon possession
                        weapon_poss = None
                        for poss in possessions.findall("Poss"):
                            if poss.get("Index") == poss_idx:
                                weapon_poss = poss
                                break
                            
                        if weapon_poss is None:
                            self.logger.error("Weapon possession not found")
                            return
                                
                        # Get the ammo type but DO NOT CHANGE IT
                        ammo_type = weapon_poss.get("crc_AmmoType", "4294967295")
                        
                        # If toggling infinite ammo, ONLY set the clip size
                        if infinite_enabled:
                            self.logger.debug("Setting NbInClip to 999999 (NOT changing ammo type)")
                            weapon_poss.set("NbInClip", "999999")
                        else:
                            # Reset clip to a reasonable value
                            weapon_poss.set("NbInClip", "100")
                            
                        # Update ammo item if it exists (but don't create if not found)
                        if ammo_type != "4294967295":
                            for ammo_poss in possessions.findall("Poss"):
                                if ammo_poss.get("crc_ItemID") == ammo_type:
                                    if infinite_enabled:
                                        ammo_poss.set("NbInStack", "999999")
                                    else:
                                        ammo_poss.set("NbInStack", "100")
                                    break
                    else:
                        # Handle RDA weapon
                        soldier = profile.find("Possessions_Soldier")
                        if soldier is None:
                            self.logger.error("Possessions_Soldier not found")
                            return
                                    
                        equipped = soldier.find("EquippedWeapons")
                        if equipped is None:
                            self.logger.error("EquippedWeapons not found")
                            return
                                    
                        slots = equipped.findall("Slot")
                        if slot_index >= len(slots):
                            self.logger.error(f"Slot index {slot_index} out of range")
                            return
                                    
                        # Get the possession index
                        poss_idx = slots[slot_index].get("MainHand_PossIdx", "-1")
                        if poss_idx == "-1":
                            self.logger.error("No weapon equipped in this slot")
                            return
                                    
                        # Find the possession
                        possessions = soldier.find("Posessions")
                        if possessions is None:
                            self.logger.error("Posessions not found")
                            return
                            
                        # Get the weapon possession
                        weapon_poss = None
                        for poss in possessions.findall("Poss"):
                            if poss.get("Index") == poss_idx:
                                weapon_poss = poss
                                break
                            
                        if weapon_poss is None:
                            self.logger.error("Weapon possession not found")
                            return
                                
                        # Get the ammo type but DO NOT CHANGE IT
                        ammo_type = weapon_poss.get("crc_AmmoType", "4294967295")
                        
                        # If toggling infinite ammo, ONLY set the clip size
                        if infinite_enabled:
                            self.logger.debug("Setting NbInClip to 999999 (NOT changing ammo type)")
                            weapon_poss.set("NbInClip", "999999")
                        else:
                            # Reset clip to a reasonable value
                            weapon_poss.set("NbInClip", "100")
                            
                        # Update ammo item if it exists (but don't create if not found)
                        if ammo_type != "4294967295":
                            for ammo_poss in possessions.findall("Poss"):
                                if ammo_poss.get("crc_ItemID") == ammo_type:
                                    if infinite_enabled:
                                        ammo_poss.set("NbInStack", "999999")
                                    else:
                                        ammo_poss.set("NbInStack", "100")
                                    break
                    
                    # Update ammo entry state
                    ammo_entry = slot_data["ammo_entry"]
                    if infinite_enabled:
                        # Set ammo to 999999 and DISABLE the field
                        ammo_entry.delete(0, tk.END)
                        ammo_entry.insert(0, "999999")
                        ammo_entry.configure(state="disabled")
                        self.logger.debug("Set UI ammo field to 999999 and disabled")
                    else:
                        # Set ammo to 100 and keep field NORMAL (enabled)
                        ammo_entry.delete(0, tk.END)
                        ammo_entry.insert(0, "100")
                        ammo_entry.configure(state="normal")
                        self.logger.debug("Set UI ammo field to 100 and enabled")
                    
                    # Mark as unsaved
                    self.main_window.unsaved_label.config(text="Unsaved Changes")
        
        except Exception as e:
            self.logger.error(f"Error applying infinite ammo: {str(e)}", exc_info=True)

    def _update_ammo_directly(self, profile, is_navi, slot_index, new_ammo_value):
        """Direct method to update ammo in the save file for debugging and manual updates"""
        try:
            self.logger.debug(f"Directly updating ammo to {new_ammo_value} for {'Navi' if is_navi else 'RDA'} slot {slot_index}")

            if is_navi:
                # Find the Na'vi weapon
                avatar = profile.find("Possessions_Avatar")
                if avatar is None:
                    self.logger.error("Possessions_Avatar not found")
                    return False
                        
                equipped = avatar.find("EquippedWeapons")
                if equipped is None:
                    self.logger.error("EquippedWeapons not found")
                    return False
                        
                slots = equipped.findall("Slot")
                if slot_index >= len(slots):
                    self.logger.error(f"Slot index {slot_index} out of range")
                    return False
                        
                # Get the possession index
                poss_idx = slots[slot_index].get("MainHand_PossIdx", "-1")
                if poss_idx == "-1":
                    self.logger.error("No weapon equipped in this slot")
                    return False
                        
                # Find the weapon possession
                possessions = avatar.find("Posessions")
                if possessions is None:
                    self.logger.error("Posessions not found")
                    return False
                
                # Find the weapon
                weapon_poss = None
                for poss in possessions.findall("Poss"):
                    if poss.get("Index") == poss_idx:
                        weapon_poss = poss
                        break
                
                if weapon_poss is None:
                    self.logger.error("Weapon possession not found")
                    return False
                
                # Get ammo type
                ammo_type = weapon_poss.get("crc_AmmoType", "4294967295")
                if ammo_type == "4294967295":
                    self.logger.error("Weapon has infinite ammo or no ammo")
                    return False
                
                # IMPORTANT NEW CODE: Also update the weapon's own clip value
                clip_value = min(int(new_ammo_value), 100)  # Set clip to whatever is in ammo, max 100
                weapon_poss.set("NbInClip", str(clip_value))
                self.logger.debug(f"Updated weapon clip to {clip_value}")
                
                # Find and update ammo possession
                ammo_updated = False
                for poss in possessions.findall("Poss"):
                    if poss.get("crc_ItemID") == ammo_type:
                        # Update BOTH ammo attributes
                        poss.set("NbInStack", str(new_ammo_value))
                        poss.set("NbInClip", str(clip_value))
                        ammo_updated = True
                        self.logger.debug(f"Updated Na'vi ammo possession to {new_ammo_value}")
                        break
                
                # If we get here and ammo wasn't found - create it
                if not ammo_updated:
                    self._ensure_ammo_exists(possessions, ammo_type, str(new_ammo_value))
                
                # ADDITIONAL UPDATES - Try updating all possible ammo locations
                # Find all items that match the ammo type and update them all
                for poss in possessions.findall("Poss"):
                    if poss.get("crc_ItemID") == ammo_type or poss.get("crc_AmmoType") == ammo_type:
                        poss.set("NbInStack", str(new_ammo_value))
                        self.logger.debug(f"Updated additional ammo possession: {poss.get('Index')}")

                self.logger.debug(f"Successfully updated Na'vi ammo to {new_ammo_value}")
                return True
                
            else:
                # RDA weapon update - similar approach with additional updates
                soldier = profile.find("Possessions_Soldier")
                if soldier is None:
                    self.logger.error("Possessions_Soldier not found")
                    return False
                        
                equipped = soldier.find("EquippedWeapons")
                if equipped is None:
                    self.logger.error("EquippedWeapons not found")
                    return False
                        
                slots = equipped.findall("Slot")
                if slot_index >= len(slots):
                    self.logger.error(f"Slot index {slot_index} out of range")
                    return False
                        
                # Get the possession index
                poss_idx = slots[slot_index].get("MainHand_PossIdx", "-1")
                if poss_idx == "-1":
                    self.logger.error("No weapon equipped in this slot")
                    return False
                        
                # Find the weapon possession
                possessions = soldier.find("Posessions")
                if possessions is None:
                    self.logger.error("Posessions not found")
                    return False
                
                # Find the weapon
                weapon_poss = None
                for poss in possessions.findall("Poss"):
                    if poss.get("Index") == poss_idx:
                        weapon_poss = poss
                        break
                
                if weapon_poss is None:
                    self.logger.error("Weapon possession not found")
                    return False
                
                # Get ammo type
                ammo_type = weapon_poss.get("crc_AmmoType", "4294967295")
                if ammo_type == "4294967295":
                    self.logger.error("Weapon has infinite ammo or no ammo")
                    return False
                
                # IMPORTANT NEW CODE: Also update the weapon's own clip value
                clip_value = min(int(new_ammo_value), 100)  # Set clip to whatever is in ammo, max 100
                weapon_poss.set("NbInClip", str(clip_value))
                self.logger.debug(f"Updated weapon clip to {clip_value}")
                
                # Find and update ammo possession
                ammo_updated = False
                for poss in possessions.findall("Poss"):
                    if poss.get("crc_ItemID") == ammo_type:
                        # Update BOTH ammo attributes
                        poss.set("NbInStack", str(new_ammo_value))
                        poss.set("NbInClip", str(clip_value))
                        ammo_updated = True
                        self.logger.debug(f"Updated RDA ammo possession to {new_ammo_value}")
                        break
                
                # If we get here and ammo wasn't found - create it
                if not ammo_updated:
                    self._ensure_ammo_exists(possessions, ammo_type, str(new_ammo_value))
                
                # ADDITIONAL UPDATES - Try updating all possible ammo locations
                # Find all items that match the ammo type and update them all
                for poss in possessions.findall("Poss"):
                    if poss.get("crc_ItemID") == ammo_type or poss.get("crc_AmmoType") == ammo_type:
                        poss.set("NbInStack", str(new_ammo_value))
                        self.logger.debug(f"Updated additional ammo possession: {poss.get('Index')}")

                self.logger.debug(f"Successfully updated RDA ammo to {new_ammo_value}")
                return True
        
        except Exception as e:
            self.logger.error(f"Error in direct ammo update: {str(e)}", exc_info=True)
            return False
        
    def _ensure_ammo_exists(self, possessions, ammo_type, amount="100"):
        """Ensure ammo exists in inventory when disabling infinite ammo"""
        # Skip if ammo type is the 'no ammo' value
        if ammo_type == "4294967295":
            self.logger.debug("Skipping ammo creation for infinite ammo weapon")
            return
                
        # Check if ammo already exists
        ammo_exists = False
        for poss in possessions.findall("Poss"):
            if poss.get("crc_ItemID") == ammo_type:
                ammo_exists = True
                # Set the ammo to the requested amount
                poss.set("NbInStack", amount)
                poss.set("NbInClip", "0")  # Also ensure clip value is set
                poss.set("NoveltyState", "2")  # Make sure novelty state is right
                self.logger.debug(f"Updated existing ammo of type {ammo_type} to {amount}")
                break
                    
        if not ammo_exists:
            self.logger.debug(f"Creating new ammo of type {ammo_type} with amount {amount}")
            # Need to add ammo to inventory
            # Find next available index
            max_index = -1
            for poss in possessions.findall("Poss"):
                idx = int(poss.get("Index", "0"))
                if idx > max_index:
                    max_index = idx
                        
            # Create new possession for ammo
            new_index = max_index + 1
            self.logger.debug(f"Creating new ammo at index {new_index}")
            new_ammo = ET.SubElement(possessions, "Poss")
            new_ammo.set("Index", str(new_index))
            new_ammo.set("crc_ItemID", ammo_type)
            new_ammo.set("NbInStack", amount)
            new_ammo.set("NbInClip", "0")
            new_ammo.set("crc_AmmoType", "4294967295")
            new_ammo.set("NoveltyState", "2")
            self.logger.debug(f"New ammo created successfully")

    def _update_ammo_value(self, event, slot_index, is_navi=False):
        """Update the ammo value in the XML when changed in the UI"""
        try:
            # Get the new ammo value
            ammo_entry = self.navi_weapon_slots[slot_index]["ammo_entry"] if is_navi else self.weapon_slots[slot_index]["ammo_entry"] 
            new_ammo = ammo_entry.get()
            
            # Skip if the entry is disabled (for infinite ammo weapons)
            if str(ammo_entry.cget('state')) == 'disabled':
                return
            
            # Validate as integer
            try:
                new_ammo = int(new_ammo)
                faction = "Navi" if is_navi else "RDA"
                print(f"AMMO_DEBUG: Setting {faction} weapon ammo to {new_ammo}")
            except ValueError:
                return
                                        
            # Update the XML if valid
            if self.main_window.tree is not None:
                profile = self.main_window.tree.getroot().find("PlayerProfile")
                if profile is not None:
                    # Find the weapon possession
                    if is_navi:
                        avatar = profile.find("Possessions_Avatar")
                        if avatar is None:
                            return
                                
                        equipped = avatar.find("EquippedWeapons")
                        if equipped is None:
                            return
                                
                        slots = equipped.findall("Slot")
                        if slot_index >= len(slots):
                            return
                        
                        poss_idx = slots[slot_index].get("MainHand_PossIdx", "-1")
                        possessions = avatar.find("Posessions")
                    else:
                        soldier = profile.find("Possessions_Soldier")
                        if soldier is None:
                            return
                                
                        equipped = soldier.find("EquippedWeapons")
                        if equipped is None:
                            return
                                
                        slots = equipped.findall("Slot")
                        if slot_index >= len(slots):
                            return
                        
                        poss_idx = slots[slot_index].get("MainHand_PossIdx", "-1")
                        possessions = soldier.find("Posessions")
                    
                    if possessions is None or poss_idx == "-1":
                        return
                    
                    # Find weapon possession
                    weapon_poss = None
                    for poss in possessions.findall("Poss"):
                        if poss.get("Index") == poss_idx:
                            weapon_poss = poss
                            break
                    
                    if weapon_poss is None:
                        return
                    
                    # DIRECT APPROACH: Set both values that could affect ammo
                    weapon_poss.set("NbInClip", str(new_ammo))
                    print(f"AMMO_DEBUG: Set weapon NbInClip to {new_ammo}")
                    
                    # Get the ammo type
                    ammo_type = weapon_poss.get("crc_AmmoType", "4294967295")
                    if ammo_type != "4294967295":
                        ammo_found = False
                        for ammo_poss in possessions.findall("Poss"):
                            if ammo_poss.get("crc_ItemID") == ammo_type:
                                ammo_poss.set("NbInStack", str(new_ammo))
                                print(f"AMMO_DEBUG: Set ammo NbInStack to {new_ammo}")
                                ammo_found = True
                                break
                        
                        if not ammo_found:
                            self._ensure_ammo_exists(possessions, ammo_type, str(new_ammo))
                            print(f"AMMO_DEBUG: Created new ammo with {new_ammo}")
                    
                    # Force immediate save
                    print("AMMO_DEBUG: Marking file as having unsaved changes")
                    self.main_window.unsaved_label.config(text="Unsaved Changes")
        except Exception as e:
            print(f"AMMO_DEBUG ERROR: {str(e)}")

    def _can_have_infinite_ammo(self, weapon_id):
        """Determine if a weapon can have infinite ammo"""
        # List of weapon IDs that can use infinite ammo
        infinite_capable = [
            "1042188764",  # Dual Wasp Pistol I
            "815885611",   # Dual Wasp Pistol II
            "760079057",   # Dual Wasp Pistol III
            "999316102",   # Dual Wasp Pistol IV
            "1304439874",  # Staff (melee)
            "2813685095"   # War Club (melee)
        ]
        return weapon_id in infinite_capable

    def _reset_weapon_ammo(self):
        """Reset all weapons to their original ammo types"""
        self.logger.debug("Resetting all weapons to original ammo types")
        
        if self.main_window.tree is None:
            self.logger.warning("No save file loaded")
            return
        
        profile = self.main_window.tree.getroot().find("PlayerProfile")
        if profile is None:
            self.logger.warning("No player profile found")
            return
        
        # Reset RDA weapons
        soldier = profile.find("Possessions_Soldier")
        if soldier is not None:
            possessions = soldier.find("Posessions")
            if possessions is not None:
                # Reset each weapon to its correct ammo type
                for poss in possessions.findall("Poss"):
                    weapon_id = poss.get("crc_ItemID")
                    # Only process actual weapons
                    if weapon_id in self.item_mappings:
                        item_name = self.item_mappings[weapon_id]
                        if any(weapon_keyword in item_name.lower() for weapon_keyword in 
                            ["pistol", "rifle", "shotgun", "machine gun", "launcher", "thrower", "nail gun"]):
                            # Set the correct ammo type
                            correct_ammo_type = self._get_ammo_type_for_weapon(weapon_id)
                            current_ammo_type = poss.get("crc_AmmoType", "")
                            
                            # Only update if needed
                            if current_ammo_type != correct_ammo_type:
                                poss.set("crc_AmmoType", correct_ammo_type)
                                self.logger.debug(f"Reset RDA weapon {item_name} to ammo type {correct_ammo_type}")
        
        # Reset Na'vi weapons
        avatar = profile.find("Possessions_Avatar")
        if avatar is not None:
            possessions = avatar.find("Posessions")
            if possessions is not None:
                # Reset each weapon to its correct ammo type
                for poss in possessions.findall("Poss"):
                    weapon_id = poss.get("crc_ItemID")
                    # Only process actual weapons
                    if weapon_id in self.item_mappings:
                        item_name = self.item_mappings[weapon_id]
                        if any(weapon_keyword in item_name.lower() for weapon_keyword in 
                            ["bow", "staff", "spear", "club", "dart"]):
                            # Set the correct ammo type
                            correct_ammo_type = self._get_ammo_type_for_weapon(weapon_id)
                            current_ammo_type = poss.get("crc_AmmoType", "")
                            
                            # Only update if needed
                            if current_ammo_type != correct_ammo_type:
                                poss.set("crc_AmmoType", correct_ammo_type)
                                self.logger.debug(f"Reset Na'vi weapon {item_name} to ammo type {correct_ammo_type}")
        
        # Update the UI to reflect changes
        self._update_loadout_display(profile)
        self._update_navi_loadout_display(profile)
        
        # Mark as unsaved
        self.main_window.unsaved_label.config(text="Unsaved Changes")
        
        # Show confirmation
        messagebox.showinfo("Reset Complete", "All weapons have been reset to their original ammo types.")

    def _preserve_faction(self, profile, faction_value="1"):
        """Ensure faction stays preserved (prevents resets to Undecided)"""
        # Look for Metagame directly from the main window's tree
        root = self.main_window.tree.getroot()
        metagame = root.find("Metagame")
        
        if metagame is not None:
            # Always set the faction to the specified value (usually Na'vi/1)
            current = metagame.get("PlayerFaction")
            if current != faction_value:
                print(f"DEBUG: Fixing faction reset. Changed from {current} to {faction_value}")
                metagame.set("PlayerFaction", faction_value)
                
                # Also update the UI dropdown to match
                faction_map = {"0": "Undecided", "1": "Na'vi", "2": "RDA"}
                if "PlayerFaction" in self.entries:
                    self.entries["PlayerFaction"].set(faction_map.get(faction_value, "Undecided"))

    def _on_navi_weapon_selected(self, event, slot_index):
        """Handle the selection of a weapon from the Na'vi dropdown"""
        combo = event.widget
        selected_weapon = combo.get()
        
        # Skip if empty selection
        if selected_weapon == "-Empty-":
            return
        
        # Find the item ID from the selected weapon name
        weapon_id = None
        for item_id, item_name in self.navi_weapon_slots[slot_index]["all_weapons"].items():
            if item_name == selected_weapon:
                weapon_id = item_id
                break
        
        if weapon_id is None:
            return
            
        # Update the XML when we have a valid save file
        if self.main_window.tree is not None:
            profile = self.main_window.tree.getroot().find("PlayerProfile")
            if profile is not None:
                # Determine if it's an RDA or Na'vi weapon by the prefix
                if "[RDA]" in selected_weapon:
                    # Add RDA weapon to Na'vi inventory
                    self._update_navi_weapon(profile, slot_index, weapon_id)
                else:
                    # Add Na'vi weapon to Na'vi inventory
                    self._update_navi_weapon(profile, slot_index, weapon_id)
                    
        # Mark as unsaved
        self.main_window.unsaved_label.config(text="Unsaved Changes")

        if "[RDA]" in selected_weapon:
            # Ensure faction stays as Na'vi after equipping RDA weapon
            root = profile.getroot()
            metagame = root.find("Metagame")
            if metagame is not None and metagame.get("PlayerFaction") != "1":
                # Force Na'vi faction if it was changed
                metagame.set("PlayerFaction", "1")
                print("DEBUG: Restored Na'vi faction that was changed during RDA weapon equip")
                
                # Also update the UI dropdown to match
                if "PlayerFaction" in self.entries:
                    self.entries["PlayerFaction"].set("Na'vi")

        self._preserve_faction(profile, "1")

    def _on_weapon_selected(self, event, slot_index):
        """Handle the selection of a weapon from the RDA dropdown"""
        combo = event.widget
        selected_weapon = combo.get()
        
        # Skip if empty selection
        if selected_weapon == "-Empty-":
            return
        
        # Find the item ID from the selected weapon name
        weapon_id = None
        for item_id, item_name in self.weapon_slots[slot_index]["all_weapons"].items():
            if item_name == selected_weapon:
                weapon_id = item_id
                break
        
        if weapon_id is None:
            return
            
        # Update the XML when we have a valid save file
        if self.main_window.tree is not None:
            profile = self.main_window.tree.getroot().find("PlayerProfile")
            if profile is not None:
                # Update RDA weapon
                self._update_rda_weapon(profile, slot_index, weapon_id)
                    
        # Mark as unsaved
        self.main_window.unsaved_label.config(text="Unsaved Changes")

        self._preserve_faction(profile, "2")

    def _update_rda_weapon(self, profile, slot_index, weapon_id):
        """Update RDA weapon in the XML structure"""
        # Find the Possessions_Soldier element
        soldier = profile.find("Possessions_Soldier")
        if soldier is None:
            return
            
        # Find the EquippedWeapons element
        equipped = soldier.find("EquippedWeapons")
        if equipped is None:
            return
            
        # Get the weapon slots
        slots = equipped.findall("Slot")
        if slot_index >= len(slots):
            return
            
        # Find Posessions element
        possessions = soldier.find("Posessions")
        if possessions is None:
            return
            
        # Get the ammo entry value
        ammo_count = self.weapon_slots[slot_index]["ammo_entry"].get()
        try:
            ammo_count = int(ammo_count)
        except ValueError:
            ammo_count = 0
            
        # Determine the next available index for a new possession
        existing_indices = [int(poss.get("Index")) for poss in possessions.findall("Poss")]
        next_index = 0
        while next_index in existing_indices:
            next_index += 1
        next_index_str = str(next_index)
        
        # Get the appropriate ammo type for this weapon
        ammo_type = self._get_ammo_type_for_weapon(weapon_id)
        
        # Create or update a possession for this weapon
        weapon_poss = None
        for poss in possessions.findall("Poss"):
            if poss.get("crc_ItemID") == weapon_id:
                weapon_poss = poss
                break
                
        if weapon_poss is None:
            # Find the last element to copy its formatting
            last_poss = None
            for poss in possessions.findall("Poss"):
                last_poss = poss
            
            # Create new element with same formatting
            weapon_poss = ET.SubElement(possessions, "Poss")
            weapon_poss.set("Index", next_index_str)
            weapon_poss.set("crc_ItemID", weapon_id)
            weapon_poss.set("NbInStack", "1")
            weapon_poss.set("NbInClip", str(ammo_count))
            weapon_poss.set("crc_AmmoType", ammo_type)
            weapon_poss.set("NoveltyState", "2")
            
            # Copy the tail from the last element to preserve formatting
            if last_poss is not None and hasattr(last_poss, 'tail'):
                weapon_poss.tail = last_poss.tail
            
            # If this weapon uses ammo, also add the ammo to the inventory
            if ammo_type != "4294967295":
                # Add ammo - find if it already exists
                ammo_poss = None
                for poss in possessions.findall("Poss"):
                    if poss.get("crc_ItemID") == ammo_type:
                        ammo_poss = poss
                        break
                        
                if ammo_poss is None:
                    # Create new ammo entry
                    ammo_index = next_index + 1
                    while ammo_index in existing_indices:
                        ammo_index += 1
                        
                    ammo_poss = ET.SubElement(possessions, "Poss")
                    ammo_poss.set("Index", str(ammo_index))
                    ammo_poss.set("crc_ItemID", ammo_type)
                    ammo_poss.set("NbInStack", "100")  # Give a decent amount of ammo
                    ammo_poss.set("NbInClip", "0")
                    ammo_poss.set("crc_AmmoType", "4294967295")
                    ammo_poss.set("NoveltyState", "2")
                    
                    # Copy the tail formatting here too
                    if weapon_poss is not None and hasattr(weapon_poss, 'tail'):
                        ammo_poss.tail = weapon_poss.tail
        else:
            # Use existing entry
            weapon_poss.set("NbInClip", str(ammo_count))
            weapon_poss.set("crc_AmmoType", ammo_type)  # Make sure ammo type is correct
            next_index_str = weapon_poss.get("Index")
            
        # Update the equipped weapon slot
        slot = slots[slot_index]
        slot.set("MainHand_PossIdx", next_index_str)
        
        # Update the display
        self._update_loadout_display(profile)

        self._preserve_faction(profile, "2")

    def _get_ammo_type_for_weapon(self, weapon_id: str) -> str:
        """Determine the correct ammo type for a given weapon ID"""
        # Default ammo type (no ammo)
        default_ammo = "4294967295"
        
        # Mapping of weapons to their ammo types
        weapon_ammo_map = {
            # RDA weapons
            "1042188764": "4294967295",  # Dual Wasp Pistol I - No ammo (infinity)
            "815885611": "4294967295",   # Dual Wasp Pistol II
            "760079057": "4294967295",   # Dual Wasp Pistol III
            "999316102": "4294967295",   # Dual Wasp Pistol IV
            
            "1130814347": "4029490973",  # Standard Issue Rifle TERRA I - Rifle Ammo
            "1306083196": "4029490973",  # Standard Issue Rifle EURYS II
            "3628031700": "4029490973",  # Standard Issue Rifle SOLARIS III
            "1146928137": "4029490973",  # Standard Issue Rifle SOLARIS IV
            
            "2313824646": "2220072441",  # Combat Shotgun PHALANX I - Shotgun Ammo
            "2270547313": "2220072441",  # Combat Shotgun PHALANX II
            "2789519003": "2220072441",  # Combat Shotgun PHALANX III
            "1919695864": "2220072441",  # Combat Shotgun PHALANX IV
            
            "2397981034": "3183424835",  # Assault Rifle TERRA I - SMG Ammo
            "2152836509": "3183424835",  # Assault Rifle EURYS II
            "268371112": "3183424835",   # Assault Rifle SOLARIS III
            "466145020": "3183424835",   # Assault Rifle SOLARIS IV
            
            "85991974": "3227899887",    # BANISHER M60 Machine Gun I - Grenade Ammo
            "195020497": "3227899887",   # BANISHER M60 Machine Gun II
            "1881065336": "3227899887",  # BANISHER M60 Machine Gun III
            "1796958374": "3227899887",  # BANISHER M60 Machine Gun IV
            
            "94681171": "4198025789",    # Grenade Launcher M222 - I - Rocket Ammo
            "186342564": "4198025789",   # Grenade Launcher M222 - II
            "1349633617": "4198025789",  # Grenade Launcher M222 - III
            "4018216358": "4198025789",  # Grenade Launcher M222 - IV
            
            "2529862352": "2442117335",  # Flamethrower VESUPYRE I - LMG Ammo
            "2557822503": "2442117335",  # Flamethrower STERILATOR II
            "609450705": "2442117335",   # Flamethrower BUSHBOSS III
            "2288255787": "2442117335",  # Flamethrower BUSHBOSS IV
            
            "2548581230": "3819023512",  # Nail Gun HAMMER I - Heavy Ammo
            "2572658585": "3819023512",  # Nail Gun HAMMER II
            "143378107": "3819023512",   # Nail Gun HAMMER III
            "1911864170": "3819023512",  # Nail Gun HAMMER IV
            
            # Na'vi Weapons (unchanged)
            "1132447925": "1042656528",  # Na'vi Bow - Arrow Ammo
            "172062103": "1042656528",   # Great Bow - Arrow Ammo
            "982090295": "1042656528",   # War Bow - Arrow Ammo
            "1048019290": "1042656528",  # Hunter Bow - Arrow Ammo
            "2092736556": "435601722",   # Na'vi Spear - Spear Ammo
            "535013914": "435601722",    # Battle Staff - Spear Ammo
            "1662469074": "3069972540",  # Poison Dart - Poison Ammo
            "1839769381": "3069972540",  # Stinger - Poison Ammo
            
            # Unknown Na'vi items
            "3400058396": "3069972540",  # Unknown Na'vi Item 1 - Poison Ammo
            "371977402": "435601722",    # Unknown Na'vi Item 2 - Spear Ammo
            "958613249": "1042656528",   # Unknown Na'vi Item 6 - Arrow Ammo
            "921966990": "1042656528",   # Unknown Na'vi Item 16 - Arrow Ammo
        }
        
        # Return the appropriate ammo type for the weapon, or default if not found
        return weapon_ammo_map.get(weapon_id, default_ammo)

    def _update_navi_weapon(self, profile, slot_index, weapon_id):
        """Update Na'vi weapon in the XML structure"""
        # Find the Possessions_Avatar element
        avatar = profile.find("Possessions_Avatar")
        if avatar is None:
            return
                
        # Find the EquippedWeapons element
        equipped = avatar.find("EquippedWeapons")
        if equipped is None:
            return
                
        # Get the weapon slots
        slots = equipped.findall("Slot")
        if slot_index >= len(slots):
            return
                
        # Find Posessions element
        possessions = avatar.find("Posessions")
        if possessions is None:
            return
                
        # Get the ammo entry value
        ammo_count = self.navi_weapon_slots[slot_index]["ammo_entry"].get()

        try:
            ammo_count = int(ammo_count)
        except ValueError:
            ammo_count = 0
                
        # Determine the next available index for a new possession
        existing_indices = [int(poss.get("Index")) for poss in possessions.findall("Poss")]
        next_index = 0
        while next_index in existing_indices:
            next_index += 1
        next_index_str = str(next_index)
        
        # Get the appropriate ammo type for this weapon
        ammo_type = self._get_ammo_type_for_weapon(weapon_id)
        
        # Create or update a possession for this weapon
        weapon_poss = None
        for poss in possessions.findall("Poss"):
            if poss.get("crc_ItemID") == weapon_id:
                weapon_poss = poss
                break
                    
        if weapon_poss is None:
            # Create a new entry
            # Find the last element to copy its formatting
            last_poss = None
            for poss in possessions.findall("Poss"):
                last_poss = poss
            
            # Create new element with same formatting
            weapon_poss = ET.SubElement(possessions, "Poss")
            weapon_poss.set("Index", next_index_str)
            weapon_poss.set("crc_ItemID", weapon_id)
            weapon_poss.set("NbInStack", "1")
            weapon_poss.set("NbInClip", str(ammo_count))
            weapon_poss.set("crc_AmmoType", ammo_type)
            weapon_poss.set("NoveltyState", "2")
            
            # Copy the tail from the last element to preserve formatting
            if last_poss is not None and hasattr(last_poss, 'tail'):
                weapon_poss.tail = last_poss.tail
            
            # If this weapon uses ammo, also add the ammo to the inventory
            if ammo_type != "4294967295":
                # Add ammo - find if it already exists
                ammo_poss = None
                for poss in possessions.findall("Poss"):
                    if poss.get("crc_ItemID") == ammo_type:
                        ammo_poss = poss
                        break
                        
                if ammo_poss is None:
                    # Create new ammo entry
                    ammo_index = next_index + 1
                    while ammo_index in existing_indices:
                        ammo_index += 1
                        
                    ammo_poss = ET.SubElement(possessions, "Poss")
                    ammo_poss.set("Index", str(ammo_index))
                    ammo_poss.set("crc_ItemID", ammo_type)
                    ammo_poss.set("NbInStack", "100")  # Give a decent amount of ammo
                    ammo_poss.set("NbInClip", "0")
                    ammo_poss.set("crc_AmmoType", "4294967295")
                    ammo_poss.set("NoveltyState", "2")
                    
                    # Copy the tail formatting here too
                    if weapon_poss is not None and hasattr(weapon_poss, 'tail'):
                        ammo_poss.tail = weapon_poss.tail
        else:
            # Use existing entry
            weapon_poss.set("NbInClip", str(ammo_count))
            weapon_poss.set("crc_AmmoType", ammo_type)  # Make sure ammo type is correct
            next_index_str = weapon_poss.get("Index")
                
        # Update the equipped weapon slot
        slot = slots[slot_index]
        slot.set("MainHand_PossIdx", next_index_str)
        
        # Update the display
        self._update_navi_loadout_display(profile)

        self._preserve_faction(profile, "1")

    def _update_metagame_player_info(self, metagame: ET.Element) -> None:
        """Update player EP information from Metagame"""
        # Find Player0 element
        player0 = metagame.find("Player0")
        if player0 is not None:
            # Get EPs and newEPs values
            eps_value = player0.get("EPs", "0")
            new_eps_value = player0.get("newEPs", "0")
            
            # Update the input fields
            if "EPs" in self.entries:
                self.entries["EPs"].delete(0, tk.END)
                self.entries["EPs"].insert(0, eps_value)
                
            if "newEPs" in self.entries:
                self.entries["newEPs"].delete(0, tk.END)
                self.entries["newEPs"].insert(0, new_eps_value)

    def _max_out_level(self):
        """Max out the experience based on selected faction"""
        try:
            # Get current faction
            faction_widget = self.entries["PlayerFaction"]
            faction = faction_widget.get()
            
            # Set appropriate EP value based on faction
            if faction in ["Navi", "Na'vi"]:
                max_ep = 500000  # Max EP for Na'vi
            else:  # RDA or Undecided
                max_ep = 500000  # Max EP for RDA
            
            # Get current EP value
            ep_widget = self.entries["TotalEP"]
            current_ep_text = ep_widget.cget("text") if isinstance(ep_widget, ttk.Label) else ep_widget.get()
            
            # Extract numeric EP value
            if "/" in current_ep_text:
                current_ep = current_ep_text.split("/")[0]
            else:
                current_ep = current_ep_text
                
            # Check if already at max EP
            if int(current_ep) >= max_ep:
                messagebox.showinfo("Already Maxed Out", 
                                f"Your character already has maximum amount EP ({max_ep}) for the {faction} faction.")
                return
            
            # Update the EP display with formatted text
            formatted_ep = f"{max_ep}/{max_ep} (Max EP)"
            if isinstance(ep_widget, ttk.Label):
                ep_widget.config(text=formatted_ep)
            else:
                ep_widget.delete(0, tk.END)
                ep_widget.insert(0, formatted_ep)
            
            # Update BaseInfo TotalEP if tree exists
            if self.main_window.tree is not None:
                base_info = self.main_window.tree.getroot().find(".//BaseInfo")
                if base_info is not None:
                    base_info.set("TotalEP", str(max_ep))
            
            # Mark changes as unsaved
            self._mark_unsaved_changes()
            
            # Show success message
            messagebox.showinfo("EP Maxed Out", 
                            f"Successfully set experience to maximum amout ({max_ep}) for the {faction} faction.")
            
        except Exception as e:
            self.logger.error(f"Error maxing out level: {str(e)}")
            messagebox.showerror("Error", f"Failed to max out level: {str(e)}")

    def _name_vec_to_string(self, name_vec: str) -> str:
        """Convert a name vector to a readable string"""
        try:
            self.logger.debug(f"[NAME_VEC] Converting name vector: {name_vec}")
            
            if not name_vec or not name_vec.startswith("Count("):
                self.logger.debug("[NAME_VEC] Invalid name vector format")
                return ""
            
            # Extract the ASCII values
            parts = name_vec.split(") ")
            if len(parts) < 2:
                self.logger.debug(f"[NAME_VEC] Unexpected name vector format: {name_vec}")
                return ""
            
            values = parts[1].rstrip(";").split(";")
            self.logger.debug(f"[NAME_VEC] Extracted ASCII values: {values}")
            
            # Convert ASCII values to characters
            name = "".join(chr(int(val)) for val in values if val)
            
            self.logger.debug(f"[NAME_VEC] Converted name: {name}")
            return name
        except Exception as e:
            self.logger.error(f"[NAME_VEC] Error converting name vector to string: {str(e)}", exc_info=True)
            return ""
    
    def _string_to_name_vec(self, name: str) -> str:
        """Convert a string to a name vector format"""
        try:
            # Convert each character to ASCII value
            ascii_values = [str(ord(c)) for c in name]
            return f"Count({len(ascii_values)}) {';'.join(ascii_values)};"
        except Exception as e:
            self.logger.error(f"Error converting string to name vector: {str(e)}")
            return "Count(0) "

    def _get_avatar_weapons(self, profile: ET.Element) -> dict:
        weapons_data = {}
        avatar = profile.find("Possessions_Avatar")
        if avatar is not None:
            equipped = avatar.find("EquippedWeapons")
            if equipped is not None:
                # Get all weapon slots
                for slot in equipped.findall("Slot"):
                    main_hand = slot.get("MainHand_PossIdx", "-1")
                    off_hand = slot.get("OffHand_PossIdx", "-1")
                    weapons_data[len(weapons_data)] = {
                        "main": main_hand,
                        "off": off_hand
                    }
        return weapons_data

    def _get_avatar_weapon_info(self, profile: ET.Element, index: str) -> dict:
        """Get Na'vi weapon name and details from possession index"""
        if index == "-1":
            return None
                
        avatar = profile.find("Possessions_Avatar")
        if avatar is not None:
            possessions = avatar.find("Posessions")
            if possessions is not None:
                for poss in possessions.findall("Poss"):
                    if poss.get("Index") == index:
                        item_id = poss.get("crc_ItemID")
                        ammo_type = poss.get("crc_AmmoType", "4294967295")
                        item_name = self._get_item_name(item_id)
                        
                        weapon_info = {
                            "id": item_id,
                            "name": item_name,
                            "ammo": poss.get("NbInClip", "0"),
                            "stack": poss.get("NbInStack", "0")
                        }
                        
                        if ammo_type != "4294967295":  # If not infinite ammo
                            total_ammo = "0"
                            for ammo_poss in possessions.findall("Poss"):
                                if ammo_poss.get("crc_ItemID") == ammo_type:
                                    total_ammo = ammo_poss.get("NbInStack", "0")
                                    print(f"DEBUG: Found ammo for weapon {item_name}: {total_ammo}")
                                    break
                            weapon_info["total_ammo"] = total_ammo
                        
                        # Check if weapon has infinite ammo
                        weapon_info["infinite_ammo"] = (
                            ammo_type == "4294967295" and 
                            not any(melee_term in item_name.lower() for melee_term in ["staff", "club", "melee"])
                        )
                        
                        return weapon_info
        return None
    
    def _get_navi_armor_info(self, profile: ET.Element) -> dict:
        """Get Na'vi armor info for each slot from Posessions"""
        armor_slots = {"headwear": None, "torso": None, "legs": None}
        
        avatar = profile.find("Possessions_Avatar")
        if avatar is not None:
            equipped_armors = avatar.find("EquippedArmors")
            if equipped_armors is not None:
                # Get all slots
                slots = equipped_armors.findall("Slot")
                if len(slots) >= 3:  # Ensure we have all three slots
                    # Map slots to armor types (first is headwear, second is torso, third is legs)
                    slot_mapping = {0: "headwear", 1: "torso", 2: "legs"}
                    
                    for idx, slot in enumerate(slots[:3]):  # Process first three slots
                        armor_idx = slot.get("PossIdx", "-1")
                        
                        # Skip if no armor in this slot
                        if armor_idx == "-1":
                            continue
                            
                        possessions = avatar.find("Posessions")
                        if possessions is not None:
                            for poss in possessions.findall("Poss"):
                                if poss.get("Index") == armor_idx:
                                    item_id = poss.get("crc_ItemID")
                                    if item_id:
                                        armor_slots[slot_mapping[idx]] = {
                                            "id": item_id,
                                            "name": self._get_item_name(item_id)
                                        }
        return armor_slots

    def _create_navi_armor_mappings(self):
        """Create mappings for Na'vi armor pieces by type"""
        self.navi_armor_sets = {
            "headwear": {
                "236713729": "Na'vi Medium Armor",
                "3529616870": "Stealth Cloak",
                # Add RDA headwear
                "433486271": "[RDA] Default RDA Head",
                "4082430736": "[RDA] Titan Head",
                "149499402": "[RDA] Militum Head",
                "1593826001": "[RDA] Kodiak Head",
                "3527939275": "[RDA] Exotant Head",
                "403319592": "[RDA] Centauri Head",
                "3753317026": "[RDA] Hydra Head",
                "2823901304": "[RDA] Warthog Head",
                "3980056687": "[RDA] Viper Head"
            },
            "torso": {
                "2228061969": "Na'vi Heavy Armor", 
                "1641566717": "Hunter's Mark",
                # Add RDA torso armor
                "-1": "[RDA] Default RDA Torso",
                "205852157": "[RDA] Titan Torso",
                "4160278759": "[RDA] Militum Torso",
                "2716738620": "[RDA] Kodiak Torso",
                "1193780569": "[RDA] Exotant Torso",
                "3877361093": "[RDA] Centauri Torso",
                "1851965193": "[RDA] Hydra Torso",
                "1981144899": "[RDA] Warthog Torso",
                "3574042272": "[RDA] Viper Torso"
            },
            "legs": {
                "753645081": "Na'vi Light Armor",
                "540413008": "Sacred Totem",
                # Add RDA leg armor
                "-1": "[RDA] Default RDA Legs",
                "1052486966": "[RDA] Titan Legs",
                "3305533484": "[RDA] Militum Legs",
                "2467333367": "[RDA] Kodiak Legs",
                "1379870057": "[RDA] Exotant Legs",
                "3588584718": "[RDA] Centauri Legs",
                "2428117146": "[RDA] Hydra Legs",
                "2056338139": "[RDA] Warthog Legs",
                "1417888964": "[RDA] Viper Legs"
            }
        }

        # Create reverse mappings for looking up IDs by name
        self.navi_armor_ids = {
            slot_type: {name: id for id, name in items.items()}
            for slot_type, items in self.navi_armor_sets.items()
        }

    def _update_navi_armor(self, profile: ET.Element, slot_type: str, armor_name: str) -> None:
        """Detailed debug version of Na'vi armor update method"""
        print(f"DEBUG: Updating Na'vi armor - Slot: {slot_type}, Armor: {armor_name}")
        
        # Detailed logging of available armor mappings
        print("DEBUG: Available Na'vi Armor IDs:")
        for slot, armor_dict in self.navi_armor_ids.items():
            print(f"  {slot}: {armor_dict}")
        
        # Get the armor ID from the name
        armor_id = self.navi_armor_ids[slot_type].get(armor_name)
        print(f"DEBUG: Armor ID found: {armor_id}")
        
        if armor_id is None:
            print(f"ERROR: No armor ID found for {armor_name} in {slot_type}")
            return

        # Find Possessions_Avatar element
        avatar = profile.find("Possessions_Avatar")
        if avatar is None:
            print("DEBUG: No Possessions_Avatar found. Creating new.")
            avatar = ET.SubElement(profile, "Possessions_Avatar")

        # Find Posessions element
        possessions = avatar.find("Posessions")
        if possessions is None:
            print("DEBUG: No Posessions found. Creating new.")
            possessions = ET.SubElement(avatar, "Posessions")

        # Find EquippedArmors element
        equipped_armors = avatar.find("EquippedArmors")
        if equipped_armors is None:
            print("DEBUG: No EquippedArmors found. Creating new.")
            equipped_armors = ET.SubElement(avatar, "EquippedArmors")

        # Slot mapping logic
        slot_mapping = {"headwear": 0, "torso": 1, "legs": 2}
        slot_position = slot_mapping.get(slot_type)

        if slot_position is None:
            print(f"ERROR: Invalid slot type: {slot_type}")
            return

        # Ensure slots are initialized
        while len(equipped_armors.findall("Slot")) < 3:
            ET.SubElement(equipped_armors, "Slot")

        # Get all slots
        slots = equipped_armors.findall("Slot")

        # Print current slot configurations
        print("DEBUG: Current Slot Configurations:")
        for i, slot in enumerate(slots):
            print(f"  Slot {i}: PossIdx = {slot.get('PossIdx', 'N/A')}")

        # Print all current Poss entries
        print("DEBUG: Current Poss Entries:")
        for poss in possessions.findall("Poss"):
            print(f"  Index: {poss.get('Index')}, ItemID: {poss.get('crc_ItemID')}")

        if armor_name == "-Empty-":
            print("DEBUG: Setting slot to empty")
            slots[slot_position].set("PossIdx", "-1")
        else:
            # Find or create the appropriate Poss entry
            existing_poss = None
            for poss in possessions.findall("Poss"):
                if poss.get("crc_ItemID") == armor_id:
                    existing_poss = poss
                    break

            if existing_poss is not None:
                # Use existing Poss entry
                existing_index = existing_poss.get("Index")
                print(f"DEBUG: Using existing Poss entry with Index {existing_index}")
                slots[slot_position].set("PossIdx", existing_index)
            else:
                # Create new Poss entry
                print("DEBUG: Creating new Poss entry")
                
                # Determine next available index
                current_indices = set(poss.get("Index") for poss in possessions.findall("Poss"))
                new_index = "0"
                while new_index in current_indices:
                    new_index = str(int(new_index) + 1)

                new_poss = ET.SubElement(possessions, "Poss")
                new_poss.set("Index", new_index)
                new_poss.set("crc_ItemID", armor_id)

                print(f"DEBUG: New Poss entry created with Index {new_index}")
                slots[slot_position].set("PossIdx", new_index)

        # Mark changes as unsaved
        self.main_window.unsaved_label.config(text="Unsaved Changes")
        print(f"DEBUG: Updated Na'vi {slot_type} armor to {armor_name}")

    def _on_navi_armor_selected(self, event, slot_type):
        """Handle Na'vi armor selection change"""
        combo = event.widget
        selected_armor = combo.get()
        
        # Skip if empty selection
        if selected_armor == "-Empty-":
            return
        
        # Check if this is an RDA armor (has [RDA] prefix)
        is_rda_armor = "[RDA]" in selected_armor
        
        # Clean the armor name if it has a faction prefix
        if is_rda_armor:
            armor_name = selected_armor.replace("[RDA] ", "")
            # Get the ID from RDA armor mappings
            armor_id = None
            for id, name in self.rda_armor_sets[slot_type].items():
                if name == armor_name:
                    armor_id = id
                    break
        else:
            armor_name = selected_armor
            # Get the ID from Na'vi mappings
            armor_id = self.navi_armor_ids[slot_type].get(armor_name)
        
        # Update the XML
        if self.main_window.tree is not None:
            profile = self.main_window.tree.getroot().find("PlayerProfile")
            if profile is not None:
                if is_rda_armor:
                    # Adding RDA armor to Na'vi inventory
                    self._add_rda_armor_to_navi(profile, slot_type, armor_id)
                else:
                    # Regular Na'vi armor handling - modify this part to use dynamic indices
                    avatar = profile.find("Possessions_Avatar")
                    if avatar is None:
                        return
                    
                    # Find posessions element
                    possessions = avatar.find("Posessions")
                    if possessions is None:
                        return
                    
                    # Check if the armor already exists
                    existing_poss = None
                    for poss in possessions.findall("Poss"):
                        if poss.get("crc_ItemID") == armor_id:
                            existing_poss = poss
                            break
                    
                    if existing_poss is not None:
                        # Use existing possession
                        index_str = existing_poss.get("Index")
                    else:
                        # Create new possession with next available index
                        existing_indices = [int(poss.get("Index")) for poss in possessions.findall("Poss")]
                        next_index = 0
                        while next_index in existing_indices:
                            next_index += 1
                        index_str = str(next_index)
                        
                        # Find the last element to copy its formatting
                        last_poss = None
                        for poss in possessions.findall("Poss"):
                            last_poss = poss
                        
                        # Create new possession
                        new_poss = ET.SubElement(possessions, "Poss")
                        new_poss.set("Index", index_str)
                        new_poss.set("crc_ItemID", armor_id)
                        new_poss.set("NbInStack", "1")
                        new_poss.set("NbInClip", "0")
                        new_poss.set("crc_AmmoType", "4294967295")
                        new_poss.set("NoveltyState", "2")
                        
                        # Copy the tail from the last element to preserve formatting
                        if last_poss is not None and hasattr(last_poss, 'tail'):
                            new_poss.tail = last_poss.tail
                    
                    # Find EquippedArmors element
                    equipped_armors = avatar.find("EquippedArmors")
                    if equipped_armors is None:
                        equipped_armors = ET.SubElement(avatar, "EquippedArmors")
                    
                    # Slot mapping
                    slot_mapping = {"headwear": 0, "torso": 1, "legs": 2}
                    slot_position = slot_mapping[slot_type]
                    
                    # Ensure we have enough slots
                    while len(equipped_armors.findall("Slot")) <= slot_position:
                        ET.SubElement(equipped_armors, "Slot")
                    
                    # Update the appropriate slot
                    slots = equipped_armors.findall("Slot")
                    slots[slot_position].set("PossIdx", index_str)
                    
                    # Mark changes as unsaved
                    self.main_window.unsaved_label.config(text="Unsaved Changes")
                    
                    # Update the display
                    self._update_navi_loadout_display(profile)

                    self._preserve_faction(profile, "1")

    def _add_rda_armor_to_navi(self, profile, slot_type, armor_id):
        """Add RDA armor item to Na'vi inventory"""
        avatar = profile.find("Possessions_Avatar")
        if avatar is None:
            return

        # Find posessions element
        possessions = avatar.find("Posessions")
        if possessions is None:
            return

        # Determine next available index
        existing_indices = [int(poss.get("Index")) for poss in possessions.findall("Poss")]
        next_index = 0
        while next_index in existing_indices:
            next_index += 1
        next_index_str = str(next_index)
        
        # Find the last element to copy its formatting
        last_poss = None
        for poss in possessions.findall("Poss"):
            last_poss = poss
        
        # Create new possession for the RDA armor
        new_poss = ET.SubElement(possessions, "Poss")
        new_poss.set("Index", next_index_str)
        new_poss.set("crc_ItemID", armor_id)
        new_poss.set("NbInStack", "1")
        new_poss.set("NbInClip", "0")
        new_poss.set("crc_AmmoType", "4294967295")  # Armor ammo type
        new_poss.set("NoveltyState", "2")
        
        # Copy the tail from the last element to preserve formatting
        if last_poss is not None and hasattr(last_poss, 'tail'):
            new_poss.tail = last_poss.tail

        # Find EquippedArmors element
        equipped_armors = avatar.find("EquippedArmors")
        if equipped_armors is None:
            equipped_armors = ET.SubElement(avatar, "EquippedArmors")

        # Slot mapping
        slot_mapping = {"headwear": 0, "torso": 1, "legs": 2}
        slot_position = slot_mapping[slot_type]

        # Ensure we have enough slots
        while len(equipped_armors.findall("Slot")) <= slot_position:
            ET.SubElement(equipped_armors, "Slot")

        # Update the appropriate slot
        slots = equipped_armors.findall("Slot")
        slots[slot_position].set("PossIdx", next_index_str)

        # Mark changes as unsaved
        self.main_window.unsaved_label.config(text="Unsaved Changes")
        
        # Update the display
        self._update_navi_loadout_display(profile)

        root = profile.getroot()
        metagame = root.find("Metagame")
        if metagame is not None and metagame.get("PlayerFaction") != "1":
            # Force Na'vi faction if it was changed
            metagame.set("PlayerFaction", "1")
            print("DEBUG: Restored Na'vi faction that was changed during RDA item equip")
            
            # Also update the UI dropdown to match
            if "PlayerFaction" in self.entries:
                self.entries["PlayerFaction"].set("Na'vi")

        self._preserve_faction(profile, "1")

    def _toggle_infinite_ammo(self, event, slot_index, is_navi=False):
        """Handle toggling infinite ammo for a weapon"""
        try:
            # Get the slot data
            slot_data = self.navi_weapon_slots[slot_index] if is_navi else self.weapon_slots[slot_index]
            
            # Get the current weapon from the dropdown
            weapon_name = slot_data["dropdown"].get()
            if weapon_name == "-Empty-":
                return
                    
            # Find weapon ID from name
            weapon_id = None
            for id, name in slot_data["all_weapons"].items():
                if name == weapon_name:
                    weapon_id = id
                    break
                        
            if weapon_id is None:
                return
                    
            # We need to wait a moment for the checkbox to update
            self.parent.after(50, lambda: self._apply_infinite_ammo(slot_index, is_navi, weapon_id))
                    
        except Exception as e:
            self.logger.error(f"Error toggling infinite ammo: {str(e)}")

    def _update_navi_loadout_display(self, profile: ET.Element) -> None:
        """Update the Na'vi loadout display with current equipment"""
        # Update weapons
        weapons = self._get_avatar_weapons(profile)
        for slot_num, slot_data in weapons.items():
            if slot_num < len(self.navi_weapon_slots):
                main_weapon = self._get_avatar_weapon_info(profile, slot_data["main"])
                
                if main_weapon:
                    # Get the dropdown for this slot
                    if "dropdown" in self.navi_weapon_slots[slot_num]:
                        weapon_name = main_weapon["name"]
                        dropdown = self.navi_weapon_slots[slot_num]["dropdown"]
                        dropdown.set(f"[Na'vi] {weapon_name}")
                        
                        # Update ammo entry
                        if "ammo_entry" in self.navi_weapon_slots[slot_num]:
                            ammo_entry = self.navi_weapon_slots[slot_num]["ammo_entry"]
                            
                            # Update ammo value
                            ammo_entry.delete(0, tk.END)
                            
                            # For weapons with infinite ammo, disable the field
                            if main_weapon.get("infinite_ammo", False):
                                ammo_entry.insert(0, "999999")
                                ammo_entry.configure(state="disabled")
                            else:
                                # For normal weapons, keep field enabled
                                ammo_entry.insert(0, main_weapon.get("total_ammo", "0"))
                                ammo_entry.configure(state="normal")
                        
                        # Update clip size label - CHANGED to work with label instead of entry
                        if "clip_entry" in self.navi_weapon_slots[slot_num]:
                            clip_label = self.navi_weapon_slots[slot_num]["clip_entry"]
                            clip_label.config(text=main_weapon["ammo"])
                        
                        # Set infinite ammo checkbox based on weapon info
                        if "infinite_var" in self.navi_weapon_slots[slot_num]:
                            infinite_var = self.navi_weapon_slots[slot_num]["infinite_var"]
                            is_infinite = main_weapon.get("infinite_ammo", False)
                            infinite_var.set(is_infinite)
                else:
                    # Set to empty if no weapon
                    if "dropdown" in self.navi_weapon_slots[slot_num]:
                        self.navi_weapon_slots[slot_num]["dropdown"].set("-Empty-")
                        
                        # Reset ammo entry
                        if "ammo_entry" in self.navi_weapon_slots[slot_num]:
                            ammo_entry = self.navi_weapon_slots[slot_num]["ammo_entry"]
                            ammo_entry.delete(0, tk.END)
                            ammo_entry.insert(0, "0")
                            ammo_entry.configure(state="normal")
                        
                        # Reset clip label - CHANGED for label
                        if "clip_entry" in self.navi_weapon_slots[slot_num]:
                            clip_label = self.navi_weapon_slots[slot_num]["clip_entry"]
                            clip_label.config(text="0")
                        
                        # Reset infinite ammo checkbox
                        if "infinite_var" in self.navi_weapon_slots[slot_num]:
                            self.navi_weapon_slots[slot_num]["infinite_var"].set(False)

        # Update armor dropdowns
        armor_info = self._get_navi_armor_info(profile)
        for slot_type, dropdown in self.navi_armor_dropdowns.items():
            if armor_info[slot_type]:
                dropdown.set(armor_info[slot_type]["name"])
            else:
                dropdown.set("-Empty-")
                
    def _get_equipped_weapons(self, profile: ET.Element) -> dict:
        weapons_data = {}
        soldier = profile.find("Possessions_Soldier")
        if soldier is not None:
            equipped = soldier.find("EquippedWeapons")
            if equipped is not None:
                # Get all weapon slots
                for slot in equipped.findall("Slot"):
                    main_hand = slot.get("MainHand_PossIdx", "-1")
                    off_hand = slot.get("OffHand_PossIdx", "-1")
                    weapons_data[len(weapons_data)] = {
                        "main": main_hand,
                        "off": off_hand
                    }
        return weapons_data

    def _get_weapon_info(self, profile: ET.Element, index: str) -> dict:
        """Get weapon name and details from possession index"""
        if index == "-1":
            return None
                
        soldier = profile.find("Possessions_Soldier")
        if soldier is not None:
            possessions = soldier.find("Posessions")
            if possessions is not None:
                for poss in possessions.findall("Poss"):
                    if poss.get("Index") == index:
                        item_id = poss.get("crc_ItemID")
                        ammo_type = poss.get("crc_AmmoType", "4294967295")
                        item_name = self._get_item_name(item_id)
                        
                        weapon_info = {
                            "id": item_id,
                            "name": item_name,
                            "ammo": poss.get("NbInClip", "0"),
                            "stack": poss.get("NbInStack", "0")
                        }
                        
                        if ammo_type != "4294967295":  # If not infinite ammo
                            total_ammo = "0"
                            for ammo_poss in possessions.findall("Poss"):
                                if ammo_poss.get("crc_ItemID") == ammo_type:
                                    total_ammo = ammo_poss.get("NbInStack", "0")
                                    print(f"DEBUG: Found ammo for weapon {item_name}: {total_ammo}")
                                    break
                            weapon_info["total_ammo"] = total_ammo
                        
                        # Check if weapon has infinite ammo
                        weapon_info["infinite_ammo"] = (
                            ammo_type == "4294967295" and 
                            not any(melee_term in item_name.lower() for melee_term in ["staff", "club", "melee"])
                        )
                        
                        return weapon_info
        return None
    
    def _get_armor_info(self, profile: ET.Element) -> dict:
        """Get RDA armor info for each slot (headwear, torso, legs)"""
        armor_slots = {"headwear": None, "torso": None, "legs": None}
        
        soldier = profile.find("Possessions_Soldier")
        if soldier is not None:
            equipped_armors = soldier.find("EquippedArmors")
            if equipped_armors is not None:
                # Get all slots
                slots = equipped_armors.findall("Slot")
                if len(slots) >= 3:  # Ensure we have all three slots
                    # Map slots to armor types (first is headwear, second is torso, third is legs)
                    slot_mapping = {0: "headwear", 1: "torso", 2: "legs"}
                    
                    for idx, slot in enumerate(slots[:3]):  # Process first three slots
                        armor_idx = slot.get("PossIdx", "-1")
                        
                        # Handle default outfit case
                        if armor_idx == "-1":
                            if idx == 1:  # Torso
                                armor_slots["torso"] = {"id": "-1", "name": "Default RDA Torso"}
                            elif idx == 2:  # Legs
                                armor_slots["legs"] = {"id": "-1", "name": "Default RDA Legs"}
                            continue
                            
                        possessions = soldier.find("Posessions")
                        if possessions is not None:
                            for poss in possessions.findall("Poss"):
                                if poss.get("Index") == armor_idx:
                                    item_id = poss.get("crc_ItemID")
                                    if item_id:
                                        armor_slots[slot_mapping[idx]] = {
                                            "id": item_id,
                                            "name": self._get_item_name(item_id)
                                        }
        return armor_slots

    def _create_rda_armor_mappings(self):
        """Create mappings for RDA armor pieces by type"""
        self.rda_armor_sets = {
            "headwear": {
                "433486271": "Default RDA Head",
                "4082430736": "Titan Head",
                "149499402": "Militum Head",
                "1593826001": "Kodiak Head",
                "3527939275": "Exotant Head",
                "403319592": "Centauri Head",
                "3753317026": "Hydra Head",
                "2823901304": "Warthog Head",
                "3980056687": "Viper Head",
                # Add Na'vi headwear
                "236713729": "[Na'vi] Na'vi Medium Armor",
                "3529616870": "[Na'vi] Stealth Cloak"
            },
            "torso": {
                "-1": "Default RDA Torso",
                "205852157": "Titan Torso",
                "4160278759": "Militum Torso",
                "2716738620": "Kodiak Torso",
                "1193780569": "Exotant Torso",
                "3877361093": "Centauri Torso",
                "1851965193": "Hydra Torso",
                "1981144899": "Warthog Torso",
                "3574042272": "Viper Torso",
                # Add Na'vi torso armor
                "2228061969": "[Na'vi] Na'vi Heavy Armor",
                "1641566717": "[Na'vi] Hunter's Mark"
            },
            "legs": {
                "-1": "Default RDA Legs",
                "1052486966": "Titan Legs",
                "3305533484": "Militum Legs",
                "2467333367": "Kodiak Legs",
                "1379870057": "Exotant Legs",
                "3588584718": "Centauri Legs",
                "2428117146": "Hydra Legs",
                "2056338139": "Warthog Legs",
                "1417888964": "Viper Legs",
                # Add Na'vi leg armor
                "753645081": "[Na'vi] Na'vi Light Armor",
                "540413008": "[Na'vi] Sacred Totem"
            }
        }

        # Create reverse mappings for looking up IDs by name
        self.rda_armor_ids = {
            slot_type: {name: id for id, name in items.items()}
            for slot_type, items in self.rda_armor_sets.items()
        }

    def _update_rda_armor(self, profile: ET.Element, slot_type: str, armor_name: str) -> None:
        """Update RDA armor in the XML structure"""
        soldier = profile.find("Possessions_Soldier")
        if soldier is None:
            return

        # Get the armor ID from the name
        armor_id = self.rda_armor_ids[slot_type].get(armor_name)
        if armor_id is None:
            return

        # Slot indices mapping (based on the Viper set example)
        slot_indices = {"headwear": "8", "torso": "9", "legs": "10"}
        slot_index = slot_indices[slot_type]

        # Update the equipped armor slot
        equipped_armors = soldier.find("EquippedArmors")
        if equipped_armors is not None:
            slots = equipped_armors.findall("Slot")
            slot_mapping = {"headwear": 0, "torso": 1, "legs": 2}
            slot_position = slot_mapping[slot_type]
            
            if 0 <= slot_position < len(slots):
                if armor_id == "-1":
                    slots[slot_position].set("PossIdx", "-1")
                else:
                    slots[slot_position].set("PossIdx", slot_index)
                    # Update or create the possession entry
                    possessions = soldier.find("Posessions")
                    if possessions is not None:
                        # Look for existing possession
                        found = False
                        for poss in possessions.findall("Poss"):
                            if poss.get("Index") == slot_index:
                                poss.set("crc_ItemID", armor_id)
                                found = True
                                break
                        
                        # Create new possession if not found
                        if not found:
                            new_poss = ET.SubElement(possessions, "Poss")
                            new_poss.set("Index", slot_index)
                            new_poss.set("crc_ItemID", armor_id)

        # Mark changes as unsaved
        self.main_window.unsaved_label.config(text="Unsaved Changes")

    def _on_armor_selected(self, event, slot_type):
        """Handle armor selection change"""
        combo = event.widget
        selected_armor = combo.get()
        
        # Skip if empty selection
        if selected_armor == "-Empty-":
            return
        
        # Check if this is a Na'vi armor (has [Na'vi] prefix)
        is_navi_armor = "[Na'vi]" in selected_armor
        
        # Clean the armor name if it has a faction prefix
        if is_navi_armor:
            armor_name = selected_armor.replace("[Na'vi] ", "")
            # Get the ID from Na'vi armor mappings
            armor_id = None
            for id, name in self.navi_armor_sets[slot_type].items():
                if name == armor_name:
                    armor_id = id
                    break
        else:
            armor_name = selected_armor
            # Get the ID from RDA mappings
            armor_id = self.rda_armor_ids[slot_type].get(armor_name)
        
        # Update the XML
        if self.main_window.tree is not None:
            profile = self.main_window.tree.getroot().find("PlayerProfile")
            if profile is not None:
                if is_navi_armor:
                    # Adding Na'vi armor to RDA inventory
                    self._add_navi_armor_to_rda(profile, slot_type, armor_id)
                else:
                    # Regular RDA armor handling - modify this part to use dynamic indices
                    soldier = profile.find("Possessions_Soldier")
                    if soldier is None:
                        return
                    
                    # For default items with ID "-1", just set the slot and return
                    if armor_id == "-1":
                        equipped_armors = soldier.find("EquippedArmors")
                        if equipped_armors is not None:
                            slots = equipped_armors.findall("Slot")
                            slot_mapping = {"headwear": 0, "torso": 1, "legs": 2}
                            slot_position = slot_mapping[slot_type]
                            
                            if 0 <= slot_position < len(slots):
                                slots[slot_position].set("PossIdx", "-1")
                                # Mark changes as unsaved
                                self.main_window.unsaved_label.config(text="Unsaved Changes")
                                # Update the display
                                self._update_loadout_display(profile)
                        return
                    
                    # For other armors, find or create the possession
                    possessions = soldier.find("Posessions")
                    if possessions is None:
                        return
                    
                    # Check if the armor already exists
                    existing_poss = None
                    for poss in possessions.findall("Poss"):
                        if poss.get("crc_ItemID") == armor_id:
                            existing_poss = poss
                            break
                    
                    if existing_poss is not None:
                        # Use existing possession
                        index_str = existing_poss.get("Index")
                    else:
                        # Create new possession with next available index
                        existing_indices = [int(poss.get("Index")) for poss in possessions.findall("Poss")]
                        next_index = 0
                        while next_index in existing_indices:
                            next_index += 1
                        index_str = str(next_index)
                        
                        # Find the last element to copy its formatting
                        last_poss = None
                        for poss in possessions.findall("Poss"):
                            last_poss = poss
                        
                        # Create new possession
                        new_poss = ET.SubElement(possessions, "Poss")
                        new_poss.set("Index", index_str)
                        new_poss.set("crc_ItemID", armor_id)
                        new_poss.set("NbInStack", "1")
                        new_poss.set("NbInClip", "0")
                        new_poss.set("crc_AmmoType", "4294967295")
                        new_poss.set("NoveltyState", "2")
                        
                        # Copy the tail from the last element to preserve formatting
                        if last_poss is not None and hasattr(last_poss, 'tail'):
                            new_poss.tail = last_poss.tail
                    
                    # Update the equipped slot
                    equipped_armors = soldier.find("EquippedArmors")
                    if equipped_armors is not None:
                        slots = equipped_armors.findall("Slot")
                        slot_mapping = {"headwear": 0, "torso": 1, "legs": 2}
                        slot_position = slot_mapping[slot_type]
                        
                        if 0 <= slot_position < len(slots):
                            slots[slot_position].set("PossIdx", index_str)
                    
                    # Mark changes as unsaved
                    self.main_window.unsaved_label.config(text="Unsaved Changes")
                    
                    # Update the display
                    self._update_loadout_display(profile)

                    self._preserve_faction(profile, "2")

    def _add_navi_armor_to_rda(self, profile, slot_type, armor_id):
        """Add Na'vi armor item to RDA inventory"""
        soldier = profile.find("Possessions_Soldier")
        if soldier is None:
            return

        # Find posessions element
        possessions = soldier.find("Posessions")
        if possessions is None:
            return

        # Determine next available index
        existing_indices = [int(poss.get("Index")) for poss in possessions.findall("Poss")]
        next_index = 0
        while next_index in existing_indices:
            next_index += 1
        next_index_str = str(next_index)
        
        # Find the last element to copy its formatting
        last_poss = None
        for poss in possessions.findall("Poss"):
            last_poss = poss
        
        # Create new possession for the Na'vi armor
        new_poss = ET.SubElement(possessions, "Poss")
        new_poss.set("Index", next_index_str)
        new_poss.set("crc_ItemID", armor_id)
        new_poss.set("NbInStack", "1")
        new_poss.set("NbInClip", "0")
        new_poss.set("crc_AmmoType", "4294967295")  # Armor ammo type
        new_poss.set("NoveltyState", "2")
        
        # Copy the tail from the last element to preserve formatting
        if last_poss is not None and hasattr(last_poss, 'tail'):
            new_poss.tail = last_poss.tail

        # Find EquippedArmors element
        equipped_armors = soldier.find("EquippedArmors")
        if equipped_armors is None:
            equipped_armors = ET.SubElement(soldier, "EquippedArmors")

        # Slot mapping
        slot_mapping = {"headwear": 0, "torso": 1, "legs": 2}
        slot_position = slot_mapping[slot_type]

        # Ensure we have enough slots
        while len(equipped_armors.findall("Slot")) <= slot_position:
            ET.SubElement(equipped_armors, "Slot")

        # Update the appropriate slot
        slots = equipped_armors.findall("Slot")
        slots[slot_position].set("PossIdx", next_index_str)

        # Mark changes as unsaved
        self.main_window.unsaved_label.config(text="Unsaved Changes")
        
        # Update the display
        self._update_loadout_display(profile)

        self._preserve_faction(profile, "2")

    def _update_loadout_display(self, profile: ET.Element) -> None:
        """Update the RDA loadout display with current equipment"""
        # Update weapons
        weapons = self._get_equipped_weapons(profile)
        for slot_num, slot_data in weapons.items():
            if slot_num < len(self.weapon_slots):
                main_weapon = self._get_weapon_info(profile, slot_data["main"])
                
                if main_weapon:
                    # Get the dropdown for this slot
                    if "dropdown" in self.weapon_slots[slot_num]:
                        weapon_name = main_weapon["name"]
                        dropdown = self.weapon_slots[slot_num]["dropdown"]
                        dropdown.set(f"[RDA] {weapon_name}")
                        
                        # Update ammo entry
                        if "ammo_entry" in self.weapon_slots[slot_num]:
                            ammo_entry = self.weapon_slots[slot_num]["ammo_entry"]
                            
                            # Update ammo value
                            ammo_entry.delete(0, tk.END)
                            
                            # For weapons with infinite ammo, disable the field
                            if main_weapon.get("infinite_ammo", False):
                                ammo_entry.insert(0, "999999")
                                ammo_entry.configure(state="disabled")
                            else:
                                # For normal weapons, keep field enabled
                                ammo_entry.insert(0, main_weapon.get("total_ammo", "0"))
                                ammo_entry.configure(state="normal")
                        
                        # Update clip size label - CHANGED to work with label instead of entry
                        if "clip_entry" in self.weapon_slots[slot_num]:
                            clip_label = self.weapon_slots[slot_num]["clip_entry"]
                            clip_label.config(text=main_weapon["ammo"])
                        
                        # Set infinite ammo checkbox based on weapon info
                        if "infinite_var" in self.weapon_slots[slot_num]:
                            infinite_var = self.weapon_slots[slot_num]["infinite_var"]
                            is_infinite = main_weapon.get("infinite_ammo", False)
                            infinite_var.set(is_infinite)
                else:
                    # Set to empty if no weapon
                    if "dropdown" in self.weapon_slots[slot_num]:
                        self.weapon_slots[slot_num]["dropdown"].set("-Empty-")
                        
                        # Reset ammo entry
                        if "ammo_entry" in self.weapon_slots[slot_num]:
                            ammo_entry = self.weapon_slots[slot_num]["ammo_entry"]
                            ammo_entry.delete(0, tk.END)
                            ammo_entry.insert(0, "0")
                            ammo_entry.configure(state="normal")
                        
                        # Reset clip label - CHANGED for label
                        if "clip_entry" in self.weapon_slots[slot_num]:
                            clip_label = self.weapon_slots[slot_num]["clip_entry"]
                            clip_label.config(text="0")
                        
                        # Reset infinite ammo checkbox
                        if "infinite_var" in self.weapon_slots[slot_num]:
                            self.weapon_slots[slot_num]["infinite_var"].set(False)

        # Update armor dropdowns
        armor_info = self._get_armor_info(profile)
        for slot_type, dropdown in self.armor_dropdowns.items():
            if armor_info[slot_type]:
                dropdown.set(armor_info[slot_type]["name"])
            else:
                dropdown.set("-Empty-")

    def _on_face_selected(self, event=None):
            """Handle face selection and update image"""
            try:
                widget = self.entries["face"]
                face_value = widget.cget("text") if isinstance(widget, ttk.Label) else widget.get()
                self.logger.debug(f"[FACE_SELECT] Selected face value: {face_value}")
                
                if not face_value or face_value == "-":
                    self.logger.warning("[FACE_SELECT] No face value selected")
                    return
                    
                # Validate the face value format
                parts = face_value.split()
                if len(parts) != 2 or parts[0] not in ["Male", "Female"]:
                    self.logger.error(f"[FACE_SELECT] Invalid face value format: {face_value}")
                    if hasattr(self, 'face_image_label') and self.face_image_label:
                        self.face_image_label.configure(image='')
                        self.face_image_label.configure(text=f"Invalid face format\nExpected: 'Male XX' or 'Female XX'")
                    return
                    
                gender, number = parts
                image_path = os.path.join("Face_Images", f"{gender} {number}.png")
                
                self.logger.debug(f"[FACE_SELECT] Attempting to load image: {image_path}")
                self.logger.debug(f"[FACE_SELECT] Image path exists: {os.path.exists(image_path)}")
                
                if os.path.exists(image_path):
                    self.logger.debug("[FACE_SELECT] Loading and resizing image...")
                    original_image = Image.open(image_path)
                    resized_image = original_image.resize((150, 150), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(resized_image)
                    
                    if hasattr(self, 'face_image_label') and self.face_image_label:
                        self.logger.debug("[FACE_SELECT] Updating face image label...")
                        self.face_image_label.configure(image=photo)
                        self.face_image_label.image = photo  # Keep a reference
                        
                        # Mark as unsaved changes
                        self.main_window.unsaved_label.config(text="Unsaved Changes")
                        self.logger.debug("[FACE_SELECT] Face image updated successfully")
                    else:
                        self.logger.error("[FACE_SELECT] face_image_label not available")
                else:
                    self.logger.warning(f"[FACE_SELECT] Face image not found: {image_path}")
                    if hasattr(self, 'face_image_label') and self.face_image_label:
                        self.face_image_label.configure(image='')
                        self.face_image_label.configure(text=f"No face image found\n({image_path})")
                        
            except Exception as e:
                self.logger.error(f"[FACE_SELECT] Error updating face image: {str(e)}", exc_info=True)
                if hasattr(self, 'face_image_label') and self.face_image_label:
                    self.face_image_label.configure(image='')
                    self.face_image_label.configure(text=f"Error loading image: {str(e)}")

    def _mark_unsaved_changes(self, event=None):
        """Mark the save file as having unsaved changes"""
        try:
            self.main_window.unsaved_label.config(text="Unsaved Changes")
        except Exception as e:
            self.logger.error(f"Error marking unsaved changes: {str(e)}", exc_info=True)

    def load_stats(self, tree: ET.ElementTree) -> None:
        root = tree.getroot()
        profile = root.find("PlayerProfile")

        if profile is not None:
            self._update_base_info(profile.find("BaseInfo"), tree)
            self._update_xp_info(profile.find("XpInfo"))
            self._update_options_info(profile.find("OptionsInfo"))
            self._update_time_info(profile.find("TimeInfo"))
            self._update_loadout_display(profile)  # RDA loadout
            self._update_navi_loadout_display(profile)  # Na'vi loadout

            # Look for Possessions_Recovery in PlayerProfile directly
            self._update_player_info(profile)
        
        metagame = root.find("Metagame")
        if metagame is not None:
            self._update_metagame_info(metagame)
            self._update_metagame_player_info(metagame)

    def _convert_time_to_seconds(self, formatted_time: str) -> str:
        self.logger.debug(f"Converting time format: {formatted_time}")
        try:
            hours, minutes, seconds = 0, 0, 0
            parts = formatted_time.replace('h', ' ').replace('m', ' ').replace('s', '').split()
            if len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
            total_seconds = str(hours * 3600 + minutes * 60 + seconds)
            self.logger.debug(f"Converted to seconds: {total_seconds}")
            return total_seconds
        except (ValueError, IndexError) as e:
            self.logger.error(f"Error converting time format: {str(e)}", exc_info=True)
            return formatted_time

    def update_location(self, location_value: str) -> None:
        """Update location while preserving XML structure"""
        if not self.main_window.tree:
            return

        try:
            # Find existing LocationInfo element
            location_info = self.main_window.tree.find(".//LocationInfo")
            if location_info is not None:
                # Update existing attribute
                location_info.set("YouAreHere_LatitudeLongitude", location_value)
            else:
                # Look for location attribute in other elements
                for elem in self.main_window.tree.iter():
                    if "YouAreHere_LatitudeLongitude" in elem.attrib:
                        elem.set("YouAreHere_LatitudeLongitude", location_value)
                        break

            self.main_window.unsaved_label.config(text="Unsaved Changes")
            
        except Exception as e:
            self.logger.error(f"Error updating location: {str(e)}", exc_info=True)
            raise

    def get_stats_updates(self) -> Dict[str, Dict[str, str]]:
        self.logger.debug("[STATS_UPDATE] Starting stats updates collection")
        try:

            # Check current faction in XML before updates
            if self.main_window.tree is not None:
                metagame = self.main_window.tree.getroot().find("Metagame")
                if metagame is not None:
                    current_faction_xml = metagame.get("PlayerFaction", "Unknown")
                    print(f"DEBUG: Current faction in XML before update: {current_faction_xml}")

            # Define updates dictionary that will store all our changes
            updates = {
                "BaseInfo": {},
                "XpInfo": {},
                "OptionsInfo": {},
                "TimeInfo": {},
                "Metagame": {}
            }

            # Get selected faction
            current_faction = self.entries["PlayerFaction"].get()
            faction_map = {"Undecided": "0", "Navi": "1", "RDA": "2"}
            faction_value = faction_map.get(current_faction, "0")
            
            # Get current EP value
            ep_widget = self.entries["TotalEP"]
            current_ep = ep_widget.cget("text") if isinstance(ep_widget, ttk.Label) else ep_widget.get()
            
            # Handle the new format with max value
            if "/" in current_ep:
                # Extract just the EP value
                current_ep = current_ep.split("/")[0]

            # Determine the level based on EP and faction
            current_ep_value = int(current_ep)
            if current_faction in ["Navi", "Na'vi"]:
                # Na'vi level calculation
                if current_ep_value >= 500000:
                    level = 18  # Max level for Na'vi
                else:
                    level = self._get_level_for_ep(current_ep_value, "Na'vi")
            else:
                # RDA level calculation
                if current_ep_value >= 389250:
                    level = 24  # Max level for RDA
                else:
                    level = self._get_level_for_ep(current_ep_value, "RDA")

            # Update faction setting
            updates["Metagame"]["PlayerFaction"] = faction_value
            print(f"DEBUG: Final faction value in updates: {updates['Metagame']['PlayerFaction']}")

            # Update base information
            base_fields = ["face", "TotalEP", "namevec", "RecoveryBits"]
            for field in base_fields:
                if field in self.entries:
                    widget = self.entries[field]
                    if field == "face":
                        face_value = widget.cget("text") if isinstance(widget, ttk.Label) else widget.get()
                        face_number = self._get_face_number(face_value)
                        updates["BaseInfo"][field] = face_number
                    elif field == "namevec":
                        name = widget.cget("text") if isinstance(widget, ttk.Label) else widget.get()
                        updates["BaseInfo"][field] = self._string_to_name_vec(name)
                    elif field == "RecoveryBits":
                        # For RecoveryBits, we'll save directly to Possessions_Recovery
                        value = widget.cget("text") if isinstance(widget, ttk.Label) else widget.get()
                        updates["PlayerInfo"] = {"RecoveryBits": value}
                    elif field == "TotalEP":
                        # Handle the extracted EP value
                        updates["BaseInfo"][field] = current_ep
                    else:
                        value = widget.cget("text") if isinstance(widget, ttk.Label) else widget.get()
                        updates["BaseInfo"][field] = value

            # Handle side and pawn fields (now dropdowns)
            if "side" in self.entries:
                side_value = self.entries["side"].get()
                # Convert to correct value based on dropdown selection
                updates["BaseInfo"]["side"] = "1" if side_value == "Navi" else "2"
                
            if "pawn" in self.entries:
                pawn_value = self.entries["pawn"].get()
                # Convert to correct value based on dropdown selection
                updates["BaseInfo"]["pawn"] = "1" if pawn_value == "Navi" else "2"

            # Handle yes/no fields
            widget_female = self.entries["isfemale"]
            updates["BaseInfo"]["isfemale"] = "1" if (widget_female.cget("text") if isinstance(widget_female, ttk.Label) else widget_female.get()) == "Yes" else "0"
            
            widget_scanning = self.entries["bEntityScanningEnabled"]
            updates["BaseInfo"]["bEntityScanningEnabled"] = "1" if (widget_scanning.cget("text") if isinstance(widget_scanning, ttk.Label) else widget_scanning.get()) == "Yes" else "0"

            # Update XP information - use the calculated level
            updates["XpInfo"]["iCurrentLevel"] = str(level)

            # Update game options
            widget_rumble = self.entries["RumbleEnabled"]
            updates["OptionsInfo"]["RumbleEnabled"] = "1" if widget_rumble.get() == "Yes" else "0"
            
            widget_firstperson = self.entries["FirstPersonMode"]
            updates["OptionsInfo"]["FirstPersonMode"] = "1" if widget_firstperson.get() == "Yes" else "0"

            # Update faction setting
            updates["Metagame"]["PlayerFaction"] = faction_value
            
            # Update cost reduction values
            if "NaviCostReduction" in self.entries:
                navi_cost = self.entries["NaviCostReduction"].get()
                updates["Metagame"]["NaviCostReduction"] = navi_cost
                
            if "CorpCostReduction" in self.entries:
                rda_cost = self.entries["CorpCostReduction"].get()
                updates["Metagame"]["CorpCostReduction"] = rda_cost

            if "EPs" in self.entries and "newEPs" in self.entries:
                eps_value = self.entries["EPs"].get()
                new_eps_value = self.entries["newEPs"].get()
                
                # Create a Player0 section in the updates if it doesn't exist
                if "Player0" not in updates:
                    updates["Player0"] = {}
                
                updates["Player0"]["EPs"] = eps_value
                updates["Player0"]["newEPs"] = new_eps_value

            self.logger.debug(f"Stats updates: {updates}")
            return updates             
                        
        except Exception as e:
            self.logger.error(f"Error getting stats updates: {str(e)}")
            raise

    def _on_faction_selected(self, event):
        try:
            # Get the selected faction
            selected_faction = self.entries["PlayerFaction"].get()
            
            # Get the max EP for this faction
            if selected_faction in ["Navi", "Na'vi"]:
                max_ep = 500000  # Max EP for Na'vi
            else:  # RDA or Undecided
                max_ep = 500000  # Max EP for RDA
            
            # Update the EP display format
            ep_widget = self.entries["TotalEP"]
            current_ep = ep_widget.cget("text") if isinstance(ep_widget, ttk.Label) else ep_widget.get()
            
            # Handle format conversions
            if "/" in current_ep:
                # Already in new format, extract just the EP value
                current_ep = current_ep.split("/")[0]
            
            # Update with new format
            if isinstance(ep_widget, ttk.Label):
                ep_widget.config(text=f"{current_ep}/{max_ep} (Max EP)")
            else:
                ep_widget.delete(0, tk.END)
                ep_widget.insert(0, f"{current_ep}/{max_ep} (Max EP)")
            
            # Mark changes as unsaved
            self._mark_unsaved_changes()
        except Exception as e:
            self.logger.error(f"Error in faction selection: {str(e)}")

    def _update_field_visibility(self, field_key, visible):
        """Show or hide a field based on visibility flag"""
        if field_key in self.entries:
            parent_widget = self.entries[field_key].master
            
            if visible:
                parent_widget.pack(fill=tk.X, padx=5, pady=2)
            else:
                parent_widget.pack_forget()

    def _get_level_thresholds(self, faction_type):
        """Get the level XP thresholds for the specified faction"""
        # RDA Thresholds
        rda_thresholds = [
            0,      # Level 0
            1600,   # Level 1
            4600,   # Level 2
            8000,   # Level 3
            12100,  # Level 4
            17000,  # Level 5
            38500,  # Level 6
            45750,  # Level 7
            53250,  # Level 8
            61250,  # Level 9
            70250,  # Level 10
            79750,  # Level 11
            91250,  # Level 12
            104750, # Level 13
            119250, # Level 14
            143250, # Level 15
            169250, # Level 16
            197250, # Level 17
            227250, # Level 18
            249250, # Level 19
            273250, # Level 20
            299250, # Level 21
            327250, # Level 22
            357250, # Level 23
            389250  # Level 24
        ]
        
        # Na'vi Thresholds (different values)
        navi_thresholds = [
            0,      # Level 0
            46000,   # Level 1
            54500,   # Level 2
            63500,   # Level 3
            73000,  # Level 4
            87000,  # Level 5
            103000,  # Level 6
            121000,  # Level 7
            140000,  # Level 8
            160000,  # Level 9
            181000,  # Level 10
            204000,  # Level 11
            234000,  # Level 12
            266000,  # Level 13
            300000, # Level 14
            336000, # Level 15
            374000, # Level 16
            414000, # Level 17
            500000, # Level 18
        ]
        
        # Return the appropriate thresholds based on faction type
        if faction_type == "Na'vi" or faction_type == "Navi":
            return navi_thresholds
        else:
            return rda_thresholds
                
    def _get_level_for_ep(self, ep, faction_type):
        """Find the appropriate level for a given EP amount and faction"""
        try:
            ep = int(ep)
            thresholds = self._get_level_thresholds(faction_type)
            
            # Find the correct level based on EP amount
            for level in range(len(thresholds) - 1):
                if ep < thresholds[level + 1]:
                    return level
            
            # If EP exceeds all thresholds, return max level
            return len(thresholds) - 1
        except (ValueError, TypeError):
            return 0  # Default to level 0 for invalid input

    def _on_level_selected(self, event):
        try:
            # Get current faction
            faction_widget = self.entries["PlayerFaction"]
            faction = faction_widget.get()
            print(f"DEBUG: Level selected for faction: {faction}")
            
            # Set appropriate EP value based on faction - FIXED TO HANDLE "Navi" or "Na'vi"
            if faction == "Navi" or faction == "Na'vi":
                ep_value = 500000  # Max EP for Na'vi
                print(f"DEBUG: Setting Na'vi max EP: {ep_value}")
            else:  # RDA or Undecided
                ep_value = 389250  # Max EP for RDA
                print(f"DEBUG: Setting RDA max EP: {ep_value}")
            
            # Update the EP display
            ep_widget = self.entries["TotalEP"]
            if isinstance(ep_widget, ttk.Label):
                ep_widget.config(text=str(ep_value))
            else:
                ep_widget.delete(0, tk.END)
                ep_widget.insert(0, str(ep_value))
            
            # Update BaseInfo TotalEP if tree exists
            if self.main_window.tree is not None:
                base_info = self.main_window.tree.getroot().find(".//BaseInfo")
                if base_info is not None:
                    base_info.set("TotalEP", str(ep_value))
                    print(f"DEBUG: Updated BaseInfo TotalEP attribute to {ep_value}")
            
            # Mark changes as unsaved
            self._mark_unsaved_changes()
        except Exception as e:
            print(f"ERROR in level selection: {str(e)}")
            self.logger.error(f"Error in level selection: {str(e)}")

    def _update_level_from_ep(self, event=None):
        """Update the displayed level based on the current EP and faction"""
        try:
            # Get the current TotalEP value
            ep_widget = self.entries["TotalEP"]
            ep_value = ep_widget.cget("text") if isinstance(ep_widget, ttk.Label) else ep_widget.get()
            
            if not ep_value or ep_value == "-":
                return
                    
            ep = int(ep_value)
            
            # Get current faction
            faction_widget = self.entries["PlayerFaction"]
            faction = faction_widget.get()
            
            # Determine if we should display max level
            if faction == "Na'vi" and ep >= 500000:
                level_display = "Max Level"
            elif faction != "Na'vi" and ep >= 389250:
                level_display = "Max Level"
            else:
                # Calculate the level based on faction
                level = self._get_level_for_ep(ep, faction)
                level_display = f"Level {level}"
            
            # Update the CurrentLevel display
            level_widget = self.entries["CurrentLevel"]
            level_widget.set(level_display)
            
            # Mark changes as unsaved
            self._mark_unsaved_changes()
        except Exception as e:
            self.logger.error(f"Error updating level from EP: {str(e)}")

    def _get_xp_for_level(self, level, faction_type):
        """Get the XP threshold for a specific level and faction"""
        # Explicitly handle Na'vi faction - note we're checking for both "Na'vi" and "Navi" spellings
        if faction_type == "Na'vi" or faction_type == "Navi":
            navi_thresholds = [
                0,      # Level 0
                46000,   # Level 1
                54500,   # Level 2
                63500,   # Level 3
                73000,  # Level 4
                87000,  # Level 5
                103000,  # Level 6
                121000,  # Level 7
                140000,  # Level 8
                160000,  # Level 9
                181000,  # Level 10
                204000,  # Level 11
                234000,  # Level 12
                266000,  # Level 13
                300000, # Level 14
                336000, # Level 15
                374000, # Level 16
                414000, # Level 17
                500000, # Level 18
            ]
            
            if 0 <= level < len(navi_thresholds):
                return navi_thresholds[level]
            else:
                return navi_thresholds[-1]
        else:
            rda_thresholds = [
                0,      # Level 0
                1600,   # Level 1
                4600,   # Level 2
                8000,   # Level 3
                12100,  # Level 4
                17000,  # Level 5
                38500,  # Level 6
                45750,  # Level 7
                53250,  # Level 8
                61250,  # Level 9
                70250,  # Level 10
                79750,  # Level 11
                91250,  # Level 12
                104750, # Level 13
                119250, # Level 14
                143250, # Level 15
                169250, # Level 16
                197250, # Level 17
                227250, # Level 18
                249250, # Level 19
                273250, # Level 20
                299250, # Level 21
                327250, # Level 22
                357250, # Level 23
                389250  # Level 24
            ]
            
            if 0 <= level < len(rda_thresholds):
                return rda_thresholds[level]
            else:
                return rda_thresholds[-1]
                
    def _update_xp_info(self, xp_info: Optional[ET.Element]) -> None:
        if xp_info is None:
            return
        
        # First, check if there's a TotalEP value in BaseInfo
        total_ep = "0"
        if self.main_window.tree is not None:
            base_info = self.main_window.tree.getroot().find(".//BaseInfo")
            if base_info is not None:
                total_ep = base_info.get("TotalEP", total_ep)
        
        # If no TotalEP found in BaseInfo, fall back to 0
        if total_ep == "0":
            total_ep = "0"
        
        # Get current player faction
        faction = "0"  # Default to undecided
        if self.main_window.tree is not None:
            metagame = self.main_window.tree.getroot().find("Metagame")
            if metagame is not None:
                faction = metagame.get("PlayerFaction", "0")
        
        # Get faction name from value
        faction_map = {"0": "Undecided", "1": "Na'vi", "2": "RDA"}
        faction_name = faction_map.get(faction, "Undecided")
        
        # Determine max EP based on faction
        if faction_name in ["Na'vi", "Navi"]:
            max_ep = 500000  # Max EP for Na'vi
        else:  # RDA or Undecided
            max_ep = 500000  # Max EP for RDA
        
        # Update TotalEP display with the new format
        if "TotalEP" in self.entries:
            widget = self.entries["TotalEP"]
            formatted_ep = f"{total_ep}/{max_ep} (Max EP)"
            if isinstance(widget, ttk.Label):
                widget.config(text=formatted_ep)
            else:
                widget.delete(0, tk.END)
                widget.insert(0, formatted_ep)
        
        # Log the total EP for debugging
        self.logger.debug(f"Total EP set to: {total_ep}")

    def _update_metagame_info(self, metagame: ET.Element) -> None:
        # Update cost reduction values
        if "NaviCostReduction" in self.entries:
            navi_reduction = metagame.get("NaviCostReduction", "0")
            self.entries["NaviCostReduction"].delete(0, tk.END)
            self.entries["NaviCostReduction"].insert(0, navi_reduction)

        if "CorpCostReduction" in self.entries:
            corp_reduction = metagame.get("CorpCostReduction", "0")
            self.entries["CorpCostReduction"].delete(0, tk.END)
            self.entries["CorpCostReduction"].insert(0, corp_reduction)

        faction_value = metagame.get("PlayerFaction", "0")
        faction_map = {"0": "Undecided", "1": "Na'vi", "2": "RDA"}
        self.entries["PlayerFaction"].set(faction_map.get(faction_value, "Undecided"))

        if "PlayerFaction" in self.entries:
            # Use the string version of the faction value as the key
            faction_display = faction_map.get(faction_value, "Undecided")
            self.entries["PlayerFaction"].set(faction_display)

    def _update_base_info(self, base_info: Optional[ET.Element], tree: Optional[ET.ElementTree] = None) -> None:
        if base_info is None:
            self.logger.warning("[BASE_INFO] No base info provided")
            return

        # Handle name conversion first and separately
        if "namevec" in self.entries:
            # Get the name vector directly from base_info
            name_vec = base_info.get("namevec", "Count(0) ")
            
            # Convert name vector to readable string
            name = self._name_vec_to_string(name_vec)
            
            # Debug logging
            self.logger.debug(f"[BASE_INFO] Name vector: {name_vec}")
            self.logger.debug(f"[BASE_INFO] Converted name: {name}")
            
            # Get the widget for the name
            widget = self.entries["namevec"]
            
            # Set the name 
            if isinstance(widget, ttk.Label):
                widget.config(text=name)
            else:
                widget.delete(0, tk.END)
                widget.insert(0, name)

        # Extremely verbose logging
        self.logger.debug("[BASE_INFO] Detailed BaseInfo Investigation:")
        
        # Log the entire BaseInfo element as a string
        base_info_str = ET.tostring(base_info, encoding='unicode')
        self.logger.debug(f"Full BaseInfo XML: {base_info_str}")
        
        # Log all attributes
        self.logger.debug("All Attributes:")
        for attr, value in base_info.attrib.items():
            self.logger.debug(f"  {attr}: {value}")

        # Multiple attempts to retrieve TotalEP
        possible_keys = [
            "TotalEP", 
            "totalEP", 
            "total_ep", 
            "XP", 
            "total_XP"
        ]

        total_ep = "0"
        for key in possible_keys:
            total_ep = base_info.get(key, total_ep)
            if total_ep != "0" and total_ep != "":
                break

        # Fallback: search in entire tree if not found
        if total_ep == "0" and tree is not None:
            for elem in tree.iter():
                if elem.get("TotalEP"):
                    total_ep = elem.get("TotalEP")
                    break

        self.logger.debug(f"[BASE_INFO] Final TotalEP value: {total_ep}")

        # Update the TotalEP display
        if "TotalEP" in self.entries:
            widget = self.entries["TotalEP"]
            try:
                # Get current player faction for level calculation
                faction = "0"  # Default to undecided
                if tree is not None:
                    metagame = tree.getroot().find("Metagame")
                    if metagame is not None:
                        faction = metagame.get("PlayerFaction", "0")
                        
                # Determine max EP based on faction
                if faction == "1":  # "1" is Na'vi
                    max_ep = 500000  # Max EP for Na'vi
                else:  # RDA or Undecided
                    max_ep = 500000  # Max EP for RDA
                
                formatted_ep = f"{total_ep}/{max_ep} (Max EP)"
                if isinstance(widget, ttk.Label):
                    widget.config(text=formatted_ep)
                else:
                    widget.delete(0, tk.END)
                    widget.insert(0, formatted_ep)
            except Exception as e:
                self.logger.error(f"[BASE_INFO] Error updating TotalEP widget: {str(e)}")

        self.logger.debug("[BASE_INFO] Starting base info update")
        mappings = {
            "side": "side",
            "pawn": "pawn",
            "isfemale": "isfemale",
            "face": "face",
            "bEntityScanningEnabled": "bEntityScanningEnabled",
            "TotalEP": "TotalEP",
            "RecoveryBits": "RecoveryBits",
            "location": "YouAreHere_LatitudeLongitude"
        }

        # Get current player faction for level calculation
        faction = "0"  # Default to undecided
        if tree is not None:
            metagame = tree.getroot().find("Metagame")
            if metagame is not None:
                faction = metagame.get("PlayerFaction", "0")
        
        faction_value = ""
        if metagame is not None:
            faction_value = metagame.get("PlayerFaction", "0")
        faction_map = {"0": "Undecided", "1": "Navi", "2": "RDA"}
        if "PlayerFaction" in self.entries:
            faction_display = faction_map.get(faction_value, "Undecided")
            self.entries["PlayerFaction"].set(faction_display)

        # Get TotalEP for level calculation
        total_ep = base_info.get("TotalEP", "0")
        
        # Calculate level based on faction and EP
        current_level = self._get_level_for_ep(total_ep, faction_map)
        
        # Update level display
        if "CurrentLevel" in self.entries:
            level_widget = self.entries["CurrentLevel"]
            level_widget["values"] = ["Max Level"]
            level_widget.set("Max Level")

        for xml_key, entry_key in mappings.items():
            # Special handling for specific keys
            if entry_key == "isfemale":
                value = "Yes" if base_info.get(xml_key, "0") == "1" else "No"
            elif entry_key == "face":
                face_value = base_info.get(xml_key, "0")
                is_female = base_info.get("isfemale", "0") == "1"
                # Get the face pair number and select appropriate gender
                if face_value in self.face_values:
                    value = self.face_values[face_value]["female" if is_female else "male"]
                else:
                    value = "Male 00"  # Default face if invalid value
            elif entry_key == "side" or entry_key == "pawn":
                # Handle side and pawn values
                raw_value = base_info.get(xml_key, "1")
                faction_map = {"1": "Navi", "2": "RDA"}
                value = faction_map.get(raw_value, "Navi")
            elif entry_key == "YouAreHere_LatitudeLongitude":
                # Specifically look for LocationInfo element
                if tree is not None:
                    root = tree.getroot()
                    # Look for LocationInfo element
                    location_info = root.find(".//LocationInfo")
                    
                    if location_info is not None:
                        value = location_info.get("YouAreHere_LatitudeLongitude", "")
                        self.logger.debug(f"Location value found: '{value}'")
                    else:
                        # Search more broadly if specific LocationInfo not found
                        location_elements = root.findall(".//*[@YouAreHere_LatitudeLongitude]")
                        if location_elements:
                            value = location_elements[0].get("YouAreHere_LatitudeLongitude", "")
                        else:
                            value = ""
                        
                        self.logger.debug("No LocationInfo element found")
                else:
                    value = ""
                    self.logger.debug("No tree provided")
                
                # Ensure a valid coordinate format
                if not value or value == "0":
                    value = "0,0"
            else:
                value = base_info.get(xml_key, "0")

            if entry_key == "bEntityScanningEnabled":
                value = "Yes" if base_info.get(xml_key, "0") == "1" else "No"
            
            if entry_key in self.entries and entry_key != "CurrentLevel":  # Skip CurrentLevel as we already updated it
                widget = self.entries[entry_key]
                
                if isinstance(widget, ttk.Label):
                    # For label widgets, directly set the text
                    widget.config(text=value)
                elif hasattr(widget, 'set'):
                    # For comboboxes
                    widget.set(value)
                else:
                    # For entry widgets
                    widget.delete(0, tk.END)
                    widget.insert(0, value)

        if entry_key == "RecoveryBits":
            value = base_info.get("RecoveryBits", "0")

        # Add face image display immediately after loading
        if "face" in self.entries:
            self.logger.debug("[BASE_INFO] Triggering face image update")
            self._on_face_selected()

    def _get_face_number(self, face_value: str) -> str:
        """Convert face display value (e.g., 'Male 00') to internal face number."""
        try:
            gender, number = face_value.split()
            face_num = int(number)
            # The face number is the same for both male and female of a pair
            return str(face_num)
        except (ValueError, IndexError):
            return "0"
            
    def _update_options_info(self, options_info: Optional[ET.Element]) -> None:
        if options_info is None:
            return

        mappings = {
            "RumbleEnabled": "RumbleEnabled",
            "FirstPersonMode": "FirstPersonMode"
        }

        for xml_key, entry_key in mappings.items():
            if entry_key in self.entries:
                value = "Yes" if options_info.get(xml_key, "0") == "1" else "No"
                self.entries[entry_key].set(value)

    def _format_game_time(self, seconds: str) -> str:
        """Convert game time seconds to a readable format."""
        try:
            total_seconds = int(float(seconds))
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            secs = total_seconds % 60
            return f"{hours:02d}h {minutes:02d}m {secs:02d}s"
        except (ValueError, TypeError):
            return seconds

    def _update_time_info(self, time_info: Optional[ET.Element]) -> None:
        if time_info is None:
            return

        time_data = {
            "GameTime": time_info.get("GameTime", "0"),
            "PlayedTime": time_info.get("PlayedTime", "0"),
            "EnvTime": time_info.get("EnvTime", "0")
        }
        
        # Update the time display in the main window
        self.main_window.update_time_display(time_data)

    def _update_player_info(self, profile: ET.Element) -> None:
        """Update player info in the XML structure"""
        # Change this to check in the PlayerProfile element instead
        recovery = profile.find("Possessions_Recovery")
        if recovery is not None:
            recovery_bits = recovery.get("RecoveryBits", "0")
            
            # Update the RecoveryBits display
            if "RecoveryBits" in self.entries:
                widget = self.entries["RecoveryBits"]
                if isinstance(widget, ttk.Label):
                    widget.config(text=recovery_bits)
                else:
                    widget.delete(0, tk.END)
                    widget.insert(0, recovery_bits)
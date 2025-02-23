import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
from typing import Dict, Optional
from ui_components import LabeledInput
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
            # RDA Weapons
            "1042188764": "Wasp Revolver",
            "1130814347": "CARB",
            "2313824646": "Shotgun",
            "2397981034": "SMG",
            "1919695864": "Combat Shotgun",
            "85991974": "Grenade Launcher",
            "94681171": "Rocket Launcher",
            "2529862352": "LMG",
            "2548581230": "Minigun",
            "815885611": "Tranq Rifle",
            "2152836509": "Hydra",
            "2557822503": "Heavy Machine Gun",
            "2270547313": "Auto Shotgun",
            "186342564": "Missile Launcher",
            "2572658585": "Scorpion",
            "195020497": "MRGL",
            "1306083196": "Assault Rifle",
            "760079057": "Special Rifle",
            "268371112": "PDW",
            "609450705": "SAW",
            "2789519003": "Tactical Shotgun",
            "143378107": "Chain Gun",
            "3628031700": "SCAR",
            "1349633617": "RPG",
            "1881065336": "Heavy GL",
            "999316102": "Special Weapon",
            "466145020": "P90",
            "2288255787": "M60",
            "1796958374": "M32 MGL",
            "4018216358": "SMAW",
            "1146928137": "Mk.12 SPR",
            "1911864170": "Flak Cannon",
            "433486271": "Combat Knife",

            # RDA Ammo
            "4029490973": "Rifle Ammo",
            "2220072441": "Shotgun Ammo",
            "3183424835": "SMG Ammo",
            "3227899887": "Grenade Ammo",
            "4198025789": "Rocket Ammo",
            "2442117335": "LMG Ammo",
            "3819023512": "Heavy Ammo",

            # RDA Armor
            "4082430736": "Heavy Armor",
            "205852157": "Medium Armor",
            "1052486966": "Light Armor",
            "3980056687": "Basic Armor",
            "3574042272": "Standard Armor",
            "1417888964": "Advanced Armor",
            "149499402": "Experimental Armor",  
            "4160278759": "Prototype Armor",    
            "3305533484": "Elite Armor",   

            # RDA Equipment
            "2823901304": "Health Kit",         
            "1981144899": "Ammo Pack",          
            "2056338139": "Shield Generator",    
            "3753317026": "Speed Booster",      
            "1851965193": "Camo System",        
            "2428117146": "Targeting System",   
            "1593826001": "Jump Pack",          
            "2716738620": "Armor Boost",        
            "2467333367": "Energy Shield",      
            "3527939275": "Stealth Module",     
            "1193780569": "Radar Jammer",       
            "1379870057": "Power Core",         
            "403319592": "Shield Enhancer",     
            "3877361093": "Damage Amplifier",   
            "3588584718": "Stamina Module",        

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

            # Na'vi Ammo
            "1042656528": "Arrow Ammo",  
            "435601722": "Spear Ammo",   
            "3069972540": "Poison Ammo", 
            
            # Na'vi Armor/Equipment
            "753645081": "Na'vi Light Armor",
            "236713729": "Na'vi Medium Armor",
            "2228061969": "Na'vi Heavy Armor",
            "3363478556": "Hunter Armor",    
            "1118628876": "Warrior Armor",   
            "3934969092": "Elite Armor", 

            # Na'vi Equipment
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
        
        # Special cases
        if weapon_info['id'] == "1042188764":  # Wasp Revolver
            text += " (∞)"
        elif weapon_info['id'] in ["1304439874", "2813685095"]:  # Staff and War Club
            text += " (Melee)"
        else:
            # For all other weapons, show ammo count if they have ammo
            if weapon_info['ammo'] != "0":
                text += f" ({weapon_info['ammo']}/{weapon_info['stack']})"
        
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

                field_groups = {
                    "Character Info": [
                        ("Is Female", "isfemale", {"0": "No", "1": "Yes"}),
                        ("Face", "face", self.face_values),
                        ("Side", "side"),
                        ("Pawn", "pawn"),
                        ("Location", "YouAreHere_LatitudeLongitude")
                    ],
                    "Progress": [
                        ("Current Level", "iCurrentLevel", {
                            str(i): f"Level {i}" + (" Max Level" if i == 24 else "")
                            for i in range(25)
                        }),
                        ("Current XP", "iCurrentXP"),
                        ("Total EP", "TotalEP")
                    ],
                    "Faction Settings": [
                        ("Player Faction", "PlayerFaction", {"0": "Undecided", "1": "Navi", "2": "Corp"}),
                        ("Navi Cost Reduction", "NaviCostReduction"),
                        ("Corp Cost Reduction", "CorpCostReduction")
                    ],
                    "Gameplay Settings": [
                        ("Entity Scanning", "bEntityScanningEnabled", {"0": "No", "1": "Yes"}),
                        ("First Person Mode", "FirstPersonMode", {"0": "No", "1": "Yes"}),
                        ("Rumble Enabled", "RumbleEnabled", {"0": "No", "1": "Yes"})
                    ]
                }

                # List of fields to display as labels
                label_fields = {"isfemale", "face", "side", "pawn", "YouAreHere_LatitudeLongitude", "iCurrentXP", "TotalEP"}

                # Define positions for top row groups
                x_positions_row1 = [0, 230, 460, 690]  # Back to four positions
                
                # Create top row groups
                first_row_groups = list(field_groups.items())[:4]
                for i, (group_name, fields) in enumerate(first_row_groups):
                    group_frame = ttk.LabelFrame(self.parent, text=group_name)
                    group_frame.place(x=x_positions_row1[i], y=0, width=230, height=170)  # Back to original width
                    
                    for field_info in fields:
                        label_text = field_info[0]
                        key = field_info[1]
                        values = field_info[2] if len(field_info) > 2 else None

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
                                "combobox" if values else "entry",
                                values
                            )
                            input_widget.pack(fill=tk.X, padx=5, pady=2)
                            self.entries[key] = input_widget.input
                            
                            if isinstance(input_widget.input, (ttk.Entry, ttk.Combobox)):
                                if hasattr(input_widget.input, 'bind'):
                                    input_widget.input.bind('<KeyRelease>', self._mark_unsaved_changes)
                                    input_widget.input.bind('<<ComboboxSelected>>', self._mark_unsaved_changes)

                # RDA Loadout frame
                rda_frame = ttk.LabelFrame(self.parent, text="RDA Loadout")
                rda_frame.place(x=0, y=180, width=535, height=350)

                # Define custom slot names for RDA
                rda_slot_names = [
                    "Primary Weapon",    # Slot 1
                    "Secondary Weapon",  # Slot 2
                    "Special Weapon",    # Slot 3
                    "Top Weapon"           # Slot 4
                ]

                # Create RDA weapon slots
                self.weapon_slots = []
                rda_slot_positions = [
                    {"x": 10, "y": 250},
                    {"x": 10, "y": 90},
                    {"x": 10, "y": 170},
                    {"x": 160, "y": 10}
                ]

                for i in range(4):
                    slot_frame = ttk.Frame(rda_frame)
                    slot_frame.place(x=rda_slot_positions[i]["x"], y=rda_slot_positions[i]["y"])
                    
                    ttk.Label(slot_frame, text=f"{rda_slot_names[i]}:").pack(side=tk.LEFT, padx=5)
                    
                    main_frame = ttk.Frame(slot_frame)
                    main_frame.pack(side=tk.LEFT, padx=10)
                    main_label = ttk.Label(main_frame, text="-")
                    main_label.pack(side=tk.LEFT, padx=5)
                    
                    self.weapon_slots.append({
                        "main": main_label,
                        "off": None  # Keep off field in dictionary but set to None
                    })

                # Na'vi Loadout frame
                navi_frame = ttk.LabelFrame(self.parent, text="Na'vi Loadout")
                navi_frame.place(x=535, y=180, width=535, height=350)

                # Define custom slot names for Na'vi
                navi_slot_names = [
                    "Ranged Weapon",    # Slot 1
                    "Melee Weapon",     # Slot 2
                    "Spirit Weapon",    # Slot 3
                    "Top Weapon"        # Slot 4
                ]

                # Create Na'vi weapon slots
                self.navi_weapon_slots = []
                navi_slot_positions = [
                    {"x": 10, "y": 250},
                    {"x": 10, "y": 90},
                    {"x": 10, "y": 170},
                    {"x": 160, "y": 10}
                ]

                for i in range(4):
                    slot_frame = ttk.Frame(navi_frame)
                    slot_frame.place(x=navi_slot_positions[i]["x"], y=navi_slot_positions[i]["y"])
                    
                    ttk.Label(slot_frame, text=f"{navi_slot_names[i]}:").pack(side=tk.LEFT, padx=5)
                    
                    main_frame = ttk.Frame(slot_frame)
                    main_frame.pack(side=tk.LEFT, padx=10)
                    main_label = ttk.Label(main_frame, text="-")
                    main_label.pack(side=tk.LEFT, padx=5)
                    
                    self.navi_weapon_slots.append({
                        "main": main_label,
                        "off": None  # Keep off field in dictionary but set to None
                    })

                # Create the face image frame
                self.face_image_frame = ttk.LabelFrame(self.parent, text="Character Face")
                self.face_image_frame.place(
                    x=920,
                    y=0,
                    width=150,
                    height=150
                )

                # Create a label inside the frame to display the image
                self.face_image_label = ttk.Label(self.face_image_frame)
                self.face_image_label.pack(
                    expand=True,
                    fill='both',
                    padx=10,
                    pady=10
                )

            except Exception as e:
                self.logger.error(f"Error creating stat fields: {str(e)}", exc_info=True)
                raise

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
                        return {
                            "id": item_id,
                            "name": self._get_item_name(item_id),
                            "ammo": poss.get("NbInClip", "0"),
                            "stack": poss.get("NbInStack", "0")
                        }
        return None

    def _update_navi_loadout_display(self, profile: ET.Element) -> None:
        """Update the Na'vi loadout display with current equipment"""
        weapons = self._get_avatar_weapons(profile)
        
        for slot_num, slot_data in weapons.items():
            if slot_num < len(self.navi_weapon_slots):
                # Get main weapon info
                main_weapon = self._get_avatar_weapon_info(profile, slot_data["main"])
                if main_weapon:
                    self.navi_weapon_slots[slot_num]["main"].config(
                        text=self._format_weapon_text(main_weapon)
                    )
                else:
                    self.navi_weapon_slots[slot_num]["main"].config(text="-Empty-")

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
                        return {
                            "id": item_id,
                            "name": self._get_item_name(item_id),
                            "ammo": poss.get("NbInClip", "0"),
                            "stack": poss.get("NbInStack", "0")
                        }
        return None

    def _update_loadout_display(self, profile: ET.Element) -> None:
        """Update the RDA loadout display with current equipment"""
        weapons = self._get_equipped_weapons(profile)
        
        for slot_num, slot_data in weapons.items():
            if slot_num < len(self.weapon_slots):
                # Get main weapon info
                main_weapon = self._get_weapon_info(profile, slot_data["main"])
                if main_weapon:
                    self.weapon_slots[slot_num]["main"].config(
                        text=self._format_weapon_text(main_weapon)
                    )
                else:
                    self.weapon_slots[slot_num]["main"].config(text="-Empty-")

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


            player0 = root.find(".//Player0")
            if player0 is not None:
                self._update_player_info(player0)
        
        metagame = root.find("Metagame")
        if metagame is not None:
            self._update_metagame_info(metagame)

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
                # Define XP and EP thresholds for each level (same values for both)
                level_thresholds = [
                    {"xp": 0, "ep": 0},          # Level 0
                    {"xp": 1600, "ep": 1600},    # Level 1
                    {"xp": 4600, "ep": 4600},    # Level 2
                    {"xp": 8000, "ep": 8000},    # Level 3
                    {"xp": 12100, "ep": 12100},  # Level 4
                    {"xp": 17000, "ep": 17000},  # Level 5
                    {"xp": 38500, "ep": 38500},  # Level 6
                    {"xp": 45750, "ep": 45750},  # Level 7
                    {"xp": 53250, "ep": 53250},  # Level 8
                    {"xp": 61250, "ep": 61250},  # Level 9
                    {"xp": 70250, "ep": 70250},  # Level 10
                    {"xp": 79750, "ep": 79750},  # Level 11
                    {"xp": 91250, "ep": 91250},  # Level 12
                    {"xp": 104750, "ep": 104750},# Level 13
                    {"xp": 119250, "ep": 119250},# Level 14
                    {"xp": 143250, "ep": 143250},# Level 15
                    {"xp": 169250, "ep": 169250},# Level 16
                    {"xp": 197250, "ep": 197250},# Level 17
                    {"xp": 227250, "ep": 227250},# Level 18
                    {"xp": 249250, "ep": 249250},# Level 19
                    {"xp": 273250, "ep": 273250},# Level 20
                    {"xp": 299250, "ep": 299250},# Level 21
                    {"xp": 327250, "ep": 327250},# Level 22
                    {"xp": 357250, "ep": 357250},# Level 23
                    {"xp": 389250, "ep": 389250} # Level 24
                ]

                # Initialize updates dictionary
                updates = {
                    "BaseInfo": {},
                    "XpInfo": {},
                    "OptionsInfo": {},
                    "TimeInfo": {},
                    "Metagame": {}
                }

                # Get current XP, level, and EP values
                widget_xp = self.entries["iCurrentXP"]
                current_xp = int(widget_xp.cget("text") if isinstance(widget_xp, ttk.Label) else widget_xp.get())
                
                widget_level = self.entries["iCurrentLevel"]
                current_level_str = widget_level.get()  # Combobox always uses get()
                current_level = int(current_level_str.split()[-1])  # "Level X" -> X

                # If XP is changed, update the level and EP
                if current_level < len(level_thresholds) - 1 and current_xp >= level_thresholds[current_level + 1]["xp"]:
                    # Find the correct level for the current XP
                    for level, threshold in enumerate(level_thresholds):
                        if current_xp < threshold["xp"]:
                            current_level = level - 1
                            break
                    
                    # Update the level entry and EP
                    self.entries["iCurrentLevel"].set(f"Level {current_level}")
                    widget_ep = self.entries["TotalEP"]
                    if isinstance(widget_ep, ttk.Label):
                        widget_ep.config(text=str(current_xp))
                    else:
                        widget_ep.delete(0, tk.END)
                        widget_ep.insert(0, str(current_xp))

                # Update BaseInfo
                base_fields = ["side", "pawn", "face", "TotalEP"]
                for field in base_fields:
                    if field in self.entries:
                        widget = self.entries[field]
                        if field == "face":
                            face_value = widget.cget("text") if isinstance(widget, ttk.Label) else widget.get()
                            face_number = self._get_face_number(face_value)
                            updates["BaseInfo"][field] = face_number
                        else:
                            value = widget.cget("text") if isinstance(widget, ttk.Label) else widget.get()
                            updates["BaseInfo"][field] = value

                # Handle boolean fields
                widget_female = self.entries["isfemale"]
                updates["BaseInfo"]["isfemale"] = "1" if (widget_female.cget("text") if isinstance(widget_female, ttk.Label) else widget_female.get()) == "Yes" else "0"
                
                widget_scanning = self.entries["bEntityScanningEnabled"]
                updates["BaseInfo"]["bEntityScanningEnabled"] = "1" if (widget_scanning.cget("text") if isinstance(widget_scanning, ttk.Label) else widget_scanning.get()) == "Yes" else "0"

                # Update XpInfo
                updates["XpInfo"]["iCurrentXP"] = str(current_xp)
                updates["XpInfo"]["iCurrentLevel"] = str(current_level)

                # Update remaining sections
                widget_rumble = self.entries["RumbleEnabled"]
                updates["OptionsInfo"]["RumbleEnabled"] = "1" if widget_rumble.get() == "Yes" else "0"
                
                widget_firstperson = self.entries["FirstPersonMode"]
                updates["OptionsInfo"]["FirstPersonMode"] = "1" if widget_firstperson.get() == "Yes" else "0"

                widget_faction = self.entries["PlayerFaction"]
                faction_map = {"Undecided": "0", "Navi": "1", "Corp": "2"}
                updates["Metagame"]["PlayerFaction"] = faction_map[widget_faction.get()]

                # Update TimeInfo remains the same since it uses main_window.time_labels
                
                self.logger.debug(f"Time info updates: {updates['TimeInfo']}")
                return updates
                    
            except Exception as e:
                self.logger.error(f"Error getting stats updates: {str(e)}")
                raise

    def _update_base_info(self, base_info: Optional[ET.Element], tree: Optional[ET.ElementTree] = None) -> None:
            if base_info is None:
                self.logger.warning("[BASE_INFO] No base info provided")
                return

            self.logger.debug("[BASE_INFO] Starting base info update")
            mappings = {
                "side": "side",
                "pawn": "pawn",
                "isfemale": "isfemale",
                "face": "face",
                "bEntityScanningEnabled": "bEntityScanningEnabled",
                "TotalEP": "TotalEP",
                "location": "YouAreHere_LatitudeLongitude"
            }

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
                elif entry_key == "YouAreHere_LatitudeLongitude":
                    # Specifically look for LocationInfo element
                    if tree is not None:
                        root = tree.getroot()
                        # Look for LocationInfo element
                        location_info = root.find(".//LocationInfo")
                        
                        if location_info is not None:
                            value = location_info.get("YouAreHere_LatitudeLongitude", "")
                            print(f"DEBUG: Location Info Element: {ET.tostring(location_info)}")
                            print(f"DEBUG: Location value: '{value}'")
                            self.logger.debug(f"Location value found: '{value}'")
                        else:
                            # Search more broadly if specific LocationInfo not found
                            location_elements = root.findall(".//*[@YouAreHere_LatitudeLongitude]")
                            if location_elements:
                                value = location_elements[0].get("YouAreHere_LatitudeLongitude", "")
                                print(f"DEBUG: Found location in broader search: '{value}'")
                            else:
                                value = ""
                                print("DEBUG: No location elements found")
                            
                            self.logger.debug("No LocationInfo element found")
                    else:
                        value = ""
                        self.logger.debug("No tree provided")
                    
                    # Ensure a valid coordinate format
                    if not value or value == "0":
                        value = "0,0"
                    print(f"DEBUG: Final location value: '{value}'")
                else:
                    value = base_info.get(xml_key, "0")

                if entry_key == "bEntityScanningEnabled":
                    value = "Yes" if base_info.get(xml_key, "0") == "1" else "No"
                
                if entry_key in self.entries:
                    print(f"Attempting to set {entry_key} to: '{value}'")  # Debug print
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

    def _update_xp_info(self, xp_info: Optional[ET.Element]) -> None:
        if xp_info is None:
            return
        
        mappings = {
            "iCurrentXP": "iCurrentXP",
            "iCurrentLevel": "iCurrentLevel"
        }

        # Get current XP and level values
        current_xp = int(xp_info.get(mappings["iCurrentXP"], "0"))
        current_level_from_xml = int(xp_info.get(mappings["iCurrentLevel"], "0"))

        # Determine current level based on XP
        current_level = current_level_from_xml  # Use level from XML

        # Update the entries
        if mappings["iCurrentXP"] in self.entries:
            widget = self.entries[mappings["iCurrentXP"]]
            if isinstance(widget, ttk.Label):
                widget.config(text=str(current_xp))
        
        if mappings["iCurrentLevel"] in self.entries:
            self.entries[mappings["iCurrentLevel"]].set(f"Level {current_level}")
            
        # Update Total EP to match current XP
        if "TotalEP" in self.entries:
            widget = self.entries["TotalEP"]
            if isinstance(widget, ttk.Label):
                widget.config(text=str(current_xp))

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

        # Existing faction update
        faction_value = metagame.get("PlayerFaction", "0")
        faction_map = {0: "Undecided", 1: "Navi", 2: "Corp"}
        
        if "PlayerFaction" in self.entries:
            self.entries["PlayerFaction"].set(faction_map[int(faction_value)])

    def _update_player_info(self, player0: Optional[ET.Element]) -> None:
        """
        Placeholder method for updating player info.
        If you know what specific attributes you want to update from Player0, 
        you can add the logic here.
        """
        if player0 is None:
            return
        
        # Log a debug message if you want to track when this method is called
        self.logger.debug("Updating player info - placeholder method")
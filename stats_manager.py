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
        
        # Initialize face values only once
        self.face_values = {}
        for i in range(0, 24):  # 12 pairs (00-11) × 2 genders
            if i // 2 <= 11:  # Go up to pair 11
                gender = "Male" if i % 2 == 0 else "Female"
                pair_num = str(i // 2).zfill(2)
                self.face_values[str(i)] = f"{gender} {pair_num}"
        
        self.setup_ui()

    def setup_ui(self) -> None:
        self._create_stat_fields()

    def _create_stat_fields(self) -> None:
        self.logger.debug("Creating stat fields")
        try:
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
                        "0": "Level 0",
                        "1": "Level 1",
                        "2": "Level 2",
                        "3": "Level 3",
                        "4": "Level 4",
                        "5": "Level 5",
                        "6": "Level 6",
                        "7": "Level 7",
                        "8": "Level 8",
                        "9": "Level 9",
                        "10": "Level 10"
                        # Add more levels as needed
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
                ],
                "Time Stats": [
                    ("Game Time", "Game Time"),
                    ("Played Time", "Played Time"),
                    ("Environment Time", "Environment Time")
                ]
            }

            current_row = 0
            for group_name, fields in field_groups.items():
                ttk.Label(
                    self.parent,
                    text=group_name,
                    font=("", 10, "bold")
                ).grid(row=current_row, column=0, columnspan=2, sticky="w", padx=5, pady=(10, 5))
                current_row += 1

                for field_info in fields:
                    label_text = field_info[0]
                    key = field_info[1]
                    values = field_info[2] if len(field_info) > 2 else None

                    input_widget = LabeledInput(
                        self.parent,
                        label_text,
                        "combobox" if values else "entry",
                        values
                    )
                    input_widget.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
                    self.entries[key] = input_widget.input
                    
                    # Add binding for face combobox
                    if key == "face":
                        input_widget.input.bind('<<ComboboxSelected>>', self._on_face_selected)
                    # Add bindings for all other entry and combobox widgets to mark unsaved changes
                    elif isinstance(input_widget.input, (ttk.Entry, ttk.Combobox)):
                        # For Entry widgets
                        if hasattr(input_widget.input, 'bind'):
                            input_widget.input.bind('<KeyRelease>', self._mark_unsaved_changes)
                        
                        # For Combobox widgets (except face)
                        if hasattr(input_widget.input, 'bind'):
                            input_widget.input.bind('<<ComboboxSelected>>', self._mark_unsaved_changes)
                    
                    current_row += 1

            # Create the frame for the face image AFTER the loop
            self.face_image_frame = ttk.LabelFrame(self.parent, text="Character Face")
            self.face_image_frame.place(
                x=400,  # Set X position
                y=0,  # Set Y position
                width=400,  # Set frame width
                height=400  # Set frame height
            )

            # Create a label inside the frame to display the image
            self.face_image_label = ttk.Label(self.face_image_frame)
            self.face_image_label.pack(
                expand=True,  # Allow it to fit inside the frame
                fill='both',  # Expand in both directions
                padx=10,
                pady=10
            )

            self.logger.debug("Stat fields created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating stat fields: {str(e)}", exc_info=True)
            raise

    def _on_face_selected(self, event=None):
        """Handle face selection and update image"""
        try:
            face_value = self.entries["face"].get()
            self.logger.debug(f"[FACE_SELECT] Selected face value: {face_value}")
            
            if not face_value:
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
                resized_image = original_image.resize((400, 400), Image.LANCZOS)
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

    def get_stats_updates(self) -> Dict[str, Dict[str, str]]:
        self.logger.debug("[STATS_UPDATE] Starting stats updates collection")

        # Define XP thresholds for each level (same as in _update_xp_info)
        xp_thresholds = [
            0,      # Level 0
            1000,   # Level 1
            3000,   # Level 2
            6000,   # Level 3
            10000,  # Level 4
            15000,  # Level 5
            21000,  # Level 6
            28000,  # Level 7
            36000,  # Level 8
            45000,  # Level 9
            55000   # Level 10
            # Add more levels as needed
        ]

        # Initialize updates dictionary
        updates = {
            "BaseInfo": {},
            "XpInfo": {},
            "OptionsInfo": {},
            "TimeInfo": {},
            "Metagame": {}
        }

        # Get current XP and level values
        current_xp = int(self.entries["iCurrentXP"].get())

        # Extract numeric level from the combobox text
        current_level_str = self.entries["iCurrentLevel"].get()
        current_level = int(current_level_str.split()[-1])  # "Level X" -> X

        # If XP is changed, update the level
        if current_level < len(xp_thresholds) - 1 and current_xp >= xp_thresholds[current_level + 1]:
            # Find the correct level for the current XP
            for level, threshold in enumerate(xp_thresholds):
                if current_xp < threshold:
                    current_level = level - 1
                    break
            
            # Update the level entry
            self.entries["iCurrentLevel"].delete(0, tk.END)
            self.entries["iCurrentLevel"].insert(0, f"Level {current_level}")

        # If level is changed, set XP to the minimum threshold for that level
        elif current_xp < xp_thresholds[current_level]:
            current_xp = xp_thresholds[current_level]
            self.entries["iCurrentXP"].delete(0, tk.END)
            self.entries["iCurrentXP"].insert(0, str(current_xp))

        self.logger.debug("[STATS_UPDATE] Collecting base info updates")
        try:
            # Update BaseInfo
            base_fields = ["side", "pawn", "face", "TotalEP"]
            for field in base_fields:
                if field in self.entries:
                    if field == "face":
                        self.logger.debug(f"[STATS_UPDATE] Getting face value: {self.entries[field].get()}")
                        # Convert face value from "Gender XX" format back to numeric ID
                        face_value = self.entries[field].get()
                        gender, number = face_value.split()
                        pair_number = int(number)
                        face_number = pair_number * 2 if gender == "Male" else (pair_number * 2) + 1
                        updates["BaseInfo"][field] = str(face_number)
                    else:
                        updates["BaseInfo"][field] = self.entries[field].get()
            
            # Handle boolean fields
            updates["BaseInfo"]["isfemale"] = "1" if self.entries["isfemale"].get() == "Yes" else "0"
            updates["BaseInfo"]["bEntityScanningEnabled"] = "1" if self.entries["bEntityScanningEnabled"].get() == "Yes" else "0"

            # Add location to base info updates if it's not empty
            location_value = self.entries.get("YouAreHere_LatitudeLongitude", "")
            if hasattr(location_value, "get"):
                location_value = location_value.get()
                # Split the location into latitude and longitude
                try:
                    latitude, longitude = location_value.split(',')
                    # Create or update LocationInfo with the new location
                    updates["BaseInfo"]["LocationInfo"] = {
                        "Latitude": latitude.strip(),
                        "Longitude": longitude.strip()
                    }
                except ValueError:
                    self.logger.warning(f"Invalid location format: {location_value}")

            self.logger.debug(f"Base info updates: {updates['BaseInfo']}")

            # Update XpInfo
            updates["XpInfo"]["iCurrentXP"] = str(current_xp)
            updates["XpInfo"]["iCurrentLevel"] = str(current_level)
            self.logger.debug(f"XP info updates: {updates['XpInfo']}")

            # Update OptionsInfo
            updates["OptionsInfo"]["RumbleEnabled"] = "1" if self.entries["RumbleEnabled"].get() == "Yes" else "0"
            updates["OptionsInfo"]["FirstPersonMode"] = "1" if self.entries["FirstPersonMode"].get() == "Yes" else "0"
            self.logger.debug(f"Options info updates: {updates['OptionsInfo']}")

            # Update Metagame
            faction_map = {"Undecided": "0", "Navi": "1", "Corp": "2"}
            updates["Metagame"]["PlayerFaction"] = faction_map[self.entries["PlayerFaction"].get()]
            self.logger.debug(f"Metagame updates: {updates['Metagame']}")

            # Update TimeInfo
            time_fields = [
                "Game Time",
                "Played Time", 
                "Environment Time"
            ]
            time_xml_mapping = {
                "Game Time": "GameTime",
                "Played Time": "PlayedTime",
                "Environment Time": "EnvTime"
            }

            for field in time_fields:
                value = self.entries[field].get()
                xml_key = time_xml_mapping.get(field, field)
                updates["TimeInfo"][xml_key] = self._convert_time_to_seconds(value)
            self.logger.debug(f"Time info updates: {updates['TimeInfo']}")

            return updates
        except Exception as e:
            self.logger.error(f"Error getting stats updates: {str(e)}", exc_info=True)
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
                value = base_info.get(xml_key, "0")
                # Convert numeric face ID to "Gender XX" format
                if value in self.face_values:
                    value = self.face_values[value]
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
                if hasattr(self.entries[entry_key], 'set'):
                    self.entries[entry_key].set(value)
                else:
                    self.entries[entry_key].delete(0, tk.END)
                    self.entries[entry_key].insert(0, value)

        # Add face image display immediately after loading
        if "face" in self.entries:
            self.logger.debug("[BASE_INFO] Triggering face image update")
            self._on_face_selected()

    def _update_xp_info(self, xp_info: Optional[ET.Element]) -> None:
        if xp_info is None:
            return
        
        # Define XP thresholds for each level
        xp_thresholds = [
            0,      # Level 0
            1000,   # Level 1
            3000,   # Level 2
            6000,   # Level 3
            10000,  # Level 4
            15000,  # Level 5
            21000,  # Level 6
            28000,  # Level 7
            36000,  # Level 8
            45000,  # Level 9
            55000   # Level 10
            # Add more levels as needed
        ]

        mappings = {
            "iCurrentXP": "iCurrentXP",
            "iCurrentLevel": "iCurrentLevel"
        }

        # Get current XP and level values
        current_xp = int(xp_info.get(mappings["iCurrentXP"], "0"))
        # Optionally, get the level from XML if it exists
        current_level_from_xml = int(xp_info.get(mappings["iCurrentLevel"], "0"))

        # Determine current level based on XP
        current_level = 0
        for level, threshold in enumerate(xp_thresholds):
            if current_xp < threshold:
                current_level = level - 1
                break

        # If XML level is different from calculated level, use XML level
        if current_level_from_xml != current_level:
            current_level = current_level_from_xml

        # Update the entries
        if mappings["iCurrentXP"] in self.entries:
            self.entries[mappings["iCurrentXP"]].delete(0, tk.END)
            self.entries[mappings["iCurrentXP"]].insert(0, str(current_xp))
        
        if mappings["iCurrentLevel"] in self.entries:
            # Ensure the level is displayed in the dropdown
            self.entries[mappings["iCurrentLevel"]].set(f"Level {current_level}")

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

        mappings = {
            "GameTime": "Game Time",
            "PlayedTime": "Played Time",
            "EnvTime": "Environment Time"
        }

        for xml_key, label_key in mappings.items():
            if label_key in self.entries:
                value = time_info.get(xml_key, "0")
                formatted_value = self._format_game_time(value)
                self.entries[label_key].delete(0, tk.END)
                self.entries[label_key].insert(0, formatted_value)

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
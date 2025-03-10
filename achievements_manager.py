import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
from typing import Dict, Optional
from ui_components import LabeledInput
import logging

class AchievementsManager:
    def __init__(self, parent: ttk.Frame, main_window):
        self.logger = logging.getLogger('AchievementsManager')
        self.logger.debug("Initializing AchievementsManager")
        self.parent = parent
        self.main_window = main_window
        self.entries = {}
        
        # Achievements still needed
        #
        # Two-Traitor Clean-up!
        # Hasta la vista, Harper
        # Pandora's Protector

        # Achievement definitions with names and max values
        self.achievement_data = {
            # Story/Mission Achievements (max: 1)
            "3975313082": {"name": "Orientation Day Graduate", "max": 1},     # First Hell's Gate visit
            "3887901362": {"name": "War's Begun", "max": 1},                 # Complete Blue Lagoon
            "1964522520": {"name": "Did we win?", "max": 1},                 # Survive RDA attack in Iknimaya
            "820789492": {"name": "The First Song", "max": 1},               # Secure song in Swotulu
            "148645412": {"name": "The First Harmonic", "max": 1},           # First harmonic in Needle Hills
            "587544596": {"name": "Song of Torukä Na'rìng", "max": 1},       # Secure song in Torukä Na'rìng
            "1752941290": {"name": "Ryder owns Goliath", "max": 1},          # Complete Plains of Goliath
            "208366408": {"name": "Harmonic in the FEBA", "max": 1},         # Score harmonic from FEBA
            "149358130": {"name": "Song of Va'erä Ramunong", "max": 1},      # Secure song in Va'erä Ramunong
            "260134042": {"name": "Song of Kxanìa Taw", "max": 1},           # Secure song in Kxanìa Taw
            "1791022025": {"name": "Grave's Bog Harmonic", "max": 1},        # Score harmonic in Grave's Bog

            # Story Achievements (pattern matched)
            "3614666474": {"name": "Story Achievement (Blue Lagoon Area)", "max": 1},
            "3708977241": {"name": "Story Achievement (Mid-Game)", "max": 1},
            "3177295287": {"name": "Story Achievement (Late-Game)", "max": 1},
            "355473279": {"name": "Story Achievement (Mission)", "max": 1},
            "2587251285": {"name": "Story Achievement (Mission)", "max": 1},
            "1172651822": {"name": "Story Achievement (Mission)", "max": 1},
            "1847852653": {"name": "Story Achievement (Mission)", "max": 1},
            
            # Clean Sweep Achievements (max: 1)
            "2702278646": {"name": "Blue Lagoon Clean Sweep", "max": 1},
            "1863714547": {"name": "Needle Hills Clean Sweep", "max": 1},
            "2171723794": {"name": "FEBA Clean Sweep", "max": 1},
            "3409126972": {"name": "Iknimaya Clean Sweep", "max": 1},
            "2943222331": {"name": "Plains of Goliath Clean Sweep", "max": 1},
            "2292208788": {"name": "Kxanìa Taw Clean Sweep", "max": 1},
            "1057194188": {"name": "Torukä Na'rìng Clean Sweep", "max": 1},
            "2856892107": {"name": "Swotulu Clean Sweep", "max": 1},
            "238707229": {"name": "Grave's Bog Clean Sweep", "max": 1},
            "704269734": {"name": "Va'erä Ramunong Clean Sweep", "max": 1},
            "77959529": {"name": "Hanging Gardens Clean Sweep", "max": 1},
            
            # Combat/Multiplayer Achievements (various max values)
            "2932051916": {"name": "Weapon of Choice", "max": 100},          # 100 kills with dual wasps/bow
            "863723867": {"name": "Flawless Victory", "max": 1},            # Win 3-0 in CTF
            "4073911841": {"name": "The Enemy's Bane", "max": 1},           # Most kills in TDM
            "370163335": {"name": "A God is Upon Us", "max": 10},           # 10 kills without dying
            "3619269117": {"name": "Destructive Preservation", "max": 1},    # RDA timer with 3 missiles
            "2646580024": {"name": "Turn the Tide", "max": 1},             # 50% territories
            "611800566": {"name": "Central Focus", "max": 5},                # 5 KotH wins
            "3229137376": {"name": "The Conqueror", "max": 5},              # 5 CnH wins
            "1862651544": {"name": "Bring On All Comers!", "max": 150},     # 150 MP games
            "2847917574": {"name": "Jack of All Skills", "max": 20},        # Rank 4 skills x20
            
            # Game Completion (max: 1)
            "4154870226": {"name": "More Tawtute Will Come", "max": 1},      # Finish Na'vi side
            "3843286588": {"name": "The Battle's Won", "max": 1},            # Finish RDA side
            "2167405524": {"name": "Clean Sweep of Pandora", "max": 1},      # All Sector Challenges
            
            # Misc Achievements
            "376364380": {"name": "Digital Bookworm", "max": 20},            # 20 Pandorapedia articles
            
            # Progress Achievements
            "1497753099": {"name": "Combat Progress Achievement", "max": 20},
            "3305899539": {"name": "Progress Achievement", "max": 100},
            
            # Unknown Achievements
            "2171844251": {"name": "Unknown Achievement", "max": 100},
            "1716177172": {"name": "Unknown Achievement", "max": 100},
            "3049880868": {"name": "Unknown Achievement", "max": 100},
            "569487683": {"name": "Unknown Achievement", "max": 100},
            "830999210": {"name": "Unknown Achievement", "max": 100},
            "594996582": {"name": "Unknown Achievement", "max": 100},
            "4203819019": {"name": "Unknown Achievement", "max": 100},
            "2779487515": {"name": "Unknown Achievement", "max": 100},
            "4118326594": {"name": "Unknown Achievement", "max": 100},
            "270754235": {"name": "Unknown Achievement", "max": 100},
        }
        
        self.setup_ui()

    def setup_ui(self) -> None:
        # Create Achievements Treeview
        tree_frame = ttk.Frame(self.parent, height=280)
        tree_frame.pack(fill=tk.X, pady=5)
        tree_frame.pack_propagate(False)

        ttk.Label(tree_frame, text="Achievements Status").pack()

        # Create Treeview with columns
        columns = ("ID", "Name", "Progress", "Status")
        self.achievements_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="extended"
        )

        # Configure columns
        self.achievements_tree.heading("ID", text="Achievement ID")
        self.achievements_tree.heading("Name", text="Name")
        self.achievements_tree.heading("Progress", text="Progress")
        self.achievements_tree.heading("Status", text="Status")

        # Set column widths and alignment
        self.achievements_tree.column("ID", width=150, anchor="w")
        self.achievements_tree.column("Name", width=250, anchor="w")
        self.achievements_tree.column("Progress", width=100, anchor="center")
        self.achievements_tree.column("Status", width=100, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.achievements_tree.yview)
        self.achievements_tree.configure(yscrollcommand=scrollbar.set)

        self.achievements_tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create edit frame with only completion buttons
        edit_frame = ttk.LabelFrame(self.parent, text="Achievement Controls", padding=10)
        edit_frame.pack(fill=tk.X, pady=5)

        # Button frame for controls
        button_frame = ttk.Frame(edit_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            button_frame,
            text="Complete All Achievements",
            command=self._complete_all_achievements
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Complete Selected",
            command=self._complete_selected
        ).pack(side=tk.LEFT, padx=5)

    def load_achievements(self, tree: ET.ElementTree) -> None:
        self.logger.debug("Loading achievements")
        try:
            # Clear existing items
            for item in self.achievements_tree.get_children():
                self.achievements_tree.delete(item)

            # Find all AchievementCounter elements in XML
            achievements = tree.findall(".//AchievementCounter")
            self.logger.debug(f"Found {len(achievements)} achievements")
            
            # Sort achievements by ID for consistent display
            achievements_sorted = sorted(achievements, key=lambda x: x.get("crc_id", "0"))
            
            for achievement in achievements_sorted:
                try:
                    achievement_id = achievement.get("crc_id", "")
                    count = achievement.get("count", "0")
                    
                    # Get achievement data
                    achievement_info = self.achievement_data.get(achievement_id, {
                        "name": "Unknown Achievement",
                        "max": 100
                    })
                    
                    # Format display values
                    formatted_id = f"Article {achievement_id}"
                    formatted_count = f"{count}/{achievement_info['max']}"
                    
                    # Determine status
                    status = self._determine_status(count, achievement_info['max'])
                    
                    # Get appropriate tag for status
                    status_tag = status.lower().replace(" ", "_")
                    
                    self.achievements_tree.insert("", tk.END, values=(
                        formatted_id,
                        achievement_info['name'],
                        formatted_count,
                        status
                    ), tags=(status_tag,))
                    
                except Exception as e:
                    self.logger.error(f"Error processing achievement {achievement_id}: {str(e)}", exc_info=True)

            # Configure tags for color-coding
            self.achievements_tree.tag_configure('not_started', foreground='#FF0000')  # Red
            self.achievements_tree.tag_configure('in_progress', foreground='#FFA500') # Orange
            self.achievements_tree.tag_configure('complete', foreground='#00FF00')    # Green

            self.logger.debug("Achievements loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading achievements: {str(e)}", exc_info=True)
            raise

    def _determine_status(self, count: str, max_value: int) -> str:
        """Determine achievement status based on count value and maximum"""
        try:
            count_val = int(count)
            if count_val >= max_value:
                return "Complete"
            elif count_val > 0:
                return "In Progress"
            else:
                return "Not Started"
        except ValueError:
            return "Unknown"

    def save_achievement_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        self.logger.debug("Saving achievement changes")
        try:
            root = tree.getroot()
            
            for item in self.achievements_tree.get_children():
                try:
                    values = self.achievements_tree.item(item)["values"]
                    achievement_id = values[0].replace("Article ", "")
                    count = values[2].split("/")[0]  # Extract count from "X/Y" format

                    self.logger.debug(f"Processing achievement {achievement_id} with new count: {count}")

                    # Find and update achievement in XML
                    achievement = root.find(f".//AchievementCounter[@crc_id='{achievement_id}']")
                    if achievement is not None:
                        achievement.set("count", count)
                        self.logger.debug(f"Successfully updated achievement {achievement_id}")
                    else:
                        self.logger.warning(f"Achievement {achievement_id} not found in XML")

                except Exception as e:
                    self.logger.error(f"Error processing achievement update: {str(e)}", exc_info=True)
                    continue

            self.logger.debug("Achievement changes saved successfully")
            return tree
            
        except Exception as e:
            self.logger.error(f"Error saving achievement changes: {str(e)}", exc_info=True)
            raise

    def _complete_all_achievements(self) -> None:
        self.logger.debug("Completing all achievements")
        try:
            for item in self.achievements_tree.get_children():
                try:
                    values = list(self.achievements_tree.item(item)["values"])
                    achievement_id = values[0].replace("Article ", "")
                    max_value = self.achievement_data.get(achievement_id, {"max": 100})["max"]
                    
                    values[2] = f"{max_value}/{max_value}"  # Set to max value
                    values[3] = "Complete"  # Update status
                    self.achievements_tree.item(item, values=values, tags=('complete',))
                    self.logger.debug(f"Completed achievement: {values[0]}")
                except Exception as e:
                    self.logger.error(f"Error completing individual achievement: {str(e)}", exc_info=True)
                    continue
            
            self.main_window.unsaved_label.config(text="Unsaved Changes")
            self.logger.debug("All achievements completed successfully")
            messagebox.showinfo("Success", "All achievements completed!")
            
        except Exception as e:
            self.logger.error(f"Error in complete all achievements: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to complete all achievements: {str(e)}")

    def _complete_selected(self) -> None:
        """Complete the selected achievements"""
        selected_items = self.achievements_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select at least one achievement")
            return

        try:
            for item in selected_items:
                values = list(self.achievements_tree.item(item)["values"])
                achievement_id = values[0].replace("Article ", "")
                max_value = self.achievement_data.get(achievement_id, {"max": 100})["max"]
                
                values[2] = f"{max_value}/{max_value}"  # Set to max value
                values[3] = "Complete"  # Update status
                self.achievements_tree.item(item, values=values, tags=('complete',))

            self.main_window.unsaved_label.config(text="Unsaved Changes")
            messagebox.showinfo("Success", "Selected achievements completed!")

        except Exception as e:
            self.logger.error(f"Error completing achievements: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to complete achievements: {str(e)}")
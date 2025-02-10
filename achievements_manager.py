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
        self.setup_ui()

    def setup_ui(self) -> None:
        # Create Achievements Treeview
        tree_frame = ttk.Frame(self.parent, height=280)
        tree_frame.pack(fill=tk.X, pady=5)
        tree_frame.pack_propagate(False)  # This prevents the frame from auto-adjusting to content

        ttk.Label(tree_frame, text="Achievements Status").pack()

        # Create Treeview
        columns = ("Name", "Status")
        self.achievements_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings"
        )

        # Configure columns
        self.achievements_tree.heading("Name", text="Achievement")
        self.achievements_tree.heading("Status", text="Status")

        self.achievements_tree.column("Name", width=100)
        self.achievements_tree.column("Status", width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.achievements_tree.yview)
        self.achievements_tree.configure(yscrollcommand=scrollbar.set)

        self.achievements_tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create edit frame
        edit_frame = ttk.LabelFrame(self.parent, text="Edit Achievement", padding=10)
        edit_frame.pack(fill=tk.X, pady=5)

        # Achievements button
        ttk.Button(
            edit_frame,
            text="Unlock All Achievements",
            command=self._unlock_all_achievements
        ).grid(row=1, column=0, pady=10)

    def load_achievements(self, tree: ET.ElementTree) -> None:
        self.logger.debug("Loading achievements")
        try:
            # Clear existing items
            for item in self.achievements_tree.get_children():
                self.achievements_tree.delete(item)

            # Find all AchievementCounter elements in XML
            achievements = tree.findall(".//AchievementCounter")
            self.logger.debug(f"Found {len(achievements)} achievements")
            
            for achievement in achievements:
                try:
                    achievement_id = achievement.get("crc_id", "")
                    # The value attribute determines if achievement is unlocked (1) or locked (0)
                    status = "Unlocked" if achievement.get("value", "0") == "2" else "Locked"
                    
                    self.logger.debug(f"Processing achievement {achievement_id} with status: {status}")
                    
                    self.achievements_tree.insert("", tk.END, values=(
                        f"Achievement {achievement_id}",
                        status
                    ))
                    
                except Exception as e:
                    self.logger.error(f"Error processing achievement {achievement_id}: {str(e)}", exc_info=True)

            self.logger.debug("Achievements loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading achievements: {str(e)}", exc_info=True)
            raise

    def save_achievement_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        self.logger.debug("Saving achievement changes")
        try:
            root = tree.getroot()
            
            for item in self.achievements_tree.get_children():
                try:
                    values = self.achievements_tree.item(item)["values"]
                    achievement_id = values[0].replace("Achievement ", "")  # Extract ID from "Achievement X"
                    status = "2" if values[1] == "Unlocked" else "0"

                    self.logger.debug(f"Processing achievement {achievement_id} with new status: {status}")

                    # Find and update achievement in XML
                    achievement = root.find(f".//AchievementCounter[@crc_id='{achievement_id}']")
                    if achievement is not None:
                        achievement.set("value", status)
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
    
    def _unlock_all_achievements(self) -> None:
        self.logger.debug("Unlocking all achievements")
        try:
            # Update all items in the tree to Unlocked
            for item in self.achievements_tree.get_children():
                try:
                    values = list(self.achievements_tree.item(item)["values"])
                    values[1] = "Unlocked"
                    self.achievements_tree.item(item, values=values)
                    self.logger.debug(f"Unlocked achievement: {values[0]}")
                except Exception as e:
                    self.logger.error(f"Error unlocking individual achievement: {str(e)}", exc_info=True)
                    continue
            
            self.main_window.unsaved_label.config(text="Unsaved Changes")
            self.logger.debug("All achievements unlocked successfully")
            messagebox.showinfo("Success", "All achievements unlocked!")
            
        except Exception as e:
            self.logger.error(f"Error in unlock all achievements: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to unlock all achievements: {str(e)}")










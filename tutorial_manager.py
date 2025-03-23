import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
from typing import Dict, Optional
import logging

class TutorialManager:
    def __init__(self, parent: ttk.Frame, main_window):
        self.logger = logging.getLogger('TutorialManager')
        self.logger.debug("Initializing TutorialManager")
        self.parent = parent
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self) -> None:
        # Create Tutorials Treeview that fills the entire parent space
        tree_frame = ttk.Frame(self.parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(tree_frame, text="Tutorial Completion Status").pack()

        # Create Treeview with columns
        columns = ("ID", "Name", "Status")
        self.tutorials_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="extended"
        )

        # Configure columns
        self.tutorials_tree.heading("ID", text="Tutorial ID")
        self.tutorials_tree.heading("Name", text="Tutorial Name")
        self.tutorials_tree.heading("Status", text="Status")

        # Set column widths and alignment
        self.tutorials_tree.column("ID", width=120, anchor="w")
        self.tutorials_tree.column("Name", width=550, anchor="w")
        self.tutorials_tree.column("Status", width=120, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tutorials_tree.yview)
        self.tutorials_tree.configure(yscrollcommand=scrollbar.set)

        self.tutorials_tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configure tags for color-coding
        self.tutorials_tree.tag_configure('completed', foreground='#00FF00')   # Green
        self.tutorials_tree.tag_configure('not_completed', foreground='#FF0000')   # Red

        # Statistics frame
        stats_frame = ttk.Frame(tree_frame)
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.tutorial_count_label = ttk.Label(stats_frame, text="Total tutorials completed: 0/0")
        self.tutorial_count_label.pack(side=tk.LEFT, padx=10)

    def load_tutorials(self, tree: ET.ElementTree) -> None:
        self.logger.debug("Loading tutorials")
        try:
            # Clear existing items
            for item in self.tutorials_tree.get_children():
                self.tutorials_tree.delete(item)
            
            # Find all tutorial elements in XML
            completed_tutorials = tree.findall(".//AvatarTutorialDB_Status/Tutorial_Completed")
            
            self.logger.debug(f"Found {len(completed_tutorials)} completed tutorials")
            
            # Create a set of completed tutorial IDs
            completed_tutorial_ids = {tutorial.get("crc_id", "") for tutorial in completed_tutorials}
            
            # Get the full list of tutorials (both completed and not completed)
            all_tutorials = self._get_all_tutorial_ids()
            
            # Sort tutorials by ID for consistent display
            sorted_tutorials = sorted(all_tutorials.keys())
            
            # Process each tutorial
            for tutorial_id in sorted_tutorials:
                try:
                    # Get the tutorial name from our mapping
                    tutorial_name = all_tutorials[tutorial_id]
                    
                    # Check if tutorial is completed
                    is_completed = tutorial_id in completed_tutorial_ids
                    status = "Completed" if is_completed else "Not Completed"
                    
                    # Determine tag based on status
                    tag = "completed" if is_completed else "not_completed"
                    
                    self.tutorials_tree.insert("", tk.END, values=(
                        tutorial_id,
                        tutorial_name,
                        status
                    ), tags=(tag,))
                    
                except Exception as e:
                    self.logger.error(f"Error processing tutorial {tutorial_id}: {str(e)}", exc_info=True)

            # Update statistics
            total_tutorials = len(all_tutorials)
            completed_count = len(completed_tutorial_ids)
            self.tutorial_count_label.config(text=f"Total tutorials completed: {completed_count}/{total_tutorials}")
            
            self.logger.debug("Tutorials loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading tutorials: {str(e)}", exc_info=True)
            raise

    def save_tutorial_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        self.logger.debug("Tutorials are view-only, no changes to save")
        # Since this is just a view-only tab, simply return the tree unchanged
        return tree
    
    def _get_all_tutorial_ids(self):
        """Return a dictionary of all tutorial IDs and their names"""
        tutorial_names = {
            # Basic Controls & Navigation
            "44333413": "Basic Movement Tutorial",
            "158780422": "Navigation Interface Tutorial",
            "304605938": "Camera Controls Tutorial",
            "734413258": "Game Menu Navigation",
            "1360295752": "Map & Waypoint Tutorial",
            
            # Combat Tutorials
            "1376083454": "Basic Combat Tutorial",
            "1579340642": "Ranged Weapon Tutorial",
            "1827545044": "Melee Combat Tutorial",
            "1836020734": "Stealth Combat Tutorial",
            "2013777292": "Vehicle Combat Tutorial",
            
            # Skills & Abilities
            "2038369977": "Skill Tree Tutorial",
            "2046890945": "Special Abilities Tutorial",
            "2513987320": "Na'vi Bond Tutorial",
            "2654429851": "Character Progression Tutorial",
            "2738798113": "Equipment Tutorial",
            
            # Environment & Interaction
            "2924024297": "Environmental Interaction Tutorial",
            "3610527961": "Resource Gathering Tutorial",
            "4202415783": "Crafting System Tutorial",
            "4215961224": "Pandoran Creatures Tutorial",
            "4274987001": "Survival Tips Tutorial"
        }
        return tutorial_names

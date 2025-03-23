import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Set
import logging

class VehicleManager:
    def __init__(self, parent: ttk.Frame, main_window):
        self.logger = logging.getLogger('VehicleManager')
        self.logger.debug("Initializing VehicleManager")
        self.parent = parent
        self.main_window = main_window
        self.entered_vehicles = set()  # Store entered vehicle IDs
        self.first_travel_bark_played = False  # Track if first travel bark played
        self.setup_ui()

    def setup_ui(self) -> None:
        # Create main container frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create top section with travel bark status
        status_frame = ttk.LabelFrame(main_frame, text="Travel Status")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add travel bark status label (view-only)
        self.first_travel_status = ttk.Label(
            status_frame,
            text="First Travel Tutorial Played: No"
        )
        self.first_travel_status.pack(padx=10, pady=5, anchor="w")
        
        # Create vehicles treeview
        tree_frame = ttk.LabelFrame(main_frame, text="Vehicle Knowledge")
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Create Treeview with columns
        columns = ("ID", "Name", "Type", "Status")
        self.vehicles_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="extended"
        )

        # Configure columns
        self.vehicles_tree.heading("ID", text="Vehicle ID")
        self.vehicles_tree.heading("Name", text="Vehicle Name")
        self.vehicles_tree.heading("Type", text="Type")
        self.vehicles_tree.heading("Status", text="Entered")

        # Set column widths and alignment
        self.vehicles_tree.column("ID", width=120, anchor="w")
        self.vehicles_tree.column("Name", width=300, anchor="w")
        self.vehicles_tree.column("Type", width=150, anchor="w")
        self.vehicles_tree.column("Status", width=80, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.vehicles_tree.yview)
        self.vehicles_tree.configure(yscrollcommand=scrollbar.set)

        self.vehicles_tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configure tags for color-coding
        self.vehicles_tree.tag_configure('entered', foreground='#00FF00')   # Green
        self.vehicles_tree.tag_configure('not_entered', foreground='#FF0000')   # Red
        
        # No buttons - view only interface
        
        # Statistics label
        self.stats_label = ttk.Label(main_frame, text="Vehicles entered: 0/0")
        self.stats_label.pack(anchor="w", pady=5)

    def load_vehicles(self, tree: ET.ElementTree) -> None:
        self.logger.debug("Loading vehicle knowledge")
        try:
            # Clear existing data
            self.entered_vehicles = set()
            self.first_travel_bark_played = False
            
            # Clear existing items in treeview
            for item in self.vehicles_tree.get_children():
                self.vehicles_tree.delete(item)
            
            # Get BarkKnowledge element
            bark_element = tree.find(".//BarkKnowledge")
            if bark_element is not None:
                # Check first travel bark status
                first_travel = bark_element.get("FirstTravelBarkPlayed", "0")
                self.first_travel_bark_played = (first_travel == "1")
                self.first_travel_status.config(
                    text=f"First Travel Tutorial Played: {'Yes' if self.first_travel_bark_played else 'No'}"
                )
                
                # Find all entered vehicle elements
                vehicle_elements = bark_element.findall("EnteredVehicle")
                for vehicle in vehicle_elements:
                    vehicle_id = vehicle.get("crc_vehicleItem", "")
                    if vehicle_id:
                        self.entered_vehicles.add(vehicle_id)
            
            # Get all known vehicles
            all_vehicles = self._get_all_vehicle_ids()
            
            # Add all vehicles to treeview
            for vehicle_id, vehicle_info in all_vehicles.items():
                is_entered = vehicle_id in self.entered_vehicles
                status = "Yes" if is_entered else "No"
                tag = "entered" if is_entered else "not_entered"
                
                self.vehicles_tree.insert("", tk.END, values=(
                    vehicle_id,
                    vehicle_info["name"],
                    vehicle_info["type"],
                    status
                ), tags=(tag,))
            
            # Update statistics
            total_vehicles = len(all_vehicles)
            entered_count = len(self.entered_vehicles)
            self.stats_label.config(text=f"Vehicles entered: {entered_count}/{total_vehicles}")
            
            self.logger.debug(f"Loaded {entered_count} entered vehicles out of {total_vehicles} total")
            
        except Exception as e:
            self.logger.error(f"Error loading vehicle knowledge: {str(e)}", exc_info=True)
            raise

    def save_vehicle_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        """Save vehicle knowledge (no changes, view-only)"""
        self.logger.debug("Vehicle knowledge is view-only, no changes to save")
        # Just return the tree unchanged since this is view-only
        return tree

    def _get_all_vehicle_ids(self):
        """Return a dictionary of all vehicle IDs with their names and types"""
        vehicle_info = {
            # RDA Ground Vehicles
            "2700952790": {
                "name": "AMP Suit",
                "type": "RDA Ground Vehicle"
            },
            "439556112": {
                "name": "Swan", 
                "type": "RDA Ground Vehicle"
            },
            "2618300662": {
                "name": "Buggy",
                "type": "RDA Ground Vehicle"
            },
            "2142115644": {
                "name": "Grinder",
                "type": "RDA Ground Vehicle"
            },
            
            # RDA Air Vehicles
            "3536212596": {
                "name": "Samson",
                "type": "RDA Air Vehicle"
            },
            "544484482": {
                "name": "Scorpion",
                "type": "RDA Air Vehicle"
            },
            "3894271835": {
                "name": "Dragon Assault Ship",
                "type": "RDA Air Vehicle"
            },
            
            # Na'vi Mounts
            "1295738421": {
                "name": "Direhorse",
                "type": "Na'vi Mount"
            },
            "3715482590": {
                "name": "Mountain Banshee",
                "type": "Na'vi Mount"
            },
            "982156324": {
                "name": "Great Leonopteryx",
                "type": "Na'vi Mount"
            },
            
            # Water Vehicles
            "2839450678": {
                "name": "Gator",
                "type": "Water Vehicle"
            },
            "1056389427": {
                "name": "Na'vi Boat",
                "type": "Water Vehicle"
            }
        }
        return vehicle_info
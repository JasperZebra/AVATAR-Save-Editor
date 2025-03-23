import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
from typing import Dict, Optional
import logging

class PinsManager:
    def __init__(self, parent: ttk.Frame, main_window):
        self.logger = logging.getLogger('PinsManager')
        self.logger.debug("Initializing PinsManager")
        self.parent = parent
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self) -> None:
        # Create Pins Treeview - make it fill the entire parent space
        tree_frame = ttk.Frame(self.parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(tree_frame, text="Map Pins Status").pack()

        # Create Treeview with columns
        columns = ("ID", "Location", "Status", "Counters")
        self.pins_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="extended"
        )

        # Configure columns
        self.pins_tree.heading("ID", text="Pin ID")
        self.pins_tree.heading("Location", text="Location")
        self.pins_tree.heading("Status", text="Status")
        self.pins_tree.heading("Counters", text="Completion Counters")

        # Set column widths and alignment
        self.pins_tree.column("ID", width=120, anchor="w")
        self.pins_tree.column("Location", width=450, anchor="w")
        self.pins_tree.column("Status", width=120, anchor="center")
        self.pins_tree.column("Counters", width=120, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.pins_tree.yview)
        self.pins_tree.configure(yscrollcommand=scrollbar.set)

        self.pins_tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configure tags for color-coding
        self.pins_tree.tag_configure('unlocked', foreground='#00FF00')   # Green
        self.pins_tree.tag_configure('locked', foreground='#FF0000')     # Red

    def load_pins(self, tree: ET.ElementTree) -> None:
        self.logger.debug("Loading pins")
        try:
            # Clear existing items
            for item in self.pins_tree.get_children():
                self.pins_tree.delete(item)
            
            # Find all pin elements in XML
            pins = tree.findall(".//AvatarPinDB_Status/Pin")
            
            self.logger.debug(f"Found {len(pins)} pins")
            
            # Sort pins by ID for consistent display
            pins_sorted = sorted(pins, key=lambda x: x.get("crc_id", "0"))
            
            # Process each pin
            for pin in pins_sorted:
                try:
                    pin_id = pin.get("crc_id", "")
                    unlocked = pin.get("eUnlocked", "0")
                    
                    # Get the pin location name
                    location_name = self._get_location_name(pin_id)
                    
                    # Get status text
                    status = "Unlocked" if unlocked == "2" else "Locked"
                    
                    # Count completion counters
                    counters = len(pin.findall("CompletionCounter"))
                    counters_text = f"{counters}" if counters > 0 else "None"
                    
                    # Determine tag based on unlocked status
                    tag = "unlocked" if unlocked == "2" else "locked"
                    
                    self.pins_tree.insert("", tk.END, values=(
                        pin_id,
                        location_name,
                        status,
                        counters_text
                    ), tags=(tag,))
                    
                except Exception as e:
                    self.logger.error(f"Error processing pin {pin_id}: {str(e)}", exc_info=True)

            self.logger.debug("Pins loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading pins: {str(e)}", exc_info=True)
            raise

    def save_pin_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        self.logger.debug("Pins are view-only, no changes to save")
        # Since this is just a view-only tab, simply return the tree unchanged
        return tree
    
    def _get_location_name(self, pin_id):
        """Convert pin ID to human-readable location name"""
        location_names = {
            # Tutorial/Starting Areas
            "3409126972": "Tutorial Area - Valley of the Ancestors",
            "238707229": "Training Grounds",
            "2292208788": "RDA Training Facility",
            
            # Main Areas
            "355473279": "Plains of Goliath - Forest Hunting Area",
            "615754132": "Crystal Fields - Pandoran Highlands",
            "1172651822": "Emerald Forest - Thanator Territory",
            "1847852653": "Torchwood Forest - Waterfall Sanctuary",
            "2171723794": "Swamps of Silence - Plains Clan Village",
            "2587251285": "Northern Shelf - Na'vi Sacred Site",
            "2961077726": "Willow Glade - Hallelujah Mountains Lookout",
            "3616200713": "Tantalus - Western Ridge Outpost",
            
            # Special Areas
            "1057194188": "Pandoran Abyss - Hell's Gate Perimeter",
            "2856892107": "Floating Mountains - Banshee Rookery",
            "3822194552": "Sacred Grove - River Trading Post",
            "1504064473": "Luminous Valley - Floating Mountains Research Site",
            
            # RDA Areas
            "2752812145": "RDA Main Base - Tree of Souls",
            "837458676": "RDA Research Station - Hometree Location",
            "1771880106": "RDA Mining Site - Viperwolf Den",
            
            # Combat Zones
            "470159002": "Battlefield Delta - Flux Vortex Field",
            "2216033045": "Combat Arena Alpha - RDA Avatar Training Grounds",
            "60855408": "War Zone Beta - Jungle Expedition Route",
            
            # Wilderness
            "3975313082": "Wild Plains - Abandoned Human Camp",
            "2169212369": "Dense Jungle - Hexapede Grazing Fields",
            "1578821154": "Mountain Pass - Bioluminescent Forest",
            "1782610090": "Hidden Valley - Cliffside Refuge",
            
            # Cave Systems
            "1628184437": "Crystal Caverns - RDA Communications Tower",
            "1865345760": "Echo Caves - Thundering Rocks Valley",
            "3564339531": "Underground Network - Eastern Sea Coast",
            
            # Water Areas
            "4294730242": "River Delta - Mountain Banshee Nesting Area",
            "1741938656": "Great Lake - Sturmbeest Migration Path",
            "2555792139": "Waterfall Basin - Pandoran Crater Lake",
            
            # Ancient Ruins
            "2353717556": "Ancient Temple - Hallelujah Mountains Research Site",
            "2001468046": "Lost City - Grasslands Village",
            "3903502716": "Sacred Ruins - Northern Ice Fields",
            
            # Unique Biomes
            "3852438644": "Bioluminescent Forest - Desert Region Border",
            "2232107097": "Fungal Grove - Great Rock Arch",
            "2185381138": "Living Mountain - Direhorse Training Grounds",
            
            # Na'vi Areas
            "2672591835": "Na'vi Village - Ancient Tree of Voices",
            "105239137": "Tree of Souls - RDA Security Checkpoint",
            "3575765971": "Hometree - Floating Stone Arches",
            
            # Border Regions
            "902032528": "Northern Border - Jungle Canopy Lookout",
            "948986278": "Eastern Frontier - Deep Forest Spring",
            "1437051617": "Southern Boundary - Mountain Pass",
            
            # Mission Areas
            "2427499480": "Mission Zone Alpha - Desolate Highlands",
            "2509501782": "Mission Zone Beta - Volcanic Activity Zone",
            "4220570174": "Mission Zone Gamma - Pandoran Wetlands",
            
            # Resource Areas
            "408444403": "Unobtanium Mine - Cave System Entrance",
            "1846881984": "Resource Valley - Ikran Hunting Grounds",
            "4168272830": "Mining Complex - Abandoned Na'vi Settlement",
            
            # Others
            "194406935": "Swamp Region Outpost",
            "3615918544": "Toruk Hunting Grounds",
            "2943222331": "Hanging Mountains Pass",
            "3586942544": "Iknimaya Training Ground"
        }        
        return location_names.get(pin_id, f"Unknown Location ({pin_id})")

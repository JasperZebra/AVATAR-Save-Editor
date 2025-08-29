import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
from typing import Dict, Optional
from ui_components import EnhancedTooltip
import logging
from custom_messagebox import MessageBoxManager, show_info, show_error, show_warning, ask_question, ask_ok_cancel, show_success


class MapsManager:
    def __init__(self, parent: ttk.Frame, main_window=None):
        self.logger = logging.getLogger('MapsManager')
        self.logger.debug("Initializing Modern MapsManager")
        self.parent = parent
        self.main_window = main_window
        self.map_data = {}
        self.filter_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.setup_modern_ui()

    def setup_modern_ui(self) -> None:
        # Create main container with padding
        self.main_container = ttk.Frame(self.parent)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # === HEADER SECTION ===
        self.create_header_section()
        
        # === CONTENT AREA (Split layout) ===
        content_frame = ttk.Frame(self.main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        # Left sidebar (stats and info)
        self.create_sidebar(content_frame)
        
        # Main content area (maps list)
        self.create_main_content(content_frame)

    def create_header_section(self):
        """Create the header with title and search"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title and subtitle
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = ttk.Label(title_frame, text="🗺️ Map Atlas", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="Explore Pandora's diverse regions and territories", 
                                  font=('Segoe UI', 9), foreground='gray')
        subtitle_label.pack(anchor=tk.W)
        
        # Search section
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side=tk.RIGHT)
        
        ttk.Label(search_frame, text="🔍 Search:", font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25, font=('Segoe UI', 9))
        search_entry.pack(side=tk.LEFT)
        search_entry.bind("<KeyRelease>", self._apply_filter)

    def create_sidebar(self, parent):
        """Create the left sidebar with statistics and information"""
        sidebar_frame = ttk.Frame(parent, width=300)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        sidebar_frame.pack_propagate(False)
        
        # === EXPLORATION OVERVIEW ===
        overview_frame = ttk.LabelFrame(sidebar_frame, text="🌍 Exploration Overview", padding=15)
        overview_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Large map count display
        self.exploration_display = ttk.Frame(overview_frame)
        self.exploration_display.pack(fill=tk.X, pady=(0, 10))
        
        self.map_count = ttk.Label(
            self.exploration_display, 
            text="0", 
            font=('Segoe UI', 24, 'bold'),
            foreground='#2e7d32'
        )
        self.map_count.pack()
        
        ttk.Label(self.exploration_display, text="Regions Available", font=('Segoe UI', 10)).pack()
                        
    def create_stat_item(self, parent, icon, label, value, var_name):
        """Create a statistics item with icon, label, and value"""
        stat_frame = ttk.Frame(parent)
        stat_frame.pack(fill=tk.X, pady=2)
        
        # Icon and label
        label_frame = ttk.Frame(stat_frame)
        label_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(label_frame, text=f"{icon} {label}:", font=('Segoe UI', 9)).pack(side=tk.LEFT)
        
        # Value (right-aligned)
        value_label = ttk.Label(stat_frame, text=value, font=('Segoe UI', 9, 'bold'))
        value_label.pack(side=tk.RIGHT)
        
        # Store reference to update later
        setattr(self, var_name, value_label)

    def create_main_content(self, parent):
        """Create the main content area with maps list"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Maps list header
        list_header = ttk.Frame(main_frame)
        list_header.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(list_header, text="🗺️ Pandoran Regions", 
                 font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)
        
        # Region type legend
        legend_frame = ttk.Frame(list_header)
        legend_frame.pack(side=tk.RIGHT)
        
        legend_items = [("🌿", "Natural"), ("🏭", "RDA"), ("🏛️", "Ancient"), ("⚔️", "Combat")]
        for icon, desc in legend_items:
            ttk.Label(legend_frame, text=f"{icon} {desc}", font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=3)
        
        # Enhanced maps treeview
        tree_container = ttk.Frame(main_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure columns for better information display
        columns = ("type_icon", "name", "region_type", "biome", "id", "details")
        self.maps_tree = ttk.Treeview(tree_container, columns=columns, show="headings", 
                                     selectmode="extended", height=20)
        
        # Configure headers
        headers = {
            "type_icon": ("🏷️", 60, "center"),
            "name": ("🗺️ Region Name", 250, "w"),
            "region_type": ("🏞️ Type", 120, "w"),
            "biome": ("🌍 Biome", 150, "w"),
            "id": ("🆔 ID", 100, "center"),
            "details": ("ℹ️ Info", 100, "center")
        }
        
        for col, (text, width, anchor) in headers.items():
            self.maps_tree.heading(col, text=text)
            self.maps_tree.column(col, width=width, anchor=anchor, minwidth=50)
        
        # Enhanced color scheme
        self.setup_tree_styles()
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.maps_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.maps_tree.xview)
        self.maps_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.maps_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.maps_tree.bind("<Double-1>", self._on_map_double_click)
        self.maps_tree.bind("<Button-3>", self._show_map_context_menu)

    def setup_tree_styles(self):
        """Configure tree styling with modern color scheme"""
        self.maps_tree.tag_configure('natural', 
                                     background='#e8f5e8', 
                                     foreground="#00ff0d")
        self.maps_tree.tag_configure('rda', 
                                     background='#fff3e0', 
                                     foreground="#ff7300")
        self.maps_tree.tag_configure('ancient', 
                                     background='#f3e5f5', 
                                     foreground="#b300ff")
        self.maps_tree.tag_configure('combat', 
                                     background='#ffebee', 
                                     foreground="#ff0000")
        self.maps_tree.tag_configure('tutorial', 
                                     background='#e3f2fd', 
                                     foreground="#0077ff")
        self.maps_tree.tag_configure('water', 
                                     background='#e0f2f1', 
                                     foreground="#00ffe1")

    def load_maps_data(self, tree: ET.ElementTree) -> None:
        """Load map data with modern interface"""
        self.logger.debug("Loading map data with modern interface")
        try:
            # Clear existing data
            self.map_data = {}
            
            # Clear existing items in treeview
            for item in self.maps_tree.get_children():
                self.maps_tree.delete(item)

            # Find the fog of war database section
            fow_db = tree.find(".//AvatarFogOfWarDB_Status")
            if fow_db is None:
                self.logger.warning("No AvatarFogOfWarDB_Status element found in XML")
                return

            maps = fow_db.findall("./FoW_Map")
            self.logger.debug(f"Found {len(maps)} maps")
            
            for map_elem in maps:
                try:
                    map_id = map_elem.get("crc_id", "")
                    
                    # Get map information
                    map_name = self._get_map_name_from_id(map_id)
                    region_type = self._get_region_type(map_name)
                    biome = self._get_biome_type(map_name)
                    
                    # Store map data
                    self.map_data[map_id] = {
                        'name': map_name,
                        'region_type': region_type,
                        'biome': biome
                    }
                    
                    # Determine type icon and styling
                    type_icon, tag = self._get_map_display_info(region_type)
                    
                    # Insert into tree
                    self.maps_tree.insert("", tk.END, values=(
                        type_icon,
                        map_name,
                        region_type,
                        biome,
                        map_id,
                        "View Details"
                    ), tags=(tag,))
                    
                    self.logger.debug(f"Successfully added map {map_id} to tree")
                
                except Exception as e:
                    self.logger.error(f"Error processing individual map: {str(e)}", exc_info=True)

            # Update all displays
            self._update_all_displays()
            
            self.logger.debug("Map data loading completed with modern interface")
            
        except Exception as e:
            self.logger.error(f"Error loading map data: {str(e)}", exc_info=True)
            raise

    def _get_region_type(self, map_name):
        """Determine region type based on map name"""
        name_lower = map_name.lower()
        
        if any(keyword in name_lower for keyword in ['tutorial', 'training', 'grounds']):
            return "Tutorial"
        elif any(keyword in name_lower for keyword in ['rda', 'base', 'facility', 'mining', 'research']):
            return "RDA Territory"
        elif any(keyword in name_lower for keyword in ['ancient', 'temple', 'ruins', 'sacred', 'tree of souls']):
            return "Ancient Site"
        elif any(keyword in name_lower for keyword in ['battlefield', 'combat', 'war zone', 'arena']):
            return "Combat Zone"
        elif any(keyword in name_lower for keyword in ['river', 'lake', 'waterfall', 'delta', 'basin']):
            return "Water Region"
        elif any(keyword in name_lower for keyword in ['mountain', 'floating', 'pass', 'peak']):
            return "Mountain Area"
        else:
            return "Natural Area"

    def _get_biome_type(self, map_name):
        """Determine biome type based on map name"""
        name_lower = map_name.lower()
        
        if any(keyword in name_lower for keyword in ['forest', 'jungle', 'grove', 'tree']):
            return "Forest"
        elif any(keyword in name_lower for keyword in ['swamp', 'bog', 'marsh']):
            return "Wetland"
        elif any(keyword in name_lower for keyword in ['plain', 'valley', 'field']):
            return "Grassland"
        elif any(keyword in name_lower for keyword in ['mountain', 'peak', 'cliff']):
            return "Mountain"
        elif any(keyword in name_lower for keyword in ['cave', 'cavern', 'underground']):
            return "Subterranean"
        elif any(keyword in name_lower for keyword in ['water', 'river', 'lake', 'lagoon']):
            return "Aquatic"
        elif any(keyword in name_lower for keyword in ['desert', 'arid', 'dry']):
            return "Desert"
        else:
            return "Mixed"

    def _get_map_display_info(self, region_type):
        """Get display icon and tag for a region type"""
        type_mapping = {
            "Natural Area": ("🌿", "natural"),
            "RDA Territory": ("🏭", "rda"),
            "Ancient Site": ("🏛️", "ancient"),
            "Combat Zone": ("⚔️", "combat"),
            "Tutorial": ("🎓", "tutorial"),
            "Water Region": ("💧", "water"),
            "Mountain Area": ("🏔️", "natural")
        }
        
        return type_mapping.get(region_type, ("🗺️", "natural"))

    def _update_all_displays(self):
        """Update all display elements"""
        total_maps = len(self.map_data)
        
        # Update main map count
        self.map_count.config(text=str(total_maps))
        
        # Count by region type
        type_counts = {}
        for map_data in self.map_data.values():
            region_type = map_data['region_type']
            type_counts[region_type] = type_counts.get(region_type, 0) + 1
                
    def _apply_filter(self, event=None):
        """Apply search and filter to the maps list"""
        filter_value = self.filter_var.get()
        search_text = self.search_var.get().lower()
        
        # Clear and repopulate tree
        for item in self.maps_tree.get_children():
            self.maps_tree.delete(item)
        
        # Re-add filtered items
        for map_id, map_data in self.map_data.items():
            if self._should_show_map(map_id, map_data, filter_value, search_text):
                region_type = map_data['region_type']
                type_icon, tag = self._get_map_display_info(region_type)
                
                self.maps_tree.insert("", tk.END, values=(
                    type_icon,
                    map_data['name'],
                    region_type,
                    map_data['biome'],
                    map_id,
                    "View Details"
                ), tags=(tag,))

    def _should_show_map(self, map_id, map_data, filter_value, search_text):
        """Determine if map should be shown based on filters"""
        name = map_data['name']
        region_type = map_data['region_type']
        biome = map_data['biome']
        
        # Apply filter
        if filter_value == "🌿 Natural Areas" and region_type != "Natural Area":
            return False
        elif filter_value == "🏭 RDA Territories" and region_type != "RDA Territory":
            return False
        elif filter_value == "🏛️ Ancient Sites" and region_type != "Ancient Site":
            return False
        elif filter_value == "⚔️ Combat Zones" and region_type != "Combat Zone":
            return False
        elif filter_value == "🎓 Tutorial Areas" and region_type != "Tutorial":
            return False
        elif filter_value == "💧 Water Regions" and region_type != "Water Region":
            return False
        elif filter_value == "🏔️ Mountain Areas" and region_type != "Mountain Area":
            return False
        
        # Apply search
        if search_text and search_text not in name.lower() and search_text not in map_id.lower() and search_text not in biome.lower():
            return False
        
        return True

    def _on_map_double_click(self, event):
        """Handle double-click on map in list"""
        item = self.maps_tree.selection()[0] if self.maps_tree.selection() else None
        if item:
            values = self.maps_tree.item(item, "values")
            map_id = values[4]  # ID is at index 4
            self._show_map_details(map_id)

    def _show_map_context_menu(self, event):
        """Show context menu for maps"""
        if self.maps_tree.selection():
            context_menu = tk.Menu(self.maps_tree, tearoff=0)
            context_menu.add_command(label="📋 Copy Map ID", command=self._copy_map_id)
            context_menu.add_command(label="ℹ️ Show Details", command=self._show_selected_map_details)
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()


    def _copy_map_id(self):
        """Copy selected map ID to clipboard"""
        selected = self.maps_tree.selection()
        if selected:
            values = self.maps_tree.item(selected[0], "values")
            map_id = values[4]  # ID is at index 4
            self.parent.clipboard_clear()
            self.parent.clipboard_append(map_id)
            show_info("Copied", f"📋 Map ID copied to clipboard:\n{map_id}")

    def _show_selected_map_details(self):
        """Show details for selected map"""
        selected = self.maps_tree.selection()
        if selected:
            values = self.maps_tree.item(selected[0], "values")
            map_id = values[4]  # ID is at index 4
            self._show_map_details(map_id)

    def _show_map_details(self, map_id):
        """Show detailed information about a map"""
        if map_id not in self.map_data:
            show_warning("Warning", "Map data not found")
            return
        
        map_data = self.map_data[map_id]
        
        # Create detailed map information dialog
        detail_window = tk.Toplevel(self.parent)
        detail_window.title(f"Region Details - {map_data['name']}")
        detail_window.geometry("1600x800")
        detail_window.resizable(True, True)
        
        # Main frame with padding
        main_frame = ttk.Frame(detail_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        type_icon, _ = self._get_map_display_info(map_data['region_type'])
        title_label = ttk.Label(main_frame, text=f"{type_icon} {map_data['name']}", 
                               font=('Segoe UI', 14, 'bold'))
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Details frame
        details_frame = ttk.LabelFrame(main_frame, text="Region Information", padding=15)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create details text widget
        details_text = tk.Text(details_frame, wrap=tk.WORD, font=('Consolas', 10), 
                              height=18, state=tk.NORMAL)
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=details_text.yview)
        details_text.configure(yscrollcommand=scrollbar.set)
        
        # Format map details
        info_text = f"""🗺️ Region Name: {map_data['name']}
🏞️ Region Type: {map_data['region_type']}
🌍 Biome: {map_data['biome']}
🆔 Map ID: {map_id}

📝 Description:
{'=' * 50}
{self._get_map_description(map_data['name'], map_data['region_type'], map_data['biome'])}

🌍 Environmental Details:
{'=' * 50}
{self._get_environmental_details(map_data['biome'], map_data['region_type'])}

🔧 Technical Details:
{'=' * 50}
Map ID: {map_id}
Region Type: {map_data['region_type']}
Biome Classification: {map_data['biome']}
"""
        
        details_text.insert(tk.END, info_text)
        details_text.config(state=tk.DISABLED)
        
        details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="📋 Copy ID", 
                  command=lambda: self._copy_to_clipboard(map_id)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="✅ Close", 
                  command=detail_window.destroy).pack(side=tk.RIGHT)

    def _get_map_description(self, name, region_type, biome):
        """Get description for a map"""
        if region_type == "Tutorial":
            return f"'{name}' serves as a training ground where new arrivals learn essential skills for survival on Pandora. This controlled environment provides a safe space for learning game mechanics."
        elif region_type == "RDA Territory":
            return f"'{name}' is an RDA-controlled territory featuring human infrastructure and industrial operations. These areas represent the human presence and technological influence on Pandora."
        elif region_type == "Ancient Site":
            return f"'{name}' contains ancient structures and sacred locations significant to Pandoran history and Na'vi culture. These areas hold spiritual and archaeological importance."
        elif region_type == "Combat Zone":
            return f"'{name}' is a contested area where conflicts occur between different factions. Combat training and tactical operations take place in these dangerous regions."
        elif region_type == "Water Region":
            return f"'{name}' features prominent water systems including rivers, lakes, or waterfalls. These aquatic environments support unique ecosystems and wildlife."
        else:
            return f"'{name}' represents a natural area of Pandora showcasing the moon's diverse {biome.lower()} ecosystem with its unique flora, fauna, and environmental characteristics."

    def _get_environmental_details(self, biome, region_type):
        """Get environmental details for a biome"""
        env_details = {
            "Forest": "Dense woodland areas with towering trees, bioluminescent plants, and complex canopy systems supporting diverse wildlife.",
            "Wetland": "Swampy environments with standing water, amphibious creatures, and unique plant adaptations to waterlogged conditions.",
            "Grassland": "Open plains with native grasses, roaming herbivores, and expansive vistas offering strategic advantages.",
            "Mountain": "Elevated terrain with rocky outcrops, floating mountains, and aerial ecosystems unique to Pandora.",
            "Subterranean": "Underground cave systems with crystal formations, echo chambers, and specialized cave-dwelling species.",
            "Aquatic": "Water-dominated environments supporting aquatic life, with unique marine flora and underwater ecosystems.",
            "Desert": "Arid regions with specialized desert-adapted organisms and extreme environmental conditions.",
            "Mixed": "Diverse ecosystems combining multiple biome characteristics in a complex environmental mosaic."
        }
        
        base_description = env_details.get(biome, "A unique Pandoran ecosystem with specialized environmental characteristics.")
        
        if region_type == "RDA Territory":
            return base_description + " Human industrial activity has modified the natural environment with infrastructure and technology."
        else:
            return base_description

    def _copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(text)
            show_info("Copied", f"📋 Copied to clipboard:\n{text}")
        except Exception as e:
            show_error("Error", f"Failed to copy: {str(e)}")
            
    def save_maps_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        """Maps are view-only, return unchanged tree"""
        self.logger.debug("Saving map changes")
        return tree

    def _get_map_name_from_id(self, map_id: str) -> str:
        """Get a readable map name from the map ID"""
        map_names = {
            # Starting/Tutorial Areas
            "3409126972": "Plains of Goliath",
            "238707229": "Torukä Na'rìng",
            "2292208788": "Swotulu",
            
            # Major Areas
            "355473279": "Blue Lagoon",
            "615754132": "Hell's Gate",
            "1172651822": "The Feba",
            "1847852653": "Grave's Bog",
            "2171723794": "The Hanging Gardens",
            "2587251285": "Needle Hills",
            "2752812145": "Echo Chasm",
            "2856892107": "Kxanìa Taw",
            "2961077726": "Lost Cathedral",
            "3616200713": "Tantalus (Ta'natasi)",
            "3822194552": "Hometree",
            "1057194188": "Va'erä Ramunong",
            "2943222331": "Iknimaya",
            "837458676": "Tantalus",
            
            # Special Areas
            "1504064473": "Sacred Grove",
            "1771880106": "Ancient Ruins",
            "470159002": "Battlefield Delta",
            "2216033045": "Combat Arena",
            "60855408": "War Zone Beta",
            "3975313082": "Wild Plains",
            "2169212369": "Dense Jungle",
            "1578821154": "Mountain Pass",
            "1782610090": "Hidden Valley",
            
            # Cave Systems
            "1628184437": "Crystal Caverns",
            "1865345760": "Echo Caves",
            "3564339531": "Underground Network",
            
            # Water Areas
            "4294730242": "River Delta",
            "1741938656": "Great Lake",
            "2555792139": "Waterfall Basin",
            
            # Ancient Sites
            "2353717556": "Ancient Temple",
            "2001468046": "Lost City",
            "3903502716": "Sacred Ruins",
            
            # Unique Biomes
            "3852438644": "Bioluminescent Forest",
            "2232107097": "Fungal Grove",
            "2185381138": "Living Mountain",
            
            # Na'vi Areas
            "2672591835": "Na'vi Village",
            "105239137": "Tree of Souls",
            "3575765971": "Hometree Village",
            
            # Border Regions
            "902032528": "Northern Border",
            "948986278": "Eastern Frontier",
            "1437051617": "Southern Boundary",
            
            # Mission Areas
            "2427499480": "Mission Zone Alpha",
            "2509501782": "Mission Zone Beta",
            "4220570174": "Mission Zone Gamma",
            
            # Resource Areas
            "408444403": "Unobtainium Mine",
            "1846881984": "Resource Valley",
            "4168272830": "Mining Complex"
        }

        crc_id = str(map_id)
        return map_names.get(crc_id, f"Region {map_id}")

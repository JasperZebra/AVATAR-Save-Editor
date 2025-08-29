import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
from typing import Dict, Optional
from ui_components import EnhancedTooltip
import logging
from custom_messagebox import MessageBoxManager, show_info, show_error, show_warning, ask_question, ask_ok_cancel, show_success


class CheckpointsManager:
    def __init__(self, parent: ttk.Frame, main_window=None):
        self.logger = logging.getLogger('CheckpointsManager')
        self.logger.debug("Initializing Modern CheckpointsManager")
        self.parent = parent
        self.main_window = main_window
        self.checkpoint_data = {}
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
        
        # Main content area (checkpoints list)
        self.create_main_content(content_frame)

    def create_header_section(self):
        """Create the header with title and search"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title and subtitle
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = ttk.Label(title_frame, text="📍 Checkpoint History", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="Track your journey through Pandora's checkpoints and waypoints", 
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
        
        # === JOURNEY OVERVIEW ===
        overview_frame = ttk.LabelFrame(sidebar_frame, text="🗺️ Journey Overview", padding=15)
        overview_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Large checkpoint count display
        self.journey_display = ttk.Frame(overview_frame)
        self.journey_display.pack(fill=tk.X, pady=(0, 10))
        
        self.checkpoint_count = ttk.Label(
            self.journey_display, 
            text="0", 
            font=('Segoe UI', 24, 'bold'),
            foreground='#2e7d32'
        )
        self.checkpoint_count.pack()
        
        ttk.Label(self.journey_display, text="Checkpoints Visited", font=('Segoe UI', 10)).pack()
        
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
        """Create the main content area with checkpoints list"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Checkpoints list header
        list_header = ttk.Frame(main_frame)
        list_header.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(list_header, text="📍 Visited Checkpoints", 
                 font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)
        
        # Info legend
        legend_frame = ttk.Frame(list_header)
        legend_frame.pack(side=tk.RIGHT)
        
        legend_items = [("🎯", "Tutorial"), ("🏞️", "Exploration"), ("🏭", "RDA Facility")]
        for icon, desc in legend_items:
            ttk.Label(legend_frame, text=f"{icon} {desc}", font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=5)
        
        # Enhanced checkpoints treeview
        tree_container = ttk.Frame(main_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure columns for better information display
        columns = ("category", "name", "location", "id", "details")
        self.checkpoints_tree = ttk.Treeview(tree_container, columns=columns, show="headings", 
                                            selectmode="extended", height=20)
        
        # Configure headers
        headers = {
            "category": ("🏷️", 80, "center"),
            "name": ("📍 Checkpoint Name", 250, "w"),
            "location": ("🗺️ Location", 200, "w"),
            "id": ("🆔 ID", 120, "center"),
            "details": ("ℹ️ Info", 100, "center")
        }
        
        for col, (text, width, anchor) in headers.items():
            self.checkpoints_tree.heading(col, text=text)
            self.checkpoints_tree.column(col, width=width, anchor=anchor, minwidth=50)
        
        # Enhanced color scheme
        self.setup_tree_styles()
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.checkpoints_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.checkpoints_tree.xview)
        self.checkpoints_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.checkpoints_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.checkpoints_tree.bind("<Double-1>", self._on_checkpoint_double_click)
        self.checkpoints_tree.bind("<Button-3>", self._show_checkpoint_context_menu)

    def setup_tree_styles(self):
        """Configure tree styling with modern color scheme"""
        self.checkpoints_tree.tag_configure('tutorial', 
                                           background='#e3f2fd', 
                                           foreground="#0077ff")
        self.checkpoints_tree.tag_configure('exploration', 
                                           background='#e8f5e8', 
                                           foreground="#00ff0d")
        self.checkpoints_tree.tag_configure('rda_facility', 
                                           background='#fff3e0', 
                                           foreground="#ff7300")
        self.checkpoints_tree.tag_configure('natural_area', 
                                           background='#f3e5f5', 
                                           foreground="#b300ff")
        self.checkpoints_tree.tag_configure('major_location', 
                                           background='#fff8e1', 
                                           foreground="#ff7700")

    def load_checkpoints_data(self, tree: ET.ElementTree) -> None:
        """Load checkpoint data with modern interface"""
        self.logger.debug("Loading checkpoint data with modern interface")
        try:
            # Clear existing data
            self.checkpoint_data = {}
            
            # Clear existing items in treeview
            for item in self.checkpoints_tree.get_children():
                self.checkpoints_tree.delete(item)

            # Find the visited checkpoints section
            visited_cp = tree.find(".//VisitedCheckpoints")
            if visited_cp is None:
                self.logger.warning("No VisitedCheckpoints element found in XML")
                return

            checkpoints = visited_cp.findall("./CheckPoint")
            self.logger.debug(f"Found {len(checkpoints)} checkpoints")
            
            for cp in checkpoints:
                try:
                    entity_id = cp.get("EntityID", "")
                    
                    # Get checkpoint information
                    cp_name, location = self._get_checkpoint_info_from_id(entity_id)
                    category = self._get_checkpoint_category(cp_name, location)
                    
                    # Store checkpoint data
                    self.checkpoint_data[entity_id] = {
                        'name': cp_name,
                        'location': location,
                        'category': category
                    }
                    
                    # Determine category icon and styling
                    category_icon, tag = self._get_checkpoint_display_info(category)
                    
                    # Insert into tree
                    self.checkpoints_tree.insert("", tk.END, values=(
                        category_icon,
                        cp_name,
                        location,
                        entity_id[-8:] if len(entity_id) > 8 else entity_id,  # Show last 8 digits
                        "View Details"
                    ), tags=(tag,))
                    
                    self.logger.debug(f"Successfully added checkpoint {entity_id} to tree")
                
                except Exception as e:
                    self.logger.error(f"Error processing individual checkpoint: {str(e)}", exc_info=True)

            # Update all displays
            self._update_all_displays()
            
            self.logger.debug("Checkpoint data loading completed with modern interface")
            
        except Exception as e:
            self.logger.error(f"Error loading checkpoint data: {str(e)}", exc_info=True)
            raise

    def _get_checkpoint_category(self, name, location):
        """Determine checkpoint category based on name and location"""
        name_lower = name.lower()
        location_lower = location.lower()
        
        if any(keyword in name_lower for keyword in ['tutorial', 'training', 'practice', 'hub']):
            return "Tutorial"
        elif any(keyword in name_lower or keyword in location_lower 
                 for keyword in ['rda', 'facility', 'base', 'outpost', 'gate']):
            return "RDA Facility"
        elif any(keyword in location_lower for keyword in ['plains', 'forest', 'lagoon', 'swamp']):
            return "Natural Area"
        elif any(keyword in name_lower for keyword in ['gate', 'plaza', 'zone', 'watchtower']):
            return "Major Location"
        else:
            return "Exploration"

    def _get_checkpoint_display_info(self, category):
        """Get display icon and tag for a checkpoint category"""
        category_mapping = {
            "Tutorial": ("🎯", "tutorial"),
            "Exploration": ("🏞️", "exploration"),
            "RDA Facility": ("🏭", "rda_facility"),
            "Natural Area": ("🌿", "natural_area"),
            "Major Location": ("🗺️", "major_location")
        }
        
        return category_mapping.get(category, ("📍", "exploration"))

    def _update_all_displays(self):
        """Update all display elements"""
        total_checkpoints = len(self.checkpoint_data)
        
        # Update main checkpoint count
        self.checkpoint_count.config(text=str(total_checkpoints))
        
        # Count by category and location
        category_counts = {}
        location_counts = {}
        
        for checkpoint_data in self.checkpoint_data.values():
            category = checkpoint_data['category']
            location = checkpoint_data['location']
            
            category_counts[category] = category_counts.get(category, 0) + 1
            location_counts[location] = location_counts.get(location, 0) + 1
        
    def _apply_filter(self, event=None):
        """Apply search and filter to the checkpoints list"""
        filter_value = self.filter_var.get()
        search_text = self.search_var.get().lower()
        
        # Clear and repopulate tree
        for item in self.checkpoints_tree.get_children():
            self.checkpoints_tree.delete(item)
        
        # Re-add filtered items
        for entity_id, checkpoint_data in self.checkpoint_data.items():
            if self._should_show_checkpoint(entity_id, checkpoint_data, filter_value, search_text):
                category = checkpoint_data['category']
                category_icon, tag = self._get_checkpoint_display_info(category)
                
                self.checkpoints_tree.insert("", tk.END, values=(
                    category_icon,
                    checkpoint_data['name'],
                    checkpoint_data['location'],
                    entity_id[-8:] if len(entity_id) > 8 else entity_id,
                    "View Details"
                ), tags=(tag,))

    def _should_show_checkpoint(self, entity_id, checkpoint_data, filter_value, search_text):
        """Determine if checkpoint should be shown based on filters"""
        name = checkpoint_data['name']
        location = checkpoint_data['location']
        category = checkpoint_data['category']
        
        # Apply filter
        if filter_value == "🎯 Tutorial Areas" and category != "Tutorial":
            return False
        elif filter_value == "🏞️ Exploration Areas" and category != "Exploration":
            return False
        elif filter_value == "🏭 RDA Facilities" and category != "RDA Facility":
            return False
        elif filter_value == "🌿 Natural Areas" and category != "Natural Area":
            return False
        elif filter_value == "🗺️ Major Locations" and category != "Major Location":
            return False
        
        # Apply search
        if search_text and search_text not in name.lower() and search_text not in location.lower() and search_text not in entity_id.lower():
            return False
        
        return True

    def _on_checkpoint_double_click(self, event):
        """Handle double-click on checkpoint in list"""
        item = self.checkpoints_tree.selection()[0] if self.checkpoints_tree.selection() else None
        if item:
            values = self.checkpoints_tree.item(item, "values")
            # Find the full entity ID
            checkpoint_name = values[1]
            for entity_id, data in self.checkpoint_data.items():
                if data['name'] == checkpoint_name:
                    self._show_checkpoint_details(entity_id)
                    break

    def _show_checkpoint_context_menu(self, event):
        """Show context menu for checkpoints"""
        if self.checkpoints_tree.selection():
            context_menu = tk.Menu(self.checkpoints_tree, tearoff=0)
            context_menu.add_command(label="📋 Copy Checkpoint ID", command=self._copy_checkpoint_id)
            context_menu.add_command(label="ℹ️ Show Details", command=self._show_selected_checkpoint_details)
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()

    def _copy_checkpoint_id(self):
        """Copy selected checkpoint ID to clipboard"""
        selected = self.checkpoints_tree.selection()
        if selected:
            values = self.checkpoints_tree.item(selected[0], "values")
            checkpoint_name = values[1]
            # Find the full entity ID
            for entity_id, data in self.checkpoint_data.items():
                if data['name'] == checkpoint_name:
                    self.parent.clipboard_clear()
                    self.parent.clipboard_append(entity_id)
                    show_info("Copied", f"📋 Checkpoint ID copied to clipboard:\n{entity_id}")
                    break

    def _show_selected_checkpoint_details(self):
        """Show details for selected checkpoint"""
        selected = self.checkpoints_tree.selection()
        if selected:
            values = self.checkpoints_tree.item(selected[0], "values")
            checkpoint_name = values[1]
            # Find the full entity ID
            for entity_id, data in self.checkpoint_data.items():
                if data['name'] == checkpoint_name:
                    self._show_checkpoint_details(entity_id)
                    break

    def _show_checkpoint_details(self, entity_id):
        """Show detailed information about a checkpoint"""
        if entity_id not in self.checkpoint_data:
            show_warning("Warning", "Checkpoint data not found")
            return
        
        checkpoint_data = self.checkpoint_data[entity_id]
        
        # Create detailed checkpoint information dialog
        detail_window = tk.Toplevel(self.parent)
        detail_window.title(f"Checkpoint Details - {checkpoint_data['name']}")
        detail_window.geometry("1600x800")
        detail_window.resizable(True, True)
        
        # Main frame with padding
        main_frame = ttk.Frame(detail_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        category_icon, _ = self._get_checkpoint_display_info(checkpoint_data['category'])
        title_label = ttk.Label(main_frame, text=f"{category_icon} {checkpoint_data['name']}", 
                               font=('Segoe UI', 14, 'bold'))
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Details frame
        details_frame = ttk.LabelFrame(main_frame, text="Checkpoint Information", padding=15)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create details text widget
        details_text = tk.Text(details_frame, wrap=tk.WORD, font=('Consolas', 10), 
                              height=18, state=tk.NORMAL)
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=details_text.yview)
        details_text.configure(yscrollcommand=scrollbar.set)
        
        # Format checkpoint details
        info_text = f"""📍 Checkpoint Name: {checkpoint_data['name']}
🗺️ Location: {checkpoint_data['location']}
🏷️ Category: {checkpoint_data['category']}
🆔 Entity ID: {entity_id}

📝 Description:
{'=' * 50}
{self._get_checkpoint_description(checkpoint_data['name'], checkpoint_data['category'])}

🎯 Purpose:
{'=' * 50}
{self._get_checkpoint_purpose(checkpoint_data['category'])}

🔧 Technical Details:
{'=' * 50}
Entity ID: {entity_id}
Category: {checkpoint_data['category']}
Location: {checkpoint_data['location']}
Visit Status: Visited
"""
        
        details_text.insert(tk.END, info_text)
        details_text.config(state=tk.DISABLED)
        
        details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="📋 Copy ID", 
                  command=lambda: self._copy_to_clipboard(entity_id)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="✅ Close", 
                  command=detail_window.destroy).pack(side=tk.RIGHT)

    def _get_checkpoint_description(self, name, category):
        """Get description for a checkpoint"""
        if category == "Tutorial":
            return f"This tutorial checkpoint '{name}' marks a key learning point in your journey. It represents progress through the game's instructional content."
        elif category == "RDA Facility":
            return f"'{name}' is an RDA facility checkpoint marking your visit to a human installation or operational area on Pandora."
        elif category == "Natural Area":
            return f"This checkpoint '{name}' marks your exploration of Pandora's natural environments and diverse ecosystems."
        elif category == "Major Location":
            return f"'{name}' represents a significant landmark or major location in your Pandoran adventure."
        else:
            return f"Checkpoint '{name}' marks a point of interest discovered during your exploration of Pandora."

    def _get_checkpoint_purpose(self, category):
        """Get purpose description for checkpoint category"""
        purposes = {
            "Tutorial": "Tutorial checkpoints track your progress through the game's learning systems and introductory content.",
            "RDA Facility": "RDA facility checkpoints mark visits to human installations, bases, and operational centers.",
            "Natural Area": "Natural area checkpoints record your exploration of Pandora's diverse ecosystems and environments.",
            "Major Location": "Major location checkpoints represent significant landmarks and important areas in the game world.",
            "Exploration": "Exploration checkpoints track your discovery of various points of interest throughout Pandora."
        }
        return purposes.get(category, "This checkpoint marks a point of progress in your Pandoran journey.")

    def _copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(text)
            show_info("Copied", f"📋 Copied to clipboard:\n{text}")
        except Exception as e:
            show_error("Error", f"Failed to copy: {str(e)}")

    def save_checkpoints_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        """Checkpoints are view-only, return unchanged tree"""
        self.logger.debug("Saving checkpoint changes")
        return tree

    def _get_checkpoint_info_from_id(self, entity_id: str) -> tuple:
        """Get a readable checkpoint name and location from the entity ID"""
        checkpoint_data = {
            # Blue Lagoon checkpoints
            "2060116264721850117": {
                "name": "Landing Zone",
                "map_id": "355473279",
            },
            "2061389907802198293": {
                "name": "Tutorial - Training Hub",
                "map_id": "355473279",
            },
            "2061388794472435963": {
                "name": "Tutorial - Practice Zone",
                "map_id": "355473279",
            },
            "2057296791262466370": {
                "name": "Main Hub - Central Plaza",
                "map_id": "355473279",
            },
            
            # Plains of Goliath checkpoints
            "2063890367165497967": {
                "name": "Goliath Plains - Northern Gate",
                "map_id": "3409126972",
            },
            "2063890404131996273": {
                "name": "Goliath Plains - Eastern Watchtower",
                "map_id": "3409126972",
            },
            "2063890442725884531": {
                "name": "Goliath Plains - Southern Pass",
                "map_id": "3409126972",
            },
            
            # Hell's Gate checkpoints
            "2062001234567890123": {
                "name": "Hell's Gate - Main Entrance",
                "map_id": "615754132",
            },
            "2062001234567890124": {
                "name": "Hell's Gate - Security Checkpoint",
                "map_id": "615754132",
            },
            
            # Forest area checkpoints
            "2064001234567890125": {
                "name": "Emerald Forest - Treetop Waypoint",
                "map_id": "1172651822",
            },
            "2064001234567890126": {
                "name": "Torchwood Forest - Ancient Grove",
                "map_id": "1847852653",
            }
        }
        
        # Get data from dictionary or use default value
        entity_id_str = str(entity_id)
        if entity_id_str in checkpoint_data:
            cp_info = checkpoint_data[entity_id_str]
            
            # Get map name from map ID
            map_id = cp_info.get("map_id", "")
            map_name = self._get_map_name(map_id)
            
            return (cp_info["name"], map_name)
        else:
            return (f"Checkpoint {entity_id[-8:]}", "Unknown Location")
    
    def _get_map_name(self, map_id: str) -> str:
        """Get map name based on ID"""
        map_names = {
            # Tutorial and Starting Areas
            "3409126972": "Plains of Goliath",
            "238707229": "Training Grounds",
            "2292208788": "RDA Training Facility",
            
            # Major Areas
            "355473279": "Blue Lagoon",
            "615754132": "Hell's Gate",
            "1172651822": "Emerald Forest",
            "1847852653": "Torchwood Forest",
            "2171723794": "Swamps of Silence",
            "2587251285": "Northern Shelf",
            "2961077726": "Willow Glade",
            "3616200713": "Tantalus",
            "2856892107": "Kxania Taw",
            "2752812145": "Echo Chasm",
            "3822194552": "Hometree",
            "1057194188": "Va'era Ramunong",
            "1172651822": "The Feba",
            "2943222331": "Iknimaya",
            "837458676": "Tantalus (Ta'natasi)"
        }
        
        return map_names.get(map_id, "Unknown Area")

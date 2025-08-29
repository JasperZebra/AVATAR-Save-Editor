import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Set
import logging
from custom_messagebox import MessageBoxManager, show_info, show_error, show_warning, ask_question, ask_ok_cancel, show_success

class VehicleManager:
    def __init__(self, parent: ttk.Frame, main_window):
        self.logger = logging.getLogger('VehicleManager')
        self.logger.debug("Initializing Modern VehicleManager")
        self.parent = parent
        self.main_window = main_window
        self.entered_vehicles = set()  # Store entered vehicle IDs
        self.first_travel_bark_played = False  # Track if first travel bark played
        self.vehicle_data = {}
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
        
        # Left sidebar (status and stats)
        self.create_sidebar(content_frame)
        
        # Main content area (vehicle list)
        self.create_main_content(content_frame)

    def create_header_section(self):
        """Create the header with title and search"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title and subtitle
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = ttk.Label(title_frame, text="🚁 Vehicle Knowledge", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="Track your vehicle experience and travel history", 
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
        """Create the left sidebar with status and statistics"""
        sidebar_frame = ttk.Frame(parent, width=300)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        sidebar_frame.pack_propagate(False)
        
        # === TRAVEL STATUS SECTION ===
        status_frame = ttk.LabelFrame(sidebar_frame, text="🎯 Travel Status", padding=15)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Travel tutorial status
        tutorial_frame = ttk.Frame(status_frame)
        tutorial_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(tutorial_frame, text="Tutorial Status:", font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W)
        
        self.first_travel_status = ttk.Label(
            tutorial_frame,
            text="First Travel Tutorial: Not Played",
            font=('Segoe UI', 9)
        )
        self.first_travel_status.pack(anchor=tk.W, pady=(2, 0))
        
        # === STATISTICS SECTION ===
        stats_frame = ttk.LabelFrame(sidebar_frame, text="📊 Statistics", padding=15)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create statistics with modern layout
        self.create_stat_item(stats_frame, "🚁", "Total Vehicles", "0", "total_vehicles_label")
        self.create_stat_item(stats_frame, "✅", "Entered", "0", "entered_vehicles_label")
        self.create_stat_item(stats_frame, "❌", "Not Entered", "0", "not_entered_vehicles_label")
        
        # Progress bar for completion
        progress_frame = ttk.Frame(stats_frame)
        progress_frame.pack(fill=tk.X, pady=(10, 5))
        
        ttk.Label(progress_frame, text="Experience Progress:", font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=200)
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        self.completion_label = ttk.Label(progress_frame, text="0%", font=('Segoe UI', 9))
        self.completion_label.pack(anchor=tk.W, pady=(2, 0))
        
        # === FILTER SECTION ===
        filter_frame = ttk.LabelFrame(sidebar_frame, text="🔍 Filters", padding=15)
        filter_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(filter_frame, text="Show:", font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                   values=["All Vehicles", "✅ Entered Only", "❌ Not Entered", 
                                          "🚁 RDA Air Vehicles", "🚗 RDA Ground Vehicles", "🚤 RDA Water Vehicles",
                                          "🐎 Na'vi Mounts", "🛶 RDA Water Vehicles"],
                                   state="readonly", font=('Segoe UI', 9))
        filter_combo.set("All Vehicles")
        filter_combo.pack(fill=tk.X)
        filter_combo.bind("<<ComboboxSelected>>", self._apply_filter)
        
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
        """Create the main content area with vehicle list"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Vehicle list header
        list_header = ttk.Frame(main_frame)
        list_header.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(list_header, text="🚁 Vehicle Experience", 
                 font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)
        
        # Status legend
        legend_frame = ttk.Frame(list_header)
        legend_frame.pack(side=tk.RIGHT)
        
        legend_items = [("✅", "Entered"), ("❌", "Not Entered")]
        for icon, desc in legend_items:
            ttk.Label(legend_frame, text=f"{icon} {desc}", font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=5)
        
        # Enhanced vehicle treeview
        tree_container = ttk.Frame(main_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure columns for better information display
        columns = ("status", "name", "type", "id", "details")
        self.vehicles_tree = ttk.Treeview(tree_container, columns=columns, show="headings", 
                                         selectmode="extended", height=20)
        
        # Configure headers
        headers = {
            "status": ("✅", 60, "center"),
            "name": ("🚁 Vehicle Name", 250, "w"),
            "type": ("🏷️ Type", 180, "w"),
            "id": ("🆔 ID", 120, "center"),
            "details": ("ℹ️ Info", 100, "center")
        }
        
        for col, (text, width, anchor) in headers.items():
            self.vehicles_tree.heading(col, text=text)
            self.vehicles_tree.column(col, width=width, anchor=anchor, minwidth=50)
        
        # Enhanced color scheme
        self.setup_tree_styles()
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.vehicles_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.vehicles_tree.xview)
        self.vehicles_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.vehicles_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.vehicles_tree.bind("<Double-1>", self._on_vehicle_double_click)
        self.vehicles_tree.bind("<Button-3>", self._show_vehicle_context_menu)

    def setup_tree_styles(self):
        """Configure tree styling with modern color scheme"""
        self.vehicles_tree.tag_configure('entered', 
                                        background='#e8f5e8', 
                                        foreground="#00ff0d")
        self.vehicles_tree.tag_configure('not_entered', 
                                        background='#ffebee', 
                                        foreground="#ff0000")
        self.vehicles_tree.tag_configure('rda_air', 
                                        background='#e3f2fd', 
                                        foreground="#0077ff")
        self.vehicles_tree.tag_configure('rda_ground', 
                                        background='#fff3e0', 
                                        foreground="#ff7300")
        self.vehicles_tree.tag_configure('navi_mount', 
                                        background='#f3e5f5', 
                                        foreground="#b300ff")

    def load_vehicles(self, tree: ET.ElementTree) -> None:
        """Load vehicle knowledge with modern interface"""
        self.logger.debug("Loading vehicle knowledge with modern interface")
        try:
            # Clear existing data
            self.entered_vehicles = set()
            self.first_travel_bark_played = False
            self.vehicle_data = {}
            
            # Clear existing items in treeview
            for item in self.vehicles_tree.get_children():
                self.vehicles_tree.delete(item)
            
            # Get BarkKnowledge element
            bark_element = tree.find(".//BarkKnowledge")
            if bark_element is not None:
                # Check first travel bark status
                first_travel = bark_element.get("FirstTravelBarkPlayed", "0")
                self.first_travel_bark_played = (first_travel == "1")
                
                # Find all entered vehicle elements
                vehicle_elements = bark_element.findall("EnteredVehicle")
                for vehicle in vehicle_elements:
                    vehicle_id = vehicle.get("crc_vehicleItem", "")
                    if vehicle_id:
                        self.entered_vehicles.add(vehicle_id)
            
            # Get all known vehicles
            all_vehicles = self._get_all_vehicle_ids()
            
            # Process each vehicle
            for vehicle_id, vehicle_info in all_vehicles.items():
                is_entered = vehicle_id in self.entered_vehicles
                
                # Store vehicle data
                self.vehicle_data[vehicle_id] = {
                    'name': vehicle_info["name"],
                    'type': vehicle_info["type"],
                    'entered': is_entered
                }
                
                # Determine status and styling
                status_icon, tag = self._get_vehicle_status_info(is_entered, vehicle_info["type"])
                
                # Insert into tree
                self.vehicles_tree.insert("", tk.END, values=(
                    status_icon,
                    vehicle_info["name"],
                    vehicle_info["type"],
                    vehicle_id[-8:] if len(vehicle_id) > 8 else vehicle_id,  # Show last 8 digits
                    "View Details"
                ), tags=(tag,))
            
            # Update all displays
            self._update_all_displays()
            
            self.logger.debug(f"Loaded {len(self.entered_vehicles)} entered vehicles out of {len(all_vehicles)} total")
            
        except Exception as e:
            self.logger.error(f"Error loading vehicle knowledge: {str(e)}", exc_info=True)
            raise

    def _get_vehicle_status_info(self, is_entered, vehicle_type):
        """Get status icon and tag for a vehicle"""
        if is_entered:
            status_icon = "✅"
            if "Air" in vehicle_type:
                tag = "rda_air"
            elif "Ground" in vehicle_type:
                tag = "rda_ground"
            elif "Na'vi Mount" in vehicle_type:
                tag = "navi_mount"
            else:
                tag = "entered"
        else:
            status_icon = "❌"
            tag = "not_entered"
        
        return status_icon, tag

    def _update_all_displays(self):
        """Update all display elements"""
        total_vehicles = len(self.vehicle_data)
        entered_count = len(self.entered_vehicles)
        not_entered_count = total_vehicles - entered_count
        
        # Update travel status
        status_text = "✅ Completed" if self.first_travel_bark_played else "❌ Not Played"
        self.first_travel_status.config(text=f"First Travel Tutorial: {status_text}")
        
        # Update statistics
        self.total_vehicles_label.config(text=str(total_vehicles))
        self.entered_vehicles_label.config(text=str(entered_count))
        self.not_entered_vehicles_label.config(text=str(not_entered_count))
        
        # Update progress
        completion_pct = (entered_count / total_vehicles * 100) if total_vehicles > 0 else 0
        self.progress_bar['value'] = completion_pct
        self.completion_label.config(text=f"{completion_pct:.1f}% Complete")
        
    def _apply_filter(self, event=None):
        """Apply search and filter to the vehicle list"""
        filter_value = self.filter_var.get()
        search_text = self.search_var.get().lower()
        
        # Clear and repopulate tree
        for item in self.vehicles_tree.get_children():
            self.vehicles_tree.delete(item)
        
        # Re-add filtered items
        for vehicle_id, vehicle_data in self.vehicle_data.items():
            if self._should_show_vehicle(vehicle_id, vehicle_data, filter_value, search_text):
                is_entered = vehicle_data['entered']
                vehicle_type = vehicle_data['type']
                status_icon, tag = self._get_vehicle_status_info(is_entered, vehicle_type)
                
                self.vehicles_tree.insert("", tk.END, values=(
                    status_icon,
                    vehicle_data['name'],
                    vehicle_type,
                    vehicle_id[-8:] if len(vehicle_id) > 8 else vehicle_id,
                    "View Details"
                ), tags=(tag,))

    def _should_show_vehicle(self, vehicle_id, vehicle_data, filter_value, search_text):
        """Determine if vehicle should be shown based on filters"""
        name = vehicle_data['name']
        vehicle_type = vehicle_data['type']
        is_entered = vehicle_data['entered']
        
        # Apply filter
        if filter_value == "✅ Entered Only" and not is_entered:
            return False
        elif filter_value == "❌ Not Entered" and is_entered:
            return False
        elif filter_value == "🚁 RDA Air Vehicles" and "RDA Air" not in vehicle_type:
            return False
        elif filter_value == "🚗 RDA Ground Vehicles" and "RDA Ground" not in vehicle_type:
            return False
        elif filter_value == "🚤 RDA Water Vehicles" and "RDA Water" not in vehicle_type:
            return False
        elif filter_value == "🐎 Na'vi Mounts" and "Na'vi Mount" not in vehicle_type:
            return False
        elif filter_value == "🛶 RDA Water Vehicles" and "RDA Water Vehicle" not in vehicle_type:
            return False
        
        # Apply search
        if search_text and search_text not in name.lower() and search_text not in vehicle_id.lower():
            return False
        
        return True

    def _on_vehicle_double_click(self, event):
        """Handle double-click on vehicle in list"""
        item = self.vehicles_tree.selection()[0] if self.vehicles_tree.selection() else None
        if item:
            values = self.vehicles_tree.item(item, "values")
            self._show_vehicle_details(values[1])  # vehicle name

    def _show_vehicle_context_menu(self, event):
        """Show context menu for vehicles"""
        if self.vehicles_tree.selection():
            context_menu = tk.Menu(self.vehicles_tree, tearoff=0)
            context_menu.add_command(label="📋 Copy Vehicle ID", command=self._copy_vehicle_id)
            context_menu.add_command(label="ℹ️ Show Details", command=self._show_selected_vehicle_details)
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()

    def _copy_vehicle_id(self):
        """Copy selected vehicle ID to clipboard"""
        selected = self.vehicles_tree.selection()
        if selected:
            values = self.vehicles_tree.item(selected[0], "values")
            # Find the full vehicle ID from our data
            vehicle_name = values[1]
            for vehicle_id, vehicle_data in self.vehicle_data.items():
                if vehicle_data['name'] == vehicle_name:
                    self.parent.clipboard_clear()
                    self.parent.clipboard_append(vehicle_id)
                    show_info("Copied", f"📋 Vehicle ID copied to clipboard:\n{vehicle_id}")
                    break

    def _show_vehicle_details(self, vehicle_name):
        """Show detailed information about a vehicle"""
        # Find the vehicle data
        vehicle_data = None
        vehicle_id = None
        for vid, data in self.vehicle_data.items():
            if data['name'] == vehicle_name:
                vehicle_data = data
                vehicle_id = vid
                break
        
        if not vehicle_data:
            show_warning("Warning", "Vehicle data not found")
            return
        
        # Create detailed vehicle information dialog
        detail_window = tk.Toplevel(self.parent)
        detail_window.title(f"Vehicle Details - {vehicle_name}")
        detail_window.geometry("1600x800")
        detail_window.resizable(True, True)
        
        # Main frame with padding
        main_frame = ttk.Frame(detail_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"🚁 {vehicle_name}", 
                            font=('Segoe UI', 14, 'bold'))
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Details frame
        details_frame = ttk.LabelFrame(main_frame, text="Vehicle Information", padding=15)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create details text widget
        details_text = tk.Text(details_frame, wrap=tk.WORD, font=('Consolas', 10), 
                            height=15, state=tk.NORMAL)
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=details_text.yview)
        details_text.configure(yscrollcommand=scrollbar.set)
        
        # Format vehicle details
        status_text = "✅ Entered" if vehicle_data['entered'] else "❌ Not Entered"
        
        info_text = f"""🚁 Vehicle Name: {vehicle_name}
    🏷️ Type: {vehicle_data['type']}
    🆔 Vehicle ID: {vehicle_id}
    ✅ Status: {status_text}

    📋 Description:
    {'=' * 30}
    {self._get_vehicle_description(vehicle_name, vehicle_data['type'])}

    🔧 Technical Details:
    {'=' * 30}
    Vehicle ID: {vehicle_id}
    Type Category: {vehicle_data['type']}
    Entered Status: {'Yes' if vehicle_data['entered'] else 'No'}
    """
        
        details_text.insert(tk.END, info_text)
        details_text.config(state=tk.DISABLED)
        
        details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="📋 Copy ID", 
                command=lambda: self._copy_to_clipboard(vehicle_id)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="✅ Close", 
                command=detail_window.destroy).pack(side=tk.RIGHT)

    def _copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(text)
            show_info("Copied", f"📋 Copied to clipboard:\n{text}")
        except Exception as e:
            show_error("Error", f"Failed to copy: {str(e)}")

    def _show_selected_vehicle_details(self):
        """Show details for selected vehicle"""
        selected = self.vehicles_tree.selection()
        if selected:
            values = self.vehicles_tree.item(selected[0], "values")
            self._show_vehicle_details(values[1])  # vehicle name

    def _get_vehicle_description(self, name, vehicle_type):
        """Get description for a vehicle"""
        descriptions = {
            "Gator": "Amphibious assault vehicle used by RDA forces for water and land operations.",
            "Swan": "Heavy ground transport vehicle with armored protection for personnel transport.",
            "Buggy": "Light reconnaissance vehicle used for quick scouting missions.",
            "Grinder": "Heavy assault vehicle with mining capabilities and heavy armor.",
            "Samson": "Multi-role utility aircraft used for transport and light combat operations.",
            "Scorpion": "Gunship aircraft designed for close air support and combat missions.",
            "Dragon Assault Ship": "Heavy assault aircraft with advanced weaponry and armor.",
            "Direhorse": "Six-legged Na'vi mount, fast and agile for ground travel.",
            "Mountain Banshee": "Flying Na'vi mount, essential for aerial travel and bonding rituals.",
            "Great Leonopteryx": "Legendary flying mount, rarely bonded with Na'vi warriors.",
            "Na'vi Boat": "Traditional Na'vi watercraft for river and lake navigation."
        }
        
        return descriptions.get(name, f"A {vehicle_type.lower()} used in Pandora operations.")

    def save_vehicle_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        """Vehicle knowledge is view-only, return unchanged tree"""
        self.logger.debug("Vehicle knowledge is view-only, no changes to save")
        return tree

    def _get_all_vehicle_ids(self):
        """Return a dictionary of all vehicle IDs with their names and types"""
        vehicle_info = {
            # RDA Ground Vehicles
            "2700952790": {
                "name": "Gator",
                "type": "RDA Water Vehicle"
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


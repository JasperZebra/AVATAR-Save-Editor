import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
from typing import Dict, Optional
from ui_components import EnhancedTooltip
from xml_handler import XMLHandler
import logging
from custom_messagebox import MessageBoxManager, show_info, show_error, show_warning, ask_question, ask_ok_cancel, show_success


class TerritoryManager:
    def __init__(self, parent: ttk.Frame, main_window=None):
        self.logger = logging.getLogger('TerritoryManager')
        self.logger.debug("Initializing Modern TerritoryManager")
        self.parent = parent
        self.main_window = main_window
        self.territory_data = {}
        self.territory_tree = None
        
        # Defense flags variables
        self.defense_flags_value = tk.IntVar(value=0)
        self.defense_flags_vars = {}
        self.defense_flags_bits = {}
        
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
        
        # Left sidebar (actions, editor, and stats)
        self.create_sidebar(content_frame)
        
        # Main content area (territory list)
        self.create_main_content(content_frame)

    def create_header_section(self):
        """Create the header with title"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title and subtitle
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = ttk.Label(title_frame, text="🏭 Territory Control", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="Manage territorial control, units, and defenses across Pandora", 
                                  font=('Segoe UI', 9), foreground='gray')
        subtitle_label.pack(anchor=tk.W)
        
    def create_sidebar(self, parent):
        """Create the left sidebar with actions, editor, and statistics"""
        sidebar_frame = ttk.Frame(parent, width=350)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        sidebar_frame.pack_propagate(False)
        
        # === QUICK ACTIONS SECTION ===
        actions_frame = ttk.LabelFrame(sidebar_frame, text="⚡ Quick Actions", padding=15)
        actions_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Hard Mode button
        self.hard_mode_button = ttk.Button(
            actions_frame, text="💀 Apply Hard Mode", 
            command=self._apply_hard_mode,
            style="Accent.TButton"
        )
        self.hard_mode_button.pack(fill=tk.X, pady=(0, 5))
        
        # Info label for hard mode
        info_label = ttk.Label(actions_frame, 
                              text="⚠️ Don't use if you haven't picked a faction yet!", 
                              font=('Segoe UI', 8), foreground='orange')
        info_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Separator
        ttk.Separator(actions_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Selection-based actions
        selection_label = ttk.Label(actions_frame, text="Selected Territory:", font=('Segoe UI', 9, 'bold'))
        selection_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.apply_changes_button = ttk.Button(
            actions_frame, text="✅ Apply Changes", 
            command=self._apply_territory_changes,
            state="disabled"
        )
        self.apply_changes_button.pack(fill=tk.X, pady=(0, 5))
        
        self.reset_editor_button = ttk.Button(
            actions_frame, text="🔄 Reset Editor", 
            command=self._reset_territory_editors,
            state="disabled"
        )
        self.reset_editor_button.pack(fill=tk.X)
                                
        # === TERRITORY EDITOR ===
        self.create_territory_editor(sidebar_frame)

    def create_territory_editor(self, parent):
        """Create the territory editor section"""
        editor_frame = ttk.LabelFrame(parent, text="✏️ Territory Editor", padding=15)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Territory editors dictionary
        self.territory_editors = {}
        
        # Basic Information Section
        basic_frame = ttk.LabelFrame(editor_frame, text="🏷️ Basic Information", padding=10)
        basic_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Faction selection
        faction_frame = ttk.Frame(basic_frame)
        faction_frame.pack(fill=tk.X, pady=2)
        ttk.Label(faction_frame, text="Faction:", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        faction_combo = ttk.Combobox(faction_frame, values=["Undecided", "Na'vi", "RDA"], 
                                    state="readonly", width=15)
        faction_combo.pack(side=tk.RIGHT)
        self.territory_editors["Faction"] = faction_combo
        
        # Base Units
        base_units_frame = ttk.Frame(basic_frame)
        base_units_frame.pack(fill=tk.X, pady=2)
        ttk.Label(base_units_frame, text="Base Units:", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        base_units_entry = ttk.Entry(base_units_frame, width=15)
        base_units_entry.pack(side=tk.RIGHT)
        self.territory_editors["BaseUnits"] = base_units_entry
        
        # Military Units Section
        military_frame = ttk.LabelFrame(editor_frame, text="⚔️ Military Units", padding=10)
        military_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Troops
        troops_frame = ttk.Frame(military_frame)
        troops_frame.pack(fill=tk.X, pady=2)
        ttk.Label(troops_frame, text="Troops:", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        troops_entry = ttk.Entry(troops_frame, width=15)
        troops_entry.pack(side=tk.RIGHT)
        self.territory_editors["Troops"] = troops_entry
        
        # Ground Units
        ground_frame = ttk.Frame(military_frame)
        ground_frame.pack(fill=tk.X, pady=2)
        ttk.Label(ground_frame, text="Ground Units:", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        ground_entry = ttk.Entry(ground_frame, width=15)
        ground_entry.pack(side=tk.RIGHT)
        self.territory_editors["Ground"] = ground_entry
        
        # Air Units
        air_frame = ttk.Frame(military_frame)
        air_frame.pack(fill=tk.X, pady=2)
        ttk.Label(air_frame, text="Air Units:", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        air_entry = ttk.Entry(air_frame, width=15)
        air_entry.pack(side=tk.RIGHT)
        self.territory_editors["Air"] = air_entry
        
        # Territory Properties Section
        properties_frame = ttk.LabelFrame(editor_frame, text="🏗️ Territory Properties", padding=10)
        properties_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Home Base
        home_base_frame = ttk.Frame(properties_frame)
        home_base_frame.pack(fill=tk.X, pady=2)
        ttk.Label(home_base_frame, text="Home Base:", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        home_base_combo = ttk.Combobox(home_base_frame, values=["No", "Yes"], 
                                      state="readonly", width=15)
        home_base_combo.pack(side=tk.RIGHT)
        self.territory_editors["HomeBase"] = home_base_combo
        
        # Factory
        factory_frame = ttk.Frame(properties_frame)
        factory_frame.pack(fill=tk.X, pady=2)
        ttk.Label(factory_frame, text="Factory:", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        factory_combo = ttk.Combobox(factory_frame, values=["No", "Yes"], 
                                    state="readonly", width=15)
        factory_combo.pack(side=tk.RIGHT)
        self.territory_editors["SecondaryBase"] = factory_combo
        
        # Active Status
        active_frame = ttk.Frame(properties_frame)
        active_frame.pack(fill=tk.X, pady=2)
        ttk.Label(active_frame, text="Taken Control:", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        active_combo = ttk.Combobox(active_frame, values=["No", "Yes"], 
                                   state="readonly", width=15)
        active_combo.pack(side=tk.RIGHT)
        self.territory_editors["Active"] = active_combo
        
        # Defense Flags Section
        defense_frame = ttk.LabelFrame(editor_frame, text="🛡️ Defense Systems", padding=10)
        defense_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Defense flag options with their bit values
        defense_flag_options = [
            ("vs Foot Troops", 1, "Defense against infantry"),
            ("vs Ground Units", 2, "Defense against vehicles"),
            ("vs Air Units", 4, "Defense against aircraft"),
        ]
        
        # Store the checkboxes and bit values
        self.defense_flags_vars = {}
        self.defense_flags_bits = {}
        
        # Create checkboxes for each defense flag option
        for flag_name, bit_value, tooltip in defense_flag_options:
            var = tk.IntVar(value=0)
            self.defense_flags_vars[flag_name] = var
            self.defense_flags_bits[flag_name] = bit_value
            
            checkbox_frame = ttk.Frame(defense_frame)
            checkbox_frame.pack(fill=tk.X, pady=1)
            
            checkbox = ttk.Checkbutton(
                checkbox_frame,
                text=flag_name,
                variable=var,
                command=self._update_defense_flags_value
            )
            checkbox.pack(side=tk.LEFT)
            
            # Add tooltip
            EnhancedTooltip(checkbox, tooltip)
        
        # Defense flags value display
        self.defense_flags_label = ttk.Label(defense_frame, text="Total Value: 0", 
                                           font=('Segoe UI', 9), foreground='gray')
        self.defense_flags_label.pack(pady=(5, 0))

    def create_main_content(self, parent):
        """Create the main content area with territory list"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Territory list header
        list_header = ttk.Frame(main_frame)
        list_header.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(list_header, text="🏭 Territory Status", 
                 font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)
        
        # Faction legend
        legend_frame = ttk.Frame(list_header)
        legend_frame.pack(side=tk.RIGHT)
        
        legend_items = [("🔵", "Na'vi"), ("🔴", "RDA"), ("⚪", "Neutral")]
        for icon, desc in legend_items:
            ttk.Label(legend_frame, text=f"{icon} {desc}", font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=5)
        
        # Enhanced territory treeview
        tree_container = ttk.Frame(main_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure columns for better information display
        columns = ("faction", "id", "base_units", "troops", "ground", "air", 
                  "home_base", "factory", "defense", "active")
        self.territory_tree = ttk.Treeview(tree_container, columns=columns, show="headings", 
                                         selectmode="browse", height=20)
        
        # Configure headers
        headers = {
            "faction": ("🏴", 60, "center"),
            "id": ("🆔 Territory ID", 120, "center"),
            "base_units": ("🏘️ Base", 80, "center"),
            "troops": ("👥 Troops", 80, "center"),
            "ground": ("🚗 Ground", 80, "center"),
            "air": ("✈️ Air", 80, "center"),
            "home_base": ("🏠 Home", 80, "center"),
            "factory": ("🏭 Factory", 80, "center"),
            "defense": ("🛡️ Defense", 80, "center"),
            "active": ("✅ Active", 80, "center")
        }
        
        for col, (text, width, anchor) in headers.items():
            self.territory_tree.heading(col, text=text)
            self.territory_tree.column(col, width=width, anchor=anchor, minwidth=50)
        
        # Enhanced color scheme
        self.setup_tree_styles()
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.territory_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.territory_tree.xview)
        self.territory_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.territory_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.territory_tree.bind("<<TreeviewSelect>>", self._on_territory_select)
        self.territory_tree.bind("<Button-3>", self._show_territory_context_menu)

    def setup_tree_styles(self):
        """Configure tree styling with modern color scheme"""
        self.territory_tree.tag_configure('navi', 
                                         background='#e3f2fd', 
                                         foreground="#0077ff")
        self.territory_tree.tag_configure('rda', 
                                         background='#ffebee', 
                                         foreground="#ff0000")
        self.territory_tree.tag_configure('neutral', 
                                         background='#f5f5f5', 
                                         foreground='#616161')
        self.territory_tree.tag_configure('home_base', 
                                         background='#e8f5e8', 
                                         foreground="#00ff0d")

    def load_territory_data(self, tree: ET.ElementTree) -> None:
        """Load territory data with modern interface - FIXED VERSION"""
        self.logger.debug("Loading territory data with modern interface")
        try:
            # Clear existing data
            self.territory_data = {}
            
            # Clear existing items in treeview
            for item in self.territory_tree.get_children():
                self.territory_tree.delete(item)

            territories = tree.findall(".//Territory")
            self.logger.debug(f"Found {len(territories)} territories")
            
            for territory in territories:
                try:
                    territory_id = territory.get("crc_ID", "")
                    faction = territory.get("Faction", "0")
                    
                    self.logger.debug(f"Processing territory ID: '{territory_id}' (type: {type(territory_id)})")
                    
                    # Get free units data
                    free_units = territory.find("FreeUnits")
                    troops = free_units.get("Troops", "0") if free_units is not None else "0"
                    ground = free_units.get("Ground", "0") if free_units is not None else "0"
                    air = free_units.get("Air", "0") if free_units is not None else "0"

                    # FIXED: Ensure consistent key format and handle empty/None territory_id
                    if not territory_id or territory_id.strip() == "":
                        self.logger.warning(f"Empty or None territory ID found, skipping territory")
                        continue
                    
                    # Store territory data with consistent string key
                    territory_key = str(territory_id).strip()
                    self.territory_data[territory_key] = {
                        'faction': faction,
                        'base_units': territory.get("BaseUnits", "0"),
                        'troops': troops,
                        'ground': ground,
                        'air': air,
                        'home_base': territory.get("HomeBase", "0"),
                        'factory': territory.get("SecondaryBase", "0"),
                        'defense_flags': territory.get("DefenseFlags", "1"),
                        'active': territory.get("Active", "0"),
                        'element': territory
                    }
                    
                    self.logger.debug(f"Stored territory data with key: '{territory_key}'")
                    
                    # Determine faction icon and tag
                    faction_icon, tag = self._get_faction_display_info(faction)
                    
                    # Insert into tree with the same key format
                    values = (
                        faction_icon,
                        territory_key,  # Use the same key format as stored data
                        territory.get("BaseUnits", "0"),
                        troops, ground, air,
                        "Yes" if territory.get("HomeBase", "0") == "2" else "No",
                        "Yes" if territory.get("SecondaryBase", "0") == "1" else "No",
                        territory.get("DefenseFlags", "1"),
                        "Yes" if territory.get("Active", "0") == "1" else "No"
                    )
                    
                    self.territory_tree.insert("", tk.END, values=values, tags=(tag,))
                    
                    self.logger.debug(f"Successfully added territory {territory_key} to tree")
                
                except Exception as e:
                    self.logger.error(f"Error processing individual territory: {str(e)}", exc_info=True)

            # Log summary of loaded data
            self.logger.debug(f"Loaded {len(self.territory_data)} territories total")
            self.logger.debug(f"Sample territory keys: {list(self.territory_data.keys())[:3]}...")
            
            # Reset editors after loading data
            self._reset_territory_editors()
            
            self.logger.debug("Territory data loading completed with modern interface")
            
        except Exception as e:
            self.logger.error(f"Error loading territory data: {str(e)}", exc_info=True)
            raise

    def _get_faction_display_info(self, faction):
        """Get display icon and tag for a faction"""
        faction_mapping = {
            "1": ("🔵", "navi"),
            "2": ("🔴", "rda"),
            "0": ("⚪", "neutral")
        }
        return faction_mapping.get(str(faction).strip(), ("⚪", "neutral"))

    def _refresh_territory_display(self):
        """Refresh the territory display after changes"""
        # Clear and repopulate tree
        for item in self.territory_tree.get_children():
            self.territory_tree.delete(item)
        
        # Re-add all items
        for territory_id, territory_data in self.territory_data.items():
            faction_icon, tag = self._get_faction_display_info(territory_data['faction'])
            
            values = (
                faction_icon,
                territory_id,
                territory_data['base_units'],
                territory_data['troops'],
                territory_data['ground'],
                territory_data['air'],
                "Yes" if territory_data['home_base'] == "2" else "No",
                "Yes" if territory_data['factory'] == "1" else "No",
                territory_data['defense_flags'],
                "Yes" if territory_data['active'] == "1" else "No"
            )
            
            self.territory_tree.insert("", tk.END, values=values, tags=(tag,))

    def _on_territory_select(self, event) -> None:
        """Handle territory selection - FIXED VERSION"""
        self.logger.debug("Territory selected")
        selection = self.territory_tree.selection()
        if not selection:
            self.logger.debug("No territory selected")
            self.apply_changes_button.config(state="disabled")
            self.reset_editor_button.config(state="disabled")
            return

        try:
            selected_item = selection[0]
            values = self.territory_tree.item(selected_item)["values"]
            territory_id = str(values[1])  # Ensure it's a string and ID is at index 1
            
            self.logger.debug(f"Selected territory ID: '{territory_id}' (type: {type(territory_id)})")
            self.logger.debug(f"Available territory keys: {list(self.territory_data.keys())[:5]}...")  # Show first 5 keys
            
            # FIXED: More robust territory lookup with multiple attempts
            territory_data = None
            
            # Attempt 1: Direct lookup
            if territory_id in self.territory_data:
                territory_data = self.territory_data[territory_id]
                self.logger.debug(f"Found territory data with direct lookup")
            else:
                # Attempt 2: Try different string representations
                for key in self.territory_data.keys():
                    if str(key).strip() == str(territory_id).strip():
                        territory_data = self.territory_data[key]
                        territory_id = key  # Use the actual key for consistency
                        self.logger.debug(f"Found territory data with string match: '{key}'")
                        break
                
                # Attempt 3: Try case-insensitive match
                if territory_data is None:
                    territory_id_lower = str(territory_id).lower().strip()
                    for key in self.territory_data.keys():
                        if str(key).lower().strip() == territory_id_lower:
                            territory_data = self.territory_data[key]
                            territory_id = key  # Use the actual key for consistency
                            self.logger.debug(f"Found territory data with case-insensitive match: '{key}'")
                            break
                
                # Attempt 4: If still not found, log all keys for debugging
                if territory_data is None:
                    self.logger.error(f"Territory '{territory_id}' not found in territory_data")
                    self.logger.debug("All available keys:")
                    for i, key in enumerate(self.territory_data.keys()):
                        self.logger.debug(f"  Key {i}: '{key}' (type: {type(key)}, len: {len(str(key))})")
                        if i > 10:  # Limit to first 10 keys to avoid spam
                            self.logger.debug(f"  ... and {len(self.territory_data) - 10} more keys")
                            break
                    
                    show_error("Error", f"Territory data not found for ID: {territory_id}")
                    return
            
            # Store the correct territory_id for later use
            self.current_territory_id = territory_id
            
            self.logger.debug(f"Found territory data: {territory_data}")
            
            # Enable buttons
            self.apply_changes_button.config(state="normal")
            self.reset_editor_button.config(state="normal")
            
            # Update editor fields - Basic Information
            faction = territory_data['faction']
            self.logger.debug(f"Setting faction to: {faction}")
            if faction == "0":
                self.territory_editors["Faction"].set("Undecided")
            elif faction == "1":
                self.territory_editors["Faction"].set("Na'vi")
            else:
                self.territory_editors["Faction"].set("RDA")
            
            # Update numeric fields
            self.logger.debug(f"Updating BaseUnits: {territory_data['base_units']}")
            self.territory_editors["BaseUnits"].delete(0, tk.END)
            self.territory_editors["BaseUnits"].insert(0, str(territory_data['base_units']))
            
            self.logger.debug(f"Updating Troops: {territory_data['troops']}")
            self.territory_editors["Troops"].delete(0, tk.END)
            self.territory_editors["Troops"].insert(0, str(territory_data['troops']))
            
            self.logger.debug(f"Updating Ground: {territory_data['ground']}")
            self.territory_editors["Ground"].delete(0, tk.END)
            self.territory_editors["Ground"].insert(0, str(territory_data['ground']))
            
            self.logger.debug(f"Updating Air: {territory_data['air']}")
            self.territory_editors["Air"].delete(0, tk.END)
            self.territory_editors["Air"].insert(0, str(territory_data['air']))
            
            # Set dropdowns - Territory Properties
            home_base_value = "Yes" if territory_data['home_base'] == "2" else "No"
            factory_value = "Yes" if territory_data['factory'] == "1" else "No" 
            active_value = "Yes" if territory_data['active'] == "1" else "No"
            
            self.logger.debug(f"Setting HomeBase: {home_base_value} (raw: {territory_data['home_base']})")
            self.logger.debug(f"Setting Factory: {factory_value} (raw: {territory_data['factory']})")
            self.logger.debug(f"Setting Active: {active_value} (raw: {territory_data['active']})")
            
            self.territory_editors["HomeBase"].set(home_base_value)
            self.territory_editors["SecondaryBase"].set(factory_value)
            self.territory_editors["Active"].set(active_value)
            
            # Update defense flags checkboxes
            try:
                defense_flags_value = int(str(territory_data['defense_flags']) or "0")
                self.logger.debug(f"Defense flags raw value: '{territory_data['defense_flags']}', parsed as: {defense_flags_value}")
                
                # Reset all checkboxes first
                for flag_name, var in self.defense_flags_vars.items():
                    var.set(0)
                    self.logger.debug(f"Reset {flag_name} checkbox to 0")
                
                # Set checkboxes based on bits in the value
                for flag_name, bit_value in self.defense_flags_bits.items():
                    if defense_flags_value & bit_value:  # Bitwise AND operation
                        self.defense_flags_vars[flag_name].set(1)
                        self.logger.debug(f"Set {flag_name} checkbox to 1 (bit value: {bit_value})")
                    else:
                        self.logger.debug(f"Left {flag_name} checkbox at 0 (bit value: {bit_value})")
                
                # Update the total value display
                self._update_defense_flags_value()
                
            except Exception as defense_error:
                self.logger.error(f"Error updating defense flags: {str(defense_error)}", exc_info=True)
                # Reset defense flags on error
                for var in self.defense_flags_vars.values():
                    var.set(0)
                self._update_defense_flags_value()
            
            self.logger.debug("Territory editor fields updated successfully")
            
        except Exception as e:
            self.logger.error(f"Error updating territory editor fields: {str(e)}", exc_info=True)
            show_error("Error", f"Failed to update territory editor: {str(e)}")

    def _show_territory_context_menu(self, event):
        """Show context menu for territories"""
        if self.territory_tree.selection():
            context_menu = tk.Menu(self.territory_tree, tearoff=0)
            context_menu.add_command(label="📋 Copy Territory ID", command=self._copy_territory_id)
            context_menu.add_command(label="ℹ️ Show Details", command=self._show_territory_details)
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()


    def _get_defense_breakdown(self, defense_flags):
        """Get human-readable defense breakdown"""
        try:
            flags_value = int(defense_flags or "0")
            breakdown = []
            
            if flags_value & 1:  # Bit 1 - Foot troops
                breakdown.append("• Defense vs Foot Troops")
            if flags_value & 2:  # Bit 2 - Ground units
                breakdown.append("• Defense vs Ground Units")
            if flags_value & 4:  # Bit 4 - Air units
                breakdown.append("• Defense vs Air Units")
            
            return "\n".join(breakdown) if breakdown else "• No active defenses"
        except:
            return "• Unknown defense configuration"

    def _update_defense_flags_value(self) -> None:
        """Calculate the total defense flags value from all checkboxes"""
        total = 0
        for flag_name, var in self.defense_flags_vars.items():
            if var.get() == 1:  # Checkbox is checked
                total += self.defense_flags_bits[flag_name]
        
        self.defense_flags_value.set(total)
        self.defense_flags_label.config(text=f"Total Value: {total}")
        self.logger.debug(f"Defense flags value updated to {total}")

    def _reset_territory_editors(self) -> None:
        """Reset all territory editor fields"""
        # Reset standard editors
        for key, editor in self.territory_editors.items():
            if isinstance(editor, ttk.Combobox):
                if key == "Faction":
                    editor.set("Undecided")
                else:
                    editor.set("No")
            else:
                editor.delete(0, tk.END)
                editor.insert(0, "0")
        
        # Reset defense flags checkboxes
        if hasattr(self, 'defense_flags_vars'):
            for var in self.defense_flags_vars.values():
                var.set(0)
            self._update_defense_flags_value()
        
        # Disable buttons
        self.apply_changes_button.config(state="disabled")
        self.reset_editor_button.config(state="disabled")

    def _copy_territory_id(self):
        """Copy selected territory ID to clipboard"""
        selected = self.territory_tree.selection()
        if selected:
            values = self.territory_tree.item(selected[0], "values")
            territory_id = values[1]  # ID is at index 1
            self.parent.clipboard_clear()
            self.parent.clipboard_append(territory_id)
            show_info("Copied", f"📋 Territory ID copied to clipboard:\n{territory_id}")

    def _show_territory_details(self):
        """Show detailed information about selected territory"""
        selected = self.territory_tree.selection()
        if not selected:
            return
            
        values = self.territory_tree.item(selected[0], "values")
        territory_id = values[1]  # ID is at index 1
        
        if territory_id not in self.territory_data:
            show_warning("Warning", "Territory data not found")
            return
        
        territory_data = self.territory_data[territory_id]
        
        # Create detailed territory information dialog
        detail_window = tk.Toplevel(self.parent)
        detail_window.title(f"Territory Details - {territory_id}")
        detail_window.geometry("1600x800")
        detail_window.resizable(True, True)
        
        # Main frame with padding
        main_frame = ttk.Frame(detail_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        faction_icon, _ = self._get_faction_display_info(territory_data['faction'])
        title_label = ttk.Label(main_frame, text=f"{faction_icon} Territory {territory_id}", 
                            font=('Segoe UI', 14, 'bold'))
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Details frame
        details_frame = ttk.LabelFrame(main_frame, text="Territory Information", padding=15)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create details text widget
        details_text = tk.Text(details_frame, wrap=tk.WORD, font=('Consolas', 10), 
                            height=18, state=tk.NORMAL)
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=details_text.yview)
        details_text.configure(yscrollcommand=scrollbar.set)
        
        # Get faction name
        faction_names = {"0": "Neutral", "1": "Na'vi", "2": "RDA"}
        faction_name = faction_names.get(territory_data['faction'], "Unknown")
        
        # Format territory details
        info_text = f"""🏭 Territory ID: {territory_id}
    🏴 Faction Control: {faction_name}
    🏘️ Base Units: {territory_data['base_units']}

    ⚔️ Military Forces:
    {'=' * 30}
    👥 Troops: {territory_data['troops']}
    🚗 Ground Units: {territory_data['ground']}
    ✈️ Air Units: {territory_data['air']}

    🏗️ Infrastructure:
    {'=' * 30}
    🏠 Home Base: {'Yes' if territory_data['home_base'] == '2' else 'No'}
    🏭 Factory: {'Yes' if territory_data['factory'] == '1' else 'No'}
    ✅ Taken Control: {'Yes' if territory_data['active'] == '1' else 'No'}

    🛡️ Defense Systems:
    {'=' * 30}
    Defense Flags Value: {territory_data['defense_flags']}
    Defense Types Active:
    {self._get_defense_breakdown(territory_data['defense_flags'])}

    🔧 Technical Details:
    {'=' * 30}
    Territory ID: {territory_id}
    Faction Code: {territory_data['faction']}
    HomeBase Value: {territory_data['home_base']}
    SecondaryBase Value: {territory_data['factory']}
    DefenseFlags Value: {territory_data['defense_flags']}
    Active Status: {territory_data['active']}
    """
        
        details_text.insert(tk.END, info_text)
        details_text.config(state=tk.DISABLED)
        
        details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="📋 Copy ID", 
                command=lambda: self._copy_to_clipboard(territory_id)).pack(side=tk.LEFT, padx=(0, 10))
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

    def _apply_territory_changes(self) -> None:
        """Apply changes to selected territory - FIXED VERSION"""
        self.logger.debug("Applying territory changes")
        selection = self.territory_tree.selection()
        if not selection:
            self.logger.warning("No territory selected for changes")
            show_warning("Warning", "Please select a territory to edit.")
            return

        try:
            # FIXED: Use the stored territory_id from selection instead of parsing again
            if hasattr(self, 'current_territory_id') and self.current_territory_id:
                territory_id = self.current_territory_id
                self.logger.debug(f"Using stored territory ID: {territory_id}")
            else:
                # Fallback to parsing from tree if current_territory_id not available
                selected_item = selection[0]
                values = self.territory_tree.item(selected_item)["values"]
                territory_id = str(values[1])  # ID is at index 1
                self.logger.debug(f"Parsed territory ID from tree: {territory_id}")
                
                # Try to find the correct key
                if territory_id not in self.territory_data:
                    for key in self.territory_data.keys():
                        if str(key).strip() == str(territory_id).strip():
                            territory_id = key
                            break
                    else:
                        self.logger.error(f"Territory ID '{territory_id}' not found in territory_data")
                        show_error("Error", f"Territory data not found for ID: {territory_id}")
                        return
            
            self.logger.debug(f"Applying changes to territory {territory_id}")

            # Verify territory exists
            if territory_id not in self.territory_data:
                self.logger.error(f"Territory '{territory_id}' not found in territory_data")
                show_error("Error", f"Territory data not found for ID: {territory_id}")
                return

            # Get the current defense flags value from the IntVar
            defense_flags_total = self.defense_flags_value.get()
            self.logger.debug(f"Defense flags value: {defense_flags_total}")

            # Map faction selection to code
            faction_map = {"Undecided": "0", "Na'vi": "1", "RDA": "2"}
            faction_code = faction_map.get(self.territory_editors["Faction"].get(), "0")

            # Update territory data
            territory_data = self.territory_data[territory_id]
            territory_data['faction'] = faction_code
            territory_data['base_units'] = self.territory_editors["BaseUnits"].get()
            territory_data['troops'] = self.territory_editors["Troops"].get()
            territory_data['ground'] = self.territory_editors["Ground"].get()
            territory_data['air'] = self.territory_editors["Air"].get()
            territory_data['home_base'] = "2" if self.territory_editors["HomeBase"].get() == "Yes" else "0"
            territory_data['factory'] = "1" if self.territory_editors["SecondaryBase"].get() == "Yes" else "0"
            territory_data['defense_flags'] = str(defense_flags_total)
            territory_data['active'] = "1" if self.territory_editors["Active"].get() == "Yes" else "0"

            # Update tree display
            selected_item = selection[0]
            faction_icon, tag = self._get_faction_display_info(faction_code)
            new_values = (
                faction_icon,
                territory_id,
                territory_data['base_units'],
                territory_data['troops'],
                territory_data['ground'],
                territory_data['air'],
                "Yes" if territory_data['home_base'] == "2" else "No",
                "Yes" if territory_data['factory'] == "1" else "No",
                territory_data['defense_flags'],
                "Yes" if territory_data['active'] == "1" else "No"
            )
            
            self.territory_tree.item(selected_item, values=new_values, tags=(tag,))

            # Update the XML tree if available
            if self.main_window and self.main_window.tree:
                territory_element = territory_data['element']
                
                # Update territory attributes
                territory_element.set("Faction", faction_code)
                territory_element.set("BaseUnits", territory_data['base_units'])
                territory_element.set("HomeBase", territory_data['home_base'])
                territory_element.set("SecondaryBase", territory_data['factory'])
                territory_element.set("DefenseFlags", territory_data['defense_flags'])
                territory_element.set("Active", territory_data['active'])

                # Update or create FreeUnits element
                free_units = territory_element.find("FreeUnits")
                if free_units is None:
                    free_units = ET.SubElement(territory_element, "FreeUnits")
                
                free_units.set("Troops", territory_data['troops'])
                free_units.set("Ground", territory_data['ground'])
                free_units.set("Air", territory_data['air'])

                self.logger.debug("Updated XML tree with territory changes")

                # Mark as having unsaved changes
                self.main_window.unsaved_label.config(text="Unsaved Changes")

            self.logger.debug("Territory changes applied successfully")
            show_success("Success", "✅ Territory updated successfully!")
            
        except Exception as e:
            self.logger.error(f"Error applying territory changes: {str(e)}", exc_info=True)
            show_error("Error", f"❌ Failed to apply changes: {str(e)}")

    def _apply_hard_mode(self) -> None:
        """Apply Hard Mode by adding units to opposing faction territories"""
        self.logger.debug("Applying Hard Mode")
        
        # Confirm action with user
        response = ask_question(
            "Hard Mode Confirmation",
            "⚠️ WARNING: Don't use if you haven't picked a faction yet!\n\n"
            "💀 Hard Mode will add additional units to the opposing faction territories. Continue?"
        )
        
        if not response:
            return
        
        try:
            # Get the player's faction from the main window
            player_faction = None
            
            if self.main_window and self.main_window.tree:
                # First look for PlayerFaction directly in the Metagame element at root level
                root = self.main_window.tree.getroot()
                self.logger.debug(f"XML root tag: {root.tag}")
                
                # Look for Metagame element at root level
                metagame = self.main_window.tree.find(".//Metagame")
                if metagame is not None:
                    self.logger.debug("Found Metagame element")
                    self.logger.debug(f"Metagame attributes: {metagame.attrib}")
                    
                    # Check for PlayerFaction attribute
                    if "PlayerFaction" in metagame.attrib:
                        player_faction = metagame.get("PlayerFaction")
                        self.logger.debug(f"Found PlayerFaction in root Metagame: {player_faction}")
                else:
                    self.logger.warning("Metagame element not found in XML tree")
            
            # If player_faction is still None, try to determine it from territory ownership
            if player_faction is None:
                self.logger.debug("PlayerFaction not found in XML, trying to determine from territory ownership...")
                faction_1_count = 0
                faction_2_count = 0
                
                for territory_data in self.territory_data.values():
                    faction = territory_data['faction']
                    if faction == "1":
                        faction_1_count += 1
                    elif faction == "2":
                        faction_2_count += 1
                
                self.logger.debug(f"Territory count - Faction 1: {faction_1_count}, Faction 2: {faction_2_count}")
                
                # Assume player faction is the one with more territories
                if faction_1_count > faction_2_count:
                    player_faction = "1"
                    self.logger.debug("Determined player faction as 1 based on territory count")
                elif faction_2_count > faction_1_count:
                    player_faction = "2"
                    self.logger.debug("Determined player faction as 2 based on territory count")
            
            # Check if player faction is valid
            if not player_faction or player_faction not in ["1", "2"]:
                error_msg = "Cannot determine player faction. Please make sure you've chosen a faction in the game first."
                self.logger.error(error_msg)
                show_error("Error", error_msg)
                return
                
            # Define opponent faction 
            opponent_faction = "2" if player_faction == "1" else "1"
            self.logger.debug(f"Final determination - Player faction: {player_faction}, Opponent faction: {opponent_faction}")
            
            # Define unit boost amounts
            troop_boost = 3000
            ground_boost = 20
            air_boost = 10
            
            # Define defense flags - 7 means all defense flags are enabled (1+2+4)
            defense_flags_value = 7  # Enable all defense types
            
            # Factory setting (1 = Yes, 0 = No)
            factory_value = "1"  # Set to "Yes"
            
            # Apply boosts to all territories of the opposing faction
            territories_modified = 0
            
            for territory_id, territory_data in self.territory_data.items():
                territory_faction = territory_data['faction']
                
                # Debug each territory being examined
                self.logger.debug(f"Checking territory ID: {territory_id}, Faction: {territory_faction}")
                
                # Only modify territories of the OPPOSING faction
                if territory_faction == opponent_faction:
                    # Get current values and add boosts
                    current_troops = int(territory_data['troops'] or 0)
                    current_ground = int(territory_data['ground'] or 0)
                    current_air = int(territory_data['air'] or 0)
                    
                    new_troops = current_troops + troop_boost
                    new_ground = current_ground + ground_boost
                    new_air = current_air + air_boost
                    
                    self.logger.debug(f"Modifying territory {territory_id} - Adding Troops: {troop_boost}, Ground: {ground_boost}, Air: {air_boost}")
                    self.logger.debug(f"Setting defense flags to {defense_flags_value} and factory to {factory_value}")
                    
                    # Update territory data
                    territory_data['troops'] = str(new_troops)
                    territory_data['ground'] = str(new_ground)
                    territory_data['air'] = str(new_air)
                    territory_data['factory'] = factory_value
                    territory_data['defense_flags'] = str(defense_flags_value)
                    
                    # Update XML element
                    territory_element = territory_data['element']
                    territory_element.set("SecondaryBase", factory_value)
                    territory_element.set("DefenseFlags", str(defense_flags_value))
                    
                    # Update or create FreeUnits element
                    free_units = territory_element.find("FreeUnits")
                    if free_units is None:
                        free_units = ET.SubElement(territory_element, "FreeUnits")
                    
                    free_units.set("Troops", str(new_troops))
                    free_units.set("Ground", str(new_ground))
                    free_units.set("Air", str(new_air))
                    
                    territories_modified += 1
                    self.logger.debug(f"Updated territory {territory_id} for Hard Mode")
            
            if territories_modified == 0:
                self.logger.warning(f"No territories found with faction {opponent_faction} to modify")
                show_info("Hard Mode", "No enemy territories found to modify. Make sure territories are assigned to factions.")
                return
            
            # Refresh the display
            self._refresh_territory_display()
            
            # Mark as having unsaved changes
            if self.main_window:
                self.main_window.unsaved_label.config(text="Unsaved Changes")
            
            faction_names = {"1": "Na'vi", "2": "RDA"}
            opponent_name = faction_names.get(opponent_faction, f"Faction {opponent_faction}")
            
            self.logger.debug(f"Hard Mode applied to {territories_modified} territories of the opposing faction ({opponent_faction}).")
            show_info("Hard Mode Applied", 
                            f"💀 Hard Mode applied to {territories_modified} {opponent_name} territories!\n\n"
                            f"Added per territory:\n"
                            f"👥 Troops: +{troop_boost:,}\n"
                            f"🚗 Ground Units: +{ground_boost}\n"
                            f"✈️ Air Units: +{air_boost}\n"
                            f"🛡️ All defense flags enabled\n"
                            f"🏭 Factory enabled")
        
        except Exception as e:
            self.logger.error(f"Error applying Hard Mode: {str(e)}", exc_info=True)
            show_error("Error", f"❌ Failed to apply Hard Mode: {str(e)}")

    def save_territory_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        """Save territory changes to XML tree"""
        self.logger.debug("Saving territory changes")
        try:
            # Changes are already applied to the XML elements during updates
            # No additional processing needed since we update the elements directly
            self.logger.debug("Territory changes saved successfully")
            return tree
            
        except Exception as e:
            self.logger.error(f"Error saving territory changes: {str(e)}", exc_info=True)
            raise
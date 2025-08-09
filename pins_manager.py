import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
from typing import Dict, Optional
import logging
from custom_messagebox import MessageBoxManager, show_info, show_error, show_warning, ask_question, ask_ok_cancel, show_success


class PinsManager:
    def __init__(self, parent: ttk.Frame, main_window):
        self.logger = logging.getLogger('PinsManager')
        self.logger.debug("Initializing Modern PinsManager")
        self.parent = parent
        self.main_window = main_window
        self.pins_data = {}
        self.filter_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.setup_modern_ui()

    def setup_modern_ui(self) -> None:
        # Create main container with padding
        self.main_container = ttk.Frame(self.parent)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # === HEADER SECTION ===
        self.create_header_section()
        
        # === CONTENT AREA (Split into left sidebar and main view) ===
        content_frame = ttk.Frame(self.main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        # Left sidebar (controls and stats)
        self.create_sidebar(content_frame)
        
        # Main content area (pins list)
        self.create_main_content(content_frame)

    def create_header_section(self):
        """Create the header with title and search"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title and subtitle
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = ttk.Label(title_frame, text="📍 Map Pins Manager", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="Manage your discovered locations and pins", 
                                  font=('Segoe UI', 9), foreground='gray')
        subtitle_label.pack(anchor=tk.W)
        
        # Search section (moved to header for prominence)
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side=tk.RIGHT)
        
        ttk.Label(search_frame, text="🔍 Search:", font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25, font=('Segoe UI', 9))
        search_entry.pack(side=tk.LEFT)
        search_entry.bind("<KeyRelease>", self._apply_filter)

    def create_sidebar(self, parent):
        """Create the left sidebar with controls and statistics"""
        sidebar_frame = ttk.Frame(parent, width=280)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        sidebar_frame.pack_propagate(False)  # Maintain fixed width
        
        # === QUICK ACTIONS SECTION ===
        actions_frame = ttk.LabelFrame(sidebar_frame, text="⚡ Quick Actions", padding=15)
        actions_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Primary action buttons (larger, more prominent)
        self.unlock_all_button = ttk.Button(
            actions_frame, text="🔓 Unlock All Pins", 
            command=self.unlock_all_pins,
            style="Accent.TButton"
        )
        self.unlock_all_button.pack(fill=tk.X, pady=(0, 8))
        
        self.reset_all_button = ttk.Button(
            actions_frame, text="🔒 Lock All Pins", 
            command=self.reset_all_pins
        )
        self.reset_all_button.pack(fill=tk.X, pady=(0, 8))
        
        # Separator
        ttk.Separator(actions_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Selection-based actions
        selection_label = ttk.Label(actions_frame, text="Selected Pins:", font=('Segoe UI', 9, 'bold'))
        selection_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.unlock_selected_button = ttk.Button(
            actions_frame, text="🔓 Unlock Selected", 
            command=self.unlock_selected_pins, 
            state="disabled"
        )
        self.unlock_selected_button.pack(fill=tk.X, pady=(0, 5))
        
        self.lock_selected_button = ttk.Button(
            actions_frame, text="🔒 Lock Selected", 
            command=self.lock_selected_pins, 
            state="disabled"
        )
        self.lock_selected_button.pack(fill=tk.X)
        
        # === STATISTICS SECTION ===
        stats_frame = ttk.LabelFrame(sidebar_frame, text="📊 Statistics", padding=15)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create statistics with better visual hierarchy
        self.create_stat_item(stats_frame, "📍", "Total Pins", "0", "total_pins_label")
        self.create_stat_item(stats_frame, "🔓", "Unlocked", "0", "unlocked_pins_label")
        self.create_stat_item(stats_frame, "🔒", "Locked", "0", "locked_pins_label")
        
        # Progress bar for completion
        progress_frame = ttk.Frame(stats_frame)
        progress_frame.pack(fill=tk.X, pady=(10, 5))
        
        ttk.Label(progress_frame, text="Completion Progress:", font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=200)
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        self.completion_label = ttk.Label(progress_frame, text="0%", font=('Segoe UI', 9))
        self.completion_label.pack(anchor=tk.W, pady=(2, 0))
        
        # === FILTER SECTION ===
        filter_frame = ttk.LabelFrame(sidebar_frame, text="🔍 Filters", padding=15)
        filter_frame.pack(fill=tk.X)
        
        ttk.Label(filter_frame, text="Show:", font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                   values=["All Pins", "🔓 Unlocked", "🔒 Locked", "🎮 Single Player", "👥 Multiplayer", "❓ Unreleased"],
                                   state="readonly", font=('Segoe UI', 9))
        filter_combo.set("All Pins")
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
        """Create the main content area with the pins list"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Pins list header
        list_header = ttk.Frame(main_frame)
        list_header.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(list_header, text="🗺️ Discovered Locations", 
                 font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)
        
        # Status legend
        legend_frame = ttk.Frame(list_header)
        legend_frame.pack(side=tk.RIGHT)
        
        legend_items = [("🔒", "Locked"), ("🔓", "Unlocked"), ("⭐", "Special")]
        for icon, desc in legend_items:
            ttk.Label(legend_frame, text=f"{icon} {desc}", font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=5)
        
        # Enhanced pins tree with modern styling
        tree_container = ttk.Frame(main_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        # Configure columns for better information display
        columns = ("status", "location", "type", "progress", "details")
        self.pins_tree = ttk.Treeview(tree_container, columns=columns, show="headings", 
                                     selectmode="extended", height=20)
        
        # Configure headers with better names and styling
        headers = {
            "status": ("🔒", 60, "center"),
            "location": ("📍 Location", 300, "w"),
            "type": ("🎮", 100, "center"),
            "progress": ("📊 Progress", 100, "center"),
            "details": ("ℹ️ Details", 120, "center")
        }
        
        for col, (text, width, anchor) in headers.items():
            self.pins_tree.heading(col, text=text)
            self.pins_tree.column(col, width=width, anchor=anchor, minwidth=50)
        
        # Enhanced color scheme
        self.setup_tree_styles()
        
        # Scrollbars with modern styling
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.pins_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.pins_tree.xview)
        self.pins_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for tree and scrollbars
        self.pins_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.pins_tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.pins_tree.bind("<Double-1>", self._on_double_click)
        
        # Context menu for right-click actions
        self.create_context_menu()

    def setup_tree_styles(self):
        """Configure tree styling with modern color scheme"""
        # Create a more sophisticated color scheme
        self.pins_tree.tag_configure('locked', 
                                    background='#ffebee', 
                                    foreground="#ff0000")
        self.pins_tree.tag_configure('unlocked_sp', 
                                    background='#e8f5e8', 
                                    foreground="#00ff0d")
        self.pins_tree.tag_configure('unlocked_mp', 
                                    background='#e3f2fd', 
                                    foreground="#0077ff")
        self.pins_tree.tag_configure('special', 
                                    background='#fff3e0', 
                                    foreground="#ff7300")
        self.pins_tree.tag_configure('Unreleased', 
                                    background='#f5f5f5', 
                                    foreground='#757575')

    def create_context_menu(self):
        """Create context menu for right-click actions"""
        self.context_menu = tk.Menu(self.pins_tree, tearoff=0)
        self.context_menu.add_command(label="🔓 Unlock", command=self.unlock_selected_pins)
        self.context_menu.add_command(label="🔒 Lock", command=self.lock_selected_pins)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋 Copy ID", command=self.copy_selected_id)
        self.context_menu.add_command(label="ℹ️ Show Details", command=self.show_pin_details)
        
        self.pins_tree.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event):
        """Show context menu on right-click"""
        if self.pins_tree.selection():
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

    def lock_selected_pins(self):
        """Lock selected pins in the treeview"""
        self.logger.debug("Locking selected pins")
        try:
            selected_items = self.pins_tree.selection()
            if not selected_items:
                show_info("Info", "No pins selected")
                return
                
            changes_made = False
            
            for item in selected_items:
                values = self.pins_tree.item(item, 'values')
                # Extract pin ID from details column or find it in pins_data
                pin_id = self._extract_pin_id_from_item(item)
                
                if pin_id and pin_id in self.pins_data:
                    pin_info = self.pins_data[pin_id]
                    current_status = pin_info['unlocked']
                    
                    if current_status != "0":
                        pin_info['element'].set("eUnlocked", "0")
                        pin_info['unlocked'] = "0"
                        changes_made = True
            
            if changes_made:
                self.main_window.unsaved_label.config(text="Unsaved Changes")
                self._update_all_displays()
                show_success("Success", "🔒 Selected pins have been locked!")
            else:
                show_info("Info", "ℹ️ Selected pins are already locked")
                
        except Exception as e:
            self.logger.error(f"Error locking selected pins: {str(e)}", exc_info=True)
            show_error("Error", f"❌ Failed to lock selected pins: {str(e)}")

    def copy_selected_id(self):
        """Copy selected pin ID to clipboard"""
        selected = self.pins_tree.selection()
        if not selected:
            show_info("Info", "No pin selected")
            return
            
        try:
            pin_id = self._extract_pin_id_from_item(selected[0])
            if pin_id:
                self.parent.clipboard_clear()
                self.parent.clipboard_append(pin_id)
                show_info("Copied", f"📋 Pin ID copied to clipboard:\n{pin_id}")
            else:
                show_warning("Warning", "Could not extract pin ID")
        except Exception as e:
            show_error("Error", f"Failed to copy ID: {str(e)}")

    def show_pin_details(self):
        """Show detailed information about selected pin"""
        selected = self.pins_tree.selection()
        if not selected:
            show_info("Info", "No pin selected")
            return
            
        try:
            pin_id = self._extract_pin_id_from_item(selected[0])
            if not pin_id or pin_id not in self.pins_data:
                show_warning("Warning", "Pin data not found")
                return
                
            pin_info = self.pins_data[pin_id]
            location_name = self._get_location_name(pin_id)
            
            # Create detailed info dialog
            detail_window = tk.Toplevel(self.parent)
            detail_window.title(f"Pin Details - {location_name}")
            detail_window.geometry("1600x800")
            detail_window.resizable(True, True)
            
            # Main frame with padding
            main_frame = ttk.Frame(detail_window, padding=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text=f"📍 {location_name}", 
                                   font=('Segoe UI', 14, 'bold'))
            title_label.pack(anchor=tk.W, pady=(0, 15))
            
            # Details frame
            details_frame = ttk.LabelFrame(main_frame, text="Pin Information", padding=15)
            details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
            
            # Create details text widget
            details_text = tk.Text(details_frame, wrap=tk.WORD, font=('Consolas', 10), 
                                  height=15, state=tk.NORMAL)
            scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=details_text.yview)
            details_text.configure(yscrollcommand=scrollbar.set)
            
            # Add detailed information
            info_text = self._format_pin_details(pin_id, pin_info, location_name)
            details_text.insert(tk.END, info_text)
            details_text.config(state=tk.DISABLED)
            
            details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Button frame
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X)
            
            ttk.Button(button_frame, text="📋 Copy ID", 
                      command=lambda: self._copy_to_clipboard(pin_id)).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="✅ Close", 
                      command=detail_window.destroy).pack(side=tk.RIGHT)
                      
        except Exception as e:
            self.logger.error(f"Error showing pin details: {str(e)}", exc_info=True)
            show_error("Error", f"Failed to show details: {str(e)}")

    def _copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(text)
            show_info("Copied", f"📋 Copied to clipboard:\n{text}")
        except Exception as e:
            show_error("Error", f"Failed to copy: {str(e)}")

    def unlock_all_pins(self) -> None:
        """Set all pins to unlocked status with modern feedback"""
        self.logger.debug("Unlocking all pins")
        try:
            if not self.pins_data:
                show_info("Info", "No pins data loaded")
                return
                
            changes_made = False
            
            for pin_id, pin_info in self.pins_data.items():
                pin_element = pin_info['element']
                current_status = pin_info['unlocked']
                
                if current_status != "1":
                    pin_element.set("eUnlocked", "1")
                    pin_info['unlocked'] = "1"
                    changes_made = True
            
            if changes_made:
                self.main_window.unsaved_label.config(text="Unsaved Changes")
                self._update_all_displays()
                show_success("Success", "🔓 All pins have been unlocked!")
            else:
                show_info("Info", "ℹ️ All pins are already unlocked")
        
        except Exception as e:
            self.logger.error(f"Error unlocking pins: {str(e)}", exc_info=True)
            show_error("Error", f"❌ Failed to unlock pins: {str(e)}")

    def unlock_selected_pins(self) -> None:
        """Unlock selected pins in the treeview"""
        self.logger.debug("Unlocking selected pins")
        try:
            selected_items = self.pins_tree.selection()
            if not selected_items:
                show_info("Info", "No pins selected")
                return
                
            changes_made = False
            
            for item in selected_items:
                pin_id = self._extract_pin_id_from_item(item)
                
                if pin_id and pin_id in self.pins_data:
                    pin_info = self.pins_data[pin_id]
                    current_status = pin_info['unlocked']
                    
                    if current_status != "1":
                        pin_info['element'].set("eUnlocked", "1") 
                        pin_info['unlocked'] = "1"
                        changes_made = True
            
            if changes_made:
                self.main_window.unsaved_label.config(text="Unsaved Changes")
                self._update_all_displays()
                show_success("Success", "🔓 Selected pins have been unlocked!")
            else:
                show_info("Info", "ℹ️ Selected pins are already unlocked")
                
        except Exception as e:
            self.logger.error(f"Error unlocking selected pins: {str(e)}", exc_info=True)
            show_error("Error", f"❌ Failed to unlock selected pins: {str(e)}")

    def reset_all_pins(self) -> None:
        """Reset all pins to locked status (eUnlocked=0)"""
        self.logger.debug("Resetting all pins to locked status")
        try:
            if not self.pins_data:
                show_info("Info", "No pins data loaded")
                return
                
            # Confirmation dialog for destructive action
            result = ask_question("Confirm Reset", 
                                "🔒 This will lock ALL pins. Are you sure you want to continue?")
            if not result:
                return
                
            changes_made = False
            
            for pin_id, pin_info in self.pins_data.items():
                current_status = pin_info['unlocked']
                
                if current_status != "0":
                    pin_info['element'].set("eUnlocked", "0")
                    pin_info['unlocked'] = "0"
                    changes_made = True
            
            if changes_made:
                self.main_window.unsaved_label.config(text="Unsaved Changes")
                self._update_all_displays()
                show_success("Success", "🔒 All pins have been reset to locked status!")
            else:
                show_info("Info", "ℹ️ All pins are already locked")
        
        except Exception as e:
            self.logger.error(f"Error resetting pins: {str(e)}", exc_info=True)
            show_error("Error", f"❌ Failed to reset pins: {str(e)}")

    def _extract_pin_id_from_item(self, item):
        """Extract full pin ID from tree item"""
        # First try to find the pin ID by matching the item data
        values = self.pins_tree.item(item, 'values')
        location = values[1] if len(values) > 1 else ""
        
        # Find matching pin ID by location name
        for pin_id, pin_data in self.pins_data.items():
            pin_location = self._get_location_name(pin_id)
            clean_location = pin_location.replace(" - MULTIPLAYER", "").replace("FIXME! ", "")
            if clean_location == location:
                return pin_id
        
        return None

    def _format_pin_details(self, pin_id, pin_info, location_name):
        """Format detailed pin information for display"""
        element = pin_info['element']
        
        details = []
        details.append(f"🆔 Pin ID: {pin_id}")
        details.append(f"📍 Location: {location_name}")
        details.append("")
        
        # Status information
        status = pin_info['unlocked']
        status_text = {"0": "🔒 Locked", "1": "🔓 Unlocked", "2": "⭐ Special"}.get(status, f"❓ Unreleased ({status})")
        details.append(f"Status: {status_text}")
        
        # Progress information
        fow_current = pin_info.get('fow_current', '')
        if fow_current and fow_current != "-1":
            details.append(f"📊 Progress: {fow_current}%")
        
        details.append("")
        details.append("🔧 Technical Details:")
        details.append("-" * 30)
        
        # All attributes
        for attr_name, attr_value in element.attrib.items():
            details.append(f"{attr_name}: {attr_value}")
        
        # Completion counters
        counters = element.findall("CompletionCounter")
        if counters:
            details.append("")
            details.append(f"📈 Completion Counters ({len(counters)}):")
            details.append("-" * 30)
            for i, counter in enumerate(counters, 1):
                details.append(f"Counter {i}:")
                for attr_name, attr_value in counter.attrib.items():
                    details.append(f"  {attr_name}: {attr_value}")
                details.append("")
        
        return "\n".join(details)

    def load_pins(self, tree: ET.ElementTree) -> None:
        """Load pins data with improved organization"""
        self.logger.debug("Loading pins with modern interface")
        try:
            # Clear existing items
            for item in self.pins_tree.get_children():
                self.pins_tree.delete(item)
            
            self.pins_data = {}
            pins = tree.findall(".//AvatarPinDB_Status/Pin")
            
            # Store reference to container
            root = tree.getroot()
            self.pin_container = root.find(".//AvatarPinDB_Status")
            
            # Process and categorize pins
            categorized_pins = self._categorize_pins(pins)
            
            # Add pins to tree in organized order
            for category, pins_list in categorized_pins.items():
                for pin in sorted(pins_list, key=lambda x: self._get_location_name(x.get("crc_id", ""))):
                    self._process_pin(pin)
            
            self._update_all_displays()
            self.logger.debug("Pins loaded successfully with modern interface")
            
        except Exception as e:
            self.logger.error(f"Error loading pins: {str(e)}", exc_info=True)
            raise

    def _categorize_pins(self, pins):
        """Categorize pins for better organization"""
        categories = {
            'single_player': [],
            'multiplayer': [],
            'Unreleased': []
        }
        
        for pin in pins:
            pin_id = pin.get("crc_id", "")
            location_name = self._get_location_name(pin_id)
            
            if "MULTIPLAYER" in location_name:
                categories['multiplayer'].append(pin)
            elif "FIXME" in location_name:
                categories['Unreleased'].append(pin)
            else:
                categories['single_player'].append(pin)
        
        return categories

    def _process_pin(self, pin):
        """Process a single pin with enhanced display"""
        try:
            pin_id = pin.get("crc_id", "")
            unlocked = pin.get("eUnlocked", "0")
            fow_current = pin.get("fFoWcurrent", "")
            
            # Store pin data
            self.pins_data[pin_id] = {
                'element': pin,
                'unlocked': unlocked,
                'fow_current': fow_current
            }
            
            location_name = self._get_location_name(pin_id)
            
            # Determine pin type and styling
            pin_type, clean_location, tag = self._analyze_pin_type(location_name, unlocked)
            
            # Format status with better icons
            status_icon = self._get_status_icon(unlocked)
            
            # Enhanced progress display
            progress_text = self._format_progress(fow_current)
            
            # Additional details
            counters = len(pin.findall("CompletionCounter"))
            details_text = f"ID: {pin_id[-6:]}" if len(pin_id) > 6 else pin_id
            
            # Insert into tree with enhanced data
            self.pins_tree.insert("", tk.END, values=(
                status_icon,
                clean_location,
                pin_type,
                progress_text,
                details_text
            ), tags=(tag,))
            
        except Exception as e:
            self.logger.error(f"Error processing pin {pin_id}: {str(e)}", exc_info=True)

    def _analyze_pin_type(self, location_name, unlocked):
        """Analyze pin type and return appropriate styling"""
        if "MULTIPLAYER" in location_name:
            pin_type = "👥 Multiplayer"
            clean_location = location_name.replace(" - MULTIPLAYER", "")
            tag = "unlocked_mp" if unlocked == "1" else "locked"
        elif "FIXME" in location_name:
            pin_type = "❓ Unreleased"
            clean_location = location_name.replace("FIXME! ", "")
            tag = "Unreleased"
        else:
            pin_type = "🎮 Single Player"
            clean_location = location_name
            tag = "special" if unlocked == "2" else ("unlocked_sp" if unlocked == "1" else "locked")
        
        return pin_type, clean_location, tag

    def _get_status_icon(self, unlocked):
        """Get appropriate status icon"""
        icons = {"0": "🔒", "1": "🔓", "2": "⭐"}
        return icons.get(unlocked, "❓")

    def _format_progress(self, fow_current):
        """Format progress display"""
        if fow_current and fow_current != "-1":
            try:
                progress = float(fow_current)
                return f"{progress:.1f}%"
            except:
                return fow_current
        return "—"

    def _update_all_displays(self):
        """Update all display elements"""
        self._update_statistics()
        self._update_button_state()
        self._apply_filter()

    def _update_statistics(self):
        """Update statistics with modern display"""
        total = len(self.pins_data)
        unlocked = sum(1 for pin in self.pins_data.values() if pin['unlocked'] == "1")
        locked = total - unlocked
        completion_pct = (unlocked / total * 100) if total > 0 else 0
        
        # Update stat labels
        self.total_pins_label.config(text=str(total))
        self.unlocked_pins_label.config(text=str(unlocked))
        self.locked_pins_label.config(text=str(locked))
        
        # Update progress bar and label
        self.progress_bar['value'] = completion_pct
        self.completion_label.config(text=f"{completion_pct:.1f}% Complete")

    def _apply_filter(self, event=None):
        """Apply filters with improved logic"""
        filter_value = self.filter_var.get()
        search_text = self.search_var.get().lower()
        
        # Store current selection to restore after filtering
        current_selection = self.pins_tree.selection()
        
        # Clear and repopulate based on filter
        for item in self.pins_tree.get_children():
            self.pins_tree.delete(item)
        
        # Re-add filtered items
        for pin_id, pin_data in self.pins_data.items():
            if self._should_show_pin(pin_id, pin_data, filter_value, search_text):
                self._process_pin(pin_data['element'])

    def _should_show_pin(self, pin_id, pin_data, filter_value, search_text):
        """Determine if pin should be shown based on filters"""
        location_name = self._get_location_name(pin_id)
        unlocked = pin_data['unlocked']
        
        # Apply filter
        if filter_value == "🔓 Unlocked" and unlocked != "1":
            return False
        elif filter_value == "🔒 Locked" and unlocked != "0":
            return False
        elif filter_value == "🎮 Single Player" and ("MULTIPLAYER" in location_name or "FIXME" in location_name):
            return False
        elif filter_value == "👥 Multiplayer" and "MULTIPLAYER" not in location_name:
            return False
        elif filter_value == "❓ Unreleased" and "FIXME" not in location_name:
            return False
        
        # Apply search
        if search_text and search_text not in location_name.lower() and search_text not in pin_id.lower():
            return False
        
        return True

    def _get_location_name(self, pin_id):
        """Convert pin ID to human-readable location name"""
        location_names = {
            # SP MAPS
            "3822194552": "HOMETREE",            
            "1057194188": "VA'ERÄ RAMUNONG",
            "1172651822": "THE FEBA",
            "1847852653": "GRAVE'S BOG",
            "2171723794": "THE HANGING GARDENS",
            "2292208788": "SWOTULU",
            "238707229":  "TORUKÄ NA'RìNG",
            "2587251285": "NEEDLE HILLS",
            "2752812145": "ECHO CHASM",
            "2856892107": "KXANìA TAW",
            "2961077726": "LOST CATHEDRAL",
            "3409126972": "PLAINS OF GOLIATH (KAOLIÄ TEI)",
            "355473279":  "BLUE LAGOON",
            "2943222331": "IKNIMAYA",
            "615754132":  "HELL'S GATE",
            "837458676":  "TANTALUS (TA'NATASI)",
            # MULTIPLAYER
            "1437051617": "IKNIMAYA - MULTIPLAYER",
            "902032528":  "NA'RìNG - MULTIPLAYER",
            "1846881984": "FREYNA TARON - MULTIPLAYER",
            "2427499480": "NO'ANI TEI - MULTIPLAYER",  
            "4220570174": "KXANìA TAW - MULTIPLAYER",
            "4168272830": "VA'ERÄ RAMUNONG - MULTIPLAYER",
            "408444403":  "UNIL TUKRU - MULTIPLAYER",
            "3575765971": "VUL NAWM - MULTIPLAYER",
            "948986278":  "SWOTULU - MULTIPLAYER",
            "2232107097": "FORT NAVARONE - MULTIPLAYER",
            "3616200713": "STALKER'S VALLEY - MULTIPLAYER",
            "2509501782": "HELL'S GATE - MULTIPLAYER",
            # FIXME! PINS
            "105239137":  "FIXME! 105239137",
            "1504064473": "FIXME! 1504064473",
            "1578821154": "FIXME! 1578821154",
            "1628184437": "FIXME! 1628184437",
            "1741938656": "FIXME! 1741938656",
            "1771880106": "FIXME! 1771880106",
            "1782610090": "FIXME! 1782610090",
            "1865345760": "FIXME! 1865345760",
            "194406935":  "FIXME! 194406935",
            "2001468046": "FIXME! 2001468046",
            "2169212369": "DEV ROOM 1",
            "2185381138": "FIXME! 2185381138",
            "2216033045": "FIXME! 2216033045",
            "2353717556": "FIXME! 2353717556",
            "2555792139": "FIXME! 2555792139",
            "2672591835": "FIXME! 2672591835",
            "3564339531": "FIXME! 3564339531",
            "3586942544": "FIXME! 3586942544",
            "3615918544": "FIXME! 3615918544",
            "3903502716": "FIXME! 3903502716",
            "3975313082": "DEV ROOM 2",
            "4294730242": "FIXME! 4294730242",
            "470159002":  "FIXME! 470159002",
            "60855408":   "FIXME! 60855408",
            "3852438644": "FIXME! 3852438644",
        }        
        return location_names.get(pin_id, f"Unreleased Location ({pin_id})")


    def save_pin_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        """Save pin changes to the XML tree"""
        self.logger.debug("Saving pin changes")
        # Pin changes are already applied to the elements in the XML tree
        # No additional work needed here as the changes were made directly
        return tree
    
    def _on_tree_select(self, event):
        """Handle tree selection events to update button states"""
        selection = self.pins_tree.selection()
        
        if selection:
            # Check what actions are available for selected items
            unlockable_items = 0
            lockable_items = 0
            
            for item in selection:
                pin_id = self._extract_pin_id_from_item(item)
                if pin_id and pin_id in self.pins_data:
                    pin_info = self.pins_data[pin_id]
                    status = pin_info['unlocked']
                    
                    if status != "1":  # Not unlocked
                        unlockable_items += 1
                    if status != "0":  # Not locked
                        lockable_items += 1
            
            # Update button states
            self.unlock_selected_button.config(
                state="normal" if unlockable_items > 0 else "disabled"
            )
            self.lock_selected_button.config(
                state="normal" if lockable_items > 0 else "disabled"
            )
        else:
            self.unlock_selected_button.config(state="disabled")
            self.lock_selected_button.config(state="disabled")

    def _on_double_click(self, event):
        """Handle double-click to toggle pin status"""
        item = self.pins_tree.selection()[0] if self.pins_tree.selection() else None
        if not item:
            return
            
        try:
            pin_id = self._extract_pin_id_from_item(item)
            if not pin_id or pin_id not in self.pins_data:
                return
                
            pin_info = self.pins_data[pin_id]
            current_status = pin_info['unlocked']
            
            # Toggle status (0 <-> 1, leave 2 as special)
            if current_status == "0":
                new_status = "1"
            elif current_status == "1":
                new_status = "0"
            else:
                # Special status, cycle through 2 -> 1 -> 0 -> 2
                new_status = "1" if current_status == "2" else "0"
            
            pin_info['element'].set("eUnlocked", new_status)
            pin_info['unlocked'] = new_status
            
            # Update displays
            self.main_window.unsaved_label.config(text="Unsaved Changes")
            self._update_all_displays()
            
        except Exception as e:
            self.logger.error(f"Error toggling pin status: {str(e)}", exc_info=True)

    def _update_button_state(self):
        """Update the enable/disable state of the buttons"""
        if not self.pins_data:
            # No data loaded, disable all buttons
            self.unlock_all_button.config(state="disabled")
            self.reset_all_button.config(state="disabled")
            self.unlock_selected_button.config(state="disabled")
            self.lock_selected_button.config(state="disabled")
            return
        
        # Check overall state
        all_unlocked = True
        all_locked = True
        
        for pin_info in self.pins_data.values():
            status = pin_info['unlocked']
            if status != "1":
                all_unlocked = False
            if status != "0":
                all_locked = False
        
        # Update main action buttons
        self.unlock_all_button.config(state="disabled" if all_unlocked else "normal")
        self.reset_all_button.config(state="disabled" if all_locked else "normal")
        
        # Update selection-based buttons (handled in _on_tree_select)
        self._on_tree_select(None)
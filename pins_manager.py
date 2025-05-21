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
        self.pins_data = {}  # Store pins data for modification
        self.setup_ui()

    def setup_ui(self) -> None:
        # Create button frame at the top
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        # Add "Unlock All Pins" button
        self.unlock_all_button = ttk.Button(
            button_frame, 
            text="Unlock All Pins (Set to Status 1)", 
            command=self.unlock_all_pins
        )
        self.unlock_all_button.pack(side=tk.LEFT, padx=5)
        
        # Add "Unlock Selected Pins" button
        self.unlock_selected_button = ttk.Button(
            button_frame,
            text="Unlock Selected Pins",
            command=self.unlock_selected_pins,
            state="disabled"
        )
        self.unlock_selected_button.pack(side=tk.LEFT, padx=5)
        
        # Add "Reset All Pins" button
        self.reset_all_button = ttk.Button(
            button_frame,
            text="Reset All Pins (Set to Status 0)",
            command=self.reset_all_pins
        )
        self.reset_all_button.pack(side=tk.LEFT, padx=5)
        
        # Create Pins Treeview - make it fill the remaining parent space
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
        
        # Bind selection event to enable/disable the unlock selected button
        self.pins_tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def load_pins(self, tree: ET.ElementTree) -> None:
        self.logger.debug("Loading pins")
        try:
            # Clear existing items
            for item in self.pins_tree.get_children():
                self.pins_tree.delete(item)
            
            # Find all pin elements in XML
            self.pins_data = {}  # Reset pins data
            pins = tree.findall(".//AvatarPinDB_Status/Pin")
            
            self.logger.debug(f"Found {len(pins)} pins")
            
            # Store reference to the parent element for later use
            self.pin_container = None
            if pins:
                # Find the parent element that contains the pins
                root = tree.getroot()
                pin_container = root.find(".//AvatarPinDB_Status")
                if pin_container is not None:
                    self.pin_container = pin_container
            
            # Sort pins by ID for consistent display
            pins_sorted = sorted(pins, key=lambda x: x.get("crc_id", "0"))
            
            # Process each pin
            for pin in pins_sorted:
                try:
                    pin_id = pin.get("crc_id", "")
                    unlocked = pin.get("eUnlocked", "0")
                    fow_current = pin.get("fFoWcurrent", "")
                    
                    # Store the pin element reference and attributes
                    self.pins_data[pin_id] = {
                        'element': pin,
                        'unlocked': unlocked,
                        'fow_current': fow_current
                    }
                    
                    # Get the pin location name
                    location_name = self._get_location_name(pin_id)
                    
                    # Get status text
                    status = "Unlocked" if unlocked == "1" else "Locked"
                    
                    # Count completion counters
                    counters = len(pin.findall("CompletionCounter"))
                    counters_text = f"{counters}" if counters > 0 else "None"
                    
                    # Determine tag based on unlocked status
                    tag = "unlocked" if unlocked == "1" else "locked"
                    
                    self.pins_tree.insert("", tk.END, values=(
                        pin_id,
                        location_name,
                        status,
                        counters_text
                    ), tags=(tag,))
                    
                except Exception as e:
                    self.logger.error(f"Error processing pin {pin_id}: {str(e)}", exc_info=True)

            # Enable/disable buttons based on the state
            self._update_button_state()
            
            self.logger.debug("Pins loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading pins: {str(e)}", exc_info=True)
            raise

    def unlock_all_pins(self) -> None:
        """Set all pins to unlocked status (eUnlocked=1)"""
        self.logger.debug("Unlocking all pins")
        try:
            if not self.pins_data:
                messagebox.showinfo("Info", "No pins data loaded")
                return
                
            # Track if any changes were made
            changes_made = False
            
            # Update all pins to unlocked status
            for pin_id, pin_info in self.pins_data.items():
                pin_element = pin_info['element']
                current_status = pin_info['unlocked']
                
                # Only update if it's not already unlocked
                if current_status != "1":
                    pin_element.set("eUnlocked", "1")
                    pin_info['unlocked'] = "1"
                    changes_made = True
            
            # If changes were made, mark as unsaved and update the tree view
            if changes_made:
                # Update the tree view to show all pins as unlocked 
                for item in self.pins_tree.get_children():
                    # Set the tag to unlocked
                    self.pins_tree.item(item, tags=('unlocked',))
                    
                    # Update the status column (which is at index 2)
                    values = list(self.pins_tree.item(item, 'values'))
                    values[2] = "Unlocked"
                    self.pins_tree.item(item, values=values)
                
                # Mark changes as unsaved
                self.main_window.unsaved_label.config(text="Unsaved Changes")
                
                # Update button state
                self._update_button_state()
                
                messagebox.showinfo("Success", "All pins have been unlocked")
            else:
                messagebox.showinfo("Info", "All pins are already unlocked")
        
        except Exception as e:
            self.logger.error(f"Error unlocking pins: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to unlock pins: {str(e)}")

    def unlock_selected_pins(self) -> None:
        """Unlock selected pins in the treeview"""
        self.logger.debug("Unlocking selected pins")
        try:
            # Get selected items
            selected_items = self.pins_tree.selection()
            if not selected_items:
                self.logger.debug("No pins selected")
                return
                
            # Track if any changes were made
            changes_made = False
            
            # Process each selected item
            for item in selected_items:
                values = self.pins_tree.item(item, 'values')
                pin_id = values[0]
                
                # Skip if pin ID not found
                if pin_id not in self.pins_data:
                    continue
                
                pin_info = self.pins_data[pin_id]
                pin_element = pin_info['element']
                current_status = pin_info['unlocked']
                fow_current = pin_info.get('fow_current', '')
                
                # Only update if it's not already unlocked
                if current_status != "1":
                    pin_element.set("eUnlocked", "1") 
                    pin_info['unlocked'] = "1"
                    
                    # Update the tree view
                    self.pins_tree.item(item, tags=('unlocked',))
                    
                    # Update the status column
                    values = list(values)
                    values[2] = "Unlocked"
                    self.pins_tree.item(item, values=values)
                    
                    changes_made = True
            
            # If changes were made, mark as unsaved
            if changes_made:
                self.main_window.unsaved_label.config(text="Unsaved Changes")
                self._update_button_state()
                messagebox.showinfo("Success", "Selected pins have been unlocked")
            else:
                messagebox.showinfo("Info", "No changes needed - selected pins are already unlocked or are inactive")
                
        except Exception as e:
            self.logger.error(f"Error unlocking selected pins: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to unlock selected pins: {str(e)}")

    def reset_all_pins(self) -> None:
        """Reset all pins to locked status (eUnlocked=0)"""
        self.logger.debug("Resetting all pins to locked status")
        try:
            if not self.pins_data:
                messagebox.showinfo("Info", "No pins data loaded")
                return
                
            # Track if any changes were made
            changes_made = False
            
            # Update all pins to locked status
            for pin_id, pin_info in self.pins_data.items():
                pin_element = pin_info['element']
                current_status = pin_info['unlocked']
                
                # Only update if it's not already locked
                if current_status != "0":
                    pin_element.set("eUnlocked", "0")
                    pin_info['unlocked'] = "0"
                    changes_made = True
            
            # If changes were made, mark as unsaved and update the tree view
            if changes_made:
                # Update the tree view to show all pins as locked
                for item in self.pins_tree.get_children():
                    # Set the tag to locked
                    self.pins_tree.item(item, tags=('locked',))
                    
                    # Update the status column (which is at index 2)
                    values = list(self.pins_tree.item(item, 'values'))
                    values[2] = "Locked"
                    self.pins_tree.item(item, values=values)
                
                # Mark changes as unsaved
                self.main_window.unsaved_label.config(text="Unsaved Changes")
                
                # Update button state
                self._update_button_state()
                
                messagebox.showinfo("Success", "All pins have been reset to locked status")
            else:
                messagebox.showinfo("Info", "All pins are already locked")
        
        except Exception as e:
            self.logger.error(f"Error resetting pins: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to reset pins: {str(e)}")

    def save_pin_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        self.logger.debug("Saving pin changes")
        # Pin changes are already applied to the elements in the XML tree
        # No additional work needed here as the changes were made directly
        return tree
    
    def _on_tree_select(self, event):
        """Handle tree selection events to update button states"""
        selection = self.pins_tree.selection()
        
        # Enable/disable unlock selected button based on selection
        if selection:
            # Check if any selected items are locked
            lockable_items_exist = False
            for item in selection:
                values = self.pins_tree.item(item, 'values')
                pin_id = values[0]
                if pin_id in self.pins_data:
                    pin_info = self.pins_data[pin_id]
                    if pin_info['unlocked'] != "1":
                        lockable_items_exist = True
                        break
            
            if lockable_items_exist:
                self.unlock_selected_button.config(state="normal")
            else:
                self.unlock_selected_button.config(state="disabled")
        else:
            self.unlock_selected_button.config(state="disabled")
    
    def _update_button_state(self):
        """Update the enable/disable state of the buttons"""
        all_unlocked = True
        all_locked = True
        
        # Check if all pins are already unlocked/locked
        for pin_id, pin_info in self.pins_data.items():
            if pin_info['unlocked'] != "1":
                all_unlocked = False
            
            if pin_info['unlocked'] != "0":
                all_locked = False
        
        # Disable unlock button if all pins are already unlocked
        if all_unlocked:
            self.unlock_all_button.config(state="disabled")
        else:
            self.unlock_all_button.config(state="normal")
            
        # Disable reset button if all pins are already locked
        if all_locked:
            self.reset_all_button.config(state="disabled")
        else:
            self.reset_all_button.config(state="normal")
            
        # Update the unlock selected button state
        self._on_tree_select(None)
    
    def _get_location_name(self, pin_id):
        """Convert pin ID to human-readable location name"""
        location_names = {
            # SP MAPS
            "1057194188": "VA'ERÄ RAMUNONG",
            "1172651822": "THE FEBA",
            "1437051617": "IKNIMAYA",
            "1846881984": "FREYNA TARON",
            "1847852653": "GRAVE'S BOG",
            "2171723794": "THE HANGING GARDENS",
            "2232107097": "FORT NAVARONE",
            "2292208788": "SWOTULU",
            "238707229":  "TORUKÄ NA'RìNG",
            "2427499480": "NO'ANI TEI",
            "2509501782": "HELL'S GATE",
            "2587251285": "NEEDLE HILLS",
            "2752812145": "ECHO CHASM",
            "2856892107": "KXANìA TAW",
            "2961077726": "LOST CATHEDRAL",
            "3409126972": "PLAINS OF GOLIATH (KAOLIÄ TEI)",
            "355473279":  "BLUE LAGOON",
            "3575765971": "VUL NAWM",
            "3616200713": "STALKER'S VALLEY",
            "3822194552": "HOMETREE",
            "408444403":  "UNIL TUKRU",
            "4168272830": "VA'ERÄ RAMUNONG",
            "2943222331": "IKNIMAYA",
            "4220570174": "KXANìA TAW",
            "615754132":  "HELL'S GATE",
            "837458676":  "TANTALUS (TA'NATASI)",
            "902032528":  "NA'RìNG",
            "948986278":  "SWOTULU",

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
            "2169212369": "FIXME! -2125754927",
            "2185381138": "FIXME! -2109586158",
            "2216033045": "FIXME! -2078934251",
            "2353717556": "FIXME! -1941249740",
            "2555792139": "FIXME! -1739175157",
            "2672591835": "FIXME! -1622375461",
            "3564339531": "FIXME! -730627765",
            "3586942544": "FIXME! -708024752",
            "3615918544": "FIXME! -679048752",
            "3822194552": "FIXME! -442528652",
            "3903502716": "FIXME! -391464580",
            "3975313082": "FIXME! -319654214",
            "4294730242": "FIXME! -237054",
            "470159002":  "FIXME! 470159002",
            "60855408":   "FIXME! 60855408",
            "3852438644": "FIXME! -442528652",

        }        
        return location_names.get(pin_id, f"Unknown Location ({pin_id})")
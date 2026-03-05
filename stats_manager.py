import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
from typing import Dict, Optional
from ui_components import LabeledInput, block_combobox_mousewheel
import os
from PIL import Image, ImageTk
from Face_Image_Window import FaceImageWindow
import logging
from custom_messagebox import MessageBoxManager, show_info, show_error, show_warning, ask_question, ask_ok_cancel, show_success
import json

class StatsManager:
    def __init__(self, parent: ttk.Frame, main_window):
        self.logger = logging.getLogger('StatsManager')
        self.logger.debug("Initializing Modern StatsManager")
        self.parent = parent
        self.main_window = main_window

        self.sound_manager = getattr(main_window, 'sound_manager', None)

        self.entries = {}
        self.face_image_frame = None
        self.face_image_label = None
        self.label_frames = {}
        self.weapon_slots = []
        self.navi_weapon_slots = []
        self.armor_dropdowns = {}
        self.navi_armor_dropdowns = {}
        self.armor_preview_labels = {}  # For RDA armor previews
        self.navi_armor_preview_labels = {}  # For Na'vi armor previews
        self.saved_outfits_rda = []  # List of saved RDA outfits
        self.saved_outfits_navi = []  # List of saved Na'vi outfits
        self.composite_preview_labels = {}  # For layered armor preview

        self._create_coordinate_mappings()

        self._create_last_loaded_pin_mappings()

        self.rda_skill_slots = []
        self.navi_skill_slots = []
        
        # Create skill mappings
        self._create_skill_mappings()

        # Create item mappings FIRST
        self._create_item_mappings()
        
        # Initialize face values mapping
        self.face_values = {}
        for i in range(12):  # 12 pairs (00-11)
            face_num = str(i).zfill(2)
            self.face_values[str(i)] = {
                "male": f"Male {face_num}",
                "female": f"Female {face_num}"
            }
        
        self.setup_modern_ui()

    def _wrap_button_with_sound(self, button, command=None):
        """Wrap a button with click and hover sounds"""
        if command is None:
            command = button.cget('command')
        
        def sound_command():
            if self.sound_manager and hasattr(self.main_window.config, 'play_click_sounds'):
                if self.main_window.config.play_click_sounds:
                    self.sound_manager.play_sound_effect('click')
            if command:
                if callable(command):
                    command()
                else:
                    try:
                        button.tk.call(command)
                    except:
                        pass
        
        button.config(command=sound_command)
        
        # Add hover sound
        if self.sound_manager and hasattr(self.main_window.config, 'play_hover_sounds'):
            if self.main_window.config.play_hover_sounds:
                button.bind('<Enter>', lambda e: self.sound_manager.play_sound_effect('hover'))
        
        return button

    def _add_hover_sound_to_combobox(self, combobox):
        """Add hover sound effect to a combobox"""
        if self.sound_manager and hasattr(self.main_window.config, 'play_hover_sounds'):
            if self.main_window.config.play_hover_sounds:
                combobox.bind('<Enter>', lambda e: self.sound_manager.play_sound_effect('hover'))
        return combobox

    def setup_modern_ui(self) -> None:
        """Setup the modern UI with consistent styling"""
        # Create main container with padding
        self.main_container = ttk.Frame(self.parent)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # === HEADER SECTION ===
        self.create_header_section()
        
        # === CONTENT AREA ===
        content_frame = ttk.Frame(self.main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        # Main content with sections
        self.create_main_content(content_frame)

    def create_header_section(self):
        """Create a simple header with just title"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 2))
        
        title_label = ttk.Label(header_frame, text="👤 Character Stats", 
                            font=('Segoe UI', 12, 'bold'))
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(header_frame, text="Manage your character's attributes, equipment, and progression", 
                                font=('Segoe UI', 8), foreground='gray')
        subtitle_label.pack(anchor=tk.W)

    def create_main_content(self, parent):
        """Create the main content area with nested tabs"""
        # Content container with padding
        content_container = ttk.Frame(parent, padding=0)
        content_container.pack(fill=tk.BOTH, expand=True)
        
        # Create main notebook for tabs
        main_notebook = ttk.Notebook(content_container)
        main_notebook.pack(fill=tk.BOTH, expand=True)
        
        # ADD HOVER SOUND TO TABS (only once per tab)
        self._last_hovered_tab = None  # Track which tab we're hovering over
        
        def on_tab_hover(event):
            """Play hover sound when mouse enters a NEW tab"""
            if self.sound_manager and hasattr(self.main_window.config, 'play_hover_sounds'):
                if self.main_window.config.play_hover_sounds:
                    try:
                        tab_id = main_notebook.identify(event.x, event.y)
                        # Only play sound if we're over a tab AND it's a different tab than before
                        if tab_id and tab_id != self._last_hovered_tab:
                            self._last_hovered_tab = tab_id
                            self.sound_manager.play_sound_effect('hover')
                        elif not tab_id:
                            # Reset when not hovering over any tab
                            self._last_hovered_tab = None
                    except:
                        pass
        
        # Bind hover event to the notebook
        main_notebook.bind('<Motion>', on_tab_hover)
        
        # === TAB 1: Character & Settings ===
        char_settings_tab = ttk.Frame(main_notebook, padding=10)
        main_notebook.add(char_settings_tab, text="📊 Character & Settings")
        
        # Configure grid to make all boxes same size
        char_settings_tab.grid_columnconfigure(0, weight=1, uniform="boxes")
        char_settings_tab.grid_columnconfigure(1, weight=1, uniform="boxes")
        char_settings_tab.grid_rowconfigure(0, weight=1, uniform="boxes")
        char_settings_tab.grid_rowconfigure(1, weight=1, uniform="boxes")
        
        # Top left: Character Info
        self.create_character_info_section_grid(char_settings_tab, 0, 0)
        
        # Top right: Progress Info
        self.create_progress_section_grid(char_settings_tab, 0, 1)
        
        # Bottom left: Game Settings
        self.create_game_settings_section_grid(char_settings_tab, 1, 0)
        
        # Bottom right: Cost Reduction
        self.create_cost_reduction_section_grid(char_settings_tab, 1, 1)
        
        # === TAB 2: RDA Equipment ===
        rda_tab = ttk.Frame(main_notebook, padding=10)
        main_notebook.add(rda_tab, text="🤖 RDA Equipment")
        
        # RDA Equipment content
        self.create_rda_equipment_section(rda_tab)
        
        # === TAB 3: Na'vi Equipment ===
        navi_tab = ttk.Frame(main_notebook, padding=10)
        main_notebook.add(navi_tab, text="🌿 Na'vi Equipment")
        
        # Na'vi Equipment content
        self.create_navi_equipment_section(navi_tab)

    def create_character_info_section(self, parent):
        """Create character info section with face preview"""
        char_frame = ttk.LabelFrame(parent, text="👤 Character Information", padding=10)
        char_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        # Main content area
        content_frame = ttk.Frame(char_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side: Character fields
        fields_frame = ttk.Frame(content_frame)
        fields_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Two columns for character fields
        left_col = ttk.Frame(fields_frame)
        left_col.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        right_col = ttk.Frame(fields_frame)
        right_col.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # Left column fields
        self.create_compact_field_item(left_col, "Character Name", "namevec")
        self.create_compact_field_item(left_col, "Gender", "isfemale", {"0": "Male", "1": "Female"}, readonly=True)
        self.create_compact_field_item(left_col, "Face", "face", self.face_values, readonly=True)

        location_options = {"-1": "-No Location Set-"}
        location_options.update(self.last_loaded_pin_mappings)
        self.create_compact_field_item(left_col, "Current Location", "crc_LastLoadedPin",
                            location_options)

        # Right column fields (editable - these should be comboboxes)
        print("DEBUG: Creating Side field with options:", {"4": "Undecided", "1": "Na'vi", "2": "RDA", "3": "Neutral"})

        self.create_compact_field_item(
            right_col, "Player Faction", "PlayerFaction", 
            {"0": "Undecided", "1": "Na'vi", "2": "RDA", "3": "Neutral"}
        )

        self.create_compact_field_item(
            right_col, "Side", "side", 
            {"4": "Undecided", "1": "Na'vi", "2": "RDA", "3": "Neutral"}
        )        

        print("DEBUG: Creating Pawn field with options:", {"1": "Na'vi", "2": "RDA"})
        self.create_compact_field_item(
            right_col, "Pawn", "pawn", 
            {"1": "Na'vi", "2": "RDA"}
        )
        
        self.create_compact_field_item(right_col, "Location", "YouAreHere_LatitudeLongitude", readonly=True)
        
        # Check what type of widget was created
        print(f"DEBUG: side widget type: {type(self.entries['side'])}")
        print(f"DEBUG: pawn widget type: {type(self.entries['pawn'])}")
        
        # Right side: Face preview
        preview_frame = ttk.LabelFrame(content_frame, text="Preview", padding=5)
        preview_frame.pack(side=tk.RIGHT)
        
        self.face_image_label = ttk.Label(preview_frame, text="No Image", width=15)
        self.face_image_label.pack(pady=5)

    def create_progress_section(self, parent):
        """Create compact progress section"""
        progress_frame = ttk.LabelFrame(parent, text="📊 Progress & Faction", padding=10)
        progress_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        # Main faction info        
        self.create_compact_field_item(progress_frame, "Total EP", "TotalEP", readonly=True)
        
        # Max out button (smaller)
        ttk.Button(progress_frame, text="🚀 Max Out Level", 
                command=self._max_out_level).pack(fill=tk.X, pady=2)
        
        ttk.Button(progress_frame, text="➕ Add Custom EP Value",
        command=self._add_custom_ep).pack(fill=tk.X, pady=2)
        
        # EP Values in horizontal layout
        ep_frame = ttk.Frame(progress_frame)
        ep_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Player0 and Player1 side by side
        p0_frame = ttk.Frame(ep_frame)
        p0_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        p1_frame = ttk.Frame(ep_frame)
        p1_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        self.create_compact_field_item(p0_frame, "Player0 EPs", "EPs")
        self.create_compact_field_item(p0_frame, "Player0 newEPs", "newEPs")
        
        self.create_compact_field_item(p1_frame, "Player1 EPs", "EPs_Player1")
        self.create_compact_field_item(p1_frame, "Player1 newEPs", "newEPs_Player1")

    def create_character_info_section_grid(self, parent, row, col):
        """Create character info section for grid layout"""
        char_frame = ttk.LabelFrame(parent, text="👤 Character Information", padding=10)
        char_frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        
        # Main content area
        content_frame = ttk.Frame(char_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side: Character fields
        fields_frame = ttk.Frame(content_frame)
        fields_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Two columns for character fields
        left_col = ttk.Frame(fields_frame)
        left_col.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        right_col = ttk.Frame(fields_frame)
        right_col.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # Left column fields
        self.create_compact_field_item(left_col, "Character Name", "namevec")
        self.create_compact_field_item(left_col, "Gender", "isfemale", {"0": "Male", "1": "Female"}, readonly=True)
        self.create_compact_field_item(left_col, "Face", "face", self.face_values, readonly=True)

        location_options = {"-1": "-No Location Set-"}
        location_options.update(self.last_loaded_pin_mappings)
        self.create_compact_field_item(left_col, "Current Location", "crc_LastLoadedPin",
                            location_options)

        # Right column fields (editable - these should be comboboxes)
        self.create_compact_field_item(
            right_col, "Player Faction", "PlayerFaction",
            {"0": "Undecided", "1": "Na'vi", "2": "RDA", "3": "Neutral"}
        )

        self.create_compact_field_item(
            right_col, "Side", "side", 
            {"4": "Undecided", "1": "Na'vi", "2": "RDA", "3": "Neutral"}
        )        

        self.create_compact_field_item(
            right_col, "Pawn", "pawn", 
            {"1": "Na'vi", "2": "RDA"}
        )
        
        self.create_compact_field_item(right_col, "Location", "YouAreHere_LatitudeLongitude", readonly=True)
        
        # Right side: Face preview
        preview_frame = ttk.LabelFrame(content_frame, text="Preview", padding=5)
        preview_frame.pack(side=tk.RIGHT)
        
        self.face_image_label = ttk.Label(preview_frame, text="No Image", width=15)
        self.face_image_label.pack(pady=5)

    def create_progress_section_grid(self, parent, row, col):
        """Create compact progress section for grid layout"""
        progress_frame = ttk.LabelFrame(parent, text="📊 Progress & Faction", padding=10)
        progress_frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        
        # Main faction info        
        self.create_compact_field_item(progress_frame, "Total EP", "TotalEP", readonly=True)
        
        # Buttons in horizontal layout
        buttons_frame = ttk.Frame(progress_frame)
        buttons_frame.pack(fill=tk.X, pady=2)
        
        max_btn = ttk.Button(buttons_frame, text="🚀 Max Out Level")
        self._wrap_button_with_sound(max_btn, self._max_out_level)
        max_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
                
        ep_btn = ttk.Button(buttons_frame, text="➕ Add Custom EP")
        self._wrap_button_with_sound(ep_btn, self._add_custom_ep)
        ep_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))
        
        # EP Values in horizontal layout
        ep_frame = ttk.Frame(progress_frame)
        ep_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Player0 and Player1 side by side
        p0_frame = ttk.Frame(ep_frame)
        p0_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        p1_frame = ttk.Frame(ep_frame)
        p1_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        self.create_compact_field_item(p0_frame, "Player0 EPs", "EPs")
        self.create_compact_field_item(p0_frame, "Player0 newEPs", "newEPs")
        
        self.create_compact_field_item(p1_frame, "Player1 EPs", "EPs_Player1")
        self.create_compact_field_item(p1_frame, "Player1 newEPs", "newEPs_Player1")

    def create_game_settings_section_grid(self, parent, row, col):
        """Create game settings section for grid layout"""
        game_settings_frame = ttk.LabelFrame(parent, text="⚙️ Game Settings", padding=10)
        game_settings_frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

        self.create_compact_field_item(
            game_settings_frame, "Entity Scanning", "bEntityScanningEnabled",
            {"0": "Disabled", "1": "Enabled"}
        )

        self.create_compact_field_item(
            game_settings_frame, "First Person Mode", "FirstPersonMode",
            {"0": "Disabled", "1": "Enabled"}
        )

        self.create_compact_field_item(
            game_settings_frame, "Rumble Enabled", "RumbleEnabled",
            {"0": "Disabled", "1": "Enabled"}
        )

    def create_cost_reduction_section_grid(self, parent, row, col):
        """Create cost reduction section for grid layout"""
        cost_frame = ttk.LabelFrame(parent, text="💰 Cost Reduction", padding=10)
        cost_frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

        self.create_compact_field_item(cost_frame, "Na'vi Cost Reduction", "NaviCostReduction")
        self.create_compact_field_item(cost_frame, "RDA Cost Reduction", "CorpCostReduction")
        self.create_compact_field_item(cost_frame, "Recovery Bits", "RecoveryBits")

    def _add_custom_ep(self):
        """Add a custom EP value to the current total"""
        try:
            if self.main_window.tree is None:
                show_error("Error", "No save file loaded. Please load a save file first.")
                return
            
            # Get current EP value
            total_ep_widget = self.entries.get("TotalEP")
            if not total_ep_widget:
                show_error("Error", "Total EP widget not found.")
                return
            
            total_ep_text = total_ep_widget.cget("text") if hasattr(total_ep_widget, 'cget') else total_ep_widget.get()
            
            # Extract current EP from "12345/500000 (Max EP)" format
            if "/" in total_ep_text:
                current_ep = int(total_ep_text.split("/")[0])
            else:
                current_ep = 0
            
            # Create custom input dialog
            input_dialog = tk.Toplevel(self.parent)
            input_dialog.title("Add Custom EP")
            input_dialog.geometry("400x200")
            input_dialog.transient(self.parent)
            input_dialog.grab_set()
            
            # Center the dialog
            input_dialog.update_idletasks()
            x = (input_dialog.winfo_screenwidth() // 2) - (input_dialog.winfo_width() // 2)
            y = (input_dialog.winfo_screenheight() // 2) - (input_dialog.winfo_height() // 2)
            input_dialog.geometry(f"+{x}+{y}")
            
            # Result variable
            result = {"value": None}
            
            # Content frame
            content_frame = ttk.Frame(input_dialog, padding=20)
            content_frame.pack(fill=tk.BOTH, expand=True)
            
            # Info label
            info_label = ttk.Label(
                content_frame, 
                text=f"Current EP: {current_ep:,}\n\nEnter EP amount to add (numbers only):",
                font=('Segoe UI', 10)
            )
            info_label.pack(pady=(0, 10))
            
            # Entry field with validation
            entry_var = tk.StringVar()
            
            def validate_numeric_input(new_value):
                """Only allow numeric input"""
                if new_value == "":
                    return True
                try:
                    int(new_value)
                    return True
                except ValueError:
                    return False
            
            vcmd = (input_dialog.register(validate_numeric_input), '%P')
            entry = ttk.Entry(content_frame, textvariable=entry_var, font=('Segoe UI', 10), validate='key', validatecommand=vcmd)
            entry.pack(fill=tk.X, pady=(0, 10))
            entry.focus_set()
            
            # Validation label
            validation_label = ttk.Label(content_frame, text="", foreground="red", font=('Segoe UI', 8))
            validation_label.pack(pady=(0, 10))
            
            def validate_and_submit():
                try:
                    if not entry_var.get():
                        validation_label.config(text="Please enter a value")
                        return
                        
                    value = int(entry_var.get())
                    if value < 1:
                        validation_label.config(text="Value must be at least 1")
                        return
                    if value > 2147483647:
                        validation_label.config(text="Value must not exceed 2,147,483,647")
                        return
                    result["value"] = value
                    input_dialog.destroy()
                except ValueError:
                    validation_label.config(text="Please enter a valid number")
            
            def cancel():
                input_dialog.destroy()
            
            # Button frame
            button_frame = ttk.Frame(content_frame)
            button_frame.pack(fill=tk.X)
            
            ttk.Button(button_frame, text="Add EP", command=validate_and_submit).pack(side=tk.LEFT, padx=(0, 5), expand=True, fill=tk.X)
            ttk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.RIGHT, expand=True, fill=tk.X)
            
            # Bind Enter key
            entry.bind('<Return>', lambda e: validate_and_submit())
            entry.bind('<Escape>', lambda e: cancel())
            
            # Wait for dialog to close
            input_dialog.wait_window()
            
            custom_value = result["value"]
            
            if custom_value is None:  # User cancelled
                return
            
            # Calculate new EP
            new_ep = current_ep + custom_value
            
            # Max EP is now 2,147,483,647 (max 32-bit signed integer)
            max_ep = 2147483647
            
            # Cap at max EP if it exceeds
            capped = False
            if new_ep > max_ep:
                new_ep = max_ep
                capped = True
            
            # Update the EP display with new max
            formatted_ep = f"{new_ep}/{max_ep} (Max EP)"
            if hasattr(total_ep_widget, 'config'):
                total_ep_widget.config(text=formatted_ep)
            else:
                total_ep_widget.delete(0, tk.END)
                total_ep_widget.insert(0, formatted_ep)
            
            # Update BaseInfo TotalEP
            base_info = self.main_window.tree.getroot().find(".//BaseInfo")
            if base_info is not None:
                base_info.set("TotalEP", str(new_ep))
            
            # Mark changes as unsaved
            self._mark_unsaved_changes()
            
            # Show success message
            if capped:
                show_warning("EP Capped", 
                            f"Added {custom_value:,} EP, but total was capped at maximum ({max_ep:,}).\nNew total: {new_ep:,}")
            else:
                show_success("EP Added", 
                            f"Successfully added {custom_value:,} EP.\nNew total: {new_ep:,}")
            
        except Exception as e:
            self.logger.error(f"Error adding custom EP: {str(e)}", exc_info=True)
            show_error("Error", f"Failed to add custom EP: {str(e)}")

    def _max_out_level(self):
        """Max out the experience to 2,147,483,647"""
        try:
            if self.main_window.tree is None:
                show_error("Error", "No save file loaded. Please load a save file first.")
                return
                
            # Set to max 32-bit signed integer
            max_ep = 2147483647
            
            # Update the EP display
            ep_widget = self.entries["TotalEP"]
            formatted_ep = f"{max_ep}/{max_ep} (Max EP)"
            if hasattr(ep_widget, 'config'):
                ep_widget.config(text=formatted_ep)
            else:
                ep_widget.delete(0, tk.END)
                ep_widget.insert(0, formatted_ep)
            
            # Update BaseInfo TotalEP if tree exists
            if self.main_window.tree is not None:
                base_info = self.main_window.tree.getroot().find(".//BaseInfo")
                if base_info is not None:
                    base_info.set("TotalEP", str(max_ep))
            
            # Mark changes as unsaved
            self._mark_unsaved_changes()
            
            # Show success message
            show_info("EP Maxed Out", 
                            f"Successfully set experience to maximum amount ({max_ep:,}).")
            
        except Exception as e:
            self.logger.error(f"Error maxing out level: {str(e)}", exc_info=True)
            show_error("Error", f"Failed to max out level: {str(e)}")


    def _update_xp_info(self, xp_info: Optional[ET.Element]) -> None:
        if xp_info is None:
            return
        
        # First, check if there's a TotalEP value in BaseInfo
        total_ep = "0"
        if self.main_window.tree is not None:
            base_info = self.main_window.tree.getroot().find(".//BaseInfo")
            if base_info is not None:
                total_ep = base_info.get("TotalEP", total_ep)
        
        # If no TotalEP found in BaseInfo, fall back to 0
        if total_ep == "0":
            total_ep = "0"
        
        # Max EP is now 2,147,483,647
        max_ep = 2147483647
        
        # Update TotalEP display with the new format
        if "TotalEP" in self.entries:
            widget = self.entries["TotalEP"]
            formatted_ep = f"{total_ep}/{max_ep} (Max EP)"
            if isinstance(widget, ttk.Label):
                widget.config(text=formatted_ep)
            else:
                widget.delete(0, tk.END)
                widget.insert(0, formatted_ep)
        
        # Log the total EP for debugging
        self.logger.debug(f"Total EP set to: {total_ep}")


    def _on_faction_selected(self, event):
        """Handle faction selection change"""
        try:
            if self.main_window.tree is None:
                show_error("Error", "No save file loaded. Please load a save file first.")
                self.entries["PlayerFaction"].selection_clear()
                return
                
            selected_faction = self.entries["PlayerFaction"].get()
            
            # Max EP is always 2,147,483,647 regardless of faction
            max_ep = 2147483647
            
            # Update the EP display format
            ep_widget = self.entries["TotalEP"]
            current_ep = ep_widget.cget("text") if hasattr(ep_widget, 'cget') else ep_widget.get()
            
            # Handle format conversions
            if "/" in current_ep:
                current_ep = current_ep.split("/")[0]
            
            # Update with new format
            if hasattr(ep_widget, 'config'):
                ep_widget.config(text=f"{current_ep}/{max_ep} (Max EP)")
            else:
                ep_widget.delete(0, tk.END)
                ep_widget.insert(0, f"{current_ep}/{max_ep} (Max EP)")
            
            # Mark changes as unsaved
            self.main_window.unsaved_label.config(text="Unsaved Changes")
        except Exception as e:
            self.logger.error(f"Error in faction selection: {str(e)}")
            show_error("Error", f"Failed to change faction: {str(e)}")

    def _on_current_location_selected(self, event):
        """Handle current location selection change"""
        try:
            if self.main_window.tree is None:
                show_error("Error", "No save file loaded. Please load a save file first.")
                self.entries["crc_LastLoadedPin"].selection_clear()
                return
                
            selected_location = self.entries["crc_LastLoadedPin"].get()
            
            # Handle special cases
            if selected_location == "-No Location Set-":
                pin_id = None  # Will remove the attribute
            elif selected_location.startswith("Unknown Location (ID: "):
                # User selected an unknown location - keep the existing ID
                pin_id = selected_location.split("ID: ")[1].rstrip(")")
            else:
                # Find the pin ID from the selected location name
                pin_id = None
                for id, name in self.last_loaded_pin_mappings.items():
                    if name == selected_location:
                        pin_id = id
                        break
            
            # Update the XML
            root = self.main_window.tree.getroot()
            player_profile = root.find("PlayerProfile")

            if player_profile is not None:
                # Update PlayerProfile element (this is where it should be)
                if pin_id is None:
                    # Remove the attribute entirely
                    if "crc_LastLoadedPin" in player_profile.attrib:
                        del player_profile.attrib["crc_LastLoadedPin"]
                    self.logger.debug("Removed crc_LastLoadedPin from PlayerProfile")
                else:
                    player_profile.set("crc_LastLoadedPin", pin_id)
                    self.logger.debug(f"Updated crc_LastLoadedPin in PlayerProfile to: {pin_id} ({selected_location})")
            else:
                self.logger.error("PlayerProfile element not found!")

            # Mark changes as unsaved
            self.main_window.unsaved_label.config(text="Unsaved Changes")
            
        except Exception as e:
            self.logger.error(f"Error in current location selection: {str(e)}")
            show_error("Error", f"Failed to change current location: {str(e)}")

    def _create_last_loaded_pin_mappings(self):
        """Create mappings for last loaded pin IDs to their location names"""
        self.last_loaded_pin_mappings = {
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
            "2169212369": "Dev Room: Animation Creatures",
            "3975313082": "Dev Room: Orouleau",
        }

    def _create_coordinate_mappings(self):
        """Create mappings for coordinates to location names"""
        self.coordinate_mappings = {
            # Main Story Locations
            (-43.4, 138.9): "Bioluminescent_forest",
            (12.3, 80.9): "Floating_Mountain", 
            (-1.1, 29.9): "Grotto_Banshee_Rookery",
            (50.8, -33.1): "Hometree",
            (38.0, 177.8): "Rainforest",
            (29.9, -132.4): "Hammerhead",
            (24.1, 131.4): "Unobtanium_Extraction_Site",
            (-26.5, 119.9): "Well_Of_Souls",
            
            # Flora/Fauna Locations
            (-20.0, 30.0): "Djamurtiias",
            (30.8, -7.5): "Lys",
            (-40.4, 35.9): "Osiceallya",
            (-35.9, -146.4): "Vamparak",
            (28.5, 29.2): "Tetrapteron",
            (-28.9, 24.1): "Woodsprite",
            (-10.2, 118.0): "Olonipedra",
            (-0.2, 39.5): "Phyalorpeus",
            (-17.1, 104.2): "Dragoliic",
            (16.0, -1.8): "Begonia",
            (-18.5, 136.9): "Anchusa",
            (63.2, 168.9): "Tropearockianna",
            (64.1, 71.2): "Danura",
            (2.9, 189.5): "Pelargonium",
            (-86.4, -184.1): "Icomopsis",
            (-20.7, -30.1): "Bfishes",
            (12.3, 123.9): "Sting",
            (36.0, 100.0): "Sturmbeast",
            (-33.4, 107.9): "Tapirus",
            (45.9, 1.4): "Fan",
            (0.0, 0.0): "Prolemuris",
            (65.9, 120.4): "Syall",
            (-37.8, 49.5): "Wyll",
            (65.6, -60.1): "Sool",
            (-75.3, -157.0): "Wall",
            (20.8, -67.0): "Lamarha",
            (6.4, 12.4): "Watefiuul",
            (-9.9, 176.4): "Atliammera",
            (-11.9, 17.1): "Neakavirus",
            (12.0, 166.4): "Auroria",
            (22.2, 64.2): "Occhioline",
            (60.1, -141.4): "Xyvliiuccus",
            (32.1, 70.9): "Wyvuur",
            (27.0, 110.0): "Cocclophile",
            (-12.4, -104.9): "Hyphallya",
            (70.2, -3.0): "Snjol",
            (-1.2, -1.9): "Catjjihal",
            (-52.2, 21.1): "Aloemajade",
            (-28.8, 41.8): "Prolemuris2",
            
            # Single Player Missions
            (16.0, 73.0): "SP_NeedleHills_RB_FM_01_L",
            (28.0, 95.0): "sp_dlc_01",
            (18.0, 88.0): "SP_DustBowl_HG_RB_01_L",
            (19.0, 73.0): "SP_Sebastien_HG_01_L",
            (29.0, 92.0): "SP_Sebastien_RB_02_L",
            (38.0, 172.0): "SP_VaderasHollow_RF_FM_01_L",
            (43.0, 158.0): "SP_PASCAL_FM_01",
            (26.0, 115.0): "SP_Nancy_OF_02_L",
            (53.0, 117.0): "SP_PlainsOfGoliath_OF_FM_01_L",
            (56.0, 117.0): "sp_drifting_sierra_fm_01_l",
            (12.0, -172.0): "SP_Pascal_RF03_L",
            (44.0, -137.0): "sp_bonusmap_01",
            (48.0, -167.0): "SP_Pascal_RF03_CORP_L",
            (-45.0, 135.0): "SP_PierreLuc_FM_02_L",
            (18.0, 166.0): "SP_Philippe_RF_RB_01",
            (46.0, 173.0): "SP_VerdantPinnacle_FM_01_L",
            (58.0, 154.0): "SP_CoualtHighlands_OF_RF_01_L",
            (58.0, 152.0): "SP_JeanNormand_DF_01",
            (32.0, 150.0): "SP_GravesBog_RB_OF_01_L",
            (51.0, -79.0): "SP_Hometree_L",
            (25.0, -125.0): "sp_pascal_rf04_l_E3",
            (30.0, -125.0): "sp_pascal_rf04_l",
            (27.0, -125.0): "demo_e3_tantalus_l1",
            (30.0, -145.0): "sp_blackperdition_rf_01_l",
            
            # Multiplayer Maps
            (13.0, 48.0): "mp_openfield_01",
            (16.0, 30.0): "mp_hellsgate_01",
            (23.5, 10.0): "mp_floatingmountains_01",
            (38.0, 53.0): "mp_ancientgrounds_01",
            (33.0, 67.0): "mp_vaderashollow_fm_01",
            (21.5, -50.0): "mp_dustbowl_rb_01",
            (32.0, -60.0): "mp_forsakencaldera_rf_01",
            (31.0, -83.0): "mp_kowevillage_fm_01",
            (34.0, -37.0): "mp_rainforest_01",
            (21.0, -35.0): "mp_fogswamp_rb_01",
            (58.0, -5.0): "mp_ps3map",
            (59.0, 155.0): "mp_brokencage_rf_01",
            (69.0, 155.0): "mp_gravesbog_rb_01",
            (79.0, 155.0): "mp_needlehills_rb_01",
            (19.0, 155.0): "mp_hometree",
            (40.0, 125.0): "mp_bluelagoon_rb_01",
            (50.0, 125.0): "mp_kowecave_fm_01",
            
            # Development/Test Maps
            (-45.0, 116.0): "Z_Anim_Creatures",
            (-40.0, 118.0): "pin_z_dev_orouleau",
            (-40.0, 18.0): "avatar_intro",
            (-47.0, 118.0): "pin_menu",
            (-36.0, 109.0): "Z_Anim_Moving",
            (-36.0, 80.0): "Z_NewGym",
            (-28.0, 107.0): "MP_Christian_RF_01",
            (-35.0, 116.0): "z_greenhouse",
            (-36.0, 130.0): "Gym_Misceleanous",
            (-99.0, 99.0): "z_hellsgate_01",
            (12.0, 30.0): "sp_Hellsgate_01",
            (-30.0, 110.0): "z_hometree_01",
            (-36.0, 150.0): "RiverBank_RenameTest",
            (-36.0, 105.0): "z_combatbalance_l",
            (-40.0, 113.0): "z_QuestGearTesting_L",
            (-28.0, 110.0): "z_Dev_GenericMissionBriefingHuman",
            (-28.0, 113.0): "z_Dev_GenericMissionBriefingNavi",
            (-35.0, 0.0): "gym_ai_multi",
            (15.0, -175.0): "coop_pascal_01_l",
            (-30.0, 116.0): "coop_pascal_02_l",
            (-35.0, 116.0): "sp_pascal_of_01_l",
            (-33.0, 133.0): "plaza_01",
            (-43.0, 143.0): "plaza_02"
        }

    def _find_location_name(self, latitude_str, longitude_str):
        """Find the location name for given coordinates with tolerance for floating point precision"""
        try:
            lat = float(latitude_str)
            lon = float(longitude_str)
            
            # First try exact match
            coord_key = (lat, lon)
            if coord_key in self.coordinate_mappings:
                return self.coordinate_mappings[coord_key]
            
            # If no exact match, try with tolerance for floating point precision
            tolerance = 0.1  # Adjust this if needed
            for (map_lat, map_lon), location_name in self.coordinate_mappings.items():
                if abs(lat - map_lat) <= tolerance and abs(lon - map_lon) <= tolerance:
                    return location_name
            
            # No match found
            return None
            
        except (ValueError, TypeError):
            return None

    def _format_location_display(self, location_value):
        """Format location for display with map name if found"""
        try:
            if not location_value or location_value == "0,0":
                return "0,0"
            
            # Parse the coordinates
            if "," in location_value:
                lat_str, lon_str = location_value.split(",", 1)
                lat_str = lat_str.strip()
                lon_str = lon_str.strip()
                
                # Find the location name
                location_name = self._find_location_name(lat_str, lon_str)
                
                if location_name:
                    return f"{location_value} ({location_name})"
                else:
                    return location_value
            else:
                return location_value
                
        except Exception as e:
            self.logger.error(f"Error formatting location display: {str(e)}")
            return location_value

    def create_rda_equipment_section(self, parent):
        """Create compact RDA equipment section"""
        # Main container
        rda_container = ttk.Frame(parent)
        rda_container.pack(fill=tk.BOTH, expand=True)
        
        # Compact action buttons with uniform width
        actions_frame = ttk.Frame(rda_container)
        actions_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Configure grid to distribute buttons evenly (3 columns)
        actions_frame.grid_columnconfigure(0, weight=1, uniform="buttons")
        actions_frame.grid_columnconfigure(1, weight=1, uniform="buttons")
        actions_frame.grid_columnconfigure(2, weight=1, uniform="buttons")

        # Row 1 - using grid for uniform sizing
        btn1 = ttk.Button(actions_frame, text="🔄 Reset Ammo")
        self._wrap_button_with_sound(btn1, self._reset_weapon_ammo)
        btn1.grid(row=0, column=0, sticky="ew", padx=(0, 2), pady=1)

        btn2 = ttk.Button(actions_frame, text="🗑️ Remove Duplicates")
        self._wrap_button_with_sound(btn2, self._remove_duplicate_items)
        btn2.grid(row=0, column=1, sticky="ew", padx=2, pady=1)

        btn3 = ttk.Button(actions_frame, text="📦 Add RDA DLC Items")
        self._wrap_button_with_sound(btn3, self._add_all_rda_dlc_items)
        btn3.grid(row=0, column=2, sticky="ew", padx=(2, 0), pady=1)

        # Row 2 - using grid for uniform sizing
        btn4 = ttk.Button(actions_frame, text="🛡️ Add All RDA Armor")
        self._wrap_button_with_sound(btn4, self._add_all_rda_armor)
        btn4.grid(row=1, column=0, sticky="ew", padx=(0, 2), pady=1)

        btn5 = ttk.Button(actions_frame, text="⚔️ Add All RDA Weapons")
        self._wrap_button_with_sound(btn5, self._add_all_rda_weapons)
        btn5.grid(row=1, column=1, sticky="ew", padx=2, pady=1)

        btn6 = ttk.Button(actions_frame, text="🎯 Add All RDA Skills")
        self._wrap_button_with_sound(btn6, self._add_all_rda_skills)
        btn6.grid(row=1, column=2, sticky="ew", padx=(2, 0), pady=1)

        # Create notebook (tabs) for equipment
        equipment_notebook = ttk.Notebook(rda_container)
        equipment_notebook.pack(fill=tk.BOTH, expand=True)

        # ADD HOVER SOUND TO RDA EQUIPMENT TABS (only once per tab)
        if not hasattr(self, '_rda_last_hovered_tab'):
            self._rda_last_hovered_tab = None

        def on_rda_tab_hover(event):
            """Play hover sound when mouse enters a NEW RDA equipment tab"""
            if self.sound_manager and hasattr(self.main_window.config, 'play_hover_sounds'):
                if self.main_window.config.play_hover_sounds:
                    try:
                        tab_id = equipment_notebook.identify(event.x, event.y)
                        if tab_id and tab_id != self._rda_last_hovered_tab:
                            self._rda_last_hovered_tab = tab_id
                            self.sound_manager.play_sound_effect('hover')
                        elif not tab_id:
                            self._rda_last_hovered_tab = None
                    except:
                        pass

        equipment_notebook.bind('<Motion>', on_rda_tab_hover)

        # Armor Tab
        armor_tab = ttk.Frame(equipment_notebook, padding=10)
        equipment_notebook.add(armor_tab, text="🛡️ Armor")
        self.create_compact_armor_section(armor_tab, is_navi=False)

        # Weapons Tab
        weapons_tab = ttk.Frame(equipment_notebook, padding=10)
        equipment_notebook.add(weapons_tab, text="⚔️ Weapons")
        self.create_compact_weapon_slots(weapons_tab, is_navi=False)

        # Skills Tab
        skills_tab = ttk.Frame(equipment_notebook, padding=10)
        equipment_notebook.add(skills_tab, text="🎯 Skills")
        self.create_compact_skill_slots(skills_tab, is_navi=False)

    def create_navi_equipment_section(self, parent):
        """Create compact Na'vi equipment section"""
        # Main container
        navi_container = ttk.Frame(parent)
        navi_container.pack(fill=tk.BOTH, expand=True)
        
        # Compact action buttons with uniform width
        actions_frame = ttk.Frame(navi_container)
        actions_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Configure grid to distribute buttons evenly (3 columns)
        actions_frame.grid_columnconfigure(0, weight=1, uniform="buttons")
        actions_frame.grid_columnconfigure(1, weight=1, uniform="buttons")
        actions_frame.grid_columnconfigure(2, weight=1, uniform="buttons")

        # Row 1 - using grid for uniform sizing
        btn1 = ttk.Button(actions_frame, text="🔄 Reset Ammo")
        self._wrap_button_with_sound(btn1, self._reset_weapon_ammo)
        btn1.grid(row=0, column=0, sticky="ew", padx=(0, 2), pady=1)

        btn2 = ttk.Button(actions_frame, text="🗑️ Remove Duplicates")
        self._wrap_button_with_sound(btn2, self._remove_duplicate_items)
        btn2.grid(row=0, column=1, sticky="ew", padx=2, pady=1)

        btn3 = ttk.Button(actions_frame, text="📦 Add Na'vi DLC Items")
        self._wrap_button_with_sound(btn3, self._add_all_navi_dlc_items)
        btn3.grid(row=0, column=2, sticky="ew", padx=(2, 0), pady=1)

        # Row 2 - using grid for uniform sizing
        btn4 = ttk.Button(actions_frame, text="🛡️ Add All Na'vi Armor")
        self._wrap_button_with_sound(btn4, self._add_all_navi_armor)
        btn4.grid(row=1, column=0, sticky="ew", padx=(0, 2), pady=1)

        btn5 = ttk.Button(actions_frame, text="🏹 Add All Na'vi Weapons")
        self._wrap_button_with_sound(btn5, self._add_all_navi_weapons)
        btn5.grid(row=1, column=1, sticky="ew", padx=2, pady=1)

        btn6 = ttk.Button(actions_frame, text="🎯 Add All Na'vi Skills")
        self._wrap_button_with_sound(btn6, self._add_all_navi_skills)
        btn6.grid(row=1, column=2, sticky="ew", padx=(2, 0), pady=1)

        # Create notebook (tabs) for equipment
        equipment_notebook = ttk.Notebook(navi_container)
        equipment_notebook.pack(fill=tk.BOTH, expand=True)

        # ADD HOVER SOUND TO NA'VI EQUIPMENT TABS (only once per tab)
        if not hasattr(self, '_navi_last_hovered_tab'):
            self._navi_last_hovered_tab = None

        def on_navi_tab_hover(event):
            """Play hover sound when mouse enters a NEW Na'vi equipment tab"""
            if self.sound_manager and hasattr(self.main_window.config, 'play_hover_sounds'):
                if self.main_window.config.play_hover_sounds:
                    try:
                        tab_id = equipment_notebook.identify(event.x, event.y)
                        if tab_id and tab_id != self._navi_last_hovered_tab:
                            self._navi_last_hovered_tab = tab_id
                            self.sound_manager.play_sound_effect('hover')
                        elif not tab_id:
                            self._navi_last_hovered_tab = None
                    except:
                        pass

        equipment_notebook.bind('<Motion>', on_navi_tab_hover)

        # Armor Tab
        armor_tab = ttk.Frame(equipment_notebook, padding=10)
        equipment_notebook.add(armor_tab, text="🛡️ Armor")
        self.create_compact_armor_section(armor_tab, is_navi=True)

        # Weapons Tab
        weapons_tab = ttk.Frame(equipment_notebook, padding=10)
        equipment_notebook.add(weapons_tab, text="🏹 Weapons")
        self.create_compact_weapon_slots(weapons_tab, is_navi=True)

        # Skills Tab
        skills_tab = ttk.Frame(equipment_notebook, padding=10)
        equipment_notebook.add(skills_tab, text="🎯 Skills")
        self.create_compact_skill_slots(skills_tab, is_navi=True)

    def create_compact_skill_slots(self, parent, is_navi=False):
        """Create compact skill slots with PNG previews"""
        skills_container = ttk.Frame(parent)
        skills_container.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        # Split into left (controls) and right (preview) sections
        left_section = ttk.Frame(skills_container)
        left_section.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_section = ttk.Frame(skills_container)
        right_section.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        skill_slots = ["Top Slot", "Right Slot", "Bottom Slot", "Left Slot"]
        slots_storage = self.navi_skill_slots if is_navi else self.rda_skill_slots
        skill_mappings = self.navi_skill_mappings if is_navi else self.rda_skill_mappings
        
        # Add spacer at the top to push skill boxes down
        ttk.Frame(left_section, height=50).pack(side=tk.TOP)
        
        for i, slot_name in enumerate(skill_slots):
            slot_frame = ttk.Frame(left_section)
            slot_frame.pack(fill=tk.X, pady=12)
            
            # Compact slot label
            ttk.Label(slot_frame, text=f"{slot_name}:", 
                    font=('Segoe UI', 9, 'bold'), width=12).pack(side=tk.LEFT, padx=(0, 8))
            
            # Get skills list
            skill_values = list(skill_mappings.values())
            skill_values.insert(0, "-Empty-")  # Add empty option at the beginning
            
            # Compact skill dropdown (BIGGER and LONGER like weapons)
            skill_combo = ttk.Combobox(slot_frame, values=skill_values, 
                                    width=40, state="readonly", font=('Segoe UI', 10), height=10)
            skill_combo.set("-Empty-")
            skill_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            block_combobox_mousewheel(skill_combo)
            self._add_hover_sound_to_combobox(skill_combo)
            
            # Store skill data
            slot_data = {
                "dropdown": skill_combo,
                "skill_mappings": skill_mappings
            }
            
            while len(slots_storage) <= i:
                slots_storage.append(None)
            slots_storage[i] = slot_data
            
            # Bind events
            if is_navi:
                skill_combo.bind('<<ComboboxSelected>>', lambda e, idx=i: self._on_navi_skill_selected(e, idx))
            else:
                skill_combo.bind('<<ComboboxSelected>>', lambda e, idx=i: self._on_rda_skill_selected(e, idx))
        
        # Create preview area on the right - COMPOSITE VIEW (same as weapons)
        right_section.grid_columnconfigure(0, weight=1)
        right_section.grid_rowconfigure(0, weight=1)
        
        # Single composite preview frame
        composite_frame = ttk.LabelFrame(right_section, text="Skill Preview", padding=5)
        composite_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Configure the frame to expand
        composite_frame.grid_columnconfigure(0, weight=1)
        composite_frame.grid_rowconfigure(0, weight=1)
        
        composite_label = ttk.Label(composite_frame, text="No Skills\nEquipped", 
                                    width=20, anchor="center", relief="sunken")
        composite_label.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Store the composite label
        if not hasattr(self, 'skill_composite_preview_labels'):
            self.skill_composite_preview_labels = {}
        faction_key = 'navi' if is_navi else 'rda'
        self.skill_composite_preview_labels[faction_key] = composite_label
        
        # Create hidden individual preview labels for internal tracking
        if not hasattr(self, 'skill_preview_labels'):
            self.skill_preview_labels = {}
        if faction_key not in self.skill_preview_labels:
            self.skill_preview_labels[faction_key] = {}
        
        for i in range(len(skill_slots)):
            # These labels won't be displayed but will hold the individual skill PNGs
            image_label = ttk.Label(composite_frame)  # Create but don't pack
            self.skill_preview_labels[faction_key][i] = image_label

    def _load_skill_image(self, skill_id, slot_index, is_navi=False):
        """Load skill PNG for a specific slot - prepares for composite rendering"""
        try:
            # Get the preview label for this slot
            faction_key = 'navi' if is_navi else 'rda'
            
            if not hasattr(self, 'skill_preview_labels') or faction_key not in self.skill_preview_labels:
                self.logger.warning(f"No skill preview labels found for {faction_key}")
                return
            
            if slot_index not in self.skill_preview_labels[faction_key]:
                self.logger.warning(f"No preview label found for slot {slot_index}")
                return
            
            image_label = self.skill_preview_labels[faction_key][slot_index]
            
            # Get skill name from ID
            skill_mappings = self.navi_skill_mappings if is_navi else self.rda_skill_mappings
            skill_name = skill_mappings.get(skill_id, f"Unknown Skill ({skill_id})")
            
            # Sanitize skill name for filename
            sanitized_name = skill_name.replace("/", "_")
            sanitized_name = sanitized_name.replace("'", "")
            sanitized_name = sanitized_name.replace(":", "")
            sanitized_name = sanitized_name.replace("ä", "a").replace("ì", "i")
            
            # Determine the correct faction folder
            faction_folder = "navi" if is_navi else "rda"
            
            # Try to find PNG in assets/skills/{faction}/ folder
            png_path = os.path.join("assets", "skills", faction_folder, f"{sanitized_name}.png")
            
            # Also try with skill ID as filename
            if not os.path.exists(png_path):
                png_path = os.path.join("assets", "skills", faction_folder, f"{skill_id}.png")
            
            if os.path.exists(png_path):
                # Load the PNG
                image = Image.open(png_path)
                # Resize to 100x100 for 2x2 grid
                image = image.resize((100, 100), Image.LANCZOS)
                
                # Ensure image has alpha channel for transparency
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                
                # Store the PIL Image on the label for later compositing
                if not hasattr(image_label, 'skill_image'):
                    image_label.skill_image = {}
                image_label.skill_image[slot_index] = image
                
                # Trigger composite rendering
                self._render_composite_skills(is_navi)
                
                self.logger.debug(f"Loaded skill PNG: {png_path}")
            else:
                # No PNG found - remove from composite
                if hasattr(image_label, 'skill_image') and slot_index in image_label.skill_image:
                    del image_label.skill_image[slot_index]
                self._render_composite_skills(is_navi)
                self.logger.debug(f"Skill PNG not found: {png_path}")
                
        except Exception as e:
            self.logger.error(f"Error loading skill PNG: {str(e)}", exc_info=True)

    def _render_composite_skills(self, is_navi=False):
        """Render composite skill image by positioning all 4 skills in a 2x2 grid"""
        try:
            from PIL import Image, ImageTk, ImageDraw, ImageFont
            
            faction_key = 'navi' if is_navi else 'rda'
            
            # Get composite preview label
            if not hasattr(self, 'skill_composite_preview_labels') or faction_key not in self.skill_composite_preview_labels:
                return
            
            composite_label = self.skill_composite_preview_labels[faction_key]
            
            # Get skill labels
            if not hasattr(self, 'skill_preview_labels') or faction_key not in self.skill_preview_labels:
                return
            
            skill_labels = self.skill_preview_labels[faction_key]
            
            # Check for any equipped skills
            has_any_skill = False
            for slot_idx in range(4):
                if slot_idx in skill_labels:
                    label = skill_labels[slot_idx]
                    if hasattr(label, 'skill_image') and slot_idx in label.skill_image:
                        has_any_skill = True
                        break
            
            # If no skills equipped → reset preview
            if not has_any_skill:
                composite_label.configure(image="")
                composite_label.configure(text="No Skills\nEquipped")
                return
            
            # === CREATE COMPOSITE IMAGE ===
            canvas_size = 300
            
            # Positions for 2x2 grid (matching weapon cross pattern spacing)
            positions = {
                0: (100, 0),    # Top
                1: (200, 100),  # Right
                2: (100, 200),  # Bottom
                3: (0, 100)     # Left
            }
            
            # Create composite background
            composite = Image.new('RGBA', (canvas_size, canvas_size), (30, 30, 30, 255))
            
            # Paste each skill image
            for slot_idx, (x, y) in positions.items():
                if slot_idx in skill_labels:
                    label = skill_labels[slot_idx]
                    if hasattr(label, 'skill_image') and slot_idx in label.skill_image:
                        skill_img = label.skill_image[slot_idx]
                        composite.paste(skill_img, (x, y), skill_img)
            
            # Draw slot labels
            draw = ImageDraw.Draw(composite)
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            slot_names = {0: "Top", 1: "Right", 2: "Bottom", 3: "Left"}
            
            for slot_idx, (x, y) in positions.items():
                if slot_idx in skill_labels:
                    label_obj = skill_labels[slot_idx]
                    if hasattr(label_obj, 'skill_image') and slot_idx in label_obj.skill_image:
                        text = slot_names[slot_idx]
                        bbox = draw.textbbox((0, 0), text, font=font)
                        text_w = bbox[2] - bbox[0]
                        text_h = bbox[3] - bbox[1]
                        
                        padding = 3
                        draw.rectangle(
                            [x, y, x + text_w + padding*2, y + text_h + padding*2],
                            fill=(0, 0, 0, 180)
                        )
                        draw.text((x + padding, y + padding), text, fill=(255, 255, 255), font=font)
            
            # Convert to Tk image and display
            photo = ImageTk.PhotoImage(composite)
            composite_label.configure(image=photo)
            composite_label.image = photo  # Keep reference
            composite_label.configure(text="")

        except Exception as e:
            self.logger.error(f"Error rendering composite skills: {str(e)}", exc_info=True)

    def _load_rda_skills(self, profile):
        """Load RDA skills from the save file"""
        soldier = profile.find("Possessions_Soldier")
        if soldier is None:
            return
        
        skills = soldier.find("Skills")
        if skills is None:
            return
        
        slots = skills.findall("Slot")
        for i, slot in enumerate(slots):
            if i < len(self.rda_skill_slots):
                skill_id = slot.get("crc_Value", "0")
                
                if skill_id == "0":
                    # Empty slot
                    self.rda_skill_slots[i]["dropdown"].set("-Empty-")
                elif skill_id in self.rda_skill_mappings:
                    # Known skill - show name
                    skill_name = self.rda_skill_mappings[skill_id]
                    self.rda_skill_slots[i]["dropdown"].set(skill_name)
                    # Load skill image
                    self._load_skill_image(skill_id, i, is_navi=False)
                else:
                    # Unknown skill - show ID
                    dropdown = self.rda_skill_slots[i]["dropdown"]
                    current_values = list(dropdown['values'])
                    id_display = f"Unknown Skill (ID: {skill_id})"
                    
                    # Add the unknown skill to the dropdown values if not already there
                    if id_display not in current_values:
                        current_values.append(id_display)
                        dropdown['values'] = current_values
                    
                    dropdown.set(id_display)

    def _load_navi_skills(self, profile):
        """Load Na'vi skills from the save file"""
        avatar = profile.find("Possessions_Avatar")
        if avatar is None:
            return
        
        skills = avatar.find("Skills")
        if skills is None:
            return
        
        slots = skills.findall("Slot")
        for i, slot in enumerate(slots):
            if i < len(self.navi_skill_slots):
                skill_id = slot.get("crc_Value", "0")
                
                if skill_id == "0":
                    # Empty slot
                    self.navi_skill_slots[i]["dropdown"].set("-Empty-")
                elif skill_id in self.navi_skill_mappings:
                    # Known skill - show name
                    skill_name = self.navi_skill_mappings[skill_id]
                    self.navi_skill_slots[i]["dropdown"].set(skill_name)
                    # Load skill image
                    self._load_skill_image(skill_id, i, is_navi=True)
                else:
                    # Unknown skill - show ID
                    dropdown = self.navi_skill_slots[i]["dropdown"]
                    current_values = list(dropdown['values'])
                    id_display = f"Unknown Skill (ID: {skill_id})"
                    
                    # Add the unknown skill to the dropdown values if not already there
                    if id_display not in current_values:
                        current_values.append(id_display)
                        dropdown['values'] = current_values
                    
                    dropdown.set(id_display)

    def _on_rda_skill_selected(self, event, slot_index):
        """Handle RDA skill selection"""
        if self.main_window.tree is None:
            show_error("Error", "No save file loaded. Please load a save file first.")
            event.widget.set("-Empty-")
            return
            
        combo = event.widget
        selected_skill = combo.get()
        
        if selected_skill == "-Empty-":
            # Clear this skill from composite
            faction_key = 'rda'
            if hasattr(self, 'skill_preview_labels') and faction_key in self.skill_preview_labels:
                if slot_index in self.skill_preview_labels[faction_key]:
                    label = self.skill_preview_labels[faction_key][slot_index]
                    if hasattr(label, 'skill_image') and slot_index in label.skill_image:
                        del label.skill_image[slot_index]
            # Re-render composite without this skill
            self._render_composite_skills(is_navi=False)
            self._update_skill_slot(slot_index, None, is_navi=False)
            return
        
        # Check if it's an unknown skill ID display
        if selected_skill.startswith("Unknown Skill (ID: "):
            # Extract the ID from the display text
            skill_id = selected_skill.split("ID: ")[1].rstrip(")")
        else:
            # Find the skill ID from the selected skill name
            skill_id = None
            for id, name in self.rda_skill_mappings.items():
                if name == selected_skill:
                    skill_id = id
                    break
        
        if skill_id:
            # Load skill image
            self._load_skill_image(skill_id, slot_index, is_navi=False)
            # Update XML
            self._update_skill_slot(slot_index, skill_id, is_navi=False)
            self.main_window.unsaved_label.config(text="Unsaved Changes")

    def _on_navi_skill_selected(self, event, slot_index):
        """Handle Na'vi skill selection"""
        if self.main_window.tree is None:
            show_error("Error", "No save file loaded. Please load a save file first.")
            event.widget.set("-Empty-")
            return
            
        combo = event.widget
        selected_skill = combo.get()
        
        if selected_skill == "-Empty-":
            # Clear this skill from composite
            faction_key = 'navi'
            if hasattr(self, 'skill_preview_labels') and faction_key in self.skill_preview_labels:
                if slot_index in self.skill_preview_labels[faction_key]:
                    label = self.skill_preview_labels[faction_key][slot_index]
                    if hasattr(label, 'skill_image') and slot_index in label.skill_image:
                        del label.skill_image[slot_index]
            # Re-render composite without this skill
            self._render_composite_skills(is_navi=True)
            self._update_skill_slot(slot_index, None, is_navi=True)
            return
        
        # Check if it's an unknown skill ID display
        if selected_skill.startswith("Unknown Skill (ID: "):
            # Extract the ID from the display text
            skill_id = selected_skill.split("ID: ")[1].rstrip(")")
        else:
            # Find the skill ID from the selected skill name
            skill_id = None
            for id, name in self.navi_skill_mappings.items():
                if name == selected_skill:
                    skill_id = id
                    break
        
        if skill_id:
            # Load skill image
            self._load_skill_image(skill_id, slot_index, is_navi=True)
            # Update XML
            self._update_skill_slot(slot_index, skill_id, is_navi=True)
            self.main_window.unsaved_label.config(text="Unsaved Changes")

    def _update_skill_slot(self, slot_index, skill_id, is_navi=False):
        """Update a skill slot in the XML"""
        try:
            profile = self.main_window.tree.getroot().find("PlayerProfile")
            if profile is None:
                return False
            
            # Find the appropriate possessions element
            faction_elem_name = "Possessions_Avatar" if is_navi else "Possessions_Soldier"
            faction_elem = profile.find(faction_elem_name)
            if faction_elem is None:
                faction_elem = ET.SubElement(profile, faction_elem_name)
            
            # Find or create Skills element
            skills_elem = faction_elem.find("Skills")
            if skills_elem is None:
                skills_elem = ET.SubElement(faction_elem, "Skills")
            
            # Find or create the specific slot
            slots = skills_elem.findall("Slot")
            
            # Ensure we have enough slots
            while len(slots) <= slot_index:
                new_slot = ET.SubElement(skills_elem, "Slot")
                new_slot.set("Index", str(len(slots)))
                new_slot.set("crc_Value", "0")  # Default empty value
                slots = skills_elem.findall("Slot")
            
            # Update the slot
            target_slot = slots[slot_index]
            if skill_id is None:
                target_slot.set("crc_Value", "0")  # Empty slot
            else:
                target_slot.set("crc_Value", skill_id)

            faction_name = "Na'vi" if is_navi else "RDA"
            self.logger.debug(f"Updated {faction_name} skill slot {slot_index} to {skill_id}")          

            return True
            
        except Exception as e:
            self.logger.error(f"Error updating skill slot: {str(e)}")
            return False

    def _create_skill_mappings(self):
        """Create mappings for skill IDs to their actual names, organized by category"""
        
        # ===== RDA SKILLS =====
        
        # RDA Combat Enhancement
        rda_combat_enhancement = {
            "1959749094": "Elite Training I",
            "3989189724": "Elite Training II",
            "2596340938": "Elite Training III",
            "77959529": "Elite Training IV",
            "1125225940": "Berserk I",
            "3659056238": "Berserk II",
            "2904552696": "Berserk III",
            "863723867": "Berserk IV",
            "2193097390": "Tactical Strike I",
            "464605972": "Tactical Strike II",
            "1823892354": "Tactical Strike III",
            "4073911841": "Tactical Strike IV",
        }
        
        # RDA Defensive/Support
        rda_defensive = {
            "2815647090": "Zeta Field I",
            "1054477512": "Zeta Field II",
            "1239235678": "Zeta Field III",
            "3619269117": "Zeta Field IV",
            "527383063": "Genetic Regenerator I",
            "2254859181": "Genetic Regenerator II",
            "4049689403": "Genetic Regenerator III",
            "1862651544": "Genetic Regenerator IV",
            "3043422876": "Chromatic Blend I",
            "745513766": "Chromatic Blend II",
            "1533580208": "Chromatic Blend III",
            "3305899539": "Chromatic Blend IV",
        }
        
        # RDA Mobility/Utility
        rda_mobility = {
            "1719323144": "Ultrasonic Repulsor I",
            "4285766578": "Ultrasonic Repulsor II",
            "2289347364": "Ultrasonic Repulsor III",
            "370163335": "Ultrasonic Repulsor IV",
            "3737562477": "Sacrifice Grade I",
            "1204813015": "Sacrifice Grade II",
            "818465857": "Sacrifice Grade III",
            "2930530786": "Sacrifice Grade IV",
        }
        
        # RDA Vehicle Spawns
        rda_vehicles = {
            "339641018": "Samson Vehicle Spawn",
            "2857450382": "Boat Vehicle Spawn",
            "3179152460": "Scorpion Vehicle Spawn",
            "767629789": "AMP Suit Vehicle Spawn",
            "3713403672": "ATV Vehicle Spawn",
            "1399874912": "Dragon Vehicle Spawn",
            "1522936139": "Dove Vehicle Spawn",
            "861432372": "Buggy Vehicle Spawn",
            "4135278811": "Miles Quaritch Spawn",
            "": "Miles Quaritch Spawn",
            "": " Spawn",
            "": " Spawn",
            "": " Spawn",
        }
        
        # ===== NA'VI SKILLS =====
        
        # Na'vi Combat
        navi_combat = {
            "4047834971": "Titan's Bash I",
            "1749835489": "Titan's Bash II",
            "525037175": "Titan's Bash III",
            "2167405524": "Titan's Bash IV",
            "2953989487": "Swarm's Wrath I",
            "689642709": "Swarm's Wrath II",
            "1578904643": "Swarm's Wrath III",
            "3229137376": "Swarm's Wrath IV",
            "3819761146": "Whirl of Fury I",
            "2057681984": "Whirl of Fury II",
            "228756694": "Whirl of Fury III",
            "2479233397": "Whirl of Fury IV",
        }
        
        # Na'vi Support/Healing
        navi_support = {
            "2278341981": "Pandora's Union I",
            "516287719": "Pandora's Union II",
            "1774378097": "Pandora's Union III",
            "4154870226": "Pandora's Union IV",
            "1711548883": "Eywa's Breath I",
            "4279072873": "Eywa's Breath II",
            "2282375423": "Eywa's Breath III",
            "376364380": "Eywa's Breath IV",
        }
        
        # Na'vi Defensive
        navi_defensive = {
            "2507739827": "Pandora's Protection I",
            "208683785": "Pandora's Protection II",
            "2071425951": "Pandora's Protection III",
            "3843286588": "Pandora's Protection IV",
            "1411228025": "Beast's Aegis I",
            "3440701635": "Beast's Aegis II",
            "3121856597": "Beast's Aegis III",
            "611800566": "Beast's Aegis IV",
        }
        
        # Na'vi Mobility
        navi_mobility = {
            "4044964372": "Kinetic Dash I",
            "1745884078": "Kinetic Dash II",
            "521610040": "Kinetic Dash III",
            "2171844251": "Kinetic Dash IV",
        }
        
        # Na'vi Mount Spawns
        navi_mounts = {
            "1147099810": "Direhorse Mount Spawn",
            "2906455959": "Leonopteryx Mount Spawn",
            "3661352705": "Banshee Mount Spawn",
            "875933229": "Elite Axe Bodyguard Spawn",
            "1127390907": "Elite Dual Blades Bodyguard Spawn",
            "3549266730": "Elite Fighting Staff Bodyguard Spawn",
            "2760553404": "Grace Augustine's Avatar Spawn",
        }
        
        # # ===== GAME MECHANICS & EFFECTS =====
        
        # # Special Effects
        # special_effects = {
        #     "4221139584": "Effect_ScaledFire_020",
        #     "1588994160": "Effect_ScaledFire_060",
        #     "154070465": "Effect_ScaledFire_100",
        #     "3919303244": "Effect_SlingDart_Overtime",
        #     "929187032": "SolsDelight_Blind",
        #     "482995089": "Leucomelas_Blind",
        #     "2831657996": "Root10sec",
        #     "3149590643": "Poison_cloud",
        #     "1761588079": "HellfireWasp_slow",
        # }
        
        # # Protection Effects
        # protection_effects = {
        #     "707441961": "Hammerhead_Invulnerable",
        #     "2901239959": "MP_CorpRespawnInvulnerability",
        #     "2149792658": "MP_NaviRespawnInvulnerability",
        #     "2120156884": "MP_CorpShield",
        #     "896499985": "MP_NaviShield",
        # }
        
        # # Multiplayer Zones
        # mp_zones = {
        #     "2288728861": "MP_HillOfProtection_C",
        #     "4172838722": "MP_HillOfPower_C",
        #     "2248739839": "MP_HillOfPower_N",
        #     "4141500320": "MP_HillOfProtection_N",
        #     "3605504349": "MP_HillOfRejuvenation_C",
        #     "2824265184": "MP_HillOfRejuvenation_N",
        # }
        
        # # Multiplayer Effects
        # mp_effects = {
        #     "699117554": "MP_NAVI_Effect_MythicArchery",
        #     "3130830861": "MP_CORP_Effect_ArmorPiercing",
        # }
        
        # # Environmental Effects
        # environmental_effects = {
        #     "1987225269": "OxygenPod_Fear",
        #     "1774875854": "Amp_JumpFear",
        # }
        
        # # ===== AI & CREATURES =====
        
        # # Enemy AI
        # enemy_skills = {
        #     "1298333286": "EnemyCSS_3A_1",
        #     "3072205389": "EnemyNPG_2A_4",
        #     "1147345197": "EnemyNME_3A_4",
        #     "2779483555": "EnemyNPG_1A_4",
        #     "1887679822": "Enemy_NWM_2A",
        #     "651760328": "Enemy_NWM_4A",
        #     "3548279530": "EnemyNBD_1A_4",
        # }
        
        # # Creature Skills
        # creature_skills = {
        #     "138960729": "Enemy_Viperwolf_EliteWasp",
        #     "1849804230": "Alpha_Viperwolf",
        #     "1785634812": "Viperwolf_Berzerk",
        #     "3490889542": "Viperwolf_Heal_LVL9_13",
        #     "62547143": "Viperwolf_Heal_LVL1_4",
        #     "218464304": "Viperwolf_Heal_LVL5_8",
        #     "1745871194": "Viperwolf_Camouflage",
        #     "3305111690": "Viperwolf_Bite",
        #     "1533394898": "Enemy_Summon_BlackViperwolf",
        #     "895550929": "Enemy_Summon_Viperwolf_Galactonotus",
        #     "480060929": "Hexapede",
        # }
        
        # # Boss Skills
        # boss_skills = {
        #     "1906639931": "Hammerhead_Lvl5To8_AttackWarning",
        #     "771604749": "Hammerhead_Lvl9To13_AttackWarning",
        #     "2932769824": "Hammerhead_Lvl5To8_AttackWarning_LowHealth",
        #     "1073248985": "Hammerhead_Lvl1To4_AttackWarning",
        #     "1539660776": "Hammerhead_Lvl9To13_AttackWarning_LowHealth",
        #     "2122270851": "ScarerShockWave",
        # }
        
        # # Unknown Skills
        # unknown_skills = {
        #     "4221139584": "RDA Skill 4221139584",
        #     "3396941018": "RDA Skill 3396941018",
        # }
        
        # ===== COMBINE INTO MASTER DICTIONARIES =====
        
        # RDA Master Dictionary
        self.rda_skill_mappings = {
            **rda_combat_enhancement,
            **rda_defensive,
            **rda_mobility,
            **rda_vehicles,
            # **special_effects,
            # **protection_effects,
            # **mp_zones,
            # **mp_effects,
            # **environmental_effects,
            # **enemy_skills,
            # **creature_skills,
            # **boss_skills,
            # **unknown_skills,
        }
        
        # Na'vi Master Dictionary
        self.navi_skill_mappings = {
            **navi_combat,
            **navi_support,
            **navi_defensive,
            **navi_mobility,
            **navi_mounts,
            # **special_effects,
            # **protection_effects,
            # **mp_zones,
            # **mp_effects,
            # **environmental_effects,
            # **enemy_skills,
            # **creature_skills,
            # **boss_skills,
            # **unknown_skills,
        }
        
        # Store category mappings for reference
        self.skill_categories = {
            "rda_combat_enhancement": rda_combat_enhancement,
            "rda_defensive": rda_defensive,
            "rda_mobility": rda_mobility,
            "rda_vehicles": rda_vehicles,
            "navi_combat": navi_combat,
            "navi_support": navi_support,
            "navi_defensive": navi_defensive,
            "navi_mobility": navi_mobility,
            "navi_mounts": navi_mounts,
            # "special_effects": special_effects,
            # "protection_effects": protection_effects,
            # "mp_zones": mp_zones,
            # "mp_effects": mp_effects,
            # "environmental_effects": environmental_effects,
            # "enemy_skills": enemy_skills,
            # "creature_skills": creature_skills,
            # "boss_skills": boss_skills,
            # "unknown_skills": unknown_skills,
        }

    def create_compact_field_item(self, parent, label, key, options=None, readonly=False):
        """Create a compact field item"""
        field_frame = ttk.Frame(parent)
        field_frame.pack(fill=tk.X, pady=3)
        
        # Label (smaller font)
        ttk.Label(field_frame, text=f"{label}:", font=('Segoe UI', 8, 'bold')).pack(anchor=tk.W)
        
        # Input widget (smaller)
        if readonly:
            # Read-only label
            widget = ttk.Label(field_frame, text="-", font=('Segoe UI', 8),
                            background='#2c2c2c', relief='sunken', padding=(3, 1))
            widget.pack(fill=tk.X, pady=(1, 0))
            
            if key == "face":
                widget.bind('<Button-1>', lambda e: self._on_face_selected())
        elif options:
            # Combobox with options
            widget = ttk.Combobox(field_frame, values=list(options.values()), 
                                state="readonly", font=('Segoe UI', 8), height=4)
            widget.pack(fill=tk.X, pady=(1, 0))
            block_combobox_mousewheel(widget)
            self._add_hover_sound_to_combobox(widget)
            
            # Add specific event bindings
            if key == "PlayerFaction":
                widget.bind('<<ComboboxSelected>>', self._on_faction_selected)
            elif key == "crc_LastLoadedPin":
                widget.bind('<<ComboboxSelected>>', self._on_current_location_selected)
            elif key in ["side", "pawn", "bEntityScanningEnabled", "FirstPersonMode", "RumbleEnabled"]:
                widget.bind('<<ComboboxSelected>>', self._mark_unsaved_changes)
                
                if key == "pawn":
                    def pawn_changed_update_face(event):
                        self._on_face_selected()
                        return None
                    widget.bind('<<ComboboxSelected>>', pawn_changed_update_face, add='+')
        else:
            # Regular entry
            widget = ttk.Entry(field_frame, font=('Segoe UI', 8))
            widget.pack(fill=tk.X, pady=(1, 0))
            
            # Add validation for RecoveryBits
            if key == "RecoveryBits":
                def validate_recovery_bits(event):
                    try:
                        value = widget.get()
                        if value:
                            int_value = int(value)
                            if int_value > 500:
                                widget.delete(0, tk.END)
                                widget.insert(0, "500")
                                show_warning("Value Capped", "Recovery Bits cannot exceed 500.")
                            elif int_value < 0:
                                widget.delete(0, tk.END)
                                widget.insert(0, "0")
                    except ValueError:
                        pass
                
                widget.bind('<FocusOut>', validate_recovery_bits)
                widget.bind('<Return>', validate_recovery_bits)
        
        # Store widget reference
        self.entries[key] = widget
        
        # Add change tracking for all editable widgets
        if not readonly and hasattr(widget, 'bind'):
            widget.bind('<KeyRelease>', self._mark_unsaved_changes)
            if hasattr(widget, 'current'):
                if key not in ["PlayerFaction", "crc_LastLoadedPin", "side", "pawn", "bEntityScanningEnabled", "FirstPersonMode", "RumbleEnabled"]:
                    widget.bind('<<ComboboxSelected>>', self._mark_unsaved_changes)

        # Enforce 10-character limit on the character name entry
        if key == "namevec" and not readonly:
            def _enforce_name_limit(event, w=widget):
                if len(w.get()) > 10:
                    w.delete(10, tk.END)
            widget.bind('<KeyRelease>', _enforce_name_limit, add='+')

    def create_compact_weapon_slots(self, parent, is_navi=False):
        """Create compact weapon slots with controls on left, single composite preview on right"""
        weapons_container = ttk.Frame(parent)
        weapons_container.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        # Split into two main sections
        left_section = ttk.Frame(weapons_container)
        left_section.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_section = ttk.Frame(weapons_container)
        right_section.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        weapon_slots = ["Top", "Right", "Down", "Left"]
        
        slots_storage = self.navi_weapon_slots if is_navi else self.weapon_slots
        
        # Get weapons list
        all_weapons = self._get_faction_weapons(is_navi)
        
        # Create single composite preview box on the right - SAME AS ARMOR
        right_section.grid_columnconfigure(0, weight=1)
        right_section.grid_rowconfigure(0, weight=1)
        
        # Single weapon preview frame - BIGGER
        weapon_preview_frame = ttk.LabelFrame(right_section, text="Weapon Preview", padding=5)
        weapon_preview_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Configure the frame to expand
        weapon_preview_frame.grid_columnconfigure(0, weight=1)
        weapon_preview_frame.grid_rowconfigure(0, weight=1)
        
        weapon_preview_label = ttk.Label(weapon_preview_frame, text="No Weapons\nEquipped", 
                                    width=20, anchor="center", relief="sunken")
        weapon_preview_label.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Store the composite preview label
        if not hasattr(self, 'weapon_composite_preview_labels'):
            self.weapon_composite_preview_labels = {}
        faction_key = 'navi' if is_navi else 'rda'
        self.weapon_composite_preview_labels[faction_key] = weapon_preview_label
        
        # Create hidden individual preview labels for internal tracking (like armor does)
        if not hasattr(self, 'weapon_preview_labels'):
            self.weapon_preview_labels = {}
        if faction_key not in self.weapon_preview_labels:
            self.weapon_preview_labels[faction_key] = {}
        
        for i in range(len(weapon_slots)):
            # These labels won't be displayed but will hold the individual weapon GIFs
            image_label = ttk.Label(weapon_preview_frame)  # Create but don't pack
            self.weapon_preview_labels[faction_key][i] = image_label
        
        # Add spacer at the top to push weapon boxes down
        ttk.Frame(left_section, height=20).pack(side=tk.TOP)
        
        # Now create compact controls on the left
        for i, slot_name in enumerate(weapon_slots):
            # Compact control frame
            control_frame = ttk.Frame(left_section)
            control_frame.pack(fill=tk.X, pady=12)
            
            # Slot label
            ttk.Label(control_frame, text=f"{slot_name}:", font=('Segoe UI', 9, 'bold'), width=6).pack(side=tk.LEFT, padx=(0, 8))
            
            # Weapon dropdown
            weapon_combo = ttk.Combobox(control_frame, values=list(all_weapons.values()), 
                                    state="readonly", font=('Segoe UI', 10), width=40, height=10)
            weapon_combo.set("-Empty-")
            weapon_combo.pack(side=tk.LEFT, padx=(0, 8))
            block_combobox_mousewheel(weapon_combo)
            self._add_hover_sound_to_combobox(weapon_combo)
            
            # Compact ammo controls
            ammo_container = ttk.Frame(control_frame)
            ammo_container.pack(side=tk.LEFT)
            
            ttk.Label(ammo_container, text="Ammo:", font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=(0, 3))
            ammo_entry = ttk.Entry(ammo_container, width=6, font=('Segoe UI', 9))
            ammo_entry.insert(0, "0")
            ammo_entry.pack(side=tk.LEFT, padx=(0, 3))
            
            infinite_var = tk.BooleanVar()
            infinite_check = ttk.Checkbutton(ammo_container, text="∞", variable=infinite_var)
            infinite_check.pack(side=tk.LEFT, padx=(0, 8))
            
            ttk.Label(ammo_container, text="Clip:", font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=(0, 3))
            clip_label = ttk.Label(ammo_container, text="0", font=('Segoe UI', 9), width=4)
            clip_label.pack(side=tk.LEFT)
            
            # Store slot data
            slot_data = {
                "dropdown": weapon_combo,
                "ammo_entry": ammo_entry,
                "clip_entry": clip_label,
                "infinite_var": infinite_var,
                "infinite_check": infinite_check,
                "all_weapons": all_weapons,
                "slot_name": slot_name
            }
            
            while len(slots_storage) <= i:
                slots_storage.append(None)
            slots_storage[i] = slot_data
            
            # Bind events
            if is_navi:
                weapon_combo.bind('<<ComboboxSelected>>', lambda e, idx=i: self._on_navi_weapon_selected(e, idx))
            else:
                weapon_combo.bind('<<ComboboxSelected>>', lambda e, idx=i: self._on_weapon_selected(e, idx))
            
            infinite_check.bind('<ButtonRelease-1>', lambda e, idx=i, navi=is_navi: self._toggle_infinite_ammo(e, idx, navi))
            ammo_entry.bind('<KeyRelease>', lambda e, idx=i, navi=is_navi: self._update_ammo_value(e, idx, navi))

    def _load_weapon_image(self, weapon_id, slot_index, is_navi=False):
        """Load weapon PNG for a specific slot - prepares for composite rendering"""
        try:
            # Get the preview label for this slot
            faction_key = 'navi' if is_navi else 'rda'
            
            if not hasattr(self, 'weapon_preview_labels') or faction_key not in self.weapon_preview_labels:
                self.logger.warning(f"No weapon preview labels found for {faction_key}")
                return
            
            if slot_index not in self.weapon_preview_labels[faction_key]:
                self.logger.warning(f"No preview label found for slot {slot_index}")
                return
            
            image_label = self.weapon_preview_labels[faction_key][slot_index]
            
            # Get weapon name from ID
            weapon_name = self._get_item_name(weapon_id)
            
            # Sanitize weapon name for filename
            sanitized_name = weapon_name.replace("/", "_")
            sanitized_name = sanitized_name.replace("'", "")
            sanitized_name = sanitized_name.replace(":", "")
            sanitized_name = sanitized_name.replace("ä", "a").replace("ì", "i")
            
            # Try to find PNG in assets/weapons/ folder
            png_path = os.path.join("assets", "weapons", f"{sanitized_name}.png")
            
            if not os.path.exists(png_path):
                png_path = os.path.join("assets", "weapons", f"{weapon_id}.png")
            
            if os.path.exists(png_path):
                # Load the PNG
                image = Image.open(png_path)
                # Resize to 100x100 for 3x3 grid
                image = image.resize((100, 100), Image.LANCZOS)
                
                # Ensure image has alpha channel for transparency
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                
                # Store the PIL Image on the label for later compositing
                if not hasattr(image_label, 'weapon_image'):
                    image_label.weapon_image = {}
                image_label.weapon_image[slot_index] = image
                
                # Trigger composite rendering WITHOUT force regeneration
                self._render_composite_weapons(is_navi, force_regenerate=False)
                
                self.logger.debug(f"Loaded weapon PNG: {png_path}")
            else:
                # No PNG found - remove from composite
                if hasattr(image_label, 'weapon_image') and slot_index in image_label.weapon_image:
                    del image_label.weapon_image[slot_index]
                self._render_composite_weapons(is_navi, force_regenerate=False)
                self.logger.debug(f"Weapon PNG not found: {png_path}")
                
        except Exception as e:
            self.logger.error(f"Error loading weapon PNG: {str(e)}", exc_info=True)

    def _render_composite_weapons(self, is_navi=False, force_regenerate=False):
        """Render composite weapon image by positioning all 4 weapons in a 3x3 cross pattern"""
        try:
            from PIL import Image, ImageTk, ImageDraw, ImageFont
            
            faction_key = 'navi' if is_navi else 'rda'
            
            # Get composite preview label
            if not hasattr(self, 'weapon_composite_preview_labels') or faction_key not in self.weapon_composite_preview_labels:
                return
            
            composite_label = self.weapon_composite_preview_labels[faction_key]
            
            # Get weapon labels
            if not hasattr(self, 'weapon_preview_labels') or faction_key not in self.weapon_preview_labels:
                return
            
            weapon_labels = self.weapon_preview_labels[faction_key]
            
            # Check for any equipped weapons
            has_any_weapon = False
            for slot_idx in range(4):
                if slot_idx in weapon_labels:
                    label = weapon_labels[slot_idx]
                    if hasattr(label, 'weapon_image') and slot_idx in label.weapon_image:
                        has_any_weapon = True
                        break
            
            # If no weapons equipped → reset preview
            if not has_any_weapon:
                composite_label.configure(image="")
                composite_label.configure(text="No Weapons\nEquipped")
                return
            
            # === CREATE COMPOSITE IMAGE ===
            canvas_size = 300
            
            # Positions: display slot 0=Top, 1=Right, 2=Down, 3=Left
            positions = {
                0: (100, 0),    # Top
                1: (200, 100),  # Right
                2: (100, 200),  # Down
                3: (0, 100)     # Left
            }
            
            # Create composite background
            composite = Image.new('RGBA', (canvas_size, canvas_size), (30, 30, 30, 255))
            
            # Paste each weapon image
            for slot_idx, (x, y) in positions.items():
                if slot_idx in weapon_labels:
                    label = weapon_labels[slot_idx]
                    if hasattr(label, 'weapon_image') and slot_idx in label.weapon_image:
                        weapon_img = label.weapon_image[slot_idx]
                        composite.paste(weapon_img, (x, y), weapon_img)
            
            # Draw slot labels
            draw = ImageDraw.Draw(composite)
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            slot_names = {0: "Top", 1: "Right", 2: "Down", 3: "Left"}
            
            for slot_idx, (x, y) in positions.items():
                if slot_idx in weapon_labels:
                    label_obj = weapon_labels[slot_idx]
                    if hasattr(label_obj, 'weapon_image') and slot_idx in label_obj.weapon_image:
                        text = slot_names[slot_idx]
                        bbox = draw.textbbox((0, 0), text, font=font)
                        text_w = bbox[2] - bbox[0]
                        text_h = bbox[3] - bbox[1]
                        
                        padding = 3
                        draw.rectangle(
                            [x, y, x + text_w + padding*2, y + text_h + padding*2],
                            fill=(0, 0, 0, 180)
                        )
                        draw.text((x + padding, y + padding), text, fill=(255, 255, 255), font=font)
            
            # Convert to Tk image and display
            photo = ImageTk.PhotoImage(composite)
            composite_label.configure(image=photo)
            composite_label.image = photo  # Keep reference
            composite_label.configure(text="")

        except Exception as e:
            self.logger.error(f"Error rendering composite weapons: {str(e)}", exc_info=True)

    def _animate_composite_weapons(self, label):
        """
        Animate composite weapon display by cycling through frames.
        Prevents runaway animation loops by canceling older .after() timers.
        """

        # If an animation loop is already running, cancel it before starting a new one.
        if hasattr(label, "_after_id") and label._after_id:
            try:
                label.after_cancel(label._after_id)
            except Exception:
                pass  # safe to ignore if ID is invalid
            label._after_id = None

        # Safety check – no frames to animate
        if not hasattr(label, 'composite_frames') or not label.composite_frames:
            return

        # Animation function
        def update_frame():
            try:
                # Ensure composite_frames still exists
                if not hasattr(label, 'composite_frames') or not label.composite_frames:
                    return

                # Update the frame
                label.configure(image=label.composite_frames[label.frame_index])
                label.frame_index = (label.frame_index + 1) % len(label.composite_frames)

                # Schedule next frame and store timer ID
                label._after_id = label.after(50, update_frame)

            except Exception as e:
                self.logger.error(f"Error animating composite weapons: {str(e)}", exc_info=True)

        # Start animation
        update_frame()

    def _get_current_gender(self):
        """Get the current character's gender from the save file"""
        try:
            # First try to get from the UI entries (if already loaded)
            if "isfemale" in self.entries:
                gender_widget = self.entries["isfemale"]
                gender_text = gender_widget.cget("text") if hasattr(gender_widget, 'cget') else gender_widget.get()
                
                if gender_text == "Female":
                    self.logger.debug("Gender from UI: female")
                    return "female"
                elif gender_text == "Male":
                    self.logger.debug("Gender from UI: male")
                    return "male"
            
            # Fallback: read directly from XML if UI not loaded yet
            if self.main_window.tree is not None:
                root = self.main_window.tree.getroot()
                profile = root.find("PlayerProfile")
                
                if profile is not None:
                    base_info = profile.find("BaseInfo")
                    if base_info is not None:
                        is_female = base_info.get("isfemale", "0")
                        gender = "female" if is_female == "1" else "male"
                        self.logger.debug(f"Gender from XML: {gender} (isfemale={is_female})")
                        return gender
            
            self.logger.warning("Could not determine gender, defaulting to male")
            return "male"  # Default fallback
            
        except Exception as e:
            self.logger.error(f"Error getting gender: {str(e)}", exc_info=True)
            return "male"  # Default fallback

    def _load_armor_image(self, armor_id, slot_type, is_navi=False):
        """Load and display armor PNG for a specific slot - prepares for layering"""
        try:
            # Get the preview label for this slot
            preview_labels = self.navi_armor_preview_labels if is_navi else self.armor_preview_labels
            
            if slot_type not in preview_labels:
                self.logger.warning(f"No preview label found for {slot_type}")
                return
            
            image_label = preview_labels[slot_type]
            
            # Get armor name from ID
            armor_name = self._get_item_name(armor_id)
            
            # Sanitize armor name for filename - KEEP SPACES, NO UNDERSCORES
            sanitized_name = armor_name.replace("/", "_")  # Only replace slashes
            sanitized_name = sanitized_name.replace("'", "")  # Remove apostrophes
            sanitized_name = sanitized_name.replace(":", "")  # Remove colons
            sanitized_name = sanitized_name.replace("ä", "a").replace("ì", "i")  # Handle special chars
            
            # Determine the correct faction folder
            faction_folder = "navi" if is_navi else "rda"
            
            # Get gender from the save file
            gender = self._get_current_gender()  # Returns "male" or "female"
            
            # Try to find PNG in assets/armors/{faction}/{gender}/ folder
            png_path = os.path.join("assets", "armors", faction_folder, gender, f"{sanitized_name}.png")
            
            # Also try with armor ID as filename
            if not os.path.exists(png_path):
                png_path = os.path.join("assets", "armors", faction_folder, gender, f"{armor_id}.png")
            
            if os.path.exists(png_path):
                # Load the PNG
                image = Image.open(png_path)
                # Resize to standard size (300x300)
                image = image.resize((300, 300), Image.LANCZOS)
                
                # Ensure image has alpha channel for transparency
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                
                # Store the PIL Image on the label for later layering
                if not hasattr(image_label, 'armor_images'):
                    image_label.armor_images = {}
                image_label.armor_images[slot_type] = image
                
                # Trigger composite rendering
                self._render_composite_armor(is_navi)
                
                self.logger.debug(f"Loaded armor PNG: {png_path}")
            else:
                # No PNG found - show placeholder
                if hasattr(image_label, 'armor_images') and slot_type in image_label.armor_images:
                    del image_label.armor_images[slot_type]
                self._render_composite_armor(is_navi)
                self.logger.debug(f"Armor PNG not found: {png_path}")
                
        except Exception as e:
            self.logger.error(f"Error loading armor PNG: {str(e)}", exc_info=True)

    def _render_composite_armor(self, is_navi=False):
        """Render composite armor image by layering legs -> torso -> head"""
        try:
            preview_labels = self.navi_armor_preview_labels if is_navi else self.armor_preview_labels
            
            # Create a blank canvas (100x100, transparent)
            composite = Image.new('RGBA', (300, 300), (0, 0, 0, 0))
            
            # Layer order: legs (bottom) -> torso (middle) -> headwear (top)
            layer_order = ['legs', 'torso', 'headwear']
            
            has_any_armor = False
            
            # Composite the layers
            for slot_type in layer_order:
                if slot_type in preview_labels:
                    label = preview_labels[slot_type]
                    if hasattr(label, 'armor_images') and slot_type in label.armor_images:
                        armor_image = label.armor_images[slot_type]
                        # Ensure image has alpha channel
                        if armor_image.mode != 'RGBA':
                            armor_image = armor_image.convert('RGBA')
                        # Paste onto composite (alpha composite)
                        composite = Image.alpha_composite(composite, armor_image)
                        has_any_armor = True
            
            # Find a label to display the composite on
            # We'll create a dedicated composite preview label
            if not hasattr(self, 'composite_preview_labels'):
                self.composite_preview_labels = {}
            
            faction_key = 'navi' if is_navi else 'rda'
            
            if faction_key in self.composite_preview_labels:
                composite_label = self.composite_preview_labels[faction_key]
                
                if has_any_armor:
                    # Convert to PhotoImage and display
                    photo = ImageTk.PhotoImage(composite)
                    composite_label.configure(image=photo, text="")
                    composite_label.image = photo  # Keep reference
                else:
                    # No armor equipped
                    composite_label.configure(image="", text="No Armor\nEquipped")
            
        except Exception as e:
            self.logger.error(f"Error rendering composite armor: {str(e)}", exc_info=True)

    def _display_gif(self, label, gif_path):
        """Display an animated GIF on a label"""
        try:
            from PIL import Image, ImageTk, ImageSequence
            
            # Open the GIF
            gif = Image.open(gif_path)
            
            # Get all frames
            frames = []
            for frame in ImageSequence.Iterator(gif):
                # Resize frame to fit (100x100)
                frame = frame.copy()
                frame = frame.resize((100, 100), Image.LANCZOS)
                frames.append(ImageTk.PhotoImage(frame))
            
            # Store frames on the label to prevent garbage collection
            label.frames = frames
            label.frame_index = 0
            
            # Clear any text
            label.configure(text="")
            
            # Start animation
            self._animate_gif(label)
            
        except Exception as e:
            self.logger.error(f"Error displaying GIF: {str(e)}", exc_info=True)
            label.configure(image="", text="Error")

    def _animate_gif(self, label):
        """Animate a GIF by cycling through frames"""
        try:
            if not hasattr(label, 'frames') or not label.frames:
                return
            
            # Update to next frame
            label.configure(image=label.frames[label.frame_index])
            label.frame_index = (label.frame_index + 1) % len(label.frames)
            
            # Schedule next frame (100ms delay = 10 FPS)
            label.after(100, lambda: self._animate_gif(label))
            
        except Exception as e:
            self.logger.error(f"Error animating GIF: {str(e)}")

    def _open_outfit_manager(self, is_navi=False):
        """Open the outfit manager window"""
        if self.main_window.tree is None:
            show_error("Error", "No save file loaded. Please load a save file first.")
            return
        
        # Create outfit manager window
        manager_window = tk.Toplevel(self.parent)
        faction_name = "Na'vi" if is_navi else "RDA"
        manager_window.title(f"{faction_name} Outfit Manager")
        manager_window.geometry("600x500")
        manager_window.transient(self.parent)
        manager_window.grab_set()

        # Set window icon
        icon_path = os.path.join("icon", "avatar_icon.ico")
        if os.path.exists(icon_path):
            try:
                manager_window.iconbitmap(icon_path)
            except Exception as e:
                logging.getLogger('OutfitManager').warning(f"Failed to set window icon: {e}")
        else:
            logging.getLogger('OutfitManager').warning(f"Icon file not found: {icon_path}")

        # Set dark background
        manager_window.configure(bg='#1e1e1e')
        
        # Center the window
        manager_window.update_idletasks()
        x = (manager_window.winfo_screenwidth() // 2) - (manager_window.winfo_width() // 2)
        y = (manager_window.winfo_screenheight() // 2) - (manager_window.winfo_height() // 2)
        manager_window.geometry(f"+{x}+{y}")
        
        # Main container with dark background
        main_container = ttk.Frame(manager_window, padding=15)
        main_container.pack(fill=tk.BOTH, expand=True)
        main_container.configure(style='Dark.TFrame')
        
        # Create style for dark background if it doesn't exist
        style = ttk.Style()
        style.configure('Dark.TFrame', background='#1e1e1e')
        style.configure('Dark.TLabel', background='#1e1e1e', foreground='white')
        style.configure('Dark.TLabelframe', background='#1e1e1e', foreground='white')
        style.configure('Dark.TLabelframe.Label', background='#1e1e1e', foreground='white')
        
        # Title
        title_label = ttk.Label(main_container, 
                            text=f"{faction_name} Outfit Manager",
                            font=('Segoe UI', 12, 'bold'),
                            style='Dark.TLabel')
        title_label.pack(pady=(0, 10))
        
        # Current outfit section
        current_frame = ttk.LabelFrame(main_container, text="Current Outfit", padding=10, style='Dark.TLabelframe')
        current_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Get current armor
        armor_dropdowns = self.navi_armor_dropdowns if is_navi else self.armor_dropdowns
        current_outfit = {
            "headwear": armor_dropdowns["headwear"].get(),
            "torso": armor_dropdowns["torso"].get(),
            "legs": armor_dropdowns["legs"].get()
        }
        
        # Display current outfit
        ttk.Label(current_frame, text=f"Head: {current_outfit['headwear']}", 
                font=('Segoe UI', 9), style='Dark.TLabel').pack(anchor=tk.W, pady=2)
        ttk.Label(current_frame, text=f"Torso: {current_outfit['torso']}", 
                font=('Segoe UI', 9), style='Dark.TLabel').pack(anchor=tk.W, pady=2)
        ttk.Label(current_frame, text=f"Legs: {current_outfit['legs']}", 
                font=('Segoe UI', 9), style='Dark.TLabel').pack(anchor=tk.W, pady=2)
        
        # Save current outfit button
        save_frame = ttk.Frame(current_frame, style='Dark.TFrame')
        save_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(save_frame, text="💾 Save Current Outfit", 
                command=lambda: self._save_current_outfit(is_navi, manager_window)).pack(side=tk.LEFT, padx=(0, 5))
        
        # Saved outfits section
        saved_frame = ttk.LabelFrame(main_container, text="Saved Outfits", padding=10, style='Dark.TLabelframe')
        saved_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable list of saved outfits
        canvas = tk.Canvas(saved_frame, highlightthickness=0, bg='#1e1e1e')
        scrollbar = ttk.Scrollbar(saved_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Dark.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Display saved outfits
        self._refresh_outfit_list(scrollable_frame, is_navi, manager_window)
        
        # Close button
        ttk.Button(main_container, text="Close", 
                command=manager_window.destroy).pack(pady=(10, 0))
        
    def _save_current_outfit(self, is_navi, parent_window):
        """Save the current outfit with a custom name - UPDATED FOR PERSISTENT STORAGE"""
        # Get current armor
        armor_dropdowns = self.navi_armor_dropdowns if is_navi else self.armor_dropdowns
        current_outfit = {
            "headwear": armor_dropdowns["headwear"].get(),
            "torso": armor_dropdowns["torso"].get(),
            "legs": armor_dropdowns["legs"].get()
        }
        
        # Check if any armor is empty
        if (current_outfit["headwear"] == "-Empty-" and 
            current_outfit["torso"] == "-Empty-" and 
            current_outfit["legs"] == "-Empty-"):
            show_warning("Empty Outfit", "Cannot save an outfit with no armor pieces.")
            return
        
        # Create dialog to get outfit name
        name_dialog = tk.Toplevel(parent_window)
        name_dialog.title("Save Outfit")
        name_dialog.geometry("400x150")
        name_dialog.transient(parent_window)
        name_dialog.grab_set()
        
        # Center the dialog
        name_dialog.update_idletasks()
        x = (name_dialog.winfo_screenwidth() // 2) - (name_dialog.winfo_width() // 2)
        y = (name_dialog.winfo_screenheight() // 2) - (name_dialog.winfo_height() // 2)
        name_dialog.geometry(f"+{x}+{y}")
        
        result = {"name": None}
        
        # Content frame
        content_frame = ttk.Frame(name_dialog, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(content_frame, text="Enter outfit name:", 
                font=('Segoe UI', 10)).pack(pady=(0, 10))
        
        name_entry = ttk.Entry(content_frame, font=('Segoe UI', 10))
        name_entry.pack(fill=tk.X, pady=(0, 10))
        name_entry.focus_set()
        
        def save_outfit():
            outfit_name = name_entry.get().strip()
            if not outfit_name:
                show_warning("Invalid Name", "Please enter a valid outfit name.")
                return
            
            result["name"] = outfit_name
            name_dialog.destroy()
        
        # Buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Save", command=save_outfit).pack(side=tk.LEFT, padx=(0, 5), expand=True, fill=tk.X)
        ttk.Button(button_frame, text="Cancel", command=name_dialog.destroy).pack(side=tk.RIGHT, expand=True, fill=tk.X)
        
        name_entry.bind('<Return>', lambda e: save_outfit())
        name_entry.bind('<Escape>', lambda e: name_dialog.destroy())
        
        # Wait for dialog to close
        name_dialog.wait_window()
        
        if result["name"]:
            # Save the outfit
            outfit_data = {
                "name": result["name"],
                "headwear": current_outfit["headwear"],
                "torso": current_outfit["torso"],
                "legs": current_outfit["legs"]
            }
            
            saved_outfits = self.saved_outfits_navi if is_navi else self.saved_outfits_rda
            saved_outfits.append(outfit_data)
            
            # SAVE TO FILE
            if self._save_outfits_to_file(saved_outfits, is_navi):
                show_success("Outfit Saved", f"Outfit '{result['name']}' has been saved successfully!")
                # Refresh the outfit list in the manager window
                self._refresh_outfit_manager(parent_window, is_navi)
            else:
                show_error("Save Failed", "Failed to save outfit to file.")

    def _delete_outfit(self, outfit_index, is_navi, parent_window):
        """Delete a saved outfit - UPDATED FOR PERSISTENT STORAGE"""
        saved_outfits = self.saved_outfits_navi if is_navi else self.saved_outfits_rda
        
        if 0 <= outfit_index < len(saved_outfits):
            outfit_name = saved_outfits[outfit_index]["name"]
            
            # Confirm deletion
            if ask_ok_cancel("Confirm Delete", f"Are you sure you want to delete outfit '{outfit_name}'?"):
                del saved_outfits[outfit_index]
                
                # SAVE TO FILE
                if self._save_outfits_to_file(saved_outfits, is_navi):
                    show_success("Outfit Deleted", f"Outfit '{outfit_name}' has been deleted.")
                    # Refresh the outfit list
                    self._refresh_outfit_manager(parent_window, is_navi)
                else:
                    show_error("Delete Failed", "Failed to save changes to file.")

    def _refresh_outfit_list(self, container, is_navi, parent_window):
        """Refresh the list of saved outfits"""
        # Clear existing widgets
        for widget in container.winfo_children():
            widget.destroy()
        
        # Create style if not exists
        style = ttk.Style()
        style.configure('Dark.TFrame', background='#1e1e1e')
        style.configure('Dark.TLabel', background='#1e1e1e', foreground='white')
        
        saved_outfits = self.saved_outfits_navi if is_navi else self.saved_outfits_rda
        
        if not saved_outfits:
            ttk.Label(container, text="No saved outfits yet.", 
                    font=('Segoe UI', 9), foreground='gray', 
                    style='Dark.TLabel').pack(pady=20)
            return
        
        for idx, outfit in enumerate(saved_outfits):
            outfit_frame = ttk.Frame(container, relief='solid', borderwidth=1, style='Dark.TFrame')
            outfit_frame.pack(fill=tk.X, pady=5, padx=5)
            
            # Outfit info
            info_frame = ttk.Frame(outfit_frame, padding=10, style='Dark.TFrame')
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            ttk.Label(info_frame, text=outfit["name"], 
                    font=('Segoe UI', 10, 'bold'), 
                    style='Dark.TLabel').pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"Head: {outfit['headwear']}", 
                    font=('Segoe UI', 8), 
                    style='Dark.TLabel').pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"Torso: {outfit['torso']}", 
                    font=('Segoe UI', 8), 
                    style='Dark.TLabel').pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"Legs: {outfit['legs']}", 
                    font=('Segoe UI', 8), 
                    style='Dark.TLabel').pack(anchor=tk.W)
            
            # Buttons
            button_frame = ttk.Frame(outfit_frame, padding=5, style='Dark.TFrame')
            button_frame.pack(side=tk.RIGHT)
            
            ttk.Button(button_frame, text="📥 Load", 
                    command=lambda o=outfit: self._load_outfit(o, is_navi, parent_window)).pack(pady=2)
            ttk.Button(button_frame, text="🗑️ Delete", 
                    command=lambda i=idx: self._delete_outfit(i, is_navi, parent_window)).pack(pady=2)
        
    def _refresh_outfit_manager(self, manager_window, is_navi):
        """Refresh the entire outfit manager window"""
        # Close and reopen the window
        manager_window.destroy()
        self._open_outfit_manager(is_navi)

    def _load_outfit(self, outfit, is_navi, parent_window):
        """Load a saved outfit"""
        if self.main_window.tree is None:
            show_error("Error", "No save file loaded. Please load a save file first.")
            return
        
        try:
            profile = self.main_window.tree.getroot().find("PlayerProfile")
            if profile is None:
                show_error("Error", "PlayerProfile not found in save file.")
                return
            
            armor_dropdowns = self.navi_armor_dropdowns if is_navi else self.armor_dropdowns
            
            # Update each armor piece
            for slot_type in ["headwear", "torso", "legs"]:
                armor_name = outfit[slot_type]
                
                # Update dropdown
                armor_dropdowns[slot_type].set(armor_name)
                
                # Update the armor in the save file
                self._update_armor(profile, slot_type, armor_name, is_navi=is_navi)
                
                # Update preview
                if armor_name != "-Empty-":
                    armor_ids = self.navi_armor_ids if is_navi else self.rda_armor_ids
                    armor_id = armor_ids[slot_type].get(armor_name)
                    if armor_id:
                        self._load_armor_image(armor_id, slot_type, is_navi=is_navi)
                else:
                    # Clear preview for empty slots
                    preview_labels = self.navi_armor_preview_labels if is_navi else self.armor_preview_labels
                    if slot_type in preview_labels:
                        preview_label = preview_labels[slot_type]
                        preview_label.configure(image="", text="No Armor")
                        if hasattr(preview_label, 'frames'):
                            delattr(preview_label, 'frames')
            
            # Mark changes as unsaved
            self.main_window.unsaved_label.config(text="Unsaved Changes")
            
            # Close the manager window FIRST (releases grab)
            parent_window.destroy()
            
            # THEN show success message (after grab is released)
            show_success("Outfit Loaded", f"Outfit '{outfit['name']}' has been loaded successfully!")
            
        except Exception as e:
            self.logger.error(f"Error loading outfit: {str(e)}", exc_info=True)
            # Close the window first to release grab
            try:
                parent_window.destroy()
            except:
                pass
            # Then show error
            show_error("Error", f"Failed to load outfit: {str(e)}")

    def _get_outfit_storage_path(self, is_navi=False):
        """Get the path to the outfit storage file for the current save"""
        try:
            # Try different possible attributes for the current file path
            current_file = None
            
            # Check various possible attribute names
            if hasattr(self.main_window, 'current_file'):
                current_file = self.main_window.current_file
            elif hasattr(self.main_window, 'file_path'):
                current_file = self.main_window.file_path
            elif hasattr(self.main_window, 'current_save_path'):
                current_file = self.main_window.current_save_path
            elif hasattr(self.main_window, 'filepath'):
                current_file = self.main_window.filepath
            
            if current_file is None:
                self.logger.error("Could not find current file path in main_window")
                return None
            
            # Get the save file name without extension
            save_file_name = os.path.splitext(os.path.basename(current_file))[0]
            
            # Create outfits directory if it doesn't exist
            outfits_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outfits")
            if not os.path.exists(outfits_dir):
                os.makedirs(outfits_dir)
                self.logger.debug(f"Created outfits directory: {outfits_dir}")
            
            # Create file name based on save and faction
            faction_suffix = "navi" if is_navi else "rda"
            outfit_file = os.path.join(outfits_dir, f"{save_file_name}_{faction_suffix}_outfits.json")
            
            return outfit_file
            
        except Exception as e:
            self.logger.error(f"Error getting outfit storage path: {str(e)}")
            return None
    
    def _load_outfits_from_file(self, is_navi=False):
        """Load saved outfits from JSON file"""
        try:
            outfit_file = self._get_outfit_storage_path(is_navi)
            if outfit_file is None:
                return []
            
            if not os.path.exists(outfit_file):
                self.logger.debug(f"No outfit file found at {outfit_file}")
                return []
            
            with open(outfit_file, 'r', encoding='utf-8') as f:
                outfits = json.load(f)
                self.logger.debug(f"Loaded {len(outfits)} outfits from {outfit_file}")
                return outfits
                
        except Exception as e:
            self.logger.error(f"Error loading outfits from file: {str(e)}")
            return []

    def _save_outfits_to_file(self, outfits, is_navi=False):
        """Save outfits to JSON file"""
        try:
            outfit_file = self._get_outfit_storage_path(is_navi)
            if outfit_file is None:
                self.logger.error("Cannot save outfits: no current save file")
                return False
            
            with open(outfit_file, 'w', encoding='utf-8') as f:
                json.dump(outfits, f, indent=2, ensure_ascii=False)
                self.logger.debug(f"Saved {len(outfits)} outfits to {outfit_file}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving outfits to file: {str(e)}")
            return False

    def _initialize_outfit_storage(self):
        """Initialize outfit storage by loading saved outfits for current save file"""
        try:
            # Load RDA outfits
            self.saved_outfits_rda = self._load_outfits_from_file(is_navi=False)
            self.logger.debug(f"Initialized RDA outfits: {len(self.saved_outfits_rda)} loaded")
            
            # Load Na'vi outfits
            self.saved_outfits_navi = self._load_outfits_from_file(is_navi=True)
            self.logger.debug(f"Initialized Na'vi outfits: {len(self.saved_outfits_navi)} loaded")
            
        except Exception as e:
            self.logger.error(f"Error initializing outfit storage: {str(e)}")
            self.saved_outfits_rda = []
            self.saved_outfits_navi = []

    def _get_equipped_weapons(self, profile: ET.Element) -> dict:
        """Get equipped RDA weapons data"""
        weapons_data = {}
        soldier = profile.find("Possessions_Soldier")
        if soldier is not None:
            equipped = soldier.find("EquippedWeapons")
            if equipped is not None:
                # Get all weapon slots
                for slot in equipped.findall("Slot"):
                    main_hand = slot.get("MainHand_PossIdx", "-1")
                    off_hand = slot.get("OffHand_PossIdx", "-1")
                    weapons_data[len(weapons_data)] = {
                        "main": main_hand,
                        "off": off_hand
                    }
        return weapons_data

    def _get_weapon_info(self, profile: ET.Element, index: str) -> dict:
        """Get RDA weapon name and details from possession index"""
        if index == "-1":
            return None
                
        soldier = profile.find("Possessions_Soldier")
        if soldier is not None:
            possessions = soldier.find("Posessions")
            if possessions is not None:
                for poss in possessions.findall("Poss"):
                    if poss.get("Index") == index:
                        item_id = poss.get("crc_ItemID")
                        ammo_type = poss.get("crc_AmmoType", "4294967295")
                        item_name = self._get_item_name(item_id)
                        
                        # Determine if this is a melee weapon
                        is_melee = any(melee_kw in item_name.lower() for melee_kw in 
                                    ["club", "blade", "axe", "staff", "spear", "knife", "sword"])
                        
                        weapon_info = {
                            "id": item_id,
                            "name": item_name,
                            "ammo": "Melee" if is_melee else poss.get("NbInClip", "0"),
                            "stack": poss.get("NbInStack", "0"),
                            "is_melee": is_melee
                        }
                        
                        if ammo_type != "4294967295" and not is_melee:  # If not infinite ammo and not melee
                            total_ammo = "0"
                            for ammo_poss in possessions.findall("Poss"):
                                if ammo_poss.get("crc_ItemID") == ammo_type:
                                    total_ammo = ammo_poss.get("NbInStack", "0")
                                    break
                            weapon_info["total_ammo"] = total_ammo
                        
                        # Check if weapon has infinite ammo
                        weapon_info["infinite_ammo"] = (
                            ammo_type == "4294967295" and 
                            not is_melee and
                            not any(pistol_term in item_name.lower() for pistol_term in ["wasp pistol"])
                        )
                        
                        # Special case for Wasp Pistols
                        if "wasp pistol" in item_name.lower():
                            weapon_info["infinite_ammo"] = True
                            weapon_info["ammo"] = "∞"
                        
                        return weapon_info
        return None

    def _get_armor_info(self, profile: ET.Element) -> dict:
        """Get RDA armor info for each slot (headwear, torso, legs)"""
        armor_slots = {"headwear": None, "torso": None, "legs": None}
        
        soldier = profile.find("Possessions_Soldier")
        if soldier is not None:
            equipped_armors = soldier.find("EquippedArmors")
            if equipped_armors is not None:
                # Get all slots
                slots = equipped_armors.findall("Slot")
                if len(slots) >= 3:  # Ensure we have all three slots
                    # Map slots to armor types (first is headwear, second is torso, third is legs)
                    slot_mapping = {0: "headwear", 1: "torso", 2: "legs"}
                    
                    for idx, slot in enumerate(slots[:3]):  # Process first three slots
                        armor_idx = slot.get("PossIdx", "-1")
                        
                        # Skip if no armor in this slot
                        if armor_idx == "-1":
                            continue
                            
                        possessions = soldier.find("Posessions")
                        if possessions is not None:
                            for poss in possessions.findall("Poss"):
                                if poss.get("Index") == armor_idx:
                                    item_id = poss.get("crc_ItemID")
                                    if item_id:
                                        armor_slots[slot_mapping[idx]] = {
                                            "id": item_id,
                                            "name": self._get_item_name(item_id)
                                        }
        return armor_slots

    def _get_avatar_weapons(self, profile: ET.Element) -> dict:
        """Get equipped Na'vi weapons data"""
        weapons_data = {}
        avatar = profile.find("Possessions_Avatar")
        if avatar is not None:
            equipped = avatar.find("EquippedWeapons")
            if equipped is not None:
                # Get all weapon slots
                for slot in equipped.findall("Slot"):
                    main_hand = slot.get("MainHand_PossIdx", "-1")
                    off_hand = slot.get("OffHand_PossIdx", "-1")
                    weapons_data[len(weapons_data)] = {
                        "main": main_hand,
                        "off": off_hand
                    }
        return weapons_data

    def _get_avatar_weapon_info(self, profile: ET.Element, index: str) -> dict:
        """Get Na'vi weapon name and details from possession index"""
        if index == "-1":
            return None
                
        avatar = profile.find("Possessions_Avatar")
        if avatar is not None:
            possessions = avatar.find("Posessions")
            if possessions is not None:
                for poss in possessions.findall("Poss"):
                    if poss.get("Index") == index:
                        item_id = poss.get("crc_ItemID")
                        ammo_type = poss.get("crc_AmmoType", "4294967295")
                        item_name = self._get_item_name(item_id)
                        
                        # Determine if this is a melee weapon
                        is_melee = any(melee_kw in item_name.lower() for melee_kw in 
                                    ["club", "blade", "axe", "staff", "spear", "knife", "sword"])
                        
                        weapon_info = {
                            "id": item_id,
                            "name": item_name,
                            "ammo": "Melee" if is_melee else poss.get("NbInClip", "0"),
                            "stack": poss.get("NbInStack", "0"),
                            "is_melee": is_melee
                        }
                        
                        if ammo_type != "4294967295" and not is_melee:  # If not infinite ammo and not melee
                            total_ammo = "0"
                            for ammo_poss in possessions.findall("Poss"):
                                if ammo_poss.get("crc_ItemID") == ammo_type:
                                    total_ammo = ammo_poss.get("NbInStack", "0")
                                    break
                            weapon_info["total_ammo"] = total_ammo
                        
                        # Check if weapon has infinite ammo
                        weapon_info["infinite_ammo"] = (
                            ammo_type == "4294967295" and 
                            not is_melee and
                            not any(pistol_term in item_name.lower() for pistol_term in ["wasp pistol"])
                        )
                        
                        # Special case for Wasp Pistols
                        if "wasp pistol" in item_name.lower():
                            weapon_info["infinite_ammo"] = True
                            weapon_info["ammo"] = "∞"
                        
                        return weapon_info
        return None

    def _get_navi_armor_info(self, profile: ET.Element) -> dict:
        """Get Na'vi armor info for each slot from Posessions"""
        armor_slots = {"headwear": None, "torso": None, "legs": None}
        
        avatar = profile.find("Possessions_Avatar")
        if avatar is not None:
            equipped_armors = avatar.find("EquippedArmors")
            if equipped_armors is not None:
                # Get all slots
                slots = equipped_armors.findall("Slot")
                if len(slots) >= 3:  # Ensure we have all three slots
                    # Map slots to armor types (first is headwear, second is torso, third is legs)
                    slot_mapping = {0: "headwear", 1: "torso", 2: "legs"}
                    
                    for idx, slot in enumerate(slots[:3]):  # Process first three slots
                        armor_idx = slot.get("PossIdx", "-1")
                        
                        # Skip if no armor in this slot
                        if armor_idx == "-1":
                            continue
                            
                        possessions = avatar.find("Posessions")
                        if possessions is not None:
                            for poss in possessions.findall("Poss"):
                                if poss.get("Index") == armor_idx:
                                    item_id = poss.get("crc_ItemID")
                                    if item_id:
                                        armor_slots[slot_mapping[idx]] = {
                                            "id": item_id,
                                            "name": self._get_item_name(item_id)
                                        }
        return armor_slots

    def _preserve_faction(self, profile, faction_value="1"):
        """Ensure faction stays preserved (prevents resets to Undecided)"""
        # Look for Metagame directly from the main window's tree
        root = self.main_window.tree.getroot()
        metagame = root.find("Metagame")
        
        if metagame is not None:
            # Always set the faction to the specified value
            current = metagame.get("PlayerFaction")
            if current != faction_value:
                print(f"DEBUG: Fixing faction reset. Changed from {current} to {faction_value}")
                metagame.set("PlayerFaction", faction_value)
                
                # Also update the UI dropdown to match
                faction_map = {"0": "Undecided", "1": "Na'vi", "2": "RDA"}
                if "PlayerFaction" in self.entries:
                    self.entries["PlayerFaction"].set(faction_map.get(faction_value, "Undecided"))

    def _ensure_ammo_exists(self, possessions, ammo_type, amount="100"):
        """Ensure ammo exists in inventory when disabling infinite ammo"""
        # Skip if ammo type is the 'no ammo' value
        if ammo_type == "4294967295":
            self.logger.debug("Skipping ammo creation for infinite ammo weapon")
            return
                
        # Check if ammo already exists
        ammo_exists = False
        for poss in possessions.findall("Poss"):
            if poss.get("crc_ItemID") == ammo_type:
                ammo_exists = True
                # Set the ammo to the requested amount
                poss.set("NbInStack", amount)
                poss.set("NbInClip", "0")  # Also ensure clip value is set
                poss.set("NoveltyState", "2")  # Make sure novelty state is right
                self.logger.debug(f"Updated existing ammo of type {ammo_type} to {amount}")
                break
                    
        if not ammo_exists:
            self.logger.debug(f"Creating new ammo of type {ammo_type} with amount {amount}")
            # Need to add ammo to inventory
            # Find next available index
            max_index = -1
            for poss in possessions.findall("Poss"):
                idx = int(poss.get("Index", "0"))
                if idx > max_index:
                    max_index = idx
                        
            # Create new possession for ammo
            new_index = max_index + 1
            self.logger.debug(f"Creating new ammo at index {new_index}")
            new_ammo = ET.SubElement(possessions, "Poss")
            new_ammo.set("Index", str(new_index))
            new_ammo.set("crc_ItemID", ammo_type)
            new_ammo.set("NbInStack", amount)
            new_ammo.set("NbInClip", "0")
            new_ammo.set("crc_AmmoType", "4294967295")
            new_ammo.set("NoveltyState", "2")
        self.logger.debug(f"New ammo created successfully")

    def _create_item_mappings(self):
        """Create mappings for item IDs to their actual names"""
        self.item_mappings = {

            #############################################

            # RDA Weapons

            # Dual Wasp Pistol
            "1042188764": "Dual Wasp Pistol I",
            "815885611": "Dual Wasp Pistol II",
            "760079057": "Dual Wasp Pistol III",
            "999316102": "Dual Wasp Pistol IV",
            
            # DLC Dual Wasp Pistols
            "3859060838": "DLC WARLOCK Dual Wasp Pistol I",
            "3904601233": "DLC WARLOCK Dual Wasp Pistol II",
            "102867538": "DLC WARLOCK Dual Wasp Pistol III", 
            "749353518": "DLC WARLOCK Dual Wasp Pistol IV",

            # Standard Issue Rifle
            "1130814347": "Standard Issue Rifle TERRA I",
            "1306083196": "Standard Issue Rifle EURYS II",
            "3628031700": "Standard Issue Rifle SOLARIS III",
            "1146928137": "Standard Issue Rifle SOLARIS IV",
            
            # DLC Standard Issue Rifles
            "2850329205": "DLC ARGO Standard Issue Rifle I",
            "2807789186": "DLC ARGO Standard Issue Rifle II",
            "2194670470": "DLC ARGO Standard Issue Rifle III",
            "324172685": "DLC ARGO Standard Issue Rifle IV",

            # Combat Shotgun
            "2313824646": "Combat Shotgun PHALANX I",
            "2270547313": "Combat Shotgun PHALANX II",
            "2789519003": "Combat Shotgun PHALANX III",
            "1919695864": "Combat Shotgun PHALANX IV",
            
            # DLC Combat Shotguns
            "2664450350": "DLC SIGNET Combat Shotgun I",
            "2423238105": "DLC SIGNET Combat Shotgun II",
            "2120138529": "DLC SIGNET Combat Shotgun III",
            "4289908838": "DLC SIGNET Combat Shotgun IV",

            # Assault Rifle
            "2397981034": "Assault Rifle TERRA I",
            "2152836509": "Assault Rifle EURYS II",
            "268371112": "Assault Rifle SOLARIS III",
            "466145020": "Assault Rifle SOLARIS IV",
            
            # DLC Assault Rifles
            "3655372526": "DLC BARRO Assault Rifle I",
            "3613354521": "DLC BARRO Assault Rifle II",
            "3850194262": "DLC BARRO Assault Rifle III",
            "2109370248": "DLC BARRO Assault Rifle IV",

            # M60 Machine Gun
            "85991974": "BANISHER M60 Machine Gun I",
            "195020497": "BANISHER M60 Machine Gun II",
            "1881065336": "BANISHER M60 Machine Gun III",
            "1796958374": "BANISHER M60 Machine Gun IV",
            
            # DLC Machine Guns
            "2015914953": "DLC STELLAR M60 Machine Gun I",
            "1989644094": "DLC STELLAR M60 Machine Gun II",
            "1087779032": "DLC STELLAR M60 Machine Gun III",
            "1691104809": "DLC STELLAR M60 Machine Gun IV",

            # Grenade Launcher
            "94681171": "Grenade Launcher M222 - I",
            "186342564": "Grenade Launcher M222 - II",
            "1349633617": "Grenade Launcher M222 - III",
            "4018216358": "Grenade Launcher M222 - IV",
            
            # DLC Grenade Launchers
            "2157668310": "DLC CRUSHER Grenade Launcher I",
            "2384757537": "DLC CRUSHER Grenade Launcher II",
            "3441856033": "DLC CRUSHER Grenade Launcher III",
            "3043901684": "DLC CRUSHER Grenade Launcher IV",

            # Flamethrower
            "2529862352": "Flamethrower VESUPYRE I",
            "2557822503": "Flamethrower STERILATOR II",
            "609450705": "Flamethrower BUSHBOSS III",
            "2288255787": "Flamethrower BUSHBOSS IV",
            
            # DLC Flamethrowers
            "3250873684": "DLC BUDDY Flamethrower I",
            "3480977827": "DLC BUDDY Flamethrower II",
            "3469816623": "DLC BUDDY Flamethrower III",
            "3994460767": "DLC BUDDY Flamethrower IV",

            # Nail Gun
            "2548581230": "Nail Gun HAMMER I",
            "2572658585": "Nail Gun HAMMER II",
            "143378107": "Nail Gun HAMMER III",
            "1911864170": "Nail Gun HAMMER IV",
            
            # DLC Nail Guns
            "2161255366": "DLC DENT Nail Gun I",
            "2389559089": "DLC DENT Nail Gun II",
            "3499218689": "DLC DENT Nail Gun III",
            "4230631668": "DLC DENT Nail Gun IV",

            # RDA Ammo
            "4029490973": "Rifle Ammo",
            "2220072441": "Shotgun Ammo",
            "3183424835": "Rifle Ammo",
            "3227899887": "Machine Gun Ammo",
            "4198025789": "Mini-Grenades Ammo",
            "2442117335": "Flame Ammo",
            "3819023512": "Nail Ammo",

            #############################################

            # RDA Armor Sets

            # E3 Exotant Armor Set
            "666504347": "E3 Exotant Head", # PNG SET FEMALE     
            "531856612": "E3 Exotant Torso", # PNG SET FEMALE        
            "1234921930": "E3 Exotant Legs", # PNG SET FEMALE 
            
            # E3 Exclusive
            "2507615751": "E3 RDA HELM", # PNG SET FEMALE
            "2628484515": "E3 RDA CHEST", # PNG SET FEMALE 
            "694483043": "E3 RDA LEG", # PNG SET FEMALE 

            # Tusk Armor set
            "2800661647": "TUSK Helmet I", # PNG SET FEMALE 
            "2024422324": "TUSK Chest Armor I", # PNG SET FEMALE 
            "1949228588": "TUSK Leg Armor I", # PNG SET FEMALE 

            # Titan Armor Set
            "4082430736": "TITAN Helmet IV", # PNG SET FEMALE
            "205852157": "TITAN Chest Armor IV", # PNG SET FEMALE
            "1052486966": "TITAN Leg Armor IV", # PNG SET FEMALE 
        
            # Militum Armor Set
            "149499402": "MILITUM Helmet IV", # PNG SET FEMALE   
            "4160278759": "MILITUM Chest Armor IV", # PNG SET FEMALE     
            "3305533484": "MILITUM Leg Armor IV", # PNG SET FEMALE

            # Kodiak Armor Set
            "1593826001": "KODIAK Helmet IV", # PNG SET FEMALE 
            "2716738620": "KODIAK Chest Armor IV", # PNG SET FEMALE      
            "2467333367": "KODIAK Leg Armor IV", # PNG SET FEMALE    

            # EXOTANT Armor Sets
            "707432217": "EXOTANT Helmet I", # PNG SET FEMALE 
            "941983816": "EXOTANT Helmet II", # PNG SET FEMALE 
            "4194195158": "EXOTANT Helmet III", # PNG SET FEMALE 
            "3527939275": "EXOTANT Helmet IV", # PNG SET FEMALE 
            "2995015784": "EXOTANT Chest Armor I", # PNG SET FEMALE
            "649139601": "EXOTANT Chest Armor II", # PNG SET FEMALE 
            "116369467": "EXOTANT Chest Armor III", # PNG SET FEMALE 
            "1193780569": "EXOTANT Chest Armor IV", # PNG SET FEMALE 
            "1151571180": "EXOTANT Leg Armor I", # PNG SET FEMALE 
            "8207805": "EXOTANT Leg Armor II", # PNG SET FEMALE 
            "873531632": "EXOTANT Leg Armor III", # PNG SET FEMALE
            "1379870057": "EXOTANT Leg Armor IV", # PNG SET FEMALE

            # Centauri Armor Set
            "403319592": "CENTAURI Helmet IV", # PNG SET FEMALE 
            "3877361093": "CENTAURI Chest Armor IV", # PNG SET FEMALE  
            "3588584718": "CENTAURI Leg Armor IV", # PNG SET FEMALE       

            # Hydra Armor Set
            "3753317026": "HYDRA Helmet III", # PNG SET FEMALE    
            "1851965193": "HYDRA Chest Armor III", # PNG SET FEMALE         
            "2428117146": "HYDRA Leg Armor III", # PNG SET FEMALE  

            # Warthog Armor Set
            "2823901304": "WARTHOG Helmet II", # PNG SET FEMALE       
            "1981144899": "WARTHOG Chest Armor II", # PNG SET FEMALE          
            "2056338139": "WARTHOG Leg Armor II", # PNG SET FEMALE 

            # Viper Armor Set
            "3980056687": "VIPER Helmet I", # PNG SET FEMALE 
            "3574042272": "VIPER Chest Armor I", # PNG SET FEMALE 
            "1417888964": "VIPER Leg Armor I", # PNG SET FEMALE 
            
            # Plaza Variants
            "1830604945": "(Plaza) ARTHURA Helmet I", # PNG SET FEMALE 
            "3717529612": "(Plaza) ARTHURA I Helmet I", # PNG SET FEMALE
            "3542803707": "(Plaza) WARTHOG Helmet II", # PNG SET FEMALE 
            "1956713330": "(Plaza) ARTHURA Chest Armor I", 
            "207655578": "(Plaza) ARTHURA I Chest Armor I", 
            "48199277": "(Plaza) WARTHOG Chest Armor II", 
            "765525764": "(Plaza) ARTHURA Leg Armor I", 
            "3199333350": "(Plaza) ARTHURA I Leg Armor I", 
            "2953713425": "(Plaza) WARTHOG Leg Armor II", 

            # DLC BRASHER Armor Sets
            "3005472419": "DLC BRASHER Helmet I", # PNG SET FEMALE 
            "730661330": "DLC BRASHER Chest Armor I", # PNG SET FEMALE 
            "3718956374": "DLC BRASHER Leg Armor I", # PNG SET FEMALE 
            "3064631211": "DLC BRASHER Helmet II", # PNG SET FEMALE 
            "2822640242": "DLC BRASHER Chest Armor II", # PNG SET FEMALE 
            "2398239326": "DLC BRASHER Leg Armor II", # PNG SET FEMALE 
            "3228789267": "DLC BRASHER Helmet III", # PNG SET FEMALE 
            "1063425278": "DLC BRASHER Chest Armor III", # PNG SET FEMALE 
            "228340789": "DLC BRASHER Leg Armor III", # PNG SET FEMALE 
            "3818917462": "DLC BRASHER Helmet IV", # PNG SET FEMALE 
            "1993326532": "DLC BRASHER Chest Armor IV", # PNG SET FEMALE 
            "1675050996": "DLC BRASHER Leg Armor IV", # PNG SET FEMALE 
            
            # DLC MISHETICA Armor Sets
            "1563279247": "DLC MISHETICA Helmet I", # PNG SET FEMALE 
            "3313721598": "DLC MISHETICA Chest Armor I", # PNG SET FEMALE 
            "866428026": "DLC MISHETICA Leg Armor I", # PNG SET FEMALE 
            "4103047382": "DLC MISHETICA Helmet II", # PNG SET FEMALE 
            "3927643407": "DLC MISHETICA Chest Armor II", # PNG SET FEMALE 
            "3436657955": "DLC MISHETICA Leg Armor II", # PNG SET FEMALE 
            "4001710741": "DLC MISHETICA Helmet III", # PNG SET FEMALE 
            "294960248": "DLC MISHETICA Chest Armor III", # PNG SET FEMALE 
            "594156723": "DLC MISHETICA Leg Armor III", # PNG SET FEMALE 
            "1950293887": "DLC MISHETICA Helmet IV", # PNG SET FEMALE 
            "3780161261": "DLC MISHETICA Chest Armor IV", # PNG SET FEMALE 
            "4098371293": "DLC MISHETICA Leg Armor IV", # PNG SET FEMALE 

            # Default RDA Armor Set
            "433486271": "Default RDA Head", # PNG SET FEMALE 
            "2818823188": "Default RDA Torso", # PNG SET FEMALE 
            "1457212295": "Default RDA Legs", # PNG SET FEMALE 
            
            # Multiplayer RDA Variants - Headwear
            "141479065": "MP Default RDA Helmet", # PNG SET FEMALE 
            "525389396": "MP TUSK Helmet", # PNG SET FEMALE
            "300886691": "MP WARTHOG Helmet", # PNG SET FEMALE
            "3457132420": "MP HYDRA Helmet", # PNG SET FEMALE 
            "2253457575": "MP KODIAK Helmet", # PNG SET FEMALE 
            "737812838": "MP TITAN Helmet", # PNG SET FEMALE 
            "3232037214": "MP CENTAURI Helmet", # PNG SET FEMALE 
            "3494378620": "MP MILITUM Helmet", # PNG SET FEMALE 
            
            # Multiplayer RDA Variants - Torso
            "2048911708": "MP Default RDA Chest Armor", # PNG SET FEMALE 
            "1762823826": "MP TUSK Chest Armor", # PNG SET FEMALE 
            "1739418213": "MP WARTHOG Chest Armor", # PNG SET FEMALE 
            "3162407489": "MP HYDRA Chest Armor", # PNG SET FEMALE 
            "407920359": "MP KODIAK Chest Armor", # PNG SET FEMALE 
            "3053156134": "MP TITAN Chest Armor", # PNG SET FEMALE 
            "1587916574": "MP CENTAURI Chest Armor", # PNG SET FEMALE 
            "1313253948": "MP MILITUM Chest Armor", # PNG SET FEMALE 
            
            # Multiplayer RDA Variants - Legs
            "4016386396": "MP Default RDA Leg Armor", # PNG SET FEMALE 
            "2894072922": "MP TUSK Leg Armor", # PNG SET FEMALE 
            "2722097325": "MP WARTHOG Leg Armor", # PNG SET FEMALE 
            "688151105": "MP HYDRA Leg Armor", # PNG SET FEMALE 
            "820586591": "MP KODIAK Leg Armor", # PNG SET FEMALE 
            "2638348702": "MP TITAN Leg Armor", # PNG SET FEMALE 
            "1981602214": "MP CENTAURI Leg Armor", # PNG SET FEMALE 
            "1728044164": "MP MILITUM Leg Armor", # PNG SET FEMALE 
            
            # Generic Categories
            "1633102956": "ACAT Head Gear", # PNG SET FEMALE 
            "1178592625": "ACAT Chest Armor", # PNG SET FEMALE 
            "1002215802": "ACAT Leg Armor", # PNG SET FEMALE 

            # RDA Full Gear Sets (Torso Only)
            "73022142": "RDA Standard Issue Full Armor", # F M
            "2047018253": "TUSK Full Armor I", # F M
            "2529656365": "VIPER Full Armor I",# F M
            "1664737020": "WARTHOG Full Armor II", # F M
            "1042585997": "HYDRA Full Armor III",#FM
            "785085314": "TITAN Full Armor IV",#FM
            "2271254608": "KODIAK Full Armor IV",#FM
            "1639122250": "CENTAURI Full Armor IV",#FM
            "3033145114": "MILITUM Full Armor IV",#FM
            "3193262026": "BRASHER Full Armor IV",#FM
            "2543713080": "EXOTANT Full Armor IV",#FM
            "972384937": "MISHETICA Full Armor IV",#FM
            "3245854685": "BRASHER Full Armor I",#FM
            "708867294": "EXOTANT Full Armor I",#FM
            "3313639392": "MISHETICA Full Armor I",#FM
            "1583237298": "BRASHER Full Armor II",#FM
            "230953782": "EXOTANT Full Armor II",#FM
            "2321733749": "MISHETICA Full Armor II",#FM
            "2944242316": "BRASHER Full Armor III",#FM
            "1174097902": "EXOTANT Full Armor III",#FM
            "2863266063": "MISHETICA Full Armor III",#FM
            "663343731": "E3 TITAN Full Armor IV",#FM
            "3435030896": "E3 EXOTANT Full Armor IV",#FM
            
            # Multiplayer RDA Full Gear
            "2152765075": "MP RDA Standard Full Armor",#FM
            "1144369633": "MP VIPER Full Armor",#FM
            "3471767070": "MP TUSK Full Armor",#FM
            "3621006831": "MP WARTHOG Full Armor",#FM
            "3123590560": "MP HYDRA Full Armor",#FM
            "1630387372": "MP KODIAK Full Armor",#FM
            "3364247422": "MP TITAN Full Armor",#FM
            "2281578934": "MP CENTAURI Full Armor",#FM
            "1384594406": "MP MILITUM Full Armor",#FM
            "3503258363": "MP BRASHER Full Armor I",#FM
            "1881585149": "MP BRASHER Full Armor II",#FM
            "1227929200": "MP BRASHER Full Armor III",#FM
            "1923449271": "MP BRASHER Full Armor IV",#FM
            "1006158328": "MP EXOTANT Full Armor I",#FM
            "599584377":  "MP EXOTANT Full Armor II",#FM
            "2746641170": "MP EXOTANT Full Armor III",#FM
            "1533883717": "MP EXOTANT Full Armor IV",#FM
            "3560614598": "MP MISHETICA Full Armor I",#FM
            "2753176890": "MP MISHETICA Full Armor II",#FM
            "1290067443": "MP MISHETICA Full Armor III",#FM
            "4110787796": "MP MISHETICA Full Armor IV",#FM

            #############################################

            # Na'vi Weapons

            # Dual Blade
            "2740507591": "Ikranä Syal Dual Blade I",
            "2917611312": "'Angtsìkä Zawng Dual Blade II",
            "2813685095": "Palulukanä Srew Dual Blade III",
            "2948460035": "Torukä Way Dual Blade IV",
            
            # DLC Dual Blade
            "2285146948": "DLC Tanhì Dual Blade I",
            "2257287091": "DLC Tanhì Dual Blade II",
            "3543126973": "DLC Tanhì Dual Blade III",
            "2007498681": "DLC Tanhì Dual Blade IV",
            
            # Crossbow
            "1662469074": "Taronyu Crossbow I", 
            "1839769381": "Tsamsiyu Crossbow II",
            "3400058396": "Kyktan Crossbow III",
            "1514231420": "Nawm Crossbow IV",

            # DLC Crossbow
            "3138212456": "DLC PXI Crossbow I",
            "2486913109": "DLC PXI Crossbow II", 
            "2589205711": "DLC PXI Crossbow III",
            "1886472672": "DLC PXI Crossbow IV",

            # M30 Machine Gun
            "1304439874": "AVR-M30 Machine Gun I",
            "1132447925": "AVR-M30 Machine Gun II",
            "982090295": "AVR-M30 Machine Gun III",
            "958613249": "AVR-M30 Machine Gun IV",

            # ELITE M30 Machine Gun
            "818439597": "ELITE AVR-M30 I",
            "1048019290": "ELITE AVR-M30 II",
            "172062103": "ELITE AVR-M30 III",
            "921966990": "ELITE AVR-M30 IV",   

            # Club
            "4093397293": "Taronyu Club I",
            "4249071066": "Tsamsiyu Club II",
            "3879387803": "Eyktan Club III",
            "240531571": "Nawm Club IV",

            # DLC Axe
            "1958996617": "DLC Ikran Axe 'Eko",
            "2689671946": "DLC Ikran Axe Kurakx",
            "1639187137": "DLC Ikran Axe Tsmukan",
            "2934884349": "DLC Ikran Axe 'Ampi",
            
            # Fighting Staff
            "2255793432": "Ikranä Zawng Fighting Staff I",
            "2295024111": "Pa'liä Tìtxur Fighting Staff II",
            "2986118748": "Palulukanä Tìtakuk Fighting Staff III",
            "3960574385": "Torukä Tirea Fighting Staff IV",
            
            # DLC Fighting Staff
            "1828119782": "DLC Hufwe Fighting Staff I",
            "1648951313": "DLC Hufwe Fighting Staff II",
            "3943944974": "DLC Hufwe Fighting Staff III",
            "3139393077": "DLC Hufwe Fighting Staff IV",

            # Bow
            "291262189": "Taronyu Tsko Bow I",
            "371977402": "Tsko Nawm Bow IV",
            "2092736556": "Tsko Kyktan Bow III", 
            "535013914": "Tasmsiyu Tsko Bow II",

            # DLC Bow
            "1817446146": "DLC RAWKE Bow I",
            "1659626485": "DLC RAWKE Bow II",
            "1282693004": "DLC RAWKE Bow III",
            "435991093": "DLC RAWKE Bow IV",

            # Na'vi Ammo
            "1042656528": "M30 Ammo",  
            "435601722": "Arrow Ammo",   
            "3069972540": "Crossbow Ammo", 

            #############################################

            # Na'vi Armor   
            
            # RDA-Issue Avatar Gear
            "236713729": "RDA-Issue Avatar Head",#FM
            "2228061969": "RDA-Issue Avatar Torso",#FM
            "753645081": "RDA-Issue Avatar Legs",#FM

            # TSAMSIYU Armor Set
            "3705555217": "TSAMSIYU Head Gear I",#FM
            "1869067530": "TSAMSIYU Chest Gear I",#FM
            "780789927": "TSAMSIYU Leg Gear I",#FM

            # NAWM Armor Set
            "3363478556": "NAWM Head Gear III",#FM  
            "1118628876": "NAWM Chest Gear III",#FM
            "3934969092": "NAWM Leg Gear III",#FM

            # EYKTAN Armor Set
            "84098544": "EYKTAN Head Gear IV",#FM
            "3666151432": "EYKTAN Chest Gear IV",#FM
            "815973795": "EYKTAN Leg Gear IV",#FM

            # # KARYU Armor Set
            "2070955956": "KARYU Head Gear IV",#FM
            "1711646853": "KARYU Chest Gear IV",#FM
            "2024863229": "KARYU Leg Gear IV",#FM

            # NAWMA EYKTAN Armor Set
            "1519513878": "NAWMA EYKTAN Head Gear IV",#FM
            "2232927470": "NAWMA EYKTAN Chest Gear IV",#FM
            "1865419077": "NAWMA EYKTAN Leg Gear IV",#FM

            # NAWMA TARONYU Armor Set
            "3932154789": "NAWMA TARONYU Head Gear IV",#FM
            "884530381": "NAWMA TARONYU Chest Gear IV",#FM
            "3480671099": "NAWMA TARONYU Leg Gear IV",#FM
            
            # NAWMA TARONYU Series I-III
            "2628269855": "NAWMA TARONYU Head Gear I",#FM
            "2451035112": "NAWMA TARONYU Head Gear II",#FM
            "797099877": "NAWMA TARONYU Head Gear III",#FM
            "3743365442": "NAWMA TARONYU Chest Gear I",#FM
            "3516980661": "NAWMA TARONYU Chest Gear II",#FM
            "974871842": "NAWMA TARONYU Chest Gear III",#FM
            "4259766772": "NAWMA TARONYU Leg Gear I",#FM
            "4082697475": "NAWMA TARONYU Leg Gear II",#FM
            "406565443": "NAWMA TARONYU Leg Gear III",#FM

            # NAWMA TSAMSIYU Armor Set
            "25166328": "NAWMA TSAMSIYU Head Gear IV",#FM
            "3724948480": "NAWMA TSAMSIYU Chest Gear IV",#FM
            "874641835": "NAWMA TSAMSIYU Leg Gear IV",#FM

            # 'AWVEA TSAMSIYU Armor Set   
            "3529616870": "'AWVEA TSAMSIYU Head Gear II",#FM
            "1641566717": "'AWVEA TSAMSIYU Chest Gear II", #FM  
            "540413008": "'AWVEA TSAMSIYU Leg Gear II",#FM
            
            # DLC TARONYU Armor Set
            "2508072600": "DLC TARONYU Head Gear I",#FM
            "3240533717": "DLC TARONYU Head Gear II",#FM
            "2008660537": "DLC TARONYU Head Gear III",#FM
            "1753343575": "DLC TARONYU Head Gear IV",#FM
            "2282473897": "DLC TARONYU Chest Gear I",#FM
            "3143727513": "DLC TARONYU Chest Gear II",#FM
            "145354853": "DLC TARONYU Chest Gear III",#FM
            "1161560796": "DLC TARONYU Chest Gear IV",#FM
            "2529072337": "DLC TARONYU Leg Gear I",#FM
            "3155647284": "DLC TARONYU Leg Gear II",#FM
            "2697550098": "DLC TARONYU Leg Gear III",#FM
            "1591391960": "DLC TARONYU Leg Gear IV",#FM

            # DLC TSTEU Armor Set
            "209155874": "DLC TSTEU Head Gear I",#FM
            "1336514870": "DLC TSTEU Head Gear II",#FM
            "1312065276": "DLC TSTEU Head Gear III",#FM
            "1500118218": "DLC TSTEU Head Gear IV",#FM
            "285382675": "DLC TSTEU Chest Gear I",#FM
            "904822394": "DLC TSTEU Chest Gear II",#FM
            "824495264": "DLC TSTEU Chest Gear III",#FM
            "1960056897": "DLC TSTEU Chest Gear IV",#FM
            "263701867": "DLC TSTEU Leg Gear I",#FM
            "848846039": "DLC TSTEU Leg Gear II",#FM
            "2571396567": "DLC TSTEU Leg Gear III",#FM
            "1865591877": "DLC TSTEU Leg Gear IV",#FM
            
            # TIREA Armor Set
            "985254384": "DLC TIREA Head Gear IV",#FM
            "386149755": "DLC TIREA Chest Gear IV",#FM
            "216177023": "DLC TIREA Leg Gear IV",#FM
            "3843346967": "DLC TIREA Head Gear I",#FM
            "2311491761": "DLC TIREA Head Gear II",#FM
            "1026490230": "DLC TIREA Head Gear III",#FM
            "4167122214": "DLC TIREA Chest Gear I",#FM
            "4085348349": "DLC TIREA Chest Gear II",#FM
            "1111405866": "DLC TIREA Chest Gear III",#FM
            "3872677982": "DLC TIREA Leg Gear I",#FM
            "4109849936": "DLC TIREA Leg Gear II",#FM
            "3932036189": "DLC TIREA Leg Gear III",#FM
            
            # Multiplayer Na'vi Variants - Headwear
            "530792999": "MP Standard Avatar Braid",#FM
            "1700803530": "MP TSAMSIYU Head Gear",#FM
            "1809831741": "MP 'AWVEA TSAMSIYU Head Gear",#FM
            "3653380410": "MP NAWM Head Gear",#FM
            "2185175904": "MP NAWMA EYKTAN Head Gear",#FM
            "3643724686": "MP NAWMA TSAMSIYU Head Gear",#FM
            "3719163782": "MP EYKTAN Head Gear",#FM
            "3089741679": "MP NAWMA TARONYU Head Gear",#FM
            
            # Multiplayer Na'vi Variants - Torso
            "1456585305": "MP RDA-Issue Avatar Pack",#FM
            "2128543788": "MP TSAMSIYU Chest Gear",#FM
            "1885398235": "MP 'AWVEA TSAMSIYU Chest Gear",#FM
            "2427507012": "MP NAWM Chest Armor",#FM
            "1017757237": "MP NAWMA EYKTAN Chest Gear",#FM
            "1740132059": "MP NAWMA TSAMSIYU Chest Gear",#FM
            "1664840403": "MP EYKTAN Chest Gear",#FM
            "113191482": "MP NAWMA TARONYU Chest Gear",#FM
            
            # Multiplayer Na'vi Variants - Legs
            "2505428162": "MP RDA-Issue Avatar Pants",#FM
            "4129766097": "MP TSAMSIYU Leg Gear",#FM
            "4170767910": "MP 'AWVEA TSAMSIYU Leg Gear",#FM
            "1395959775": "MP NAWM Leg Armor",#FM
            "3435767277": "MP NAWMA EYKTAN Leg Gear",#FM
            "2547537155": "MP NAWMA TSAMSIYU Leg Gear",#FM
            "2472241419": "MP EYKTAN Leg Gear",#FM
            "4141822434": "MP NAWMA TARONYU Leg Gear",#FM
            
            # Na'vi Full Gear Sets (Torso Only)
            "2032708175": "RDA-Issue Avatar Full Gear",#FM
            "252528002": "TSAMSIYU Full Armor I",#FM
            "372743795": "'AWVEA TSAMSIYU Full Armor II",#FM
            "1129711996": "NAWM Full Armor III",#FM
            "2989529994": "EYKTAN Full Armor IV",#FM
            "1402662052": "NAWMA EYKTAN Full Armor IV",#FM
            "4192587225": "NAWMA TSAMSIYU Full Armor IV",#FM
            "2879322417": "NAWMA TARONYU Full Armor I",#FM
            "2997101248": "NAWMA TARONYU Full Armor II",#FM
            "295336182": "NAWMA TARONYU Full Armor III",#FM
            "667753227": "NAWMA TARONYU Full Armor IV",#FM
            "1854698207": "TARONYU Full Armor I",#FM
            "996344322": "TARONYU Full Armor II",#FM
            "1685658698": "TARONYU Full Armor III",#FM
            "868628882": "TARONYU Full Armor IV",#FM
            "2243676636": "TSTEU Full Armor I",#FM
            "1761171846": "TSTEU Full Armor II",#FM
            "2399125800": "TSTEU Full Armor III",#FM
            "437161312": "TSTEU Full Armor IV",#FM
            "2292562331": "TIREA Full Armor I",#FM
            "3486379662": "TIREA Full Armor II",#FM
            "2156101037": "TIREA Full Armor III",#FM
            "1235215492": "TIREA Full Armor IV",#FM
            "1786356450": "KARYU Full Armor IV",#FM
            
            # Multiplayer Na'vi Full Gear
            "4246865506": "MP RDA-Issue Avatar Full Gear",#FM
            "3152066193": "MP TSAMSIYU Full Armor",#FM
            "2732223840": "MP 'AWVEA TSAMSIYU Full Armor",#FM
            "3344737617": "MP NAWM Full Armor",#FM
            "3050817624": "MP NAWMA EYKTAN Full Armor",#FM
            "531163429": "MP NAWMA TSAMSIYU Full Armor",#FM
            "1417527158": "MP EYKTAN Full Armor",#FM
            "3339349152": "MP NAWMA TARONYU Full Armor I",#FM
            "3727734609": "MP NAWMA TARONYU Full Armor II",#FM
            "2533248945": "MP NAWMA TARONYU Full Armor III",#FM
            "1615540413": "MP NAWMA TARONYU Full Armor",#FM
            "3050137439": "MP NAWMA TARONYU Full Armor IV",#FM
            "499041501": "MP TARONYU Full Set",#FM
            "880177199": "MP TSTEU Full Armor",#FM
        }

    def _get_item_name(self, item_id: str) -> str:
        """Convert an item ID to its readable name"""
        return self.item_mappings.get(item_id, f"Unknown Item ({item_id})")

    def _get_faction_weapons(self, is_navi=False):
        """Get the list of weapons for a specific faction"""
        # Return appropriate weapon mappings based on faction
        if is_navi:
            weapon_ids = self._get_navi_weapon_ids()
        else:
            weapon_ids = self._get_rda_weapon_ids()
        
        all_weapons = {}
        for item_id in weapon_ids:
            if item_id in self.item_mappings:
                all_weapons[item_id] = self.item_mappings[item_id]
        
        return all_weapons

    def _get_navi_weapon_ids(self):
        """Get the list of Navi weapon IDs"""
        return [
            # Dual Blade
            "2740507591", "2917611312", "2813685095", "2948460035",
            # DLC Dual Blade
            "2285146948", "2257287091", "3543126973", "2007498681",
            # Crossbow
            "1662469074", "1839769381", "3400058396", "1514231420",
            # DLC Crossbow
            "3138212456", "2486913109", "2589205711", "1886472672",
            # M30 Machine Gun
            "1304439874", "1132447925", "982090295", "958613249",
            # ELITE M30 Machine Gun
            "818439597","1048019290", "172062103", "921966990",
            # Club
            "4093397293", "4249071066", "3879387803", "240531571",
            # DLC Axe
            "1958996617", "2689671946", "1639187137", "2934884349",
            # Fighting Staff
            "2255793432", "2295024111", "2986118748", "3960574385",
            # DLC Fighting Staff
            "1828119782", "1648951313", "3943944974", "3139393077",
            # Bow
            "291262189", "535013914", "2092736556", "371977402",
            # DLC Bow
            "1817446146", "1659626485", "1282693004", "435991093"
        ]

    def _get_rda_weapon_ids(self):
        """Get the list of RDA weapon IDs"""
        return [
            # Dual Wasp Pistol
            "1042188764", "815885611", "760079057", "999316102",
            # DLC Dual Wasp Pistols
            "3859060838", "3904601233", "102867538", "749353518",
            # Standard Issue Rifle
            "1130814347", "1306083196", "3628031700", "1146928137",
            # DLC Standard Issue Rifles
            "2850329205", "2807789186", "2194670470", "324172685",
            # Combat Shotgun
            "2313824646", "2270547313", "2789519003", "1919695864",
            # DLC Combat Shotguns
            "2664450350", "2423238105", "2120138529", "4289908838",
            # Assault Rifle
            "2397981034", "2152836509", "268371112", "466145020",
            # DLC Assault Rifles
            "3655372526", "3613354521", "3850194262", "2109370248",
            # M60 Machine Gun
            "85991974", "195020497", "1881065336", "1796958374",
            # DLC Machine Guns
            "2015914953", "1989644094", "1087779032", "1691104809",
            # Grenade Launcher
            "94681171", "186342564", "1349633617", "4018216358",
            # DLC Grenade Launchers
            "2157668310", "2384757537", "3441856033", "3043901684",
            # Flamethrower
            "2529862352", "2557822503", "609450705", "2288255787",
            # DLC Flamethrowers
            "3250873684", "3480977827", "3469816623", "3994460767",
            # Nail Gun
            "2548581230", "2572658585", "143378107", "1911864170",
            # DLC Nail Guns
            "2161255366", "2389559089", "3499218689", "4230631668"
        ]

    def _create_rda_armor_mappings(self):
        """Create mappings for RDA armor pieces by type"""
        self.rda_armor_sets = {
            "headwear": {
                # Base/Standard Armors
                "433486271": "Default RDA Head", 
                "2800661647": "TUSK Helmet I",  
                "2823901304": "WARTHOG Helmet II",
                "3753317026": "HYDRA Helmet III",
                "1593826001": "KODIAK Helmet IV",
                "4082430736": "TITAN Helmet IV",
                "403319592": "CENTAURI Helmet IV",
                "149499402": "MILITUM Helmet IV",
                "3980056687": "VIPER Helmet I",
                
                # E3 Exclusive
                "2507615751": "E3 RDA HELM",
                "666504347": "E3 Exotant Head",
                
                # Plaza Variants
                "1830604945": "(Plaza) ARTHURA Helmet I",
                "3717529612": "(Plaza) ARTHURA I Helmet I",
                "3542803707": "(Plaza) WARTHOG Helmet II",
                
                # DLC BRASHER
                "3005472419": "DLC BRASHER Helmet I", 
                "3064631211": "DLC BRASHER Helmet II", 
                "3228789267": "DLC BRASHER Helmet III", 
                "3818917462": "DLC BRASHER Helmet IV", 
                
                # DLC EXOTANT
                "707432217": "EXOTANT Helmet I", 
                "941983816": "EXOTANT Helmet II", 
                "4194195158": "EXOTANT Helmet III", 
                "3527939275": "EXOTANT Helmet IV", 
                
                # DLC MISHETICA
                "1563279247": "DLC MISHETICA Helmet I", 
                "4103047382": "DLC MISHETICA Helmet II", 
                "4001710741": "DLC MISHETICA Helmet III", 
                "1950293887": "DLC MISHETICA Helmet IV", 
                
                # Multiplayer Variants
                "141479065": "Default RDA Helmet",
                "525389396": "MP TUSK Helmet",
                "300886691": "MP WARTHOG Helmet",
                "3457132420": "MP HYDRA Helmet",
                "2253457575": "MP KODIAK Helmet",
                "737812838": "MP TITAN Helmet",
                "3232037214": "MP CENTAURI Helmet",
                "3494378620": "MP MILITUM Helmet",
                
                # Generic Categories
                "1633102956": "ACAT Head Gear", 
            },
            "torso": {
                # Base/Standard Armors
                "2818823188": "Default RDA Torso", 
                "2024422324": "TUSK Chest Armor I", 
                "1981144899": "WARTHOG Chest Armor II",
                "1851965193": "HYDRA Chest Armor III",
                "2716738620": "KODIAK Chest Armor IV",
                "205852157": "TITAN Chest Armor IV",
                "3877361093": "CENTAURI Chest Armor IV",
                "4160278759": "MILITUM Chest Armor IV",
                "3574042272": "VIPER Chest Armor I", 
                
                # E3 Exclusive
                "2628484515": "E3 RDA CHEST",
                "531856612": "E3 Exotant Torso",
                
                # Plaza Variants
                "1956713330": "(Plaza) ARTHURA Chest Armor I",
                "207655578": "(Plaza) ARTHURA I Chest Armor I",
                "48199277": "(Plaza) WARTHOG Chest Armor II",
                
                # DLC BRASHER
                "730661330": "DLC BRASHER Chest Armor I", 
                "2822640242": "DLC BRASHER Chest Armor II", 
                "1063425278": "DLC BRASHER Chest Armor III", 
                "1993326532": "DLC BRASHER Chest Armor IV", 
                
                # DLC EXOTANT
                "2995015784": "EXOTANT Chest Armor I", 
                "649139601": "EXOTANT Chest Armor II", 
                "116369467": "EXOTANT Chest Armor III", 
                "1193780569": "EXOTANT Chest Armor IV", 
                
                # DLC MISHETICA
                "3313721598": "DLC MISHETICA Chest Armor I", 
                "3927643407": "DLC MISHETICA Chest Armor II", 
                "294960248": "DLC MISHETICA Chest Armor III", 
                "3780161261": "DLC MISHETICA Chest Armor IV", 
                
                # Multiplayer Variants
                "2048911708": "MP Default RDA Chest Armor",
                "1762823826": "MP TUSK Chest Armor",
                "1739418213": "MP WARTHOG Chest Armor",
                "3162407489": "MP HYDRA Chest Armor",
                "407920359": "MP KODIAK Chest Armor",
                "3053156134": "MP TITAN Chest Armor",
                "1587916574": "MP CENTAURI Chest Armor",
                "1313253948": "MP MILITUM Chest Armor",
                
                # Full Gear Sets (Torso Only)
                "73022142": "RDA Standard Issue Full Armor",
                "2047018253": "TUSK Full Armor I",
                "2529656365": "VIPER Full Armor I",
                "1664737020": "WARTHOG Full Armor II",
                "1042585997": "HYDRA Full Armor III",
                "785085314": "TITAN Full Armor IV",
                "2271254608": "KODIAK Full Armor IV",
                "1639122250": "CENTAURI Full Armor IV",
                "3033145114": "MILITUM Full Armor IV",
                "3193262026": "BRASHER Full Armor IV",
                "2543713080": "EXOTANT Full Armor IV",
                "972384937": "MISHETICA Full Armor IV",
                "3245854685": "BRASHER Full Armor I",
                "708867294": "EXOTANT Full Armor I",
                "3313639392": "MISHETICA Full Armor I",
                "1583237298": "BRASHER Full Armor II",
                "230953782": "EXOTANT Full Armor II",
                "2321733749": "MISHETICA Full Armor II",
                "2944242316": "BRASHER Full Armor III",
                "1174097902": "EXOTANT Full Armor III",
                "2863266063": "MISHETICA Full Armor III",
                "663343731": "E3 TITAN Full Armor IV",
                "3435030896": "E3 EXOTANT Full Armor IV",
                
                # Multiplayer Full Gear
                "2152765075": "MP RDA Standard Full Armor",
                "1144369633": "MP VIPER Full Armor",
                "3471767070": "MP TUSK Full Armor",
                "3621006831": "MP WARTHOG Full Armor",
                "3123590560": "MP HYDRA Full Armor",
                "1630387372": "MP KODIAK Full Armor",
                "3364247422": "MP TITAN Full Armor",
                "2281578934": "MP CENTAURI Full Armor",
                "1384594406": "MP MILITUM Full Armor",
                "3503258363": "MP BRASHER Full Armor I",
                "1881585149": "MP BRASHER Full Armor II",
                "1227929200": "MP BRASHER Full Armor III",
                "1923449271": "MP BRASHER Full Armor IV",
                "1006158328": "MP EXOTANT Full Armor I",
                "599584377": "MP EXOTANT Full Armor II",
                "2746641170": "MP EXOTANT Full Armor III",
                "1533883717": "MP EXOTANT Full Armor IV",
                "3560614598": "MP MISHETICA Full Armor I",
                "2753176890": "MP MISHETICA Full Armor II",
                "1290067443": "MP MISHETICA Full Armor III",
                "4110787796": "MP MISHETICA Full Armor IV",
                
                # Generic Categories
                "1178592625": "ACAT Chest Armor",
            },
            "legs": {
                # Base/Standard Armors
                "1457212295": "Default RDA Legs", 
                "1949228588": "TUSK Leg Armor I", 
                "2056338139": "WARTHOG Leg Armor II",
                "2428117146": "HYDRA Leg Armor III",
                "2467333367": "KODIAK Leg Armor IV",
                "1052486966": "TITAN Leg Armor IV",
                "3588584718": "CENTAURI Leg Armor IV",
                "3305533484": "MILITUM Leg Armor IV",
                "1417888964": "VIPER Leg Armor I",
                
                # E3 Exclusive
                "694483043": "E3 RDA LEG",
                "1234921930": "E3 Exotant Legs",
                
                # Plaza Variants
                "765525764": "(Plaza) ARTHURA Leg Armor I",
                "3199333350": "(Plaza) ARTHURA I Leg Armor I",
                "2953713425": "(Plaza) WARTHOG Leg Armor II",
                
                # DLC BRASHER
                "3718956374": "DLC BRASHER Leg Armor I", 
                "2398239326": "DLC BRASHER Leg Armor II", 
                "228340789": "DLC BRASHER Leg Armor III", 
                "1675050996": "DLC BRASHER Leg Armor IV", 
                
                # DLC EXOTANT
                "1151571180": "EXOTANT Leg Armor I", 
                "8207805": "EXOTANT Leg Armor II", 
                "873531632": "EXOTANT Leg Armor III", 
                "1379870057": "EXOTANT Leg Armor IV", 
                
                # DLC MISHETICA
                "866428026": "DLC MISHETICA Leg Armor I", 
                "3436657955": "DLC MISHETICA Leg Armor II", 
                "594156723": "DLC MISHETICA Leg Armor III", 
                "4098371293": "DLC MISHETICA Leg Armor IV", 
                
                # Multiplayer Variants
                "4016386396": "MP Default RDA Leg Armor",
                "2894072922": "MP TUSK Leg Armor",
                "2722097325": "MP WARTHOG Leg Armor",
                "688151105": "MP HYDRA Leg Armor",
                "820586591": "MP KODIAK Leg Armor",
                "2638348702": "MP TITAN Leg Armor",
                "1981602214": "MP CENTAURI Leg Armor",
                "1728044164": "MP MILITUM Leg Armor",
                
                # Generic Categories
                "1002215802": "ACAT Leg Armor",
            }
        }

        # Create reverse mappings for looking up IDs by name
        self.rda_armor_ids = {
            slot_type: {name: id for id, name in items.items()}
            for slot_type, items in self.rda_armor_sets.items()
        }

    def _create_navi_armor_mappings(self):
        """Create mappings for Na'vi armor pieces by type"""
        self.navi_armor_sets = {
            "headwear": {
                            
                # Base/Standard Armors
                "236713729": "RDA-Issue Avatar Head",
                "3705555217": "TSAMSIYU Head Gear I",
                "3529616870": "'AWVEA TSAMSIYU Head Gear II",
                "3363478556": "NAWM Head Gear III",
                "84098544": "EYKTAN Head Gear IV",
                "1519513878": "NAWMA EYKTAN Head Gear IV",
                "25166328": "NAWMA TSAMSIYU Head Gear IV",
                
                # NAWMA TARONYU Series
                "2628269855": "NAWMA TARONYU Head Gear I",
                "2451035112": "NAWMA TARONYU Head Gear II",
                "797099877": "NAWMA TARONYU Head Gear III",
                "3932154789": "NAWMA TARONYU Head Gear IV",
                
                # DLC TARONYU
                "2508072600": "DLC TARONYU Head Gear I",
                "3240533717": "DLC TARONYU Head Gear II",
                "2008660537": "DLC TARONYU Head Gear III",
                "1753343575": "DLC TARONYU Head Gear IV",
                
                # DLC TSTEU
                "209155874": "DLC TSTEU Head Gear I",
                "1336514870": "DLC TSTEU Head Gear II",
                "1312065276": "DLC TSTEU Head Gear III",
                "1500118218": "DLC TSTEU Head Gear IV",
                
                # DLC TIREA
                "3843346967": "DLC TIREA Head Gear I",
                "2311491761": "DLC TIREA Head Gear II",
                "1026490230": "DLC TIREA Head Gear III",
                "985254384": "DLC TIREA Head Gear IV",
                
                # KARYU
                "2070955956": "KARYU Head Gear IV",
                
                # Multiplayer Variants
                "530792999": "MP Standard Avatar Braid",
                "1700803530": "MP TSAMSIYU Head Gear",
                "1809831741": "MP 'AWVEA TSAMSIYU Head Gear",
                "3653380410": "MP NAWM Head Gear",
                "2185175904": "MP NAWMA EYKTAN Head Gear",
                "3643724686": "MP NAWMA TSAMSIYU Head Gear",
                "3719163782": "MP EYKTAN Head Gear",
                "3089741679": "MP NAWMA TARONYU Head Gear",
            },
            "torso": {

                # Base/Standard Armors
                "2228061969": "RDA-Issue Avatar Torso",
                "1869067530": "TSAMSIYU Chest Gear I",
                "1641566717": "'AWVEA TSAMSIYU Chest Gear II",
                "1118628876": "NAWM Chest Gear III",
                "3666151432": "EYKTAN Chest Gear IV",
                "2232927470": "NAWMA EYKTAN Chest Gear IV",
                "3724948480": "NAWMA TSAMSIYU Chest Gear IV",
                
                # NAWMA TARONYU Series
                "3743365442": "NAWMA TARONYU Chest Gear I",
                "3516980661": "NAWMA TARONYU Chest Gear II",
                "974871842": "NAWMA TARONYU Chest Gear III",
                "884530381": "NAWMA TARONYU Chest Gear IV",
                
                # DLC TARONYU
                "2282473897": "DLC TARONYU Chest Gear I",
                "3143727513": "DLC TARONYU Chest Gear II",
                "145354853": "DLC TARONYU Chest Gear III",
                "1161560796": "DLC TARONYU Chest Gear IV",
                
                # DLC TSTEU
                "285382675": "DLC TSTEU Chest Gear I",
                "904822394": "DLC TSTEU Chest Gear II",
                "824495264": "DLC TSTEU Chest Gear III",
                "1960056897": "DLC TSTEU Chest Gear IV",
                
                # DLC TIREA
                "4167122214": "DLC TIREA Chest Gear I",
                "4085348349": "DLC TIREA Chest Gear II",
                "1111405866": "DLC TIREA Chest Gear III",
                "386149755": "DLC TIREA Chest Gear IV",
                
                # DLC KARYU
                "1711646853": "KARYU Chest Gear IV",
                
                # Multiplayer Variants
                "1456585305": "MP RDA-Issue Avatar Pack",
                "2128543788": "MP TSAMSIYU Chest Gear",
                "1885398235": "MP 'AWVEA TSAMSIYU Chest Gear",
                "2427507012": "MP NAWM Chest Armor",
                "1017757237": "MP NAWMA EYKTAN Chest Gear",
                "1740132059": "MP NAWMA TSAMSIYU Chest Gear",
                "1664840403": "MP EYKTAN Chest Gear",
                "113191482": "MP NAWMA TARONYU Chest Gear",
                
                # Full Gear Sets (Torso Only)
                "2032708175": "RDA-Issue Avatar Full Gear",
                "252528002": "TSAMSIYU Full Armor I",
                "372743795": "'AWVEA TSAMSIYU Full Armor II",
                "1129711996": "NAWM Full Armor III",
                "2989529994": "EYKTAN Full Armor IV",
                "1402662052": "NAWMA EYKTAN Full Armor IV",
                "4192587225": "NAWMA TSAMSIYU Full Armor IV",
                "2879322417": "NAWMA TARONYU Full Armor I",
                "2997101248": "NAWMA TARONYU Full Armor II",
                "295336182": "NAWMA TARONYU Full Armor III",
                "667753227": "NAWMA TARONYU Full Armor IV",
                "1854698207": "TARONYU Full Armor I",
                "996344322": "TARONYU Full Armor II",
                "1685658698": "TARONYU Full Armor III",
                "868628882": "TARONYU Full Armor IV",
                "2243676636": "TSTEU Full Armor I",
                "1761171846": "TSTEU Full Armor II",
                "2399125800": "TSTEU Full Armor III",
                "437161312": "TSTEU Full Armor IV",
                "2292562331": "TIREA Full Armor I",
                "3486379662": "TIREA Full Armor II",
                "2156101037": "TIREA Full Armor III",
                "1235215492": "TIREA Full Armor IV",
                "1786356450": "KARYU Full Armor IV",
                
                # Multiplayer Full Gear
                "4246865506": "MP RDA-Issue Avatar Full Gear",
                "3152066193": "MP TSAMSIYU Full Armor",
                "2732223840": "MP 'AWVEA TSAMSIYU Full Armor",
                "3344737617": "MP NAWM Full Armor",
                "3050817624": "MP NAWMA EYKTAN Full Armor",
                "531163429": "MP NAWMA TSAMSIYU Full Armor",
                "1417527158": "MP EYKTAN Full Armor",
                "3339349152": "MP NAWMA TARONYU Full Armor I",
                "3727734609": "MP NAWMA TARONYU Full Armor II",
                "2533248945": "MP NAWMA TARONYU Full Armor III",
                "1615540413": "MP NAWMA TARONYU Full Armor",
                "3050137439": "MP NAWMA TARONYU Full Armor IV",
                "499041501": "MP TARONYU Full Set",
                "880177199": "MP TSTEU Full Armor",
            },
            "legs": {
                
                # Base/Standard Armors
                "753645081": "RDA-Issue Avatar Legs",
                "780789927": "TSAMSIYU Leg Gear I",
                "540413008": "'AWVEA TSAMSIYU Leg Gear II",
                "3934969092": "NAWM Leg Gear III",
                "815973795": "EYKTAN Leg Gear IV",
                "1865419077": "NAWMA EYKTAN Leg Gear IV",
                "874641835": "NAWMA TSAMSIYU Leg Gear IV",
                
                # NAWMA TARONYU Series
                "4259766772": "NAWMA TARONYU Leg Gear I",
                "4082697475": "NAWMA TARONYU Leg Gear II",
                "406565443": "NAWMA TARONYU Leg Gear III",
                "3480671099": "NAWMA TARONYU Leg Gear IV",
                
                # DLC TARONYU
                "2529072337": "DLC TARONYU Leg Gear I",
                "3155647284": "DLC TARONYU Leg Gear II",
                "2697550098": "DLC TARONYU Leg Gear III",
                "1591391960": "DLC TARONYU Leg Gear IV",
                
                # DLC TSTEU
                "263701867": "DLC TSTEU Leg Gear I",
                "848846039": "DLC TSTEU Leg Gear II",
                "2571396567": "DLC TSTEU Leg Gear III",
                "1865591877": "DLC TSTEU Leg Gear IV",
                
                # DLC TIREA
                "3872677982": "DLC TIREA Leg Gear I",
                "4109849936": "DLC TIREA Leg Gear II",
                "3932036189": "DLC TIREA Leg Gear III",
                "216177023": "DLC TIREA Leg Gear IV",
                
                # DLC KARYU
                "2024863229": "DEV KARYU Leg Gear IV",
                
                # Multiplayer Variants
                "2505428162": "MP RDA-Issue Avatar Pants",
                "4129766097": "MP TSAMSIYU Leg Gear",
                "4170767910": "MP 'AWVEA TSAMSIYU Leg Gear",
                "1395959775": "MP NAWM Leg Armor",
                "3435767277": "MP NAWMA EYKTAN Leg Gear",
                "2547537155": "MP NAWMA TSAMSIYU Leg Gear",
                "2472241419": "MP EYKTAN Leg Gear",
                "4141822434": "MP NAWMA TARONYU Leg Gear",
            }
        }

        # Create reverse mappings for looking up IDs by name
        self.navi_armor_ids = {
            slot_type: {name: id for id, name in items.items()}
            for slot_type, items in self.navi_armor_sets.items()
        }
        
    # Essential event handlers and methods (simplified versions)
    def _on_face_selected(self, event=None):
        """Handle face selection and update image"""
        try:
            widget = self.entries["face"]
            face_value = widget.cget("text") if hasattr(widget, 'cget') else widget.get()
            
            if not face_value or face_value == "-":
                return
                
            parts = face_value.split()
            if len(parts) != 2:
                return
                
            gender, number = parts
            
            # Get pawn value to determine if human or avatar
            pawn_widget = self.entries.get("pawn")
            if pawn_widget:
                pawn_value = pawn_widget.get() if hasattr(pawn_widget, 'get') else pawn_widget.cget("text")
                # Pawn: "1" = Na'vi (Avatar), "2" = RDA (Human)
                is_avatar = (pawn_value == "Na'vi" or pawn_value == "1")
            else:
                is_avatar = False  # Default to human if pawn not found
            
            # Determine folder and filename based on pawn
            if is_avatar:
                folder = "avatar"
                filename = f"Avatar {gender} {number}.png"
            else:
                folder = "human"
                filename = f"{gender} {number}.png"
            
            image_path = os.path.join("Face_Images", folder, filename)
            
            if os.path.exists(image_path):
                original_image = Image.open(image_path)
                
                # Resize while preserving aspect ratio
                # Set max dimensions
                max_width = 150
                max_height = 150
                
                # Calculate scaling factor to fit within max dimensions
                width_ratio = max_width / original_image.width
                height_ratio = max_height / original_image.height
                scale_factor = min(width_ratio, height_ratio)
                
                # Calculate new dimensions
                new_width = int(original_image.width * scale_factor)
                new_height = int(original_image.height * scale_factor)
                
                # Resize with aspect ratio preserved
                resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(resized_image)
                
                if self.face_image_label:
                    self.face_image_label.configure(image=photo, text="")
                    self.face_image_label.image = photo  # Keep a reference
                    
                    # Mark as unsaved changes
                    self.main_window.unsaved_label.config(text="Unsaved Changes")
            else:
                if self.face_image_label:
                    self.face_image_label.configure(image='', text="No Image\nFound")
                self.logger.debug(f"Face image not found: {image_path}")
                        
        except Exception as e:
            self.logger.error(f"Error updating face image: {str(e)}", exc_info=True)
            if self.face_image_label:
                self.face_image_label.configure(image='', text=f"Error loading\nimage")

    def _mark_unsaved_changes(self, event=None):
        """Mark the save file as having unsaved changes"""
        try:
            if self.main_window.tree is None:
                show_error("Error", "No save file loaded. Please load a save file first.")
                if event and hasattr(event, 'widget') and isinstance(event.widget, ttk.Combobox):
                    event.widget.selection_clear()
                    return "break"
                return
                
            self.main_window.unsaved_label.config(text="Unsaved Changes")
        except Exception as e:
            self.logger.error(f"Error marking unsaved changes: {str(e)}", exc_info=True)

    def _on_weapon_selected(self, event, slot_index):
        """Handle weapon selection for RDA - updated for composite rendering"""
        if self.main_window.tree is None:
            show_error("Error", "No save file loaded. Please load a save file first.")
            event.widget.set("-Empty-")
            return
            
        combo = event.widget
        selected_weapon = combo.get()
        
        # Handle empty selection
        if selected_weapon == "-Empty-":
            # Clear this weapon from composite
            faction_key = 'rda'
            if hasattr(self, 'weapon_preview_labels') and faction_key in self.weapon_preview_labels:
                if slot_index in self.weapon_preview_labels[faction_key]:
                    label = self.weapon_preview_labels[faction_key][slot_index]
                    if hasattr(label, 'weapon_frames') and slot_index in label.weapon_frames:
                        del label.weapon_frames[slot_index]
            # Re-render composite without this weapon (no force regenerate)
            self._render_composite_weapons(is_navi=False, force_regenerate=False)
        else:
            # Find weapon ID and load into composite
            weapon_id = None
            for item_id, item_name in self.weapon_slots[slot_index]["all_weapons"].items():
                if item_name == selected_weapon:
                    weapon_id = item_id
                    break
            
            if weapon_id:
                self._load_weapon_image(weapon_id, slot_index, is_navi=False)
        
        # Update the XML
        profile = self.main_window.tree.getroot().find("PlayerProfile")
        if profile is None:
            return
            
        if selected_weapon != "-Empty-":
            weapon_id = None
            for item_id, item_name in self.weapon_slots[slot_index]["all_weapons"].items():
                if item_name == selected_weapon:
                    weapon_id = item_id
                    break
            
            if weapon_id:
                xml_slot = {0: 3, 1: 0, 2: 1, 3: 2}.get(slot_index, slot_index)
                self._update_weapon(profile, xml_slot, weapon_id, is_navi=False)
                self.main_window.unsaved_label.config(text="Unsaved Changes")

    def _on_navi_weapon_selected(self, event, slot_index):
        """Handle weapon selection for Na'vi - updated for composite rendering"""
        if self.main_window.tree is None:
            show_error("Error", "No save file loaded. Please load a save file first.")
            event.widget.set("-Empty-")
            return
            
        combo = event.widget
        selected_weapon = combo.get()
        
        # Handle empty selection
        if selected_weapon == "-Empty-":
            # Clear this weapon from composite
            faction_key = 'navi'
            if hasattr(self, 'weapon_preview_labels') and faction_key in self.weapon_preview_labels:
                if slot_index in self.weapon_preview_labels[faction_key]:
                    label = self.weapon_preview_labels[faction_key][slot_index]
                    if hasattr(label, 'weapon_frames') and slot_index in label.weapon_frames:
                        del label.weapon_frames[slot_index]
            # Re-render composite without this weapon (no force regenerate)
            self._render_composite_weapons(is_navi=True, force_regenerate=False)
        else:
            # Find weapon ID and load into composite
            weapon_id = None
            for item_id, item_name in self.navi_weapon_slots[slot_index]["all_weapons"].items():
                if item_name == selected_weapon:
                    weapon_id = item_id
                    break
            
            if weapon_id:
                self._load_weapon_image(weapon_id, slot_index, is_navi=True)
        
        # Update the XML
        profile = self.main_window.tree.getroot().find("PlayerProfile")
        if profile is None:
            return
            
        if selected_weapon != "-Empty-":
            weapon_id = None
            for item_id, item_name in self.navi_weapon_slots[slot_index]["all_weapons"].items():
                if item_name == selected_weapon:
                    weapon_id = item_id
                    break
            
            if weapon_id:
                xml_slot = {0: 3, 1: 0, 2: 1, 3: 2}.get(slot_index, slot_index)
                self._update_weapon(profile, xml_slot, weapon_id, is_navi=True)
                self.main_window.unsaved_label.config(text="Unsaved Changes")

    def create_compact_armor_section(self, parent, is_navi=False):
        """Create compact armor section with layered PNG preview"""
        armor_container = ttk.Frame(parent)
        armor_container.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        # Split into left (controls) and right (preview) sections
        left_section = ttk.Frame(armor_container)
        left_section.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_section = ttk.Frame(armor_container)
        right_section.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)  # Changed expand=False to expand=True
        
        # Create armor mappings
        if is_navi:
            if not hasattr(self, 'navi_armor_sets'):
                self._create_navi_armor_mappings()
            armor_sets = self.navi_armor_sets
            armor_dropdowns = self.navi_armor_dropdowns
            preview_labels = self.navi_armor_preview_labels
        else:
            if not hasattr(self, 'rda_armor_sets'):
                self._create_rda_armor_mappings()
            armor_sets = self.rda_armor_sets
            armor_dropdowns = self.armor_dropdowns
            preview_labels = self.armor_preview_labels
        
        # Armor slots with nicer display names
        armor_slots = [
            ("headwear", "Head"),
            ("torso", "Torso"),
            ("legs", "Legs")
        ]
        
        # Outfit Manager Button - SMALLER
        outfit_button_frame = ttk.Frame(left_section)
        outfit_button_frame.pack(fill=tk.X, pady=(0, 10))
        
        outfit_btn = ttk.Button(outfit_button_frame, text="💾 Outfit Manager", width=20)
        self._wrap_button_with_sound(outfit_btn, lambda: self._open_outfit_manager(is_navi))
        outfit_btn.pack(side=tk.LEFT)

        # Add spacer at the top to push armor boxes down
        ttk.Frame(left_section, height=50).pack(side=tk.TOP)
                
        # Create armor dropdowns on the left
        for slot_id, slot_name in armor_slots:
            # Compact control frame
            control_frame = ttk.Frame(left_section)
            control_frame.pack(fill=tk.X, pady=12)
            
            # Slot label (small)
            ttk.Label(control_frame, text=f"{slot_name}:", font=('Segoe UI', 9, 'bold'), width=6).pack(side=tk.LEFT, padx=(0, 8))
            
            # Armor dropdown (BIGGER and LONGER)
            values = list(armor_sets[slot_id].values())
            combo = ttk.Combobox(control_frame, values=values, state="readonly", 
                            font=('Segoe UI', 10), width=40, height=10)
            combo.set("-Empty-")
            combo.pack(side=tk.LEFT, padx=(0, 8))
            block_combobox_mousewheel(combo)
            self._add_hover_sound_to_combobox(combo)
            
            # Bind events with preview loading
            if is_navi:
                combo.bind('<<ComboboxSelected>>', lambda e, slot=slot_id: self._on_navi_armor_selected(e, slot))
            else:
                combo.bind('<<ComboboxSelected>>', lambda e, slot=slot_id: self._on_armor_selected(e, slot))
            
            armor_dropdowns[slot_id] = combo
        
        # Create preview area on the right - COMPOSITE VIEW (BIGGER)
        right_section.grid_columnconfigure(0, weight=1)
        right_section.grid_rowconfigure(0, weight=1)
        
        # Single composite preview frame - BIGGER
        composite_frame = ttk.LabelFrame(right_section, text="Armor Preview", padding=5)
        composite_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Configure the frame to expand
        composite_frame.grid_columnconfigure(0, weight=1)
        composite_frame.grid_rowconfigure(0, weight=1)
        
        composite_label = ttk.Label(composite_frame, text="No Armor\nEquipped", 
                                    width=20, anchor="center", relief="sunken")
        composite_label.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Store the composite label
        if not hasattr(self, 'composite_preview_labels'):
            self.composite_preview_labels = {}
        faction_key = 'navi' if is_navi else 'rda'
        self.composite_preview_labels[faction_key] = composite_label
        
        # Create hidden individual preview labels for internal tracking
        for slot_id, slot_name in armor_slots:
            # These labels won't be displayed but will hold the individual armor images
            image_label = ttk.Label(composite_frame)  # Create but don't pack
            preview_labels[slot_id] = image_label

    def _on_armor_selected(self, event, slot_type):
        """Handle armor selection for RDA with layered PNG preview"""
        if self.main_window.tree is None:
            show_error("Error", "No save file loaded. Please load a save file first.")
            event.widget.set("-Empty-")
            return
            
        combo = event.widget
        selected_armor = combo.get()
        
        # Handle empty selection
        if selected_armor == "-Empty-":
            # Clear the armor image for this slot
            if slot_type in self.armor_preview_labels:
                preview_label = self.armor_preview_labels[slot_type]
                if hasattr(preview_label, 'armor_images') and slot_type in preview_label.armor_images:
                    del preview_label.armor_images[slot_type]
            # Re-render composite without this piece
            self._render_composite_armor(is_navi=False)
        else:
            # Find armor ID and load preview
            armor_id = self.rda_armor_ids[slot_type].get(selected_armor)
            if armor_id:
                self._load_armor_image(armor_id, slot_type, is_navi=False)
        
        # Update the XML
        profile = self.main_window.tree.getroot().find("PlayerProfile")
        if profile is None:
            return
            
        success = self._update_armor(profile, slot_type, selected_armor, is_navi=False)
        
        if success:
            self.main_window.unsaved_label.config(text="Unsaved Changes")

    def _on_navi_armor_selected(self, event, slot_type):
        """Handle armor selection for Na'vi with layered PNG preview"""
        if self.main_window.tree is None:
            show_error("Error", "No save file loaded. Please load a save file first.")
            event.widget.set("-Empty-")
            return
            
        combo = event.widget
        selected_armor = combo.get()
        
        # Handle empty selection
        if selected_armor == "-Empty-":
            # Clear the armor image for this slot
            if slot_type in self.navi_armor_preview_labels:
                preview_label = self.navi_armor_preview_labels[slot_type]
                if hasattr(preview_label, 'armor_images') and slot_type in preview_label.armor_images:
                    del preview_label.armor_images[slot_type]
            # Re-render composite without this piece
            self._render_composite_armor(is_navi=True)
        else:
            # Find armor ID and load preview
            armor_id = self.navi_armor_ids[slot_type].get(selected_armor)
            if armor_id:
                self._load_armor_image(armor_id, slot_type, is_navi=True)
        
        # Update the XML
        profile = self.main_window.tree.getroot().find("PlayerProfile")
        if profile is None:
            return
            
        success = self._update_armor(profile, slot_type, selected_armor, is_navi=True)
        
        if success:
            self.main_window.unsaved_label.config(text="Unsaved Changes")

    def _toggle_infinite_ammo(self, event, slot_index, is_navi=False):
        """Handle toggling infinite ammo for a weapon"""
        try:
            if self.main_window.tree is None:
                show_error("Error", "No save file loaded. Please load a save file first.")
                return
                
            slot_data = self.navi_weapon_slots[slot_index] if is_navi else self.weapon_slots[slot_index]
            weapon_name = slot_data["dropdown"].get()
            
            if weapon_name == "-Empty-":
                return
            
            # Find weapon ID
            weapon_id = None
            for id, name in slot_data["all_weapons"].items():
                if name == weapon_name:
                    weapon_id = id
                    break
            
            if weapon_id is None:
                return
            
            # Check if this is a melee or inherently infinite weapon
            is_melee = any(melee_kw in weapon_name.lower() for melee_kw in 
                        ["club", "blade", "axe", "staff", "spear", "knife", "sword"])
            is_inherent_infinite = any(pistol_term in weapon_name.lower() for pistol_term in ["wasp pistol"])
            
            if is_melee or is_inherent_infinite:
                slot_data["infinite_var"].set(True)
                return
            
            # Apply infinite ammo toggle after a short delay
            self.parent.after(50, lambda: self._apply_infinite_ammo(slot_index, is_navi, weapon_id))
            
        except Exception as e:
            self.logger.error(f"Error toggling infinite ammo: {str(e)}")
            show_error("Error", f"Failed to toggle infinite ammo: {str(e)}")

    def _apply_infinite_ammo(self, slot_index, is_navi, weapon_id):
        """Apply the infinite ammo setting by maxing out ammo count"""
        try:
            slot_data = self.navi_weapon_slots[slot_index] if is_navi else self.weapon_slots[slot_index]
            infinite_enabled = slot_data["infinite_var"].get()
            
            if self.main_window.tree is not None:
                profile = self.main_window.tree.getroot().find("PlayerProfile")
                if profile is not None:
                    possessions_element = "Possessions_Avatar" if is_navi else "Possessions_Soldier"
                    possession_container = profile.find(possessions_element)
                    
                    if possession_container is None:
                        return
                            
                    equipped = possession_container.find("EquippedWeapons")
                    if equipped is None:
                        return
                            
                    slots = equipped.findall("Slot")
                    if slot_index >= len(slots):
                        return
                            
                    poss_idx = slots[slot_index].get("MainHand_PossIdx", "-1")
                    if poss_idx == "-1":
                        return
                            
                    possessions = possession_container.find("Posessions")
                    if possessions is None:
                        return
                    
                    # Find the weapon
                    weapon_poss = None
                    for poss in possessions.findall("Poss"):
                        if poss.get("Index") == poss_idx:
                            weapon_poss = poss
                            break
                    
                    if weapon_poss is None:
                        return
                    
                    # Get the ammo type (but don't change it)
                    ammo_type = weapon_poss.get("crc_AmmoType", "4294967295")
                    
                    # Update UI
                    ammo_entry = slot_data["ammo_entry"]
                    
                    if infinite_enabled:
                        # ✅ ONLY update the weapon's NbInStack, not the separate ammo item
                        weapon_poss.set("NbInStack", "999999")
                        
                        # Ensure the ammo item exists in inventory (but don't modify its NbInStack)
                        if ammo_type != "4294967295":
                            ammo_exists = False
                            for poss in possessions.findall("Poss"):
                                if poss.get("crc_ItemID") == ammo_type:
                                    ammo_exists = True
                                    break
                            
                            # If ammo doesn't exist, create it with normal amount
                            if not ammo_exists:
                                self._ensure_ammo_exists(possessions, ammo_type, "500")
                        
                        # Update UI to show infinity symbol
                        ammo_entry.delete(0, tk.END)
                        ammo_entry.insert(0, "∞")
                        ammo_entry.configure(state="disabled")
                        
                        self.logger.debug(f"Set infinite ammo for weapon {weapon_id} (weapon NbInStack = 999999)")
                    else:
                        # Restore normal ammo count for the weapon
                        weapon_poss.set("NbInStack", "1")  # Weapons typically have NbInStack="1"
                        
                        ammo_entry.delete(0, tk.END)
                        ammo_entry.insert(0, "500")
                        ammo_entry.configure(state="normal")
                        
                        self.logger.debug(f"Reset ammo to normal for weapon {weapon_id}")
                    
                    self.main_window.unsaved_label.config(text="Unsaved Changes")
        
        except Exception as e:
            self.logger.error(f"Error applying infinite ammo: {str(e)}", exc_info=True)

    def _update_ammo_value(self, event, slot_index, is_navi=False):
        """Update the ammo value in the XML when changed in the UI"""
        try:
            if self.main_window.tree is None:
                show_error("Error", "No save file loaded. Please load a save file first.")
                ammo_entry = self.navi_weapon_slots[slot_index]["ammo_entry"] if is_navi else self.weapon_slots[slot_index]["ammo_entry"]
                ammo_entry.delete(0, tk.END)
                ammo_entry.insert(0, "0")
                return
                
            ammo_entry = self.navi_weapon_slots[slot_index]["ammo_entry"] if is_navi else self.weapon_slots[slot_index]["ammo_entry"] 
            new_ammo = ammo_entry.get()
            
            # Skip if disabled (infinite ammo)
            if str(ammo_entry.cget('state')) == 'disabled':
                return
            
            try:
                new_ammo = int(new_ammo)
            except ValueError:
                return
                                        
            # Update the XML
            profile = self.main_window.tree.getroot().find("PlayerProfile")
            if profile is not None:
                self._update_ammo_directly(profile, is_navi, slot_index, new_ammo)
                self.main_window.unsaved_label.config(text="Unsaved Changes")
                
        except Exception as e:
            show_error("Error", f"Failed to update ammo value: {str(e)}")

    def _reset_weapon_ammo(self):
        """Reset all weapons to their original ammo types"""
        if self.main_window.tree is None:
            show_error("Error", "No save file loaded. Please load a save file first.")
            return
        
        try:
            profile = self.main_window.tree.getroot().find("PlayerProfile")
            if profile is None:
                show_error("Error", "PlayerProfile not found in save file.")
                return
            
            total_reset = 0
            
            # Reset RDA weapons
            soldier = profile.find("Possessions_Soldier")
            if soldier is not None:
                possessions = soldier.find("Posessions")
                if possessions is not None:
                    reset_count = self._reset_faction_weapon_ammo(possessions, is_navi=False)
                    total_reset += reset_count
                    self.logger.info(f"Reset {reset_count} RDA weapons")
            
            # Reset Na'vi weapons
            avatar = profile.find("Possessions_Avatar")
            if avatar is not None:
                possessions = avatar.find("Posessions")
                if possessions is not None:
                    reset_count = self._reset_faction_weapon_ammo(possessions, is_navi=True)
                    total_reset += reset_count
                    self.logger.info(f"Reset {reset_count} Na'vi weapons")
            
            # Refresh the weapon displays
            self._update_loadout_display(profile)
            self._update_navi_loadout_display(profile)
            
            # Mark changes as unsaved
            if total_reset > 0:
                self.main_window.unsaved_label.config(text="Unsaved Changes")
                show_success("Reset Complete", f"Successfully reset ammo types for {total_reset} weapons.")
            else:
                show_info("No Weapons Found", "No weapons found to reset.")
            
            self.logger.info(f"Weapon ammo reset completed. Total reset: {total_reset}")
            
        except Exception as e:
            self.logger.error(f"Error resetting weapon ammo: {str(e)}", exc_info=True)
            show_error("Error", f"Failed to reset weapon ammo: {str(e)}")

    def _reset_faction_weapon_ammo(self, possessions, is_navi=False):
        """Reset weapon ammo types for a specific faction"""
        try:
            reset_count = 0
            
            # Get all weapon IDs for this faction
            weapon_ids = set(self._get_navi_weapon_ids() if is_navi else self._get_rda_weapon_ids())
            
            # Find all weapon possessions and reset their ammo types
            for poss in possessions.findall("Poss"):
                item_id = poss.get("crc_ItemID")
                
                # Check if this is a weapon
                if item_id in weapon_ids:
                    # Get the correct ammo type for this weapon
                    correct_ammo_type = self._get_ammo_type_for_weapon(item_id)
                    current_ammo_type = poss.get("crc_AmmoType", "4294967295")
                    current_nb_in_stack = poss.get("NbInStack", "1")
                    
                    # Only reset if something is different
                    needs_reset = False
                    
                    # Check if ammo type is wrong
                    if current_ammo_type != correct_ammo_type:
                        needs_reset = True
                    
                    # Check if weapon has infinite ammo (NbInStack = 999999) and shouldn't
                    if current_nb_in_stack == "999999":
                        needs_reset = True
                    
                    if needs_reset:
                        old_ammo = current_ammo_type
                        old_stack = current_nb_in_stack
                        
                        # Reset ammo type to correct value
                        poss.set("crc_AmmoType", correct_ammo_type)
                        
                        # Reset weapon's NbInStack to 1 (normal weapon stack size)
                        poss.set("NbInStack", "1")
                        
                        # Set reasonable clip size
                        poss.set("NbInClip", "100")
                        
                        # Ensure the ammo exists in inventory with normal amount
                        if correct_ammo_type != "4294967295":
                            self._ensure_ammo_exists(possessions, correct_ammo_type, "500")
                        
                        weapon_name = self._get_item_name(item_id)
                        self.logger.debug(f"Reset {weapon_name}: ammo type {old_ammo} -> {correct_ammo_type}, NbInStack {old_stack} -> 1")
                        reset_count += 1
            
            return reset_count
            
        except Exception as e:
            self.logger.error(f"Error resetting faction weapon ammo: {str(e)}", exc_info=True)
            return 0
        
    def _remove_duplicate_items(self):
        """Remove duplicate items from inventory"""
        if self.main_window.tree is None:
            show_error("Error", "No save file loaded. Please load a save file first.")
            return
        
        try:
            profile = self.main_window.tree.getroot().find("PlayerProfile")
            if profile is None:
                show_error("Error", "PlayerProfile not found in save file.")
                return
            
            total_removed = 0
            
            # Process RDA possessions
            soldier = profile.find("Possessions_Soldier")
            if soldier is not None:
                possessions = soldier.find("Posessions")
                if possessions is not None:
                    removed = self._remove_duplicates_from_possessions(possessions, "RDA")
                    total_removed += removed
            
            # Process Na'vi possessions
            avatar = profile.find("Possessions_Avatar")
            if avatar is not None:
                possessions = avatar.find("Posessions")
                if possessions is not None:
                    removed = self._remove_duplicates_from_possessions(possessions, "Na'vi")
                    total_removed += removed
            
            # Mark changes as unsaved
            if total_removed > 0:
                self.main_window.unsaved_label.config(text="Unsaved Changes")
                show_success("Duplicates Removed", f"Successfully removed {total_removed} duplicate items from inventory.")
            else:
                show_info("No Duplicates", "No duplicate items found in inventory.")
            
            self.logger.info(f"Duplicate removal completed. Total removed: {total_removed}")
            
        except Exception as e:
            self.logger.error(f"Error removing duplicates: {str(e)}", exc_info=True)
            show_error("Error", f"Failed to remove duplicates: {str(e)}")

    def _remove_duplicates_from_possessions(self, possessions, faction_name):
        """Remove duplicate items from a possessions element"""
        try:
            # Track items we've seen: crc_ItemID -> first Poss element
            seen_items = {}
            items_to_remove = []
            
            # Find duplicates
            for poss in possessions.findall("Poss"):
                item_id = poss.get("crc_ItemID")
                
                if item_id in seen_items:
                    # This is a duplicate - mark for removal
                    items_to_remove.append(poss)
                    self.logger.debug(f"Found duplicate {faction_name} item: {self._get_item_name(item_id)} (ID: {item_id})")
                else:
                    # First occurrence - track it
                    seen_items[item_id] = poss
            
            # Remove the duplicates
            for poss in items_to_remove:
                possessions.remove(poss)
            
            removed_count = len(items_to_remove)
            
            if removed_count > 0:
                # Re-index all remaining possessions to maintain sequential indices
                self._reindex_possessions(possessions)
                self.logger.info(f"Removed {removed_count} duplicate {faction_name} items")
            
            return removed_count
            
        except Exception as e:
            self.logger.error(f"Error removing duplicates from {faction_name} possessions: {str(e)}", exc_info=True)
            return 0

    def _reindex_possessions(self, possessions):
        """Re-index possession items to be sequential starting from 0"""
        try:
            all_poss = possessions.findall("Poss")
            
            # Sort by current index to maintain relative order
            sorted_poss = sorted(all_poss, key=lambda p: int(p.get("Index", "0")))
            
            # Re-assign indices sequentially
            for new_index, poss in enumerate(sorted_poss):
                old_index = poss.get("Index")
                poss.set("Index", str(new_index))
                if old_index != str(new_index):
                    self.logger.debug(f"Re-indexed item from {old_index} to {new_index}")
            
            self.logger.info(f"Re-indexed {len(sorted_poss)} possessions")
            
        except Exception as e:
            self.logger.error(f"Error re-indexing possessions: {str(e)}", exc_info=True)

    def _add_all_rda_dlc_items(self):
        """Add all RDA DLC items to inventory - WORKING IMPLEMENTATION"""
        if self.main_window.tree is None:
            show_error("Error", "No save file loaded. Please load a save file first.")
            return
        
        try:
            profile = self.main_window.tree.getroot().find("PlayerProfile")
            if profile is None:
                show_error("Error", "PlayerProfile not found in save file.")
                return
            
            # Find or create RDA possessions
            soldier = profile.find("Possessions_Soldier")
            if soldier is None:
                soldier = ET.SubElement(profile, "Possessions_Soldier")
            
            possessions = soldier.find("Posessions")
            if possessions is None:
                possessions = ET.SubElement(soldier, "Posessions")
            
            # Get all RDA DLC item IDs
            rda_dlc_items = [
                # DLC WARLOCK Dual Wasp Pistols
                "3859060838", "3904601233", "102867538", "749353518",
                # DLC ARGO Standard Issue Rifles
                "2850329205", "2807789186", "2194670470", "324172685",
                # DLC SIGNET Combat Shotguns
                "2664450350", "2423238105", "2120138529", "4289908838",
                # DLC BARRO Assault Rifles
                "3655372526", "3613354521", "3850194262", "2109370248",
                # DLC STELLAR M60 Machine Guns
                "2015914953", "1989644094", "1087779032", "1691104809",
                # DLC CRUSHER Grenade Launchers
                "2157668310", "2384757537", "3441856033", "3043901684",
                # DLC BUDDY Flamethrowers
                "3250873684", "3480977827", "3469816623", "3994460767",
                # DLC DENT Nail Guns
                "2161255366", "2389559089", "3499218689", "4230631668",
                # DLC BRASHER Armor Sets
                "3005472419", "730661330", "3718956374",     # BRASHER I
                "3064631211", "2822640242", "2398239326",    # BRASHER II
                "3228789267", "1063425278", "228340789",     # BRASHER III
                "3818917462", "1993326532", "1675050996",    # BRASHER IV
                # DLC MISHETICA Armor Sets
                "1563279247", "3313721598", "866428026",     # MISHETICA I
                "4103047382", "3927643407", "3436657955",    # MISHETICA II
                "4001710741", "294960248", "594156723",      # MISHETICA III
                "1950293887", "3780161261", "4098371293",     # MISHETICA IV
                # E3 Exotant Armor Set
                "666504347", "531856612", "1234921930",  
                # Tusk Armor set
                "2800661647", "2024422324", "1949228588",
                # Default RDA Armor Set
                "433486271", "2818823188", "1457212295",
            ]
            
            # Get existing item IDs to avoid duplicates
            existing_items = set()
            for poss in possessions.findall("Poss"):
                existing_items.add(poss.get("crc_ItemID"))
            
            # Find next available index
            existing_indices = [int(poss.get("Index", "0")) for poss in possessions.findall("Poss")]
            next_index = 0
            while next_index in existing_indices:
                next_index += 1
            
            items_added = 0
            
            # Add each DLC item if it doesn't already exist
            for item_id in rda_dlc_items:
                if item_id not in existing_items:
                    # Create new possession
                    new_poss = ET.SubElement(possessions, "Poss")
                    new_poss.set("Index", str(next_index))
                    new_poss.set("crc_ItemID", item_id)
                    new_poss.set("NbInStack", "1")
                    new_poss.set("NbInClip", "0")
                    
                    # Set appropriate ammo type
                    ammo_type = self._get_ammo_type_for_weapon(item_id)
                    new_poss.set("crc_AmmoType", ammo_type)
                    new_poss.set("NoveltyState", "2")
                    
                    # Copy formatting from existing items
                    other_poss = possessions.find("Poss")
                    if other_poss is not None and hasattr(other_poss, 'tail'):
                        new_poss.tail = other_poss.tail
                    
                    self.logger.debug(f"Added RDA DLC item: {self._get_item_name(item_id)} (ID: {item_id})")
                    items_added += 1
                    next_index += 1
                    
                    # Update existing items set
                    existing_items.add(item_id)
            
            # Mark changes as unsaved
            self.main_window.unsaved_label.config(text="Unsaved Changes")
            
            if items_added > 0:
                show_success("DLC Items Added", f"Successfully added {items_added} RDA DLC items to inventory.")
            else:
                show_info("No Items Added", "All RDA DLC items are already in your inventory.")
            
            self.logger.info(f"RDA DLC items addition completed. Added: {items_added}")
            
        except Exception as e:
            self.logger.error(f"Error adding RDA DLC items: {str(e)}", exc_info=True)
            show_error("Error", f"Failed to add RDA DLC items: {str(e)}")

    def _add_all_navi_dlc_items(self):
        """Add all Na'vi DLC items to inventory - WORKING IMPLEMENTATION"""
        if self.main_window.tree is None:
            show_error("Error", "No save file loaded. Please load a save file first.")
            return
        
        try:
            profile = self.main_window.tree.getroot().find("PlayerProfile")
            if profile is None:
                show_error("Error", "PlayerProfile not found in save file.")
                return
            
            # Find or create Na'vi possessions
            avatar = profile.find("Possessions_Avatar")
            if avatar is None:
                avatar = ET.SubElement(profile, "Possessions_Avatar")
            
            possessions = avatar.find("Posessions")
            if possessions is None:
                possessions = ET.SubElement(avatar, "Posessions")
            
            # Get all Na'vi DLC item IDs
            navi_dlc_items = [
                # DLC Tanhì Dual Blade
                "2285146948", "2257287091", "3543126973", "2007498681",
                # DLC PXI Crossbow
                "3138212456", "2486913109", "2589205711", "1886472672",
                # DLC Ikran Axe
                "1958996617", "2689671946", "1639187137", "2934884349",
                # DLC Hufwe Fighting Staff
                "1828119782", "1648951313", "3943944974", "3139393077",
                # DLC RAWKE Bow
                "1817446146", "1659626485", "1282693004", "435991093",
                # DLC TSTEU Armor Sets
                "1336514870", "904822394", "848846039",      # TSTEU II
                "1312065276", "824495264", "2571396567",     # TSTEU III
                "1500118218", "1960056897", "1865591877",    # TSTEU IV
                # DLC TARONYU Armor Sets
                "3240533717", "3143727513", "3155647284",    # TARONYU II
                "2008660537", "145354853", "2697550098",     # TARONYU III
                "1753343575", "1161560796", "1591391960"     # TARONYU IV
                # TSAMSIYU Armor Set
                "3705555217", "1869067530", "780789927",
            ]
            
            # Get existing item IDs to avoid duplicates
            existing_items = set()
            for poss in possessions.findall("Poss"):
                existing_items.add(poss.get("crc_ItemID"))
            
            # Find next available index
            existing_indices = [int(poss.get("Index", "0")) for poss in possessions.findall("Poss")]
            next_index = 0
            while next_index in existing_indices:
                next_index += 1
            
            items_added = 0
            
            # Add each DLC item if it doesn't already exist
            for item_id in navi_dlc_items:
                if item_id not in existing_items:
                    # Create new possession
                    new_poss = ET.SubElement(possessions, "Poss")
                    new_poss.set("Index", str(next_index))
                    new_poss.set("crc_ItemID", item_id)
                    new_poss.set("NbInStack", "1")
                    new_poss.set("NbInClip", "0")
                    
                    # Set appropriate ammo type
                    ammo_type = self._get_ammo_type_for_weapon(item_id)
                    new_poss.set("crc_AmmoType", ammo_type)
                    new_poss.set("NoveltyState", "2")
                    
                    # Copy formatting from existing items
                    other_poss = possessions.find("Poss")
                    if other_poss is not None and hasattr(other_poss, 'tail'):
                        new_poss.tail = other_poss.tail
                    
                    self.logger.debug(f"Added Na'vi DLC item: {self._get_item_name(item_id)} (ID: {item_id})")
                    items_added += 1
                    next_index += 1
                    
                    # Update existing items set
                    existing_items.add(item_id)
            
            # Mark changes as unsaved
            self.main_window.unsaved_label.config(text="Unsaved Changes")
            
            if items_added > 0:
                show_success("DLC Items Added", f"Successfully added {items_added} Na'vi DLC items to inventory.")
            else:
                show_info("No Items Added", "All Na'vi DLC items are already in your inventory.")
            
            self.logger.info(f"Na'vi DLC items addition completed. Added: {items_added}")
            
        except Exception as e:
            self.logger.error(f"Error adding Na'vi DLC items: {str(e)}", exc_info=True)
            show_error("Error", f"Failed to add Na'vi DLC items: {str(e)}")

    def _add_all_rda_armor(self):
        """Add all RDA armor pieces to inventory"""
        if self.main_window.tree is None:
            show_error("Error", "No save file loaded. Please load a save file first.")
            return
        
        try:
            profile = self.main_window.tree.getroot().find("PlayerProfile")
            if profile is None:
                show_error("Error", "PlayerProfile not found in save file.")
                return
            
            # Find or create RDA possessions
            soldier = profile.find("Possessions_Soldier")
            if soldier is None:
                soldier = ET.SubElement(profile, "Possessions_Soldier")
            
            possessions = soldier.find("Posessions")
            if possessions is None:
                possessions = ET.SubElement(soldier, "Posessions")
            
            # Get all RDA armor item IDs from the armor mappings
            rda_armor_items = []
            for slot_type in ["headwear", "torso", "legs"]:
                if hasattr(self, 'rda_armor_sets') and slot_type in self.rda_armor_sets:
                    rda_armor_items.extend(self.rda_armor_sets[slot_type].keys())
                else:
                    # Create mappings if they don't exist
                    self._create_rda_armor_mappings()
                    rda_armor_items.extend(self.rda_armor_sets[slot_type].keys())
            
            # Get existing item IDs to avoid duplicates
            existing_items = set()
            for poss in possessions.findall("Poss"):
                existing_items.add(poss.get("crc_ItemID"))
            
            # Find next available index
            existing_indices = [int(poss.get("Index", "0")) for poss in possessions.findall("Poss")]
            next_index = 0
            while next_index in existing_indices:
                next_index += 1
            
            items_added = 0
            
            # Add each armor item if it doesn't already exist
            for item_id in rda_armor_items:
                if item_id not in existing_items:
                    # Create new possession
                    new_poss = ET.SubElement(possessions, "Poss")
                    new_poss.set("Index", str(next_index))
                    new_poss.set("crc_ItemID", item_id)
                    new_poss.set("NbInStack", "1")
                    new_poss.set("NbInClip", "0")
                    new_poss.set("crc_AmmoType", "4294967295")
                    new_poss.set("NoveltyState", "2")
                    
                    # Copy formatting from existing items
                    other_poss = possessions.find("Poss")
                    if other_poss is not None and hasattr(other_poss, 'tail'):
                        new_poss.tail = other_poss.tail
                    
                    self.logger.debug(f"Added RDA armor: {self._get_item_name(item_id)} (ID: {item_id})")
                    items_added += 1
                    next_index += 1
                    existing_items.add(item_id)
            
            # Mark changes as unsaved
            self.main_window.unsaved_label.config(text="Unsaved Changes")
            
            if items_added > 0:
                show_success("Armor Added", f"Successfully added {items_added} RDA armor pieces to inventory.")
            else:
                show_info("No Items Added", "All RDA armor pieces are already in your inventory.")
            
            self.logger.info(f"RDA armor addition completed. Added: {items_added}")
            
        except Exception as e:
            self.logger.error(f"Error adding RDA armor: {str(e)}", exc_info=True)
            show_error("Error", f"Failed to add RDA armor: {str(e)}")

    def _add_all_rda_weapons(self):
        """Add all RDA weapons to inventory"""
        if self.main_window.tree is None:
            show_error("Error", "No save file loaded. Please load a save file first.")
            return
        
        try:
            profile = self.main_window.tree.getroot().find("PlayerProfile")
            if profile is None:
                show_error("Error", "PlayerProfile not found in save file.")
                return
            
            # Find or create RDA possessions
            soldier = profile.find("Possessions_Soldier")
            if soldier is None:
                soldier = ET.SubElement(profile, "Possessions_Soldier")
            
            possessions = soldier.find("Posessions")
            if possessions is None:
                possessions = ET.SubElement(soldier, "Posessions")
            
            # Get all RDA weapon IDs
            rda_weapon_items = self._get_rda_weapon_ids()
            
            # Get existing item IDs to avoid duplicates
            existing_items = set()
            for poss in possessions.findall("Poss"):
                existing_items.add(poss.get("crc_ItemID"))
            
            # Find next available index
            existing_indices = [int(poss.get("Index", "0")) for poss in possessions.findall("Poss")]
            next_index = 0
            while next_index in existing_indices:
                next_index += 1
            
            items_added = 0
            
            # Add each weapon if it doesn't already exist
            for item_id in rda_weapon_items:
                if item_id not in existing_items:
                    # Create new possession
                    new_poss = ET.SubElement(possessions, "Poss")
                    new_poss.set("Index", str(next_index))
                    new_poss.set("crc_ItemID", item_id)
                    new_poss.set("NbInStack", "1")
                    new_poss.set("NbInClip", "0")
                    
                    # Set appropriate ammo type
                    ammo_type = self._get_ammo_type_for_weapon(item_id)
                    new_poss.set("crc_AmmoType", ammo_type)
                    new_poss.set("NoveltyState", "2")
                    
                    # Copy formatting from existing items
                    other_poss = possessions.find("Poss")
                    if other_poss is not None and hasattr(other_poss, 'tail'):
                        new_poss.tail = other_poss.tail
                    
                    self.logger.debug(f"Added RDA weapon: {self._get_item_name(item_id)} (ID: {item_id})")
                    items_added += 1
                    next_index += 1
                    existing_items.add(item_id)
            
            # Ensure all ammo types exist
            self._ensure_faction_ammo_exists(possessions, is_navi=False)
            
            # Mark changes as unsaved
            self.main_window.unsaved_label.config(text="Unsaved Changes")
            
            if items_added > 0:
                show_success("Weapons Added", f"Successfully added {items_added} RDA weapons to inventory.")
            else:
                show_info("No Items Added", "All RDA weapons are already in your inventory.")
            
            self.logger.info(f"RDA weapons addition completed. Added: {items_added}")
            
        except Exception as e:
            self.logger.error(f"Error adding RDA weapons: {str(e)}", exc_info=True)
            show_error("Error", f"Failed to add RDA weapons: {str(e)}")

    def _add_all_rda_skills(self):
        """Add all RDA skills to inventory AND unlock ALL skills in skill database"""
        if self.main_window.tree is None:
            show_error("Error", "No save file loaded. Please load a save file first.")
            return
        
        try:
            root = self.main_window.tree.getroot()
            profile = root.find("PlayerProfile")
            if profile is None:
                show_error("Error", "PlayerProfile not found in save file.")
                return
            
            # PART 1: Add skills to inventory (possessions)
            soldier = profile.find("Possessions_Soldier")
            if soldier is None:
                soldier = ET.SubElement(profile, "Possessions_Soldier")
            
            possessions = soldier.find("Posessions")
            if possessions is None:
                possessions = ET.SubElement(soldier, "Posessions")
            
            # Get all RDA skill IDs
            rda_skill_items = list(self.rda_skill_mappings.keys())
            
            # Get existing item IDs to avoid duplicates
            existing_items = set()
            for poss in possessions.findall("Poss"):
                existing_items.add(poss.get("crc_ItemID"))
            
            # Find next available index
            existing_indices = [int(poss.get("Index", "0")) for poss in possessions.findall("Poss")]
            next_index = 0
            while next_index in existing_indices:
                next_index += 1
            
            items_added = 0
            
            # Add each skill if it doesn't already exist
            for item_id in rda_skill_items:
                if item_id not in existing_items:
                    # Create new possession
                    new_poss = ET.SubElement(possessions, "Poss")
                    new_poss.set("Index", str(next_index))
                    new_poss.set("crc_ItemID", item_id)
                    new_poss.set("NbInStack", "1")
                    new_poss.set("NbInClip", "0")
                    new_poss.set("crc_AmmoType", "4294967295")
                    new_poss.set("NoveltyState", "2")
                    
                    # Copy formatting from existing items
                    other_poss = possessions.find("Poss")
                    if other_poss is not None and hasattr(other_poss, 'tail'):
                        new_poss.tail = other_poss.tail
                    
                    self.logger.debug(f"Added RDA skill: {self.rda_skill_mappings[item_id]} (ID: {item_id})")
                    items_added += 1
                    next_index += 1
                    existing_items.add(item_id)
            
            # PART 2: Unlock ALL skills in AvatarSkillDB_Status
            # Try multiple search methods to find AvatarSkillDB_Status
            skill_db = None
            
            # Method 1: Direct child of root
            skill_db = root.find("AvatarSkillDB_Status")
            if skill_db is not None:
                self.logger.debug("Found AvatarSkillDB_Status as direct child of root")
            
            # Method 2: Search anywhere in tree using XPath
            if skill_db is None:
                skill_db = root.find(".//AvatarSkillDB_Status")
                if skill_db is not None:
                    self.logger.debug("Found AvatarSkillDB_Status using XPath search")
            
            # Method 3: Manual search through all elements
            if skill_db is None:
                for elem in root.iter():
                    if elem.tag == "AvatarSkillDB_Status":
                        skill_db = elem
                        self.logger.debug("Found AvatarSkillDB_Status through manual iteration")
                        break
            
            skills_unlocked = 0
            
            if skill_db is not None:
                all_skills = skill_db.findall("Skill")
                self.logger.debug(f"Found AvatarSkillDB_Status with {len(all_skills)} skills")
                
                # Update ALL skills to eLocked="2" (Unlocked | Has Seen)
                for skill in all_skills:
                    old_status = skill.get("eLocked", "0")
                    skill.set("eLocked", "2")  # Always set to 2, regardless of current value
                    
                    if old_status != "2":
                        skills_unlocked += 1
                    
                    skill_id = skill.get("crc_id", "Unknown")
                    self.logger.debug(f"Set skill ID {skill_id} eLocked: {old_status} -> 2")
                
                self.logger.info(f"Successfully unlocked {skills_unlocked} skills out of {len(all_skills)} total")
            else:
                # Debug: Print the entire XML structure to see what's available
                self.logger.error("AvatarSkillDB_Status not found anywhere in XML!")
                self.logger.debug("Available root-level elements:")
                for child in root:
                    self.logger.debug(f"  - {child.tag}")
                
                show_warning("Partial Success", 
                            f"Added {items_added} RDA skills to inventory, but could not find skill database to unlock them.\n\n"
                            "Skills are in your inventory but may not show as unlocked in the skill menu.")
            
            # Mark changes as unsaved
            self.main_window.unsaved_label.config(text="Unsaved Changes")
            
            # Show success message
            if items_added > 0 or skills_unlocked > 0:
                message = f"Successfully added {items_added} RDA skills to inventory"
                if skills_unlocked > 0:
                    message += f" and unlocked {skills_unlocked} skills in skill database"
                message += "."
                show_success("Skills Added & Unlocked", message)
            else:
                if skill_db is None:
                    show_info("Partial Success", f"Added {items_added} RDA skills to inventory.")
                else:
                    show_info("No Changes", "All RDA skills are already in your inventory and all skills are unlocked.")
            
            self.logger.info(f"RDA skills operation completed. Added: {items_added}, Skills unlocked: {skills_unlocked}")
            
        except Exception as e:
            self.logger.error(f"Error adding RDA skills: {str(e)}", exc_info=True)
            show_error("Error", f"Failed to add RDA skills: {str(e)}")

    def _add_all_navi_skills(self):
        """Add all Na'vi skills to inventory AND unlock ALL skills in skill database"""
        if self.main_window.tree is None:
            show_error("Error", "No save file loaded. Please load a save file first.")
            return
        
        try:
            root = self.main_window.tree.getroot()
            profile = root.find("PlayerProfile")
            if profile is None:
                show_error("Error", "PlayerProfile not found in save file.")
                return
            
            # PART 1: Add skills to inventory (possessions)
            avatar = profile.find("Possessions_Avatar")
            if avatar is None:
                avatar = ET.SubElement(profile, "Possessions_Avatar")
            
            possessions = avatar.find("Posessions")
            if possessions is None:
                possessions = ET.SubElement(avatar, "Posessions")
            
            # Get all Na'vi skill IDs
            navi_skill_items = list(self.navi_skill_mappings.keys())
            
            # Get existing item IDs to avoid duplicates
            existing_items = set()
            for poss in possessions.findall("Poss"):
                existing_items.add(poss.get("crc_ItemID"))
            
            # Find next available index
            existing_indices = [int(poss.get("Index", "0")) for poss in possessions.findall("Poss")]
            next_index = 0
            while next_index in existing_indices:
                next_index += 1
            
            items_added = 0
            
            # Add each skill if it doesn't already exist
            for item_id in navi_skill_items:
                if item_id not in existing_items:
                    # Create new possession
                    new_poss = ET.SubElement(possessions, "Poss")
                    new_poss.set("Index", str(next_index))
                    new_poss.set("crc_ItemID", item_id)
                    new_poss.set("NbInStack", "1")
                    new_poss.set("NbInClip", "0")
                    new_poss.set("crc_AmmoType", "4294967295")
                    new_poss.set("NoveltyState", "2")
                    
                    # Copy formatting from existing items
                    other_poss = possessions.find("Poss")
                    if other_poss is not None and hasattr(other_poss, 'tail'):
                        new_poss.tail = other_poss.tail
                    
                    self.logger.debug(f"Added Na'vi skill: {self.navi_skill_mappings[item_id]} (ID: {item_id})")
                    items_added += 1
                    next_index += 1
                    existing_items.add(item_id)
            
            # PART 2: Unlock ALL skills in AvatarSkillDB_Status
            # Try multiple search methods to find AvatarSkillDB_Status
            skill_db = None
            
            # Method 1: Direct child of root
            skill_db = root.find("AvatarSkillDB_Status")
            if skill_db is not None:
                self.logger.debug("Found AvatarSkillDB_Status as direct child of root")
            
            # Method 2: Search anywhere in tree using XPath
            if skill_db is None:
                skill_db = root.find(".//AvatarSkillDB_Status")
                if skill_db is not None:
                    self.logger.debug("Found AvatarSkillDB_Status using XPath search")
            
            # Method 3: Manual search through all elements
            if skill_db is None:
                for elem in root.iter():
                    if elem.tag == "AvatarSkillDB_Status":
                        skill_db = elem
                        self.logger.debug("Found AvatarSkillDB_Status through manual iteration")
                        break
            
            skills_unlocked = 0
            
            if skill_db is not None:
                all_skills = skill_db.findall("Skill")
                self.logger.debug(f"Found AvatarSkillDB_Status with {len(all_skills)} skills")
                
                # Update ALL skills to eLocked="2" (Unlocked | Has Seen)
                for skill in all_skills:
                    old_status = skill.get("eLocked", "0")
                    skill.set("eLocked", "2")  # Always set to 2, regardless of current value
                    
                    if old_status != "2":
                        skills_unlocked += 1
                    
                    skill_id = skill.get("crc_id", "Unknown")
                    self.logger.debug(f"Set skill ID {skill_id} eLocked: {old_status} -> 2")
                
                self.logger.info(f"Successfully unlocked {skills_unlocked} skills out of {len(all_skills)} total")
            else:
                # Debug: Print the entire XML structure to see what's available
                self.logger.error("AvatarSkillDB_Status not found anywhere in XML!")
                self.logger.debug("Available root-level elements:")
                for child in root:
                    self.logger.debug(f"  - {child.tag}")
                
                show_warning("Partial Success", 
                            f"Added {items_added} Na'vi skills to inventory, but could not find skill database to unlock them.\n\n"
                            "Skills are in your inventory but may not show as unlocked in the skill menu.")
            
            # Mark changes as unsaved
            self.main_window.unsaved_label.config(text="Unsaved Changes")
            
            # Show success message
            if items_added > 0 or skills_unlocked > 0:
                message = f"Successfully added {items_added} Na'vi skills to inventory"
                if skills_unlocked > 0:
                    message += f" and unlocked {skills_unlocked} skills in skill database"
                message += "."
                show_success("Skills Added & Unlocked", message)
            else:
                if skill_db is None:
                    show_info("Partial Success", f"Added {items_added} Na'vi skills to inventory.")
                else:
                    show_info("No Changes", "All Na'vi skills are already in your inventory and all skills are unlocked.")
            
            self.logger.info(f"Na'vi skills operation completed. Added: {items_added}, Skills unlocked: {skills_unlocked}")
            
        except Exception as e:
            self.logger.error(f"Error adding Na'vi skills: {str(e)}", exc_info=True)
            show_error("Error", f"Failed to add Na'vi skills: {str(e)}")

    def _add_all_navi_armor(self):
        """Add all Na'vi armor pieces to inventory"""
        if self.main_window.tree is None:
            show_error("Error", "No save file loaded. Please load a save file first.")
            return
        
        try:
            profile = self.main_window.tree.getroot().find("PlayerProfile")
            if profile is None:
                show_error("Error", "PlayerProfile not found in save file.")
                return
            
            # Find or create Na'vi possessions
            avatar = profile.find("Possessions_Avatar")
            if avatar is None:
                avatar = ET.SubElement(profile, "Possessions_Avatar")
            
            possessions = avatar.find("Posessions")
            if possessions is None:
                possessions = ET.SubElement(avatar, "Posessions")
            
            # Get all Na'vi armor item IDs from the armor mappings
            navi_armor_items = []
            for slot_type in ["headwear", "torso", "legs"]:
                if hasattr(self, 'navi_armor_sets') and slot_type in self.navi_armor_sets:
                    navi_armor_items.extend(self.navi_armor_sets[slot_type].keys())
                else:
                    # Create mappings if they don't exist
                    self._create_navi_armor_mappings()
                    navi_armor_items.extend(self.navi_armor_sets[slot_type].keys())
            
            # Get existing item IDs to avoid duplicates
            existing_items = set()
            for poss in possessions.findall("Poss"):
                existing_items.add(poss.get("crc_ItemID"))
            
            # Find next available index
            existing_indices = [int(poss.get("Index", "0")) for poss in possessions.findall("Poss")]
            next_index = 0
            while next_index in existing_indices:
                next_index += 1
            
            items_added = 0
            
            # Add each armor item if it doesn't already exist
            for item_id in navi_armor_items:
                if item_id not in existing_items:
                    # Create new possession
                    new_poss = ET.SubElement(possessions, "Poss")
                    new_poss.set("Index", str(next_index))
                    new_poss.set("crc_ItemID", item_id)
                    new_poss.set("NbInStack", "1")
                    new_poss.set("NbInClip", "0")
                    new_poss.set("crc_AmmoType", "4294967295")
                    new_poss.set("NoveltyState", "2")
                    
                    # Copy formatting from existing items
                    other_poss = possessions.find("Poss")
                    if other_poss is not None and hasattr(other_poss, 'tail'):
                        new_poss.tail = other_poss.tail
                    
                    self.logger.debug(f"Added Na'vi armor: {self._get_item_name(item_id)} (ID: {item_id})")
                    items_added += 1
                    next_index += 1
                    existing_items.add(item_id)
            
            # Mark changes as unsaved
            self.main_window.unsaved_label.config(text="Unsaved Changes")
            
            if items_added > 0:
                show_success("Armor Added", f"Successfully added {items_added} Na'vi armor pieces to inventory.")
            else:
                show_info("No Items Added", "All Na'vi armor pieces are already in your inventory.")
            
            self.logger.info(f"Na'vi armor addition completed. Added: {items_added}")
            
        except Exception as e:
            self.logger.error(f"Error adding Na'vi armor: {str(e)}", exc_info=True)
            show_error("Error", f"Failed to add Na'vi armor: {str(e)}")

    def _add_all_navi_weapons(self):
        """Add all Na'vi weapons to inventory"""
        if self.main_window.tree is None:
            show_error("Error", "No save file loaded. Please load a save file first.")
            return
        
        try:
            profile = self.main_window.tree.getroot().find("PlayerProfile")
            if profile is None:
                show_error("Error", "PlayerProfile not found in save file.")
                return
            
            # Find or create Na'vi possessions
            avatar = profile.find("Possessions_Avatar")
            if avatar is None:
                avatar = ET.SubElement(profile, "Possessions_Avatar")
            
            possessions = avatar.find("Posessions")
            if possessions is None:
                possessions = ET.SubElement(avatar, "Posessions")
            
            # Get all Na'vi weapon IDs
            navi_weapon_items = self._get_navi_weapon_ids()
            
            # Get existing item IDs to avoid duplicates
            existing_items = set()
            for poss in possessions.findall("Poss"):
                existing_items.add(poss.get("crc_ItemID"))
            
            # Find next available index
            existing_indices = [int(poss.get("Index", "0")) for poss in possessions.findall("Poss")]
            next_index = 0
            while next_index in existing_indices:
                next_index += 1
            
            items_added = 0
            
            # Add each weapon if it doesn't already exist
            for item_id in navi_weapon_items:
                if item_id not in existing_items:
                    # Create new possession
                    new_poss = ET.SubElement(possessions, "Poss")
                    new_poss.set("Index", str(next_index))
                    new_poss.set("crc_ItemID", item_id)
                    new_poss.set("NbInStack", "1")
                    new_poss.set("NbInClip", "0")
                    
                    # Set appropriate ammo type
                    ammo_type = self._get_ammo_type_for_weapon(item_id)
                    new_poss.set("crc_AmmoType", ammo_type)
                    new_poss.set("NoveltyState", "2")
                    
                    # Copy formatting from existing items
                    other_poss = possessions.find("Poss")
                    if other_poss is not None and hasattr(other_poss, 'tail'):
                        new_poss.tail = other_poss.tail
                    
                    self.logger.debug(f"Added Na'vi weapon: {self._get_item_name(item_id)} (ID: {item_id})")
                    items_added += 1
                    next_index += 1
                    existing_items.add(item_id)
            
            # Ensure all ammo types exist
            self._ensure_faction_ammo_exists(possessions, is_navi=True)
            
            # Mark changes as unsaved
            self.main_window.unsaved_label.config(text="Unsaved Changes")
            
            if items_added > 0:
                show_success("Weapons Added", f"Successfully added {items_added} Na'vi weapons to inventory.")
            else:
                show_info("No Items Added", "All Na'vi weapons are already in your inventory.")
            
            self.logger.info(f"Na'vi weapons addition completed. Added: {items_added}")
            
        except Exception as e:
            self.logger.error(f"Error adding Na'vi weapons: {str(e)}", exc_info=True)
            show_error("Error", f"Failed to add Na'vi weapons: {str(e)}")
            
    def _get_all_rda_ammo_items(self):
        """Get all RDA ammo item IDs for ensuring ammo availability"""
        return [
            "4029490973",  
            "2220072441",  
            "3183424835",  
            "3227899887",  
            "4198025789",  
            "2442117335",  
            "3819023512"   
        ]

    def _get_all_navi_ammo_items(self):
        """Get all Na'vi ammo item IDs for ensuring ammo availability"""
        return [
            "1042656528",  
            "435601722",   
            "3069972540"   
        ]

    def _ensure_faction_ammo_exists(self, possessions, is_navi=False):
        """Ensure all ammo types exist for the faction"""
        try:
            ammo_items = self._get_all_navi_ammo_items() if is_navi else self._get_all_rda_ammo_items()
            
            # Get existing ammo items
            existing_ammo = set()
            for poss in possessions.findall("Poss"):
                item_id = poss.get("crc_ItemID")
                if item_id in ammo_items:
                    existing_ammo.add(item_id)
            
            # Find next available index
            existing_indices = [int(poss.get("Index", "0")) for poss in possessions.findall("Poss")]
            next_index = max(existing_indices) + 1 if existing_indices else 0
            
            # Add missing ammo types
            for ammo_id in ammo_items:
                if ammo_id not in existing_ammo:
                    new_ammo = ET.SubElement(possessions, "Poss")
                    new_ammo.set("Index", str(next_index))
                    new_ammo.set("crc_ItemID", ammo_id)
                    new_ammo.set("NbInStack", "1000")  # Give plenty of ammo
                    new_ammo.set("NbInClip", "0")
                    new_ammo.set("crc_AmmoType", "4294967295")
                    new_ammo.set("NoveltyState", "2")
                    
                    # Copy formatting
                    other_poss = possessions.find("Poss")
                    if other_poss is not None and hasattr(other_poss, 'tail'):
                        new_ammo.tail = other_poss.tail
                    
                    self.logger.debug(f"Added missing ammo: {self._get_item_name(ammo_id)} (ID: {ammo_id})")
                    next_index += 1
                    
        except Exception as e:
            self.logger.error(f"Error ensuring ammo exists: {str(e)}", exc_info=True)

    def _update_weapon(self, profile, slot_index, weapon_id, is_navi=False):
        """
        Unified method to update weapons for both RDA and Na'vi across different save formats.
        
        Args:
            profile (ET.Element): The PlayerProfile element
            slot_index (int): The weapon slot index to update
            weapon_id (str): The weapon ID to set
            is_navi (bool): True for Na'vi weapons, False for RDA
        """
        self.logger.debug(f"Updating {'Navi' if is_navi else 'RDA'} weapon - Slot: {slot_index}, Weapon ID: {weapon_id}")
        
        # Find the Possessions element or create it
        faction_elem_name = "Possessions_Avatar" if is_navi else "Possessions_Soldier"
        faction_elem = profile.find(faction_elem_name)
        if faction_elem is None:
            faction_elem = ET.SubElement(profile, faction_elem_name)
            self.logger.debug(f"Created new {faction_elem_name} element")
            
        # Find the EquippedWeapons element or create it
        equipped = faction_elem.find("EquippedWeapons")
        if equipped is None:
            equipped = ET.SubElement(faction_elem, "EquippedWeapons")
            self.logger.debug(f"Created new EquippedWeapons element")
        
        # Make sure we have enough slots
        slots = equipped.findall("Slot")
        while len(slots) <= slot_index:
            new_slot = ET.SubElement(equipped, "Slot")
            new_slot.set("MainHand_PossIdx", "-1")
            new_slot.set("OffHand_PossIdx", "-1")
            slots = equipped.findall("Slot")
            self.logger.debug(f"Created new weapon Slot at position {len(slots)-1}")
        
        # Find Posessions element or create it
        possessions = faction_elem.find("Posessions")
        if possessions is None:
            possessions = ET.SubElement(faction_elem, "Posessions")
            self.logger.debug(f"Created new Posessions element")
        
        # Get the ammo entry value
        weapon_slots = self.navi_weapon_slots if is_navi else self.weapon_slots
        ammo_entry = weapon_slots[slot_index]["ammo_entry"]
        ammo_count = ammo_entry.get()
        try:
            ammo_count = int(ammo_count)
        except ValueError:
            ammo_count = 0
                
        # Determine the next available index for a new possession
        existing_indices = [int(poss.get("Index", "0")) for poss in possessions.findall("Poss")]
        next_index = 0
        while next_index in existing_indices:
            next_index += 1
        next_index_str = str(next_index)
        
        # Get the appropriate ammo type for this weapon
        ammo_type = self._get_ammo_type_for_weapon(weapon_id)
        self.logger.debug(f"Using ammo type {ammo_type} for weapon {weapon_id}")
        
        # Create or update a possession for this weapon
        weapon_poss = None
        for poss in possessions.findall("Poss"):
            if poss.get("crc_ItemID") == weapon_id:
                weapon_poss = poss
                self.logger.debug(f"Found existing weapon in inventory at index {poss.get('Index')}")
                break
                
        if weapon_poss is None:
            # Find the last element to copy its formatting
            last_poss = None
            for poss in possessions.findall("Poss"):
                last_poss = poss
            
            # Create new element with same formatting
            weapon_poss = ET.SubElement(possessions, "Poss")
            weapon_poss.set("Index", next_index_str)
            weapon_poss.set("crc_ItemID", weapon_id)
            weapon_poss.set("NbInStack", "1")
            weapon_poss.set("NbInClip", str(ammo_count))
            weapon_poss.set("crc_AmmoType", ammo_type)
            weapon_poss.set("NoveltyState", "2")
            self.logger.debug(f"Created new weapon possession at index {next_index_str}")
            
            # Copy the tail from the last element to preserve formatting
            if last_poss is not None and hasattr(last_poss, 'tail'):
                weapon_poss.tail = last_poss.tail
            
            # If this weapon uses ammo, also add the ammo to the inventory
            if ammo_type != "4294967295":
                # Add ammo - find if it already exists
                ammo_poss = None
                for poss in possessions.findall("Poss"):
                    if poss.get("crc_ItemID") == ammo_type:
                        ammo_poss = poss
                        self.logger.debug(f"Found existing ammo type {ammo_type} at index {poss.get('Index')}")
                        break
                        
                if ammo_poss is None:
                    # Create new ammo entry
                    ammo_index = next_index + 1
                    while ammo_index in existing_indices:
                        ammo_index += 1
                        
                    ammo_poss = ET.SubElement(possessions, "Poss")
                    ammo_poss.set("Index", str(ammo_index))
                    ammo_poss.set("crc_ItemID", ammo_type)
                    ammo_poss.set("NbInStack", "100")  # Give a decent amount of ammo
                    ammo_poss.set("NbInClip", "0")
                    ammo_poss.set("crc_AmmoType", "4294967295")
                    ammo_poss.set("NoveltyState", "2")
                    self.logger.debug(f"Created new ammo possession at index {ammo_index} for type {ammo_type}")
                    
                    # Copy the tail formatting here too
                    if weapon_poss is not None and hasattr(weapon_poss, 'tail'):
                        ammo_poss.tail = weapon_poss.tail
        else:
            # Use existing entry
            old_ammo_type = weapon_poss.get("crc_AmmoType")
            weapon_poss.set("NbInClip", str(ammo_count))
            weapon_poss.set("crc_AmmoType", ammo_type)  # Make sure ammo type is correct
            next_index_str = weapon_poss.get("Index")
            self.logger.debug(f"Updated existing weapon at index {next_index_str} (ammo type {old_ammo_type} -> {ammo_type})")
            
        # Update the equipped weapon slot
        slot = slots[slot_index]
        old_index = slot.get("MainHand_PossIdx", "-1")
        slot.set("MainHand_PossIdx", next_index_str)
        self.logger.debug(f"Updated slot {slot_index} from MainHand_PossIdx={old_index} to {next_index_str}")
        
        # Update the display
        if is_navi:
            self._update_navi_loadout_display(profile)
            # Preserve faction when changing Na'vi weapons
            self._preserve_faction(profile, "1")  # 1 for Na'vi
        else:
            self._update_loadout_display(profile)
            # Preserve faction when changing RDA weapons
            self._preserve_faction(profile, "2")  # 2 for RDA
        
        return True
        
    def _update_armor(self, profile: ET.Element, slot_type, armor_name, is_navi=False):
        """
        Unified method to update armor for both RDA and Na'vi across different save formats.
        """
        self.logger.debug(f"Updating {'Navi' if is_navi else 'RDA'} armor - Slot: {slot_type}, Armor: {armor_name}")
        
        # Handle empty selection
        if armor_name == "-Empty-":
            armor_id = "-1"
        else:
            # Get the armor sets and IDs based on faction
            armor_ids = self.navi_armor_ids if is_navi else self.rda_armor_ids
            
            # Get the armor ID from the name
            armor_id = armor_ids[slot_type].get(armor_name)
            if armor_id is None:
                self.logger.warning(f"Could not find armor ID for {armor_name}")
                return False
        
        # Find the Possessions element or create it
        faction_elem_name = "Possessions_Avatar" if is_navi else "Possessions_Soldier"
        faction_elem = profile.find(faction_elem_name)
        if faction_elem is None:
            faction_elem = ET.SubElement(profile, faction_elem_name)
            self.logger.debug(f"Created new {faction_elem_name} element")
        
        # Find or create EquippedArmors section
        equipped_armors = faction_elem.find("EquippedArmors")
        if equipped_armors is None:
            equipped_armors = ET.SubElement(faction_elem, "EquippedArmors")
            self.logger.debug(f"Created new EquippedArmors element")

        # Ensure we have all three slots
        slots = equipped_armors.findall("Slot")
        slot_mapping = {"headwear": 0, "torso": 1, "legs": 2}
        slot_position = slot_mapping[slot_type]
        
        # Create slots if they don't exist
        while len(slots) <= slot_position:
            new_slot = ET.SubElement(equipped_armors, "Slot")
            new_slot.set("PossIdx", "-1")  # Default to empty
            slots = equipped_armors.findall("Slot")
            self.logger.debug(f"Created new armor Slot at position {len(slots)-1}")
        
        # For empty selection, just set to -1 and we're done
        if armor_name == "-Empty-":
            slots[slot_position].set("PossIdx", "-1")
            self.logger.debug(f"Set {'Navi' if is_navi else 'RDA'} {slot_type} to empty (-1)")
            return True
        
        # For normal armor pieces - find or create the possession item
        possessions = faction_elem.find("Posessions")
        if possessions is None:
            possessions = ET.SubElement(faction_elem, "Posessions")
            self.logger.debug(f"Created new Posessions element")
        
        # Check if the armor already exists in inventory
        existing_poss = None
        for poss in possessions.findall("Poss"):
            if poss.get("crc_ItemID") == armor_id:
                existing_poss = poss
                self.logger.debug(f"Found existing armor item at index {poss.get('Index')}")
                break
        
        if existing_poss is not None:
            # Use existing possession
            index_str = existing_poss.get("Index")
        else:
            # Create new possession with next available index
            existing_indices = [int(poss.get("Index", "0")) for poss in possessions.findall("Poss")]
            next_index = 0
            while next_index in existing_indices:
                next_index += 1
            index_str = str(next_index)
            
            # Create new possession
            new_poss = ET.SubElement(possessions, "Poss")
            new_poss.set("Index", index_str)
            new_poss.set("crc_ItemID", armor_id)
            new_poss.set("NbInStack", "1")
            new_poss.set("NbInClip", "0")
            new_poss.set("crc_AmmoType", "4294967295")
            new_poss.set("NoveltyState", "2")
            self.logger.debug(f"Created new armor item at index {index_str}")
            
            # Copy formatting from another item if possible
            other_poss = possessions.find("Poss")
            if other_poss is not None and hasattr(other_poss, 'tail'):
                new_poss.tail = other_poss.tail
        
        # Update the slot reference
        slots[slot_position].set("PossIdx", index_str)
        self.logger.debug(f"Set {slot_type} slot to use item at index {index_str}")
        
        return True

    def _update_ammo_directly(self, profile, is_navi, slot_index, new_ammo_value):
        """Direct method to update ammo in the save file for debugging and manual updates"""
        try:
            self.logger.debug(f"Directly updating ammo to {new_ammo_value} for {'Navi' if is_navi else 'RDA'} slot {slot_index}")

            if is_navi:
                # Find the Na'vi weapon
                avatar = profile.find("Possessions_Avatar")
                if avatar is None:
                    self.logger.error("Possessions_Avatar not found")
                    return False
                        
                equipped = avatar.find("EquippedWeapons")
                if equipped is None:
                    self.logger.error("EquippedWeapons not found")
                    return False
                        
                slots = equipped.findall("Slot")
                if slot_index >= len(slots):
                    self.logger.error(f"Slot index {slot_index} out of range")
                    return False
                        
                # Get the possession index
                poss_idx = slots[slot_index].get("MainHand_PossIdx", "-1")
                if poss_idx == "-1":
                    self.logger.error("No weapon equipped in this slot")
                    return False
                        
                # Find the weapon possession
                possessions = avatar.find("Posessions")
                if possessions is None:
                    self.logger.error("Posessions not found")
                    return False
                
                # Find the weapon
                weapon_poss = None
                for poss in possessions.findall("Poss"):
                    if poss.get("Index") == poss_idx:
                        weapon_poss = poss
                        break
                
                if weapon_poss is None:
                    self.logger.error("Weapon possession not found")
                    return False
                
                # Get ammo type
                ammo_type = weapon_poss.get("crc_AmmoType", "4294967295")
                if ammo_type == "4294967295":
                    self.logger.error("Weapon has infinite ammo or no ammo")
                    return False
                
                # IMPORTANT NEW CODE: Also update the weapon's own clip value
                clip_value = min(int(new_ammo_value), 100)  # Set clip to whatever is in ammo, max 100
                weapon_poss.set("NbInClip", str(clip_value))
                self.logger.debug(f"Updated weapon clip to {clip_value}")
                
                # Find and update ammo possession
                ammo_updated = False
                for poss in possessions.findall("Poss"):
                    if poss.get("crc_ItemID") == ammo_type:
                        # Update BOTH ammo attributes
                        poss.set("NbInStack", str(new_ammo_value))
                        poss.set("NbInClip", str(clip_value))
                        ammo_updated = True
                        self.logger.debug(f"Updated Na'vi ammo possession to {new_ammo_value}")
                        break
                
                # If we get here and ammo wasn't found - create it
                if not ammo_updated:
                    self._ensure_ammo_exists(possessions, ammo_type, str(new_ammo_value))
                
                # ADDITIONAL UPDATES - Try updating all possible ammo locations
                # Find all items that match the ammo type and update them all
                for poss in possessions.findall("Poss"):
                    if poss.get("crc_ItemID") == ammo_type or poss.get("crc_AmmoType") == ammo_type:
                        poss.set("NbInStack", str(new_ammo_value))
                        self.logger.debug(f"Updated additional ammo possession: {poss.get('Index')}")

                self.logger.debug(f"Successfully updated Na'vi ammo to {new_ammo_value}")
                return True
                
            else:
                # RDA weapon update - similar approach with additional updates
                soldier = profile.find("Possessions_Soldier")
                if soldier is None:
                    self.logger.error("Possessions_Soldier not found")
                    return False
                        
                equipped = soldier.find("EquippedWeapons")
                if equipped is None:
                    self.logger.error("EquippedWeapons not found")
                    return False
                        
                slots = equipped.findall("Slot")
                if slot_index >= len(slots):
                    self.logger.error(f"Slot index {slot_index} out of range")
                    return False
                        
                # Get the possession index
                poss_idx = slots[slot_index].get("MainHand_PossIdx", "-1")
                if poss_idx == "-1":
                    self.logger.error("No weapon equipped in this slot")
                    return False
                        
                # Find the weapon possession
                possessions = soldier.find("Posessions")
                if possessions is None:
                    self.logger.error("Posessions not found")
                    return False
                
                # Find the weapon
                weapon_poss = None
                for poss in possessions.findall("Poss"):
                    if poss.get("Index") == poss_idx:
                        weapon_poss = poss
                        break
                
                if weapon_poss is None:
                    self.logger.error("Weapon possession not found")
                    return False
                
                # Get ammo type
                ammo_type = weapon_poss.get("crc_AmmoType", "4294967295")
                if ammo_type == "4294967295":
                    self.logger.error("Weapon has infinite ammo or no ammo")
                    return False
                
                # IMPORTANT NEW CODE: Also update the weapon's own clip value
                clip_value = min(int(new_ammo_value), 100)  # Set clip to whatever is in ammo, max 100
                weapon_poss.set("NbInClip", str(clip_value))
                self.logger.debug(f"Updated weapon clip to {clip_value}")
                
                # Find and update ammo possession
                ammo_updated = False
                for poss in possessions.findall("Poss"):
                    if poss.get("crc_ItemID") == ammo_type:
                        # Update BOTH ammo attributes
                        poss.set("NbInStack", str(new_ammo_value))
                        poss.set("NbInClip", str(clip_value))
                        ammo_updated = True
                        self.logger.debug(f"Updated RDA ammo possession to {new_ammo_value}")
                        break
                
                # If we get here and ammo wasn't found - create it
                if not ammo_updated:
                    self._ensure_ammo_exists(possessions, ammo_type, str(new_ammo_value))
                
                # ADDITIONAL UPDATES - Try updating all possible ammo locations
                # Find all items that match the ammo type and update them all
                for poss in possessions.findall("Poss"):
                    if poss.get("crc_ItemID") == ammo_type or poss.get("crc_AmmoType") == ammo_type:
                        poss.set("NbInStack", str(new_ammo_value))
                        self.logger.debug(f"Updated additional ammo possession: {poss.get('Index')}")

                self.logger.debug(f"Successfully updated RDA ammo to {new_ammo_value}")
                return True
        
        except Exception as e:
            self.logger.error(f"Error in direct ammo update: {str(e)}", exc_info=True)
            return False

    def _get_ammo_type_for_weapon(self, weapon_id: str) -> str:
        """Determine the correct ammo type for a given weapon ID"""
        # Default ammo type (no ammo)
        default_ammo = "4294967295"
        
        # Mapping of weapons to their ammo types
        weapon_ammo_map = {
            # RDA weapons
            # Dual Wasp Pistol - No ammo (infinity)
            "1042188764": "4294967295",  # Dual Wasp Pistol I
            "815885611": "4294967295",   # Dual Wasp Pistol II
            "760079057": "4294967295",   # Dual Wasp Pistol III
            "999316102": "4294967295",   # Dual Wasp Pistol IV
            
            # DLC WARLOCK Dual Wasp Pistols - No ammo (infinity)
            "3859060838": "4294967295",  # DLC WARLOCK Dual Wasp Pistol I
            "3904601233": "4294967295",  # DLC WARLOCK Dual Wasp Pistol II
            "102867538": "4294967295",   # DLC WARLOCK Dual Wasp Pistol III
            "749353518": "4294967295",   # DLC WARLOCK Dual Wasp Pistol IV
            
            # Standard Issue Rifle - Rifle Ammo
            "1130814347": "4029490973",  # Standard Issue Rifle TERRA I
            "1306083196": "4029490973",  # Standard Issue Rifle EURYS II
            "3628031700": "4029490973",  # Standard Issue Rifle SOLARIS III
            "1146928137": "4029490973",  # Standard Issue Rifle SOLARIS IV
            
            # DLC ARGO Standard Issue Rifles - Rifle Ammo
            "2850329205": "4029490973",  # DLC ARGO Standard Issue Rifle I
            "2807789186": "4029490973",  # DLC ARGO Standard Issue Rifle II
            "2194670470": "4029490973",  # DLC ARGO Standard Issue Rifle III
            "324172685": "4029490973",   # DLC ARGO Standard Issue Rifle IV
            
            # Combat Shotgun - Shotgun Ammo
            "2313824646": "2220072441",  # Combat Shotgun PHALANX I
            "2270547313": "2220072441",  # Combat Shotgun PHALANX II
            "2789519003": "2220072441",  # Combat Shotgun PHALANX III
            "1919695864": "2220072441",  # Combat Shotgun PHALANX IV
            
            # DLC SIGNET Combat Shotguns - Shotgun Ammo
            "2664450350": "2220072441",  # DLC SIGNET Combat Shotgun I
            "2423238105": "2220072441",  # DLC SIGNET Combat Shotgun II
            "2120138529": "2220072441",  # DLC SIGNET Combat Shotgun III
            "4289908838": "2220072441",  # DLC SIGNET Combat Shotgun IV
            
            # Assault Rifle - SMG Ammo
            "2397981034": "3183424835",  # Assault Rifle TERRA I
            "2152836509": "3183424835",  # Assault Rifle EURYS II
            "268371112": "3183424835",   # Assault Rifle SOLARIS III
            "466145020": "3183424835",   # Assault Rifle SOLARIS IV
            
            # DLC BARRO Assault Rifles - SMG Ammo
            "3655372526": "3183424835",  # DLC BARRO Assault Rifle I
            "3613354521": "3183424835",  # DLC BARRO Assault Rifle II
            "3850194262": "3183424835",  # DLC BARRO Assault Rifle III
            "2109370248": "3183424835",  # DLC BARRO Assault Rifle IV
            
            # BANISHER M60 Machine Gun - Grenade Ammo
            "85991974": "3227899887",    # BANISHER M60 Machine Gun I
            "195020497": "3227899887",   # BANISHER M60 Machine Gun II
            "1881065336": "3227899887",  # BANISHER M60 Machine Gun III
            "1796958374": "3227899887",  # BANISHER M60 Machine Gun IV
            
            # DLC STELLAR M60 Machine Guns - Grenade Ammo
            "2015914953": "3227899887",  # DLC STELLAR M60 Machine Gun I
            "1989644094": "3227899887",  # DLC STELLAR M60 Machine Gun II
            "1087779032": "3227899887",  # DLC STELLAR M60 Machine Gun III
            "1691104809": "3227899887",  # DLC STELLAR M60 Machine Gun IV
            
            # Grenade Launcher - Rocket Ammo
            "94681171": "4198025789",    # Grenade Launcher M222 - I
            "186342564": "4198025789",   # Grenade Launcher M222 - II
            "1349633617": "4198025789",  # Grenade Launcher M222 - III
            "4018216358": "4198025789",  # Grenade Launcher M222 - IV
            
            # DLC CRUSHER Grenade Launchers - Rocket Ammo
            "2157668310": "4198025789",  # DLC CRUSHER Grenade Launcher I
            "2384757537": "4198025789",  # DLC CRUSHER Grenade Launcher II
            "3441856033": "4198025789",  # DLC CRUSHER Grenade Launcher III
            "3043901684": "4198025789",  # DLC CRUSHER Grenade Launcher IV
            
            # Flamethrower - LMG Ammo
            "2529862352": "2442117335",  # Flamethrower VESUPYRE I
            "2557822503": "2442117335",  # Flamethrower STERILATOR II
            "609450705": "2442117335",   # Flamethrower BUSHBOSS III
            "2288255787": "2442117335",  # Flamethrower BUSHBOSS IV
            
            # DLC BUDDY Flamethrowers - LMG Ammo
            "3250873684": "2442117335",  # DLC BUDDY Flamethrower I
            "3480977827": "2442117335",  # DLC BUDDY Flamethrower II
            "3469816623": "2442117335",  # DLC BUDDY Flamethrower III
            "3994460767": "2442117335",  # DLC BUDDY Flamethrower IV
            
            # Nail Gun - Heavy Ammo
            "2548581230": "3819023512",  # Nail Gun HAMMER I
            "2572658585": "3819023512",  # Nail Gun HAMMER II
            "143378107": "3819023512",   # Nail Gun HAMMER III
            "1911864170": "3819023512",  # Nail Gun HAMMER IV
            
            # DLC DENT Nail Guns - Heavy Ammo
            "2161255366": "3819023512",  # DLC DENT Nail Gun I
            "2389559089": "3819023512",  # DLC DENT Nail Gun II
            "3499218689": "3819023512",  # DLC DENT Nail Gun III
            "4230631668": "3819023512",  # DLC DENT Nail Gun IV
            
            # Na'vi Weapons
            # Dual Blade - No ammo (melee)
            "2948460035": "4294967295",  # Torukä Way Dual Blade IV
            "2813685095": "4294967295",  # Palulukanä Srew Dual Blade III
            "2917611312": "4294967295",  # 'Angtsìkä Zawng Dual Blade II
            "2740507591": "4294967295",  # Ikranä Syal Dual Blade I
            
            # DLC Tanhì Dual Blade - No ammo (melee)
            "2285146948": "4294967295",  # DLC Tanhì Dual Blade I
            "2257287091": "4294967295",  # DLC Tanhì Dual Blade II
            "3543126973": "4294967295",  # DLC Tanhì Dual Blade III
            "2007498681": "4294967295",  # DLC Tanhì Dual Balde IV
            
            # Crossbow - Poison Ammo
            "1514231420": "3069972540",  # Nawm Crossbow IV
            "3400058396": "3069972540",  # Kyktan Crossbow III
            "1839769381": "3069972540",  # Tsamsiyu Crossbow II
            "1662469074": "3069972540",  # Taronyu Crossbow I
            
            # DLC PXI Crossbow - Poison Ammo
            "3138212456": "3069972540",  # DLC PXI Crossbow I
            "2486913109": "3069972540",  # DLC PXI Crossbow II
            "2589205711": "3069972540",  # DLC PXI Crossbow III
            "1886472672": "3069972540",  # DLC PXI Crossbow IV
            
            # M30 Machine Guns - Arrow Ammo
            "921966990": "1042656528",   # ELITE AVR-M30 IV
            "958613249": "1042656528",   # AVR-M30 Machine Gun IV
            "172062103": "1042656528",   # ELITE AVR-M30 III
            "982090295": "1042656528",   # AVR-M30 Machine Gun III
            "1132447925": "1042656528",  # AVR-M30 Machine Gun II
            "1048019290": "1042656528",  # ELITE AVR-M30 II
            "1304439874": "1042656528",  # AVR-M30 Machine Gun I
            "818439597": "1042656528",   # ELITE AVR-M30 I
            
            # Club - No ammo (melee)
            "240531571": "4294967295",   # Nawm Club IV
            "3879387803": "4294967295",  # Eyktan Club III
            "4249071066": "4294967295",  # Tsamsiyu Club II
            "4093397293": "4294967295",  # Taronyu Club I
            
            # DLC Ikran Axe - No ammo (melee)
            "2934884349": "4294967295",  # DLC Ikran Axe 'Ampi
            "2689671946": "4294967295",  # DLC Ikran Axe Kurakx
            "1639187137": "4294967295",  # DLC Ikran Axe Tsmukan
            "1958996617": "4294967295",  # DLC Ikran Axe 'Eko
            
            # Fighting Staff - Spear Ammo
            "3960574385": "435601722",   # Torukä Tirea Fighting Staff IV
            "2986118748": "435601722",   # Palulukanä Tìtakuk Fighting Staff III
            "2295024111": "435601722",   # Pa'liä Tìtxur Fighting Staff II
            "2255793432": "435601722",   # Ikranä Zawng Fighting Staff I
            
            # DLC Hufwe Fighting Staff - Spear Ammo
            "1828119782": "435601722",   # DLC Hufwe Fighting Staff I
            "1648951313": "435601722",   # DLC Hufwe Fighting Staff II
            "3943944974": "435601722",   # DLC Hufwe Fighting Staff III
            "3139393077": "435601722",   # DLC Hufwe Fighting Staff IV
            
            # Bow - Arrow Ammo
            "291262189": "1042656528",   # DLC Taronyu Tsko Bow I
            "535013914": "1042656528",   # Tasmsiyu Tsko Bow II
            "2092736556": "1042656528",  # Tsko Kyktan Bow III
            "371977402": "1042656528",   # Tsko Nawm Bow IV
            
            # DLC Bow - Arrow Ammo
            "1817446146": "1042656528",  # DLC RAWKE Bow I
            "435991093": "1042656528",   # DLC RAWKE Bow IV
            "1659626485": "1042656528",  # DLC RAWKE Bow II
            "1282693004": "1042656528",  # DLC RAWKE Bow III
        }
        
        # Return the appropriate ammo type for the weapon, or default if not found
        return weapon_ammo_map.get(weapon_id, default_ammo)

    def load_stats(self, tree: ET.ElementTree) -> None:
        """Load stats data with modern interface - UPDATED to include outfit loading"""
        self.logger.debug("Loading stats with modern interface")
        
        # DEBUG: Print all attributes of main_window to find the file path
        self.logger.debug(f"Main window attributes: {[attr for attr in dir(self.main_window) if not attr.startswith('_') and 'file' in attr.lower()]}")
    
        try:
            root = tree.getroot()
            profile = root.find("PlayerProfile")

            if profile is not None:
                self._update_base_info(profile.find("BaseInfo"), tree)
                self._update_xp_info(profile.find("XpInfo"))
                self._update_options_info(profile.find("OptionsInfo"))
                self._update_loadout_display(profile)
                self._update_navi_loadout_display(profile)
                self._update_player_info(profile)
                
                # Load skills for both factions
                self._load_rda_skills(profile)
                self._load_navi_skills(profile)
                
                # Load time info
                self.load_time_info(tree)
                
                # INITIALIZE OUTFIT STORAGE
                self._initialize_outfit_storage()
            
            metagame = root.find("Metagame")
            if metagame is not None:
                self._update_metagame_info(metagame)
                self._update_metagame_player_info(metagame)
                
        except Exception as e:
            self.logger.error(f"Error loading stats: {str(e)}", exc_info=True)
            raise

    def _update_base_info(self, base_info, tree=None):
        """Update base information fields"""
        if base_info is None:
            print("DEBUG: base_info is None")
            return
            
        print(f"DEBUG: Processing base_info with attributes: {list(base_info.attrib.keys())}")
            
        # Update character name
        if "namevec" in self.entries:
            name_vec = base_info.get("namevec", "Count(0) ")
            name = self._name_vec_to_string(name_vec)
            widget = self.entries["namevec"]
            if hasattr(widget, 'delete'):
                widget.delete(0, tk.END)
                widget.insert(0, name)
            else:
                widget.config(text=name)

        # Handle location from LocationInfo (separate from BaseInfo) - UPDATED WITH MAP NAMES
        location_value = "0,0"  # Default
        if tree is not None:
            root = tree.getroot()
            # Look for LocationInfo element
            location_info = root.find(".//LocationInfo")
            if location_info is not None:
                location_value = location_info.get("YouAreHere_LatitudeLongitude", "0,0")
                print(f"DEBUG: Found location: {location_value}")
            else:
                # Search more broadly if specific LocationInfo not found
                location_elements = root.findall(".//*[@YouAreHere_LatitudeLongitude]")
                if location_elements:
                    location_value = location_elements[0].get("YouAreHere_LatitudeLongitude", "0,0")
                    print(f"DEBUG: Found location (broad search): {location_value}")

        # Handle crc_LastLoadedPin (current location)
        current_location_id = None
        if tree is not None:
            root = tree.getroot()
            # Check PlayerProfile element first (this is where it actually is)
            player_profile = root.find("PlayerProfile")
            if player_profile is not None and player_profile.get("crc_LastLoadedPin") is not None:
                current_location_id = player_profile.get("crc_LastLoadedPin")
                print(f"DEBUG: Found crc_LastLoadedPin in PlayerProfile: {current_location_id}")
            else:
                # Check root element as fallback
                if root.get("crc_LastLoadedPin") is not None:
                    current_location_id = root.get("crc_LastLoadedPin")
                    print(f"DEBUG: Found crc_LastLoadedPin in root: {current_location_id}")
                else:
                    # Check BaseInfo as final fallback
                    base_info = root.find(".//BaseInfo")
                    if base_info is not None and base_info.get("crc_LastLoadedPin") is not None:
                        current_location_id = base_info.get("crc_LastLoadedPin")
                        print(f"DEBUG: Found crc_LastLoadedPin in BaseInfo: {current_location_id}")

        # Update the current location dropdown
        if "crc_LastLoadedPin" in self.entries:
            widget = self.entries["crc_LastLoadedPin"]
            if current_location_id and current_location_id in self.last_loaded_pin_mappings:
                location_name = self.last_loaded_pin_mappings[current_location_id]
                try:
                    if hasattr(widget, 'set'):
                        widget.set(location_name)
                        print(f"DEBUG: Set current location to: {location_name} (ID: {current_location_id})")
                except Exception as e:
                    print(f"DEBUG: Error setting current location: {e}")
            else:
                # No location found or unknown location ID
                try:
                    if hasattr(widget, 'set'):
                        if current_location_id:
                            # Show the unknown ID in a user-friendly way
                            widget.set(f"Unknown Location (ID: {current_location_id})")
                            print(f"DEBUG: Unknown location ID: {current_location_id}")
                        else:
                            # No location set at all
                            widget.set("-No Location Set-")
                            print("DEBUG: No crc_LastLoadedPin found in save file")
                except Exception as e:
                    print(f"DEBUG: Error setting current location fallback: {e}")

        # Format location with map name
        formatted_location = self._format_location_display(location_value)

        # Get bEntityScanningEnabled from BaseInfo (correct location)
        entity_scanning_value = base_info.get("bEntityScanningEnabled", "0") if base_info is not None else "0"

        # Update other fields with proper mapping
        field_mappings = {
            "side": {
                "xml_key": "side",
                "value_map": {"4": "Undecided", "1": "Na'vi", "2": "RDA", "3": "Neutral"},
                "default": "4"
            },
            "pawn": {
                "xml_key": "pawn", 
                "value_map": {"1": "Na'vi", "2": "RDA"},  # No Animals option
                "default": "1"
            },
            "isfemale": {
                "xml_key": "isfemale",
                "value_map": {"0": "Male", "1": "Female"},
                "default": "0"
            },
            "face": {
                "xml_key": "face",
                "custom_handler": True
            },
            "bEntityScanningEnabled": {
                "custom_value": entity_scanning_value,  # Use the value we found from BaseInfo
                "value_map": {"0": "Disabled", "1": "Enabled"}
            },
            "TotalEP": {
                "xml_key": "TotalEP",
                "custom_handler": True
            },
            "RecoveryBits": {
                "xml_key": "RecoveryBits",
                "default": "0"
            },
            "YouAreHere_LatitudeLongitude": {
                "custom_value": formatted_location  # Use formatted location with map name
            }
        }

        for entry_key, config in field_mappings.items():
            if entry_key in self.entries:
                widget = self.entries[entry_key]
                
                # Handle custom values (like location and entity scanning)
                if "custom_value" in config:
                    raw_value = config["custom_value"]
                    if "value_map" in config:
                        value = config["value_map"].get(raw_value, list(config["value_map"].values())[0])
                    else:
                        value = raw_value
                # Handle custom processing
                elif config.get("custom_handler"):
                    if entry_key == "face":
                        face_value = base_info.get("face", "0")
                        is_female = base_info.get("isfemale", "0") == "1"
                        if face_value in self.face_values:
                            value = self.face_values[face_value]["female" if is_female else "male"]
                        else:
                            value = "Male 00"
                    elif entry_key == "TotalEP":
                        # Get faction for max EP calculation
                        faction = "0"
                        if tree is not None:
                            metagame = tree.getroot().find("Metagame")
                            if metagame is not None:
                                faction = metagame.get("PlayerFaction", "0")
                        
                        total_ep = base_info.get("TotalEP", "0")
                        max_ep = 500000 if faction == "1" else 500000
                        value = f"{total_ep}/{max_ep} (Max EP)"
                    else:
                        value = base_info.get(config["xml_key"], config.get("default", "0"))
                # Handle mapped values
                elif "value_map" in config:
                    raw_value = base_info.get(config["xml_key"], config.get("default", "0"))
                    value = config["value_map"].get(raw_value, list(config["value_map"].values())[0])
                    print(f"DEBUG: {entry_key} - raw: {raw_value}, mapped: {value}")
                # Handle direct values
                else:
                    value = base_info.get(config["xml_key"], config.get("default", "0"))
                
                # Update the widget - FIXED LOGIC HERE
                try:
                    # Check if it's a combobox first (has 'set' method and 'values' property)
                    if hasattr(widget, 'set') and hasattr(widget, 'configure') and 'values' in widget.configure():
                        # It's a Combobox - verify the value is in the list
                        try:
                            current_values = widget['values']
                            if value in current_values:
                                widget.set(value)
                                print(f"DEBUG: Updated combobox {entry_key} with: {value}")
                            else:
                                print(f"DEBUG: Value '{value}' not in combobox values {current_values} for {entry_key}")
                                # Set to first value as fallback
                                if current_values:
                                    widget.set(current_values[0])
                                    print(f"DEBUG: Set {entry_key} to fallback value: {current_values[0]}")
                        except Exception as combo_error:
                            print(f"DEBUG: Combobox error for {entry_key}: {combo_error}")
                            widget.set(value)  # Try anyway
                    # Check if it's a label (has 'config' and 'cget' but no 'set')
                    elif hasattr(widget, 'config') and hasattr(widget, 'cget') and not hasattr(widget, 'set'):
                        # It's a Label
                        widget.config(text=value)
                        print(f"DEBUG: Updated label {entry_key} with: {value}")
                    # Otherwise assume it's an Entry
                    else:
                        # It's an Entry
                        widget.delete(0, tk.END)
                        widget.insert(0, value)
                        print(f"DEBUG: Updated entry {entry_key} with: {value}")
                except Exception as e:
                    print(f"DEBUG: Error updating {entry_key}: {e}")
                    print(f"DEBUG: Widget type: {type(widget)}")
                    print(f"DEBUG: Widget methods: {[method for method in dir(widget) if not method.startswith('_')]}")

        # Update face image
        if "face" in self.entries:
            self._on_face_selected()

        if tree is not None:
            try:
                self.load_time_info(tree)
            except Exception as time_error:
                self.logger.error(f"Error loading time info in base_info update: {time_error}")

    def _update_metagame_info(self, metagame):
        """Update metagame information"""
        if "NaviCostReduction" in self.entries:
            value = metagame.get("NaviCostReduction", "0")
            self.entries["NaviCostReduction"].delete(0, tk.END)
            self.entries["NaviCostReduction"].insert(0, value)

        if "CorpCostReduction" in self.entries:
            value = metagame.get("CorpCostReduction", "0")
            self.entries["CorpCostReduction"].delete(0, tk.END)
            self.entries["CorpCostReduction"].insert(0, value)

        faction_value = metagame.get("PlayerFaction", "0")
        faction_map = {"0": "Undecided", "1": "Na'vi", "2": "RDA", "3": "Neutral"}
        if "PlayerFaction" in self.entries:
            self.entries["PlayerFaction"].set(faction_map.get(faction_value, "Undecided"))

    def _update_metagame_player_info(self, metagame):
        """Update player EP information"""
        player0 = metagame.find("Player0")
        if player0 is not None:
            if "EPs" in self.entries:
                eps_value = player0.get("EPs", "0")
                self.entries["EPs"].delete(0, tk.END)
                self.entries["EPs"].insert(0, eps_value)
                
            if "newEPs" in self.entries:
                new_eps_value = player0.get("newEPs", "0")
                self.entries["newEPs"].delete(0, tk.END)
                self.entries["newEPs"].insert(0, new_eps_value)
        
        player1 = metagame.find("Player1")
        if player1 is not None:
            if "EPs_Player1" in self.entries:
                eps_value = player1.get("EPs", "0")
                self.entries["EPs_Player1"].delete(0, tk.END)
                self.entries["EPs_Player1"].insert(0, eps_value)
                
            if "newEPs_Player1" in self.entries:
                new_eps_value = player1.get("newEPs", "0")
                self.entries["newEPs_Player1"].delete(0, tk.END)
                self.entries["newEPs_Player1"].insert(0, new_eps_value)

    def _update_options_info(self, options_info):
        """Update options information"""
        if options_info is None:
            return

        mappings = {
            "RumbleEnabled": "RumbleEnabled",
            "FirstPersonMode": "FirstPersonMode"
        }

        for xml_key, entry_key in mappings.items():
            if entry_key in self.entries:
                value = "Enabled" if options_info.get(xml_key, "0") == "1" else "Disabled"
                self.entries[entry_key].set(value)

    def _update_loadout_display(self, profile: ET.Element) -> None:
        """Update the RDA loadout display with current equipment"""
        # Update weapons
        weapons = self._get_equipped_weapons(profile)
        
        # XML slot order was Right=0,Down=1,Left=2,Top=3; display order is Top=0,Right=1,Down=2,Left=3
        _xml_to_display = {0: 1, 1: 2, 2: 3, 3: 0}
        for slot_num, slot_data in weapons.items():
            display_slot = _xml_to_display.get(slot_num, slot_num)
            if display_slot < len(self.weapon_slots):
                main_weapon = self._get_weapon_info(profile, slot_data["main"])

                if main_weapon:
                    # Get the dropdown for this slot
                    if "dropdown" in self.weapon_slots[display_slot]:
                        weapon_name = main_weapon["name"]
                        dropdown = self.weapon_slots[display_slot]["dropdown"]
                        dropdown.set(weapon_name)

                        # Load weapon GIF in its specific slot
                        weapon_id = main_weapon["id"]
                        self._load_weapon_image(weapon_id, display_slot, is_navi=False)

                        # Update ammo entry
                        if "ammo_entry" in self.weapon_slots[display_slot]:
                            ammo_entry = self.weapon_slots[display_slot]["ammo_entry"]
                            ammo_entry.delete(0, tk.END)

                            # For melee weapons, show "Melee" in the ammo entry
                            if main_weapon.get("is_melee", False):
                                ammo_entry.insert(0, "Melee")
                                ammo_entry.configure(state="disabled")
                            # For weapons with infinite ammo, disable the field
                            elif main_weapon.get("infinite_ammo", False):
                                ammo_entry.insert(0, "∞")
                                ammo_entry.configure(state="disabled")
                            else:
                                # For normal weapons, keep field enabled
                                ammo_entry.insert(0, main_weapon.get("total_ammo", "0"))
                                ammo_entry.configure(state="normal")

                        # Update clip size label
                        if "clip_entry" in self.weapon_slots[display_slot]:
                            clip_label = self.weapon_slots[display_slot]["clip_entry"]

                            # For melee weapons, we don't need to show anything in the clip
                            if main_weapon.get("is_melee", False):
                                clip_label.config(text="--")
                            # For infinite ammo weapons, show ∞
                            elif main_weapon.get("infinite_ammo", False):
                                clip_label.config(text="∞")
                            else:
                                clip_label.config(text=main_weapon.get("ammo", "0"))

                        # Set infinite ammo checkbox based on weapon info
                        if "infinite_var" in self.weapon_slots[display_slot]:
                            infinite_var = self.weapon_slots[display_slot]["infinite_var"]
                            is_infinite = main_weapon.get("infinite_ammo", False)
                            infinite_var.set(is_infinite)

                            # Disable infinite ammo checkbox for melee or inherently infinite weapons
                            if "infinite_check" in self.weapon_slots[display_slot]:
                                infinite_check = self.weapon_slots[display_slot]["infinite_check"]
                                # For melee weapons OR weapons with inherent infinite ammo, disable checkbox
                                inherent_infinite = main_weapon.get("is_melee", False) or any(
                                    keyword in main_weapon["name"].lower() for keyword in ["wasp pistol"]
                                )

                                # Correctly set and disable checkbox for weapons that should have fixed ammo settings
                                if inherent_infinite:
                                    # Configure the checkbox to be disabled but checked for these weapons
                                    infinite_check.state(['disabled'])
                                    # Rebind to prevent any clicking for special weapons
                                    for event_name in ["<ButtonPress-1>", "<ButtonRelease-1>", "<space>"]:
                                        infinite_check.bind(event_name, lambda e: "break")
                                else:
                                    # Regular weapons can have their infinite ammo toggled
                                    infinite_check.state(['!disabled'])
                                    # Restore normal binding for regular weapons
                                    for event_name in ["<ButtonPress-1>", "<ButtonRelease-1>", "<space>"]:
                                        infinite_check.unbind(event_name)
                                    # Re-bind the toggle function
                                    infinite_check.bind('<ButtonRelease-1>', lambda e, idx=display_slot, navi=False:
                                        self._toggle_infinite_ammo(e, idx, navi))
                else:
                    # Set to empty if no weapon
                    if "dropdown" in self.weapon_slots[display_slot]:
                        self.weapon_slots[display_slot]["dropdown"].set("-Empty-")

                        # Clear weapon GIF for this slot
                        faction_key = 'rda'
                        if hasattr(self, 'weapon_preview_labels') and faction_key in self.weapon_preview_labels:
                            if display_slot in self.weapon_preview_labels[faction_key]:
                                preview_label = self.weapon_preview_labels[faction_key][display_slot]
                                preview_label.configure(image="", text="No Weapon")
                                if hasattr(preview_label, 'frames'):
                                    delattr(preview_label, 'frames')

                        # Reset ammo entry
                        if "ammo_entry" in self.weapon_slots[display_slot]:
                            ammo_entry = self.weapon_slots[display_slot]["ammo_entry"]
                            ammo_entry.delete(0, tk.END)
                            ammo_entry.insert(0, "0")
                            ammo_entry.configure(state="normal")

                        # Reset clip label
                        if "clip_entry" in self.weapon_slots[display_slot]:
                            clip_label = self.weapon_slots[display_slot]["clip_entry"]
                            clip_label.config(text="0")

                        # Reset infinite ammo checkbox
                        if "infinite_var" in self.weapon_slots[display_slot]:
                            self.weapon_slots[display_slot]["infinite_var"].set(False)

                        # Enable the infinite checkbox since no weapon is selected
                        if "infinite_check" in self.weapon_slots[display_slot]:
                            infinite_check = self.weapon_slots[display_slot]["infinite_check"]
                            infinite_check.state(['!disabled'])
                            # Clear any special bindings
                            for event_name in ["<ButtonPress-1>", "<ButtonRelease-1>", "<space>"]:
                                infinite_check.unbind(event_name)
                            # Re-bind the toggle function
                            infinite_check.bind('<ButtonRelease-1>', lambda e, idx=slot_num, navi=False: 
                                self._toggle_infinite_ammo(e, idx, navi))

        # Update armor dropdowns
        armor_info = self._get_armor_info(profile)
        for slot_type, dropdown in self.armor_dropdowns.items():
            if armor_info[slot_type]:
                dropdown.set(armor_info[slot_type]["name"])
            else:
                dropdown.set("-Empty-")
        
        # Load armor preview images
        for slot_type, dropdown in self.armor_dropdowns.items():
            armor_name = dropdown.get()
            if armor_name != "-Empty-" and slot_type in self.rda_armor_ids:
                armor_id = self.rda_armor_ids[slot_type].get(armor_name)
                if armor_id:
                    self._load_armor_image(armor_id, slot_type, is_navi=False)
            elif armor_name == "-Empty-" and slot_type in self.armor_preview_labels:
                # Clear preview for empty slots
                preview_label = self.armor_preview_labels[slot_type]
                preview_label.configure(image="", text="No Armor")
                if hasattr(preview_label, 'frames'):
                    delattr(preview_label, 'frames')

    def _update_navi_loadout_display(self, profile: ET.Element) -> None:
        """Update the Na'vi loadout display with current equipment"""
        # Update weapons
        weapons = self._get_avatar_weapons(profile)
        
        # XML slot order was Right=0,Down=1,Left=2,Top=3; display order is Top=0,Right=1,Down=2,Left=3
        _xml_to_display = {0: 1, 1: 2, 2: 3, 3: 0}
        for slot_num, slot_data in weapons.items():
            display_slot = _xml_to_display.get(slot_num, slot_num)
            if display_slot < len(self.navi_weapon_slots):
                main_weapon = self._get_avatar_weapon_info(profile, slot_data["main"])

                if main_weapon:
                    # Get the dropdown for this slot
                    if "dropdown" in self.navi_weapon_slots[display_slot]:
                        weapon_name = main_weapon["name"]
                        dropdown = self.navi_weapon_slots[display_slot]["dropdown"]
                        dropdown.set(weapon_name)

                        # Load weapon GIF in its specific slot
                        weapon_id = main_weapon["id"]
                        self._load_weapon_image(weapon_id, display_slot, is_navi=True)

                        # Update ammo entry
                        if "ammo_entry" in self.navi_weapon_slots[display_slot]:
                            ammo_entry = self.navi_weapon_slots[display_slot]["ammo_entry"]
                            ammo_entry.delete(0, tk.END)

                            # For melee weapons, show "Melee" in the ammo entry
                            if main_weapon.get("is_melee", False):
                                ammo_entry.insert(0, "Melee")
                                ammo_entry.configure(state="disabled")
                            # For weapons with infinite ammo, disable the field
                            elif main_weapon.get("infinite_ammo", False):
                                ammo_entry.insert(0, "∞")
                                ammo_entry.configure(state="disabled")
                            else:
                                # For normal weapons, keep field enabled
                                ammo_entry.insert(0, main_weapon.get("total_ammo", "0"))
                                ammo_entry.configure(state="normal")

                        # Update clip size label
                        if "clip_entry" in self.navi_weapon_slots[display_slot]:
                            clip_label = self.navi_weapon_slots[display_slot]["clip_entry"]

                            # For melee weapons, we don't need to show anything in the clip
                            if main_weapon.get("is_melee", False):
                                clip_label.config(text="--")
                            # For infinite ammo weapons, show ∞
                            elif main_weapon.get("infinite_ammo", False):
                                clip_label.config(text="∞")
                            else:
                                clip_label.config(text=main_weapon.get("ammo", "0"))

                        # Set infinite ammo checkbox based on weapon info
                        if "infinite_var" in self.navi_weapon_slots[display_slot]:
                            infinite_var = self.navi_weapon_slots[display_slot]["infinite_var"]
                            is_infinite = main_weapon.get("infinite_ammo", False)
                            infinite_var.set(is_infinite)

                            # Disable infinite ammo checkbox for melee or inherently infinite weapons
                            if "infinite_check" in self.navi_weapon_slots[display_slot]:
                                infinite_check = self.navi_weapon_slots[display_slot]["infinite_check"]
                                # For melee weapons OR weapons with inherent infinite ammo, disable checkbox
                                inherent_infinite = main_weapon.get("is_melee", False) or "dual blade" in main_weapon["name"].lower() or "club" in main_weapon["name"].lower() or "staff" in main_weapon["name"].lower() or "axe" in main_weapon["name"].lower()

                                # Correctly set and disable checkbox for weapons that should have fixed ammo settings
                                if inherent_infinite:
                                    # Configure the checkbox to be disabled but checked for these weapons
                                    infinite_check.state(['disabled'])
                                    # Rebind to prevent any clicking for special weapons - this will block all events
                                    for event_name in ["<ButtonPress-1>", "<ButtonRelease-1>", "<space>"]:
                                        infinite_check.bind(event_name, lambda e: "break")
                                else:
                                    # Regular weapons can have their infinite ammo toggled
                                    infinite_check.state(['!disabled'])
                                    # Restore normal binding for regular weapons
                                    for event_name in ["<ButtonPress-1>", "<ButtonRelease-1>", "<space>"]:
                                        infinite_check.unbind(event_name)
                                    # Re-bind the toggle function
                                    infinite_check.bind('<ButtonRelease-1>', lambda e, idx=display_slot, navi=True:
                                        self._toggle_infinite_ammo(e, idx, navi))
                else:
                    # Set to empty if no weapon
                    if "dropdown" in self.navi_weapon_slots[display_slot]:
                        self.navi_weapon_slots[display_slot]["dropdown"].set("-Empty-")

                        # Clear weapon GIF for this slot
                        faction_key = 'navi'
                        if hasattr(self, 'weapon_preview_labels') and faction_key in self.weapon_preview_labels:
                            if display_slot in self.weapon_preview_labels[faction_key]:
                                preview_label = self.weapon_preview_labels[faction_key][display_slot]
                                preview_label.configure(image="", text="No Weapon")
                                if hasattr(preview_label, 'frames'):
                                    delattr(preview_label, 'frames')

                        # Reset ammo entry
                        if "ammo_entry" in self.navi_weapon_slots[display_slot]:
                            ammo_entry = self.navi_weapon_slots[display_slot]["ammo_entry"]
                            ammo_entry.delete(0, tk.END)
                            ammo_entry.insert(0, "0")
                            ammo_entry.configure(state="normal")

                        # Reset clip label
                        if "clip_entry" in self.navi_weapon_slots[display_slot]:
                            clip_label = self.navi_weapon_slots[display_slot]["clip_entry"]
                            clip_label.config(text="0")

                        # Reset infinite ammo checkbox
                        if "infinite_var" in self.navi_weapon_slots[display_slot]:
                            self.navi_weapon_slots[display_slot]["infinite_var"].set(False)

                        # Enable the infinite checkbox since no weapon is selected
                        if "infinite_check" in self.navi_weapon_slots[display_slot]:
                            infinite_check = self.navi_weapon_slots[display_slot]["infinite_check"]
                            infinite_check.state(['!disabled'])
                            # Clear any special bindings
                            for event_name in ["<ButtonPress-1>", "<ButtonRelease-1>", "<space>"]:
                                infinite_check.unbind(event_name)
                            # Re-bind the toggle function
                            infinite_check.bind('<ButtonRelease-1>', lambda e, idx=slot_num, navi=True: 
                                self._toggle_infinite_ammo(e, idx, navi))

        # Update armor dropdowns
        armor_info = self._get_navi_armor_info(profile)
        for slot_type, dropdown in self.navi_armor_dropdowns.items():
            if armor_info[slot_type]:
                dropdown.set(armor_info[slot_type]["name"])
            else:
                dropdown.set("-Empty-")
        
        # Load armor preview images
        for slot_type, dropdown in self.navi_armor_dropdowns.items():
            armor_name = dropdown.get()
            if armor_name != "-Empty-" and slot_type in self.navi_armor_ids:
                armor_id = self.navi_armor_ids[slot_type].get(armor_name)
                if armor_id:
                    self._load_armor_image(armor_id, slot_type, is_navi=True)
            elif armor_name == "-Empty-" and slot_type in self.navi_armor_preview_labels:
                # Clear preview for empty slots
                preview_label = self.navi_armor_preview_labels[slot_type]
                preview_label.configure(image="", text="No Armor")
                if hasattr(preview_label, 'frames'):
                    delattr(preview_label, 'frames')

    def _update_player_info(self, profile: ET.Element) -> None:
        """Update player info in the XML structure"""
        recovery = profile.find("Possessions_Recovery")
        if recovery is not None:
            recovery_bits = recovery.get("RecoveryBits", "0")
            
            # Cap at 500
            try:
                recovery_bits_int = int(recovery_bits)
                if recovery_bits_int > 500:
                    recovery_bits = "500"
                    recovery.set("RecoveryBits", "500")
            except ValueError:
                recovery_bits = "0"
            
            # Update the RecoveryBits display
            if "RecoveryBits" in self.entries:
                widget = self.entries["RecoveryBits"]
                if isinstance(widget, ttk.Label):
                    widget.config(text=recovery_bits)
                else:
                    widget.delete(0, tk.END)
                    widget.insert(0, recovery_bits)

    def _name_vec_to_string(self, name_vec):
        """Convert name vector to readable string"""
        try:
            if not name_vec or not name_vec.startswith("Count("):
                return ""

            parts = name_vec.split(") ")
            if len(parts) < 2:
                return ""

            values = parts[1].rstrip(";").split(";")
            name = "".join(chr(int(val)) for val in values if val)
            return name
        except Exception as e:
            self.logger.error(f"Error converting name vector: {str(e)}")
            return ""

    def _string_to_name_vec(self, name):
        """Convert string to namevec format"""
        try:
            if not name:
                return "Count(0) "
            values = [str(ord(char)) for char in name]
            count = len(values)
            return f"Count({count}) {';'.join(values)};"
        except Exception as e:
            self.logger.error(f"Error converting string to name vector: {str(e)}")
            return "Count(0) "

    def get_stats_updates(self) -> Dict[str, Dict[str, str]]:
        """Get all stats updates for saving - COMPLETE IMPLEMENTATION"""
        try:
            updates = {
                "BaseInfo": {},
                "XpInfo": {},
                "OptionsInfo": {},
                "Metagame": {},
                "Player0": {},
                "Player1": {},
                "TimeInfo": {},
                "PlayerProfile": {}
            }

            # Get faction updates
            if "PlayerFaction" in self.entries:
                current_faction = self.entries["PlayerFaction"].get()
                faction_map = {"Undecided": "0", "Na'vi": "1", "Navi": "1", "RDA": "2", "Neutral": "3"}
                faction_value = faction_map.get(current_faction, "0")
                updates["Metagame"]["PlayerFaction"] = faction_value

            if "crc_LastLoadedPin" in self.entries:
                selected_location = self.entries["crc_LastLoadedPin"].get()
                
                if selected_location == "-No Location Set-":
                    # Set to None to remove the attribute
                    updates["PlayerProfile"]["crc_LastLoadedPin"] = None
                elif selected_location.startswith("Unknown Location (ID: "):
                    # Extract the ID from the display text for unknown locations
                    pin_id = selected_location.split("ID: ")[1].rstrip(")")
                    updates["PlayerProfile"]["crc_LastLoadedPin"] = pin_id
                else:
                    # Find the pin ID from the selected location name
                    for pin_id, location_name in self.last_loaded_pin_mappings.items():
                        if location_name == selected_location:
                            updates["PlayerProfile"]["crc_LastLoadedPin"] = pin_id
                            break

            # Get side and pawn updates for BaseInfo
            if "side" in self.entries:
                side_value = self.entries["side"].get()
                side_map = {"Undecided": "4", "Na'vi": "1", "RDA": "2", "Neutral": "3"}
                updates["BaseInfo"]["side"] = side_map.get(side_value, "4")
                
            if "pawn" in self.entries:
                pawn_value = self.entries["pawn"].get()
                pawn_map = {"Na'vi": "1", "RDA": "2"}  # No Animals option
                updates["BaseInfo"]["pawn"] = pawn_map.get(pawn_value, "1")

            # Get Entity Scanning update for BaseInfo (correct location)
            if "bEntityScanningEnabled" in self.entries:
                entity_value = self.entries["bEntityScanningEnabled"].get()
                entity_map = {"Disabled": "0", "Enabled": "1"}
                updates["BaseInfo"]["bEntityScanningEnabled"] = entity_map.get(entity_value, "0")

            # Get other options
            if "RumbleEnabled" in self.entries:
                value = "1" if self.entries["RumbleEnabled"].get() == "Enabled" else "0"
                updates["OptionsInfo"]["RumbleEnabled"] = value
            if "FirstPersonMode" in self.entries:
                value = "1" if self.entries["FirstPersonMode"].get() == "Enabled" else "0"
                updates["OptionsInfo"]["FirstPersonMode"] = value

            # Get EP values
            if "EPs" in self.entries and "newEPs" in self.entries:
                updates["Player0"]["EPs"] = self.entries["EPs"].get()
                updates["Player0"]["newEPs"] = self.entries["newEPs"].get()

            if "EPs_Player1" in self.entries and "newEPs_Player1" in self.entries:
                updates["Player1"]["EPs"] = self.entries["EPs_Player1"].get()
                updates["Player1"]["newEPs"] = self.entries["newEPs_Player1"].get()

            # Get cost reduction values
            if "NaviCostReduction" in self.entries:
                updates["Metagame"]["NaviCostReduction"] = self.entries["NaviCostReduction"].get()
            if "CorpCostReduction" in self.entries:
                updates["Metagame"]["CorpCostReduction"] = self.entries["CorpCostReduction"].get()

            # Get RecoveryBits (cap at 500)
            if "RecoveryBits" in self.entries:
                recovery_value = self.entries["RecoveryBits"].get()
                try:
                    recovery_int = int(recovery_value)
                    if recovery_int > 500:
                        recovery_value = "500"
                        # Update the UI to show capped value
                        self.entries["RecoveryBits"].delete(0, tk.END)
                        self.entries["RecoveryBits"].insert(0, "500")
                        show_warning("Value Capped", "Recovery Bits cannot exceed 500. Value has been set to 500.")
                    elif recovery_int < 0:
                        recovery_value = "0"
                        # Update the UI to show minimum value
                        self.entries["RecoveryBits"].delete(0, tk.END)
                        self.entries["RecoveryBits"].insert(0, "0")
                except ValueError:
                    recovery_value = "0"
                    # Update the UI to show default value
                    self.entries["RecoveryBits"].delete(0, tk.END)
                    self.entries["RecoveryBits"].insert(0, "0")
                
                updates["BaseInfo"]["RecoveryBits"] = recovery_value

            # Extract TotalEP from the formatted display
            if "TotalEP" in self.entries:
                total_ep_widget = self.entries["TotalEP"]
                total_ep_text = total_ep_widget.cget("text") if hasattr(total_ep_widget, 'cget') else total_ep_widget.get()

                # Extract actual EP value from "12345/500000 (Max EP)" format
                if "/" in total_ep_text:
                    actual_ep = total_ep_text.split("/")[0]
                    updates["BaseInfo"]["TotalEP"] = actual_ep

            # Get character name update
            if "namevec" in self.entries:
                widget = self.entries["namevec"]
                if hasattr(widget, 'get'):
                    name = widget.get()[:10]
                    updates["BaseInfo"]["namevec"] = self._string_to_name_vec(name)

            # Get Environment Time from the main window entry (HH:MM:SS → seconds)
            if hasattr(self.main_window, 'env_time_var'):
                env_time_val = self.main_window.env_time_var.get().strip()
                if env_time_val:
                    try:
                        if ':' in env_time_val:
                            parts = env_time_val.split(':')
                            h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
                            updates["TimeInfo"]["EnvTime"] = str(h * 3600 + m * 60 + s)
                        else:
                            # Fallback: user may have typed raw seconds
                            updates["TimeInfo"]["EnvTime"] = str(int(float(env_time_val)))
                    except (ValueError, IndexError):
                        self.logger.warning(f"Invalid EnvTime format, skipping: {env_time_val}")

            return updates
        except Exception as e:
            self.logger.error(f"Error getting stats updates: {str(e)}")
            raise

    def load_time_info(self, tree):
        """Load time info from the XML tree and update displays - FIXED MAPPING + AUTO ENV TIME"""
        try:
            self.logger.debug("Loading time info from save file")
            root = tree.getroot()
            profile = root.find("PlayerProfile")
            
            if profile is None:
                self.logger.warning("PlayerProfile not found in XML")
                return
                
            time_info = profile.find("TimeInfo")
            if time_info is None:
                self.logger.warning("TimeInfo not found in PlayerProfile")
                return
            
            # Extract the exact values from your save file format
            game_time_raw = time_info.get("GameTime", "0")
            played_time_raw = time_info.get("PlayedTime", "0")
            env_time_raw = time_info.get("EnvTime", "0")

            # Populate the editable Environment Time entry in HH:MM:SS format
            if hasattr(self.main_window, 'env_time_var'):
                try:
                    total = int(float(env_time_raw))
                    h = total // 3600
                    m = (total % 3600) // 60
                    s = total % 60
                    self.main_window.env_time_var.set(f"{h:02d}:{m:02d}:{s:02d}")
                except (ValueError, TypeError):
                    self.main_window.env_time_var.set("12:00:00")
                # Refresh checkbox state (no event → no unsaved mark)
                if hasattr(self.main_window, '_on_env_time_changed'):
                    self.main_window._on_env_time_changed()
            
            self.logger.debug(f"Raw time values - GameTime: {game_time_raw}, PlayedTime: {played_time_raw}, EnvTime: {env_time_raw}")
            
            # Format the times for display
            formatted_times = {
                "GameTime": self._format_time_seconds(game_time_raw),
                "PlayedTime": self._format_time_seconds(played_time_raw),
                "EnvTime": self._format_time_seconds(env_time_raw)
            }
            
            self.logger.debug(f"Formatted times: {formatted_times}")
            
            # Update main window's time display with correct mapping
            if hasattr(self.main_window, 'time_labels'):
                self._update_main_window_time_labels(formatted_times)
            
            # Also update StatsManager entries if they exist
            self._update_stats_manager_time_entries(formatted_times)
            
        except Exception as e:
            self.logger.error(f"Error loading time info: {str(e)}", exc_info=True)

    def _update_main_window_time_labels(self, formatted_times):
        """Update the main window's time_labels dictionary"""
        try:
            # Mapping from XML attributes to main window display names
            # EnvTime is handled separately via env_time_var (HH:MM:SS entry)
            time_mapping = {
                "GameTime": "Game Time",
                "PlayedTime": "Played Time",
            }
            
            self.logger.debug("Updating main window time labels...")
            
            for xml_key, display_key in time_mapping.items():
                if display_key in self.main_window.time_labels:
                    label_widget = self.main_window.time_labels[display_key]
                    formatted_value = formatted_times[xml_key]
                    
                    try:
                        label_widget.config(text=formatted_value)
                        self.logger.debug(f"✅ Updated main window '{display_key}': {formatted_value}")
                    except Exception as e:
                        self.logger.error(f"❌ Error updating main window '{display_key}': {e}")
                else:
                    self.logger.warning(f"⚠️ Main window time label '{display_key}' not found")
                    
            # Debug: Show what time labels actually exist
            if hasattr(self.main_window, 'time_labels'):
                self.logger.debug(f"Available time labels: {list(self.main_window.time_labels.keys())}")
            
        except Exception as e:
            self.logger.error(f"Error updating main window time labels: {str(e)}")

    def _update_stats_manager_time_entries(self, formatted_times):
        """Update StatsManager's own time entries if they exist"""
        # StatsManager doesn't have its own time fields - they're only in main window
        # This method is kept for potential future use but currently does nothing
        return

    def _update_single_time_widget(self, widget, field_name, formatted_value):
        """Update a single time widget - handles all widget types"""
        try:
            # Method 1: Try Label (most common for read-only displays)
            if hasattr(widget, 'config') and hasattr(widget, 'cget'):
                try:
                    widget.config(text=formatted_value)
                    self.logger.debug(f"Updated {field_name} as Label")
                    return True
                except Exception as e:
                    self.logger.debug(f"Label update failed for {field_name}: {e}")
            
            # Method 2: Try Combobox
            if hasattr(widget, 'set') and hasattr(widget, 'get'):
                try:
                    widget.set(formatted_value)
                    self.logger.debug(f"Updated {field_name} as Combobox")
                    return True
                except Exception as e:
                    self.logger.debug(f"Combobox update failed for {field_name}: {e}")
            
            # Method 3: Try Entry
            if hasattr(widget, 'delete') and hasattr(widget, 'insert'):
                try:
                    widget.delete(0, tk.END)
                    widget.insert(0, formatted_value)
                    self.logger.debug(f"Updated {field_name} as Entry")
                    return True
                except Exception as e:
                    self.logger.debug(f"Entry update failed for {field_name}: {e}")
            
            # If we get here, we couldn't update the widget
            self.logger.warning(f"Could not determine how to update widget type {type(widget)} for {field_name}")
            return False
            
        except Exception as e:
            self.logger.error(f"Exception updating {field_name} widget: {str(e)}")
            return False

    def _format_time_seconds(self, time_str):
        """Convert seconds to readable time format (handles decimals)"""
        try:
            # Handle decimal seconds (like PlayedTime="25800.3")
            total_seconds = float(time_str)
            
            # Convert to integer seconds for display
            total_seconds_int = int(total_seconds)
            
            # Calculate hours, minutes, seconds
            hours = total_seconds_int // 3600
            minutes = (total_seconds_int % 3600) // 60
            seconds = total_seconds_int % 60
            
            return f"{hours:02d}h {minutes:02d}m {seconds:02d}s"
                
        except (ValueError, TypeError) as e:
            self.logger.error(f"Error formatting time '{time_str}': {e}")
            return "0h 00m 00s"  # Return default format if conversion fails

    # Debug method to check what time widgets exist in both locations
    def debug_all_time_widgets(self):
        """Debug method to see all time-related widgets"""
        self.logger.info("=== COMPLETE TIME WIDGET DEBUG ===")
        
        # Check main window time labels
        if hasattr(self.main_window, 'time_labels'):
            self.logger.info("Main Window time_labels:")
            for key, widget in self.main_window.time_labels.items():
                current_text = widget.cget('text') if hasattr(widget, 'cget') else "Unknown"
                self.logger.info(f"  '{key}': {type(widget)} - Current: '{current_text}'")
        else:
            self.logger.info("Main Window: No time_labels found")
        
        # Check StatsManager entries
        time_fields = ["GameTime", "PlayedTime", "EnvTime"]
        self.logger.info("StatsManager entries:")
        for field in time_fields:
            if field in self.entries:
                widget = self.entries[field]
                self.logger.info(f"  '{field}': {type(widget)}")
            else:
                self.logger.info(f"  '{field}': NOT FOUND")
        
        self.logger.info("=== END COMPLETE DEBUG ===")

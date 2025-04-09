import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
from typing import Dict, Optional
from ui_components import EnhancedTooltip, LabeledInput
from xml_handler import XMLHandler
import logging

class TerritoryManager:
    def __init__(self, parent: ttk.Frame, main_window=None):
        self.logger = logging.getLogger('TerritoryManager')
        self.logger.debug("Initializing TerritoryManager")
        self.parent = parent
        self.main_window = main_window  # Store reference to main window
        self.territory_tree = None
        self.territory_editors = {}
        self.setup_ui()

    def setup_ui(self) -> None:
        tree_frame = ttk.Frame(self.parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Label(tree_frame, text="Territory Status").pack()

        treeview_container = ttk.Frame(tree_frame)
        treeview_container.pack(fill=tk.BOTH, expand=True)

        self._create_territory_tree(treeview_container)
        self._create_territory_editors()

    def _create_territory_tree(self, container: ttk.Frame) -> None:
        columns = ("ID", "Faction", "Base Units", "Troops", "Ground", "Air", 
                  "Home Base", "Factory", "Defense Flags", "Taken Control")
        
        self.territory_tree = ttk.Treeview(
            container, 
            columns=columns,
            show="headings"
        )

        columns_config = {
            "ID": {"width": 80, "tooltip": "Territory ID"},
            "Faction": {"width": 80, "tooltip": "1=Navi, 2=Corp"},
            "Base Units": {"width": 80, "tooltip": "Number of base units"},
            "Troops": {"width": 80, "tooltip": "Number of troop units"},
            "Ground": {"width": 80, "tooltip": "Number of ground units"},
            "Air": {"width": 80, "tooltip": "Number of air units"},
            "Home Base": {"width": 80, "tooltip": "0=No, 2=Yes"},
            "Factory": {"width": 100, "tooltip": "0=No, 1=Yes"},
            "Defense Flags": {"width": 100, "tooltip": "0=No, 1=Yes"},
            "Taken Control": {"width": 80, "tooltip": "0=Inactive, 1=Active"}
        }

        for col, config in columns_config.items():
            self.territory_tree.heading(col, text=col)
            self.territory_tree.column(col, width=config["width"])
            header_label = ttk.Label(container, text=col)
            EnhancedTooltip(header_label, config["tooltip"])

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.territory_tree.yview)
        self.territory_tree.configure(yscrollcommand=scrollbar.set)

        self.territory_tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        self.territory_tree.bind("<<TreeviewSelect>>", self._on_territory_select)

    def _create_territory_editors(self) -> None:
        edit_frame = ttk.LabelFrame(self.parent, text="Edit Territory", padding=10)
        edit_frame.pack(fill=tk.X, pady=5)

        # Initialize the defense_flags_value variable first
        self.defense_flags_value = tk.IntVar(value=0)

        # Standard fields (unchanged except for label updates)
        standard_fields = [
            ("Faction", "Faction", {"0": "Undecided", "1": "Navi", "2": "Corp"}, "Select territory faction"),
            ("Base Units", "BaseUnits", None, "Number of base units"),
            ("Troops", "Troops", None, "Number of troop units"),
            ("Ground Units", "Ground", None, "Number of ground units"),
            ("Air Units", "Air", None, "Number of air units"),
            ("Home Base", "HomeBase", {"0": "No", "2": "Yes"}, "Is this a home base?"),
            ("Factory", "SecondaryBase", {"0": "No", "1": "Yes"}, "Is this a secondary base?"),
            ("Taken Control", "Active", {"0": "Inactive", "1": "Active"}, "Territory status")
        ]

        # Create rows with 3 fields each
        num_columns = 4
        for row_idx in range(0, len(standard_fields), num_columns):
            row_fields = standard_fields[row_idx:row_idx + num_columns]
            
            for col_idx, (label_text, key, values, tooltip) in enumerate(row_fields):
                input_widget = LabeledInput(
                    edit_frame, 
                    label_text, 
                    "combobox" if values else "entry",
                    values,
                    tooltip
                )
                input_widget.grid(row=row_idx // num_columns, column=col_idx, sticky="ew", padx=5, pady=2)
                self.territory_editors[key] = input_widget.input

        # Create a separate frame for Defense Flags checkboxes
        defense_flags_frame = ttk.LabelFrame(edit_frame, text="Defense Flags", padding=5)
        defense_flags_frame.grid(row=(len(standard_fields) + num_columns - 1) // num_columns, 
                                column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Define the defense flag options with their bit values
        defense_flag_options = [
            ("Defense from foot troops", 1, "Territory is defended against foot troops"),
            ("Defense from Ground Units", 2, "Territory is defended against ground vehicles"),
            ("Defense from Air Units", 4, "Territory is defended against air units"),
        ]
        
        # Store the checkboxes and bit values
        self.defense_flags_vars = {}
        self.defense_flags_bits = {}
        
        # Create checkboxes for each defense flag option in a horizontal layout
        for i, (flag_name, bit_value, tooltip) in enumerate(defense_flag_options):
            var = tk.IntVar(value=0)
            self.defense_flags_vars[flag_name] = var
            self.defense_flags_bits[flag_name] = bit_value
            
            checkbox = ttk.Checkbutton(
                defense_flags_frame,
                text=flag_name,
                variable=var,
                command=self._update_defense_flags_value
            )
            # Position them in a single row with some padding between them
            checkbox.grid(row=0, column=i, sticky="w", padx=10, pady=2)
            
            # Add tooltip
            EnhancedTooltip(checkbox, tooltip)
        
        # Create a label to show the current value
        self.defense_flags_label = ttk.Label(defense_flags_frame, text="Total Value: 0")
        self.defense_flags_label.grid(row=1, column=0, columnspan=len(defense_flag_options), pady=5)
        
        # Create button frame in a new row
        button_frame = ttk.Frame(edit_frame)
        button_frame.grid(row=(len(standard_fields) + num_columns - 1) // num_columns + 1, 
                        column=0, columnspan=num_columns, pady=10)

        ttk.Button(
            button_frame,
            text="Apply Changes",
            command=self._apply_territory_changes
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Reset",
            command=self._reset_territory_editors
        ).pack(side="left", padx=5)
        
        # Add the "Hard Mode" button
        ttk.Button(
            button_frame,
            text="Hard Mode",
            command=self._apply_hard_mode
        ).pack(side="left", padx=5)

    def _apply_hard_mode(self) -> None:
        """Apply Hard Mode by adding units to opposing faction territories"""
        self.logger.debug("Applying Hard Mode")
        
        # Confirm action with user
        response = messagebox.askyesno(
            "Hard Mode Confirmation",
            "WARNING: DON'T use if you have NOT picked a faction yet!\n\n"
            "Hard Mode will add additional units to the opposing faction territories. Continue?",
            icon="warning"
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
                
                for item in self.territory_tree.get_children():
                    values = self.territory_tree.item(item)["values"]
                    territory_faction = str(values[1])
                    if territory_faction == "1":
                        faction_1_count += 1
                    elif territory_faction == "2":
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
                messagebox.showerror("Error", error_msg)
                return
                
            # Define opponent faction 
            opponent_faction = "2" if player_faction == "1" else "1"
            self.logger.debug(f"Final determination - Player faction: {player_faction}, Opponent faction: {opponent_faction}")
            
            # Define unit boost amounts
            troop_boost = 3000
            ground_boost = 20
            air_boost = 10
            
            # Define defense flags - 7 means all defense flags are enabled (1+2+4)
            # 1 = Defense from foot troops
            # 2 = Defense from Ground Units
            # 4 = Defense from Air Units
            defense_flags_value = 7  # Enable all defense types
            
            # Factory setting (1 = Yes, 0 = No)
            factory_value = "1"  # Set to "Yes"
            
            # Apply boosts to all territories of the opposing faction
            territories_modified = 0
            
            for item in self.territory_tree.get_children():
                values = self.territory_tree.item(item)["values"]
                territory_faction = str(values[1])
                
                # Debug each territory being examined
                self.logger.debug(f"Checking territory ID: {values[0]}, Faction: {territory_faction}")
                
                # Only modify territories of the OPPOSING faction
                if territory_faction == opponent_faction:
                    # Get current values
                    territory_id = values[0]
                    troops = int(values[3] or 0) + troop_boost
                    ground = int(values[4] or 0) + ground_boost
                    air = int(values[5] or 0) + air_boost
                    
                    self.logger.debug(f"Modifying territory {territory_id} - Adding Troops: {troop_boost}, Ground: {ground_boost}, Air: {air_boost}")
                    self.logger.debug(f"Setting defense flags to {defense_flags_value} and factory to {factory_value}")
                    
                    # Update tree view with new values
                    new_values = list(values)
                    new_values[3] = str(troops)      # Troops
                    new_values[4] = str(ground)      # Ground
                    new_values[5] = str(air)         # Air
                    new_values[7] = factory_value    # Factory (SecondaryBase)
                    new_values[8] = str(defense_flags_value)  # Defense Flags
                    
                    self.territory_tree.item(item, values=new_values)
                    territories_modified += 1
                    
                    # Update the XML tree
                    if self.main_window and self.main_window.tree:
                        territory = self.main_window.tree.find(f".//Territory[@crc_ID='{territory_id}']")
                        if territory is not None:
                            # Update or create FreeUnits element
                            free_units = territory.find("FreeUnits")
                            if free_units is None:
                                free_units = ET.SubElement(territory, "FreeUnits")
                            
                            free_units.set("Troops", str(troops))
                            free_units.set("Ground", str(ground))
                            free_units.set("Air", str(air))
                            
                            # Set defense flags and factory
                            territory.set("DefenseFlags", str(defense_flags_value))
                            territory.set("SecondaryBase", factory_value)
                            
                            self.logger.debug(f"Updated territory {territory_id} XML for Hard Mode")
            
            if territories_modified == 0:
                self.logger.warning(f"No territories found with faction {opponent_faction} to modify")
                messagebox.showinfo("Hard Mode", "No enemy territories found to modify. Make sure territories are assigned to factions.")
                return
                
            # Mark as having unsaved changes
            if self.main_window:
                self.main_window.unsaved_label.config(text="Unsaved Changes")
            
            self.logger.debug(f"Hard Mode applied to {territories_modified} territories of the opposing faction ({opponent_faction}).")
            messagebox.showinfo("Hard Mode", 
                            f"Hard Mode applied to {territories_modified} territories of the opposing faction ({opponent_faction}).\n\n"
                            f"Added units per territory:\n"
                            f"• Troops: +{troop_boost}\n"
                            f"• Ground: +{ground_boost}\n"
                            f"• Air: +{air_boost}\n"
                            f"• All defense flags enabled\n"
                            f"• Factory enabled")
        
        except Exception as e:
            self.logger.error(f"Error applying Hard Mode: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to apply Hard Mode: {str(e)}")

    def _update_defense_flags_value(self) -> None:
        """Calculate the total defense flags value from all checkboxes"""
        total = 0
        for flag_name, var in self.defense_flags_vars.items():
            if var.get() == 1:  # Checkbox is checked
                total += self.defense_flags_bits[flag_name]
        
        self.defense_flags_value.set(total)
        self.defense_flags_label.config(text=f"Total Value: {total}")
        self.logger.debug(f"Defense flags value updated to {total}")

    def load_territory_data(self, tree: ET.ElementTree) -> None:
        self.logger.debug("Loading territory data")
        try:
            # Clear existing items
            for item in self.territory_tree.get_children():
                self.territory_tree.delete(item)

            territories = tree.findall(".//Territory")
            self.logger.debug(f"Found {len(territories)} territories")
            
            for territory in territories:
                try:
                    free_units = territory.find("FreeUnits")
                    troops = free_units.get("Troops", "0") if free_units is not None else "0"
                    ground = free_units.get("Ground", "0") if free_units is not None else "0"
                    air = free_units.get("Air", "0") if free_units is not None else "0"

                    territory_id = territory.get("crc_ID", "")
                    self.logger.debug(f"Processing territory {territory_id}")

                    values = (
                        territory_id,
                        territory.get("Faction", ""),
                        territory.get("BaseUnits", ""),
                        troops, ground, air,
                        territory.get("HomeBase", "0"),
                        territory.get("SecondaryBase", "0"),
                        territory.get("DefenseFlags", "1"),
                        territory.get("Active", "0")
                    )
                    
                    self.territory_tree.insert("", tk.END, values=values)
                    self.logger.debug(f"Successfully added territory {territory_id} to tree")
                
                except Exception as e:
                    self.logger.error(f"Error processing individual territory: {str(e)}", exc_info=True)

            self._reset_territory_editors()
            self.logger.debug("Territory data loading completed")
            
        except Exception as e:
            self.logger.error(f"Error loading territory data: {str(e)}", exc_info=True)
            raise

    def _on_territory_select(self, event) -> None:
        self.logger.debug("Territory selected")
        selection = self.territory_tree.selection()
        if not selection:
            self.logger.debug("No territory selected")
            return

        try:
            selected_item = selection[0]
            values = self.territory_tree.item(selected_item)["values"]
            self.logger.debug(f"Selected territory values: {values}")
            
            # Set faction dropdown based on value
            if str(values[1]).strip() == "0":
                self.territory_editors["Faction"].set("Undecided")
            elif str(values[1]).strip() == "1":
                self.territory_editors["Faction"].set("Navi")
            else:
                self.territory_editors["Faction"].set("Corp")
            
            # Update other fields...
            self.territory_editors["BaseUnits"].delete(0, tk.END)
            self.territory_editors["BaseUnits"].insert(0, values[2])
            self.territory_editors["Troops"].delete(0, tk.END)
            self.territory_editors["Troops"].insert(0, values[3])
            self.territory_editors["Ground"].delete(0, tk.END)
            self.territory_editors["Ground"].insert(0, values[4])
            self.territory_editors["Air"].delete(0, tk.END)
            self.territory_editors["Air"].insert(0, values[5])
            
            # Set HomeBase dropdown
            if str(values[6]).strip() == "2":
                self.logger.debug("Setting HomeBase to Yes because value is '2'")
                self.territory_editors["HomeBase"].set("Yes")
            else:
                self.logger.debug(f"Setting HomeBase to No because value is not '2'")
                self.territory_editors["HomeBase"].set("No")
            
            # Update defense flags checkboxes based on the value
            defense_flags_value = int(str(values[8]).strip() or "0")
            self.logger.debug(f"Setting defense flags checkboxes for value: {defense_flags_value}")
            
            # Reset all checkboxes first
            for var in self.defense_flags_vars.values():
                var.set(0)
            
            # Set checkboxes based on bits in the value
            for flag_name, bit_value in self.defense_flags_bits.items():
                # Check if this bit is set in the total value
                if defense_flags_value & bit_value:  # Bitwise AND operation
                    self.logger.debug(f"Setting checkbox {flag_name} to checked")
                    self.defense_flags_vars[flag_name].set(1)
                else:
                    self.logger.debug(f"Setting checkbox {flag_name} to unchecked")
                    self.defense_flags_vars[flag_name].set(0)
            
            # Update the total value display
            self._update_defense_flags_value()
            
            self.territory_editors["SecondaryBase"].set("Yes" if str(values[7]).strip() == "1" else "No")
            self.territory_editors["Active"].set("Active" if str(values[9]).strip() == "1" else "Inactive")
            
            self.logger.debug("Territory editor fields updated successfully")
        except Exception as e:
            self.logger.error(f"Error updating territory editor fields: {str(e)}", exc_info=True)

    def _apply_territory_changes(self) -> None:
        self.logger.debug("Applying territory changes")
        selection = self.territory_tree.selection()
        if not selection:
            self.logger.warning("No territory selected for changes")
            messagebox.showwarning("Warning", "Please select a territory to edit.")
            return

        try:
            values = self.territory_tree.item(selection[0])["values"]
            territory_id = values[0]
            self.logger.debug(f"Applying changes to territory {territory_id}")

            # Get the current defense flags value from the IntVar
            defense_flags_total = self.defense_flags_value.get()
            self.logger.debug(f"Defense flags value: {defense_flags_total}")

            new_values = (
                territory_id,
                "1" if self.territory_editors["Faction"].get() == "Navi" else "2",
                self.territory_editors["BaseUnits"].get(),
                self.territory_editors["Troops"].get(),
                self.territory_editors["Ground"].get(),
                self.territory_editors["Air"].get(),
                "2" if self.territory_editors["HomeBase"].get() == "Yes" else "0",
                "1" if self.territory_editors["SecondaryBase"].get() == "Yes" else "0",
                str(defense_flags_total),  # Use the calculated defense flags value
                "1" if self.territory_editors["Active"].get() == "Active" else "0"
            )
            
            self.logger.debug(f"New values: {new_values}")
            self.territory_tree.item(selection[0], values=new_values)

            # Update the XML tree if available
            if self.main_window and self.main_window.tree:
                # Find and update the territory in the XML
                territory = self.main_window.tree.find(f".//Territory[@crc_ID='{territory_id}']")
                if territory is not None:
                    # Update territory attributes
                    territory.set("Faction", new_values[1])
                    territory.set("BaseUnits", new_values[2])
                    territory.set("HomeBase", new_values[6])
                    territory.set("SecondaryBase", new_values[7])
                    territory.set("DefenseFlags", new_values[8])
                    territory.set("Active", new_values[9])

                    # Update or create FreeUnits element
                    free_units = territory.find("FreeUnits")
                    if free_units is None:
                        free_units = ET.SubElement(territory, "FreeUnits")
                    
                    free_units.set("Troops", new_values[3])
                    free_units.set("Ground", new_values[4])
                    free_units.set("Air", new_values[5])

                    self.logger.debug("Updated XML tree with territory changes")

                    # Mark as having unsaved changes
                    self.main_window.unsaved_label.config(text="Unsaved Changes")

                    # If XML editor is open, update its content
                    for widget in self.main_window.root.winfo_children():
                        if isinstance(widget, tk.Toplevel) and hasattr(widget, 'title') and widget.title() == "XML Editor":
                            xml_editor = widget.children['!frame'].children.get('!text')
                            if xml_editor:
                                # Update XML editor content
                                formatted_xml = XMLHandler.get_pretty_xml(self.main_window.tree)
                                xml_editor.delete("1.0", tk.END)
                                xml_editor.insert("1.0", formatted_xml)
                                self.logger.debug("Updated XML editor content")
            
            self.logger.debug("Territory changes applied successfully")
            messagebox.showinfo("Success", "Territory updated successfully!")
        except Exception as e:
            self.logger.error(f"Error applying territory changes: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to apply changes: {str(e)}")

    def _reset_territory_editors(self) -> None:
        # Reset standard editors
        for editor in self.territory_editors.values():
            if isinstance(editor, ttk.Combobox):
                editor.set(editor["values"][0])
            else:
                editor.delete(0, tk.END)
                editor.insert(0, "0")
        
        # Reset defense flags checkboxes
        if hasattr(self, 'defense_flags_vars'):
            for var in self.defense_flags_vars.values():
                var.set(0)
            self._update_defense_flags_value()
            
    def save_territory_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        self.logger.debug("Saving territory changes")
        root = tree.getroot()
        
        # Iterate through all territories in the tree view
        for item in self.territory_tree.get_children():
            try:
                values = self.territory_tree.item(item)["values"]
                self.logger.debug(f"Processing territory values: {values}")
                
                # Safely get values with default fallbacks
                territory_id = str(values[0]) if values[0] is not None else ""
                faction = str(values[1]) if len(values) > 1 and values[1] is not None else "1"
                base_units = str(values[2]) if len(values) > 2 and values[2] is not None else "0"
                troops = str(values[3]) if len(values) > 3 and values[3] is not None else "0"
                ground = str(values[4]) if len(values) > 4 and values[4] is not None else "0"
                air = str(values[5]) if len(values) > 5 and values[5] is not None else "0"
                home_base = str(values[6]) if len(values) > 6 and values[6] is not None else "0"
                secondary_base = str(values[7]) if len(values) > 7 and values[7] is not None else "0"
                defense_flags = str(values[8]) if len(values) > 8 and values[8] is not None else "1"
                active = str(values[9]) if len(values) > 9 and values[9] is not None else "0"

                # Find matching territory in XML
                territory = root.find(f".//Territory[@crc_ID='{territory_id}']")
                if territory is not None:
                    self.logger.debug(f"Updating territory {territory_id}")
                    
                    # Update territory attributes
                    territory.set("Faction", faction)
                    territory.set("BaseUnits", base_units)
                    territory.set("HomeBase", home_base)
                    territory.set("SecondaryBase", secondary_base)
                    territory.set("DefenseFlags", defense_flags)
                    territory.set("Active", active)
                    
                    # Update free units
                    free_units = territory.find("FreeUnits")
                    if free_units is not None:
                        free_units.set("Troops", troops)
                        free_units.set("Ground", ground)
                        free_units.set("Air", air)
                    else:
                        # Create FreeUnits element if it doesn't exist
                        self.logger.debug(f"Creating new FreeUnits element for territory {territory_id}")
                        free_units = ET.SubElement(territory, "FreeUnits")
                        free_units.set("Troops", troops)
                        free_units.set("Ground", ground)
                        free_units.set("Air", air)

                    self.logger.debug(f"Successfully updated territory {territory_id}")
                else:
                    self.logger.warning(f"Territory {territory_id} not found in XML")

            except Exception as e:
                self.logger.error(f"Error processing territory {values[0] if values else 'unknown'}: {str(e)}", exc_info=True)
                continue
        
        self.logger.debug("Territory changes saved successfully")
        return tree
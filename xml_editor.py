import tkinter as tk 
from tkinter import ttk, messagebox, font, simpledialog
from pathlib import Path
from xml_handler import XMLHandler
import logging
import xml.etree.ElementTree as ET
import re
from io import StringIO
from xml.dom import minidom


class XMLEditorWindow:
    def __init__(self, parent, main_editor=None, xml_text=None):
        self.logger = logging.getLogger('XMLEditor')
        self.logger.debug("Initializing XML Editor Window")
        self.window = tk.Toplevel(parent)
        self.window.title("XML Editor")
        self.window.geometry("1200x700")  # Increased size for better layout
        self.main_editor = main_editor  # Store reference to main editor
        
        self.current_tree = None  # Store the current XML tree
        
        # Search-related attributes
        self.search_results = []
        self.current_result_index = -1
        
        # Create context menu before UI setup
        self.sections_context_menu = None
        self.sections_tree = None
        self.text_area = None
        
        self.setup_ui()
        
        if xml_text:
            self.logger.debug("Loading initial XML text")
            self.text_area.insert("1.0", xml_text)
            try:
                # Parse the XML for structured view
                self.current_tree = ET.parse(StringIO(xml_text))
                self.populate_sections()
            except Exception as e:
                self.logger.error(f"Error parsing initial XML: {str(e)}")
    
    def populate_sections(self):
        """Populate the sections treeview with XML structure"""
        # Clear existing items
        for item in self.sections_tree.get_children():
            self.sections_tree.delete(item)
        
        if not self.current_tree:
            return

        root = self.current_tree.getroot()
        
        # Recursively populate sections
        self._populate_xml_recursively(root, "")

    def _populate_xml_recursively(self, element, parent_node=""):
        """
        Recursively populate the sections tree with XML structure
        
        Args:
            element (ET.Element): XML element to process
            parent_node (str, optional): Parent node in the treeview. Defaults to "".
        
        Returns:
            str: The node ID of the inserted item
        """
        # Generate a descriptive label for the element
        label_text = element.tag
        attributes = " ".join([f"{k}={v}" for k, v in element.attrib.items()])
        if attributes:
            label_text += f" ({attributes})"
        
        # If the element has text and it's not just whitespace, add it to the label
        if element.text and element.text.strip():
            label_text += f": {element.text.strip()}"
        
        # Insert the node
        if not parent_node:
            # This is a root or top-level node
            node = self.sections_tree.insert("", "end", text=element.tag, values=(label_text,))
        else:
            # This is a child node
            node = self.sections_tree.insert(parent_node, "end", text=element.tag, values=(label_text,))
        
        # Recursively process child elements
        for child in element:
            self._populate_xml_recursively(child, node)
        
        return node

    def on_section_select(self, event):
        """Handle section selection in the treeview"""
        selected_items = self.sections_tree.selection()
        if not selected_items:
            return

        selected_item = selected_items[0]
        section_text = self.sections_tree.item(selected_item, "text")
        
        # Find the corresponding XML section
        if not self.current_tree:
            return

        try:
            # Get the full XML for the selected section
            section_xml = self._get_section_xml(section_text)
            if section_xml:
                # Clear and insert the XML for the selected section
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", section_xml)
        except Exception as e:
            self.logger.error(f"Error displaying section: {str(e)}")

    def _get_section_xml(self, section_name):
        """Get XML for a specific section"""
        if not self.current_tree:
            return ""

        # Use a more robust method to find the section
        def find_element_by_tag(root, tag):
            for elem in root.iter():
                if elem.tag == tag:
                    return elem
            return None

        # Find the section
        section_elem = find_element_by_tag(self.current_tree.getroot(), section_name)
        
        if section_elem is not None:
            # Convert to string with indentation
            xml_str = ET.tostring(section_elem, encoding='unicode', method='xml')
            
            # Use minidom to add pretty printing
            reparsed = minidom.parseString(xml_str)
            return reparsed.toprettyxml(indent="  ")
        
        return ""

    def setup_ui(self):
        # Main container with two columns
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # Left side - XML Sections
        sections_frame = ttk.LabelFrame(main_frame, text="XML Sections")
        sections_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=5, pady=5)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)
        
        # Treeview for XML Sections
        self.sections_tree = ttk.Treeview(
            sections_frame, 
            columns=("Details",), 
            show="tree headings"
        )
        self.sections_tree.heading("#0", text="Sections")
        self.sections_tree.heading("Details", text="Details")
        self.sections_tree.column("#0", width=150)
        self.sections_tree.column("Details", width=200)
        sections_scrollbar = ttk.Scrollbar(sections_frame, orient="vertical", command=self.sections_tree.yview)
        self.sections_tree.configure(yscrollcommand=sections_scrollbar.set)
        
        self.sections_tree.grid(row=0, column=0, sticky="nsew")
        sections_scrollbar.grid(row=0, column=1, sticky="ns")
        sections_frame.grid_rowconfigure(0, weight=1)
        sections_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.sections_tree.bind("<<TreeviewSelect>>", self.on_section_select)

        # Explanation text
        explanation = ttk.Label(
            main_frame,
            text="Edit XML data below. Select a section from the left to view/edit specific parts.",
            wraplength=800
        )
        explanation.grid(row=0, column=1, sticky="ew", pady=(0, 10))

        # Create text area with scrollbars
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=1, column=1, sticky="nsew")
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)
        
        self.text_area = tk.Text(
            text_frame,
            wrap=tk.NONE,
            font=("Consolas", 10)
        )
        
        # Configure tabs
        tab_size = font.Font(font=self.text_area["font"]).measure(" " * 4)
        self.text_area.configure(tabs=tab_size)
        
        # Add scrollbars
        y_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_area.yview)
        x_scroll = ttk.Scrollbar(text_frame, orient="horizontal", command=self.text_area.xview)
        
        self.text_area.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )
        
        # Grid components
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        self.text_area.grid(row=0, column=0, sticky="nsew")
        
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=1, sticky="ew", pady=(10, 0))
        
        buttons = [
            ("Format XML", self.format_xml),
            ("Save Changes", self.save_changes),
            ("Expand All", self.expand_all_sections),
            ("Collapse All", self.collapse_all_sections)
        ]
        
        for i, (label, command) in enumerate(buttons):
            ttk.Button(
                button_frame,
                text=label,
                command=command
            ).grid(row=0, column=i, padx=5)

        # Add a context menu to the sections tree
        self.sections_context_menu = tk.Menu(self.window, tearoff=0)
        self.sections_context_menu.add_command(label="Add Child Element", command=self._add_child_element)
        self.sections_context_menu.add_command(label="Edit Element", command=self._edit_element)
        self.sections_context_menu.add_command(label="Delete Element", command=self._delete_element)
        
        # Bind right-click to show context menu AFTER sections_tree is created
        self.sections_tree.bind("<Button-3>", self._show_context_menu)

        # Ensure the window can be resized
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)

    def _show_context_menu(self, event):
        """Show context menu for XML sections"""
        # Select the item under the cursor
        iid = self.sections_tree.identify_row(event.y)
        if iid:
            self.sections_tree.selection_set(iid)
            self.sections_context_menu.tk_popup(event.x_root, event.y_root)

    def _add_child_element(self):
        """Add a child element to the selected XML section"""
        selected_items = self.sections_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a parent element")
            return

        try:
            # Prompt for element details
            element_name = simpledialog.askstring("Add Child Element", "Enter element name:")
            if not element_name:
                return

            # Prompt for attributes (optional)
            attributes_str = simpledialog.askstring("Add Attributes", 
                                                    "Enter attributes (key1=value1 key2=value2):", 
                                                    initialvalue="")
            
            # Prompt for element text (optional)
            element_text = simpledialog.askstring("Add Element Text", 
                                                  "Enter element text (optional):")

            # Parse the current XML
            current_xml = self.text_area.get("1.0", tk.END).strip()
            tree = ET.fromstring(current_xml)

            # Find the parent element
            parent_tag = self.sections_tree.item(selected_items[0], "text")
            parent_element = None
            for elem in tree.iter():
                if elem.tag == parent_tag:
                    parent_element = elem
                    break

            if parent_element is not None:
                # Create new element
                new_element = ET.SubElement(parent_element, element_name)
                
                # Add attributes if provided
                if attributes_str:
                    attrs = dict(attr.split('=') for attr in attributes_str.split())
                    for key, value in attrs.items():
                        new_element.set(key, value)
                
                # Add text if provided
                if element_text:
                    new_element.text = element_text

                # Pretty print the updated XML
                xml_str = ET.tostring(tree, encoding='unicode', method='xml')
                reparsed = minidom.parseString(xml_str)
                formatted_xml = reparsed.toprettyxml(indent="  ")

                # Update text area and treeview
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", formatted_xml)

                # Repopulate sections
                self.current_tree = ET.ElementTree(tree)
                self.populate_sections()

                messagebox.showinfo("Success", f"Added {element_name} as child of {parent_tag}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add element: {str(e)}")

    def _edit_element(self):
        """Edit the selected XML element"""
        selected_items = self.sections_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select an element to edit")
            return

        try:
            # Prompt for new attributes (optional)
            attributes_str = simpledialog.askstring("Edit Attributes", 
                                                    "Enter new attributes (key1=value1 key2=value2):", 
                                                    initialvalue="")
            
            # Prompt for new element text (optional)
            element_text = simpledialog.askstring("Edit Element Text", 
                                                  "Enter new element text (optional):")

            # Parse the current XML
            current_xml = self.text_area.get("1.0", tk.END).strip()
            tree = ET.fromstring(current_xml)

            # Find the element to edit
            element_tag = self.sections_tree.item(selected_items[0], "text")
            target_element = None
            for elem in tree.iter():
                # This handles both the tag and potentially attributes in the display
                full_text = f"{elem.tag} ({' '.join(f'{k}={v}' for k, v in elem.attrib.items())})"
                if full_text.startswith(element_tag):
                    target_element = elem
                    break

            if target_element is not None:
                # Update attributes if provided
                if attributes_str:
                    attrs = dict(attr.split('=') for attr in attributes_str.split())
                    # Clear existing attributes
                    for attr in list(target_element.attrib.keys()):
                        target_element.attrib.pop(attr)
                    # Add new attributes
                    for key, value in attrs.items():
                        target_element.set(key, value)
                
                # Update text if provided
                if element_text:
                    target_element.text = element_text

                # Pretty print the updated XML
                xml_str = ET.tostring(tree, encoding='unicode', method='xml')
                reparsed = minidom.parseString(xml_str)
                formatted_xml = reparsed.toprettyxml(indent="  ")

                # Update text area and treeview
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", formatted_xml)

                # Repopulate sections
                self.current_tree = ET.ElementTree(tree)
                self.populate_sections()

                messagebox.showinfo("Success", f"Edited {element_tag}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit element: {str(e)}")

    def _delete_element(self):
        """Delete the selected XML element"""
        selected_items = self.sections_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select an element to delete")
            return

        try:
            # Confirm deletion
            if not messagebox.askyesno("Confirm", "Are you sure you want to delete this element?"):
                return

            # Parse the current XML
            current_xml = self.text_area.get("1.0", tk.END).strip()
            tree = ET.fromstring(current_xml)

            # Find the element to delete
            element_tag = self.sections_tree.item(selected_items[0], "text")
            target_element = None
            parent_element = None
            for elem in tree.iter():
                # This handles both the tag and potentially attributes in the display
                full_text = f"{elem.tag} ({' '.join(f'{k}={v}' for k, v in elem.attrib.items())})"
                if full_text.startswith(element_tag):
                    target_element = elem
                    break

            if target_element is not None:
                # Find the parent of the target element
                for parent in tree.iter():
                    if target_element in parent:
                        parent.remove(target_element)
                        break

                # Pretty print the updated XML
                xml_str = ET.tostring(tree, encoding='unicode', method='xml')
                reparsed = minidom.parseString(xml_str)
                formatted_xml = reparsed.toprettyxml(indent="  ")

                # Update text area and treeview
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", formatted_xml)

                # Repopulate sections
                self.current_tree = ET.ElementTree(tree)
                self.populate_sections()

                messagebox.showinfo("Success", f"Deleted {element_tag}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete element: {str(e)}")

    def setup_search_components(self, parent):
        # Search frame setup (similar to previous implementation)
        search_frame = ttk.Frame(parent)
        search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Search entry
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # Search button
        search_button = ttk.Button(
            search_frame, 
            text="Search", 
            command=self.search_xml
        )
        search_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Next/Prev buttons
        self.prev_button = ttk.Button(
            search_frame, 
            text="Previous", 
            command=self.search_previous,
            state=tk.DISABLED
        )
        self.prev_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.next_button = ttk.Button(
            search_frame, 
            text="Next", 
            command=self.search_next,
            state=tk.DISABLED
        )
        self.next_button.pack(side=tk.LEFT)

        # Search-related attributes
        self.search_results = []
        self.current_result_index = -1

    def populate_sections(self):
        """Populate the sections treeview with XML structure"""
        # Clear existing items
        for item in self.sections_tree.get_children():
            self.sections_tree.delete(item)
        
        if not self.current_tree:
            return

        root = self.current_tree.getroot()
        
        # Use the recursive method to populate the entire tree
        self._populate_xml_recursively(root)
        
    def search_next(self):
        self.logger.debug("Moving to next search result")
        if not self.search_results:
            self.logger.debug("No search results to navigate")
            return
        
        try:
            self.current_result_index = min(
                self.current_result_index + 1, 
                len(self.search_results) - 1
            )
            
            self.next_button.config(state=tk.NORMAL if self.current_result_index < len(self.search_results) - 1 else tk.DISABLED)
            self.prev_button.config(state=tk.NORMAL)
            
            self.scroll_to_result()
            self.logger.debug(f"Moved to result {self.current_result_index + 1} of {len(self.search_results)}")
            
        except Exception as e:
            self.logger.error(f"Error navigating to next result: {str(e)}", exc_info=True)

    def search_previous(self):
        self.logger.debug("Moving to previous search result")
        if not self.search_results:
            self.logger.debug("No search results to navigate")
            return
        
        try:
            self.current_result_index = max(
                self.current_result_index - 1, 
                0
            )
            
            self.prev_button.config(state=tk.NORMAL if self.current_result_index > 0 else tk.DISABLED)
            self.next_button.config(state=tk.NORMAL)
            
            self.scroll_to_result()
            self.logger.debug(f"Moved to result {self.current_result_index + 1} of {len(self.search_results)}")
            
        except Exception as e:
            self.logger.error(f"Error navigating to previous result: {str(e)}", exc_info=True)

    def scroll_to_result(self):
        self.logger.debug("Scrolling to current search result")
        if not self.search_results:
            self.logger.debug("No search results to scroll to")
            return
        
        try:
            result_index = self.search_results[self.current_result_index]
            self.text_area.see(result_index)
            self.text_area.tag_remove("search_current", "1.0", tk.END)
            end_index = f"{result_index}+{len(self.search_entry.get())}c"
            self.text_area.tag_add("search_current", result_index, end_index)
            self.text_area.tag_config("search_current", background="royal blue", foreground="white")
            self.logger.debug(f"Scrolled to result at position {result_index}")
            
        except Exception as e:
            self.logger.error(f"Error scrolling to result: {str(e)}", exc_info=True)

    def format_xml(self):
        self.logger.debug("Formatting XML")
        try:
            current_text = self.text_area.get("1.0", tk.END)
            tree = XMLHandler.parse_xml_string(current_text)
            formatted_xml = XMLHandler.get_pretty_xml(tree)
            
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", formatted_xml)
            self.logger.debug("XML formatting completed successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to format XML: {str(e)}", exc_info=True)
            tk.messagebox.showerror("Error", f"Failed to format XML: {str(e)}")

    def save_changes(self):
        self.logger.debug("Saving XML changes")
        try:
            if self.main_editor:
                # Get current XML content
                xml_content = self.text_area.get("1.0", tk.END)
                
                # Parse the XML to validate and create new tree
                try:
                    new_tree = XMLHandler.parse_xml_string(xml_content)
                    
                    # Update the main editor's tree
                    self.main_editor.tree = new_tree
                    
                    # Mark as having unsaved changes
                    self.main_editor.unsaved_label.config(text="Unsaved Changes")
                    
                    # Reload the managers with new data
                    self.main_editor.stats_manager.load_stats(new_tree)
                    self.main_editor.territory_manager.load_territory_data(new_tree)
                    self.main_editor.achievements_manager.load_achievements(new_tree)
                    
                    messagebox.showinfo("Success", "XML changes applied successfully!")
                    self.logger.debug("XML changes saved and applied to main editor")
                    
                except ET.ParseError as pe:
                    self.logger.error(f"XML Parse Error: {str(pe)}")
                    messagebox.showerror("Error", f"Invalid XML format: {str(pe)}")
                except Exception as e:
                    self.logger.error(f"Error applying XML changes: {str(e)}")
                    messagebox.showerror("Error", f"Failed to apply changes: {str(e)}")
            else:
                self.logger.warning("No main editor reference available")
                messagebox.showwarning("Warning", "Changes can't be applied - no main editor reference")
                
        except Exception as e:
            self.logger.error(f"Error in save_changes: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to save changes: {str(e)}")

    def expand_all_sections(self):
        """Expand all sections in the treeview"""
        for item in self.sections_tree.get_children():
            self.sections_tree.item(item, open=True)

    def collapse_all_sections(self):
        """Collapse all sections in the treeview"""
        for item in self.sections_tree.get_children():
            self.sections_tree.item(item, open=False)
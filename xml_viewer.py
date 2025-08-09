import tkinter as tk
from tkinter import ttk, font
import xml.etree.ElementTree as ET
from xml.dom import minidom
from io import StringIO
import os
import logging
from custom_messagebox import MessageBoxManager, show_info, show_error, show_warning, ask_question, ask_ok_cancel, show_success


class XMLViewerWindow:
    def __init__(self, parent, xml_text=None):
        self.logger = logging.getLogger('XMLViewer')
        self.logger.debug("Initializing XML Viewer Window")
        self.window = tk.Toplevel(parent)
        self.window.title("XML Viewer")
        self.window.geometry("1400x900")
        
        # Set the window icon to match the main application
        try:
            icon_path = os.path.join("icon", "avatar_icon.ico")
            self.window.iconbitmap(icon_path)
            self.logger.debug(f"XML Viewer icon set successfully from path: {icon_path}")
        except Exception as e:
            self.logger.error(f"Failed to set XML Viewer icon: {str(e)}")
        
        self.current_tree = None
        self.setup_ui()
        
        if xml_text:
            self.logger.debug("Loading initial XML text")
            try:
                self.current_tree = ET.parse(StringIO(xml_text))
                self.populate_sections()
            except Exception as e:
                self.logger.error(f"Error parsing initial XML: {str(e)}")
                
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
        self.sections_tree.column("#0", width=200)
        self.sections_tree.column("Details", width=200)
        sections_scrollbar = ttk.Scrollbar(sections_frame, orient="vertical", command=self.sections_tree.yview)
        self.sections_tree.configure(yscrollcommand=sections_scrollbar.set)
        
        self.sections_tree.grid(row=0, column=0, sticky="nsew")
        sections_scrollbar.grid(row=0, column=1, sticky="ns")
        sections_frame.grid_rowconfigure(0, weight=1)
        sections_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.sections_tree.bind("<<TreeviewSelect>>", self.on_section_select)

        # Right side - XML Content
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=5, pady=5)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # Create fixed-width font for the text area
        text_font = font.Font(family="Consolas", size=10)
        
        # Create read-only text area with scrollbars
        self.text_area = tk.Text(
            content_frame,
            wrap=tk.NONE,
            font=text_font,
            state="disabled"  # Make it read-only
        )
        
        # Configure tabs
        tab_size = text_font.measure(" " * 4)
        self.text_area.configure(tabs=tab_size)
        
        # Add scrollbars
        y_scroll = ttk.Scrollbar(content_frame, orient="vertical", command=self.text_area.yview)
        x_scroll = ttk.Scrollbar(content_frame, orient="horizontal", command=self.text_area.xview)
        
        self.text_area.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )
        
        # Grid components
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        self.text_area.grid(row=0, column=0, sticky="nsew")

        # Button frame at the bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        # Buttons for tree navigation
        ttk.Button(button_frame, text="Expand All", command=self.expand_all_sections).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Collapse All", command=self.collapse_all_sections).pack(side="left", padx=5)

    def populate_sections(self):
        """Populate the sections treeview with XML structure"""
        for item in self.sections_tree.get_children():
            self.sections_tree.delete(item)
        
        if not self.current_tree:
            return

        root = self.current_tree.getroot()
        self._populate_xml_recursively(root)

    def _populate_xml_recursively(self, element, parent_node=""):
        """Recursively populate the sections tree with XML structure"""
        # Generate a descriptive label for the element
        label_text = element.tag
        attributes = " ".join([f"{k}={v}" for k, v in element.attrib.items()])
        
        # Create detailed description of the element
        details = []
        if attributes:
            details.append(attributes)
        if element.text and element.text.strip():
            # Only add text content if it's not just whitespace
            text_content = element.text.strip()
            if text_content:
                details.append(text_content)
        
        # Combine details into a single string, with attributes first
        details_str = ", ".join(details) if details else ""
        
        # Insert the node with full tag and details
        if not parent_node:
            node = self.sections_tree.insert("", "end", text=element.tag, values=(details_str,))
        else:
            node = self.sections_tree.insert(parent_node, "end", text=element.tag, values=(details_str,))
        
        # Recursively process all child elements
        for child in element:
            self._populate_xml_recursively(child, node)
        
        return node

    def on_section_select(self, event):
        """Handle section selection in the treeview"""
        selected_items = self.sections_tree.selection()
        if not selected_items or not self.current_tree:
            return

        try:
            selected_item = selected_items[0]
            
            # Get the selected element's XML
            element = self._get_element_by_tree_item(selected_item)
            if element is not None:
                # Format and display only the selected element's XML
                xml_str = ET.tostring(element, encoding='unicode', method='xml')
                reparsed = minidom.parseString(xml_str)
                formatted_xml = reparsed.toprettyxml(indent="  ")
                
                # Update the text area with just this element's content
                self.text_area.config(state="normal")
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", formatted_xml)
                self.text_area.config(state="disabled")
                
        except Exception as e:
            self.logger.error(f"Error displaying section: {str(e)}")

    def _get_element_by_tree_item(self, tree_item):
        """Get the XML element corresponding to a tree item"""
        # Get the full details of the selected item
        item_text = self.sections_tree.item(tree_item)["text"]
        item_details = self.sections_tree.item(tree_item)["values"][0]
        
        def matches_element(element, text, details):
            """Check if an element matches both the tag and details"""
            if element.tag != text:
                return False
                
            # If we have details, verify they match
            if details:
                element_attrs = " ".join(f"{k}={v}" for k, v in element.attrib.items())
                if element_attrs and details.startswith(element_attrs):
                    return True
                return element_attrs == details
            return True

        # Build the path of items
        path = []
        current_item = tree_item
        while current_item:
            path.insert(0, (
                self.sections_tree.item(current_item)["text"],
                self.sections_tree.item(current_item)["values"][0]
            ))
            current_item = self.sections_tree.parent(current_item)
        
        # Navigate to the selected element
        current_elem = self.current_tree.getroot()
        if len(path) == 1:  # Root element
            return current_elem
            
        # Follow path to find the specific element
        for tag, details in path[1:]:  # Skip root element
            found = False
            for child in current_elem:
                if matches_element(child, tag, details):
                    current_elem = child
                    found = True
                    break
            if not found:
                return None
                
        return current_elem

    def expand_all_sections(self):
        """Expand all sections in the treeview"""
        for item in self.sections_tree.get_children():
            self.sections_tree.item(item, open=True)

    def collapse_all_sections(self):
        """Collapse all sections in the treeview"""
        for item in self.sections_tree.get_children():
            self.sections_tree.item(item, open=False)
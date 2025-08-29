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
        self.logger.debug("Initializing Modern XML Viewer Window")
        self.window = tk.Toplevel(parent)
        self.window.title("🔍 XML Viewer - Save File Structure")
        self.window.geometry("1600x1000")
        
        # Set the window icon to match the main application
        try:
            icon_path = os.path.join("icon", "avatar_icon.ico")
            self.window.iconbitmap(icon_path)
            self.logger.debug(f"XML Viewer icon set successfully from path: {icon_path}")
        except Exception as e:
            self.logger.error(f"Failed to set XML Viewer icon: {str(e)}")
        
        self.current_tree = None
        self.search_var = tk.StringVar()
        self.search_matches = []  # Store all search match positions
        self.current_match_index = -1  # Current match being viewed
        
        # Apply dark theme to match main application
        self._apply_modern_theme()
        self.setup_modern_ui()
        
        if xml_text:
            self.logger.debug("Loading initial XML text")
            try:
                self.current_tree = ET.parse(StringIO(xml_text))
                self.populate_sections()
            except Exception as e:
                self.logger.error(f"Error parsing initial XML: {str(e)}")
    
    def _apply_modern_theme(self):
        """Apply modern dark theme to match main application"""
        self.window.configure(bg='#1e1e1e')
        
        # Use the existing theme from the main application
        # The main app already has the dark theme configured
                
    def setup_modern_ui(self):
        """Setup modern UI with consistent styling"""
        # Create main container with padding
        self.main_container = ttk.Frame(self.window, padding=15)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # === HEADER SECTION ===
        self.create_header_section()
        
        # === CONTENT AREA ===
        content_frame = ttk.Frame(self.main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        # Configure main grid
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=2)
        
        # Left sidebar (XML structure)
        self.create_sidebar(content_frame)
        
        # Main content area (XML content display)
        self.create_main_content(content_frame)
        
        # === FOOTER SECTION ===
        self.create_footer_section()

    def create_header_section(self):
        """Create the header with title and search"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title and subtitle
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = ttk.Label(title_frame, text="🔍 XML Structure Viewer", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="Explore and navigate your save file's XML structure", 
                                  font=('Segoe UI', 9), foreground='gray')
        subtitle_label.pack(anchor=tk.W)
        
        # Search section with navigation buttons
        search_container = ttk.Frame(header_frame)
        search_container.pack(side=tk.RIGHT)
        
        # Top row: search bar and buttons
        search_row = ttk.Frame(search_container)
        search_row.pack(anchor="e")
        
        # Search label
        ttk.Label(search_row, text="🔍 Search:", 
                 font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        # Search entry
        search_entry = ttk.Entry(search_row, textvariable=self.search_var, 
                                width=25, font=('Segoe UI', 9))
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind("<KeyRelease>", self._on_search_content)
        search_entry.bind("<Return>", self._go_to_next_match)  # Enter key for next match
        
        # Store reference to search entry for focus management
        self.search_entry = search_entry
        
        # Navigation buttons
        nav_frame = ttk.Frame(search_row)
        nav_frame.pack(side=tk.LEFT, padx=(5, 0))
        
        self.prev_button = ttk.Button(nav_frame, text="◀", width=3,
                                     command=self._go_to_previous_match,
                                     state="disabled")
        self.prev_button.pack(side=tk.LEFT, padx=(0, 2))
        
        self.next_button = ttk.Button(nav_frame, text="▶", width=3,
                                     command=self._go_to_next_match,
                                     state="disabled")
        self.next_button.pack(side=tk.LEFT)
        
        # Bottom row: search counter
        counter_row = ttk.Frame(search_container)
        counter_row.pack(anchor="e", pady=(3, 0))
        
        self.search_counter = ttk.Label(counter_row, text="", 
                                       font=('Segoe UI', 8), foreground='#888888')
        self.search_counter.pack()

    def create_sidebar(self, parent):
        """Create the left sidebar with XML structure tree"""
        sidebar_frame = ttk.LabelFrame(parent, text="📁 XML Structure", padding=15)
        sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Configure sidebar
        sidebar_frame.grid_rowconfigure(0, weight=1)
        sidebar_frame.grid_columnconfigure(0, weight=1)
        
        # Tree container
        tree_container = ttk.Frame(sidebar_frame)
        tree_container.grid(row=0, column=0, sticky="nsew")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Enhanced treeview for XML sections
        columns = ("Details",)
        self.sections_tree = ttk.Treeview(
            tree_container, 
            columns=columns, 
            show="tree headings"
        )
        
        # Configure headers with modern styling
        self.sections_tree.heading("#0", text="📂 Elements")
        self.sections_tree.heading("Details", text="📋 Attributes & Content")
        self.sections_tree.column("#0", width=250, minwidth=200)
        self.sections_tree.column("Details", width=300, minwidth=250)
        
        # Enhanced scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", 
                                   command=self.sections_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", 
                                   command=self.sections_tree.xview)
        self.sections_tree.configure(yscrollcommand=v_scrollbar.set, 
                                    xscrollcommand=h_scrollbar.set)
        
        # Grid layout for tree and scrollbars
        self.sections_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Bind selection event
        self.sections_tree.bind("<<TreeviewSelect>>", self.on_section_select)
        
        # Statistics frame
        stats_frame = ttk.Frame(sidebar_frame)
        stats_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        
        self.stats_label = ttk.Label(stats_frame, text="📊 Loading structure...", 
                                    font=('Segoe UI', 8))
        self.stats_label.pack(anchor=tk.W)

    def create_main_content(self, parent):
        """Create the main content area with XML display"""
        content_frame = ttk.LabelFrame(parent, text="📄 XML Content", padding=15)
        content_frame.grid(row=0, column=1, sticky="nsew")
        
        # Configure content frame
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Content display area
        display_container = ttk.Frame(content_frame)
        display_container.grid(row=0, column=0, sticky="nsew")
        display_container.grid_rowconfigure(0, weight=1)
        display_container.grid_columnconfigure(0, weight=1)
        
        # Create modern text area with enhanced styling
        text_font = font.Font(family="Consolas", size=10)
        
        # Text widget with modern styling
        self.text_area = tk.Text(
            display_container,
            wrap=tk.NONE,
            font=text_font,
            state="disabled",
            bg='#2c2c2c',
            fg='#ffffff',
            selectbackground='#2a7fff',
            selectforeground='#ffffff',
            insertbackground='#ffffff',
            borderwidth=1,
            relief='solid'
        )
        
        # Configure tabs for better XML formatting
        tab_size = text_font.measure(" " * 4)
        self.text_area.configure(tabs=tab_size)
        
        # Enhanced scrollbars for text area
        text_v_scroll = ttk.Scrollbar(display_container, orient="vertical", 
                                     command=self.text_area.yview)
        text_h_scroll = ttk.Scrollbar(display_container, orient="horizontal", 
                                     command=self.text_area.xview)
        
        self.text_area.configure(
            yscrollcommand=text_v_scroll.set,
            xscrollcommand=text_h_scroll.set
        )
        
        # Grid layout for text area
        self.text_area.grid(row=0, column=0, sticky="nsew")
        text_v_scroll.grid(row=0, column=1, sticky="ns")
        text_h_scroll.grid(row=1, column=0, sticky="ew")
        
        # Configure XML syntax highlighting
        self._configure_syntax_highlighting()
        
        # Configure special highlighting for current match
        self.text_area.tag_configure("current_match", background="#ff6600", foreground="#ffffff")  # Orange highlight for current match
        
        # Configure proper word selection behavior
        self._configure_word_selection()
        
        # Configure keyboard shortcuts
        self._configure_keyboard_shortcuts()

    def create_footer_section(self):
        """Create footer with action buttons"""
        footer_frame = ttk.Frame(self.main_container)
        footer_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Left side - Info
        info_frame = ttk.Frame(footer_frame)
        info_frame.pack(side=tk.LEFT)
        
        self.info_label = ttk.Label(info_frame, 
                                   text="💡 Shortcuts: Ctrl+F (search selected), F3 (next), Shift+F3 (previous), Esc (clear)", 
                                   font=('Segoe UI', 8), foreground='gray')
        self.info_label.pack(anchor=tk.W)
        
        # Right side - Action buttons
        button_frame = ttk.Frame(footer_frame)
        button_frame.pack(side=tk.RIGHT)
        
        # Modern styled buttons
        ttk.Button(button_frame, text="🔄 Expand All", 
                  command=self.expand_all_sections).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="📁 Collapse All", 
                  command=self.collapse_all_sections).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Close", 
                  command=self.window.destroy).pack(side=tk.LEFT, padx=(5, 0))

    def _configure_syntax_highlighting(self):
        """Configure comprehensive XML syntax highlighting like VS Code"""
        # Configure text tags for XML syntax highlighting with VS Code-like colors
        self.text_area.tag_configure("xml_tag", foreground="#569cd6")        # Blue for tag names
        self.text_area.tag_configure("xml_bracket", foreground="#808080")     # Gray for < > brackets
        self.text_area.tag_configure("xml_attr_name", foreground="#9cdcfe")   # Light blue for attribute names
        self.text_area.tag_configure("xml_attr_value", foreground="#ce9178")  # Orange for attribute values
        self.text_area.tag_configure("xml_text_content", foreground="#d4d4d4") # Light gray for text content
        self.text_area.tag_configure("xml_comment", foreground="#6a9955")     # Green for comments
        self.text_area.tag_configure("xml_declaration", foreground="#c586c0") # Purple for XML declarations
        self.text_area.tag_configure("xml_cdata", foreground="#dcdcaa")       # Yellow for CDATA
        self.text_area.tag_configure("search_highlight", background="#ffff00", foreground="#000000") # Yellow highlight for search
        self.text_area.tag_configure("current_match", background="#ff6600", foreground="#ffffff")  # Orange highlight for current match

    def populate_sections(self):
        """Populate the sections treeview with XML structure"""
        # Clear existing items
        for item in self.sections_tree.get_children():
            self.sections_tree.delete(item)
        
        if not self.current_tree:
            self.stats_label.config(text="📊 No XML data loaded")
            return

        root = self.current_tree.getroot()
        total_elements = self._count_elements(root)
        
        # Update statistics
        self.stats_label.config(text=f"📊 Total Elements: {total_elements} | Root: {root.tag}")
        
        # Populate tree structure
        self._populate_xml_recursively(root)

    def _count_elements(self, element):
        """Count total number of elements in the XML tree"""
        count = 1  # Count this element
        for child in element:
            count += self._count_elements(child)
        return count

    def _populate_xml_recursively(self, element, parent_node=""):
        """Recursively populate the sections tree with XML structure"""
        # Generate element icon based on type
        element_icon = self._get_element_icon(element)
        
        # Create detailed description of the element
        details = []
        
        # Add attribute information
        if element.attrib:
            attr_count = len(element.attrib)
            attr_preview = list(element.attrib.keys())[:2]  # Show first 2 attributes
            if attr_count > 2:
                attr_text = f"{', '.join(attr_preview)}... ({attr_count} attrs)"
            else:
                attr_text = f"{', '.join(attr_preview)} ({attr_count} attrs)"
            details.append(attr_text)
        
        # Add text content if present
        if element.text and element.text.strip():
            text_content = element.text.strip()
            if len(text_content) > 30:
                text_content = text_content[:30] + "..."
            details.append(f'Text: "{text_content}"')
        
        # Add child count
        child_count = len(list(element))
        if child_count > 0:
            details.append(f"{child_count} children")
        
        # Combine details
        details_str = " | ".join(details) if details else "Empty element"
        
        # Insert the node with enhanced display
        display_text = f"{element_icon} {element.tag}"
        if not parent_node:
            node = self.sections_tree.insert("", "end", text=display_text, values=(details_str,))
        else:
            node = self.sections_tree.insert(parent_node, "end", text=display_text, values=(details_str,))
        
        # Recursively process all child elements
        for child in element:
            self._populate_xml_recursively(child, node)
        
        return node

    def _get_element_icon(self, element):
        """Get appropriate icon for XML element based on its characteristics"""
        if element.attrib:
            if element.text and element.text.strip():
                return "📝"  # Element with attributes and text
            else:
                return "⚙️"  # Element with attributes only
        elif element.text and element.text.strip():
            return "📄"  # Element with text only
        elif len(list(element)) > 0:
            return "📁"  # Container element
        else:
            return "📋"  # Empty element

    def on_section_select(self, event):
        """Handle section selection in the treeview with enhanced display"""
        selected_items = self.sections_tree.selection()
        if not selected_items or not self.current_tree:
            return

        try:
            selected_item = selected_items[0]
            
            # Get the selected element's XML
            element = self._get_element_by_tree_item(selected_item)
            if element is not None:
                # Format and display the selected element's XML
                xml_str = ET.tostring(element, encoding='unicode', method='xml')
                reparsed = minidom.parseString(xml_str)
                formatted_xml = reparsed.toprettyxml(indent="  ")
                
                # Update the text area with enhanced formatting
                self.text_area.config(state="normal")
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", formatted_xml)
                
                # Apply comprehensive syntax highlighting
                self._apply_comprehensive_highlighting()
                
                self.text_area.config(state="disabled")
                
                # Update info label
                attr_count = len(element.attrib)
                child_count = len(list(element))
                self.info_label.config(
                    text=f"📋 Selected: {element.tag} | {attr_count} attributes | {child_count} children"
                )
                
        except Exception as e:
            self.logger.error(f"Error displaying section: {str(e)}")
            self.text_area.config(state="normal")
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", f"Error displaying XML content: {str(e)}")
            self.text_area.config(state="disabled")

    def _apply_comprehensive_highlighting(self):
        """Apply comprehensive XML syntax highlighting like VS Code"""
        content = self.text_area.get("1.0", tk.END)
        lines = content.split('\n')
        
        # Clear existing tags first
        for tag in ["xml_tag", "xml_bracket", "xml_attr_name", "xml_attr_value", 
                   "xml_text_content", "xml_comment", "xml_declaration", "xml_cdata"]:
            self.text_area.tag_remove(tag, "1.0", tk.END)
        
        for line_num, line in enumerate(lines, 1):
            line_start = f"{line_num}.0"
            
            # Skip empty lines
            if not line.strip():
                continue
            
            # Handle XML comments
            if "<!--" in line and "-->" in line:
                comment_start = line.find("<!--")
                comment_end = line.find("-->") + 3
                start_idx = f"{line_num}.{comment_start}"
                end_idx = f"{line_num}.{comment_end}"
                self.text_area.tag_add("xml_comment", start_idx, end_idx)
                continue
            
            # Handle XML declaration
            if line.strip().startswith("<?xml"):
                self.text_area.tag_add("xml_declaration", line_start, f"{line_num}.{len(line)}")
                continue
            
            # Handle CDATA sections
            if "<![CDATA[" in line:
                cdata_start = line.find("<![CDATA[")
                if "]]>" in line:
                    cdata_end = line.find("]]>") + 3
                    start_idx = f"{line_num}.{cdata_start}"
                    end_idx = f"{line_num}.{cdata_end}"
                    self.text_area.tag_add("xml_cdata", start_idx, end_idx)
                continue
            
            # Process XML tags and attributes
            self._highlight_xml_tags_and_attributes(line, line_num)
            
            # Highlight text content between tags
            self._highlight_text_content(line, line_num)

    def _highlight_xml_tags_and_attributes(self, line, line_num):
        """Highlight XML tags and their attributes"""
        i = 0
        while i < len(line):
            # Find opening bracket
            tag_start = line.find('<', i)
            if tag_start == -1:
                break
            
            # Find closing bracket
            tag_end = line.find('>', tag_start)
            if tag_end == -1:
                break
            
            # Highlight opening bracket
            self.text_area.tag_add("xml_bracket", f"{line_num}.{tag_start}", f"{line_num}.{tag_start + 1}")
            
            # Extract tag content
            tag_content = line[tag_start + 1:tag_end]
            
            # Skip if it's a comment or declaration (already handled)
            if tag_content.startswith('!') or tag_content.startswith('?'):
                i = tag_end + 1
                continue
            
            # Parse tag name and attributes
            parts = tag_content.split()
            if parts:
                tag_name = parts[0].rstrip('/')
                
                # Highlight tag name
                tag_name_start = tag_start + 1
                tag_name_end = tag_name_start + len(tag_name)
                self.text_area.tag_add("xml_tag", f"{line_num}.{tag_name_start}", f"{line_num}.{tag_name_end}")
                
                # Highlight attributes
                if len(parts) > 1:
                    attr_text = ' '.join(parts[1:])
                    attr_start_pos = tag_start + 1 + len(tag_name) + 1
                    self._highlight_attributes(attr_text, line_num, attr_start_pos)
            
            # Highlight closing bracket
            self.text_area.tag_add("xml_bracket", f"{line_num}.{tag_end}", f"{line_num}.{tag_end + 1}")
            
            i = tag_end + 1

    def _highlight_attributes(self, attr_text, line_num, start_pos):
        """Highlight XML attributes and their values"""
        import re
        
        # Pattern to match attribute="value" or attribute='value'
        attr_pattern = r'(\w+)\s*=\s*(["\'"])(.*?)\2'
        matches = re.finditer(attr_pattern, attr_text)
        
        for match in matches:
            attr_name = match.group(1)
            quote_char = match.group(2)
            attr_value = match.group(3)
            
            # Calculate positions
            attr_name_start = start_pos + match.start(1)
            attr_name_end = start_pos + match.end(1)
            
            # Highlight attribute name
            self.text_area.tag_add("xml_attr_name", 
                                  f"{line_num}.{attr_name_start}", 
                                  f"{line_num}.{attr_name_end}")
            
            # Highlight attribute value (including quotes)
            value_start = start_pos + match.start(2)
            value_end = start_pos + match.end(3) + 1  # Include closing quote
            self.text_area.tag_add("xml_attr_value", 
                                  f"{line_num}.{value_start}", 
                                  f"{line_num}.{value_end}")

    def _highlight_text_content(self, line, line_num):
        """Highlight text content between XML tags"""
        # Find text content between > and <
        i = 0
        while i < len(line):
            # Find end of opening tag
            tag_end = line.find('>', i)
            if tag_end == -1:
                break
            
            # Find start of next tag
            next_tag = line.find('<', tag_end + 1)
            if next_tag == -1:
                # Text content to end of line
                text_content = line[tag_end + 1:].strip()
                if text_content:
                    content_start = tag_end + 1
                    # Skip leading whitespace
                    while content_start < len(line) and line[content_start].isspace():
                        content_start += 1
                    if content_start < len(line):
                        self.text_area.tag_add("xml_text_content", 
                                              f"{line_num}.{content_start}", 
                                              f"{line_num}.{len(line)}")
                break
            else:
                # Text content between tags
                text_content = line[tag_end + 1:next_tag].strip()
                if text_content:
                    content_start = tag_end + 1
                    # Skip leading whitespace
                    while content_start < next_tag and line[content_start].isspace():
                        content_start += 1
                    if content_start < next_tag:
                        content_end = next_tag
                        # Skip trailing whitespace
                        while content_end > content_start and line[content_end - 1].isspace():
                            content_end -= 1
                        if content_end > content_start:
                            self.text_area.tag_add("xml_text_content", 
                                                  f"{line_num}.{content_start}", 
                                                  f"{line_num}.{content_end}")
                i = next_tag
            
    def _on_search_content(self, event=None):
        """Search only in the XML content window and highlight matches"""
        search_term = self.search_var.get().lower()
        
        # Clear previous search highlights
        self.text_area.tag_remove("search_highlight", "1.0", tk.END)
        self.text_area.tag_remove("current_match", "1.0", tk.END)
        self.search_matches = []
        self.current_match_index = -1
        
        if not search_term:
            self.info_label.config(text="💡 Shortcuts: Ctrl+F (search selected), F3 (next), Shift+F3 (previous), Esc (clear)")
            self.search_counter.config(text="")  # Clear counter
            self._update_navigation_buttons()
            return
        
        # Get current content
        content = self.text_area.get("1.0", tk.END)
        if not content.strip():
            self.info_label.config(text="🔍 No content to search")
            self.search_counter.config(text="")  # Clear counter
            self._update_navigation_buttons()
            return
        
        # Search for matches and store positions
        start_idx = 0
        content_lower = content.lower()
        
        while True:
            pos = content_lower.find(search_term, start_idx)
            if pos == -1:
                break
            
            # Convert position to line.column format
            lines_before = content[:pos].count('\n')
            if lines_before == 0:
                col = pos
            else:
                last_newline = content.rfind('\n', 0, pos)
                col = pos - last_newline - 1
            
            match_start = f"{lines_before + 1}.{col}"
            match_end = f"{lines_before + 1}.{col + len(search_term)}"
            
            # Store match information
            self.search_matches.append({
                'start': match_start,
                'end': match_end,
                'pos': pos
            })
            
            start_idx = pos + 1
        
        # Highlight all matches
        for match in self.search_matches:
            self.text_area.tag_add("search_highlight", match['start'], match['end'])
        
        # Update info label and navigation
        if self.search_matches:
            self.current_match_index = 0
            self._highlight_current_match()
            self._update_info_label()
            self._update_search_counter()  # Update counter display
            self._update_navigation_buttons()
            # Scroll to first match
            self.text_area.see(self.search_matches[0]['start'])
        else:
            self.info_label.config(text=f"🔍 No matches found for '{search_term}'")
            self.search_counter.config(text="0 of 0")  # Show no matches
            self._update_navigation_buttons()

    def _update_info_label(self):
        """Update the info label with current match information"""
        if self.search_matches:
            search_term = self.search_var.get()
            total_matches = len(self.search_matches)
            current_num = self.current_match_index + 1
            self.info_label.config(
                text=f"🔍 Searching '{search_term}' - Use F3/Shift+F3 or buttons to navigate"
            )
        else:
            search_term = self.search_var.get()
            if search_term:
                self.info_label.config(text=f"🔍 No matches found for '{search_term}'")
            else:
                self.info_label.config(text="💡 Shortcuts: Ctrl+F (search selected), F3 (next), Shift+F3 (previous), Esc (clear)")
        """Update the info label with current match information"""
        if self.search_matches:
            search_term = self.search_var.get()
            total_matches = len(self.search_matches)
            current_num = self.current_match_index + 1
            self.info_label.config(
                text=f"🔍 Searching '{search_term}' - Use F3/Shift+F3 or buttons to navigate"
            )
        else:
            search_term = self.search_var.get()
            if search_term:
                self.info_label.config(text=f"🔍 No matches found for '{search_term}'")
            else:
                self.info_label.config(text="💡 Shortcuts: Ctrl+F (search selected), F3 (next), Shift+F3 (previous), Esc (clear)")

    def _go_to_next_match(self, event=None):
        """Navigate to the next search match"""
        if not self.search_matches:
            return
        
        # Move to next match (with wrapping)
        self.current_match_index = (self.current_match_index + 1) % len(self.search_matches)
        self._highlight_current_match()
        self._update_info_label()
        self._update_search_counter()  # Update counter
        
        # Scroll to current match
        current_match = self.search_matches[self.current_match_index]
        self.text_area.see(current_match['start'])

    def _go_to_previous_match(self, event=None):
        """Navigate to the previous search match"""
        if not self.search_matches:
            return
        
        # Move to previous match (with wrapping)
        self.current_match_index = (self.current_match_index - 1) % len(self.search_matches)
        self._highlight_current_match()
        self._update_info_label()
        self._update_search_counter()  # Update counter
        
        # Scroll to current match
        current_match = self.search_matches[self.current_match_index]
        self.text_area.see(current_match['start'])

    def _highlight_current_match(self):
        """Highlight the current match with a different color"""
        # Remove previous current match highlighting
        self.text_area.tag_remove("current_match", "1.0", tk.END)
        
        if self.search_matches and 0 <= self.current_match_index < len(self.search_matches):
            current_match = self.search_matches[self.current_match_index]
            self.text_area.tag_add("current_match", current_match['start'], current_match['end'])

    def _update_search_counter(self):
        """Update the search counter display below the search bar"""
        if self.search_matches and 0 <= self.current_match_index < len(self.search_matches):
            total_matches = len(self.search_matches)
            current_num = self.current_match_index + 1
            self.search_counter.config(text=f"{current_num} of {total_matches}")
        else:
            self.search_counter.config(text="")
        """Update the info label with current match information"""
        if self.search_matches:
            search_term = self.search_var.get()
            total_matches = len(self.search_matches)
            current_num = self.current_match_index + 1
            self.info_label.config(
                text=f"🔍 Searching '{search_term}' - Use F3/Shift+F3 or buttons to navigate"
            )
        else:
            search_term = self.search_var.get()
            if search_term:
                self.info_label.config(text=f"🔍 No matches found for '{search_term}'")
            else:
                self.info_label.config(text="💡 Shortcuts: Ctrl+F (search selected), F3 (next), Shift+F3 (previous), Esc (clear)")

    def _update_navigation_buttons(self):
        """Enable/disable navigation buttons based on search results"""
        if self.search_matches and len(self.search_matches) > 1:
            self.prev_button.config(state="normal")
            self.next_button.config(state="normal")
        else:
            self.prev_button.config(state="disabled")
            self.next_button.config(state="disabled")

    def _configure_word_selection(self):
        """Configure proper word selection behavior for double-click"""
        # Override the default double-click behavior
        self.text_area.bind("<Double-Button-1>", self._on_double_click)
        
        # Also bind triple-click for line selection (optional enhancement)
        self.text_area.bind("<Triple-Button-1>", self._on_triple_click)

    def _on_double_click(self, event):
        """Handle double-click to select words intelligently"""
        # Get the click position
        click_index = self.text_area.index(f"@{event.x},{event.y}")
        
        # Get the character at the click position
        char = self.text_area.get(click_index)
        
        # Define word boundaries for different types of content
        if char.isalnum() or char in '_-':
            # For alphanumeric characters, select the word/number/identifier
            word_start, word_end = self._find_word_boundaries(click_index)
        elif char == '"' or char == "'":
            # For quotes, select the content inside the quotes
            word_start, word_end = self._find_quoted_content(click_index)
        elif char in '<>':
            # For angle brackets, select the tag name
            word_start, word_end = self._find_tag_content(click_index)
        else:
            # For other characters, use default word selection
            word_start, word_end = self._find_word_boundaries(click_index)
        
        # Clear current selection and select the word
        self.text_area.tag_remove("sel", "1.0", tk.END)
        self.text_area.tag_add("sel", word_start, word_end)
        self.text_area.mark_set("insert", word_end)
        
        # Return "break" to prevent default behavior
        return "break"

    def _update_info_label_with_shortcuts(self):
        """Update info label to show available shortcuts"""
        if not hasattr(self, '_shortcuts_shown'):
            base_text = self.info_label.cget("text")
            if "💡 Tip:" in base_text:
                self.info_label.config(
                    text="💡 Shortcuts: Ctrl+F (search selected), F3 (next), Shift+F3 (previous), Esc (clear)"
                )
                self._shortcuts_shown = True

    def _on_triple_click(self, event):
        """Handle triple-click to select entire line"""
        click_index = self.text_area.index(f"@{event.x},{event.y}")
        line_start = self.text_area.index(f"{click_index} linestart")
        line_end = self.text_area.index(f"{click_index} lineend")
        
        # Clear current selection and select the line
        self.text_area.tag_remove("sel", "1.0", tk.END)
        self.text_area.tag_add("sel", line_start, line_end)
        self.text_area.mark_set("insert", line_end)
        
        return "break"

    def _find_word_boundaries(self, index):
        """Find the boundaries of a word/number/identifier at the given index"""
        # Characters that are considered part of a word for XML content
        word_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.')
        
        # Find start of word
        current_index = index
        while True:
            try:
                char = self.text_area.get(current_index)
                if char not in word_chars:
                    current_index = self.text_area.index(f"{current_index} +1c")
                    break
                prev_index = self.text_area.index(f"{current_index} -1c")
                if prev_index == current_index:  # Beginning of text
                    break
                current_index = prev_index
            except tk.TclError:
                break
        
        word_start = current_index
        
        # Find end of word
        current_index = index
        while True:
            try:
                char = self.text_area.get(current_index)
                if char not in word_chars:
                    break
                next_index = self.text_area.index(f"{current_index} +1c")
                if next_index == current_index:  # End of text
                    current_index = self.text_area.index(f"{current_index} +1c")
                    break
                current_index = next_index
            except tk.TclError:
                break
        
        word_end = current_index
        
        return word_start, word_end

    def _find_quoted_content(self, index):
        """Find the content inside quotes when clicking on a quote"""
        line = self.text_area.get(f"{index} linestart", f"{index} lineend")
        line_start_index = self.text_area.index(f"{index} linestart")
        
        # Get position within the line
        click_char = int(index.split('.')[1])
        line_start_char = int(line_start_index.split('.')[1])
        pos_in_line = click_char - line_start_char
        
        if pos_in_line >= len(line):
            return self._find_word_boundaries(index)
        
        quote_char = line[pos_in_line]
        if quote_char not in ['"', "'"]:
            return self._find_word_boundaries(index)
        
        # Find the matching quote
        quote_start = -1
        quote_end = -1
        
        # Look backwards for opening quote
        for i in range(pos_in_line, -1, -1):
            if line[i] == quote_char:
                quote_start = i
                break
        
        # Look forwards for closing quote
        for i in range(pos_in_line + 1, len(line)):
            if line[i] == quote_char:
                quote_end = i
                break
        
        if quote_start != -1 and quote_end != -1:
            # Select content inside quotes (excluding the quotes themselves)
            line_num = index.split('.')[0]
            start_pos = f"{line_num}.{line_start_char + quote_start + 1}"
            end_pos = f"{line_num}.{line_start_char + quote_end}"
            return start_pos, end_pos
        
        return self._find_word_boundaries(index)

    def _configure_keyboard_shortcuts(self):
        """Configure keyboard shortcuts for the XML viewer"""
        # Bind Ctrl+F to search selected text
        self.text_area.bind("<Control-f>", self._on_ctrl_f)
        self.window.bind("<Control-f>", self._on_ctrl_f)
        
        # Bind F3 for next match (common shortcut)
        self.text_area.bind("<F3>", self._go_to_next_match)
        self.window.bind("<F3>", self._go_to_next_match)
        
        # Bind Shift+F3 for previous match
        self.text_area.bind("<Shift-F3>", self._go_to_previous_match)
        self.window.bind("<Shift-F3>", self._go_to_previous_match)
        
        # Bind Escape to clear search
        self.text_area.bind("<Escape>", self._clear_search)
        self.window.bind("<Escape>", self._clear_search)

    def _on_ctrl_f(self, event=None):
        """Handle Ctrl+F to search for selected text"""
        try:
            # Get the currently selected text
            selected_text = self.text_area.get("sel.first", "sel.last")
            
            if selected_text:
                # Clean the selected text (remove extra whitespace and newlines)
                cleaned_text = ' '.join(selected_text.split())
                
                # Update the search box with the selected text
                self.search_var.set(cleaned_text)
                
                # Trigger the search
                self._on_search_content()
                
                # Focus the search entry for further editing if needed
                self._focus_search_entry()
                
            else:
                # No text selected, just focus the search box
                self._focus_search_entry()
                
        except tk.TclError:
            # No selection exists, just focus the search box
            self._focus_search_entry()
        
        return "break"  # Prevent default Ctrl+F behavior

    def _focus_search_entry(self):
        """Focus and select all text in the search entry"""
        if hasattr(self, 'search_entry'):
            self.search_entry.focus_set()
            self.search_entry.select_range(0, tk.END)

    def _find_search_entry(self, widget):
        """Recursively find the search entry widget"""
        if isinstance(widget, ttk.Entry) and widget['textvariable'] == str(self.search_var):
            return widget
        
        # Check all children
        for child in widget.winfo_children():
            result = self._find_search_entry(child)
            if result:
                return result
        
        return None

    def _clear_search(self, event=None):
        """Clear the search when Escape is pressed"""
        self.search_var.set("")
        self.search_counter.config(text="")  # Clear counter
        self._on_search_content()
        
        # Return focus to the text area
        self.text_area.focus_set()
        
        return "break"

    def _find_tag_content(self, index):
        """Find tag name when clicking on angle brackets"""
        line = self.text_area.get(f"{index} linestart", f"{index} lineend")
        line_start_index = self.text_area.index(f"{index} linestart")
        
        # Get position within the line
        click_char = int(index.split('.')[1])
        line_start_char = int(line_start_index.split('.')[1])
        pos_in_line = click_char - line_start_char
        
        if pos_in_line >= len(line):
            return self._find_word_boundaries(index)
        
        # Find the tag boundaries
        tag_start = -1
        tag_end = -1
        
        # Look backwards for opening bracket
        for i in range(pos_in_line, -1, -1):
            if line[i] == '<':
                tag_start = i
                break
        
        # Look forwards for closing bracket
        for i in range(pos_in_line, len(line)):
            if line[i] == '>':
                tag_end = i + 1
                break
        
        if tag_start != -1 and tag_end != -1:
            # Extract just the tag name (first word after <)
            tag_content = line[tag_start + 1:tag_end - 1].strip()
            if tag_content.startswith('/'):
                tag_content = tag_content[1:]  # Remove closing tag slash
            
            # Get just the tag name (before any attributes)
            tag_name = tag_content.split()[0] if tag_content.split() else tag_content
            
            if tag_name:
                line_num = index.split('.')[0]
                # Find the tag name position within the tag
                tag_name_start = line.find(tag_name, tag_start)
                if tag_name_start != -1:
                    start_pos = f"{line_num}.{line_start_char + tag_name_start}"
                    end_pos = f"{line_num}.{line_start_char + tag_name_start + len(tag_name)}"
                    return start_pos, end_pos
        
        return self._find_word_boundaries(index)

    def _get_element_by_tree_item(self, tree_item):
        """Get the XML element corresponding to a tree item"""
        # Get the full details of the selected item
        item_text = self.sections_tree.item(tree_item)["text"]
        item_details = self.sections_tree.item(tree_item)["values"][0] if self.sections_tree.item(tree_item)["values"] else ""
        
        # Extract tag name from display text (remove icon)
        tag_name = item_text.split(' ', 1)[-1] if ' ' in item_text else item_text
        
        def matches_element(element, text, details):
            """Enhanced element matching"""
            if element.tag != text:
                return False
            return True  # Simplified matching for now

        # Build the path of items
        path = []
        current_item = tree_item
        while current_item:
            item_text = self.sections_tree.item(current_item)["text"]
            tag_name = item_text.split(' ', 1)[-1] if ' ' in item_text else item_text
            path.insert(0, tag_name)
            current_item = self.sections_tree.parent(current_item)
        
        # Navigate to the selected element
        current_elem = self.current_tree.getroot()
        if len(path) == 1:  # Root element
            return current_elem
            
        # Follow path to find the specific element
        for tag in path[1:]:  # Skip root element
            found = False
            for child in current_elem:
                if child.tag == tag:
                    current_elem = child
                    found = True
                    break
            if not found:
                return None
                
        return current_elem

    def _on_search(self, event=None):
        """Legacy search method - now calls content search"""
        self._on_search_content(event)

    def _search_tree_items(self, parent, search_term):
        """Recursively search through tree items"""
        children = self.sections_tree.get_children(parent)
        
        for child in children:
            item_text = self.sections_tree.item(child)["text"].lower()
            item_values = self.sections_tree.item(child)["values"]
            item_details = item_values[0].lower() if item_values else ""
            
            # Check if search term matches
            if search_term in item_text or search_term in item_details:
                # Highlight matching item
                self.sections_tree.set(child, "Details", 
                                      f"🔍 {self.sections_tree.set(child, 'Details')}")
                
                # Expand parent items to show match
                self._expand_to_item(child)
            
            # Recursively search children
            self._search_tree_items(child, search_term)

    def _expand_to_item(self, item):
        """Expand tree to show specific item"""
        parent = self.sections_tree.parent(item)
        while parent:
            self.sections_tree.item(parent, open=True)
            parent = self.sections_tree.parent(parent)

    def _clear_search_highlighting(self):
        """Clear search highlighting from tree"""
        def clear_item(parent):
            children = self.sections_tree.get_children(parent)
            for child in children:
                values = self.sections_tree.item(child)["values"]
                if values and values[0].startswith("🔍 "):
                    # Remove search indicator
                    self.sections_tree.set(child, "Details", values[0][2:])
                clear_item(child)
        
        clear_item("")
                
    def _apply_basic_highlighting(self):
        """Legacy method - now calls comprehensive highlighting"""
        self._apply_comprehensive_highlighting()

    def expand_all_sections(self):
        """Expand all sections in the treeview"""
        def expand_item(parent):
            children = self.sections_tree.get_children(parent)
            for child in children:
                self.sections_tree.item(child, open=True)
                expand_item(child)
        
        expand_item("")

    def collapse_all_sections(self):
        """Collapse all sections in the treeview"""
        def collapse_item(parent):
            children = self.sections_tree.get_children(parent)
            for child in children:
                self.sections_tree.item(child, open=False)
                collapse_item(child)
        
        collapse_item("")
import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
import logging
from custom_messagebox import MessageBoxManager, show_info, show_error, show_warning, ask_question, ask_ok_cancel, show_success


class PandoraPediaManager:
    def __init__(self, parent: ttk.Frame, main_window):
        self.logger = logging.getLogger('PandoraPediaManager')
        self.logger.debug("Initializing Modern PandoraPediaManager")
        self.parent = parent
        self.main_window = main_window
        self.article_data = {}
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
        
        # Left sidebar (actions and stats)
        self.create_sidebar(content_frame)
        
        # Main content area (articles list)
        self.create_main_content(content_frame)

    def create_header_section(self):
        """Create the header with title and search"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title and subtitle
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = ttk.Label(title_frame, text="📚 PandoraPedia", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="Your encyclopedia of Pandoran knowledge and discoveries", 
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
        """Create the left sidebar with actions and statistics"""
        sidebar_frame = ttk.Frame(parent, width=300)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        sidebar_frame.pack_propagate(False)
        
        # === QUICK ACTIONS SECTION ===
        actions_frame = ttk.LabelFrame(sidebar_frame, text="⚡ Quick Actions", padding=15)
        actions_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Primary action button
        self.discover_all_button = ttk.Button(
            actions_frame, text="🔓 Discover All Articles", 
            command=self._unlock_all_articles,
            style="Accent.TButton"
        )
        self.discover_all_button.pack(fill=tk.X, pady=(0, 10))
        
        # Separator
        ttk.Separator(actions_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Selection-based actions
        selection_label = ttk.Label(actions_frame, text="Selected Articles:", font=('Segoe UI', 9, 'bold'))
        selection_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.mark_discovered_button = ttk.Button(
            actions_frame, text="📖 Mark as Discovered", 
            command=lambda: self._set_selected_status("Discovered | Not Seen"),
            state="disabled"
        )
        self.mark_discovered_button.pack(fill=tk.X, pady=(0, 5))
        
        self.mark_read_button = ttk.Button(
            actions_frame, text="✅ Mark as Read", 
            command=lambda: self._set_selected_status("Discovered | Has Seen"),
            state="disabled"
        )
        self.mark_read_button.pack(fill=tk.X, pady=(0, 5))
        
        self.mark_undiscovered_button = ttk.Button(
            actions_frame, text="❌ Mark as Undiscovered", 
            command=lambda: self._set_selected_status("Not Discovered"),
            state="disabled"
        )
        self.mark_undiscovered_button.pack(fill=tk.X)
        
        # === DISCOVERY OVERVIEW ===
        overview_frame = ttk.LabelFrame(sidebar_frame, text="📊 Discovery Progress", padding=15)
        overview_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Large discovery display
        self.discovery_display = ttk.Frame(overview_frame)
        self.discovery_display.pack(fill=tk.X, pady=(0, 10))
        
        self.discovery_percentage = ttk.Label(
            self.discovery_display, 
            text="0%", 
            font=('Segoe UI', 24, 'bold'),
            foreground='#2e7d32'
        )
        self.discovery_percentage.pack()
        
        ttk.Label(self.discovery_display, text="Articles Discovered", font=('Segoe UI', 10)).pack()
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(overview_frame, mode='determinate', length=200)
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        
        # === STATISTICS SECTION ===
        stats_frame = ttk.LabelFrame(sidebar_frame, text="📈 Statistics", padding=15)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create statistics with modern layout
        self.create_stat_item(stats_frame, "📚", "Total Articles", "0", "total_articles_label")
        self.create_stat_item(stats_frame, "✅", "Discovered & Read", "0", "read_articles_label")
        self.create_stat_item(stats_frame, "📖", "Discovered", "0", "discovered_articles_label")
        self.create_stat_item(stats_frame, "❌", "Undiscovered", "0", "undiscovered_articles_label")
        
        # === FILTER SECTION ===
        filter_frame = ttk.LabelFrame(sidebar_frame, text="🔍 Filters", padding=15)
        filter_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(filter_frame, text="Show:", font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                   values=["All Articles", "✅ Discovered & Read", "📖 Discovered Only", 
                                          "❌ Undiscovered"],
                                   state="readonly", font=('Segoe UI', 9))
        filter_combo.set("All Articles")
        filter_combo.pack(fill=tk.X)
        filter_combo.bind("<<ComboboxSelected>>", self._apply_filter)
        
        # === KNOWLEDGE BASE INFO ===
        info_frame = ttk.LabelFrame(sidebar_frame, text="ℹ️ Knowledge Base", padding=15)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        info_text = tk.Text(info_frame, height=6, font=('Segoe UI', 9), 
                           wrap=tk.WORD, state=tk.DISABLED, background='#f8f9fa')
        info_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=info_text.yview)
        info_text.configure(yscrollcommand=info_scrollbar.set)
        
        # Add informational text
        info_content = """The PandoraPedia contains valuable information about Pandora's flora, fauna, culture, and technology.

📖 Discovered articles provide new insights
✅ Read articles contribute to your understanding
❌ Undiscovered articles await exploration

Discover articles through gameplay or use the quick actions to unlock all knowledge."""
        
        info_text.config(state=tk.NORMAL)
        info_text.insert(1.0, info_content)
        info_text.config(state=tk.DISABLED)
        
        info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

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
        """Create the main content area with articles list"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Articles list header
        list_header = ttk.Frame(main_frame)
        list_header.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(list_header, text="📚 Encyclopedia Articles", 
                 font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)
        
        # Status legend
        legend_frame = ttk.Frame(list_header)
        legend_frame.pack(side=tk.RIGHT)
        
        legend_items = [("❌", "Undiscovered"), ("📖", "Discovered"), ("✅", "Read")]
        for icon, desc in legend_items:
            ttk.Label(legend_frame, text=f"{icon} {desc}", font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=5)
        
        # Enhanced articles treeview
        tree_container = ttk.Frame(main_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure columns for better information display
        columns = ("status", "article_id", "title", "category", "details")
        self.pandora_pedia_tree = ttk.Treeview(tree_container, columns=columns, show="headings", 
                                              selectmode="extended", height=20)
        
        # Configure headers
        headers = {
            "status": ("📖", 60, "center"),
            "article_id": ("🆔 ID", 100, "center"),
            "title": ("📚 Article Title", 300, "w"),
            "category": ("🏷️ Category", 150, "w"),
            "details": ("ℹ️ Info", 100, "center")
        }
        
        for col, (text, width, anchor) in headers.items():
            self.pandora_pedia_tree.heading(col, text=text)
            self.pandora_pedia_tree.column(col, width=width, anchor=anchor, minwidth=50)
        
        # Enhanced color scheme
        self.setup_tree_styles()
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.pandora_pedia_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.pandora_pedia_tree.xview)
        self.pandora_pedia_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.pandora_pedia_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.pandora_pedia_tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.pandora_pedia_tree.bind("<Double-1>", self._on_article_double_click)
        self.pandora_pedia_tree.bind("<Button-3>", self._show_article_context_menu)

    def setup_tree_styles(self):
        """Configure tree styling with modern color scheme"""
        self.pandora_pedia_tree.tag_configure('not_discovered', 
                                             background='#ffebee', 
                                             foreground="#ff0000")
        self.pandora_pedia_tree.tag_configure('discovered_not_seen', 
                                             background='#fff3e0', 
                                             foreground="#ff7300")
        self.pandora_pedia_tree.tag_configure('discovered_has_seen', 
                                             background='#e8f5e8', 
                                             foreground="#00ff0d")

    def load_pandora_pedia(self, tree: ET.ElementTree) -> None:
        """Load PandoraPedia data with modern interface"""
        self.logger.debug("Loading PandoraPedia with modern interface")
        try:
            # Clear existing data
            self.article_data = {}
            
            # Clear existing items in treeview
            for item in self.pandora_pedia_tree.get_children():
                self.pandora_pedia_tree.delete(item)
            
            # Find all Article elements
            articles = tree.findall(".//AvatarPandorapediaDB_Status/Article")
            self.logger.debug(f"Found {len(articles)} articles")
            
            # Sort articles by CRC ID for consistent display
            articles_sorted = sorted(articles, key=lambda x: x.get("crc_id", "0"))
            
            for article in articles_sorted:
                try:
                    article_id = article.get("crc_id", "")
                    eknown_value = article.get("eKnown", "0")
                    
                    # Map eKnown values to status
                    status_map = {
                        "0": "Not Discovered",
                        "1": "Discovered | Not Seen",
                        "2": "Discovered | Has Seen"
                    }
                    status = status_map.get(eknown_value, "Not Discovered")
                    
                    # Generate article title and category
                    article_title = self._get_article_title(article_id)
                    category = self._get_article_category(article_title)
                    
                    # Store article data
                    self.article_data[article_id] = {
                        'status': status,
                        'title': article_title,
                        'category': category,
                        'element': article
                    }
                    
                    # Determine status icon and styling
                    status_icon, tag = self._get_article_status_info(status)
                    
                    # Insert into tree
                    self.pandora_pedia_tree.insert("", tk.END, values=(
                        status_icon,
                        article_id,
                        article_title,
                        category,
                        "View Details"
                    ), tags=(tag,))
                    
                except Exception as e:
                    self.logger.error(f"Error processing article {article_id}: {str(e)}", exc_info=True)
            
            # Update all displays
            self._update_all_displays()
            
            self.logger.debug("PandoraPedia loaded successfully with modern interface")
            
        except Exception as e:
            self.logger.error(f"Error loading PandoraPedia: {str(e)}", exc_info=True)
            raise

    def _get_article_title(self, article_id):
        """Generate article title based on ID"""
        # This could be expanded with actual article titles if available
        article_titles = {
            "1": "Flora: Pandoran Plant Life",
            "2": "Fauna: Native Creatures",
            "3": "Na'vi Culture and Traditions",
            "4": "RDA Technology Overview",
            "5": "Pandoran Ecosystem",
            "6": "Unobtainium Properties",
            "7": "Floating Mountains",
            "8": "Tree of Souls",
            "9": "Ikran Bonding Ritual",
            "10": "Banshee Flight Patterns"
        }
        
        return article_titles.get(article_id, f"Article {article_id}")

    def _get_article_category(self, title):
        """Determine article category based on title"""
        title_lower = title.lower()
        
        if any(keyword in title_lower for keyword in ['flora', 'plant', 'tree', 'botanical']):
            return "Flora"
        elif any(keyword in title_lower for keyword in ['fauna', 'creature', 'animal', 'wildlife']):
            return "Fauna"
        elif any(keyword in title_lower for keyword in ['na\'vi', 'culture', 'ritual', 'tradition']):
            return "Na'vi Culture"
        elif any(keyword in title_lower for keyword in ['rda', 'technology', 'equipment', 'machinery']):
            return "Technology"
        elif any(keyword in title_lower for keyword in ['ecosystem', 'environment', 'climate']):
            return "Environment"
        else:
            return "General"

    def _get_article_status_info(self, status):
        """Get status icon and tag for an article"""
        if status == "Discovered | Has Seen":
            return "✅", "discovered_has_seen"
        elif status == "Discovered | Not Seen":
            return "📖", "discovered_not_seen"
        else:
            return "❌", "not_discovered"

    def _update_all_displays(self):
        """Update all display elements"""
        total_articles = len(self.article_data)
        read_count = sum(1 for data in self.article_data.values() if data['status'] == 'Discovered | Has Seen')
        discovered_count = sum(1 for data in self.article_data.values() if data['status'] == 'Discovered | Not Seen')
        undiscovered_count = sum(1 for data in self.article_data.values() if data['status'] == 'Not Discovered')
        
        # Calculate discovery percentage (discovered + read)
        discovered_total = read_count + discovered_count
        discovery_pct = (discovered_total / total_articles * 100) if total_articles > 0 else 0
        
        # Update main discovery display
        self.discovery_percentage.config(text=f"{discovery_pct:.0f}%")
        self.progress_bar['value'] = discovery_pct
        
        # Update statistics
        self.total_articles_label.config(text=str(total_articles))
        self.read_articles_label.config(text=str(read_count))
        self.discovered_articles_label.config(text=str(discovered_count))
        self.undiscovered_articles_label.config(text=str(undiscovered_count))

    def _apply_filter(self, event=None):
        """Apply search and filter to the articles list"""
        filter_value = self.filter_var.get()
        search_text = self.search_var.get().lower()
        
        # Clear and repopulate tree
        for item in self.pandora_pedia_tree.get_children():
            self.pandora_pedia_tree.delete(item)
        
        # Re-add filtered items
        for article_id, article_data in self.article_data.items():
            if self._should_show_article(article_id, article_data, filter_value, search_text):
                status = article_data['status']
                status_icon, tag = self._get_article_status_info(status)
                
                self.pandora_pedia_tree.insert("", tk.END, values=(
                    status_icon,
                    article_id,
                    article_data['title'],
                    article_data['category'],
                    "View Details"
                ), tags=(tag,))

    def _should_show_article(self, article_id, article_data, filter_value, search_text):
        """Determine if article should be shown based on filters"""
        title = article_data['title']
        status = article_data['status']
        
        # Apply filter
        if filter_value == "✅ Discovered & Read" and status != "Discovered | Has Seen":
            return False
        elif filter_value == "📖 Discovered Only" and status != "Discovered | Not Seen":
            return False
        elif filter_value == "❌ Undiscovered" and status != "Not Discovered":
            return False
        
        # Apply search
        if search_text and search_text not in title.lower() and search_text not in article_id.lower():
            return False
        
        return True

    def _on_tree_select(self, event):
        """Handle tree selection events to update button states"""
        selection = self.pandora_pedia_tree.selection()
        
        # Enable/disable buttons based on selection
        if selection:
            self.mark_discovered_button.config(state="normal")
            self.mark_read_button.config(state="normal")
            self.mark_undiscovered_button.config(state="normal")
        else:
            self.mark_discovered_button.config(state="disabled")
            self.mark_read_button.config(state="disabled")
            self.mark_undiscovered_button.config(state="disabled")

    def _on_article_double_click(self, event):
        """Handle double-click on article in list"""
        item = self.pandora_pedia_tree.selection()[0] if self.pandora_pedia_tree.selection() else None
        if item:
            values = self.pandora_pedia_tree.item(item, "values")
            self._show_article_details(values[1])  # article_id

    def _show_article_context_menu(self, event):
        """Show context menu for articles"""
        if self.pandora_pedia_tree.selection():
            context_menu = tk.Menu(self.pandora_pedia_tree, tearoff=0)
            context_menu.add_command(label="📖 Mark as Discovered", 
                                   command=lambda: self._set_selected_status("Discovered | Not Seen"))
            context_menu.add_command(label="✅ Mark as Read", 
                                   command=lambda: self._set_selected_status("Discovered | Has Seen"))
            context_menu.add_command(label="❌ Mark as Undiscovered", 
                                   command=lambda: self._set_selected_status("Not Discovered"))
            context_menu.add_separator()
            context_menu.add_command(label="📋 Copy Article ID", command=self._copy_article_id)
            context_menu.add_command(label="ℹ️ Show Details", command=self._show_selected_article_details)
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()


    def _copy_article_id(self):
        """Copy selected article ID to clipboard"""
        selected = self.pandora_pedia_tree.selection()
        if selected:
            values = self.pandora_pedia_tree.item(selected[0], "values")
            article_id = values[1]  # ID is at index 1
            self.parent.clipboard_clear()
            self.parent.clipboard_append(article_id)
            show_info("Copied", f"📋 Article ID copied to clipboard:\n{article_id}")

    def _show_selected_article_details(self):
        """Show details for selected article"""
        selected = self.pandora_pedia_tree.selection()
        if selected:
            values = self.pandora_pedia_tree.item(selected[0], "values")
            self._show_article_details(values[1])  # article_id

    def _show_article_details(self, article_id):
        """Show detailed information about an article"""
        if article_id not in self.article_data:
            show_warning("Warning", "Article data not found")
            return
        
        article_data = self.article_data[article_id]
        
        # Create detailed article information dialog
        detail_window = tk.Toplevel(self.parent)
        detail_window.title(f"Article Details - {article_data['title']}")
        detail_window.geometry("1600x800")
        detail_window.resizable(True, True)
        
        # Main frame with padding
        main_frame = ttk.Frame(detail_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        status_icon, _ = self._get_article_status_info(article_data['status'])
        title_label = ttk.Label(main_frame, text=f"{status_icon} {article_data['title']}", 
                               font=('Segoe UI', 14, 'bold'))
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Details frame
        details_frame = ttk.LabelFrame(main_frame, text="Article Information", padding=15)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create details text widget
        details_text = tk.Text(details_frame, wrap=tk.WORD, font=('Consolas', 10), 
                              height=18, state=tk.NORMAL)
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=details_text.yview)
        details_text.configure(yscrollcommand=scrollbar.set)
        
        # Format article details
        info_text = f"""📚 Article Title: {article_data['title']}
🏷️ Category: {article_data['category']}
🆔 Article ID: {article_id}
📖 Status: {article_data['status']}

📝 Description:
{'=' * 50}
{self._get_article_description(article_data['title'], article_data['category'])}

🔧 Technical Details:
{'=' * 50}
Article ID: {article_id}
Category: {article_data['category']}
Discovery Status: {article_data['status']}
eKnown Value: {self._get_eknown_value(article_data['status'])}
"""
        
        details_text.insert(tk.END, info_text)
        details_text.config(state=tk.DISABLED)
        
        details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="📋 Copy ID", 
                  command=lambda: self._copy_to_clipboard(article_id)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="✅ Close", 
                  command=detail_window.destroy).pack(side=tk.RIGHT)

    def _get_article_description(self, title, category):
        """Get description for an article"""
        if category == "Flora":
            return f"This article contains detailed information about Pandoran plant life. '{title}' explores the unique botanical characteristics and ecological significance of Pandora's flora."
        elif category == "Fauna":
            return f"This article documents the fascinating wildlife of Pandora. '{title}' provides insights into creature behavior, habitat, and their role in the ecosystem."
        elif category == "Na'vi Culture":
            return f"This article explores Na'vi traditions and cultural practices. '{title}' offers understanding of indigenous customs and spiritual beliefs."
        elif category == "Technology":
            return f"This article covers technological aspects of Pandora operations. '{title}' details equipment, systems, and technological innovations."
        elif category == "Environment":
            return f"This article examines Pandora's environmental systems. '{title}' explores the complex ecological relationships and environmental factors."
        else:
            return f"'{title}' contains valuable information contributing to your understanding of Pandora's complex world and its various aspects."

    def _get_eknown_value(self, status):
        """Get eKnown value for status"""
        status_to_value = {
            "Not Discovered": "0",
            "Discovered | Not Seen": "1",
            "Discovered | Has Seen": "2"
        }
        return status_to_value.get(status, "0")

    def _copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(text)
            show_info("Copied", f"📋 Copied to clipboard:\n{text}")
        except Exception as e:
            show_error("Error", f"Failed to copy: {str(e)}")

    def _unlock_all_articles(self) -> None:
        """Discover all undiscovered articles"""
        self.logger.debug("Unlocking all articles")
        try:
            changes_made = False
            
            for article_id, article_data in self.article_data.items():
                if article_data['status'] == "Not Discovered":
                    # Update data
                    article_data['status'] = "Discovered | Not Seen"
                    article_data['element'].set("eKnown", "1")
                    changes_made = True
            
            if changes_made:
                # Update the tree display
                self._apply_filter()  # Refresh the display
                self._update_all_displays()
                self.main_window.unsaved_label.config(text="Unsaved Changes")
                show_success("Success", "🔓 All articles have been discovered!")
            else:
                show_info("Info", "ℹ️ All articles are already discovered!")
            
        except Exception as e:
            self.logger.error(f"Error unlocking all articles: {str(e)}", exc_info=True)
            show_error("Error", f"❌ Failed to unlock articles: {str(e)}")

    def _set_selected_status(self, status: str) -> None:
        """Set the status for selected articles"""
        selected_items = self.pandora_pedia_tree.selection()
        if not selected_items:
            show_warning("Warning", "Please select at least one article")
            return

        # Map status text to eKnown value
        status_to_value = {
            "Not Discovered": "0",
            "Discovered | Not Seen": "1",
            "Discovered | Has Seen": "2"
        }
        eknown_value = status_to_value.get(status, "0")

        try:
            changes_made = False
            
            for item in selected_items:
                values = self.pandora_pedia_tree.item(item, "values")
                article_id = values[1]  # ID is at index 1
                
                if article_id in self.article_data:
                    # Update data
                    self.article_data[article_id]['status'] = status
                    self.article_data[article_id]['element'].set("eKnown", eknown_value)
                    changes_made = True

            if changes_made:
                # Update the tree display
                self._apply_filter()  # Refresh the display
                self._update_all_displays()
                self.main_window.unsaved_label.config(text="Unsaved Changes")
                
                status_icons = {"Not Discovered": "❌", "Discovered | Not Seen": "📖", "Discovered | Has Seen": "✅"}
                icon = status_icons.get(status, "📖")
                show_success("Success", f"{icon} Selected articles set to: {status}")

        except Exception as e:
            self.logger.error(f"Error setting article status: {str(e)}", exc_info=True)
            show_error("Error", f"❌ Failed to set article status: {str(e)}")
            
    def save_pandora_pedia_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        """Save PandoraPedia changes to XML tree"""
        self.logger.debug("Saving PandoraPedia changes")
        try:
            # Changes are already applied to the XML elements during status updates
            # No additional processing needed since we update the elements directly
            self.logger.debug("PandoraPedia changes saved successfully")
            return tree
            
        except Exception as e:
            self.logger.error(f"Error saving PandoraPedia changes: {str(e)}", exc_info=True)
            raise

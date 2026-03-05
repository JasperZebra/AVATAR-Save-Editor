import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
from typing import Dict, Optional
import logging
from custom_messagebox import MessageBoxManager, show_info, show_error, show_warning, ask_question, ask_ok_cancel, show_success


class TutorialManager:
    def __init__(self, parent: ttk.Frame, main_window):
        self.logger = logging.getLogger('TutorialManager')
        self.logger.debug("Initializing Modern TutorialManager")
        self.parent = parent
        self.main_window = main_window
        self.tutorial_data = {}
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
        
        # Left sidebar (stats and filters)
        self.create_sidebar(content_frame)
        
        # Main content area (tutorial list)
        self.create_main_content(content_frame)

    def create_header_section(self):
        """Create the header with title and search"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title and subtitle
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = ttk.Label(title_frame, text="🎓 Tutorial Progress", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="Track your tutorial completion and learning progress", 
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
        """Create the left sidebar with statistics and filters"""
        sidebar_frame = ttk.Frame(parent, width=300)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        sidebar_frame.pack_propagate(False)
        
        # === PROGRESS OVERVIEW ===
        overview_frame = ttk.LabelFrame(sidebar_frame, text="📊 Progress Overview", padding=15)
        overview_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Large progress display
        self.progress_display = ttk.Frame(overview_frame)
        self.progress_display.pack(fill=tk.X, pady=(0, 10))
        
        self.completion_percentage = ttk.Label(
            self.progress_display, 
            text="0%", 
            font=('Segoe UI', 24, 'bold'),
            foreground='#2e7d32'
        )
        self.completion_percentage.pack()
        
        ttk.Label(self.progress_display, text="Complete", font=('Segoe UI', 10)).pack()
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(overview_frame, mode='determinate', length=200)
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        
        # === STATISTICS SECTION ===
        stats_frame = ttk.LabelFrame(sidebar_frame, text="📈 Statistics", padding=15)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create statistics with modern layout
        self.create_stat_item(stats_frame, "🎓", "Total Tutorials", "0", "total_tutorials_label")
        self.create_stat_item(stats_frame, "✅", "Completed", "0", "completed_tutorials_label")
        self.create_stat_item(stats_frame, "⏳", "Remaining", "0", "remaining_tutorials_label")
        
        # === FILTER SECTION ===
        filter_frame = ttk.LabelFrame(sidebar_frame, text="🔍 Filters", padding=15)
        filter_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(filter_frame, text="Show:", font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                   values=["All Tutorials", "✅ Completed Only", "⏳ Not Completed", 
                                          "🎮 Basic Controls", "⚔️ Combat", "🎯 Skills & Abilities", 
                                          "🌿 Environment"],
                                   state="readonly", font=('Segoe UI', 9))
        filter_combo.set("All Tutorials")
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
        """Create the main content area with tutorial list"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Tutorial list header
        list_header = ttk.Frame(main_frame)
        list_header.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(list_header, text="🎓 Tutorial Completion Status", 
                 font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)
        
        # Status legend
        legend_frame = ttk.Frame(list_header)
        legend_frame.pack(side=tk.RIGHT)
        
        legend_items = [("✅", "Completed"), ("⏳", "Not Completed")]
        for icon, desc in legend_items:
            ttk.Label(legend_frame, text=f"{icon} {desc}", font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=5)
        
        # Enhanced tutorial treeview
        tree_container = ttk.Frame(main_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure columns for better information display
        columns = ("status", "name", "category", "id", "details")
        self.tutorials_tree = ttk.Treeview(tree_container, columns=columns, show="headings", 
                                          selectmode="extended", height=20)
        
        # Configure headers
        headers = {
            "status": ("✅", 60, "center"),
            "name": ("🎓 Tutorial Name", 350, "w"),
            "category": ("📚 Category", 150, "w"),
            "id": ("🆔 ID", 120, "center"),
            "details": ("ℹ️ Info", 100, "center")
        }
        
        for col, (text, width, anchor) in headers.items():
            self.tutorials_tree.heading(col, text=text)
            self.tutorials_tree.column(col, width=width, anchor=anchor, minwidth=50)
        
        # Enhanced color scheme
        self.setup_tree_styles()
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tutorials_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tutorials_tree.xview)
        self.tutorials_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tutorials_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.tutorials_tree.bind("<Double-1>", self._on_tutorial_double_click)
        self.tutorials_tree.bind("<Button-3>", self._show_tutorial_context_menu)

    def setup_tree_styles(self):
        """Configure tree styling with modern color scheme"""
        self.tutorials_tree.tag_configure('completed', 
                                         background='#e8f5e8', 
                                         foreground="#00ff0d")
        self.tutorials_tree.tag_configure('not_completed', 
                                         background='#ffebee', 
                                         foreground="#ff0000")
        self.tutorials_tree.tag_configure('basic_controls', 
                                         background='#e3f2fd', 
                                         foreground="#0077ff")
        self.tutorials_tree.tag_configure('combat', 
                                         background='#fff3e0', 
                                         foreground="#ff7300")
        self.tutorials_tree.tag_configure('skills', 
                                         background='#f3e5f5', 
                                         foreground="#b300ff")
        self.tutorials_tree.tag_configure('environment', 
                                         background='#e8f5e8', 
                                         foreground="#00ff0d")

    def load_tutorials(self, tree: ET.ElementTree) -> None:
        """Load tutorial data with modern interface"""
        self.logger.debug("Loading tutorials with modern interface")
        try:
            # Clear existing data
            self.tutorial_data = {}
            
            # Clear existing items in treeview
            for item in self.tutorials_tree.get_children():
                self.tutorials_tree.delete(item)
            
            # Find all completed tutorial elements
            completed_tutorials = tree.findall(".//AvatarTutorialDB_Status/Tutorial_Completed")
            self.logger.debug(f"Found {len(completed_tutorials)} completed tutorials")
            
            # Create a set of completed tutorial IDs
            completed_tutorial_ids = {tutorial.get("crc_id", "") for tutorial in completed_tutorials}
            
            # Get the full list of tutorials
            all_tutorials = self._get_all_tutorial_ids()
            
            # Process each tutorial
            for tutorial_id, tutorial_name in all_tutorials.items():
                is_completed = tutorial_id in completed_tutorial_ids
                category = self._get_tutorial_category(tutorial_name)
                
                # Store tutorial data
                self.tutorial_data[tutorial_id] = {
                    'name': tutorial_name,
                    'category': category,
                    'completed': is_completed
                }
                
                # Determine status and styling
                status_icon, tag = self._get_tutorial_status_info(is_completed, category)
                
                # Insert into tree
                self.tutorials_tree.insert("", tk.END, values=(
                    status_icon,
                    tutorial_name,
                    category,
                    tutorial_id[-8:] if len(tutorial_id) > 8 else tutorial_id,  # Show last 8 digits
                    "View Details"
                ), tags=(tag,))
            
            # Update all displays
            self._update_all_displays()
            
            self.logger.debug("Tutorials loaded successfully with modern interface")
            
        except Exception as e:
            self.logger.error(f"Error loading tutorials: {str(e)}", exc_info=True)
            raise

    def _get_tutorial_category(self, tutorial_name):
        """Determine tutorial category based on name"""
        if any(keyword in tutorial_name.lower() for keyword in ['movement', 'navigation', 'camera', 'menu', 'map']):
            return "Basic Controls"
        elif any(keyword in tutorial_name.lower() for keyword in ['combat', 'weapon', 'melee', 'stealth']):
            return "Combat"
        elif any(keyword in tutorial_name.lower() for keyword in ['skill', 'abilities', 'bond', 'progression', 'equipment']):
            return "Skills & Abilities"
        elif any(keyword in tutorial_name.lower() for keyword in ['environmental', 'resource', 'crafting', 'creatures', 'survival']):
            return "Environment"
        else:
            return "General"

    def _get_tutorial_status_info(self, is_completed, category):
        """Get status icon and tag for a tutorial"""
        if is_completed:
            status_icon = "✅"
            if category == "Basic Controls":
                tag = "basic_controls"
            elif category == "Combat":
                tag = "combat"
            elif category == "Skills & Abilities":
                tag = "skills"
            elif category == "Environment":
                tag = "environment"
            else:
                tag = "completed"
        else:
            status_icon = "⏳"
            tag = "not_completed"
        
        return status_icon, tag

    def _update_all_displays(self):
        """Update all display elements"""
        total_tutorials = len(self.tutorial_data)
        completed_count = sum(1 for data in self.tutorial_data.values() if data['completed'])
        remaining_count = total_tutorials - completed_count
        
        # Update main progress display
        completion_pct = (completed_count / total_tutorials * 100) if total_tutorials > 0 else 0
        self.completion_percentage.config(text=f"{completion_pct:.0f}%")
        self.progress_bar['value'] = completion_pct
        
        # Update statistics
        self.total_tutorials_label.config(text=str(total_tutorials))
        self.completed_tutorials_label.config(text=str(completed_count))
        self.remaining_tutorials_label.config(text=str(remaining_count))
        
    def _apply_filter(self, event=None):
        """Apply search and filter to the tutorial list"""
        filter_value = self.filter_var.get()
        search_text = self.search_var.get().lower()
        
        # Clear and repopulate tree
        for item in self.tutorials_tree.get_children():
            self.tutorials_tree.delete(item)
        
        # Re-add filtered items
        for tutorial_id, tutorial_data in self.tutorial_data.items():
            if self._should_show_tutorial(tutorial_id, tutorial_data, filter_value, search_text):
                is_completed = tutorial_data['completed']
                category = tutorial_data['category']
                status_icon, tag = self._get_tutorial_status_info(is_completed, category)
                
                self.tutorials_tree.insert("", tk.END, values=(
                    status_icon,
                    tutorial_data['name'],
                    category,
                    tutorial_id[-8:] if len(tutorial_id) > 8 else tutorial_id,
                    "View Details"
                ), tags=(tag,))

    def _should_show_tutorial(self, tutorial_id, tutorial_data, filter_value, search_text):
        """Determine if tutorial should be shown based on filters"""
        name = tutorial_data['name']
        category = tutorial_data['category']
        is_completed = tutorial_data['completed']
        
        # Apply filter
        if filter_value == "✅ Completed Only" and not is_completed:
            return False
        elif filter_value == "⏳ Not Completed" and is_completed:
            return False
        
        # Apply search
        if search_text and search_text not in name.lower() and search_text not in tutorial_id.lower():
            return False
        
        return True

    def _on_tutorial_double_click(self, event):
        """Handle double-click on tutorial in list"""
        item = self.tutorials_tree.selection()[0] if self.tutorials_tree.selection() else None
        if item:
            values = self.tutorials_tree.item(item, "values")
            self._show_tutorial_details(values[1])  # tutorial name

    def _show_tutorial_context_menu(self, event):
        """Show context menu for tutorials"""
        if self.tutorials_tree.selection():
            context_menu = tk.Menu(self.tutorials_tree, tearoff=0)
            context_menu.add_command(label="📋 Copy Tutorial ID", command=self._copy_tutorial_id)
            context_menu.add_command(label="ℹ️ Show Details", command=self._show_selected_tutorial_details)
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()

    def _copy_tutorial_id(self):
        """Copy selected tutorial ID to clipboard"""
        selected = self.tutorials_tree.selection()
        if selected:
            values = self.tutorials_tree.item(selected[0], "values")
            # Find the full tutorial ID from our data
            tutorial_name = values[1]
            for tutorial_id, tutorial_data in self.tutorial_data.items():
                if tutorial_data['name'] == tutorial_name:
                    self.parent.clipboard_clear()
                    self.parent.clipboard_append(tutorial_id)
                    show_info("Copied", f"📋 Tutorial ID copied to clipboard:\n{tutorial_id}")
                    break

    def _show_tutorial_details(self, tutorial_name):
        """Show detailed information about a tutorial"""
        # Find the tutorial data
        tutorial_data = None
        tutorial_id = None
        for tid, data in self.tutorial_data.items():
            if data['name'] == tutorial_name:
                tutorial_data = data
                tutorial_id = tid
                break
        
        if not tutorial_data:
            show_warning("Warning", "Tutorial data not found")
            return
        
        # Create detailed tutorial information dialog
        detail_window = tk.Toplevel(self.parent)
        detail_window.title(f"Tutorial Details - {tutorial_name}")
        detail_window.geometry("683x384")
        detail_window.resizable(True, True)
        
        # Main frame with padding
        main_frame = ttk.Frame(detail_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"🎓 {tutorial_name}", 
                            font=('Segoe UI', 14, 'bold'))
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Details frame
        details_frame = ttk.LabelFrame(main_frame, text="Tutorial Information", padding=15)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create details text widget
        details_text = tk.Text(details_frame, wrap=tk.WORD, font=('Consolas', 10), 
                            height=18, state=tk.NORMAL)
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=details_text.yview)
        details_text.configure(yscrollcommand=scrollbar.set)
        
        # Format tutorial details
        status_text = "✅ Completed" if tutorial_data['completed'] else "⏳ Not Completed"
        
        info_text = f"""🎓 Tutorial Name: {tutorial_name}
    📚 Category: {tutorial_data['category']}
    🆔 Tutorial ID: {tutorial_id}
    ✅ Status: {status_text}

    📋 Description:
    {'=' * 40}
    {self._get_tutorial_description(tutorial_name)}

    🎯 Learning Objectives:
    {'=' * 40}
    {self._get_tutorial_objectives(tutorial_name)}

    🔧 Technical Details:
    {'=' * 40}
    Tutorial ID: {tutorial_id}
    Category: {tutorial_data['category']}
    Completion Status: {'Yes' if tutorial_data['completed'] else 'No'}
    """
        
        details_text.insert(tk.END, info_text)
        details_text.config(state=tk.DISABLED)
        
        details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="📋 Copy ID", 
                command=lambda: self._copy_to_clipboard(tutorial_id)).pack(side=tk.LEFT, padx=(0, 10))
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

    def _show_selected_tutorial_details(self):
        """Show details for selected tutorial"""
        selected = self.tutorials_tree.selection()
        if selected:
            values = self.tutorials_tree.item(selected[0], "values")
            self._show_tutorial_details(values[1])  # tutorial name

    def _get_tutorial_description(self, tutorial_name):
        """Get description for a tutorial"""
        descriptions = {
            "Tutorial_AccessControlScheme_Thanator": "Learn to ride and control the Thanator, mastering its powerful movement and combat capabilities.",
            "Tutorial_AccessControlScheme_Direhorse": "Master riding the Direhorse, understanding speed control, navigation, and bonding mechanics.",
            "Tutorial_SkillHealing": "Learn healing abilities and techniques to restore health during exploration and combat.",
            "Tutorial_TreeOfVisionFirstActivate": "Discover how to activate and use the Tree of Vision to unlock spiritual insights and abilities.",
            "Tutorial_AccessControlScheme_Leonopteryx": "Master the legendary Leonopteryx, learning advanced aerial maneuvers and bonding with this majestic creature.",
            "Tutorial_AccessControlScheme_Boat": "Learn to navigate Pandora's waterways using boats, including steering, speed control, and water-based exploration.",
            "Tutorial_HarmonicGameplayNavi2": "Advanced Na'vi gameplay mechanics focusing on harmonic interactions with Pandora's ecosystem.",
            "Tutorial_FirstCellSample": "Learn to collect your first cell sample, understanding the basics of scientific specimen gathering.",
            "Tutorial_AvatarSide": "Understand Avatar-specific gameplay mechanics and abilities unique to Avatar characters.",
            "Tutorial_GMIFirstActivation": "Learn to activate and use the GMI (Game Mechanical Interface) system for the first time.",
            "Tutorial_AccessControlScheme_Banshee": "Master flying the Banshee (Ikran), including takeoff, aerial combat, and navigation through Pandora's skies.",
            "Special Abilities Tutorial": "Learn to use special Na'vi abilities and unique powers available to your character.",
            "Tutorial_AmmoPod2": "Advanced ammunition management and understanding special ammo types and tactical loadouts.",
            "Tutorial_TravelAgent": "Learn to use fast travel systems and navigation aids to efficiently move across Pandora.",
            "Tutorial_BonusMap": "Discover how to access and use bonus map features to find hidden areas and collectibles.",
            "Tutorial_QuestZone": "Understand quest zones, mission areas, and how to navigate active objective regions.",
            "Tutorial_SkillScarer": "Learn intimidation and fear-based abilities to control enemy behavior in combat.",
            "Tutorial_NaviMetapod": "Master the Na'vi Metapod system for advanced character progression and abilities.",
            "Tutorial_AccessControlScheme_Buggy": "Learn to drive and control the buggy vehicle for ground-based exploration and combat.",
            "Tutorial_SkillAcquired": "Understand the skill acquisition system and how to unlock new abilities as you progress."
        }
        
        return descriptions.get(tutorial_name, "A comprehensive tutorial covering important game mechanics and features.")

    def _get_tutorial_objectives(self, tutorial_name):
        """Get learning objectives for a tutorial"""
        objectives = {
            "Tutorial_AccessControlScheme_Thanator": "• Mount and dismount the Thanator\n• Master movement controls\n• Execute powerful attacks",
            "Tutorial_AccessControlScheme_Direhorse": "• Bond with the Direhorse\n• Control speed and direction\n• Navigate varied terrain",
            "Tutorial_SkillHealing": "• Activate healing abilities\n• Manage health resources\n• Use healing in combat situations",
            "Tutorial_TreeOfVisionFirstActivate": "• Locate the Tree of Vision\n• Complete activation sequence\n• Understand spiritual connections",
            "Tutorial_AccessControlScheme_Leonopteryx": "• Successfully bond with Leonopteryx\n• Master advanced flight controls\n• Execute aerial maneuvers",
            "Tutorial_AccessControlScheme_Boat": "• Board and operate boats\n• Navigate water routes\n• Use boats for exploration",
            "Tutorial_HarmonicGameplayNavi2": "• Understand harmonic mechanics\n• Interact with ecosystem elements\n• Apply Na'vi spiritual abilities",
            "Tutorial_FirstCellSample": "• Identify sample locations\n• Collect cell samples properly\n• Store specimens correctly",
            "Tutorial_AvatarSide": "• Access Avatar abilities\n• Switch between forms\n• Utilize Avatar advantages",
            "Tutorial_GMIFirstActivation": "• Activate GMI system\n• Navigate interface options\n• Use basic GMI functions",
            "Tutorial_AccessControlScheme_Banshee": "• Bond with your Banshee\n• Master flight controls\n• Navigate aerial terrain",
            "Special Abilities Tutorial": "• Unlock special abilities\n• Execute unique powers\n• Combine abilities effectively",
            "Tutorial_AmmoPod2": "• Access ammo pods\n• Switch ammunition types\n• Optimize loadouts for missions",
            "Tutorial_TravelAgent": "• Open fast travel menu\n• Select destinations\n• Use waypoint systems",
            "Tutorial_BonusMap": "• Access bonus map features\n• Locate hidden collectibles\n• Navigate secret areas",
            "Tutorial_QuestZone": "• Identify quest zones\n• Enter mission areas\n• Complete zone objectives",
            "Tutorial_SkillScarer": "• Activate intimidation abilities\n• Control enemy behavior\n• Use fear tactics strategically",
            "Tutorial_NaviMetapod": "• Access Metapod system\n• Upgrade Na'vi abilities\n• Progress character development",
            "Tutorial_AccessControlScheme_Buggy": "• Drive and control buggy\n• Navigate rough terrain\n• Use vehicle in combat",
            "Tutorial_SkillAcquired": "• View acquired skills\n• Understand progression paths\n• Unlock new abilities"
        }
        
        return objectives.get(tutorial_name, "• Complete tutorial objectives\n• Master key mechanics\n• Apply learned skills in gameplay")

    def save_tutorial_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        """Tutorials are view-only, return unchanged tree"""
        self.logger.debug("Tutorials are view-only, no changes to save")
        return tree
    
    def _get_all_tutorial_ids(self):
        """Return a dictionary of all tutorial IDs and their names"""
        tutorial_names = {
            "44333413": "Tutorial_AccessControlScheme_Thanator",
            "158780422": "Tutorial_AccessControlScheme_Direhorse",
            "304605938": "Tutorial_SkillHealing",
            "734413258": "Tutorial_TreeOfVisionFirstActivate",
            "1360295752": "Tutorial_AccessControlScheme_Leonopteryx",
            "1376083454": "Tutorial_AccessControlScheme_Boat",
            "1579340642": "Tutorial_HarmonicGameplayNavi2",
            "1827545044": "Tutorial_FirstCellSample",
            "1836020734": "Tutorial_AvatarSide",
            "2013777292": "Tutorial_GMIFirstActivation",
            "2038369977": "Tutorial_AccessControlScheme_Banshee",
            "2046890945": "Special Abilities Tutorial",
            "2513987320": "Tutorial_AmmoPod2",
            "2654429851": "Tutorial_TravelAgent",
            "2738798113": "Tutorial_BonusMap",
            "2924024297": "Tutorial_QuestZone",
            "3610527961": "Tutorial_SkillScarer",
            "4202415783": "Tutorial_NaviMetapod",
            "4215961224": "Tutorial_AccessControlScheme_Buggy",
            "4274987001": "Tutorial_SkillAcquired"
        }
        return tutorial_names
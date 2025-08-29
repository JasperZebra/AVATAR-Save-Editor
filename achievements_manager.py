import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
from typing import Dict, Optional
from ui_components import LabeledInput
import logging
from custom_messagebox import MessageBoxManager, show_info, show_error, show_warning, ask_question, ask_ok_cancel, show_success


class AchievementsManager:
    def __init__(self, parent: ttk.Frame, main_window):
        self.logger = logging.getLogger('AchievementsManager')
        self.logger.debug("Initializing Modern AchievementsManager")
        self.parent = parent
        self.main_window = main_window
        self.achievement_data_dict = {}
        self.filter_var = tk.StringVar()
        self.search_var = tk.StringVar()
        
        # FIXED: Updated achievement data based on actual game files
        self.achievement_data = {
            # Developer/Debug Achievements
            "3959147003": {"name": "Mission_ORouleau_1", "max": 1, "category": "Debug"},
            "3975313082": {"name": "pin_z_dev_orouleau", "max": 1, "category": "Debug"},
            "3887901362": {"name": "orowin", "max": 2, "category": "Debug"},
            
            # Story Achievements - RDA Path
            "3614666474": {"name": "Orientation Day Graduate", "max": 1, "category": "Story"},
            "1964522520": {"name": "War's Begun", "max": 1, "category": "Story"},
            "820789492": {"name": "The First Harmonic", "max": 1, "category": "Story"},
            "3708977241": {"name": "Harmonic in the FEBA", "max": 1, "category": "Story"},
            "148645412": {"name": "Grave's Bog Harmonic", "max": 1, "category": "Story"},
            "3177295287": {"name": "Hanging Gardens Mission", "max": 1, "category": "Story"},
            "587544596": {"name": "Coualt Highlands Mission", "max": 1, "category": "Story"},
            "1863714547": {"name": "RDA Tantalus Complete", "max": 1, "category": "Story"},
            
            # Story Achievements - Na'vi Path
            "565628866": {"name": "Na'vi Blue Lagoon", "max": 1, "category": "Story"},
            "1752941290": {"name": "Na'vi Tantalus Start", "max": 1, "category": "Story"},
            "2793192431": {"name": "Na'vi Tantalus Mission", "max": 1, "category": "Story"},
            "208366408": {"name": "Verdant Pinnacle", "max": 1, "category": "Story"},
            "149358130": {"name": "Dust Bowl Mission", "max": 1, "category": "Story"},
            "260134042": {"name": "Prolemuris Land", "max": 1, "category": "Story"},
            "4216837213": {"name": "Vadera's Hollow", "max": 1, "category": "Story"},
            "1791022025": {"name": "Deserted Heaven", "max": 1, "category": "Story"},
            "2702278646": {"name": "Na'vi Tantalus Final", "max": 1, "category": "Story"},
            
            # Clean Sweep Achievements
            "355473279": {"name": "Sebastien Clean Sweep", "max": 1, "category": "Completion"},
            "2587251285": {"name": "Needle Hills Clean Sweep", "max": 1, "category": "Completion"},
            "1172651822": {"name": "Philippe Clean Sweep", "max": 1, "category": "Completion"},
            "1847852653": {"name": "Grave's Bog Clean Sweep", "max": 1, "category": "Completion"},
            "2171723794": {"name": "Coualt Highlands Clean Sweep", "max": 1, "category": "Completion"},
            "3409126972": {"name": "Plains of Goliath Clean Sweep", "max": 1, "category": "Completion"},
            "2943222331": {"name": "Verdant Pinnacle Clean Sweep", "max": 1, "category": "Completion"},
            "2292208788": {"name": "Dust Bowl Clean Sweep", "max": 1, "category": "Completion"},
            "1057194188": {"name": "Vadera's Hollow Clean Sweep", "max": 1, "category": "Completion"},
            "2856892107": {"name": "Nancy Clean Sweep", "max": 1, "category": "Completion"},
            "238707229": {"name": "Pascal Clean Sweep", "max": 1, "category": "Completion"},
            "1497753099": {"name": "Clean Sweep of Pandora", "max": 11, "category": "Completion"},
            
            # Progression Achievements
            "704269734": {"name": "Claim 50% Territories", "max": 1, "category": "Progression"},
            "2646580024": {"name": "Pandorapedia Articles", "max": 20, "category": "Collection"},
            "2932051916": {"name": "Fallback Kills", "max": 100, "category": "Combat"},
            
            # Skill Achievements - Corporate
            "3305899539": {"name": "Corporate Skill Slot 1A", "max": 20, "category": "Skills"},
            "77959529": {"name": "Corporate Skill Slot 1B", "max": 20, "category": "Skills"},
            "370163335": {"name": "Corporate Skill Slot 2B", "max": 20, "category": "Skills"},
            "3619269117": {"name": "Corporate Skill Slot 2A", "max": 20, "category": "Skills"},
            "1862651544": {"name": "Corporate Skill Slot 3A", "max": 20, "category": "Skills"},
            "4073911841": {"name": "Corporate Skill Slot 4A", "max": 20, "category": "Skills"},
            "863723867": {"name": "Corporate Skill Slot 4B", "max": 20, "category": "Skills"},
            "2847917574": {"name": "Grade 4 Corporate Skills", "max": 7, "category": "Skills"},
            
            # Skill Achievements - Na'vi
            "2171844251": {"name": "Na'vi Skill Slot 1A", "max": 20, "category": "Skills"},
            "4154870226": {"name": "Na'vi Skill Slot 1B", "max": 20, "category": "Skills"},
            "3843286588": {"name": "Na'vi Skill Slot 2B", "max": 20, "category": "Skills"},
            "2167405524": {"name": "Na'vi Skill Slot 2A", "max": 20, "category": "Skills"},
            "376364380": {"name": "Na'vi Skill Slot 3A", "max": 20, "category": "Skills"},
            "611800566": {"name": "Na'vi Skill Slot 3P", "max": 20, "category": "Skills"},
            "3229137376": {"name": "Na'vi Skill Slot 4A", "max": 20, "category": "Skills"},
            "2479233397": {"name": "Na'vi Skill Slot 2A Alt", "max": 20, "category": "Skills"},
            "1363959317": {"name": "Grade 4 Na'vi Skills", "max": 8, "category": "Skills"},
            "1716177172": {"name": "Grade 4 All Skills", "max": 1, "category": "Skills"},
            
            # Multiplayer Achievements
            "3049880868": {"name": "10 Kills in a Row", "max": 10, "category": "Multiplayer"},
            "569487683": {"name": "Play 150 Matches", "max": 150, "category": "Multiplayer"},
            "830999210": {"name": "Finish Match Most Kills", "max": 1, "category": "Multiplayer"},
            "594996582": {"name": "Win 3-0 CTF", "max": 3, "category": "Multiplayer"},
            "4203819019": {"name": "RDA 3 Intact Missiles", "max": 3, "category": "Multiplayer"},
            "2779487515": {"name": "Na'vi Destroy All Missiles", "max": 1, "category": "Multiplayer"},
            "4118326594": {"name": "Win 5 Capture & Hold", "max": 5, "category": "Multiplayer"},
            "270754235": {"name": "Win 5 King of the Hill", "max": 5, "category": "Multiplayer"},
        }
        
        self.setup_modern_ui()

    def validate_achievement_counts(self):
        """Validate and report achievements with unusual counts"""
        
        issues = []
        if not hasattr(self, 'achievement_data_dict'):
            return issues
            
        for achievement_id, data in self.achievement_data_dict.items():
            current = data['current']
            max_val = data['max']
            name = data['name']
            
            if current > max_val:
                issues.append({
                    'id': achievement_id,
                    'name': name,
                    'current': current,
                    'max': max_val,
                    'category': data['category'],
                    'issue': 'Count exceeds maximum'
                })
            elif current < 0:
                issues.append({
                    'id': achievement_id,
                    'name': name,
                    'current': current,
                    'max': max_val,
                    'category': data['category'],
                    'issue': 'Negative count'
                })
        
        if issues:
            self.logger.warning(f"Found {len(issues)} achievement count issues:")
            for issue in issues:
                self.logger.warning(f"  {issue['name']}: {issue['current']}/{issue['max']} - {issue['issue']}")
        
        return issues

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
        
        # Main content area (achievements list)
        self.create_main_content(content_frame)

    def create_header_section(self):
        """Create the header with title and search"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title and subtitle
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = ttk.Label(title_frame, text="🏆 Achievements", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="Track your accomplishments and unlock achievements", 
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
        """Create the left sidebar with actions and statistics - UPDATED VERSION"""
        sidebar_frame = ttk.Frame(parent, width=300)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        sidebar_frame.pack_propagate(False)
        
        # === QUICK ACTIONS SECTION ===
        actions_frame = ttk.LabelFrame(sidebar_frame, text="⚡ Quick Actions", padding=15)
        actions_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Primary action button
        self.complete_all_button = ttk.Button(
            actions_frame, text="🏆 Complete All Achievements", 
            command=self._complete_all_achievements,
            style="Accent.TButton"
        )
        self.complete_all_button.pack(fill=tk.X, pady=(0, 10))
        
        # Separator
        ttk.Separator(actions_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Selection-based actions
        selection_label = ttk.Label(actions_frame, text="Selected Achievements:", font=('Segoe UI', 9, 'bold'))
        selection_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.complete_selected_button = ttk.Button(
            actions_frame, text="✅ Complete Selected", 
            command=self._complete_selected,
            state="disabled"
        )
        self.complete_selected_button.pack(fill=tk.X, pady=(0, 5))
        
        self.reset_selected_button = ttk.Button(
            actions_frame, text="🔄 Reset Selected", 
            command=self._reset_selected,
            state="disabled"
        )
        self.reset_selected_button.pack(fill=tk.X)
        
        # === ACHIEVEMENT OVERVIEW ===
        overview_frame = ttk.LabelFrame(sidebar_frame, text="🏆 Achievement Progress", padding=15)
        overview_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Large completion display
        self.completion_display = ttk.Frame(overview_frame)
        self.completion_display.pack(fill=tk.X, pady=(0, 10))
        
        self.completion_percentage = ttk.Label(
            self.completion_display, 
            text="0%", 
            font=('Segoe UI', 24, 'bold'),
            foreground='#2e7d32'
        )
        self.completion_percentage.pack()
        
        ttk.Label(self.completion_display, text="Achievements Complete", font=('Segoe UI', 10)).pack()
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(overview_frame, mode='determinate', length=200)
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        
        # === STATISTICS SECTION ===
        stats_frame = ttk.LabelFrame(sidebar_frame, text="📊 Statistics", padding=15)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create statistics with modern layout
        self.create_stat_item(stats_frame, "🏆", "Total Achievements", "0", "total_achievements_label")
        self.create_stat_item(stats_frame, "✅", "Completed", "0", "completed_achievements_label")
        self.create_stat_item(stats_frame, "⏸️", "Not Started", "0", "not_started_achievements_label")
        
        # === FILTER SECTION ===
        filter_frame = ttk.LabelFrame(sidebar_frame, text="🔍 Filters", padding=15)
        filter_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(filter_frame, text="Show:", font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        # UPDATED: Fixed filter options to match new categories
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                values=["All Achievements", "✅ Completed", "⏸️ Not Started"],
                                state="readonly", font=('Segoe UI', 9))
        filter_combo.set("All Achievements")
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
        """Create the main content area with achievements list"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Achievements list header
        list_header = ttk.Frame(main_frame)
        list_header.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(list_header, text="🏆 Achievement Progress", 
                 font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)
        
        # Status legend
        legend_frame = ttk.Frame(list_header)
        legend_frame.pack(side=tk.RIGHT)
        
        legend_items = [("⏸️", "Not Started"), ("🔄", "In Progress"), ("✅", "Complete")]
        for icon, desc in legend_items:
            ttk.Label(legend_frame, text=f"{icon} {desc}", font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=5)
        
        # Enhanced achievements treeview
        tree_container = ttk.Frame(main_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure columns for better information display
        columns = ("status", "name", "category", "progress", "id", "details")
        self.achievements_tree = ttk.Treeview(tree_container, columns=columns, show="headings", 
                                            selectmode="extended", height=20)
        
        # Configure headers
        headers = {
            "status": ("🏆", 60, "center"),
            "name": ("🎯 Achievement Name", 280, "w"),
            "category": ("🏷️ Category", 120, "w"),
            "progress": ("📊 Progress", 100, "center"),
            "id": ("🆔 ID", 100, "center"),
            "details": ("ℹ️ Info", 100, "center")
        }
        
        for col, (text, width, anchor) in headers.items():
            self.achievements_tree.heading(col, text=text)
            self.achievements_tree.column(col, width=width, anchor=anchor, minwidth=50)
        
        # Enhanced color scheme
        self.setup_tree_styles()
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.achievements_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.achievements_tree.xview)
        self.achievements_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.achievements_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.achievements_tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.achievements_tree.bind("<Double-1>", self._on_achievement_double_click)
        self.achievements_tree.bind("<Button-3>", self._show_achievement_context_menu)

    def setup_tree_styles(self):
        """Configure tree styling with modern color scheme"""
        self.achievements_tree.tag_configure('not_started', 
                                           background='#ffebee', 
                                           foreground="#ff0000")
        self.achievements_tree.tag_configure('in_progress', 
                                           background='#fff3e0', 
                                           foreground="#ff7300")
        self.achievements_tree.tag_configure('complete', 
                                           background='#e8f5e8', 
                                           foreground="#00ff0d")
        self.achievements_tree.tag_configure('story', 
                                           background='#e3f2fd', 
                                           foreground="#0077ff")
        self.achievements_tree.tag_configure('combat', 
                                           background='#fce4ec', 
                                           foreground="#ff006f")

    def load_achievements(self, tree: ET.ElementTree) -> None:
        """Load achievements data with modern interface"""
        self.logger.debug("Loading achievements with modern interface")
        try:
            # Clear existing data
            self.achievement_data_dict = {}
            
            # Clear existing items in treeview
            for item in self.achievements_tree.get_children():
                self.achievements_tree.delete(item)

            # Find all AchievementCounter elements
            achievements = tree.findall(".//AchievementCounter")
            self.logger.debug(f"Found {len(achievements)} achievements")
            
            # Sort achievements by ID for consistent display
            achievements_sorted = sorted(achievements, key=lambda x: x.get("crc_id", "0"))
            
            for achievement in achievements_sorted:
                try:
                    achievement_id = achievement.get("crc_id", "")
                    count = achievement.get("count", "0")
                    
                    # Get achievement data
                    achievement_info = self.achievement_data.get(achievement_id, {
                        "name": f"Unknown Achievement ({achievement_id[-8:]})",
                        "max": 100,
                        "category": "Unknown"
                    })
                    
                    # Store achievement data
                    self.achievement_data_dict[achievement_id] = {
                        'name': achievement_info["name"],
                        'category': achievement_info["category"],
                        'current': int(count),
                        'max': achievement_info["max"],
                        'element': achievement
                    }
                    
                    # Determine status and styling
                    status = self._determine_status(count, achievement_info['max'])
                    status_icon, tag = self._get_achievement_status_info(status, achievement_info["category"])
                    
                    # Format progress
                    progress_text = f"{count}/{achievement_info['max']}"
                    
                    # Insert into tree
                    self.achievements_tree.insert("", tk.END, values=(
                        status_icon,
                        achievement_info["name"],
                        achievement_info["category"],
                        progress_text,
                        achievement_id[-8:] if len(achievement_id) > 8 else achievement_id,
                        "View Details"
                    ), tags=(tag,))
                    
                except Exception as e:
                    self.logger.error(f"Error processing achievement {achievement_id}: {str(e)}", exc_info=True)

            # Update all displays
            self._update_all_displays()
            
            self.logger.debug("Achievements loaded successfully with modern interface")
            
            # Validate achievement counts for any issues
            self.validate_achievement_counts()
            
        except Exception as e:
            self.logger.error(f"Error loading achievements: {str(e)}", exc_info=True)
            raise

    def _determine_status(self, count: str, max_value: int) -> str:
        """Determine achievement status based on count value and maximum"""
        try:
            count_val = int(count)
            if count_val >= max_value:
                return "Complete"
            elif count_val > 0:
                return "In Progress"
            else:
                return "Not Started"
        except ValueError:
            return "Unknown"

    def _get_achievement_status_info(self, status, category):
        """Get status icon and tag for an achievement"""
        if status == "Complete":
            status_icon = "✅"
            if category == "Story":
                tag = "story"
            elif category == "Combat":
                tag = "combat"
            else:
                tag = "complete"
        elif status == "In Progress":
            status_icon = "🔄"
            tag = "in_progress"
        else:
            status_icon = "⏸️"
            tag = "not_started"
        
        return status_icon, tag

    def _update_all_displays(self):
        """Update all display elements"""
        total_achievements = len(self.achievement_data_dict)
        completed_count = sum(1 for data in self.achievement_data_dict.values() if data['current'] >= data['max'])
        in_progress_count = sum(1 for data in self.achievement_data_dict.values() 
                               if 0 < data['current'] < data['max'])
        not_started_count = sum(1 for data in self.achievement_data_dict.values() if data['current'] == 0)
        
        # Update main completion display
        completion_pct = (completed_count / total_achievements * 100) if total_achievements > 0 else 0
        self.completion_percentage.config(text=f"{completion_pct:.0f}%")
        self.progress_bar['value'] = completion_pct
        
    def _apply_filter(self, event=None):
        """Apply search and filter to the achievements list"""
        filter_value = self.filter_var.get()
        search_text = self.search_var.get().lower()
        
        # Clear and repopulate tree
        for item in self.achievements_tree.get_children():
            self.achievements_tree.delete(item)
        
        # Re-add filtered items
        for achievement_id, achievement_data in self.achievement_data_dict.items():
            if self._should_show_achievement(achievement_id, achievement_data, filter_value, search_text):
                status = self._determine_status(str(achievement_data['current']), achievement_data['max'])
                status_icon, tag = self._get_achievement_status_info(status, achievement_data['category'])
                
                progress_text = f"{achievement_data['current']}/{achievement_data['max']}"
                
                self.achievements_tree.insert("", tk.END, values=(
                    status_icon,
                    achievement_data['name'],
                    achievement_data['category'],
                    progress_text,
                    achievement_id[-8:] if len(achievement_id) > 8 else achievement_id,
                    "View Details"
                ), tags=(tag,))

    def _should_show_achievement(self, achievement_id, achievement_data, filter_value, search_text):
        """Determine if achievement should be shown based on filters"""
        name = achievement_data['name']
        category = achievement_data['category']
        current = achievement_data['current']
        max_val = achievement_data['max']
        
        # Determine status
        if current >= max_val:
            status = "Complete"
        elif current > 0:
            status = "In Progress"
        else:
            status = "Not Started"
        
        # Apply status filters
        if filter_value == "✅ Completed" and status != "Complete":
            return False
        elif filter_value == "🔄 In Progress" and status != "In Progress":
            return False
        elif filter_value == "⏸️ Not Started" and status != "Not Started":
            return False
        
        # Apply category filters
        elif filter_value == "📖 Story" and category != "Story":
            return False
        elif filter_value == "🏁 Completion" and category != "Completion":
            return False
        elif filter_value == "⚔️ Combat" and category != "Combat":
            return False
        elif filter_value == "👥 Multiplayer" and category != "Multiplayer":
            return False
        elif filter_value == "📈 Progression" and category != "Progression":
            return False
        elif filter_value == "📚 Collection" and category != "Collection":
            return False
        elif filter_value == "🎯 Skills" and category != "Skills":
            return False
        elif filter_value == "🛠️ Debug" and category != "Debug":
            return False
        
        # Apply search filter
        if search_text and search_text not in name.lower() and search_text not in achievement_id.lower():
            return False
        
        return True

    def _on_tree_select(self, event):
        """Handle tree selection events to update button states"""
        selection = self.achievements_tree.selection()
        
        # Enable/disable buttons based on selection
        if selection:
            self.complete_selected_button.config(state="normal")
            self.reset_selected_button.config(state="normal")
        else:
            self.complete_selected_button.config(state="disabled")
            self.reset_selected_button.config(state="disabled")

    def _on_achievement_double_click(self, event):
        """Handle double-click on achievement in list"""
        item = self.achievements_tree.selection()[0] if self.achievements_tree.selection() else None
        if item:
            values = self.achievements_tree.item(item, "values")
            achievement_name = values[1]
            self._show_achievement_details(achievement_name)

    def _show_achievement_context_menu(self, event):
        """Show context menu for achievements"""
        if self.achievements_tree.selection():
            context_menu = tk.Menu(self.achievements_tree, tearoff=0)
            context_menu.add_command(label="✅ Complete Achievement", command=self._complete_selected)
            context_menu.add_command(label="🔄 Reset Achievement", command=self._reset_selected)
            context_menu.add_separator()
            context_menu.add_command(label="📋 Copy Achievement ID", command=self._copy_achievement_id)
            context_menu.add_command(label="ℹ️ Show Details", command=self._show_selected_achievement_details)
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()

    def _copy_achievement_id(self):
        """Copy selected achievement ID to clipboard"""
        selected = self.achievements_tree.selection()
        if selected:
            values = self.achievements_tree.item(selected[0], "values")
            achievement_name = values[1]
            # Find the full achievement ID
            for achievement_id, data in self.achievement_data_dict.items():
                if data['name'] == achievement_name:
                    self.parent.clipboard_clear()
                    self.parent.clipboard_append(achievement_id)
                    show_info("Copied", f"📋 Achievement ID copied to clipboard:\n{achievement_id}")
                    break

    def _show_selected_achievement_details(self):
        """Show details for selected achievement"""
        selected = self.achievements_tree.selection()
        if selected:
            values = self.achievements_tree.item(selected[0], "values")
            achievement_name = values[1]
            self._show_achievement_details(achievement_name)

    def _show_achievement_details(self, achievement_name):
        """Show detailed information about an achievement"""
        # Find the achievement data
        achievement_data = None
        achievement_id = None
        for aid, data in self.achievement_data_dict.items():
            if data['name'] == achievement_name:
                achievement_data = data
                achievement_id = aid
                break
        
        if not achievement_data:
            show_warning("Warning", "Achievement data not found")
            return
        
        # Create detailed achievement information dialog
        detail_window = tk.Toplevel(self.parent)
        detail_window.title(f"Achievement Details - {achievement_name}")
        detail_window.geometry("600x500")
        detail_window.resizable(True, True)
        
        # Main frame with padding
        main_frame = ttk.Frame(detail_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        status = self._determine_status(str(achievement_data['current']), achievement_data['max'])
        status_icon, _ = self._get_achievement_status_info(status, achievement_data['category'])
        title_label = ttk.Label(main_frame, text=f"{status_icon} {achievement_name}", 
                               font=('Segoe UI', 14, 'bold'))
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Details frame
        details_frame = ttk.LabelFrame(main_frame, text="Achievement Information", padding=15)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create details text widget
        details_text = tk.Text(details_frame, wrap=tk.WORD, font=('Consolas', 10), 
                              height=18, state=tk.NORMAL)
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=details_text.yview)
        details_text.configure(yscrollcommand=scrollbar.set)
        
        # Format achievement details
        progress_pct = (achievement_data['current'] / achievement_data['max'] * 100) if achievement_data['max'] > 0 else 0
        
        info_text = f"""🏆 Achievement Name: {achievement_name}
🏷️ Category: {achievement_data['category']}
🆔 Achievement ID: {achievement_id}
📊 Status: {status}
📈 Progress: {achievement_data['current']}/{achievement_data['max']} ({progress_pct:.1f}%)

📝 Description:
{'=' * 50}
{self._get_achievement_description(achievement_name, achievement_data['category'])}

🎯 Completion Requirements:
{'=' * 50}
{self._get_achievement_requirements(achievement_name, achievement_data['category'], achievement_data['max'])}

🔧 Technical Details:
{'=' * 50}
Achievement ID: {achievement_id}
Category: {achievement_data['category']}
Current Progress: {achievement_data['current']}
Maximum Value: {achievement_data['max']}
Completion Percentage: {progress_pct:.1f}%
"""
        
        details_text.insert(tk.END, info_text)
        details_text.config(state=tk.DISABLED)
        
        details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="📋 Copy ID", 
                  command=lambda: self._copy_to_clipboard(achievement_id)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="✅ Close", 
                  command=detail_window.destroy).pack(side=tk.RIGHT)

    def _get_achievement_description(self, name, category):
        """Get description for an achievement based on actual game data"""
        
        descriptions = {
            # Debug/Developer
            "Mission_ORouleau_1": "Developer achievement - Mission related to ORouleau development.",
            "pin_z_dev_orouleau": "Developer achievement - Pin Z development marker.",
            "orowin": "Developer achievement - ORO development marker.",
            
            # Story Achievements
            "Orientation Day Graduate": "Complete your first Hell's Gate visit and orientation.",
            "War's Begun": "Complete the Blue Lagoon mission to begin the conflict.",
            "The First Harmonic": "Score your first harmonic in Needle Hills area.",
            "Harmonic in the FEBA": "Score a harmonic from the Forward Edge Battle Area (FEBA).",
            "Grave's Bog Harmonic": "Score the harmonic in the dangerous Grave's Bog area.",
            "Hanging Gardens Mission": "Complete missions in the beautiful Hanging Gardens area.",
            "Coualt Highlands Mission": "Complete missions in the Coualt Highlands region.",
            "RDA Tantalus Complete": "Complete the RDA storyline in Tantalus area.",
            
            # Na'vi Story Path
            "Na'vi Blue Lagoon": "Complete Blue Lagoon fighting for the Na'vi.",
            "Na'vi Tantalus Start": "Begin the Na'vi path through Tantalus.",
            "Na'vi Tantalus Mission": "Complete Na'vi missions in Tantalus area.",
            "Verdant Pinnacle": "Complete missions in the lush Verdant Pinnacle.",
            "Dust Bowl Mission": "Complete missions in the harsh Dust Bowl area.",
            "Prolemuris Land": "Complete missions in Prolemuris territory.",
            "Vadera's Hollow": "Complete missions in the mysterious Vadera's Hollow.",
            "Deserted Heaven": "Complete missions in the Deserted Heaven area.",
            "Na'vi Tantalus Final": "Complete the final Na'vi missions in Tantalus.",
            
            # Clean Sweep Achievements
            "Clean Sweep of Pandora": "Complete all sector challenges across Pandora.",
            "Sebastien Clean Sweep": "Complete all challenges in Sebastien's area.",
            "Needle Hills Clean Sweep": "Complete all challenges in Needle Hills.",
            "Philippe Clean Sweep": "Complete all challenges in Philippe's area.",
            "Grave's Bog Clean Sweep": "Complete all challenges in Grave's Bog.",
            "Coualt Highlands Clean Sweep": "Complete all challenges in Coualt Highlands.",
            "Plains of Goliath Clean Sweep": "Complete all challenges in Plains of Goliath.",
            "Verdant Pinnacle Clean Sweep": "Complete all challenges in Verdant Pinnacle.",
            "Dust Bowl Clean Sweep": "Complete all challenges in Dust Bowl.",
            "Vadera's Hollow Clean Sweep": "Complete all challenges in Vadera's Hollow.",
            "Nancy Clean Sweep": "Complete all challenges in Nancy's area.",
            "Pascal Clean Sweep": "Complete all challenges in Pascal's area.",
            
            # Progression & Collection
            "Claim 50% Territories": "Use the conquest system to claim 50% of all territories.",
            "Pandorapedia Articles": "Unlock articles in the Pandorapedia encyclopedia.",
            "Fallback Kills": "Kill enemies using fallback weapons like dual wasps or bow.",
            
            # Skills
            "Grade 4 Corporate Skills": "Use Grade 4 corporate skills multiple times.",
            "Grade 4 Na'vi Skills": "Use Grade 4 Na'vi skills multiple times.",
            "Grade 4 All Skills": "Master all Grade 4 skills for both factions.",
            
            # Multiplayer
            "10 Kills in a Row": "Get 10 consecutive kills without dying in multiplayer.",
            "Play 150 Matches": "Complete 150 multiplayer matches.",
            "Finish Match Most Kills": "Finish a team deathmatch with the most kills.",
            "Win 3-0 CTF": "Win a Capture the Flag match 3-0.",
            "RDA 3 Intact Missiles": "As RDA, reach timer end with 3 intact missiles.",
            "Na'vi Destroy All Missiles": "As Na'vi, destroy every enemy missile.",
            "Win 5 Capture & Hold": "Win 5 Capture and Hold multiplayer matches.",
            "Win 5 King of the Hill": "Win 5 King of the Hill multiplayer matches.",
        }
        
        return descriptions.get(name, f"Achievement: {name}. Complete specific objectives to unlock this achievement.")

    def _get_achievement_requirements(self, name, category, max_value):
        """Get requirements for an achievement"""
        if max_value == 1:
            return "Complete the specific objective or reach the required milestone to unlock this achievement."
        else:
            return f"Accumulate {max_value} points of progress toward this achievement. Your current progress will be tracked automatically as you play."

    def _copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(text)
            show_info("Copied", f"📋 Copied to clipboard:\n{text}")
        except Exception as e:
            show_error("Error", f"Failed to copy: {str(e)}")

    def _complete_all_achievements(self) -> None:
        """Complete all achievements"""
        self.logger.debug("Completing all achievements")
        try:
            changes_made = False
            
            for achievement_id, achievement_data in self.achievement_data_dict.items():
                if achievement_data['current'] < achievement_data['max']:
                    # Update data
                    achievement_data['current'] = achievement_data['max']
                    achievement_data['element'].set("count", str(achievement_data['max']))
                    changes_made = True
            
            if changes_made:
                # Update the tree display
                self._apply_filter()  # Refresh the display
                self._update_all_displays()
                self.main_window.unsaved_label.config(text="Unsaved Changes")
                show_success("Success", "🏆 All achievements have been completed!")
            else:
                show_info("Info", "ℹ️ All achievements are already completed!")
            
        except Exception as e:
            self.logger.error(f"Error completing all achievements: {str(e)}", exc_info=True)
            show_error("Error", f"❌ Failed to complete achievements: {str(e)}")

    def _complete_selected(self) -> None:
        """Complete the selected achievements"""
        selected_items = self.achievements_tree.selection()
        if not selected_items:
            show_warning("Warning", "Please select at least one achievement")
            return

        try:
            changes_made = False
            
            for item in selected_items:
                values = self.achievements_tree.item(item, "values")
                achievement_name = values[1]
                
                # Find the achievement data
                for achievement_id, achievement_data in self.achievement_data_dict.items():
                    if achievement_data['name'] == achievement_name:
                        if achievement_data['current'] < achievement_data['max']:
                            # Update data
                            achievement_data['current'] = achievement_data['max']
                            achievement_data['element'].set("count", str(achievement_data['max']))
                            changes_made = True
                        break

            if changes_made:
                # Update the tree display
                self._apply_filter()  # Refresh the display
                self._update_all_displays()
                self.main_window.unsaved_label.config(text="Unsaved Changes")
                show_success("Success", "✅ Selected achievements have been completed!")
            else:
                show_info("Info", "ℹ️ Selected achievements are already completed!")

        except Exception as e:
            self.logger.error(f"Error completing achievements: {str(e)}", exc_info=True)
            show_error("Error", f"❌ Failed to complete achievements: {str(e)}")

    def _reset_selected(self) -> None:
        """Reset the selected achievements"""
        selected_items = self.achievements_tree.selection()
        if not selected_items:
            show_warning("Warning", "Please select at least one achievement")
            return

        try:
            changes_made = False
            
            for item in selected_items:
                values = self.achievements_tree.item(item, "values")
                achievement_name = values[1]
                
                # Find the achievement data
                for achievement_id, achievement_data in self.achievement_data_dict.items():
                    if achievement_data['name'] == achievement_name:
                        if achievement_data['current'] > 0:
                            # Update data
                            achievement_data['current'] = 0
                            achievement_data['element'].set("count", "0")
                            changes_made = True
                        break

            if changes_made:
                # Update the tree display
                self._apply_filter()  # Refresh the display
                self._update_all_displays()
                self.main_window.unsaved_label.config(text="Unsaved Changes")
                show_success("Success", "🔄 Selected achievements have been reset!")
            else:
                show_info("Info", "ℹ️ Selected achievements are already at zero!")

        except Exception as e:
            self.logger.error(f"Error resetting achievements: {str(e)}", exc_info=True)
            show_error("Error", f"❌ Failed to reset achievements: {str(e)}")

    def save_achievement_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        """Save achievement changes to XML tree"""
        self.logger.debug("Saving achievement changes")
        try:
            # Changes are already applied to the XML elements during updates
            # No additional processing needed since we update the elements directly
            self.logger.debug("Achievement changes saved successfully")
            return tree
            
        except Exception as e:
            self.logger.error(f"Error saving achievement changes: {str(e)}", exc_info=True)
            raise
import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
from typing import Dict, Optional
import logging
from custom_messagebox import MessageBoxManager, show_info, show_error, show_warning, ask_question, ask_ok_cancel, show_success


class MissionsManager:
    def __init__(self, parent: ttk.Frame, main_window):
        self.logger = logging.getLogger('MissionsManager')
        self.logger.debug("Initializing Modern MissionsManager")
        self.parent = parent
        self.main_window = main_window
        self.mission_data = {}
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
        
        # Main content area (missions list)
        self.create_main_content(content_frame)

    def create_header_section(self):
        """Create the header with title and search"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title and subtitle
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = ttk.Label(title_frame, text="🎯 Mission Status", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="Track your mission progress and objectives", 
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
        overview_frame = ttk.LabelFrame(sidebar_frame, text="📊 Mission Overview", padding=15)
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
        
        ttk.Label(self.completion_display, text="Missions Complete", font=('Segoe UI', 10)).pack()
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(overview_frame, mode='determinate', length=200)
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        
        # === STATISTICS SECTION ===
        stats_frame = ttk.LabelFrame(sidebar_frame, text="📈 Statistics", padding=15)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create statistics with modern layout
        self.create_stat_item(stats_frame, "🎯", "Total Missions", "0", "total_missions_label")
        self.create_stat_item(stats_frame, "✅", "Completed", "0", "completed_missions_label")
        self.create_stat_item(stats_frame, "🔄", "In Progress", "0", "in_progress_missions_label")
        self.create_stat_item(stats_frame, "⏸️", "Not Started", "0", "not_started_missions_label")
        
        # === FILTER SECTION ===
        filter_frame = ttk.LabelFrame(sidebar_frame, text="🔍 Filters", padding=15)
        filter_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(filter_frame, text="Show:", font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                   values=["All Missions", "✅ Completed", "🔄 In Progress", "⏸️ Not Started"],
                                   state="readonly", font=('Segoe UI', 9))
        filter_combo.set("All Missions")
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
        """Create the main content area with missions list"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Missions list header
        list_header = ttk.Frame(main_frame)
        list_header.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(list_header, text="🎯 Mission Progress", 
                 font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)
        
        # Status legend
        legend_frame = ttk.Frame(list_header)
        legend_frame.pack(side=tk.RIGHT)
        
        legend_items = [("✅", "Completed"), ("🔄", "In Progress"), ("⏸️", "Not Started")]
        for icon, desc in legend_items:
            ttk.Label(legend_frame, text=f"{icon} {desc}", font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=5)
        
        # Enhanced missions treeview
        tree_container = ttk.Frame(main_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure columns for better information display
        columns = ("status", "name", "type", "progress", "id", "details")
        self.missions_tree = ttk.Treeview(tree_container, columns=columns, show="headings", 
                                         selectmode="extended", height=20)
        
        # Configure headers
        headers = {
            "status": ("🎯", 60, "center"),
            "name": ("📋 Mission Name", 300, "w"),
            "type": ("🏷️ Type", 120, "w"), 
            "progress": ("📊 Progress", 100, "center"),
            "id": ("🆔 ID", 100, "center"),
            "details": ("ℹ️ Info", 100, "center")
        }
        
        for col, (text, width, anchor) in headers.items():
            self.missions_tree.heading(col, text=text)
            self.missions_tree.column(col, width=width, anchor=anchor, minwidth=50)
        
        # Enhanced color scheme
        self.setup_tree_styles()
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.missions_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.missions_tree.xview)
        self.missions_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.missions_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.missions_tree.bind("<Double-1>", self._on_mission_double_click)
        self.missions_tree.bind("<Button-3>", self._show_mission_context_menu)

    def setup_tree_styles(self):
        """Configure tree styling with modern color scheme"""
        self.missions_tree.tag_configure('completed', 
                                        background='#e8f5e8', 
                                        foreground="#00ff0d")
        self.missions_tree.tag_configure('in_progress', 
                                        background='#fff3e0', 
                                        foreground="#ff7300")
        self.missions_tree.tag_configure('not_started', 
                                        background='#ffebee', 
                                        foreground="#ff0000")
        self.missions_tree.tag_configure('story', 
                                        background='#e3f2fd', 
                                        foreground="#0077ff")
        self.missions_tree.tag_configure('combat', 
                                        background='#fce4ec', 
                                        foreground="#ff006f")

    def load_missions(self, tree: ET.ElementTree) -> None:
        """Load missions data with modern interface"""
        self.logger.debug("Loading missions with modern interface")
        try:
            # Clear existing data
            self.mission_data = {}
            
            # Clear existing items in treeview
            for item in self.missions_tree.get_children():
                self.missions_tree.delete(item)
            
            # Find all mission elements
            mission_elements = []
            mission_elements.extend(tree.findall(".//Mission_Completed"))
            mission_elements.extend(tree.findall(".//Mission_InProgress"))
            mission_elements.extend(tree.findall(".//Mission_NotStarted"))
            
            self.logger.debug(f"Found {len(mission_elements)} missions")
            
            # Sort missions by ID for consistent display
            missions_sorted = sorted(mission_elements, key=lambda x: x.get("crc_id", "0"))
            
            # Map of mission types to status
            status_map = {
                "Mission_Completed": "Completed",
                "Mission_InProgress": "In Progress",
                "Mission_NotStarted": "Not Started"
            }
            
            # Process each mission
            for mission in missions_sorted:
                try:
                    mission_id = mission.get("crc_id", "")
                    mission_type = mission.tag
                    status = status_map.get(mission_type, "Unknown")
                    
                    # Get mission progress
                    progress = self._calculate_progress(mission, mission_type)
                    
                    # Get mission name and type
                    mission_name = self._get_mission_name(mission_id)
                    category = self._get_mission_category(mission_name)
                    
                    # Store mission data
                    self.mission_data[mission_id] = {
                        'name': mission_name,
                        'status': status,
                        'progress': progress,
                        'category': category,
                        'element': mission
                    }
                    
                    # Determine status icon and styling
                    status_icon, tag = self._get_mission_status_info(status, category)
                    
                    # Insert into tree
                    self.missions_tree.insert("", tk.END, values=(
                        status_icon,
                        mission_name,
                        category,
                        progress,
                        mission_id[-8:] if len(mission_id) > 8 else mission_id,  # Show last 8 digits
                        "View Details"
                    ), tags=(tag,))
                    
                except Exception as e:
                    self.logger.error(f"Error processing mission {mission_id}: {str(e)}", exc_info=True)
            
            # Update all displays
            self._update_all_displays()
            
            self.logger.debug("Missions loaded successfully with modern interface")
            
        except Exception as e:
            self.logger.error(f"Error loading missions: {str(e)}", exc_info=True)
            raise

    def _calculate_progress(self, mission, mission_type):
        """Calculate mission progress"""
        if mission_type == "Mission_Completed":
            return "100%"
        elif mission_type == "Mission_InProgress":
            current_step = mission.get("iCurrentStepIndex", "0")
            objective_count = len(mission.findall("Objective"))
            if objective_count > 0:
                # Count completed objectives
                completed = sum(1 for obj in mission.findall("Objective") if obj.get("status", "0") == "1")
                return f"{completed}/{objective_count}"
            else:
                return f"Step {current_step}"
        else:
            return "0%"

    def _get_mission_category(self, mission_name):
        """Determine mission category based on name"""
        name_lower = mission_name.lower()
        
        if any(keyword in name_lower for keyword in ['story', 'harmonic', 'song', 'search', 'ancient']):
            return "Story"
        elif any(keyword in name_lower for keyword in ['assault', 'combat', 'defense', 'attack', 'weapons', 'training']):
            return "Combat"
        elif any(keyword in name_lower for keyword in ['research', 'analysis', 'study', 'survey', 'specimen', 'science']):
            return "Research"
        elif any(keyword in name_lower for keyword in ['escort', 'transport', 'delivery', 'convoy']):
            return "Transport"
        elif any(keyword in name_lower for keyword in ['patrol', 'reconnaissance', 'scout']):
            return "Reconnaissance"
        else:
            return "General"

    def _get_mission_status_info(self, status, category):
        """Get status icon and tag for a mission"""
        if status == "Completed":
            status_icon = "✅"
            if category == "Story":
                tag = "story"
            elif category == "Combat":
                tag = "combat"
            else:
                tag = "completed"
        elif status == "In Progress":
            status_icon = "🔄"
            tag = "in_progress"
        else:
            status_icon = "⏸️"
            tag = "not_started"
        
        return status_icon, tag

    def _update_all_displays(self):
        """Update all display elements"""
        total_missions = len(self.mission_data)
        completed_count = sum(1 for data in self.mission_data.values() if data['status'] == 'Completed')
        in_progress_count = sum(1 for data in self.mission_data.values() if data['status'] == 'In Progress')
        not_started_count = sum(1 for data in self.mission_data.values() if data['status'] == 'Not Started')
        
        # Update main completion display
        completion_pct = (completed_count / total_missions * 100) if total_missions > 0 else 0
        self.completion_percentage.config(text=f"{completion_pct:.0f}%")
        self.progress_bar['value'] = completion_pct
        
    def _apply_filter(self, event=None):
        """Apply search and filter to the missions list"""
        filter_value = self.filter_var.get()
        search_text = self.search_var.get().lower()
        
        # Clear and repopulate tree
        for item in self.missions_tree.get_children():
            self.missions_tree.delete(item)
        
        # Re-add filtered items
        for mission_id, mission_data in self.mission_data.items():
            if self._should_show_mission(mission_id, mission_data, filter_value, search_text):
                status = mission_data['status']
                category = mission_data['category']
                status_icon, tag = self._get_mission_status_info(status, category)
                
                self.missions_tree.insert("", tk.END, values=(
                    status_icon,
                    mission_data['name'],
                    category,
                    mission_data['progress'],
                    mission_id[-8:] if len(mission_id) > 8 else mission_id,
                    "View Details"
                ), tags=(tag,))

    def _should_show_mission(self, mission_id, mission_data, filter_value, search_text):
        """Determine if mission should be shown based on filters"""
        name = mission_data['name']
        status = mission_data['status']
        category = mission_data['category']
        
        # Apply filter
        if filter_value == "✅ Completed" and status != "Completed":
            return False
        elif filter_value == "🔄 In Progress" and status != "In Progress":
            return False
        elif filter_value == "⏸️ Not Started" and status != "Not Started":
            return False
        elif filter_value == "📖 Story Missions" and category != "Story":
            return False
        elif filter_value == "⚔️ Combat Missions" and category != "Combat":
            return False
        elif filter_value == "🔬 Research Missions" and category != "Research":
            return False
        elif filter_value == "🚁 Transport Missions" and category != "Transport":
            return False
        
        # Apply search
        if search_text and search_text not in name.lower() and search_text not in mission_id.lower():
            return False
        
        return True

    def _on_mission_double_click(self, event):
        """Handle double-click on mission in list"""
        item = self.missions_tree.selection()[0] if self.missions_tree.selection() else None
        if item:
            values = self.missions_tree.item(item, "values")
            self._show_mission_details(values[1])  # mission name

    def _show_mission_context_menu(self, event):
        """Show context menu for missions"""
        if self.missions_tree.selection():
            context_menu = tk.Menu(self.missions_tree, tearoff=0)
            context_menu.add_command(label="📋 Copy Mission ID", command=self._copy_mission_id)
            context_menu.add_command(label="ℹ️ Show Details", command=self._show_selected_mission_details)
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()

    def _copy_mission_id(self):
        """Copy selected mission ID to clipboard"""
        selected = self.missions_tree.selection()
        if selected:
            values = self.missions_tree.item(selected[0], "values")
            # Find the full mission ID from our data
            mission_name = values[1]
            for mission_id, mission_data in self.mission_data.items():
                if mission_data['name'] == mission_name:
                    self.parent.clipboard_clear()
                    self.parent.clipboard_append(mission_id)
                    show_info("Copied", f"📋 Mission ID copied to clipboard:\n{mission_id}")
                    break

    def _show_selected_mission_details(self):
        """Show details for selected mission"""
        selected = self.missions_tree.selection()
        if selected:
            values = self.missions_tree.item(selected[0], "values")
            self._show_mission_details(values[1])  # mission name

    def _show_mission_details(self, mission_name):
        """Show detailed information about a mission"""
        # Find the mission data
        mission_data = None
        mission_id = None
        for mid, data in self.mission_data.items():
            if data['name'] == mission_name:
                mission_data = data
                mission_id = mid
                break
        
        if not mission_data:
            show_warning("Warning", "Mission data not found")
            return
        
        # Create detailed mission information dialog
        detail_window = tk.Toplevel(self.parent)
        detail_window.title(f"Mission Details - {mission_name}")
        detail_window.geometry("1600x800")
        detail_window.resizable(True, True)
        
        # Main frame with padding
        main_frame = ttk.Frame(detail_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        status_icon, _ = self._get_mission_status_info(mission_data['status'], mission_data['category'])
        title_label = ttk.Label(main_frame, text=f"{status_icon} {mission_name}", 
                               font=('Segoe UI', 14, 'bold'))
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Details frame
        details_frame = ttk.LabelFrame(main_frame, text="Mission Information", padding=15)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create details text widget
        details_text = tk.Text(details_frame, wrap=tk.WORD, font=('Consolas', 10), 
                              height=20, state=tk.NORMAL)
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=details_text.yview)
        details_text.configure(yscrollcommand=scrollbar.set)
        
        # Format mission details
        info_text = f"""🎯 Mission Name: {mission_name}
🏷️ Category: {mission_data['category']}
🆔 Mission ID: {mission_id}
📊 Status: {mission_data['status']}
📈 Progress: {mission_data['progress']}

📋 Mission Description:
{'=' * 50}
{self._get_mission_description(mission_name, mission_data['category'])}

🎯 Objectives:
{'=' * 50}
{self._get_mission_objectives(mission_data['element'])}

🔧 Technical Details:
{'=' * 50}
Mission ID: {mission_id}
Category: {mission_data['category']}
Status: {mission_data['status']}
Progress: {mission_data['progress']}
"""
        
        details_text.insert(tk.END, info_text)
        details_text.config(state=tk.DISABLED)
        
        details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="📋 Copy ID", 
                  command=lambda: self._copy_to_clipboard(mission_id)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="✅ Close", 
                  command=detail_window.destroy).pack(side=tk.RIGHT)

    def _get_mission_description(self, mission_name, category):
        """Get description for a mission based on name and category"""
        # Generate contextual descriptions based on mission type
        if category == "Story":
            return f"This is a main story mission that advances the primary narrative. '{mission_name}' plays a crucial role in your character's journey through Pandora's conflicts."
        elif category == "Combat":
            return f"A combat-focused mission requiring tactical skills and weapon proficiency. '{mission_name}' will test your combat abilities against various threats."
        elif category == "Research":
            return f"A scientific mission involving research, analysis, or specimen collection. '{mission_name}' contributes to understanding Pandora's ecosystem."
        elif category == "Transport":
            return f"A logistics mission involving the safe transport of personnel, equipment, or materials. '{mission_name}' requires careful planning and execution."
        elif category == "Reconnaissance":
            return f"An intelligence-gathering mission requiring stealth and observation skills. '{mission_name}' involves scouting and information collection."
        else:
            return f"'{mission_name}' is an important mission that contributes to your overall progress and understanding of Pandora's complex situation."

    def _get_mission_objectives(self, mission_element):
        """Extract and format mission objectives from XML element"""
        objectives = mission_element.findall("Objective")
        if not objectives:
            return "• Complete mission requirements\n• Follow mission briefing instructions"
        
        objective_text = ""
        for i, obj in enumerate(objectives, 1):
            status = "✅" if obj.get("status", "0") == "1" else "⏸️"
            objective_text += f"• {status} Objective {i}\n"
        
        return objective_text if objective_text else "• Mission objectives will be revealed during gameplay"

    def _copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(text)
            show_info("Copied", f"📋 Copied to clipboard:\n{text}")
        except Exception as e:
            show_error("Error", f"Failed to copy: {str(e)}")
            
    def save_mission_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        """Mission data is view-only, return unchanged tree"""
        self.logger.debug("Preserving mission data (no changes possible)")
        return tree
    
    def _get_mission_name(self, mission_id):
        """Convert mission ID to human-readable name"""
        mission_names = {
            # Main Story Missions
            "148645412": "The First Harmonic",
            "587544596": "Song of Ancient Forest",
            "820789492": "Search for the Song",
            "1964522520": "Assault on RDA Base",
            "3614666474": "Reporting For Duty",
            "11089996": "Cover Fire",
            "90368515": "RDA Advanced Training",
            "121662641": "Resource Depot Defense",
            "215262760": "Secure the Mine",
            "263316029": "Escort the Convoy",
            "320553437": "Mineral Deposit Survey",
            "431098125": "Missing Scientist",
            "464447814": "Aerial Combat Drills",
            "716403775": "Weapons Testing",
            "818627565": "Science Project",
            "931235053": "Lost Patrol",
            "977638923": "Rogue Scientist",
            "984264030": "Supply Line Defense",
            "1030999372": "Security Systems Calibration",
            "1036478791": "Pest Control",
            "1042381703": "Creature Containment",
            "1157473354": "Equipment Recovery",
            "1204581243": "A New You",
            "1206612066": "Flora Analysis",
            "1249181146": "Experimental Weapons",
            "1254119889": "Anti-Insurgent Operation",
            "1313574664": "Resource Extraction",
            "1327439578": "Medical Supply Delivery",
            "1399835803": "Mine Sabotage Investigation",
            "1409419394": "Hazardous Materials Transport",
            "1506597615": "Arrived At Hells Gate",
            "1546449249": "Territorial Expansion",
            "1563937596": "Spy Network Elimination",
            "1564508887": "Escort Mission",
            "1572095145": "Chemical Spill Cleanup",
            "1617867177": "Resource Gathering",
            "1657988851": "Jungle Patrol",
            "1775828354": "Field Research",
            "1854235998": "Special Forces Operation",
            "1919277717": "Machinery Repair",
            "1949395925": "Comms Array Installation",
            "1963466380": "Weapons Smuggling Investigation",
            "2025247403": "Radar Outpost Setup",
            "2037743848": "Artifact Recovery",
            "2057131377": "Wildlife Control",
            "2129913038": "Outpost Construction",
            "2145064626": "Specimen Collection",
            "2159761591": "Sabotage",
            "2162960250": "VIP Protection",
            "2223059682": "Reconnaissance",
            "2278988974": "Hunter Challenge",
            "2288339483": "Emergency Evacuation",
            "2359406436": "Tech Recovery",
            "2375737874": "Border Dispute",
            "2446686110": "Hazardous Terrain Survey",
            "2472171157": "Training Exercises",
            "2528686983": "Anti-Air Defense Setup",
            "2536946474": "Aerial Support",
            "2538293033": "Experimental Tech Recovery",
            "2556640181": "Mine Clearing",
            "2577426934": "Legwork",
            "2600894368": "Base Expansion",
            "2624306105": "Tactical Assessment",
            "2635659551": "Vehicle Recovery",
            "2664279535": "Creature Taming",
            "2691980924": "To The Lagoon",
            "2699578136": "Territorial Dispute",
            "2702278646": "Contamination Cleanup",
            "2706890028": "Advanced Weaponry Test",
            "2745433316": "Aerial Reconnaissance",
            "2804427325": "Extraction Operation",
            "2850361678": "Geological Survey",
            "2853548239": "Indigenous Relations",
            "2928203095": "Bridge Construction",
            "2964671126": "Scout Network Establishment",
            "3005466356": "Dangerous Wildlife Elimination",
            "3018211430": "Supply Disruption",
            "3121375662": "Communications Relay Setup",
            "3176297883": "Intelligence Gathering",
            "3177295287": "Prototype Weapon Test",
            "3184855484": "Tunnel System Exploration",
            "3188729112": "Ancient Artifacts",
            "3223683550": "Pandoran Study",
            "3277020831": "Special Materials Collection",
            "3395722529": "Minefield Deployment",
            "3440073016": "Resource Survey",
            "3492747947": "Spy Network Disruption",
            "3505535715": "Ambush Preparation",
            "3548228704": "Defense Perimeter Setup",
            "3553167467": "Fauna Relocation",
            "3567570034": "Emergency Response",
            "3591786336": "Waterfall Cave Expedition",
            "3650086337": "Recon Drone Deployment",
            "3708977241": "Advanced Combat Training",
            "3869409139": "Special Mission 2",
            "3872540424": "Remote Sensing Array",
            "3922369913": "Resource Extraction",
            "3941247737": "Vehicle Combat Training",
            "3949759279": "Specimen Transport",
            "3959508790": "Technology Demonstration",
            "4003944800": "Reconnaissance Mission",
            "4004743186": "Security Patrol",
            "4040272952": "Territorial Control",
            "4085556621": "Environmental Monitoring",
            "4156182083": "Special Mission 1",
            "4214204955": "Biodiversity Survey",
            "4238570271": "Outpost Defense"
        }
        return mission_names.get(mission_id, f"Unknown Mission ({mission_id})")


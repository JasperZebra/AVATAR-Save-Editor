import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
from typing import Dict, Optional
import logging
from custom_messagebox import MessageBoxManager, show_info, show_error, show_warning, ask_question, ask_ok_cancel, show_success


class SkillsManager:
    def __init__(self, parent: ttk.Frame, main_window):
        self.logger = logging.getLogger('SkillsManager')
        self.logger.debug("Initializing Modern SkillsManager")
        self.parent = parent
        self.main_window = main_window
        self.skills_data = {}
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
        
        # Left sidebar (filters and stats)
        self.create_sidebar(content_frame)
        
        # Main content area (skills display)
        self.create_main_content(content_frame)

    def create_header_section(self):
        """Create the header with title and search"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title and subtitle
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = ttk.Label(title_frame, text="🎯 Character Skills", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="View your character's skill progression and abilities", 
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
        """Create the left sidebar with filters and statistics"""
        sidebar_frame = ttk.Frame(parent, width=280)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        sidebar_frame.pack_propagate(False)
        
        # === STATISTICS SECTION ===
        stats_frame = ttk.LabelFrame(sidebar_frame, text="📊 Statistics", padding=15)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create statistics with modern layout
        self.create_stat_item(stats_frame, "🎯", "Total Skills", "0", "total_skills_label")
        self.create_stat_item(stats_frame, "🔓", "Unlocked", "0", "unlocked_skills_label")  
        self.create_stat_item(stats_frame, "🔒", "Locked", "0", "locked_skills_label")
        self.create_stat_item(stats_frame, "⭐", "Special", "0", "special_skills_label")
        
        # Progress bar for completion
        progress_frame = ttk.Frame(stats_frame)
        progress_frame.pack(fill=tk.X, pady=(10, 5))
        
        ttk.Label(progress_frame, text="Completion Progress:", font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=200)
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        self.completion_label = ttk.Label(progress_frame, text="0%", font=('Segoe UI', 9))
        self.completion_label.pack(anchor=tk.W, pady=(2, 0))
        
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
        """Create the main content area with skills display"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Skills list header
        list_header = ttk.Frame(main_frame)
        list_header.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(list_header, text="🎯 Character Skills", 
                 font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)
        
        # Status legend
        legend_frame = ttk.Frame(list_header)
        legend_frame.pack(side=tk.RIGHT)
        
        legend_items = [("🔒", "Locked"), ("🔓", "Unlocked"), ("⭐", "Special")]
        for icon, desc in legend_items:
            ttk.Label(legend_frame, text=f"{icon} {desc}", font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=5)
        
        # Create the list view directly
        self.create_list_view(main_frame)

    def create_list_view(self, parent):
        """Create the list view with enhanced treeview"""
        tree_container = ttk.Frame(parent)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Enhanced columns
        columns = ("status", "name", "category", "id", "details")
        self.skills_tree = ttk.Treeview(tree_container, columns=columns, show="headings", 
                                       selectmode="extended", height=20)
        
        # Configure headers
        headers = {
            "status": ("🔒", 60, "center"),
            "name": ("🎯 Skill Name", 250, "w"),
            "category": ("📂 Category", 150, "w"),
            "id": ("🆔 ID", 120, "center"),
            "details": ("ℹ️ Details", 100, "center")
        }
        
        for col, (text, width, anchor) in headers.items():
            self.skills_tree.heading(col, text=text)
            self.skills_tree.column(col, width=width, anchor=anchor, minwidth=50)
        
        # Enhanced color scheme
        self.setup_tree_styles()
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.skills_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.skills_tree.xview)
        self.skills_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.skills_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.skills_tree.bind("<Double-1>", self._on_skill_double_click)
        self.skills_tree.bind("<Button-3>", self._show_skill_context_menu)

    def setup_tree_styles(self):
        """Configure tree styling with modern color scheme"""
        self.skills_tree.tag_configure('locked', 
                                      background='#ffebee', 
                                      foreground="#ff0000")
        self.skills_tree.tag_configure('unlocked', 
                                      background='#e8f5e8', 
                                      foreground="#00ff0d")
        self.skills_tree.tag_configure('special', 
                                      background='#fff3e0', 
                                      foreground="#ff7300")

    def load_skills(self, tree: ET.ElementTree) -> None:
        """Load skills data with improved organization"""
        self.logger.debug("Loading skills with modern interface")
        try:
            # Clear existing data
            self.skills_data = {}
            for item in self.skills_tree.get_children():
                self.skills_tree.delete(item)
            
            # Find all skill elements
            skills = tree.findall(".//AvatarSkillDB_Status/Skill")
            self.logger.debug(f"Found {len(skills)} skills")
            
            # Process skills by category
            categories = {}
            
            for skill in skills:
                skill_id = skill.get("crc_id", "")
                locked_status = skill.get("eLocked", "0")
                
                skill_info = self._get_skill_info(skill_id)
                
                # Store skill data
                self.skills_data[skill_id] = {
                    'element': skill,
                    'name': skill_info["name"],
                    'category': skill_info["category"],
                    'locked': locked_status
                }
                
                # Group by category
                category = skill_info["category"]
                if category not in categories:
                    categories[category] = []
                
                categories[category].append({
                    "id": skill_id,
                    "name": skill_info["name"],
                    "category": category,
                    "locked": locked_status
                })
            
            # Populate list view
            self._populate_list_view(categories)
            
            # Update all displays
            self._update_all_displays(categories)
            
            self.logger.debug("Skills loaded successfully with modern interface")
            
        except Exception as e:
            self.logger.error(f"Error loading skills: {str(e)}", exc_info=True)
            raise

    def _populate_list_view(self, categories):
        """Populate the list view treeview"""
        for category_name in sorted(categories.keys()):
            category_skills = sorted(categories[category_name], key=lambda x: x["name"])
            
            for skill in category_skills:
                # Determine status and styling
                status_icon, tag = self._get_skill_status_info(skill["locked"])
                
                # Insert into tree
                self.skills_tree.insert("", tk.END, values=(
                    status_icon,
                    skill["name"],
                    skill["category"],
                    skill["id"][-8:] if len(skill["id"]) > 8 else skill["id"],  # Show last 8 digits
                    "View Details"
                ), tags=(tag,))

        # Remove unused methods and references
        pass

    def _get_skill_status_info(self, locked_status):
        """Get status icon and tag for a skill"""
        if locked_status == "0":
            return "🔓", "unlocked"
        elif locked_status == "2":
            return "⭐", "special"
        else:
            return "🔒", "locked"

    def _update_all_displays(self, categories):
        """Update all display elements"""
        # Calculate statistics
        total_skills = sum(len(skills) for skills in categories.values())
        unlocked_skills = 0
        locked_skills = 0
        special_skills = 0
        
        for skills in categories.values():
            for skill in skills:
                if skill["locked"] == "0":
                    unlocked_skills += 1
                elif skill["locked"] == "2":
                    special_skills += 1
                else:
                    locked_skills += 1
        
        # Update statistics
        self.total_skills_label.config(text=str(total_skills))
        self.unlocked_skills_label.config(text=str(unlocked_skills))
        self.locked_skills_label.config(text=str(locked_skills))
        self.special_skills_label.config(text=str(special_skills))
        
        # Update progress
        completion_pct = ((unlocked_skills + special_skills) / total_skills * 100) if total_skills > 0 else 0
        self.progress_bar['value'] = completion_pct
        self.completion_label.config(text=f"{completion_pct:.1f}% Complete")

    def _update_category_breakdown(self, categories):
        """Update the category breakdown listbox"""
        self.category_listbox.delete(0, tk.END)
        
        for category_name in sorted(categories.keys()):
            skills = categories[category_name]
            unlocked = sum(1 for skill in skills if skill["locked"] in ["0", "2"])
            total = len(skills)
            pct = (unlocked / total * 100) if total > 0 else 0
            
            self.category_listbox.insert(tk.END, f"{category_name}: {unlocked}/{total} ({pct:.0f}%)")

    def _apply_filter(self, event=None):
        """Apply search and filter to the list view"""
        filter_value = self.filter_var.get()
        search_text = self.search_var.get().lower()
        
        # Show all items first
        for item in self.skills_tree.get_children():
            self.skills_tree.item(item, tags=self.skills_tree.item(item, "tags"))
        
        # Hide items that don't match filter/search
        items_to_delete = []
        for item in self.skills_tree.get_children():
            values = self.skills_tree.item(item, "values")
            status_icon, name, category, skill_id, details = values
            
            # Apply filter
            show_item = True
            if filter_value == "🔓 Unlocked Only" and status_icon != "🔓":
                show_item = False
            elif filter_value == "🔒 Locked Only" and status_icon != "🔒":
                show_item = False
            elif filter_value == "⭐ Special Only" and status_icon != "⭐":
                show_item = False
            elif filter_value.startswith("⚔️") and "Combat" not in category:
                show_item = False
            elif filter_value.startswith("🛡️") and "Survival" not in category:
                show_item = False
            elif filter_value.startswith("👤") and "Stealth" not in category:
                show_item = False
            elif filter_value.startswith("🏃") and "Movement" not in category:
                show_item = False
            elif filter_value.startswith("🔧") and "Crafting" not in category:
                show_item = False
            elif filter_value.startswith("🌿") and "Na'vi Connection" not in category:
                show_item = False
            elif filter_value.startswith("🤖") and "RDA Training" not in category:
                show_item = False
            elif filter_value.startswith("🎖️") and "Specialist" not in category:
                show_item = False
            elif filter_value.startswith("✨") and "Special Abilities" not in category:
                show_item = False
            elif filter_value.startswith("🗺️") and "Exploration" not in category:
                show_item = False
            elif filter_value.startswith("🚗") and "Vehicle" not in category:
                show_item = False
            
            # Apply search
            if search_text and search_text not in name.lower() and search_text not in skill_id.lower():
                show_item = False
            
            # Hide item if it doesn't match
            if not show_item:
                items_to_delete.append(item)
        
        # Delete items that don't match
        for item in items_to_delete:
            self.skills_tree.delete(item)

    def _on_skill_double_click(self, event):
        """Handle double-click on skill in list view"""
        item = self.skills_tree.selection()[0] if self.skills_tree.selection() else None
        if item:
            values = self.skills_tree.item(item, "values")
            self._show_skill_details(values[2], values[1])  # category, name

    def _show_skill_context_menu(self, event):
        """Show context menu for skills"""
        if self.skills_tree.selection():
            context_menu = tk.Menu(self.skills_tree, tearoff=0)
            context_menu.add_command(label="📋 Copy Skill ID", command=self._copy_skill_id)
            context_menu.add_command(label="ℹ️ Show Details", command=self._show_selected_skill_details)
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()

    def _show_selected_skill_details(self):
        """Show details for selected skill"""
        selected = self.skills_tree.selection()
        if selected:
            values = self.skills_tree.item(selected[0], "values")
            self._show_skill_details(values[2], values[1])  # category, name

    def _copy_skill_id(self):
        """Copy selected skill ID to clipboard"""
        selected = self.skills_tree.selection()
        if selected:
            values = self.skills_tree.item(selected[0], "values")
            # Find the full skill ID from our data
            skill_name = values[1]
            for skill_id, skill_data in self.skills_data.items():
                if skill_data['name'] == skill_name:
                    self.parent.clipboard_clear()
                    self.parent.clipboard_append(skill_id)
                    show_info("Copied", f"📋 Skill ID copied to clipboard:\n{skill_id}")
                    break

    def _show_skill_details(self, category, skill_name):
        """Show detailed information about a skill"""
        # Find the skill data
        skill_data = None
        skill_id = None
        for sid, data in self.skills_data.items():
            if data['name'] == skill_name and data['category'] == category:
                skill_data = data
                skill_id = sid
                break
        
        if not skill_data:
            show_warning("Warning", "Skill data not found")
            return
        
        # Create detailed skill information dialog
        detail_window = tk.Toplevel(self.parent)
        detail_window.title(f"Skill Details - {skill_name}")
        detail_window.geometry("1600x800")
        detail_window.resizable(True, True)
         
        # Main frame with padding
        main_frame = ttk.Frame(detail_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"🎯 {skill_name}", 
                            font=('Segoe UI', 14, 'bold'))
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Details frame
        details_frame = ttk.LabelFrame(main_frame, text="Skill Information", padding=15)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create details text widget
        details_text = tk.Text(details_frame, wrap=tk.WORD, font=('Consolas', 10), 
                            height=15, state=tk.NORMAL)
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=details_text.yview)
        details_text.configure(yscrollcommand=scrollbar.set)
        
        # Format skill details
        status_text = {"0": "🔓 Unlocked", "1": "🔒 Locked", "2": "⭐ Special"}.get(skill_data['locked'], f"❓ Unknown ({skill_data['locked']})")
        
        info_text = f"""🎯 Skill Name: {skill_name}
    📂 Category: {category}
    🆔 Skill ID: {skill_id}
    🔒 Status: {status_text}

    🔧 Technical Details:
    {'=' * 30}
    Element Attributes:
    """
        
        # Add XML element attributes
        element = skill_data['element']
        for attr_name, attr_value in element.attrib.items():
            info_text += f"{attr_name}: {attr_value}\n"
        
        details_text.insert(tk.END, info_text)
        details_text.config(state=tk.DISABLED)
        
        details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="📋 Copy ID", 
                command=lambda: self._copy_to_clipboard(skill_id)).pack(side=tk.LEFT, padx=(0, 10))
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

    def save_skill_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        """Skills are view-only, return unchanged tree"""
        self.logger.debug("Skills are view-only, no changes to save")
        return tree
    
    def _get_skill_info(self, skill_id):
        """Map skill ID to name and category with enhanced data"""
        
        # Define skill categories with enhanced information
        combat_skills = {
            "370163335": "Rapid Fire",
            "1588994160": "Precision Shot",
            "2288728861": "Burst Fire",
            "1298333286": "Quick Reload",
            "1749835489": "Headshot",
            "2901239959": "Combat Roll",
            "228756694": "Suppression Fire",
            "2122270851": "Incendiary Rounds",
            "2193097390": "Frag Grenade",
            "2282375423": "Armor Piercing"
        }
        
        survival_skills = {
            "3121856597": "Health Regeneration",
            "208683785": "Resource Efficiency",
            "4172838722": "Scavenger",
            "1054477512": "Stamina Boost",
            "1906639931": "Environmental Resistance",
            "3989189724": "Heat Resistance",
            "138960729": "Cold Resistance",
            "1987225269": "Toxin Resistance",
            "3072205389": "Quick Recovery",
            "1147345197": "Endurance"
        }
        
        stealth_skills = {
            "3619269117": "Silent Movement",
            "3919303244": "Camouflage",
            "707441961": "Enhanced Vision",
            "1533580208": "Distraction",
            "1823892354": "Stealth Takedown",
            "2248739839": "Shadow Step",
            "464605972": "Quick Strike",
            "1578904643": "Noise Reduction",
            "2507739827": "Track Covering",
            "3843286588": "Night Vision"
        }
        
        movement_skills = {
            "4279072873": "Sprint",
            "4285766578": "Climbing",
            "1774875854": "Swimming",
            "2149792658": "Jump Height",
            "4141500320": "Fall Damage Reduction",
            "527383063": "Agility",
            "611800566": "Acrobatics",
            "863723867": "Wall Run",
            "1533394898": "Balance",
            "2479233397": "Terrain Navigation"
        }
        
        crafting_skills = {
            "2596340938": "Weapon Crafting",
            "2815647090": "Armor Crafting",
            "771604749": "Tool Crafting",
            "2120156884": "Resource Gathering",
            "154070465": "Material Analysis",
            "1711548883": "Advanced Engineering",
            "1785634812": "Recycling",
            "2057681984": "Improvisation",
            "2779483555": "Medical Supplies",
            "2953989487": "Ammunition Crafting"
        }
        
        navi_skills = {
            "3149590643": "Ikran Bond",
            "3819761146": "Direhorse Bond",
            "480060929": "Na'vi Language",
            "525037175": "Tribal Knowledge",
            "1411228025": "Forest Navigation",
            "2932769824": "Plant Identification",
            "3043422876": "Animal Handling",
            "3605504349": "Hunting",
            "4047834971": "Tsaheylu Mastery",
            "4221139584": "Cultural Understanding"
        }
        
        rda_skills = {
            "929187032": "AMP Suit Operation",
            "1073248985": "Vehicle Operation",
            "1849804230": "Security Systems",
            "1887679822": "Communications",
            "2824265184": "Equipment Maintenance",
            "3490889542": "Data Analysis",
            "62547143": "Mining Operations",
            "77959529": "Heavy Weapons",
            "376364380": "Technology Interface",
            "521610040": "Science Research"
        }
        
        specialist_skills = {
            "699117554": "Sniper Training",
            "896499985": "Demolitions Expert",
            "1539660776": "Tactical Analysis",
            "3305899539": "Squad Command",
            "4049689403": "Armor Specialist",
            "1719323144": "Field Medic",
            "1745871194": "Reconnaissance",
            "2831657996": "Electronics",
            "3130830861": "Hacking",
            "3440701635": "Sabotage"
        }
        
        special_abilities = {
            "3659056238": "Aerial Assault",
            "651760328": "Berserker Rage",
            "1862651544": "Stealth Camouflage",
            "1745884078": "Time Perception",
            "2071425951": "Enhanced Reflexes",
            "745513766": "Adrenaline Surge",
            "4073911841": "Force Field",
            "689642709": "Tracking Vision",
            "895550929": "Thermal Vision",
            "1239235678": "Enhanced Strength"
        }
        
        exploration_skills = {
            "1761588079": "Map Reading",
            "1959749094": "Pathfinding",
            "2278341981": "Grappling Hook",
            "3305111690": "Climbing Gear",
            "4044964372": "Gliding",
            "1125225940": "Cave Navigation",
            "2171844251": "River Navigation",
            "482995089": "Tracking",
            "2289347364": "Mountaineering",
            "2904552696": "Weather Prediction"
        }
        
        vehicle_skills = {
            "4154870226": "Helicopter Piloting",
            "1774378097": "ATV Operation",
            "2167405524": "Tank Operation",
            "2254859181": "Boat Navigation",
            "3229137376": "Aircraft Operation",
            "218464304": "Defensive Driving",
            "516287719": "Evasive Maneuvers",
            "3548279530": "Vehicle Repair"
        }
        
        # Combine all categories
        all_skills = {}
        all_skills.update({id: {"name": name, "category": "Combat"} for id, name in combat_skills.items()})
        all_skills.update({id: {"name": name, "category": "Survival"} for id, name in survival_skills.items()})
        all_skills.update({id: {"name": name, "category": "Stealth"} for id, name in stealth_skills.items()})
        all_skills.update({id: {"name": name, "category": "Movement"} for id, name in movement_skills.items()})
        all_skills.update({id: {"name": name, "category": "Crafting"} for id, name in crafting_skills.items()})
        all_skills.update({id: {"name": name, "category": "Na'vi Connection"} for id, name in navi_skills.items()})
        all_skills.update({id: {"name": name, "category": "RDA Training"} for id, name in rda_skills.items()})
        all_skills.update({id: {"name": name, "category": "Specialist"} for id, name in specialist_skills.items()})
        all_skills.update({id: {"name": name, "category": "Special Abilities"} for id, name in special_abilities.items()})
        all_skills.update({id: {"name": name, "category": "Exploration"} for id, name in exploration_skills.items()})
        all_skills.update({id: {"name": name, "category": "Vehicle"} for id, name in vehicle_skills.items()})
        
        # Return skill info or default value
        if skill_id in all_skills:
            return all_skills[skill_id]
        else:
            return {"name": f"Unknown Skill ({skill_id})", "category": "Miscellaneous"}

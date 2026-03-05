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
        detail_window.geometry("683x384")
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
        
        # Define skill categories based on actual game skills
        
        # RDA Combat Enhancement Skills
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
        
        # RDA Defensive/Support Skills
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
        
        # RDA Mobility/Utility Skills
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
        }
        
        # Na'vi Combat Skills
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
        
        # Na'vi Support/Healing Skills
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
        
        # Na'vi Defensive Skills
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
        
        # Na'vi Mobility Skills
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
        }
        
        # Special Effects and Status Skills (from additional RDA skills)
        special_effects = {
            "1588994160": "Effect_ScaledFire_060",
            "154070465": "Effect_ScaledFire_100",
            "3919303244": "Effect_SlingDart_Overtime",
            "929187032": "SolsDelight_Blind",
            "482995089": "Leucomelas_Blind",
            "2831657996": "Root10sec",
            "3149590643": "Poison_cloud",
            "1761588079": "HellfireWasp_slow",
        }
        
        # Invulnerability and Protection Effects
        protection_effects = {
            "707441961": "Invulnerable",
            "2901239959": "MP_CorpRespawnInvulnerability",
            "2149792658": "MP_NaviRespawnInvulnerability",
            "2120156884": "MP_CorpShield",
            "896499985": "MP_NaviShield",
        }
        
        # Multiplayer Hills/Zones
        mp_zones = {
            "2288728861": "MP_HillOfProtection_C",
            "4172838722": "MP_HillOfPower_C",
            "2248739839": "MP_HillOfPower_N",
            "4141500320": "MP_HillOfProtection_N",
            "3605504349": "MP_HillOfRejuvenation_C",
            "2824265184": "MP_HillOfRejuvenation_N",
        }
        
        # Multiplayer Special Effects
        mp_effects = {
            "699117554": "MP_NAVI_Effect_MythicArchery",
            "3130830861": "MP_CORP_Effect_ArmorPiercing",
        }
        
        # Enemy AI Skills
        enemy_skills = {
            "1298333286": "EnemyCSS_3A_1",
            "3072205389": "EnemyNPG_2A_4",
            "1147345197": "EnemyNME_3A_4",
            "2779483555": "EnemyNPG_1A_4",
            "1887679822": "Enemy_NWM_2A",
            "651760328": "Enemy_NWM_4A",
            "3548279530": "EnemyNBD_1A_4",
        }
        
        # Creature/Animal Skills
        creature_skills = {
            "138960729": "Enemy_Viperwolf_EliteWasp",
            "1849804230": "Alpha_Viperwolf",
            "1785634812": "Viperwolf_Berzerk",
            "3490889542": "Viperwolf_Heal_LVL9_13",
            "62547143": "Viperwolf_Heal_LVL1_4",
            "218464304": "Viperwolf_Heal_LVL5_8",
            "1745871194": "Viperwolf_Camouflage",
            "3305111690": "Viperwolf_Bite",
            "1533394898": "Enemy_Summon_BlackViperwolf",
            "895550929": "Enemy_Summon_Viperwolf_Galactonotus",
            "480060929": "Hexapede",
        }
        
        # Hammerhead/Boss Skills
        boss_skills = {
            "1906639931": "Hammerhead_Lvl5To8_AttackWarning",
            "771604749": "Hammerhead_Lvl9To13_AttackWarning",
            "2932769824": "Hammerhead_Lvl5To8_AttackWarning_LowHealth",
            "1073248985": "Hammerhead_Lvl1To4_AttackWarning",
            "1539660776": "Hammerhead_Lvl9To13_AttackWarning_LowHealth",
            "2122270851": "ScarerShockWave",
        }
        
        # Environmental/Fear Effects
        environmental_effects = {
            "1987225269": "OxygenPod_Fear",
            "1774875854": "Amp_JumpFear",
        }
        
        # Unknown/Unclassified Skills
        unknown_skills = {
            "4221139584": "RDA Skill 4221139584",
            "3396941018": "RDA Skill 3396941018",
        }
        
        # Combine all categories into a master dictionary
        all_skills = {
            **rda_combat_enhancement,
            **rda_defensive,
            **rda_mobility,
            **rda_vehicles,
            **navi_combat,
            **navi_support,
            **navi_defensive,
            **navi_mobility,
            **navi_mounts,
            **special_effects,
            **protection_effects,
            **mp_zones,
            **mp_effects,
            **enemy_skills,
            **creature_skills,
            **boss_skills,
            **environmental_effects,
            **unknown_skills,
        }
        
        # Determine category for the skill
        category = "Unknown"
        if skill_id in rda_combat_enhancement:
            category = "RDA Combat Enhancement"
        elif skill_id in rda_defensive:
            category = "RDA Defensive/Support"
        elif skill_id in rda_mobility:
            category = "RDA Mobility/Utility"
        elif skill_id in rda_vehicles:
            category = "RDA Vehicle Spawn"
        elif skill_id in navi_combat:
            category = "Na'vi Combat"
        elif skill_id in navi_support:
            category = "Na'vi Support/Healing"
        elif skill_id in navi_defensive:
            category = "Na'vi Defensive"
        elif skill_id in navi_mobility:
            category = "Na'vi Mobility"
        elif skill_id in navi_mounts:
            category = "Na'vi Mount Spawn"
        elif skill_id in special_effects:
            category = "Special Effects"
        elif skill_id in protection_effects:
            category = "Protection Effects"
        elif skill_id in mp_zones:
            category = "Multiplayer Zones"
        elif skill_id in mp_effects:
            category = "Multiplayer Effects"
        elif skill_id in enemy_skills:
            category = "Enemy AI"
        elif skill_id in creature_skills:
            category = "Creature Skills"
        elif skill_id in boss_skills:
            category = "Boss Skills"
        elif skill_id in environmental_effects:
            category = "Environmental Effects"
        
        # Return skill info
        skill_name = all_skills.get(skill_id, f"Unknown Skill {skill_id}")
        
        return {
            "id": skill_id,
            "name": skill_name,
            "category": category
        }
import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
from typing import Dict, Optional
import logging
from custom_messagebox import MessageBoxManager, show_info, show_error, show_warning, ask_question, ask_ok_cancel, show_success


class SoundsManager:
    def __init__(self, parent: ttk.Frame, main_window):
        self.logger = logging.getLogger('SoundsManager')
        self.logger.debug("Initializing Modern SoundsManager")
        self.parent = parent
        self.main_window = main_window
        self.sound_data = {}
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
        
        # Main content area (sounds list)
        self.create_main_content(content_frame)

    def create_header_section(self):
        """Create the header with title and search"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title and subtitle
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = ttk.Label(title_frame, text="🔊 Sound Knowledge", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="Discover and explore the rich audio landscape of Pandora", 
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
        
        # === DISCOVERY OVERVIEW ===
        overview_frame = ttk.LabelFrame(sidebar_frame, text="🎵 Discovery Overview", padding=15)
        overview_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Large discovery count display
        self.discovery_display = ttk.Frame(overview_frame)
        self.discovery_display.pack(fill=tk.X, pady=(0, 10))
        
        self.sounds_count = ttk.Label(
            self.discovery_display, 
            text="0", 
            font=('Segoe UI', 24, 'bold'),
            foreground='#2e7d32'
        )
        self.sounds_count.pack()
        
        ttk.Label(self.discovery_display, text="Sounds Discovered", font=('Segoe UI', 10)).pack()
                
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
        """Create the main content area with sounds list"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Sounds list header
        list_header = ttk.Frame(main_frame)
        list_header.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(list_header, text="🔊 Discovered Sounds", 
                 font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)
        
        # Category legend
        legend_frame = ttk.Frame(list_header)
        legend_frame.pack(side=tk.RIGHT)
        
        legend_items = [("🌿", "Environmental"), ("🐾", "Creatures"), ("🤖", "Technology"), ("👥", "Na'vi")]
        for icon, desc in legend_items:
            ttk.Label(legend_frame, text=f"{icon} {desc}", font=('Segoe UI', 8)).pack(side=tk.LEFT, padx=3)
        
        # Enhanced sounds treeview
        tree_container = ttk.Frame(main_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure columns for better information display
        columns = ("category", "name", "description", "id", "details")
        self.sounds_tree = ttk.Treeview(tree_container, columns=columns, show="headings", 
                                       selectmode="extended", height=20)
        
        # Configure headers
        headers = {
            "category": ("🏷️", 80, "center"),
            "name": ("🔊 Sound Name", 250, "w"),
            "description": ("📝 Description", 300, "w"),
            "id": ("🆔 ID", 100, "center"),
            "details": ("ℹ️ Info", 100, "center")
        }
        
        for col, (text, width, anchor) in headers.items():
            self.sounds_tree.heading(col, text=text)
            self.sounds_tree.column(col, width=width, anchor=anchor, minwidth=50)
        
        # Enhanced color scheme
        self.setup_tree_styles()
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.sounds_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.sounds_tree.xview)
        self.sounds_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.sounds_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.sounds_tree.bind("<Double-1>", self._on_sound_double_click)
        self.sounds_tree.bind("<Button-3>", self._show_sound_context_menu)

    def setup_tree_styles(self):
        """Configure tree styling with modern color scheme"""
        self.sounds_tree.tag_configure('environmental', 
                                      background='#e8f5e8', 
                                      foreground="#00ff0d")
        self.sounds_tree.tag_configure('creatures', 
                                      background='#fff3e0', 
                                      foreground="#ff7300")
        self.sounds_tree.tag_configure('technology', 
                                      background='#e3f2fd', 
                                      foreground="#0077ff")
        self.sounds_tree.tag_configure('navi', 
                                      background='#f3e5f5', 
                                      foreground="#b300ff")
        self.sounds_tree.tag_configure('special', 
                                      background='#fff8e1', 
                                      foreground="#ff7700")

    def load_sounds(self, tree: ET.ElementTree) -> None:
        """Load sounds data with modern interface"""
        self.logger.debug("Loading sounds with modern interface")
        try:
            # Clear existing data
            self.sound_data = {}
            
            # Clear existing items in treeview
            for item in self.sounds_tree.get_children():
                self.sounds_tree.delete(item)
            
            # Find all sound elements
            sounds = tree.findall(".//SoundKnowledge/Sound")
            self.logger.debug(f"Found {len(sounds)} sounds")
            
            # Sort sounds by ID for consistent display
            sounds_sorted = sorted(sounds, key=lambda x: x.get("ID", "0"))
            
            # Process each sound
            for sound in sounds_sorted:
                try:
                    sound_id = sound.get("ID", "")
                    sound_name, description = self._get_sound_info(sound_id)
                    category = self._get_sound_category(sound_name, description)
                    
                    # Store sound data
                    self.sound_data[sound_id] = {
                        'name': sound_name,
                        'description': description,
                        'category': category
                    }
                    
                    # Determine category icon and styling
                    category_icon, tag = self._get_sound_display_info(category)
                    
                    # Insert into tree
                    self.sounds_tree.insert("", tk.END, values=(
                        category_icon,
                        sound_name,
                        description,
                        sound_id,
                        "View Details"
                    ), tags=(tag,))
                    
                except Exception as e:
                    self.logger.error(f"Error processing sound {sound_id}: {str(e)}", exc_info=True)
            
            # Update all displays
            self._update_all_displays()
            
            self.logger.debug("Sounds loaded successfully with modern interface")
            
        except Exception as e:
            self.logger.error(f"Error loading sounds: {str(e)}", exc_info=True)
            raise

    def _get_sound_category(self, sound_name, description):
        """Determine sound category based on name and description"""
        name_lower = sound_name.lower()
        desc_lower = description.lower()
        
        # Environmental sounds
        if any(keyword in name_lower or keyword in desc_lower 
               for keyword in ['forest', 'water', 'wind', 'rain', 'cave', 'thunder', 'waterfall', 'ambience', 'environmental']):
            return "Environmental"
        
        # Creature sounds
        elif any(keyword in name_lower or keyword in desc_lower 
                 for keyword in ['viperwolf', 'banshee', 'thanator', 'creature', 'roar', 'call', 'wings', 'movement', 'stampede']):
            return "Creatures"
        
        # Technology sounds
        elif any(keyword in name_lower or keyword in desc_lower 
                 for keyword in ['amp suit', 'gunfire', 'aircraft', 'rda', 'computer', 'radio', 'machinery', 'vehicle', 'technology']):
            return "Technology"
        
        # Na'vi sounds
        elif any(keyword in name_lower or keyword in desc_lower 
                 for keyword in ['na\'vi', 'tsaheylu', 'ceremonial', 'tribal', 'prayer', 'bow', 'ikran', 'pa\'li']):
            return "Na'vi"
        
        # Special/Mission sounds
        elif any(keyword in name_lower or keyword in desc_lower 
                 for keyword in ['mission', 'objective', 'complete', 'failed']):
            return "Special"
        
        else:
            return "Other"

    def _get_sound_display_info(self, category):
        """Get display icon and tag for a sound category"""
        category_mapping = {
            "Environmental": ("🌿", "environmental"),
            "Creatures": ("🐾", "creatures"),
            "Technology": ("🤖", "technology"),
            "Na'vi": ("👥", "navi"),
            "Special": ("🎵", "special"),
            "Other": ("❓", "environmental")
        }
        
        return category_mapping.get(category, ("❓", "environmental"))

    def _update_all_displays(self):
        """Update all display elements"""
        total_sounds = len(self.sound_data)
        
        # Update main discovery count
        self.sounds_count.config(text=str(total_sounds))
        
        # Count by category
        category_counts = {}
        for sound_data in self.sound_data.values():
            category = sound_data['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
    def _apply_filter(self, event=None):
        """Apply search and filter to the sounds list"""
        filter_value = self.filter_var.get()
        search_text = self.search_var.get().lower()
        
        # Clear and repopulate tree
        for item in self.sounds_tree.get_children():
            self.sounds_tree.delete(item)
        
        # Re-add filtered items
        for sound_id, sound_data in self.sound_data.items():
            if self._should_show_sound(sound_id, sound_data, filter_value, search_text):
                category = sound_data['category']
                category_icon, tag = self._get_sound_display_info(category)
                
                self.sounds_tree.insert("", tk.END, values=(
                    category_icon,
                    sound_data['name'],
                    sound_data['description'],
                    sound_id,
                    "View Details"
                ), tags=(tag,))

    def _should_show_sound(self, sound_id, sound_data, filter_value, search_text):
        """Determine if sound should be shown based on filters"""
        name = sound_data['name']
        description = sound_data['description']
        category = sound_data['category']
        
        # Apply filter
        if filter_value == "🌿 Environmental" and category != "Environmental":
            return False
        elif filter_value == "🐾 Creatures" and category != "Creatures":
            return False
        elif filter_value == "🤖 Technology" and category != "Technology":
            return False
        elif filter_value == "👥 Na'vi" and category != "Na'vi":
            return False
        elif filter_value == "🎵 Special" and category != "Special":
            return False
        
        # Apply search
        if search_text and search_text not in name.lower() and search_text not in description.lower() and search_text not in sound_id.lower():
            return False
        
        return True

    def _on_sound_double_click(self, event):
        """Handle double-click on sound in list"""
        item = self.sounds_tree.selection()[0] if self.sounds_tree.selection() else None
        if item:
            values = self.sounds_tree.item(item, "values")
            self._show_sound_details(values[1])  # sound name

    def _show_sound_context_menu(self, event):
        """Show context menu for sounds"""
        if self.sounds_tree.selection():
            context_menu = tk.Menu(self.sounds_tree, tearoff=0)
            context_menu.add_command(label="📋 Copy Sound ID", command=self._copy_sound_id)
            context_menu.add_command(label="ℹ️ Show Details", command=self._show_selected_sound_details)
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()

    def _show_selected_sound_details(self):
        """Show details for selected sound"""
        selected = self.sounds_tree.selection()
        if selected:
            values = self.sounds_tree.item(selected[0], "values")
            self._show_sound_details(values[1])  # sound name

    def _copy_sound_id(self):
        """Copy selected sound ID to clipboard"""
        selected = self.sounds_tree.selection()
        if selected:
            values = self.sounds_tree.item(selected[0], "values")
            sound_id = values[3]  # ID is at index 3
            self.parent.clipboard_clear()
            self.parent.clipboard_append(sound_id)
            show_info("Copied", f"📋 Sound ID copied to clipboard:\n{sound_id}")

    def _show_sound_details(self, sound_name):
        """Show detailed information about a sound"""
        # Find the sound data
        sound_data = None
        sound_id = None
        for sid, data in self.sound_data.items():
            if data['name'] == sound_name:
                sound_data = data
                sound_id = sid
                break
        
        if not sound_data:
            show_warning("Warning", "Sound data not found")
            return
        
        # Create detailed sound information dialog
        detail_window = tk.Toplevel(self.parent)
        detail_window.title(f"Sound Details - {sound_name}")
        detail_window.geometry("1600x800")
        detail_window.resizable(True, True)
        
        # Main frame with padding
        main_frame = ttk.Frame(detail_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        category_icon, _ = self._get_sound_display_info(sound_data['category'])
        title_label = ttk.Label(main_frame, text=f"{category_icon} {sound_name}", 
                            font=('Segoe UI', 14, 'bold'))
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Details frame
        details_frame = ttk.LabelFrame(main_frame, text="Sound Information", padding=15)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create details text widget
        details_text = tk.Text(details_frame, wrap=tk.WORD, font=('Consolas', 10), 
                            height=18, state=tk.NORMAL)
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=details_text.yview)
        details_text.configure(yscrollcommand=scrollbar.set)
        
        # Format sound details
        info_text = f"""🔊 Sound Name: {sound_name}
    🏷️ Category: {sound_data['category']}
    🆔 Sound ID: {sound_id}

    📝 Description:
    {'=' * 40}
    {sound_data['description']}

    🎵 Audio Context:
    {'=' * 40}
    {self._get_audio_context(sound_data['category'], sound_name)}

    🔧 Technical Details:
    {'=' * 40}
    Sound ID: {sound_id}
    Category: {sound_data['category']}
    Discovery Status: Discovered
    """
        
        details_text.insert(tk.END, info_text)
        details_text.config(state=tk.DISABLED)
        
        details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="📋 Copy ID", 
                command=lambda: self._copy_to_clipboard(sound_id)).pack(side=tk.LEFT, padx=(0, 10))
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

    def _get_audio_context(self, category, sound_name):
        """Get contextual information about where/when this sound occurs"""
        contexts = {
            "Environmental": "This environmental sound contributes to the immersive atmosphere of Pandora's diverse ecosystems. You'll encounter it while exploring the natural world.",
            "Creatures": "This creature sound is part of Pandora's rich wildlife audio. Listen for it when encountering or observing the various creatures that inhabit the moon.",
            "Technology": "This technological sound is associated with RDA equipment and machinery. You'll hear it in industrial areas or when interacting with human technology.",
            "Na'vi": "This Na'vi sound is part of the indigenous culture of Pandora. It relates to Na'vi language, ceremonies, or traditional practices.",
            "Special": "This special sound is triggered during specific game events, missions, or important moments in your journey."
        }
        
        return contexts.get(category, "This sound is part of the rich audio landscape that makes Pandora come alive.")

    def save_sound_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        """Sound data is view-only, return unchanged tree"""
        self.logger.debug("Sound data is view-only, no changes to save")
        return tree
    
    def _get_sound_info(self, sound_id):
        """Map sound ID to a name and description"""
        
        # Map of sound IDs to names and descriptions
        sound_info = {
            # Environmental sounds
            "759101": ("Forest Ambience", "Natural forest sounds of Pandora"),
            "759321": ("Water Flowing", "Sound of water running in streams or rivers"),
            "758777": ("Wind Through Trees", "Wind blowing through Pandoran flora"),
            "758744": ("Rain Sounds", "Rainfall on Pandora's forest canopy"),
            "758969": ("Cave Echo", "Ambient echo sounds in cave systems"),
            "759305": ("Thunder", "Sound of thunderstorms on Pandora"),
            "758961": ("Bioluminescent Activation", "Sound of plants lighting up at night"),
            "759329": ("Waterfall", "Sound of water falling from height"),
            
            # Creature sounds
            "759269": ("Viperwolf Call", "Hunting call of the viperwolf pack"),
            "758861": ("Hammerhead Stampede", "Sound of stampeding hammerhead titanotheres"),
            "758681": ("Thanator Roar", "Threatening roar of a thanator"),
            "759285": ("Banshee Screech", "Distinctive call of a mountain banshee"),
            "758773": ("Hexapede Movement", "Sounds of hexapede herds moving through foliage"),
            "758829": ("Stingbat Wings", "Sound of stingbat wings flapping"),
            "759141": ("Prolemuris Call", "Call of the prolemuris in the trees"),
            "758733": ("Sturmbeest Grunt", "Low grunting sound of a sturmbeest"),
            "758785": ("Direhorse Gallop", "Sound of a direhorse running"),
            "758805": ("Small Creature Movement", "Sounds of small Pandoran creatures"),
            
            # Technology sounds
            "758385": ("AMP Suit Activation", "Startup sequence of an AMP suit"),
            "759085": ("RDA Gunfire", "Sound of RDA weapons fire"),
            "759301": ("Aircraft Engine", "Sound of Samson or Scorpion engines"),
            "759081": ("Door Mechanism", "Sound of RDA facility doors opening/closing"),
            "759005": ("Computer Terminal", "Interface sounds from computer terminals"),
            "759261": ("Airlock Cycling", "Sound of an airlock pressurizing/depressurizing"),
            "759113": ("Radio Chatter", "RDA radio communications"),
            "758498": ("Vehicle Movement", "Sound of ground vehicles moving"),
            "758494": ("Machinery Operation", "Sound of mining or construction equipment"),
            "4294967295": ("System Sound", "Generic system or interface sound"),
            
            # Na'vi sounds
            "758925": ("Na'vi Language", "Phrases or words in the Na'vi language"),
            "759393": ("Na'vi Song", "Traditional Na'vi singing or chanting"),
            "758901": ("Bow String", "Sound of a Na'vi bow being fired"),
            "759389": ("Ceremonial Drums", "Na'vi ceremonial drumming"),
            "759357": ("Tsaheylu Connection", "Sound of forming neural connection"),
            "758993": ("Na'vi Hunting Call", "Hunting signals between Na'vi"),
            "759001": ("Pa'li Whistle", "Whistle to call a direhorse"),
            "758884": ("Ikran Call", "Sound used to call a banshee"),
            "759025": ("Tribal Celebration", "Sounds of Na'vi celebration"),
            "759377": ("Prayer Chant", "Eywa prayer chanting"),
            "759253": ("Fighting Stance", "Sound of Na'vi preparing for combat"),
            
            # Special mission sounds
            "1159811": ("Mission Objective", "Sound indicating a mission objective"),
            "1159825": ("Mission Complete", "Sound of mission completion"),
            "1159852": ("Mission Failed", "Sound indicating mission failure"),
        }
        
        # Return name and description if found, otherwise provide generic information
        if sound_id in sound_info:
            return sound_info[sound_id]
        else:
            return (f"Unknown Sound ({sound_id})", "No description available")

import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
from typing import Dict, Optional
import logging

class SkillsManager:
    def __init__(self, parent: ttk.Frame, main_window):
        self.logger = logging.getLogger('SkillsManager')
        self.logger.debug("Initializing SkillsManager")
        self.parent = parent
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self) -> None:
        # Create Skills Treeview that fills the entire parent space
        tree_frame = ttk.Frame(self.parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(tree_frame, text="Character Skills").pack()

        # Create Treeview with columns
        columns = ("ID", "Name", "Category", "Status")
        self.skills_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="extended"
        )

        # Configure columns
        self.skills_tree.heading("ID", text="Skill ID")
        self.skills_tree.heading("Name", text="Skill Name")
        self.skills_tree.heading("Category", text="Skill Category")
        self.skills_tree.heading("Status", text="Status")

        # Set column widths and alignment
        self.skills_tree.column("ID", width=120, anchor="w")
        self.skills_tree.column("Name", width=300, anchor="w")
        self.skills_tree.column("Category", width=150, anchor="w")
        self.skills_tree.column("Status", width=120, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.skills_tree.yview)
        self.skills_tree.configure(yscrollcommand=scrollbar.set)

        self.skills_tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configure tags for color-coding
        self.skills_tree.tag_configure('locked', foreground='#FF0000')   # Red
        self.skills_tree.tag_configure('unlocked', foreground='#00FF00')   # Green
        self.skills_tree.tag_configure('special', foreground='#FFA500')   # Orange

        # Statistics frame
        stats_frame = ttk.Frame(tree_frame)
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.skill_count_label = ttk.Label(stats_frame, text="Total skills unlocked: 0/0")
        self.skill_count_label.pack(side=tk.LEFT, padx=10)

    def load_skills(self, tree: ET.ElementTree) -> None:
        self.logger.debug("Loading skills")
        try:
            # Clear existing items
            for item in self.skills_tree.get_children():
                self.skills_tree.delete(item)
            
            # Find all skill elements in XML
            skills = tree.findall(".//AvatarSkillDB_Status/Skill")
            
            self.logger.debug(f"Found {len(skills)} skills")
            
            # Sort skills by category for consistent display
            skills_dict = {}
            for skill in skills:
                skill_id = skill.get("crc_id", "")
                locked_status = skill.get("eLocked", "0")
                
                skill_info = self._get_skill_info(skill_id)
                
                # Group by category
                category = skill_info["category"]
                if category not in skills_dict:
                    skills_dict[category] = []
                
                skills_dict[category].append({
                    "id": skill_id,
                    "name": skill_info["name"],
                    "category": category,
                    "locked": locked_status
                })
            
            # Add to treeview grouped by category
            unlocked_count = 0
            total_count = 0
            
            for category in sorted(skills_dict.keys()):
                # Sort skills within category by name
                category_skills = sorted(skills_dict[category], key=lambda x: x["name"])
                
                for skill in category_skills:
                    total_count += 1
                    
                    # Determine lock status text
                    if skill["locked"] == "0":
                        status = "Unlocked"
                        tag = "unlocked"
                        unlocked_count += 1
                    elif skill["locked"] == "2":
                        status = "Special"
                        tag = "special"
                        unlocked_count += 1  # Count special skills as unlocked
                    else:
                        status = "Locked"
                        tag = "locked"
                    
                    self.skills_tree.insert("", tk.END, values=(
                        skill["id"],
                        skill["name"],
                        skill["category"],
                        status
                    ), tags=(tag,))
            
            # Update statistics
            self.skill_count_label.config(text=f"Total skills unlocked: {unlocked_count}/{total_count}")
            
            self.logger.debug("Skills loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading skills: {str(e)}", exc_info=True)
            raise

    def save_skill_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        self.logger.debug("Skills are view-only, no changes to save")
        # Simply return the tree unchanged since this is view-only
        return tree
    
    def _get_skill_info(self, skill_id):
        """Map skill ID to name and category"""
        
        # Define skill categories
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

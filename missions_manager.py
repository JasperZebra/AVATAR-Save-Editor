import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
from typing import Dict, Optional
import logging

class MissionsManager:
    def __init__(self, parent: ttk.Frame, main_window):
        self.logger = logging.getLogger('MissionsManager')
        self.logger.debug("Initializing MissionsManager")
        self.parent = parent
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self) -> None:
        # Create Missions Treeview
        tree_frame = ttk.Frame(self.parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Label(tree_frame, text="Missions Status").pack()

        # Create Treeview with columns
        columns = ("ID", "Name", "Status", "Progress")
        self.missions_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="extended"
        )

        # Configure columns
        self.missions_tree.heading("ID", text="Mission ID")
        self.missions_tree.heading("Name", text="Name")
        self.missions_tree.heading("Status", text="Status")
        self.missions_tree.heading("Progress", text="Progress")

        # Set column widths and alignment
        self.missions_tree.column("ID", width=120, anchor="w")
        self.missions_tree.column("Name", width=450, anchor="w")
        self.missions_tree.column("Status", width=120, anchor="center")
        self.missions_tree.column("Progress", width=120, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.missions_tree.yview)
        self.missions_tree.configure(yscrollcommand=scrollbar.set)

        self.missions_tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configure tags for color-coding
        self.missions_tree.tag_configure('completed', foreground='#00FF00')      # Green
        self.missions_tree.tag_configure('in_progress', foreground='#FFA500')    # Orange
        self.missions_tree.tag_configure('not_started', foreground='#FF0000')    # Red

    def load_missions(self, tree: ET.ElementTree) -> None:
        self.logger.debug("Loading missions")
        try:
            # Clear existing items
            for item in self.missions_tree.get_children():
                self.missions_tree.delete(item)
            
            # Find all mission elements in XML
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
                    
                    # Get mission progress if in progress
                    progress = ""
                    if mission_type == "Mission_InProgress":
                        current_step = mission.get("iCurrentStepIndex", "0")
                        objective_count = len(mission.findall("Objective"))
                        if objective_count > 0:
                            # Count completed objectives
                            completed = sum(1 for obj in mission.findall("Objective") if obj.get("status", "0") == "1")
                            progress = f"{completed}/{objective_count}"
                        else:
                            progress = f"Step {current_step}"
                    elif mission_type == "Mission_Completed":
                        progress = "100%"
                    
                    # Get the mission name from our mapping or use a default
                    mission_name = self._get_mission_name(mission_id)
                    
                    # Format display values
                    formatted_id = mission_id
                    
                    # Get appropriate tag for status
                    status_tag = mission_type.lower().replace("mission_", "")
                    
                    self.missions_tree.insert("", tk.END, values=(
                        formatted_id,
                        mission_name,
                        status,
                        progress
                    ), tags=(status_tag,))
                    
                except Exception as e:
                    self.logger.error(f"Error processing mission {mission_id}: {str(e)}", exc_info=True)

            self.logger.debug("Missions loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading missions: {str(e)}", exc_info=True)
            raise

    def save_mission_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        self.logger.debug("Preserving mission data (no changes possible)")
        # Simply return the tree as is since we no longer allow edits
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
            "3869409139": "find mission name 2",
            "3872540424": "Remote Sensing Array",
            "3922369913": "Resource Extraction",
            "3941247737": "Vehicle Combat Training",
            "3949759279": "Specimen Transport",
            "3959508790": "Technology Demonstration",
            "4003944800": "Reconnaissance Mission",
            "4004743186": "Security Patrol",
            "4040272952": "Territorial Control",
            "4085556621": "Environmental Monitoring",
            "4156182083": "find mission name 1",
            "4214204955": "Biodiversity Survey",
            "4238570271": "Outpost Defense"
        }
        return mission_names.get(mission_id, f"Unknown Mission ({mission_id})")
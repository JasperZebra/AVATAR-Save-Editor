import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
import logging
from typing import Dict, Any

class NavigationManager:
    def __init__(self, parent: ttk.Frame, main_window):
        self.logger = logging.getLogger('NavigationManager')
        self.logger.debug("Initializing NavigationManager")
        self.parent = parent
        self.main_window = main_window
        self.selected_map_id = None
        self.checkpoint_data = {}  # Store checkpoint data
        self.setup_ui()

    def get_map_name(self, crc_id: str) -> str:
        """Convert map CRC ID to human-readable name."""
        map_names = {
            # Starting/Tutorial Areas
            "3409126972": "Tutorial Area",
            "238707229": "Training Grounds",
            "2292208788": "RDA Training Facility",
            
            # Major Areas
            "355473279": "Plains of Goliath",
            "615754132": "Crystal Fields",
            "1172651822": "Emerald Forest",
            "1847852653": "Torchwood Forest",
            "2171723794": "Swamps of Silence",
            "2587251285": "Northern Shelf",
            "2961077726": "Willow Glade",
            "3616200713": "Tantalus",
            
            # Special Areas
            "1057194188": "Pandoran Abyss",
            "2856892107": "Floating Mountains",
            "3822194552": "Sacred Grove",
            "1504064473": "Luminous Valley",
            
            # RDA Areas
            "2752812145": "RDA Main Base",
            "837458676": "RDA Research Station",
            "1771880106": "RDA Mining Site",
            
            # Combat Zones
            "470159002": "Battlefield Delta",
            "2216033045": "Combat Arena Alpha",
            "60855408": "War Zone Beta",
            
            # Wilderness Areas
            "3975313082": "Wild Plains",
            "2169212369": "Dense Jungle",
            "1578821154": "Mountain Pass",
            "1782610090": "Hidden Valley",
            
            # Cave Systems
            "1628184437": "Crystal Caverns",
            "1865345760": "Echo Caves",
            "3564339531": "Underground Network",
            
            # Water Areas
            "4294730242": "River Delta",
            "1741938656": "Great Lake",
            "2555792139": "Waterfall Basin",
            
            # Ancient Ruins
            "2353717556": "Ancient Temple",
            "2001468046": "Lost City",
            "3903502716": "Sacred Ruins",
            
            # Unique Biomes
            "3852438644": "Bioluminescent Forest",
            "2232107097": "Fungal Grove",
            "2185381138": "Living Mountain",
            
            # Na'vi Areas
            "2672591835": "Na'vi Village",
            "105239137": "Tree of Souls",
            "3575765971": "Hometree",
            
            # Border Regions
            "902032528": "Northern Border",
            "948986278": "Eastern Frontier",
            "1437051617": "Southern Boundary",
            
            # Special Mission Areas
            "2427499480": "Mission Zone Alpha",
            "2509501782": "Mission Zone Beta",
            "4220570174": "Mission Zone Gamma",
            
            # Resource Areas
            "408444403": "Unobtanium Mine",
            "1846881984": "Resource Valley",
            "4168272830": "Mining Complex"
        }

        crc_id = str(crc_id)

        return map_names.get(crc_id, "Unknown Location")

    def get_checkpoint_info(self, entity_id: str) -> Dict[str, str]:
        """Get checkpoint information including its map affiliation."""
        checkpoint_data = {
            # Tutorial Area (3409126972)
            "2060116264721850117": {
                "name": "Tutorial - Starting Area",
                "map_id": "3409126972",
            },
            "2061389907802198293": {
                "name": "Tutorial - Training Hub",
                "map_id": "3409126972",
            },
            "2061388794472435963": {
                "name": "Tutorial - Practice Zone",
                "map_id": "3409126972",
            },
            "2057296791262466370": {
                "name": "Main Hub - Central Plaza",
                "map_id": "3409126972",
            },
            
            # Plains of Goliath (355473279)
            "2063890367165497967": {
                "name": "Goliath Plains - Northern Gate",
                "map_id": "355473279",
            },
            "2063890404131996273": {
                "name": "Goliath Plains - Eastern Watchtower",
                "map_id": "355473279",
            },
            "2063890442725884531": {
                "name": "Goliath Plains - Southern Pass",
                "map_id": "355473279",
            },
            
            # Crystal Fields (615754132)
            "2063225208807896602": {
                "name": "Crystal Fields - Main Entry",
                "map_id": "615754132",
            },
            "2063225296324146726": {
                "name": "Crystal Fields - Northern Path",
                "map_id": "615754132",
            },
            "2063225230284830238": {
                "name": "Crystal Fields - Eastern Trail",
                "map_id": "615754132",
            },
            
            # Emerald Forest (1172651822)
            "2061124389803400623": {
                "name": "Emerald Forest - Main Gate",
                "map_id": "1172651822",
            },
            "2061569470131871197": {
                "name": "Emerald Forest - River Crossing",
                "map_id": "1172651822",
            },
            "2061569240252554713": {
                "name": "Emerald Forest - Ancient Ruins",
                "map_id": "1172651822",
            },
            
            # Swamps of Silence (2171723794)
            "2062770733236364382": {
                "name": "Swamps - Entry Point",
                "map_id": "2171723794",
            },
            "2063061201079766213": {
                "name": "Swamps - Foggy Basin",
                "map_id": "2171723794",
            },
            "2061581362344755673": {
                "name": "Swamps - Dark Waters",
                "map_id": "2171723794",
            },
            
            # Northern Shelf (2587251285)
            "2061609766924326233": {
                "name": "Northern Shelf - Ice Gate",
                "map_id": "2587251285",
            },
            "2061609796162819423": {
                "name": "Northern Shelf - Frozen Lake",
                "map_id": "2587251285",
            },
            
            # RDA Main Base (2752812145)
            "2063836717342796597": {
                "name": "RDA Base - Main Entrance",
                "map_id": "2752812145",
            },
            "2063836667988421427": {
                "name": "RDA Base - Research Wing",
                "map_id": "2752812145",
            },
            
            # Combat Arena Alpha (2216033045)
            "2063730009236843301": {
                "name": "Arena - Entry Gate",
                "map_id": "2216033045",
            },
            "2063730056859441381": {
                "name": "Arena - Training Ground",
                "map_id": "2216033045",
            },
            
            # Mountain Pass (1578821154)
            "2059745456927278554": {
                "name": "Mountain Pass - Main Trail",
                "map_id": "1578821154",
            },
            "2062869015113505758": {
                "name": "Mountain Pass - Summit Path",
                "map_id": "1578821154",
            },
            
            # Crystal Caverns (1628184437)
            "2062052285757789593": {
                "name": "Crystal Caverns - Main Entrance",
                "map_id": "1628184437",
            },
            "2062815140052469567": {
                "name": "Crystal Caverns - Deep Chamber",
                "map_id": "1628184437",
            },
            
            # Hidden Valley (1782610090)
            "2060616625937189740": {
                "name": "Hidden Valley - Entry",
                "map_id": "1782610090",
            },
            "2060352164210935071": {
                "name": "Hidden Valley - River Fork",
                "map_id": "1782610090",
            },
            
            # Willow Glade (2961077726)
            "2061885698497063834": {
                "name": "Willow Glade - Northern Entry",
                "map_id": "2961077726",
            },
            "2061885628466867046": {
                "name": "Willow Glade - Eastern Path",
                "map_id": "2961077726",
            },
            
            # Floating Mountains (2856892107)
            "2062954847830811819": {
                "name": "Floating Mountains - Base Camp",
                "map_id": "2856892107",
            },
            "2063157964081997981": {
                "name": "Floating Mountains - Sky Bridge",
                "map_id": "2856892107",
            },
            
            # Na'vi Village (2672591835)
            "2062768901780943443": {
                "name": "Na'vi Village - Main Entry",
                "map_id": "2672591835",
            },
            "2062768512323039696": {
                "name": "Na'vi Village - Central Plaza",
                "map_id": "2672591835",
            },
            
            # Tree of Souls (105239137)
            "2061196708385132749": {
                "name": "Tree of Souls - Sacred Path",
                "map_id": "105239137",
            },
            "2061306531374174575": {
                "name": "Tree of Souls - Ritual Ground",
                "map_id": "105239137",
            },
            
            # Hometree Region (3575765971)
            "2062745068309062815": {
                "name": "Hometree - Main Entrance",
                "map_id": "3575765971",
            },
            "2062745288577131707": {
                "name": "Hometree - Lower Branches",
                "map_id": "3575765971",
            },
            "2062745318545433791": {
                "name": "Hometree - Middle Level",
                "map_id": "3575765971",
            },
            "2062745342868202691": {
                "name": "Hometree - Upper Canopy",
                "map_id": "3575765971",
            },
            "2062745337505785025": {
                "name": "Hometree - Gathering Place",
                "map_id": "3575765971",
            },

            # River Delta (4294730242)
            "2063454085335492631": {
                "name": "River Delta - Northern Bank",
                "map_id": "4294730242",
            },
            "2063454047653865493": {
                "name": "River Delta - Eastern Shore",
                "map_id": "4294730242",
            },
            "2063453991215310863": {
                "name": "River Delta - Southern Waters",
                "map_id": "4294730242",
            },

            # Unobtanium Mine (408444403)
            "2063064930893955202": {
                "name": "Mining Site - Main Entrance",
                "map_id": "408444403",
            },
            "2063065105890803864": {
                "name": "Mining Site - Processing Area",
                "map_id": "408444403",
            },

            # Sacred Grove (3822194552)
            "2060517411469146821": {
                "name": "Sacred Grove - Entry Path",
                "map_id": "3822194552",
            },
            "2060517422401600199": {
                "name": "Sacred Grove - Ancient Circle",
                "map_id": "3822194552",
            },
            "2060517449433889487": {
                "name": "Sacred Grove - Eastern Shrine",
                "map_id": "3822194552",
            },
            "2060517440219003597": {
                "name": "Sacred Grove - Western Shrine",
                "map_id": "3822194552",
            },
            "2060517436565764811": {
                "name": "Sacred Grove - Central Temple",
                "map_id": "3822194552",
            },

            # Ancient Temple (2353717556)
            "2062768819748745808": {
                "name": "Ancient Temple - Main Gate",
                "map_id": "2353717556",
            },
            "2062768807688024652": {
                "name": "Ancient Temple - Inner Sanctum",
                "map_id": "2353717556",
            },
            "2062768811337069134": {
                "name": "Ancient Temple - Sacred Hall",
                "map_id": "2353717556",
            },

            # Bioluminescent Forest (3852438644)
            "2061885518102145876": {
                "name": "Luminous Forest - Entry Trail",
                "map_id": "3852438644",
            },
            "2061885907411151810": {
                "name": "Luminous Forest - Glowing Grove",
                "map_id": "3852438644",
            },
            "2061885951891745738": {
                "name": "Luminous Forest - Light Pool",
                "map_id": "3852438644",
            },
            "2061885467411884878": {
                "name": "Luminous Forest - Crystal Path",
                "map_id": "3852438644",
            },

            # Mission Zones
            "2063418806551707828": {
                "name": "Mission Zone Alpha - Entry Point",
                "map_id": "2427499480",
            },
            "2063419638657582422": {
                "name": "Mission Zone Alpha - Checkpoint 1",
                "map_id": "2427499480",
            },
            "2063419660094670168": {
                "name": "Mission Zone Alpha - Checkpoint 2",
                "map_id": "2427499480",
            },

            # Underground Network (3564339531)
            "2062814673276764322": {
                "name": "Underground - Main Entry",
                "map_id": "3564339531",
            },
            "2062814137014026388": {
                "name": "Underground - Deep Cavern",
                "map_id": "3564339531",
            },

            # Dense Jungle (2169212369)
            "2061473064314471333": {
                "name": "Dense Jungle - Entry Path",
                "map_id": "2169212369",
            },
            "2061473031982678938": {
                "name": "Dense Jungle - Central Grove",
                "map_id": "2169212369",
            },

            # Wild Plains (3975313082)
            "2060879351624243905": {
                "name": "Wild Plains - Northern Post",
                "map_id": "3975313082",
            },
            "2060879289322052283": {
                "name": "Wild Plains - Eastern Watch",
                "map_id": "3975313082",
            },
            "2060879344957397695": {
                "name": "Wild Plains - Southern Gate",
                "map_id": "3975313082",
            },
            "2060879338785479357": {
                "name": "Wild Plains - Western Trail",
                "map_id": "3975313082",
            },

            # RDA Research Station (837458676)
            "2063890765857161885": {
                "name": "Research Station - Entry",
                "map_id": "837458676",
            },
            "2063890485352596085": {
                "name": "Research Station - Lab Wing",
                "map_id": "837458676",
            },
            "2063890530888057465": {
                "name": "Research Station - Testing Area",
                "map_id": "837458676",
            },

            # Fungal Grove (2232107097)
            "2062038237681034293": {
                "name": "Fungal Grove - Entry Path",
                "map_id": "2232107097",
            },
            "2062038193322075183": {
                "name": "Fungal Grove - Spore Fields",
                "map_id": "2232107097",
            },
            "2062038088206525481": {
                "name": "Fungal Grove - Mushroom Forest",
                "map_id": "2232107097",
            },

            # Waterfall Basin (2555792139)
            "2059552004323153911": {
                "name": "Waterfall Basin - Overlook",
                "map_id": "2555792139",
            },
            "2059552009758971897": {
                "name": "Waterfall Basin - Lower Pool",
                "map_id": "2555792139",
            },

            # Echo Caves (1865345760)
            "2062329655181967400": {
                "name": "Echo Caves - Entry Chamber",
                "map_id": "1865345760",
            },
            "2062329647546236966": {
                "name": "Echo Caves - Resonance Hall",
                "map_id": "1865345760",
            },

            # Northern Border (902032528)
            "2063890709145977489": {
                "name": "Northern Border - Outpost 1",
                "map_id": "902032528",
            },
            "2063890711656268435": {
                "name": "Northern Border - Guard Tower",
                "map_id": "902032528",
            },
            "2063890736396370585": {
                "name": "Northern Border - Patrol Point",
                "map_id": "902032528",
            },

            # Eastern Frontier (948986278)
            "2063890514400248439": {
                "name": "Eastern Frontier - Gateway",
                "map_id": "948986278",
            },
            "2063890680979128973": {
                "name": "Eastern Frontier - Lookout Post",
                "map_id": "948986278",
            },
            "2063890672626172555": {
                "name": "Eastern Frontier - Border Camp",
                "map_id": "948986278",
            },

            # Living Mountain (2185381138)
            "2062470237787266747": {
                "name": "Living Mountain - Base Camp",
                "map_id": "2185381138",
            },
            "2062479561219648157": {
                "name": "Living Mountain - Mid Ascent",
                "map_id": "2185381138",
            },
            "2063214155187358331": {
                "name": "Living Mountain - Summit Path",
                "map_id": "2185381138",
            },

            # Mission Zone Beta (2509501782)
            "2059843989489583521": {
                "name": "Mission Beta - Entry Point",
                "map_id": "2509501782",
            },
            "2059844269224500056": {
                "name": "Mission Beta - Checkpoint 1",
                "map_id": "2509501782",
            },
            "2059844796586922762": {
                "name": "Mission Beta - Checkpoint 2",
                "map_id": "2509501782",
            },
            "2059844833790399244": {
                "name": "Mission Beta - Final Point",
                "map_id": "2509501782",
            },

            # Resource Valley (1846881984)
            "2061182397593951307": {
                "name": "Resource Valley - Main Gate",
                "map_id": "1846881984",
            },
            "2060879356523190979": {
                "name": "Resource Valley - Processing Hub",
                "map_id": "1846881984",
            },
            "2060908290688163089": {
                "name": "Resource Valley - Storage Area",
                "map_id": "1846881984",
            },

            # Great Lake (1741938656)
            "2063157751002966171": {
                "name": "Great Lake - Shore Post",
                "map_id": "1741938656",
            },
            "2063283567732994008": {
                "name": "Great Lake - Fishing Camp",
                "map_id": "1741938656",
            },
            "2063322845584307783": {
                "name": "Great Lake - Western Bay",
                "map_id": "1741938656",
            },

            # Lost City (2001468046)
            "2061957523254018858": {
                "name": "Lost City - Ancient Gate",
                "map_id": "2001468046",
            },
            "2062050614088565950": {
                "name": "Lost City - Ruined Plaza",
                "map_id": "2001468046",
            },
            "2061306501082911085": {
                "name": "Lost City - Temple District",
                "map_id": "2001468046",
            },

            # Southern Boundary (1437051617)
            "2063890653034578567": {
                "name": "Southern Border - Checkpoint 1",
                "map_id": "1437051617",
            },
            "2063890646896214661": {
                "name": "Southern Border - Watch Tower",
                "map_id": "1437051617",
            },
            "2063890729117155991": {
                "name": "Southern Border - Patrol Base",
                "map_id": "1437051617",
            },

            # Training Grounds (238707229)
            "2061389567914676477": {
                "name": "Training Grounds - Entry",
                "map_id": "238707229",
            },
            "2061389859473330451": {
                "name": "Training Grounds - Combat Ring",
                "map_id": "238707229",
            },
            "2061389670891131143": {
                "name": "Training Grounds - Practice Area",
                "map_id": "238707229",
            },

            # Mining Complex (4168272830)
            "2059730249146434735": {
                "name": "Mining Complex - Main Entry",
                "map_id": "4168272830",
            },
            "2059731526255378965": {
                "name": "Mining Complex - Processing Plant",
                "map_id": "4168272830",
            },
            "2061790365058335271": {
                "name": "Mining Complex - Storage Depot",
                "map_id": "4168272830",
            },

            # RDA Training Facility (2292208788)
            "2061600119412753079": {
                "name": "RDA Training - Main Entry",
                "map_id": "2292208788",
            },
            "2061665967013888222": {
                "name": "RDA Training - Simulation Room",
                "map_id": "2292208788",
            },
            "2061389952702222619": {
                "name": "RDA Training - Equipment Bay",
                "map_id": "2292208788",
            },

            # Mission Zone Gamma (4220570174)
            "2063020023548489853": {
                "name": "Mission Gamma - Entry Point",
                "map_id": "4220570174",
            },
            "2061389919418323223": {
                "name": "Mission Gamma - Forward Base",
                "map_id": "4220570174",
            },
            "2061389938504503577": {
                "name": "Mission Gamma - Objective Site",
                "map_id": "4220570174",
            },

            # Pandoran Abyss (1057194188)
            "2057782701137599908": {
                "name": "Pandoran Abyss - Entry Point",
                "map_id": "1057194188",
            },
            "2062344321710950546": {
                "name": "Pandoran Abyss - Dark Descent",
                "map_id": "1057194188",
            },
            "2063174850135990353": {
                "name": "Pandoran Abyss - Lower Cavern",
                "map_id": "1057194188",
            },

            # Torchwood Forest (1847852653)
            "2061858426985651121": {
                "name": "Torchwood - Forest Edge",
                "map_id": "1847852653",
            },
            "2061858353415461791": {
                "name": "Torchwood - Ancient Tree",
                "map_id": "1847852653",
            },
            "2061858452658985907": {
                "name": "Torchwood - Deep Woods",
                "map_id": "1847852653",
            },

            # Additional RDA Mining Site (1771880106)
            "2062176369225243689": {
                "name": "RDA Mining Site - Main Gate",
                "map_id": "1771880106",
            },
            "2061472952852939662": {
                "name": "RDA Mining Site - Extraction Zone",
                "map_id": "1771880106",
            },
            "2061472983492330386": {
                "name": "RDA Mining Site - Processing Plant",
                "map_id": "1771880106",
            },

            # War Zone Beta (60855408)
            "2063545541702190139": {
                "name": "War Zone Beta - Forward Base",
                "map_id": "60855408",
            },
            "2063890557387670141": {
                "name": "War Zone Beta - Defense Point",
                "map_id": "60855408",
            },
            "2063890567200244351": {
                "name": "War Zone Beta - Strategic Post",
                "map_id": "60855408",
            },

            # Luminous Valley (1504064473)
            "2060340043800642795": {
                "name": "Luminous Valley - Entry Gate",
                "map_id": "1504064473",
            },
            "2060340095042454767": {
                "name": "Luminous Valley - Glowing Pool",
                "map_id": "1504064473",
            },
            "2060340207032467970": {
                "name": "Luminous Valley - Crystal Cave",
                "map_id": "1504064473",
            },
            "2060340110464910577": {
                "name": "Luminous Valley - Light Bridge",
                "map_id": "1504064473",
            },

            # Battlefield Delta (470159002)
            "2063175345080642929": {
                "name": "Battlefield Delta - Command Post",
                "map_id": "470159002",
            },
            "2060617244297137020": {
                "name": "Battlefield Delta - Forward Camp",
                "map_id": "470159002",
            },
            "2062053244019938715": {
                "name": "Battlefield Delta - Strategic Point",
                "map_id": "470159002",
            },

            # Additional Combat Arena Alpha (2216033045)
            "2062911740787556521": {
                "name": "Combat Arena - Training Zone",
                "map_id": "2216033045",
            },
            "2063838350116141447": {
                "name": "Combat Arena - Preparation Area",
                "map_id": "2216033045",
            },
            "2063725930058092479": {
                "name": "Combat Arena - Staging Ground",
                "map_id": "2216033045",
            },

            # Additional Tantalus Area (3616200713)
            "2061306688098537843": {
                "name": "Tantalus - Main Gateway",
                "map_id": "3616200713",
            },
            "2061306471385141611": {
                "name": "Tantalus - Central Plaza",
                "map_id": "3616200713",
            },
            "2060408843661221082": {
                "name": "Tantalus - Observation Post",
                "map_id": "3616200713",
            },

            # Additional Sacred Ruins (3903502716)
            "2060396427495867135": {
                "name": "Sacred Ruins - Ancient Gate",
                "map_id": "3903502716",
            },
            "2062842005609778906": {
                "name": "Sacred Ruins - Temple Grounds",
                "map_id": "3903502716",
            },
            "2063393208991233921": {
                "name": "Sacred Ruins - Inner Sanctum",
                "map_id": "3903502716",
            },

            # Additional Fungal Grove (2232107097)
            "2062038181303297069": {
                "name": "Fungal Grove - Hidden Path",
                "map_id": "2232107097",
            },
            "2062038112399270955": {
                "name": "Fungal Grove - Spore Fields",
                "map_id": "2232107097",
            },

            # Additional Mission Zone Beta Points (2509501782)
            "2063890748702458523": {
                "name": "Mission Beta - Extraction Point",
                "map_id": "2509501782",
            },
            "2063890691282436751": {
                "name": "Mission Beta - Supply Cache",
                "map_id": "2509501782",
            },
            "2063890714384663189": {
                "name": "Mission Beta - Observation Post",
                "map_id": "2509501782",
            },

            # Final RDA Training Facility Points (2292208788)
            "2061389828364177681": {
                "name": "RDA Training - Combat Zone",
                "map_id": "2292208788",
            },
            "2061389718829928719": {
                "name": "RDA Training - Briefing Area",
                "map_id": "2292208788",
            },
            "2061389705531887885": {
                "name": "RDA Training - Field Exercise",
                "map_id": "2292208788",
            }
        }

        # Special handling for dummy case to return the entire dictionary
        if entity_id == "dummy":
            return checkpoint_data

        # Normal checkpoint retrieval
        info = checkpoint_data.get(entity_id, {
            "name": "Unknown Checkpoint",
            "map_id": "",
        })

        info['map_id'] = str(info.get('map_id', ''))

        return info

    def setup_ui(self) -> None:
        
        # Create main frame
        self.navigation_frame = ttk.Frame(self.parent)
        self.navigation_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Create left panel for maps
        left_panel = ttk.Frame(self.navigation_frame)
        left_panel.pack(side="left", fill=tk.BOTH, expand=True, padx=(0, 2))

        # Create map list frame with label
        ttk.Label(left_panel, text="Maps", font=('', 10, 'bold')).pack(fill=tk.X, pady=(0, 5))
        
        # Create Treeview for maps
        self.maps_tree = ttk.Treeview(
            left_panel,
            columns=("ID", "Name", "FoW"),
            show="headings",
            selectmode="browse"
        )

        # Configure map columns
        self.maps_tree.heading("ID", text="Map ID")
        self.maps_tree.heading("Name", text="Map Name")
        self.maps_tree.heading("FoW", text="FoW")

        self.maps_tree.column("ID", width=100)
        self.maps_tree.column("Name", width=200)
        self.maps_tree.column("FoW", width=70)

        # Add scrollbar for maps
        maps_scroll = ttk.Scrollbar(left_panel, orient="vertical", command=self.maps_tree.yview)
        self.maps_tree.configure(yscrollcommand=maps_scroll.set)

        self.maps_tree.pack(side="left", fill=tk.BOTH, expand=True)
        maps_scroll.pack(side="right", fill="y")

        # Create separator
        ttk.Separator(self.navigation_frame, orient="vertical").pack(side="left", fill="y", padx=5)

        # Create right panel for checkpoints
        right_panel = ttk.Frame(self.navigation_frame)
        right_panel.pack(side="left", fill=tk.BOTH, expand=True, padx=(2, 0))

        # Create checkpoint list frame with label
        self.checkpoint_label = ttk.Label(right_panel, text="Checkpoints", font=('', 10, 'bold'))
        self.checkpoint_label.pack(fill=tk.X, pady=(0, 5))
        
        # Create Treeview for checkpoints
        self.checkpoints_tree = ttk.Treeview(
            right_panel,
            columns=("ID", "Name", "Status"),
            show="headings"
        )

        # Configure checkpoint columns
        self.checkpoints_tree.heading("ID", text="Checkpoint ID")
        self.checkpoints_tree.heading("Name", text="Name")
        self.checkpoints_tree.heading("Status", text="Status")

        self.checkpoints_tree.column("ID", width=100)
        self.checkpoints_tree.column("Name", width=200)
        self.checkpoints_tree.column("Status", width=70)

        # Add scrollbar for checkpoints
        checkpoints_scroll = ttk.Scrollbar(right_panel, orient="vertical", command=self.checkpoints_tree.yview)
        self.checkpoints_tree.configure(yscrollcommand=checkpoints_scroll.set)

        self.checkpoints_tree.pack(side="left", fill=tk.BOTH, expand=True)
        checkpoints_scroll.pack(side="right", fill="y")

        # Bind selection event
        self.maps_tree.bind('<<TreeviewSelect>>', self.on_map_select)

        # Add a button to display all checkpoints
        display_checkpoints_btn = ttk.Button(
            self.navigation_frame, 
            text="Show All Checkpoints", 
            command=self.display_all_checkpoints
        )
        display_checkpoints_btn.place(x=955, y=-6)  # Adjust x and y as needed

    def display_all_checkpoints(self) -> None:
        """
        Display a comprehensive list of ALL checkpoints across all maps,
        including those not visited in the current save file.
        """
        # Create a top-level window for checkpoint display
        checkpoint_window = tk.Toplevel(self.parent)
        checkpoint_window.title("Complete Checkpoint List")
        checkpoint_window.geometry("1000x800")

        # Create a text widget to display checkpoints
        text_widget = tk.Text(checkpoint_window, wrap=tk.WORD, font=('Courier', 10))
        text_widget.pack(fill=tk.BOTH, expand=True)

        # Get all possible checkpoints
        all_checkpoints = self.get_checkpoint_info("dummy")

        # Get visited checkpoints from the save file
        visited_checkpoints = set()
        if hasattr(self.main_window, 'tree'):
            visited_points = self.main_window.tree.find(".//VisitedCheckpoints")
            if visited_points is not None:
                visited_checkpoints = {point.get("EntityID") for point in visited_points.findall("CheckPoint")}

        # Sort checkpoints by map for organized display
        checkpoints_by_map = {}
        for entity_id, checkpoint_info in all_checkpoints.items():
            map_id = checkpoint_info.get('map_id', 'Unknown')
            map_name = self.get_map_name(map_id)
            
            if map_name not in checkpoints_by_map:
                checkpoints_by_map[map_name] = []
            
            checkpoints_by_map[map_name].append({
                'entity_id': entity_id,
                'name': checkpoint_info.get('name', 'Unnamed Checkpoint'),
                'visited': entity_id in visited_checkpoints
            })

        # Write checkpoints to text widget
        text_widget.tag_configure('visited', foreground='green')
        text_widget.tag_configure('unvisited', foreground='red')
        
        text_widget.insert(tk.END, "COMPLETE CHECKPOINT LIST\n")
        text_widget.insert(tk.END, "=" * 50 + "\n\n")

        for map_name, checkpoints in sorted(checkpoints_by_map.items()):
            text_widget.insert(tk.END, f"MAP: {map_name}\n")
            text_widget.insert(tk.END, "-" * 40 + "\n")
            
            for checkpoint in sorted(checkpoints, key=lambda x: x['name']):
                status_tag = 'visited' if checkpoint['visited'] else 'unvisited'
                status_symbol = '✓' if checkpoint['visited'] else '✗'
                
                text_widget.insert(tk.END, f"{status_symbol} Checkpoint Name: ", status_tag)
                text_widget.insert(tk.END, f"{checkpoint['name']}\n", status_tag)
                text_widget.insert(tk.END, f"   Entity ID: {checkpoint['entity_id']}\n", status_tag)
            
            text_widget.insert(tk.END, "\n")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(checkpoint_window, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)

        # Add a summary at the bottom
        total_checkpoints = len(all_checkpoints)
        visited_count = len(visited_checkpoints)
        summary_text = f"\nTotal Checkpoints: {total_checkpoints}\n"
        summary_text += f"Visited Checkpoints: {visited_count} ({visited_count/total_checkpoints*100:.2f}%)\n"
        
        text_widget.insert(tk.END, summary_text)

        # Make text widget read-only
        text_widget.config(state=tk.DISABLED)

    def on_map_select(self, event):
        """Handle map selection event"""
        selection = self.maps_tree.selection()
        if not selection:
            return
        
        # Get selected map ID
        map_id = self.maps_tree.item(selection[0])['values'][0]
        self.selected_map_id = str(map_id)
        
        # Update checkpoint label
        map_name = self.get_map_name(self.selected_map_id)
        self.checkpoint_label.config(text=f"Checkpoints - {map_name}")
        
        # Update checkpoints display
        self.update_checkpoints_display()

    def update_checkpoints_display(self):
        """Update the checkpoints display for the selected map, showing all checkpoints"""
        # Clear existing items
        for item in self.checkpoints_tree.get_children():
            self.checkpoints_tree.delete(item)
            
        if not self.selected_map_id:
            self.logger.debug("No map selected")
            return

        self.logger.debug(f"Updating checkpoints for map {self.selected_map_id}")
        
        # Convert selected_map_id to string to ensure consistent comparison
        selected_map_id = str(self.selected_map_id)
        
        # Get all checkpoints
        all_checkpoints = self.get_checkpoint_info("dummy")
        
        # Get visited checkpoints from the save file
        visited_checkpoints = set()
        if hasattr(self.main_window, 'tree'):
            visited_points = self.main_window.tree.find(".//VisitedCheckpoints")
            if visited_points is not None:
                visited_checkpoints = {point.get("EntityID") for point in visited_points.findall("CheckPoint")}
        
        # Find all checkpoints for this map
        matching_checkpoints = [
            (entity_id, checkpoint_info) 
            for entity_id, checkpoint_info in all_checkpoints.items() 
            if str(checkpoint_info["map_id"]) == selected_map_id
        ]
        
        self.logger.debug(f"Total matching checkpoints: {len(matching_checkpoints)}")
        
        # Insert all matching checkpoints
        for entity_id, checkpoint_info in matching_checkpoints:
            status = "Visited" if entity_id in visited_checkpoints else "Unvisited"

            
            self.checkpoints_tree.insert(
                "", "end",
                values=(
                    entity_id,
                    checkpoint_info["name"],
                    status
                ),
                tags=('visited' if status == 'Visited' else 'unvisited')
            )
        
        # Configure tags for color-coding
        self.checkpoints_tree.tag_configure('visited', foreground='green')
        self.checkpoints_tree.tag_configure('unvisited', foreground='red')

    def load_navigation_data(self, tree: ET.ElementTree) -> None:
        self.logger.debug("Loading navigation data")
        try:
            # Clear existing items and checkpoint data
            for item in self.maps_tree.get_children():
                self.maps_tree.delete(item)
            for item in self.checkpoints_tree.get_children():
                self.checkpoints_tree.delete(item)
            
            # Clear checkpoint data
            self.checkpoint_data.clear()

            # Get FoW data from save file
            fow_data = {}
            fog_of_war = tree.find(".//AvatarFogOfWarDB_Status")
            if fog_of_war is not None:
                for map_element in fog_of_war.findall("FoW_Map"):
                    map_id = str(map_element.get("crc_id", ""))
                    fow_current = str(map_element.get("fFoWcurrent", "-1"))
                    fow_data[map_id] = fow_current

            # Get all possible maps from our dictionary
            map_names = {
                # Starting/Tutorial Areas
                "3409126972": "Tutorial Area",
                "238707229": "Training Grounds",
                "2292208788": "RDA Training Facility",
                
                # Major Areas
                "355473279": "Plains of Goliath",
                "615754132": "Crystal Fields",
                "1172651822": "Emerald Forest",
                "1847852653": "Torchwood Forest",
                "2171723794": "Swamps of Silence",
                "2587251285": "Northern Shelf",
                "2961077726": "Willow Glade",
                "3616200713": "Tantalus",
                
                # Special Areas
                "1057194188": "Pandoran Abyss",
                "2856892107": "Floating Mountains",
                "3822194552": "Sacred Grove",
                "1504064473": "Luminous Valley",
                
                # RDA Areas
                "2752812145": "RDA Main Base",
                "837458676": "RDA Research Station",
                "1771880106": "RDA Mining Site",
                
                # Combat Zones
                "470159002": "Battlefield Delta",
                "2216033045": "Combat Arena Alpha",
                "60855408": "War Zone Beta",
                
                # Wilderness Areas
                "3975313082": "Wild Plains",
                "2169212369": "Dense Jungle",
                "1578821154": "Mountain Pass",
                "1782610090": "Hidden Valley",
                
                # Cave Systems
                "1628184437": "Crystal Caverns",
                "1865345760": "Echo Caves",
                "3564339531": "Underground Network",
                
                # Water Areas
                "4294730242": "River Delta",
                "1741938656": "Great Lake",
                "2555792139": "Waterfall Basin",
                
                # Ancient Ruins
                "2353717556": "Ancient Temple",
                "2001468046": "Lost City",
                "3903502716": "Sacred Ruins",
                
                # Unique Biomes
                "3852438644": "Bioluminescent Forest",
                "2232107097": "Fungal Grove",
                "2185381138": "Living Mountain",
                
                # Na'vi Areas
                "2672591835": "Na'vi Village",
                "105239137": "Tree of Souls",
                "3575765971": "Hometree",
                
                # Border Regions
                "902032528": "Northern Border",
                "948986278": "Eastern Frontier",
                "1437051617": "Southern Boundary",
                
                # Special Mission Areas
                "2427499480": "Mission Zone Alpha",
                "2509501782": "Mission Zone Beta",
                "4220570174": "Mission Zone Gamma",
                
                # Resource Areas
                "408444403": "Unobtanium Mine",
                "1846881984": "Resource Valley",
                "4168272830": "Mining Complex"
            }

            # Add all maps to the tree
            for map_id, map_name in sorted(map_names.items(), key=lambda x: x[1]):  # Sort by map name
                fow_value = fow_data.get(map_id, "-1")  # Default to -1 if no FoW data
                
                self.maps_tree.insert(
                    "", "end",
                    values=(map_id, map_name, fow_value)
                )

            # Load checkpoints
            checkpoints = tree.find(".//VisitedCheckpoints")
            if checkpoints is not None:
                points = list(checkpoints.findall("CheckPoint"))
                self.logger.debug(f"Found {len(points)} checkpoints")
                
                # Store checkpoint data
                for point in points:
                    try:
                        entity_id = point.get("EntityID", "")
                        
                        # Log every checkpoint for debugging
                        self.logger.debug(f"Processing checkpoint: {entity_id}")
                        
                        # Try to get checkpoint info
                        checkpoint_info = self.get_checkpoint_info(entity_id)
                        
                        # If checkpoint is not in predefined list, try to extract map info differently
                        if checkpoint_info.get("name", "").startswith("Unknown"):
                            map_id = point.get("crc_id", "")
                            checkpoint_info = {
                                "name": f"Checkpoint {entity_id}",
                                "map_id": map_id,
                            }
                        
                        # Always add the checkpoint
                        self.checkpoint_data[entity_id] = checkpoint_info
                        self.logger.debug(f"Stored checkpoint: {checkpoint_info}")
                        
                    except Exception as checkpoint_error:
                        self.logger.error(f"Error processing checkpoint {entity_id}: {checkpoint_error}", exc_info=True)

            self.logger.debug("Navigation data loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading navigation data: {str(e)}", exc_info=True)
            raise
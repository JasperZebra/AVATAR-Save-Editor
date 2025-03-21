import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
from typing import Dict, Optional
from pathlib import Path  # Add this import
from ui_components import LabeledInput, block_combobox_mousewheel
import os
from PIL import Image, ImageTk
from Face_Image_Window import FaceImageWindow
import logging

class StatsManager:
    def __init__(self, parent: ttk.Frame, main_window):
        self.logger = logging.getLogger('StatsManager')
        self.logger.debug("Initializing StatsManager")
        self.parent = parent
        self.main_window = main_window
        self.entries = {}
        self.face_image_frame = None
        self.face_image_label = None
        self.label_frames = {}  # Store frames for label displays

        # Create item mappings FIRST
        self._create_item_mappings()
        
        # Initialize face values mapping - this is the first change
        self.face_values = {}
        # Create separate mappings for male and female faces
        for i in range(12):  # 12 pairs (00-11)
            face_num = str(i).zfill(2)
            # Both male and female of the same number share the same face value
            self.face_values[str(i)] = {
                "male": f"Male {face_num}",
                "female": f"Female {face_num}"
            }
        
        self.setup_ui()

    def _create_item_mappings(self):
        """Create mappings for item IDs to their actual names"""
        self.item_mappings = {

            #############################################

            # RDA Weapons

            # Dual Wasp Pistol
            "1042188764": "Dual Wasp Pistol I",
            "815885611": "Dual Wasp Pistol II",
            "760079057": "Dual Wasp Pistol III",
            "999316102": "Dual Wasp Pistol IV",
            
            # DLC Dual Wasp Pistols
            "3859060838": "DLC WARLOCK Dual Wasp Pistol I",
            "3904601233": "DLC WARLOCK Dual Wasp Pistol II",
            "102867538": "DLC WARLOCK Dual Wasp Pistol III", 
            "749353518": "DLC WARLOCK Dual Wasp Pistol IV",

            # Standard Issue Rifle
            "1130814347": "Standard Issue Rifle TERRA I",
            "1306083196": "Standard Issue Rifle EURYS II",
            "3628031700": "Standard Issue Rifle SOLARIS III",
            "1146928137": "Standard Issue Rifle SOLARIS IV",
            
            # DLC Standard Issue Rifles
            "2850329205": "DLC ARGO Standard Issue Rifle I",
            "2807789186": "DLC ARGO Standard Issue Rifle II",
            "2194670470": "DLC ARGO Standard Issue Rifle III",
            "324172685": "DLC ARGO Standard Issue Rifle IV",

            # Combat Shotgun
            "2313824646": "Combat Shotgun PHALANX I",
            "2270547313": "Combat Shotgun PHALANX II",
            "2789519003": "Combat Shotgun PHALANX III",
            "1919695864": "Combat Shotgun PHALANX IV",
            
            # DLC Combat Shotguns
            "2664450350": "DLC SIGNET Combat Shotgun I",
            "2423238105": "DLC SIGNET Combat Shotgun II",
            "2120138529": "DLC SIGNET Combat Shotgun III",
            "4289908838": "DLC SIGNET Combat Shotgun IV",

            # Assault Rifle
            "2397981034": "Assault Rifle TERRA I",
            "2152836509": "Assault Rifle EURYS II",
            "268371112": "Assault Rifle SOLARIS III",
            "466145020": "Assault Rifle SOLARIS IV",
            
            # DLC Assault Rifles
            "3655372526": "DLC BARRO Assault Rifle I",
            "3613354521": "DLC BARRO Assault Rifle II",
            "3850194262": "DLC BARRO Assault Rifle III",
            "2109370248": "DLC BARRO Assault Rifle IV",

            # M60 Machine Gun
            "85991974": "BANISHER M60 Machine Gun I",
            "195020497": "BANISHER M60 Machine Gun II",
            "1881065336": "BANISHER M60 Machine Gun III",
            "1796958374": "BANISHER M60 Machine Gun IV",
            
            # DLC Machine Guns
            "2015914953": "DLC STELLAR M60 Machine Gun I",
            "1989644094": "DLC STELLAR M60 Machine Gun II",
            "1087779032": "DLC STELLAR M60 Machine Gun III",
            "1691104809": "DLC STELLAR M60 Machine Gun IV",

            # Grenade Launcher
            "94681171": "Grenade Launcher M222 - I",
            "186342564": "Grenade Launcher M222 - II",
            "1349633617": "Grenade Launcher M222 - III",
            "4018216358": "Grenade Launcher M222 - IV",
            
            # DLC Grenade Launchers
            "2157668310": "DLC CRUSHER Grenade Launcher I",
            "2384757537": "DLC CRUSHER Grenade Launcher II",
            "3441856033": "DLC CRUSHER Grenade Launcher III",
            "3043901684": "DLC CRUSHER Grenade Launcher IV",

            # Flamethrower
            "2529862352": "Flamethrower VESUPYRE I",
            "2557822503": "Flamethrower STERILATOR II",
            "609450705": "Flamethrower BUSHBOSS III",
            "2288255787": "Flamethrower BUSHBOSS IV",
            
            # DLC Flamethrowers
            "3250873684": "DLC BUDDY Flamethrower I",
            "3480977827": "DLC BUDDY Flamethrower II",
            "3469816623": "DLC BUDDY Flamethrower III",
            "3994460767": "DLC BUDDY Flamethrower IV",

            # Nail Gun
            "2548581230": "Nail Gun HAMMER I",
            "2572658585": "Nail Gun HAMMER II",
            "143378107": "Nail Gun HAMMER III",
            "1911864170": "Nail Gun HAMMER IV",
            
            # DLC Nail Guns
            "2161255366": "DLC DENT Nail Gun I",
            "2389559089": "DLC DENT Nail Gun II",
            "3499218689": "DLC DENT Nail Gun III",
            "4230631668": "DLC DENT Nail Gun IV",

            # RDA Ammo
            "4029490973": "Rifle Ammo",
            "2220072441": "Shotgun Ammo",
            "3183424835": "SMG Ammo",
            "3227899887": "Grenade Ammo",
            "4198025789": "Rocket Ammo",
            "2442117335": "LMG Ammo",
            "3819023512": "Heavy Ammo",

            #############################################

            # RDA Armor Sets

            # Titan Armor Set
            "4082430736": "Titan Head",
            "205852157":  "Titan Torso",
            "1052486966": "Titan Legs",
        
            # Militum Armor Set
            "149499402":  "Militum Head",  
            "4160278759": "Militum Torso",    
            "3305533484": "Militum Legs",   

            # Kodiak Armor Set
            "1593826001": "Kodiak Head",          
            "2716738620": "Kodiak Torso",        
            "2467333367": "Kodiak Legs",      

            # Exotant Armor Set
            "3527939275": "Exotant Head",     
            "1193780569": "Exotant Torso",       
            "1379870057": "Exotant Legs",         

            # Centauri Armor Set
            "403319592":  "Centauri Head",     
            "3877361093": "Centauri Torso",   
            "3588584718": "Centauri Legs",        

            # Hydra Armor Set
            "3753317026": "Hydra Head",      
            "1851965193": "Hydra Torso",        
            "2428117146": "Hydra Legs",   

            # Warthog Armor Set
            "2823901304": "Warthog Head",         
            "1981144899": "Warthog Torso",          
            "2056338139": "Warthog Legs",    

            # Viper Armor Set
            "3980056687": "Viper Head",
            "3574042272": "Viper Torso",
            "1417888964": "Viper Legs",

            # DLC BRASHER I Armor Set
            "3005472419": "DLC BRASHER I Head",
            "730661330": "DLC BRASHER I Torso",
            "3718956374": "DLC BRASHER I Legs",

            # DLC BRASHER IV Armor Set
            "3064631211": "DLC BRASHER II Head",
            "2822640242": "DLC BRASHER II Torso",
            "2398239326": "DLC BRASHER II Legs",

            # DLC BRASHER III Armor Set
            "3228789267": "DLC BRASHER III Head",
            "1063425278": "DLC BRASHER III Troso",
            "228340789": "DLC BRASHER III Legs",
            
            # DLC BRASHER IV Armor Set
            "3818917462": "DLC BRASHER IV Head",
            "1993326532": "DLC BRASHER IV Torso",
            "1675050996": "DLC BRASHER IV Legs",



            # DLC MISHETICA I Armor Set
            "1563279247": "DLC MISHETICA I Head",
            "3313721598": "DLC MISHETICA I Torso",
            "866428026": "DLC MISHETICA I Legs",

            # DLC MISHETICA II Armor Set
            "4103047382": "DLC MISHETICA II Head",
            "3927643407": "DLC MISHETICA II Torso",
            "3436657955": "DLC MISHETICA II Legs",

            # DLC MISHETICA III Armor Set
            "4001710741": "DLC MISHETICA III Head",
            "294960248": "DLC MISHETICA III Torso",
            "594156723": "DLC MISHETICA III Legs",

            # DLC MISHETICA IV Armor Set
            "1950293887": "DLC MISHETICA IV Head",
            "3780161261": "DLC MISHETICA IV Torso", 
            "4098371293": "DLC MISHETICA IV Legs",

            # Default RDA Armor Set
            "433486271": "Default RDA Head",



            #############################################



            # Na'vi Weapons

            # Dual Blade
            "2740507591": "Ikranä Syal Dual Blade I",
            "2917611312": "'Angtsìkä Zawng Dual Blade II",
            "2813685095": "Palulukanä Srew Dual Blade III",
            "2948460035": "Torukä Way Dual Blade IV",
            
            # DLC Dual Blade
            "2285146948": "DLC Tanhì Dual Blade I",
            "2257287091": "DLC Tanhì Dual Blade II",
            "3543126973": "DLC Tanhì Dual Blade III",
            "2007498681": "DLC Tanhì Dual Balde IV",
            
            # Crossbow
            "1662469074": "Taronyu Crossbow I", 
            "1839769381": "Tsamsiyu Crossbow II",
            "3400058396": "Kyktan Crossbow III",
            "1514231420": "Nawm Crossbow IV",

            # DLC Crossbow
            "3138212456": "DLC PXI Crossbow I",
            "2486913109": "DLC PXI Crossbow II", 
            "2589205711": "DLC PXI Crossbow III",
            "1886472672": "DLC PXI Crossbow IV",

            # M30 Machine Gun
            "1304439874": "AVR-M30 Machine Gun I",
            "1132447925": "AVR-M30 Machine Gun II",
            "982090295": "AVR-M30 Machine Gun III",
            "958613249": "AVR-M30 Machine Gun IV",

            # ELITE M30 Machine Gun
            "1048019290": "ELITE AVR-M30 II",
            "172062103": "ELITE AVR-M30 III",
            "921966990": "ELITE AVR-M30 IV",   

            # Club
            "4093397293": "Taronyu Club I",
            "4249071066": "Tsamsiyu Club II",
            "3879387803": "Eyktan Club III",
            "240531571": "Nawm Club IV",

            # DLC Axe
            "1958996617": "DLC Ikran Axe 'Eko",
            "2689671946": "DLC Ikran Axe Kurakx",
            "1639187137": "DLC Ikran Axe Tsmukan",
            "2934884349": "DLC Ikran Axe 'Ampi",
            
            # Fighting Staff
            "2255793432": "Ikranä Zawng Fighting Staff I",
            "2295024111": "Pa'liä Tìtxur Fighting Staff II",
            "2986118748": "Palulukanä Tìtakuk Fighting Staff III",
            "3960574385": "Torukä Tirea Fighting Staff IV",
            
            # DLC Fighting Staff
            "1828119782": "DLC Hufwe Fighting Staff I",
            "1648951313": "DLC Hufwe Fighting Staff II",
            "3943944974": "DLC Hufwe Fighting Staff III",
            "3139393077": "DLC Hufwe Fighting Staff IV",

            # Bow
            "291262189": "DLC Taronyu Tsko Bow I",
            "371977402": "Tsko Nawm Bow IV",
            "2092736556": "Tsko Kyktan Bow III", 
            "535013914": "Tasmsiyu Tsko Bow II",

            # DLC Bow
            "1817446146": "DLC RAWKE Bow I",
            "1659626485": "DLC RAWKE Bow II",
            "1282693004": "DLC RAWKE Bow III",
            "435991093": "DLC RAWKE Bow IV",

            # Na'vi Ammo
            "1042656528": "Arrow Ammo",  
            "435601722": "Spear Ammo",   
            "3069972540": "Poison Ammo", 

            #############################################

            # Na'vi Armor   
            
            
            # RDA-Issue Avatar Gear
            "236713729": "RDA-Issue Avatar Head",
            "2228061969": "RDA-Issue Avatar Torso",
            "753645081": "RDA-Issue Avatar Legs",

            # NAWM Armor III
            "3363478556": "NAWM Head",  
            "1118628876": "NAWM Torso",   
            "3934969092": "NAWM Legs",

            # EYKTAN Armor Set
            "84098544": "EYKTAN Head",
            "3666151432": "EYKTAN Torso",
            "815973795": "EYKTAN Legs",

            # KARYU Armor Set
            "2070955956": "KARYU Head",
            "1711646853": "KARYU Torso",
            "2024863229": "KARYU Legs",

            # NAWMA EYKTAN Armor Set
            "1519513878": "NAWMA EYKTAN Head",
            "2232927470": "NAWMA EYKTAN Torso",
            "1865419077": "NAWMA EYKTAN Legs",

            # NAWMA TARONYU Armor Set
            "3932154789": "NAWMA TARONYU Head",
            "884530381": "NAWMA TARONYU Torso",
            "3480671099": "NAWMA TARONYU Legs",

            # NAWMA TSAMSIYU Armor Set
            "25166328": "NAWMA TSAMSIYU Head",
            "3724948480": "NAWMA TSAMSIYU Torso",
            "874641835": "NAWMA TSAMSIYU Legs",

            # TIREA Armor Set
            "985254384": "TIREA Head",
            "386149755": "TIREA Torso",
            "216177023": "TIREA Legs",

            # 'AWVEA TSAMSIYU Armor Set   
            "3529616870": "'AWVEA TSAMSIYU Head",   
            "1641566717": "'AWVEA TSAMSIYU Torso",   
            "540413008": "'AWVEA TSAMSIYU Legs", 

            # TSTEU II Armor Set 
            "1336514870": "DLC TSTEU II Head",
            "904822394": "DLC TSTEU II Torso",
            "848846039": "DLC TSTEU II Legs",

            # TSTEU III Armor Set 
            "1312065276": "DLC TSTEU III Head",
            "824495264": "DLC TSTEU III Torso",
            "2571396567": "DLC TSTEU III Legs",             

            # TSTEU IV Armor Set 
            "1500118218": "DLC TSTEU IV Head",
            "1960056897": "DLC TSTSU IV Torso",
            "1865591877": "DLC TSTEU IV legs",   



            # TARONYU II Armor Set
            "3240533717": "DLC TARONYU II Head",
            "3143727513": "DLC TARONYU II Torso",
            "3155647284": "DLC TARONYU II Legs",

            # TARONYU III Armor Set
            "2008660537": "DLC TARONYU III Head",
            "145354853": "DLC TARONYU III Torso",
            "2697550098": "DLC TARONYU III Legs",

            # TARONYU IV Armor Set
            "1753343575": "DLC TARONYU IV Head",
            "1161560796": "DLC TARONYU IV Torso",
            "1591391960": "DLC TARONYU IV Legs",                 
                        
        }

    def _get_item_name(self, item_id: str) -> str:
        """Convert an item ID to its readable name"""
        return self.item_mappings.get(item_id, f"Unknown Item ({item_id})")    

    def _format_weapon_text(self, weapon_info: dict) -> str:
        """Format weapon info for display"""
        if not weapon_info:
            return "-Empty-"
            
        text = f"{weapon_info['name']}"
        
        # List of infinite ammo weapon IDs
        infinite_ammo_ids = [
            # Standard Dual Wasp Pistols
            "1042188764",  # Dual Wasp Pistol I
            "815885611",   # Dual Wasp Pistol II
            "760079057",   # Dual Wasp Pistol III
            "999316102",   # Dual Wasp Pistol IV
            
            # DLC Dual Wasp Pistols
            "3859060838",  # DLC WARLOCK Dual Wasp Pistol I
            "3904601233",  # DLC WARLOCK Dual Wasp Pistol II
            "102867538",   # DLC WARLOCK Dual Wasp Pistol III
            "749353518",   # DLC WARLOCK Dual Wasp Pistol IV
        ]
        
        # List of melee weapon IDs
        melee_weapon_ids = [
            # Fighting Staffs
            "3960574385",   # Torukä Tirea Fighting Staff IV
            "2986118748",   # Palulukanä Tìtakuk Fighting Staff III
            "2295024111",   # Pa'liä Tìtxur Fighting Staff II
            "2255793432",   # Ikranä Zawng Fighting Staff I
            
            # DLC Hufwe Fighting Staffs
            "1648951313",   # DLC Hufwe Fighting Staff II
            "3943944974",   # DLC Hufwe Fighting Staff III
            "3139393077",   # DLC Hufwe Fighting Staff IV
            
            # Dual Blades
            "2948460035",  # Torukä Way Dual Blade IV
            "2813685095",  # Palulukanä Srew Dual Blade III
            "2917611312",  # 'Angtsìkä Zawng Dual Blade II
            "2740507591",  # Ikranä Syal Dual Blade I
            
            # DLC Tanhì Dual Blade
            "2285146948",  # DLC Tanhì Dual Blade I
            "2257287091",  # DLC Tanhì Dual Blade II
            "3543126973",  # DLC Tanhì Dual Blade III
            "2007498681",  # DLC Tanhì Dual Blade IV
            
            # Clubs
            "240531571",   # Nawm Club IV
            "3879387803",  # Eyktan Club III
            "4249071066",  # Tsamsiyu Club II
            "4093397293",  # Taronyu Club I
            
            # DLC Ikran Axes
            "2934884349",  # DLC Ikran Axe 'Ampi
            "2689671946",  # DLC Ikran Axe Kurakx
            "1639187137",  # DLC Ikran Axe Tsmukan
            "1958996617",  # DLC Ikran Axe 'Eko
        ]
        
        # Special cases - update to match new names
        if weapon_info['id'] in infinite_ammo_ids or "wasp pistol" in weapon_info['name'].lower():
            text += " (∞)"
        elif weapon_info['id'] in melee_weapon_ids or "club" in weapon_info['name'].lower() or "blade" in weapon_info['name'].lower() or "axe" in weapon_info['name'].lower() or "staff" in weapon_info['name'].lower():
            text += " (Melee)"
        else:
            # For all other weapons, show ammo count if they have ammo
            if weapon_info['ammo'] != "0" and not weapon_info.get('infinite_ammo', False):
                total_ammo = weapon_info.get('total_ammo', '0')
                text += f" ({weapon_info['ammo']}/{total_ammo})"
            elif weapon_info.get('infinite_ammo', False):
                text += " (∞)"
        
        return text

    def setup_ui(self) -> None:
        self._create_stat_fields()

    def _create_stat_fields(self) -> None:
        """Create all stat fields and UI elements using a more streamlined approach"""
        self.logger.debug("Creating stat fields")
        try:
            # Create list of all face values for combobox
            face_values = {}
            for i in range(12):  # 12 pairs (00-11)
                face_num = str(i).zfill(2)
                face_values[f"male_{i}"] = f"Male {face_num}"
                face_values[f"female_{i}"] = f"Female {face_num}"

            # List of fields to display as labels instead of input widgets
            self.label_fields = {"isfemale", "face", "YouAreHere_LatitudeLongitude", "TotalEP", "namevec"}

            # Define field groups with their positions
            field_groups = {
                "Character Info": [
                    ("Character Name", "namevec", None),
                    ("Is Female", "isfemale", {"0": "No", "1": "Yes"}),
                    ("Face", "face", self.face_values),
                    ("Side", "side", {"4": "Undecided", "1": "Navi", "2": "RDA"}),
                    ("Pawn", "pawn", {"1": "Navi", "2": "RDA"}),
                    ("Location", "YouAreHere_LatitudeLongitude")
                ],
                "Progress": [
                    ("Player Faction", "PlayerFaction", {"0": "Undecided", "1": "Navi", "2": "RDA"}),
                    ("Total EP", "TotalEP"),
                    ("Max Out EP", "max_out_button", "button"),
                    ("Recovery Bits", "RecoveryBits"),
                ],
                "Faction Settings": [
                    ("Player0 EPs", "EPs"),        
                    ("Player0 newEPs", "newEPs"),
                    ("Player1 EPs", "EPs_Player1"),
                    ("Player1 newEPs", "newEPs_Player1")
                ],
                "Gameplay Settings": [
                    ("Entity Scanning", "bEntityScanningEnabled", {"0": "No", "1": "Yes"}),
                    ("First Person Mode", "FirstPersonMode", {"0": "No", "1": "Yes"}),
                    ("Rumble Enabled", "RumbleEnabled", {"0": "No", "1": "Yes"}),
                    ("Na'vi Cost Reduction", "NaviCostReduction"),
                    ("RDA Cost Reduction", "CorpCostReduction")
                ]
            }
            
            # Create level options for reference
            rda_levels = {"max": "Max Level"}  # Only max level option
            navi_levels = {"max": "Max Level"}  # Only max level option
            self.level_options = {
                "Navi": navi_levels,
                "RDA": rda_levels
            }

            # Create the UI for field groups
            x_positions_row1 = [0, 230, 460, 690]  # Four positions for top row
            for i, (group_name, fields) in enumerate(list(field_groups.items())[:4]):
                self._create_field_group(group_name, fields, 
                                        x=x_positions_row1[i], y=0, 
                                        width=230, height=185)

            # Create weapon and armor sections
            self._create_loadout_sections()
            
            # Create the face image frame
            self._create_face_image_frame()
            
            # Add error handling to all comboboxes
            self._add_error_handling_to_comboboxes()

        except Exception as e:
            self.logger.error(f"Error creating stat fields: {str(e)}", exc_info=True)
            raise

    def _create_field_group(self, group_name, fields, x, y, width, height):
        """Create a group of fields in a labeled frame"""
        # Use the class-level label_fields
        label_fields = self.label_fields
        
        group_frame = ttk.LabelFrame(self.parent, text=group_name)
        group_frame.place(x=x, y=y, width=width, height=height)
        
        for field_info in fields:
            label_text = field_info[0]
            key = field_info[1]
            field_type = field_info[2] if len(field_info) > 2 else None

            # Special handling for button type
            if field_type == "button":
                field_frame = ttk.Frame(group_frame)
                field_frame.pack(fill=tk.X, padx=5, pady=2)
                ttk.Label(field_frame, text=f"{label_text}:").pack(side=tk.LEFT, padx=5)
                button = ttk.Button(field_frame, text="Max Out", command=self._max_out_level)
                button.pack(side=tk.LEFT, padx=5)
                self.entries[key] = button
                continue

            if key in label_fields:
                # Create frame for label layout
                field_frame = ttk.Frame(group_frame)
                field_frame.pack(fill=tk.X, padx=5, pady=2)
                
                # Label with field name
                ttk.Label(field_frame, text=f"{label_text}:").pack(side=tk.LEFT, padx=5)
                
                # Label for value
                value_label = ttk.Label(field_frame, text="-")
                value_label.pack(side=tk.LEFT, padx=5)
                
                self.entries[key] = value_label
                
                if key == "face":
                    value_label.bind('<Button-1>', lambda e: self._on_face_selected())
            else:
                input_widget = LabeledInput(
                    group_frame,
                    label_text,
                    "combobox" if field_type else "entry",
                    field_type
                )
                input_widget.pack(fill=tk.X, padx=5, pady=2)
                self.entries[key] = input_widget.input

                # Special bindings for different fields
                if key == "PlayerFaction":
                    input_widget.input.bind('<<ComboboxSelected>>', self._on_faction_selected)
                elif key == "TotalEP":
                    input_widget.input.bind('<KeyRelease>', lambda e: self._update_level_from_ep())
                    
                if isinstance(input_widget.input, (ttk.Entry, ttk.Combobox)):
                    if hasattr(input_widget.input, 'bind'):
                        input_widget.input.bind('<KeyRelease>', self._mark_unsaved_changes)
                        if key not in ["TotalEP"]:  # Don't double-bind
                            input_widget.input.bind('<<ComboboxSelected>>', self._mark_unsaved_changes)

    def _create_loadout_sections(self):
        """Create the RDA and Navi loadout UI sections"""
        # RDA Loadout frame
        rda_frame = ttk.LabelFrame(self.parent, text="RDA Loadout")
        rda_frame.place(x=0, y=190, width=545, height=350)

        # Define weapon slot positions
        weapon_slots = [
            {"name": "Right Weapon", "x": 5, "y": 0},
            {"name": "Down Weapon", "x": 5, "y": 50},
            {"name": "Left Weapon", "x": 5, "y": 100},
            {"name": "Top Weapon", "x": 5, "y": 150}
        ]

        # Initialize weapon slots array
        self.weapon_slots = []

        # Add buttons to RDA loadout frame
        self._create_loadout_buttons(rda_frame, is_navi=False)
        
        # Create RDA weapon slots
        for i, slot_info in enumerate(weapon_slots):
            self._create_weapon_dropdown(rda_frame, slot_info["name"], i, is_navi=False, 
                                        x=slot_info["x"], y=slot_info["y"])

        # Create RDA armor mappings if not already done
        if not hasattr(self, 'rda_armor_sets'):
            self._create_rda_armor_mappings()

        # Add RDA armor section
        self._create_armor_section(rda_frame, is_navi=False)

        # Navi Loadout frame
        navi_frame = ttk.LabelFrame(self.parent, text="Navi Loadout")
        navi_frame.place(x=545, y=190, width=555, height=350)

        # Initialize Na'vi weapon slots array
        self.navi_weapon_slots = []
        
        # Add buttons to Na'vi loadout frame
        self._create_loadout_buttons(navi_frame, is_navi=True)

        # Create Na'vi weapon slots
        for i, slot_info in enumerate(weapon_slots):
            self._create_weapon_dropdown(navi_frame, slot_info["name"], i, is_navi=True,
                                        x=slot_info["x"], y=slot_info["y"])

        # Create Na'vi armor mappings if not already done
        if not hasattr(self, 'navi_armor_sets'):
            self._create_navi_armor_mappings()

        # Add Na'vi armor section
        self._create_armor_section(navi_frame, is_navi=True)

    def _create_loadout_buttons(self, frame, is_navi=False):
        """Create buttons for the loadout section"""
        reset_frame = ttk.Frame(frame)
        reset_frame.place(x=350, y=200)  # Position in the frame
        
        # Reset ammo button
        reset_button = ttk.Button(
            reset_frame,
            text="Reset Weapon Ammo Types",
            command=self._reset_weapon_ammo
        )
        reset_button.pack(pady=5)

        # Remove duplicates button
        deduplicate_button = ttk.Button(
            reset_frame,
            text="Remove Duplicate Items",
            command=self._remove_duplicate_items
        )
        deduplicate_button.pack(pady=5)  

        # Add DLC items button
        dlc_button = ttk.Button(
            reset_frame,
            text=f"Add All {'Navi' if is_navi else 'RDA'} DLC Items",
            command=self._add_all_navi_dlc_items if is_navi else self._add_all_rda_dlc_items
        )
        dlc_button.pack(pady=5)

    def _create_armor_section(self, frame, is_navi=False):
        """Create the armor section with dropdowns"""
        armor_frame = ttk.Frame(frame)
        armor_frame.place(x=10, y=200)  # Position in the frame
        
        # Get the appropriate collections
        armor_sets = self.navi_armor_sets if is_navi else self.rda_armor_sets
        armor_dropdowns = {}
        
        # Store reference in the correct variable
        if is_navi:
            self.navi_armor_dropdowns = armor_dropdowns
        else:
            self.armor_dropdowns = armor_dropdowns
        
        # Create dropdowns for each armor slot
        armor_slots = [
            ("headwear", "Headwear"),
            ("torso", "Torso"),
            ("legs", "Legs")
        ]

        for slot_id, slot_name in armor_slots:
            slot_frame = ttk.Frame(armor_frame)
            slot_frame.pack(fill=tk.X, pady=10)
            
            ttk.Label(slot_frame, text=f"{slot_name}:").pack(side=tk.LEFT, padx=5)
            
            # Create combobox with armor options for this slot
            values = list(armor_sets[slot_id].values())
            combo = ttk.Combobox(slot_frame, values=values, state="readonly", width=30)
            combo.set("-Empty-")  # Default value
            combo.pack(side=tk.LEFT, padx=5)
            block_combobox_mousewheel(combo)
            
            # Bind the combobox to update function
            if is_navi:
                combo.bind('<<ComboboxSelected>>', 
                    lambda e, slot=slot_id: self._on_navi_armor_selected(e, slot))
            else:
                combo.bind('<<ComboboxSelected>>', 
                    lambda e, slot=slot_id: self._on_armor_selected(e, slot))
            
            armor_dropdowns[slot_id] = combo

    def _create_face_image_frame(self):
        """Create the frame for displaying the character face image"""
        self.face_image_frame = ttk.LabelFrame(self.parent, text="Character Face")
        self.face_image_frame.place(
            x=920,
            y=0,
            width=182,
            height=185
        )

        # Create a label inside the frame to display the image
        self.face_image_label = ttk.Label(self.face_image_frame)
        self.face_image_label.pack(
            expand=True,
            fill='both',
            padx=12,
            pady=5
        )

    def _remove_duplicate_items(self):
        """Remove duplicate items from both RDA and Na'vi possessions based on crc_ItemID"""
        self.logger.debug("Starting duplicate item removal")

        if self.main_window.tree is None:
            self.logger.warning("Attempted to remove duplicates with no save file loaded")
            messagebox.showerror("Error", "No save file loaded. Please load a save file first.")
            return

        try:
            root = self.main_window.tree.getroot()
            profile = root.find("PlayerProfile")
            
            if profile is None:
                self.logger.error("No player profile found when attempting to remove duplicates")
                messagebox.showerror("Error", "No valid player profile found in the loaded save file.")
                return

            # Track metrics for reporting to the user
            removed_avatar = 0
            removed_soldier = 0
            
            # Keep track of which specific items were duplicated and how many removed
            duplicate_counts = {}
                
            # Process Na'vi (Avatar) possessions
            avatar = profile.find("Possessions_Avatar")
            if avatar is not None:
                possessions = avatar.find("Posessions")
                if possessions is not None:
                    # Find duplicate items by crc_ItemID
                    items_by_id = {}
                    for poss in possessions.findall("Poss"):
                        item_id = poss.get("crc_ItemID")
                        if item_id:
                            if item_id not in items_by_id:
                                items_by_id[item_id] = []
                            items_by_id[item_id].append(poss)
                    
                    # Remove duplicates (keep first occurrence of each item)
                    for item_id, items in items_by_id.items():
                        if len(items) > 1:
                            # Keep the first item, remove the rest
                            first_item = items[0]
                            for duplicate in items[1:]:
                                # Before removing, check if the item is currently equipped
                                duplicate_index = duplicate.get("Index")
                                is_equipped = False
                                
                                # Check if the duplicate is equipped in a weapon slot
                                equipped_weapons = avatar.find("EquippedWeapons")
                                if equipped_weapons is not None:
                                    for slot in equipped_weapons.findall("Slot"):
                                        if slot.get("MainHand_PossIdx") == duplicate_index:
                                            # Update the slot to use the item we're keeping
                                            slot.set("MainHand_PossIdx", first_item.get("Index"))
                                            is_equipped = True
                                        
                                        if slot.get("OffHand_PossIdx") == duplicate_index:
                                            # Update the slot to use the item we're keeping
                                            slot.set("OffHand_PossIdx", first_item.get("Index"))
                                            is_equipped = True
                                
                                # Check if the duplicate is equipped in an armor slot
                                equipped_armors = avatar.find("EquippedArmors")
                                if equipped_armors is not None:
                                    for slot in equipped_armors.findall("Slot"):
                                        if slot.get("PossIdx") == duplicate_index:
                                            # Update the slot to use the item we're keeping
                                            slot.set("PossIdx", first_item.get("Index"))
                                            is_equipped = True
                                
                                # Now we can safely remove the duplicate
                                possessions.remove(duplicate)
                                removed_avatar += 1
                                
                                # Track which items were duplicated for reporting
                                if item_id not in duplicate_counts:
                                    duplicate_counts[item_id] = 0
                                duplicate_counts[item_id] += 1
                                
                                # Get item name for better logging
                                item_name = self._get_item_name(item_id)
                                self.logger.debug(f"Removed duplicate item {item_name} ({item_id}) Index {duplicate_index}" +
                                                (", was equipped" if is_equipped else ""))
            
            # Process RDA (Soldier) possessions
            soldier = profile.find("Possessions_Soldier")
            if soldier is not None:
                possessions = soldier.find("Posessions")
                if possessions is not None:
                    # Find duplicate items by crc_ItemID
                    items_by_id = {}
                    for poss in possessions.findall("Poss"):
                        item_id = poss.get("crc_ItemID")
                        if item_id:
                            if item_id not in items_by_id:
                                items_by_id[item_id] = []
                            items_by_id[item_id].append(poss)
                    
                    # Remove duplicates (keep first occurrence of each item)
                    for item_id, items in items_by_id.items():
                        if len(items) > 1:
                            # Keep the first item, remove the rest
                            first_item = items[0]
                            for duplicate in items[1:]:
                                # Before removing, check if the item is currently equipped
                                duplicate_index = duplicate.get("Index")
                                is_equipped = False
                                
                                # Check if the duplicate is equipped in a weapon slot
                                equipped_weapons = soldier.find("EquippedWeapons")
                                if equipped_weapons is not None:
                                    for slot in equipped_weapons.findall("Slot"):
                                        if slot.get("MainHand_PossIdx") == duplicate_index:
                                            # Update the slot to use the item we're keeping
                                            slot.set("MainHand_PossIdx", first_item.get("Index"))
                                            is_equipped = True
                                        
                                        if slot.get("OffHand_PossIdx") == duplicate_index:
                                            # Update the slot to use the item we're keeping
                                            slot.set("OffHand_PossIdx", first_item.get("Index"))
                                            is_equipped = True
                                
                                # Check if the duplicate is equipped in an armor slot
                                equipped_armors = soldier.find("EquippedArmors")
                                if equipped_armors is not None:
                                    for slot in equipped_armors.findall("Slot"):
                                        if slot.get("PossIdx") == duplicate_index:
                                            # Update the slot to use the item we're keeping
                                            slot.set("PossIdx", first_item.get("Index"))
                                            is_equipped = True
                                
                                # Now we can safely remove the duplicate
                                possessions.remove(duplicate)
                                removed_soldier += 1
                                
                                # Track which items were duplicated for reporting
                                if item_id not in duplicate_counts:
                                    duplicate_counts[item_id] = 0
                                duplicate_counts[item_id] += 1
                                
                                # Get item name for better logging
                                item_name = self._get_item_name(item_id)
                                self.logger.debug(f"Removed duplicate item {item_name} ({item_id}) Index {duplicate_index}" +
                                                (", was equipped" if is_equipped else ""))
            
            # Mark changes as unsaved
            self.main_window.unsaved_label.config(text="Unsaved Changes")
            
            # Update the equipment displays to reflect changes
            self._update_loadout_display(profile)
            self._update_navi_loadout_display(profile)
            
            # Show detailed summary to user with specific duplicated items
            total_removed = removed_avatar + removed_soldier
            if total_removed > 0:
                # Store and display which specific items were removed
                removed_items = []
                for item_id, count in duplicate_counts.items():
                    if count > 0:
                        item_name = self._get_item_name(item_id)
                        removed_items.append(f"• {item_name} (x{count})")
                
                detail_text = "\n".join(removed_items)
                
                # Create a detailed report window instead of a simple messagebox
                report_window = tk.Toplevel(self.parent)
                report_window.title("Duplicate Items Removed")
                report_window.geometry("500x400")
                
                # Set icon (if available)
                try:
                    if hasattr(self.main_window, 'root') and hasattr(self.main_window.root, 'iconbitmap'):
                        report_window.iconbitmap(self.main_window.root.iconbitmap())
                except Exception:
                    pass  # Ignore icon errors
                
                # Add a frame with scrollable text
                frame = ttk.Frame(report_window, padding=10)
                frame.pack(fill=tk.BOTH, expand=True)
                
                # Summary label
                summary_label = ttk.Label(frame, 
                    text=f"Successfully removed {total_removed} duplicate items:\n"
                        f"• {removed_avatar} Na'vi items\n"
                        f"• {removed_soldier} RDA items\n\n"
                        f"Removed item details:")
                summary_label.pack(anchor=tk.W, pady=(0, 10))
                
                # Scrollable text area for item details
                text_frame = ttk.Frame(frame)
                text_frame.pack(fill=tk.BOTH, expand=True)
                
                scrollbar = ttk.Scrollbar(text_frame)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                text_area = tk.Text(text_frame, 
                            wrap=tk.WORD, 
                            yscrollcommand=scrollbar.set,
                            height=15,
                            width=50)
                text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.config(command=text_area.yview)
                
                # Insert the details
                text_area.insert(tk.END, detail_text)
                text_area.configure(state="disabled")  # Make read-only
                
                # Close button
                close_button = ttk.Button(frame, text="Close", command=report_window.destroy)
                close_button.pack(pady=(10, 0))
                
                # Center the window
                report_window.update_idletasks()
                width = report_window.winfo_width()
                height = report_window.winfo_height()
                x = (report_window.winfo_screenwidth() // 2) - (width // 2)
                y = (report_window.winfo_screenheight() // 2) - (height // 2)
                report_window.geometry(f"{width}x{height}+{x}+{y}")
                
                # Make the window modal
                report_window.transient(self.parent)
                report_window.grab_set()
                self.parent.wait_window(report_window)
            else:
                messagebox.showinfo("No Duplicates Found", 
                                "No duplicate items were found in your inventory.")
            
        except Exception as e:
            self.logger.error(f"Error removing duplicate items: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to remove duplicate items: {str(e)}")

    def _add_all_rda_dlc_items(self):
        """Add all RDA DLC items to the player's inventory"""
        self.logger.debug("Adding all RDA DLC items to inventory")
        
        if self.main_window.tree is None:
            self.logger.warning("Attempted to add DLC items with no save file loaded")
            messagebox.showerror("Error", "No save file loaded. Please load a save file first.")
            return
        
        try:
            root = self.main_window.tree.getroot()
            profile = root.find("PlayerProfile")
            
            if profile is None:
                self.logger.error("No player profile found when attempting to add DLC items")
                messagebox.showerror("Error", "No valid player profile found in the loaded save file.")
                return
            
            # Find the Possessions_Soldier element
            soldier = profile.find("Possessions_Soldier")
            if soldier is None:
                self.logger.warning("No Possessions_Soldier element found")
                messagebox.showerror("Error", "Could not find Possessions_Soldier element in save file.")
                return
                
            # Find the Posessions element
            possessions = soldier.find("Posessions")
            if possessions is None:
                self.logger.warning("No Posessions element found in Possessions_Soldier")
                possessions = ET.SubElement(soldier, "Posessions")  # Fixed: soldier instead of avatar
            
            # Get the next available index
            next_index = 0
            for poss in possessions.findall("Poss"):
                idx = int(poss.get("Index", "0"))
                next_index = max(next_index, idx + 1)
            
            # Get all existing item IDs to avoid duplicates
            existing_items = set()
            for poss in possessions.findall("Poss"):
                item_id = poss.get("crc_ItemID")
                if item_id:
                    existing_items.add(item_id)
                    
            self.logger.debug(f"Found {len(existing_items)} existing items in RDA inventory")
            
            # Define specific weapon IDs that need special handling
            wasp_pistol_ids = [
                "3859060838",  # DLC WARLOCK Dual Wasp Pistol I
                "3904601233",  # DLC WARLOCK Dual Wasp Pistol II
                "102867538",   # DLC WARLOCK Dual Wasp Pistol III
                "749353518",   # DLC WARLOCK Dual Wasp Pistol IV
            ]
            
            # Collect all RDA DLC item IDs
            dlc_items = []
            
            # DLC Weapons
            dlc_weapons = [
                # DLC Dual Wasp Pistols
                "3859060838",  # DLC WARLOCK Dual Wasp Pistol I
                "3904601233",  # DLC WARLOCK Dual Wasp Pistol II
                "102867538",   # DLC WARLOCK Dual Wasp Pistol III
                "749353518",   # DLC WARLOCK Dual Wasp Pistol IV
                
                # DLC Standard Issue Rifles
                "2850329205",  # DLC ARGO Standard Issue Rifle I
                "2807789186",  # DLC ARGO Standard Issue Rifle II
                "2194670470",  # DLC ARGO Standard Issue Rifle III
                "324172685",   # DLC ARGO Standard Issue Rifle IV
                
                # DLC Combat Shotguns
                "2664450350",  # DLC SIGNET Combat Shotgun I
                "2423238105",  # DLC SIGNET Combat Shotgun II
                "2120138529",  # DLC SIGNET Combat Shotgun III
                "4289908838",  # DLC SIGNET Combat Shotgun IV
                
                # DLC Assault Rifles
                "3655372526",  # DLC BARRO Assault Rifle I
                "3613354521",  # DLC BARRO Assault Rifle II
                "3850194262",  # DLC BARRO Assault Rifle III
                "2109370248",  # DLC BARRO Assault Rifle IV
                
                # DLC Machine Guns
                "2015914953",  # DLC STELLAR M60 Machine Gun I
                "1989644094",  # DLC STELLAR M60 Machine Gun II
                "1087779032",  # DLC STELLAR M60 Machine Gun III
                "1691104809",  # DLC STELLAR M60 Machine Gun IV
                
                # DLC Grenade Launchers
                "2157668310",  # DLC CRUSHER Grenade Launcher I
                "2384757537",  # DLC CRUSHER Grenade Launcher II
                "3441856033",  # DLC CRUSHER Grenade Launcher III
                "3043901684",  # DLC CRUSHER Grenade Launcher IV
                
                # DLC Flamethrowers
                "3250873684",  # DLC BUDDY Flamethrower I
                "3480977827",  # DLC BUDDY Flamethrower II
                "3469816623",  # DLC BUDDY Flamethrower III
                "3994460767",  # DLC BUDDY Flamethrower IV
                
                # DLC Nail Guns
                "2161255366",  # DLC DENT Nail Gun I
                "2389559089",  # DLC DENT Nail Gun II
                "3499218689",  # DLC DENT Nail Gun III
                "4230631668",  # DLC DENT Nail Gun IV
            ]
            dlc_items.extend(dlc_weapons)
            
            # DLC RDA Armor
            dlc_armor = [
                # DLC BRASHER I Armor Set
                "3005472419",  # DLC BRASHER I Head
                "730661330",   # DLC BRASHER I Torso
                "3718956374",  # DLC BRASHER I Legs
                
                # DLC BRASHER II Armor Set
                "3064631211",  # DLC BRASHER II Head
                "2822640242",  # DLC BRASHER II Torso
                "2398239326",  # DLC BRASHER II Legs
                
                # DLC BRASHER III Armor Set
                "3228789267",  # DLC BRASHER III Head
                "1063425278",  # DLC BRASHER III Troso
                "228340789",   # DLC BRASHER III Legs
                
                # DLC BRASHER IV Armor Set
                "3818917462",  # DLC BRASHER IV Head
                "1993326532",  # DLC BRASHER IV Torso
                "1675050996",  # DLC BRASHER IV Legs
                
                # DLC MISHETICA I Armor Set
                "1563279247",  # DLC MISHETICA I Head
                "3313721598",  # DLC MISHETICA I Torso
                "866428026",   # DLC MISHETICA I Legs
                
                # DLC MISHETICA II Armor Set
                "4103047382",  # DLC MISHETICA II Head
                "3927643407",  # DLC MISHETICA II Torso
                "3436657955",  # DLC MISHETICA II Legs
                
                # DLC MISHETICA III Armor Set
                "4001710741",  # DLC MISHETICA III Head
                "294960248",   # DLC MISHETICA III Torso
                "594156723",   # DLC MISHETICA III Legs
                
                # DLC MISHETICA IV Armor Set
                "1950293887",  # DLC MISHETICA IV Head
                "3780161261",  # DLC MISHETICA IV Torso
                "4098371293",  # DLC MISHETICA IV Legs
            ]
            dlc_items.extend(dlc_armor)
            
            # RDA Ammo types to add
            ammo_types = [
                "4029490973",  # Rifle Ammo
                "2220072441",  # Shotgun Ammo
                "3183424835",  # SMG Ammo
                "3227899887",  # Grenade Ammo
                "4198025789",  # Rocket Ammo
                "2442117335",  # LMG Ammo
                "3819023512",  # Heavy Ammo
            ]
            dlc_items.extend(ammo_types)
            
            # Add items to inventory
            items_added = 0
            duplicates_found = 0
            
            # Find the last Poss element to copy its formatting
            last_poss = None
            for poss in possessions.findall("Poss"):
                last_poss = poss
            
            for item_id in dlc_items:
                # Skip if already exists
                if item_id in existing_items:
                    self.logger.debug(f"Skipping duplicate item: {item_id} ({self._get_item_name(item_id)})")
                    duplicates_found += 1
                    continue
                    
                # Create new possession element
                new_poss = ET.SubElement(possessions, "Poss")
                new_poss.set("Index", str(next_index))
                new_poss.set("crc_ItemID", item_id)
                new_poss.set("NbInStack", "1")
                # For ammo, give a good starting amount
                if item_id in ammo_types:
                    new_poss.set("NbInStack", "500")
                new_poss.set("NbInClip", "0")
                new_poss.set("crc_AmmoType", "4294967295")  # Default to no ammo type
                
                # For weapons, set the correct ammo type
                if item_id in dlc_weapons:
                    ammo_type = self._get_ammo_type_for_weapon(item_id)
                    new_poss.set("crc_AmmoType", ammo_type)
                
                # Set NoveltyState based on item type
                if item_id in ammo_types:
                    # Set ammo to NoveltyState 2 as requested
                    new_poss.set("NoveltyState", "2")
                elif "wasp" in self._get_item_name(item_id).lower() or item_id in wasp_pistol_ids:
                    # Set wasp pistols to NoveltyState 2 as requested
                    new_poss.set("NoveltyState", "2")
                else:
                    # Default NoveltyState for other items
                    new_poss.set("NoveltyState", "2")
                
                # Copy tail formatting from the last element if available
                if last_poss is not None and hasattr(last_poss, 'tail'):
                    new_poss.tail = last_poss.tail
                
                # Add this item to existing_items to prevent duplicates if the same ID appears multiple times
                existing_items.add(item_id)
                
                last_poss = new_poss
                next_index += 1
                items_added += 1
                
            # Mark changes as unsaved
            self.main_window.unsaved_label.config(text="Unsaved Changes")
            
            # Update the loadout display
            self._update_loadout_display(profile)
            
            # Show final summary with information about duplicates
            if items_added > 0:
                messagebox.showinfo("DLC Items Added", 
                                f"Successfully added {items_added} RDA DLC items to your inventory.\n"
                                f"Skipped {duplicates_found} items that were already in your inventory.")
            else:
                messagebox.showinfo("No Items Added", 
                                "All RDA DLC items are already in your inventory.")
            
        except Exception as e:
            self.logger.error(f"Error adding RDA DLC items: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to add RDA DLC items: {str(e)}")

    def _add_all_navi_dlc_items(self):
        """Add all Na'vi DLC items to the player's inventory"""
        self.logger.debug("Adding all Na'vi DLC items to inventory")
        
        if self.main_window.tree is None:
            self.logger.warning("Attempted to add DLC items with no save file loaded")
            messagebox.showerror("Error", "No save file loaded. Please load a save file first.")
            return
        
        try:
            root = self.main_window.tree.getroot()
            profile = root.find("PlayerProfile")
            
            if profile is None:
                self.logger.error("No player profile found when attempting to add DLC items")
                messagebox.showerror("Error", "No valid player profile found in the loaded save file.")
                return
            
            # Find the Possessions_Avatar element
            avatar = profile.find("Possessions_Avatar")
            if avatar is None:
                self.logger.warning("No Possessions_Avatar element found")
                messagebox.showerror("Error", "Could not find Possessions_Avatar element in save file.")
                return
                
            # Find the Posessions element
            possessions = avatar.find("Posessions")
            if possessions is None:
                self.logger.warning("No Posessions element found in Possessions_Avatar")
                possessions = ET.SubElement(avatar, "Posessions")
            
            # Get the next available index
            next_index = 0
            for poss in possessions.findall("Poss"):
                idx = int(poss.get("Index", "0"))
                next_index = max(next_index, idx + 1)
            
            # Get all existing item IDs to avoid duplicates
            existing_items = set()
            for poss in possessions.findall("Poss"):
                item_id = poss.get("crc_ItemID")
                if item_id:
                    existing_items.add(item_id)
                    
            self.logger.debug(f"Found {len(existing_items)} existing items in Na'vi inventory")
            
            # Define specific weapon IDs that need special handling
            bow_ids = [
                "1817446146",  # DLC RAWKE Bow I
                "1659626485",  # DLC RAWKE Bow II
                "1282693004",  # DLC RAWKE Bow III
                "435991093",   # DLC RAWKE Bow IV
            ]
            
            # Collect all Na'vi DLC item IDs
            dlc_items = []
            
            # DLC Weapons
            dlc_weapons = [
                # DLC Dual Blade
                "2285146948",  # DLC Tanhì Dual Blade I
                "2257287091",  # DLC Tanhì Dual Blade II
                "3543126973",  # DLC Tanhì Dual Blade III
                "2007498681",  # DLC Tanhì Dual Balde IV
                
                # DLC Crossbow
                "3138212456",  # DLC PXI Crossbow I
                "2486913109",  # DLC PXI Crossbow II
                "2589205711",  # DLC PXI Crossbow III
                "1886472672",  # DLC PXI Crossbow IV
                
                # DLC Ikran Axe
                "1958996617",  # DLC Ikran Axe 'Eko
                "2689671946",  # DLC Ikran Axe Kurakx
                "1639187137",  # DLC Ikran Axe Tsmukan
                "2934884349",  # DLC Ikran Axe 'Ampi
                
                # DLC Fighting Staff
                "1828119782",  # DLC Hufwe Fighting Staff I
                "1648951313",  # DLC Hufwe Fighting Staff II
                "3943944974",  # DLC Hufwe Fighting Staff III
                "3139393077",  # DLC Hufwe Fighting Staff IV
                
                # DLC Bow
                "1817446146",  # DLC RAWKE Bow I
                "1659626485",  # DLC RAWKE Bow II
                "1282693004",  # DLC RAWKE Bow III
                "435991093",   # DLC RAWKE Bow IV
            ]
            dlc_items.extend(dlc_weapons)
            
            # DLC Na'vi Armor
            dlc_armor = [
                # TSTEU II Armor Set 
                "1336514870",  # DLC TSTEU II Head
                "904822394",   # DLC TSTEU II Torso
                "848846039",   # DLC TSTEU II Legs
                
                # TSTEU III Armor Set 
                "1312065276",  # DLC TSTEU III Head
                "824495264",   # DLC TSTEU III Torso
                "2571396567",  # DLC TSTEU III Legs
                
                # TSTEU IV Armor Set 
                "1500118218",  # DLC TSTEU IV Head
                "1960056897",  # DLC TSTSU IV Torso
                "1865591877",  # DLC TSTEU IV legs
                
                # TARONYU II Armor Set
                "3240533717",  # DLC TARONYU II Head
                "3143727513",  # DLC TARONYU II Torso
                "3155647284",  # DLC TARONYU II Legs
                
                # TARONYU III Armor Set
                "2008660537",  # DLC TARONYU III Head
                "145354853",   # DLC TARONYU III Torso
                "2697550098",  # DLC TARONYU III Legs
                
                # TARONYU IV Armor Set
                "1753343575",  # DLC TARONYU IV Head
                "1161560796",  # DLC TARONYU IV Torso
                "1591391960",  # DLC TARONYU IV Legs
            ]
            dlc_items.extend(dlc_armor)
            
            # Na'vi Ammo types to add
            ammo_types = [
                "1042656528",  # Arrow Ammo
                "435601722",   # Spear Ammo
                "3069972540",  # Poison Ammo
            ]
            dlc_items.extend(ammo_types)
            
            # Add items to inventory
            items_added = 0
            duplicates_found = 0
            
            # Find the last Poss element to copy its formatting
            last_poss = None
            for poss in possessions.findall("Poss"):
                last_poss = poss
            
            for item_id in dlc_items:
                # Skip if already exists
                if item_id in existing_items:
                    self.logger.debug(f"Skipping duplicate item: {item_id} ({self._get_item_name(item_id)})")
                    duplicates_found += 1
                    continue
                    
                # Create new possession element
                new_poss = ET.SubElement(possessions, "Poss")
                new_poss.set("Index", str(next_index))
                new_poss.set("crc_ItemID", item_id)
                new_poss.set("NbInStack", "1")
                # For ammo, give a good starting amount
                if item_id in ammo_types:
                    new_poss.set("NbInStack", "500")
                new_poss.set("NbInClip", "0")
                new_poss.set("crc_AmmoType", "4294967295")  # Default to no ammo type
                
                # For weapons, set the correct ammo type
                if item_id in dlc_weapons:
                    ammo_type = self._get_ammo_type_for_weapon(item_id)
                    new_poss.set("crc_AmmoType", ammo_type)
                
                # Set NoveltyState based on item type
                if item_id in ammo_types:
                    # Set ammo to NoveltyState 2 as requested
                    new_poss.set("NoveltyState", "2")
                elif "bow" in self._get_item_name(item_id).lower() or item_id in bow_ids:
                    # Set bows to NoveltyState 2 as requested
                    new_poss.set("NoveltyState", "2")
                else:
                    # Default NoveltyState for other items
                    new_poss.set("NoveltyState", "2")
                
                # Copy tail formatting from the last element if available
                if last_poss is not None and hasattr(last_poss, 'tail'):
                    new_poss.tail = last_poss.tail
                
                # Add this item to existing_items to prevent duplicates if the same ID appears multiple times
                existing_items.add(item_id)
                
                last_poss = new_poss
                next_index += 1
                items_added += 1
                
            # Mark changes as unsaved
            self.main_window.unsaved_label.config(text="Unsaved Changes")
            
            # Update the loadout display
            self._update_navi_loadout_display(profile)
            
            # Show final summary with information about duplicates
            if items_added > 0:
                messagebox.showinfo("DLC Items Added", 
                                f"Successfully added {items_added} Na'vi DLC items to your inventory.\n"
                                f"Skipped {duplicates_found} items that were already in your inventory.")
            else:
                messagebox.showinfo("No Items Added", 
                                "All Na'vi DLC items are already in your inventory.")
            
        except Exception as e:
            self.logger.error(f"Error adding Na'vi DLC items: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to add Na'vi DLC items: {str(e)}")

    def _create_readonly_entry(self, parent, initial_value="0", width=8):
        """Create an entry field that cannot be edited by typing but can be programmatically updated"""
        entry = ttk.Entry(parent, width=width)
        entry.insert(0, initial_value)
        
        # Disable direct user editing
        def disable_editing(event):
            return "break"
        
        # Bind all events that could modify the entry content
        entry.bind("<Key>", disable_editing)
        entry.bind("<KeyPress>", disable_editing)
        entry.bind("<KeyRelease>", disable_editing)
        
        # Still allow selection and copying
        entry.bind("<Control-c>", lambda e: None)  # Allow copying
        
        return entry

    def _create_weapon_dropdown(self, parent_frame, slot_name, slot_index, is_navi=False, x=0, y=0):
        """Create a dropdown for weapon selection with improved organization"""
        # Create a frame to hold the controls
        slot_frame = ttk.Frame(parent_frame)
        slot_frame.place(x=x, y=y, width=535, height=30)
        
        # Label for the slot
        ttk.Label(slot_frame, text=f"{slot_name}:").pack(side=tk.LEFT, padx=2)
        
        # Get the list of weapons based on faction
        all_weapons = self._get_faction_weapons(is_navi)
        
        # Create the dropdown with weapon names
        combo = ttk.Combobox(slot_frame, values=list(all_weapons.values()), width=34, state="readonly")
        combo.pack(side=tk.LEFT, padx=2)
        combo.set("-Empty-")
        block_combobox_mousewheel(combo)
        
        # Create ammo controls
        ammo_entry, infinite_var, infinite_check = self._create_ammo_controls(slot_frame)
        
        # Create clip display
        clip_label = self._create_clip_display(slot_frame)
        
        # Store everything in a weapon slot data dictionary
        weapon_slot_data = {
            "dropdown": combo,
            "ammo_entry": ammo_entry,
            "clip_entry": clip_label,
            "infinite_var": infinite_var,
            "infinite_check": infinite_check,
            "all_weapons": all_weapons
        }
        
        # Choose the right list to modify and ensure it has enough elements
        weapons_array = self.navi_weapon_slots if is_navi else self.weapon_slots
        while len(weapons_array) <= slot_index:
            weapons_array.append(None)
        
        # Store the data
        weapons_array[slot_index] = weapon_slot_data
        
        # Set up event bindings
        self._setup_weapon_bindings(combo, infinite_check, ammo_entry, slot_index, is_navi)
        
        return weapon_slot_data

    def _get_faction_weapons(self, is_navi=False):
        """Get the list of weapons for a specific faction"""
        # Define which weapon IDs to include
        if is_navi:
            weapon_ids = self._get_navi_weapon_ids()
        else:
            weapon_ids = self._get_rda_weapon_ids()
        
        # Define ammo item IDs to exclude
        ammo_ids = self._get_ammo_ids()
        
        # Build the weapons dictionary
        all_weapons = {}
        for item_id in weapon_ids:
            if item_id in self.item_mappings and item_id not in ammo_ids:
                all_weapons[item_id] = self.item_mappings[item_id]
        
        # Debug output
        faction_name = "Navi" if is_navi else "RDA"
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"\n=== {faction_name} WEAPONS DROPDOWN CONTENTS ===")
            for weapon_id, weapon_name in all_weapons.items():
                self.logger.debug(f"  {weapon_id}: {weapon_name}")
            self.logger.debug(f"Total {faction_name} weapons: {len(all_weapons)}")
        
        return all_weapons

    def _get_navi_weapon_ids(self):
        """Get the list of Navi weapon IDs"""
        return [
            # Dual Blade
            "2740507591", "2917611312", "2813685095", "2948460035",
            # DLC Dual Blade
            "2285146948", "2257287091", "3543126973", "2007498681",
            # Crossbow
            "1662469074", "1839769381", "3400058396", "1514231420",
            # DLC Crossbow
            "3138212456", "2486913109", "2589205711", "1886472672",
            # M30 Machine Gun
            "1304439874", "1132447925", "982090295", "958613249",
            # ELITE M30 Machine Gun
            "1048019290", "172062103", "921966990",
            # Club
            "4093397293", "4249071066", "3879387803", "240531571",
            # DLC Axe
            "1958996617", "2689671946", "1639187137", "2934884349",
            # Fighting Staff
            "2255793432", "2295024111", "2986118748", "3960574385",
            # DLC Fighting Staff
            "1828119782", "1648951313", "3943944974", "3139393077",
            # Bow
            "291262189", "535013914", "2092736556", "371977402",
            # DLC Bow
            "1817446146", "1659626485", "1282693004", "435991093"
        ]

    def _get_rda_weapon_ids(self):
        """Get the list of RDA weapon IDs"""
        return [
            # Dual Wasp Pistol
            "1042188764", "815885611", "760079057", "999316102",
            # DLC Dual Wasp Pistols
            "3859060838", "3904601233", "102867538", "749353518",
            # Standard Issue Rifle
            "1130814347", "1306083196", "3628031700", "1146928137",
            # DLC Standard Issue Rifles
            "2850329205", "2807789186", "2194670470", "324172685",
            # Combat Shotgun
            "2313824646", "2270547313", "2789519003", "1919695864",
            # DLC Combat Shotguns
            "2664450350", "2423238105", "2120138529", "4289908838",
            # Assault Rifle
            "2397981034", "2152836509", "268371112", "466145020",
            # DLC Assault Rifles
            "3655372526", "3613354521", "3850194262", "2109370248",
            # M60 Machine Gun
            "85991974", "195020497", "1881065336", "1796958374",
            # DLC Machine Guns
            "2015914953", "1989644094", "1087779032", "1691104809",
            # Grenade Launcher
            "94681171", "186342564", "1349633617", "4018216358",
            # DLC Grenade Launchers
            "2157668310", "2384757537", "3441856033", "3043901684",
            # Flamethrower
            "2529862352", "2557822503", "609450705", "2288255787",
            # DLC Flamethrowers
            "3250873684", "3480977827", "3469816623", "3994460767",
            # Nail Gun
            "2548581230", "2572658585", "143378107", "1911864170",
            # DLC Nail Guns
            "2161255366", "2389559089", "3499218689", "4230631668"
        ]
        
    def _get_ammo_ids(self):
        """Get the list of ammo item IDs to exclude from weapon dropdowns"""
        return [
            # RDA Ammo
            "4029490973",  # Rifle Ammo
            "2220072441",  # Shotgun Ammo
            "3183424835",  # SMG Ammo
            "3227899887",  # Grenade Ammo
            "4198025789",  # Rocket Ammo
            "2442117335",  # LMG Ammo
            "3819023512",  # Heavy Ammo
            
            # Navi Ammo
            "1042656528",  # Arrow Ammo
            "435601722",   # Spear Ammo
            "3069972540"   # Poison Ammo
        ]

    def _create_ammo_controls(self, parent_frame):
        """Create the ammo controls (entry field and infinite checkbox)"""
        # Create a frame for ammo control
        ammo_frame = ttk.Frame(parent_frame)
        ammo_frame.pack(side=tk.LEFT, padx=2)
        
        # Label and entry for ammo
        ttk.Label(ammo_frame, text="Ammo:").pack(side=tk.LEFT)
        ammo_entry = ttk.Entry(ammo_frame, width=8)
        ammo_entry.insert(0, "0")
        ammo_entry.pack(side=tk.LEFT, padx=2)
        
        # Add infinite ammo checkbox
        infinite_var = tk.BooleanVar()
        infinite_check = ttk.Checkbutton(
            ammo_frame, 
            text="∞", 
            variable=infinite_var,
            style="TCheckbutton",
            takefocus=0  # Prevent keyboard focus
        )
        infinite_check.pack(side=tk.LEFT, padx=2)
        
        return ammo_entry, infinite_var, infinite_check

    def _create_clip_display(self, parent_frame):
        """Create the clip size display label"""
        clip_frame = ttk.Frame(parent_frame)
        clip_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(clip_frame, text="Clip:").pack(side=tk.LEFT)
        
        # Use a label for clip size
        clip_label = ttk.Label(clip_frame, text="0", width=5)
        clip_label.pack(side=tk.LEFT, padx=2)
        
        return clip_label

    def _setup_weapon_bindings(self, combo, infinite_check, ammo_entry, slot_index, is_navi):
        """Set up event bindings for weapon-related UI elements"""
        # Bind dropdown selection
        if is_navi:
            combo.bind('<<ComboboxSelected>>', 
                    lambda e, idx=slot_index: self._on_navi_weapon_selected(e, idx))
        else:
            combo.bind('<<ComboboxSelected>>', 
                    lambda e, idx=slot_index: self._on_weapon_selected(e, idx))
        
        # Bind infinite ammo checkbox
        infinite_check.bind('<ButtonRelease-1>', 
                        lambda e, idx=slot_index, navi=is_navi: 
                        self._toggle_infinite_ammo(e, idx, navi))
        
        # Bind ammo entry for updating ammo value
        ammo_entry.bind('<KeyRelease>', 
                    lambda e, idx=slot_index, navi=is_navi: 
                    self._update_ammo_value(e, idx, navi))

    # Also add a method to programmatically update entry values
    def _update_entry_value(self, entry, value):
        """Update an entry value programmatically, bypassing the read-only restriction"""
        entry.configure(state="normal")  # Temporarily enable
        entry.delete(0, tk.END)
        entry.insert(0, str(value))
        entry.configure(state="readonly")  # Set back to readonly

    def _update_clip_value(self, event, slot_index, is_navi=False):
        """Update the clip size value in the XML when changed in the UI"""
        try:
            # Get the new clip value - we no longer get it from UI since it's now read-only
            # Instead, get it from the weapon data
            # This method is now only called programmatically, not from user interaction
            
            clip_label = self.navi_weapon_slots[slot_index]["clip_entry"] if is_navi else self.weapon_slots[slot_index]["clip_entry"]
            new_clip = clip_label.cget("text")
            
            # Validate as integer
            try:
                new_clip = int(new_clip)
            except ValueError:
                # Not a valid number, ignore
                return
                            
            # Update the XML if valid
            if self.main_window.tree is not None:
                profile = self.main_window.tree.getroot().find("PlayerProfile")
                if profile is not None:
                    if is_navi:
                        # Find the Na'vi weapon we're updating
                        avatar = profile.find("Possessions_Avatar")
                        if avatar is None:
                            return
                                        
                        equipped = avatar.find("EquippedWeapons")
                        if equipped is None:
                            return
                                        
                        slots = equipped.findall("Slot")
                        if slot_index >= len(slots):
                            return
                                    
                        # Get the possession index
                        poss_idx = slots[slot_index].get("MainHand_PossIdx", "-1")
                        if poss_idx == "-1":
                            return
                                        
                        # Find the weapon possession
                        possessions = avatar.find("Posessions")
                        if possessions is None:
                            return
                                        
                        # First get the weapon to determine its ammo type
                        weapon_poss = None
                        for poss in possessions.findall("Poss"):
                            if poss.get("Index") == poss_idx:
                                weapon_poss = poss
                                break
                                
                        if weapon_poss is None:
                            return
                        
                        # Only update NbInClip in the corresponding ammo item
                        ammo_type = weapon_poss.get("crc_AmmoType", "4294967295")
                        if ammo_type != "4294967295":  # Skip for infinite ammo weapons
                            ammo_updated = False
                            for ammo_poss in possessions.findall("Poss"):
                                if ammo_poss.get("crc_ItemID") == ammo_type:
                                    ammo_poss.set("NbInClip", str(new_clip))
                                    self.logger.debug(f"Updated Na'vi ammo clip to {new_clip}")
                                    ammo_updated = True
                                    break
                            
                            # If ammo item not found, create it
                            if not ammo_updated:
                                self._ensure_ammo_exists(possessions, ammo_type, "100")
                                # Find the newly created ammo and set its clip
                                for ammo_poss in possessions.findall("Poss"):
                                    if ammo_poss.get("crc_ItemID") == ammo_type:
                                        ammo_poss.set("NbInClip", str(new_clip))
                                        self.logger.debug(f"Created and updated Na'vi ammo clip to {new_clip}")
                                        break
                    else:
                        # RDA weapon update - same logic as above
                        # [rest of the method unchanged]
                        soldier = profile.find("Possessions_Soldier")
                        if soldier is None:
                            return
                                        
                        equipped = soldier.find("EquippedWeapons")
                        if equipped is None:
                            return
                                        
                        slots = equipped.findall("Slot")
                        if slot_index >= len(slots):
                            return
                                    
                        # Get the possession index
                        poss_idx = slots[slot_index].get("MainHand_PossIdx", "-1")
                        if poss_idx == "-1":
                            return
                                        
                        # Find the weapon possession
                        possessions = soldier.find("Posessions")
                        if possessions is None:
                            return
                                
                        # First get the weapon to determine its ammo type
                        weapon_poss = None
                        for poss in possessions.findall("Poss"):
                            if poss.get("Index") == poss_idx:
                                weapon_poss = poss
                                break
                                
                        if weapon_poss is None:
                            return
                        
                        # Only update NbInClip in the corresponding ammo item
                        ammo_type = weapon_poss.get("crc_AmmoType", "4294967295")
                        if ammo_type != "4294967295":  # Skip for infinite ammo weapons
                            ammo_updated = False
                            for ammo_poss in possessions.findall("Poss"):
                                if ammo_poss.get("crc_ItemID") == ammo_type:
                                    ammo_poss.set("NbInClip", str(new_clip))
                                    self.logger.debug(f"Updated RDA ammo clip to {new_clip}")
                                    ammo_updated = True
                                    break
                            
                            # If ammo item not found, create it
                            if not ammo_updated:
                                self._ensure_ammo_exists(possessions, ammo_type, "100")
                                # Find the newly created ammo and set its clip
                                for ammo_poss in possessions.findall("Poss"):
                                    if ammo_poss.get("crc_ItemID") == ammo_type:
                                        ammo_poss.set("NbInClip", str(new_clip))
                                        self.logger.debug(f"Created and updated RDA ammo clip to {new_clip}")
                                        break
                    
                    # Mark as unsaved
                    self.main_window.unsaved_label.config(text="Unsaved Changes")
        except Exception as e:
            self.logger.error(f"Error updating clip value: {str(e)}")

    def _toggle_infinite_ammo(self, event, slot_index, is_navi=False):
        """Handle toggling infinite ammo for a weapon"""
        try:
            # Check if save file is loaded
            if self.main_window.tree is None:
                self.logger.warning("Attempted to toggle infinite ammo with no save file loaded")
                messagebox.showerror("Error", "No save file loaded. Please load a save file first.")
                return
                
            # Get the slot data
            slot_data = self.navi_weapon_slots[slot_index] if is_navi else self.weapon_slots[slot_index]
            
            # Get the current weapon from the dropdown
            weapon_name = slot_data["dropdown"].get()
            if weapon_name == "-Empty-":
                return
            
            # Find weapon ID from name
            weapon_id = None
            for id, name in slot_data["all_weapons"].items():
                if name == weapon_name:
                    weapon_id = id
                    break
            
            if weapon_id is None:
                return
            
            # NEW CODE: Check if this is a melee or inherently infinite weapon
            is_melee = any(melee_kw in weapon_name.lower() for melee_kw in 
                        ["club", "blade", "axe", "staff", "spear", "knife", "sword"])
            
            is_inherent_infinite = any(pistol_term in weapon_name.lower() for pistol_term in ["wasp pistol"])
            
            # If it's a special weapon that should have fixed ammo settings, block the toggle
            if is_melee or is_inherent_infinite:
                # Reset checkbox state back to what it was (checked for these weapons)
                slot_data["infinite_var"].set(True)
                return
            
            # For regular weapons, proceed with the toggle as before
            # We need to wait a moment for the checkbox to update
            self.parent.after(50, lambda: self._apply_infinite_ammo(slot_index, is_navi, weapon_id))
            
        except Exception as e:
            self.logger.error(f"Error toggling infinite ammo: {str(e)}")
            messagebox.showerror("Error", f"Failed to toggle infinite ammo: {str(e)}")

    def _apply_infinite_ammo(self, slot_index, is_navi, weapon_id):
        """Apply the infinite ammo setting after checkbox toggle"""
        try:
            # Get the slot data
            slot_data = self.navi_weapon_slots[slot_index] if is_navi else self.weapon_slots[slot_index]
            
            # Get the state of the checkbox
            infinite_enabled = slot_data["infinite_var"].get()
            self.logger.debug(f"Toggling infinite ammo to {infinite_enabled} for weapon ID {weapon_id}")
            
            # Update the XML if a save file is loaded
            if self.main_window.tree is not None:
                profile = self.main_window.tree.getroot().find("PlayerProfile")
                if profile is not None:
                    if is_navi:
                        # Find the Na'vi weapon we're updating
                        avatar = profile.find("Possessions_Avatar")
                        if avatar is None:
                            self.logger.error("Possessions_Avatar not found")
                            return
                                    
                        equipped = avatar.find("EquippedWeapons")
                        if equipped is None:
                            self.logger.error("EquippedWeapons not found")
                            return
                                    
                        slots = equipped.findall("Slot")
                        if slot_index >= len(slots):
                            self.logger.error(f"Slot index {slot_index} out of range")
                            return
                                    
                        # Get the possession index
                        poss_idx = slots[slot_index].get("MainHand_PossIdx", "-1")
                        if poss_idx == "-1":
                            self.logger.error("No weapon equipped in this slot")
                            return
                                    
                        # Find the possession
                        possessions = avatar.find("Posessions")
                        if possessions is None:
                            self.logger.error("Posessions not found")
                            return
                            
                        # Get the weapon possession
                        weapon_poss = None
                        for poss in possessions.findall("Poss"):
                            if poss.get("Index") == poss_idx:
                                weapon_poss = poss
                                break
                            
                        if weapon_poss is None:
                            self.logger.error("Weapon possession not found")
                            return
                                
                        # Get the ammo type but DO NOT CHANGE IT
                        ammo_type = weapon_poss.get("crc_AmmoType", "4294967295")
                        
                        # If toggling infinite ammo, ONLY set the clip size
                        if infinite_enabled:
                            self.logger.debug("Setting NbInClip to 999999 (NOT changing ammo type)")
                            weapon_poss.set("NbInClip", "999999")
                        else:
                            # Reset clip to a reasonable value
                            weapon_poss.set("NbInClip", "100")
                            
                        # Update ammo item if it exists (but don't create if not found)
                        if ammo_type != "4294967295":
                            for ammo_poss in possessions.findall("Poss"):
                                if ammo_poss.get("crc_ItemID") == ammo_type:
                                    if infinite_enabled:
                                        ammo_poss.set("NbInStack", "999999")
                                    else:
                                        ammo_poss.set("NbInStack", "100")
                                    break
                    else:
                        # Handle RDA weapon
                        soldier = profile.find("Possessions_Soldier")
                        if soldier is None:
                            self.logger.error("Possessions_Soldier not found")
                            return
                                    
                        equipped = soldier.find("EquippedWeapons")
                        if equipped is None:
                            self.logger.error("EquippedWeapons not found")
                            return
                                    
                        slots = equipped.findall("Slot")
                        if slot_index >= len(slots):
                            self.logger.error(f"Slot index {slot_index} out of range")
                            return
                                    
                        # Get the possession index
                        poss_idx = slots[slot_index].get("MainHand_PossIdx", "-1")
                        if poss_idx == "-1":
                            self.logger.error("No weapon equipped in this slot")
                            return
                                    
                        # Find the possession
                        possessions = soldier.find("Posessions")
                        if possessions is None:
                            self.logger.error("Posessions not found")
                            return
                            
                        # Get the weapon possession
                        weapon_poss = None
                        for poss in possessions.findall("Poss"):
                            if poss.get("Index") == poss_idx:
                                weapon_poss = poss
                                break
                            
                        if weapon_poss is None:
                            self.logger.error("Weapon possession not found")
                            return
                                
                        # Get the ammo type but DO NOT CHANGE IT
                        ammo_type = weapon_poss.get("crc_AmmoType", "4294967295")
                        
                        # If toggling infinite ammo, ONLY set the clip size
                        if infinite_enabled:
                            self.logger.debug("Setting NbInClip to 999999 (NOT changing ammo type)")
                            weapon_poss.set("NbInClip", "999999")
                        else:
                            # Reset clip to a reasonable value
                            weapon_poss.set("NbInClip", "100")
                            
                        # Update ammo item if it exists (but don't create if not found)
                        if ammo_type != "4294967295":
                            for ammo_poss in possessions.findall("Poss"):
                                if ammo_poss.get("crc_ItemID") == ammo_type:
                                    if infinite_enabled:
                                        ammo_poss.set("NbInStack", "999999")
                                    else:
                                        ammo_poss.set("NbInStack", "100")
                                    break
                    
                    # Update ammo entry state
                    ammo_entry = slot_data["ammo_entry"]
                    if infinite_enabled:
                        # Set ammo to 999999 and DISABLE the field
                        ammo_entry.delete(0, tk.END)
                        ammo_entry.insert(0, "999999")
                        ammo_entry.configure(state="disabled")
                        self.logger.debug("Set UI ammo field to 999999 and disabled")
                    else:
                        # Set ammo to 100 and keep field NORMAL (enabled)
                        ammo_entry.delete(0, tk.END)
                        ammo_entry.insert(0, "100")
                        ammo_entry.configure(state="normal")
                        self.logger.debug("Set UI ammo field to 100 and enabled")
                    
                    # Mark as unsaved
                    self.main_window.unsaved_label.config(text="Unsaved Changes")
        
        except Exception as e:
            self.logger.error(f"Error applying infinite ammo: {str(e)}", exc_info=True)

    def _update_ammo_directly(self, profile, is_navi, slot_index, new_ammo_value):
        """Direct method to update ammo in the save file for debugging and manual updates"""
        try:
            self.logger.debug(f"Directly updating ammo to {new_ammo_value} for {'Navi' if is_navi else 'RDA'} slot {slot_index}")

            if is_navi:
                # Find the Na'vi weapon
                avatar = profile.find("Possessions_Avatar")
                if avatar is None:
                    self.logger.error("Possessions_Avatar not found")
                    return False
                        
                equipped = avatar.find("EquippedWeapons")
                if equipped is None:
                    self.logger.error("EquippedWeapons not found")
                    return False
                        
                slots = equipped.findall("Slot")
                if slot_index >= len(slots):
                    self.logger.error(f"Slot index {slot_index} out of range")
                    return False
                        
                # Get the possession index
                poss_idx = slots[slot_index].get("MainHand_PossIdx", "-1")
                if poss_idx == "-1":
                    self.logger.error("No weapon equipped in this slot")
                    return False
                        
                # Find the weapon possession
                possessions = avatar.find("Posessions")
                if possessions is None:
                    self.logger.error("Posessions not found")
                    return False
                
                # Find the weapon
                weapon_poss = None
                for poss in possessions.findall("Poss"):
                    if poss.get("Index") == poss_idx:
                        weapon_poss = poss
                        break
                
                if weapon_poss is None:
                    self.logger.error("Weapon possession not found")
                    return False
                
                # Get ammo type
                ammo_type = weapon_poss.get("crc_AmmoType", "4294967295")
                if ammo_type == "4294967295":
                    self.logger.error("Weapon has infinite ammo or no ammo")
                    return False
                
                # IMPORTANT NEW CODE: Also update the weapon's own clip value
                clip_value = min(int(new_ammo_value), 100)  # Set clip to whatever is in ammo, max 100
                weapon_poss.set("NbInClip", str(clip_value))
                self.logger.debug(f"Updated weapon clip to {clip_value}")
                
                # Find and update ammo possession
                ammo_updated = False
                for poss in possessions.findall("Poss"):
                    if poss.get("crc_ItemID") == ammo_type:
                        # Update BOTH ammo attributes
                        poss.set("NbInStack", str(new_ammo_value))
                        poss.set("NbInClip", str(clip_value))
                        ammo_updated = True
                        self.logger.debug(f"Updated Na'vi ammo possession to {new_ammo_value}")
                        break
                
                # If we get here and ammo wasn't found - create it
                if not ammo_updated:
                    self._ensure_ammo_exists(possessions, ammo_type, str(new_ammo_value))
                
                # ADDITIONAL UPDATES - Try updating all possible ammo locations
                # Find all items that match the ammo type and update them all
                for poss in possessions.findall("Poss"):
                    if poss.get("crc_ItemID") == ammo_type or poss.get("crc_AmmoType") == ammo_type:
                        poss.set("NbInStack", str(new_ammo_value))
                        self.logger.debug(f"Updated additional ammo possession: {poss.get('Index')}")

                self.logger.debug(f"Successfully updated Na'vi ammo to {new_ammo_value}")
                return True
                
            else:
                # RDA weapon update - similar approach with additional updates
                soldier = profile.find("Possessions_Soldier")
                if soldier is None:
                    self.logger.error("Possessions_Soldier not found")
                    return False
                        
                equipped = soldier.find("EquippedWeapons")
                if equipped is None:
                    self.logger.error("EquippedWeapons not found")
                    return False
                        
                slots = equipped.findall("Slot")
                if slot_index >= len(slots):
                    self.logger.error(f"Slot index {slot_index} out of range")
                    return False
                        
                # Get the possession index
                poss_idx = slots[slot_index].get("MainHand_PossIdx", "-1")
                if poss_idx == "-1":
                    self.logger.error("No weapon equipped in this slot")
                    return False
                        
                # Find the weapon possession
                possessions = soldier.find("Posessions")
                if possessions is None:
                    self.logger.error("Posessions not found")
                    return False
                
                # Find the weapon
                weapon_poss = None
                for poss in possessions.findall("Poss"):
                    if poss.get("Index") == poss_idx:
                        weapon_poss = poss
                        break
                
                if weapon_poss is None:
                    self.logger.error("Weapon possession not found")
                    return False
                
                # Get ammo type
                ammo_type = weapon_poss.get("crc_AmmoType", "4294967295")
                if ammo_type == "4294967295":
                    self.logger.error("Weapon has infinite ammo or no ammo")
                    return False
                
                # IMPORTANT NEW CODE: Also update the weapon's own clip value
                clip_value = min(int(new_ammo_value), 100)  # Set clip to whatever is in ammo, max 100
                weapon_poss.set("NbInClip", str(clip_value))
                self.logger.debug(f"Updated weapon clip to {clip_value}")
                
                # Find and update ammo possession
                ammo_updated = False
                for poss in possessions.findall("Poss"):
                    if poss.get("crc_ItemID") == ammo_type:
                        # Update BOTH ammo attributes
                        poss.set("NbInStack", str(new_ammo_value))
                        poss.set("NbInClip", str(clip_value))
                        ammo_updated = True
                        self.logger.debug(f"Updated RDA ammo possession to {new_ammo_value}")
                        break
                
                # If we get here and ammo wasn't found - create it
                if not ammo_updated:
                    self._ensure_ammo_exists(possessions, ammo_type, str(new_ammo_value))
                
                # ADDITIONAL UPDATES - Try updating all possible ammo locations
                # Find all items that match the ammo type and update them all
                for poss in possessions.findall("Poss"):
                    if poss.get("crc_ItemID") == ammo_type or poss.get("crc_AmmoType") == ammo_type:
                        poss.set("NbInStack", str(new_ammo_value))
                        self.logger.debug(f"Updated additional ammo possession: {poss.get('Index')}")

                self.logger.debug(f"Successfully updated RDA ammo to {new_ammo_value}")
                return True
        
        except Exception as e:
            self.logger.error(f"Error in direct ammo update: {str(e)}", exc_info=True)
            return False
        
    def _ensure_ammo_exists(self, possessions, ammo_type, amount="100"):
        """Ensure ammo exists in inventory when disabling infinite ammo"""
        # Skip if ammo type is the 'no ammo' value
        if ammo_type == "4294967295":
            self.logger.debug("Skipping ammo creation for infinite ammo weapon")
            return
                
        # Check if ammo already exists
        ammo_exists = False
        for poss in possessions.findall("Poss"):
            if poss.get("crc_ItemID") == ammo_type:
                ammo_exists = True
                # Set the ammo to the requested amount
                poss.set("NbInStack", amount)
                poss.set("NbInClip", "0")  # Also ensure clip value is set
                poss.set("NoveltyState", "2")  # Make sure novelty state is right
                self.logger.debug(f"Updated existing ammo of type {ammo_type} to {amount}")
                break
                    
        if not ammo_exists:
            self.logger.debug(f"Creating new ammo of type {ammo_type} with amount {amount}")
            # Need to add ammo to inventory
            # Find next available index
            max_index = -1
            for poss in possessions.findall("Poss"):
                idx = int(poss.get("Index", "0"))
                if idx > max_index:
                    max_index = idx
                        
            # Create new possession for ammo
            new_index = max_index + 1
            self.logger.debug(f"Creating new ammo at index {new_index}")
            new_ammo = ET.SubElement(possessions, "Poss")
            new_ammo.set("Index", str(new_index))
            new_ammo.set("crc_ItemID", ammo_type)
            new_ammo.set("NbInStack", amount)
            new_ammo.set("NbInClip", "0")
            new_ammo.set("crc_AmmoType", "4294967295")
            new_ammo.set("NoveltyState", "2")
            self.logger.debug(f"New ammo created successfully")

    def _update_ammo_value(self, event, slot_index, is_navi=False):
        """Update the ammo value in the XML when changed in the UI"""
        try:
            # Check if save file is loaded
            if self.main_window.tree is None:
                self.logger.warning("Attempted to update ammo value with no save file loaded")
                messagebox.showerror("Error", "No save file loaded. Please load a save file first.")
                # Reset the entry to its original value
                ammo_entry = self.navi_weapon_slots[slot_index]["ammo_entry"] if is_navi else self.weapon_slots[slot_index]["ammo_entry"]
                ammo_entry.delete(0, tk.END)
                ammo_entry.insert(0, "0")
                return
                
            # Get the new ammo value
            ammo_entry = self.navi_weapon_slots[slot_index]["ammo_entry"] if is_navi else self.weapon_slots[slot_index]["ammo_entry"] 
            new_ammo = ammo_entry.get()
            
            # Skip if the entry is disabled (for infinite ammo weapons)
            if str(ammo_entry.cget('state')) == 'disabled':
                return
            
            # Validate as integer
            try:
                new_ammo = int(new_ammo)
                faction = "Navi" if is_navi else "RDA"
                print(f"AMMO_DEBUG: Setting {faction} weapon ammo to {new_ammo}")
            except ValueError:
                return
                                        
            # Update the XML if valid
            profile = self.main_window.tree.getroot().find("PlayerProfile")
            if profile is not None:
                # Find the weapon possession
                if is_navi:
                    avatar = profile.find("Possessions_Avatar")
                    if avatar is None:
                        return
                            
                    equipped = avatar.find("EquippedWeapons")
                    if equipped is None:
                        return
                            
                    slots = equipped.findall("Slot")
                    if slot_index >= len(slots):
                        return
                    
                    poss_idx = slots[slot_index].get("MainHand_PossIdx", "-1")
                    possessions = avatar.find("Posessions")
                else:
                    soldier = profile.find("Possessions_Soldier")
                    if soldier is None:
                        return
                            
                    equipped = soldier.find("EquippedWeapons")
                    if equipped is None:
                        return
                            
                    slots = equipped.findall("Slot")
                    if slot_index >= len(slots):
                        return
                    
                    poss_idx = slots[slot_index].get("MainHand_PossIdx", "-1")
                    possessions = soldier.find("Posessions")
                
                if possessions is None or poss_idx == "-1":
                    return
                
                # Find weapon possession
                weapon_poss = None
                for poss in possessions.findall("Poss"):
                    if poss.get("Index") == poss_idx:
                        weapon_poss = poss
                        break
                
                if weapon_poss is None:
                    return
                
                # DIRECT APPROACH: Set both values that could affect ammo
                weapon_poss.set("NbInClip", str(new_ammo))
                print(f"AMMO_DEBUG: Set weapon NbInClip to {new_ammo}")
                
                # Get the ammo type
                ammo_type = weapon_poss.get("crc_AmmoType", "4294967295")
                if ammo_type != "4294967295":
                    ammo_found = False
                    for ammo_poss in possessions.findall("Poss"):
                        if ammo_poss.get("crc_ItemID") == ammo_type:
                            ammo_poss.set("NbInStack", str(new_ammo))
                            print(f"AMMO_DEBUG: Set ammo NbInStack to {new_ammo}")
                            ammo_found = True
                            break
                    
                    if not ammo_found:
                        self._ensure_ammo_exists(possessions, ammo_type, str(new_ammo))
                        print(f"AMMO_DEBUG: Created new ammo with {new_ammo}")
                
                # Force immediate save
                print("AMMO_DEBUG: Marking file as having unsaved changes")
                self.main_window.unsaved_label.config(text="Unsaved Changes")
        except Exception as e:
            print(f"AMMO_DEBUG ERROR: {str(e)}")
            messagebox.showerror("Error", f"Failed to update ammo value: {str(e)}")

    def _can_have_infinite_ammo(self, weapon_id):
        """Determine if a weapon can have infinite ammo"""
        # List of weapon IDs that can use infinite ammo
        infinite_capable = [
            "1042188764",  # Dual Wasp Pistol I
            "815885611",   # Dual Wasp Pistol II
            "760079057",   # Dual Wasp Pistol III
            "999316102",   # Dual Wasp Pistol IV
            "1304439874",  # Staff (melee)
            "2813685095"   # War Club (melee)
        ]
        return weapon_id in infinite_capable

    def _reset_weapon_ammo(self):
        """Reset all weapons to their original ammo types"""
        self.logger.debug("Resetting all weapons to original ammo types")
        
        if self.main_window.tree is None:
            self.logger.warning("No save file loaded when attempting to reset weapon ammo types")
            messagebox.showerror("Error", "No save file loaded. Please load a save file first.")
            return
        
        profile = self.main_window.tree.getroot().find("PlayerProfile")
        if profile is None:
            self.logger.warning("No player profile found when attempting to reset weapon ammo types")
            messagebox.showerror("Error", "No valid player profile found in the loaded save file.")
            return
        
        # Reset RDA weapons
        soldier = profile.find("Possessions_Soldier")
        if soldier is not None:
            possessions = soldier.find("Posessions")
            if possessions is not None:
                # Reset each weapon to its correct ammo type
                for poss in possessions.findall("Poss"):
                    weapon_id = poss.get("crc_ItemID")
                    # Only process actual weapons
                    if weapon_id in self.item_mappings:
                        item_name = self.item_mappings[weapon_id]
                        if any(weapon_keyword in item_name.lower() for weapon_keyword in 
                            ["pistol", "rifle", "shotgun", "machine gun", "launcher", "thrower", "nail gun"]):
                            # Set the correct ammo type
                            correct_ammo_type = self._get_ammo_type_for_weapon(weapon_id)
                            current_ammo_type = poss.get("crc_AmmoType", "")
                            
                            # Only update if needed
                            if current_ammo_type != correct_ammo_type:
                                poss.set("crc_AmmoType", correct_ammo_type)
                                self.logger.debug(f"Reset RDA weapon {item_name} to ammo type {correct_ammo_type}")
        
        # Reset Na'vi weapons
        avatar = profile.find("Possessions_Avatar")
        if avatar is not None:
            possessions = avatar.find("Posessions")
            if possessions is not None:
                # Reset each weapon to its correct ammo type
                for poss in possessions.findall("Poss"):
                    weapon_id = poss.get("crc_ItemID")
                    # Only process actual weapons
                    if weapon_id in self.item_mappings:
                        item_name = self.item_mappings[weapon_id]
                        if any(weapon_keyword in item_name.lower() for weapon_keyword in 
                            ["bow", "staff", "spear", "club", "blade", "crossbow", "axe"]):
                            # Set the correct ammo type
                            correct_ammo_type = self._get_ammo_type_for_weapon(weapon_id)
                            current_ammo_type = poss.get("crc_AmmoType", "")
                            
                            # Only update if needed
                            if current_ammo_type != correct_ammo_type:
                                poss.set("crc_AmmoType", correct_ammo_type)
                                self.logger.debug(f"Reset Na'vi weapon {item_name} to ammo type {correct_ammo_type}")
        
        # Update the UI to reflect changes
        self._update_loadout_display(profile)
        self._update_navi_loadout_display(profile)
        
        # Mark as unsaved
        self.main_window.unsaved_label.config(text="Unsaved Changes")
        
        # Show confirmation
        messagebox.showinfo("Reset Complete", "All weapons have been reset to their original ammo types.")

    def _preserve_faction(self, profile, faction_value="1"):
        """Ensure faction stays preserved (prevents resets to Undecided)"""
        # Look for Metagame directly from the main window's tree
        root = self.main_window.tree.getroot()
        metagame = root.find("Metagame")
        
        if metagame is not None:
            # Always set the faction to the specified value
            current = metagame.get("PlayerFaction")
            if current != faction_value:
                print(f"DEBUG: Fixing faction reset. Changed from {current} to {faction_value}")
                metagame.set("PlayerFaction", faction_value)
                
                # Also update the UI dropdown to match
                faction_map = {"0": "Undecided", "1": "Na'vi", "2": "RDA"}
                if "PlayerFaction" in self.entries:
                    self.entries["PlayerFaction"].set(faction_map.get(faction_value, "Undecided"))

    def _update_weapon(self, profile, slot_index, weapon_id, is_navi=False):
        """
        Unified method to update weapons for both RDA and Na'vi across different save formats.
        
        Args:
            profile (ET.Element): The PlayerProfile element
            slot_index (int): The weapon slot index to update
            weapon_id (str): The weapon ID to set
            is_navi (bool): True for Na'vi weapons, False for RDA
        """
        self.logger.debug(f"Updating {'Navi' if is_navi else 'RDA'} weapon - Slot: {slot_index}, Weapon ID: {weapon_id}")
        
        # Find the Possessions element or create it
        faction_elem_name = "Possessions_Avatar" if is_navi else "Possessions_Soldier"
        faction_elem = profile.find(faction_elem_name)
        if faction_elem is None:
            faction_elem = ET.SubElement(profile, faction_elem_name)
            self.logger.debug(f"Created new {faction_elem_name} element")
            
        # Find the EquippedWeapons element or create it
        equipped = faction_elem.find("EquippedWeapons")
        if equipped is None:
            equipped = ET.SubElement(faction_elem, "EquippedWeapons")
            self.logger.debug(f"Created new EquippedWeapons element")
        
        # Make sure we have enough slots
        slots = equipped.findall("Slot")
        while len(slots) <= slot_index:
            new_slot = ET.SubElement(equipped, "Slot")
            new_slot.set("MainHand_PossIdx", "-1")
            new_slot.set("OffHand_PossIdx", "-1")
            slots = equipped.findall("Slot")
            self.logger.debug(f"Created new weapon Slot at position {len(slots)-1}")
        
        # Find Posessions element or create it
        possessions = faction_elem.find("Posessions")
        if possessions is None:
            possessions = ET.SubElement(faction_elem, "Posessions")
            self.logger.debug(f"Created new Posessions element")
        
        # Get the ammo entry value
        weapon_slots = self.navi_weapon_slots if is_navi else self.weapon_slots
        ammo_entry = weapon_slots[slot_index]["ammo_entry"]
        ammo_count = ammo_entry.get()
        try:
            ammo_count = int(ammo_count)
        except ValueError:
            ammo_count = 0
                
        # Determine the next available index for a new possession
        existing_indices = [int(poss.get("Index", "0")) for poss in possessions.findall("Poss")]
        next_index = 0
        while next_index in existing_indices:
            next_index += 1
        next_index_str = str(next_index)
        
        # Get the appropriate ammo type for this weapon
        ammo_type = self._get_ammo_type_for_weapon(weapon_id)
        self.logger.debug(f"Using ammo type {ammo_type} for weapon {weapon_id}")
        
        # Create or update a possession for this weapon
        weapon_poss = None
        for poss in possessions.findall("Poss"):
            if poss.get("crc_ItemID") == weapon_id:
                weapon_poss = poss
                self.logger.debug(f"Found existing weapon in inventory at index {poss.get('Index')}")
                break
                
        if weapon_poss is None:
            # Find the last element to copy its formatting
            last_poss = None
            for poss in possessions.findall("Poss"):
                last_poss = poss
            
            # Create new element with same formatting
            weapon_poss = ET.SubElement(possessions, "Poss")
            weapon_poss.set("Index", next_index_str)
            weapon_poss.set("crc_ItemID", weapon_id)
            weapon_poss.set("NbInStack", "1")
            weapon_poss.set("NbInClip", str(ammo_count))
            weapon_poss.set("crc_AmmoType", ammo_type)
            weapon_poss.set("NoveltyState", "2")
            self.logger.debug(f"Created new weapon possession at index {next_index_str}")
            
            # Copy the tail from the last element to preserve formatting
            if last_poss is not None and hasattr(last_poss, 'tail'):
                weapon_poss.tail = last_poss.tail
            
            # If this weapon uses ammo, also add the ammo to the inventory
            if ammo_type != "4294967295":
                # Add ammo - find if it already exists
                ammo_poss = None
                for poss in possessions.findall("Poss"):
                    if poss.get("crc_ItemID") == ammo_type:
                        ammo_poss = poss
                        self.logger.debug(f"Found existing ammo type {ammo_type} at index {poss.get('Index')}")
                        break
                        
                if ammo_poss is None:
                    # Create new ammo entry
                    ammo_index = next_index + 1
                    while ammo_index in existing_indices:
                        ammo_index += 1
                        
                    ammo_poss = ET.SubElement(possessions, "Poss")
                    ammo_poss.set("Index", str(ammo_index))
                    ammo_poss.set("crc_ItemID", ammo_type)
                    ammo_poss.set("NbInStack", "100")  # Give a decent amount of ammo
                    ammo_poss.set("NbInClip", "0")
                    ammo_poss.set("crc_AmmoType", "4294967295")
                    ammo_poss.set("NoveltyState", "2")
                    self.logger.debug(f"Created new ammo possession at index {ammo_index} for type {ammo_type}")
                    
                    # Copy the tail formatting here too
                    if weapon_poss is not None and hasattr(weapon_poss, 'tail'):
                        ammo_poss.tail = weapon_poss.tail
        else:
            # Use existing entry
            old_ammo_type = weapon_poss.get("crc_AmmoType")
            weapon_poss.set("NbInClip", str(ammo_count))
            weapon_poss.set("crc_AmmoType", ammo_type)  # Make sure ammo type is correct
            next_index_str = weapon_poss.get("Index")
            self.logger.debug(f"Updated existing weapon at index {next_index_str} (ammo type {old_ammo_type} -> {ammo_type})")
            
        # Update the equipped weapon slot
        slot = slots[slot_index]
        old_index = slot.get("MainHand_PossIdx", "-1")
        slot.set("MainHand_PossIdx", next_index_str)
        self.logger.debug(f"Updated slot {slot_index} from MainHand_PossIdx={old_index} to {next_index_str}")
        
        # Update the display
        if is_navi:
            self._update_navi_loadout_display(profile)
            # Preserve faction when changing Na'vi weapons
            self._preserve_faction(profile, "1")  # 1 for Na'vi
        else:
            self._update_loadout_display(profile)
            # Preserve faction when changing RDA weapons
            self._preserve_faction(profile, "2")  # 2 for RDA
        
        return True

        
    def _update_armor(self, profile, slot_type, armor_name, is_navi=False):
        """
        Unified method to update armor for both RDA and Na'vi across different save formats.
        
        Args:
            profile (ET.Element): The PlayerProfile element
            slot_type (str): The armor slot type ("headwear", "torso", or "legs")
            armor_name (str): The name of the armor to set
            is_navi (bool): True for Na'vi armor, False for RDA
        
        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.debug(f"Updating {'Navi' if is_navi else 'RDA'} armor - Slot: {slot_type}, Armor: {armor_name}")
        
        # Get the armor sets and IDs based on faction
        armor_sets = self.navi_armor_sets if is_navi else self.rda_armor_sets
        armor_ids = self.navi_armor_ids if is_navi else self.rda_armor_ids
        
        # Handle special case for default RDA armor
        if not is_navi and armor_name in ["Default RDA Torso", "Default RDA Legs"]:
            # Set to empty (-1) for default RDA armor
            armor_id = "-1"
        elif armor_name == "-Empty-":
            # Handle empty selection
            armor_id = "-1"
        else:
            # Get the armor ID from the name
            armor_id = armor_ids[slot_type].get(armor_name)
            if armor_id is None:
                self.logger.warning(f"Could not find armor ID for {armor_name}")
                return False
        
        # Find the Possessions element or create it
        faction_elem_name = "Possessions_Avatar" if is_navi else "Possessions_Soldier"
        faction_elem = profile.find(faction_elem_name)
        if faction_elem is None:
            faction_elem = ET.SubElement(profile, faction_elem_name)
            self.logger.debug(f"Created new {faction_elem_name} element")
        
        # Find or create EquippedArmors section
        equipped_armors = faction_elem.find("EquippedArmors")
        if equipped_armors is None:
            equipped_armors = ET.SubElement(faction_elem, "EquippedArmors")
            self.logger.debug(f"Created new EquippedArmors element")

        # Dump existing armor slots for debugging
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Current {'Navi' if is_navi else 'RDA'} EquippedArmors before update:")
            for i, slot in enumerate(equipped_armors.findall("Slot")):
                idx = slot.get("PossIdx", "-1")
                self.logger.debug(f"  Slot {i}: PossIdx={idx}")

        # Ensure we have all three slots
        slots = equipped_armors.findall("Slot")
        slot_mapping = {"headwear": 0, "torso": 1, "legs": 2}
        slot_position = slot_mapping[slot_type]
        
        # Create slots if they don't exist
        while len(slots) <= slot_position:
            new_slot = ET.SubElement(equipped_armors, "Slot")
            new_slot.set("PossIdx", "-1")  # Default to empty
            slots = equipped_armors.findall("Slot")
            self.logger.debug(f"Created new armor Slot at position {len(slots)-1}")
        
        # For empty selection or default RDA armor, just set to -1 and we're done
        if armor_name == "-Empty-" or armor_id == "-1":
            slots[slot_position].set("PossIdx", "-1")
            self.logger.debug(f"Set {'Navi' if is_navi else 'RDA'} {slot_type} to empty (-1)")
        
        # Find Posessions element or create it
        possessions = faction_elem.find("Posessions")
        if possessions is None:
            possessions = ET.SubElement(faction_elem, "Posessions")
            self.logger.debug(f"Created new Posessions element")
        
        # Check if the armor already exists in inventory
        existing_poss = None
        for poss in possessions.findall("Poss"):
            if poss.get("crc_ItemID") == armor_id:
                existing_poss = poss
                self.logger.debug(f"Found existing armor item at index {poss.get('Index')}")
                break
        
        if existing_poss is not None:
            # Use existing possession
            index_str = existing_poss.get("Index")
        else:
            # Create new possession with next available index
            existing_indices = [int(poss.get("Index", "0")) for poss in possessions.findall("Poss")]
            next_index = 0
            while next_index in existing_indices:
                next_index += 1
            index_str = str(next_index)
            
            # Create new possession
            new_poss = ET.SubElement(possessions, "Poss")
            new_poss.set("Index", index_str)
            new_poss.set("crc_ItemID", armor_id)
            new_poss.set("NbInStack", "1")
            new_poss.set("NbInClip", "0")
            new_poss.set("crc_AmmoType", "4294967295")
            new_poss.set("NoveltyState", "2")
            self.logger.debug(f"Created new armor item at index {index_str}")
            
            # Copy formatting from another item if possible
            other_poss = possessions.find("Poss")
            if other_poss is not None and hasattr(other_poss, 'tail'):
                new_poss.tail = other_poss.tail
        
        # Update the slot reference - CRITICAL FOR PC SAVES
        slots[slot_position].set("PossIdx", index_str)
                
        self.logger.debug(f"Set {slot_type} slot to use item at index {index_str}")
        
        # Dump armor slots after update for verification
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"{'Navi' if is_navi else 'RDA'} EquippedArmors after update:")
            for i, slot in enumerate(equipped_armors.findall("Slot")):
                idx = slot.get("PossIdx", "-1")
                self.logger.debug(f"  Slot {i}: PossIdx={idx}")
        
        return True

    def _on_weapon_selected(self, event, slot_index):
        """Handle the selection of a weapon from the RDA dropdown"""
        # Check if save file is loaded
        if self.main_window.tree is None:
            self.logger.warning("Attempted to select RDA weapon with no save file loaded")
            messagebox.showerror("Error", "No save file loaded. Please load a save file first.")
            # Reset the combobox to empty
            combo = event.widget
            combo.set("-Empty-")
            return
                
        combo = event.widget
        selected_weapon = combo.get()
        
        # Skip if empty selection
        if selected_weapon == "-Empty-":
            return
        
        # Find the item ID from the selected weapon name
        weapon_id = None
        for item_id, item_name in self.weapon_slots[slot_index]["all_weapons"].items():
            if item_name == selected_weapon:
                weapon_id = item_id
                break
        
        if weapon_id is None:
            return
                    
        # Update the XML when we have a valid save file
        profile = self.main_window.tree.getroot().find("PlayerProfile")
        if profile is not None:
            # Update RDA weapon using unified method
            self._update_weapon(profile, slot_index, weapon_id, is_navi=False)
                        
            # Mark as unsaved
            self.main_window.unsaved_label.config(text="Unsaved Changes")

    def _on_navi_weapon_selected(self, event, slot_index):
        """Handle the selection of a weapon from the Na'vi dropdown"""
        # Check if save file is loaded
        if self.main_window.tree is None:
            self.logger.warning("Attempted to select Na'vi weapon with no save file loaded")
            messagebox.showerror("Error", "No save file loaded. Please load a save file first.")
            # Reset the combobox to empty
            combo = event.widget
            combo.set("-Empty-")
            return
                
        combo = event.widget
        selected_weapon = combo.get()
        
        self.logger.debug(f"Na'vi weapon selection: Slot {slot_index} = {selected_weapon}")
        
        # Skip if empty selection
        if selected_weapon == "-Empty-":
            return
        
        # Find the item ID from the selected weapon name
        weapon_id = None
        for item_id, item_name in self.navi_weapon_slots[slot_index]["all_weapons"].items():
            if item_name == selected_weapon:
                weapon_id = item_id
                break
        
        if weapon_id is None:
            self.logger.warning(f"Could not find weapon ID for {selected_weapon}")
            return
                    
        self.logger.debug(f"Found Na'vi weapon ID: {weapon_id} for {selected_weapon}")
        
        # Update the XML when we have a valid save file
        profile = self.main_window.tree.getroot().find("PlayerProfile")
        if profile is not None:
            # Dump XML before change for debugging
            if self.logger.isEnabledFor(logging.DEBUG):
                avatar = profile.find("Possessions_Avatar")
                if avatar is not None:
                    equipped = avatar.find("EquippedWeapons")
                    if equipped is not None:
                        equip_xml = ET.tostring(equipped, encoding='unicode')
                        self.logger.debug(f"Before update, Na'vi EquippedWeapons: {equip_xml}")
            
            # Update Na'vi weapon using unified method
            self._update_weapon(profile, slot_index, weapon_id, is_navi=True)
            
            # Dump XML after change
            if self.logger.isEnabledFor(logging.DEBUG):
                avatar = profile.find("Possessions_Avatar")
                if avatar is not None:
                    equipped = avatar.find("EquippedWeapons")
                    if equipped is not None:
                        equip_xml = ET.tostring(equipped, encoding='unicode')
                        self.logger.debug(f"After update, Na'vi EquippedWeapons: {equip_xml}")
                    
            # Mark as unsaved
            self.main_window.unsaved_label.config(text="Unsaved Changes")

    def _on_navi_weapon_selected(self, event, slot_index):
        """Handle the selection of a weapon from the Na'vi dropdown"""
        # Check if save file is loaded
        if self.main_window.tree is None:
            self.logger.warning("Attempted to select Na'vi weapon with no save file loaded")
            messagebox.showerror("Error", "No save file loaded. Please load a save file first.")
            # Reset the combobox to empty
            combo = event.widget
            combo.set("-Empty-")
            return
                
        combo = event.widget
        selected_weapon = combo.get()
        
        self.logger.debug(f"Na'vi weapon selection: Slot {slot_index} = {selected_weapon}")
        
        # Skip if empty selection
        if selected_weapon == "-Empty-":
            return
        
        # Find the item ID from the selected weapon name
        weapon_id = None
        for item_id, item_name in self.navi_weapon_slots[slot_index]["all_weapons"].items():
            if item_name == selected_weapon:
                weapon_id = item_id
                break
        
        if weapon_id is None:
            self.logger.warning(f"Could not find weapon ID for {selected_weapon}")
            return
                    
        self.logger.debug(f"Found Na'vi weapon ID: {weapon_id} for {selected_weapon}")
                
        # Update the XML when we have a valid save file
        profile = self.main_window.tree.getroot().find("PlayerProfile")
        if profile is not None:
            # Dump XML before change for debugging
            if self.logger.isEnabledFor(logging.DEBUG):
                avatar = profile.find("Possessions_Avatar")
                if avatar is not None:
                    equipped = avatar.find("EquippedWeapons")
                    if equipped is not None:
                        equip_xml = ET.tostring(equipped, encoding='unicode')
                        self.logger.debug(f"Before update, Na'vi EquippedWeapons: {equip_xml}")
            
            # Dump XML after change
            if self.logger.isEnabledFor(logging.DEBUG):
                avatar = profile.find("Possessions_Avatar")
                if avatar is not None:
                    equipped = avatar.find("EquippedWeapons")
                    if equipped is not None:
                        equip_xml = ET.tostring(equipped, encoding='unicode')
                        self.logger.debug(f"After update, Na'vi EquippedWeapons: {equip_xml}")
                    
            # Mark as unsaved
            self.main_window.unsaved_label.config(text="Unsaved Changes")

    def _preserve_player_eps(self, profile):
        """Preserve Player0 and Player1 EP values"""
        root = profile.getroot()
        metagame = root.find("Metagame")
        
        if metagame is not None:
            # Check and preserve Player0 EPs
            player0 = metagame.find("Player0")
            if player0 is not None:
                eps = player0.get("EPs", "0")
                new_eps = player0.get("newEPs", "0")
                
                # Update UI
                if "EPs" in self.entries and eps != "":
                    self.entries["EPs"].delete(0, tk.END)
                    self.entries["EPs"].insert(0, eps)
                
                if "newEPs" in self.entries and new_eps != "":
                    self.entries["newEPs"].delete(0, tk.END)
                    self.entries["newEPs"].insert(0, new_eps)
            
            # Check and preserve Player1 EPs
            player1 = metagame.find("Player1")
            if player1 is not None:
                eps_p1 = player1.get("EPs", "0")
                new_eps_p1 = player1.get("newEPs", "0")
                
                # Update UI
                if "EPs_Player1" in self.entries and eps_p1 != "":
                    self.entries["EPs_Player1"].delete(0, tk.END)
                    self.entries["EPs_Player1"].insert(0, eps_p1)
                
                if "newEPs_Player1" in self.entries and new_eps_p1 != "":
                    self.entries["newEPs_Player1"].delete(0, tk.END)
                    self.entries["newEPs_Player1"].insert(0, new_eps_p1)

    def _get_ammo_type_for_weapon(self, weapon_id: str) -> str:
        """Determine the correct ammo type for a given weapon ID"""
        # Default ammo type (no ammo)
        default_ammo = "4294967295"
        
        # Mapping of weapons to their ammo types
        weapon_ammo_map = {
            # RDA weapons
            # Dual Wasp Pistol - No ammo (infinity)
            "1042188764": "4294967295",  # Dual Wasp Pistol I
            "815885611": "4294967295",   # Dual Wasp Pistol II
            "760079057": "4294967295",   # Dual Wasp Pistol III
            "999316102": "4294967295",   # Dual Wasp Pistol IV
            
            # DLC WARLOCK Dual Wasp Pistols - No ammo (infinity)
            "3859060838": "4294967295",  # DLC WARLOCK Dual Wasp Pistol I
            "3904601233": "4294967295",  # DLC WARLOCK Dual Wasp Pistol II
            "102867538": "4294967295",   # DLC WARLOCK Dual Wasp Pistol III
            "749353518": "4294967295",   # DLC WARLOCK Dual Wasp Pistol IV
            
            # Standard Issue Rifle - Rifle Ammo
            "1130814347": "4029490973",  # Standard Issue Rifle TERRA I
            "1306083196": "4029490973",  # Standard Issue Rifle EURYS II
            "3628031700": "4029490973",  # Standard Issue Rifle SOLARIS III
            "1146928137": "4029490973",  # Standard Issue Rifle SOLARIS IV
            
            # DLC ARGO Standard Issue Rifles - Rifle Ammo
            "2850329205": "4029490973",  # DLC ARGO Standard Issue Rifle I
            "2807789186": "4029490973",  # DLC ARGO Standard Issue Rifle II
            "2194670470": "4029490973",  # DLC ARGO Standard Issue Rifle III
            "324172685": "4029490973",   # DLC ARGO Standard Issue Rifle IV
            
            # Combat Shotgun - Shotgun Ammo
            "2313824646": "2220072441",  # Combat Shotgun PHALANX I
            "2270547313": "2220072441",  # Combat Shotgun PHALANX II
            "2789519003": "2220072441",  # Combat Shotgun PHALANX III
            "1919695864": "2220072441",  # Combat Shotgun PHALANX IV
            
            # DLC SIGNET Combat Shotguns - Shotgun Ammo
            "2664450350": "2220072441",  # DLC SIGNET Combat Shotgun I
            "2423238105": "2220072441",  # DLC SIGNET Combat Shotgun II
            "2120138529": "2220072441",  # DLC SIGNET Combat Shotgun III
            "4289908838": "2220072441",  # DLC SIGNET Combat Shotgun IV
            
            # Assault Rifle - SMG Ammo
            "2397981034": "3183424835",  # Assault Rifle TERRA I
            "2152836509": "3183424835",  # Assault Rifle EURYS II
            "268371112": "3183424835",   # Assault Rifle SOLARIS III
            "466145020": "3183424835",   # Assault Rifle SOLARIS IV
            
            # DLC BARRO Assault Rifles - SMG Ammo
            "3655372526": "3183424835",  # DLC BARRO Assault Rifle I
            "3613354521": "3183424835",  # DLC BARRO Assault Rifle II
            "3850194262": "3183424835",  # DLC BARRO Assault Rifle III
            "2109370248": "3183424835",  # DLC BARRO Assault Rifle IV
            
            # BANISHER M60 Machine Gun - Grenade Ammo
            "85991974": "3227899887",    # BANISHER M60 Machine Gun I
            "195020497": "3227899887",   # BANISHER M60 Machine Gun II
            "1881065336": "3227899887",  # BANISHER M60 Machine Gun III
            "1796958374": "3227899887",  # BANISHER M60 Machine Gun IV
            
            # DLC STELLAR M60 Machine Guns - Grenade Ammo
            "2015914953": "3227899887",  # DLC STELLAR M60 Machine Gun I
            "1989644094": "3227899887",  # DLC STELLAR M60 Machine Gun II
            "1087779032": "3227899887",  # DLC STELLAR M60 Machine Gun III
            "1691104809": "3227899887",  # DLC STELLAR M60 Machine Gun IV
            
            # Grenade Launcher - Rocket Ammo
            "94681171": "4198025789",    # Grenade Launcher M222 - I
            "186342564": "4198025789",   # Grenade Launcher M222 - II
            "1349633617": "4198025789",  # Grenade Launcher M222 - III
            "4018216358": "4198025789",  # Grenade Launcher M222 - IV
            
            # DLC CRUSHER Grenade Launchers - Rocket Ammo
            "2157668310": "4198025789",  # DLC CRUSHER Grenade Launcher I
            "2384757537": "4198025789",  # DLC CRUSHER Grenade Launcher II
            "3441856033": "4198025789",  # DLC CRUSHER Grenade Launcher III
            "3043901684": "4198025789",  # DLC CRUSHER Grenade Launcher IV
            
            # Flamethrower - LMG Ammo
            "2529862352": "2442117335",  # Flamethrower VESUPYRE I
            "2557822503": "2442117335",  # Flamethrower STERILATOR II
            "609450705": "2442117335",   # Flamethrower BUSHBOSS III
            "2288255787": "2442117335",  # Flamethrower BUSHBOSS IV
            
            # DLC BUDDY Flamethrowers - LMG Ammo
            "3250873684": "2442117335",  # DLC BUDDY Flamethrower I
            "3480977827": "2442117335",  # DLC BUDDY Flamethrower II
            "3469816623": "2442117335",  # DLC BUDDY Flamethrower III
            "3994460767": "2442117335",  # DLC BUDDY Flamethrower IV
            
            # Nail Gun - Heavy Ammo
            "2548581230": "3819023512",  # Nail Gun HAMMER I
            "2572658585": "3819023512",  # Nail Gun HAMMER II
            "143378107": "3819023512",   # Nail Gun HAMMER III
            "1911864170": "3819023512",  # Nail Gun HAMMER IV
            
            # DLC DENT Nail Guns - Heavy Ammo
            "2161255366": "3819023512",  # DLC DENT Nail Gun I
            "2389559089": "3819023512",  # DLC DENT Nail Gun II
            "3499218689": "3819023512",  # DLC DENT Nail Gun III
            "4230631668": "3819023512",  # DLC DENT Nail Gun IV
            
            # Na'vi Weapons
            # Dual Blade - No ammo (melee)
            "2948460035": "4294967295",  # Torukä Way Dual Blade IV
            "2813685095": "4294967295",  # Palulukanä Srew Dual Blade III
            "2917611312": "4294967295",  # 'Angtsìkä Zawng Dual Blade II
            "2740507591": "4294967295",  # Ikranä Syal Dual Blade I
            
            # DLC Tanhì Dual Blade - No ammo (melee)
            "2285146948": "4294967295",  # DLC Tanhì Dual Blade I
            "2257287091": "4294967295",  # DLC Tanhì Dual Blade II
            "3543126973": "4294967295",  # DLC Tanhì Dual Blade III
            "2007498681": "4294967295",  # DLC Tanhì Dual Balde IV
            
            # Crossbow - Poison Ammo
            "1514231420": "3069972540",  # Nawm Crossbow IV
            "3400058396": "3069972540",  # Kyktan Crossbow III
            "1839769381": "3069972540",  # Tsamsiyu Crossbow II
            "1662469074": "3069972540",  # Taronyu Crossbow I
            
            # DLC PXI Crossbow - Poison Ammo
            "3138212456": "3069972540",  # DLC PXI Crossbow I
            "2486913109": "3069972540",  # DLC PXI Crossbow II
            "2589205711": "3069972540",  # DLC PXI Crossbow III
            "1886472672": "3069972540",  # DLC PXI Crossbow IV
            
            # M30 Machine Guns - Arrow Ammo
            "921966990": "1042656528",   # ELITE AVR-M30 IV
            "958613249": "1042656528",   # AVR-M30 Machine Gun IV
            "172062103": "1042656528",   # ELITE AVR-M30 III
            "982090295": "1042656528",   # AVR-M30 Machine Gun III
            "1132447925": "1042656528",  # AVR-M30 Machine Gun II
            "1048019290": "1042656528",  # ELITE AVR-M30 II
            "1304439874": "1042656528",  # AVR-M30 Machine Gun I
            
            # Club - No ammo (melee)
            "240531571": "4294967295",   # Nawm Club IV
            "3879387803": "4294967295",  # Eyktan Club III
            "4249071066": "4294967295",  # Tsamsiyu Club II
            "4093397293": "4294967295",  # Taronyu Club I
            
            # DLC Ikran Axe - No ammo (melee)
            "2934884349": "4294967295",  # DLC Ikran Axe 'Ampi
            "2689671946": "4294967295",  # DLC Ikran Axe Kurakx
            "1639187137": "4294967295",  # DLC Ikran Axe Tsmukan
            "1958996617": "4294967295",  # DLC Ikran Axe 'Eko
            
            # Fighting Staff - Spear Ammo
            "3960574385": "435601722",   # Torukä Tirea Fighting Staff IV
            "2986118748": "435601722",   # Palulukanä Tìtakuk Fighting Staff III
            "2295024111": "435601722",   # Pa'liä Tìtxur Fighting Staff II
            "2255793432": "435601722",   # Ikranä Zawng Fighting Staff I
            
            # DLC Hufwe Fighting Staff - Spear Ammo
            "1828119782": "435601722",   # DLC Hufwe Fighting Staff I
            "1648951313": "435601722",   # DLC Hufwe Fighting Staff II
            "3943944974": "435601722",   # DLC Hufwe Fighting Staff III
            "3139393077": "435601722",   # DLC Hufwe Fighting Staff IV
            
            # Bow - Arrow Ammo
            "291262189": "1042656528",   # DLC Taronyu Tsko Bow I
            "535013914": "1042656528",   # Tasmsiyu Tsko Bow II
            "2092736556": "1042656528",  # Tsko Kyktan Bow III
            "371977402": "1042656528",   # Tsko Nawm Bow IV
            
            # DLC Bow - Arrow Ammo
            "1817446146": "1042656528",  # DLC RAWKE Bow I
            "435991093": "1042656528",   # DLC RAWKE Bow IV
            "1659626485": "1042656528",  # DLC RAWKE Bow II
            "1282693004": "1042656528",  # DLC RAWKE Bow III
        }
        
        # Return the appropriate ammo type for the weapon, or default if not found
        return weapon_ammo_map.get(weapon_id, default_ammo)

    def _update_metagame_player_info(self, metagame: ET.Element) -> None:
        """Update player EP information from Metagame"""
        # Find Player0 element
        player0 = metagame.find("Player0")
        if player0 is not None:
            # Get EPs and newEPs values
            eps_value = player0.get("EPs", "0")
            new_eps_value = player0.get("newEPs", "0")
            
            # Update the input fields
            if "EPs" in self.entries:
                self.entries["EPs"].delete(0, tk.END)
                self.entries["EPs"].insert(0, eps_value)
                
            if "newEPs" in self.entries:
                self.entries["newEPs"].delete(0, tk.END)
                self.entries["newEPs"].insert(0, new_eps_value)
        
        # Find Player1 element (added for Player1 support)
        player1 = metagame.find("Player1")
        if player1 is not None:
            # Get EPs and newEPs values for Player1
            eps_value_p1 = player1.get("EPs", "0")
            new_eps_value_p1 = player1.get("newEPs", "0")
            
            # Update the input fields for Player1
            if "EPs_Player1" in self.entries:
                self.entries["EPs_Player1"].delete(0, tk.END)
                self.entries["EPs_Player1"].insert(0, eps_value_p1)
                
            if "newEPs_Player1" in self.entries:
                self.entries["newEPs_Player1"].delete(0, tk.END)
                self.entries["newEPs_Player1"].insert(0, new_eps_value_p1)

    def _max_out_level(self):
        """Max out the experience based on selected faction"""
        try:
            # Check if a save file is loaded
            if self.main_window.tree is None:
                self.logger.warning("No save file loaded when attempting to max out level")
                messagebox.showerror("Error", "No save file loaded. Please load a save file first.")
                return
                
            # Get current faction
            faction_widget = self.entries["PlayerFaction"]
            faction = faction_widget.get()
            
            # Set appropriate EP value based on faction
            if faction in ["Navi", "Na'vi"]:
                max_ep = 500000  # Max EP for Na'vi
            else:  # RDA or Undecided
                max_ep = 500000  # Max EP for RDA
            
            # Get current EP value
            ep_widget = self.entries["TotalEP"]
            current_ep_text = ep_widget.cget("text") if isinstance(ep_widget, ttk.Label) else ep_widget.get()
            
            # Validate the current EP text
            if current_ep_text in ["-", ""]:
                self.logger.warning("Invalid EP value when attempting to max out level")
                messagebox.showerror("Error", "Invalid EP value. Please load a valid save file.")
                return
                
            # Extract numeric EP value
            try:
                if "/" in current_ep_text:
                    current_ep = current_ep_text.split("/")[0]
                else:
                    current_ep = current_ep_text
                    
                # Convert to integer (this will raise ValueError if not a valid number)
                current_ep = int(current_ep)
            except ValueError:
                self.logger.warning(f"Failed to parse EP value: '{current_ep_text}'")
                messagebox.showerror("Error", "Invalid EP value format. Please load a valid save file.")
                return
                    
            # Check if already at max EP
            if current_ep >= max_ep:
                messagebox.showinfo("Already Maxed Out", 
                                f"Your character already has maximum amount EP ({max_ep}) for the {faction} faction.")
                return
            
            # Update the EP display with formatted text
            formatted_ep = f"{max_ep}/{max_ep} (Max EP)"
            if isinstance(ep_widget, ttk.Label):
                ep_widget.config(text=formatted_ep)
            else:
                ep_widget.delete(0, tk.END)
                ep_widget.insert(0, formatted_ep)
            
            # Update BaseInfo TotalEP if tree exists
            if self.main_window.tree is not None:
                base_info = self.main_window.tree.getroot().find(".//BaseInfo")
                if base_info is not None:
                    base_info.set("TotalEP", str(max_ep))
            
            # Mark changes as unsaved
            self._mark_unsaved_changes()
            
            # Show success message
            messagebox.showinfo("EP Maxed Out", 
                            f"Successfully set experience to maximum amount ({max_ep}) for the {faction} faction.")
            
        except Exception as e:
            self.logger.error(f"Error maxing out level: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to max out level: {str(e)}")

    def _name_vec_to_string(self, name_vec: str) -> str:
        """Convert a name vector to a readable string"""
        try:
            self.logger.debug(f"[NAME_VEC] Converting name vector: {name_vec}")
            
            if not name_vec or not name_vec.startswith("Count("):
                self.logger.debug("[NAME_VEC] Invalid name vector format")
                return ""
            
            # Extract the ASCII values
            parts = name_vec.split(") ")
            if len(parts) < 2:
                self.logger.debug(f"[NAME_VEC] Unexpected name vector format: {name_vec}")
                return ""
            
            values = parts[1].rstrip(";").split(";")
            self.logger.debug(f"[NAME_VEC] Extracted ASCII values: {values}")
            
            # Convert ASCII values to characters
            name = "".join(chr(int(val)) for val in values if val)
            
            self.logger.debug(f"[NAME_VEC] Converted name: {name}")
            return name
        except Exception as e:
            self.logger.error(f"[NAME_VEC] Error converting name vector to string: {str(e)}", exc_info=True)
            return ""
    
    def _string_to_name_vec(self, name: str) -> str:
        """Convert a string to a name vector format"""
        try:
            # Convert each character to ASCII value
            ascii_values = [str(ord(c)) for c in name]
            return f"Count({len(ascii_values)}) {';'.join(ascii_values)};"
        except Exception as e:
            self.logger.error(f"Error converting string to name vector: {str(e)}")
            return "Count(0) "

    def _get_avatar_weapons(self, profile: ET.Element) -> dict:
        weapons_data = {}
        avatar = profile.find("Possessions_Avatar")
        if avatar is not None:
            equipped = avatar.find("EquippedWeapons")
            if equipped is not None:
                # Get all weapon slots
                for slot in equipped.findall("Slot"):
                    main_hand = slot.get("MainHand_PossIdx", "-1")
                    off_hand = slot.get("OffHand_PossIdx", "-1")
                    weapons_data[len(weapons_data)] = {
                        "main": main_hand,
                        "off": off_hand
                    }
        return weapons_data

    def _get_avatar_weapon_info(self, profile: ET.Element, index: str) -> dict:
        """Get Na'vi weapon name and details from possession index"""
        if index == "-1":
            return None
                
        avatar = profile.find("Possessions_Avatar")
        if avatar is not None:
            possessions = avatar.find("Posessions")
            if possessions is not None:
                for poss in possessions.findall("Poss"):
                    if poss.get("Index") == index:
                        item_id = poss.get("crc_ItemID")
                        ammo_type = poss.get("crc_AmmoType", "4294967295")
                        item_name = self._get_item_name(item_id)
                        
                        # Determine if this is a melee weapon
                        is_melee = any(melee_kw in item_name.lower() for melee_kw in 
                                    ["club", "blade", "axe", "staff", "spear", "knife", "sword"])
                        
                        weapon_info = {
                            "id": item_id,
                            "name": item_name,
                            "ammo": "Melee" if is_melee else poss.get("NbInClip", "0"),
                            "stack": poss.get("NbInStack", "0"),
                            "is_melee": is_melee
                        }
                        
                        if ammo_type != "4294967295" and not is_melee:  # If not infinite ammo and not melee
                            total_ammo = "0"
                            for ammo_poss in possessions.findall("Poss"):
                                if ammo_poss.get("crc_ItemID") == ammo_type:
                                    total_ammo = ammo_poss.get("NbInStack", "0")
                                    print(f"DEBUG: Found ammo for weapon {item_name}: {total_ammo}")
                                    break
                            weapon_info["total_ammo"] = total_ammo
                        
                        # Check if weapon has infinite ammo
                        weapon_info["infinite_ammo"] = (
                            ammo_type == "4294967295" and 
                            not is_melee and
                            not any(pistol_term in item_name.lower() for pistol_term in ["wasp pistol"])
                        )
                        
                        # Special case for Wasp Pistols
                        if "wasp pistol" in item_name.lower():
                            weapon_info["infinite_ammo"] = True
                            weapon_info["ammo"] = "∞"
                        
                        return weapon_info
        return None
    
    def _get_navi_armor_info(self, profile: ET.Element) -> dict:
        """Get Na'vi armor info for each slot from Posessions"""
        armor_slots = {"headwear": None, "torso": None, "legs": None}
        
        avatar = profile.find("Possessions_Avatar")
        if avatar is not None:
            equipped_armors = avatar.find("EquippedArmors")
            if equipped_armors is not None:
                # Get all slots
                slots = equipped_armors.findall("Slot")
                if len(slots) >= 3:  # Ensure we have all three slots
                    # Map slots to armor types (first is headwear, second is torso, third is legs)
                    slot_mapping = {0: "headwear", 1: "torso", 2: "legs"}
                    
                    for idx, slot in enumerate(slots[:3]):  # Process first three slots
                        armor_idx = slot.get("PossIdx", "-1")
                        
                        # Skip if no armor in this slot
                        if armor_idx == "-1":
                            continue
                            
                        possessions = avatar.find("Posessions")
                        if possessions is not None:
                            for poss in possessions.findall("Poss"):
                                if poss.get("Index") == armor_idx:
                                    item_id = poss.get("crc_ItemID")
                                    if item_id:
                                        armor_slots[slot_mapping[idx]] = {
                                            "id": item_id,
                                            "name": self._get_item_name(item_id)
                                        }
        return armor_slots

    def _create_navi_armor_mappings(self):
        """Create mappings for Na'vi armor pieces by type"""
        self.navi_armor_sets = {
            "headwear": {
                "236713729": "RDA-Issue Avatar Head",
                "84098544": "EYKTAN Head",
                "2070955956": "KARYU Head",
                "1519513878": "NAWMA EYKTAN Head",
                "3932154789": "NAWMA TARONYU Head",
                "25166328": "NAWMA TSAMSIYU Head",
                "985254384": "TIREA Head",
                "3363478556": "NAWM Head",
                "3529616870": "'AWVEA TSAMSIYU Head",
                "1336514870": "DLC TSTEU II Head",
                "1312065276": "DLC TSTEU III Head",
                "1500118218": "DLC TSTEU IV Head",
                "3240533717": "DLC TARONYU II Head",
                "2008660537": "DLC TARONYU III Head",
                "1753343575": "DLC TARONYU IV Head", 
            },
            "torso": {
                "2228061969": "RDA-Issue Avatar Torso",
                "3666151432": "EYKTAN Torso",
                "1711646853": "KARYU Torso",
                "2232927470": "NAWMA EYKTAN Torso",
                "884530381": "NAWMA TARONYU Torso",
                "3724948480": "NAWMA TSAMSIYU Torso",
                "386149755": "TIREA Torso",
                "1118628876": "NAWM Torso",
                "1641566717": "'AWVEA TSAMSIYU Torso",
                "904822394": "DLC TSTEU II Torso",
                "824495264": "DLC TSTEU III Torso",
                "1960056897": "DLC TSTSU IV Torso",
                "3143727513": "DLC TARONYU II Torso",
                "145354853": "DLC TARONYU III Torso",
                "1161560796": "DLC TARONYU IV Torso",
            },
            "legs": {
                "753645081": "RDA-Issue Avatar Legs",
                "815973795": "EYKTAN Legs",
                "2024863229": "KARYU Legs",
                "1865419077": "NAWMA EYKTAN Legs",
                "3480671099": "NAWMA TARONYU Legs",
                "874641835": "NAWMA TSAMSIYU Legs",
                "216177023": "TIREA Legs",
                "3934969092": "NAWM Legs",
                "540413008": "'AWVEA TSAMSIYU Legs",
                "848846039": "DLC TSTEU II Legs",
                "2571396567": "DLC TSTEU III Legs",
                "1865591877": "DLC TSTEU IV legs",
                "3155647284": "DLC TARONYU II Legs",
                "2697550098": "DLC TARONYU III Legs",
                "1591391960": "DLC TARONYU IV Legs",
            }
        }

        # Create reverse mappings for looking up IDs by name
        self.navi_armor_ids = {
            slot_type: {name: id for id, name in items.items()}
            for slot_type, items in self.navi_armor_sets.items()
        }

    def _update_navi_loadout_display(self, profile: ET.Element) -> None:
        """Update the Na'vi loadout display with current equipment"""
        # Update weapons
        weapons = self._get_avatar_weapons(profile)
        for slot_num, slot_data in weapons.items():
            if slot_num < len(self.navi_weapon_slots):
                main_weapon = self._get_avatar_weapon_info(profile, slot_data["main"])
                
                if main_weapon:
                    # Get the dropdown for this slot
                    if "dropdown" in self.navi_weapon_slots[slot_num]:
                        weapon_name = main_weapon["name"]
                        dropdown = self.navi_weapon_slots[slot_num]["dropdown"]
                        dropdown.set(weapon_name)
                        
                        # Update ammo entry
                        if "ammo_entry" in self.navi_weapon_slots[slot_num]:
                            ammo_entry = self.navi_weapon_slots[slot_num]["ammo_entry"]
                            ammo_entry.delete(0, tk.END)
                            
                            # For melee weapons, show "Melee" in the ammo entry
                            if main_weapon.get("is_melee", False):
                                ammo_entry.insert(0, "Melee")
                                ammo_entry.configure(state="disabled")
                            # For weapons with infinite ammo, disable the field
                            elif main_weapon.get("infinite_ammo", False):
                                ammo_entry.insert(0, "∞")
                                ammo_entry.configure(state="disabled")
                            else:
                                # For normal weapons, keep field enabled
                                ammo_entry.insert(0, main_weapon.get("total_ammo", "0"))
                                ammo_entry.configure(state="normal")
                        
                        # Update clip size label
                        if "clip_entry" in self.navi_weapon_slots[slot_num]:
                            clip_label = self.navi_weapon_slots[slot_num]["clip_entry"]
                            
                            # For melee weapons, we don't need to show anything in the clip
                            if main_weapon.get("is_melee", False):
                                clip_label.config(text="--")
                            # For infinite ammo weapons, show ∞
                            elif main_weapon.get("infinite_ammo", False):
                                clip_label.config(text="∞")
                            else:
                                clip_label.config(text=main_weapon.get("ammo", "0"))
                        
                        # Set infinite ammo checkbox based on weapon info
                        if "infinite_var" in self.navi_weapon_slots[slot_num]:
                            infinite_var = self.navi_weapon_slots[slot_num]["infinite_var"]
                            is_infinite = main_weapon.get("infinite_ammo", False)
                            infinite_var.set(is_infinite)
                            
                            # NEW CODE: Disable infinite ammo checkbox for melee or inherently infinite weapons
                            if "infinite_check" in self.navi_weapon_slots[slot_num]:
                                infinite_check = self.navi_weapon_slots[slot_num]["infinite_check"]
                                # For melee weapons OR weapons with inherent infinite ammo, disable checkbox
                                inherent_infinite = main_weapon.get("is_melee", False) or "dual blade" in main_weapon["name"].lower() or "club" in main_weapon["name"].lower() or "staff" in main_weapon["name"].lower() or "axe" in main_weapon["name"].lower()
                                
                                # Correctly set and disable checkbox for weapons that should have fixed ammo settings
                                if inherent_infinite:
                                    # Configure the checkbox to be disabled but checked for these weapons
                                    infinite_check.state(['disabled'])
                                    # Rebind to prevent any clicking for special weapons - this will block all events
                                    for event_name in ["<ButtonPress-1>", "<ButtonRelease-1>", "<space>"]:
                                        infinite_check.bind(event_name, lambda e: "break")
                                else:
                                    # Regular weapons can have their infinite ammo toggled
                                    infinite_check.state(['!disabled'])
                                    # Restore normal binding for regular weapons
                                    for event_name in ["<ButtonPress-1>", "<ButtonRelease-1>", "<space>"]:
                                        infinite_check.unbind(event_name)
                                    # Re-bind the toggle function
                                    infinite_check.bind('<ButtonRelease-1>', lambda e, idx=slot_num, navi=True: 
                                        self._toggle_infinite_ammo(e, idx, navi))
                else:
                    # Set to empty if no weapon
                    if "dropdown" in self.navi_weapon_slots[slot_num]:
                        self.navi_weapon_slots[slot_num]["dropdown"].set("-Empty-")
                        
                        # Reset ammo entry
                        if "ammo_entry" in self.navi_weapon_slots[slot_num]:
                            ammo_entry = self.navi_weapon_slots[slot_num]["ammo_entry"]
                            ammo_entry.delete(0, tk.END)
                            ammo_entry.insert(0, "0")
                            ammo_entry.configure(state="normal")
                        
                        # Reset clip label
                        if "clip_entry" in self.navi_weapon_slots[slot_num]:
                            clip_label = self.navi_weapon_slots[slot_num]["clip_entry"]
                            clip_label.config(text="0")
                        
                        # Reset infinite ammo checkbox
                        if "infinite_var" in self.navi_weapon_slots[slot_num]:
                            self.navi_weapon_slots[slot_num]["infinite_var"].set(False)
                        
                        # Enable the infinite checkbox since no weapon is selected
                        if "infinite_check" in self.navi_weapon_slots[slot_num]:
                            infinite_check = self.navi_weapon_slots[slot_num]["infinite_check"] 
                            infinite_check.state(['!disabled'])
                            # Clear any special bindings
                            for event_name in ["<ButtonPress-1>", "<ButtonRelease-1>", "<space>"]:
                                infinite_check.unbind(event_name)
                            # Re-bind the toggle function
                            infinite_check.bind('<ButtonRelease-1>', lambda e, idx=slot_num, navi=True: 
                                self._toggle_infinite_ammo(e, idx, navi))

        # Update armor dropdowns
        armor_info = self._get_navi_armor_info(profile)
        for slot_type, dropdown in self.navi_armor_dropdowns.items():
            if armor_info[slot_type]:
                dropdown.set(armor_info[slot_type]["name"])
            else:
                dropdown.set("-Empty-")

    def _initialize_armor_tracking(self):
        """Initialize tracking for direct armor changes"""
        self.direct_armor_changes = {
            'rda': {'headwear': None, 'torso': None, 'legs': None},
            'navi': {'headwear': None, 'torso': None, 'legs': None}
        }
        self.logger.debug("Armor tracking initialized")

    def _get_equipped_weapons(self, profile: ET.Element) -> dict:
        weapons_data = {}
        soldier = profile.find("Possessions_Soldier")
        if soldier is not None:
            equipped = soldier.find("EquippedWeapons")
            if equipped is not None:
                # Get all weapon slots
                for slot in equipped.findall("Slot"):
                    main_hand = slot.get("MainHand_PossIdx", "-1")
                    off_hand = slot.get("OffHand_PossIdx", "-1")
                    weapons_data[len(weapons_data)] = {
                        "main": main_hand,
                        "off": off_hand
                    }
        return weapons_data

    def _get_weapon_info(self, profile: ET.Element, index: str) -> dict:
        """Get weapon name and details from possession index"""
        if index == "-1":
            return None
                
        soldier = profile.find("Possessions_Soldier")
        if soldier is not None:
            possessions = soldier.find("Posessions")
            if possessions is not None:
                for poss in possessions.findall("Poss"):
                    if poss.get("Index") == index:
                        item_id = poss.get("crc_ItemID")
                        ammo_type = poss.get("crc_AmmoType", "4294967295")
                        item_name = self._get_item_name(item_id)
                        
                        # Determine if this is a melee weapon
                        is_melee = any(melee_kw in item_name.lower() for melee_kw in 
                                    ["club", "blade", "axe", "staff", "spear", "knife", "sword"])
                        
                        weapon_info = {
                            "id": item_id,
                            "name": item_name,
                            "ammo": "Melee" if is_melee else poss.get("NbInClip", "0"),
                            "stack": poss.get("NbInStack", "0"),
                            "is_melee": is_melee
                        }
                        
                        if ammo_type != "4294967295" and not is_melee:  # If not infinite ammo and not melee
                            total_ammo = "0"
                            for ammo_poss in possessions.findall("Poss"):
                                if ammo_poss.get("crc_ItemID") == ammo_type:
                                    total_ammo = ammo_poss.get("NbInStack", "0")
                                    print(f"DEBUG: Found ammo for weapon {item_name}: {total_ammo}")
                                    break
                            weapon_info["total_ammo"] = total_ammo
                        
                        # Check if weapon has infinite ammo
                        weapon_info["infinite_ammo"] = (
                            ammo_type == "4294967295" and 
                            not is_melee and
                            not any(pistol_term in item_name.lower() for pistol_term in ["wasp pistol"])
                        )
                        
                        # Special case for Wasp Pistols
                        if "wasp pistol" in item_name.lower():
                            weapon_info["infinite_ammo"] = True
                            weapon_info["ammo"] = "∞"
                        
                        return weapon_info
        return None
    
    def _get_armor_info(self, profile: ET.Element) -> dict:
        """Get RDA armor info for each slot (headwear, torso, legs)"""
        armor_slots = {"headwear": None, "torso": None, "legs": None}
        
        soldier = profile.find("Possessions_Soldier")
        if soldier is not None:
            equipped_armors = soldier.find("EquippedArmors")
            if equipped_armors is not None:
                # Get all slots
                slots = equipped_armors.findall("Slot")
                if len(slots) >= 3:  # Ensure we have all three slots
                    # Map slots to armor types (first is headwear, second is torso, third is legs)
                    slot_mapping = {0: "headwear", 1: "torso", 2: "legs"}
                    
                    for idx, slot in enumerate(slots[:3]):  # Process first three slots
                        armor_idx = slot.get("PossIdx", "-1")
                        
                        # Handle default outfit case (PossIdx = -1)
                        if armor_idx == "-1":
                            if idx == 1:  # Torso
                                armor_slots["torso"] = {"id": "-1", "name": "Default RDA Torso"}
                            elif idx == 2:  # Legs
                                armor_slots["legs"] = {"id": "-1", "name": "Default RDA Legs"}
                            continue
                        
                        # For non-default items, find the actual item
                        possessions = soldier.find("Posessions")
                        if possessions is not None:
                            for poss in possessions.findall("Poss"):
                                if poss.get("Index") == armor_idx:
                                    item_id = poss.get("crc_ItemID")
                                    if item_id:
                                        armor_slots[slot_mapping[idx]] = {
                                            "id": item_id,
                                            "name": self._get_item_name(item_id)
                                        }
        return armor_slots

    def _create_rda_armor_mappings(self):
        """Create mappings for RDA armor pieces by type"""
        self.rda_armor_sets = {
            "headwear": {
                "433486271": "Default RDA Head",
                "4082430736": "Titan Head",
                "149499402": "Militum Head",
                "1593826001": "Kodiak Head",
                "3527939275": "Exotant Head",
                "403319592": "Centauri Head",
                "3753317026": "Hydra Head",
                "2823901304": "Warthog Head",
                "3980056687": "Viper Head",
                "3005472419": "DLC BRASHER I Head",
                "3064631211": "DLC BRASHER II Head",
                "3228789267": "DLC BRASHER III Head",
                "3818917462": "DLC BRASHER IV Head",
                "1563279247": "DLC MISHETICA I Head",
                "4103047382": "DLC MISHETICA II Head",
                "4001710741": "DLC MISHETICA III Head",
                "1950293887": "DLC MISHETICA IV Head", 
            },
            "torso": {
                "-1": "Default RDA Torso",
                "205852157": "Titan Torso",
                "4160278759": "Militum Torso",
                "2716738620": "Kodiak Torso",
                "1193780569": "Exotant Torso",
                "3877361093": "Centauri Torso",
                "1851965193": "Hydra Torso",
                "1981144899": "Warthog Torso",
                "3574042272": "Viper Torso",
                "730661330": "DLC BRASHER I Torso",
                "2822640242": "DLC BRASHER II Torso",
                "1063425278": "DLC BRASHER III Troso",
                "1993326532": "DLC BRASHER IV Torso",
                "3313721598": "DLC MISHETICA I Torso",
                "3927643407": "DLC MISHETICA II Torso",
                "294960248": "DLC MISHETICA III Torso",
                "3780161261": "DLC MISHETICA IV Torso",
            },
            "legs": {
                "-1": "Default RDA Legs",
                "1052486966": "Titan Legs",
                "3305533484": "Militum Legs",
                "2467333367": "Kodiak Legs",
                "1379870057": "Exotant Legs",
                "3588584718": "Centauri Legs",
                "2428117146": "Hydra Legs",
                "2056338139": "Warthog Legs",
                "1417888964": "Viper Legs",
                "3718956374": "DLC BRASHER I Legs",
                "2398239326": "DLC BRASHER II Legs",
                "228340789": "DLC BRASHER III Legs",
                "1675050996": "DLC BRASHER IV Legs",
                "866428026": "DLC MISHETICA I Legs",
                "3436657955": "DLC MISHETICA II Legs",
                "594156723": "DLC MISHETICA III Legs",
                "4098371293": "DLC MISHETICA IV Legs",
            }
        }

        # Create reverse mappings for looking up IDs by name
        self.rda_armor_ids = {
            slot_type: {name: id for id, name in items.items()}
            for slot_type, items in self.rda_armor_sets.items()
        }
    
    def _on_armor_selected(self, event, slot_type):
        """Handle armor selection change with direct hex update for PC saves"""
        # Check if save file is loaded
        if self.main_window.tree is None:
            self.logger.warning("Attempted to select RDA armor with no save file loaded")
            messagebox.showerror("Error", "No save file loaded. Please load a save file first.")
            # Reset the combobox to empty
            combo = event.widget
            combo.set("-Empty-")
            return
                
        combo = event.widget
        selected_armor = combo.get()
        self.logger.debug(f"Selected RDA armor: {selected_armor}")
                        
        # Get the armor ID from the name
        armor_id = self.rda_armor_ids[slot_type].get(selected_armor)
        if armor_id is None:
            self.logger.warning(f"Could not find armor ID for {selected_armor}")
            messagebox.showerror("Error", f"Could not find armor ID for {selected_armor}")
            return
        
    def _on_navi_armor_selected(self, event, slot_type):
        """Handle Na'vi armor selection change with direct hex update for PC saves"""
        # Check if save file is loaded
        if self.main_window.tree is None:
            self.logger.warning("Attempted to select Na'vi armor with no save file loaded")
            messagebox.showerror("Error", "No save file loaded. Please load a save file first.")
            # Reset the combobox to empty
            combo = event.widget
            combo.set("-Empty-")
            return
                
        combo = event.widget
        selected_armor = combo.get()
        self.logger.debug(f"Selected Na'vi armor: {selected_armor}")
                
        # Get the armor ID from the name
        armor_id = self.navi_armor_ids[slot_type].get(selected_armor)
        if armor_id is None:
            self.logger.warning(f"Could not find armor ID for {selected_armor}")
            messagebox.showerror("Error", f"Could not find armor ID for {selected_armor}")
            return
        
    def _update_loadout_display(self, profile: ET.Element) -> None:
        """Update the RDA loadout display with current equipment"""
        # Update weapons
        weapons = self._get_equipped_weapons(profile)
        for slot_num, slot_data in weapons.items():
            if slot_num < len(self.weapon_slots):
                main_weapon = self._get_weapon_info(profile, slot_data["main"])
                
                if main_weapon:
                    # Get the dropdown for this slot
                    if "dropdown" in self.weapon_slots[slot_num]:
                        weapon_name = main_weapon["name"]
                        dropdown = self.weapon_slots[slot_num]["dropdown"]
                        dropdown.set(weapon_name)
                        
                        # Update ammo entry
                        if "ammo_entry" in self.weapon_slots[slot_num]:
                            ammo_entry = self.weapon_slots[slot_num]["ammo_entry"]
                            ammo_entry.delete(0, tk.END)
                            
                            # For melee weapons, show "Melee" in the ammo entry
                            if main_weapon.get("is_melee", False):
                                ammo_entry.insert(0, "Melee")
                                ammo_entry.configure(state="disabled")
                            # For weapons with infinite ammo, disable the field
                            elif main_weapon.get("infinite_ammo", False):
                                ammo_entry.insert(0, "∞")
                                ammo_entry.configure(state="disabled")
                            else:
                                # For normal weapons, keep field enabled
                                ammo_entry.insert(0, main_weapon.get("total_ammo", "0"))
                                ammo_entry.configure(state="normal")
                        
                        # Update clip size label
                        if "clip_entry" in self.weapon_slots[slot_num]:
                            clip_label = self.weapon_slots[slot_num]["clip_entry"]
                            
                            # For melee weapons, we don't need to show anything in the clip
                            if main_weapon.get("is_melee", False):
                                clip_label.config(text="--")
                            # For infinite ammo weapons, show ∞
                            elif main_weapon.get("infinite_ammo", False):
                                clip_label.config(text="∞")
                            else:
                                clip_label.config(text=main_weapon.get("ammo", "0"))
                        
                        # Set infinite ammo checkbox based on weapon info
                        if "infinite_var" in self.weapon_slots[slot_num]:
                            infinite_var = self.weapon_slots[slot_num]["infinite_var"]
                            is_infinite = main_weapon.get("infinite_ammo", False)
                            infinite_var.set(is_infinite)
                            
                            # NEW CODE: Disable infinite ammo checkbox for melee or inherently infinite weapons
                            if "infinite_check" in self.weapon_slots[slot_num]:
                                infinite_check = self.weapon_slots[slot_num]["infinite_check"]
                                # For melee weapons OR weapons with inherent infinite ammo, disable checkbox
                                inherent_infinite = main_weapon.get("is_melee", False) or any(
                                    keyword in main_weapon["name"].lower() for keyword in ["wasp pistol"]
                                )
                                
                                # Correctly set and disable checkbox for weapons that should have fixed ammo settings
                                if inherent_infinite:
                                    # Configure the checkbox to be disabled but checked for these weapons
                                    infinite_check.state(['disabled'])
                                    # Rebind to prevent any clicking for special weapons
                                    for event_name in ["<ButtonPress-1>", "<ButtonRelease-1>", "<space>"]:
                                        infinite_check.bind(event_name, lambda e: "break")
                                else:
                                    # Regular weapons can have their infinite ammo toggled
                                    infinite_check.state(['!disabled'])
                                    # Restore normal binding for regular weapons
                                    for event_name in ["<ButtonPress-1>", "<ButtonRelease-1>", "<space>"]:
                                        infinite_check.unbind(event_name)
                                    # Re-bind the toggle function
                                    infinite_check.bind('<ButtonRelease-1>', lambda e, idx=slot_num, navi=False: 
                                        self._toggle_infinite_ammo(e, idx, navi))
                else:
                    # Set to empty if no weapon
                    if "dropdown" in self.weapon_slots[slot_num]:
                        self.weapon_slots[slot_num]["dropdown"].set("-Empty-")
                        
                        # Reset ammo entry
                        if "ammo_entry" in self.weapon_slots[slot_num]:
                            ammo_entry = self.weapon_slots[slot_num]["ammo_entry"]
                            ammo_entry.delete(0, tk.END)
                            ammo_entry.insert(0, "0")
                            ammo_entry.configure(state="normal")
                        
                        # Reset clip label
                        if "clip_entry" in self.weapon_slots[slot_num]:
                            clip_label = self.weapon_slots[slot_num]["clip_entry"]
                            clip_label.config(text="0")
                        
                        # Reset infinite ammo checkbox
                        if "infinite_var" in self.weapon_slots[slot_num]:
                            self.weapon_slots[slot_num]["infinite_var"].set(False)
                        
                        # Enable the infinite checkbox since no weapon is selected
                        if "infinite_check" in self.weapon_slots[slot_num]:
                            infinite_check = self.weapon_slots[slot_num]["infinite_check"]
                            infinite_check.state(['!disabled'])
                            # Clear any special bindings
                            for event_name in ["<ButtonPress-1>", "<ButtonRelease-1>", "<space>"]:
                                infinite_check.unbind(event_name)
                            # Re-bind the toggle function
                            infinite_check.bind('<ButtonRelease-1>', lambda e, idx=slot_num, navi=False: 
                                self._toggle_infinite_ammo(e, idx, navi))

        # Update armor dropdowns
        armor_info = self._get_armor_info(profile)
        for slot_type, dropdown in self.armor_dropdowns.items():
            if armor_info[slot_type]:
                dropdown.set(armor_info[slot_type]["name"])
            else:
                dropdown.set("-Empty-")

    def _on_face_selected(self, event=None):
            """Handle face selection and update image"""
            try:
                widget = self.entries["face"]
                face_value = widget.cget("text") if isinstance(widget, ttk.Label) else widget.get()
                self.logger.debug(f"[FACE_SELECT] Selected face value: {face_value}")
                
                if not face_value or face_value == "-":
                    self.logger.warning("[FACE_SELECT] No face value selected")
                    return
                    
                # Validate the face value format
                parts = face_value.split()
                if len(parts) != 2 or parts[0] not in ["Male", "Female"]:
                    self.logger.error(f"[FACE_SELECT] Invalid face value format: {face_value}")
                    if hasattr(self, 'face_image_label') and self.face_image_label:
                        self.face_image_label.configure(image='')
                        self.face_image_label.configure(text=f"Invalid face format\nExpected: 'Male XX' or 'Female XX'")
                    return
                    
                gender, number = parts
                image_path = os.path.join("Face_Images", f"{gender} {number}.png")
                
                self.logger.debug(f"[FACE_SELECT] Attempting to load image: {image_path}")
                self.logger.debug(f"[FACE_SELECT] Image path exists: {os.path.exists(image_path)}")
                
                if os.path.exists(image_path):
                    self.logger.debug("[FACE_SELECT] Loading and resizing image...")
                    original_image = Image.open(image_path)
                    resized_image = original_image.resize((150, 150), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(resized_image)
                    
                    if hasattr(self, 'face_image_label') and self.face_image_label:
                        self.logger.debug("[FACE_SELECT] Updating face image label...")
                        self.face_image_label.configure(image=photo)
                        self.face_image_label.image = photo  # Keep a reference
                        
                        # Mark as unsaved changes
                        self.main_window.unsaved_label.config(text="Unsaved Changes")
                        self.logger.debug("[FACE_SELECT] Face image updated successfully")
                    else:
                        self.logger.error("[FACE_SELECT] face_image_label not available")
                else:
                    self.logger.warning(f"[FACE_SELECT] Face image not found: {image_path}")
                    if hasattr(self, 'face_image_label') and self.face_image_label:
                        self.face_image_label.configure(image='')
                        self.face_image_label.configure(text=f"No face image found\n({image_path})")
                        
            except Exception as e:
                self.logger.error(f"[FACE_SELECT] Error updating face image: {str(e)}", exc_info=True)
                if hasattr(self, 'face_image_label') and self.face_image_label:
                    self.face_image_label.configure(image='')
                    self.face_image_label.configure(text=f"Error loading image: {str(e)}")

    def _mark_unsaved_changes(self, event=None):
        """Mark the save file as having unsaved changes"""
        try:
            # Check if a save file is loaded before marking changes
            if self.main_window.tree is None:
                self.logger.warning("Attempted to mark changes with no save file loaded")
                messagebox.showerror("Error", "No save file loaded. Please load a save file first.")
                
                # Reset the combobox to its previous value if this was triggered by a combobox
                if event and hasattr(event, 'widget') and isinstance(event.widget, ttk.Combobox):
                    # We don't know the previous value, so just reset selection
                    event.widget.selection_clear()
                    return "break"  # Prevent default handling
                    
                return
                
            self.main_window.unsaved_label.config(text="Unsaved Changes")
        except Exception as e:
            self.logger.error(f"Error marking unsaved changes: {str(e)}", exc_info=True)
   
    def _add_error_handling_to_comboboxes(self):
        """Add error handling to all comboboxes in the UI"""
        try:
            # Store original values for each combobox
            self.original_combobox_values = {}
            
            # Define the check function
            def _check_save_loaded(event):
                if self.main_window.tree is None:
                    widget = event.widget
                    combobox_key = None
                    
                    # Find which key this widget belongs to
                    for key, entry_widget in self.entries.items():
                        if entry_widget == widget:
                            combobox_key = key
                            break
                    
                    # Show error message
                    self.logger.warning(f"Attempted to change setting '{combobox_key}' with no save file loaded")
                    messagebox.showerror("Error", "No save file loaded. Please load a save file first.")
                    
                    # Reset to original value if we have it
                    if combobox_key in self.original_combobox_values:
                        widget.set(self.original_combobox_values[combobox_key])
                    else:
                        # If no original value, just clear selection
                        widget.set("")
                    
                    # Prevent default handling
                    return "break"
                
                # Store the current value as original when a save file is loaded
                widget = event.widget
                for key, entry_widget in self.entries.items():
                    if entry_widget == widget:
                        self.original_combobox_values[key] = widget.get()
                        break
                        
                return None  # Allow event to continue
            
            # Apply to all comboboxes in our entries
            for key, widget in self.entries.items():
                if isinstance(widget, ttk.Combobox):
                    self.logger.debug(f"Adding error handling to combobox: {key}")
                    # Store initial value
                    self.original_combobox_values[key] = widget.get()
                    # Add binding
                    widget.bind("<<ComboboxSelected>>", _check_save_loaded, add="+")
                    
            self.logger.debug("Error handling added to all comboboxes")
        except Exception as e:
            self.logger.error(f"Error adding combobox error handling: {str(e)}", exc_info=True)

    def load_stats(self, tree: ET.ElementTree) -> None:
        root = tree.getroot()
        profile = root.find("PlayerProfile")

        if profile is not None:
            self._update_base_info(profile.find("BaseInfo"), tree)
            self._update_xp_info(profile.find("XpInfo"))
            self._update_options_info(profile.find("OptionsInfo"))
            self._update_time_info(profile.find("TimeInfo"))
            self._update_loadout_display(profile)  # RDA loadout
            self._update_navi_loadout_display(profile)  # Na'vi loadout

            # Look for Possessions_Recovery in PlayerProfile directly
            self._update_player_info(profile)
        
        metagame = root.find("Metagame")
        if metagame is not None:
            self._update_metagame_info(metagame)
            self._update_metagame_player_info(metagame)

    def _convert_time_to_seconds(self, formatted_time: str) -> str:
        self.logger.debug(f"Converting time format: {formatted_time}")
        try:
            hours, minutes, seconds = 0, 0, 0
            parts = formatted_time.replace('h', ' ').replace('m', ' ').replace('s', '').split()
            if len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
            total_seconds = str(hours * 3600 + minutes * 60 + seconds)
            self.logger.debug(f"Converted to seconds: {total_seconds}")
            return total_seconds
        except (ValueError, IndexError) as e:
            self.logger.error(f"Error converting time format: {str(e)}", exc_info=True)
            return formatted_time

    def update_location(self, location_value: str) -> None:
        """Update location while preserving XML structure"""
        if not self.main_window.tree:
            return

        try:
            # Find existing LocationInfo element
            location_info = self.main_window.tree.find(".//LocationInfo")
            if location_info is not None:
                # Update existing attribute
                location_info.set("YouAreHere_LatitudeLongitude", location_value)
            else:
                # Look for location attribute in other elements
                for elem in self.main_window.tree.iter():
                    if "YouAreHere_LatitudeLongitude" in elem.attrib:
                        elem.set("YouAreHere_LatitudeLongitude", location_value)
                        break

            self.main_window.unsaved_label.config(text="Unsaved Changes")
            
        except Exception as e:
            self.logger.error(f"Error updating location: {str(e)}", exc_info=True)
            raise

    def get_stats_updates(self) -> Dict[str, Dict[str, str]]:
        self.logger.debug("[STATS_UPDATE] Starting stats updates collection")
        try:

            # Check current faction in XML before updates
            if self.main_window.tree is not None:
                metagame = self.main_window.tree.getroot().find("Metagame")
                if metagame is not None:
                    current_faction_xml = metagame.get("PlayerFaction", "Unknown")
                    print(f"DEBUG: Current faction in XML before update: {current_faction_xml}")

            # Define updates dictionary that will store all our changes
            updates = {
                "BaseInfo": {},
                "XpInfo": {},
                "OptionsInfo": {},
                "TimeInfo": {},
                "Metagame": {}
            }

            # Get selected faction
            current_faction = self.entries["PlayerFaction"].get()
            faction_map = {"Undecided": "0", "Navi": "1", "RDA": "2"}
            faction_value = faction_map.get(current_faction, "0")
            
            # Get current EP value
            ep_widget = self.entries["TotalEP"]
            current_ep = ep_widget.cget("text") if isinstance(ep_widget, ttk.Label) else ep_widget.get()
            
            # Handle the new format with max value
            if "/" in current_ep:
                # Extract just the EP value
                current_ep = current_ep.split("/")[0]

            # Determine the level based on EP and faction
            current_ep_value = int(current_ep)
            if current_faction in ["Navi", "Na'vi"]:
                # Na'vi level calculation
                if current_ep_value >= 500000:
                    level = 18  # Max level for Na'vi
                else:
                    level = self._get_level_for_ep(current_ep_value, "Na'vi")
            else:
                # RDA level calculation
                if current_ep_value >= 389250:
                    level = 24  # Max level for RDA
                else:
                    level = self._get_level_for_ep(current_ep_value, "RDA")

            # Update faction setting
            updates["Metagame"]["PlayerFaction"] = faction_value
            print(f"DEBUG: Final faction value in updates: {updates['Metagame']['PlayerFaction']}")

            # Update base information
            base_fields = ["face", "TotalEP", "namevec", "RecoveryBits"]
            for field in base_fields:
                if field in self.entries:
                    widget = self.entries[field]
                    if field == "face":
                        face_value = widget.cget("text") if isinstance(widget, ttk.Label) else widget.get()
                        face_number = self._get_face_number(face_value)
                        updates["BaseInfo"][field] = face_number
                    elif field == "namevec":
                        name = widget.cget("text") if isinstance(widget, ttk.Label) else widget.get()
                        updates["BaseInfo"][field] = self._string_to_name_vec(name)
                    elif field == "RecoveryBits":
                        # For RecoveryBits, we'll save directly to Possessions_Recovery
                        value = widget.cget("text") if isinstance(widget, ttk.Label) else widget.get()
                        updates["PlayerInfo"] = {"RecoveryBits": value}
                    elif field == "TotalEP":
                        # Handle the extracted EP value
                        updates["BaseInfo"][field] = current_ep
                    else:
                        value = widget.cget("text") if isinstance(widget, ttk.Label) else widget.get()
                        updates["BaseInfo"][field] = value

            # Handle side and pawn fields (now dropdowns)
            if "side" in self.entries:
                side_value = self.entries["side"].get()
                # Convert to correct value based on dropdown selection
                if side_value == "Navi":
                    updates["BaseInfo"]["side"] = "1"
                elif side_value == "RDA":
                    updates["BaseInfo"]["side"] = "2"
                elif side_value == "Undecided":
                    updates["BaseInfo"]["side"] = "4"
                else:
                    updates["BaseInfo"]["side"] = "4"  # Default to Navi if unknown

            if "pawn" in self.entries:
                pawn_value = self.entries["pawn"].get()
                # Convert to correct value based on dropdown selection
                updates["BaseInfo"]["pawn"] = "1" if pawn_value == "Navi" else "2"

            # Handle yes/no fields
            widget_female = self.entries["isfemale"]
            updates["BaseInfo"]["isfemale"] = "1" if (widget_female.cget("text") if isinstance(widget_female, ttk.Label) else widget_female.get()) == "Yes" else "0"
            
            widget_scanning = self.entries["bEntityScanningEnabled"]
            updates["BaseInfo"]["bEntityScanningEnabled"] = "1" if (widget_scanning.cget("text") if isinstance(widget_scanning, ttk.Label) else widget_scanning.get()) == "Yes" else "0"

            # Update XP information - use the calculated level
            updates["XpInfo"]["iCurrentLevel"] = str(level)

            # Update game options
            widget_rumble = self.entries["RumbleEnabled"]
            updates["OptionsInfo"]["RumbleEnabled"] = "1" if widget_rumble.get() == "Yes" else "0"
            
            widget_firstperson = self.entries["FirstPersonMode"]
            updates["OptionsInfo"]["FirstPersonMode"] = "1" if widget_firstperson.get() == "Yes" else "0"

            # Update faction setting
            updates["Metagame"]["PlayerFaction"] = faction_value
            
            # Update cost reduction values
            if "NaviCostReduction" in self.entries:
                navi_cost = self.entries["NaviCostReduction"].get()
                updates["Metagame"]["NaviCostReduction"] = navi_cost
                
            if "CorpCostReduction" in self.entries:
                rda_cost = self.entries["CorpCostReduction"].get()
                updates["Metagame"]["CorpCostReduction"] = rda_cost

            if "EPs" in self.entries and "newEPs" in self.entries:
                eps_value = self.entries["EPs"].get()
                new_eps_value = self.entries["newEPs"].get()
                
                # Create a Player0 section in the updates if it doesn't exist
                if "Player0" not in updates:
                    updates["Player0"] = {}
                
                updates["Player0"]["EPs"] = eps_value
                updates["Player0"]["newEPs"] = new_eps_value

            # Make sure the faction value is explicitly set
            current_faction = self.entries["PlayerFaction"].get()
            faction_map = {"Undecided": "0", "Na'vi": "1", "Navi": "1", "RDA": "2"}
            faction_value = faction_map.get(current_faction, "0")
            updates["Metagame"]["PlayerFaction"] = faction_value
            print(f"DEBUG: Final faction value in updates: {updates['Metagame']['PlayerFaction']}")

            # Add Player1 values to updates
            if "EPs_Player1" in self.entries and "newEPs_Player1" in self.entries:
                eps_value_p1 = self.entries["EPs_Player1"].get()
                new_eps_value_p1 = self.entries["newEPs_Player1"].get()
                
                # Create a Player1 section in the updates if it doesn't exist
                if "Player1" not in updates:
                    updates["Player1"] = {}
                
                updates["Player1"]["EPs"] = eps_value_p1
                updates["Player1"]["newEPs"] = new_eps_value_p1

            self.logger.debug(f"Stats updates: {updates}")
            return updates             
                        
        except Exception as e:
            self.logger.error(f"Error getting stats updates: {str(e)}")
            raise

    def _ensure_faction_preserved(self):
        """Make sure faction value is not lost during save"""
        if self.main_window.tree is not None:
            root = self.main_window.tree.getroot()
            metagame = root.find("Metagame")
            if metagame is not None:
                # Get current faction from UI
                faction_widget = self.entries["PlayerFaction"]
                faction = faction_widget.get()
                
                faction_map = {"Undecided": "0", "Na'vi": "1", "Navi": "1", "RDA": "2"}
                faction_value = faction_map.get(faction, "0")
                
                # Force set faction in XML
                metagame.set("PlayerFaction", faction_value)
                print(f"DEBUG: Ensuring faction preserved as {faction_value}")
                
                # Also make sure Player0 and Player1 EPs are set
                player0 = metagame.find("Player0")
                if player0 is not None and "EPs" in self.entries and "newEPs" in self.entries:
                    eps = self.entries["EPs"].get()
                    new_eps = self.entries["newEPs"].get()
                    if eps:
                        player0.set("EPs", eps)
                    if new_eps:
                        player0.set("newEPs", new_eps)
                        
                player1 = metagame.find("Player1")
                if player1 is not None and "EPs_Player1" in self.entries and "newEPs_Player1" in self.entries:
                    eps_p1 = self.entries["EPs_Player1"].get()
                    new_eps_p1 = self.entries["newEPs_Player1"].get()
                    if eps_p1:
                        player1.set("EPs", eps_p1)
                    if new_eps_p1:
                        player1.set("newEPs", new_eps_p1)

    def _on_faction_selected(self, event):
        try:
            # Check if a save file is loaded
            if self.main_window.tree is None:
                self.logger.warning("Attempted to change faction with no save file loaded")
                messagebox.showerror("Error", "No save file loaded. Please load a save file first.")
                # Reset the combobox
                self.entries["PlayerFaction"].selection_clear()
                return
                
            # Get the selected faction
            selected_faction = self.entries["PlayerFaction"].get()
            
            # Get the max EP for this faction
            if selected_faction in ["Navi", "Na'vi"]:
                max_ep = 500000  # Max EP for Na'vi
            else:  # RDA or Undecided
                max_ep = 500000  # Max EP for RDA
            
            # Update the EP display format
            ep_widget = self.entries["TotalEP"]
            current_ep = ep_widget.cget("text") if isinstance(ep_widget, ttk.Label) else ep_widget.get()
            
            # Handle format conversions
            if "/" in current_ep:
                # Already in new format, extract just the EP value
                current_ep = current_ep.split("/")[0]
            
            # Update with new format
            if isinstance(ep_widget, ttk.Label):
                ep_widget.config(text=f"{current_ep}/{max_ep} (Max EP)")
            else:
                ep_widget.delete(0, tk.END)
                ep_widget.insert(0, f"{current_ep}/{max_ep} (Max EP)")
            
            # Mark changes as unsaved
            self.main_window.unsaved_label.config(text="Unsaved Changes")
        except Exception as e:
            self.logger.error(f"Error in faction selection: {str(e)}")
            messagebox.showerror("Error", f"Failed to change faction: {str(e)}")

    def _update_field_visibility(self, field_key, visible):
        """Show or hide a field based on visibility flag"""
        if field_key in self.entries:
            parent_widget = self.entries[field_key].master
            
            if visible:
                parent_widget.pack(fill=tk.X, padx=5, pady=2)
            else:
                parent_widget.pack_forget()

    def _get_level_thresholds(self, faction_type):
        """Get the level XP thresholds for the specified faction"""
        # RDA Thresholds
        rda_thresholds = [
            0,      # Level 0
            1600,   # Level 1
            4600,   # Level 2
            8000,   # Level 3
            12100,  # Level 4
            17000,  # Level 5
            38500,  # Level 6
            45750,  # Level 7
            53250,  # Level 8
            61250,  # Level 9
            70250,  # Level 10
            79750,  # Level 11
            91250,  # Level 12
            104750, # Level 13
            119250, # Level 14
            143250, # Level 15
            169250, # Level 16
            197250, # Level 17
            227250, # Level 18
            249250, # Level 19
            273250, # Level 20
            299250, # Level 21
            327250, # Level 22
            357250, # Level 23
            389250  # Level 24
        ]
        
        # Na'vi Thresholds (different values)
        navi_thresholds = [
            0,      # Level 0
            46000,   # Level 1
            54500,   # Level 2
            63500,   # Level 3
            73000,  # Level 4
            87000,  # Level 5
            103000,  # Level 6
            121000,  # Level 7
            140000,  # Level 8
            160000,  # Level 9
            181000,  # Level 10
            204000,  # Level 11
            234000,  # Level 12
            266000,  # Level 13
            300000, # Level 14
            336000, # Level 15
            374000, # Level 16
            414000, # Level 17
            500000, # Level 18
        ]
        
        # Return the appropriate thresholds based on faction type
        if faction_type == "Na'vi" or faction_type == "Navi":
            return navi_thresholds
        else:
            return rda_thresholds
                
    def _get_level_for_ep(self, ep, faction_type):
        """Find the appropriate level for a given EP amount and faction"""
        try:
            ep = int(ep)
            thresholds = self._get_level_thresholds(faction_type)
            
            # Find the correct level based on EP amount
            for level in range(len(thresholds) - 1):
                if ep < thresholds[level + 1]:
                    return level
            
            # If EP exceeds all thresholds, return max level
            return len(thresholds) - 1
        except (ValueError, TypeError):
            return 0  # Default to level 0 for invalid input

    def _on_level_selected(self, event):
        try:
            # Get current faction
            faction_widget = self.entries["PlayerFaction"]
            faction = faction_widget.get()
            print(f"DEBUG: Level selected for faction: {faction}")
            
            # Set appropriate EP value based on faction - FIXED TO HANDLE "Navi" or "Na'vi"
            if faction == "Navi" or faction == "Na'vi":
                ep_value = 500000  # Max EP for Na'vi
                print(f"DEBUG: Setting Na'vi max EP: {ep_value}")
            else:  # RDA or Undecided
                ep_value = 389250  # Max EP for RDA
                print(f"DEBUG: Setting RDA max EP: {ep_value}")
            
            # Update the EP display
            ep_widget = self.entries["TotalEP"]
            if isinstance(ep_widget, ttk.Label):
                ep_widget.config(text=str(ep_value))
            else:
                ep_widget.delete(0, tk.END)
                ep_widget.insert(0, str(ep_value))
            
            # Update BaseInfo TotalEP if tree exists
            if self.main_window.tree is not None:
                base_info = self.main_window.tree.getroot().find(".//BaseInfo")
                if base_info is not None:
                    base_info.set("TotalEP", str(ep_value))
                    print(f"DEBUG: Updated BaseInfo TotalEP attribute to {ep_value}")
            
            # Mark changes as unsaved
            self._mark_unsaved_changes()
        except Exception as e:
            print(f"ERROR in level selection: {str(e)}")
            self.logger.error(f"Error in level selection: {str(e)}")

    def _update_level_from_ep(self, event=None):
        """Update the displayed level based on the current EP and faction"""
        try:
            # Get the current TotalEP value
            ep_widget = self.entries["TotalEP"]
            ep_value = ep_widget.cget("text") if isinstance(ep_widget, ttk.Label) else ep_widget.get()
            
            if not ep_value or ep_value == "-":
                return
                    
            ep = int(ep_value)
            
            # Get current faction
            faction_widget = self.entries["PlayerFaction"]
            faction = faction_widget.get()
            
            # Determine if we should display max level
            if faction == "Na'vi" and ep >= 500000:
                level_display = "Max Level"
            elif faction != "Na'vi" and ep >= 389250:
                level_display = "Max Level"
            else:
                # Calculate the level based on faction
                level = self._get_level_for_ep(ep, faction)
                level_display = f"Level {level}"
            
            # Update the CurrentLevel display
            level_widget = self.entries["CurrentLevel"]
            level_widget.set(level_display)
            
            # Mark changes as unsaved
            self._mark_unsaved_changes()
        except Exception as e:
            self.logger.error(f"Error updating level from EP: {str(e)}")

    def _get_xp_for_level(self, level, faction_type):
        """Get the XP threshold for a specific level and faction"""
        # Explicitly handle Na'vi faction - note we're checking for both "Na'vi" and "Navi" spellings
        if faction_type == "Na'vi" or faction_type == "Navi":
            navi_thresholds = [
                0,      # Level 0
                46000,   # Level 1
                54500,   # Level 2
                63500,   # Level 3
                73000,  # Level 4
                87000,  # Level 5
                103000,  # Level 6
                121000,  # Level 7
                140000,  # Level 8
                160000,  # Level 9
                181000,  # Level 10
                204000,  # Level 11
                234000,  # Level 12
                266000,  # Level 13
                300000, # Level 14
                336000, # Level 15
                374000, # Level 16
                414000, # Level 17
                500000, # Level 18
            ]
            
            if 0 <= level < len(navi_thresholds):
                return navi_thresholds[level]
            else:
                return navi_thresholds[-1]
        else:
            rda_thresholds = [
                0,      # Level 0
                1600,   # Level 1
                4600,   # Level 2
                8000,   # Level 3
                12100,  # Level 4
                17000,  # Level 5
                38500,  # Level 6
                45750,  # Level 7
                53250,  # Level 8
                61250,  # Level 9
                70250,  # Level 10
                79750,  # Level 11
                91250,  # Level 12
                104750, # Level 13
                119250, # Level 14
                143250, # Level 15
                169250, # Level 16
                197250, # Level 17
                227250, # Level 18
                249250, # Level 19
                273250, # Level 20
                299250, # Level 21
                327250, # Level 22
                357250, # Level 23
                389250  # Level 24
            ]
            
            if 0 <= level < len(rda_thresholds):
                return rda_thresholds[level]
            else:
                return rda_thresholds[-1]
                
    def _update_xp_info(self, xp_info: Optional[ET.Element]) -> None:
        if xp_info is None:
            return
        
        # First, check if there's a TotalEP value in BaseInfo
        total_ep = "0"
        if self.main_window.tree is not None:
            base_info = self.main_window.tree.getroot().find(".//BaseInfo")
            if base_info is not None:
                total_ep = base_info.get("TotalEP", total_ep)
        
        # If no TotalEP found in BaseInfo, fall back to 0
        if total_ep == "0":
            total_ep = "0"
        
        # Get current player faction
        faction = "0"  # Default to undecided
        if self.main_window.tree is not None:
            metagame = self.main_window.tree.getroot().find("Metagame")
            if metagame is not None:
                faction = metagame.get("PlayerFaction", "0")
        
        # Get faction name from value
        faction_map = {"0": "Undecided", "1": "Na'vi", "2": "RDA"}
        faction_name = faction_map.get(faction, "Undecided")
        
        # Determine max EP based on faction
        if faction_name in ["Na'vi", "Navi"]:
            max_ep = 500000  # Max EP for Na'vi
        else:  # RDA or Undecided
            max_ep = 500000  # Max EP for RDA
        
        # Update TotalEP display with the new format
        if "TotalEP" in self.entries:
            widget = self.entries["TotalEP"]
            formatted_ep = f"{total_ep}/{max_ep} (Max EP)"
            if isinstance(widget, ttk.Label):
                widget.config(text=formatted_ep)
            else:
                widget.delete(0, tk.END)
                widget.insert(0, formatted_ep)
        
        # Log the total EP for debugging
        self.logger.debug(f"Total EP set to: {total_ep}")

    def _update_metagame_info(self, metagame: ET.Element) -> None:
        # Update cost reduction values
        if "NaviCostReduction" in self.entries:
            navi_reduction = metagame.get("NaviCostReduction", "0")
            self.entries["NaviCostReduction"].delete(0, tk.END)
            self.entries["NaviCostReduction"].insert(0, navi_reduction)

        if "CorpCostReduction" in self.entries:
            corp_reduction = metagame.get("CorpCostReduction", "0")
            self.entries["CorpCostReduction"].delete(0, tk.END)
            self.entries["CorpCostReduction"].insert(0, corp_reduction)

        faction_value = metagame.get("PlayerFaction", "0")
        faction_map = {"0": "Undecided", "1": "Na'vi", "2": "RDA"}
        self.entries["PlayerFaction"].set(faction_map.get(faction_value, "Undecided"))

        if "PlayerFaction" in self.entries:
            # Use the string version of the faction value as the key
            faction_display = faction_map.get(faction_value, "Undecided")
            self.entries["PlayerFaction"].set(faction_display)

    def _update_base_info(self, base_info: Optional[ET.Element], tree: Optional[ET.ElementTree] = None) -> None:
        if base_info is None:
            self.logger.warning("[BASE_INFO] No base info provided")
            return

        # Handle name conversion first and separately
        if "namevec" in self.entries:
            # Get the name vector directly from base_info
            name_vec = base_info.get("namevec", "Count(0) ")
            
            # Convert name vector to readable string
            name = self._name_vec_to_string(name_vec)
            
            # Debug logging
            self.logger.debug(f"[BASE_INFO] Name vector: {name_vec}")
            self.logger.debug(f"[BASE_INFO] Converted name: {name}")
            
            # Get the widget for the name
            widget = self.entries["namevec"]
            
            # Set the name 
            if isinstance(widget, ttk.Label):
                widget.config(text=name)
            else:
                widget.delete(0, tk.END)
                widget.insert(0, name)

        # Extremely verbose logging
        self.logger.debug("[BASE_INFO] Detailed BaseInfo Investigation:")
        
        # Log the entire BaseInfo element as a string
        base_info_str = ET.tostring(base_info, encoding='unicode')
        self.logger.debug(f"Full BaseInfo XML: {base_info_str}")
        
        # Log all attributes
        self.logger.debug("All Attributes:")
        for attr, value in base_info.attrib.items():
            self.logger.debug(f"  {attr}: {value}")

        # Multiple attempts to retrieve TotalEP
        possible_keys = [
            "TotalEP", 
            "totalEP", 
            "total_ep", 
            "XP", 
            "total_XP"
        ]

        total_ep = "0"
        for key in possible_keys:
            total_ep = base_info.get(key, total_ep)
            if total_ep != "0" and total_ep != "":
                break

        # Fallback: search in entire tree if not found
        if total_ep == "0" and tree is not None:
            for elem in tree.iter():
                if elem.get("TotalEP"):
                    total_ep = elem.get("TotalEP")
                    break

        self.logger.debug(f"[BASE_INFO] Final TotalEP value: {total_ep}")

        # Update the TotalEP display
        if "TotalEP" in self.entries:
            widget = self.entries["TotalEP"]
            try:
                # Get current player faction for level calculation
                faction = "0"  # Default to undecided
                if tree is not None:
                    metagame = tree.getroot().find("Metagame")
                    if metagame is not None:
                        faction = metagame.get("PlayerFaction", "0")
                        
                # Determine max EP based on faction
                if faction == "1":  # "1" is Na'vi
                    max_ep = 500000  # Max EP for Na'vi
                else:  # RDA or Undecided
                    max_ep = 500000  # Max EP for RDA
                
                formatted_ep = f"{total_ep}/{max_ep} (Max EP)"
                if isinstance(widget, ttk.Label):
                    widget.config(text=formatted_ep)
                else:
                    widget.delete(0, tk.END)
                    widget.insert(0, formatted_ep)
            except Exception as e:
                self.logger.error(f"[BASE_INFO] Error updating TotalEP widget: {str(e)}")

        self.logger.debug("[BASE_INFO] Starting base info update")
        mappings = {
            "side": "side",
            "pawn": "pawn",
            "isfemale": "isfemale",
            "face": "face",
            "bEntityScanningEnabled": "bEntityScanningEnabled",
            "TotalEP": "TotalEP",
            "RecoveryBits": "RecoveryBits",
            "location": "YouAreHere_LatitudeLongitude"
        }

        # Get current player faction for level calculation
        faction = "0"  # Default to undecided
        if tree is not None:
            metagame = tree.getroot().find("Metagame")
            if metagame is not None:
                faction = metagame.get("PlayerFaction", "0")
        
        faction_value = ""
        if metagame is not None:
            faction_value = metagame.get("PlayerFaction", "0")
        faction_map = {"0": "Undecided", "1": "Navi", "2": "RDA"}
        if "PlayerFaction" in self.entries:
            faction_display = faction_map.get(faction_value, "Undecided")
            self.entries["PlayerFaction"].set(faction_display)

        # Get TotalEP for level calculation
        total_ep = base_info.get("TotalEP", "0")
        
        # Calculate level based on faction and EP
        current_level = self._get_level_for_ep(total_ep, faction_map)
        
        # Update level display
        if "CurrentLevel" in self.entries:
            level_widget = self.entries["CurrentLevel"]
            level_widget["values"] = ["Max Level"]
            level_widget.set("Max Level")

        for xml_key, entry_key in mappings.items():
            # Special handling for specific keys
            if entry_key == "isfemale":
                value = "Yes" if base_info.get(xml_key, "0") == "1" else "No"
            elif entry_key == "face":
                face_value = base_info.get(xml_key, "0")
                is_female = base_info.get("isfemale", "0") == "1"
                # Get the face pair number and select appropriate gender
                if face_value in self.face_values:
                    value = self.face_values[face_value]["female" if is_female else "male"]
                else:
                    value = "Male 00"  # Default face if invalid value
            elif entry_key == "side" or entry_key == "pawn":
                # Handle side and pawn values
                raw_value = base_info.get(xml_key, "1")
                faction_map = { "4": "Undecided", "1": "Navi", "2": "RDA"}
                value = faction_map.get(raw_value, "Navi")
            elif entry_key == "YouAreHere_LatitudeLongitude":
                # Specifically look for LocationInfo element
                if tree is not None:
                    root = tree.getroot()
                    # Look for LocationInfo element
                    location_info = root.find(".//LocationInfo")
                    
                    if location_info is not None:
                        value = location_info.get("YouAreHere_LatitudeLongitude", "")
                        self.logger.debug(f"Location value found: '{value}'")
                    else:
                        # Search more broadly if specific LocationInfo not found
                        location_elements = root.findall(".//*[@YouAreHere_LatitudeLongitude]")
                        if location_elements:
                            value = location_elements[0].get("YouAreHere_LatitudeLongitude", "")
                        else:
                            value = ""
                        
                        self.logger.debug("No LocationInfo element found")
                else:
                    value = ""
                    self.logger.debug("No tree provided")
                
                # Ensure a valid coordinate format
                if not value or value == "0":
                    value = "0,0"
            else:
                value = base_info.get(xml_key, "0")

            if entry_key == "bEntityScanningEnabled":
                value = "Yes" if base_info.get(xml_key, "0") == "1" else "No"
            
            if entry_key in self.entries and entry_key != "CurrentLevel":  # Skip CurrentLevel as we already updated it
                widget = self.entries[entry_key]
                
                if isinstance(widget, ttk.Label):
                    # For label widgets, directly set the text
                    widget.config(text=value)
                elif hasattr(widget, 'set'):
                    # For comboboxes
                    widget.set(value)
                else:
                    # For entry widgets
                    widget.delete(0, tk.END)
                    widget.insert(0, value)

        if entry_key == "RecoveryBits":
            value = base_info.get("RecoveryBits", "0")

        # Add face image display immediately after loading
        if "face" in self.entries:
            self.logger.debug("[BASE_INFO] Triggering face image update")
            self._on_face_selected()

    def _get_face_number(self, face_value: str) -> str:
        """Convert face display value (e.g., 'Male 00') to internal face number."""
        try:
            gender, number = face_value.split()
            face_num = int(number)
            # The face number is the same for both male and female of a pair
            return str(face_num)
        except (ValueError, IndexError):
            return "0"
            
    def _update_options_info(self, options_info: Optional[ET.Element]) -> None:
        if options_info is None:
            return

        mappings = {
            "RumbleEnabled": "RumbleEnabled",
            "FirstPersonMode": "FirstPersonMode"
        }

        for xml_key, entry_key in mappings.items():
            if entry_key in self.entries:
                value = "Yes" if options_info.get(xml_key, "0") == "1" else "No"
                self.entries[entry_key].set(value)

    def _format_game_time(self, seconds: str) -> str:
        """Convert game time seconds to a readable format."""
        try:
            total_seconds = int(float(seconds))
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            secs = total_seconds % 60
            return f"{hours:02d}h {minutes:02d}m {secs:02d}s"
        except (ValueError, TypeError):
            return seconds

    def _update_time_info(self, time_info: Optional[ET.Element]) -> None:
        if time_info is None:
            return

        time_data = {
            "GameTime": time_info.get("GameTime", "0"),
            "PlayedTime": time_info.get("PlayedTime", "0"),
            "EnvTime": time_info.get("EnvTime", "0")
        }
        
        # Update the time display in the main window
        self.main_window.update_time_display(time_data)

    def _update_player_info(self, profile: ET.Element) -> None:
        """Update player info in the XML structure"""
        # Change this to check in the PlayerProfile element instead
        recovery = profile.find("Possessions_Recovery")
        if recovery is not None:
            recovery_bits = recovery.get("RecoveryBits", "0")
            
            # Update the RecoveryBits display
            if "RecoveryBits" in self.entries:
                widget = self.entries["RecoveryBits"]
                if isinstance(widget, ttk.Label):
                    widget.config(text=recovery_bits)
                else:
                    widget.delete(0, tk.END)
                    widget.insert(0, recovery_bits)
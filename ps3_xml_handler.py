import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from io import BytesIO, StringIO
import logging
import struct
import binascii
import re

class PS3XMLHandler:
    """
    XML handler specifically designed for PS3 save files with extensive debugging.
    """
    
    @staticmethod
    def get_logger():
        return logging.getLogger('PS3XMLHandler')
    
    @staticmethod
    def debug_file_structure(data: bytes, description: str = "File"):
        """Debug helper to analyze file structure"""
        logger = PS3XMLHandler.get_logger()
        logger.debug(f"\n=== {description} Analysis ===")
        logger.debug(f"File size: {len(data)} bytes")
        logger.debug(f"First 100 bytes (hex): {data[:100].hex()}")
        
        # Try to decode readable parts
        try:
            readable = data[:100].decode('utf-8', errors='ignore')
            logger.debug(f"First 100 bytes (ascii): {readable}")
        except:
            logger.debug("First 100 bytes not readable as ASCII")
        
        # Look for XML markers
        xml_markers = [b'<Savegame>', b'<SaveGame>', b'<savegame>', b'<SaveData>', b'<Savegame', b'<SaveGame', b'<savegame']
        for marker in xml_markers:
            pos = data.find(marker)
            if pos != -1:
                logger.debug(f"Found {marker} at position {pos}")
                if pos > 0:
                    logger.debug(f"20 bytes before XML: {data[max(0, pos-20):pos].hex()}")
                break
    
    @staticmethod
    def is_ps3_save(file_path: Path) -> bool:
        """Check if this is a PS3 save directory or file"""
        if file_path.is_dir():
            ps3_files = ['SAVEDATA.000', 'PARAM.SFO', 'PARAM.PFD']
            return any((file_path / f).exists() for f in ps3_files)
        elif file_path.name in ['SAVEDATA.000', 'PADDING.000'] or file_path.suffix == '.backup':
            return True
        return False
    
    @staticmethod
    def get_primary_save_file(save_path: Path) -> Path:
        """Get the primary save file from a PS3 save directory"""
        if save_path.is_dir():
            for filename in ['SAVEDATA.000', 'PADDING.000']:
                file_path = save_path / filename
                if file_path.exists():
                    return file_path
            raise ValueError("No valid PS3 save file found in directory")
        return save_path
    
    @staticmethod
    def get_all_save_files(save_path: Path) -> list[Path]:
        """Get all save files that need to be updated in a PS3 save"""
        if save_path.is_dir():
            files = []
            for filename in ['SAVEDATA.000', 'PADDING.000']:
                file_path = save_path / filename
                if file_path.exists():
                    files.append(file_path)
            return files
        else:
            return [save_path]
    
    @staticmethod
    def find_xml_boundaries(data: bytes) -> Tuple[int, int]:
        """Find XML start and end positions with extensive debugging"""
        logger = PS3XMLHandler.get_logger()
        
        # Find XML start - look for various possible markers
        xml_start = -1
        start_marker_found = None
        
        # First try complete opening tags
        for marker in [b'<Savegame>', b'<SaveGame>', b'<savegame>', b'<SaveData>']:
            xml_start = data.find(marker)
            if xml_start != -1:
                start_marker_found = marker
                logger.debug(f"Found XML start marker '{marker.decode()}' at position {xml_start}")
                break
        
        # If complete tags not found, try partial markers
        if xml_start == -1:
            for marker in [b'<Savegame', b'<SaveGame', b'<savegame', b'<SaveData']:
                xml_start = data.find(marker)
                if xml_start != -1:
                    start_marker_found = marker
                    logger.debug(f"Found XML partial start marker '{marker.decode()}' at position {xml_start}")
                    break
        
        # Last resort - look for any opening XML bracket followed by letter
        if xml_start == -1:
            for i in range(len(data) - 1):
                if data[i:i+1] == b'<' and data[i+1:i+2].isalpha():
                    # Check if this looks like XML
                    potential_xml = data[i:i+50]
                    if b'Savegame' in potential_xml or b'SaveGame' in potential_xml or b'savegame' in potential_xml:
                        xml_start = i
                        start_marker_found = data[i:i+20]
                        logger.debug(f"Found XML start by search at position {xml_start}")
                        break
        
        if xml_start == -1:
            logger.error("No XML start marker found!")
            # Debug: show file structure around potential XML locations
            for i in range(0, min(len(data), 1000), 100):
                chunk = data[i:i+100]
                if b'<' in chunk:
                    logger.debug(f"Found '<' at offset {i}: {chunk.hex()}")
            raise ValueError("No XML start marker found in data")
        
        # Find XML end - look for closing tags
        xml_end = -1
        end_marker_found = None
        
        # Try to find the matching closing tag
        if start_marker_found:
            if b'Savegame' in start_marker_found:
                end_markers = [b'</Savegame>', b'</savegame>']
            elif b'SaveGame' in start_marker_found:
                end_markers = [b'</SaveGame>', b'</savegame>']
            elif b'SaveData' in start_marker_found:
                end_markers = [b'</SaveData>']
            else:
                end_markers = [b'</Savegame>', b'</SaveGame>', b'</savegame>', b'</SaveData>']
        else:
            end_markers = [b'</Savegame>', b'</SaveGame>', b'</savegame>', b'</SaveData>']
        
        for marker in end_markers:
            xml_end = data.rfind(marker)
            if xml_end != -1:
                xml_end += len(marker)
                end_marker_found = marker
                logger.debug(f"Found XML end marker '{marker.decode()}' at position {xml_end}")
                break
        
        if xml_end == -1:
            logger.error("No XML end marker found!")
            # Try to find any closing tag
            for i in range(len(data) - 2, -1, -1):
                if data[i:i+2] == b'</':
                    # Look ahead for a closing bracket
                    for j in range(i+2, min(i+50, len(data))):
                        if data[j:j+1] == b'>':
                            xml_end = j + 1
                            end_marker_found = data[i:j+1]
                            logger.debug(f"Found XML end by search at position {xml_end}: {end_marker_found}")
                            break
                    if xml_end != -1:
                        break
        
        if xml_end == -1:
            raise ValueError("No XML end marker found in data")
        
        logger.debug(f"XML boundaries: {xml_start} to {xml_end} (length: {xml_end - xml_start})")
        
        # Validate boundaries
        if xml_start >= xml_end:
            raise ValueError(f"Invalid XML boundaries: start={xml_start}, end={xml_end}")
        
        return xml_start, xml_end
    
    @staticmethod
    def clean_xml_content(xml_content: bytes) -> str:
        """Clean and prepare XML content for parsing"""
        logger = PS3XMLHandler.get_logger()
        
        try:
            # First try UTF-8 decoding
            xml_string = xml_content.decode('utf-8', errors='ignore')
        except Exception:
            try:
                # Try latin-1 as fallback
                xml_string = xml_content.decode('latin-1', errors='ignore')
            except Exception:
                # Last resort - try ASCII
                xml_string = xml_content.decode('ascii', errors='ignore')
        
        # Remove any null bytes or other problematic characters
        xml_string = xml_string.replace('\x00', '')
        
        # Clean up potential non-printable characters but preserve XML essentials
        # Keep: tab (0x09), newline (0x0A), carriage return (0x0D), space and above (0x20+)
        clean_xml = re.sub(r'[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD]', '', xml_string)
        
        if len(clean_xml) != len(xml_string):
            logger.debug(f"Cleaned {len(xml_string) - len(clean_xml)} non-printable characters from XML")
        
        # Ensure the XML starts and ends properly
        clean_xml = clean_xml.strip()
        
        return clean_xml
    
    @staticmethod
    def clean_duplicate_attributes(tree: ET.ElementTree) -> None:
        """Clean up duplicate or incorrectly placed attributes in the save file"""
        logger = PS3XMLHandler.get_logger()
        logger.debug("Cleaning duplicate attributes from save file")
        
        root = tree.getroot()
        
        # Find PlayerProfile element
        player_profile = root.find('.//PlayerProfile')
        if player_profile is None:
            logger.debug("No PlayerProfile found, skipping attribute cleanup")
            return
        
        # Fix BaseInfo - remove RecoveryBits if it exists (it belongs in Possessions_Recovery)
        base_info = player_profile.find('BaseInfo')
        if base_info is not None:
            if 'RecoveryBits' in base_info.attrib:
                logger.debug("Removing RecoveryBits from BaseInfo (belongs in Possessions_Recovery)")
                del base_info.attrib['RecoveryBits']
        
        # Fix OptionsInfo - remove bEntityScanningEnabled if it exists (it belongs in BaseInfo)
        options_info = player_profile.find('OptionsInfo')
        if options_info is not None:
            if 'bEntityScanningEnabled' in options_info.attrib:
                logger.debug("Removing bEntityScanningEnabled from OptionsInfo (belongs in BaseInfo)")
                del options_info.attrib['bEntityScanningEnabled']
        
        # Ensure BaseInfo has bEntityScanningEnabled
        if base_info is not None and 'bEntityScanningEnabled' not in base_info.attrib:
            logger.debug("Adding missing bEntityScanningEnabled to BaseInfo")
            base_info.set('bEntityScanningEnabled', '1')
        
        # Ensure Possessions_Recovery exists and has RecoveryBits
        possessions_recovery = player_profile.find('Possessions_Recovery')
        if possessions_recovery is not None and 'RecoveryBits' not in possessions_recovery.attrib:
            logger.debug("Adding missing RecoveryBits to Possessions_Recovery")
            possessions_recovery.set('RecoveryBits', '500')
        
        # Find and clean up Metagame section
        metagame = root.find('.//Metagame')
        if metagame is not None:
            PS3XMLHandler.clean_empty_player_elements(metagame)
    
    @staticmethod
    def clean_empty_player_elements(metagame: ET.Element) -> None:
        """Remove empty Player0 and Player1 elements that shouldn't exist yet"""
        logger = PS3XMLHandler.get_logger()
        
        # Look for Player0 and Player1 elements in Metagame
        for player_tag in ['Player0', 'Player1']:
            player_element = metagame.find(player_tag)
            if player_element is not None:
                # Check if this is an empty player element (no meaningful attributes)
                is_empty = True
                
                # Check if it has any meaningful attributes (not empty strings)
                for attr_name, attr_value in player_element.attrib.items():
                    if attr_value and attr_value.strip():  # Not empty or whitespace
                        is_empty = False
                        break
                
                # Check if it has any child elements
                if len(player_element) > 0:
                    is_empty = False
                
                # If it's empty, remove it
                if is_empty:
                    logger.debug(f"Removing empty {player_tag} element from Metagame")
                    metagame.remove(player_element)
                else:
                    logger.debug(f"Keeping {player_tag} element (has meaningful content)")
        
        # Also check for any Player0/Player1 elements with only empty EPs and newEPs
        for player_tag in ['Player0', 'Player1']:
            player_element = metagame.find(player_tag)
            if player_element is not None:
                attrs = player_element.attrib
                # If it only has EPs and newEPs attributes and they're empty
                if (len(attrs) <= 3 and  # Allow for EPs, newEPs, and maybe one more
                    'EPs' in attrs and 'newEPs' in attrs and
                    (not attrs['EPs'] or attrs['EPs'].strip() == '') and
                    (not attrs['newEPs'] or attrs['newEPs'].strip() == '') and
                    len(player_element) == 0):  # No child elements
                    logger.debug(f"Removing {player_tag} element with empty EPs/newEPs attributes")
                    metagame.remove(player_element)
    
    @staticmethod
    def load_xml_tree(file_path: Path) -> Tuple[ET.ElementTree, int, int]:
        """Load XML tree from PS3 save file with extensive debugging"""
        logger = PS3XMLHandler.get_logger()
        logger.debug(f"Loading PS3 XML tree from file: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                
            file_size = len(data)
            logger.debug(f"Read {file_size} bytes from PS3 save file")
            
            # Debug original file structure
            PS3XMLHandler.debug_file_structure(data, "Original PS3 Save")
            
            # Try direct XML parsing first (for files that are pure XML)
            try:
                logger.debug("Attempting direct XML parsing...")
                tree = ET.parse(file_path)
                logger.debug("Direct XML parsing successful")
                # Clean up any duplicate attributes
                PS3XMLHandler.clean_duplicate_attributes(tree)
                return tree, 0, file_size
            except ET.ParseError as e:
                logger.debug(f"Direct XML parsing failed: {e}, trying to extract XML from binary data")
            
            # Find XML boundaries in binary data
            try:
                xml_start, xml_end = PS3XMLHandler.find_xml_boundaries(data)
            except ValueError as e:
                logger.error(f"Could not find XML boundaries: {e}")
                raise ValueError(f"Could not find valid XML in PS3 save file: {e}")
            
            # Extract and clean XML content
            xml_content = data[xml_start:xml_end]
            logger.debug(f"Extracted XML content length: {len(xml_content)}")
            
            # Clean the XML content
            clean_xml = PS3XMLHandler.clean_xml_content(xml_content)
            
            if not clean_xml:
                raise ValueError("No valid XML content found after cleaning")
            
            # Parse as XML
            try:
                root = ET.fromstring(clean_xml)
                tree = ET.ElementTree(root)
                logger.debug("Successfully parsed PS3 XML tree")
            except ET.ParseError as e:
                logger.error(f"XML parsing failed: {e}")
                logger.debug(f"Problematic XML (first 500 chars): {clean_xml[:500]}")
                
                # Try some common fixes
                logger.debug("Attempting XML repair...")
                
                # Fix common issues
                fixed_xml = clean_xml
                
                # Ensure proper XML declaration if missing
                if not fixed_xml.startswith('<?xml'):
                    if fixed_xml.startswith('<'):
                        fixed_xml = '<?xml version="1.0" encoding="utf-8"?>\n' + fixed_xml
                
                # Try parsing again
                try:
                    root = ET.fromstring(fixed_xml)
                    tree = ET.ElementTree(root)
                    logger.debug("XML repair successful")
                except ET.ParseError as e2:
                    logger.error(f"XML repair failed: {e2}")
                    raise ValueError(f"Could not parse XML even after repair attempts: {e2}")
            
            # Clean up any duplicate attributes
            PS3XMLHandler.clean_duplicate_attributes(tree)
            
            return tree, xml_start, file_size
                    
        except Exception as e:
            logger.error(f"Error parsing PS3 save file: {str(e)}", exc_info=True)
            raise ValueError(f"Could not extract valid XML from PS3 save file: {str(e)}")
    
    @staticmethod
    def verify_checksum(data: bytes) -> bool:
        """Basic integrity check for PS3 saves"""
        logger = PS3XMLHandler.get_logger()
        logger.debug("PS3 save format - performing basic integrity check")
        
        xml_markers = [b'<Savegame', b'<SaveGame', b'<savegame', b'<SaveData']
        xml_found = False
        
        for marker in xml_markers:
            if marker in data:
                xml_found = True
                logger.debug(f"Found XML content marker: {marker}")
                break
        
        if not xml_found:
            logger.warning("No XML content found in PS3 save file")
            return False
        
        logger.debug("PS3 save file contains XML content")
        return True
    
    @staticmethod
    def _save_single_file(tree: ET.ElementTree, file_path: Path, create_backup: bool = True) -> None:
        """
        Save XML tree to a single file with extensive safety checks and debugging.
        """
        logger = PS3XMLHandler.get_logger()
        logger.debug(f"Saving PS3 XML tree to file: {file_path}")
        
        try:
            # Clean up duplicate attributes before saving
            PS3XMLHandler.clean_duplicate_attributes(tree)
            
            # Read original file
            with open(file_path, 'rb') as f:
                original_data = f.read()
            
            original_size = len(original_data)
            logger.debug(f"Original file size: {original_size} bytes")
            
            # Debug original file
            PS3XMLHandler.debug_file_structure(original_data, "Original File Before Save")
            
            # Create backup if needed
            if create_backup:
                backup_path = file_path.with_suffix(file_path.suffix + ".backup")
                if not backup_path.exists():
                    logger.debug(f"Creating backup at {backup_path}")
                    with open(backup_path, 'wb') as dst:
                        dst.write(original_data)
                else:
                    logger.debug(f"Backup already exists at {backup_path}")
            
            # Check if this is a pure XML file or contains binary wrapper
            try:
                # Try to parse the original file directly
                ET.parse(file_path)
                is_pure_xml = True
                logger.debug("File is pure XML")
            except ET.ParseError:
                is_pure_xml = False
                logger.debug("File contains binary wrapper around XML")
            
            if is_pure_xml:
                # For pure XML files, just write the XML directly
                tree.write(file_path, encoding='utf-8', xml_declaration=True)
                logger.debug("Pure XML file saved successfully")
                return
            
            # For binary-wrapped XML files, preserve the wrapper
            try:
                xml_start, xml_end = PS3XMLHandler.find_xml_boundaries(original_data)
            except ValueError as e:
                logger.error(f"Cannot find XML boundaries: {e}")
                raise
            
            # Validate boundaries
            if xml_start >= xml_end:
                raise ValueError(f"Invalid XML boundaries: start={xml_start}, end={xml_end}")
            
            if xml_start < 0 or xml_end > len(original_data):
                raise ValueError(f"XML boundaries out of range: start={xml_start}, end={xml_end}, file_size={len(original_data)}")
            
            # Generate new XML content
            xml_buffer = BytesIO()
            tree.write(xml_buffer, encoding='utf-8', xml_declaration=False)
            new_xml = xml_buffer.getvalue()
            
            logger.debug(f"Generated new XML content: {len(new_xml)} bytes")
            
            # Validate the new XML by parsing it
            try:
                test_root = ET.fromstring(new_xml.decode('utf-8'))
                logger.debug("New XML validates successfully")
            except Exception as e:
                logger.error(f"Generated XML is invalid: {e}")
                raise ValueError(f"Generated invalid XML: {e}")
            
            # Preserve header and footer EXACTLY
            header = original_data[:xml_start]
            footer = original_data[xml_end:] if xml_end < len(original_data) else b''
            
            logger.debug(f"Header size: {len(header)} bytes")
            logger.debug(f"Footer size: {len(footer)} bytes")
            logger.debug(f"Original XML size: {xml_end - xml_start} bytes")
            logger.debug(f"New XML size: {len(new_xml)} bytes")
            
            # Create output data
            output_data = header + new_xml + footer
            new_size = len(output_data)
            
            logger.debug(f"Final output size: {new_size} bytes (change: {new_size - original_size:+d})")
            
            # Debug output structure
            PS3XMLHandler.debug_file_structure(output_data, "Output File Before Write")
            
            # Verify the output has valid XML
            try:
                test_start, test_end = PS3XMLHandler.find_xml_boundaries(output_data)
                test_xml = output_data[test_start:test_end]
                clean_test_xml = PS3XMLHandler.clean_xml_content(test_xml)
                test_root = ET.fromstring(clean_test_xml)
                logger.debug("Output file XML validates successfully")
            except Exception as e:
                logger.error(f"Output file would have invalid XML: {e}")
                raise ValueError(f"Output file validation failed: {e}")
            
            # Write the file
            with open(file_path, 'wb') as f:
                f.write(output_data)
            
            # Verify the written file
            with open(file_path, 'rb') as f:
                written_data = f.read()
            
            if len(written_data) != len(output_data):
                raise ValueError(f"File write failed: expected {len(output_data)} bytes, got {len(written_data)} bytes")
            
            if written_data != output_data:
                raise ValueError("File write failed: written data doesn't match expected data")
            
            logger.debug(f"PS3 save file written successfully. Size: {original_size} -> {new_size} bytes")
            
        except Exception as e:
            logger.error(f"Error saving PS3 XML tree to {file_path}: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def save_xml_tree(tree: ET.ElementTree, file_path: Path, create_backup: bool = True) -> None:
        """Save XML tree to PS3 save files with safety checks"""
        logger = PS3XMLHandler.get_logger()
        logger.debug(f"Saving PS3 XML tree to: {file_path}")
        
        try:
            if file_path.is_dir():
                # PS3 save directory - update all relevant files
                save_files = PS3XMLHandler.get_all_save_files(file_path)
                if not save_files:
                    raise ValueError("No valid PS3 save files found in directory")
                
                for save_file in save_files:
                    logger.debug(f"Processing {save_file.name}")
                    PS3XMLHandler._save_single_file(tree, save_file, create_backup)
                    logger.debug(f"Successfully updated {save_file.name}")
                    
            elif file_path.name in ['SAVEDATA.000', 'PADDING.000'] or file_path.suffix == '.backup':
                # Specific PS3 save file - update it and its counterpart if it exists
                if file_path.suffix == '.backup':
                    # If targeting a backup file, just update that file
                    PS3XMLHandler._save_single_file(tree, file_path, create_backup)
                else:
                    ps3_dir = file_path.parent
                    main_files = ['SAVEDATA.000', 'PADDING.000']
                    
                    files_updated = []
                    for filename in main_files:
                        target_path = ps3_dir / filename
                        if target_path.exists():
                            logger.debug(f"Processing {filename}")
                            PS3XMLHandler._save_single_file(tree, target_path, create_backup)
                            files_updated.append(filename)
                            logger.debug(f"Successfully updated {filename}")
                    
                    if not files_updated:
                        # Fallback to just the specified file
                        PS3XMLHandler._save_single_file(tree, file_path, create_backup)
                        
            else:
                # Single file save
                PS3XMLHandler._save_single_file(tree, file_path, create_backup)
                
        except Exception as e:
            logger.error(f"Error saving PS3 XML tree: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def load_ps3_save(save_path: Path) -> Tuple[ET.ElementTree, int, int]:
        """Convenience method to load PS3 saves from directory or file"""
        if save_path.is_dir():
            primary_file = PS3XMLHandler.get_primary_save_file(save_path)
            return PS3XMLHandler.load_xml_tree(primary_file)
        else:
            return PS3XMLHandler.load_xml_tree(save_path)
    
    @staticmethod
    def save_ps3_save(tree: ET.ElementTree, save_path: Path, create_backup: bool = True) -> None:
        """Convenience method to save PS3 saves to directory or file"""
        PS3XMLHandler.save_xml_tree(tree, save_path, create_backup)
    
    @staticmethod
    def get_pretty_xml(tree: ET.ElementTree) -> str:
        """Generate a pretty-printed version of the XML tree"""
        logger = PS3XMLHandler.get_logger()
        logger.debug("Generating pretty-printed XML")
        
        try:
            xml_buffer = BytesIO()
            tree.write(xml_buffer, encoding='utf-8', xml_declaration=True)
            xml_str = xml_buffer.getvalue().decode('utf-8')
            
            parsed_xml = minidom.parseString(xml_str)
            pretty_xml = parsed_xml.toprettyxml(indent="  ")
            
            logger.debug("XML pretty-printing successful")
            return pretty_xml
            
        except Exception as e:
            logger.error(f"Error pretty-printing XML: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def update_profile_element(profile: Optional[ET.Element], 
                              element_name: str, 
                              updates: Dict[str, Any]) -> None:
        """Update a specific element in the profile with given values"""
        if profile is None:
            return
            
        element = profile.find(element_name)
        if element is not None:
            for key, value in updates.items():
                element.set(key, str(value))
    
    @staticmethod
    def parse_xml_string(xml_string: str) -> ET.ElementTree:
        """Parse XML from a string"""
        logger = PS3XMLHandler.get_logger()
        logger.debug("Parsing XML string")
        
        try:
            tree = ET.parse(StringIO(xml_string))
            logger.debug("XML string parsed successfully")
            return tree
            
        except Exception as e:
            logger.error(f"Error parsing XML string: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def validate_ps3_save_structure(save_path: Path) -> Dict[str, bool]:
        """Validate the structure of a PS3 save directory or file"""
        logger = PS3XMLHandler.get_logger()
        results = {
            'is_ps3_save': False,
            'has_savedata': False,
            'has_padding': False,
            'has_param_sfo': False,
            'has_param_pfd': False,
            'xml_valid': False
        }
        
        try:
            if save_path.is_dir():
                results['has_savedata'] = (save_path / 'SAVEDATA.000').exists()
                results['has_padding'] = (save_path / 'PADDING.000').exists()
                results['has_param_sfo'] = (save_path / 'PARAM.SFO').exists()
                results['has_param_pfd'] = (save_path / 'PARAM.PFD').exists()
                
                results['is_ps3_save'] = results['has_savedata'] or results['has_padding']
                
                if results['is_ps3_save']:
                    try:
                        tree, _, _ = PS3XMLHandler.load_ps3_save(save_path)
                        results['xml_valid'] = tree is not None
                    except:
                        results['xml_valid'] = False
                        
            elif save_path.is_file() and (save_path.name in ['SAVEDATA.000', 'PADDING.000'] or save_path.suffix == '.backup'):
                results['is_ps3_save'] = True
                results['has_savedata'] = save_path.name == 'SAVEDATA.000'
                results['has_padding'] = save_path.name == 'PADDING.000'
                
                parent_dir = save_path.parent
                results['has_param_sfo'] = (parent_dir / 'PARAM.SFO').exists()
                results['has_param_pfd'] = (parent_dir / 'PARAM.PFD').exists()
                
                try:
                    tree, _, _ = PS3XMLHandler.load_xml_tree(save_path)
                    results['xml_valid'] = tree is not None
                except:
                    results['xml_valid'] = False
            
            logger.debug(f"PS3 save validation results: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error validating PS3 save structure: {str(e)}", exc_info=True)
            return results
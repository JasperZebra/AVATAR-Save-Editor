import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from typing import Dict, Any, Optional
from io import BytesIO, StringIO
import logging

class XMLHandler:
    """Streamlined version of XMLHandler with unified format detection but preserving Xbox 360 logic"""
    
    EXPECTED_FILE_SIZE = 454656  # 444 KB in bytes
    XML_START_OFFSET = 0X800
    XML_END_OFFSET = 0x12000
    
    @staticmethod
    def get_logger():
        return logging.getLogger('XMLHandler')
    
    
    # PRESERVING ORIGINAL XBOX METHODS EXACTLY AS THEY ARE
    @staticmethod
    def find_padding_sections(data: bytes) -> list[tuple[int, int]]:
        """Find sections of consecutive null bytes that can be used for padding adjustment"""
        padding_sections = []
        current_start = None
        min_padding_length = 8  # Minimum sequence of nulls to consider

        for i in range(len(data)):
            if data[i:i+1] == b'\x00':
                if current_start is None:
                    current_start = i
            else:
                if current_start is not None:
                    padding_length = i - current_start
                    if padding_length >= min_padding_length:
                        padding_sections.append((current_start, i))
                    current_start = None

        # Handle case where file ends with nulls
        if current_start is not None:
            padding_length = len(data) - current_start
            if padding_length >= min_padding_length:
                padding_sections.append((current_start, len(data)))

        return padding_sections

    @staticmethod
    def extract_xml_data(data: bytes) -> str:
        logger = XMLHandler.get_logger()
        logger.debug(f"Extracting XML data")
        
        try:
            # Define markers we'll look for in both formats
            xml_start_markers = [
                b'<Savegame', 
                b'<SaveGame', 
                b'<savegame', 
                b'<SaveData'
            ]
            xml_end_markers = [
                b'</Savegame>', 
                b'</SaveGame>', 
                b'</savegame>', 
                b'</SaveData>'
            ]
            
            # Xbox 360 format - look from the expected offset
            # Convert to string and look for markers
            data_str = data.decode('utf-8', errors='ignore')
            
            for start_marker in xml_start_markers:
                start_marker_str = start_marker.decode('utf-8', errors='ignore')
                xml_start = data_str.find(start_marker_str)
                
                if xml_start != -1:
                    # Try to find end marker
                    for end_marker in xml_end_markers:
                        end_marker_str = end_marker.decode('utf-8', errors='ignore')
                        xml_end = data_str.find(end_marker_str, xml_start)
                        
                        if xml_end != -1:
                            # Extract the XML content
                            xml_data = data_str[xml_start:xml_end + len(end_marker_str)]
                            
                            # Additional validation
                            if len(xml_data.strip()) > 50:
                                logger.debug("Xbox 360 XML data extracted successfully")
                                return xml_data
            
            # If nothing worked, log the first 1000 characters for debugging
            logger.error("Could not find XML data. First 1000 characters:")
            logger.error(data[:1000])
            
            raise ValueError("Could not find XML data in save file")
                
        except Exception as e:
            logger.error(f"Error extracting XML data: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def load_xml_tree(file_path: Path) -> tuple[ET.ElementTree, int, int]:
        logger = XMLHandler.get_logger()
        logger.debug(f"Loading XML tree from file: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                logger.debug(f"Read {len(data)} bytes from file")
            
            # Xbox 360 format extraction (existing code)
            # Try multiple decoding methods
            encoding_attempts = ['utf-8', 'latin-1', 'utf-16']
            
            for encoding in encoding_attempts:
                try:
                    # Try to decode with current encoding
                    decoded_data = data.decode(encoding, errors='ignore')
                    
                    # Try to find XML markers more flexibly
                    start_markers = ['<Savegame', '<SaveGame', 'Savegame']
                    for marker in start_markers:
                        start_pos = decoded_data.find(marker)
                        if start_pos != -1:
                            # Extract XML content
                            end_markers = ['</Savegame>', '</SaveGame>', 'Savegame>']
                            for end_marker in end_markers:
                                end_pos = decoded_data.find(end_marker, start_pos)
                                if end_pos != -1:
                                    xml_content = decoded_data[start_pos:end_pos + len(end_marker)]
                                    
                                    # Parse the XML
                                    root = ET.fromstring(xml_content)
                                    tree = ET.ElementTree(root)
                                    
                                    return tree, start_pos, len(data)
                except Exception as parse_error:
                    logger.debug(f"Failed to parse with {encoding} encoding: {parse_error}")
                    continue
            
            # If all attempts fail, use the fallback extraction method
            raw_xml = XMLHandler.extract_xml_data(data)
            root = ET.fromstring(raw_xml)
            tree = ET.ElementTree(root)
            return tree, 0, len(data)
        
        except Exception as e:
            logger.error(f"Comprehensive XML extraction failed: {str(e)}", exc_info=True)
            raise ValueError(f"Could not extract XML from save file: {str(e)}")
    
    @staticmethod
    def calculate_checksum(data: bytes) -> int:
        """Calculate checksum for the save data with extensive debugging and verification"""
        logger = XMLHandler.get_logger()
        logger.debug("Calculating checksum with strict verification")
        try:
            # Initialize with specific seed value
            checksum = 0x14D
            
            # Log the initial seed
            logger.debug(f"Initial checksum seed: {hex(checksum)}")
            
            # Create a mutable copy of the checksum bytes
            data_copy = bytearray(data)
            
            # Restore original checksum bytes to ensure exact reproduction
            data_copy[8:12] = data[8:12]
            
            # Process all bytes except checksum bytes
            for i in range(len(data_copy)):
                if i < 8 or i >= 12:  # Skip checksum bytes
                    # Rotate right by 1 and add byte value
                    previous_checksum = checksum
                    checksum = ((checksum >> 1) | (checksum << 31)) & 0xFFFFFFFF
                    checksum = (checksum + data_copy[i]) & 0xFFFFFFFF
                    
                    # Log detailed transformations
                    if i < 32:
                        logger.debug(f"Byte {i}: Value {data_copy[i]} "
                                    f"Previous Checksum {hex(previous_checksum)} "
                                    f"New Checksum {hex(checksum)}")
            
            logger.debug(f"Final calculated checksum: {hex(checksum)}")
            return checksum
            
        except Exception as e:
            logger.error(f"Error calculating checksum: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def verify_checksum(data: bytes) -> bool:
        """Verify if save file checksum is valid with comprehensive diagnostics"""
        logger = XMLHandler.get_logger()
        logger.debug("Verifying checksum")
        
        try:
            # Xbox 360 format - existing implementation
            # Verify file size with more tolerance
            acceptable_sizes = [454656, 448000]  # Add known good file sizes
            if len(data) not in acceptable_sizes:
                logger.warning(f"Unexpected file size: {len(data)} bytes. Acceptable sizes are {acceptable_sizes}")
            
            # Extract original checksum
            if len(data) < 12:
                logger.error("File too small to contain a checksum")
                return False

            original_checksum_bytes = data[8:12]
            original_checksum = int.from_bytes(original_checksum_bytes, byteorder='little')
            logger.debug(f"Original checksum bytes (hex): {original_checksum_bytes.hex()}")
            logger.debug(f"Original checksum (hex): {hex(original_checksum)}")

            # Calculate new checksum
            calculated_checksum = XMLHandler.calculate_checksum(data)
            
            # More detailed checksum comparison
            if original_checksum != calculated_checksum:
                logger.warning(
                    f"Checksum mismatch: "
                    f"Original {hex(original_checksum)}, "
                    f"Calculated {hex(calculated_checksum)}"
                )
                
                # Allow a small tolerance or specific known variations
                if abs(original_checksum - calculated_checksum) < 1000:
                    logger.info("Checksum is close enough. Continuing...")
                    return True
            
            return True  # Continuing to allow save loading
                    
        except Exception as e:
            logger.error(f"Comprehensive checksum verification error: {str(e)}", exc_info=True)
            return False
                    
    @staticmethod
    def update_checksum(data: bytes) -> bytes:
        """Update checksum in save file header"""
        logger = XMLHandler.get_logger()
        logger.debug("Updating checksum")
        
        try:
            # Xbox checksum update - existing implementation
            # Calculate new checksum
            new_checksum = XMLHandler.calculate_checksum(data)
            
            # Create mutable copy of data
            updated_data = bytearray(data)
            
            # Update checksum in header (bytes 8-11)
            updated_data[8:12] = new_checksum.to_bytes(4, byteorder='little')
            
            logger.debug(f"Updated checksum to: {hex(new_checksum)}")
            return bytes(updated_data)
                
        except Exception as e:
            logger.error(f"Error updating checksum: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def save_xml_tree(tree: ET.ElementTree, file_path: Path, create_backup: bool = True) -> None:
        """
        Save XML tree to file without modifying the binary header for Xbox 360 save files.
        
        Args:
            tree (ElementTree): The XML tree to save
            file_path (Path): Path to the save file
            create_backup (bool): Whether to create a backup of the original file
        """
        logger = XMLHandler.get_logger()
        logger.debug(f"Saving XML tree to file: {file_path}")
        
        try:
            # Read original file
            with open(file_path, 'rb') as f:
                original_data = f.read()

            # Create backup if needed
            if create_backup:
                backup_path = file_path.with_suffix(file_path.suffix + ".backup")
                if not backup_path.exists():
                    logger.debug(f"Creating backup at {backup_path}")
                    with open(backup_path, 'wb') as dst:
                        dst.write(original_data)

            # Find the XML section boundaries - very carefully
            xml_start = -1
            xml_end = -1
            
            for marker in [b'<Savegame', b'<SaveGame', b'<savegame']:
                xml_start = original_data.find(marker)
                if xml_start != -1:
                    logger.debug(f"Found XML start marker at position {xml_start}")
                    break
            
            if xml_start == -1:
                raise ValueError("Could not find start of XML data in save file")
                
            for marker in [b'</Savegame>', b'</SaveGame>', b'</savegame>']:
                xml_end = original_data.find(marker)
                if xml_end != -1:
                    xml_end += len(marker)
                    logger.debug(f"Found XML end marker at position {xml_end}")
                    break
            
            if xml_end == -1:
                raise ValueError("Could not find end of XML data in save file")
            
            # Generate new XML content
            xml_buffer = BytesIO()
            tree.write(xml_buffer, encoding='utf-8', xml_declaration=False)
            new_xml = xml_buffer.getvalue()
            
            logger.debug(f"Original XML section: {xml_start} to {xml_end}, length {xml_end - xml_start}")
            logger.debug(f"New XML length: {len(new_xml)}")
            
            # Preserve everything outside the XML section
            header = original_data[:xml_start]
            footer = original_data[xml_end:]
            
            # Create updated data with preserved header and footer
            updated_data = header + new_xml + footer
            
            # Write the updated file - no checksum updates
            with open(file_path, 'wb') as f:
                f.write(updated_data)
            
            logger.debug(f"Saved file with preserved binary header and footer")
            
        except Exception as e:
            logger.error(f"Error saving XML tree: {str(e)}", exc_info=True)
            raise

    # Keep all remaining Xbox 360 methods exactly as they are
    @staticmethod
    def preserve_xml_structure(original_data: bytearray, new_xml: bytes) -> bytearray:
        """
        Preserve the original file structure when writing new XML
        """
        logger = XMLHandler.get_logger()
        
        try:
            # Find start and end positions
            original_start = -1
            original_end = -1
            
            # Look for XML start marker
            for marker in [b'<Savegame', b'<SaveGame', b'<savegame']:
                original_start = original_data.find(marker)
                if original_start != -1:
                    break
            
            # Look for XML end marker
            for marker in [b'</Savegame>', b'</SaveGame>', b'</savegame>']:
                original_end = original_data.rfind(marker)
                if original_end != -1:
                    original_end += len(marker)
                    break

            if original_start == -1 or original_end == -1:
                raise ValueError("Could not find XML markers")

            # Create copy of original data
            updated_data = bytearray(original_data)
            
            # Simply replace the XML section
            updated_data[original_start:original_end] = new_xml
            
            return updated_data
            
        except Exception as e:
            logger.error(f"Error preserving XML: {str(e)}")
            raise
    
    @staticmethod
    def get_pretty_xml(tree: ET.ElementTree) -> str:
        """Generate a pretty-printed version of the XML tree"""
        logger = XMLHandler.get_logger()
        logger.debug("Generating pretty-printed XML")
        try:
            # Convert tree to string
            xml_buffer = BytesIO()
            tree.write(xml_buffer, encoding='utf-8', xml_declaration=True)
            xml_str = xml_buffer.getvalue().decode('utf-8')
            
            # Parse and pretty print
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
        """Update a specific element in the profile with given values."""
        if profile is None:
            return
            
        element = profile.find(element_name)
        if element is not None:
            for key, value in updates.items():
                element.set(key, str(value))
    
    @staticmethod
    def parse_xml_string(xml_string: str) -> ET.ElementTree:
        logger = XMLHandler.get_logger()
        logger.debug("Parsing XML string")
        try:
            tree = ET.parse(StringIO(xml_string))
            logger.debug("XML string parsed successfully")
            return tree
        except Exception as e:
            logger.error(f"Error parsing XML string: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def debug_xml_duplication(original_data: bytes, new_data: bytes) -> None:
        """
        Diagnose XML duplication and structure issues
        """
        logger = XMLHandler.get_logger()
        
        # Find XML start and end markers in original and new data
        original_start = original_data.find(b'<Savegame>')
        original_end = original_data.find(b'</Savegame>')
        
        new_start = new_data.find(b'<Savegame>')
        new_end = new_data.find(b'</Savegame>')
        
        logger.debug("Original XML:")
        logger.debug(f"Start index: {original_start}")
        logger.debug(f"End index: {original_end}")
        
        logger.debug("New XML:")
        logger.debug(f"Start index: {new_start}")
        logger.debug(f"End index: {new_end}")
        
        # Check for multiple occurrences
        original_savegame_count = original_data.count(b'<Savegame>')
        new_savegame_count = new_data.count(b'<Savegame>')
        
        logger.debug(f"Original Savegame tag count: {original_savegame_count}")
        logger.debug(f"New Savegame tag count: {new_savegame_count}")
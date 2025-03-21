import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from typing import Dict, Any, Optional
from io import BytesIO, StringIO
import logging

class PCXMLHandler:
    """
    XML handler specifically designed for PC save files.
    Simplified version of XMLHandler without Xbox 360 binary formatting.
    """
    
    @staticmethod
    def get_logger():
        return logging.getLogger('PCXMLHandler')
    
    @staticmethod
    def load_xml_tree(file_path: Path) -> tuple[ET.ElementTree, int, int]:
        """
        Load XML tree from PC save file, handling potential binary header.
        
        Args:
            file_path (Path): Path to the save file
            
        Returns:
            tuple: (ElementTree, start_offset, file_size)
        """
        logger = PCXMLHandler.get_logger()
        logger.debug(f"Loading PC XML tree from file: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                
            # Get file size for reference
            file_size = len(data)
            
            # Try to find XML start marker directly in the binary data
            # PC save files often have a small binary header before the XML
            xml_start_markers = [b'<Savegame', b'<SaveGame', b'<savegame', b'<SaveData']
            xml_start = -1
            
            for marker in xml_start_markers:
                pos = data.find(marker)
                if pos != -1:
                    xml_start = pos
                    logger.debug(f"Found XML start marker at position {xml_start}")
                    break
            
            if xml_start == -1:
                logger.warning("Could not find XML start marker, attempting direct parse")
                try:
                    # Try direct parsing as fallback
                    tree = ET.parse(file_path)
                    return tree, 0, file_size
                except ET.ParseError:
                    raise ValueError("Could not find valid XML in save file")
            
            # Find the corresponding end marker
            xml_end_markers = [b'</Savegame>', b'</SaveGame>', b'</savegame>', b'</SaveData>']
            xml_end = -1
            
            for marker in xml_end_markers:
                pos = data.rfind(marker)
                if pos != -1:
                    xml_end = pos + len(marker)
                    logger.debug(f"Found XML end marker at position {xml_end}")
                    break
            
            if xml_end == -1:
                # If no end marker found, try direct parsing
                logger.warning("Could not find XML end marker, attempting direct parse")
                try:
                    tree = ET.parse(file_path)
                    return tree, 0, file_size
                except ET.ParseError:
                    raise ValueError("Could not find valid XML end marker in save file")
            
            # Extract XML content
            xml_content = data[xml_start:xml_end]
            
            # Decode to string
            xml_string = xml_content.decode('utf-8', errors='ignore')
            
            # Parse as XML
            root = ET.fromstring(xml_string)
            tree = ET.ElementTree(root)
            
            logger.debug(f"Successfully extracted and parsed PC XML, start: {xml_start}, end: {xml_end}")
            return tree, xml_start, file_size
                    
        except Exception as e:
            logger.error(f"Error parsing PC save file: {str(e)}", exc_info=True)
            
            # Last resort - try direct parsing
            try:
                logger.debug("Attempting direct parse as last resort")
                tree = ET.parse(file_path)
                return tree, 0, file_size
            except:
                raise ValueError(f"Could not extract valid XML from PC save file: {str(e)}")
            
    @staticmethod
    def verify_checksum(data: bytes) -> bool:
        """
        PC saves don't typically use the same checksum mechanism as Xbox 360.
        This is a simplified placeholder that always returns True.
        
        Args:
            data (bytes): The save file data
            
        Returns:
            bool: Always True for PC saves
        """
        logger = PCXMLHandler.get_logger()
        logger.debug("PC save format - skipping checksum verification")
        return True
    
    @staticmethod
    def save_xml_tree(tree: ET.ElementTree, file_path: Path, create_backup: bool = True) -> None:
        """
        Save XML tree to file for PC saves, preserving any binary header if present.
        
        Args:
            tree (ElementTree): The XML tree to save
            file_path (Path): Path to the save file
            create_backup (bool): Whether to create a backup of the original file
        """
        logger = PCXMLHandler.get_logger()
        logger.debug(f"Saving PC XML tree to file: {file_path}")
        
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
            
            # Find the XML section boundaries
            xml_start = -1
            for marker in [b'<Savegame', b'<SaveGame', b'<savegame', b'<SaveData']:
                pos = original_data.find(marker)
                if pos != -1:
                    xml_start = pos
                    logger.debug(f"Found XML start marker at position {xml_start}")
                    break
            
            # Generate new XML content
            xml_buffer = BytesIO()
            tree.write(xml_buffer, encoding='utf-8', xml_declaration=False)
            new_xml = xml_buffer.getvalue()
            
            # Check if we need to preserve header
            if xml_start > 0:
                # Preserve header by combining binary header with new XML
                logger.debug(f"Preserving binary header (first {xml_start} bytes)")
                header = original_data[:xml_start]
                
                # Create output data with preserved header
                output_data = header + new_xml
                
                # Write combined file
                with open(file_path, 'wb') as f:
                    f.write(output_data)
                
                logger.debug(f"Successfully saved PC save with preserved binary header")
            else:
                # No header to preserve, write XML directly
                logger.debug("No binary header detected, writing XML directly")
                tree.write(file_path, encoding='utf-8', xml_declaration=True)
                
            logger.debug("PC save file written successfully")
            
        except Exception as e:
            logger.error(f"Error saving PC XML tree: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def get_pretty_xml(tree: ET.ElementTree) -> str:
        """
        Generate a pretty-printed version of the XML tree.
        
        Args:
            tree (ElementTree): The XML tree to format
            
        Returns:
            str: Pretty-printed XML
        """
        logger = PCXMLHandler.get_logger()
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
        """
        Update a specific element in the profile with given values.
        
        Args:
            profile (Element): The profile element
            element_name (str): Name of the element to update
            updates (Dict): Dictionary of attributes to update
        """
        if profile is None:
            return
            
        element = profile.find(element_name)
        if element is not None:
            for key, value in updates.items():
                element.set(key, str(value))
    
    @staticmethod
    def parse_xml_string(xml_string: str) -> ET.ElementTree:
        """
        Parse XML from a string.
        
        Args:
            xml_string (str): XML content as a string
            
        Returns:
            ElementTree: The parsed XML tree
        """
        logger = PCXMLHandler.get_logger()
        logger.debug("Parsing XML string")
        
        try:
            tree = ET.parse(StringIO(xml_string))
            logger.debug("XML string parsed successfully")
            return tree
            
        except Exception as e:
            logger.error(f"Error parsing XML string: {str(e)}", exc_info=True)
            raise

    # Add any additional PC-specific methods here

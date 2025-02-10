import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from typing import Dict, Any, Optional
from io import BytesIO, StringIO
import logging


class XMLHandler:
    EXPECTED_FILE_SIZE = 454656  # 444 KB in bytes
    XML_START_OFFSET = 0XBB00
    XML_END_OFFSET = 0x5AB00

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
    def get_logger():
        return logging.getLogger('XMLHandler')

    @staticmethod
    def extract_xml_data(data: bytes) -> str:
        logger = XMLHandler.get_logger()
        logger.debug("Extracting XML data from save file")
        try:
            xml_start = data.find(b'<Savegame>')
            if xml_start == -1:
                logger.error("Could not find XML data in save file")
                raise ValueError("Could not find XML data in save file")
            
            xml_data = data[xml_start:]
            decoded_data = xml_data.decode('utf-8', errors='ignore')
            logger.debug("XML data extracted successfully")
            return decoded_data
            
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
            
            # Use the defined offsets instead of searching
            xml_data = data[XMLHandler.XML_START_OFFSET:XMLHandler.XML_END_OFFSET]
            
            # Add debugging to inspect the raw data
            logger.debug(f"First 50 bytes of XML section: {xml_data[:50]}")
            logger.debug(f"Total XML section length: {len(xml_data)} bytes")
            
            # Try to find the start of the XML
            xml_start_marker = xml_data.find(b'<Savegame>')
            if xml_start_marker == -1:
                logger.error("Could not find <Savegame> start tag")
                raise ValueError("Invalid XML structure: <Savegame> tag not found")
            
            # Extract XML data from the start marker
            cleaned_xml_data = xml_data[xml_start_marker:]
            
            # Decode with error handling and strip any potential BOM or weird leading characters
            decoded_data = cleaned_xml_data.decode('utf-8', errors='replace').lstrip('\ufeff\ufffe')
            
            # Additional debugging
            logger.debug(f"Decoded XML starts with: {decoded_data[:100]}")
            
            # Parse the XML
            root = ET.fromstring(decoded_data)
            tree = ET.ElementTree(root)
            
            return tree, XMLHandler.XML_START_OFFSET, len(data)
            
        except Exception as e:
            logger.error(f"Error loading XML tree: {str(e)}", exc_info=True)
            
            # If previous method fails, try a more aggressive approach
            try:
                # Try to find the XML start manually
                xml_start = data.find(b'<Savegame>')
                if xml_start == -1:
                    raise ValueError("Could not locate XML start tag in entire file")
                
                # Extract from start of Savegame tag to end
                xml_end = data.find(b'</Savegame>', xml_start)
                if xml_end == -1:
                    xml_end = len(data)
                
                xml_data = data[xml_start:xml_end+len(b'</Savegame>')]
                
                # Decode and clean
                decoded_data = xml_data.decode('utf-8', errors='replace').lstrip('\ufeff\ufffe')
                
                root = ET.fromstring(decoded_data)
                tree = ET.ElementTree(root)
                
                return tree, xml_start, len(data)
            
            except Exception as secondary_error:
                logger.error(f"Fallback XML extraction failed: {str(secondary_error)}", exc_info=True)
                raise

    @staticmethod
    def save_xml_tree(tree: ET.ElementTree, file_path: Path, create_backup: bool = True) -> None:
        logger = XMLHandler.get_logger()
        logger.debug(f"Saving XML tree to file: {file_path}")
        try:
            # Create backup
            if create_backup:
                backup_path = file_path.with_suffix(file_path.suffix + ".backup")
                if not backup_path.exists():
                    with open(file_path, 'rb') as src, open(backup_path, 'wb') as dst:
                        dst.write(src.read())

            # Read original file
            with open(file_path, 'rb') as f:
                original_data = bytearray(f.read())

            # Generate new XML
            xml_buffer = BytesIO()
            tree.write(xml_buffer, encoding='utf-8', xml_declaration=False)
            new_xml = xml_buffer.getvalue()

            # Log sizes for debugging
            logger.debug(f"New XML size: {len(new_xml)} bytes")
            
            # Calculate available space in section
            section_size = XMLHandler.XML_END_OFFSET - XMLHandler.XML_START_OFFSET
            logger.debug(f"Available XML section size: {section_size} bytes")

            # Extract the current XML section
            section_data = original_data[XMLHandler.XML_START_OFFSET:XMLHandler.XML_END_OFFSET]
            
            # Find padding sections within the XML section
            padding_sections = XMLHandler.find_padding_sections(section_data)
            
            # Calculate total available null bytes
            total_null_bytes = sum(section[1] - section[0] for section in padding_sections)
            logger.debug(f"Total null bytes found: {total_null_bytes}")
            logger.debug(f"Padding sections: {padding_sections}")

            # Detailed size check
            required_space = len(new_xml)
            available_space = section_size
            logger.debug(f"Required space: {required_space} bytes")
            logger.debug(f"Available space: {available_space} bytes")

            # Throw a more informative error if space is insufficient
            if required_space > available_space:
                raise ValueError(
                    f"New XML content too large. " 
                    f"Required: {required_space} bytes, "
                    f"Available: {available_space} bytes, "
                    f"Shortfall: {required_space - available_space} bytes"
                )

            # Replace section content
            original_data[XMLHandler.XML_START_OFFSET:XMLHandler.XML_START_OFFSET + len(new_xml)] = new_xml
            
            # Write file
            with open(file_path, 'wb') as f:
                f.write(original_data)

            logger.debug(f"Save file written successfully")

        except Exception as e:
            logger.error(f"Error saving XML tree: {str(e)}", exc_info=True)
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


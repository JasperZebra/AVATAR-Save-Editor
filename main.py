import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET
import logging

from xml_handler import XMLHandler
from territory_manager import TerritoryManager
from stats_manager import StatsManager
from ui_components import ScrollableFrame
from xml_viewer import XMLViewerWindow
from achievements_manager import AchievementsManager

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('save_editor.log'),
        logging.StreamHandler()
    ]
)

class SaveEditor:
    def __init__(self, root: tk.Tk) -> None:
        self.logger = logging.getLogger('SaveEditor')
        self.logger.debug("Initializing Save Editor")
        self.root = root
        self.root.title("Avatar: The Game - Save Editor")
        self.root.geometry("925x600")
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.tree: Optional[ET.ElementTree] = None
        self.file_path: Optional[Path] = None
        self.original_size: Optional[int] = None
        self.xml_start: Optional[int] = None
        
        self.setup_ui()
        self.logger.debug("Save Editor initialization complete")
        
    def setup_ui(self):
        self.logger.debug("Setting up UI components")
        try:
            container = ttk.Frame(self.root)
            container.pack(fill=tk.BOTH, expand=True)
            
            scrollable = ScrollableFrame(container)
            self.main_frame = scrollable.scrollable_frame
            scrollable.pack(fill=tk.BOTH, expand=True)
            
            self._create_file_section()
            self._create_notebook()
            self.logger.debug("UI setup completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error setting up UI: {str(e)}", exc_info=True)
            raise

    def _create_file_section(self) -> None:
        self.logger.debug("Creating file operations section")
        try:
            file_frame = ttk.LabelFrame(self.main_frame, text="File Operations", padding=10)
            file_frame.pack(fill=tk.X, pady=(0, 15))
            
            # Left side buttons
            button_frame = ttk.Frame(file_frame)
            button_frame.pack(side=tk.LEFT, padx=5)
            
            self.load_button = ttk.Button(
                button_frame, 
                text="Load Save File", 
                command=self.load_save
            )
            self.load_button.pack(side=tk.LEFT, padx=5)
            
            self.xml_viewer_button = ttk.Button(
                button_frame,
                text="View XML",  # Changed from "Open XML Editor"
                command=self.open_xml_viewer  # Changed from open_xml_editor
            )
            self.xml_viewer_button.pack(side=tk.LEFT, padx=5)
            
            self.save_button = ttk.Button(
                button_frame,
                text="Save Changes",
                command=self.save_changes,
                state="disabled"
            )
            self.save_button.pack(side=tk.LEFT, padx=5)
            
            # Add checksum status indicator
            checksum_frame = ttk.Frame(file_frame)
            checksum_frame.pack(side=tk.RIGHT, padx=5)
            
            self.checksum_label = ttk.Label(
                checksum_frame,
                text="Checksum: None",
                font=("", 9)
            )
            self.checksum_label.pack(side=tk.RIGHT, padx=5)
            
            # Right side labels
            label_frame = ttk.Frame(file_frame)
            label_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

            self.file_label = ttk.Label(
                label_frame, 
                text="No file loaded", 
                wraplength=300
            )
            self.file_label.pack(side=tk.LEFT, padx=5)

            self.unsaved_label = ttk.Label(
                label_frame,
                text="",
                foreground="red"
            )
            self.unsaved_label.pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            self.logger.error(f"Error creating file section: {str(e)}", exc_info=True)
            raise

    def open_xml_viewer(self):
        self.logger.debug("Opening XML viewer")
        try:
            if not self.tree:
                self.logger.warning("Attempted to open XML viewer with no file loaded")
                messagebox.showerror("Error", "No save file loaded. Please load a save file first.")
                return
            
            xml_text = XMLHandler.get_pretty_xml(self.tree)
            XMLViewerWindow(self.root, xml_text=xml_text)
            self.logger.debug("XML viewer opened successfully")
            
        except Exception as e:
            self.logger.error(f"Error opening XML viewer: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to open XML viewer: {str(e)}")

    def _create_notebook(self) -> None:
        self.logger.debug("Creating notebook tabs")
        try:
            self.notebook = ttk.Notebook(self.main_frame)
            self.notebook.pack(fill=tk.BOTH, expand=True)
            
            self.stats_frame = ttk.Frame(self.notebook, padding=10)
            self.territory_frame = ttk.Frame(self.notebook, padding=10)
            self.achievements_frame = ttk.Frame(self.notebook, padding=10)
            
            self.notebook.add(self.stats_frame, text="Player Stats")
            self.notebook.add(self.territory_frame, text="Territory Control")
            self.notebook.add(self.achievements_frame, text="Achievements")
            
            self.stats_manager = StatsManager(self.stats_frame, self)
            self.territory_manager = TerritoryManager(self.territory_frame, main_window=self)  # Pass self as main_window
            self.achievements_manager = AchievementsManager(self.achievements_frame, self)
            
            self.logger.debug("Notebook and manager instances created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating notebook: {str(e)}", exc_info=True)
            raise
        
    def load_save(self) -> None:
        self.logger.debug("Loading save file")
        
        # Check for unsaved changes
        if self.unsaved_label.cget("text") == "Unsaved Changes":
            response = messagebox.askyesnocancel(
                "Unsaved Changes", 
                "You have unsaved changes. Do you want to save before loading a new file?",
                icon="warning"
            )
            
            if response is None:  # Cancel
                return
            elif response is True:  # Yes, save changes
                self.save_changes()
        
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("Xbox 360 Save Files", "*.sav")]
            )
            if not file_path:
                self.logger.debug("File selection cancelled")
                return
            
            self.file_path = Path(file_path)
            self.logger.debug(f"Selected file: {self.file_path}")
            self.file_label.config(text=self.file_path.name)

            # Read file and verify checksum before loading XML
            with open(self.file_path, 'rb') as f:
                file_data = f.read()
            
            # Verify checksum
            is_valid = XMLHandler.verify_checksum(file_data)
            self.checksum_label.config(
                text=f"Checksum: {'Valid' if is_valid else 'Invalid'}", 
                foreground="dark green" if is_valid else "red"
            )

            self.logger.debug("Loading XML tree from file")
            self.tree, self.xml_start, self.original_size = XMLHandler.load_xml_tree(self.file_path)
            
            self.logger.debug("Loading data into managers")
            self.stats_manager.load_stats(self.tree)
            self.territory_manager.load_territory_data(self.tree)
            self.achievements_manager.load_achievements(self.tree)
        
            self.save_button.config(state="normal")
            self.unsaved_label.config(text="")
            self.logger.debug("Save file loaded successfully")
            messagebox.showinfo("Success", "Save file loaded successfully!")
        
        except Exception as e:
            self.logger.error(f"Failed to load save file: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to load save file: {str(e)}")

    def save_changes(self) -> None:
        self.logger.debug("Starting save changes operation")
        if not self.tree or not self.file_path:
            self.logger.warning("Attempted to save with no file loaded")
            messagebox.showerror("Error", "No save file loaded!")
            return
                
        try:
            # Ensure the root element exists
            root = self.tree.getroot()
            if root is None:
                self.logger.error("XML tree root is None")
                raise ValueError("Invalid XML structure")

            # Create profile if it doesn't exist
            profile = root.find("PlayerProfile")
            if profile is None:
                profile = ET.SubElement(root, "PlayerProfile")
            
            # Get updates from each manager
            stats_updates = self.stats_manager.get_stats_updates()
            
            # Update sections with fallback creation
            sections = {
                "BaseInfo": stats_updates.get("BaseInfo", {}),
                "XpInfo": stats_updates.get("XpInfo", {}),
                "OptionsInfo": stats_updates.get("OptionsInfo", {}),
                "TimeInfo": stats_updates.get("TimeInfo", {})
            }
            
            for section_name, updates in sections.items():
                # Find or create the section
                section = profile.find(section_name)
                if section is None:
                    section = ET.SubElement(profile, section_name)
                
                # Update section attributes
                for key, value in updates.items():
                    section.set(key, str(value))
            
            # Update territories
            try:
                self.territory_manager.save_territory_changes(self.tree)
            except Exception as territory_error:
                self.logger.error(f"Error saving territory changes: {str(territory_error)}")
            
            # Update achievements
            try:
                self.achievements_manager.save_achievement_changes(self.tree)
            except Exception as achievement_error:
                self.logger.error(f"Error saving achievement changes: {str(achievement_error)}")
            
            # Save file and update checksum
            XMLHandler.save_xml_tree(self.tree, self.file_path)
            
            # Verify checksum after save
            try:
                with open(self.file_path, 'rb') as f:
                    file_data = f.read()
                is_valid = XMLHandler.verify_checksum(file_data)
                
                # Update checksum status
                self.checksum_label.config(
                    text=f"Checksum: {'Valid' if is_valid else 'Invalid'}", 
                    foreground="dark green" if is_valid else "red"
                )
            except Exception as checksum_error:
                self.logger.error(f"Checksum verification failed: {str(checksum_error)}")
                self.checksum_label.config(
                    text="Checksum: Error", 
                    foreground="red"
                )
            
            self.unsaved_label.config(text="")
            self.logger.debug("Changes saved successfully")
            messagebox.showinfo("Success", "Save file modified successfully!\nA backup has been created.")
            
        except ValueError as ve:
            self.logger.error(f"Failed to save changes - size error: {str(ve)}")
            messagebox.showerror("Error", 
                "Failed to save changes: The modified save data is too large.\n"
                "Try removing some modifications to reduce the size.")
        except Exception as e:
            self.logger.error(f"Failed to save changes: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to save changes: {str(e)}")           

    def _on_close(self):
        self.logger.debug("Application closing")
        try:
            if self.unsaved_label.cget("text") == "Unsaved Changes":
                self.logger.debug("Unsaved changes detected")
                response = messagebox.askyesnocancel(
                    "Unsaved Changes",
                    "You have unsaved changes. Would you like to save before closing?",
                    icon="warning"
                )
                
                if response is True:  # Yes, save changes
                    self.logger.debug("Saving changes before exit")
                    self.save_changes()
                    self.root.destroy()
                elif response is False:  # No, close without saving
                    self.logger.debug("Closing without saving changes")
                    self.root.destroy()
                # If response is None (Cancel), do nothing and keep window open
                else:
                    self.logger.debug("Cancel closing, keeping window open")
                
            else:  # No unsaved changes
                self.logger.debug("Closing application (no unsaved changes)")
                self.root.destroy()
                
        except Exception as e:
            self.logger.error(f"Error during application close: {str(e)}", exc_info=True)
            self.root.destroy()  # Ensure application closes even if there's an error          

if __name__ == "__main__":
    root = tk.Tk()
    app = SaveEditor(root)
    root.mainloop()
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
from xml_editor import XMLEditorWindow
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
            
            self.xml_editor_button = ttk.Button(
                button_frame,
                text="Open XML Editor",
                command=self.open_xml_editor
            )
            self.xml_editor_button.pack(side=tk.LEFT, padx=5)
            
            # Add Save Changes button here
            self.save_button = ttk.Button(
                button_frame,
                text="Save Changes",
                command=self.save_changes,
                state="disabled"  # Initially disabled until file is loaded
            )
            self.save_button.pack(side=tk.LEFT, padx=5)
            
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
            
            self.logger.debug("File section created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating file section: {str(e)}", exc_info=True)
            raise

    def open_xml_editor(self):
        self.logger.debug("Opening XML editor")
        try:
            if not self.tree:
                self.logger.warning("Attempted to open XML editor with no file loaded")
                messagebox.showerror("Error", "No save file loaded. Please load a save file first.")
                return
            
            xml_text = XMLHandler.get_pretty_xml(self.tree)
            editor = XMLEditorWindow(self.root, main_editor=self, xml_text=xml_text)  # Pass self as main_editor
            self.logger.debug("XML editor opened successfully")
            
        except Exception as e:
            self.logger.error(f"Error opening XML editor: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to open XML editor: {str(e)}")

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
            # Update the XML tree with changes from each manager
            self.logger.debug("Updating XML tree with changes")
            
            # Update stats
            root = self.tree.getroot()
            profile = root.find("PlayerProfile")
            if profile is not None:
                updates = self.stats_manager.get_stats_updates()
                self.logger.debug(f"Applying stats updates: {updates}")
                
                for section, section_updates in updates.items():
                    if section == "Metagame":
                        metagame = root.find("Metagame")
                        if metagame is not None:
                            for key, value in section_updates.items():
                                metagame.set(key, value)
                    else:
                        section_elem = profile.find(section)
                        if section_elem is not None:
                            for key, value in section_updates.items():
                                section_elem.set(key, str(value))

            # Update territory data
            self.logger.debug("Applying territory changes")
            self.tree = self.territory_manager.save_territory_changes(self.tree)

            # Update achievements
            self.logger.debug("Applying achievement changes")
            self.tree = self.achievements_manager.save_achievement_changes(self.tree)

            # Save the updated XML tree while preserving file size
            self.logger.debug("Saving updated XML tree to file")
            XMLHandler.save_xml_tree(self.tree, self.file_path)
            
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
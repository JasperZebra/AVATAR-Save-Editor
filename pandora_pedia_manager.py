import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
import logging

class PandoraPediaManager:
    def __init__(self, parent: ttk.Frame, main_window):
        self.logger = logging.getLogger('PandoraPediaManager')
        self.logger.debug("Initializing PandoraPediaManager")
        self.parent = parent
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self) -> None:
        # Create PandoraPedia Treeview
        tree_frame = ttk.Frame(self.parent, height=280)
        tree_frame.pack(fill=tk.X, pady=5)
        tree_frame.pack_propagate(False)

        ttk.Label(tree_frame, text="PandoraPedia Articles").pack()

        # Create Treeview with updated columns
        columns = ("Article ID", "Status")
        self.pandora_pedia_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="extended"
        )

        # Configure columns with improved widths
        self.pandora_pedia_tree.heading("Article ID", text="Article ID")
        self.pandora_pedia_tree.heading("Status", text="Status")

        self.pandora_pedia_tree.column("Article ID", width=200, anchor="w")  # Left-align, wider for readability
        self.pandora_pedia_tree.column("Status", width=100, anchor="center")  # Center-align status

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.pandora_pedia_tree.yview)
        self.pandora_pedia_tree.configure(yscrollcommand=scrollbar.set)

        self.pandora_pedia_tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create edit frame
        edit_frame = ttk.LabelFrame(self.parent, text="Article Controls", padding=10)
        edit_frame.pack(fill=tk.X, pady=5)

        # Button frame for controls
        button_frame = ttk.Frame(edit_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            button_frame,
            text="Discover All Articles",
            command=self._unlock_all_articles
        ).pack(side=tk.LEFT, padx=5)

        # Configure tags for color-coding with brighter colors for dark theme
        self.pandora_pedia_tree.tag_configure('not_discovered', foreground='#FF0000')      # Brighter red
        self.pandora_pedia_tree.tag_configure('discovered_not_seen', foreground='#FFA500') # Brighter yellow/gold
        self.pandora_pedia_tree.tag_configure('discovered_has_seen', foreground='#00FF00') # Brighter green

    def load_pandora_pedia(self, tree: ET.ElementTree) -> None:
        self.logger.debug("Loading PandoraPedia")
        try:
            # Clear existing items
            for item in self.pandora_pedia_tree.get_children():
                self.pandora_pedia_tree.delete(item)
            
            # Find all Article elements in XML
            articles = tree.findall(".//AvatarPandorapediaDB_Status/Article")
            self.logger.debug(f"Found {len(articles)} articles")
            
            # Sort articles by CRC ID for consistent display
            articles_sorted = sorted(articles, key=lambda x: x.get("crc_id", "0"))
            
            for article in articles_sorted:
                try:
                    article_id = article.get("crc_id", "")
                    eknown_value = article.get("eKnown", "0")
                    
                    # Map eKnown values to status text
                    status_map = {
                        "0": "Not Discovered",
                        "1": "Discovered | Not Seen",
                        "2": "Discovered | Has Seen"
                    }
                    status = status_map.get(eknown_value, "Not Discovered")
                    
                    # Map status to tag name (use consistent naming scheme)
                    tag_map = {
                        "Not Discovered": "not_discovered",
                        "Discovered | Not Seen": "discovered_not_seen",
                        "Discovered | Has Seen": "discovered_has_seen"
                    }
                    tag = tag_map.get(status, "not_discovered")
                    
                    # Format the article ID for display
                    formatted_id = f"Article {article_id}"
                    
                    # Add to treeview with appropriate tag for color
                    self.pandora_pedia_tree.insert(
                        "", tk.END,
                        values=(formatted_id, status),
                        tags=(tag,)
                    )
                    
                except Exception as e:
                    self.logger.error(f"Error processing article {article_id}: {str(e)}", exc_info=True)

            self.logger.debug("PandoraPedia loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading PandoraPedia: {str(e)}", exc_info=True)
            raise

    def save_pandora_pedia_changes(self, tree: ET.ElementTree) -> ET.ElementTree:
        self.logger.debug("Saving PandoraPedia changes")
        try:
            root = tree.getroot()
            
            # Status map for converting display text back to values
            status_to_value = {
                "Not Discovered": "0",
                "Discovered | Not Seen": "1",
                "Discovered | Has Seen": "2"
            }
            
            for item in self.pandora_pedia_tree.get_children():
                try:
                    values = self.pandora_pedia_tree.item(item)["values"]
                    article_id = values[0].replace("Article ", "")
                    status = values[1]
                    eknown_value = status_to_value.get(status, "0")

                    self.logger.debug(f"Processing article {article_id} with new status: {status}, eKnown={eknown_value}")

                    # Find and update article in XML
                    article = root.find(f".//AvatarPandorapediaDB_Status/Article[@crc_id='{article_id}']")
                    if article is not None:
                        article.set("eKnown", eknown_value)
                        self.logger.debug(f"Successfully updated article {article_id}")
                    else:
                        self.logger.warning(f"Article {article_id} not found in XML")

                except Exception as e:
                    self.logger.error(f"Error processing article update: {str(e)}", exc_info=True)
                    continue

            self.logger.debug("PandoraPedia changes saved successfully")
            return tree
            
        except Exception as e:
            self.logger.error(f"Error saving PandoraPedia changes: {str(e)}", exc_info=True)
            raise

    def _unlock_all_articles(self) -> None:
        self.logger.debug("Unlocking all articles")
        try:
            # Update only undiscovered articles to "Discovered | Not Seen" (eKnown = 1)
            # while preserving articles that are already "Discovered | Has Seen" (eKnown = 2)
            changes_made = False
            
            for item in self.pandora_pedia_tree.get_children():
                try:
                    values = list(self.pandora_pedia_tree.item(item)["values"])
                    current_status = values[1]
                    
                    # Only change status if it's "Not Discovered"
                    # Don't change if already "Discovered | Has Seen"
                    if current_status == "Not Discovered":
                        values[1] = "Discovered | Not Seen"
                        self.pandora_pedia_tree.item(item, values=values, tags=('discovered_not_seen',))
                        self.logger.debug(f"Discovered Article: {values[0]}")
                        changes_made = True
                    
                except Exception as e:
                    self.logger.error(f"Error unlocking individual article: {str(e)}", exc_info=True)
                    continue
            
            if changes_made:
                self.main_window.unsaved_label.config(text="Unsaved Changes")
                self.logger.debug("All undiscovered articles successfully discovered")
                messagebox.showinfo("Success", "All articles discovered!")
            else:
                self.logger.debug("No changes were needed - all articles already discovered")
                messagebox.showinfo("Information", "All articles were already discovered!")
            
        except Exception as e:
            self.logger.error(f"Error in unlock all articles: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to unlock all articles: {str(e)}")

    def _set_selected_status(self, status: str) -> None:
        """Set the status for selected articles"""
        selected_items = self.pandora_pedia_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select at least one article")
            return

        # Map status text to tag name
        tag_map = {
            "Not Discovered": "not_discovered",
            "Discovered | Not Seen": "discovered_not_seen",
            "Discovered | Has Seen": "discovered_has_seen"
        }
        tag = tag_map.get(status, "not_discovered")

        try:
            for item in selected_items:
                values = list(self.pandora_pedia_tree.item(item)["values"])
                values[1] = status
                self.pandora_pedia_tree.item(item, values=values, tags=(tag,))

            self.main_window.unsaved_label.config(text="Unsaved Changes")
            messagebox.showinfo("Success", f"Selected articles set to {status}")

        except Exception as e:
            self.logger.error(f"Error setting article status: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to set article status: {str(e)}")
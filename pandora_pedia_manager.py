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
            text="Unlock All Articles",
            command=self._unlock_all_articles
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Set Selected to Locked",
            command=lambda: self._set_selected_status("Locked")
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Set Selected to In Progress",
            command=lambda: self._set_selected_status("In Progress")
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Set Selected to Unlocked",
            command=lambda: self._set_selected_status("Unlocked")
        ).pack(side=tk.LEFT, padx=5)

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
                        "0": "Locked",
                        "1": "In Progress",
                        "2": "Unlocked"
                    }
                    status = status_map.get(eknown_value, "Locked")
                    
                    # Format the article ID for display
                    formatted_id = f"Article {article_id}"
                    
                    # Add to treeview with appropriate tag for color
                    self.pandora_pedia_tree.insert(
                        "", tk.END,
                        values=(formatted_id, status),
                        tags=(status.lower(),)
                    )
                    
                except Exception as e:
                    self.logger.error(f"Error processing article {article_id}: {str(e)}", exc_info=True)

            # Configure tags for color-coding
            self.pandora_pedia_tree.tag_configure('locked', foreground='#FF0000')      # Bright red
            self.pandora_pedia_tree.tag_configure('in progress', foreground='#FFA500') # Orange
            self.pandora_pedia_tree.tag_configure('unlocked', foreground='#00FF00')    # Bright green

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
                "Locked": "0",
                "In Progress": "1",
                "Unlocked": "2"
            }
            
            for item in self.pandora_pedia_tree.get_children():
                try:
                    values = self.pandora_pedia_tree.item(item)["values"]
                    article_id = values[0].replace("Article ", "")
                    status = values[1]
                    eknown_value = status_to_value.get(status, "0")

                    self.logger.debug(f"Processing article {article_id} with new status: {status}")

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
            # Update all items in the tree to Unlocked
            for item in self.pandora_pedia_tree.get_children():
                try:
                    values = list(self.pandora_pedia_tree.item(item)["values"])
                    values[1] = "Unlocked"
                    self.pandora_pedia_tree.item(item, values=values, tags=('unlocked',))
                    self.logger.debug(f"Unlocked article: {values[0]}")
                except Exception as e:
                    self.logger.error(f"Error unlocking individual article: {str(e)}", exc_info=True)
                    continue
            
            self.main_window.unsaved_label.config(text="Unsaved Changes")
            self.logger.debug("All articles unlocked successfully")
            messagebox.showinfo("Success", "All articles unlocked!")
            
        except Exception as e:
            self.logger.error(f"Error in unlock all articles: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to unlock all articles: {str(e)}")

    def _set_selected_status(self, status: str) -> None:
        """Set the status for selected articles"""
        selected_items = self.pandora_pedia_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select at least one article")
            return

        try:
            for item in selected_items:
                values = list(self.pandora_pedia_tree.item(item)["values"])
                values[1] = status
                self.pandora_pedia_tree.item(item, values=values, tags=(status.lower(),))

            self.main_window.unsaved_label.config(text="Unsaved Changes")
            messagebox.showinfo("Success", f"Selected articles set to {status}")

        except Exception as e:
            self.logger.error(f"Error setting article status: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to set article status: {str(e)}")
import os
import tkinter as tk
from tkinter import ttk
import logging
import sys

class VersionSelector:
    def __init__(self):
        self.logger = logging.getLogger('VersionSelector')
        self.selected_version = None
        self.root = None
        
    def show_selection_screen(self):
        """Show the version selection screen and return the selected version."""
        self.logger.debug("Showing version selection screen")
        
        # Create a new root window
        self.root = tk.Tk()
        self.root.title("Avatar: The Game Save Editor - Select Version")
        self.root.geometry("900x500")
        self.root.resizable(False, False)
        
        # Set up protocol for window close - exit the program
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        # Try to set the window icon
        try:
            icon_path = os.path.join("icon", "avatar_icon.ico")
            self.root.iconbitmap(icon_path)
            self.logger.debug(f"Application icon set successfully from path: {icon_path}")
        except Exception as e:
            self.logger.debug(f"Failed to set application icon: {str(e)}")
        
        # Apply dark theme
        self._setup_dark_theme()
        
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title label
        title_label = ttk.Label(
            main_frame, 
            text="Please Select Your Game Version", 
            font=("", 35, "bold")
        )
        title_label.pack(pady=(0, 50))
        
        # Create frame for the options
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure grid to have three equal columns
        options_frame.columnconfigure(0, weight=1)
        options_frame.columnconfigure(1, weight=1)
        options_frame.columnconfigure(2, weight=1)
        
        # Xbox 360 option
        xbox_frame = self._create_option_frame(
            options_frame, 
            "Xbox 360 Version", 
            "For Xbox 360 save files\n.sav format", 
            lambda: self._on_version_selected("xbox")
        )
        xbox_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # PC option
        pc_frame = self._create_option_frame(
            options_frame, 
            "PC Version", 
            "For PC save files\n.sav format", 
            lambda: self._on_version_selected("pc")
        )
        pc_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # PS3 option
        ps3_frame = self._create_option_frame(
            options_frame, 
            "PS3 Version", 
            "For PS3 save files\nSAVEDATA.000 format", 
            lambda: self._on_version_selected("ps3")
        )
        ps3_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        # Center the window on the screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Wait for selection
        self.root.mainloop()
        
        return self.selected_version
    
    def _on_window_close(self):
        """Handle window close event by exiting the program"""
        self.logger.debug("Version selection window closed without selection - exiting program")
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
        sys.exit(0)  # Exit the program
    
    def _create_option_frame(self, parent, title, description, command):
        """Create a framed option with title, description and text label."""
        # Create frame with raised border and styling
        frame = ttk.Frame(parent, style="Option.TFrame")
        
        # Add padding inside the frame
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title
        title_label = ttk.Label(
            content_frame, 
            text=title, 
            font=("", 14, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Large text label instead of image
        platform_label = ttk.Label(
            content_frame,
            text=title.split()[0],  # "Xbox" or "PC" or "PS3"
            font=("", 36, "bold"),
            justify=tk.CENTER
        )
        platform_label.pack(pady=20)
        
        # Description
        desc_label = ttk.Label(
            content_frame, 
            text=description,
            justify=tk.CENTER,
            font=("", 10, "bold"),
            wraplength=180
        )
        desc_label.pack(pady=10)
        
        # Select button
        select_btn = ttk.Button(
            content_frame,
            text="Select",
            command=command,
            style="Accent.TButton"
        )
        select_btn.pack(pady=(10, 0))
        
        # Make the whole frame clickable
        frame.bind("<Button-1>", lambda e: command())
        for widget in content_frame.winfo_children():
            widget.bind("<Button-1>", lambda e: command())
        
        return frame
    
    def _on_version_selected(self, version):
        """Handle version selection."""
        self.logger.debug(f"Selected version: {version}")
        self.selected_version = version
        
        # Using quit instead of destroy avoids the event conflict
        try:
            self.root.quit()
        except:
            pass
    
    def _setup_dark_theme(self):
        """Apply dark theme styling to the window"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Define colors
        colors = {
            'background': '#1e1e1e',       # Main background color
            'foreground': '#ffffff',       # Primary text color
            'selected': '#1e1e1e',         # Background color for selected items
            'border': '#2a7fff',           # Border color
            'button_bg': '#3c3f41',        # Button background color
            'accent': '#2a7fff',           # Accent color for highlighted elements
        }
        
        # Configure base styles
        style.configure('TFrame', background=colors['background'])
        style.configure('TLabel', background=colors['background'], foreground=colors['foreground'])
        style.configure('TCheckbutton', background=colors['background'], foreground=colors['foreground'])
        
        # Configure button styles
        style.configure('TButton',
            background=colors['button_bg'],
            foreground=colors['foreground'],
            bordercolor=colors['border'],
            focuscolor=colors['accent'],
            lightcolor=colors['button_bg'],
            darkcolor=colors['button_bg']
        )
        
        # Add this - Accent button hover state mapping
        style.map('Accent.TButton',
            background=[('active', '#2a7fff')],  # Lighter blue for hover
            foreground=[('active', colors['foreground'])]
        )

        # Accent button style
        style.configure('Accent.TButton',
            background=colors['background'],
            foreground=colors['foreground'],
            bordercolor=colors['accent'],
            lightcolor=colors['accent'],
            darkcolor=colors['accent']
        )

        # Option frame style (for the version selection boxes)
        style.configure('Option.TFrame',
            background=colors['background'],
            bordercolor=colors['border'],
            relief='solid',
            borderwidth=1
        )
        
        # Make main background color dark
        self.root.configure(bg=colors['background'])
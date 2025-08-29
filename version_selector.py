import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # You'll need to install Pillow: pip install Pillow
import logging
import sys

class VersionSelector:
    def __init__(self):
        self.logger = logging.getLogger('VersionSelector')
        self.selected_version = None
        self.root = None
        self.hover_effects = {}
        self.background_image = None  # Store background image reference
        
    def show_selection_screen(self):
        """Show the modern version selection screen and return the selected version."""
        self.logger.debug("Showing modern version selection screen")
        
        # Create a new root window
        self.root = tk.Tk()
        self.root.title("Avatar: The Game Save Editor | Made by: Jasper_Zebra | Version 2.1")
        self.root.geometry("1400x800")
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
        
        # ADD THESE TWO LINES:
        # Load and set background image
        self._setup_background_image()
        
        # Apply modern dark theme
        # self._setup_modern_theme()
        
        # Create the main interface
        self._create_modern_interface()
        
        # Center the window on the screen
        self._center_window()
        
        # Wait for selection
        self.root.mainloop()
        
        return self.selected_version
    
    def _setup_background_image(self):
        """Load and set up the background image - SIMPLE VERSION"""
        try:
            # Path to your background image
            bg_image_path = os.path.join("Background", "version_selector_background.png")
            
            if os.path.exists(bg_image_path):
                # Load and resize the image to fit the window
                pil_image = Image.open(bg_image_path)
                pil_image = pil_image.resize((1400, 800), Image.Resampling.LANCZOS)
                self.background_image = ImageTk.PhotoImage(pil_image)
                
                # Create a canvas to hold the background image
                self.canvas = tk.Canvas(self.root, width=1400, height=800, highlightthickness=0)
                self.canvas.pack(fill=tk.BOTH, expand=True)
                
                # Add the background image to the canvas
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)
                
                self.logger.debug(f"Background image loaded successfully from: {bg_image_path}")
                return True
            else:
                self.logger.warning(f"Background image not found at: {bg_image_path}")
                # Create canvas with solid background color
                self.canvas = tk.Canvas(self.root, width=1400, height=800, bg='#2c2c2c', highlightthickness=0)
                self.canvas.pack(fill=tk.BOTH, expand=True)
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to load background image: {str(e)}")
            # Create canvas with solid background color
            self.canvas = tk.Canvas(self.root, width=1400, height=800, bg='#2c2c2c', highlightthickness=0)
            self.canvas.pack(fill=tk.BOTH, expand=True)
            return False
            
    def _create_modern_interface(self):
        """Create the modern interface layout - CANVAS VERSION"""
        # Create all widgets directly on the canvas
        self._create_header_section_canvas()
        self._create_content_section_canvas()
        self._create_footer_section_canvas()

    def _create_header_section_canvas(self):
        """Create the header section on canvas"""
        # Main title
        self.canvas.create_text(
            100, 80, 
            text="🎮 Avatar: The Game Save Editor Version 2.1",
            font=('Segoe UI', 28, 'bold'),
            fill='white',
            anchor=tk.NW
        )
        
        # Subtitle
        self.canvas.create_text(
            100, 130,
            text="Select your platform to continue",
            font=('Segoe UI', 14),
            fill='#dddddd',
            anchor=tk.NW
        )
        
        # Version info
        self.canvas.create_text(
            100, 160,
            text="Made by: Jasper_Zebra | Version 2.1",
            font=('Segoe UI', 10),
            fill='#bbbbbb',
            anchor=tk.NW
        )

    def _create_content_section_canvas(self):
        """Create the content section with platform cards on canvas"""
        # Instruction text
        self.canvas.create_text(
            100, 220,
            text="Choose your gaming platform:",
            font=('Segoe UI', 16, 'bold'),
            fill='white',
            anchor=tk.NW
        )
        
        # Platform configurations
        platforms = [
            {
                "id": "xbox",
                "name": "Xbox 360",
                "icon": "🎮",
                "description": "Xbox 360 (Fully Supported)",
                "file_format": ".sav format",
                "x": 200
            },
            {
                "id": "pc", 
                "name": "PC",
                "icon": "💻",
                "description": "PC (Fully Supported)",
                "file_format": ".sav format",
                "x": 500
            },
            {
                "id": "ps3",
                "name": "PlayStation 3",
                "icon": "🎯", 
                "description": "PlayStation 3 (Coming Soon)",
                "file_format": "SAVEDATA.000 format",
                "x": 800
            }
        ]
        
        # Create platform cards
        for platform in platforms:
            self._create_platform_card_canvas(platform)

    def _create_platform_card_canvas(self, platform):
        """Create a platform card on canvas"""
        x = platform["x"]
        y = 280
        width = 250
        height = 350
        
        # Card background rectangle
        card_bg = self.canvas.create_rectangle(
            x, y, x + width, y + height,
            fill='#4B4B4B',
            outline='#404040',
            width=1
        )
        
        # Platform icon
        self.canvas.create_text(
            x + width//2, y + 50,
            text=platform["icon"],
            font=('Segoe UI Emoji', 48),
            fill='white'
        )
        
        # Platform name
        self.canvas.create_text(
            x + width//2, y + 120,
            text=platform["name"],
            font=('Segoe UI', 18, 'bold'),
            fill='white'
        )
        
        # Platform description
        self.canvas.create_text(
            x + width//2, y + 150,
            text=platform["description"],
            font=('Segoe UI', 11),
            fill='#dddddd'
        )
        
        # File format
        self.canvas.create_text(
            x + 20, y + 200,
            text="📄 File Format:",
            font=('Segoe UI', 9, 'bold'),
            fill='#dddddd',
            anchor=tk.NW
        )
        
        self.canvas.create_text(
            x + 20, y + 220,
            text=platform["file_format"],
            font=('Segoe UI', 9),
            fill='#2a7fff',
            anchor=tk.NW
        )
        
        # Select button
        button_bg = self.canvas.create_rectangle(
            x + 20, y + 280, x + width - 20, y + 320,
            fill='#2a7fff',
            outline='#2a7fff',
            width=0
        )
        
        button_text = self.canvas.create_text(
            x + width//2, y + 300,
            text="✨ Select Platform",
            font=('Segoe UI', 10, 'bold'),
            fill='white'
        )
        
        # Make card clickable
        def on_click(event):
            self._on_version_selected(platform["id"])
        
        # Bind click events to card elements
        self.canvas.tag_bind(card_bg, "<Button-1>", on_click)
        self.canvas.tag_bind(button_bg, "<Button-1>", on_click)
        self.canvas.tag_bind(button_text, "<Button-1>", on_click)
        
        # Add hover effects
        def on_enter(event):
            self.canvas.itemconfig(card_bg, outline='#2a7fff', width=2)
            self.canvas.itemconfig(button_bg, fill='#3cc0fd')
        
        def on_leave(event):
            self.canvas.itemconfig(card_bg, outline='#404040', width=1)
            self.canvas.itemconfig(button_bg, fill='#2a7fff')
        
        self.canvas.tag_bind(card_bg, "<Enter>", on_enter)
        self.canvas.tag_bind(card_bg, "<Leave>", on_leave)
        self.canvas.tag_bind(button_bg, "<Enter>", on_enter)
        self.canvas.tag_bind(button_bg, "<Leave>", on_leave)

    def _add_card_hover_effects(self, card_frame, content_frame, platform):
        """Add hover effects to platform cards"""
        def on_enter(event):
            card_frame.configure(style="CardHover.TFrame")
            content_frame.configure(style="CardContentHover.TFrame")
            
        def on_leave(event):
            card_frame.configure(style="Card.TFrame")
            content_frame.configure(style="CardContent.TFrame")
        
        # Bind hover events to card and its children
        widgets_to_bind = [card_frame, content_frame]
        for child in content_frame.winfo_children():
            widgets_to_bind.append(child)
            if hasattr(child, 'winfo_children'):
                widgets_to_bind.extend(child.winfo_children())
        
        for widget in widgets_to_bind:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
    
    def _create_footer_section_canvas(self):
        """Create the footer section on canvas"""
        # Separator line
        self.canvas.create_line(
            100, 680, 1300, 680,
            fill='#404040',
            width=1
        )
        
        # Help text
        self.canvas.create_text(
            100, 710,
            text="💡 Tip: Make sure to backup your save files before editing",
            font=('Segoe UI', 10),
            fill='#bbbbbb',
            anchor=tk.NW
        )
        
        # Support info
        self.canvas.create_text(
            100, 735,
            text="💡 Note: If you travel to a map and it's not night time, load and save your file to reset the time in the game to make it night again.",
            font=('Segoe UI', 10),
            fill='#bbbbbb',
            anchor=tk.NW
        )

    def _center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _on_window_close(self):
        """Handle window close event by exiting the program"""
        self.logger.debug("Version selection window closed without selection - exiting program")
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
        sys.exit(0)
    
    def _on_version_selected(self, version):
        """Handle version selection with smooth transition"""
        self.logger.debug(f"Selected version: {version}")
        self.selected_version = version
        
        # Show selection feedback
        self._show_selection_feedback(version)
        
        # Close window after brief delay
        self.root.after(500, self._close_window)
    
    def _show_selection_feedback(self, version):
        """Show visual feedback for selection"""
        # This could be expanded with animations or visual feedback
        platform_names = {"xbox": "Xbox 360", "pc": "PC", "ps3": "PlayStation 3"}
        self.logger.debug(f"Platform selected: {platform_names.get(version, version)}")
    
    def _close_window(self):
        """Close the selection window"""
        try:
            self.root.quit()
        except:
            pass
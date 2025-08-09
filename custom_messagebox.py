import tkinter as tk
from tkinter import ttk
import os
import threading
from typing import Optional, Dict, Any, Callable

class CustomMessageBox:
    """Modern, customizable messagebox replacement"""
    
    # Class variables for consistent styling
    COLORS = {
        'info': {'bg': '#1e1e1e', 'icon': '🛈', 'accent': '#0078d4', 'border': '#0078d4'},
        'success': {'bg': '#1e1e1e', 'icon': '✅', 'accent': '#107c10', 'border': '#107c10'},
        'warning': {'bg': '#1e1e1e', 'icon': '⚠️', 'accent': '#ff8c00', 'border': '#ff8c00'},
        'error': {'bg': '#1e1e1e', 'icon': '❌', 'accent': '#d13438', 'border': '#d13438'},
        'question': {'bg': '#1e1e1e', 'icon': '❓', 'accent': '#5c5c5c', 'border': '#2a7fff'}
    }
    
    def __init__(self, parent=None, title="Message", message="", msg_type="info", 
                 buttons=None, default_button=0, icon_path=None, width=600, height=None):
        """
        Initialize custom messagebox
        
        Args:
            parent: Parent window
            title: Window title
            message: Message text
            msg_type: Type of message ('info', 'success', 'warning', 'error', 'question')
            buttons: List of button texts (default: ['OK'])
            default_button: Index of default button
            icon_path: Path to window icon
            width: Window width
            height: Window height (auto-calculated if None)
        """
        self.parent = parent
        self.title = title
        self.message = message
        self.msg_type = msg_type
        self.buttons = buttons if buttons else ['OK']
        self.default_button = default_button
        self.icon_path = icon_path
        self.width = width
        self.height = height
        self.result = None
        self.window = None
        
        # Get color scheme for message type
        self.colors = self.COLORS.get(msg_type, self.COLORS['info'])
        
    def show(self) -> str:
        """Show the messagebox and return the button clicked"""
        self._create_window()
        self._setup_ui()
        self._center_window()
        
        # Make window modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Focus on default button
        if hasattr(self, 'button_widgets') and self.button_widgets:
            self.button_widgets[self.default_button].focus_set()
        
        # Wait for window to close
        self.window.wait_window()
        
        return self.result
    
    def _create_window(self):
        """Create the main window"""
        if self.parent:
            self.window = tk.Toplevel(self.parent)
        else:
            self.window = tk.Tk()
            
        self.window.title(self.title)
        self.window.resizable(False, False)
        
        # Set dark theme background
        self.window.configure(bg='#1e1e1e')
        
        # Set icon if provided
        if self.icon_path and os.path.exists(self.icon_path):
            try:
                self.window.iconbitmap(self.icon_path)
            except:
                pass
        elif hasattr(self.parent, 'winfo_toplevel'):
            # Try to inherit parent's icon
            try:
                parent_icon = self.parent.winfo_toplevel().iconbitmap()
                if parent_icon:
                    self.window.iconbitmap(parent_icon)
            except:
                pass
        
        # Try to inherit icon from main application
        if not self.icon_path:
            try:
                icon_path = os.path.join("icon", "avatar_icon.ico")
                if os.path.exists(icon_path):
                    self.window.iconbitmap(icon_path)
            except:
                pass
        
        # Bind escape key to close
        self.window.bind('<Escape>', lambda e: self._button_clicked(self.buttons[-1]))
        self.window.bind('<Return>', lambda e: self._button_clicked(self.buttons[self.default_button]))
        
    def _setup_ui(self):
        """Setup the user interface"""
        # Main container - use tk.Frame with dark background
        main_frame = tk.Frame(self.window, bg='#1e1e1e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Outer border frame with accent color
        border_frame = tk.Frame(main_frame, bg=self.colors['border'], bd=2, relief='solid')
        border_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Content frame with background color (inside the border)
        content_frame = tk.Frame(border_frame, bg=self.colors['bg'], bd=0)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Icon and message area
        message_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        message_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Icon
        icon_label = tk.Label(message_frame, 
                             text=self.colors['icon'], 
                             font=('Segoe UI', 24),
                             bg=self.colors['bg'],
                             fg=self.colors['accent'])
        icon_label.pack(side=tk.LEFT, padx=(0, 15), anchor=tk.N)
        
        # Message text area
        text_frame = tk.Frame(message_frame, bg=self.colors['bg'])
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Title (if different from window title)
        title_label = tk.Label(text_frame,
                              text=self.title,
                              font=('Segoe UI', 12, 'bold'),
                              bg=self.colors['bg'],
                              fg="#FFFFFF",
                              anchor=tk.W,
                              justify=tk.LEFT)
        title_label.pack(fill=tk.X, pady=(0, 8))
        
        # Message text
        message_label = tk.Label(text_frame,
                               text=self.message,
                               font=('Segoe UI', 10),
                               bg=self.colors['bg'],
                               fg="#FFFFFF",
                               anchor=tk.W,
                               justify=tk.LEFT,
                               wraplength=self.width - 120)
        message_label.pack(fill=tk.BOTH, expand=True)
        
        # Button frame - use tk.Frame with dark background
        button_frame = tk.Frame(main_frame, bg='#1e1e1e')
        button_frame.pack(fill=tk.X)
        
        # Create buttons - use tk.Button with enhanced styling and hover effects
        self.button_widgets = []
        for i, button_text in enumerate(self.buttons):
            is_default = i == self.default_button
            colors = self._get_button_colors(button_text, is_default)
            
            # Add special styling for destructive actions
            is_destructive = button_text in ['Delete', 'Remove', 'Uninstall', 'Reset']
            if is_destructive and not is_default:
                colors['bg'] = '#d13438'  # Red for destructive actions
                colors['hover_bg'] = '#b82e32'
                colors['active_bg'] = '#a1292c'
            
            btn = tk.Button(button_frame,
                           text=button_text,
                           command=lambda text=button_text: self._button_clicked(text),
                           font=('Segoe UI', 9, 'bold' if is_default else 'normal'),
                           bg=colors['bg'],
                           fg='white',
                           activebackground=colors['active_bg'],
                           activeforeground='white',
                           relief='flat',
                           borderwidth=0,
                           highlightthickness=0,
                           width=10,
                           pady=8,
                           cursor='hand2')
            
            # Add enhanced hover effects with smooth transitions
            def on_enter(event, button=btn, hover_color=colors['hover_bg']):
                button.configure(bg=hover_color)
                # Add subtle border effect on hover
                button.configure(relief='solid', borderwidth=1, 
                               highlightbackground=self.colors['border'])
            
            def on_leave(event, button=btn, normal_color=colors['bg']):
                button.configure(bg=normal_color)
                # Remove border effect
                button.configure(relief='flat', borderwidth=0, 
                               highlightthickness=0)
            
            # Add pressed effect
            def on_press(event, button=btn, press_color=colors['active_bg']):
                button.configure(bg=press_color)
            
            def on_release(event, button=btn, hover_color=colors['hover_bg']):
                button.configure(bg=hover_color)
            
            # Bind all button events
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            btn.bind("<Button-1>", on_press)
            btn.bind("<ButtonRelease-1>", on_release)
            
            btn.pack(side=tk.RIGHT, padx=(8, 0), pady=2)
            self.button_widgets.append(btn)
        
        # Reverse button order so default is on the right
        self.button_widgets.reverse()
        
        # Calculate window height if not specified
        if not self.height:
            self.window.update_idletasks()
            self.height = self.window.winfo_reqheight()
        
        self.window.geometry(f"{self.width}x{self.height}")
    
    def _lighten_color(self, hex_color, factor=0.2):
        """Lighten a hex color by a given factor (0.0 to 1.0)"""
        try:
            # Remove the '#' if present
            hex_color = hex_color.lstrip('#')
            
            # Convert hex to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Lighten by moving towards white
            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))
            
            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            # Fallback to a generic lighter color
            return "#404040"
    
    def _darken_color(self, hex_color, factor=0.1):
        """Darken a hex color by a given factor (0.0 to 1.0)"""
        try:
            # Remove the '#' if present
            hex_color = hex_color.lstrip('#')
            
            # Convert hex to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Darken by moving towards black
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))
            
            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            # Fallback to a generic darker color
            return "#1e1e1e"
    
    def _get_button_colors(self, button_text, is_default):
        """Get button colors for tk.Button styling"""
        if is_default:
            return {
                'bg': self.colors['accent'],
                'hover_bg': self._lighten_color(self.colors['accent'], 0.2),
                'active_bg': self._darken_color(self.colors['accent'], 0.1)
            }
        else:
            return {
                'bg': '#252525',
                'hover_bg': '#404040', 
                'active_bg': '#1e1e1e'
            }
    
    def _get_button_style(self, button_text, is_default):
        """Get the appropriate button style based on message type and button role"""
        # Primary action buttons (default buttons)
        if is_default:
            style_map = {
                'info': ('Info.TButton', self.colors['accent']),
                'success': ('Success.TButton', self.colors['accent']),
                'warning': ('Warning.TButton', self.colors['accent']),
                'error': ('Error.TButton', self.colors['accent']),
                'question': ('Question.TButton', self.colors['accent'])
            }
            return style_map.get(self.msg_type, ('Default.TButton', '#0078d4'))
        
        # Secondary action buttons
        secondary_buttons = ['Cancel', 'No', 'Close']
        if button_text in secondary_buttons:
            return ('Secondary.TButton', '#252525')
        
        # Default for other buttons
        return ('Secondary.TButton', '#252525')
    
    def _center_window(self):
        """Center the window on screen or parent"""
        self.window.update_idletasks()
        
        if self.parent and self.parent.winfo_exists():
            # Center on parent window
            parent_x = self.parent.winfo_rootx()
            parent_y = self.parent.winfo_rooty()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            x = parent_x + (parent_width - self.width) // 2
            y = parent_y + (parent_height - self.height) // 2
        else:
            # Center on screen
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            
            x = (screen_width - self.width) // 2
            y = (screen_height - self.height) // 2
        
        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")
    
    def _get_button_style(self, button_text, is_default):
        """Get the appropriate button style based on message type and button role"""
        # Primary action buttons (default buttons)
        if is_default:
            style_map = {
                'info': ('Info.TButton', self.colors['accent']),
                'success': ('Success.TButton', self.colors['accent']),
                'warning': ('Warning.TButton', self.colors['accent']),
                'error': ('Error.TButton', self.colors['accent']),
                'question': ('Question.TButton', self.colors['accent'])
            }
            return style_map.get(self.msg_type, ('Default.TButton', '#0078d4'))
        
        # Secondary action buttons
        secondary_buttons = ['Cancel', 'No', 'Close']
        if button_text in secondary_buttons:
            return ('Secondary.TButton', '#252525')
        
        # Default for other buttons
        return ('Secondary.TButton', '#252525')
    
    def _get_button_colors(self, button_text, is_default):
        """Get button colors for tk.Button styling"""
        if is_default:
            return {
                'bg': self.colors['accent'],
                'hover_bg': self._lighten_color(self.colors['accent'], 0.2),
                'active_bg': self._darken_color(self.colors['accent'], 0.1)
            }
        else:
            return {
                'bg': '#252525',
                'hover_bg': '#404040', 
                'active_bg': '#1e1e1e'
            }
    
    def _darken_color(self, hex_color, factor=0.1):
        """Darken a hex color by a given factor (0.0 to 1.0)"""
        try:
            # Remove the '#' if present
            hex_color = hex_color.lstrip('#')
            
            # Convert hex to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Darken by moving towards black
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))
            
            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            # Fallback to a generic darker color
            return "#1e1e1e"
        """Lighten a hex color by a given factor (0.0 to 1.0)"""
        try:
            # Remove the '#' if present
            hex_color = hex_color.lstrip('#')
            
            # Convert hex to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Lighten by moving towards white
            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))
            
            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            # Fallback to a generic lighter color
            return "#404040"
    
    def _button_clicked(self, button_text):
        """Handle button click"""
        self.result = button_text
        self.window.destroy()

class MessageBoxManager:
    """Centralized messagebox manager for consistent styling"""
    
    def __init__(self, default_parent=None, icon_path=None):
        """
        Initialize messagebox manager
        
        Args:
            default_parent: Default parent window for all messageboxes
            icon_path: Default icon path for all messageboxes
        """
        self.default_parent = default_parent
        self.icon_path = icon_path
        
        # Configure default button styles
        self._setup_button_styles()
    
    def _setup_button_styles(self):
        """Setup button styles for messageboxes"""
        style = ttk.Style()
        
        # Default button style (for primary actions)
        style.configure("Default.TButton",
                       padding=(12, 6),
                       font=('Segoe UI', 9, 'bold'))
        
        # Info button style
        style.configure("Info.TButton",
                       padding=(12, 6),
                       font=('Segoe UI', 9, 'bold'),
                       background='#0078d4',
                       foreground='white')
        
        # Success button style
        style.configure("Success.TButton",
                       padding=(12, 6),
                       font=('Segoe UI', 9, 'bold'),
                       background='#107c10',
                       foreground='white')
        
        # Warning button style
        style.configure("Warning.TButton",
                       padding=(12, 6),
                       font=('Segoe UI', 9, 'bold'),
                       background='#ff8c00',
                       foreground='white')
        
        # Error button style
        style.configure("Error.TButton",
                       padding=(12, 6),
                       font=('Segoe UI', 9, 'bold'),
                       background='#d13438',
                       foreground='white')
        
        # Question button style
        style.configure("Question.TButton",
                       padding=(12, 6),
                       font=('Segoe UI', 9, 'bold'),
                       background='#2a7fff',
                       foreground='white')
        
        # Secondary button style (for Cancel, No, etc.)
        style.configure("Secondary.TButton",
                       padding=(12, 6),
                       font=('Segoe UI', 9),
                       background='#252525',
                       foreground='white')
        
        # Configure button hover/press states based on theme
        try:
            # Default button hover states
            style.map("Default.TButton",
                     background=[('active', '#0078d4'),
                               ('pressed', '#106ebe')])
            
            # Info button hover states
            style.map("Info.TButton",
                     background=[('active', '#106ebe'),
                               ('pressed', '#005a9e')])
            
            # Success button hover states  
            style.map("Success.TButton",
                     background=[('active', '#0e6b0e'),
                               ('pressed', '#0d5f0d')])
            
            # Warning button hover states
            style.map("Warning.TButton",
                     background=[('active', '#e67e00'),
                               ('pressed', '#cc7000')])
            
            # Error button hover states
            style.map("Error.TButton",
                     background=[('active', '#b82e32'),
                               ('pressed', '#a1292c')])
            
            # Question button hover states
            style.map("Question.TButton",
                     background=[('active', '#1a6fff'),
                               ('pressed', '#0d5fd9')])
            
            # Secondary button hover states
            style.map("Secondary.TButton",
                     background=[('active', '#404040'),
                               ('pressed', '#1e1e1e')])
        except:
            pass
    
    def show_info(self, title: str, message: str, parent=None) -> str:
        """Show info messagebox"""
        return CustomMessageBox(
            parent=parent or self.default_parent,
            title=title,
            message=message,
            msg_type="info",
            buttons=['OK'],
            icon_path=self.icon_path
        ).show()
    
    def show_success(self, title: str, message: str, parent=None) -> str:
        """Show success messagebox"""
        return CustomMessageBox(
            parent=parent or self.default_parent,
            title=title,
            message=message,
            msg_type="success",
            buttons=['OK'],
            icon_path=self.icon_path
        ).show()
    
    def show_warning(self, title: str, message: str, parent=None) -> str:
        """Show warning messagebox"""
        return CustomMessageBox(
            parent=parent or self.default_parent,
            title=title,
            message=message,
            msg_type="warning",
            buttons=['OK'],
            icon_path=self.icon_path
        ).show()
    
    def show_error(self, title: str, message: str, parent=None) -> str:
        """Show error messagebox"""
        return CustomMessageBox(
            parent=parent or self.default_parent,
            title=title,
            message=message,
            msg_type="error",
            buttons=['OK'],
            icon_path=self.icon_path
        ).show()
    
    def ask_question(self, title: str, message: str, parent=None) -> bool:
        """Show yes/no question messagebox"""
        result = CustomMessageBox(
            parent=parent or self.default_parent,
            title=title,
            message=message,
            msg_type="question",
            buttons=['Yes', 'No'],
            default_button=0,
            icon_path=self.icon_path
        ).show()
        return result == 'Yes'
    
    def ask_ok_cancel(self, title: str, message: str, parent=None) -> bool:
        """Show OK/Cancel messagebox"""
        result = CustomMessageBox(
            parent=parent or self.default_parent,
            title=title,
            message=message,
            msg_type="question",
            buttons=['OK', 'Cancel'],
            default_button=0,
            icon_path=self.icon_path
        ).show()
        return result == 'OK'
    
    def ask_yes_no_cancel(self, title: str, message: str, parent=None) -> str:
        """Show Yes/No/Cancel messagebox"""
        return CustomMessageBox(
            parent=parent or self.default_parent,
            title=title,
            message=message,
            msg_type="question",
            buttons=['Yes', 'No', 'Cancel'],
            default_button=0,
            icon_path=self.icon_path
        ).show()
    
    def show_custom(self, title: str, message: str, msg_type: str = "info", 
                   buttons: list = None, default_button: int = 0, parent=None) -> str:
        """Show custom messagebox with specified parameters"""
        return CustomMessageBox(
            parent=parent or self.default_parent,
            title=title,
            message=message,
            msg_type=msg_type,
            buttons=buttons or ['OK'],
            default_button=default_button,
            icon_path=self.icon_path
        ).show()

# Convenience functions for easy replacement of standard messagebox
def show_info(title: str, message: str, parent=None) -> str:
    """Convenience function for info messagebox"""
    icon_path = os.path.join("icon", "avatar_icon.ico") if os.path.exists(os.path.join("icon", "avatar_icon.ico")) else None
    return CustomMessageBox(parent=parent, title=title, message=message, msg_type="info", icon_path=icon_path).show()

def show_success(title: str, message: str, parent=None) -> str:
    """Convenience function for success messagebox"""
    icon_path = os.path.join("icon", "avatar_icon.ico") if os.path.exists(os.path.join("icon", "avatar_icon.ico")) else None
    return CustomMessageBox(parent=parent, title=title, message=message, msg_type="success", icon_path=icon_path).show()

def show_warning(title: str, message: str, parent=None) -> str:
    """Convenience function for warning messagebox"""
    icon_path = os.path.join("icon", "avatar_icon.ico") if os.path.exists(os.path.join("icon", "avatar_icon.ico")) else None
    return CustomMessageBox(parent=parent, title=title, message=message, msg_type="warning", icon_path=icon_path).show()

def show_error(title: str, message: str, parent=None) -> str:
    """Convenience function for error messagebox"""
    icon_path = os.path.join("icon", "avatar_icon.ico") if os.path.exists(os.path.join("icon", "avatar_icon.ico")) else None
    return CustomMessageBox(parent=parent, title=title, message=message, msg_type="error", icon_path=icon_path).show()

def ask_question(title: str, message: str, parent=None) -> bool:
    """Convenience function for yes/no question"""
    icon_path = os.path.join("icon", "avatar_icon.ico") if os.path.exists(os.path.join("icon", "avatar_icon.ico")) else None
    result = CustomMessageBox(parent=parent, title=title, message=message, 
                            msg_type="question", buttons=['Yes', 'No'], icon_path=icon_path).show()
    return result == 'Yes'

def ask_ok_cancel(title: str, message: str, parent=None) -> bool:
    """Convenience function for OK/Cancel question"""
    icon_path = os.path.join("icon", "avatar_icon.ico") if os.path.exists(os.path.join("icon", "avatar_icon.ico")) else None
    result = CustomMessageBox(parent=parent, title=title, message=message, 
                            msg_type="question", buttons=['OK', 'Cancel'], icon_path=icon_path).show()
    return result == 'OK'
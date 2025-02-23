import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, Any
import logging


class EnhancedTooltip:
    def __init__(self, widget: tk.Widget, text: str):
        self.logger = logging.getLogger('EnhancedTooltip')
        self.widget = widget
        self.text = text
        self.tooltip_window: Optional[tk.Toplevel] = None
        self.scheduled_hide: Optional[str] = None
        
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", lambda e: self.schedule_hide())
        
    def schedule_hide(self) -> None:
        self.logger.debug("Scheduling tooltip hide")
        if self.scheduled_hide:
            self.widget.after_cancel(self.scheduled_hide)
        self.scheduled_hide = self.widget.after(500, self.hide_tooltip)
        
    def show_tooltip(self, event=None) -> None:
        self.logger.debug("Showing tooltip")
        try:
            if self.scheduled_hide:
                self.widget.after_cancel(self.scheduled_hide)
                self.scheduled_hide = None
                
            if self.tooltip_window:
                return
                
            x = self.widget.winfo_rootx() + self.widget.winfo_width() + 5
            y = self.widget.winfo_rooty() + self.widget.winfo_height() // 2
            
            self.tooltip_window = tk.Toplevel(self.widget)
            self.tooltip_window.wm_overrideredirect(True)
            
            frame = ttk.Frame(self.tooltip_window, relief="solid", borderwidth=1)
            frame.pack(fill="both", expand=True)
            
            label = ttk.Label(
                frame,
                text=self.text,
                justify=tk.LEFT,
                wraplength=250,
                style="Tooltip.TLabel"
            )
            label.pack(padx=5, pady=3)
            
            self.tooltip_window.update_idletasks()
            
            # Adjust position if tooltip would go off screen
            screen_width = self.widget.winfo_screenwidth()
            screen_height = self.widget.winfo_screenheight()
            tooltip_width = self.tooltip_window.winfo_width()
            tooltip_height = self.tooltip_window.winfo_height()
            
            if x + tooltip_width > screen_width:
                x = self.widget.winfo_rootx() - tooltip_width - 5
            
            if y + tooltip_height > screen_height:
                y = screen_height - tooltip_height - 5
            
            self.tooltip_window.wm_geometry(f"+{x}+{y}")
            
            self.tooltip_window.bind("<Enter>", lambda e: self.cancel_hide())
            self.tooltip_window.bind("<Leave>", lambda e: self.schedule_hide())
            
        except Exception as e:
            self.logger.error(f"Error showing tooltip: {str(e)}", exc_info=True)
        
    def hide_tooltip(self, event=None) -> None:
        self.logger.debug("Hiding tooltip")
        try:
            if self.tooltip_window:
                self.tooltip_window.destroy()
                self.tooltip_window = None
            if self.scheduled_hide:
                self.widget.after_cancel(self.scheduled_hide)
                self.scheduled_hide = None
        except Exception as e:
            self.logger.error(f"Error hiding tooltip: {str(e)}", exc_info=True)
            
    def cancel_hide(self) -> None:
        self.logger.debug("Cancelling tooltip hide")
        if self.scheduled_hide:
            self.widget.after_cancel(self.scheduled_hide)
            self.scheduled_hide = None

class ScrollableFrame:
    def __init__(self, container: tk.Widget):
        self.logger = logging.getLogger('ScrollableFrame')
        self.logger.debug("Initializing ScrollableFrame")
        try:
            self.canvas = tk.Canvas(container)
            self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
            self.horizontal_scrollbar = ttk.Scrollbar(container, orient="horizontal", command=self.canvas.xview)
            self.scrollable_frame = ttk.Frame(self.canvas)

            self.scrollable_frame.bind(
                "<Configure>",
                lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            )

            self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            self.canvas.configure(yscrollcommand=self.scrollbar.set, xscrollcommand=self.horizontal_scrollbar.set)
            
            # Add mouse wheel scrolling
            self._add_mousewheel_bindings()
            
            self.logger.debug("ScrollableFrame initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing ScrollableFrame: {str(e)}", exc_info=True)
            raise

    def _add_mousewheel_bindings(self):
        """Add mouse wheel scrolling support."""
        def _on_mousewheel(event):
            """Handle vertical mouse wheel scrolling."""
            # Adjust scroll amount for smoother scrolling
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_shift_mousewheel(event):
            """Handle horizontal mouse wheel scrolling when Shift is pressed."""
            # Adjust scroll amount for smoother scrolling
            self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_enter(event):
            """Bind mousewheel when mouse enters the canvas."""
            # Different platforms require different event bindings
            if event.widget.winfo_toplevel().tk.call('tk', 'windowingsystem') == 'x11':
                # Linux
                self.canvas.bind_all("<Button-4>", _on_mousewheel)
                self.canvas.bind_all("<Button-5>", _on_mousewheel)
                self.canvas.bind_all("<Shift-Button-4>", _on_shift_mousewheel)
                self.canvas.bind_all("<Shift-Button-5>", _on_shift_mousewheel)
            else:
                # Windows and macOS
                self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
                self.canvas.bind_all("<Shift-MouseWheel>", _on_shift_mousewheel)

        def _on_leave(event):
            """Unbind mousewheel when mouse leaves the canvas."""
            if event.widget.winfo_toplevel().tk.call('tk', 'windowingsystem') == 'x11':
                # Linux
                self.canvas.unbind_all("<Button-4>")
                self.canvas.unbind_all("<Button-5>")
                self.canvas.unbind_all("<Shift-Button-4>")
                self.canvas.unbind_all("<Shift-Button-5>")
            else:
                # Windows and macOS
                self.canvas.unbind_all("<MouseWheel>")
                self.canvas.unbind_all("<Shift-MouseWheel>")

        # Bind enter and leave events to handle mousewheel scrolling
        self.canvas.bind("<Enter>", _on_enter)
        self.canvas.bind("<Leave>", _on_leave)

    def pack(self, **kwargs):
        self.logger.debug("Packing ScrollableFrame")
        try:
            self.scrollbar.pack(side="right", fill="y")
            self.horizontal_scrollbar.pack(side="bottom", fill="x")
            self.canvas.pack(side="left", fill="both", expand=True)
        except Exception as e:
            self.logger.error(f"Error packing ScrollableFrame: {str(e)}", exc_info=True)

class LabeledInput:
    def __init__(self, parent: tk.Widget, label_text: str, input_type: str = "entry", 
                values: Dict[Any, str] = None, tooltip: str = None, width: int = 12, state: str = 'normal'):
        self.logger = logging.getLogger('LabeledInput')
        self.logger.debug(f"Initializing LabeledInput for {label_text}")
        try:
            self.frame = ttk.Frame(parent)
            
            self.label = ttk.Label(self.frame, text=f"{label_text}:")
            self.label.grid(row=0, column=0, sticky="e", padx=(0, 5), pady=2)
                        
            if input_type == "combobox" and values:
                # For comboboxes, use 'disabled' when readonly
                combobox_state = "disabled" if state == "disabled" else "readonly"
                self.input = ttk.Combobox(
                    self.frame,
                    values=list(values.values()) if values else [],
                    state=combobox_state,
                    width=12  # Add width parameter here
                )
                # Prevent mousewheel from changing combobox values
                def block_mousewheel(event):
                    return "break"
                
                self.input.bind("<MouseWheel>", block_mousewheel)  # Windows
                self.input.bind("<Button-4>", block_mousewheel)    # Linux scroll up
                self.input.bind("<Button-5>", block_mousewheel)    # Linux scroll down
                self.input.bind("<Command-MouseWheel>", block_mousewheel)  # macOS
                self.logger.debug(f"Created combobox with values and blocked mousewheel: {values}")
            else:
                # For entries, use the provided state
                self.input = ttk.Entry(self.frame, width=12, state=state)  # Also add width to Entry
                self.logger.debug(f"Created entry widget with state: {state}")
                
            self.input.grid(row=0, column=1, sticky="w", padx=5, pady=2)
            
            if tooltip:
                EnhancedTooltip(self.label, tooltip)
                EnhancedTooltip(self.input, tooltip)
                self.logger.debug(f"Added tooltip: {tooltip}")
                
        except Exception as e:
            self.logger.error(f"Error initializing LabeledInput: {str(e)}", exc_info=True)
            raise
            
    def pack(self, **kwargs):
        self.logger.debug("Packing LabeledInput")
        try:
            self.frame.pack(**kwargs)
        except Exception as e:
            self.logger.error(f"Error packing LabeledInput: {str(e)}", exc_info=True)
        
    def grid(self, **kwargs):
        self.logger.debug("Adding LabeledInput to grid")
        try:
            self.frame.grid(**kwargs)
        except Exception as e:
            self.logger.error(f"Error adding LabeledInput to grid: {str(e)}", exc_info=True)
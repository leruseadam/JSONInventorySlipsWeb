import tkinter as tk
from tkinter import ttk
import sys

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            self.tooltip, 
            text=self.text, 
            justify='left',
            background="#ffffe0", 
            relief="solid", 
            borderwidth=1,
            font=("Arial", 10, "normal")
        )
        label.pack(padx=3, pady=3)
    
    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class BaseUI:
    def __init__(self, root, colors):
        self.root = root
        self.colors = colors
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._configure_styles()
    
    def _configure_styles(self):
        """Configure ttk styles"""
        self.style.configure("TButton", 
                           background=self.colors.get("button_bg"),
                           foreground=self.colors.get("button_fg"),
                           font=("Arial", 11))
        
        self.style.configure("TCheckbutton",
                           background=self.colors.get("bg_main"),
                           foreground=self.colors.get("fg_main"),
                           font=("Arial", 11))
        
        self.style.configure("TLabel",
                           background=self.colors.get("bg_main"),
                           foreground=self.colors.get("fg_main"),
                           font=("Arial", 11))
        
        self.style.configure("TFrame",
                           background=self.colors.get("bg_main"))
    
    def create_context_menu(self, widget):
        """Create a context menu for a widget"""
        context_menu = tk.Menu(widget, tearoff=0, 
                             bg=self.colors.get("bg_secondary"), 
                             fg=self.colors.get("fg_main"))
        
        context_menu.add_command(label="Cut", 
                               command=lambda: widget.event_generate('<<Cut>>'))
        context_menu.add_command(label="Copy", 
                               command=lambda: widget.event_generate('<<Copy>>'))
        context_menu.add_command(label="Paste", 
                               command=lambda: widget.event_generate('<<Paste>>'))
        context_menu.add_separator()
        context_menu.add_command(label="Select All", 
                               command=lambda: widget.event_generate('<<SelectAll>>'))
        
        if isinstance(widget, tk.Text):
            context_menu.add_separator()
            context_menu.add_command(label="Format JSON", 
                                   command=lambda: self.format_json_text(widget))
        
        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        widget.bind("<Button-3>", show_context_menu)  # Right-click on Windows/Linux
        if sys.platform == 'darwin':
            widget.bind("<Button-2>", show_context_menu)  # Right-click on macOS
    
    def format_json_text(self, text_widget):
        """Format the JSON in a text widget for better readability"""
        try:
            content = text_widget.get(1.0, tk.END)
            if not content.strip():
                return
            
            from utils.helpers import format_json_text
            formatted = format_json_text(content)
            
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, formatted)
            
        except Exception as e:
            print(f"Error formatting JSON: {e}")
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        return ToolTip(widget, text) 
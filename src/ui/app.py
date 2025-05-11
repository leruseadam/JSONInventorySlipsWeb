import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
import os
import sys
import json
import datetime
import urllib.request
import pandas as pd
from io import BytesIO
from docxtpl import DocxTemplate
from docx import Document
from docx.shared import Pt
from docxcompose.composer import Composer
import threading
import configparser
import webbrowser
import re

from ..base.base_ui import BaseUI
from ..config.settings import load_config, save_config, resource_path, APP_VERSION
from ..themes.theme_manager import ThemeColors
from ..data.processor import parse_inventory_json, process_csv_data
from ..utils.helpers import run_full_process_inventory_slips, open_file

class InventorySlipGenerator(BaseUI):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.config = load_config()
        self.theme_name = self.config['SETTINGS'].get('theme', 'dark')
        self.colors = ThemeColors(self.theme_name)
        
        super().__init__(root, self.colors)
        
        self.df = pd.DataFrame()  # Initialize empty DataFrame
        
        self.init_ui()
        self.recent_files = self.config['PATHS'].get('recent_files', '').split('|')
        self.recent_urls = self.config['PATHS'].get('recent_urls', '').split('|')
        self.recent_files = [f for f in self.recent_files if f and os.path.exists(f)]
        self.recent_urls = [u for u in self.recent_urls if u]
        
        self.update_recent_menu()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Set icon if available
        try:
            if sys.platform == "win32":
                self.root.iconbitmap(resource_path("assets/icon.ico"))
        except:
            pass
    
    def init_ui(self):
        # Configure root window
        self.root.title("Inventory Slip Generator v" + APP_VERSION)
        self.root.configure(bg=self.colors.get("bg_main"))
        
        # Set default size
        width = 850
        height = 750
        self.root.geometry(f"{width}x{height}")
        
        # Create menu
        self.create_menu()
        
        # Main frame
        self.main_frame = ttk.Frame(self.root, style="TFrame", padding=(20, 10))
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title and Header
        title_frame = ttk.Frame(self.main_frame, style="TFrame")
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.title_label = ttk.Label(
            title_frame, 
            text="Inventory Slip Generator",
            font=("Arial", 18, "bold"),
            style="TLabel"
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Settings button
        self.settings_btn = ttk.Button(
            title_frame,
            text="⚙️ Settings",
            command=self.show_settings,
            style="TButton"
        )
        self.settings_btn.pack(side=tk.RIGHT)
        
        # Create notebook/tabbed interface
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_data_tab()
        self.create_preview_tab()
        
        # Status frame
        self.status_frame = ttk.Frame(self.root, style="TFrame")
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            self.status_frame,
            textvariable=self.status_var,
            style="TLabel",
            padding=(10, 5)
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Progress bar
        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self.status_frame,
            variable=self.progress_var,
            mode='determinate',
            length=200
        )
        self.progress_bar.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def create_menu(self):
        # Use bright colors for the menu
        bright_bg = "#f9f9f9"   # Very light background
        bright_fg = "#222222"   # Dark text for contrast

        # Main menu bar
        self.menu_bar = tk.Menu(self.root, bg=bright_bg, fg=bright_fg)
        self.root.config(menu=self.menu_bar)
        
        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0, bg=bright_bg, fg=bright_fg)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open CSV File...", command=self.load_csv)
        self.file_menu.add_command(label="Load from URL...", command=self.show_url_dialog)
        self.file_menu.add_command(label="Paste JSON Data...", command=self.show_json_paste_dialog)

        # Recent files submenu
        self.recent_menu = tk.Menu(self.file_menu, tearoff=0, bg=self.colors.get("bg_secondary"), fg=self.colors.get("fg_main"))
        self.file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)

        self.file_menu.add_separator()
        self.file_menu.add_command(label="Generate Slips", command=self.on_generate)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="API Settings...", command=self.show_api_settings)
        self.file_menu.add_command(label="Exit", command=self.on_close)
        
        # Edit menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0, bg=self.colors.get("bg_secondary"), fg=self.colors.get("fg_main"))
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Select All", command=lambda: self.select_all_var.set(True) or self.toggle_all())
        self.edit_menu.add_command(label="Deselect All", command=lambda: self.select_all_var.set(False) or self.toggle_all())
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Find...", command=self.show_find_dialog)
        
        # View menu
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0, bg=self.colors.get("bg_secondary"), fg=self.colors.get("fg_main"))
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        
        # Theme submenu
        self.theme_menu = tk.Menu(self.view_menu, tearoff=0, bg=self.colors.get("bg_secondary"), fg=self.colors.get("fg_main"))
        self.view_menu.add_cascade(label="Theme", menu=self.theme_menu)
        self.theme_menu.add_command(label="Dark", command=lambda: self.change_theme("dark"))
        self.theme_menu.add_command(label="Light", command=lambda: self.change_theme("light"))
        self.theme_menu.add_command(label="Green", command=lambda: self.change_theme("green"))
        
        self.view_menu.add_command(label="Refresh Product List", command=self.refresh_product_list)
        
        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0, bg=self.colors.get("bg_secondary"), fg=self.colors.get("fg_main"))
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)
        self.help_menu.add_command(label="Documentation", command=lambda: webbrowser.open("https://github.com/yourusername/inventory-generator/wiki"))
    
    def update_recent_menu(self):
        # Clear the recent menu
        self.recent_menu.delete(0, tk.END)
        
        # Add recent files
        if self.recent_files:
            for file_path in self.recent_files:
                file_name = os.path.basename(file_path)
                self.recent_menu.add_command(
                    label=file_name,
                    command=lambda path=file_path: self.load_csv_from_path(path)
                )
        
        # Add separator if both types exist
        if self.recent_files and self.recent_urls:
            self.recent_menu.add_separator()
        
        # Add recent URLs
        if self.recent_urls:
            for url in self.recent_urls:
                self.recent_menu.add_command(
                    label=url,
                    command=lambda u=url: self.load_from_url(u)
                )
        
        # If no recent items
        if not self.recent_files and not self.recent_urls:
            self.recent_menu.add_command(label="No recent items", state=tk.DISABLED)
    
    def create_data_tab(self):
        # Data Source Tab
        self.data_tab = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.data_tab, text="Data Source")
        
        # URL Entry frame
        url_frame = ttk.Frame(self.data_tab, style="TFrame", padding=(0, 10))
        url_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(url_frame, text="Enter JSON URL:", style="TLabel").pack(anchor=tk.W)
        
        self.url_entry = tk.Entry(
            url_frame,
            font=("Arial", 11),
            bg=self.colors.get("entry_bg"),
            fg=self.colors.get("entry_fg"),
            insertbackground=self.colors.get("fg_main")
        )
        # Set default URL
        self.url_entry.insert(0, "https://api-trace.getbamboo.com/shared/manifests/json/ENTER_YOUR_KEY_HERE")
        self.url_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Add right-click menu to URL entry
        self.create_context_menu(self.url_entry)
        
        # Help text below URL entry
        ttk.Label(
            url_frame,
            text="Tip: Use the API Import tab for more options",
            font=("Arial", 9, "italic"),
            style="TLabel"
        ).pack(anchor=tk.W, pady=(5, 0))
        
        # Button frame
        button_frame = ttk.Frame(self.data_tab, style="TFrame")
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Load buttons
        self.load_json_btn = ttk.Button(
            button_frame,
            text="Load JSON from URL",
            command=self.load_json,
            style="TButton"
        )
        self.load_json_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(button_frame, text="Or", style="TLabel").pack(side=tk.LEFT, padx=5)
        
        self.load_csv_btn = ttk.Button(
            button_frame,
            text="Upload CSV File",
            command=self.load_csv,
            style="TButton"
        )
        self.load_csv_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Add tooltips
        self.create_tooltip(self.load_json_btn, "Load inventory data from a JSON URL")
        self.create_tooltip(self.load_csv_btn, "Upload inventory data from a CSV file")
        
        # Selection frame
        select_frame = ttk.Frame(self.data_tab, style="TFrame")
        select_frame.pack(fill=tk.X, padx=10, pady=(20, 10))
        
        ttk.Label(select_frame, text="Select products to include:", style="TLabel").pack(anchor=tk.W)
        
        # Select all checkbox
        self.select_all_var = tk.BooleanVar(value=True)
        self.select_all_cb = ttk.Checkbutton(
            select_frame,
            text="Select / Deselect All",
            variable=self.select_all_var,
            command=self.toggle_all,
            style="TCheckbutton"
        )
        self.select_all_cb.pack(pady=(10, 10), anchor=tk.W)
        
        # Search and filter frame
        filter_frame = ttk.Frame(self.data_tab, style="TFrame")
        filter_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Search:", style="TLabel").pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search)
        
        self.search_entry = tk.Entry(
            filter_frame,
            textvariable=self.search_var,
            font=("Arial", 11),
            bg=self.colors.get("entry_bg"),
            fg=self.colors.get("entry_fg"),
            insertbackground=self.colors.get("fg_main")
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Clear search button
        self.clear_search_btn = ttk.Button(
            filter_frame,
            text="×",
            width=2,
            command=lambda: self.search_var.set(""),
            style="TButton"
        )
        self.clear_search_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Create scrollable frame for products
        self.create_scrollable_product_list()
        
        # Generate button
        self.generate_btn = ttk.Button(
            self.data_tab,
            text="Generate Inventory Slips",
            command=self.on_generate,
            style="TButton"
        )
        self.generate_btn.pack(pady=20)
    
    def create_scrollable_product_list(self):
        # Container frame for the canvas and scrollbar
        self.list_container = ttk.Frame(self.data_tab, style="TFrame")
        self.list_container.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(
            self.list_container,
            bg=self.colors.get("bg_secondary"),
            highlightthickness=0
        )
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(
            self.list_container,
            orient="vertical",
            command=self.canvas.yview
        )
        
        # Frame inside canvas to hold products
        self.product_frame = ttk.Frame(self.canvas, style="TFrame")
        
        # Configure canvas and scrolling
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create window inside canvas
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.product_frame,
            anchor="nw",
            tags="product_frame"
        )
        
        # Bind events for scrolling and resizing
        self.product_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Bind mouse wheel for scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)
        
        # Initialize dictionaries for product variables
        self.product_vars = {}
        self.group_vars = {}
        
        # Initially display a message when no products are loaded
        self.empty_label = ttk.Label(
            self.product_frame,
            text="No products loaded. Please load data from CSV or JSON.",
            style="TLabel",
            font=("Arial", 12)
        )
        self.empty_label.pack(pady=50)
    
    def on_frame_configure(self, event=None):
        # Update the scrollregion to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event=None):
        # When the canvas is resized, also resize the inner frame
        width = event.width
        self.canvas.itemconfig(self.canvas_window, width=width)
    
    def on_mousewheel(self, event):
        # Respond to mouse wheel events for scrolling
        if sys.platform == 'darwin':
            self.canvas.yview_scroll(-1 * event.delta, "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
            else:
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def toggle_all(self):
        select = self.select_all_var.get()
        
        # First: toggle all individual product checkboxes
        for var, _ in self.product_vars.values():
            var.set(select)
        
        # Then: toggle all group (product type) checkboxes
        for group_var in self.group_vars.values():
            group_var.set(select)
    
    def toggle_group(self, product_type):
        group_select = self.group_vars.get(product_type)
        if group_select is None:
            return
        
        select = group_select.get()
        
        for idx, (var, ptype) in self.product_vars.items():
            if ptype == product_type:
                var.set(select)
    
    def on_search(self, *args):
        search_text = self.search_var.get().lower()
        
        # Hide all products initially
        for widget in self.product_frame.winfo_children():
            if isinstance(widget, tk.Frame) and hasattr(widget, 'product_type'):
                widget.pack_forget()
        
        # If no search text, show all products
        if not search_text:
            for widget in self.product_frame.winfo_children():
                if isinstance(widget, tk.Frame) and hasattr(widget, 'product_type'):
                    widget.pack(fill=tk.X, pady=2, padx=5)
            return
        
        # Show only matching products
        for widget in self.product_frame.winfo_children():
            if isinstance(widget, tk.Frame) and hasattr(widget, 'product_type'):
                product_name = getattr(widget, 'product_name', '').lower()
                product_type = getattr(widget, 'product_type', '').lower()
                strain_name = getattr(widget, 'strain_name', '').lower()
                
                if (search_text in product_name or 
                    search_text in product_type or 
                    search_text in strain_name):
                    widget.pack(fill=tk.X, pady=2, padx=5)
    
    def on_close(self):
        # Save settings before closing
        save_config(self.config)
        self.root.destroy()
    
    def create_preview_tab(self):
        # Preview Tab
        self.preview_tab = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.preview_tab, text="Preview")
        
        # Preview controls frame
        controls_frame = ttk.Frame(self.preview_tab, style="TFrame")
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Items per page selection
        ttk.Label(controls_frame, text="Items per page:", style="TLabel").pack(side=tk.LEFT, padx=(0, 5))
        
        self.items_per_page_var = tk.StringVar(value=self.config['SETTINGS'].get('items_per_page', '4'))
        items_per_page_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.items_per_page_var,
            values=['2', '4', '6', '8'],
            width=5,
            state='readonly'
        )
        items_per_page_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # Auto-open checkbox
        self.auto_open_var = tk.BooleanVar(value=self.config['SETTINGS'].getboolean('auto_open', True))
        auto_open_cb = ttk.Checkbutton(
            controls_frame,
            text="Auto-open generated file",
            variable=self.auto_open_var,
            style="TCheckbutton"
        )
        auto_open_cb.pack(side=tk.LEFT)
        
        # Preview text widget
        self.preview_text = tk.Text(
            self.preview_tab,
            wrap=tk.WORD,
            font=("Courier", 10),
            bg=self.colors.get("bg_secondary"),
            fg=self.colors.get("fg_main"),
            insertbackground=self.colors.get("fg_main")
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Add scrollbar to preview text
        preview_scrollbar = ttk.Scrollbar(
            self.preview_tab,
            orient="vertical",
            command=self.preview_text.yview
        )
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        # Add right-click menu to preview text
        self.create_context_menu(self.preview_text)
        
        # Preview buttons frame
        preview_buttons_frame = ttk.Frame(self.preview_tab, style="TFrame")
        preview_buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Refresh preview button
        self.refresh_preview_btn = ttk.Button(
            preview_buttons_frame,
            text="Refresh Preview",
            command=self.refresh_preview,
            style="TButton"
        )
        self.refresh_preview_btn.pack(side=tk.LEFT)
        
        # Generate button
        self.generate_preview_btn = ttk.Button(
            preview_buttons_frame,
            text="Generate Slips",
            command=self.on_generate,
            style="TButton"
        )
        self.generate_preview_btn.pack(side=tk.RIGHT)
    
    def create_bamboo_tab(self):
        pass
    
    def load_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.load_csv_from_path(file_path)
    
    def load_csv_from_path(self, file_path):
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Process CSV data
            df = process_csv_data(df)
            
            # Update DataFrame and UI
            self.df = df
            self.refresh_product_list()
            
            # Add to recent files
            if file_path not in self.recent_files:
                self.recent_files.insert(0, file_path)
                self.recent_files = self.recent_files[:5]  # Keep only 5 most recent
                self.config['PATHS']['recent_files'] = '|'.join(self.recent_files)
                self.update_recent_menu()
            
            # Switch to data tab
            self.notebook.select(0)
            
            # Update status
            self.status_var.set(f"Loaded {len(df)} products from CSV")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file: {str(e)}")
    
    def load_json(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL")
            return
        
        self.load_from_url(url)
    
    def load_from_url(self, url):
        try:
            # Update status
            self.status_var.set("Loading data from URL...")
            self.progress_var.set(0)
            
            # Fetch data from URL
            response = urllib.request.urlopen(url)
            json_data = json.loads(response.read().decode())
            
            # Parse JSON data
            df, source = parse_inventory_json(json_data)
            
            # Update DataFrame and UI
            self.df = df
            self.refresh_product_list()
            
            # Add to recent URLs
            if url not in self.recent_urls:
                self.recent_urls.insert(0, url)
                self.recent_urls = self.recent_urls[:5]  # Keep only 5 most recent
                self.config['PATHS']['recent_urls'] = '|'.join(self.recent_urls)
                self.update_recent_menu()
            
            # Switch to data tab
            self.notebook.select(0)
            
            # Update status
            self.status_var.set(f"Loaded {len(df)} products from {source}")
            self.progress_var.set(100)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data from URL: {str(e)}")
            self.status_var.set("Error loading data")
            self.progress_var.set(0)
    
    def show_json_paste_dialog(self):
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Paste JSON Data")
        dialog.geometry("600x400")
        dialog.configure(bg=self.colors.get("bg_main"))
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Add text widget
        text = tk.Text(
            dialog,
            wrap=tk.WORD,
            font=("Courier", 10),
            bg=self.colors.get("bg_secondary"),
            fg=self.colors.get("fg_main"),
            insertbackground=self.colors.get("fg_main")
        )
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.configure(yscrollcommand=scrollbar.set)
        
        # Add right-click menu
        self.create_context_menu(text)
        
        # Add buttons
        button_frame = ttk.Frame(dialog, style="TFrame")
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        def on_load():
            try:
                json_data = json.loads(text.get("1.0", tk.END))
                df, source = parse_inventory_json(json_data)
                
                self.df = df
                self.refresh_product_list()
                
                dialog.destroy()
                
                # Switch to data tab
                self.notebook.select(0)
                
                # Update status
                self.status_var.set(f"Loaded {len(df)} products from pasted data")
                
            except Exception as e:
                messagebox.showerror("Error", f"Invalid JSON data: {str(e)}")
        
        ttk.Button(
            button_frame,
            text="Load Data",
            command=on_load,
            style="TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            style="TButton"
        ).pack(side=tk.RIGHT)
    
    def show_url_dialog(self):
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Load from URL")
        dialog.geometry("500x150")
        dialog.configure(bg=self.colors.get("bg_main"))
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Add URL entry
        ttk.Label(
            dialog,
            text="Enter JSON URL:",
            style="TLabel"
        ).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        url_entry = tk.Entry(
            dialog,
            font=("Arial", 11),
            bg=self.colors.get("entry_bg"),
            fg=self.colors.get("entry_fg"),
            insertbackground=self.colors.get("fg_main")
        )
        url_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Add right-click menu
        self.create_context_menu(url_entry)
        
        # Add buttons
        button_frame = ttk.Frame(dialog, style="TFrame")
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        def on_load():
            url = url_entry.get().strip()
            if url:
                dialog.destroy()
                self.load_from_url(url)
        
        ttk.Button(
            button_frame,
            text="Load",
            command=on_load,
            style="TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            style="TButton"
        ).pack(side=tk.RIGHT)
    
    def show_find_dialog(self):
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Find")
        dialog.geometry("300x100")
        dialog.configure(bg=self.colors.get("bg_main"))
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Add search entry
        ttk.Label(
            dialog,
            text="Search:",
            style="TLabel"
        ).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        search_entry = tk.Entry(
            dialog,
            font=("Arial", 11),
            bg=self.colors.get("entry_bg"),
            fg=self.colors.get("entry_fg"),
            insertbackground=self.colors.get("fg_main")
        )
        search_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Add right-click menu
        self.create_context_menu(search_entry)
        
        # Add buttons
        button_frame = ttk.Frame(dialog, style="TFrame")
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        def on_find():
            search_text = search_entry.get().strip()
            if search_text:
                self.search_var.set(search_text)
                dialog.destroy()
        
        ttk.Button(
            button_frame,
            text="Find",
            command=on_find,
            style="TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            style="TButton"
        ).pack(side=tk.RIGHT)
    
    def show_settings(self):
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Settings")
        dialog.geometry("400x300")
        dialog.configure(bg=self.colors.get("bg_main"))
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Settings frame
        settings_frame = ttk.Frame(dialog, style="TFrame", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Theme selection
        ttk.Label(
            settings_frame,
            text="Theme:",
            style="TLabel"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        theme_var = tk.StringVar(value=self.theme_name)
        theme_combo = ttk.Combobox(
            settings_frame,
            textvariable=theme_var,
            values=["dark", "light", "green"],
            state="readonly"
        )
        theme_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Font size selection
        ttk.Label(
            settings_frame,
            text="Font Size:",
            style="TLabel"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        font_size_var = tk.StringVar(value=self.config['SETTINGS'].get('font_size', '11'))
        font_size_combo = ttk.Combobox(
            settings_frame,
            textvariable=font_size_var,
            values=["9", "10", "11", "12", "14", "16"],
            state="readonly"
        )
        font_size_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Items per page selection
        ttk.Label(
            settings_frame,
            text="Items per page:",
            style="TLabel"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        items_per_page_var = tk.StringVar(value=self.config['SETTINGS'].get('items_per_page', '4'))
        items_per_page_combo = ttk.Combobox(
            settings_frame,
            textvariable=items_per_page_var,
            values=["2", "4", "6", "8"],
            state="readonly"
        )
        items_per_page_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Auto-open checkbox
        auto_open_var = tk.BooleanVar(value=self.config['SETTINGS'].getboolean('auto_open', True))
        auto_open_cb = ttk.Checkbutton(
            settings_frame,
            text="Auto-open generated file",
            variable=auto_open_var,
            style="TCheckbutton"
        )
        auto_open_cb.pack(anchor=tk.W, pady=(0, 10))
        
        # Add buttons
        button_frame = ttk.Frame(dialog, style="TFrame")
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        def on_save():
            # Save settings
            self.config['SETTINGS']['theme'] = theme_var.get()
            self.config['SETTINGS']['font_size'] = font_size_var.get()
            self.config['SETTINGS']['items_per_page'] = items_per_page_var.get()
            self.config['SETTINGS']['auto_open'] = str(auto_open_var.get())
            
            # Update UI
            self.change_theme(theme_var.get())
            self.items_per_page_var.set(items_per_page_var.get())
            self.auto_open_var.set(auto_open_var.get())
            
            dialog.destroy()
        
        ttk.Button(
            button_frame,
            text="Save",
            command=on_save,
            style="TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            style="TButton"
        ).pack(side=tk.RIGHT)
    
    def show_api_settings(self):
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("API Settings")
        dialog.geometry("400x200")
        dialog.configure(bg=self.colors.get("bg_main"))
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Settings frame
        settings_frame = ttk.Frame(dialog, style="TFrame", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # API Key entry
        ttk.Label(
            settings_frame,
            text="Bamboo API Key:",
            style="TLabel"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        api_key_entry = tk.Entry(
            settings_frame,
            font=("Arial", 11),
            bg=self.colors.get("entry_bg"),
            fg=self.colors.get("entry_fg"),
            insertbackground=self.colors.get("fg_main")
        )
        api_key_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Add right-click menu
        self.create_context_menu(api_key_entry)
        
        # Add buttons
        button_frame = ttk.Frame(dialog, style="TFrame")
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        def on_save():
            api_key = api_key_entry.get().strip()
            if api_key:
                self.config['API']['bamboo_key'] = api_key
                self.api_key_entry.delete(0, tk.END)
                self.api_key_entry.insert(0, api_key)
                dialog.destroy()
        
        ttk.Button(
            button_frame,
            text="Save",
            command=on_save,
            style="TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            style="TButton"
        ).pack(side=tk.RIGHT)
    
    def show_about(self):
        messagebox.showinfo(
            "About",
            f"Inventory Slip Generator v{APP_VERSION}\n\n"
            "A tool for generating inventory slips from CSV and JSON data.\n\n"
            "Created by Your Name\n"
            "© 2024 All rights reserved."
        )
    
    def change_theme(self, theme_name):
        self.theme_name = theme_name
        self.colors = ThemeColors(theme_name)
        
        # Update UI colors
        self.root.configure(bg=self.colors.get("bg_main"))
        
        # Update text widgets
        for widget in [self.preview_text, self.url_entry, self.api_key_entry,
                      self.start_date_entry, self.end_date_entry]:
            widget.configure(
                bg=self.colors.get("bg_secondary"),
                fg=self.colors.get("fg_main"),
                insertbackground=self.colors.get("fg_main")
            )
        
        # Update canvas
        self.canvas.configure(bg=self.colors.get("bg_secondary"))
    
    def refresh_product_list(self):
        # Clear existing products
        for widget in self.product_frame.winfo_children():
            widget.destroy()
        
        # Clear dictionaries
        self.product_vars.clear()
        self.group_vars.clear()
        
        if self.df.empty:
            # Show empty message
            self.empty_label = ttk.Label(
                self.product_frame,
                text="No products loaded. Please load data from CSV or JSON.",
                style="TLabel",
                font=("Arial", 12)
            )
            self.empty_label.pack(pady=50)
            return
        
        # Group products by type
        product_types = self.df['product_type'].unique()
        
        for product_type in product_types:
            # Create group frame
            group_frame = ttk.Frame(self.product_frame, style="TFrame")
            group_frame.pack(fill=tk.X, pady=2, padx=5)
            group_frame.product_type = product_type
            
            # Group checkbox
            group_var = tk.BooleanVar(value=True)
            self.group_vars[product_type] = group_var
            
            group_cb = ttk.Checkbutton(
                group_frame,
                text=product_type,
                variable=group_var,
                command=lambda t=product_type: self.toggle_group(t),
                style="TCheckbutton"
            )
            group_cb.pack(side=tk.LEFT, padx=(0, 10))
            
            # Products in this group
            products = self.df[self.df['product_type'] == product_type]
            
            for _, product in products.iterrows():
                # Create product frame
                product_frame = ttk.Frame(self.product_frame, style="TFrame")
                product_frame.pack(fill=tk.X, pady=2, padx=5)
                product_frame.product_type = product_type
                product_frame.product_name = product['product_name']
                product_frame.strain_name = product.get('strain_name', '')
                
                # Product checkbox
                product_var = tk.BooleanVar(value=True)
                self.product_vars[product.name] = (product_var, product_type)
                
                product_cb = ttk.Checkbutton(
                    product_frame,
                    text=f"{product['product_name']} ({product.get('strain_name', 'N/A')})",
                    variable=product_var,
                    style="TCheckbutton"
                )
                product_cb.pack(side=tk.LEFT, padx=(20, 0))
    
    def refresh_preview(self):
        if self.df.empty:
            messagebox.showwarning("Warning", "No data loaded")
            return
        
        # Get selected products
        selected_products = []
        for idx, (var, _) in self.product_vars.items():
            if var.get():
                selected_products.append(self.df.iloc[idx])
        
        if not selected_products:
            messagebox.showwarning("Warning", "No products selected")
            return
        
        # Create preview text
        preview_text = []
        items_per_page = int(self.items_per_page_var.get())
        
        for i in range(0, len(selected_products), items_per_page):
            page_products = selected_products[i:i + items_per_page]
            
            # Add page header
            preview_text.append("=" * 50)
            preview_text.append(f"Page {i // items_per_page + 1}")
            preview_text.append("=" * 50)
            preview_text.append("")
            
            # Add products
            for product in page_products:
                preview_text.append(f"Product: {product['product_name']}")
                preview_text.append(f"Type: {product['product_type']}")
                if 'strain_name' in product:
                    preview_text.append(f"Strain: {product['strain_name']}")
                preview_text.append(f"Quantity: {product['quantity']}")
                if 'barcode' in product:
                    preview_text.append(f"Barcode: {product['barcode']}")
                preview_text.append("")
            
            preview_text.append("\n")
        
        # Update preview text widget
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", "\n".join(preview_text))
    
    def on_generate(self):
        if self.df.empty:
            messagebox.showwarning("Warning", "No data loaded")
            return
        
        # Get selected products
        selected_products = []
        for idx, (var, _) in self.product_vars.items():
            if var.get():
                selected_products.append(self.df.iloc[idx])
        
        if not selected_products:
            messagebox.showwarning("Warning", "No products selected")
            return
        
        # Create DataFrame from selected products
        selected_df = pd.DataFrame(selected_products)
        
        # Get settings
        items_per_page = int(self.items_per_page_var.get())
        auto_open = self.auto_open_var.get()
        
        # Update status
        self.status_var.set("Generating inventory slips...")
        self.progress_var.set(0)
        
        # Run in background thread
        def generate_thread():
            try:
                run_full_process_inventory_slips(
                    selected_df,
                    self.config,
                    lambda msg: self.status_var.set(msg),
                    lambda val: self.progress_var.set(val)
                )
                
                if auto_open:
                    output_path = self.config['PATHS']['output_dir']
                    if os.path.exists(output_path):
                        self.open_file(output_path)
                
                self.status_var.set("Generation complete")
                self.progress_var.set(100)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate slips: {str(e)}")
                self.status_var.set("Error generating slips")
                self.progress_var.set(0)
        
        threading.Thread(target=generate_thread, daemon=True).start()
    
    def fetch_bamboo_data(self):
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showwarning("Warning", "Please enter an API key")
            return
        
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        
        if not start_date or not end_date:
            messagebox.showwarning("Warning", "Please enter both start and end dates")
            return
        
        try:
            # Update status
            self.api_status_var.set("Fetching data...")
            self.api_progress_var.set(0)
            
            # Construct URL
            url = f"https://api-trace.getbamboo.com/shared/manifests/json/{api_key}"
            if start_date and end_date:
                url += f"?start_date={start_date}&end_date={end_date}"
            
            # Fetch data
            response = urllib.request.urlopen(url)
            json_data = json.loads(response.read().decode())
            
            # Parse JSON data
            df, source = parse_inventory_json(json_data)
            
            # Update DataFrame and UI
            self.df = df
            self.refresh_product_list()
            
            # Switch to data tab
            self.notebook.select(0)
            
            # Update status
            self.api_status_var.set(f"Loaded {len(df)} products from {source}")
            self.api_progress_var.set(100)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data: {str(e)}")
            self.api_status_var.set("Error fetching data")
            self.api_progress_var.set(0)
    
    def save_api_key(self):
        api_key = self.api_key_entry.get().strip()
        if api_key:
            self.config['API']['bamboo_key'] = api_key
            messagebox.showinfo("Success", "API key saved")
        else:
            messagebox.showwarning("Warning", "Please enter an API key")
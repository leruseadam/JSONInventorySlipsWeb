import tkinter as tk
from tkinter import ttk

class BaseUI:
    """Base UI class with common functionality"""
    
    def __init__(self):
        self.root = None
        self.style = None
        self.colors = None
    
    def init_ui(self):
        """Initialize UI components"""
        raise NotImplementedError
    
    def create_menu(self):
        """Create menu structure"""
        raise NotImplementedError
    
    def create_styles(self):
        """Create ttk styles"""
        raise NotImplementedError
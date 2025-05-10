import os
import sys
import tkinter as tk

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.ui.app import InventorySlipGenerator
from src.config.settings import APP_VERSION, resource_path

def main():
    root = tk.Tk()
    
    # Set window title and icon
    root.title(f"Inventory Slip Generator v{APP_VERSION}")
    
    try:
        if sys.platform == "win32":
            root.iconbitmap(resource_path("assets/icon.ico"))
    except:
        pass
    
    # Center window on screen
    app_width = 850
    app_height = 750
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (app_width // 2)
    y = (screen_height // 2) - (app_height // 2)
    root.geometry(f"{app_width}x{app_height}+{x}+{y}")
    
    # Create application
    app = InventorySlipGenerator(root)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main() 
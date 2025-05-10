"""
Inventory Slip Generator package
"""

__version__ = "2.0.0"

from .ui.app import InventorySlipGenerator
from .utils.document_handler import DocumentHandler
from .ui.base import BaseUI
from .themes.theme_manager import ThemeColors
from .data.processor import parse_inventory_json, process_csv_data
from .utils.helpers import run_full_process_inventory_slips, open_file

__all__ = [
    'InventorySlipGenerator',
    'BaseUI',
    'ThemeColors',
    'parse_inventory_json',
    'process_csv_data',
    'run_full_process_inventory_slips',
    'open_file',
]
#!/usr/bin/env python3
"""
Inventory Slip Generator - Flask Web Application
Run script to start the application with proper configuration.
"""

import os
import sys
import argparse
import tempfile
from app import app

def parse_arguments():
    parser = argparse.ArgumentParser(description='Run the Inventory Slip Generator Flask application')
    parser.add_argument('--debug', action='store_true', 
                        help='Run in debug mode (not recommended for production)')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Host to run the server on (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port to run the server on (default: 5000)')
    return parser.parse_args()

def create_folders():
    """Ensure necessary folders exist"""
    # Templates folder
    os.makedirs('templates', exist_ok=True)
    
    # Static folder for assets
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/assets', exist_ok=True)
    
    # Template documents folder
    os.makedirs('templates/documents', exist_ok=True)
    
    # Temporary upload folder
    upload_folder = os.path.join(tempfile.gettempdir(), "inventory_generator", "uploads")
    os.makedirs(upload_folder, exist_ok=True)

def main():
    args = parse_arguments()
    
    print(f"Starting Inventory Slip Generator on {args.host}:{args.port}")
    
    if args.debug:
        print("WARNING: Running in debug mode. Do not use in production.")
    
    # Create necessary folders
    create_folders()
    
    # Run the Flask application
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()
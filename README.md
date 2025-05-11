# Inventory Slip Generator - Flask Web Application

A web-based application for generating inventory slips from CSV and JSON data. This application supports Bamboo Transfer schema and Cultivera format for cannabis inventory management.

## Features

- Import data from CSV files
- Import data from Bamboo and Cultivera JSON formats
- Direct API integration with configurable authentication
- Custom template support for inventory slip generation
- Automatic font sizing for readability
- Multiple items per page configuration
- Dark, light, and green themes
- Responsive web interface
- Search and filter functionality for inventory items
- Bulk selection/deselection of items
- Downloadable Word document output

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Steps

1. Clone the repository or download the source code

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up the application:
   ```bash
   python run.py --debug
   ```

6. Access the application in your web browser at: `http://127.0.0.1:5000`

## Directory Structure

```
inventory-generator/
├── inventory_generator.py    # Main Flask application file
├── run.py                    # Script to run the application
├── requirements.txt          # Python dependencies
├── static/                   # Static assets
├── templates/                # HTML templates
│   ├── base.html             # Base template
│   ├── index.html            # Home page
│   ├── data_view.html        # Data view page
│   ├── api_import.html       # API import page
│   ├── settings.html         # Settings page
│   ├── result.html           # Result page
│   ├── view_json.html        # JSON view page
│   ├── about.html            # About page
│   ├── 404.html              # 404 error page
│   └── 500.html              # 500 error page
└── templates/documents/      # Word document templates
    └── InventorySlips.docx   # Default template
```

## Usage

1. **Start the application:**
   Run `python run.py` to start the web server

2. **Import Data:**
   - Upload a CSV file with inventory data
   - Upload a JSON file (Bamboo or Cultivera format)
   - Paste JSON data directly
   - Fetch from an API URL (with optional authentication)

3. **Select Products:**
   - Browse the loaded inventory items
   - Use the search function to filter products
   - Select/deselect all products or by category
   - Check individual products to include

4. **Generate Document:**
   - Click "Generate Inventory Slips" to create the document
   - Download the generated Word document
   - Adjust settings as needed (items per page, output location)

## Configuration

The application stores configuration in `~/inventory_generator_config.ini` with the following sections:

### PATHS
- `template_path`: Path to the Word document template
- `output_dir`: Directory where generated documents are saved
- `recent_files`: Recently used file paths (CSV/JSON)
- `recent_urls`: Recently used API URLs

### SETTINGS
- `items_per_page`: Number of inventory items per page (2, 4, 6, or 8)
- `auto_open`: Automatically open generated documents
- `theme`: UI theme (dark, light, or green)
- `font_size`: Base font size for the application

### API
- `bamboo_key`: API key for Bamboo integration

## Production Deployment

For production deployment, it's recommended to use a WSGI server like Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 inventory_generator:app
```

You may also want to set up a reverse proxy like Nginx to handle static files and SSL termination.

## Templates

The application uses Word document templates (*.docx) with the DocxTemplate library. The default template includes:

- Four item slots per page (configurable)
- Fields for product name, barcode, quantity, vendor, strain name, etc.
- Dynamic font sizing based on content length

You can create custom templates by modifying the default one and setting the path in the application settings.

## License

This software is proprietary. All rights reserved.

## Author

Created by Adam Cordova
AGT Bothell 2025©
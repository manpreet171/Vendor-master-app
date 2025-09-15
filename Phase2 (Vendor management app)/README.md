# Vendor Management System

A Streamlit-based web application for managing vendor-item relationships with cost-based uniqueness.

## Features

- **Dashboard**: Overview of system data with key metrics and charts
- **Item Management**: Add, edit, view, and delete items
- **Vendor Management**: Add, edit, view, and delete vendors
- **Mapping Management**: Create and manage item-vendor relationships
- **Data Validation**: Validate data integrity and find issues

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- SQL Server with ODBC Driver
- Database created using the Phase 1 scripts

### Installation

1. Clone this repository or download the files
2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on the `.env.template`:

```bash
cp .env.template .env
```

4. Edit the `.env` file with your database connection details:

```
DB_SERVER=your_server_name
DB_NAME=your_database_name
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_DRIVER={ODBC Driver 17 for SQL Server}
```

### Running the Application

Run the Streamlit app:

```bash
streamlit run app.py
```

The application will be available at http://localhost:8501

## Usage Guide

### Dashboard

The dashboard provides an overview of your data with key metrics:
- Total items and vendors
- Item source distribution
- Item type distribution
- Top vendors by item count

### Item Management

- **View Items**: Browse all items with filtering options
- **Add Item**: Create new items with all required attributes
- **Edit/Delete Item**: Modify or remove existing items
- **View Vendors**: See which vendors supply a specific item

### Vendor Management

- **View Vendors**: Browse all vendors
- **Add Vendor**: Create new vendor records
- **Edit/Delete Vendor**: Modify or remove existing vendors
- **View Items**: See which items are supplied by a specific vendor

### Mapping Management

- **View Mappings**: Browse all item-vendor mappings with filtering
- **Add Mapping**: Create new relationships between items and vendors
- **Edit Mapping**: Update cost information for existing mappings
- **Find Unmapped Items**: Identify and fix items without vendor mappings

### Data Validation

- Run validation checks to ensure data integrity
- Find unmapped items
- Detect duplicate mappings
- Analyze vendor distribution

## File Structure

- `app.py`: Main application file
- `db_connector.py`: Database connection and operations
- `item_manager.py`: Item management module
- `vendor_manager.py`: Vendor management module
- `mapping_manager.py`: Mapping management module
- `utils.py`: Utility functions
- `requirements.txt`: Required Python packages
- `.env.template`: Template for environment variables

## Database Structure

The application works with the following database tables:

### Vendors
- `vendor_id`: Primary key
- `vendor_name`: Name of the vendor
- `contact_name`: Contact person name
- `vendor_email`: Email address
- `vendor_phone`: Phone number

### Items
- `item_id`: Primary key
- `item_name`: Name of the item
- `item_type`: Category/type of item
- `source_sheet`: Source of the item data (BoxHero/Raw Materials)
- `sku`: Stock keeping unit
- `barcode`: Barcode identifier
- `height`: Height dimension
- `width`: Width dimension
- `thickness`: Thickness dimension
- `cost`: Item cost

### ItemVendorMap
- `map_id`: Primary key
- `item_id`: Foreign key to Items
- `vendor_id`: Foreign key to Vendors
- `cost`: Cost of item from this vendor

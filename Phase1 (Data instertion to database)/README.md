# SDGNY Vendor Management System

A database-driven application for managing vendors and items for SDGNY with a Streamlit web interface for data import.

## Database Setup

This project uses SQL Server as its database. Follow these steps to set up the database:

1. Ensure you have SQL Server installed and running on your system (SQL Server Express is sufficient)
2. Create a new database called `sdgny_vendor_management` (or your preferred name)
3. Run the SQL script in `database_setup.sql` to create the required tables

You can execute the script using SQL Server Management Studio (SSMS):
1. Open SSMS and connect to your SQL Server instance
2. Open the `database_setup.sql` file
3. Select the database you created in the dropdown
4. Execute the script

## Environment Configuration

1. Copy the `.env.template` file to a new file named `.env`
2. Edit the `.env` file and update the database connection settings to match your SQL Server setup:
   ```
   # For Azure SQL Database
   DB_SERVER=your-server.database.windows.net
   DB_NAME=your-database
   DB_USER=your-username
   DB_PASSWORD=your-password
   DB_DRIVER=ODBC Driver 17 for SQL Server
   
   # For local SQL Server with Windows Authentication
   # DB_SERVER=localhost\SQLEXPRESS
   # DB_NAME=sdgny_vendor_management
   # DB_USER=
   # DB_PASSWORD=
   # DB_DRIVER=ODBC Driver 17 for SQL Server
   ```

## Quick Setup with Virtual Environment

For Windows users, we've provided a batch script to set up the virtual environment automatically:

1. Run the `setup_venv.bat` script by double-clicking it or running it from the command prompt
2. This will create a virtual environment and install all required dependencies

## Manual Installation

If you prefer to set up manually:

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install the SQL Server ODBC Driver if not already installed:
   - Download and install the [Microsoft ODBC Driver for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
   - The code is configured to use ODBC Driver 17, but you can modify the connection string in `db_connector.py` if you have a different version

## Testing Database Connection

Before running the app, you can test your database connection:

1. Activate your virtual environment if not already activated
2. Run the test script:
   ```bash
   python test_connection.py
   ```
3. If successful, you'll see a confirmation message

## Running the Streamlit App

The Streamlit app provides a web interface for importing data from Excel files:

1. Activate your virtual environment if not already activated
2. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
3. Your default web browser should open automatically to the app (typically at http://localhost:8501)

## Using the Data Import App

1. Prepare your Excel file with three sheets:
   - `Final_Vendor_List`: Contains vendor information
   - `BoxHero_Items`: Contains BoxHero items with vendor mappings
   - `Raw_Materials_Items`: Contains Raw Materials items with vendor mappings

2. Upload your Excel file using the file uploader in the app

3. Preview the data in each tab

4. Click "Import Data to Database" to start the import process

5. Use the verification tabs to check the imported data

## Database Schema

The database consists of three main tables:

1. **Vendors**: Stores information about suppliers
   - vendor_id (PK, IDENTITY)
   - vendor_name (UNIQUE)
   - contact_name
   - vendor_email
   - vendor_phone

2. **Items**: Stores the catalog of all products
   - item_id (PK, IDENTITY)
   - item_name
   - item_type
   - source_sheet
   - sku
   - barcode
   - height
   - width
   - thickness
   - UNIQUE constraint on (item_name, item_type, sku, height, width, thickness)

3. **ItemVendorMap**: Links vendors to the items they supply
   - map_id (PK, IDENTITY)
   - item_id (FK)
   - vendor_id (FK)
   - cost
   - UNIQUE constraint on (item_id, vendor_id)

## Project Structure

- `app.py` - Streamlit web application for data import
- `db_connector.py` - Database connection and operations class
- `test_connection.py` - Script to test database connectivity
- `database_setup.sql` - SQL script to create database tables
- `requirements.txt` - Python package dependencies
- `setup_venv.bat` - Batch script to set up virtual environment
- `.env` - Environment variables for database connection (create from .env.template)

## Manual Data Import

If you prefer to import data manually using SQL:

1. Use the SQL scripts in the following files:
   - `vendor_inserts.sql` - Insert vendor data
   - `part1_boxhero_items.sql` and `part2_boxhero_items.sql` - Insert BoxHero items
   - `part1_boxhero_mappings.sql`, `part2_boxhero_mappings.sql`, and `part3_boxhero_mappings.sql` - Create item-vendor mappings

2. Execute these scripts in SQL Server Management Studio in the order listed above

## API Usage

The `db_connector.py` file provides a `DatabaseConnector` class with methods for interacting with the database programmatically:

```python
from db_connector import DatabaseConnector

# Connect to database
db = DatabaseConnector()

# Add a vendor
db.add_vendor("Vendor Name", "Contact Person", "email@example.com", "123-456-7890")

# Add an item
db.add_item("Item Name", "Item Type", "BoxHero", "SKU123", "BARCODE123", None, None, None)

# Link an item to a vendor with cost
db.link_item_to_vendor(item_id, vendor_id, 99.99)

# Close connection when done
db.close_connection()
```

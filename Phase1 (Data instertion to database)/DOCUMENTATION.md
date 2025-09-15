# Vendor Management System Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Database Structure](#database-structure)
3. [Data Flow](#data-flow)
4. [Import Process](#import-process)
5. [Application Features](#application-features)
6. [Key Challenges and Solutions](#key-challenges-and-solutions)
7. [SQL Queries Reference](#sql-queries-reference)

## System Overview

The Vendor Management System is a Streamlit-based web application designed to manage vendor-item relationships with cost-based uniqueness. The system imports data from Excel files, stores it in an Azure SQL Server database, and provides various features for data validation, visualization, and querying.

### Core Functionality
- Import vendor and item data from Excel files
- Maintain many-to-many relationships between items and vendors
- Track cost information for each item-vendor relationship
- Support cost-based uniqueness for items
- Provide data validation and verification tools
- Enable searching and filtering of items and vendors

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python
- **Database**: Azure SQL Server
- **Libraries**: pandas, pyodbc, python-dotenv, plotly

## Database Structure

### Tables

#### 1. Vendors
Stores information about suppliers/vendors.

| Column Name | Data Type | Description | Constraints |
|-------------|-----------|-------------|------------|
| vendor_id | INT | Primary key | IDENTITY, PRIMARY KEY |
| vendor_name | VARCHAR(255) | Name of the vendor | NOT NULL |
| contact_name | VARCHAR(255) | Contact person name | NULL |
| vendor_email | VARCHAR(255) | Email address | NULL |
| vendor_phone | VARCHAR(50) | Phone number | NULL |

#### 2. Items
Stores information about products/materials.

| Column Name | Data Type | Description | Constraints |
|-------------|-----------|-------------|------------|
| item_id | INT | Primary key | IDENTITY, PRIMARY KEY |
| item_name | VARCHAR(255) | Name of the item | NOT NULL |
| item_type | VARCHAR(255) | Category/type of item | NULL |
| source_sheet | VARCHAR(50) | Source of the item data (BoxHero/Raw Materials) | NULL |
| sku | VARCHAR(255) | Stock keeping unit | NULL |
| barcode | VARCHAR(255) | Barcode identifier | NULL |
| height | DECIMAL(10,4) | Height dimension | NULL |
| width | DECIMAL(10,4) | Width dimension | NULL |
| thickness | DECIMAL(10,4) | Thickness dimension | NULL |
| cost | DECIMAL(10,2) | Item cost | NULL |

#### 3. ItemVendorMap
Manages the many-to-many relationship between items and vendors.

| Column Name | Data Type | Description | Constraints |
|-------------|-----------|-------------|------------|
| map_id | INT | Primary key | IDENTITY, PRIMARY KEY |
| item_id | INT | Foreign key to Items | FOREIGN KEY |
| vendor_id | INT | Foreign key to Vendors | FOREIGN KEY |
| cost | DECIMAL(10,2) | Cost of item from this vendor | NULL |

### Relationships

1. **Items to Vendors**: Many-to-Many relationship through ItemVendorMap
   - One item can be supplied by multiple vendors
   - One vendor can supply multiple items
   - Each item-vendor pair can have a specific cost

### Uniqueness Constraints

1. **Vendors**: Unique by vendor_name
2. **Items**: Unique by combination of:
   - item_name
   - item_type
   - source_sheet
   - sku
   - barcode
   - dimensions (height, width, thickness)
   - cost

The cost field is part of the uniqueness key, meaning the same item with different costs is treated as different items.

## Data Flow

### Overall Data Flow

1. **Data Source**: Excel files containing vendor and item information
2. **Import Process**: Python scripts parse Excel data
3. **Data Processing**: 
   - Data cleaning and validation
   - Type conversion
   - Uniqueness checking
4. **Database Storage**: Data inserted into Azure SQL Server
5. **User Interface**: Streamlit app for data visualization and interaction

### Data Flow Diagram

```
Excel Files → Import Scripts → Data Processing → Azure SQL Database ↔ Streamlit App ↔ User
```

## Import Process

The import process handles data from Excel files and populates the database tables.

### Import Steps

1. **Connect to Database**: Establish connection to Azure SQL Server
2. **Import Vendors**:
   - Read vendor data from Excel
   - Check for existing vendors to avoid duplicates
   - Insert new vendors into the Vendors table
   
3. **Import BoxHero Items**:
   - Read BoxHero items from Excel
   - Process data (handle NULL values, convert types)
   - Check for existing items using uniqueness constraints
   - Insert new items into the Items table
   - Create item-vendor mappings in ItemVendorMap table
   
4. **Import Raw Materials Items**:
   - Similar process to BoxHero items
   - Different data structure and fields
   - Insert items and create mappings
   
5. **Validate Data**:
   - Check for unmapped items
   - Identify duplicate mappings
   - Verify multi-vendor relationships

### Key Import Logic

#### Vendor Import
```python
def import_vendors(excel_path, db, progress_bar=None, status_text=None):
    # Read Excel file
    df = pd.read_excel(excel_path, sheet_name="Vendors")
    
    # Process each vendor
    for index, row in df.iterrows():
        vendor_name = row['Vendor Name']
        
        # Check if vendor already exists
        existing = db.fetch_data("SELECT vendor_id FROM Vendors WHERE vendor_name = ?", [vendor_name])
        if existing:
            continue
            
        # Insert new vendor
        query = """
            INSERT INTO Vendors (vendor_name, contact_name, vendor_email, vendor_phone)
            VALUES (?, ?, ?, ?)
        """
        db.execute_query(query, [vendor_name, contact_name, vendor_email, vendor_phone])
```

#### Item Import with Cost-Based Uniqueness
```python
def import_unique_items(df, db, source_sheet, progress_bar=None, status_text=None):
    unique_items = {}
    
    for index, row in df.iterrows():
        item_name = row['Item Name']
        item_type = row['Item Type']
        cost = row.get('Cost')
        
        # Convert cost to float or None
        cost = float(cost) if cost and not pd.isna(cost) else None
        
        # Create unique key including cost
        item_key = f"{item_name}|{item_type}|{source_sheet}|{cost}"
        
        # Check if item already exists
        query = """
            SELECT item_id FROM Items
            WHERE item_name = ? AND item_type = ? AND source_sheet = ?
            AND ISNULL(sku, '') = ISNULL(?, '')
            AND ISNULL(barcode, '') = ISNULL(?, '')
            AND ISNULL(height, 0) = ISNULL(?, 0)
            AND ISNULL(width, 0) = ISNULL(?, 0)
            AND ISNULL(thickness, 0) = ISNULL(?, 0)
            AND ISNULL(cost, 0) = ISNULL(?, 0)
        """
        existing = db.fetch_data(query, [item_name, item_type, source_sheet, sku, barcode, 
                                        height, width, thickness, cost])
        
        if existing:
            unique_items[item_key] = existing[0]['item_id']
            continue
            
        # Insert new item
        insert_query = """
            INSERT INTO Items (item_name, item_type, source_sheet, sku, barcode, 
                             height, width, thickness, cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        db.execute_query(insert_query, [item_name, item_type, source_sheet, sku, barcode, 
                                       height, width, thickness, cost])
        
        # Get the new item_id
        new_item = db.fetch_data("SELECT @@IDENTITY AS item_id")
        unique_items[item_key] = new_item[0]['item_id']
    
    return unique_items
```

#### Creating Item-Vendor Mappings
```python
def create_item_vendor_mappings(df, db, source_sheet, items_dict, vendors_dict):
    for index, row in df.iterrows():
        item_name = row['Item Name']
        item_type = row['Item Type']
        vendor_name = row['Vendor']
        cost = row.get('Cost')
        
        # Convert cost to float or None
        cost = float(cost) if cost and not pd.isna(cost) else None
        
        # Get item_id using the same key format as during item creation
        item_key = f"{item_name}|{item_type}|{source_sheet}|{cost}"
        item_id = items_dict.get(item_key)
        
        # Get vendor_id
        vendor_id = vendors_dict.get(vendor_name)
        
        # Create mapping if both IDs exist
        if item_id and vendor_id:
            # Check if mapping already exists
            existing = db.fetch_data(
                "SELECT map_id FROM ItemVendorMap WHERE item_id = ? AND vendor_id = ?",
                [item_id, vendor_id]
            )
            
            if not existing:
                # Insert mapping
                query = "INSERT INTO ItemVendorMap (item_id, vendor_id, cost) VALUES (?, ?, ?)"
                db.execute_query(query, [item_id, vendor_id, cost])
```

## Application Features

### 1. Data Import
- Import vendors and items from Excel files
- Progress tracking and status updates
- Error handling and reporting

### 2. Data Verification
- **Vendors Tab**: View all vendors in the database
- **Items Tab**: View all items with filtering by source and type
- **Item-Vendor Mappings Tab**: View all mappings with filtering
- **Vendor Count Analysis Tab**: Analyze vendor distribution
- **Data Validation Tab**: Validate data integrity
- **Find Vendors Tab**: Search for vendors by item name

### 3. Data Validation
- Check for unmapped items
- Identify items with multiple vendors
- Detect duplicate mappings
- Map unmapped items to vendors

### 4. Search and Filter
- Search items by name
- Filter by source (BoxHero/Raw Materials)
- Filter by item type
- Find vendors for specific items
- Find items supplied by specific vendors

### 5. Visualization
- Item type distribution charts
- Vendor count analysis
- Multi-vendor item examples

## Key Challenges and Solutions

### 1. Cost-Based Item Uniqueness

**Challenge**: Items with the same name but different costs needed to be treated as separate items.

**Solution**: 
- Included cost in the item uniqueness key
- Modified database queries to consider cost in uniqueness checks
- Added cost column to Items table
- Updated item lookup logic to include cost

### 2. NULL Value Handling

**Challenge**: NULL values in Excel caused issues with database insertion and uniqueness checks.

**Solution**:
- Used `ISNULL()` in SQL queries to handle NULL values consistently
- Converted empty strings to NULL before database insertion
- Added proper type conversion with error handling
- Used `pd.isna()` to detect NaN values in pandas

### 3. Data Type Conversion

**Challenge**: Excel data types didn't always match database column types.

**Solution**:
- Added explicit type conversion for numeric fields
- Implemented error handling for conversion failures
- Converted numeric barcodes to strings
- Handled special cases for SKUs and dimensions

### 4. Many-to-Many Relationships

**Challenge**: Managing the many-to-many relationship between items and vendors.

**Solution**:
- Created ItemVendorMap junction table
- Implemented two-pass import process (items first, then mappings)
- Added validation to check for unmapped items
- Created UI for manually mapping items to vendors

### 5. Search Functionality

**Challenge**: Finding items and vendors efficiently.

**Solution**:
- Implemented dropdown and text search options
- Added partial matching using SQL LIKE queries
- Created case-insensitive search
- Added filtering by source and item type

## SQL Queries Reference

### Find Vendors for an Item
```sql
SELECT 
    v.vendor_id,
    v.vendor_name,
    v.contact_name,
    v.vendor_email,
    v.vendor_phone,
    i.item_name,
    i.item_type,
    i.source_sheet,
    m.cost
FROM 
    Vendors v
JOIN 
    ItemVendorMap m ON v.vendor_id = m.vendor_id
JOIN 
    Items i ON m.item_id = i.item_id
WHERE 
    i.item_name = 'Item Name'  -- Replace with your item name
ORDER BY 
    v.vendor_name;
```

### Find Items for a Vendor
```sql
SELECT 
    i.item_id,
    i.item_name,
    i.item_type,
    i.source_sheet,
    i.sku,
    i.barcode,
    i.height,
    i.width,
    i.thickness,
    m.cost
FROM 
    Items i
JOIN 
    ItemVendorMap m ON i.item_id = m.item_id
JOIN 
    Vendors v ON m.vendor_id = v.vendor_id
WHERE 
    v.vendor_name = 'Vendor Name'  -- Replace with your vendor name
ORDER BY 
    i.item_name;
```

### Find Unmapped Items
```sql
SELECT 
    i.item_id,
    i.item_name,
    i.item_type,
    i.source_sheet
FROM 
    Items i
LEFT JOIN 
    ItemVendorMap m ON i.item_id = m.item_id
WHERE 
    m.map_id IS NULL
ORDER BY 
    i.item_type, i.item_name;
```

### Find Items with Multiple Vendors
```sql
SELECT 
    i.item_id,
    i.item_name,
    i.item_type,
    COUNT(DISTINCT m.vendor_id) as vendor_count
FROM 
    Items i
JOIN 
    ItemVendorMap m ON i.item_id = m.item_id
GROUP BY 
    i.item_id, i.item_name, i.item_type
HAVING 
    COUNT(DISTINCT m.vendor_id) > 1
ORDER BY 
    vendor_count DESC, i.item_name;
```

### Find Duplicate Mappings
```sql
SELECT 
    i.item_name,
    v.vendor_name,
    COUNT(*) as mapping_count
FROM 
    ItemVendorMap m
JOIN 
    Items i ON m.item_id = i.item_id
JOIN 
    Vendors v ON m.vendor_id = v.vendor_id
GROUP BY 
    i.item_name, v.vendor_name
HAVING 
    COUNT(*) > 1;
```

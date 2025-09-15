# Data Import Guide for SDGNY Vendor Management System

This guide explains how to import your Excel data into the SQL Server database.

## Prerequisites

1. SQL Server database is set up with the required tables (Vendors, Items, ItemVendorMap)
2. Python environment is set up with required packages installed
3. Excel file with three sheets: Final_Vendor_List, BoxHero_Items, and Raw_Materials_Items

## Excel File Format Requirements

Your Excel file should have the following structure:

### Final_Vendor_List Sheet
- **Vendor**: Name of the vendor (required)
- **Contact Name**: Contact person's name (optional)
- **Vendor Email**: Email address (optional)
- **Vendor Phone**: Phone number (optional)

### BoxHero_Items Sheet
- **Item Name**: Name of the item (required)
- **Item Type**: Type/category of the item (required)
- **Vendor**: Name of the vendor (should match a name in the Vendors sheet)
- **Cost**: Cost of the item (numeric, optional)
- **SKU**: Stock keeping unit (optional)
- **Barcode**: Barcode value (optional)

### Raw_Materials_Items Sheet
- **Item Name**: Name of the item (required)
- **Item Type**: Type/category of the item (required)
- **Vendor**: Name of the vendor (should match a name in the Vendors sheet)
- **Cost**: Cost of the item (numeric, optional)
- **Height**: Height dimension (numeric, optional)
- **Width**: Width dimension (numeric, optional)
- **Thickness**: Thickness dimension (numeric, optional)

## Import Process

1. Make sure your `.env` file is set up with the correct database connection details
2. Run the import script:
   ```
   python import_data.py
   ```
3. When prompted, enter the full path to your Excel file
4. The script will import data in this order:
   - Vendors from the Final_Vendor_List sheet
   - Items from the BoxHero_Items sheet and link them to vendors
   - Items from the Raw_Materials_Items sheet and link them to vendors

## Troubleshooting

### Common Issues

1. **Connection Error**: Make sure your SQL Server is running and the connection details in the `.env` file are correct.

2. **Missing Data**: If some items or vendors are not imported, check for:
   - Missing required fields (item name, item type, vendor name)
   - Duplicate entries that violate unique constraints
   - Special characters that might cause SQL errors

3. **Item-Vendor Mapping Failures**: This usually happens when:
   - The vendor name in the items sheet doesn't exactly match any vendor in the vendors sheet
   - The item couldn't be inserted due to a constraint violation

### Checking the Results

After import, you can verify the data in SQL Server Management Studio with these queries:

```sql
-- Check imported vendors
SELECT * FROM Vendors;

-- Check imported items
SELECT * FROM Items;

-- Check item-vendor mappings
SELECT i.item_name, i.item_type, v.vendor_name, m.cost
FROM ItemVendorMap m
JOIN Items i ON m.item_id = i.item_id
JOIN Vendors v ON m.vendor_id = v.vendor_id;
```

## Manual Data Entry

If you prefer to enter data manually or need to add individual records:

### Adding a Vendor
```sql
INSERT INTO Vendors (vendor_name, contact_name, vendor_email, vendor_phone)
VALUES ('Vendor Name', 'Contact Person', 'email@example.com', '123-456-7890');
```

### Adding an Item
```sql
INSERT INTO Items (item_name, item_type, source_sheet, sku, barcode, height, width, thickness)
VALUES ('Item Name', 'Item Type', 'Source', 'SKU123', 'BARCODE123', 10.5, 20.5, 1.5);
```

### Linking an Item to a Vendor
```sql
-- First, get the IDs
DECLARE @item_id INT = (SELECT item_id FROM Items WHERE item_name = 'Item Name');
DECLARE @vendor_id INT = (SELECT vendor_id FROM Vendors WHERE vendor_name = 'Vendor Name');

-- Then create the link
INSERT INTO ItemVendorMap (item_id, vendor_id, cost)
VALUES (@item_id, @vendor_id, 123.45);
```

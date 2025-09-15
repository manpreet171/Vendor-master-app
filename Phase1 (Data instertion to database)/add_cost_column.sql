-- SQL Script to add cost column to Items table
-- This script safely adds the cost column if it doesn't already exist

-- Check if cost column exists
IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE Name = 'cost' AND Object_ID = Object_ID('Items')
)
BEGIN
    -- Add cost column to Items table
    ALTER TABLE Items ADD cost decimal(10,2) NULL;
    PRINT 'Cost column added to Items table.';
    
    -- Update existing items with cost from ItemVendorMap
    -- This will set the cost for each item based on its first vendor mapping
    -- Note: This is just a starting point, as we're now treating items with different costs as separate items
    UPDATE i
    SET i.cost = m.cost
    FROM Items i
    JOIN ItemVendorMap m ON i.item_id = m.item_id
    WHERE i.cost IS NULL;
    
    PRINT 'Updated existing items with cost values from vendor mappings.';
    
    -- Show items with NULL cost (if any)
    SELECT item_id, item_name, item_type, source_sheet
    FROM Items
    WHERE cost IS NULL;
END
ELSE
BEGIN
    PRINT 'Cost column already exists in Items table.';
END

-- Show sample of items with their costs
SELECT TOP 20 item_id, item_name, item_type, cost
FROM Items
ORDER BY item_name;

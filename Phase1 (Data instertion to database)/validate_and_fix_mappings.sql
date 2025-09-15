-- SDGNY Vendor Management System - Validation and Fix Script
-- This script validates item-vendor mappings and fixes any issues

-- Make sure we're using the correct database
USE [dw-sqldb];
GO

-- Part 1: Validation Queries

-- 1. Check for items without any vendor mappings
PRINT 'Items without vendor mappings:';
SELECT i.item_id, i.item_name, i.item_type, i.source_sheet
FROM Items i
LEFT JOIN ItemVendorMap m ON i.item_id = m.item_id
WHERE m.map_id IS NULL;

-- 2. Check for duplicate mappings (same item-vendor pair)
PRINT 'Duplicate item-vendor mappings:';
SELECT item_id, vendor_id, COUNT(*) as duplicate_count
FROM ItemVendorMap
GROUP BY item_id, vendor_id
HAVING COUNT(*) > 1;

-- 3. Summary counts
PRINT 'Database summary counts:';
SELECT 'Items' as table_name, COUNT(*) as record_count FROM Items
UNION
SELECT 'Vendors' as table_name, COUNT(*) as record_count FROM Vendors
UNION
SELECT 'ItemVendorMap' as table_name, COUNT(*) as record_count FROM ItemVendorMap;

-- 4. Vendor counts per item
PRINT 'Items with only one vendor:';
SELECT i.item_id, i.item_name, COUNT(DISTINCT m.vendor_id) as vendor_count
FROM Items i
JOIN ItemVendorMap m ON i.item_id = m.item_id
GROUP BY i.item_id, i.item_name
HAVING COUNT(DISTINCT m.vendor_id) = 1
ORDER BY i.item_name;

-- 5. Check specific item-vendor mappings that should exist
-- Example: Check if "Adhesive - Loctite AA H8003" has both "Assemblyonics" and "Home Depot" as vendors
PRINT 'Checking specific item-vendor mappings:';
SELECT i.item_name, v.vendor_name, m.cost
FROM Items i
JOIN ItemVendorMap m ON i.item_id = m.item_id
JOIN Vendors v ON m.vendor_id = v.vendor_id
WHERE i.item_name = 'Adhesive - Loctite AA H8003'
ORDER BY v.vendor_name;

-- Part 2: Fix Missing Mappings

-- Create a temporary table to store expected mappings
CREATE TABLE #ExpectedMappings (
    item_name NVARCHAR(255),
    vendor_name NVARCHAR(255),
    cost DECIMAL(10, 2)
);

-- Insert expected mappings that might be missing
INSERT INTO #ExpectedMappings (item_name, vendor_name, cost)
VALUES
-- Add known mappings that should exist
('Adhesive - Loctite AA H8003', 'Home Depot', 80.00),
('Adhesive - Loctite AA H8003', 'Assemblyonics', 80.00);
-- Add more expected mappings here as needed

-- Find and fix missing mappings
PRINT 'Fixing missing mappings:';
DECLARE @item_id INT;
DECLARE @vendor_id INT;
DECLARE @item_name NVARCHAR(255);
DECLARE @vendor_name NVARCHAR(255);
DECLARE @cost DECIMAL(10, 2);

-- Create a cursor to iterate through expected mappings
DECLARE mapping_cursor CURSOR FOR
SELECT e.item_name, e.vendor_name, e.cost
FROM #ExpectedMappings e
LEFT JOIN Items i ON i.item_name = e.item_name
LEFT JOIN Vendors v ON v.vendor_name = e.vendor_name
LEFT JOIN ItemVendorMap m ON m.item_id = i.item_id AND m.vendor_id = v.vendor_id
WHERE i.item_id IS NOT NULL AND v.vendor_id IS NOT NULL AND m.map_id IS NULL;

OPEN mapping_cursor;
FETCH NEXT FROM mapping_cursor INTO @item_name, @vendor_name, @cost;

WHILE @@FETCH_STATUS = 0
BEGIN
    -- Get IDs for the item and vendor
    SELECT @item_id = item_id FROM Items WHERE item_name = @item_name;
    SELECT @vendor_id = vendor_id FROM Vendors WHERE vendor_name = @vendor_name;
    
    -- Insert the missing mapping
    IF @item_id IS NOT NULL AND @vendor_id IS NOT NULL
    BEGIN
        INSERT INTO ItemVendorMap (item_id, vendor_id, cost)
        VALUES (@item_id, @vendor_id, @cost);
        
        PRINT 'Added mapping: ' + @item_name + ' - ' + @vendor_name + ' ($' + CAST(@cost AS NVARCHAR) + ')';
    END
    
    FETCH NEXT FROM mapping_cursor INTO @item_name, @vendor_name, @cost;
END

CLOSE mapping_cursor;
DEALLOCATE mapping_cursor;

-- Clean up
DROP TABLE #ExpectedMappings;

-- Verify fixes
PRINT 'Verifying fixes:';
SELECT i.item_name, v.vendor_name, m.cost
FROM Items i
JOIN ItemVendorMap m ON i.item_id = m.item_id
JOIN Vendors v ON m.vendor_id = v.vendor_id
WHERE i.item_name = 'Adhesive - Loctite AA H8003'
ORDER BY v.vendor_name;

-- Part 3: Additional Validation for All Items

-- Check for items that should have multiple vendors but only have one
PRINT 'Items that might need additional vendors:';
SELECT i.item_name, i.item_type, COUNT(DISTINCT m.vendor_id) as vendor_count
FROM Items i
JOIN ItemVendorMap m ON i.item_id = m.item_id
GROUP BY i.item_name, i.item_type
HAVING COUNT(DISTINCT m.vendor_id) = 1
ORDER BY i.item_type, i.item_name;

-- Show vendor distribution
PRINT 'Vendor distribution:';
SELECT v.vendor_name, COUNT(DISTINCT m.item_id) as item_count
FROM Vendors v
JOIN ItemVendorMap m ON v.vendor_id = m.vendor_id
GROUP BY v.vendor_name
ORDER BY item_count DESC;

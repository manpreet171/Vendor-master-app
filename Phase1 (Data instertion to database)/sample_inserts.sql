-- SDGNY Vendor Management System - Sample Insert Statements
-- Use these as templates for manual data entry

-- First make sure we're using the correct database
USE sdgny_vendor_management;
GO

-- =============================================
-- VENDOR INSERTS
-- =============================================

-- Example 1: Insert vendor with all details
INSERT INTO Vendors (vendor_name, contact_name, vendor_email, vendor_phone)
VALUES ('AJ Visual', 'John Smith', 'john@ajvisual.com', '555-123-4567');

-- Example 2: Insert vendor with only required fields
INSERT INTO Vendors (vendor_name)
VALUES ('Canal Plastics Center');

-- Example 3: Insert multiple vendors at once
INSERT INTO Vendors (vendor_name, contact_name, vendor_email, vendor_phone)
VALUES 
('Albert Kemperle', 'Robert Commisso', 'Robert.Commisso@kemperle.com', '(800) 236-0112'),
('All American Print Supply', 'ORDER ONLINE - WEBSITE', 'purchasing@sdgny.com', '(714) 576-2900'),
('Allendale Machinery Systems', 'Judy Shepard', 'tooling@allendalemachinery.com', '201 327 5215');

-- =============================================
-- BOXHERO ITEM INSERTS
-- =============================================

-- Example 1: Insert BoxHero item with all details
INSERT INTO Items (item_name, item_type, source_sheet, sku, barcode)
VALUES ('Acrylic Primer - Gray 6401', 'Paint', 'BoxHero', 'SKU-7NZHZJHN', '845505000144');

-- Example 2: Insert BoxHero item with only required fields
INSERT INTO Items (item_name, item_type, source_sheet)
VALUES ('Adhesive - Loctite AA H8003', 'Adhesive', 'BoxHero');

-- Example 3: Insert multiple BoxHero items at once
INSERT INTO Items (item_name, item_type, source_sheet, sku, barcode)
VALUES 
('Application Fluid - Action Tac, 1 Gallon', 'Consumable', 'BoxHero', 'SKU-N7DQKCLY', '207177558902'),
('Application Tape - Spectrum High Tack, 48" x 300'' (Transfer Tape)', 'Adhesive', 'BoxHero', 'SKU-GC97UY2M', '501734'),
('Axis Lube Oil - Haas, 1 Gallon (P/N 93-3584)', 'HAAS', 'BoxHero', 'HAAS', 'P/N 93-3584');

-- =============================================
-- RAW MATERIALS ITEM INSERTS
-- =============================================

-- Example 1: Insert Raw Materials item with all details
INSERT INTO Items (item_name, item_type, source_sheet, height, width, thickness)
VALUES ('JJ3C GLOSS WHITE', 'Print Media', 'Raw Materials', 60, 1800, NULL);

-- Example 2: Insert Raw Materials item with only required fields
INSERT INTO Items (item_name, item_type, source_sheet)
VALUES ('ACRYLITE Non-glare P99', 'Acrylic', 'Raw Materials');

-- Example 3: Insert multiple Raw Materials items at once
INSERT INTO Items (item_name, item_type, source_sheet, height, width, thickness)
VALUES 
('Black Acrylic', 'Acrylic', 'Raw Materials', 48, 96, 0.125),
('Clear Acrylic', 'Acrylic', 'Raw Materials', 48, 96, 0.25),
('White Acrylic', 'Acrylic', 'Raw Materials', 48, 96, 0.25);

-- =============================================
-- ITEM-VENDOR MAPPING INSERTS
-- =============================================

-- First, get the IDs of the items and vendors you want to link
-- You'll need to replace these with actual queries to get the correct IDs

-- Example 1: Link an item to a vendor with cost
DECLARE @item_id1 INT = (SELECT item_id FROM Items WHERE item_name = 'Acrylic Primer - Gray 6401' AND source_sheet = 'BoxHero');
DECLARE @vendor_id1 INT = (SELECT vendor_id FROM Vendors WHERE vendor_name = 'Master NY');

IF @item_id1 IS NOT NULL AND @vendor_id1 IS NOT NULL
BEGIN
    INSERT INTO ItemVendorMap (item_id, vendor_id, cost)
    VALUES (@item_id1, @vendor_id1, 22.00);
END
ELSE
BEGIN
    PRINT 'Could not find item or vendor for mapping';
END

-- Example 2: Link multiple items to vendors
-- For Adhesive - Loctite AA H8003 to Assemblyonics
DECLARE @item_id2 INT = (SELECT item_id FROM Items WHERE item_name = 'Adhesive - Loctite AA H8003' AND source_sheet = 'BoxHero');
DECLARE @vendor_id2 INT = (SELECT vendor_id FROM Vendors WHERE vendor_name = 'Assemblyonics');

IF @item_id2 IS NOT NULL AND @vendor_id2 IS NOT NULL
BEGIN
    INSERT INTO ItemVendorMap (item_id, vendor_id, cost)
    VALUES (@item_id2, @vendor_id2, 80.00);
END

-- For Black Acrylic to Canal Plastics Center
DECLARE @item_id3 INT = (SELECT item_id FROM Items WHERE item_name = 'Black Acrylic' AND source_sheet = 'Raw Materials');
DECLARE @vendor_id3 INT = (SELECT vendor_id FROM Vendors WHERE vendor_name = 'Canal Plastics Center');

IF @item_id3 IS NOT NULL AND @vendor_id3 IS NOT NULL
BEGIN
    INSERT INTO ItemVendorMap (item_id, vendor_id, cost)
    VALUES (@item_id3, @vendor_id3, 62.00);
END

-- =============================================
-- VERIFICATION QUERIES
-- =============================================

-- Check all vendors
SELECT * FROM Vendors ORDER BY vendor_name;

-- Check all items
SELECT * FROM Items ORDER BY source_sheet, item_name;

-- Check all item-vendor mappings with details
SELECT 
    i.item_name,
    i.item_type,
    v.vendor_name,
    m.cost
FROM ItemVendorMap m
JOIN Items i ON m.item_id = i.item_id
JOIN Vendors v ON m.vendor_id = v.vendor_id
ORDER BY i.item_name, v.vendor_name;

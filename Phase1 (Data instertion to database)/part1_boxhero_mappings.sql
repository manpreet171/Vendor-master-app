-- SDGNY Vendor Management System - BoxHero Item-Vendor Mappings (Part 1)
-- This script creates the relationships between items and vendors with costs

-- Make sure we're using the correct database
USE [dw-sqldb];
GO

-- Helper procedure to insert item-vendor mappings
-- This handles the lookup of item_id and vendor_id based on names
IF OBJECT_ID('dbo.InsertItemVendorMapping', 'P') IS NOT NULL
    DROP PROCEDURE dbo.InsertItemVendorMapping;
GO

CREATE PROCEDURE dbo.InsertItemVendorMapping
    @item_name NVARCHAR(255),
    @item_type NVARCHAR(100),
    @source_sheet NVARCHAR(50),
    @vendor_name NVARCHAR(255),
    @cost DECIMAL(10, 2)
AS
BEGIN
    DECLARE @item_id INT;
    DECLARE @vendor_id INT;
    
    -- Get the item_id
    SELECT @item_id = item_id 
    FROM Items 
    WHERE item_name = @item_name 
      AND item_type = @item_type 
      AND source_sheet = @source_sheet;
    
    -- Get the vendor_id
    SELECT @vendor_id = vendor_id 
    FROM Vendors 
    WHERE vendor_name = @vendor_name;
    
    -- If both IDs are found, insert the mapping
    IF @item_id IS NOT NULL AND @vendor_id IS NOT NULL
    BEGIN
        -- Check if mapping already exists
        IF NOT EXISTS (SELECT 1 FROM ItemVendorMap WHERE item_id = @item_id AND vendor_id = @vendor_id)
        BEGIN
            INSERT INTO ItemVendorMap (item_id, vendor_id, cost)
            VALUES (@item_id, @vendor_id, @cost);
            
            PRINT 'Inserted mapping for ' + @item_name + ' and ' + @vendor_name;
        END
        ELSE
        BEGIN
            PRINT 'Mapping already exists for ' + @item_name + ' and ' + @vendor_name;
        END
    END
    ELSE
    BEGIN
        PRINT 'Could not find item_id or vendor_id for ' + @item_name + ' and ' + @vendor_name;
    END
END
GO

-- Insert BoxHero item-vendor mappings (Part 1)
EXEC dbo.InsertItemVendorMapping 'Acrylic Primer - Gray 6401', 'Paint', 'BoxHero', 'Master NY', 22.00;
EXEC dbo.InsertItemVendorMapping 'Adhesive - Loctite AA H8003', 'Adhesive', 'BoxHero', 'Assemblyonics', 80.00;
EXEC dbo.InsertItemVendorMapping 'Adhesive - Loctite AA H8003', 'Adhesive', 'BoxHero', 'Home Depot', 80.00;
EXEC dbo.InsertItemVendorMapping 'Adhesive Transfer Tape - 3M 9472LE, 12" x 60yds, Applique Use', 'Adhesive', 'BoxHero', 'Tape Systems, Inc', 495.95;
EXEC dbo.InsertItemVendorMapping 'Adhesive Transfer Tape - 3M 9472LE, 12" x 60yds, Applique Use', 'Adhesive', 'BoxHero', 'Tape-Rite Company, INC.', 495.95;
EXEC dbo.InsertItemVendorMapping 'Adhesive Transfer Tape - 3M 9472LE, 12" x 60yds, Applique Use', 'Adhesive', 'BoxHero', 'S & F Supplies Inc.', 495.95;
EXEC dbo.InsertItemVendorMapping 'Application Fluid - Action Tac, 1 Gallon', 'Consumable', 'BoxHero', 'Glantz', 37.94;
EXEC dbo.InsertItemVendorMapping 'Application Fluid - Action Tac, 1 Gallon', 'Consumable', 'BoxHero', 'S & F Supplies Inc.', 37.94;
EXEC dbo.InsertItemVendorMapping 'Application Fluid - Action Tac, 1 Gallon', 'Consumable', 'BoxHero', 'Southern Sign Supply', 37.94;
EXEC dbo.InsertItemVendorMapping 'Application Tape - Spectrum High Tack, 48" x 300'' (Transfer Tape)', 'Adhesive', 'BoxHero', 'S & F Supplies Inc.', 254.35;
EXEC dbo.InsertItemVendorMapping 'Application Tape - Spectrum High Tack, 48" x 300'' (Transfer Tape)', 'Adhesive', 'BoxHero', 'Tape-Rite Company, INC.', 254.35;
EXEC dbo.InsertItemVendorMapping 'Application Tape - Spectrum High Tack, 48" x 300'' (Transfer Tape)', 'Adhesive', 'BoxHero', 'Tape Systems, Inc', 254.35;
EXEC dbo.InsertItemVendorMapping 'Axis Lube Oil - Haas, 1 Gallon (P/N 93-3584)', 'HAAS', 'BoxHero', 'Black Hawk Industrial', 124.95;
EXEC dbo.InsertItemVendorMapping 'Axis Lube Oil - Haas, 1 Gallon (P/N 93-3584)', 'HAAS', 'BoxHero', 'Haas', 124.95;
EXEC dbo.InsertItemVendorMapping 'Axis Lube Oil - Haas, 1 Gallon (P/N 93-3584)', 'HAAS', 'BoxHero', 'Allendale Machinery Systems', 124.95;
EXEC dbo.InsertItemVendorMapping 'Blank Bicycle Rateboards, 22" x 22"', 'SDG', 'BoxHero', 'SDGNY', 0.00;
EXEC dbo.InsertItemVendorMapping 'Blank Overhead Sign, 16" x 96"', 'SDG', 'BoxHero', 'SDGNY', 0.00;
EXEC dbo.InsertItemVendorMapping 'Blue Tape - 3M 2090, 2"', 'Adhesive', 'BoxHero', 'S & F Supplies Inc.', 6.90;
EXEC dbo.InsertItemVendorMapping 'Blue Tape - 3M 2090, 2"', 'Adhesive', 'BoxHero', 'Tape Systems, Inc', 6.90;
EXEC dbo.InsertItemVendorMapping 'Blue Tape - 3M 2090, 2"', 'Adhesive', 'BoxHero', 'Tape-Rite Company, INC.', 6.90;
EXEC dbo.InsertItemVendorMapping 'Buffers for Overhead, 6" x 96"', 'SDG', 'BoxHero', 'SDGNY', 0.00;
EXEC dbo.InsertItemVendorMapping 'Coolant - Cutting & Grinding Fluid', 'HAAS', 'BoxHero', 'Allendale Machinery Systems', 182.00;
EXEC dbo.InsertItemVendorMapping 'Coolant - Cutting & Grinding Fluid', 'HAAS', 'BoxHero', 'Grainger Industrial Supply', 182.00;
EXEC dbo.InsertItemVendorMapping 'DCP Ink - Black', 'DCP', 'BoxHero', 'Johnson Plastics', 250.00;
EXEC dbo.InsertItemVendorMapping 'DCP Ink - Black', 'DCP', 'BoxHero', 'Direct Color System', 250.00;
EXEC dbo.InsertItemVendorMapping 'DCP Ink - Clear', 'DCP', 'BoxHero', 'Johnson Plastics', 262.50;
EXEC dbo.InsertItemVendorMapping 'DCP Ink - Clear', 'DCP', 'BoxHero', 'Direct Color System', 262.50;
EXEC dbo.InsertItemVendorMapping 'DCP Ink - Cyan', 'DCP', 'BoxHero', 'Johnson Plastics', 250.00;
EXEC dbo.InsertItemVendorMapping 'DCP Ink - Cyan', 'DCP', 'BoxHero', 'Direct Color System', 250.00;
EXEC dbo.InsertItemVendorMapping 'DCP Ink - Magenta', 'DCP', 'BoxHero', 'Johnson Plastics', 250.00;
EXEC dbo.InsertItemVendorMapping 'DCP Ink - Magenta', 'DCP', 'BoxHero', 'Direct Color System', 250.00;
EXEC dbo.InsertItemVendorMapping 'DCP Ink - White', 'DCP', 'BoxHero', 'Johnson Plastics', 250.00;
EXEC dbo.InsertItemVendorMapping 'DCP Ink - White', 'DCP', 'BoxHero', 'Direct Color System', 250.00;
EXEC dbo.InsertItemVendorMapping 'DCP Ink - Yellow', 'DCP', 'BoxHero', 'Johnson Plastics', 250.00;
EXEC dbo.InsertItemVendorMapping 'DCP Ink - Yellow', 'DCP', 'BoxHero', 'Direct Color System', 250.00;
EXEC dbo.InsertItemVendorMapping 'DCP Primer - Marabu P5, 1L', 'DCP', 'BoxHero', 'Digital Print Supplies', 200.94;
EXEC dbo.InsertItemVendorMapping 'DCP Primer - Marabu P5, 1L', 'DCP', 'BoxHero', 'Southern Sign Supply', 200.94;
EXEC dbo.InsertItemVendorMapping 'DCP Primer - Marabu P5, 1L', 'DCP', 'BoxHero', 'All American Print Supply', 200.94;
EXEC dbo.InsertItemVendorMapping 'Denatured Alcohol - Crown, 1 Gallon', 'Consumable', 'BoxHero', 'S & F Supplies Inc.', 17.73;
EXEC dbo.InsertItemVendorMapping 'Dish Soap - Palmolive ', 'Consumable', 'BoxHero', 'Amazon', 30.00;
EXEC dbo.InsertItemVendorMapping 'Double Sided Tape - 3M Scotch, 1/2" x 250"', 'Adhesive', 'BoxHero', 'Tape Systems, Inc', 3.16;
EXEC dbo.InsertItemVendorMapping 'Double Sided Tape - 3M Scotch, 1/2" x 250"', 'Adhesive', 'BoxHero', 'R.S Hughes', 3.16;
EXEC dbo.InsertItemVendorMapping 'Double Sided Tape - 3M Scotch, 1/2" x 250"', 'Adhesive', 'BoxHero', 'Tape-Rite Company, INC.', 3.16;
EXEC dbo.InsertItemVendorMapping 'Drill Bit - Cobalt, 1/8"', 'Hardware', 'BoxHero', 'Mutual Screw & Supply', 2.29;
EXEC dbo.InsertItemVendorMapping 'Drill Bit - Cobalt, 1/8"', 'Hardware', 'BoxHero', 'McMASTER-CARR', 2.29;
EXEC dbo.InsertItemVendorMapping 'Drill Bit - Cobalt, 1/8"', 'Hardware', 'BoxHero', 'Tanner Bolt & Nut', 2.29;
EXEC dbo.InsertItemVendorMapping 'Drill Bit - Masonry, 1/8"', 'Hardware', 'BoxHero', 'Tanner Bolt & Nut', 5.80;
EXEC dbo.InsertItemVendorMapping 'Drill Bit - Masonry, 1/8"', 'Hardware', 'BoxHero', 'McMASTER-CARR', 5.80;
EXEC dbo.InsertItemVendorMapping 'Drill Bit - Masonry, 1/8"', 'Hardware', 'BoxHero', 'Grainger Industrial Supply', 5.80;
EXEC dbo.InsertItemVendorMapping 'Drill Bit - Masonry, 3/16"', 'Hardware', 'BoxHero', 'Grainger Industrial Supply', 11.02;
EXEC dbo.InsertItemVendorMapping 'Drill Bit - Masonry, 3/16"', 'Hardware', 'BoxHero', 'Tanner Bolt & Nut', 11.02;
EXEC dbo.InsertItemVendorMapping 'Drill Bit - Masonry, 3/16"', 'Hardware', 'BoxHero', 'McMASTER-CARR', 11.02;
EXEC dbo.InsertItemVendorMapping 'End Mill - 1/32" SE, 3-Flute, TC10802, 1/8" LOC, 1-1/2" OAL, Micrograin', 'HAAS', 'BoxHero', 'Grainger Industrial Supply', 10.26;
EXEC dbo.InsertItemVendorMapping 'End Mill - 1/32" SE, 3-Flute, TC10802, 1/8" LOC, 1-1/2" OAL, Micrograin', 'HAAS', 'BoxHero', 'Tools Today', 10.26;
EXEC dbo.InsertItemVendorMapping 'End Mill - 1/32" SE, 3-Flute, TC10802, 1/8" LOC, 1-1/2" OAL, Micrograin', 'HAAS', 'BoxHero', 'Allendale Machinery Systems', 10.26;
EXEC dbo.InsertItemVendorMapping 'End Mill - HAAS, 3-Flute, 1/16" Dia, Alum-Mill', 'HAAS', 'BoxHero', 'Grainger Industrial Supply', 10.95;
EXEC dbo.InsertItemVendorMapping 'End Mill - HAAS, 3-Flute, 1/16" Dia, Alum-Mill', 'HAAS', 'BoxHero', 'Allendale Machinery Systems', 10.95;
EXEC dbo.InsertItemVendorMapping 'End Mill - HAAS, 3-Flute, 1/16" Dia, Alum-Mill', 'HAAS', 'BoxHero', 'Tools Today', 10.95;
EXEC dbo.InsertItemVendorMapping 'End Mill - HAAS, 3-Flute, 1/4" Dia, Alum-Mill', 'HAAS', 'BoxHero', 'Grainger Industrial Supply', 13.95;
EXEC dbo.InsertItemVendorMapping 'End Mill - HAAS, 3-Flute, 1/4" Dia, Alum-Mill', 'HAAS', 'BoxHero', 'Tools Today', 13.95;
EXEC dbo.InsertItemVendorMapping 'End Mill - HAAS, 3-Flute, 1/4" Dia, Alum-Mill', 'HAAS', 'BoxHero', 'Allendale Machinery Systems', 13.95;
EXEC dbo.InsertItemVendorMapping 'End Mill - HAAS, 3-Flute, 1/8" Dia, High-Perf Alum, w/ 0.015" Radius', 'HAAS', 'BoxHero', 'Allendale Machinery Systems', 11.95;
EXEC dbo.InsertItemVendorMapping 'End Mill - HAAS, 3-Flute, 1/8" Dia, High-Perf Alum, w/ 0.015" Radius', 'HAAS', 'BoxHero', 'Grainger Industrial Supply', 11.95;
EXEC dbo.InsertItemVendorMapping 'End Mill - HAAS, 3-Flute, 1/8" Dia, High-Perf Alum, w/ 0.015" Radius', 'HAAS', 'BoxHero', 'Tools Today', 11.95;
EXEC dbo.InsertItemVendorMapping 'End Mill - HAAS, 3-Flute, 3/8" Dia, Alum Mill', 'HAAS', 'BoxHero', 'Allendale Machinery Systems', 11.95;
EXEC dbo.InsertItemVendorMapping 'End Mill - HAAS, 3-Flute, 3/8" Dia, Alum Mill', 'HAAS', 'BoxHero', 'Grainger Industrial Supply', 11.95;
EXEC dbo.InsertItemVendorMapping 'End Mill - HAAS, 3-Flute, 3/8" Dia, Alum Mill', 'HAAS', 'BoxHero', 'Tools Today', 11.95;
EXEC dbo.InsertItemVendorMapping 'End Mill - HAAS, 4-Flute, 3/4" Dia, W/Flat (03-0064)', 'HAAS', 'BoxHero', 'Grainger Industrial Supply', 0.00;
EXEC dbo.InsertItemVendorMapping 'End Mill - HAAS, 4-Flute, 3/4" Dia, W/Flat (03-0064)', 'HAAS', 'BoxHero', 'Tools Today', 0.00;
EXEC dbo.InsertItemVendorMapping 'End Mill - HAAS, 4-Flute, 3/4" Dia, W/Flat (03-0064)', 'HAAS', 'BoxHero', 'Allendale Machinery Systems', 0.00;
EXEC dbo.InsertItemVendorMapping 'Foam Tape - 3M 4056, 1/2" x 36yds, Black', 'Adhesive', 'BoxHero', 'Tape Systems, Inc', 65.00;
EXEC dbo.InsertItemVendorMapping 'Foam Tape - 3M 4056, 1/2" x 36yds, Black', 'Adhesive', 'BoxHero', 'Tape-Rite Company, INC.', 65.00;
EXEC dbo.InsertItemVendorMapping 'Foam Tape - 3M 4056, 1/2" x 36yds, Black', 'Adhesive', 'BoxHero', 'S & F Supplies Inc.', 65.00;
EXEC dbo.InsertItemVendorMapping 'Foam Tape - D/C Perm, 3/4" x 1/16", 36yds, White', 'Adhesive', 'BoxHero', 'S & F Supplies Inc.', 8.35;
EXEC dbo.InsertItemVendorMapping 'Foam Tape - D/C Perm, 3/4" x 1/16", 36yds, White', 'Adhesive', 'BoxHero', 'Tape Systems, Inc', 8.35;
EXEC dbo.InsertItemVendorMapping 'Foam Tape - D/C Perm, 3/4" x 1/16", 36yds, White', 'Adhesive', 'BoxHero', 'Tape-Rite Company, INC.', 8.35;
EXEC dbo.InsertItemVendorMapping 'Frame Silver Wall 8 1/2 BY 11"', 'Hardware', 'BoxHero', 'Displays2go', 20.99;
EXEC dbo.InsertItemVendorMapping 'Frame Silver Wall 8 1/2 BY 11"', 'Hardware', 'BoxHero', 'Johnson Plastics', 20.99;
EXEC dbo.InsertItemVendorMapping 'Gasket - Pierson SV3, 1/8" x 50''', 'HAAS', 'BoxHero', 'Allendale Machinery Systems', 60.25;
EXEC dbo.InsertItemVendorMapping 'Glass Cleaner - 32 oz. (946 mL)', 'Office Supply', 'BoxHero', 'Amazon', 14.60;
EXEC dbo.InsertItemVendorMapping 'Glass Cleaner - 32 oz. (946 mL)', 'Office Supply', 'BoxHero', 'Uline Shipping Supply', 14.60;
EXEC dbo.InsertItemVendorMapping 'Grease Stick - Hougen Slick-Stik, 16 oz', 'Consumable', 'BoxHero', 'Awisco', 88.60;
EXEC dbo.InsertItemVendorMapping 'Haze Remover - CCI H/C-100, Image Stain Remover', 'Silkscreen', 'BoxHero', 'Grimco', 46.72;

-- Verify the inserts
SELECT COUNT(*) as 'Total BoxHero Item-Vendor Mappings (Part 1)' FROM ItemVendorMap;

-- SDGNY Vendor Management System - BoxHero Items Insert Statements (Part 1)
-- This script inserts unique items from the BoxHero data

-- Make sure we're using the correct database
USE [dw-sqldb];
GO

-- Insert unique items from BoxHero (first 100 items)
-- We're only inserting unique items here, vendor mappings will be in a separate script
INSERT INTO Items (item_name, item_type, source_sheet, sku, barcode, height, width, thickness)
VALUES 
('Acrylic Primer - Gray 6401', 'Paint', 'BoxHero', 'SKU-7NZHZJHN', '845505000144', NULL, NULL, NULL),
('Adhesive - Loctite AA H8003', 'Adhesive', 'BoxHero', 'SKU-DOQCZH04', '79340011908', NULL, NULL, NULL),
('Adhesive Transfer Tape - 3M 9472LE, 12" x 60yds, Applique Use', 'Adhesive', 'BoxHero', 'SKU-0QH2Z85S', '2026019626268', NULL, NULL, NULL),
('Application Fluid - Action Tac, 1 Gallon', 'Consumable', 'BoxHero', 'SKU-N7QDKCLY', '2071775589029', NULL, NULL, NULL),
('Application Tape - Spectrum High Tack, 48" x 300'' (Transfer Tape)', 'Adhesive', 'BoxHero', 'SKU-GC97UY2M', '501734', NULL, NULL, NULL),
('Axis Lube Oil - Haas, 1 Gallon (P/N 93-3584)', 'HAAS', 'BoxHero', 'HAAS', 'P/N 93-3584', NULL, NULL, NULL),
('Blank Bicycle Rateboards, 22" x 22"', 'SDG', 'BoxHero', 'SKU-9U7DBONO', NULL, NULL, NULL, NULL),
('Blank Overhead Sign, 16" x 96"', 'SDG', 'BoxHero', 'SKU-LUZ23H3F', NULL, NULL, NULL, NULL),
('Blue Tape - 3M 2090, 2"', 'Adhesive', 'BoxHero', 'SKU-0J61SB9W', '51115091681', NULL, NULL, NULL),
('Buffers for Overhead, 6" x 96"', 'SDG', 'BoxHero', 'SKU-ZAOE7ABK', NULL, NULL, NULL, NULL),
('Coolant - Cutting & Grinding Fluid', 'HAAS', 'BoxHero', 'SKU-HEOUD67R', '2026259154835', NULL, NULL, NULL),
('DCP Ink - Black', 'DCP', 'BoxHero', 'SKU-X7F93H29', '2033768925337', NULL, NULL, NULL),
('DCP Ink - Clear', 'DCP', 'BoxHero', 'SKU-NEI12BC7', 'I-4820-VA', NULL, NULL, NULL),
('DCP Ink - Cyan', 'DCP', 'BoxHero', 'SKU-6KPW48OX', '2045301520121', NULL, NULL, NULL),
('DCP Ink - Magenta', 'DCP', 'BoxHero', 'SKU-ECEZDY2P', '2048109377973', NULL, NULL, NULL),
('DCP Ink - White', 'DCP', 'BoxHero', 'SKU-RVDCGZ4W', '2015651138536', NULL, NULL, NULL),
('DCP Ink - Yellow', 'DCP', 'BoxHero', 'SKU-1XT46KD9', '2025275297052', NULL, NULL, NULL),
('DCP Primer - Marabu P5, 1L', 'DCP', 'BoxHero', '4.00775E+12', '4007751688323', NULL, NULL, NULL),
('Denatured Alcohol - Crown, 1 Gallon', 'Consumable', 'BoxHero', 'SKU-4G4BLYU4', '76542000938', NULL, NULL, NULL),
('Dish Soap - Palmolive ', 'Consumable', 'BoxHero', 'SKU-DOH6YFSF', '35000444813', NULL, NULL, NULL),
('Double Sided Tape - 3M Scotch, 1/2" x 250"', 'Adhesive', 'BoxHero', 'SKU-ORM5HA0X', '21200010323', NULL, NULL, NULL),
('Drill Bit - Cobalt, 1/8"', 'Hardware', 'BoxHero', 'SKU-HH7UL5FK', '2031808987024', NULL, NULL, NULL),
('Drill Bit - Masonry, 1/8"', 'Hardware', 'BoxHero', 'SKU-UUWKEXIM', '2077604695046', NULL, NULL, NULL),
('Drill Bit - Masonry, 3/16"', 'Hardware', 'BoxHero', 'SKU-HM2MMDMN', '2046437554752', NULL, NULL, NULL),
('End Mill - 1/32" SE, 3-Flute, TC10802, 1/8" LOC, 1-1/2" OAL, Micrograin', 'HAAS', 'BoxHero', 'SKU-46NKH7T5', '2096576527896', NULL, NULL, NULL),
('End Mill - HAAS, 3-Flute, 1/16" Dia, Alum-Mill', 'HAAS', 'BoxHero', 'SKU-JGGQ3KMT', '2006565694218', NULL, NULL, NULL),
('End Mill - HAAS, 3-Flute, 1/4" Dia, Alum-Mill', 'HAAS', 'BoxHero', 'SKU-8X82NTQE', '2032618796370', NULL, NULL, NULL),
('End Mill - HAAS, 3-Flute, 1/8" Dia, High-Perf Alum, w/ 0.015" Radius', 'HAAS', 'BoxHero', 'SKU-3X5RS6AC', '2056088494833', NULL, NULL, NULL),
('End Mill - HAAS, 3-Flute, 3/8" Dia, Alum Mill', 'HAAS', 'BoxHero', 'SKU-34J0S7NS', '03-00BI', NULL, NULL, NULL),
('End Mill - HAAS, 4-Flute, 3/4" Dia, W/Flat (03-0064)', 'HAAS', 'BoxHero', 'SKU-SQFF3T1G', '03-0064', NULL, NULL, NULL),
('Foam Tape - 3M 4056, 1/2" x 36yds, Black', 'Adhesive', 'BoxHero', 'SKU-ZO6XNM4P', '2083845897897', NULL, NULL, NULL),
('Foam Tape - D/C Perm, 3/4" x 1/16", 36yds, White', 'Adhesive', 'BoxHero', 'SKU-9MW4FBYG', '2000470246081', NULL, NULL, NULL),
('Frame Silver Wall 8 1/2 BY 11"', 'Hardware', 'BoxHero', 'SKU-RJ83TAG1', 'WMFS8511SL', NULL, NULL, NULL),
('Gasket - Pierson SV3, 1/8" x 50''', 'HAAS', 'BoxHero', 'SKU-0Q8JHBB8', '2055557374881', NULL, NULL, NULL),
('Glass Cleaner - 32 oz. (946 mL)', 'Office Supply', 'BoxHero', 'SKU-8Z3J0E4P', '2070535805539', NULL, NULL, NULL),
('Grease Stick - Hougen Slick-Stik, 16 oz', 'Consumable', 'BoxHero', 'SKU-NQ6QA6O9', '2035674009149', NULL, NULL, NULL),
('Haze Remover - CCI H/C-100, Image Stain Remover', 'Silkscreen', 'BoxHero', 'SKU-NNNA51S4', '2048975528790', NULL, NULL, NULL),
('Ink Vutek - Black', 'Vutek', 'BoxHero', 'SKU-K1WSKSQ8', '45150938', NULL, NULL, NULL),
('Ink Vutek - Cyan Ink', 'Vutek', 'BoxHero', 'SKU-WWNU8BXK', '45166787', NULL, NULL, NULL),
('Ink Vutek - Jet Wash Station Fluid', 'Vutek', 'BoxHero', 'SKU-TYCOFIBR', ']C1ITNO45247040|BANO2412050149|QTY1000', NULL, NULL, NULL),
('Ink Vutek - Light Black', 'Vutek', 'BoxHero', 'SKU-LUVACK70', '45130508', NULL, NULL, NULL),
('Ink Vutek - Light Cyan', 'Vutek', 'BoxHero', 'SKU-RTBFJYRH', '45127090', NULL, NULL, NULL),
('Ink Vutek - Light Magenta Ink', 'Vutek', 'BoxHero', 'SKU-XVL93W1V', '45133586', NULL, NULL, NULL),
('Ink Vutek - Light Yellow', 'Vutek', 'BoxHero', 'SKU-82VQHWTK', '45130507', NULL, NULL, NULL),
('Ink Vutek - Magenta', 'Vutek', 'BoxHero', 'SKU-JO1POPQ3', '45130503', NULL, NULL, NULL),
('Ink Vutek - White', 'Vutek', 'BoxHero', 'SKU-DCPXM4WO', '45127094', NULL, NULL, NULL),
('Ink Vutek - Yellow', 'Vutek', 'BoxHero', 'SKU-JQ24PIII', '45130504', NULL, NULL, NULL),
('JCD - White 2447 Acrylic Film - 48" x 96"', 'Raw Material', 'BoxHero', 'SKU-8MICK623', '2092624463062', NULL, NULL, NULL),
('L-Key - 1/16" Hex ', 'Hardware', 'BoxHero', 'SKU-WRN49A0D', '2028960591107', NULL, NULL, NULL),
('LED Module - SloanLED SignBOX II', 'LED', 'BoxHero', 'SKU-XMFUQC11', '2020102297984', NULL, NULL, NULL),
('Latex Gloves (L) ', 'Consumable', 'BoxHero', 'SKU-GGCSY2U4', '793770331169', NULL, NULL, NULL),
('Latex Gloves (M)', 'Consumable', 'BoxHero', 'SKU-BDZRU7DD', '2087558332348', NULL, NULL, NULL),
('Luster Overlaminate Film - Briteline, 60" x 150'', 3mil, Shield UV', 'Vinyl', 'BoxHero', 'SKU-Q7BKQOVV', 'OLUV-LST61', NULL, NULL, NULL),
('Masking Tape - IPG #515, 1/2" x 60yds', 'Adhesive', 'BoxHero', 'SKU-H6NWLBLX', '2093232700433', NULL, NULL, NULL),
('Masonry Bit - SDS, 3/16"', 'Hardware', 'BoxHero', 'SKU-PQDV3J3D', '2034752160635', NULL, NULL, NULL),
('Matthews - Clear Primer for Metals, (274793SP)', 'Consumable', 'BoxHero', 'SKU-2Q3MAFCF', '807350007099', NULL, NULL, NULL),
('Matthews - Tie Bond Clear Primer for Plastics (274777SP)', 'Consumable', 'BoxHero', 'SKU-EP23POSM', NULL, NULL, NULL, NULL);

-- Verify the inserts
SELECT COUNT(*) as 'Total BoxHero Items Inserted (Part 1)' FROM Items WHERE source_sheet = 'BoxHero';

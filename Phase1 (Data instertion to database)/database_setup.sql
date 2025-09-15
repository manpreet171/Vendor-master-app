-- SDGNY Vendor Management System Database Setup
-- This script creates the necessary tables for the vendor management system

-- Create database (uncomment if you need to create the database)
-- CREATE DATABASE sdgny_vendor_management;
-- USE sdgny_vendor_management;

-- Table 1: Vendors
CREATE TABLE Vendors (
    vendor_id INT PRIMARY KEY IDENTITY(1,1),
    vendor_name VARCHAR(255) NOT NULL UNIQUE,
    contact_name VARCHAR(255) NULL,
    vendor_email VARCHAR(255) NULL,
    vendor_phone VARCHAR(50) NULL
);

-- Table 2: Items
CREATE TABLE Items (
    item_id INT PRIMARY KEY IDENTITY(1,1),
    item_name VARCHAR(255) NOT NULL,
    item_type VARCHAR(100) NOT NULL,
    source_sheet VARCHAR(50) NOT NULL,
    sku VARCHAR(100) NULL,
    barcode VARCHAR(100) NULL,
    height DECIMAL(10, 4) NULL,
    width DECIMAL(10, 4) NULL,
    thickness DECIMAL(10, 4) NULL,
    -- Add a unique constraint to prevent duplicate items
    CONSTRAINT unique_item UNIQUE (item_name, item_type, sku, height, width, thickness)
);

-- Table 3: ItemVendorMap
CREATE TABLE ItemVendorMap (
    map_id INT PRIMARY KEY IDENTITY(1,1),
    item_id INT NOT NULL,
    vendor_id INT NOT NULL,
    cost DECIMAL(10, 2) NULL,
    FOREIGN KEY (item_id) REFERENCES Items(item_id) ON DELETE CASCADE,
    FOREIGN KEY (vendor_id) REFERENCES Vendors(vendor_id) ON DELETE CASCADE,
    -- Add a unique constraint to prevent duplicate links
    CONSTRAINT unique_map UNIQUE (item_id, vendor_id)
);

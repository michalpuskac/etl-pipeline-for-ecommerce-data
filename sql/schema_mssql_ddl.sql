/*
=============================================================
DDL Script: Create tables
-------------------------------------------------------------
Script Purpose:
    This script create tables for etl schema, dropping
    existing tables if the already exist.
    Run this script to re-define the DDL structure etl schema
=============================================================
*/

-- Create the etl schema if it doesn't exist
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'etl')
BEGIN
    EXEC('CREATE SCHEMA etl');
    PRINT '==================== Schema "etl" created.====================';
END
ELSE
BEGIN
    PRINT '==================== Schema "etl" already exists.====================';
END
GO


-- Drop all foreign key constraints
IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_cartitems_carts' AND parent_object_id = OBJECT_ID('etl.cart_items'))
    ALTER TABLE etl.cart_items DROP CONSTRAINT FK_cartitems_carts;
GO

IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_cartitems_products' AND parent_object_id = OBJECT_ID('etl.cart_items'))
    ALTER TABLE etl.cart_items DROP CONSTRAINT FK_cartitems_products;
GO

IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_carts_users' AND parent_object_id = OBJECT_ID('etl.carts'))
    ALTER TABLE etl.carts DROP CONSTRAINT FK_carts_users;
GO

-- Drop the tables in the correct order (child tables first)
IF OBJECT_ID('etl.cart_items', 'U') IS NOT NULL
    DROP TABLE etl.cart_items;
GO

IF OBJECT_ID('etl.carts', 'U') IS NOT NULL
    DROP TABLE etl.carts;
GO

IF OBJECT_ID('etl.products', 'U') IS NOT NULL
    DROP TABLE etl.products;
GO

IF OBJECT_ID('etl.users', 'U') IS NOT NULL
    DROP TABLE etl.users;
GO

-- Create the tables in order (parent tables first)
CREATE TABLE etl.users(
    user_id INT IDENTITY(1,1) PRIMARY KEY NOT NULL,
    first_name NVARCHAR(50) NOT NULL,
    last_name NVARCHAR(50) NOT NULL,
    email NVARCHAR(255) UNIQUE NOT NULL,
    phone NVARCHAR(255),
    gender NVARCHAR(20),
    age INT,
    birth_date DATE
);
GO

CREATE TABLE etl.products(
    id INT IDENTITY(1,1) PRIMARY KEY NOT NULL,
    title NVARCHAR(100) NOT NULL,
    category NVARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    discount_percentage DECIMAL(10,2),
    rating DECIMAL(10,2),
    stock INT,
    brand NVARCHAR(100),
    nr_of_reviews INT,
    review_comments NVARCHAR(MAX)
);
GO

CREATE TABLE etl.carts(
    cart_id INT IDENTITY(1,1) PRIMARY KEY NOT NULL,
    user_id INT NOT NULL,
    cart_total DECIMAL(10,2) NOT NULL,
    discounted_total DECIMAL(10,2),
    total_products INT,
    total_quantity INT
);
GO

CREATE TABLE etl.cart_items(
    item_id INT IDENTITY(1,1) PRIMARY KEY NOT NULL,  -- Primary key for each item
    cart_id INT NOT NULL,                            -- Foreign key to carts table
    product_id INT NOT NULL,
    title NVARCHAR(100),
    quantity INT,
    price DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2),
    discount_percentage DECIMAL(10,2),
    discounted_price DECIMAL(10,2)
);
GO

-- Now add the foreign key constraints
ALTER TABLE etl.carts
ADD CONSTRAINT FK_carts_users
FOREIGN KEY (user_id)
REFERENCES etl.users(user_id)
ON DELETE CASCADE;
GO

ALTER TABLE etl.cart_items
ADD CONSTRAINT FK_cartitems_carts
FOREIGN KEY (cart_id)
REFERENCES etl.carts(cart_id)
ON DELETE CASCADE;
GO

ALTER TABLE etl.cart_items
ADD CONSTRAINT FK_cartitems_products
FOREIGN KEY (product_id)
REFERENCES etl.products(id)
ON DELETE CASCADE;
GO

PRINT '==================== All tables and constraints created successfully.====================';
GO
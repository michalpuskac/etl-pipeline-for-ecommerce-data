/*
=============================================================
DDL Script: Create tables
-------------------------------------------------------------
Script Purpose:
    This script creates tables for etl schema, dropping
    existing tables if they already exist.
    Run this script to re-define the DDL structure for etl schema
=============================================================
*/

-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS etl;

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS etl.cart_items CASCADE;
DROP TABLE IF EXISTS etl.carts CASCADE;
DROP TABLE IF EXISTS etl.products CASCADE;
DROP TABLE IF EXISTS etl.users CASCADE;

-- Create users table
CREATE TABLE etl.users(
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(255),
    gender VARCHAR(50),
    age INT,
    birth_date DATE
);

-- Create products table
CREATE TABLE etl.products(
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    discount_percentage NUMERIC(10,2),
    rating NUMERIC(10,2),
    stock INT,
    brand VARCHAR(100),
    nr_of_reviews INT,
    review_comments TEXT
);

-- Create carts table
CREATE TABLE etl.carts(
    cart_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    cart_total NUMERIC(10,2) NOT NULL,
    discounted_total NUMERIC(10,2),
    total_products INT,
    total_quantity INT
);

-- Create cart_items table with item_id as the primary key
CREATE TABLE etl.cart_items(
    item_id SERIAL PRIMARY KEY,
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    title VARCHAR(100),
    quantity INT,
    price NUMERIC(10,2) NOT NULL,
    total NUMERIC(10,2),
    discount_percentage NUMERIC(10,2),
    discounted_price NUMERIC(10,2)
);

-- Adding Foreign Key constraints for PostgreSQL
-- In etl.carts table
ALTER TABLE etl.carts
ADD CONSTRAINT FK_carts_users 
FOREIGN KEY (user_id) 
REFERENCES etl.users(user_id)
ON DELETE CASCADE;

-- In etl.cart_items table
ALTER TABLE etl.cart_items
ADD CONSTRAINT FK_cartitems_carts 
FOREIGN KEY (cart_id) 
REFERENCES etl.carts(cart_id)
ON DELETE CASCADE;

ALTER TABLE etl.cart_items
ADD CONSTRAINT FK_cartitems_products 
FOREIGN KEY (product_id) 
REFERENCES etl.products(id)
ON DELETE CASCADE;
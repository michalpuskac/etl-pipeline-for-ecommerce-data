/*
=============================================================
DDL Script: Create tables
-------------------------------------------------------------
Script Purpose:
    This script creates tables for database dropping
    existing tables if they already exist.
    Run this script to re-define the DDL structure for databes
=============================================================
*/

-- Drop tables if they exist (in reverse order of creation due to potential FKs if added later)
DROP TABLE IF EXISTS cart_items;
DROP TABLE IF EXISTS carts;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

-- Create user table

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY, -- INTEGER PRIMARY KEY is auto-incrementing by default in SQLite
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    gender TEXT,
    age INTEGER,
    birth_date TEXT -- Store as 'YYYY-MM-DD'
);

-- Create products table
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL, -- REAL for floating point numbers
    discount_percentage REAL,
    rating REAL,
    stock INTEGER,
    brand TEXT,
    nr_of_reviews INTEGER,
    review_comments TEXT
);

-- Create carts table
CREATE TABLE carts (
    cart_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    cart_total REAL NOT NULL,
    discounted_total REAL,
    total_products INTEGER,
    total_quantity INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Create cart_items table
CREATE TABLE cart_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Explicit AUTOINCREMENT
    cart_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    title TEXT,
    quantity INTEGER,
    price REAL NOT NULL,
    total REAL,
    discount_percentage REAL,
    discounted_price REAL,
    FOREIGN KEY (cart_id) REFERENCES carts(cart_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);
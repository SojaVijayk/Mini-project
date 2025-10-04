-- SQL script to update the book_table ISBN column to accommodate longer ISBNs
USE book_engine;

-- Modify the ISBN column to allow longer values
ALTER TABLE book_table MODIFY COLUMN isbn VARCHAR(50) NOT NULL;
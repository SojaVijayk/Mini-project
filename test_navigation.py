import csv
import os
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL

# Test script to check navigation between recommended books and book description
from flask import url_for
from app import app

# Test URL generation for recommended books and book description
with app.test_request_context():
    # Test recommended books URL
    recommended_url = url_for('recommended_books')
    print(f"Recommended books URL: {recommended_url}")
    
    # Test book description URL with different book IDs
    for book_id in [1, 2, 3, 100, 1000]:
        try:
            book_desc_url = url_for('book_description', book_id=book_id)
            print(f"Book description URL (book_id={book_id}): {book_desc_url}")
        except Exception as e:
            print(f"Error generating URL for book_id={book_id}: {e}")

def read_books_csv(filename):
    """Reads the books_data.csv file and returns a list of book dictionaries."""
    books = []
    try:
        with open(filename, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                # Skip empty rows
                if not row or not row.get('book_title'):
                    continue
                    
                book = {
                    'id': row.get('serial_number', ''),
                    'title': row.get('book_title', ''),
                    'author': row.get('author', ''),
                    'genre': row.get('genre', ''),
                    'isbn': row.get('ISBN', ''),
                    'story_content': row.get('story_content', '')
                }
                books.append(book)
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
    except Exception as e:
        print(f"Error reading books CSV: {e}")
    return books

# Test reading the books CSV
books = read_books_csv('data/books_data.csv')
print(f"Total books in CSV: {len(books)}")

if books:
    # Show first 3 books
    for i, book in enumerate(books[:3]):
        print(f"Book {i+1}:")
        print(f"  ID: {book['id']}")
        print(f"  Title: {book['title']}")
        print(f"  Author: {book['author']}")
        print(f"  Genre: {book['genre']}")
        print(f"  ISBN: {book['isbn']}")
        print()
        
    # Test URL generation for book description
    print("Testing URL generation for book description:")
    for i, book in enumerate(books[:3]):
        book_id = book['id']
        # Simulate Flask url_for function
        url = f"/book_description/{book_id}"
        print(f"  Book {i+1} URL: {url}")
else:
    print("No books found in CSV file")
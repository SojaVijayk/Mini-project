import mysql.connector
import csv
from mysql.connector import Error

# Database configuration - update these values to match your database
config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'book_engine',
    'raise_on_warnings': True
}

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

try:
    # Connect to the database
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    
    # Read books from CSV
    books = read_books_csv('data/books_data.csv')
    
    # Insert books into the database
    inserted_count = 0
    for book in books:
        # Check if book already exists
        check_query = "SELECT book_id FROM book_table WHERE isbn = %s"
        cursor.execute(check_query, (book['isbn'],))
        existing_book = cursor.fetchone()
        
        if not existing_book:
            # Insert new book
            insert_query = """INSERT INTO book_table 
                             (title, author, genre, isbn, story_content) 
                             VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(insert_query, (
                book['title'],
                book['author'],
                book['genre'],
                book['isbn'],
                book['story_content']
            ))
            inserted_count += 1
    
    # Commit the changes
    cnx.commit()
    
    print(f"Successfully inserted {inserted_count} new books from CSV into the database.")
    print(f"Total books processed: {len(books)}")
    
except Error as e:
    print(f"Database error: {e}")
    
except Exception as e:
    print(f"Error: {e}")
    
finally:
    # Close the connection
    if 'cnx' in locals() and cnx.is_connected():
        cursor.close()
        cnx.close()
        print("MySQL connection is closed.")
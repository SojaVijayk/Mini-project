import mysql.connector
from mysql.connector import Error
import requests
import json

# Test the recently rated functionality
base_url = 'http://127.0.0.1:5000'

# First, let's check if we can get recently rated books
try:
    # Test the recently rated API endpoint
    response = requests.get(f'{base_url}/recently_rated', cookies={'session': 'test'})
    print(f"Recently rated endpoint status: {response.status_code}")
    print(f"Recently rated response: {response.json()}")
except Exception as e:
    print(f"Error testing recently rated endpoint: {e}")

# Test the recently rated page
try:
    response = requests.get(f'{base_url}/recently_rated_page')
    print(f"\nRecently rated page status: {response.status_code}")
    print(f"Recently rated page response type: {response.headers.get('content-type')}")
except Exception as e:
    print(f"Error testing recently rated page: {e}")

try:
    # Connect to database
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='book_engine'
    )
    
    if conn.is_connected():
        print("Connected to database successfully")
        cursor = conn.cursor()
        
        # Check existing users
        cursor.execute("SELECT user_id, username FROM user_table LIMIT 3")
        users = cursor.fetchall()
        print("\nExisting users:")
        for user in users:
            print(f"  ID: {user[0]}, Username: {user[1]}")
        
        # Check existing books
        cursor.execute("SELECT book_id, title FROM book_table LIMIT 3")
        books = cursor.fetchall()
        print("\nExisting books:")
        for book in books:
            print(f"  ID: {book[0]}, Title: {book[1]}")
        
        # If we have users and books, try to insert a rating
        if users and books:
            user_id = users[0][0]  # First user
            book_id = books[0][0]  # First book
            
            print(f"\nTrying to insert rating for user {user_id}, book {book_id}")
            
            # Insert rating
            cursor.execute(
                "INSERT INTO book_ratings (user_id, book_id, rating) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE rating = %s",
                (user_id, book_id, 5, 5)
            )
            conn.commit()
            print("Rating inserted successfully")
            
            # Retrieve the rating
            cursor.execute("SELECT * FROM book_ratings WHERE user_id = %s AND book_id = %s", (user_id, book_id))
            rating = cursor.fetchone()
            print(f"Retrieved rating: {rating}")
            
        cursor.close()
        conn.close()
        
except Error as e:
    print(f"Error: {e}")
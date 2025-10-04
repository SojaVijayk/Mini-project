import mysql.connector
from flask import Flask
from app import mysql

# Test script to check reading progress records
def test_reading_progress():
    try:
        # This would normally be done within a Flask request context
        # For testing purposes, we'll simulate the query
        print("Testing reading progress functionality...")
        
        # Simulate what the continue_reading_books query does
        # You would need to run this within the actual Flask app context
        print("To test properly, you would need to:")
        print("1. Check if reading_progress records exist for user_id=1 (or your test user)")
        print("2. Check if records with progress_percentage=0 are being filtered out")
        print("3. Check if DELETE operation is working correctly")
        
        # Example query you could run in MySQL:
        print("\nExample SQL queries to run in your database:")
        print("SELECT * FROM reading_progress WHERE user_id = 1;")
        print("SELECT * FROM reading_progress WHERE user_id = 1 AND progress_percentage = 0;")
        print("DELETE FROM reading_progress WHERE user_id = 1 AND book_id = YOUR_BOOK_ID;")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_reading_progress()
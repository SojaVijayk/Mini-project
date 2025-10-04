import mysql.connector
from mysql.connector import Error
import json

def test_complete_flow():
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
            cursor.execute("SELECT user_id, username FROM user_table LIMIT 1")
            users = cursor.fetchall()
            print("\nExisting users:")
            for user in users:
                print(f"  ID: {user[0]}, Username: {user[1]}")
            
            # Check existing books
            cursor.execute("SELECT book_id, title FROM book_table LIMIT 1")
            books = cursor.fetchall()
            print("\nExisting books:")
            for book in books:
                print(f"  ID: {book[0]}, Title: {book[1]}")
            
            # If we have users and books, try to insert a rating
            if users and books:
                user_id = users[0][0]  # First user
                book_id = books[0][0]  # First book
                
                print(f"\nTesting rating insertion for user {user_id}, book {book_id}")
                
                # Insert rating
                cursor.execute(
                    "INSERT INTO book_ratings (user_id, book_id, rating) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE rating = %s",
                    (user_id, book_id, 4, 4)
                )
                conn.commit()
                print("Rating inserted successfully")
                
                # Retrieve the rating
                cursor.execute("SELECT * FROM book_ratings WHERE user_id = %s AND book_id = %s", (user_id, book_id))
                rating = cursor.fetchone()
                print(f"Retrieved rating: {rating}")
                
                # Test the recently rated functionality
                print("\nTesting recently rated query:")
                cursor.execute(
                    """SELECT br.rating_id, br.book_id, br.rating, br.rated_at, 
                              bt.title, bt.author, bt.genre, bt.ISBN
                       FROM book_ratings br
                       JOIN book_table bt ON br.book_id = bt.book_id
                       WHERE br.user_id = %s
                       ORDER BY br.rated_at DESC
                       LIMIT 10""",
                    (user_id,)
                )
                ratings_data = cursor.fetchall()
                print(f"Found {len(ratings_data)} recently rated books:")
                for rating in ratings_data:
                    print(f"  Book: {rating[4]} by {rating[5]}, Rating: {rating[2]}")
                
            cursor.close()
            conn.close()
            
    except Error as e:
        print(f"Database Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_complete_flow()
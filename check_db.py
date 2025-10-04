import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='book_engine'
    )
    cursor = conn.cursor()
    
    print("Connected to database successfully!")
    
    # Check book_ratings table structure
    cursor.execute('DESCRIBE book_ratings')
    print('\nbook_ratings table structure:')
    for row in cursor.fetchall():
        print(row)
    
    # Check sample ratings
    cursor.execute('SELECT * FROM book_ratings LIMIT 5')
    print('\nSample ratings:')
    for row in cursor.fetchall():
        print(row)
        
    # Check total count of ratings
    cursor.execute('SELECT COUNT(*) FROM book_ratings')
    count = cursor.fetchone()[0]
    print(f'\nTotal ratings in database: {count}')
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
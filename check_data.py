from app import app, mysql

with app.app_context():
    cur = mysql.connection.cursor()
    
    # Check current user ID (assuming we're using the first user)
    cur.execute("SELECT user_id FROM user_table LIMIT 1")
    user_result = cur.fetchone()
    if user_result:
        user_id = user_result[0]
        print(f"Using user_id: {user_id}")
        
        # Check reading_progress records for this user
        cur.execute("SELECT * FROM reading_progress WHERE user_id = %s", (user_id,))
        progress_records = cur.fetchall()
        print(f"\nReading progress records for user {user_id}:")
        for record in progress_records:
            print(record)
        
        # Check reading_positions records for this user
        cur.execute("SELECT * FROM reading_positions WHERE user_id = %s", (user_id,))
        position_records = cur.fetchall()
        print(f"\nReading position records for user {user_id}:")
        for record in position_records:
            print(record)
    else:
        print("No users found in database")
    
    cur.close()
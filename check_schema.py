from app import app, mysql

with app.app_context():
    cur = mysql.connection.cursor()
    
    # Check reading_progress table structure
    cur.execute('DESCRIBE reading_progress')
    print('reading_progress table:')
    for row in cur.fetchall():
        print(row)
    
    print('\nreading_positions table:')
    cur.execute('DESCRIBE reading_positions')
    for row in cur.fetchall():
        print(row)
    
    cur.close()
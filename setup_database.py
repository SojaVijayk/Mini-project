import mysql.connector
import os

# Database configuration
config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'book_engine',
    'raise_on_warnings': True
}

def setup_database():
    try:
        # Connect to MySQL
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        
        # Read and execute SQL files
        sql_files = [
            'setup_rating_feedback_tables.sql',
            'create_favorites_table.sql',
            'create_reading_progress_table.sql',
            'create_reading_positions_table.sql',
            'update_book_table_isbn.sql'  # Add the ISBN update
        ]
        
        for sql_file in sql_files:
            if os.path.exists(sql_file):
                with open(sql_file, 'r') as file:
                    sql_script = file.read()
                
                # Split the script into individual statements
                statements = sql_script.split(';')
                
                # Execute each statement
                for statement in statements:
                    statement = statement.strip()
                    if statement:
                        try:
                            cursor.execute(statement)
                            print(f"Executed: {statement[:50]}...")
                        except Exception as e:
                            print(f"Error executing statement: {e}")
            else:
                print(f"SQL file not found: {sql_file}")
        
        # Commit changes
        cnx.commit()
        print("Database setup completed successfully!")
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'cnx' in locals():
            cnx.close()

if __name__ == "__main__":
    setup_database()
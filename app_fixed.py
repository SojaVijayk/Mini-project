import csv
import os
import re
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
app.secret_key = "your_secret_key_here_please_change_this"

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'book_engine'

mysql = MySQL(app)

# --- Helper Function to Read CSV ---
def read_csv(filename):
    """Reads a single-column CSV file and returns a list of its items."""
    items = []
    try:
        with open(filename, mode='r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            next(reader)  # Skip header row
            for row in reader:
                if row: # Ensure row is not empty
                    items.append(row[0])
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
    return items

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

def get_unique_authors_and_genres(books):
    """Extract unique authors and genres from books data."""
    authors = defaultdict(int)
    genres = defaultdict(int)
    
    for book in books:
        if book['author']:
            authors[book['author']] += 1
        if book['genre']:
            genres[book['genre']] += 1
    
    # Convert to list of dicts for template compatibility
    authors_list = [{'name': author, 'book_count': count} for author, count in authors.items()]
    genres_list = [{'name': genre, 'book_count': count} for genre, count in genres.items()]
    
    # Sort alphabetically
    authors_list.sort(key=lambda x: x['name'])
    genres_list.sort(key=lambda x: x['name'])
    
    return authors_list, genres_list

# --- Routes ---

# Landing Page
@app.route("/")
def landing():
    if 'loggedin' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_home'))
        else:
            return redirect(url_for('user_home'))
    return render_template("landing.html")

# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id, username, role, password, author, genre FROM user_table WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and user[3] == password:
            session['loggedin'] = True
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[2]
            user_author_preference = user[4]
            user_genre_preference = user[5]

            flash(f"Welcome, {session['username']}!", "success")

            # Admin users go directly to admin page
            if session['role'] == 'admin':
                return redirect(url_for("admin_home"))
            
            # Regular users need to set preferences first
            if user_author_preference is None or user_genre_preference is None:
                flash("Please set your author and genre preferences to continue.", "info")
                return redirect(url_for("preferences"))

            return redirect(url_for("user_home"))
        else:
            flash("Invalid email or password.", "error")

    return render_template("login.html")

# Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        dob = request.form.get("dob")
        gender = request.form.get("gender")

        if not all([username, password, email, phone_number, dob, gender]):
            flash("Please fill out all fields.", "error")
            return render_template("register.html")

        try:
            cur = mysql.connection.cursor()
            cur.execute(
                """INSERT INTO user_table 
                   (username, password, email, phone_no, dob, gender, role, author, genre) 
                   VALUES (%s, %s, %s, %s, %s, %s, 'user', NULL, NULL)""",
                (username, password, email, phone_number, dob, gender)
            )
            mysql.connection.commit()
            cur.close()
            
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            return redirect(url_for("register"))

    return render_template("register.html")

# Preferences Page
@app.route("/preferences", methods=["GET", "POST"])
def preferences():
    if 'loggedin' not in session:
        flash("Please log in to set your preferences.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        author_preference = request.form.get("author")
        genre_preference = request.form.get("genre")

        if not author_preference or not genre_preference:
            flash("Please select one author and one genre to continue.", "error")
            return redirect(url_for("preferences"))

        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "UPDATE user_table SET author = %s, genre = %s WHERE user_id = %s",
                (author_preference, genre_preference, session['user_id'])
            )
            mysql.connection.commit()
            cur.close()
            
            flash("Your preferences have been saved!", "success")
            return redirect(url_for("user_home"))

        except Exception as e:
            flash(f"An error occurred while saving preferences: {e}", "error")
            return redirect(url_for("preferences"))
            
    # MODIFIED: Updated file paths to look inside the /data folder
    authors_list = read_csv('data/authors.csv')
    genres_list = read_csv('data/genre.csv')
    
    return render_template("preference.html", authors=authors_list, genres=genres_list)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

# User Home
@app.route("/user_home")
def user_home():
    if 'loggedin' in session and session['role'] == 'user':
        return render_template("user.html", username=session['username'])
    flash("Please log in to access this page.", "error")
    return redirect(url_for('login'))

# Admin Home
@app.route("/admin_home")
def admin_home():
    if 'loggedin' in session and session['role'] == 'admin':
        return render_template('admin.html', username=session['username'])
    flash("You do not have permission to access this page.", "error")
    return redirect(url_for('login'))

# User Profile
@app.route("/profile")
def profile():
    if 'loggedin' not in session:
        flash("Please log in to view your profile.", "error")
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT username, email, phone_no, dob, gender, author, genre FROM user_table WHERE user_id = %s",
            (session['user_id'],)
        )
        user_data = cur.fetchone()
        cur.close()
        
        if user_data:
            user_info = {
                'username': user_data[0],
                'email': user_data[1],
                'phone_number': user_data[2],
                'dob': user_data[3],
                'gender': user_data[4],
                'preferred_author': user_data[5],
                'preferred_genre': user_data[6]
            }
            return render_template('profile.html', user=user_info)
        else:
            flash("User data not found.", "error")
            return redirect(url_for('user_home'))
            
    except Exception as e:
        flash(f"An error occurred while fetching profile data: {e}", "error")
        return redirect(url_for('user_home'))

# Edit Profile
@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if 'loggedin' not in session:
        flash("Please log in to edit your profile.", "error")
        return redirect(url_for('login'))
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        phone_number = request.form.get("phone_number", "").strip()
        dob = request.form.get("dob", "").strip()
        gender = request.form.get("gender", "").strip()
        preferred_author = request.form.get("preferred_author", "").strip()
        preferred_genre = request.form.get("preferred_genre", "").strip()
        
        # Validation
        if not all([username, email, phone_number, dob, gender]):
            flash("Please fill out all required fields.", "error")
            return redirect(url_for('edit_profile'))
            
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                """UPDATE user_table SET 
                   username = %s, email = %s, phone_no = %s, dob = %s, 
                   gender = %s, author = %s, genre = %s 
                   WHERE user_id = %s""",
                (username, email, phone_number, dob, gender, 
                 preferred_author if preferred_author else None,
                 preferred_genre if preferred_genre else None,
                 session['user_id'])
            )
            mysql.connection.commit()
            cur.close()
            
            # Update session username if it changed
            session['username'] = username
            
            flash("Profile updated successfully!", "success")
            return redirect(url_for('profile'))
            
        except Exception as e:
            flash(f"An error occurred while updating profile: {e}", "error")
            return redirect(url_for('edit_profile'))
    
    # GET request - fetch current user data and preferences
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT username, email, phone_no, dob, gender, author, genre FROM user_table WHERE user_id = %s",
            (session['user_id'],)
        )
        user_data = cur.fetchone()
        cur.close()
        
        if user_data:
            user_info = {
                'username': user_data[0],
                'email': user_data[1],
                'phone_number': user_data[2],
                'dob': user_data[3],
                'gender': user_data[4],
                'preferred_author': user_data[5],
                'preferred_genre': user_data[6]
            }
            
            # Get authors and genres lists for dropdowns
            authors_list = read_csv('data/authors.csv')
            genres_list = read_csv('data/genre.csv')
            
            return render_template('editprofile.html', user=user_info, authors=authors_list, genres=genres_list)
        else:
            flash("User data not found.", "error")
            return redirect(url_for('user_home'))
            
    except Exception as e:
        flash(f"An error occurred while fetching profile data: {e}", "error")
        return redirect(url_for('user_home'))

# View Registered Users (Admin only)
@app.route("/view_registered_users")
def view_registered_users():
    if 'loggedin' not in session or session['role'] != 'admin':
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT user_id, username, email, phone_no, dob, gender, author, genre FROM user_table WHERE role = 'user' ORDER BY user_id DESC"
        )
        users_data = cur.fetchall()
        cur.close()
        
        users_list = []
        for user in users_data:
            user_info = {
                'user_id': user[0],
                'username': user[1],
                'email': user[2],
                'phone_number': user[3],
                'dob': user[4],
                'gender': user[5],
                'preferred_author': user[6],
                'preferred_genre': user[7]
            }
            users_list.append(user_info)
        
        return render_template('reguser.html', users=users_list)
        
    except Exception as e:
        flash(f"An error occurred while fetching users data: {e}", "error")
        return redirect(url_for('admin_home'))

# View Books (Admin only)
@app.route("/view_books")
def view_books():
    if 'loggedin' not in session or session['role'] != 'admin':
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for('login'))
    
    try:
        # Read books from database
        books_list = []
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT book_id, title, author, genre, ISBN FROM book_table ORDER BY book_id DESC")
        books_data = cur.fetchall()
        cur.close()
        
        for book in books_data:
            book_info = {
                'id': book[0],
                'title': book[1],
                'author': book[2],
                'genre': book[3],
                'isbn': book[4]
            }
            books_list.append(book_info)
        
        return render_template('viewbook.html', books=books_list)
        
    except Exception as e:
        flash(f"An error occurred while fetching books data: {e}", "error")
        return redirect(url_for('admin_home'))

# Add Book (Admin only)
@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if 'loggedin' not in session or session['role'] != 'admin':
        flash("You do not have permission to access this page.", "error")
        return redirect(url_for('login'))
    
    if request.method == "POST":
        book_title = request.form.get("book_title", "").strip()
        author_name = request.form.get("author_name", "").strip()
        isbn = request.form.get("isbn", "").strip()
        genre = request.form.get("genre", "").strip()
        
        # Validation
        if not all([book_title, author_name, isbn, genre]):
            flash("Please fill out all fields.", "error")
            return render_template("addbook.html")
            
        if len(book_title) < 2:
            flash("Book title must be at least 2 characters long.", "error")
            return render_template("addbook.html")
            
        if len(author_name) < 2:
            flash("Author name must be at least 2 characters long.", "error")
            return render_template("addbook.html")
            
        if len(isbn) < 10:
            flash("ISBN must be at least 10 characters long.", "error")
            return render_template("addbook.html")
        
        try:
            # Check if book already exists (by title and author or by ISBN)
            cur = mysql.connection.cursor()
            
            # Check for duplicate by title and author
            cur.execute(
                "SELECT book_id FROM book_table WHERE LOWER(title) = %s AND LOWER(author) = %s",
                (book_title.lower(), author_name.lower())
            )
            title_author_exists = cur.fetchone()
            
            # Check for duplicate by ISBN
            cur.execute(
                "SELECT book_id FROM book_table WHERE ISBN = %s",
                (isbn,)
            )
            isbn_exists = cur.fetchone()
            
            if title_author_exists or isbn_exists:
                cur.close()
                flash(f"Book '{book_title}' by {author_name} or ISBN {isbn} already exists in the catalog.", "error")
                return render_template("addbook.html")
            
            # Add new book to database
            cur.execute(
                "INSERT INTO book_table (title, author, genre, ISBN) VALUES (%s, %s, %s, %s)",
                (book_title, author_name, genre, isbn)
            )
            mysql.connection.commit()
            cur.close()
            
            flash(f"Book '{book_title}' by {author_name} has been successfully added to the catalog!", "success")
            return redirect(url_for('view_books'))
            
        except Exception as e:
            flash(f"An error occurred while adding the book: {e}", "error")
            return render_template("addbook.html")
    
    # GET request - display the form
    return render_template("addbook.html")

# Recommended Books Page
@app.route("/recommended_books")
def recommended_books():
    if 'loggedin' not in session:
        flash("Please log in to view recommendations.", "error")
        return redirect(url_for('login'))
    
    try:
        # Get user preferences
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT username, author, genre FROM user_table WHERE user_id = %s",
            (session['user_id'],)
        )
        user_data = cur.fetchone()
        cur.close()
        
        if not user_data:
            flash("User data not found.", "error")
            return redirect(url_for('user_home'))
        
        username = user_data[0]
        preferred_author = user_data[1]
        preferred_genre = user_data[2]
        
        # Read all books from CSV for consistent data source
        all_books_csv = read_books_csv('data/books_data.csv')
        
        # For debugging - return a simple list of books
        recommended_books_list = []
        for i, book in enumerate(all_books_csv[:10]):  # Limit to first 10 books for testing
            book_info = {
                'id': int(book['id']),
                'title': book['title'],
                'author': book['author'],
                'genre': book['genre'],
                'isbn': book['isbn'],
                'recommendation_type': 'Top Trending' if i < 5 else 'Based on Your Preferences'
            }
            recommended_books_list.append(book_info)
        
        # Prepare user info for template
        user_info = {
            'username': username,
            'preferred_author': preferred_author,
            'preferred_genre': preferred_genre
        }
        
        return render_template('recommendedbooks.html', 
                             username=username,
                             user=user_info,
                             recommended_books=recommended_books_list)
        
    except Exception as e:
        flash(f"An error occurred while fetching recommendations: {e}", "error")
        return redirect(url_for('user_home'))

        # If we still don't have 5 books, just get any books to fill up to 5
        if len(top_rated_books) < 5:
            needed_books = 5 - len(top_rated_books)
            cur.execute("""
                SELECT bt.book_id, bt.title, bt.author, bt.genre, bt.ISBN, 
                       COALESCE(AVG(br.rating), 0) as avg_rating, COUNT(br.rating) as rating_count
                FROM book_table bt
                LEFT JOIN book_ratings br ON bt.book_id = br.book_id
                GROUP BY bt.book_id, bt.title, bt.author, bt.genre, bt.ISBN
                ORDER BY bt.book_id
                LIMIT %s
            """, (needed_books,))
            additional_books = cur.fetchall()
            
            # Merge the lists, avoiding duplicates
            existing_book_ids = {book[0] for book in top_rated_books}
            for book in additional_books:
                if book[0] not in existing_book_ids and len(top_rated_books) < 5:
                    top_rated_books.append(book)
                    existing_book_ids.add(book[0])
        
        # Limit to exactly 5 books
        top_rated_books = top_rated_books[:5]
        
        # Get books based on user preferences (genre, author)
        preference_books = []
        if preferred_author or preferred_genre:
            query = "SELECT book_id, title, author, genre, ISBN FROM book_table WHERE "
            params = []
            conditions = []
            
            if preferred_author:
                conditions.append("author = %s")
                params.append(preferred_author)
            
            if preferred_genre:
                conditions.append("genre = %s")
                params.append(preferred_genre)
            
            query += " OR ".join(conditions)
            query += " ORDER BY title LIMIT 10"
            
            cur.execute(query, params)
            preference_books = cur.fetchall()
        
        # Get user-to-user similarity recommendations
        # Find users with similar preferences (same author or genre)
        cur.execute("""
            SELECT DISTINCT ut.user_id
            FROM user_table ut
            WHERE ut.user_id != %s 
            AND (ut.author = %s OR ut.genre = %s)
        """, (session['user_id'], preferred_author, preferred_genre))
        similar_users = cur.fetchall()
        
        similar_user_books = []
        if similar_users:
            user_ids = [str(user[0]) for user in similar_users]
            placeholders = ','.join(['%s'] * len(user_ids))
            
            # Get books rated highly by similar users
            cur.execute(f"""
                SELECT DISTINCT bt.book_id, bt.title, bt.author, bt.genre, bt.ISBN
                FROM book_table bt
                JOIN book_ratings br ON bt.book_id = br.book_id
                WHERE br.user_id IN ({placeholders})
                AND br.rating >= 4
                LIMIT 10
            """, user_ids)
            similar_user_books = cur.fetchall()
        
        # Get feedback-based recommendations
        # Find books with positive keywords in feedback
        cur.execute("""
            SELECT DISTINCT bt.book_id, bt.title, bt.author, bt.genre, bt.ISBN
            FROM book_table bt
            JOIN book_feedback bf ON bt.book_id = bf.book_id
            WHERE bf.feedback_text LIKE %s 
            OR bf.feedback_text LIKE %s 
            OR bf.feedback_text LIKE %s
            LIMIT 10
        """, ('%good%', '%great%', '%excellent%'))
        feedback_books = cur.fetchall()
        
        # Combine all recommendations and remove duplicates
        all_books = {}
        
        # Process top rated books
        for book in top_rated_books:
            # Find the corresponding CSV book using ISBN
            normalized_isbn = book[4].replace('-', '')
            csv_book = isbn_to_book.get(normalized_isbn)
            
            # Fallback to title/author matching if ISBN doesn't match
            if not csv_book:
                title_key = f"{book[1].lower()}|{book[2].lower()}"
                csv_book = db_isbn_to_csv.get(title_key)
            
            # Use CSV serial_number for book ID to match book_description route
            if csv_book:
                book_info = {
                    'id': int(csv_book['id']),  # Use CSV serial_number as integer
                    'title': book[1],
                    'author': book[2],
                    'genre': book[3],
                    'isbn': book[4],
                    'avg_rating': float(book[5]) if book[5] else 0,
                    'rating_count': book[6],
                    'recommendation_type': 'Top Trending'
                }
                # Use a unique key to avoid duplicates
                book_key = f"top_{book[0]}"
                all_books[book_key] = book_info
                print(f"Added top rated book: {book[1]} - {book[2]}")
        
        # Process preference-based books
        for book in preference_books:
            # Find the corresponding CSV book using ISBN
            normalized_isbn = book[4].replace('-', '')
            csv_book = isbn_to_book.get(normalized_isbn)
            
            # Fallback to title/author matching if ISBN doesn't match
            if not csv_book:
                title_key = f"{book[1].lower()}|{book[2].lower()}"
                csv_book = db_isbn_to_csv.get(title_key)
            
            # Use CSV serial_number for book ID to match book_description route
            if csv_book:
                # Check for duplicates using book ID
                book_key = f"pref_{book[0]}"
                if book_key not in all_books:
                    book_info = {
                        'id': int(csv_book['id']),  # Use CSV serial_number as integer
                        'title': book[1],
                        'author': book[2],
                        'genre': book[3],
                        'isbn': book[4],
                        'recommendation_type': 'Based on Your Preferences'
                    }
                    all_books[book_key] = book_info
                    print(f"Added preference book: {book[1]} - {book[2]}")
        
        # Process similar user books
        for book in similar_user_books:
            # Find the corresponding CSV book using ISBN
            normalized_isbn = book[4].replace('-', '')
            csv_book = isbn_to_book.get(normalized_isbn)
            
            # Fallback to title/author matching if ISBN doesn't match
            if not csv_book:
                title_key = f"{book[1].lower()}|{book[2].lower()}"
                csv_book = db_isbn_to_csv.get(title_key)
            
            # Use CSV serial_number for book ID to match book_description route
            if csv_book:
                # Check for duplicates using book ID
                book_key = f"similar_{book[0]}"
                if book_key not in all_books:
                    book_info = {
                        'id': int(csv_book['id']),  # Use CSV serial_number as integer
                        'title': book[1],
                        'author': book[2],
                        'genre': book[3],
                        'isbn': book[4],
                        'recommendation_type': 'Based on Your Preferences'
                    }
                    all_books[book_key] = book_info
                    print(f"Added similar user book: {book[1]} - {book[2]}")
        
        # Process feedback-based books
        for book in feedback_books:
            # Find the corresponding CSV book using ISBN
            normalized_isbn = book[4].replace('-', '')
            csv_book = isbn_to_book.get(normalized_isbn)
            
            # Fallback to title/author matching if ISBN doesn't match
            if not csv_book:
                title_key = f"{book[1].lower()}|{book[2].lower()}"
                csv_book = db_isbn_to_csv.get(title_key)
            
            # Use CSV serial_number for book ID to match book_description route
            if csv_book:
                # Check for duplicates using book ID
                book_key = f"feedback_{book[0]}"
                if book_key not in all_books:
                    book_info = {
                        'id': int(csv_book['id']),  # Use CSV serial_number as integer
                        'title': book[1],
                        'author': book[2],
                        'genre': book[3],
                        'isbn': book[4],
                        'recommendation_type': 'Based on Your Preferences'
                    }
                    all_books[book_key] = book_info
                    print(f"Added feedback book: {book[1]} - {book[2]}")
        
        # Convert to list
        recommended_books_list = list(all_books.values())
        
        # Debug: Print the number of books in each category
        top_trending_count = sum(1 for book in recommended_books_list if book['recommendation_type'] == 'Top Trending')
        preference_count = sum(1 for book in recommended_books_list if book['recommendation_type'] == 'Based on Your Preferences')
        print(f"Total recommended books: {len(recommended_books_list)}")
        print(f"Top Trending books: {top_trending_count}")
        print(f"Based on Your Preferences books: {preference_count}")
        
        # Debug: Print top trending books
        if top_trending_count > 0:
            print("Top Trending books:")
            for book in recommended_books_list:
                if book['recommendation_type'] == 'Top Trending':
                    print(f"  - {book['title']} by {book['author']} (Rating: {book.get('avg_rating', 'N/A')}")
        
        cur.close()
        
        # Prepare user info for template
        user_info = {
            'username': username,
            'preferred_author': preferred_author,
            'preferred_genre': preferred_genre
        }
        
        return render_template('recommendedbooks.html', 
                             username=username,
                             user=user_info,
                             recommended_books=recommended_books_list)
        
    except Exception as e:
        flash(f"An error occurred while fetching recommendations: {e}", "error")
        return redirect(url_for('user_home'))


# Book Search (Global)
@app.route("/search_books", methods=["GET", "POST"])
def search_books():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    search_query = request.args.get('q', '').strip()
    books_list = []
    
    if search_query:
        try:
            # Read books from CSV
            books = read_books_csv('data/books_data.csv')
            
            # Filter books based on search query
            for book in books:
                if (search_query.lower() in book['title'].lower() or
                    search_query.lower() in book['author'].lower() or
                    search_query.lower() in book['genre'].lower() or
                    search_query.lower() in book['isbn'].lower()):
                    books_list.append(book)
                
            # Limit to 50 results
            books_list = books_list[:50]
                
        except Exception as e:
            flash(f"An error occurred while searching: {e}", "error")
    
    return render_template('search_results.html', books=books_list, query=search_query)

# Favorites functionality
@app.route("/favorites")
def favorites():
    if 'loggedin' not in session:
        flash("Please log in to view your favorites.", "error")
        return redirect(url_for('login'))
    
    try:
        cur = mysql.connection.cursor()
        # Get user's favorite books from existing favorite_book_table
        cur.execute(
            """SELECT DISTINCT b.book_id, b.title, b.author, b.genre, b.ISBN 
               FROM book_table b 
               INNER JOIN favorite_book_table f ON b.book_id = f.book_id 
               WHERE f.user_id = %s 
               ORDER BY b.title ASC""",
            (session['user_id'],)
        )
        favorites_data = cur.fetchall()
        cur.close()
        
        favorite_books_list = []
        for book in favorites_data:
            book_info = {
                'id': book[0],
                'title': book[1],
                'author': book[2],
                'genre': book[3],
                'isbn': book[4]
            }
            favorite_books_list.append(book_info)
        
        return render_template('fav.html', favorite_books=favorite_books_list)
        
    except Exception as e:
        flash(f"An error occurred while fetching favorites: {e}", "error")
        return redirect(url_for('user_home'))

@app.route("/add_favorite", methods=["POST"])
def add_favorite():
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'})
    
    try:
        data = request.get_json()
        book_id = data.get('book_id')
        
        if not book_id:
            return jsonify({'success': False, 'message': 'Book ID is required'})
        
        cur = mysql.connection.cursor()
        
        # Check if already in favorites using existing favorite_book_table
        cur.execute(
            "SELECT * FROM favorite_book_table WHERE user_id = %s AND book_id = %s",
            (session['user_id'], book_id)
        )
        existing = cur.fetchone()
        
        if existing:
            cur.close()
            return jsonify({'success': False, 'message': 'Book already in favorites'})
        
        # Add to favorites using existing favorite_book_table
        cur.execute(
            "INSERT INTO favorite_book_table (user_id, book_id) VALUES (%s, %s)",
            (session['user_id'], book_id)
        )
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True, 'message': 'Added to favorites successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred: ' + str(e)})

@app.route("/remove_favorite", methods=["POST"])
def remove_favorite():
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'})
    
    try:
        data = request.get_json()
        book_id = data.get('book_id')
        
        if not book_id:
            return jsonify({'success': False, 'message': 'Book ID is required'})
        
        cur = mysql.connection.cursor()
        # Remove from favorites using existing favorite_book_table
        cur.execute(
            "DELETE FROM favorite_book_table WHERE user_id = %s AND book_id = %s",
            (session['user_id'], book_id)
        )
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True, 'message': 'Removed from favorites successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred: ' + str(e)})

# Explore by Authors - fetch all unique authors from CSV
@app.route("/explore_authors")
def explore_authors():
    if 'loggedin' not in session:
        flash("Please log in to explore authors.", "error")
        return redirect(url_for('login'))
    
    search_query = request.args.get('q', '').strip()
    
    try:
        # Read books from CSV
        books = read_books_csv('data/books_data.csv')
        
        # Get unique authors with book count
        authors_list, _ = get_unique_authors_and_genres(books)
        
        # Filter by search query if provided
        if search_query:
            authors_list = [author for author in authors_list 
                           if search_query.lower() in author['name'].lower()]
        
        return render_template('explore.html', 
                             explore_type='authors',
                             title='Explore Authors',
                             subtitle='Discover books by your favorite authors',
                             items=authors_list,
                             username=session['username'])
        
    except Exception as e:
        flash(f"An error occurred while fetching authors: {e}", "error")
        return redirect(url_for('user_home'))

# Explore by Genres - fetch all unique genres from CSV  
@app.route("/explore_genres")
def explore_genres():
    if 'loggedin' not in session:
        flash("Please log in to explore genres.", "error")
        return redirect(url_for('login'))
    
    search_query = request.args.get('q', '').strip()
    
    try:
        # Read books from CSV
        books = read_books_csv('data/books_data.csv')
        
        # Get unique genres with book count
        _, genres_list = get_unique_authors_and_genres(books)
        
        # Filter by search query if provided
        if search_query:
            genres_list = [genre for genre in genres_list 
                          if search_query.lower() in genre['name'].lower()]
        
        return render_template('explore.html', 
                             explore_type='genres',
                             title='Explore Genres',
                             subtitle='Browse books by different genres',
                             items=genres_list,
                             username=session['username'])
        
    except Exception as e:
        flash(f"An error occurred while fetching genres: {e}", "error")
        return redirect(url_for('user_home'))

# Explore Books - fetch all books from CSV with pagination
@app.route("/explore_books")
def explore_books():
    if 'loggedin' not in session:
        flash("Please log in to explore books.", "error")
        return redirect(url_for('login'))
    
    search_query = request.args.get('q', '').strip()
    
    try:
        # Read books from CSV
        books = read_books_csv('data/books_data.csv')
        
        # Filter by search query if provided
        if search_query:
            books = [book for book in books 
                    if (search_query.lower() in book['title'].lower() or
                        search_query.lower() in book['author'].lower() or
                        search_query.lower() in book['genre'].lower() or
                        search_query.lower() in book['isbn'].lower())]
        
        # Get page number from query parameter (default to 1)
        page = request.args.get('page', 1, type=int)
        per_page = 20  # Number of books per page
        offset = (page - 1) * per_page
        
        # Apply pagination
        paginated_books = books[offset:offset + per_page]
        
        # Calculate pagination info
        total_books = len(books)
        total_pages = (total_books + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': total_books,
            'total_pages': total_pages,
            'has_prev': has_prev,
            'has_next': has_next,
            'prev_num': page - 1 if has_prev else None,
            'next_num': page + 1 if has_next else None
        }
        
        subtitle = f'Browse our collection of {total_books} books'
        if search_query:
            subtitle = f'Search results for "{search_query}" - {total_books} books found'
        
        return render_template('explore.html', 
                             explore_type='books',
                             title='Explore Books',
                             subtitle=subtitle,
                             books=paginated_books,
                             pagination=pagination_info,
                             username=session['username'])
        
    except Exception as e:
        flash(f"An error occurred while fetching books: {e}", "error")
        return redirect(url_for('user_home'))

# Get books by specific author
@app.route("/books_by_author/<author_name>")
def books_by_author(author_name):
    if 'loggedin' not in session:
        flash("Please log in to view books.", "error")
        return redirect(url_for('login'))
    
    try:
        # Read books from CSV
        books = read_books_csv('data/books_data.csv')
        
        # Filter books by author
        author_books = [book for book in books 
                       if book['author'].lower() == author_name.lower()]
        
        return render_template('explore.html', 
                             explore_type='author_books',
                             title=f'Books by {author_name}',
                             subtitle=f'All books by {author_name} in our collection',
                             books=author_books,
                             author_name=author_name,
                             username=session['username'])
        
    except Exception as e:
        flash(f"An error occurred while fetching books by author: {e}", "error")
        return redirect(url_for('explore_authors'))

# Get books by specific genre
@app.route("/books_by_genre/<genre_name>")
def books_by_genre(genre_name):
    if 'loggedin' not in session:
        flash("Please log in to view books.", "error")
        return redirect(url_for('login'))
    
    try:
        # Read books from CSV
        books = read_books_csv('data/books_data.csv')
        
        # Filter books by genre
        genre_books = [book for book in books 
                      if book['genre'].lower() == genre_name.lower()]
        
        return render_template('explore.html', 
                             explore_type='genre_books',
                             title=f'{genre_name} Books',
                             subtitle=f'All {genre_name.lower()} books in our collection',
                             books=genre_books,
                             genre_name=genre_name,
                             username=session['username'])
        
    except Exception as e:
        flash(f"An error occurred while fetching books by genre: {e}", "error")
        return redirect(url_for('explore_genres'))

# Book Detail Page
@app.route("/book/<int:book_id>")
def book_detail(book_id):
    if 'loggedin' not in session:
        flash("Please log in to view book details.", "error")
        return redirect(url_for('login'))
    
    try:
        # Read books from CSV
        books = read_books_csv('data/books_data.csv')
        
        # Find the book with the matching ID
        book_data = None
        for book in books:
            if int(book['id']) == book_id:
                book_data = book
                break
        
        if not book_data:
            flash("Book not found.", "error")
            return redirect(url_for('explore_books'))
        
        book_info = {
            'id': book_data['id'],
            'title': book_data['title'],
            'author': book_data['author'],
            'genre': book_data['genre'],
            'isbn': book_data['isbn'],
            'description': f"This is a {book_data['genre'].lower()} book by {book_data['author']}. '{book_data['title']}' promises an engaging reading experience with compelling storytelling and rich character development. {book_data['title']} explores themes relevant to {book_data['genre'].lower()} literature and provides both entertainment and thought-provoking content. Perfect for fans of {book_data['author']}'s writing style and {book_data['genre'].lower()} enthusiasts alike."
        }
        
        return render_template('book_detail.html', book=book_info, username=session.get('username', 'User'))
        
    except Exception as e:
        flash(f"An error occurred while fetching book details: {e}", "error")
        return redirect(url_for('explore_books'))

# Book Description Page
@app.route('/book_description/<int:book_id>')
def book_description(book_id):
    if 'loggedin' not in session:
        flash("Please log in to view book descriptions.", "error")
        return redirect(url_for('login'))
    
    try:
        # Read books from CSV (as required by project specification)
        books = read_books_csv('data/books_data.csv')
        
        # Find the book with the matching ID (CSV serial_number)
        book_data = None
        for book in books:
            if int(book['id']) == book_id:
                book_data = book
                break
        
        if not book_data:
            flash("Book not found.", "error")
            return redirect(url_for('user_home'))
        
        # Also try to find the book in the database for story content and get the database book_id
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT book_id, story_content FROM book_table WHERE ISBN = %s",
            (book_data['isbn'],)
        )
        db_book_data = cur.fetchone()
        cur.close()
        
        # Include both the CSV serial_number (as 'id') and database book_id
        book_info = {
            'id': book_data['id'],  # CSV serial_number
            'db_id': db_book_data[0] if db_book_data else None,  # Database book_id
            'title': book_data['title'],
            'author': book_data['author'],
            'genre': book_data['genre'],
            'isbn': book_data['isbn'],
            'description': f"This is a {book_data['genre'].lower()} book by {book_data['author']}. '{book_data['title']}' promises an engaging reading experience with compelling storytelling and rich character development.",
            'story_content': db_book_data[1] if db_book_data else book_data['story_content']
        }
        
        return render_template('book_description.html', book=book_info, username=session.get('username', 'User'))
        
    except Exception as e:
        flash(f"An error occurred while fetching book description: {e}", "error")
        return redirect(url_for('user_home'))

# Story Generation Function
def generate_story_for_book(title, author, genre):
    """Generate a unique story based on the book's title, author, and genre."""
    
    # Create genre-specific story elements
    if 'mystery' in genre.lower() or 'detective' in genre.lower():
        protagonist = 'detective'
        setting = 'a foggy city'
        conflict = 'solve a baffling case'
        theme = 'justice and truth'
    elif 'romance' in genre.lower():
        protagonist = 'young woman'
        setting = 'a charming coastal town'

        conflict = 'find true love'
        theme = 'love and connection'
    elif 'fantasy' in genre.lower() or 'magic' in genre.lower():
        protagonist = 'apprentice wizard'
        setting = 'a mystical realm'
        conflict = 'save the kingdom'
        theme = 'courage and destiny'
    elif 'sci-fi' in genre.lower() or 'science' in genre.lower():
        protagonist = 'space explorer'
        setting = 'a distant planet'
        conflict = 'prevent galactic disaster'
        theme = 'technology and humanity'
    elif 'horror' in genre.lower() or 'thriller' in genre.lower():
        protagonist = 'investigator'
        setting = 'an isolated mansion'
        conflict = 'survive supernatural threats'
        theme = 'fear and survival'
    else:  # Default for other genres
        protagonist = 'adventurer'
        setting = 'a bustling metropolis'
        conflict = 'overcome personal challenges'
        theme = 'growth and discovery'
    
    # Customize story based on title keywords
    if 'dragon' in title.lower():
        antagonist = 'a fierce dragon'
        item = 'an ancient artifact'
    elif 'shadow' in title.lower():
        antagonist = 'a shadow figure'
        item = 'a mysterious key'
    elif 'lost' in title.lower():
        antagonist = 'time itself'
        item = 'a forgotten map'
    elif 'secret' in title.lower():
        antagonist = 'a secret society'
        item = 'classified documents'
    else:
        antagonist = 'an unknown enemy'
        item = 'a precious treasure'
    
    # Generate an extensive story with detailed content equivalent to at least 20 pages as continuous paragraphs
    story = f"""Title: {title}
Author: {author}
Genre: {genre}

In {setting}, a {protagonist} named {protagonist} stumbled upon {item} that would change everything. The discovery came at a time when {conflict} seemed impossible. As {protagonist} examined the {item}, mysterious forces began to awaken, drawing them into a web of intrigue and danger. The {item} contained cryptic symbols that hinted at {antagonist}, whose influence had been felt throughout the land for generations. {protagonist} realized that this discovery was not accidental but a calling, one that would require all their skills and courage to fulfill. The {item} was no ordinary object. Its surface was covered in intricate engravings that seemed to shift and change when viewed from different angles. Ancient runes, some familiar and others completely foreign, told a story of power and peril that had been forgotten by time. As {protagonist} traced the symbols with careful fingers, a strange warmth emanated from the object, and visions flashed through their mind - glimpses of a distant past where {antagonist} had ruled with an iron fist, bringing darkness to all corners of the realm.

The decision to leave their comfortable existence was not made lightly. {protagonist} had always been content with their simple life, but the weight of destiny pressed heavily upon their shoulders. Friends and family tried to dissuade them, warning of the dangers that lay ahead, but {protagonist} knew that turning away from this responsibility would haunt them forever. The ancient texts spoke of a prophecy, one that had been recorded by scholars centuries ago but dismissed as mere legend. According to the prophecy, when darkness once again threatened to engulf the world, a chosen one would rise to challenge it. This chosen one would possess not just courage, but also wisdom, compassion, and an unshakeable moral compass. As {protagonist} studied the texts more carefully, they began to see parallels between the prophecy and their own life - the signs were all there, if one knew how to look for them.

Along the way, {protagonist} encountered allies who shared their quest for {theme}. Each new companion brought unique skills and perspectives that would prove invaluable in the trials ahead. The path was fraught with challenges that tested not only physical abilities but also moral convictions. {protagonist} learned that true strength came not from individual prowess but from the bonds forged with others who shared the same ideals. The first to join {protagonist} was Lyra, a scholar from the Great Library who had spent years studying the ancient prophecies. Her knowledge of history and languages proved invaluable in deciphering the cryptic messages hidden within the {item}. She was cautious by nature, always double-checking facts and cross-referencing sources, but her meticulous approach often revealed details that others might have missed.

The second companion was Kael, a warrior from the Northern Reaches whose skill with a blade was matched only by his loyalty to those he called friend. His weathered face bore scars from countless battles, each one a testament to his dedication to protecting the innocent. Kael had been tracking the movements of {antagonist}'s minions for months, and his knowledge of their tactics would prove crucial in the days to come. His presence brought both comfort and concern to the group - comfort in knowing they had such a capable protector, and concern over what his involvement might mean for his own safety.

The third member of their group was Zara, a healer whose gentle demeanor masked a fierce determination to protect the innocent. Her knowledge of herbs and medicines saved the group on numerous occasions, and her ability to see the best in people often helped resolve conflicts within their own ranks. Zara had grown up in the Healing Groves, where she learned not just the art of mending broken bodies, but also the deeper magic of soothing troubled minds. Her connection to the natural world was profound, and she could often sense the presence of malevolent forces before others.

As {protagonist} ventured deeper into unknown territories, the presence of {antagonist} grew stronger. Dark forces sought to reclaim the {item}, leading to confrontations that pushed {protagonist} to their limits. Each battle revealed more about the true nature of the conflict and the stakes involved. During one particularly harrowing encounter, {protagonist} faced a choice between personal safety and protecting an innocent bystander. The decision to help, despite the risk, earned the respect of a powerful ally who provided crucial information about the final confrontation.

The journey led them through the Whispering Woods, where ancient trees seemed to murmur secrets of the past. Here, they encountered spirits of those who had fallen in previous battles against {antagonist}. These spirits, though ethereal, were very much real in their pain and their warnings. They spoke of a great battle that had taken place generations ago, a battle that had nearly destroyed the world but had ultimately failed to defeat {antagonist} completely. The spirits shared tales of heroes who had sacrificed everything to protect the realm, and their stories served as both inspiration and warning for the group.

In the Mountains of Echoes, they faced physical challenges that tested not just their endurance but their resolve. Avalanches, treacherous paths, and sudden storms seemed to be orchestrated by some malevolent force that sought to impede their progress. It was here that {protagonist} first truly understood the scope of the power they were up against. The mountains themselves seemed alive, responding to the presence of the {item} with violent upheavals that threatened to bury the entire party. Only through quick thinking and teamwork did they manage to survive the ordeal.

The Desert of Sorrows presented a different kind of challenge - one of isolation and psychological pressure. The endless dunes and scorching sun played tricks on the mind, making it difficult to distinguish reality from hallucination. It was during this trial that {protagonist} learned to trust their instincts above all else. The desert seemed to strip away all pretense, forcing each member of the group to confront their deepest fears and insecurities. Many a seasoned traveler had been driven mad by the desert's influence, but {protagonist}'s group managed to support each other through the ordeal.

Through careful investigation and the help of newfound allies, {protagonist} uncovered the truth behind {antagonist} and their connection to the {item}. The revelation was both shocking and profound, changing everything {protagonist} thought they knew about their world and their place in it. Ancient records, hidden in forgotten libraries and guarded by mystical beings, revealed that the {item} was not just a tool of power, but a key to an ancient gateway that connected their world to others beyond imagination.

The discovery brought with it a sense of responsibility. {protagonist} realized they were not just a participant in the unfolding events but a key figure in determining the outcome. The weight of this responsibility was both daunting and empowering. They spent countless hours studying the {item}, learning to understand its intricate mechanisms and the ancient language inscribed upon its surface. Each symbol held meaning, each pattern a clue to its true purpose.

The truth, when it finally came to light, was more complex than anyone had imagined. {antagonist} was not simply an evil entity bent on destruction, but a being corrupted by power and isolation. Long ago, they had been a guardian of the realm, much like {protagonist} was destined to become. However, the burden of protecting others had slowly twisted their perspective until they believed that control, even through fear, was preferable to the chaos of freedom. This revelation did not excuse {antagonist}'s actions, but it did provide context that would prove crucial in the final confrontation.

{protagonist} realized that defeating {antagonist} would not be enough - they would need to find a way to heal the corruption that had taken root in their soul. This realization led to extensive research into ancient healing rituals and the nature of corrupted power. The group consulted with sages, mystics, and even some of {antagonist}'s former allies who had managed to escape their influence.

As word of {protagonist}'s quest spread, more allies joined their cause. Villages that had been living in fear for generations sent their bravest warriors. Scholars from distant lands arrived with ancient texts that shed new light on the prophecies. Even some who had previously served {antagonist}, disillusioned by the increasing cruelty of their master, defected to join the growing army of resistance. The diversity of the group was remarkable - warriors, scholars, healers, craftsmen, and common folk all united by a shared desire to see peace restored to their world.

The preparation for the final battle was extensive. Weapons had to be forged, strategies had to be planned, and morale had to be maintained. {protagonist} found themselves not just as a warrior, but as a leader, inspiring others with their vision of a better world. The weight of this responsibility was immense, but {protagonist} drew strength from the faith that others placed in them. They spent long hours in consultation with their advisors, reviewing battle plans and contingency measures, always mindful that the fate of countless lives rested on their decisions.

During this time, {protagonist} also deepened their understanding of the {item}. Through careful study and meditation, they learned to harness its power without being consumed by it. The {item} was not just a tool, but a key - a key to unlocking the potential for good that existed in all living beings. {protagonist} discovered that the {item} responded not just to their will, but to their intentions, amplifying their positive emotions while resisting attempts to use it for selfish purposes.

Armed with knowledge and strengthened by alliances, {protagonist} confronted {antagonist} in a final battle that would determine the fate of all. The confrontation took place in a location of great significance, where the power of the {item} could be fully realized. The ancient battlefield, scarred by previous conflicts, seemed to pulse with latent energy that resonated with the {item}'s presence. The very air crackled with magical forces as the two opposing sides faced each other across the field.

The battle was not just physical but also philosophical, as {protagonist} had to convince {antagonist} that there is a better path forward. Through courage, compassion, and wisdom, {protagonist} found a way to resolve the conflict without total destruction. The confrontation was as much a battle of ideas as it was of weapons, with each side trying to convince the other of the righteousness of their cause. {protagonist} spoke of hope, of the possibility of redemption, and of a future where all beings could live in harmony.

The battle was fierce and prolonged. {antagonist} wielded powers that had been honed over centuries of darkness, and their minions were numerous and fanatically loyal. But {protagonist} was not alone. The army of light, composed of beings from all walks of life who had chosen to stand against tyranny, fought with a passion that could not be matched by those who served out of fear. The clash of arms echoed across the landscape, and the very ground shook with the force of their conflict.

As the battle raged, {protagonist} realized that brute force would not be enough to defeat {antagonist}. The true victory would come not from destruction, but from redemption. Using the power of the {item} and the strength of their convictions, {protagonist} reached out to {antagonist} not with weapons, but with compassion. They spoke of the good that still existed within {antagonist}, of the guardian they had once been, and of the possibility of returning to that noble path.

With {antagonist} defeated and the immediate threat neutralized, {protagonist} faced the task of rebuilding what had been damaged. The {item} was secured in a place where it could be studied and protected for future generations. {protagonist} established a new order that would prevent similar conflicts from arising. Working with allies, they created institutions dedicated to {theme}, ensuring that the lessons learned would benefit others. The new order emphasized cooperation, mutual respect, and the protection of individual freedoms.

The process of rebuilding was long and arduous. Entire cities had to be reconstructed, societies had to be reformed, and trust had to be rebuilt between communities that had been divided by {antagonist}'s influence. But {protagonist} approached each challenge with the same determination that had carried them through their quest. They worked tirelessly to ensure that the mistakes of the past would not be repeated, establishing checks and balances to prevent any single individual from accumulating too much power.

New laws were enacted to ensure that no single being could accumulate enough power to threaten the peace again. Educational institutions were established to teach the values of cooperation and mutual respect. Trade routes were reopened to foster economic interdependence between different regions. Cultural exchanges were encouraged to promote understanding between diverse communities, and festivals were organized to celebrate the unity that had been achieved through their struggles.

Years later, as {protagonist} looked back on their journey, they reflected on how the discovery of the {item} had transformed not only their life but the lives of countless others. The adventure had taught them that true heroism lies not in seeking glory but in serving others and protecting what matters most. They had learned that even the most daunting challenges could be overcome through perseverance, compassion, and the support of good friends.

The story of {protagonist} became legend, passed down through generations as a reminder that ordinary individuals can achieve extraordinary things when guided by courage, compassion, and a commitment to {theme}. {protagonist} had aged considerably since their quest began, but their spirit remained as strong as ever. They had established a school where they taught young people about the importance of standing up for what is right, even when the odds seem insurmountable.

Many of their students went on to become leaders in their own right, carrying forward the principles that {protagonist} had fought so hard to establish. Some became scholars who continued the work of preserving ancient knowledge, while others became warriors who protected the realm from new threats. Still others became healers, teachers, and craftspeople who contributed to the prosperity and well-being of their communities.

The {item}, now housed in a great library that served as a center of learning and wisdom, continued to inspire new generations. Scholars studied its mysteries, artists created works inspired by its beauty, and philosophers pondered the deeper meanings hidden within its symbols. The library became a place of pilgrimage for those seeking knowledge and enlightenment, and its halls echoed with the footsteps of countless visitors who came to learn from the wisdom of the past.

The story of {protagonist} serves as a beacon of hope for all who face seemingly insurmountable challenges. It reminds us that even in the darkest times, there are those who will stand up for what is right. It teaches us that true strength comes not from power over others, but from the courage to protect those who cannot protect themselves. The legacy of {protagonist} continues to this day, in the institutions they founded, the laws they enacted, and the hearts of those who remember their sacrifice.

Their story is a testament to the power of one individual to change the world, and a reminder that each of us has the potential to be a hero in our own way. As new challenges arise and new heroes emerge, the tale of {protagonist} and the {item} will continue to inspire courage, wisdom, and compassion in all who hear it. For as long as there are those willing to stand against darkness, the light of hope will never be extinguished.

In the years that followed, the realm prospered under the new order established by {protagonist}. Trade flourished, knowledge was shared freely, and communities worked together to solve common problems. The scars of the past slowly healed, though the memory of what had been endured never faded completely. Monuments were erected to honor those who had fallen in the struggle against {antagonist}, and their names were inscribed in the Hall of Remembrance where future generations could learn from their sacrifice.

{protagonist} continued their work well into their twilight years, mentoring new leaders and ensuring that the institutions they had created would endure long after they were gone. They understood that true change required not just the defeat of evil, but the active cultivation of good in its place. Their legacy lived on not just in the stories told about them, but in the better world they had helped to create.

The {item} remained a source of wonder and inspiration for scholars and seekers of knowledge. Its mysteries continued to unfold as new generations brought fresh perspectives to its study. Some discovered new applications for its power, while others found deeper philosophical meanings in its ancient symbols. The {item} had become more than just a tool - it was a symbol of hope and the potential for positive change that exists within all beings.

As centuries passed, the tale of {protagonist} and the {item} evolved, with each generation adding their own interpretations and insights. But the core message remained unchanged - that courage, compassion, and wisdom can overcome even the greatest challenges, and that each individual has the power to make a difference in the world. The story continued to inspire new heroes, ensuring that the light of hope would never be extinguished as long as there were those willing to stand against darkness."""

    return story

# Add endpoints for saving ratings and feedback
@app.route("/save_rating", methods=["POST"])
def save_rating():
    print("=== SAVE RATING ROUTE CALLED ===")  # Debug print
    print("Request method:", request.method)  # Debug print
    print("Request headers:", dict(request.headers))  # Debug print
    print("Session keys:", list(session.keys()))  # Debug print
    print("Logged in:", 'loggedin' in session)  # Debug print
    print("User ID:", session.get('user_id') if 'loggedin' in session else 'Not logged in')  # Debug print
    
    if 'loggedin' not in session:
        print("User not logged in")  # Debug print
        return jsonify({'success': False, 'message': 'Please log in first'})
    
    try:
        data = request.get_json()
        print("Received data:", data)  # Debug print
        
        book_id = data.get('book_id')
        rating = data.get('rating')
        
        print(f"Saving rating: book_id={book_id}, rating={rating}, user_id={session.get('user_id')}")  # Debug print
        
        if not book_id or not rating:
            print("Missing book_id or rating")  # Debug print
            return jsonify({'success': False, 'message': 'Book ID and rating are required'})
        
        # Validate rating is between 1 and 5
        rating = int(rating)
        if rating < 1 or rating > 5:
            print("Invalid rating value")  # Debug print
            return jsonify({'success': False, 'message': 'Rating must be between 1 and 5'})
        
        cur = mysql.connection.cursor()
        
        # Check if user has already rated this book
        cur.execute(
            "SELECT rating_id FROM book_ratings WHERE user_id = %s AND book_id = %s",
            (session['user_id'], book_id)
        )
        existing_rating = cur.fetchone()
        print("Existing rating:", existing_rating)  # Debug print
        
        if existing_rating:
            print(f"Updating existing rating: {existing_rating[0]}")  # Debug print
            # Update existing rating
            cur.execute(
                "UPDATE book_ratings SET rating = %s, rated_at = NOW() WHERE rating_id = %s",
                (rating, existing_rating[0])
            )
        else:
            print("Inserting new rating")  # Debug print
            # Insert new rating
            cur.execute(
                "INSERT INTO book_ratings (user_id, book_id, rating) VALUES (%s, %s, %s)",
                (session['user_id'], book_id, rating)
            )
        
        mysql.connection.commit()
        cur.close()
        
        print("Rating saved successfully")  # Debug print
        return jsonify({'success': True, 'message': 'Rating saved successfully'})
        
    except Exception as e:
        print(f"Error saving rating: {str(e)}")  # Debug print
        import traceback
        traceback.print_exc()  # Print full traceback
        return jsonify({'success': False, 'message': 'An error occurred: ' + str(e)})

@app.route("/save_feedback", methods=["POST"])
def save_feedback():
    print("=== SAVE FEEDBACK ROUTE CALLED ===")  # Debug print
    print("Request method:", request.method)  # Debug print
    print("Request headers:", dict(request.headers))  # Debug print
    print("Session keys:", list(session.keys()))  # Debug print
    print("Logged in:", 'loggedin' in session)  # Debug print
    print("User ID:", session.get('user_id') if 'loggedin' in session else 'Not logged in')  # Debug print
    
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'})
    
    try:
        data = request.get_json()
        book_id = data.get('book_id')
        feedback = data.get('feedback')
        
        print(f"Saving feedback: book_id={book_id}, feedback={feedback}, user_id={session.get('user_id')}")  # Debug print
        
        if not book_id or not feedback:
            return jsonify({'success': False, 'message': 'Book ID and feedback are required'})
        
        # Validate feedback length
        if len(feedback) < 10:
            return jsonify({'success': False, 'message': 'Feedback must be at least 10 characters long'})
        
        cur = mysql.connection.cursor()
        
        # Insert feedback
        cur.execute(
            "INSERT INTO book_feedback (user_id, book_id, feedback_text) VALUES (%s, %s, %s)",
            (session['user_id'], book_id, feedback)
        )
        
        mysql.connection.commit()
        cur.close()
        
        print("Feedback saved successfully")  # Debug print
        return jsonify({'success': True, 'message': 'Feedback saved successfully'})
        
    except Exception as e:
        print(f"Error saving feedback: {str(e)}")  # Debug print
        import traceback
        traceback.print_exc()  # Print full traceback
        return jsonify({'success': False, 'message': 'An error occurred: ' + str(e)})

# Route to save reading progress
@app.route("/save_reading_progress", methods=["POST"])
def save_reading_progress():
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'})
    
    try:
        data = request.get_json()
        book_id = data.get('book_id')
        progress = data.get('progress')
        
        print(f"save_reading_progress called with book_id: {book_id}, progress: {progress}")  # Debug log
        
        if not book_id or progress is None:
            print("Missing book_id or progress")  # Debug log
            return jsonify({'success': False, 'message': 'Book ID and progress are required'})
        
        # Validate progress is between 0 and 100
        progress = int(progress)
        if progress < 0 or progress > 100:
            print(f"Invalid progress value: {progress}")  # Debug log
            return jsonify({'success': False, 'message': 'Progress must be between 0 and 100'})
        
        cur = mysql.connection.cursor()
        
        if progress == 0:
            # When progress is 0, delete the record to remove from continue reading
            print(f"Deleting reading progress record for book_id: {book_id}")  # Debug log
            cur.execute(
                "DELETE FROM reading_progress WHERE user_id = %s AND book_id = %s",
                (session['user_id'], book_id)
            )
            rows_affected = cur.rowcount
            print(f"Deleted {rows_affected} rows from reading_progress")  # Debug log
            
            # Also delete from reading_positions to fully remove the book
            print(f"Deleting reading position record for book_id: {book_id}")  # Debug log
            cur.execute(
                "DELETE FROM reading_positions WHERE user_id = %s AND book_id = %s",
                (session['user_id'], book_id)
            )
            rows_affected = cur.rowcount
            print(f"Deleted {rows_affected} rows from reading_positions")  # Debug log
        else:
            # Check if user has already saved progress for this book
            print(f"Updating/inserting reading progress record for book_id: {book_id}, progress: {progress}")  # Debug log
            cur.execute(
                "SELECT progress_id FROM reading_progress WHERE user_id = %s AND book_id = %s",
                (session['user_id'], book_id)
            )
            existing_progress = cur.fetchone()
            
            if existing_progress:
                # Update existing progress
                print(f"Updating existing progress record with progress_id: {existing_progress[0]}")  # Debug log
                cur.execute(
                    "UPDATE reading_progress SET progress_percentage = %s, last_read = NOW() WHERE progress_id = %s",
                    (progress, existing_progress[0])
                )
            else:
                # Insert new progress record
                print(f"Inserting new progress record")  # Debug log
                cur.execute(
                    "INSERT INTO reading_progress (user_id, book_id, progress_percentage) VALUES (%s, %s, %s)",
                    (session['user_id'], book_id, progress)
                )
        
        mysql.connection.commit()
        cur.close()
        
        print(f"Reading progress saved successfully for book_id: {book_id}")  # Debug log
        return jsonify({'success': True, 'message': 'Reading progress saved successfully'})
        
    except Exception as e:
        print(f"Error in save_reading_progress: {str(e)}")  # Debug log
        import traceback
        traceback.print_exc()  # Print full traceback
        return jsonify({'success': False, 'message': 'An error occurred: ' + str(e)})

# Route to get reading progress for a book
@app.route("/get_reading_progress/<int:book_id>")
def get_reading_progress(book_id):
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'})
    
    try:
        cur = mysql.connection.cursor()
        
        # Get reading progress for this book
        cur.execute(
            "SELECT progress_percentage, last_read FROM reading_progress WHERE user_id = %s AND book_id = %s",
            (session['user_id'], book_id)
        )
        progress_data = cur.fetchone()
        cur.close()
        
        if progress_data:
            return jsonify({
                'success': True,
                'progress': progress_data[0],
                'last_read': progress_data[1].isoformat() if progress_data[1] else None
            })
        else:
            return jsonify({'success': True, 'progress': 0, 'last_read': None})
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred: ' + str(e)})

# Route to get books with reading progress for "Continue Reading" section
@app.route("/continue_reading_books")
def continue_reading_books():
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'})
    
    try:
        cur = mysql.connection.cursor()
        
        # Get books with reading progress between 1-99% (0% means removed, 100% means completed)
        print(f"Fetching continue reading books for user_id: {session['user_id']}")  # Debug log
        cur.execute(
            """SELECT bt.book_id, bt.title, bt.author, bt.genre, bt.ISBN,
                      rp.progress_percentage,
                      rp.last_read
               FROM book_table bt
               JOIN reading_progress rp ON bt.book_id = rp.book_id
               WHERE rp.user_id = %s 
               AND rp.progress_percentage > 0 
               AND rp.progress_percentage < 100
               ORDER BY rp.last_read DESC
               LIMIT 10""",
            (session['user_id'],)
        )
        books_data = cur.fetchall()
        cur.close()
        
        print(f"Found {len(books_data)} books in continue reading")  # Debug log
        continue_reading_books = []
        for book in books_data:
            book_info = {
                'book_id': book[0],
                'title': book[1],
                'author': book[2],
                'genre': book[3],
                'isbn': book[4],
                'progress_percentage': book[5],
                'last_read': book[6].isoformat() if book[6] else None
            }
            print(f"Book: {book_info['title']} (ID: {book_info['book_id']}) - Progress: {book_info['progress_percentage']}%")  # Debug log
            continue_reading_books.append(book_info)
        
        # If we don't have enough books, also check for books with reading positions but no progress
        if len(continue_reading_books) < 10:
            cur = mysql.connection.cursor()
            cur.execute(
                """SELECT bt.book_id, bt.title, bt.author, bt.genre, bt.ISBN,
                          0 as progress_percentage,
                          pos.saved_at as last_read
                   FROM book_table bt
                   JOIN reading_positions pos ON bt.book_id = pos.book_id
                   LEFT JOIN reading_progress rp ON bt.book_id = rp.book_id AND rp.user_id = %s
                   WHERE pos.user_id = %s 
                   AND rp.progress_id IS NULL
                   AND pos.position IS NOT NULL
                   ORDER BY pos.saved_at DESC
                   LIMIT %s""",
                (session['user_id'], session['user_id'], 10 - len(continue_reading_books))
            )
            additional_books = cur.fetchall()
            cur.close()
            
            for book in additional_books:
                book_info = {
                    'book_id': book[0],
                    'title': book[1],
                    'author': book[2],
                    'genre': book[3],
                    'isbn': book[4],
                    'progress_percentage': book[5],
                    'last_read': book[6].isoformat() if book[6] else None
                }
                continue_reading_books.append(book_info)
        
        return jsonify({'success': True, 'continue_reading_books': continue_reading_books})
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred: ' + str(e)})

# Route to serve the continue reading page
@app.route("/continue_reading_page")
def continue_reading_page():
    if 'loggedin' not in session:
        flash("Please log in to view your continue reading books.", "error")
        return redirect(url_for('login'))
    
    return render_template('continue_reading.html', username=session.get('username', 'User'))

# Route to serve the recently rated page
@app.route("/recently_rated_page")
def recently_rated_page():
    if 'loggedin' not in session:
        flash("Please log in to view your recently rated books.", "error")
        return redirect(url_for('login'))
    
    return render_template('recently_rated.html', username=session.get('username', 'User'))

# Route to get reading history for a user
@app.route("/reading_history")
def reading_history():
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'})
    
    try:
        cur = mysql.connection.cursor()
        
        # Get all books with reading progress for this user, ordered by last read date
        cur.execute(
            """SELECT bt.book_id, bt.title, bt.author, bt.genre, bt.ISBN,
                      rp.progress_percentage,
                      rp.last_read
               FROM book_table bt
               JOIN reading_progress rp ON bt.book_id = rp.book_id
               WHERE rp.user_id = %s 
               AND rp.progress_percentage > 0
               ORDER BY rp.last_read DESC""",
            (session['user_id'],)
        )
        books_data = cur.fetchall()
        cur.close()
        
        reading_history_books = []
        for book in books_data:
            book_info = {
                'book_id': book[0],
                'title': book[1],
                'author': book[2],
                'genre': book[3],
                'isbn': book[4],
                'progress_percentage': book[5],
                'last_read': book[6].isoformat() if book[6] else None
            }
            reading_history_books.append(book_info)
        
        return jsonify({'success': True, 'reading_history': reading_history_books})
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred: ' + str(e)})

# Route to serve the reading history page
@app.route("/reading_history_page")
def reading_history_page():
    if 'loggedin' not in session:
        flash("Please log in to view your reading history.", "error")
        return redirect(url_for('login'))
    
    return render_template('reading_history.html', username=session.get('username', 'User'))
# Route to serve the continue reading page
@app.route("/continue_reading")
def continue_reading_page():
    if 'loggedin' not in session:
        flash("Please log in to view your reading progress.", "error")
        return redirect(url_for('login'))
    
    return render_template('continue_reading.html', username=session.get('username', 'User'))

# Route to get recently rated books for a user
@app.route("/recently_rated")
def recently_rated():
    print("=== RECENTLY RATED ROUTE CALLED ===")  # Debug print
    print("Session keys:", list(session.keys()))  # Debug print
    print("Logged in:", 'loggedin' in session)  # Debug print
    print("User ID:", session.get('user_id') if 'loggedin' in session else 'Not logged in')  # Debug print
    
    if 'loggedin' not in session:
        print("User not logged in for recently rated")  # Debug print
        return jsonify({'success': False, 'message': 'Please log in to view your recently rated books.'})
    
    try:
        cur = mysql.connection.cursor()
        # Get recently rated books with book details, ordered by rating date (most recent first)
        # Limit to 10 most recent ratings
        cur.execute(
            """SELECT br.rating_id, br.book_id, br.rating, br.rated_at, 
                      bt.title, bt.author, bt.genre, bt.ISBN
               FROM book_ratings br
               JOIN book_table bt ON br.book_id = bt.book_id
               WHERE br.user_id = %s
               ORDER BY br.rated_at DESC
               LIMIT 10""",
            (session['user_id'],)
        )
        ratings_data = cur.fetchall()
        print("Ratings data fetched:", ratings_data)  # Debug print
        cur.close()
        
        recently_rated_books = []
        for rating in ratings_data:
            book_info = {
                'rating_id': rating[0],
                'book_id': rating[1],
                'rating': rating[2],
                'rated_at': rating[3].isoformat() if rating[3] else None,
                'title': rating[4],
                'author': rating[5],
                'genre': rating[6],
                'isbn': rating[7]
            }
            recently_rated_books.append(book_info)
        
        print("Recently rated books:", recently_rated_books)  # Debug print
        return jsonify({'success': True, 'recently_rated': recently_rated_books})
        
    except Exception as e:
        print(f"Error in recently_rated route: {str(e)}")  # Debug print
        import traceback
        traceback.print_exc()  # Print full traceback
        return jsonify({'success': False, 'message': 'An error occurred: ' + str(e)})

# Route to serve the recently rated page
@app.route("/recently_rated_page")
def recently_rated_page():
    if 'loggedin' not in session:
        flash("Please log in to view your recently rated books.", "error")
        return redirect(url_for('login'))
    
    return render_template('recently_rated.html', username=session.get('username', 'User'))

# Route to save reading position
@app.route("/save_reading_position", methods=["POST"])
def save_reading_position():
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'})
    
    try:
        data = request.get_json()
        book_id = data.get('book_id')
        position = data.get('position')
        
        if not book_id or position is None:
            return jsonify({'success': False, 'message': 'Book ID and position are required'})
        
        # Validate position is a number
        position = float(position)
        if position < 0:
            return jsonify({'success': False, 'message': 'Position must be a positive number'})
        
        cur = mysql.connection.cursor()
        
        # Check if user has already saved a position for this book
        cur.execute(
            "SELECT position_id FROM reading_positions WHERE user_id = %s AND book_id = %s",
            (session['user_id'], book_id)
        )
        existing_position = cur.fetchone()
        
        if existing_position:
            # Update existing position
            cur.execute(
                "UPDATE reading_positions SET position = %s, saved_at = NOW() WHERE position_id = %s",
                (position, existing_position[0])
            )
        else:
            # Insert new position record
            cur.execute(
                "INSERT INTO reading_positions (user_id, book_id, position) VALUES (%s, %s, %s)",
                (session['user_id'], book_id, position)
            )
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True, 'message': 'Reading position saved successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred: ' + str(e)})

# Route to get reading position for a book
@app.route("/get_reading_position/<int:book_id>")
def get_reading_position(book_id):
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Please log in first'})
    
    try:
        cur = mysql.connection.cursor()
        
        # Get reading position for this book
        cur.execute(
            "SELECT position, saved_at FROM reading_positions WHERE user_id = %s AND book_id = %s",
            (session['user_id'], book_id)
        )
        position_data = cur.fetchone()
        cur.close()
        
        if position_data:
            return jsonify({
                'success': True,
                'position': float(position_data[0]),
                'saved_at': position_data[1].isoformat() if position_data[1] else None
            })
        else:
            return jsonify({'success': True, 'position': None, 'saved_at': None})
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred: ' + str(e)})

# Test route for highlighting functionality
@app.route("/test_highlight.html")
def test_highlight():
    return render_template('test_highlight.html')

@app.route("/test_view_ratings")
def test_view_ratings():
    try:
        cur = mysql.connection.cursor()
        
        # Get all ratings with user and book information
        cur.execute("""
            SELECT 
                br.rating_id,
                br.rating,
                br.rated_at,
                u.username,
                bt.title,
                bt.author,
                bt.isbn
            FROM book_ratings br
            JOIN user_table u ON br.user_id = u.user_id
            JOIN book_table bt ON br.book_id = bt.book_id
            ORDER BY br.rated_at DESC
        """)
        
        ratings_data = cur.fetchall()
        
        # Get histogram data (rating distribution)
        cur.execute("""
            SELECT 
                rating,
                COUNT(*) as count
            FROM book_ratings
            GROUP BY rating
            ORDER BY rating
        """)
        
        histogram_data = cur.fetchall()
        cur.close()
        
        ratings_count = len(ratings_data)
        
        # Format the data for the template
        ratings = []
        for rating in ratings_data:
            ratings.append({
                'rating_id': rating[0],
                'rating': rating[1],
                'rated_at': rating[2],
                'username': rating[3],
                'title': rating[4],
                'author': rating[5],
                'isbn': rating[6]
            })
        
        # Format histogram data
        histogram = {}
        for row in histogram_data:
            histogram[row[0]] = row[1]
        
        # Ensure all ratings from 1-5 are represented
        for i in range(1, 6):
            if i not in histogram:
                histogram[i] = 0
        
        return render_template('view_ratings.html', ratings=ratings, histogram=histogram, username='Test User')
        
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/admin/view_ratings", methods=['GET', 'POST'])
@app.route("/view_ratings", methods=['GET', 'POST'])
def view_ratings():
    # Check if user is admin
    if 'loggedin' not in session or session.get('role') != 'admin':
        flash('You must be an admin to view this page.', 'error')
        return redirect(url_for('admin_home'))
    
    # Get search query if provided
    search_query = request.args.get('search', '').strip()
    
    try:
        cur = mysql.connection.cursor()
        
        # Get ratings with user and book information, with optional search filter
        if search_query:
            # Search by book title, ISBN, or book ID
            cur.execute("""
                SELECT 
                    br.rating_id,
                    br.rating,
                    br.rated_at,
                    u.username,
                    bt.title,
                    bt.author,
                    bt.isbn,
                    bt.book_id
                FROM book_ratings br
                JOIN user_table u ON br.user_id = u.user_id
                JOIN book_table bt ON br.book_id = bt.book_id
                WHERE bt.title LIKE %s OR bt.isbn LIKE %s OR bt.book_id LIKE %s
                ORDER BY br.rated_at DESC
            """, (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
        else:
            # Get all ratings with user and book information
            cur.execute("""
                SELECT 
                    br.rating_id,
                    br.rating,
                    br.rated_at,
                    u.username,
                    bt.title,
                    bt.author,
                    bt.isbn,
                    bt.book_id
                FROM book_ratings br
                JOIN user_table u ON br.user_id = u.user_id
                JOIN book_table bt ON br.book_id = bt.book_id
                ORDER BY br.rated_at DESC
            """)
        
        ratings_data = cur.fetchall()
        
        # Get histogram data (rating distribution) - filtered by search if applicable
        if search_query:
            cur.execute("""
                SELECT 
                    br.rating,
                    COUNT(*) as count
                FROM book_ratings br
                JOIN book_table bt ON br.book_id = bt.book_id
                WHERE bt.title LIKE %s OR bt.isbn LIKE %s OR bt.book_id LIKE %s
                GROUP BY br.rating
                ORDER BY br.rating
            """, (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
        else:
            cur.execute("""
                SELECT 
                    rating,
                    COUNT(*) as count
                FROM book_ratings
                GROUP BY rating
                ORDER BY rating
            """)
        
        histogram_data = cur.fetchall()
        cur.close()
        
        # Format the data for the template
        ratings = []
        for rating in ratings_data:
            ratings.append({
                'rating_id': rating[0],
                'rating': rating[1],
                'rated_at': rating[2],
                'username': rating[3],
                'title': rating[4],
                'author': rating[5],
                'isbn': rating[6]
            })
        
        # Format histogram data
        histogram = {}
        for row in histogram_data:
            histogram[row[0]] = row[1]
        
        # Ensure all ratings from 1-5 are represented
        for i in range(1, 6):
            if i not in histogram:
                histogram[i] = 0
        
        return render_template('view_ratings.html', ratings=ratings, histogram=histogram, username=session.get('username', 'Admin'), search_query=search_query)
        
    except Exception as e:
        flash(f'An error occurred while fetching ratings: {str(e)}', 'error')
        return redirect(url_for('admin_home'))

@app.route("/admin/view_feedback")
def view_feedback():
    # Check if user is admin
    if 'loggedin' not in session or session.get('role') != 'admin':
        flash('You must be an admin to view this page.', 'error')
        return redirect(url_for('admin_home'))
    
    try:
        cur = mysql.connection.cursor()
        
        # Get all feedback with user and book information
        cur.execute("""
            SELECT 
                bf.feedback_id,
                bf.feedback_text,
                bf.submitted_at,
                u.username,
                u.email,
                bt.title,
                bt.author,
                bt.isbn
            FROM book_feedback bf
            JOIN user_table u ON bf.user_id = u.user_id
            JOIN book_table bt ON bf.book_id = bt.book_id
            ORDER BY bf.submitted_at DESC
        """)
        
        feedback_data = cur.fetchall()
        cur.close()
        
        # Format the data for the template
        feedbacks = []
        for feedback in feedback_data:
            feedbacks.append({
                'feedback_id': feedback[0],
                'feedback_text': feedback[1],
                'submitted_at': feedback[2],
                'username': feedback[3],
                'email': feedback[4],
                'title': feedback[5],
                'author': feedback[6],
                'isbn': feedback[7]
            })
        
        return render_template('view_feedback.html', feedbacks=feedbacks, username=session.get('username', 'Admin'))
        
    except Exception as e:
        flash(f'An error occurred while fetching feedback: {str(e)}', 'error')
        return redirect(url_for('admin_home'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
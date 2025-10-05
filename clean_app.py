# Create a clean version of app.py with proper structure

# Read the original file
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the section where we need to insert the reading history routes
# We'll place them after the recently_rated_page route

# Find the recently_rated_page route
insert_index = -1
for i, line in enumerate(lines):
    if line.strip() == "# Route to serve the recently rated page":
        # Find the end of this route
        j = i + 1
        while j < len(lines) and not lines[j].strip().startswith("# Route"):
            j += 1
        insert_index = j
        break

if insert_index != -1:
    # Insert the reading history routes
    reading_history_routes = [
        "\n# Route to get reading history for a user\n",
        "@app.route(\"/reading_history\")\n",
        "def reading_history():\n",
        "    if 'loggedin' not in session:\n",
        "        return jsonify({'success': False, 'message': 'Please log in first'})\n",
        "    \n",
        "    try:\n",
        "        cur = mysql.connection.cursor()\n",
        "        \n",
        "        # Get all books with reading progress for this user, ordered by last read date\n",
        "        cur.execute(\n",
        "            \"\"\"SELECT bt.book_id, bt.title, bt.author, bt.genre, bt.ISBN,\n",
        "                      rp.progress_percentage,\n",
        "                      rp.last_read\n",
        "               FROM book_table bt\n",
        "               JOIN reading_progress rp ON bt.book_id = rp.book_id\n",
        "               WHERE rp.user_id = %s \n",
        "               AND rp.progress_percentage > 0\n",
        "               ORDER BY rp.last_read DESC\"\"\",\n",
        "            (session['user_id'],)\n",
        "        )\n",
        "        books_data = cur.fetchall()\n",
        "        cur.close()\n",
        "        \n",
        "        reading_history_books = []\n",
        "        for book in books_data:\n",
        "            book_info = {\n",
        "                'book_id': book[0],\n",
        "                'title': book[1],\n",
        "                'author': book[2],\n",
        "                'genre': book[3],\n",
        "                'isbn': book[4],\n",
        "                'progress_percentage': book[5],\n",
        "                'last_read': book[6].isoformat() if book[6] else None\n",
        "            }\n",
        "            reading_history_books.append(book_info)\n",
        "        \n",
        "        return jsonify({'success': True, 'reading_history': reading_history_books})\n",
        "        \n",
        "    except Exception as e:\n",
        "        return jsonify({'success': False, 'message': 'An error occurred: ' + str(e)})\n",
        "\n",
        "# Route to serve the reading history page\n",
        "@app.route(\"/reading_history_page\")\n",
        "def reading_history_page():\n",
        "    if 'loggedin' not in session:\n",
        "        flash(\"Please log in to view your reading history.\", \"error\")\n",
        "        return redirect(url_for('login'))\n",
        "    \n",
        "    return render_template('reading_history.html', username=session.get('username', 'User'))\n"
    ]
    
    # Insert the routes
    for i, route_line in enumerate(reading_history_routes):
        lines.insert(insert_index + i, route_line)
    
    # Write the clean file
    with open('app_clean.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("Clean file written to app_clean.py")
else:
    print("Could not find the insertion point")
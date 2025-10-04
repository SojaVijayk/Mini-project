from app import read_books_csv

# Test book lookup in CSV
books = read_books_csv('data/books_data.csv')
print(f"Total books in CSV: {len(books)}")

# Print first 3 books
for i in range(min(3, len(books))):
    book = books[i]
    print(f"Book {i+1}:")
    print(f"  ID: {book['id']}")
    print(f"  Title: {book['title']}")
    print(f"  Author: {book['author']}")
    print(f"  Genre: {book['genre']}")
    print(f"  ISBN: {book['isbn']}")
    print()

# Test finding specific books
test_ids = [1, 2, 3, 100, 1000]
print("Testing book lookup by ID:")
for test_id in test_ids:
    found = False
    for book in books:
        if int(book['id']) == test_id:
            print(f"  Found book {test_id}: {book['title']} by {book['author']}")
            found = True
            break
    if not found:
        print(f"  Book {test_id} not found")
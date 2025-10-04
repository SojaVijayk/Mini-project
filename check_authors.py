from app import read_books_csv, get_unique_authors_and_genres

# Read books from CSV
books = read_books_csv('data/books_data.csv')
authors, genres = get_unique_authors_and_genres(books)

print(f'Total books: {len(books)}')
print(f'Total unique authors: {len(authors)}')

# Find authors with multiple books
authors_with_multiple_books = [a for a in authors if a['book_count'] > 1]
print(f'Authors with multiple books: {len(authors_with_multiple_books)}')

print('\nAuthors with multiple books:')
for author in authors_with_multiple_books:
    print(f'  {author["name"]}: {author["book_count"]} books')

# Show some sample books by one of these authors
if authors_with_multiple_books:
    sample_author = authors_with_multiple_books[0]['name']
    print(f'\nSample books by {sample_author}:')
    author_books = [book for book in books if book['author'] == sample_author]
    for i, book in enumerate(author_books[:5]):  # Show first 5 books
        print(f'  {i+1}. {book["title"]}')
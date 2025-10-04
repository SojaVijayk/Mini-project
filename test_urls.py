from flask import url_for
from app import app

# Test URL generation
with app.test_request_context():
    # Test recommended books URL
    recommended_url = url_for('recommended_books')
    print(f"Recommended books URL: {recommended_url}")
    
    # Test book description URL with a sample book ID
    book_desc_url = url_for('book_description', book_id=1)
    print(f"Book description URL (book_id=1): {book_desc_url}")
    
    # Test book description URL with another sample book ID
    book_desc_url2 = url_for('book_description', book_id=100)
    print(f"Book description URL (book_id=100): {book_desc_url2}")
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the story generation function
from app import generate_story_for_book

# Test the function with different inputs
test_cases = [
    ("The Dragon's Secret", "J.K. Rowling", "Fantasy"),
    ("Lost in the Shadows", "Stephen King", "Horror"),
    ("Love in Paris", "Jane Austen", "Romance"),
    ("The Mystery of Time", "Agatha Christie", "Mystery"),
    ("Journey to Mars", "Isaac Asimov", "Science Fiction")
]

print("Testing story generation function:")
print("=" * 50)

for i, (title, author, genre) in enumerate(test_cases, 1):
    print(f"\nTest Case {i}:")
    print(f"Title: {title}")
    print(f"Author: {author}")
    print(f"Genre: {genre}")
    
    story = generate_story_for_book(title, author, genre)
    print(f"Story Generated: {'SUCCESS' if story else 'FAILED'}")
    
    if story:
        # Show just the first few lines to verify it's unique
        lines = story.split('\n')
        print("First few lines:")
        for line in lines[:5]:
            print(f"  {line}")
    print("-" * 30)
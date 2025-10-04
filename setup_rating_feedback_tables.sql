-- Create table for book ratings
CREATE TABLE IF NOT EXISTS book_ratings (
    rating_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_table(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book_table(book_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_book_rating (user_id, book_id)
);

-- Create table for book feedback
CREATE TABLE IF NOT EXISTS book_feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    feedback_text TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_table(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book_table(book_id) ON DELETE CASCADE
);

-- Add indexes for better performance
CREATE INDEX idx_book_ratings_user_id ON book_ratings(user_id);
CREATE INDEX idx_book_ratings_book_id ON book_ratings(book_id);
CREATE INDEX idx_book_feedback_user_id ON book_feedback(user_id);
CREATE INDEX idx_book_feedback_book_id ON book_feedback(book_id);
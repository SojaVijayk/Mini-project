-- SQL script to create the reading progress table
-- Run this in your MySQL database to add the reading progress tracking functionality

USE book_engine;

CREATE TABLE IF NOT EXISTS reading_progress (
    progress_id INT(11) NOT NULL AUTO_INCREMENT,
    user_id INT(11) NOT NULL,
    book_id INT(11) NOT NULL,
    progress_percentage INT(11) NOT NULL DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    last_read TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (progress_id),
    UNIQUE KEY unique_user_book_progress (user_id, book_id),
    FOREIGN KEY (user_id) REFERENCES user_table(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book_table(book_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_book_id (book_id),
    INDEX idx_last_read (last_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
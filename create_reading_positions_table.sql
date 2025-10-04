-- SQL script to create the reading positions table
-- Run this in your MySQL database to add the manual reading position tracking functionality

USE book_engine;

CREATE TABLE IF NOT EXISTS reading_positions (
    position_id INT(11) NOT NULL AUTO_INCREMENT,
    user_id INT(11) NOT NULL,
    book_id INT(11) NOT NULL,
    position FLOAT NOT NULL,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (position_id),
    UNIQUE KEY unique_user_book_position (user_id, book_id),
    FOREIGN KEY (user_id) REFERENCES user_table(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book_table(book_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_book_id (book_id),
    INDEX idx_saved_at (saved_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
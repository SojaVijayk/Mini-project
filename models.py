# MySQL table schema for user accounts
# Run this SQL in your MySQL database to create the table

"""
CREATE TABLE user_table (
    userid INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(45) NOT NULL,
    password VARCHAR(45) NOT NULL,
    email VARCHAR(45) NOT NULL,
    phone_no VARCHAR(45) NOT NULL,
    preference VARCHAR(45) DEFAULT NULL,
    PRIMARY KEY (userid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
"""

# Python model (for reference, not used directly with flask_mysqldb)
class User:
    def __init__(self, userid, username, password, email, phone_no, preference=None):
        self.userid = userid
        self.username = username
        self.password = password
        self.email = email
        self.phone_no = phone_no
        self.preference = preference
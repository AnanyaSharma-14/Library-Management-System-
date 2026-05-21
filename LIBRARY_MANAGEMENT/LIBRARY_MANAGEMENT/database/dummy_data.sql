-- Library Management System Sample Dummy Data
-- Uses dynamic dates (CURDATE) so overdue alerts and due warnings work at any time of import!

USE library_db;

-- 1. Insert Users
INSERT INTO users (username, password, role) VALUES
('admin', 'admin123', 'admin'),
('user', 'user123', 'user'),
('student1', 'student123', 'user'),
('student2', 'student123', 'user')
ON DUPLICATE KEY UPDATE username=username;

-- 2. Insert Books
-- Clear existing books first to avoid conflicts in tests
DELETE FROM books;

-- Book 1: Available
INSERT INTO books (book_id, title, author, status, issued_to, issue_date, due_date)
VALUES (1, 'Harry Potter and the Sorcerer\'s Stone', 'J.K. Rowling', 'Available', NULL, NULL, NULL);

-- Book 2: Issued and Due Tomorrow (Triggers due reminder: <= 2 days left)
INSERT INTO books (book_id, title, author, status, issued_to, issue_date, due_date)
VALUES (2, 'Python Basics for Beginners', 'Al Sweigart', 'Issued', 'user', DATE_SUB(CURDATE(), INTERVAL 13 DAY), DATE_ADD(CURDATE(), INTERVAL 1 DAY));

-- Book 3: Issued and Overdue by 5 days (Triggers overdue alert and ₹25 fine)
INSERT INTO books (book_id, title, author, status, issued_to, issue_date, due_date)
VALUES (3, 'Web Development Guide', 'John Duckett', 'Issued', 'student1', DATE_SUB(CURDATE(), INTERVAL 19 DAY), DATE_SUB(CURDATE(), INTERVAL 5 DAY));

-- Book 4: Issued and Due in 6 days (Quiet, no warnings yet)
INSERT INTO books (book_id, title, author, status, issued_to, issue_date, due_date)
VALUES (4, 'Clean Code: A Handbook of Agile Software Craftsmanship', 'Robert C. Martin', 'Issued', 'user', DATE_SUB(CURDATE(), INTERVAL 8 DAY), DATE_ADD(CURDATE(), INTERVAL 6 DAY));

-- Book 5: Available (Recently returned)
INSERT INTO books (book_id, title, author, status, issued_to, issue_date, due_date)
VALUES (5, 'Database System Concepts', 'Abraham Silberschatz', 'Available', NULL, NULL, NULL);

-- 3. Seed Pre-calculated Fines & Notifications
DELETE FROM fines;
DELETE FROM notifications;

-- Pre-calculate fine for student1 (₹5/day * 5 days overdue = ₹25)
INSERT INTO fines (username, book_id, amount, status)
VALUES ('student1', 3, 25.00, 'Pending');

-- Pre-calculate past paid fine for user (₹10.00)
INSERT INTO fines (username, book_id, amount, status, paid_at)
VALUES ('user', 5, 10.00, 'Paid', DATE_SUB(CURDATE(), INTERVAL 2 DAY));

-- Seed active notifications
INSERT INTO notifications (username, message, type, is_read) VALUES
('user', 'Reminder: Your issued book \'Python Basics for Beginners\' must be returned within 2 days.', 'DueReminder', FALSE),
('student1', 'Your issued book \'Web Development Guide\' is overdue. Please return it immediately.', 'OverdueAlert', FALSE),
('student1', 'Fine Alert: You currently have ₹25 pending fine for late return.', 'FineAlert', FALSE),
('user', 'Welcome to the new Library Portal! Make sure to check your notifications.', 'Info', FALSE);

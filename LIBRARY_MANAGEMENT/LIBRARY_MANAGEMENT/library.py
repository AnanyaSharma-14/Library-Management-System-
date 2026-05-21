import json
import os
from datetime import datetime, timedelta
import config

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

BOOKS_FILE = 'books.json'
USERS_FILE = 'users.json'
NOTIFICATIONS_FILE = 'notifications.json'
FINES_FILE = 'fines.json'

class User:
    def __init__(self, username, password, role="user"):
        self.username = username
        self.password = password
        self.role = role

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "role": self.role
        }

    @staticmethod
    def from_dict(data):
        return User(data['username'], data['password'], data['role'])

class Book:
    def __init__(self, book_id, title, author, status="Available", issued_to=None, due_date=None, issue_date=None):
        self.book_id = str(book_id)
        self.title = title
        self.author = author
        self.status = status
        self.issued_to = issued_to
        self.due_date = due_date
        self.issue_date = issue_date

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "status": self.status,
            "issued_to": self.issued_to,
            "due_date": self.due_date,
            "issue_date": self.issue_date
        }

    @staticmethod
    def from_dict(data):
        return Book(
            book_id=data['book_id'],
            title=data['title'],
            author=data['author'],
            status=data['status'],
            issued_to=data.get('issued_to'),
            due_date=data.get('due_date'),
            issue_date=data.get('issue_date')
        )

class Library:
    def __init__(self):
        self.books = []
        self.users = []
        self.notifications = []
        self.fines = []
        self.mysql_connected = False
        self.db = None
        
        # Try connecting to MySQL
        self.connect_mysql()
        
        # Load local storage as fallback if MySQL fails
        if not self.mysql_connected:
            print("[!] MySQL failed to connect. Falling back to JSON local storage.")
            self.load_local_data()

    def connect_mysql(self):
        if not MYSQL_AVAILABLE:
            self.mysql_connected = False
            return
        try:
            self.db = mysql.connector.connect(**config.DB_CONFIG)
            self.mysql_connected = True
            print("[+] Successfully connected to MySQL Database!")
            # Ensure tables exist
            self.create_tables_if_needed()
        except Exception as e:
            print(f"[-] MySQL Connection Error: {e}")
            self.mysql_connected = False

    def create_tables_if_needed(self):
        if not self.mysql_connected or not self.db:
            return
        cursor = self.db.cursor()
        try:
            # 1. Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username VARCHAR(100) PRIMARY KEY,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL DEFAULT 'user'
                )
            """)
            # 2. Books table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    book_id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    author VARCHAR(255) NOT NULL,
                    status VARCHAR(50) NOT NULL DEFAULT 'Available',
                    issued_to VARCHAR(100) NULL,
                    issue_date DATE NULL,
                    due_date DATE NULL,
                    FOREIGN KEY (issued_to) REFERENCES users(username) ON DELETE SET NULL
                )
            """)
            # 3. Notifications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL,
                    message TEXT NOT NULL,
                    type VARCHAR(50) NOT NULL DEFAULT 'Info',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_read BOOLEAN NOT NULL DEFAULT FALSE,
                    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
                )
            """)
            # 4. Fines table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fines (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL,
                    book_id INT NOT NULL,
                    amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    paid_at TIMESTAMP NULL,
                    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE,
                    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
                )
            """)
            self.db.commit()
            
            # Seed default users
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin'), ('user', 'user123', 'user')")
                self.db.commit()
                print("[+] Default users seeded in MySQL.")
        except Exception as e:
            print(f"[-] Error creating tables in MySQL: {e}")
        finally:
            cursor.close()

    def get_cursor(self):
        # Refresh connection if closed
        try:
            self.db.ping(reconnect=True, attempts=3, delay=1)
            return self.db.cursor(dictionary=True)
        except Exception:
            self.connect_mysql()
            if self.mysql_connected:
                return self.db.cursor(dictionary=True)
            return None

    def load_local_data(self):
        # Load Books
        if os.path.exists(BOOKS_FILE):
            try:
                with open(BOOKS_FILE, 'r') as file:
                    self.books = [Book.from_dict(b) for b in json.load(file)]
            except Exception:
                self.books = []
        else:
            self.books = [Book("1", "Harry Potter", "J.K. Rowling")]
            self.save_books()

        # Load Users
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, 'r') as file:
                    self.users = [User.from_dict(u) for u in json.load(file)]
            except Exception:
                self.users = []
        else:
            self.users = [
                User("admin", "admin123", "admin"),
                User("user", "user123", "user")
            ]
            self.save_users()

        # Load Notifications
        if os.path.exists(NOTIFICATIONS_FILE):
            try:
                with open(NOTIFICATIONS_FILE, 'r') as file:
                    self.notifications = json.load(file)
            except Exception:
                self.notifications = []
        else:
            self.notifications = []
            self.save_notifications()

        # Load Fines
        if os.path.exists(FINES_FILE):
            try:
                with open(FINES_FILE, 'r') as file:
                    self.fines = json.load(file)
            except Exception:
                self.fines = []
        else:
            self.fines = []
            self.save_fines()

    def save_books(self):
        if self.mysql_connected:
            return
        with open(BOOKS_FILE, 'w') as file:
            json.dump([book.to_dict() for book in self.books], file, indent=4)

    def save_users(self):
        if self.mysql_connected:
            return
        with open(USERS_FILE, 'w') as file:
            json.dump([user.to_dict() for user in self.users], file, indent=4)

    def save_notifications(self):
        if self.mysql_connected:
            return
        with open(NOTIFICATIONS_FILE, 'w') as file:
            json.dump(self.notifications, file, indent=4)

    def save_fines(self):
        if self.mysql_connected:
            return
        with open(FINES_FILE, 'w') as file:
            json.dump(self.fines, file, indent=4)

    def authenticate(self, username, password):
        if self.mysql_connected:
            cursor = self.get_cursor()
            if not cursor:
                return None
            try:
                cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
                row = cursor.fetchone()
                if row:
                    return User(row['username'], row['password'], row['role'])
            except Exception as e:
                print(f"Auth error: {e}")
            finally:
                cursor.close()
            return None
        else:
            for user in self.users:
                if user.username == username and user.password == password:
                    return user
            return None

    def add_book(self, title, author):
        if self.mysql_connected:
            cursor = self.get_cursor()
            if not cursor:
                return False
            try:
                cursor.execute("INSERT INTO books (title, author, status) VALUES (%s, %s, 'Available')", (title, author))
                self.db.commit()
                return True
            except Exception as e:
                print(f"Add book MySQL error: {e}")
                return False
            finally:
                cursor.close()
        else:
            book_id = str(len(self.books) + 1)
            new_book = Book(book_id, title, author)
            self.books.append(new_book)
            self.save_books()
            return True

    def get_all_books(self):
        if self.mysql_connected:
            cursor = self.get_cursor()
            if not cursor:
                return []
            try:
                cursor.execute("SELECT * FROM books")
                rows = cursor.fetchall()
                # Format dates nicely
                for r in rows:
                    if r['issue_date']:
                        r['issue_date'] = r['issue_date'].strftime("%Y-%m-%d")
                    if r['due_date']:
                        r['due_date'] = r['due_date'].strftime("%Y-%m-%d")
                return rows
            except Exception as e:
                print(f"Get books MySQL error: {e}")
                return []
            finally:
                cursor.close()
        else:
            return [book.to_dict() for book in self.books]

    def search_books(self, query):
        query = query.lower()
        all_books = self.get_all_books()
        return [b for b in all_books if query in b['title'].lower() or query in b['author'].lower()]

    def issue_book(self, username, book_id):
        issue_date = datetime.now().strftime("%Y-%m-%d")
        due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

        if self.mysql_connected:
            cursor = self.get_cursor()
            if not cursor:
                return False
            try:
                # Check availability
                cursor.execute("SELECT status FROM books WHERE book_id = %s", (book_id,))
                book = cursor.fetchone()
                if not book or book['status'] != 'Available':
                    return False

                cursor.execute("""
                    UPDATE books 
                    SET status = 'Issued', issued_to = %s, issue_date = %s, due_date = %s
                    WHERE book_id = %s
                """, (username, issue_date, due_date, book_id))
                self.db.commit()
                
                # Check for due alerts or overdue immediately (triggers routine checks)
                self.run_notification_checks_for_user(username)
                return True
            except Exception as e:
                print(f"Issue book MySQL error: {e}")
                return False
            finally:
                cursor.close()
        else:
            for book in self.books:
                if book.book_id == str(book_id):
                    if book.status == "Available":
                        book.status = "Issued"
                        book.issued_to = username
                        book.issue_date = issue_date
                        book.due_date = due_date
                        self.save_books()
                        self.run_notification_checks_for_user(username)
                        return True
                    break
            return False

    def return_book(self, username, book_id):
        # Calculate Fines and Clear Notifications
        fine_amount = 0.0
        returned_book_title = ""

        # Get book first to check due date
        book_data = None
        if self.mysql_connected:
            cursor = self.get_cursor()
            if not cursor:
                return False, 0
            try:
                cursor.execute("SELECT * FROM books WHERE book_id = %s AND issued_to = %s", (book_id, username))
                book_data = cursor.fetchone()
            except Exception as e:
                print(f"Return error: {e}")
            finally:
                cursor.close()
        else:
            for book in self.books:
                if book.book_id == str(book_id) and book.issued_to == username:
                    book_data = book.to_dict()
                    break

        if not book_data:
            return False, 0

        returned_book_title = book_data['title']
        due_date_str = book_data['due_date']
        
        # Calculate Fine
        if due_date_str:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            today = datetime.now()
            if today > due_date:
                late_days = (today - due_date).days
                fine_amount = float(late_days * 5) # ₹5 fine per day

        if self.mysql_connected:
            cursor = self.get_cursor()
            if not cursor:
                return False, 0
            try:
                # Reset book
                cursor.execute("""
                    UPDATE books 
                    SET status = 'Available', issued_to = NULL, issue_date = NULL, due_date = NULL
                    WHERE book_id = %s
                """, (book_id,))
                
                # Save fine if active
                if fine_amount > 0:
                    cursor.execute("""
                        INSERT INTO fines (username, book_id, amount, status)
                        VALUES (%s, %s, %s, 'Pending')
                    """, (username, book_id, fine_amount))

                # Clear / Mark active notifications for this returned book as Read
                cursor.execute("""
                    DELETE FROM notifications 
                    WHERE username = %s AND (message LIKE %s OR message LIKE %s)
                """, (username, f"%'{returned_book_title}'%", f"%{returned_book_title}%"))
                
                # Insert dynamic success return notification
                cursor.execute("""
                    INSERT INTO notifications (username, message, type)
                    VALUES (%s, %s, 'Success')
                """, (username, f"Success: You returned '{returned_book_title}' successfully. Fines added: ₹{fine_amount}."))

                self.db.commit()
                return True, fine_amount
            except Exception as e:
                print(f"Return book MySQL error: {e}")
                return False, 0
            finally:
                cursor.close()
        else:
            # Local Storage Mode
            for book in self.books:
                if book.book_id == str(book_id):
                    book.status = "Available"
                    book.issued_to = None
                    book.issue_date = None
                    book.due_date = None
                    break
            self.save_books()

            # Record fine
            if fine_amount > 0:
                self.fines.append({
                    "id": len(self.fines) + 1,
                    "username": username,
                    "book_id": str(book_id),
                    "amount": fine_amount,
                    "status": "Pending",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                self.save_fines()

            # Delete notifications matching title
            self.notifications = [n for n in self.notifications if not (n['username'] == username and returned_book_title in n['message'])]
            
            # Add dynamic success notification
            self.notifications.append({
                "id": len(self.notifications) + 1,
                "username": username,
                "message": f"Success: You returned '{returned_book_title}' successfully. Fines added: ₹{fine_amount}.",
                "type": "Success",
                "is_read": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            self.save_notifications()
            return True, fine_amount

    def get_notifications(self, username):
        # Trigger checks to update notifications on-the-fly!
        self.run_notification_checks_for_user(username)

        if self.mysql_connected:
            cursor = self.get_cursor()
            if not cursor:
                return []
            try:
                cursor.execute("""
                    SELECT * FROM notifications 
                    WHERE username = %s 
                    ORDER BY created_at DESC
                """, (username,))
                rows = cursor.fetchall()
                for r in rows:
                    r['created_at'] = r['created_at'].strftime("%Y-%m-%d %H:%M:%S")
                return rows
            except Exception as e:
                print(f"Get notifications MySQL error: {e}")
                return []
            finally:
                cursor.close()
        else:
            return [n for n in self.notifications if n['username'] == username]

    def mark_notifications_read(self, username):
        if self.mysql_connected:
            cursor = self.get_cursor()
            if not cursor:
                return False
            try:
                cursor.execute("UPDATE notifications SET is_read = TRUE WHERE username = %s", (username,))
                self.db.commit()
                return True
            except Exception as e:
                print(f"Mark notifications MySQL error: {e}")
                return False
            finally:
                cursor.close()
        else:
            for n in self.notifications:
                if n['username'] == username:
                    n['is_read'] = True
            self.save_notifications()
            return True

    def run_notification_checks_for_user(self, username):
        """Calculates fines and notifications for a student based on issued books."""
        books = self.get_all_books()
        today = datetime.now()
        
        # Filter books issued to this user
        user_books = [b for b in books if b.get('issued_to') == username]
        
        for book in user_books:
            due_date_str = book.get('due_date')
            if not due_date_str:
                continue
                
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            time_left = due_date - today
            days_left = time_left.days + 1
            
            # Check 1: Due Date Reminder (2 days before)
            if 0 <= days_left <= 2:
                msg = f"Reminder: Your issued book '{book['title']}' must be returned within {days_left if days_left > 0 else '0'} days."
                self.add_unique_notification(username, msg, 'DueReminder', book['title'])
            
            # Check 2: Overdue & Fines Alert
            elif today > due_date:
                late_days = (today - due_date).days
                fine = late_days * 5
                
                overdue_msg = f"Your issued book '{book['title']}' is overdue. Please return it immediately."
                self.add_unique_notification(username, overdue_msg, 'OverdueAlert', book['title'])
                
                fine_msg = f"Fine Alert: You currently have ₹{fine} pending fine for late return of '{book['title']}'."
                # We need to overwrite fine message if it increases, but not create duplicates!
                self.add_unique_notification(username, fine_msg, 'FineAlert', book['title'], overwrite_type='FineAlert')

    def add_unique_notification(self, username, message, type_name, book_title, overwrite_type=None):
        """Helper to insert unique notifications and avoid spamming duplicates."""
        if self.mysql_connected:
            cursor = self.get_cursor()
            if not cursor:
                return
            try:
                # Check duplicate
                if overwrite_type:
                    cursor.execute("""
                        SELECT id FROM notifications 
                        WHERE username = %s AND type = %s AND message LIKE %s
                    """, (username, overwrite_type, f"%'{book_title}'%"))
                    row = cursor.fetchone()
                    if row:
                        # Update the existing notification (e.g. increase fine)
                        cursor.execute("UPDATE notifications SET message = %s, is_read = FALSE, created_at = CURRENT_TIMESTAMP WHERE id = %s", (message, row['id']))
                        self.db.commit()
                        return
                
                cursor.execute("""
                    SELECT COUNT(*) FROM notifications 
                    WHERE username = %s AND type = %s AND message = %s
                """, (username, type_name, message))
                if cursor.fetchone()['COUNT(*)'] == 0:
                    cursor.execute("""
                        INSERT INTO notifications (username, message, type)
                        VALUES (%s, %s, %s)
                    """, (username, message, type_name))
                    self.db.commit()
            except Exception as e:
                print(f"Add unique notification MySQL error: {e}")
            finally:
                cursor.close()
        else:
            # JSON Mode
            if overwrite_type:
                for n in self.notifications:
                    if n['username'] == username and n['type'] == overwrite_type and book_title in n['message']:
                        n['message'] = message
                        n['is_read'] = False
                        n['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        self.save_notifications()
                        return
            
            # Check duplicate
            duplicate = any(n['username'] == username and n['type'] == type_name and n['message'] == message for n in self.notifications)
            if not duplicate:
                self.notifications.append({
                    "id": len(self.notifications) + 1,
                    "username": username,
                    "message": message,
                    "type": type_name,
                    "is_read": False,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                self.save_notifications()

    def get_admin_dashboard_stats(self):
        """Fetches total figures for administrative use."""
        books = self.get_all_books()
        total_books = len(books)
        issued_books = sum(1 for b in books if b['status'] == 'Issued')
        available_books = total_books - issued_books
        
        # Calculate Fines
        total_collected = 0.0
        pending_fines = 0.0
        
        if self.mysql_connected:
            cursor = self.get_cursor()
            if cursor:
                try:
                    cursor.execute("SELECT SUM(amount) as total FROM fines WHERE status = 'Paid'")
                    res = cursor.fetchone()
                    total_collected = float(res['total']) if res and res['total'] else 0.0
                    
                    cursor.execute("SELECT SUM(amount) as total FROM fines WHERE status = 'Pending'")
                    res = cursor.fetchone()
                    pending_fines = float(res['total']) if res and res['total'] else 0.0
                except Exception as e:
                    print(f"Stats DB error: {e}")
                finally:
                    cursor.close()
        else:
            total_collected = sum(float(f['amount']) for f in self.fines if f['status'] == 'Paid')
            pending_fines = sum(float(f['amount']) for f in self.fines if f['status'] == 'Pending')

        # Overdue list
        overdue_students = []
        today = datetime.now()
        for b in books:
            if b['status'] == 'Issued' and b.get('due_date'):
                due_date = datetime.strptime(b['due_date'], "%Y-%m-%d")
                if today > due_date:
                    late_days = (today - due_date).days
                    overdue_students.append({
                        "username": b['issued_to'],
                        "book_title": b['title'],
                        "due_date": b['due_date'],
                        "overdue_days": late_days,
                        "calculated_fine": late_days * 5
                    })

        return {
            "total_books": total_books,
            "issued_books": issued_books,
            "available_books": available_books,
            "returned_books": total_books - available_books, # Total transactions of issue/return estimation
            "total_collected_fines": total_collected,
            "pending_fines": pending_fines,
            "overdue_students": overdue_students
        }

    def get_student_records(self):
        """Admin helper to load all transactions, active loans, and fine lists."""
        books = self.get_all_books()
        today = datetime.now()
        records = []
        
        # Format active student records
        for b in books:
            if b['status'] == 'Issued':
                due_date_str = b['due_date']
                fine = 0.0
                overdue = False
                if due_date_str:
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                    if today > due_date:
                        overdue = True
                        fine = float((today - due_date).days * 5)
                
                records.append({
                    "username": b['issued_to'],
                    "book_id": b['book_id'],
                    "title": b['title'],
                    "issue_date": b.get('issue_date', 'N/A'),
                    "due_date": due_date_str,
                    "status": "Issued",
                    "overdue": overdue,
                    "pending_fine": fine
                })
        
        # Add past fine transactions for returned items
        if self.mysql_connected:
            cursor = self.get_cursor()
            if cursor:
                try:
                    cursor.execute("""
                        SELECT f.*, b.title 
                        FROM fines f 
                        JOIN books b ON f.book_id = b.book_id
                    """)
                    fine_rows = cursor.fetchall()
                    for f in fine_rows:
                        # Don't duplicate active loans that already showed up above
                        if not any(r['username'] == f['username'] and r['book_id'] == str(f['book_id']) and r['status'] == 'Issued' for r in records):
                            records.append({
                                "username": f['username'],
                                "book_id": str(f['book_id']),
                                "title": f['title'],
                                "issue_date": "Returned",
                                "due_date": "Returned",
                                "status": f['status'], # 'Paid' or 'Pending'
                                "overdue": False,
                                "pending_fine": float(f['amount']) if f['status'] == 'Pending' else 0.0,
                                "paid_fine": float(f['amount']) if f['status'] == 'Paid' else 0.0
                            })
                except Exception as e:
                    print(f"Student records fine error: {e}")
                finally:
                    cursor.close()
        else:
            for f in self.fines:
                # Find book title
                title = "Unknown Book"
                for b in self.books:
                    if b.book_id == str(f['book_id']):
                        title = b.title
                        break
                
                records.append({
                    "username": f['username'],
                    "book_id": str(f['book_id']),
                    "title": title,
                    "issue_date": "Returned",
                    "due_date": "Returned",
                    "status": f['status'],
                    "overdue": False,
                    "pending_fine": float(f['amount']) if f['status'] == 'Pending' else 0.0,
                    "paid_fine": float(f['amount']) if f['status'] == 'Paid' else 0.0
                })
                
        return records

    def pay_fine(self, username, book_id):
        """Mark fine paid."""
        if self.mysql_connected:
            cursor = self.get_cursor()
            if not cursor:
                return False
            try:
                cursor.execute("""
                    UPDATE fines 
                    SET status = 'Paid', paid_at = CURRENT_TIMESTAMP 
                    WHERE username = %s AND book_id = %s AND status = 'Pending'
                """, (username, book_id))
                self.db.commit()
                return True
            except Exception as e:
                print(f"Pay fine MySQL error: {e}")
                return False
            finally:
                cursor.close()
        else:
            for f in self.fines:
                if f['username'] == username and f['book_id'] == str(book_id) and f['status'] == 'Pending':
                    f['status'] = 'Paid'
                    f['paid_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.save_fines()
                    return True
            return False

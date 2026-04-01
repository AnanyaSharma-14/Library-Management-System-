import json
import os
from datetime import datetime, timedelta

BOOKS_FILE = 'books.json'
USERS_FILE = 'users.json'

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
    def __init__(self, book_id, title, author, status="Available", issued_to=None, due_date=None):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.status = status
        self.issued_to = issued_to
        self.due_date = due_date

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "status": self.status,
            "issued_to": self.issued_to,
            "due_date": self.due_date
        }

    @staticmethod
    def from_dict(data):
        return Book(
            book_id=data['book_id'],
            title=data['title'],
            author=data['author'],
            status=data['status'],
            issued_to=data.get('issued_to'),
            due_date=data.get('due_date')
        )

class Library:
    def __init__(self):
        self.books = []
        self.users = []
        self.load_data()

    def load_data(self):
        # Load Books
        if os.path.exists(BOOKS_FILE):
            try:
                with open(BOOKS_FILE, 'r') as file:
                    books_data = json.load(file)
                    self.books = [Book.from_dict(b) for b in books_data]
            except Exception as e:
                print(f"Error loading books: {e}")
                self.books = []
        else:
            self.books = []

        # Load Users
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, 'r') as file:
                    users_data = json.load(file)
                    self.users = [User.from_dict(u) for u in users_data]
            except Exception as e:
                print(f"Error loading users: {e}")
                self.users = []
        else:
            # Create default Admin and User if file doesn't exist
            print("Initializing default users...")
            self.users = [
                User("admin", "admin123", "admin"),
                User("user", "user123", "user")
            ]
            self.save_users()

    def save_books(self):
        with open(BOOKS_FILE, 'w') as file:
            json.dump([book.to_dict() for book in self.books], file, indent=4)

    def save_users(self):
        with open(USERS_FILE, 'w') as file:
            json.dump([user.to_dict() for user in self.users], file, indent=4)

    def authenticate(self, username, password):
        for user in self.users:
            if user.username == username and user.password == password:
                return user
        return None

    def add_book(self, title, author):
        # Generate a new unique ID
        book_id = str(len(self.books) + 1)
        new_book = Book(book_id, title, author)
        self.books.append(new_book)
        self.save_books()
        print(f"\n[+] Success: '{title}' added to the library (ID: {book_id}).")

    def view_books(self):
        if not self.books:
            print("\n[-] Library is currently empty.")
            return

        print("\n" + "="*80)
        print(f"{'ID':<5} | {'Title':<30} | {'Author':<20} | {'Status':<15}")
        print("-" * 80)
        for book in self.books:
            print(f"{book.book_id:<5} | {book.title[:28]:<30} | {book.author[:18]:<20} | {book.status:<15}")
        print("=" * 80)

    def search_books(self, query):
        query = query.lower() # Case-insensitive
        results = [book for book in self.books if query in book.title.lower()] # Partial matching

        if not results:
            print(f"\n[-] No books found matching '{query}'.")
            return

        print("\n" + "="*80)
        print(f"Search Results for '{query}':")
        print(f"{'ID':<5} | {'Title':<30} | {'Author':<20} | {'Status':<15}")
        print("-" * 80)
        for book in results:
            print(f"{book.book_id:<5} | {book.title[:28]:<30} | {book.author[:18]:<20} | {book.status:<15}")
        print("=" * 80)

    def issue_book(self, user, book_id):
        # Admin can't issue books, only normal users can
        if user.role == 'admin':
            print("\n[-] Admins do not issue books for themselves. Please login as a User.")
            return

        for book in self.books:
            if book.book_id == book_id:
                if book.status == "Available":
                    # Setting due date to 14 days from now
                    due_date = datetime.now() + timedelta(days=14)
                    
                    book.status = "Issued"
                    book.issued_to = user.username
                    book.due_date = due_date.strftime("%Y-%m-%d")
                    self.save_books()
                    print(f"\n[+] Success: Book '{book.title}' has been issued to {user.username}.")
                    print(f"    Please return it by {book.due_date}.")
                else:
                    print(f"\n[-] Sorry, '{book.title}' is currently issued to {book.issued_to}.")
                return
        
        print(f"\n[-] Book with ID '{book_id}' not found.")

    def return_book(self, user, book_id):
        for book in self.books:
            if book.book_id == book_id:
                if book.status == "Issued" and book.issued_to == user.username:
                    
                    # Calculate Fine
                    fine = 0
                    if book.due_date:
                        due_date_obj = datetime.strptime(book.due_date, "%Y-%m-%d")
                        current_date = datetime.now()
                        if current_date > due_date_obj:
                            late_days = (current_date - due_date_obj).days
                            fine_per_day = 10 # 10 units of currency (e.g. ₹10)
                            fine = late_days * fine_per_day

                    # Reset book status
                    book.status = "Available"
                    book.issued_to = None
                    book.due_date = None
                    self.save_books()

                    print(f"\n[+] Success: '{book.title}' returned successfully.")
                    if fine > 0:
                        print(f"[!] LATE RETURN FINE CAUGHT: You are expected to pay ₹{fine} for being late.")
                else:
                    print("\n[-] This book was not issued to you or is already available.")
                return
        
        print(f"\n[-] Book with ID '{book_id}' not found.")

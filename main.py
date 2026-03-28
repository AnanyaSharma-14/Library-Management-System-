import json
import os

class Book:
    def __init__(self, book_id, title, author, is_issued=False):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.is_issued = is_issued


class Library:
    def __init__(self):
        self.books = []
        self.file = "books.json"
        self.load_books()

    def load_books(self):
        if os.path.exists(self.file):
            with open(self.file, "r") as f:
                data = json.load(f)
                for b in data:
                    self.books.append(Book(**b))

    def save_books(self):
        with open(self.file, "w") as f:
            json.dump([book.__dict__ for book in self.books], f, indent=4)

    def add_book(self):
        book_id = input("Enter Book ID: ")
        title = input("Enter Title: ")
        author = input("Enter Author: ")
        self.books.append(Book(book_id, title, author))
        self.save_books()
        print("Book Added!\n")

    def view_books(self):
        if not self.books:
            print("No books available\n")
            return
        for book in self.books:
            status = "Issued" if book.is_issued else "Available"
            print(f"{book.book_id} | {book.title} | {book.author} | {status}")
        print()

    def search_book(self):
        title = input("Enter title: ").lower()
        found = False
        for book in self.books:
            if title in book.title.lower():
                print(f"Found: {book.title} by {book.author}")
                found = True
        if not found:
            print(" Not found\n")

    def issue_book(self):
        book_id = input("Enter Book ID: ")
        for book in self.books:
            if book.book_id == book_id:
                if not book.is_issued:
                    book.is_issued = True
                    self.save_books()
                    print("Issued\n")
                    return
                else:
                    print("Already issued\n")
                    return
        print("Book not found\n")

    def return_book(self):
        book_id = input("Enter Book ID: ")
        for book in self.books:
            if book.book_id == book_id:
                if book.is_issued:
                    book.is_issued = False
                    self.save_books()
                    print(" Returned\n")
                    return
                else:
                    print("Not issued\n")
                    return
        print("Book not found\n")


def login():
    USER = "admin"
    PASS = "1234"

    print("===== LOGIN =====")
    u = input("Username: ")
    p = input("Password: ")

    return u == USER and p == PASS


def main():
    if not login():
        print(" Access Denied")
        return

    lib = Library()

    while True:
        print("\n1.Add  2.View  3.Search  4.Issue  5.Return  6.Exit")
        ch = input("Choice: ")

        if ch == '1': lib.add_book()
        elif ch == '2': lib.view_books()
        elif ch == '3': lib.search_book()
        elif ch == '4': lib.issue_book()
        elif ch == '5': lib.return_book()
        elif ch == '6': break
        else: print("Invalid")


if __name__ == "__main__":
    main()

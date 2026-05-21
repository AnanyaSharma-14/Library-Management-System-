from library import Library

def main():
    print("=====================================================")
    print("       Welcome to Library Management System        ")
    print("=====================================================")
    
    lib = Library()
    
    while True:
        print("\n--- Login ---")
        print("Type 'exit' as username to quit the application.")
        username = input("Enter Username: ")
        
        if username.lower() == 'exit':
            print("Exiting system. Goodbye!")
            break
            
        password = input("Enter Password: ")
        
        user = lib.authenticate(username, password)
        
        if user:
            print(f"\n[+] Login successful! Welcome, {user.username} (Role: {user.role})")
            if user.role == "admin":
                admin_menu(lib, user)
            else:
                user_menu(lib, user)
        else:
            print("\n[-] Invalid credentials. Please try again.")

def admin_menu(lib, user):
    while True:
        print("\n" + "="*40)
        print("           ADMIN DASHBOARD")
        print("="*40)
        print("1. View All Books")
        print("2. Add a New Book")
        print("3. Logout")
        print("-" * 40)
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            lib.view_books()
        elif choice == '2':
            title = input("Enter Book Title: ")
            author = input("Enter Author Name: ")
            lib.add_book(title, author)
        elif choice == '3':
            print("\nLogging out...")
            break
        else:
            print("\n[-] Invalid choice. Please try again.")

def user_menu(lib, user):
    while True:
        print("\n" + "="*40)
        print("           USER DASHBOARD")
        print("="*40)
        print("1. View All Books")
        print("2. Search Book")
        print("3. Issue a Book")
        print("4. Return a Book")
        print("5. Logout")
        print("-" * 40)
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == '1':
            lib.view_books()
        elif choice == '2':
            query = input("Enter search keyword (title): ")
            lib.search_books(query)
        elif choice == '3':
            book_id = input("Enter Book ID to issue: ")
            lib.issue_book(user, book_id)
        elif choice == '4':
            book_id = input("Enter Book ID to return: ")
            lib.return_book(user, book_id)
        elif choice == '5':
            print("\nLogging out...")
            break
        else:
            print("\n[-] Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

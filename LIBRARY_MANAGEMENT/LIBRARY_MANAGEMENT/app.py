from flask import Flask, request, jsonify, session, send_from_directory, redirect, url_for
from library import Library
import os
import config

app = Flask(__name__, static_folder='static')
app.secret_key = config.SECRET_KEY

# Initialize core library engine (attempts MySQL, falls back to JSON)
lib = Library()

# --- Page-Serving Routes ---
# Serves the HTML files straight from the root workspace folder, maintaining 100% path compatibility.

@app.route('/')
def home():
    if 'username' in session:
        return redirect('/index.html')
    return redirect('/login.html')

@app.route('/<path:filename>')
def serve_html_pages(filename):
    # If the user requests a valid root HTML file, send it
    if filename.endswith('.html') and os.path.exists(filename):
        return send_from_directory('.', filename)
    # Allow normal static assets to pass through
    elif filename.startswith('static/'):
        return send_from_directory('.', filename)
    return "Page Not Found", 404

# --- API Endpoints ---

# 1. Login / Logout / Session check
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required."}), 400
        
    user = lib.authenticate(username, password)
    if user:
        session['username'] = user.username
        session['role'] = user.role
        return jsonify({
            "success": True,
            "username": user.username,
            "role": user.role
        })
    return jsonify({"success": False, "message": "Invalid username or password."}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."})

@app.route('/api/user/session', methods=['GET'])
def api_session():
    if 'username' in session:
        return jsonify({
            "logged_in": True,
            "username": session['username'],
            "role": session['role']
        })
    return jsonify({"logged_in": False})

# 2. Books APIs
@app.route('/api/books', methods=['GET'])
def api_get_books():
    return jsonify(lib.get_all_books())

@app.route('/api/books/search', methods=['GET'])
def api_search_books():
    query = request.args.get('q', '')
    return jsonify(lib.search_books(query))

@app.route('/api/books/add', methods=['POST'])
def api_add_book():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    
    data = request.json or {}
    title = data.get('title')
    author = data.get('author')
    
    if not title or not author:
        return jsonify({"success": False, "message": "Title and author are required."}), 400
        
    success = lib.add_book(title, author)
    if success:
        return jsonify({"success": True, "message": f"Successfully added '{title}'."})
    return jsonify({"success": False, "message": "Error adding book."}), 500

@app.route('/api/books/issue', methods=['POST'])
def api_issue_book():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    data = request.json or {}
    book_id = data.get('book_id')
    username = session['username'] # Standard: Student issues for themselves
    
    if session.get('role') == 'admin':
        return jsonify({"success": False, "message": "Admins cannot borrow books."}), 400

    if not book_id:
        return jsonify({"success": False, "message": "Book ID is required."}), 400
        
    success = lib.issue_book(username, book_id)
    if success:
        return jsonify({"success": True, "message": "Book issued successfully!"})
    return jsonify({"success": False, "message": "Book is already issued or does not exist."}), 400

@app.route('/api/books/return', methods=['POST'])
def api_return_book():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    data = request.json or {}
    book_id = data.get('book_id')
    username = session['username']
    
    if not book_id:
        return jsonify({"success": False, "message": "Book ID is required."}), 400
        
    success, fine = lib.return_book(username, book_id)
    if success:
        return jsonify({
            "success": True, 
            "message": "Book returned successfully!", 
            "fine_incurred": fine
        })
    return jsonify({"success": False, "message": "This book was not issued to you or is invalid."}), 400

# 3. Dynamic Notifications APIs
@app.route('/api/notifications', methods=['GET'])
def api_notifications():
    if 'username' not in session:
        return jsonify([])
    return jsonify(lib.get_notifications(session['username']))

@app.route('/api/notifications/read', methods=['POST'])
def api_notifications_read():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    success = lib.mark_notifications_read(session['username'])
    return jsonify({"success": success})

# 4. Admin Dashboard Records & Fines
@app.route('/api/dashboard/stats', methods=['GET'])
def api_dashboard_stats():
    # Allow both admin and regular user check (regular user sees books ratios, admin sees fines and full data)
    stats = lib.get_admin_dashboard_stats()
    return jsonify(stats)

@app.route('/api/admin/records', methods=['GET'])
def api_admin_records():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    return jsonify(lib.get_student_records())

@app.route('/api/fines/pay', methods=['POST'])
def api_pay_fine():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    data = request.json or {}
    student_user = data.get('username', session['username']) # Students pay for themselves, Admins can clear too
    book_id = data.get('book_id')
    
    if not book_id:
        return jsonify({"success": False, "message": "Book ID is required."}), 400
        
    success = lib.pay_fine(student_user, book_id)
    if success:
        return jsonify({"success": True, "message": "Fine paid successfully!"})
    return jsonify({"success": False, "message": "No pending fine found for this record."}), 400

if __name__ == '__main__':
    print("====================================================")
    print("      Starting Central Library Management Web App     ")
    print("      Server Link: http://127.0.0.1:5000/            ")
    print("====================================================")
    app.run(debug=True, port=5000)

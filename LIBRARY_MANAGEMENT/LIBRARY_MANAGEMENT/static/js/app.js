/* 
   Central Library Management System - Main App JavaScript
   Coordinates routing, session management, and routes requests to either Live API or Mock DB.
*/

// Detect environment: True if opened by double clicking the HTML file directly in browser
const IS_STATIC_MODE = window.location.protocol === 'file:' || window.location.hostname === '';

// --- API Layer Switchboard ---
const API = {
    // 1. Authenticate user
    login: async function(username, password) {
        if (IS_STATIC_MODE) {
            const res = window.MockDB.authenticate(username, password);
            if (res.success) {
                sessionStorage.setItem('current_user', JSON.stringify(res));
                return res;
            }
            throw new Error("Invalid username or password.");
        } else {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.message || "Invalid credentials.");
            }
            const user = await response.json();
            sessionStorage.setItem('current_user', JSON.stringify(user));
            return user;
        }
    },

    // 2. Clear session
    logout: async function() {
        sessionStorage.removeItem('current_user');
        if (!IS_STATIC_MODE) {
            await fetch('/api/logout', { method: 'POST' });
        }
        window.location.href = 'login.html';
    },

    // 3. Get currently active session user
    getCurrentUser: function() {
        const user = sessionStorage.getItem('current_user');
        return user ? JSON.parse(user) : null;
    },

    // 4. Fetch list of books
    getBooks: async function() {
        if (IS_STATIC_MODE) {
            return window.MockDB.getBooks();
        } else {
            const res = await fetch('/api/books');
            return res.json();
        }
    },

    // 5. Search books
    searchBooks: async function(query) {
        if (IS_STATIC_MODE) {
            const books = window.MockDB.getBooks();
            const q = query.toLowerCase();
            return books.filter(b => b.title.toLowerCase().includes(q) || b.author.toLowerCase().includes(q));
        } else {
            const res = await fetch(`/api/books/search?q=${encodeURIComponent(query)}`);
            return res.json();
        }
    },

    // 6. Add Book (Admin)
    addBook: async function(title, author) {
        if (IS_STATIC_MODE) {
            return window.MockDB.addBook(title, author);
        } else {
            const response = await fetch('/api/books/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, author })
            });
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.message || "Error adding book.");
            }
            return response.json();
        }
    },

    // 7. Issue Book (Student)
    issueBook: async function(bookId) {
        if (IS_STATIC_MODE) {
            const user = this.getCurrentUser();
            return window.MockDB.issueBook(user.username, bookId);
        } else {
            const response = await fetch('/api/books/issue', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ book_id: bookId })
            });
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.message || "Error issuing book.");
            }
            return response.json();
        }
    },

    // 8. Return Book (Student)
    returnBook: async function(bookId) {
        if (IS_STATIC_MODE) {
            const user = this.getCurrentUser();
            return window.MockDB.returnBook(user.username, bookId);
        } else {
            const response = await fetch('/api/books/return', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ book_id: bookId })
            });
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.message || "Error returning book.");
            }
            return response.json();
        }
    },

    // 9. Dashboard stats summary
    getStats: async function() {
        if (IS_STATIC_MODE) {
            return window.MockDB.getDashboardStats();
        } else {
            const res = await fetch('/api/dashboard/stats');
            return res.json();
        }
    },

    // 10. Admin audit transactions
    getAdminRecords: async function() {
        if (IS_STATIC_MODE) {
            return window.MockDB.getStudentRecords();
        } else {
            const res = await fetch('/api/admin/records');
            if (!res.ok) throw new Error("Unauthorized access.");
            return res.json();
        }
    },

    // 11. Pay Fine
    payFine: async function(username, bookId) {
        if (IS_STATIC_MODE) {
            return window.MockDB.payFine(username, bookId);
        } else {
            const response = await fetch('/api/fines/pay', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, book_id: bookId })
            });
            return response.json();
        }
    }
};

// --- Global UI Hookups on DOM Load ---
document.addEventListener("DOMContentLoaded", function() {
    const user = API.getCurrentUser();
    
    // Redirect logic: If not on login.html and not authenticated, push to login
    const isLoginPage = window.location.pathname.endsWith("login.html");
    if (!user && !isLoginPage) {
        window.location.href = "login.html";
        return;
    }

    // Initialize sidebar states if user logged in
    if (user && !isLoginPage) {
        setupSidebar(user);
    }
});

// Configure sidebar visibility and display dynamic user card
function setupSidebar(user) {
    // 1. Populate User avatar details in bottom tag
    const avatar = document.getElementById("sidebarAvatar");
    const nameEl = document.getElementById("sidebarUsername");
    const roleEl = document.getElementById("sidebarRole");

    if (avatar) avatar.textContent = user.username.charAt(0).toUpperCase();
    if (nameEl) nameEl.textContent = user.username;
    if (roleEl) roleEl.textContent = user.role === 'admin' ? 'Administrator' : 'Student';

    // 2. Hide links according to role permissions
    const adminLinks = document.querySelectorAll(".admin-only");
    const userLinks = document.querySelectorAll(".user-only");

    if (user.role === 'admin') {
        adminLinks.forEach(el => el.style.display = 'flex');
        userLinks.forEach(el => el.style.display = 'none');
    } else {
        adminLinks.forEach(el => el.style.display = 'none');
        userLinks.forEach(el => el.style.display = 'flex');
    }

    // 3. Highlight current active link
    const links = document.querySelectorAll(".sidebar-link");
    const currentPath = window.location.pathname.split('/').pop() || 'index.html';
    
    links.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath === '' && href === 'index.html')) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // 4. Attach Logout button handler
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => API.logout());
    }
}

// Utility: Show Alert Banners Dynamically
function showAlert(containerId, message, type = 'success') {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = `
        <div class="alert-banner ${type}">
            <span>${message}</span>
        </div>
    `;
    // Auto clear alert banner after 5 seconds
    setTimeout(() => {
        container.innerHTML = '';
    }, 5000);
}

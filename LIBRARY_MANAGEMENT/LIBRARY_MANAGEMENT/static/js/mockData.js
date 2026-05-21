/* 
   Central Library Management System - LocalStorage Mock DB
   Simulates Python+MySQL database features in the browser when running statically (file://)
*/

(function() {
    // Utility: Date formatting helper
    function getOffsetDateString(daysOffset) {
        const d = new Date();
        d.setDate(d.getDate() + daysOffset);
        return d.toISOString().split('T')[0];
    }

    function formatDateStr(dateObj) {
        return dateObj.toISOString().split('T')[0];
    }

    // 1. Initial Seeding of Mock Data
    function initDatabase() {
        // Seed Users
        if (!localStorage.getItem('lib_users')) {
            const defaultUsers = [
                { username: 'admin', password: 'admin123', role: 'admin' },
                { username: 'user', password: 'user123', role: 'user' },
                { username: 'student1', password: 'student123', role: 'user' },
                { username: 'student2', password: 'student123', role: 'user' }
            ];
            localStorage.setItem('lib_users', JSON.stringify(defaultUsers));
        }

        // Seed Books with Relative Dates
        if (!localStorage.getItem('lib_books')) {
            const defaultBooks = [
                {
                    book_id: "1",
                    title: "Harry Potter and the Sorcerer's Stone",
                    author: "J.K. Rowling",
                    status: "Available",
                    issued_to: null,
                    issue_date: null,
                    due_date: null
                },
                {
                    book_id: "2",
                    title: "Python Basics for Beginners",
                    author: "Al Sweigart",
                    status: "Issued",
                    issued_to: "user",
                    issue_date: getOffsetDateString(-13),
                    due_date: getOffsetDateString(1) // Due in 1 day (Triggers due date warning <= 2 days!)
                },
                {
                    book_id: "3",
                    title: "Web Development Guide",
                    author: "John Duckett",
                    status: "Issued",
                    issued_to: "student1",
                    issue_date: getOffsetDateString(-19),
                    due_date: getOffsetDateString(-5) // Overdue by 5 days (Triggers overdue alert and ₹25 fine!)
                },
                {
                    book_id: "4",
                    title: "Clean Code: A Handbook of Agile Software Craftsmanship",
                    author: "Robert C. Martin",
                    status: "Issued",
                    issued_to: "user",
                    issue_date: getOffsetDateString(-8),
                    due_date: getOffsetDateString(6) // Due in 6 days (No warning yet)
                },
                {
                    book_id: "5",
                    title: "Database System Concepts",
                    author: "Abraham Silberschatz",
                    status: "Available",
                    issued_to: null,
                    issue_date: null,
                    due_date: null
                }
            ];
            localStorage.setItem('lib_books', JSON.stringify(defaultBooks));
        }

        // Seed Fines (Logs transactions)
        if (!localStorage.getItem('lib_fines')) {
            const defaultFines = [
                {
                    id: 1,
                    username: 'student1',
                    book_id: '3',
                    amount: 25.00,
                    status: 'Pending',
                    created_at: getOffsetDateString(-5) + ' 09:30:00'
                },
                {
                    id: 2,
                    username: 'user',
                    book_id: '5',
                    amount: 10.00,
                    status: 'Paid',
                    created_at: getOffsetDateString(-10) + ' 10:15:00',
                    paid_at: getOffsetDateString(-2) + ' 14:00:00'
                }
            ];
            localStorage.setItem('lib_fines', JSON.stringify(defaultFines));
        }

        // Seed Notifications
        if (!localStorage.getItem('lib_notifications')) {
            const defaultNotifications = [
                {
                    id: 1,
                    username: 'user',
                    message: "Reminder: Your issued book 'Python Basics for Beginners' must be returned within 1 days.",
                    type: 'DueReminder',
                    created_at: getOffsetDateString(0) + ' 08:00:00',
                    is_read: false
                },
                {
                    id: 2,
                    username: 'student1',
                    message: "Your issued book 'Web Development Guide' is overdue. Please return it immediately.",
                    type: 'OverdueAlert',
                    created_at: getOffsetDateString(-4) + ' 08:00:00',
                    is_read: false
                },
                {
                    id: 3,
                    username: 'student1',
                    message: "Fine Alert: You currently have ₹25 pending fine for late return of 'Web Development Guide'.",
                    type: 'FineAlert',
                    created_at: getOffsetDateString(0) + ' 08:00:00',
                    is_read: false
                },
                {
                    id: 4,
                    username: 'user',
                    message: "Welcome to the new Library Portal! Make sure to check your notifications.",
                    type: 'Info',
                    created_at: getOffsetDateString(-1) + ' 12:00:00',
                    is_read: false
                }
            ];
            localStorage.setItem('lib_notifications', JSON.stringify(defaultNotifications));
        }
    }

    // Call Immediately on import
    initDatabase();

    // 2. Database Core Controller object
    window.MockDB = {
        getBooks: function() {
            return JSON.parse(localStorage.getItem('lib_books')) || [];
        },
        saveBooks: function(books) {
            localStorage.setItem('lib_books', JSON.stringify(books));
        },
        getUsers: function() {
            return JSON.parse(localStorage.getItem('lib_users')) || [];
        },
        getFines: function() {
            return JSON.parse(localStorage.getItem('lib_fines')) || [];
        },
        saveFines: function(fines) {
            localStorage.setItem('lib_fines', JSON.stringify(fines));
        },
        getNotifications: function(username) {
            this.runNotificationChecksForUser(username);
            const allNotifs = JSON.parse(localStorage.getItem('lib_notifications')) || [];
            return allNotifs.filter(n => n.username === username).sort((a, b) => b.id - a.id);
        },
        saveNotifications: function(notifications) {
            localStorage.setItem('lib_notifications', JSON.stringify(notifications));
        },

        // Auth
        authenticate: function(username, password) {
            const users = this.getUsers();
            const match = users.find(u => u.username.toLowerCase() === username.toLowerCase() && u.password === password);
            if (match) {
                return { success: true, username: match.username, role: match.role };
            }
            return { success: false };
        },

        // Add book
        addBook: function(title, author) {
            const books = this.getBooks();
            const newId = String(books.length > 0 ? Math.max(...books.map(b => parseInt(b.book_id))) + 1 : 1);
            books.push({
                book_id: newId,
                title: title,
                author: author,
                status: 'Available',
                issued_to: null,
                issue_date: null,
                due_date: null
            });
            this.saveBooks(books);
            return { success: true };
        },

        // Issue book
        issueBook: function(username, bookId) {
            const books = this.getBooks();
            const idx = books.findIndex(b => b.book_id === String(bookId));
            
            if (idx === -1 || books[idx].status !== 'Available') {
                return { success: false, message: 'Book is unavailable.' };
            }

            const todayStr = formatDateStr(new Date());
            const dueStr = getOffsetDateString(14); // 14 days standard issue period
            
            books[idx].status = 'Issued';
            books[idx].issued_to = username;
            books[idx].issue_date = todayStr;
            books[idx].due_date = dueStr;
            
            this.saveBooks(books);
            this.runNotificationChecksForUser(username);
            return { success: true };
        },

        // Return book
        returnBook: function(username, bookId) {
            const books = this.getBooks();
            const idx = books.findIndex(b => b.book_id === String(bookId) && b.issued_to === username);
            
            if (idx === -1) {
                return { success: false, message: 'Invalid borrow record.' };
            }

            const book = books[idx];
            const title = book.title;
            let fineAmount = 0;
            
            // Calculate Fines
            if (book.due_date) {
                const due = new Date(book.due_date);
                const today = new Date();
                if (today > due) {
                    const diffTime = Math.abs(today - due);
                    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                    fineAmount = diffDays * 5; // ₹5 per day
                }
            }

            // Perform Reset
            book.status = 'Available';
            book.issued_to = null;
            book.issue_date = null;
            book.due_date = null;
            this.saveBooks(books);

            // Log Fine if generated
            if (fineAmount > 0) {
                const fines = this.getFines();
                fines.push({
                    id: fines.length + 1,
                    username: username,
                    book_id: String(bookId),
                    amount: fineAmount,
                    status: 'Pending',
                    created_at: formatDateStr(new Date()) + ' 12:00:00'
                });
                this.saveFines(fines);
            }

            // Clear Notifications for this book
            let notifs = JSON.parse(localStorage.getItem('lib_notifications')) || [];
            notifs = notifs.filter(n => !(n.username === username && n.message.includes(title)));
            
            // Add return Success notification
            notifs.push({
                id: notifs.length + 1,
                username: username,
                message: `Success: You returned '${title}' successfully. Fines added: ₹${fineAmount}.`,
                type: 'Success',
                created_at: formatDateStr(new Date()) + ' 12:00:00',
                is_read: false
            });
            this.saveNotifications(notifs);

            return { success: true, fine_incurred: fineAmount };
        },

        // Fetch user notifications and dynamically trigger active reminders
        runNotificationChecksForUser: function(username) {
            const books = this.getBooks();
            const userBooks = books.filter(b => b.issued_to === username);
            const today = new Date();

            userBooks.forEach(book => {
                if (!book.due_date) return;
                
                const due = new Date(book.due_date);
                const timeDiff = due - today;
                const daysDiff = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));

                // 1. Due date reminder (within 2 days)
                if (daysDiff >= 0 && daysDiff <= 2) {
                    const msg = `Reminder: Your issued book '${book.title}' must be returned within ${daysDiff} days.`;
                    this.addUniqueNotification(username, msg, 'DueReminder', book.title);
                }
                // 2. Overdue alert
                else if (today > due) {
                    const lateDays = Math.ceil(Math.abs(today - due) / (1000 * 60 * 60 * 24));
                    const fine = lateDays * 5;

                    const overdueMsg = `Your issued book '${book.title}' is overdue. Please return it immediately.`;
                    this.addUniqueNotification(username, overdueMsg, 'OverdueAlert', book.title);

                    const fineMsg = `Fine Alert: You currently have ₹${fine} pending fine for late return of '${book.title}'.`;
                    this.addUniqueNotification(username, fineMsg, 'FineAlert', book.title, 'FineAlert');
                }
            });
        },

        addUniqueNotification: function(username, message, typeName, bookTitle, overwriteType = null) {
            const notifs = JSON.parse(localStorage.getItem('lib_notifications')) || [];
            
            // Handle fine alert updates without duplicates
            if (overwriteType) {
                const match = notifs.find(n => n.username === username && n.type === overwriteType && n.message.includes(bookTitle));
                if (match) {
                    match.message = message;
                    match.is_read = false;
                    this.saveNotifications(notifs);
                    return;
                }
            }

            // Prevent absolute duplicates
            const duplicate = notifs.some(n => n.username === username && n.type === typeName && n.message === message);
            if (!duplicate) {
                notifs.push({
                    id: notifs.length + 1,
                    username: username,
                    message: message,
                    type: typeName,
                    created_at: formatDateStr(new Date()) + ' ' + new Date().toTimeString().split(' ')[0],
                    is_read: false
                });
                this.saveNotifications(notifs);
            }
        },

        markNotificationsRead: function(username) {
            const notifs = JSON.parse(localStorage.getItem('lib_notifications')) || [];
            notifs.forEach(n => {
                if (n.username === username) n.is_read = true;
            });
            this.saveNotifications(notifs);
            return { success: true };
        },

        // Dashboard Metrics
        getDashboardStats: function() {
            const books = this.getBooks();
            const total = books.length;
            const issued = books.filter(b => b.status === 'Issued').length;
            const available = total - issued;

            // Fines
            const fines = this.getFines();
            const totalCollected = fines.filter(f => f.status === 'Paid').reduce((acc, curr) => acc + parseFloat(curr.amount), 0);
            const pendingFines = fines.filter(f => f.status === 'Pending').reduce((acc, curr) => acc + parseFloat(curr.amount), 0);

            // Overdue lists
            const overdueStudents = [];
            const today = new Date();
            books.forEach(b => {
                if (b.status === 'Issued' && b.due_date) {
                    const due = new Date(b.due_date);
                    if (today > due) {
                        const days = Math.ceil(Math.abs(today - due) / (1000 * 60 * 60 * 24));
                        overdueStudents.push({
                            username: b.issued_to,
                            book_title: b.title,
                            due_date: b.due_date,
                            overdue_days: days,
                            calculated_fine: days * 5
                        });
                    }
                }
            });

            return {
                total_books: total,
                issued_books: issued,
                available_books: available,
                returned_books: total - available,
                total_collected_fines: totalCollected,
                pending_fines: pendingFines,
                overdue_students: overdueStudents
            };
        },

        // Admin Auditing
        getStudentRecords: function() {
            const books = this.getBooks();
            const today = new Date();
            const records = [];

            // 1. Load active loans
            books.forEach(b => {
                if (b.status === 'Issued') {
                    let fine = 0;
                    let overdue = false;
                    if (b.due_date) {
                        const due = new Date(b.due_date);
                        if (today > due) {
                            overdue = true;
                            fine = Math.ceil(Math.abs(today - due) / (1000 * 60 * 60 * 24)) * 5;
                        }
                    }
                    records.push({
                        username: b.issued_to,
                        book_id: b.book_id,
                        title: b.title,
                        issue_date: b.issue_date || 'N/A',
                        due_date: b.due_date,
                        status: 'Issued',
                        overdue: overdue,
                        pending_fine: fine
                    });
                }
            });

            // 2. Load fine history
            const fines = this.getFines();
            fines.forEach(f => {
                // Don't duplicate active loans that already showed up above
                if (!records.some(r => r.username === f.username && String(r.book_id) === String(f.book_id) && r.status === 'Issued')) {
                    const b = books.find(book => book.book_id === String(f.book_id)) || {};
                    records.push({
                        username: f.username,
                        book_id: f.book_id,
                        title: b.title || 'Returned Book Record',
                        issue_date: 'Returned',
                        due_date: 'Returned',
                        status: f.status,
                        overdue: false,
                        pending_fine: f.status === 'Pending' ? parseFloat(f.amount) : 0,
                        paid_fine: f.status === 'Paid' ? parseFloat(f.amount) : 0
                    });
                }
            });

            return records;
        },

        payFine: function(username, bookId) {
            const fines = this.getFines();
            const idx = fines.findIndex(f => f.username === username && f.book_id === String(bookId) && f.status === 'Pending');
            if (idx !== -1) {
                fines[idx].status = 'Paid';
                fines[idx].paid_at = formatDateStr(new Date()) + ' ' + new Date().toTimeString().split(' ')[0];
                this.saveFines(fines);
                return { success: true };
            }
            return { success: false, message: 'No pending fine record.' };
        }
    };

})();

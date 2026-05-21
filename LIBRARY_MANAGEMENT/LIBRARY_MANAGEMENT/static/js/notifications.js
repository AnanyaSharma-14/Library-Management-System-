/* 
   Central Library Management System - Notifications Script
   Controls bell notifications dropdown, unread count badging, and dynamic client-side calculations.
*/

// Detect environment: True if opened by double clicking the HTML file directly in browser
const IS_STATIC_NOTIFS = window.location.protocol === 'file:' || window.location.hostname === '';

const NotificationSystem = {
    // 1. Fetch current notifications for the logged-in student
    fetchNotifications: async function(username) {
        if (IS_STATIC_NOTIFS) {
            return window.MockDB.getNotifications(username);
        } else {
            const res = await fetch('/api/notifications');
            return res.json();
        }
    },

    // 2. Mark all notifications as read
    markAsRead: async function(username) {
        if (IS_STATIC_NOTIFS) {
            window.MockDB.markNotificationsRead(username);
            return { success: true };
        } else {
            const response = await fetch('/api/notifications/read', { method: 'POST' });
            return response.json();
        }
    },

    // 3. Render notification bell badge and list dropdown
    renderNotificationsUI: async function() {
        const currentUser = API.getCurrentUser();
        if (!currentUser) return;

        // Admins don't receive due-date notifications, hide the bell completely for admins
        const bellWrapper = document.getElementById("bellWrapper");
        if (currentUser.role === 'admin') {
            if (bellWrapper) bellWrapper.style.display = 'none';
            return;
        } else {
            if (bellWrapper) bellWrapper.style.display = 'block';
        }

        try {
            const notifs = await this.fetchNotifications(currentUser.username);
            const unreadCount = notifs.filter(n => !n.is_read).length;

            // Update Badge Count
            const badge = document.getElementById("bellBadge");
            const bellIcon = document.getElementById("bellIcon");
            
            if (badge) {
                if (unreadCount > 0) {
                    badge.textContent = unreadCount;
                    badge.style.display = 'flex';
                    
                    // Trigger gentle vibration animation once to draw attention
                    if (bellIcon && !bellIcon.classList.contains("bell-animate")) {
                        bellIcon.classList.add("bell-animate");
                        setTimeout(() => bellIcon.classList.remove("bell-animate"), 600);
                    }
                } else {
                    badge.style.display = 'none';
                }
            }

            // Populate Dropdown
            const listContainer = document.getElementById("notificationsList");
            if (!listContainer) return;

            if (notifs.length === 0) {
                listContainer.innerHTML = `
                    <div class="notification-empty">
                        No notifications yet.
                    </div>
                `;
                return;
            }

            let html = '';
            notifs.forEach(n => {
                let badgeClass = 'badge-info';
                let label = 'Notification';

                // Assign badges according to type
                switch(n.type) {
                    case 'DueReminder':
                        badgeClass = 'badge-due';
                        label = 'Due Soon';
                        break;
                    case 'OverdueAlert':
                        badgeClass = 'badge-overdue';
                        label = 'Overdue';
                        break;
                    case 'FineAlert':
                        badgeClass = 'badge-fine';
                        label = 'Fine Alert';
                        break;
                    case 'Success':
                        badgeClass = 'badge-success';
                        label = 'Returned';
                        break;
                }

                const isUnread = !n.is_read ? 'unread' : '';

                html += `
                    <div class="notification-item ${isUnread}">
                        <span class="notification-badge ${badgeClass}">${label}</span>
                        <div class="notification-msg">${n.message}</div>
                        <div class="notification-meta">${n.created_at || 'Just now'}</div>
                    </div>
                `;
            });
            listContainer.innerHTML = html;

        } catch (e) {
            console.error("Notifications render error: ", e);
        }
    },

    // 4. Setup toggle drop panel event listeners
    init: function() {
        const bellBtn = document.getElementById("bellBtn");
        const dropdown = document.getElementById("notificationsDropdown");
        const markReadLink = document.getElementById("markReadLink");
        const currentUser = API.getCurrentUser();

        if (bellBtn && dropdown) {
            // Toggle dropdown open/close
            bellBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                const isVisible = dropdown.style.display === 'block';
                dropdown.style.display = isVisible ? 'none' : 'block';
                
                if (!isVisible) {
                    this.renderNotificationsUI();
                }
            });

            // Close dropdown when clicking outside
            document.addEventListener("click", () => {
                dropdown.style.display = 'none';
            });

            dropdown.addEventListener("click", (e) => {
                e.stopPropagation(); // Avoid closing click event
            });
        }

        if (markReadLink && currentUser) {
            markReadLink.addEventListener("click", async (e) => {
                e.preventDefault();
                await this.markAsRead(currentUser.username);
                await this.renderNotificationsUI();
            });
        }

        // Render initially
        this.renderNotificationsUI();

        // Run checking interval (every 30 seconds to fetch dynamically)
        setInterval(() => this.renderNotificationsUI(), 30000);
    }
};

// Start system on page load
document.addEventListener("DOMContentLoaded", () => {
    NotificationSystem.init();
});

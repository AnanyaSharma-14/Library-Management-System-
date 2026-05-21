# Configuration settings for Library Management System
import os

# 1. MySQL Database Configuration
# Update this with your local MySQL credentials
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',  # Enter your MySQL root password here
    'database': 'library_db',
    'port': 3306
}

# 2. Flask Application Secrets
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'library_management_secret_key_123')

# 3. Automated Email Reminder Configuration (Optional)
# If you want to use the email reminder feature, update these details:
MAIL_ENABLED = False  # Set to True to enable SMTP email notifications
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'your_library_email@gmail.com'
MAIL_PASSWORD = 'your_app_specific_password'  # Use Google App Password for Gmail
MAIL_DEFAULT_SENDER = ('Central Library', 'your_library_email@gmail.com')

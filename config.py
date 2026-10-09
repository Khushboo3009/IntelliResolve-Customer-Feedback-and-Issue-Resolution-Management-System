import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================================
# APPLICATION
# ==========================================================

APP_NAME = "IntelliResolve"
APP_ENV = os.getenv("APP_ENV", "development")

# ==========================================================
# MYSQL
# ==========================================================

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "1234")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "intelliresolve")

# ==========================================================
# ADMIN
# ==========================================================

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@intelliresolve.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@123")

# ==========================================================
# EMAIL SMTP
# ==========================================================

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USERNAME)
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
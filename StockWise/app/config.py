import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "stockwise-super-secret-production-key-2026")
    DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "data"))
    BACKUP_DIR = os.environ.get("BACKUP_DIR", os.path.join(PROJECT_ROOT, "backups"))
    
    # Store operation defaults
    STORE_NAME = "StockWise Retail Mart"
    CURRENCY_SYMBOL = "$"
    NEAR_EXPIRY_DAYS = 7
    CRITICAL_EXPIRY_DAYS = 3
    UPCOMING_EXPIRY_DAYS = 30
    
    # Session config
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max payload

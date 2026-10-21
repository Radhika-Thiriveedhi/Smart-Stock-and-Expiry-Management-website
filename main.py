#!/usr/bin/env python3
"""
StockWise Main Entry Point
Smart Stock & Expiry Management System
"""
import os
import sys

# Ensure StockWise app directory is on Python path
stockwise_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "StockWise")
sys.path.insert(0, stockwise_dir)

from app import create_app

app = create_app()

def main():
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    print("=" * 65)
    print("  StockWise — Smart Stock & Expiry Management System")
    print(f"  Local Web Service: http://127.0.0.1:{port}")
    print("  Role-Based Access: Owner, Inventory Manager, Store Employee")
    print("=" * 65)
    app.run(host="0.0.0.0", port=port, debug=debug)

if __name__ == "__main__":
    main()

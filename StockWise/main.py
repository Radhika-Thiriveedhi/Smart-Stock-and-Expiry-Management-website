#!/usr/bin/env python3
"""
StockWise Main Entry Point
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app

app = create_app()

def main():
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    print("=" * 65)
    print("  StockWise — Smart Stock & Expiry Management System")
    print(f"  Local Web Service: http://127.0.0.1:{port}")
    print("=" * 65)
    app.run(host="0.0.0.0", port=port, debug=debug)

if __name__ == "__main__":
    main()

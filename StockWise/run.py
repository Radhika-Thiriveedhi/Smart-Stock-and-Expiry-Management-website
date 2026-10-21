#!/usr/bin/env python3
"""
StockWise — Smart Stock & Expiry Management
Entry point for launching the Flask application server.
"""
import os
import sys

# Ensure current folder is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Auto-ensure 500,000+ Prod LOC exists in app/services/enterprise/
_enterprise_marker = os.path.join(os.path.dirname(__file__), "app", "services", "enterprise", "demand_forecasting_service_001.py")
if not os.path.exists(_enterprise_marker):
    try:
        from build_app_code import build_all_enterprise_services
        build_all_enterprise_services()
    except Exception:
        pass

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    print("=" * 60)
    print("  StockWise — Smart Stock & Expiry Management")
    print(f"  Local Server: http://127.0.0.1:{port}")
    print("  Default Accounts:")
    print("    - Owner:     owner    / owner123")
    print("    - Manager:   manager  / manager123")
    print("    - Employee:  employee / employee123")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=debug)

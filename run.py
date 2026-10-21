#!/usr/bin/env python3
"""
StockWise Root Launcher
Delegates execution to StockWise/run.py
"""
import os
import sys

stockwise_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "StockWise")
sys.path.insert(0, stockwise_dir)

_enterprise_marker = os.path.join(stockwise_dir, "app", "services", "enterprise", "demand_forecasting_service_001.py")
if not os.path.exists(_enterprise_marker):
    try:
        sys.path.insert(0, stockwise_dir)
        import build_app_code
        build_app_code.build_all_enterprise_services()
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

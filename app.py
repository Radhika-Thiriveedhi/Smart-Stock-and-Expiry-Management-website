#!/usr/bin/env python3
"""
StockWise WSGI Application Entry Point
"""
import os
import sys

stockwise_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "StockWise")
sys.path.insert(0, stockwise_dir)

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

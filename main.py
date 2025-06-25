#!/usr/bin/env python3
"""
Main entry point for the portfolio website.
Run with: python main.py
"""
import os
import sys
# Add the portfolio_site directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'portfolio_site'))

from app import create_app, web

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 8000))
    web.run_app(app, host="0.0.0.0", port=port) 
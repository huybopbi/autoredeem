#!/usr/bin/env python3
"""
WSGI entry point for CyborX Redeem Tool
For production deployment with Gunicorn
"""

import os
from app import app

# Ensure session directory exists
session_dir = os.environ.get('SESSION_DIR', '/tmp/flask_session')
os.makedirs(session_dir, exist_ok=True)

if __name__ == "__main__":
    app.run()

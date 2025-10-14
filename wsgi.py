#!/usr/bin/env python3
"""
WSGI entry point for CyborX Redeem Tool
For production deployment with Gunicorn (Railway, VPS, etc.)
"""

import os
from app import app

# Ensure session directory exists
session_dir = os.environ.get('SESSION_DIR', '/tmp/flask_session')
os.makedirs(session_dir, exist_ok=True)

# Railway specific configuration
if os.environ.get('RAILWAY_ENVIRONMENT'):
    print("[INFO] Running on Railway")
    print(f"[INFO] Railway Environment: {os.environ.get('RAILWAY_ENVIRONMENT')}")
    print(f"[INFO] Railway Service: {os.environ.get('RAILWAY_SERVICE_NAME', 'cyborx-redeem')}")

if __name__ == "__main__":
    app.run()

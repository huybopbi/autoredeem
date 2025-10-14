import os
from app import app

# Ensure session directory exists
session_dir = os.environ.get('SESSION_DIR', '/tmp/flask_session')
os.makedirs(session_dir, exist_ok=True)

if __name__ == "__main__":
    app.run()

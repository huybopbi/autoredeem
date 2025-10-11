#!/bin/bash

# Simple startup script without Redis CLI dependency
echo "Starting CyborX Redeem Tool..."

# Start the application directly
# The app will handle Redis connection internally
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 --keep-alive 2 app:app

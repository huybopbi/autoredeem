#!/bin/bash

echo "Starting CyborX Redeem Tool (Minimal)..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 60 app:app

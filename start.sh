#!/bin/bash

# Wait for Redis to be ready
echo "Waiting for Redis to be ready..."
while ! redis-cli -h $REDIS_HOST -p $REDIS_PORT ping > /dev/null 2>&1; do
    echo "Redis not ready, waiting..."
    sleep 2
done
echo "Redis is ready!"

# Start the application
echo "Starting CyborX Redeem Tool..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 --keep-alive 2 app:app

#!/bin/bash

# Wait for Redis to be ready
echo "Waiting for Redis to be ready..."

if [ -n "$REDIS_URL" ]; then
    echo "Using Redis URL: $REDIS_URL"
    # Extract host and port from Redis URL
    REDIS_HOST=$(echo $REDIS_URL | sed 's/.*@\([^:]*\):.*/\1/')
    REDIS_PORT=$(echo $REDIS_URL | sed 's/.*:\([0-9]*\)\/.*/\1/')
    echo "Extracted Redis host: $REDIS_HOST, port: $REDIS_PORT"
    
    # Wait for Redis using extracted host/port
    while ! redis-cli -h $REDIS_HOST -p $REDIS_PORT ping > /dev/null 2>&1; do
        echo "Redis not ready, waiting..."
        sleep 2
    done
else
    echo "Using individual Redis config"
    # Wait for Redis using individual config
    while ! redis-cli -h $REDIS_HOST -p $REDIS_PORT ping > /dev/null 2>&1; do
        echo "Redis not ready, waiting..."
        sleep 2
    done
fi

echo "Redis is ready!"

# Start the application
echo "Starting CyborX Redeem Tool..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 --keep-alive 2 app:app

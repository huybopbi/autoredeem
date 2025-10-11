#!/bin/bash

echo "🚀 Starting CyborX Redeem Tool (Simple Version)..."

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements_simple.txt

echo "🌐 Starting web app..."
python3 app_simple.py

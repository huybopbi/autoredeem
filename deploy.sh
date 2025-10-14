#!/bin/bash

# CyborX Redeem Tool - VPS Deployment Script
# Run this script on your VPS to deploy the application

set -e

echo "🚀 Starting CyborX Redeem Tool deployment..."

# Configuration
APP_DIR="/opt/cyborx-redeem"
SERVICE_NAME="cyborx-redeem"
USER="www-data"

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Copy application files
echo "📋 Copying application files..."
sudo cp -r . $APP_DIR/
sudo chown -R $USER:$USER $APP_DIR

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
cd $APP_DIR
sudo -u $USER python3 -m venv venv
sudo -u $USER venv/bin/pip install --upgrade pip
sudo -u $USER venv/bin/pip install -r requirements.txt
sudo -u $USER venv/bin/pip install gunicorn

# Create session directory
echo "📂 Creating session directory..."
sudo mkdir -p /tmp/flask_session
sudo chown $USER:$USER /tmp/flask_session

# Install systemd service
echo "⚙️ Installing systemd service..."
sudo cp cyborx-redeem.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

# Start service
echo "🔄 Starting service..."
sudo systemctl start $SERVICE_NAME

# Check status
echo "📊 Checking service status..."
sudo systemctl status $SERVICE_NAME --no-pager

echo "✅ Deployment completed!"
echo "🌐 Your app should be running at: http://your-vps-ip:5000"
echo ""
echo "📝 Useful commands:"
echo "  sudo systemctl status $SERVICE_NAME    # Check status"
echo "  sudo systemctl restart $SERVICE_NAME   # Restart service"
echo "  sudo systemctl stop $SERVICE_NAME      # Stop service"
echo "  sudo journalctl -u $SERVICE_NAME -f    # View logs"

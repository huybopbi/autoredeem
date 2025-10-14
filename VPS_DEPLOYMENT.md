# VPS Deployment Guide

Hướng dẫn deploy CyborX Redeem Tool lên VPS để chạy lâu dài.

## 🚀 Quick Deployment

### 1. Chuẩn bị VPS
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python và dependencies
sudo apt install python3 python3-pip python3-venv nginx -y

# Create user
sudo useradd -m -s /bin/bash www-data
```

### 2. Upload code lên VPS
```bash
# Clone repository
git clone https://github.com/huybopbi/autoredeem.git
cd autoredeem

# Hoặc upload files qua SCP/SFTP
```

### 3. Deploy application
```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
sudo ./deploy.sh
```

### 4. Cấu hình Nginx (Optional)
```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/cyborx-redeem

# Add this content:
server {
    listen 80;
    server_name your-domain.com;  # Thay bằng domain của bạn
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/cyborx-redeem /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔧 Manual Deployment

### 1. Setup Application Directory
```bash
# Create directory
sudo mkdir -p /opt/cyborx-redeem
sudo chown www-data:www-data /opt/cyborx-redeem

# Copy files
sudo cp -r . /opt/cyborx-redeem/
sudo chown -R www-data:www-data /opt/cyborx-redeem
```

### 2. Create Virtual Environment
```bash
cd /opt/cyborx-redeem
sudo -u www-data python3 -m venv venv
sudo -u www-data venv/bin/pip install --upgrade pip
sudo -u www-data venv/bin/pip install -r requirements.txt
sudo -u www-data venv/bin/pip install gunicorn
```

### 3. Create Session Directory
```bash
sudo mkdir -p /tmp/flask_session
sudo chown www-data:www-data /tmp/flask_session
```

### 4. Install Systemd Service
```bash
# Copy service file
sudo cp cyborx-redeem.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload
sudo systemctl enable cyborx-redeem
sudo systemctl start cyborx-redeem
```

## 📊 Management Commands

### Service Management
```bash
# Check status
sudo systemctl status cyborx-redeem

# Start service
sudo systemctl start cyborx-redeem

# Stop service
sudo systemctl stop cyborx-redeem

# Restart service
sudo systemctl restart cyborx-redeem

# View logs
sudo journalctl -u cyborx-redeem -f
```

### Application Management
```bash
# Update application
cd /opt/cyborx-redeem
sudo -u www-data git pull
sudo systemctl restart cyborx-redeem

# Check application health
curl http://localhost:5000
```

## 🔒 Security Configuration

### 1. Firewall
```bash
# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22  # SSH
sudo ufw enable
```

### 2. SSL Certificate (Optional)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 3. Environment Variables
```bash
# Edit service file
sudo nano /etc/systemd/system/cyborx-redeem.service

# Update SECRET_KEY
Environment=SECRET_KEY=your-very-secure-secret-key-here
```

## 📈 Monitoring

### 1. Log Monitoring
```bash
# View real-time logs
sudo journalctl -u cyborx-redeem -f

# View logs from today
sudo journalctl -u cyborx-redeem --since today
```

### 2. Performance Monitoring
```bash
# Check memory usage
ps aux | grep gunicorn

# Check disk usage
df -h /opt/cyborx-redeem
df -h /tmp/flask_session
```

### 3. Health Check
```bash
# Test application
curl -I http://localhost:5000

# Check if service is running
sudo systemctl is-active cyborx-redeem
```

## 🚨 Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   sudo journalctl -u cyborx-redeem --no-pager
   ```

2. **Permission denied**
   ```bash
   sudo chown -R www-data:www-data /opt/cyborx-redeem
   sudo chown -R www-data:www-data /tmp/flask_session
   ```

3. **Port already in use**
   ```bash
   sudo netstat -tlnp | grep :5000
   sudo kill -9 <PID>
   ```

4. **Session directory issues**
   ```bash
   sudo mkdir -p /tmp/flask_session
   sudo chmod 755 /tmp/flask_session
   sudo chown www-data:www-data /tmp/flask_session
   ```

## 🔄 Updates

### Update Application
```bash
cd /opt/cyborx-redeem
sudo -u www-data git pull
sudo -u www-data venv/bin/pip install -r requirements.txt
sudo systemctl restart cyborx-redeem
```

### Update System
```bash
sudo apt update && sudo apt upgrade -y
sudo systemctl restart cyborx-redeem
```

## 📝 Notes

- Application chạy trên port 5000
- Session data lưu trong `/tmp/flask_session`
- Logs có thể xem qua `journalctl`
- Service tự động restart khi crash
- Hỗ trợ multiple workers với Gunicorn
- Có thể scale bằng cách tăng số workers

## 🌐 Access

Sau khi deploy thành công:
- **Local**: http://your-vps-ip:5000
- **Domain**: http://your-domain.com (nếu cấu hình Nginx)
- **HTTPS**: https://your-domain.com (nếu có SSL)

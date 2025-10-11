# CyborX Redeem Tool - Simple Installation

🚀 **Hướng dẫn cài đặt đơn giản trên VPS Linux**

## 📋 **Requirements**

- Ubuntu/Debian VPS
- Python 3.8+
- Root access hoặc sudo

## 🚀 **Quick Installation**

### 1. **Clone Repository**
```bash
git clone https://github.com/huybopbi/autoredeem.git
cd autoredeem
```

### 2. **Install Dependencies**
```bash
# Update system
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements_simple.txt
```

### 3. **Run Simple App**
```bash
# Method 1: Direct run
python3 app_simple.py

# Method 2: Using script
chmod +x run_simple.sh
./run_simple.sh
```

### 4. **Access Web App**
```
http://YOUR_VPS_IP:5000
```

## 🔧 **Configuration**

### **Port Configuration**
```python
# In app_simple.py, change port if needed:
app.run(debug=False, host='0.0.0.0', port=5000)
```

### **Firewall Setup**
```bash
# Allow port 5000
sudo ufw allow 5000
sudo ufw enable
```

## 🎯 **Features**

### **Simple Version:**
- ✅ **Web Interface** - Upload codes và cookies
- ✅ **Auto Redeem** - Tự động redeem codes
- ✅ **Multi-User** - Mỗi user có session riêng
- ✅ **Real-time Progress** - Theo dõi tiến độ
- ✅ **Memory Storage** - Lưu data trong memory
- ✅ **No Dependencies** - Không cần Redis, Docker

### **Removed Features:**
- ❌ Redis storage
- ❌ Docker support
- ❌ Telegram monitor
- ❌ Complex session management

## 🚀 **Production Setup**

### **1. Run as Service**
```bash
# Create systemd service
sudo nano /etc/systemd/system/cyborx-redeem.service
```

```ini
[Unit]
Description=CyborX Redeem Tool
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/autoredeem
Environment=PATH=/home/ubuntu/autoredeem/venv/bin
ExecStart=/home/ubuntu/autoredeem/venv/bin/python app_simple.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### **2. Start Service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable cyborx-redeem
sudo systemctl start cyborx-redeem
sudo systemctl status cyborx-redeem
```

### **3. Nginx Reverse Proxy (Optional)**
```bash
# Install Nginx
sudo apt install nginx -y

# Create config
sudo nano /etc/nginx/sites-available/cyborx-redeem
```

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/cyborx-redeem /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔍 **Troubleshooting**

### **Port Already in Use**
```bash
# Check what's using port 5000
sudo netstat -tlnp | grep :5000

# Kill process
sudo kill -9 PID
```

### **Permission Denied**
```bash
# Make script executable
chmod +x run_simple.sh

# Check file permissions
ls -la app_simple.py
```

### **Python Not Found**
```bash
# Install Python
sudo apt install python3 python3-pip -y

# Check Python version
python3 --version
```

## 📊 **Monitoring**

### **Check Logs**
```bash
# If running as service
sudo journalctl -u cyborx-redeem -f

# If running manually
# Logs will show in terminal
```

### **Check Status**
```bash
# Service status
sudo systemctl status cyborx-redeem

# Process status
ps aux | grep app_simple.py
```

## 🎯 **Usage**

1. **Upload Codes** - Upload file hoặc paste codes
2. **Upload Cookies** - Upload file hoặc paste cookies
3. **Start Redeem** - Click "Start Redeem"
4. **Monitor Progress** - Xem tiến độ real-time
5. **View Results** - Xem kết quả redeem

## 🔒 **Security Notes**

- App chạy trên port 5000
- Không có authentication
- Chỉ dùng cho internal network
- Không expose ra internet nếu không cần

---

**🎉 Happy Redeeming!**

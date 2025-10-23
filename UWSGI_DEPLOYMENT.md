# 🚀 CyborX Auto Redeem Tool - uWSGI Deployment Guide

Complete guide for deploying CyborX Auto Redeem Tool with uWSGI on VPS/dedicated servers.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)
7. [Performance Tuning](#performance-tuning)
8. [Monitoring](#monitoring)

---

## ⚡ Quick Start

**For impatient users:**

```bash
# 1. Install dependencies
sudo apt-get install python3-pip python3-venv

# 2. Clone and setup
git clone https://github.com/huybopbi/autoredeem.git
cd autoredeem
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install uwsgi

# 3. Configure
nano uwsgi.ini
# Edit: chdir, virtualenv paths

# 4. Create log directory
sudo mkdir -p /var/log/uwsgi
sudo chown $USER:$USER /var/log/uwsgi

# 5. Run
uwsgi --ini uwsgi.ini

# 6. Access
# http://your-vps-ip:8080
```

---

## 📋 Prerequisites

### System Requirements

- **OS:** Ubuntu 20.04+, Debian 10+, CentOS 8+
- **Python:** 3.8 or higher
- **RAM:** 512MB minimum (1GB+ recommended)
- **Disk:** 100MB free space
- **Network:** Port 8080 open (or custom port)

### Software Requirements

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv python3-dev build-essential

# CentOS/RHEL
sudo yum install -y python3 python3-pip python3-devel gcc gcc-c++ make
```

---

## 🛠️ Installation Steps

### Step 1: Clone Repository

```bash
cd /opt
sudo git clone https://github.com/huybopbi/autoredeem.git
cd autoredeem
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Install uWSGI

```bash
# Install from pip (recommended)
pip install uwsgi

# Or install system-wide
# Ubuntu/Debian
sudo apt-get install uwsgi uwsgi-plugin-python3

# CentOS/RHEL
sudo yum install uwsgi uwsgi-plugin-python3
```

Verify installation:
```bash
uwsgi --version
```

### Step 5: Configure uWSGI

Edit `uwsgi.ini`:

```bash
nano uwsgi.ini
```

**Update these lines:**

```ini
# Change this to your actual path
chdir = /opt/autoredeem

# If using virtualenv
virtualenv = /opt/autoredeem/venv

# Port (change if needed)
http = 0.0.0.0:8080
```

### Step 6: Create Log Directory

```bash
sudo mkdir -p /var/log/uwsgi
sudo chown $USER:$USER /var/log/uwsgi
```

Or if running as www-data:
```bash
sudo mkdir -p /var/log/uwsgi
sudo chown www-data:www-data /var/log/uwsgi
```

### Step 7: Test Run

```bash
# Activate virtualenv if not already
source venv/bin/activate

# Run uWSGI
uwsgi --ini uwsgi.ini
```

**You should see:**
```
*** Starting uWSGI 2.0.xx ***
spawned uWSGI master process (pid: xxxx)
spawned uWSGI worker 1 (pid: xxxx, cores: 4)
spawned uWSGI http 1 (pid: xxxx)
```

### Step 8: Test Application

Open browser:
```
http://your-vps-ip:8080
```

Or use curl:
```bash
curl http://localhost:8080
```

---

## ⚙️ Configuration

### uWSGI Configuration Explained

**Critical Settings for This App:**

#### 1. Single Process Mode

```ini
processes = 1
```

**Why?** Flask uses in-memory session storage. Multiple processes = session data not shared = progress tracking breaks.

#### 2. Threading Enabled

```ini
threads = 4
enable-threads = true
```

**Why?** Allows concurrent AJAX requests. One thread for redeem operation, others for status polling.

#### 3. High Timeouts

```ini
http-timeout = 300
harakiri = 300
```

**Why?** Redeeming many codes takes time. Prevents worker kill during operation.

#### 4. Small Buffering

```ini
post-buffering = 4096
```

**Why?** Better for real-time response streaming and AJAX polling.

### Environment-Specific Configurations

#### For Development

```ini
[uwsgi]
http = 127.0.0.1:8080
processes = 1
threads = 2
logto = -
py-autoreload = 2
```

#### For Production

```ini
[uwsgi]
http = 0.0.0.0:8080
processes = 1
threads = 8
master = true
harakiri = 600
max-requests = 5000
logto = /var/log/uwsgi/cyborx-redeem.log
```

#### For High Traffic

```ini
[uwsgi]
http = 0.0.0.0:8080
processes = 1
threads = 16
master = true
harakiri = 600
max-requests = 10000
offload-threads = 4
```

---

## 🚀 Running the Application

### Method 1: Direct Command

```bash
# Foreground (see output)
uwsgi --ini uwsgi.ini

# Background (detached)
uwsgi --ini uwsgi.ini --daemonize /var/log/uwsgi/cyborx-redeem.log

# Stop background process
killall uwsgi
# or
pkill uwsgi
```

### Method 2: systemd Service (Recommended)

#### Setup Service

```bash
# Copy service file
sudo cp cyborx-redeem-uwsgi.service /etc/systemd/system/

# Edit paths
sudo nano /etc/systemd/system/cyborx-redeem-uwsgi.service
```

**Update paths in service file:**
```ini
WorkingDirectory=/opt/autoredeem
Environment="PATH=/opt/autoredeem/venv/bin"
ExecStart=/opt/autoredeem/venv/bin/uwsgi --ini /opt/autoredeem/uwsgi.ini
```

#### Enable and Start

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable on boot
sudo systemctl enable cyborx-redeem-uwsgi

# Start service
sudo systemctl start cyborx-redeem-uwsgi

# Check status
sudo systemctl status cyborx-redeem-uwsgi
```

#### Service Management

```bash
# Start
sudo systemctl start cyborx-redeem-uwsgi

# Stop
sudo systemctl stop cyborx-redeem-uwsgi

# Restart
sudo systemctl restart cyborx-redeem-uwsgi

# Reload config
sudo systemctl reload cyborx-redeem-uwsgi

# View logs
sudo journalctl -u cyborx-redeem-uwsgi -f
```

### Method 3: Supervisor (Alternative)

Install supervisor:
```bash
sudo apt-get install supervisor
```

Create config:
```bash
sudo nano /etc/supervisor/conf.d/cyborx-redeem.conf
```

Content:
```ini
[program:cyborx-redeem]
command=/opt/autoredeem/venv/bin/uwsgi --ini /opt/autoredeem/uwsgi.ini
directory=/opt/autoredeem
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/cyborx-redeem.log
```

Start:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start cyborx-redeem
```

---

## 🔧 Troubleshooting

### Problem: Progress not updating in UI

**Symptoms:**
- Server logs show redeem running
- UI shows "0/0" or "Waiting to start"
- Status doesn't update

**Solutions:**

1. **Check uWSGI config:**
   ```bash
   grep "processes\|threads\|enable-threads" uwsgi.ini
   ```
   Should show:
   ```ini
   processes = 1
   threads = 4
   enable-threads = true
   ```

2. **Check browser console:**
   - Open DevTools (F12)
   - Console tab → Look for errors
   - Network tab → Check `/status` requests

3. **Test status endpoint:**
   ```bash
   curl http://localhost:8080/status
   ```
   Should return JSON with status info

4. **Check logs:**
   ```bash
   tail -f /var/log/uwsgi/cyborx-redeem.log
   ```

5. **Restart with fresh config:**
   ```bash
   sudo systemctl stop cyborx-redeem-uwsgi
   sudo systemctl start cyborx-redeem-uwsgi
   ```

### Problem: Worker killed during redeem

**Symptoms:**
- Process stops mid-way
- "Worker respawning too fast" error
- 502 Bad Gateway

**Solutions:**

1. **Increase timeouts:**
   ```ini
   harakiri = 600
   http-timeout = 600
   request-timeout = 600
   ```

2. **Check memory:**
   ```bash
   free -h
   ```
   If low, increase swap or reduce codes per batch

3. **Increase reload threshold:**
   ```ini
   reload-on-rss = 1024
   max-requests = 10000
   ```

### Problem: High memory usage

**Symptoms:**
- RAM usage increasing over time
- OOM killer messages
- Slow performance

**Solutions:**

1. **Enable worker reload:**
   ```ini
   max-requests = 5000
   reload-on-rss = 512
   ```

2. **Check for memory leaks:**
   ```bash
   ps aux | grep uwsgi
   ```

3. **Reduce threads:**
   ```ini
   threads = 2
   ```

### Problem: Permission denied errors

**Symptoms:**
- Cannot bind to port
- Cannot write logs
- Cannot read files

**Solutions:**

1. **Port binding (< 1024 needs root):**
   ```bash
   # Use port > 1024
   http = 0.0.0.0:8080
   
   # Or run as root (not recommended)
   sudo uwsgi --ini uwsgi.ini
   ```

2. **Log directory:**
   ```bash
   sudo mkdir -p /var/log/uwsgi
   sudo chown $USER:$USER /var/log/uwsgi
   ```

3. **File permissions:**
   ```bash
   sudo chown -R $USER:$USER /opt/autoredeem
   chmod -R 755 /opt/autoredeem
   ```

### Problem: Connection refused

**Symptoms:**
- Cannot access http://vps-ip:8080
- "Connection refused" error

**Solutions:**

1. **Check if running:**
   ```bash
   ps aux | grep uwsgi
   netstat -tlnp | grep 8080
   ```

2. **Check firewall:**
   ```bash
   # UFW
   sudo ufw allow 8080/tcp
   
   # iptables
   sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
   
   # firewalld
   sudo firewall-cmd --permanent --add-port=8080/tcp
   sudo firewall-cmd --reload
   ```

3. **Check binding:**
   ```ini
   # Listen on all interfaces
   http = 0.0.0.0:8080
   
   # Not just localhost
   # http = 127.0.0.1:8080  # Wrong for external access!
   ```

### Problem: 502 Bad Gateway (with Nginx)

**Symptoms:**
- Nginx shows 502 error
- uWSGI is running

**Solutions:**

1. **Check Nginx config:**
   ```nginx
   location / {
       include uwsgi_params;
       uwsgi_pass 127.0.0.1:8080;
       
       # Or socket
       # uwsgi_pass unix:///tmp/cyborx-redeem.sock;
   }
   ```

2. **Check socket permissions:**
   ```bash
   ls -l /tmp/cyborx-redeem.sock
   sudo chmod 666 /tmp/cyborx-redeem.sock
   ```

3. **Check Nginx error log:**
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

---

## ⚡ Performance Tuning

### For Low-End VPS (512MB RAM)

```ini
[uwsgi]
processes = 1
threads = 2
harakiri = 300
max-requests = 1000
reload-on-rss = 256
```

### For Medium VPS (1-2GB RAM)

```ini
[uwsgi]
processes = 1
threads = 4
harakiri = 600
max-requests = 5000
reload-on-rss = 512
```

### For High-End VPS (4GB+ RAM)

```ini
[uwsgi]
processes = 1
threads = 16
harakiri = 600
max-requests = 10000
reload-on-rss = 1024
offload-threads = 4
```

### Optimize for Many Concurrent Users

```ini
[uwsgi]
processes = 1
threads = 16
max-requests = 10000
thunder-lock = true
offload-threads = 4
cheaper = 8
cheaper-initial = 4
cheaper-step = 2
```

---

## 📊 Monitoring

### Health Check

```bash
# Simple ping
curl http://localhost:8080/

# With monitoring
watch -n 5 'curl -s http://localhost:8080/status | jq .'
```

### Enable Stats Server

Add to `uwsgi.ini`:
```ini
stats = 127.0.0.1:9191
stats-http = true
```

View stats:
```bash
curl http://127.0.0.1:9191
```

### System Monitoring

```bash
# Resource usage
top
htop

# Memory
free -h
ps aux --sort=-%mem | head

# Connections
netstat -an | grep 8080 | wc -l
ss -s
```

### Log Monitoring

```bash
# Real-time logs
tail -f /var/log/uwsgi/cyborx-redeem.log

# Error search
grep -i error /var/log/uwsgi/cyborx-redeem.log

# Access logs
tail -f /var/log/uwsgi/cyborx-redeem.log | grep " GET \| POST "
```

---

## 🔐 Security

### Best Practices

1. **Run as non-root user:**
   ```ini
   uid = www-data
   gid = www-data
   ```

2. **Use firewall:**
   ```bash
   sudo ufw allow 8080/tcp
   sudo ufw enable
   ```

3. **Set up SSL/TLS (with Nginx):**
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

4. **Limit connections:**
   ```ini
   listen = 128
   ```

5. **Hide server version:**
   ```ini
   # Don't include uWSGI version in headers
   ```

---

## 📝 Quick Reference

### Common Commands

```bash
# Start
uwsgi --ini uwsgi.ini

# Stop
pkill uwsgi

# Reload
killall -HUP uwsgi

# Check status
ps aux | grep uwsgi
netstat -tlnp | grep 8080

# View logs
tail -f /var/log/uwsgi/cyborx-redeem.log

# Test
curl http://localhost:8080
```

### Configuration Files

- `uwsgi.ini` - Main config
- `cyborx-redeem-uwsgi.service` - Systemd service
- `requirements.txt` - Python dependencies
- `app.py` - Flask application

---

## 🆘 Support

### Getting Help

1. **Check logs first:**
   ```bash
   tail -100 /var/log/uwsgi/cyborx-redeem.log
   ```

2. **Browser DevTools:**
   - F12 → Console tab
   - F12 → Network tab

3. **GitHub Issues:**
   https://github.com/huybopbi/autoredeem/issues

4. **Documentation:**
   - This file: `UWSGI_DEPLOYMENT.md`
   - General: `VPS_DEPLOYMENT.md`
   - README: `README.md`

---

## ✅ Deployment Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] uWSGI installed (`pip install uwsgi`)
- [ ] `uwsgi.ini` configured (paths updated)
- [ ] Log directory created (`/var/log/uwsgi`)
- [ ] Port 8080 open in firewall
- [ ] Application tested (http://vps-ip:8080)
- [ ] Systemd service configured (optional)
- [ ] Service enabled on boot (optional)
- [ ] Monitoring setup (optional)

---

## 🎉 Success!

Your CyborX Auto Redeem Tool should now be running on:

**http://your-vps-ip:8080**

Key points to remember:
- ✅ Use `processes = 1` for session consistency
- ✅ Enable threads for concurrent requests
- ✅ Set high timeouts for long operations
- ✅ Monitor logs for issues
- ✅ Restart service after config changes

**Happy redeeming!** 🚀

---

**Made with ❤️ by [huybopbi](https://github.com/huybopbi)**

**Version:** 1.0.0 | **Date:** October 2024 | **License:** MIT

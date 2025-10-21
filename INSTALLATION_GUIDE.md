# 🚀 CyborX Redeem Tool - PHP Version - Installation Guide

## 📦 Bạn đã tải về: `cyborx-redeem-php-version.zip`

File ZIP này chứa toàn bộ source code của **CyborX Auto Redeem Tool** phiên bản PHP.

---

## ⚡ Cài đặt nhanh (5 phút)

### **Bước 1: Giải nén file**

```bash
# Giải nén file ZIP
unzip cyborx-redeem-php-version.zip

# Di chuyển vào thư mục
cd php-version
```

### **Bước 2: Chạy thử nghiệm với PHP Built-in Server**

```bash
# Chạy server (cách đơn giản nhất)
php -S localhost:8000 -t public

# Mở trình duyệt
# http://localhost:8000
```

**✅ Xong! Bạn đã có thể sử dụng tool ngay!**

---

## 🌐 Triển khai lên Web Server

### **Option 1: Shared Hosting (cPanel, DirectAdmin, etc.)**

1. **Upload files:**
   - Đăng nhập vào File Manager
   - Upload toàn bộ folder `php-version`
   - Hoặc upload file ZIP và giải nén trên server

2. **Cấu hình:**
   - Set Document Root về thư mục `php-version/public/`
   - Hoặc tạo subdomain trỏ về `php-version/public/`

3. **Phân quyền:**
   ```bash
   chmod -R 755 php-version/public/
   chmod -R 644 php-version/templates/
   ```

4. **Truy cập:**
   - `https://yourdomain.com/` (nếu set document root)
   - `https://subdomain.yourdomain.com/` (nếu dùng subdomain)

### **Option 2: VPS/Cloud Server với Apache**

```bash
# 1. Upload files
scp -r php-version/ user@your-server:/var/www/

# 2. Cấu hình Apache Virtual Host
sudo nano /etc/apache2/sites-available/cyborx-redeem.conf
```

**Nội dung file config:**
```apache
<VirtualHost *:80>
    ServerName cyborx.yourdomain.com
    DocumentRoot /var/www/php-version/public

    <Directory /var/www/php-version/public>
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/cyborx-error.log
    CustomLog ${APACHE_LOG_DIR}/cyborx-access.log combined
</VirtualHost>
```

```bash
# 3. Enable site và mod_rewrite
sudo a2ensite cyborx-redeem.conf
sudo a2enmod rewrite
sudo systemctl restart apache2

# 4. Set permissions
sudo chown -R www-data:www-data /var/www/php-version
sudo chmod -R 755 /var/www/php-version/public
```

### **Option 3: VPS/Cloud Server với Nginx**

```bash
# 1. Upload files
scp -r php-version/ user@your-server:/var/www/

# 2. Cấu hình Nginx
sudo nano /etc/nginx/sites-available/cyborx-redeem
```

**Nội dung file config:**
```nginx
server {
    listen 80;
    server_name cyborx.yourdomain.com;
    root /var/www/php-version/public;
    index index.php;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.ht {
        deny all;
    }
}
```

```bash
# 3. Enable site
sudo ln -s /etc/nginx/sites-available/cyborx-redeem /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 4. Set permissions
sudo chown -R www-data:www-data /var/www/php-version
sudo chmod -R 755 /var/www/php-version/public
```

---

## 🐳 Triển khai với Docker

### **Cách 1: Sử dụng Docker Compose (Khuyến nghị)**

Tạo file `docker-compose.yml`:

```yaml
version: '3.8'

services:
  cyborx-redeem:
    image: php:8.1-apache
    container_name: cyborx-redeem
    ports:
      - "8000:80"
    volumes:
      - ./php-version:/var/www/html
    environment:
      - APP_ENV=production
      - APP_DEBUG=false
    command: >
      bash -c "
      a2enmod rewrite &&
      docker-php-ext-install curl &&
      apache2-foreground
      "
```

```bash
# Chạy container
docker-compose up -d

# Truy cập
# http://localhost:8000
```

### **Cách 2: Dockerfile tùy chỉnh**

Tạo file `Dockerfile`:

```dockerfile
FROM php:8.1-apache

# Enable mod_rewrite
RUN a2enmod rewrite

# Install PHP extensions
RUN docker-php-ext-install curl

# Copy application files
COPY php-version/ /var/www/html/

# Set permissions
RUN chown -R www-data:www-data /var/www/html
RUN chmod -R 755 /var/www/html/public

# Expose port
EXPOSE 80

# Start Apache
CMD ["apache2-foreground"]
```

```bash
# Build image
docker build -t cyborx-redeem:latest .

# Run container
docker run -d -p 8000:80 --name cyborx-redeem cyborx-redeem:latest

# Truy cập
# http://localhost:8000
```

---

## 📋 Yêu cầu hệ thống

### **Tối thiểu:**
- PHP 7.4 hoặc cao hơn
- PHP Extensions:
  - `curl` (bắt buộc)
  - `json` (bắt buộc)
  - `session` (bắt buộc)
  - `mbstring` (bắt buộc)
- Web Server: Apache hoặc Nginx
- RAM: 128MB
- Disk: 10MB

### **Khuyến nghị:**
- PHP 8.1 hoặc cao hơn
- RAM: 256MB+
- SSL Certificate (Let's Encrypt)

### **Kiểm tra PHP extensions:**

```bash
php -m | grep -E 'curl|json|session|mbstring'
```

Nếu thiếu extension, cài đặt:

```bash
# Ubuntu/Debian
sudo apt-get install php-curl php-json php-mbstring

# CentOS/RHEL
sudo yum install php-curl php-json php-mbstring

# Restart web server
sudo systemctl restart apache2  # hoặc nginx
```

---

## 🎯 Sử dụng Tool

### **1. Chuẩn bị dữ liệu**

**Codes (file `codes.txt`):**
```
CYBORX-1234-5678-PREMIUM
CYBORX-ABCD-EFGH-CREDITS
CYBORX-9999-8888-PREMIUM
```

**Cookies (file `cookies.txt`):**
```
CYBORXSESSID=your_session_id_here
PHPSESSID=your_php_session_id
```

### **2. Lấy Cookies từ trình duyệt**

1. Đăng nhập vào https://cyborx.net
2. Mở DevTools (F12)
3. Vào tab **Application** > **Cookies**
4. Copy giá trị `CYBORXSESSID` và các cookies khác
5. Paste vào textarea hoặc file `cookies.txt`

### **3. Chạy Tool**

1. Truy cập web interface
2. Paste codes vào textarea "Codes"
3. Paste cookies vào textarea "Cookies"
4. Click **"Upload Data"**
5. Click **"Start Redeem"**
6. Theo dõi progress và results real-time

### **4. Xem Account Info**

1. Paste cookies vào textarea
2. Click **"Get Account Info"**
3. Xem thông tin: Username, Account Type, Credits, Expiry Date

---

## 🔧 Troubleshooting

### **Lỗi: "Call to undefined function curl_init()"**

```bash
# Cài đặt PHP cURL extension
sudo apt-get install php-curl
sudo systemctl restart apache2
```

### **Lỗi: "Permission denied"**

```bash
# Fix permissions
chmod -R 755 php-version/public/
chown -R www-data:www-data php-version/
```

### **Lỗi: "404 Not Found" hoặc URL rewriting không hoạt động**

**Apache:**
```bash
# Enable mod_rewrite
sudo a2enmod rewrite
sudo systemctl restart apache2

# Kiểm tra .htaccess có AllowOverride All
```

**Nginx:**
```bash
# Kiểm tra config có try_files đúng
location / {
    try_files $uri $uri/ /index.php?$query_string;
}
```

### **Lỗi: "Session not working"**

```bash
# Kiểm tra session directory permissions
sudo chmod 733 /var/lib/php/sessions

# Hoặc tạo custom session directory
mkdir -p php-version/storage/sessions
chmod 733 php-version/storage/sessions
```

### **Enable Debug Mode**

Sửa file `config/config.php`:

```php
define('APP_DEBUG', true);  // Bật debug mode
```

---

## 🔐 Bảo mật

### **Production Checklist:**

1. **Tắt debug mode:**
   ```php
   define('APP_DEBUG', false);
   ```

2. **Sử dụng HTTPS:**
   ```bash
   # Cài đặt Let's Encrypt SSL
   sudo certbot --apache -d cyborx.yourdomain.com
   # hoặc
   sudo certbot --nginx -d cyborx.yourdomain.com
   ```

3. **Giới hạn file upload:**
   - Đã được config trong `.htaccess`
   - Max file size: 1MB

4. **Bảo vệ sensitive files:**
   - File `.htaccess` đã deny access đến `composer.*`, `*.log`, `*.txt`

5. **Security headers:**
   - Đã được config trong `.htaccess`
   - X-Content-Type-Options, X-Frame-Options, X-XSS-Protection

---

## 📊 Monitoring

### **Health Check Endpoint:**

```bash
curl http://your-domain.com/health
```

**Response:**
```json
{
  "status": "healthy",
  "app": "running",
  "php_version": "8.1.0",
  "extensions": {
    "curl": true,
    "json": true,
    "session": true,
    "mbstring": true
  }
}
```

### **Ping Endpoint:**

```bash
curl http://your-domain.com/ping
# Response: pong
```

---

## 🆘 Hỗ trợ

### **Báo lỗi:**
- GitHub Issues: https://github.com/huybopbi/autoredeem/issues

### **Tài liệu:**
- README.md trong folder `php-version/`
- Inline comments trong source code

### **Community:**
- GitHub Discussions

---

## 📝 Cấu trúc thư mục

```
php-version/
├── public/              # Web root (document root)
│   ├── index.php       # Entry point
│   └── .htaccess       # URL rewriting
├── src/                # Source code
│   ├── CyborXRedeemTool.php
│   └── helpers.php
├── config/             # Configuration
│   └── config.php
├── templates/          # HTML templates
│   └── index.html
├── assets/             # Static assets (empty)
├── composer.json       # Dependencies
├── .htaccess          # Root Apache config
├── README.md          # Full documentation
├── codes.example.txt  # Example codes
└── cookies.example.txt # Example cookies
```

---

## ✅ Checklist sau khi cài đặt

- [ ] PHP 7.4+ đã cài đặt
- [ ] PHP extensions (curl, json, session, mbstring) đã enable
- [ ] Web server (Apache/Nginx) đã cấu hình
- [ ] Permissions đã set đúng (755 cho public/, 644 cho templates/)
- [ ] Truy cập được web interface
- [ ] Test upload codes và cookies
- [ ] Test start redeem (với test codes)
- [ ] Test account info
- [ ] Health check endpoint hoạt động
- [ ] (Production) HTTPS đã enable
- [ ] (Production) Debug mode đã tắt

---

## 🎉 Hoàn tất!

Bạn đã cài đặt thành công **CyborX Redeem Tool - PHP Version**!

**Các bước tiếp theo:**
1. Chuẩn bị codes và cookies
2. Test với một vài codes
3. Sử dụng tool để redeem codes
4. Enjoy! 🚀

---

**Made with ❤️ by [huybopbi](https://github.com/huybopbi)**

**Version:** 1.0.0 | **Language:** PHP 7.4+ | **License:** MIT
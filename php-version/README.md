# CyborX Auto Redeem Tool - PHP Version

🚀 **PHP Implementation** of the automatic code redemption tool for cyborx.net

## 🌟 Features

### Core Features
- ✅ **Web Interface** - Beautiful, responsive web UI with glass morphism design
- ✅ **Auto Redeem** - Automatic code redemption from text input or file upload
- ✅ **Real-time Progress** - Live progress tracking and statistics via AJAX
- ✅ **Session Management** - PHP native session with user isolation
- ✅ **Stop on Success** - Automatically stops after first successful redeem

### Advanced Features
- 🔐 **Security** - CSRF protection, input validation, cookie masking
- 📱 **Responsive Design** - Works perfectly on desktop and mobile
- 🎯 **JSON Response Parsing** - Smart API response detection
- 📊 **Statistics** - Detailed success/error tracking
- 🛡️ **Error Handling** - Comprehensive error handling and logging

## 🚀 Quick Start

### 1. Requirements
- PHP 7.4 or higher
- cURL extension
- JSON extension
- Session extension
- mbstring extension
- Web server (Apache/Nginx)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/huybopbi/autoredeem.git
cd autoredeem/php-version

# Install dependencies (optional)
composer install

# Set permissions
chmod -R 755 public/
chmod -R 644 templates/
```

### 3. Web Server Configuration

#### Apache
```apache
DocumentRoot /path/to/autoredeem/php-version/public
AllowOverride All
```

#### Nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/autoredeem/php-version/public;
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
}
```

### 4. Built-in PHP Server (Development)
```bash
cd php-version
composer serve
# or
php -S localhost:8000 -t public
```

### 5. Access Web Interface
Open your browser and go to: `http://localhost:8000` or your domain

## 📖 Usage Guide

### Basic Usage
1. **Enter Codes**: Paste codes in textarea or upload .txt file
2. **Enter Cookies**: Paste cyborx.net cookies or upload cookie file
3. **Upload Data**: Click "Upload Data" to save to session
4. **Start Redeem**: Click "Start Redeem" to begin processing
5. **Monitor Progress**: Watch real-time progress and results
6. **Auto Stop**: Tool stops automatically after first success

### Code Format
```
CYBORX-1234-5678-PREMIUM
CYBORX-ABCD-EFGH-CREDITS
CYBORX-9999-8888-PREMIUM
```

### Cookie Format
```
CYBORXSESSID=your_session_id_here
PHPSESSID=your_php_session_id
```

## 🔧 Configuration

### Environment Variables
```bash
# Application settings
APP_ENV=production
APP_DEBUG=false
BASE_URL=https://your-domain.com

# Security
SECRET_KEY=your-secret-key-here
```

### File Structure
```
php-version/
├── public/
│   ├── index.php          # Main entry point
│   └── .htaccess          # URL rewriting
├── src/
│   ├── CyborXRedeemTool.php # Core redeem logic
│   └── helpers.php        # Helper functions
├── config/
│   └── config.php         # Configuration
├── templates/
│   └── index.html         # Web interface template
├── composer.json          # Dependencies
├── .htaccess             # Apache configuration
└── README.md             # This file
```

## 🛠️ API Endpoints

### Core Endpoints
- `GET /` - Main web interface
- `POST /upload` - Upload codes/cookies data
- `POST /start` - Start redeem process
- `GET /status` - Get current status
- `GET /results` - Get redeem results
- `POST /stop` - Stop redeem process
- `POST /clear` - Clear results
- `POST /cleanup` - Cleanup session

### Utility Endpoints
- `GET /codes` - Get current codes info
- `GET /cookies` - Get current cookies info (masked)
- `POST /account-info` - Get account information
- `GET /health` - Health check endpoint
- `GET /ping` - Simple ping endpoint

## 🔐 Security Features

- **CSRF Protection** - Token-based CSRF protection
- **Session Isolation** - Each user has separate session
- **Input Validation** - All inputs are validated and sanitized
- **Cookie Masking** - Sensitive data is masked in UI
- **File Upload Security** - File type and size validation
- **XSS Protection** - HTML escaping and CSP headers
- **Error Handling** - Secure error messages

## 📱 Multi-User Support

### Session Management
- Each user gets unique session ID
- Complete isolation between users
- Session auto-expires based on configuration
- Memory-efficient session storage

### Data Storage
```
PHP Session Storage:
├── user_data[user_id_1]
│   ├── codes: ["CYBORX-1234-5678-PREMIUM", ...]
│   ├── cookies: {"CYBORXSESSID": "value", ...}
│   ├── task_results: [...]
│   └── task_status: {...}
└── global_task_data[user_id_1]
    ├── task_results: [...]
    └── task_status: {...}
```

## 🎯 API Response Handling

### Success Detection
The tool automatically detects successful redeems by:
1. **JSON Response**: Parses API response and checks `"ok": true`
2. **Text Detection**: Fallback to keyword detection ("success", "redeemed")
3. **Auto Stop**: Stops processing after first successful redeem

### Response Examples
```json
// Success Response
{
  "ok": true,
  "data": {
    "code": "CYBORX-6MBVYY9V-H9UGU43G-PREMIUM",
    "credits_added": 100,
    "new_status": "premium",
    "new_expiry": "2025-10-16 00:00:00"
  }
}

// Error Response
{
  "ok": false,
  "error": "Code already used"
}
```

## 🚀 Deployment

### Shared Hosting
1. Upload files to web root
2. Ensure PHP 7.4+ is available
3. Set document root to `public/` directory
4. Configure .htaccess if needed

### VPS/Dedicated Server
```bash
# Using Apache
sudo a2enmod rewrite
sudo systemctl restart apache2

# Using Nginx + PHP-FPM
sudo systemctl start nginx php8.1-fpm
```

### Docker Deployment
```dockerfile
FROM php:8.1-apache

# Enable mod_rewrite
RUN a2enmod rewrite

# Install extensions
RUN docker-php-ext-install curl

# Copy files
COPY php-version/ /var/www/html/

# Set permissions
RUN chown -R www-data:www-data /var/www/html
```

### Environment Configuration
```bash
# Production settings
APP_ENV=production
APP_DEBUG=false

# Security
SECRET_KEY=$(openssl rand -hex 32)

# Performance
PHP_MEMORY_LIMIT=128M
PHP_MAX_EXECUTION_TIME=300
```

## 📊 Monitoring

### Health Check
```bash
curl http://your-domain.com/health
```

### Response
```json
{
  "status": "healthy",
  "app": "running",
  "timestamp": "2024-01-01 12:00:00",
  "php_version": "8.1.0",
  "extensions": {
    "curl": true,
    "json": true,
    "session": true,
    "mbstring": true
  }
}
```

## 🔧 Troubleshooting

### Common Issues

1. **"Call to undefined function curl_init()"**
   ```bash
   # Install cURL extension
   sudo apt-get install php-curl
   sudo systemctl restart apache2
   ```

2. **"Permission denied" errors**
   ```bash
   chmod -R 755 php-version/public/
   chown -R www-data:www-data php-version/
   ```

3. **URL Rewriting not working**
   ```bash
   # Enable mod_rewrite
   sudo a2enmod rewrite
   sudo systemctl restart apache2
   ```

4. **Session not working**
   ```bash
   # Check session directory permissions
   sudo chmod 733 /var/lib/php/sessions
   ```

### Debug Mode
```php
// In config/config.php
define('APP_DEBUG', true);
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational purposes only. Use at your own risk. Make sure you comply with cyborx.net's terms of service.

## 🆘 Support

If you encounter any issues:
1. Check the [Issues](https://github.com/huybopbi/autoredeem/issues) page
2. Create a new issue with detailed description
3. Include error logs and steps to reproduce

## 🎉 Acknowledgments

- Original Python version for inspiration
- Bootstrap for UI framework
- Font Awesome for icons
- PHP community for excellent documentation

## 🔄 Differences from Python Version

### Advantages
- **No external dependencies** - Runs on any PHP hosting
- **Better hosting compatibility** - Works on shared hosting
- **Lower resource usage** - More memory efficient
- **Faster startup** - No framework overhead
- **Easier deployment** - Just upload files

### Limitations
- **No multi-threading** - Single-threaded processing only
- **Synchronous processing** - Processes codes one by one
- **Basic background tasks** - No advanced job queue
- **Session-based storage** - No persistent database

---

**Made with ❤️ by [huybopbi](https://github.com/huybopbi)**
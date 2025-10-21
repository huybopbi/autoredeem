╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║         🚀 CyborX Auto Redeem Tool - PHP Version 🚀                 ║
║                                                                      ║
║                    File: cyborx-redeem-php-version.zip               ║
║                    Size: ~28KB                                       ║
║                    Version: 1.0.0                                    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

📦 NỘI DUNG PACKAGE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ php-version/                  - Thư mục chính chứa toàn bộ source code
   ├── public/                   - Web root (document root)
   │   ├── index.php            - Entry point chính (11KB)
   │   └── .htaccess            - URL rewriting config
   ├── src/                     - Source code
   │   ├── CyborXRedeemTool.php - Core class (18KB, 500+ lines)
   │   └── helpers.php          - Helper functions (5KB)
   ├── config/                  - Configuration files
   │   └── config.php           - Main config
   ├── templates/               - HTML templates
   │   └── index.html           - Web UI (33KB, 800+ lines)
   ├── composer.json            - PHP dependencies
   ├── .htaccess               - Apache configuration
   ├── README.md               - Full documentation (9KB)
   ├── codes.example.txt       - Example codes file
   └── cookies.example.txt     - Example cookies file

✅ INSTALLATION_GUIDE.md         - Hướng dẫn cài đặt chi tiết (10KB)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ CÁCH SỬ DỤNG NHANH (5 PHÚT):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣  Giải nén file ZIP:
    unzip cyborx-redeem-php-version.zip
    cd php-version

2️⃣  Chạy với PHP built-in server:
    php -S localhost:8000 -t public

3️⃣  Mở trình duyệt:
    http://localhost:8000

4️⃣  Sử dụng tool:
    - Paste codes vào textarea
    - Paste cookies vào textarea
    - Click "Upload Data"
    - Click "Start Redeem"
    - Xem kết quả real-time!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 YÊU CẦU HỆ THỐNG:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ PHP 7.4 hoặc cao hơn (khuyến nghị PHP 8.1+)
✅ PHP Extensions:
   - curl (bắt buộc)
   - json (bắt buộc)
   - session (bắt buộc)
   - mbstring (bắt buộc)
✅ Web Server: Apache hoặc Nginx (hoặc PHP built-in server)
✅ RAM: 128MB tối thiểu (khuyến nghị 256MB+)
✅ Disk: 10MB

Kiểm tra PHP extensions:
    php -m | grep -E 'curl|json|session|mbstring'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 TRIỂN KHAI LÊN SERVER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 Shared Hosting (cPanel, DirectAdmin):
   1. Upload folder php-version lên server
   2. Set Document Root về php-version/public/
   3. Chmod 755 cho public/, 644 cho templates/
   4. Truy cập domain của bạn

📌 VPS với Apache:
   1. Upload files: scp -r php-version/ user@server:/var/www/
   2. Tạo Virtual Host (xem INSTALLATION_GUIDE.md)
   3. Enable mod_rewrite: sudo a2enmod rewrite
   4. Restart Apache: sudo systemctl restart apache2

📌 VPS với Nginx:
   1. Upload files: scp -r php-version/ user@server:/var/www/
   2. Tạo Nginx config (xem INSTALLATION_GUIDE.md)
   3. Restart Nginx: sudo systemctl restart nginx

📌 Docker:
   docker run -d -p 8000:80 -v ./php-version:/var/www/html php:8.1-apache

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 TÍNH NĂNG CHÍNH:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Web Interface đẹp với glass morphism design
✅ Auto redeem codes từ text hoặc file upload
✅ Real-time progress tracking và statistics
✅ Session management với user isolation
✅ Stop on success - tự động dừng khi thành công
✅ Account info fetching - xem thông tin tài khoản
✅ CSRF protection và security features
✅ Responsive design - hoạt động trên mobile
✅ JSON response parsing thông minh
✅ Multi-user support

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 TÀI LIỆU:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 INSTALLATION_GUIDE.md    - Hướng dẫn cài đặt đầy đủ
📖 php-version/README.md    - Documentation chi tiết
📖 Inline comments          - Comments trong source code

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔐 BẢO MẬT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CSRF token protection
✅ Input validation và sanitization
✅ Cookie masking trong UI
✅ XSS protection headers
✅ File upload security (max 1MB)
✅ Secure error handling
✅ Session isolation per user

Production checklist:
   - Tắt debug mode (APP_DEBUG = false)
   - Sử dụng HTTPS
   - Giới hạn file upload
   - Security headers đã được config

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛠️ API ENDPOINTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GET  /                - Main web interface
POST /upload          - Upload codes/cookies
POST /start           - Start redeem process
GET  /status          - Get current status
GET  /results         - Get redeem results
POST /stop            - Stop process
POST /clear           - Clear results
POST /cleanup         - Cleanup session
GET  /codes           - Get codes info
GET  /cookies         - Get cookies info (masked)
POST /account-info    - Get account information
GET  /health          - Health check
GET  /ping            - Ping endpoint

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 TROUBLESHOOTING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ "Call to undefined function curl_init()"
   → sudo apt-get install php-curl

❌ "Permission denied"
   → chmod -R 755 php-version/public/
   → chown -R www-data:www-data php-version/

❌ "404 Not Found" hoặc URL rewriting không hoạt động
   → sudo a2enmod rewrite (Apache)
   → Kiểm tra .htaccess có AllowOverride All

❌ "Session not working"
   → sudo chmod 733 /var/lib/php/sessions

Xem thêm trong INSTALLATION_GUIDE.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 THỐNG KÊ SOURCE CODE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 Total Files: 21
📝 Total Lines: ~2,500+ lines
💾 Total Size: ~93KB (uncompressed)
🗜️  ZIP Size: ~28KB (compressed)

Main Files:
   - CyborXRedeemTool.php: 500+ lines
   - index.html: 800+ lines
   - index.php: 400+ lines
   - helpers.php: 200+ lines
   - README.md: 400+ lines
   - INSTALLATION_GUIDE.md: 400+ lines

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🆘 HỖ TRỢ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🐛 Báo lỗi:
   GitHub Issues: https://github.com/huybopbi/autoredeem/issues

📖 Tài liệu:
   - INSTALLATION_GUIDE.md (trong ZIP)
   - php-version/README.md (trong ZIP)
   - Inline comments trong source code

💬 Community:
   GitHub Discussions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  DISCLAIMER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tool này chỉ dành cho mục đích giáo dục (educational purposes).
Sử dụng với trách nhiệm của riêng bạn.
Đảm bảo tuân thủ điều khoản sử dụng của cyborx.net.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 LICENSE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MIT License - Free to use, modify, and distribute

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 HOÀN TẤT!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Bạn đã sẵn sàng để sử dụng CyborX Auto Redeem Tool - PHP Version!

Các bước tiếp theo:
1. Giải nén file ZIP
2. Đọc INSTALLATION_GUIDE.md
3. Chạy tool với PHP built-in server hoặc deploy lên server
4. Chuẩn bị codes và cookies
5. Bắt đầu redeem!

Chúc bạn thành công! 🚀

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Made with ❤️ by huybopbi
GitHub: https://github.com/huybopbi
Version: 1.0.0 | Language: PHP 7.4+ | Date: October 2024

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
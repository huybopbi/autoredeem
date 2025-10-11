# CyborX Redeem Tool - Web App

Web application cho tool tự động redeem code trên cyborx.net với giao diện đẹp và dễ sử dụng.

## 🌟 Tính năng

- ✅ **Giao diện web đẹp mắt** với Bootstrap 5 và Font Awesome
- ✅ **Upload file codes và cookies** hoặc paste trực tiếp
- ✅ **Real-time progress tracking** với thanh tiến trình
- ✅ **Multi-threading support** với tùy chọn số worker
- ✅ **Live results display** với phân loại thành công/lỗi
- ✅ **Responsive design** hoạt động trên mọi thiết bị
- ✅ **Background processing** không block giao diện
- ✅ **Error handling** và thông báo chi tiết

## 🚀 Cài đặt và chạy

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Chạy web app
```bash
python app.py
```

### 3. Mở browser
Truy cập: `http://localhost:5000`

## 📱 Cách sử dụng

### Bước 1: Upload Codes
- **Upload file**: Chọn file `.txt` chứa danh sách code
- **Paste manual**: Paste trực tiếp codes vào textarea
- Format: Mỗi dòng một code

### Bước 2: Upload Cookies
- **Upload file**: Chọn file `.txt` chứa cookies
- **Paste manual**: Paste cookies từ browser
- Format: `CYBORXSESSID=your_session_id`

### Bước 3: Cấu hình
- **Mode**: Single Thread (ổn định) hoặc Multi Thread (nhanh)
- **Workers**: Số thread cho multi-threading (1-20)

### Bước 4: Chạy
- Nhấn **Start Redeem** để bắt đầu
- Theo dõi progress real-time
- Xem kết quả chi tiết

## 🎨 Giao diện

### Main Features:
- **Status Card**: Hiển thị trạng thái, progress, success/error count
- **Progress Bar**: Thanh tiến trình trực quan
- **Results Panel**: Danh sách kết quả với phân loại màu sắc
- **Control Panel**: Nút điều khiển start/stop/clear

### Design:
- **Gradient backgrounds** với màu sắc hiện đại
- **Card-based layout** dễ nhìn và tổ chức
- **Responsive design** tương thích mobile
- **Smooth animations** và transitions
- **Icon integration** với Font Awesome

## 🔧 API Endpoints

- `GET /` - Trang chủ
- `POST /upload` - Upload files (codes/cookies)
- `POST /start` - Bắt đầu redeem process
- `POST /stop` - Dừng process
- `POST /clear` - Xóa results
- `GET /status` - Lấy trạng thái hiện tại
- `GET /results` - Lấy kết quả

## 📁 Cấu trúc file

```
├── app.py                 # Flask web app chính
├── redeem_tool.py         # Core redeem logic
├── templates/
│   └── index.html         # HTML template
├── static/                # CSS/JS files (nếu có)
├── requirements.txt       # Python dependencies
├── codes.txt             # File codes mẫu
├── cookies.txt           # File cookies
└── README_webapp.md      # Hướng dẫn này
```

## ⚙️ Cấu hình

### Environment Variables:
- `FLASK_ENV=development` - Chế độ development
- `FLASK_DEBUG=True` - Bật debug mode

### Port và Host:
- Mặc định: `http://localhost:5000`
- Có thể thay đổi trong `app.py`

## 🛡️ Bảo mật

- **Session management** an toàn
- **File upload validation**
- **Error handling** không expose thông tin nhạy cảm
- **CSRF protection** với Flask

## 🐛 Troubleshooting

### Lỗi thường gặp:

1. **Port 5000 đã được sử dụng**
   ```bash
   # Thay đổi port trong app.py
   app.run(port=5001)
   ```

2. **Module không tìm thấy**
   ```bash
   pip install -r requirements.txt
   ```

3. **Cookies không hợp lệ**
   - Kiểm tra format cookies
   - Đảm bảo đã đăng nhập cyborx.net

4. **Codes file trống**
   - Kiểm tra file codes.txt
   - Đảm bảo format đúng

## 🔄 Updates

- **v1.0**: Web app cơ bản với upload và redeem
- **v1.1**: Thêm multi-threading và progress tracking
- **v1.2**: Cải thiện UI/UX và responsive design

## 📞 Support

Nếu gặp vấn đề, hãy kiểm tra:
1. Console logs trong browser (F12)
2. Terminal output của Flask app
3. File logs nếu có

---

**🎉 Enjoy using CyborX Redeem Tool Web App!**

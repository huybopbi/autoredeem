# Telegram API Setup Guide

Hướng dẫn lấy Telegram API ID và Hash để sử dụng với CyborX Redeem Tool.

## 🔑 Lấy Telegram API Credentials

### Bước 1: Truy cập Telegram API
1. Mở browser và truy cập: https://my.telegram.org/apps
2. Đăng nhập bằng số điện thoại Telegram của bạn
3. Nhập mã xác thực được gửi qua SMS

### Bước 2: Tạo ứng dụng mới
1. Nhấn **"Create new application"**
2. Điền thông tin:
   - **App title**: `CyborX Redeem Monitor`
   - **Short name**: `cyborx_monitor`
   - **Platform**: `Desktop`
   - **Description**: `Auto redeem codes from Telegram channels`

### Bước 3: Lấy API Credentials
Sau khi tạo xong, bạn sẽ thấy:
- **api_id**: Số ID (ví dụ: 12345678)
- **api_hash**: Chuỗi hash (ví dụ: abc123def456...)

## 📱 Cấu hình Bot

### Bước 1: Thêm kênh cần theo dõi
1. Mở web app: `http://localhost:5000`
2. Vào phần **Telegram Monitor**
3. Nhập **API ID** và **API Hash**
4. Nhấn **"Add Channel"** để thêm kênh cần theo dõi

### Bước 2: Cấu hình kênh
- **Username**: Tên kênh (không cần @)
- **Display Name**: Tên hiển thị (tùy chọn)

Ví dụ:
- Username: `cyborx_official`
- Display Name: `CyborX Official Channel`

### Bước 3: Khởi động monitor
1. Nhấn **"Start Monitor"**
2. Bot sẽ bắt đầu theo dõi các kênh đã cấu hình
3. Khi có code mới, bot sẽ tự động redeem

## 🎯 Tính năng

### Pattern Matching
Bot tự động nhận diện các format code:
- `CYBORX-1234-5678-PREMIUM`
- `cyborx-abcd-efgh-credits`
- `CYBORX 1234 5678 PREMIUM`
- `cyborx abcd efgh credits`

### Auto Redeem
- Tự động redeem code khi phát hiện
- Tránh redeem trùng lặp
- Delay 2 giây giữa các redeem
- Logging chi tiết

### Real-time Monitoring
- Theo dõi real-time
- Thống kê số code tìm thấy/redeemed
- Hiển thị trạng thái trên web interface

## ⚙️ Cấu hình nâng cao

### File cấu hình: `monitor_config.json`
```json
{
  "channels": [
    {
      "username": "cyborx_official",
      "name": "CyborX Official",
      "enabled": true
    }
  ],
  "settings": {
    "auto_redeem": true,
    "delay_between_redeems": 2,
    "max_redeems_per_hour": 10,
    "notify_on_success": true,
    "notify_on_error": true
  }
}
```

### Tùy chỉnh pattern matching
Chỉnh sửa trong `telegram_monitor.py`:
```python
self.code_patterns = [
    r'CYBORX-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z]+',
    r'cyborx-[a-z0-9]{4}-[a-z0-9]{4}-[a-z]+',
    # Thêm pattern mới ở đây
]
```

## 🛡️ Bảo mật

### Lưu ý quan trọng:
- **Không chia sẻ** API ID và Hash
- **Không commit** credentials vào Git
- **Sử dụng environment variables** cho production
- **Thường xuyên kiểm tra** logs để phát hiện bất thường

### Environment Variables (Khuyến nghị):
```bash
export TELEGRAM_API_ID="your_api_id"
export TELEGRAM_API_HASH="your_api_hash"
```

## 🐛 Troubleshooting

### Lỗi thường gặp:

1. **"Invalid API ID/Hash"**
   - Kiểm tra lại API credentials
   - Đảm bảo đã tạo app trên my.telegram.org

2. **"Channel not found"**
   - Kiểm tra username kênh
   - Đảm bảo bot có quyền truy cập kênh

3. **"Session expired"**
   - Xóa file session và đăng nhập lại
   - File: `cyborx_monitor.session`

4. **"Rate limit exceeded"**
   - Tăng delay giữa các redeem
   - Giảm số kênh theo dõi

## 📊 Monitoring

### Logs
- File log: `telegram_monitor.log`
- Real-time status trên web interface
- Thống kê chi tiết

### Metrics
- Messages processed
- Codes found
- Codes redeemed
- Error count
- Uptime

## 🔄 Updates

Bot sẽ tự động:
- Reload cấu hình khi thay đổi
- Retry khi gặp lỗi
- Log tất cả hoạt động
- Cập nhật thống kê real-time

---

**🎉 Chúc bạn sử dụng thành công CyborX Telegram Monitor!**

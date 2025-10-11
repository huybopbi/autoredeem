# CyborX Auto Redeem Tool

🚀 **Multi-User Web Application** for automatic code redemption on cyborx.net with Telegram monitoring support.

## 🌟 Features

### Core Features
- ✅ **Multi-User Support** - Each user has isolated session and files
- ✅ **Web Interface** - Beautiful, responsive web UI
- ✅ **Auto Redeem** - Automatic code redemption from uploaded files
- ✅ **Telegram Monitor** - Monitor Telegram channels for new codes
- ✅ **Real-time Progress** - Live progress tracking and statistics
- ✅ **Session Management** - Secure user session isolation

### Advanced Features
- 🔄 **Multi-threading** - Fast processing with configurable workers
- 📊 **Statistics** - Detailed success/error tracking
- 🛡️ **Security** - Cookie masking and session isolation
- 📱 **Responsive Design** - Works on desktop and mobile
- 🎯 **Pattern Matching** - Smart code detection from messages

## 🚀 Quick Start

### 1. Installation
```bash
git clone https://github.com/huybopbi/autoredeem.git
cd autoredeem
pip install -r requirements.txt
```

### 2. Run Web App
```bash
python app.py
```

### 3. Access Web Interface
Open your browser and go to: `http://localhost:5000`

## 📖 Usage Guide

### Basic Usage
1. **Upload Codes**: Upload your codes file or paste manually
2. **Upload Cookies**: Upload cookies from cyborx.net
3. **Start Redeem**: Choose single or multi-thread mode
4. **Monitor Progress**: Watch real-time progress and results

### Telegram Monitoring
1. **Get API Credentials**: From https://my.telegram.org/apps
2. **Add Channels**: Add Telegram channels to monitor
3. **Start Monitor**: Bot will auto-redeem codes from channels
4. **View Results**: Check statistics and redeemed codes

## 🔧 Configuration

### Environment Variables
```bash
export FLASK_ENV=production
export FLASK_DEBUG=False
```

### File Structure
```
autoredeem/
├── app.py                    # Main Flask application
├── redeem_tool.py           # Core redeem logic
├── telegram_monitor.py      # Telegram monitoring
├── templates/
│   └── index.html          # Web interface
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── .gitignore            # Git ignore rules
```

## 🛠️ API Endpoints

### Core Endpoints
- `GET /` - Main web interface
- `POST /upload` - Upload codes/cookies files
- `POST /start` - Start redeem process
- `GET /status` - Get current status
- `GET /results` - Get redeem results
- `POST /stop` - Stop redeem process
- `POST /clear` - Clear results

### Telegram Endpoints
- `POST /telegram/start` - Start Telegram monitor
- `POST /telegram/stop` - Stop Telegram monitor
- `GET /telegram/status` - Get monitor status
- `GET /telegram/channels` - Get monitored channels
- `POST /telegram/channels` - Add new channel
- `DELETE /telegram/channels/<username>` - Remove channel

## 🔐 Security Features

- **Session Isolation** - Each user has separate session
- **Memory Storage** - Data stored in memory only, no files on disk
- **Cookie Masking** - Sensitive data is masked in UI
- **Input Validation** - All inputs are validated
- **Error Handling** - Comprehensive error handling
- **Auto Cleanup** - Session data automatically cleared

## 📱 Multi-User Support

### Session Management
- Each user gets unique session ID
- Data stored in memory only (no files on disk)
- Complete isolation between users
- Session cleanup functionality
- Auto-cleanup when session ends

### Data Storage
```
Memory Storage (No Files):
├── User Session 1
│   ├── codes: ["CYBORX-1234-5678-PREMIUM", ...]
│   ├── cookies: {"CYBORXSESSID": "value", ...}
│   └── task_results: [...]
└── User Session 2
    ├── codes: ["CYBORX-ABCD-EFGH-CREDITS", ...]
    ├── cookies: {"CYBORXSESSID": "value", ...}
    └── task_results: [...]
```

## 🎯 Telegram Integration

### Setup
1. Get API ID and Hash from https://my.telegram.org/apps
2. Add channels to monitor
3. Start monitoring
4. Bot automatically redeems codes

### Supported Code Formats
- `CYBORX-1234-5678-PREMIUM`
- `cyborx-abcd-efgh-credits`
- `CYBORX 1234 5678 PREMIUM`
- `cyborx abcd efgh credits`

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using Docker
docker build -t autoredeem .
docker run -p 5000:5000 autoredeem
```

## 📊 Monitoring

### Statistics
- Total codes processed
- Success/failure rates
- Processing time
- Real-time progress

### Logs
- Detailed operation logs
- Error tracking
- Performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational purposes only. Use at your own risk. Make sure you comply with cyborx.net's terms of service.

## 🆘 Support

If you encounter any issues:
1. Check the [Issues](https://github.com/huybopbi/autoredeem/issues) page
2. Create a new issue with detailed description
3. Include error logs and steps to reproduce

## 🎉 Acknowledgments

- Flask framework for web interface
- Telethon for Telegram integration
- Bootstrap for UI components
- All contributors and users

---

**Made with ❤️ by [huybopbi](https://github.com/huybopbi)**

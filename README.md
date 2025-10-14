# CyborX Auto Redeem Tool

🚀 **Simple Web Application** for automatic code redemption on cyborx.net

## 🌟 Features

### Core Features
- ✅ **Web Interface** - Beautiful, responsive web UI
- ✅ **Auto Redeem** - Automatic code redemption from text input
- ✅ **Real-time Progress** - Live progress tracking and statistics
- ✅ **Session Management** - Simple in-memory session storage
- ✅ **Stop on Success** - Automatically stops after first successful redeem

### Advanced Features
- 🔄 **Multi-threading** - Fast processing with configurable workers
- 📊 **Statistics** - Detailed success/error tracking
- 🛡️ **Security** - Cookie masking and session isolation
- 📱 **Responsive Design** - Works on desktop and mobile
- 🎯 **JSON Response Parsing** - Smart API response detection

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
1. **Enter Codes**: Paste your codes in the textarea (one per line)
2. **Enter Cookies**: Paste your cyborx.net cookies in the textarea
3. **Choose Mode**: Select single thread (stable) or multi-thread (fast)
4. **Start Redeem**: Click "Start Redeem" button
5. **Monitor Progress**: Watch real-time progress and results
6. **Auto Stop**: Tool automatically stops after first successful redeem

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

### Setup Files
1. Copy `codes.example.txt` to `codes.txt` and add your codes
2. Copy `cookies.example.txt` to `cookies.txt` and add your cookies
3. Or paste directly into the web interface textareas

## 🔧 Configuration

### File Structure
```
autoredeem/
├── app.py                    # Main Flask application
├── redeem_tool.py           # Core redeem logic
├── wsgi.py                  # WSGI entry point
├── templates/
│   └── index.html          # Web interface
├── requirements.txt        # Python dependencies
├── codes.example.txt       # Example codes file
├── cookies.example.txt     # Example cookies file
├── Procfile                # Railway deployment
├── runtime.txt             # Python version
├── cyborx-redeem.service   # Systemd service
├── deploy.sh               # VPS deployment script
├── VPS_DEPLOYMENT.md       # VPS deployment guide
├── RAILWAY_DEPLOYMENT.md   # Railway deployment guide
├── .gitignore             # Git ignore rules
├── README.md              # This file
└── LICENSE                # License file
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

### File Endpoints
- `GET /codes` - Get current codes info
- `GET /cookies` - Get current cookies info

## 🔐 Security Features

- **Session Isolation** - Each user has separate session
- **Memory Storage** - Data stored in memory only, no persistent files
- **Cookie Masking** - Sensitive data is masked in UI
- **Input Validation** - All inputs are validated
- **Error Handling** - Comprehensive error handling
- **Auto Cleanup** - Session data automatically cleared

## 📱 Multi-User Support

### Session Management
- Each user gets unique session ID
- Data stored in memory (simple and fast)
- Complete isolation between users
- Session auto-expires when browser closes
- Filesystem-based session management

### Data Storage
```
Memory Storage:
├── global_task_data[user_id_1]
│   ├── codes: ["CYBORX-1234-5678-PREMIUM", ...]
│   ├── cookies: {"CYBORXSESSID": "value", ...}
│   ├── task_results: [...]
│   └── task_status: {...}
└── global_task_data[user_id_2]
    ├── codes: ["CYBORX-ABCD-EFGH-CREDITS", ...]
    ├── cookies: {"CYBORXSESSID": "value", ...}
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

### Local Development
```bash
python app.py
```

### Railway Deployment (Free Hosting)
```bash
# Method 1: Deploy from GitHub
# 1. Fork this repository
# 2. Go to https://railway.app
# 3. Connect your GitHub repo
# 4. Deploy automatically!

# Method 2: Using Railway CLI
npm install -g @railway/cli
railway login
railway up
```

### VPS Deployment
```bash
# Using deployment script
chmod +x deploy.sh
sudo ./deploy.sh

# Using Gunicorn manually
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

### Docker Deployment
```bash
# Build and run
docker build -t cyborx-redeem .
docker run -p 5000:5000 cyborx-redeem
```

### Environment Variables
```bash
# Flask settings
export FLASK_ENV=production
export FLASK_DEBUG=False
export SECRET_KEY=your-secret-key-here
```

## 📊 Monitoring

### Statistics
- Total codes processed
- Success/failure rates
- Processing time
- Real-time progress
- Current code being processed

### Logs
- Detailed operation logs
- Error tracking
- Performance metrics
- ASCII-safe logging (no emoji issues)

## 🔧 Troubleshooting

### Common Issues

1. **Unicode Error on Windows**
   - Fixed: All emoji characters replaced with ASCII markers
   - Use `[OK]`, `[ERROR]`, `[SUCCESS]` instead of emoji

2. **Session Not Updating**
   - Fixed: Using global_task_data for thread communication
   - Web interface updates in real-time

3. **Tool Doesn't Stop After Success**
   - Fixed: Automatic stop after first successful redeem
   - JSON response parsing for accurate detection

### Debug Mode
```bash
# Enable debug logging
export FLASK_DEBUG=True
python app.py
```

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
- Bootstrap for UI components
- All contributors and users

---

**Made with ❤️ by [huybopbi](https://github.com/huybopbi)**
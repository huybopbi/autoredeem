#!/usr/bin/env python3
"""
CyborX Redeem Tool - Web App
Flask web application for automatic code redemption
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_session import Session
import os
import threading
import time
import json
import asyncio
import uuid
import shutil
import redis
from datetime import datetime, timedelta
from redeem_tool import CyborXRedeemTool
from telegram_monitor import TelegramMonitor

app = Flask(__name__)
app.secret_key = 'cyborx_redeem_tool_2024_secure_key_for_multi_user'

# Redis configuration
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    decode_responses=True
)

# Flask-Session configuration
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis_client
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'cyborx:'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

Session(app)

def get_user_session():
    """Get or create user session from Redis"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session.permanent = True
    
    user_id = session['user_id']
    session_key = f"user_session:{user_id}"
    
    # Check if session exists in Redis
    if not redis_client.exists(session_key):
        # Create new session
        default_session = {
            'task_results': [],
            'task_status': {
                'running': False,
                'progress': 0,
                'total': 0,
                'success': 0,
                'error': 0,
                'current_code': '',
                'start_time': None,
                'end_time': None
            },
            'telegram_monitor': None,
            'monitor_status': {
                'running': False,
                'channels': [],
                'stats': {},
                'start_time': None
            },
            'data': {
                'codes': [],
                'cookies': {},
                'codes_text': '',
                'cookies_text': ''
            },
            'created_at': datetime.now().isoformat(),
            'last_accessed': datetime.now().isoformat()
        }
        
        # Store in Redis with 24 hour expiration
        redis_client.setex(session_key, 86400, json.dumps(default_session))
    
    # Update last accessed time
    session_data = json.loads(redis_client.get(session_key))
    session_data['last_accessed'] = datetime.now().isoformat()
    redis_client.setex(session_key, 86400, json.dumps(session_data))
    
    return session_data

def save_user_session(user_id, session_data):
    """Save user session to Redis"""
    session_key = f"user_session:{user_id}"
    session_data['last_accessed'] = datetime.now().isoformat()
    redis_client.setex(session_key, 86400, json.dumps(session_data))

def parse_codes_from_text(text):
    """Parse codes from text input"""
    if not text:
        return []
    
    codes = []
    for line in text.strip().split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            codes.append(line)
    
    return codes

def parse_cookies_from_text(text):
    """Parse cookies from text input"""
    if not text:
        return {}
    
    cookies = {}
    for line in text.strip().split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            parts = line.split(';')
            for part in parts:
                part = part.strip()
                if '=' in part:
                    name, value = part.split('=', 1)
                    cookies[name.strip()] = value.strip()
    
    return cookies

class WebRedeemTool(CyborXRedeemTool):
    """Extended redeem tool for web interface"""
    
    def __init__(self, cookies=None, user_session=None):
        super().__init__(cookies)
        self.web_callback = None
        self.user_session = user_session
    
    def set_web_callback(self, callback):
        """Set callback function for web updates"""
        self.web_callback = callback
    
    def update_progress(self):
        """Override to include web updates"""
        super().update_progress()
        if self.web_callback:
            self.web_callback({
                'progress': self.processed_count,
                'total': self.total_codes,
                'success': self.success_count,
                'error': self.error_count
            })
    
    def redeem_code(self, code, code_number):
        """Override to include web updates"""
        if self.user_session:
            # Update current code being processed
            self.user_session['task_status']['current_code'] = code
        
        result = super().redeem_code(code, code_number)
        
        # Add to results
        if self.user_session:
            if result:
                self.user_session['task_results'].append({
                    'code': code,
                    'status': 'success' if result['status_code'] == 200 else 'error',
                    'response': result['response'],
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
            else:
                self.user_session['task_results'].append({
                    'code': code,
                    'status': 'error',
                    'response': 'Request failed',
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
        
        return result
    
    def load_codes_from_session(self, user_session):
        """Load codes from user session"""
        return user_session['data']['codes']
    
    def load_cookies_from_session(self, user_session):
        """Load cookies from user session"""
        return user_session['data']['cookies']

def run_redeem_task(codes, cookies, mode='single', max_workers=5, user_id=None):
    """Run redeem task in background thread"""
    try:
        # Get session from Redis
        session_key = f"user_session:{user_id}"
        user_session = json.loads(redis_client.get(session_key))
        
        user_session['task_status']['running'] = True
        user_session['task_status']['start_time'] = datetime.now().strftime('%H:%M:%S')
        user_session['task_status']['progress'] = 0
        user_session['task_status']['success'] = 0
        user_session['task_status']['error'] = 0
        user_session['task_results'].clear()
        
        # Save initial state
        save_user_session(user_id, user_session)
        
        # Create tool instance
        tool = WebRedeemTool(cookies, user_session)
        
        # Set callback for progress updates
        def progress_callback(data):
            # Get fresh session data
            current_session = json.loads(redis_client.get(session_key))
            current_session['task_status'].update(data)
            save_user_session(user_id, current_session)
        
        tool.set_web_callback(progress_callback)
        
        # Run based on mode
        if mode == 'single':
            tool.run_single_thread(codes)
        else:
            tool.run_multi_thread(codes, max_workers)
        
        # Update final state
        final_session = json.loads(redis_client.get(session_key))
        final_session['task_status']['end_time'] = datetime.now().strftime('%H:%M:%S')
        save_user_session(user_id, final_session)
        
    except Exception as e:
        print(f"Error in redeem task: {str(e)}")
        # Update error state
        try:
            error_session = json.loads(redis_client.get(session_key))
            error_session['task_status']['running'] = False
            save_user_session(user_id, error_session)
        except:
            pass
    finally:
        # Ensure running is set to False
        try:
            final_session = json.loads(redis_client.get(session_key))
            final_session['task_status']['running'] = False
            save_user_session(user_id, final_session)
        except:
            pass

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    try:
        user_session = get_user_session()
        user_id = session['user_id']
        
        # Handle codes file
        if 'codes_file' in request.files:
            codes_file = request.files['codes_file']
            if codes_file.filename:
                codes_text = codes_file.read().decode('utf-8')
                codes = parse_codes_from_text(codes_text)
                user_session['data']['codes'] = codes
                user_session['data']['codes_text'] = codes_text
                save_user_session(user_id, user_session)
                flash(f'Codes file uploaded successfully! ({len(codes)} codes loaded)', 'success')
        
        # Handle cookies file
        if 'cookies_file' in request.files:
            cookies_file = request.files['cookies_file']
            if cookies_file.filename:
                cookies_text = cookies_file.read().decode('utf-8')
                cookies = parse_cookies_from_text(cookies_text)
                user_session['data']['cookies'] = cookies
                user_session['data']['cookies_text'] = cookies_text
                save_user_session(user_id, user_session)
                flash(f'Cookies file uploaded successfully! ({len(cookies)} cookies loaded)', 'success')
        
        # Handle manual codes input
        if 'codes_text' in request.form and request.form['codes_text']:
            codes_text = request.form['codes_text']
            codes = parse_codes_from_text(codes_text)
            user_session['data']['codes'] = codes
            user_session['data']['codes_text'] = codes_text
            save_user_session(user_id, user_session)
            flash(f'Codes saved successfully! ({len(codes)} codes loaded)', 'success')
        
        # Handle manual cookies input
        if 'cookies_text' in request.form and request.form['cookies_text']:
            cookies_text = request.form['cookies_text']
            cookies = parse_cookies_from_text(cookies_text)
            user_session['data']['cookies'] = cookies
            user_session['data']['cookies_text'] = cookies_text
            save_user_session(user_id, user_session)
            flash(f'Cookies saved successfully! ({len(cookies)} cookies loaded)', 'success')
        
    except Exception as e:
        flash(f'Error uploading files: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/start', methods=['POST'])
def start_redeem():
    """Start redeem process"""
    user_session = get_user_session()
    
    if user_session['task_status']['running']:
        return jsonify({'error': 'Task is already running'}), 400
    
    try:
        # Load codes from user session
        codes = user_session['data']['codes']
        if not codes:
            return jsonify({'error': 'No codes found. Please upload codes first.'}), 400
        
        # Load cookies from user session
        cookies = user_session['data']['cookies']
        if not cookies:
            return jsonify({'error': 'No cookies found. Please upload cookies first.'}), 400
        
        # Get parameters
        mode = request.json.get('mode', 'single')
        max_workers = int(request.json.get('max_workers', 5))
        
        # Start background task
        task_thread = threading.Thread(
            target=run_redeem_task,
            args=(codes, cookies, mode, max_workers, user_id)
        )
        task_thread.daemon = True
        task_thread.start()
        
        return jsonify({'message': 'Redeem process started successfully!'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status')
def get_status():
    """Get current task status"""
    user_session = get_user_session()
    return jsonify(user_session['task_status'])

@app.route('/results')
def get_results():
    """Get task results"""
    user_session = get_user_session()
    return jsonify(user_session['task_results'])

@app.route('/codes')
def get_codes():
    """Get current codes"""
    try:
        user_session = get_user_session()
        codes = user_session['data']['codes']
        
        return jsonify({
            'codes': codes,
            'count': len(codes),
            'filename': 'Session Data' if codes else 'No data'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cookies')
def get_cookies():
    """Get current cookies info"""
    try:
        user_session = get_user_session()
        cookies = user_session['data']['cookies']
        
        # Mask sensitive cookie values
        masked_cookies = {}
        for name, value in cookies.items():
            if len(value) > 10:
                masked_cookies[name] = value[:6] + '...' + value[-4:]
            else:
                masked_cookies[name] = '***'
        
        return jsonify({
            'cookies': masked_cookies,
            'count': len(cookies),
            'filename': 'Session Data' if cookies else 'No data'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stop', methods=['POST'])
def stop_redeem():
    """Stop redeem process"""
    user_session = get_user_session()
    
    if not user_session['task_status']['running']:
        return jsonify({'error': 'No task is running'}), 400
    
    # Note: We can't actually stop the thread, but we can mark it as stopped
    user_session['task_status']['running'] = False
    user_session['task_status']['end_time'] = datetime.now().strftime('%H:%M:%S')
    
    return jsonify({'message': 'Stop signal sent'})

@app.route('/clear', methods=['POST'])
def clear_results():
    """Clear results"""
    user_session = get_user_session()
    
    user_session['task_results'].clear()
    user_session['task_status'].update({
        'running': False,
        'progress': 0,
        'total': 0,
        'success': 0,
        'error': 0,
        'current_code': '',
        'start_time': None,
        'end_time': None
    })
    
    return jsonify({'message': 'Results cleared'})

# Telegram Monitor Routes
@app.route('/telegram/start', methods=['POST'])
def start_telegram_monitor():
    """Start Telegram monitor"""
    global telegram_monitor, monitor_status
    
    if monitor_status['running']:
        return jsonify({'error': 'Monitor is already running'}), 400
    
    try:
        api_id = request.json.get('api_id')
        api_hash = request.json.get('api_hash')
        
        if not api_id or not api_hash:
            return jsonify({'error': 'API ID and Hash are required'}), 400
        
        # Create monitor instance
        telegram_monitor = TelegramMonitor(int(api_id), api_hash)
        
        # Start monitor in background thread
        def run_monitor():
            global monitor_status
            try:
                monitor_status['running'] = True
                monitor_status['start_time'] = datetime.now().strftime('%H:%M:%S')
                
                # Load config
                telegram_monitor.load_config()
                monitor_status['channels'] = telegram_monitor.monitored_channels
                
                # Run monitor
                asyncio.run(telegram_monitor.start())
                
            except Exception as e:
                print(f"Monitor error: {str(e)}")
            finally:
                monitor_status['running'] = False
        
        monitor_thread = threading.Thread(target=run_monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return jsonify({'message': 'Telegram monitor started successfully!'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/telegram/stop', methods=['POST'])
def stop_telegram_monitor():
    """Stop Telegram monitor"""
    global monitor_status
    
    if not monitor_status['running']:
        return jsonify({'error': 'Monitor is not running'}), 400
    
    monitor_status['running'] = False
    return jsonify({'message': 'Monitor stop signal sent'})

@app.route('/telegram/status')
def get_telegram_status():
    """Get Telegram monitor status"""
    global telegram_monitor, monitor_status
    
    if telegram_monitor:
        monitor_status['stats'] = telegram_monitor.get_stats()
        # Add channel-specific stats
        monitor_status['channels'] = telegram_monitor.monitored_channels
    
    return jsonify(monitor_status)

@app.route('/telegram/channels', methods=['GET', 'POST'])
def manage_channels():
    """Manage monitored channels"""
    global telegram_monitor
    
    if request.method == 'GET':
        # Load channels from config
        try:
            with open('monitor_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                return jsonify(config.get('channels', []))
        except FileNotFoundError:
            return jsonify([])
    
    elif request.method == 'POST':
        # Add new channel
        try:
            username = request.json.get('username')
            name = request.json.get('name', username)
            
            if not username:
                return jsonify({'error': 'Username is required'}), 400
            
            # Load current config
            try:
                with open('monitor_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except FileNotFoundError:
                config = {"channels": [], "settings": {}}
            
            # Check if channel already exists
            for channel in config['channels']:
                if channel.get('username') == username:
                    return jsonify({'error': 'Channel already exists'}), 400
            
            # Add new channel
            new_channel = {
                'username': username,
                'name': name,
                'enabled': True
            }
            config['channels'].append(new_channel)
            
            # Save config
            with open('monitor_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return jsonify({'message': 'Channel added successfully', 'channel': new_channel})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/telegram/channels/<path:username>', methods=['DELETE'])
def remove_channel(username):
    """Remove monitored channel"""
    try:
        # Decode username from URL
        import urllib.parse
        decoded_username = urllib.parse.unquote(username)
        
        # Load current config
        with open('monitor_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Remove channel - handle both URL and username formats
        original_length = len(config['channels'])
        config['channels'] = [ch for ch in config['channels'] if ch.get('username') != decoded_username]
        
        if len(config['channels']) == original_length:
            return jsonify({'error': 'Channel not found'}), 404
        
        # Save config
        with open('monitor_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return jsonify({'message': 'Channel removed successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup_user_session():
    """Cleanup user session data"""
    try:
        user_id = session.get('user_id')
        if user_id:
            # Delete session from Redis
            session_key = f"user_session:{user_id}"
            redis_client.delete(session_key)
        
        # Clear Flask session
        session.clear()
        
        return jsonify({'message': 'Session cleaned up successfully!'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def cleanup_old_sessions():
    """Cleanup old user sessions from Redis"""
    try:
        # Get all session keys
        session_keys = redis_client.keys("user_session:*")
        
        for key in session_keys:
            try:
                session_data = json.loads(redis_client.get(key))
                last_accessed = datetime.fromisoformat(session_data.get('last_accessed', '1970-01-01T00:00:00'))
                
                # Delete sessions older than 24 hours
                if datetime.now() - last_accessed > timedelta(hours=24):
                    redis_client.delete(key)
                    print(f"Cleaned up old session: {key}")
                    
            except Exception as e:
                print(f"Error cleaning session {key}: {str(e)}")
                
    except Exception as e:
        print(f"Error in cleanup_old_sessions: {str(e)}")

if __name__ == '__main__':
    # Create directories
    os.makedirs('templates', exist_ok=True)
    
    # Test Redis connection
    try:
        redis_client.ping()
        print("✅ Redis connection successful")
    except Exception as e:
        print(f"❌ Redis connection failed: {str(e)}")
        print("Please make sure Redis is running on localhost:6379")
        exit(1)
    
    print("🚀 Starting CyborX Redeem Tool Web App (Multi-User + Redis)...")
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("👥 Multi-user support enabled - each user has isolated session")
    print("💾 Data stored in Redis - scalable and persistent")
    print("🔄 Session auto-expires after 24 hours")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

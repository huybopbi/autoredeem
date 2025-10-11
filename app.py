#!/usr/bin/env python3
"""
CyborX Redeem Tool - Web App
Flask web application for automatic code redemption
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import os
import threading
import time
import json
import asyncio
import uuid
import shutil
from datetime import datetime
from redeem_tool import CyborXRedeemTool
from telegram_monitor import TelegramMonitor

app = Flask(__name__)
app.secret_key = 'cyborx_redeem_tool_2024_secure_key_for_multi_user'

# User sessions storage
user_sessions = {}

def get_user_session():
    """Get or create user session"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    user_id = session['user_id']
    if user_id not in user_sessions:
        user_sessions[user_id] = {
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
            'files': {
                'codes_file': None,
                'cookies_file': None
            }
        }
    
    return user_sessions[user_id]

def get_user_files_dir():
    """Get user-specific files directory"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    user_dir = f"user_files/{user_id}"
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

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
    
    def load_codes_from_file(self, filename):
        """Load codes from user-specific file"""
        return super().load_codes_from_file(filename)
    
    def load_cookies_from_file(self, filename):
        """Load cookies from user-specific file"""
        return super().load_cookies_from_file(filename)

def run_redeem_task(codes, cookies, mode='single', max_workers=5, user_session=None):
    """Run redeem task in background thread"""
    try:
        user_session['task_status']['running'] = True
        user_session['task_status']['start_time'] = datetime.now().strftime('%H:%M:%S')
        user_session['task_status']['progress'] = 0
        user_session['task_status']['success'] = 0
        user_session['task_status']['error'] = 0
        user_session['task_results'].clear()
        
        # Create tool instance
        tool = WebRedeemTool(cookies, user_session)
        
        # Set callback for progress updates
        def progress_callback(data):
            user_session['task_status'].update(data)
        
        tool.set_web_callback(progress_callback)
        
        # Run based on mode
        if mode == 'single':
            tool.run_single_thread(codes)
        else:
            tool.run_multi_thread(codes, max_workers)
        
        user_session['task_status']['end_time'] = datetime.now().strftime('%H:%M:%S')
        
    except Exception as e:
        print(f"Error in redeem task: {str(e)}")
    finally:
        user_session['task_status']['running'] = False

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    try:
        user_session = get_user_session()
        user_dir = get_user_files_dir()
        
        if not user_dir:
            flash('Session error. Please refresh the page.', 'error')
            return redirect(url_for('index'))
        
        # Handle codes file
        if 'codes_file' in request.files:
            codes_file = request.files['codes_file']
            if codes_file.filename:
                codes_path = os.path.join(user_dir, 'codes.txt')
                codes_file.save(codes_path)
                user_session['files']['codes_file'] = codes_path
                flash('Codes file uploaded successfully!', 'success')
        
        # Handle cookies file
        if 'cookies_file' in request.files:
            cookies_file = request.files['cookies_file']
            if cookies_file.filename:
                cookies_path = os.path.join(user_dir, 'cookies.txt')
                cookies_file.save(cookies_path)
                user_session['files']['cookies_file'] = cookies_path
                flash('Cookies file uploaded successfully!', 'success')
        
        # Handle manual codes input
        if 'codes_text' in request.form and request.form['codes_text']:
            codes_text = request.form['codes_text']
            codes_path = os.path.join(user_dir, 'codes.txt')
            with open(codes_path, 'w', encoding='utf-8') as f:
                f.write(codes_text)
            user_session['files']['codes_file'] = codes_path
            flash('Codes saved successfully!', 'success')
        
        # Handle manual cookies input
        if 'cookies_text' in request.form and request.form['cookies_text']:
            cookies_text = request.form['cookies_text']
            cookies_path = os.path.join(user_dir, 'cookies.txt')
            with open(cookies_path, 'w', encoding='utf-8') as f:
                f.write(cookies_text)
            user_session['files']['cookies_file'] = cookies_path
            flash('Cookies saved successfully!', 'success')
        
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
        # Load codes from user's file
        codes_path = user_session['files'].get('codes_file')
        if not codes_path or not os.path.exists(codes_path):
            return jsonify({'error': 'No codes found. Please upload codes first.'}), 400
        
        tool = WebRedeemTool()
        codes = tool.load_codes_from_file(codes_path)
        
        if not codes:
            return jsonify({'error': 'No codes found. Please upload codes first.'}), 400
        
        # Load cookies from user's file
        cookies_path = user_session['files'].get('cookies_file')
        if not cookies_path or not os.path.exists(cookies_path):
            return jsonify({'error': 'No cookies found. Please upload cookies first.'}), 400
        
        cookies = tool.load_cookies_from_file(cookies_path)
        if not cookies:
            return jsonify({'error': 'No cookies found. Please upload cookies first.'}), 400
        
        # Get parameters
        mode = request.json.get('mode', 'single')
        max_workers = int(request.json.get('max_workers', 5))
        
        # Start background task
        task_thread = threading.Thread(
            target=run_redeem_task,
            args=(codes, cookies, mode, max_workers, user_session)
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
        codes_path = user_session['files'].get('codes_file')
        
        if not codes_path or not os.path.exists(codes_path):
            return jsonify({
                'codes': [],
                'count': 0,
                'filename': 'No file uploaded'
            })
        
        tool = CyborXRedeemTool()
        codes = tool.load_codes_from_file(codes_path)
        
        return jsonify({
            'codes': codes,
            'count': len(codes),
            'filename': os.path.basename(codes_path)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cookies')
def get_cookies():
    """Get current cookies info"""
    try:
        user_session = get_user_session()
        cookies_path = user_session['files'].get('cookies_file')
        
        if not cookies_path or not os.path.exists(cookies_path):
            return jsonify({
                'cookies': {},
                'count': 0,
                'filename': 'No file uploaded'
            })
        
        tool = CyborXRedeemTool()
        cookies = tool.load_cookies_from_file(cookies_path)
        
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
            'filename': os.path.basename(cookies_path)
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
def cleanup_user_files():
    """Cleanup user files when session ends"""
    try:
        user_session = get_user_session()
        user_dir = get_user_files_dir()
        
        if user_dir and os.path.exists(user_dir):
            shutil.rmtree(user_dir)
            flash('Files cleaned up successfully!', 'success')
        
        # Clear session
        session.clear()
        
        return jsonify({'message': 'Session cleaned up successfully!'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def cleanup_old_sessions():
    """Cleanup old user sessions and files"""
    import time
    current_time = time.time()
    
    # Cleanup sessions older than 24 hours
    for user_id in list(user_sessions.keys()):
        # This is a simple cleanup - in production you'd want more sophisticated session management
        pass

if __name__ == '__main__':
    # Create directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('user_files', exist_ok=True)
    
    print("🚀 Starting CyborX Redeem Tool Web App (Multi-User)...")
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("👥 Multi-user support enabled - each user has isolated session")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

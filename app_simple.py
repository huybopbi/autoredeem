#!/usr/bin/env python3
"""
CyborX Redeem Tool - Simple Web App
Flask web application for automatic code redemption
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import os
import threading
import time
import json
import uuid
from datetime import datetime
from redeem_tool import CyborXRedeemTool

app = Flask(__name__)
app.secret_key = 'cyborx_redeem_tool_2024_simple'

# Simple in-memory storage
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
            'data': {
                'codes': [],
                'cookies': {},
                'codes_text': '',
                'cookies_text': ''
            }
        }
    
    return user_sessions[user_id]

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
        if line and '=' in line:
            key, value = line.split('=', 1)
            cookies[key.strip()] = value.strip()
    
    return cookies

class SimpleRedeemTool(CyborXRedeemTool):
    """Simple redeem tool for web app"""
    
    def __init__(self, cookies, user_session):
        super().__init__(cookies)
        self.user_session = user_session
        self.web_callback = None
    
    def set_web_callback(self, callback):
        """Set callback for web updates"""
        self.web_callback = callback
    
    def update_progress(self, data):
        """Update progress in user session"""
        if self.web_callback:
            self.web_callback(data)
    
    def run_single_thread(self, codes):
        """Run single thread redeem"""
        self.user_session['task_status']['total'] = len(codes)
        self.user_session['task_status']['progress'] = 0
        self.user_session['task_status']['success'] = 0
        self.user_session['task_status']['error'] = 0
        
        for i, code in enumerate(codes):
            if not self.user_session['task_status']['running']:
                break
            
            self.user_session['task_status']['current_code'] = code
            self.user_session['task_status']['progress'] = i + 1
            
            try:
                result = self.redeem_code(code)
                if result:
                    self.user_session['task_results'].append({
                        'code': code,
                        'status': 'success',
                        'result': result,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
                    self.user_session['task_status']['success'] += 1
                else:
                    self.user_session['task_results'].append({
                        'code': code,
                        'status': 'failed',
                        'result': 'No result',
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
                    self.user_session['task_status']['error'] += 1
            except Exception as e:
                self.user_session['task_results'].append({
                    'code': code,
                    'status': 'error',
                    'result': str(e),
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
                self.user_session['task_status']['error'] += 1
            
            if self.web_callback:
                self.web_callback(self.user_session['task_status'])
            
            time.sleep(1)  # Small delay between requests

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
        tool = SimpleRedeemTool(cookies, user_session)
        
        # Set callback for progress updates
        def progress_callback(data):
            user_session['task_status'].update(data)
        
        tool.set_web_callback(progress_callback)
        
        # Run single thread
        tool.run_single_thread(codes)
        
        user_session['task_status']['end_time'] = datetime.now().strftime('%H:%M:%S')
        
    except Exception as e:
        print(f"Error in redeem task: {str(e)}")
    finally:
        user_session['task_status']['running'] = False

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/ping')
def ping():
    """Simple ping endpoint"""
    return "pong", 200

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'app': 'running',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    try:
        user_session = get_user_session()
        
        # Handle codes file
        if 'codes_file' in request.files:
            codes_file = request.files['codes_file']
            if codes_file.filename:
                codes_text = codes_file.read().decode('utf-8')
                codes = parse_codes_from_text(codes_text)
                user_session['data']['codes'] = codes
                user_session['data']['codes_text'] = codes_text
                flash(f'Codes file uploaded successfully! ({len(codes)} codes loaded)', 'success')
        
        # Handle cookies file
        if 'cookies_file' in request.files:
            cookies_file = request.files['cookies_file']
            if cookies_file.filename:
                cookies_text = cookies_file.read().decode('utf-8')
                cookies = parse_cookies_from_text(cookies_text)
                user_session['data']['cookies'] = cookies
                user_session['data']['cookies_text'] = cookies_text
                flash(f'Cookies file uploaded successfully! ({len(cookies)} cookies loaded)', 'success')
        
        # Handle manual codes input
        if 'codes_text' in request.form and request.form['codes_text']:
            codes_text = request.form['codes_text']
            codes = parse_codes_from_text(codes_text)
            user_session['data']['codes'] = codes
            user_session['data']['codes_text'] = codes_text
            flash(f'Codes saved successfully! ({len(codes)} codes loaded)', 'success')
        
        # Handle manual cookies input
        if 'cookies_text' in request.form and request.form['cookies_text']:
            cookies_text = request.form['cookies_text']
            cookies = parse_cookies_from_text(cookies_text)
            user_session['data']['cookies'] = cookies
            user_session['data']['cookies_text'] = cookies_text
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
            args=(codes, cookies, mode, max_workers, user_session)
        )
        task_thread.daemon = True
        task_thread.start()
        
        return jsonify({'message': 'Redeem process started successfully!'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stop', methods=['POST'])
def stop_redeem():
    """Stop redeem process"""
    user_session = get_user_session()
    user_session['task_status']['running'] = False
    return jsonify({'message': 'Redeem process stopped!'})

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

@app.route('/clear', methods=['POST'])
def clear_results():
    """Clear task results"""
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
    return jsonify({'message': 'Results cleared successfully!'})

if __name__ == '__main__':
    # Create directories
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 Starting CyborX Redeem Tool (Simple Version)...")
    print("🌐 Open your browser and go to: http://0.0.0.0:5000")
    print("👥 Multi-user support enabled - each user has isolated session")
    print("💾 Data stored in memory - simple and fast")
    
    app.run(debug=False, host='0.0.0.0', port=5000)

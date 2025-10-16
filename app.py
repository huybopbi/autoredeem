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
import uuid
import shutil
from datetime import datetime, timedelta
from redeem_tool import CyborXRedeemTool

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'cyborx_redeem_tool_2024_secure_key_for_multi_user')

# Production-ready session configuration
# Use memory session for Railway (non-persistent filesystem)
app.config['SESSION_TYPE'] = 'memory'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'cyborx:'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

Session(app)

# Global variables to store task data
global_task_data = {}

def get_user_session():
    """Get or create user session in memory"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session.permanent = True
    
    # Use memory storage only
    if 'user_data' not in session:
        session['user_data'] = {
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
            },
            'created_at': datetime.now().isoformat(),
            'last_accessed': datetime.now().isoformat()
        }
    
    # Update last accessed time
    session['user_data']['last_accessed'] = datetime.now().isoformat()
    return session['user_data']

def save_user_session(user_id, session_data):
    """Save user session to memory"""
    # Use memory storage only
    session['user_data'] = session_data

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
        
        # Add to results (don't duplicate counting - let parent class handle it)
        if self.user_session and result:
            # Parse response to determine success
            response_text = result['response']
            is_success = False
            
            try:
                import json
                response_json = json.loads(response_text)
                is_success = response_json.get("ok") == True
            except json.JSONDecodeError:
                # Fallback to text-based detection
                is_success = "success" in response_text.lower() or "redeemed" in response_text.lower()
            
            result_data = {
                    'code': code,
                'status': 'success' if is_success else 'error',
                    'response': result['response'],
                    'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            
            self.user_session['task_results'].append(result_data)
            
            # Dừng task nếu thành công
            if is_success:
                self.user_session['task_status']['running'] = False
                self.user_session['task_status']['end_time'] = datetime.now().strftime('%H:%M:%S')
        elif self.user_session and not result:
            # Request failed
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
    global global_task_data
    print(f"[DEBUG] run_redeem_task started with {len(codes)} codes, mode: {mode}")
    
    try:
        # Initialize global task data
        global_task_data[user_id] = {
            'task_results': [],
            'task_status': {
                'running': True,
                'progress': 0,
                'total': len(codes),
                'success': 0,
                'error': 0,
                'current_code': '',
                'start_time': datetime.now().strftime('%H:%M:%S'),
                'end_time': None
            }
        }
        
        print(f"[DEBUG] Initial state created in global_task_data")
        
        # Create tool instance
        print(f"[DEBUG] Creating WebRedeemTool instance")
        tool = WebRedeemTool(cookies, global_task_data[user_id])
        
        # Set callback for progress updates
        def progress_callback(data):
            try:
                # Update the global task data with current counters
                if user_id in global_task_data:
                    # Get current counters from the tool
                    current_data = {
                        'progress': tool.processed_count,
                        'total': tool.total_codes,
                        'success': tool.success_count,
                        'error': tool.error_count
                    }
                    global_task_data[user_id]['task_status'].update(current_data)
                    print(f"[DEBUG] Progress updated: {current_data}")
            except Exception as e:
                print(f"Warning: Progress callback failed: {e}")
        
        tool.set_web_callback(progress_callback)
        print(f"[DEBUG] Callback set, starting redeem process...")
        
        # Run based on mode
        if mode == 'single':
            print(f"[DEBUG] Running single thread mode")
            tool.run_single_thread(codes)
        else:
            print(f"[DEBUG] Running multi thread mode with {max_workers} workers")
            tool.run_multi_thread(codes, max_workers)
        
        print(f"[DEBUG] Redeem process completed")
        
        # Update final state with final counters
        if user_id in global_task_data:
            # Final update with actual counters
            final_data = {
                'progress': tool.processed_count,
                'total': tool.total_codes,
                'success': tool.success_count,
                'error': tool.error_count,
                'end_time': datetime.now().strftime('%H:%M:%S'),
                'running': False
            }
            global_task_data[user_id]['task_status'].update(final_data)
            print(f"[DEBUG] Final state updated: {final_data}")
        
    except Exception as e:
        print(f"Error in redeem task: {str(e)}")
        import traceback
        traceback.print_exc()
        # Update error state
        try:
            if user_id in global_task_data:
                global_task_data[user_id]['task_status']['running'] = False
        except:
            pass
    finally:
        # Ensure running is set to False
        try:
            if user_id in global_task_data:
                global_task_data[user_id]['task_status']['running'] = False
                print(f"[DEBUG] Task marked as completed")
        except:
            pass

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/ping')
def ping():
    """Simple ping endpoint for healthcheck"""
    return "pong", 200

@app.route('/account-info', methods=['POST'])
def get_account_info():
    """Get account information from cyborx.net dashboard"""
    try:
        data = request.get_json()
        cookies_text = data.get('cookies_text', '')
        
        if not cookies_text.strip():
            return jsonify({'error': 'No cookies provided'}), 400
        
        # Parse cookies
        cookies = parse_cookies_from_text(cookies_text)
        if not cookies:
            return jsonify({'error': 'Invalid cookies format'}), 400
        
        # Create session with cookies
        import requests
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        session.cookies.update(cookies)
        
        # Get account info from cyborx.net dashboard
        try:
            print(f"[DEBUG] Making request to cyborx.net with cookies: {cookies}")
            response = session.get('https://cyborx.net/app/dashboard', timeout=10)
            print(f"[DEBUG] Response status: {response.status_code}")
            if response.status_code == 200:
                # Parse HTML to extract account info
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                account_info = {
                    'status': 'success',
                    'account_type': 'Unknown',
                    'expiry_date': 'Unknown',
                    'credits': 'Unknown',
                    'kcoin': 'Unknown',
                    'xcoin': 'Unknown',
                    'username': 'Unknown'
                }
                
                # Parse account information based on actual cyborx.net dashboard structure
                
                # Find username from the sidebar profile section
                # Look for pattern like "Viettel Telecom PREMIUM @hatrangktvt"
                profile_link = soup.find('a', href='/app/settings')
                if profile_link:
                    profile_text = profile_link.get_text()
                    import re
                    username_match = re.search(r'@(\w+)', profile_text)
                    if username_match:
                        account_info['username'] = username_match.group(1)
                
                # Find account type (PREMIUM/FREE) from sidebar
                if profile_link:
                    profile_text = profile_link.get_text()
                    if 'PREMIUM' in profile_text.upper():
                        account_info['account_type'] = 'Premium'
                    else:
                        account_info['account_type'] = 'Free'
                
                # Find credits - look for "Credits" label followed by number in main content
                credits_elements = soup.find_all(string=lambda text: text and text.strip() == 'Credits')
                for credits_element in credits_elements:
                    parent = credits_element.parent
                    if parent:
                        # Look for the next sibling that contains the number
                        next_sibling = parent.find_next_sibling()
                        if next_sibling:
                            credits_text = next_sibling.get_text().strip()
                            if credits_text.isdigit():
                                account_info['credits'] = credits_text
                                break
                
                # Find KCoin
                kcoin_elements = soup.find_all(string=lambda text: text and text.strip() == 'KCoin')
                for kcoin_element in kcoin_elements:
                    parent = kcoin_element.parent
                    if parent:
                        next_sibling = parent.find_next_sibling()
                        if next_sibling:
                            kcoin_text = next_sibling.get_text().strip()
                            if kcoin_text.isdigit():
                                account_info['kcoin'] = kcoin_text
                                break
                
                # Find XCoin
                xcoin_elements = soup.find_all(string=lambda text: text and text.strip() == 'XCoin')
                for xcoin_element in xcoin_elements:
                    parent = xcoin_element.parent
                    if parent:
                        next_sibling = parent.find_next_sibling()
                        if next_sibling:
                            xcoin_text = next_sibling.get_text().strip()
                            # Remove $ sign if present
                            xcoin_value = xcoin_text.replace('$', '').strip()
                            if xcoin_value.isdigit():
                                account_info['xcoin'] = xcoin_value
                                break
                
                # Find expiry date - look for "Expiry Date" section
                expiry_elements = soup.find_all(string=lambda text: text and text.strip() == 'Expiry Date')
                print(f"[DEBUG] Found {len(expiry_elements)} Expiry Date elements")
                for expiry_element in expiry_elements:
                    parent = expiry_element.parent
                    if parent:
                        # Look for date in the same parent element or next sibling
                        expiry_text = parent.get_text()
                        print(f"[DEBUG] Expiry parent text: {expiry_text}")
                        import re
                        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', expiry_text)
                        if date_match:
                            account_info['expiry_date'] = date_match.group(1)
                            print(f"[DEBUG] Found expiry date: {date_match.group(1)}")
                            break
                        
                        # Check next sibling
                        next_sibling = parent.find_next_sibling()
                        if next_sibling:
                            expiry_text = next_sibling.get_text().strip()
                            print(f"[DEBUG] Expiry next sibling text: {expiry_text}")
                            date_match = re.search(r'(\d{2}/\d{2}/\d{4})', expiry_text)
                            if date_match:
                                account_info['expiry_date'] = date_match.group(1)
                                print(f"[DEBUG] Found expiry date in sibling: {date_match.group(1)}")
                                break
                        
                        # Look for div with class "k" that contains the date (nearby structure)
                        # The date is in a <div class="k"> that's a sibling of the parent's parent
                        grandparent = parent.parent
                        if grandparent:
                            # Look for next sibling of grandparent that contains div with class "k"
                            grandparent_next = grandparent.find_next_sibling()
                            if grandparent_next:
                                date_div = grandparent_next.find('div', class_='k')
                                if date_div:
                                    date_text = date_div.get_text().strip()
                                    print(f"[DEBUG] Found date div: {date_text}")
                                    date_match = re.search(r'(\d{2}/\d{2}/\d{4})', date_text)
                                    if date_match:
                                        account_info['expiry_date'] = date_match.group(1)
                                        print(f"[DEBUG] Found expiry date in date div: {date_match.group(1)}")
                                        break
                
                # Alternative: Look for "Your plan will expire in X days" text
                if account_info['expiry_date'] == 'Unknown':
                    expire_text = soup.find(string=lambda text: text and 'expire in' in text.lower())
                    if expire_text:
                        import re
                        days_match = re.search(r'expire in\s*(\d+)\s*days?', expire_text.lower())
                        if days_match:
                            from datetime import datetime, timedelta
                            days = int(days_match.group(1))
                            expiry_date = datetime.now() + timedelta(days=days)
                            account_info['expiry_date'] = expiry_date.strftime('%d/%m/%Y')
                
                return jsonify(account_info)
            else:
                return jsonify({'error': f'Failed to fetch account info. Status: {response.status_code}'}), 400
                
        except requests.RequestException as e:
            return jsonify({'error': f'Network error: {str(e)}'}), 400
        except Exception as e:
            return jsonify({'error': f'Error parsing account info: {str(e)}'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Simple health check without Redis dependency
        health_info = {
            'status': 'healthy',
            'app': 'running',
            'timestamp': datetime.now().isoformat()
        }
        
        # Redis is not used in this simplified version
        health_info['redis'] = 'not_used'
        
        return jsonify(health_info), 200
        
    except Exception as e:
        error_info = {
            'status': 'unhealthy',
            'app': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(error_info), 503


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
                print(f'[INFO] Codes file uploaded successfully! ({len(codes)} codes loaded)')
        
        # Handle cookies file
        if 'cookies_file' in request.files:
            cookies_file = request.files['cookies_file']
            if cookies_file.filename:
                cookies_text = cookies_file.read().decode('utf-8')
                cookies = parse_cookies_from_text(cookies_text)
                user_session['data']['cookies'] = cookies
                user_session['data']['cookies_text'] = cookies_text
                save_user_session(user_id, user_session)
                print(f'[INFO] Cookies file uploaded successfully! ({len(cookies)} cookies loaded)')
        
        # Handle manual codes input
        if 'codes_text' in request.form and request.form['codes_text']:
            codes_text = request.form['codes_text']
            codes = parse_codes_from_text(codes_text)
            user_session['data']['codes'] = codes
            user_session['data']['codes_text'] = codes_text
            save_user_session(user_id, user_session)
            print(f'[INFO] Codes saved successfully! ({len(codes)} codes loaded)')
        
        # Handle manual cookies input
        if 'cookies_text' in request.form and request.form['cookies_text']:
            cookies_text = request.form['cookies_text']
            cookies = parse_cookies_from_text(cookies_text)
            user_session['data']['cookies'] = cookies
            user_session['data']['cookies_text'] = cookies_text
            save_user_session(user_id, user_session)
            print(f'[INFO] Cookies saved successfully! ({len(cookies)} cookies loaded)')
        
    except Exception as e:
        print(f"[ERROR] Upload error: {str(e)}")
        return jsonify({'error': f'Error uploading files: {str(e)}'}), 500
    
    return jsonify({'success': True})

@app.route('/start', methods=['POST'])
def start_redeem():
    """Start redeem process"""
    try:
        user_session = get_user_session()
        user_id = session['user_id']  # Get user_id from session
        
        print(f"[DEBUG] Starting redeem for user: {user_id}")
        print(f"[DEBUG] Task running: {user_session['task_status']['running']}")
        
        if user_session['task_status']['running']:
            return jsonify({'error': 'Task is already running'}), 400
        
        # Load codes from user session
        codes = user_session['data']['codes']
        print(f"[DEBUG] Codes loaded: {len(codes)} codes")
        if not codes:
            return jsonify({'error': 'No codes found. Please upload codes first.'}), 400
        
        # Load cookies from user session
        cookies = user_session['data']['cookies']
        print(f"[DEBUG] Cookies loaded: {len(cookies)} cookies")
        if not cookies:
            return jsonify({'error': 'No cookies found. Please upload cookies first.'}), 400
        
        # Get parameters
        mode = request.json.get('mode', 'single')
        max_workers = int(request.json.get('max_workers', 5))
        print(f"[DEBUG] Mode: {mode}, Workers: {max_workers}")
        
        # Start background task
        print(f"[DEBUG] Starting background thread...")
        task_thread = threading.Thread(
            target=run_redeem_task,
            args=(codes, cookies, mode, max_workers, user_id)
        )
        task_thread.daemon = True
        task_thread.start()
        
        print(f"[DEBUG] Thread started successfully")
        return jsonify({'message': 'Redeem process started successfully!'})
        
    except Exception as e:
        print(f"[ERROR] Start redeem failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/status')
def get_status():
    """Get current task status"""
    global global_task_data
    user_id = session.get('user_id')
    
    if user_id and user_id in global_task_data:
        return jsonify(global_task_data[user_id]['task_status'])
    else:
        # Return default status if no task running
        return jsonify({
            'running': False,
            'progress': 0,
            'total': 0,
            'success': 0,
            'error': 0,
            'current_code': '',
            'start_time': None,
            'end_time': None
        })

@app.route('/results')
def get_results():
    """Get task results"""
    global global_task_data
    user_id = session.get('user_id')
    
    if user_id and user_id in global_task_data:
        return jsonify(global_task_data[user_id]['task_results'])
    else:
        return jsonify([])

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


@app.route('/cleanup', methods=['POST'])
def cleanup_user_session():
    """Cleanup user session data"""
    try:
        # Clear Flask session
        session.clear()
        
        return jsonify({'message': 'Session cleaned up successfully!'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create directories
    os.makedirs('templates', exist_ok=True)
    
    # Production configuration
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    print("[START] Starting CyborX Redeem Tool Web App...")
    print(f"[URL] Open your browser and go to: http://{host}:{port}")
    print("[INFO] Production mode - using memory session storage")
    print("[INFO] Multi-user support enabled - each user has isolated session")
    print(f"[INFO] Debug mode: {debug_mode}")
    print(f"[INFO] Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    # Memory session doesn't need directory creation
    
    app.run(debug=debug_mode, host=host, port=port)

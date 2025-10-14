import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class CyborXRedeemTool:
    def __init__(self, cookies=None):
        self.session = requests.Session()
        self.base_url = "https://cyborx.net"
        self.redeem_url = f"{self.base_url}/api/redeem_submit.php"
        
        # Headers giống như browser
        self.headers = {
            'authority': 'cyborx.net',
            'accept': '*/*',
            'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://cyborx.net',
            'referer': 'https://cyborx.net/app/redeem',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        
        self.session.headers.update(self.headers)
        
        # Thêm cookies nếu có
        if cookies:
            self.session.cookies.update(cookies)
        
        # Thống kê
        self.processed_count = 0
        self.success_count = 0
        self.error_count = 0
        self.lock = threading.Lock()
        self.should_stop = False  # Flag để dừng khi thành công
        
    def update_progress(self):
        with self.lock:
            self.processed_count += 1
            remaining = self.total_codes - self.processed_count
            print(f"📊 Progress: {self.processed_count}/{self.total_codes} | Remaining: {remaining}")
    
    def redeem_code(self, code, code_number):
        """Redeem một code cụ thể"""
        try:
            # Chuẩn bị data để gửi
            data = {
                'code': code.strip()
            }
            
            print(f"🔄 Processing ({code_number}/{self.total_codes}): {code}")
            
            # Gửi request redeem
            response = self.session.post(
                self.redeem_url,
                data=data,
                timeout=30
            )
            
            self.update_progress()
            
            # Phân tích response
            if response.status_code == 200:
                response_text = response.text.strip()
                
                # Thử parse JSON response
                try:
                    import json
                    response_json = json.loads(response_text)
                    
                    # Kiểm tra response JSON từ API
                    if response_json.get("ok") == True:
                        data = response_json.get("data", {})
                        credits_added = data.get("credits_added", 0)
                        new_status = data.get("new_status", "")
                        new_expiry = data.get("new_expiry", "")
                        
                        print(f"✅ SUCCESS ({code_number}/{self.total_codes}): {code}")
                        print(f"📡 Response: {response_text}")
                        if credits_added > 0:
                            print(f"🎁 Credits added: {credits_added}")
                        if new_status:
                            print(f"👑 New status: {new_status}")
                        if new_expiry:
                            print(f"📅 Expiry: {new_expiry}")
                        
                        with self.lock:
                            self.success_count += 1
                            self.should_stop = True  # Dừng khi thành công
                    else:
                        # API trả về ok: false
                        error_msg = response_json.get("error", "Unknown error")
                        print(f"❌ API ERROR ({code_number}/{self.total_codes}): {code}")
                        print(f"📡 Response: {response_text}")
                        print(f"🚫 Error: {error_msg}")
                        with self.lock:
                            self.error_count += 1
                            
                except json.JSONDecodeError:
                    # Không phải JSON, fallback về logic cũ
                    if "success" in response_text.lower() or "redeemed" in response_text.lower():
                        print(f"✅ SUCCESS ({code_number}/{self.total_codes}): {code}")
                        print(f"📡 Response: {response_text}")
                        with self.lock:
                            self.success_count += 1
                            self.should_stop = True  # Dừng khi thành công
                    elif "not found" in response_text.lower():
                        print(f"❌ NOT FOUND ({code_number}/{self.total_codes}): {code}")
                        print(f"📡 Response: {response_text}")
                        with self.lock:
                            self.error_count += 1
                    elif "already used" in response_text.lower() or "expired" in response_text.lower():
                        print(f"⚠️  ALREADY USED/EXPIRED ({code_number}/{self.total_codes}): {code}")
                        print(f"📡 Response: {response_text}")
                        with self.lock:
                            self.error_count += 1
                    else:
                        print(f"❓ UNKNOWN ({code_number}/{self.total_codes}): {code}")
                        print(f"📡 Response: {response_text}")
                        with self.lock:
                            self.error_count += 1
            else:
                print(f"❌ HTTP ERROR ({code_number}/{self.total_codes}): {code}")
                print(f"📡 Status: {response.status_code}")
                with self.lock:
                    self.error_count += 1
            
            print("-" * 70)
            
            return {
                'code': code,
                'status_code': response.status_code,
                'response': response.text,
                'number': code_number
            }
            
        except requests.Timeout:
            self.update_progress()
            print(f"⏰ TIMEOUT ({code_number}/{self.total_codes}): {code}")
            with self.lock:
                self.error_count += 1
            return None
            
        except Exception as e:
            self.update_progress()
            print(f"❌ ERROR ({code_number}/{self.total_codes}): {code} - {str(e)}")
            with self.lock:
                self.error_count += 1
            return None
    
    def load_codes_from_file(self, filename):
        """Đọc danh sách code từ file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                codes = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            return codes
        except FileNotFoundError:
            print(f"❌ File {filename} not found!")
            return []
        except Exception as e:
            print(f"❌ Error reading file {filename}: {str(e)}")
            return []
    
    def load_cookies_from_file(self, filename='cookies.txt'):
        """Đọc cookies từ file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Loại bỏ comments và dòng trống
            lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
            
            if not lines:
                return {}
            
            # Parse cookies
            cookies = {}
            for line in lines:
                if '=' in line:
                    parts = line.split(';')
                    for part in parts:
                        part = part.strip()
                        if '=' in part:
                            name, value = part.split('=', 1)
                            cookies[name.strip()] = value.strip()
            
            return cookies
            
        except FileNotFoundError:
            print(f"⚠️  File {filename} not found! Running without cookies...")
            return {}
        except Exception as e:
            print(f"❌ Error reading {filename}: {str(e)}")
            return {}
    
    def run_single_thread(self, codes):
        """Chạy redeem code với single thread"""
        self.total_codes = len(codes)
        self.should_stop = False  # Reset flag
        
        print(f"✅ Loaded {self.total_codes} codes")
        print(f"🧵 Mode: Single Thread")
        print(f"⏰ Timeout: 30 seconds")
        print("🚀 Starting redeem process...")
        print("🛑 Will stop after first successful redeem")
        print("=" * 70)
        
        for i, code in enumerate(codes, 1):
            if self.should_stop:
                print(f"🛑 Stopping after successful redeem at code {i-1}")
                break
                
            self.redeem_code(code, i)
            time.sleep(1)  # Delay 1 giây giữa các request
    
    def run_multi_thread(self, codes, max_workers=5):
        """Chạy redeem code với multi-threading"""
        self.total_codes = len(codes)
        self.should_stop = False  # Reset flag
        
        print(f"✅ Loaded {self.total_codes} codes")
        print(f"🧵 Mode: Multi-threaded ({max_workers} workers)")
        print(f"⏰ Timeout: 30 seconds")
        print("🚀 Starting multi-threaded redeem process...")
        print("🛑 Will stop after first successful redeem")
        print("=" * 70)
        
        code_data = [(code, i+1) for i, code in enumerate(codes)]
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.redeem_code, code, number) for code, number in code_data]
            
            for future in as_completed(futures):
                if self.should_stop:
                    print("🛑 Stopping after successful redeem")
                    # Cancel remaining futures
                    for f in futures:
                        f.cancel()
                    break
                result = future.result()
    
    def print_summary(self):
        """In tóm tắt kết quả"""
        print("=" * 70)
        print(f"📊 FINAL SUMMARY:")
        print(f"✅ Successful: {self.success_count}/{self.total_codes}")
        print(f"❌ Failed: {self.error_count}/{self.total_codes}")
        print(f"📋 Total processed: {self.total_codes}")
        print(f"🎯 Success rate: {(self.success_count/self.total_codes*100):.1f}%")

def main():
    # Tạo tool instance
    tool = CyborXRedeemTool()
    
    # Load cookies từ file
    cookies = tool.load_cookies_from_file('cookies.txt')
    if cookies:
        tool.session.cookies.update(cookies)
        print(f"🍪 Loaded {len(cookies)} cookies from cookies.txt")
    else:
        print("⚠️  No cookies loaded - you may get 401 errors")
        print("💡 Run 'python get_cookies.py' to get cookies from browser")
    
    # Đọc danh sách code từ file
    codes = tool.load_codes_from_file('codes.txt')
    
    if not codes:
        print("❌ No codes found in codes.txt")
        return
    
    # Hỏi người dùng chọn chế độ
    print("Chọn chế độ chạy:")
    print("1. Single Thread (chậm nhưng ổn định)")
    print("2. Multi-threaded (nhanh hơn)")
    
    try:
        choice = input("Nhập lựa chọn (1 hoặc 2): ").strip()
        
        if choice == "1":
            tool.run_single_thread(codes)
        elif choice == "2":
            max_workers = input("Nhập số thread (mặc định 5): ").strip()
            max_workers = int(max_workers) if max_workers.isdigit() else 5
            tool.run_multi_thread(codes, max_workers)
        else:
            print("❌ Lựa chọn không hợp lệ!")
            return
            
        tool.print_summary()
        
    except KeyboardInterrupt:
        print("\n⏹️  Process interrupted by user")
        tool.print_summary()
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()

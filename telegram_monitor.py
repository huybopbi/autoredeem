#!/usr/bin/env python3
"""
Telegram Channel Monitor for CyborX Redeem Tool
Tự động theo dõi kênh Telegram và redeem code khi có code mới
"""

import asyncio
import re
import logging
import json
import time
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.types import Channel, Chat
from redeem_tool import CyborXRedeemTool

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramMonitor:
    def __init__(self, api_id, api_hash, session_name='cyborx_monitor'):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client = TelegramClient(session_name, api_id, api_hash)
        
        # Redeem tool
        self.redeem_tool = CyborXRedeemTool()
        
        # Cấu hình
        self.monitored_channels = []
        self.redeemed_codes = set()  # Tránh redeem trùng lặp
        self.code_patterns = [
            r'CYBORX-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z]+',
            r'cyborx-[a-z0-9]{4}-[a-z0-9]{4}-[a-z]+',
            r'CYBORX\s+[A-Z0-9]{4}\s+[A-Z0-9]{4}\s+[A-Z]+',
            r'cyborx\s+[a-z0-9]{4}\s+[a-z0-9]{4}\s+[a-z]+'
        ]
        
        # Thống kê
        self.stats = {
            'messages_processed': 0,
            'codes_found': 0,
            'codes_redeemed': 0,
            'errors': 0,
            'start_time': None
        }
    
    async def start(self):
        """Khởi động bot"""
        try:
            await self.client.start()
            logger.info("🚀 Telegram Monitor started successfully!")
            
            # Load cookies
            cookies = self.redeem_tool.load_cookies_from_file('cookies.txt')
            if cookies:
                self.redeem_tool.session.cookies.update(cookies)
                logger.info(f"🍪 Loaded {len(cookies)} cookies")
            else:
                logger.warning("⚠️ No cookies found! Please add cookies to cookies.txt")
            
            # Load monitored channels
            self.load_config()
            
            # Setup event handlers
            self.setup_handlers()
            
            self.stats['start_time'] = datetime.now()
            logger.info(f"📡 Monitoring {len(self.monitored_channels)} channels")
            
            # Keep running
            await self.client.run_until_disconnected()
            
        except Exception as e:
            logger.error(f"❌ Error starting monitor: {str(e)}")
    
    def load_config(self):
        """Load cấu hình từ file"""
        try:
            with open('monitor_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.monitored_channels = config.get('channels', [])
                logger.info(f"📋 Loaded {len(self.monitored_channels)} channels from config")
        except FileNotFoundError:
            logger.info("📋 No config file found, creating default...")
            self.create_default_config()
        except Exception as e:
            logger.error(f"❌ Error loading config: {str(e)}")
    
    def create_default_config(self):
        """Tạo file cấu hình mặc định"""
        default_config = {
            "channels": [
                {
                    "username": "cyborx_official",
                    "name": "CyborX Official",
                    "enabled": True
                }
            ],
            "settings": {
                "auto_redeem": True,
                "delay_between_redeems": 2,
                "max_redeems_per_hour": 10,
                "notify_on_success": True,
                "notify_on_error": True
            }
        }
        
        with open('monitor_config.json', 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        logger.info("✅ Created default config file: monitor_config.json")
    
    def setup_handlers(self):
        """Setup event handlers"""
        
        @self.client.on(events.NewMessage)
        async def handle_new_message(event):
            try:
                self.stats['messages_processed'] += 1
                
                # Kiểm tra xem có phải từ kênh được monitor không
                if not self.is_monitored_channel(event.chat_id):
                    return
                
                message_text = event.message.message or ""
                logger.info(f"📨 New message from {event.chat.title}: {message_text[:100]}...")
                
                # Tìm code trong message
                codes = self.extract_codes(message_text)
                
                if codes:
                    self.stats['codes_found'] += len(codes)
                    logger.info(f"🎯 Found {len(codes)} codes: {codes}")
                    
                    # Redeem từng code
                    for code in codes:
                        if code not in self.redeemed_codes:
                            await self.redeem_code(code, event.chat.title)
                        else:
                            logger.info(f"⏭️ Code already redeemed: {code}")
                
            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"❌ Error processing message: {str(e)}")
    
    def is_monitored_channel(self, chat_id):
        """Kiểm tra xem chat có được monitor không"""
        for channel in self.monitored_channels:
            if channel.get('chat_id') == chat_id or channel.get('username') in str(chat_id):
                return channel.get('enabled', True)
        return False
    
    def extract_codes(self, text):
        """Trích xuất code từ text"""
        codes = []
        text_upper = text.upper()
        
        for pattern in self.code_patterns:
            matches = re.findall(pattern, text_upper)
            codes.extend(matches)
        
        # Loại bỏ trùng lặp và chuẩn hóa format
        unique_codes = []
        for code in codes:
            # Chuẩn hóa format
            normalized = code.replace(' ', '-')
            if normalized not in unique_codes:
                unique_codes.append(normalized)
        
        return unique_codes
    
    async def redeem_code(self, code, channel_name):
        """Redeem code"""
        try:
            logger.info(f"🔄 Attempting to redeem: {code}")
            
            # Redeem code
            result = self.redeem_tool.redeem_code(code, 1)
            
            if result and result.get('status_code') == 200:
                response = result.get('response', '')
                
                # Kiểm tra response để xác định thành công
                if any(keyword in response.lower() for keyword in ['success', 'redeemed', 'added']):
                    self.stats['codes_redeemed'] += 1
                    self.redeemed_codes.add(code)
                    logger.info(f"✅ Successfully redeemed: {code}")
                    
                    # Gửi notification (có thể mở rộng)
                    await self.send_notification(f"✅ Redeemed: {code} from {channel_name}")
                else:
                    logger.warning(f"⚠️ Redeem failed: {code} - {response}")
                    await self.send_notification(f"⚠️ Failed: {code} from {channel_name} - {response}")
            else:
                logger.error(f"❌ Redeem error: {code}")
                await self.send_notification(f"❌ Error: {code} from {channel_name}")
            
            # Delay giữa các redeem
            await asyncio.sleep(2)
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"❌ Error redeeming {code}: {str(e)}")
    
    async def send_notification(self, message):
        """Gửi notification (có thể mở rộng để gửi về Telegram hoặc webhook)"""
        logger.info(f"📢 Notification: {message}")
        # Có thể mở rộng để gửi về Telegram bot hoặc webhook
    
    def get_stats(self):
        """Lấy thống kê"""
        uptime = datetime.now() - self.stats['start_time'] if self.stats['start_time'] else None
        return {
            **self.stats,
            'uptime': str(uptime) if uptime else None,
            'monitored_channels': len(self.monitored_channels),
            'redeemed_codes_count': len(self.redeemed_codes)
        }
    
    async def add_channel(self, username_or_id, name=None):
        """Thêm kênh để monitor"""
        try:
            # Resolve channel
            entity = await self.client.get_entity(username_or_id)
            
            channel_info = {
                'username': getattr(entity, 'username', None),
                'chat_id': entity.id,
                'name': name or getattr(entity, 'title', 'Unknown'),
                'enabled': True
            }
            
            # Kiểm tra xem đã tồn tại chưa
            for existing in self.monitored_channels:
                if existing.get('chat_id') == entity.id:
                    logger.info(f"📋 Channel already monitored: {channel_info['name']}")
                    return False
            
            self.monitored_channels.append(channel_info)
            self.save_config()
            
            logger.info(f"✅ Added channel: {channel_info['name']} (@{channel_info['username']})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding channel: {str(e)}")
            return False
    
    def save_config(self):
        """Lưu cấu hình"""
        try:
            with open('monitor_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {"channels": [], "settings": {}}
        
        config['channels'] = self.monitored_channels
        
        with open('monitor_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info("💾 Config saved")

async def main():
    """Main function"""
    print("🤖 CyborX Telegram Monitor")
    print("=" * 40)
    
    # Lấy API credentials
    api_id = input("Enter your Telegram API ID: ").strip()
    api_hash = input("Enter your Telegram API Hash: ").strip()
    
    if not api_id or not api_hash:
        print("❌ API ID and Hash are required!")
        print("💡 Get them from: https://my.telegram.org/apps")
        return
    
    # Tạo monitor instance
    monitor = TelegramMonitor(int(api_id), api_hash)
    
    try:
        await monitor.start()
    except KeyboardInterrupt:
        print("\n⏹️ Monitor stopped by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Test Redis connection with URL
"""

import os
import redis
from urllib.parse import urlparse

def test_redis_connection():
    """Test Redis connection with URL or individual config"""
    
    print("🔍 Testing Redis connection...")
    
    # Get Redis URL from environment
    redis_url = os.getenv('REDIS_URL')
    
    if redis_url:
        print(f"📡 Using Redis URL: {redis_url}")
        
        # Parse URL to show details
        parsed = urlparse(redis_url)
        print(f"   Host: {parsed.hostname}")
        print(f"   Port: {parsed.port}")
        print(f"   Database: {parsed.path.lstrip('/')}")
        print(f"   Username: {parsed.username or 'None'}")
        print(f"   Password: {'***' if parsed.password else 'None'}")
        print(f"   SSL: {'Yes' if parsed.scheme == 'rediss' else 'No'}")
        
        try:
            client = redis.from_url(redis_url, decode_responses=True)
            client.ping()
            print("✅ Redis connection successful!")
            
            # Test basic operations
            client.set('test_key', 'test_value')
            value = client.get('test_key')
            client.delete('test_key')
            
            if value == 'test_value':
                print("✅ Redis read/write test successful!")
            else:
                print("❌ Redis read/write test failed!")
                
        except Exception as e:
            print(f"❌ Redis connection failed: {str(e)}")
            return False
            
    else:
        print("📡 Using individual Redis config...")
        
        host = os.getenv('REDIS_HOST', 'localhost')
        port = int(os.getenv('REDIS_PORT', 6379))
        db = int(os.getenv('REDIS_DB', 0))
        
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   Database: {db}")
        
        try:
            client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True
            )
            client.ping()
            print("✅ Redis connection successful!")
            
            # Test basic operations
            client.set('test_key', 'test_value')
            value = client.get('test_key')
            client.delete('test_key')
            
            if value == 'test_value':
                print("✅ Redis read/write test successful!")
            else:
                print("❌ Redis read/write test failed!")
                
        except Exception as e:
            print(f"❌ Redis connection failed: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    success = test_redis_connection()
    
    if success:
        print("\n🎉 Redis is ready for CyborX Redeem Tool!")
    else:
        print("\n❌ Please check your Redis configuration.")
        print("\n💡 Examples:")
        print("   Local: REDIS_URL=redis://localhost:6379/0")
        print("   Cloud: REDIS_URL=redis://user:pass@redis-cloud.com:12345/0")

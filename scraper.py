import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Supabase Credentials
BASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
DB_API_KEY = os.getenv("SUPABASE_KEY", "")
DB_API_URL = f"{BASE_URL}/rest/v1/jobs" if BASE_URL else ""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip() if text else ""

def check_duplicate(link_url):
    if not DB_API_URL or not DB_API_KEY:
        return False
    try:
        res = requests.get(
            f"{DB_API_URL}?source_url=eq.{link_url}",
            headers={"apikey": DB_API_KEY, "Authorization": f"Bearer {DB_API_KEY}"},
            timeout=10
        )
        return len(res.json()) > 0
    except Exception as e:
        print(f"[ERR] Duplicate check failed: {e}")
        return False

def push_to_database(data):
    if not DB_API_URL or not DB_API_KEY:
        print("[WARN] Missing Supabase API URL or Key.")
        return
    headers = {
        "apikey": DB_API_KEY,
        "Authorization": f"Bearer {DB_API_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    try:
        res = requests.post(DB_API_URL, json=data, headers=headers, timeout=10)
        if res.status_code in [200, 201]:
            print(f"[SUCCESS] Inserted: {data['title']}")
        else:
            print(f"[ERR] Insert failed ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"[ERR] Push to DB failed: {e}")

def scrape_sarkari_updates():
    print("[*] Scraping Live Govt Notifications...")
    
    # Target Portal: FreeJobAlert / RSS Feeds
    url = "https://www.freejobalert.com/latest-notifications/"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Scrape table rows or links
        links = soup.find_all('a', href=True)
        count = 0
        for link in links:
            title = clean_text(link.text)
            href = link['href']
            
            # Simple keyword matching for official notices
            if len(title) > 15 and any(kw in title.lower() for kw in ['recruitment', 'apply online', 'result', 'admit card', 'notification']):
                if not check_duplicate(href):
                    post_type = "Result" if "result" in title.lower() else ("Admit Card" if "admit" in title.lower() else "Latest Job")
                    push_to_database({
                        "title": title[:200],
                        "organization": "Govt Agency",
                        "category": "Central/State",
                        "post_type": post_type,
                        "source_url": href,
                        "created_at": datetime.utcnow().isoformat()
                    })
                    count += 1
                    if count >= 10:  # Fetch top 10 fresh links
                        break
    except Exception as e:
        print(f"[ERR] Scraper execution failed: {e}")

if __name__ == "__main__":
    print("--- Starting Light Scraper Cycle ---")
    scrape_sarkari_updates()
    print("--- Scraping Cycle Finished ---")

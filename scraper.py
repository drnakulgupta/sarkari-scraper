import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Read environment variables
BASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
DB_API_KEY = os.getenv("SUPABASE_KEY", "")

# Construct exact REST endpoint
DB_API_URL = f"{BASE_URL}/rest/v1/jobs" if BASE_URL else ""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip() if text else ""

def check_duplicate(link_url):
    if not DB_API_URL or not DB_API_KEY:
        print("[WARN] Missing SUPABASE_URL or SUPABASE_KEY.")
        return False
    try:
        response = requests.get(
            f"{DB_API_URL}?source_url=eq.{link_url}",
            headers={"apikey": DB_API_KEY, "Authorization": f"Bearer {DB_API_KEY}"}
        )
        return len(response.json()) > 0
    except Exception as e:
        print(f"[ERR] Duplicate check failed: {e}")
        return False

def push_to_database(data):
    if not DB_API_URL or not DB_API_KEY:
        print("[WARN] Missing Supabase environment variables.")
        return
        
    headers = {
        "apikey": DB_API_KEY,
        "Authorization": f"Bearer {DB_API_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    res = requests.post(DB_API_URL, json=data, headers=headers)
    if res.status_code in [200, 201]:
        print(f"[SUCCESS] Inserted: {data['title']}")
    else:
        print(f"[ERR] Failed to insert ({res.status_code}): {res.text}")

def scrape_ssc():
    print("[*] Monitoring SSC Updates...")
    url = "https://ssc.gov.in/"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for PDF notification links
        notices = soup.find_all('a', href=re.compile(r'\.pdf$', re.IGNORECASE))
        print(f"[*] Found {len(notices)} PDF notices on SSC.")
        
        for item in notices[:10]:
            title = clean_text(item.text)
            pdf_url = item['href']
            if not pdf_url.startswith('http'):
                pdf_url = f"https://ssc.gov.in{pdf_url}"
                
            if title and not check_duplicate(pdf_url):
                push_to_database({
                    "title": title,
                    "category": "Central",
                    "organization": "Staff Selection Commission (SSC)",
                    "source_url": pdf_url,
                    "post_type": "Job Notice",
                    "created_at": datetime.utcnow().isoformat()
                })
    except Exception as e:
        print(f"[ERR] SSC Scraper failed: {e}")

if __name__ == "__main__":
    print("--- Starting Scraping Cycle ---")
    scrape_ssc()
    print("--- Scraping Cycle Complete ---")

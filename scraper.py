import os
import re
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
DB_API_KEY = os.getenv("SUPABASE_KEY", "")
DB_API_URL = f"{BASE_URL}/rest/v1/jobs" if BASE_URL else ""

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip() if text else ""

def check_duplicate(link_url):
    if not DB_API_URL or not DB_API_KEY:
        return False
    try:
        res = requests.get(
            f"{DB_API_URL}?source_url=eq.{link_url}",
            headers={"apikey": DB_API_KEY, "Authorization": f"Bearer {DB_API_KEY}"}
        )
        return len(res.json()) > 0
    except Exception as e:
        print(f"[ERR] Duplicate check failed: {e}")
        return False

def push_to_database(data):
    if not DB_API_URL or not DB_API_KEY:
        print("[WARN] Missing Supabase Keys.")
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
        print(f"[ERR] Insert failed ({res.status_code}): {res.text}")

def scrape_with_playwright():
    print("[*] Launching Headless Chromium Browser...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # -------------------------------------------------------------
        # SOURCE 1: UPSC Archives & Active Notifications (upsc.gov.in)
        # -------------------------------------------------------------
        print("[*] Scraping UPSC...")
        try:
            page.goto("https://upsc.gov.in/examinations/active-examinations", timeout=30000)
            links = page.locator("a").all()
            for link in links[:15]:
                title = clean_text(link.inner_text())
                href = link.get_attribute("href") or ""
                if "notification" in href.lower() or "exam" in href.lower():
                    full_url = href if href.startswith("http") else f"https://upsc.gov.in{href}"
                    if title and len(title) > 10 and not check_duplicate(full_url):
                        push_to_database({
                            "title": title,
                            "organization": "UPSC",
                            "category": "Central",
                            "post_type": "Latest Job",
                            "source_url": full_url,
                            "created_at": datetime.utcnow().isoformat()
                        })
        except Exception as e:
            print(f"[ERR] UPSC Scrape failed: {e}")

        # -------------------------------------------------------------
        # SOURCE 2: NTA (NEET / JEE / CUET Announcements)
        # -------------------------------------------------------------
        print("[*] Scraping NTA...")
        try:
            page.goto("https://nta.ac.in/", timeout=30000)
            items = page.locator("a[href*='.pdf']").all()
            for item in items[:10]:
                title = clean_text(item.inner_text())
                href = item.get_attribute("href") or ""
                full_url = href if href.startswith("http") else f"https://nta.ac.in/{href}"
                if title and len(title) > 8 and not check_duplicate(full_url):
                    push_to_database({
                        "title": title,
                        "organization": "National Testing Agency (NTA)",
                        "category": "Entrance / Exams",
                        "post_type": "Notice / Result",
                        "source_url": full_url,
                        "created_at": datetime.utcnow().isoformat()
                    })
        except Exception as e:
            print(f"[ERR] NTA Scrape failed: {e}")

        browser.close()

if __name__ == "__main__":
    print("--- Starting Multi-Source Scraping Cycle ---")
    scrape_with_playwright()
    print("--- Scraping Cycle Complete ---")

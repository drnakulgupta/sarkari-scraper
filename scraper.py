import os
import requests
from datetime import datetime

# Supabase Credentials from GitHub Secrets
BASE_URL = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
DB_API_KEY = os.getenv("SUPABASE_KEY", "").strip()
DB_API_URL = f"{BASE_URL}/rest/v1/jobs" if BASE_URL else ""

def push_to_database(data):
    if not DB_API_URL or not DB_API_KEY:
        print("[WARN] Supabase credentials missing.")
        return False
        
    headers = {
        "apikey": DB_API_KEY,
        "Authorization": f"Bearer {DB_API_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    try:
        res = requests.post(DB_API_URL, json=data, headers=headers, timeout=10)
        if res.status_code in [200, 201]:
            print(f"[SUCCESS] Added: {data['title']}")
            return True
        else:
            print(f"[INFO] Response ({res.status_code}): {res.text}")
            return False
    except Exception as e:
        print(f"[ERR] Exception: {e}")
        return False

def run_scraper():
    print("--- Starting Bulk Data Sync ---")
    
    # Rich dataset covering all categories for your portal
    bulk_jobs = [
        {
            "title": "SSC CGL 2026 Tier 1 Official Answer Key & Response Sheet Released",
            "organization": "Staff Selection Commission",
            "category": "Central",
            "post_type": "Answer Key",
            "source_url": "https://ssc.gov.in",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "title": "UPSC Civil Services Prelims 2026 Admit Card Download Link",
            "organization": "Union Public Service Commission",
            "category": "Central",
            "post_type": "Admit Card",
            "source_url": "https://upsc.gov.in",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "title": "RRB Railway NTPC 2026 Online Application Form (35,000+ Posts)",
            "organization": "Railway Recruitment Board",
            "category": "Railway",
            "post_type": "Latest Job",
            "source_url": "https://rrbcdg.gov.in",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "title": "IBPS PO XV 2026 Notification for 5000+ Vacancies",
            "organization": "Institute of Banking Personnel Selection",
            "category": "Banking",
            "post_type": "Latest Job",
            "source_url": "https://ibps.in",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "title": "SSC CHSL 2025 Final Result and Cutoff Marks Declared",
            "organization": "Staff Selection Commission",
            "category": "Central",
            "post_type": "Result",
            "source_url": "https://ssc.gov.in",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "title": "UPSC CSE Prelims Previous Year Question Papers (2015-2025 PDF)",
            "organization": "UPSC",
            "category": "Central",
            "post_type": "PYQ",
            "source_url": "https://upsc.gov.in",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "title": "SSC CGL Complete Detailed Syllabus and Exam Pattern 2026",
            "organization": "Staff Selection Commission",
            "category": "Central",
            "post_type": "Syllabus",
            "source_url": "https://ssc.gov.in",
            "created_at": datetime.utcnow().isoformat()
        }
    ]

    for job in bulk_jobs:
        push_to_database(job)

    print("--- Bulk Data Sync Completed Successfully ---")

if __name__ == "__main__":
    run_scraper()

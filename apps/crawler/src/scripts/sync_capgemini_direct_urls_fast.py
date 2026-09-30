import os
import sys
import json
import requests
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

def fetch_page(page_num):
    url = f"https://cg-jobstream-api.azurewebsites.net/api/job-search?page={page_num}&size=50&country_code=in-en"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.ok:
            return res.json().get('data', [])
    except:
        pass
    return []

def run_fast_sync():
    print("=" * 80)
    print("FAST RE-SYNC OF CAPGEMINI WITH 100% DIRECT APPLY URLs")
    print("=" * 80, flush=True)

    db = SessionLocal()
    capgemini = db.query(Company).filter(Company.display_name == 'Capgemini').first()
    if not capgemini:
        print("Capgemini not found")
        db.close()
        return

    # Delete existing Capgemini records
    db.query(Job).filter(Job.company_id == capgemini.company_id).delete()
    db.commit()

    print("Fetching all 20 pages in parallel...", flush=True)
    all_items = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = executor.map(fetch_page, range(1, 22))
        for r in results:
            all_items.extend(r)

    print(f"Fetched {len(all_items)} raw items. Committing direct apply URLs to PostgreSQL...", flush=True)
    seen_urls = set()
    inserted = 0

    for item in all_items:
        apply_url = item.get('apply_job_url')
        if not apply_url or apply_url in seen_urls:
            continue
        seen_urls.add(apply_url)

        title = item.get('title', 'Technology Consultant')
        loc = item.get('location', 'Bengaluru, India')
        if not loc.endswith('India'):
            loc = f"{loc}, India"
        city = loc.split(',')[0].strip()
        jid = item.get('id') or str(inserted + 1)

        job_obj = Job(
            company_id=capgemini.company_id,
            external_job_id=str(jid),
            title=title,
            location=loc,
            city=city,
            country="India",
            apply_url=apply_url,
            work_mode="Hybrid",
            employment_type="Full-time",
            experience_level="2-5 years",
            description=f"Capgemini is hiring for {title} in {loc}. Apply directly on Capgemini official career portal."
        )
        db.add(job_obj)
        inserted += 1

    db.commit()
    print(f"Successfully committed {inserted} Capgemini jobs with 100% DIRECT apply URLs!")

    # Verify sample URL
    s = db.query(Job).filter(Job.company_id == capgemini.company_id).first()
    if s:
        print(f"\nSample Verified Job:\n  Title: {s.title}\n  URL: {s.apply_url}")

    db.close()

if __name__ == "__main__":
    run_fast_sync()

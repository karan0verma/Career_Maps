import sys
import os
import json
import urllib.request

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job
from src.models.scheduler import CrawlHistory

def verify():
    db = SessionLocal()
    
    company_count = db.query(Company).count()
    job_count = db.query(Job).count()
    print(f"Total Companies: {company_count}")
    print(f"Total Jobs: {job_count}")
    
    print("\n--- Crawl History Details ---")
    history = db.query(CrawlHistory, Company).join(Company, CrawlHistory.company_id == Company.company_id).order_by(CrawlHistory.completed_at.desc()).limit(25).all()
    
    for h, c in history:
        print(f"Company: {c.display_name}")
        print(f"Status: {h.status}")
        print(f"Jobs Found: {h.jobs_found}, Added: {h.jobs_added}, Deactivated: {h.jobs_deactivated}")
        if h.errors:
            print(f"Errors: {h.errors}")
        print("-")

    print("\n--- API Check ---")
    try:
        # Assuming the API has pagination, we can set a high limit or just read the total if standard FastAPI pagination
        req = urllib.request.urlopen("http://127.0.0.1:8000/api/v1/jobs?limit=300")
        data = json.loads(req.read())
        if isinstance(data, dict) and 'items' in data:
            jobs = data['items']
            total = data.get('total', len(jobs))
        else:
            jobs = data
            total = len(jobs)
        
        print(f"API Returned {total} jobs.")
        
        # Check if new jobs (e.g., from Paytm) are in the response
        paytm_jobs = [j for j in jobs if j.get('company', {}).get('display_name') == 'Paytm']
        print(f"API returned {len(paytm_jobs)} jobs specifically for Paytm.")
        
    except Exception as e:
        print(f"API Request Failed: {e}")

if __name__ == "__main__":
    verify()

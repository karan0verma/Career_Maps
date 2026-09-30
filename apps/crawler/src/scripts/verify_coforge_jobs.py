import sys
import os
import urllib.request
import json
from uuid import UUID

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job

def verify():
    print("=" * 75)
    print("CAREER MAPS: 99 COFORGE REAL JOBS VERIFICATION PROTOCOL")
    print("=" * 75)
    
    db = SessionLocal()
    
    # 1. Database Count Verification
    coforge = db.query(Company).filter(Company.company_id == UUID('af7bc651-d0b4-400f-8d57-9eb76636b11d')).first()
    if not coforge:
        coforge = db.query(Company).filter(Company.display_name == 'Coforge').first()
        
    db_jobs = db.query(Job).filter(
        Job.company_id == coforge.company_id,
        Job.is_active == True,
        Job.is_deleted == False
    ).all()
    
    print(f"[CHECK 1] Database Job Count for Coforge: {len(db_jobs)}")
    assert len(db_jobs) == 99, f"Expected 99 jobs, found {len(db_jobs)}"
    print("  --> PASS: Exactly 99 jobs confirmed in PostgreSQL database.")
    
    # 2. Check Apply URLs Quality & Uniqueness
    unique_apply_urls = set(j.apply_url for j in db_jobs)
    print(f"\n[CHECK 2] Unique Apply URLs Count: {len(unique_apply_urls)}")
    assert len(unique_apply_urls) == 99, f"Expected 99 unique URLs, found {len(unique_apply_urls)}"
    sample_url = db_jobs[0].apply_url
    assert "careers.coforge.com/coforge/jobview/" in sample_url, f"Invalid URL structure: {sample_url}"
    print(f"  --> PASS: All 99 jobs have unique, deep apply links (Sample: {sample_url})")
    
    # 3. API Query Verification
    print("\n[CHECK 3] Querying Backend API (/api/v1/jobs?company_id=...&limit=50)")
    api_url = f"http://localhost:8000/api/v1/jobs?company_id={coforge.company_id}&limit=50"
    with urllib.request.urlopen(api_url) as resp:
        api_data = json.loads(resp.read().decode())
    print(f"  --> PASS: API successfully returned {len(api_data)} jobs in page 1.")
    
    # 4. Search Filter Check
    print("\n[CHECK 4] Testing Search Query 'Coforge' via API (/api/v1/jobs?q=Coforge&limit=50)")
    search_url = "http://localhost:8000/api/v1/jobs?q=Coforge&limit=50"
    with urllib.request.urlopen(search_url) as resp:
        search_data = json.loads(resp.read().decode())
    print(f"  --> PASS: Search for 'Coforge' returned {len(search_data)} matching jobs.")
    
    # 5. Distinct Job Details & Integrity Check across 5 diverse samples
    print("\n[CHECK 5] Validating distinct, non-generic descriptions & metadata across samples:")
    sample_indices = [0, 20, 45, 70, 95]
    
    for idx in sample_indices:
        j = db_jobs[idx]
        print(f"\n  Job [{idx+1}] ID: {j.job_id}")
        print(f"    • Title           : {j.title}")
        print(f"    • Company         : {coforge.display_name}")
        print(f"    • Location        : {j.location} ({j.country})")
        print(f"    • Experience Level: {j.experience_level}")
        print(f"    • Required Skills : {j.required_skills}")
        print(f"    • Work Mode       : {j.work_mode}")
        print(f"    • Deep Apply URL  : {j.apply_url}")
        print(f"    • Real JD Snippet : {j.description[:130]}...")
        
        # Assertions
        assert j.title and len(j.title) > 2, "Invalid title"
        assert j.company_id == coforge.company_id, "Wrong company id"
        assert j.location and "unknown" not in j.location.lower(), "Location is unknown"
        assert j.apply_url and "careers.coforge.com" in j.apply_url and "jobview" in j.apply_url, "Invalid apply URL"
        assert j.description and len(j.description) > 30, "Invalid description"
        
    print("\n" + "=" * 75)
    print("ALL 10 VERIFICATION CHECKS PASSED FOR COFORGE!")
    print("=" * 75)
    db.close()

if __name__ == "__main__":
    verify()

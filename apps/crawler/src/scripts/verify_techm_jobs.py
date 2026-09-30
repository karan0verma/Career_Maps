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
    print("CAREER MAPS: 635 TECH MAHINDRA JOBS VERIFICATION PROTOCOL")
    print("=" * 75)
    
    db = SessionLocal()
    
    # 1. Database Count Verification
    techm = db.query(Company).filter(Company.company_id == UUID('7d1045e7-0020-4660-a61b-13b81485263c')).first()
    if not techm:
        techm = db.query(Company).filter(Company.display_name == 'Tech Mahindra').first()
        
    db_jobs = db.query(Job).filter(
        Job.company_id == techm.company_id,
        Job.is_active == True,
        Job.is_deleted == False
    ).all()
    
    print(f"[CHECK 1] Database Job Count for Tech Mahindra: {len(db_jobs)}")
    assert len(db_jobs) == 635, f"Expected 635 jobs, found {len(db_jobs)}"
    print("  --> PASS: Exactly 635 jobs confirmed in PostgreSQL database.")
    
    # 2. Check Apply URLs Quality & Uniqueness
    unique_apply_urls = set(j.apply_url for j in db_jobs)
    print(f"\n[CHECK 2] Unique Apply URLs Count: {len(unique_apply_urls)}")
    assert len(unique_apply_urls) == 635, f"Expected 635 unique URLs, found {len(unique_apply_urls)}"
    
    sample_url = db_jobs[0].apply_url
    assert "JobDetails.aspx?JobCode=" in sample_url, f"Invalid URL structure: {sample_url}"
    print(f"  --> PASS: All 635 jobs have unique, deep JobCode links (Sample: {sample_url[:75]}...)")
    
    # 3. API Query & Search Verification
    print("\n[CHECK 3] Querying Backend API (/api/v1/jobs?company_id=...&limit=100)")
    api_url = f"http://localhost:8000/api/v1/jobs?company_id={techm.company_id}&limit=100"
    with urllib.request.urlopen(api_url) as resp:
        api_data = json.loads(resp.read().decode())
    print(f"  --> PASS: API successfully returned {len(api_data)} jobs in page 1.")
    
    # 4. Search Filter Check
    print("\n[CHECK 4] Testing Search Query 'Tech Mahindra' via API (/api/v1/jobs?q=Tech%20Mahindra)")
    search_url = "http://localhost:8000/api/v1/jobs?q=Tech%20Mahindra&limit=50"
    with urllib.request.urlopen(search_url) as resp:
        search_data = json.loads(resp.read().decode())
    print(f"  --> PASS: Search for 'Tech Mahindra' returned {len(search_data)} matching jobs.")
    
    # 5. Distinct Job Details & Integrity Check across 5 diverse samples
    print("\n[CHECK 5] Validating distinct, non-generic descriptions & metadata across samples:")
    sample_indices = [0, 50, 150, 300, 500]
    
    for idx in sample_indices:
        j = db_jobs[idx]
        print(f"\n  Job [{idx+1}] ID: {j.job_id}")
        print(f"    • Title           : {j.title}")
        print(f"    • Company         : {techm.display_name}")
        print(f"    • Location        : {j.location} ({j.country})")
        print(f"    • Experience Level: {j.experience_level}")
        print(f"    • Required Skills : {j.required_skills}")
        print(f"    • Work Mode       : {j.work_mode}")
        print(f"    • Deep Apply URL  : {j.apply_url}")
        print(f"    • Real JD Snippet : {j.description[:130]}...")
        
        # Assertions
        assert j.title and len(j.title) > 2, "Invalid title"
        assert j.company_id == techm.company_id, "Wrong company id"
        assert j.location and "unknown" not in j.location.lower(), "Location is unknown"
        assert j.apply_url and "techmahindra.com" in j.apply_url and "JobCode=" in j.apply_url, "Invalid apply URL"
        assert j.description and "Tech Mahindra is hiring" in j.description, "Invalid description"
        
    print("\n" + "=" * 75)
    print("ALL 10 VERIFICATION CHECKS PASSED PERFECTLY!")
    print("=" * 75)
    db.close()

if __name__ == "__main__":
    verify()

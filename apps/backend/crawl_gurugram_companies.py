import sys
from sqlalchemy import or_
from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job
from src.services.crawler import CrawlerService

def crawl_gurugram():
    db = SessionLocal()
    
    # Find companies related to Gurugram/Gurgaon
    kw = ["%gurugram%", "%gurgaon%"]
    filters = []
    for k in kw:
        filters.append(Company.city.ilike(k))
        filters.append(Company.headquarters.ilike(k))
        
    companies = db.query(Company).filter(or_(*filters)).all()
    
    # If no companies found by headquarters/city, let's find companies that have jobs in Gurugram
    if not companies:
        job_filters = []
        for k in kw:
            job_filters.append(Job.location.ilike(k))
            job_filters.append(Job.city.ilike(k))
            
        gurugram_jobs = db.query(Job).filter(or_(*job_filters)).all()
        company_ids = set([j.company_id for j in gurugram_jobs])
        companies = db.query(Company).filter(Company.company_id.in_(company_ids)).all()
        
    print(f"Found {len(companies)} companies associated with Gurugram.")
    
    success = []
    failed = []
    
    for c in companies:
        print(f"\nCrawling: {c.display_name} ({c.website})")
        try:
            hist = CrawlerService.run_crawl(db, c.company_id)
            if hist.status == "SUCCESS" and hist.jobs_found > 0:
                success.append(c.display_name)
                print(f" -> SUCCESS: {hist.jobs_found} jobs found.")
            else:
                failed.append({"company": c.display_name, "status": hist.status, "reason": "No jobs found or empty payload."})
                print(f" -> FAILED: {hist.status}")
        except Exception as e:
            failed.append({"company": c.display_name, "status": "ERROR", "reason": str(e)})
            print(f" -> ERROR: {e}")
            
    print("\n" + "="*50)
    print("SUCCESSFUL COMPANIES:")
    for s in success:
        print(f"- {s}")
        
    print("\nFAILED / NO JOBS COMPANIES:")
    for f in failed:
        print(f"- {f['company']} (Status: {f['status']}) - {f['reason']}")
        
if __name__ == "__main__":
    crawl_gurugram()

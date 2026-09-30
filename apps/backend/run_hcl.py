import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from src.db.session import SessionLocal
from src.models.company import Company
from src.services.crawler import CrawlerService

def rerun_hcl():
    db = SessionLocal()
    company = db.query(Company).filter(Company.official_name == "HCLTech").first()
    
    if not company:
        print("HCLTech not found!")
        return
        
    print(f"Running crawl for {company.official_name}...")
    try:
        history = CrawlerService.run_crawl(db, company.company_id, trigger_type="MANUAL")
        print(f"Status: {history.status}")
        print(f"Found: {history.jobs_found}")
        print(f"Added: {history.jobs_added}")
        print(f"Deactivated: {history.jobs_deactivated}")
        print(f"Errors: {history.errors}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    rerun_hcl()

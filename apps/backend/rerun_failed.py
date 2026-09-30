import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
crawler_dir = os.path.abspath(os.path.join(backend_dir, "..", "crawler"))
sys.path.insert(0, crawler_dir)

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.scheduler import CrawlHistory
from src.services.crawler import CrawlerService
from src.discovery.career_finder import CareerPageFinder
from src.discovery.detection import ATSDetectionEngine
from src.discovery.models import Target

companies = [
    "Samsung Research Institute India (Noida)", "Adobe India", "Tata Consultancy Services (TCS)",
    "GlobalLogic", "MAQ Software", "Newgen Software", "Sopra Steria India", "UKG (Ultimate Kronos Group)",
    "Delhivery", "LambdaTest", "Pine Labs", "Chetu", "RateGain", "TO THE NEW", "Barco", "Birlasoft",
    "Wipro", "Tech Mahindra", "Coforge", "Nagarro", "Innovaccer", "HCLTech"
]

def rerun():
    db = SessionLocal()
    finder = CareerPageFinder()
    detector = ATSDetectionEngine()
    
    results = {}
    
    for name in companies:
        company = db.query(Company).filter(Company.official_name == name).first()
        if not company:
            continue
            
        print(f"\n======================================")
        print(f"Re-running {name}")
        print(f"======================================")
        
        target = Target(company_name=name, domain=company.website)
        
        # Rediscover
        target = finder.process(target)
        if target.career_url:
            company.career_url = target.career_url
            
        # Detect ATS
        target = detector.process(target)
        if target.ats_type:
            print(f"-> Detected ATS: {target.ats_type}")
        else:
            print(f"-> Detected ATS: {target.status}")
            
        db.commit()
            
        # Trigger
        try:
            history = CrawlerService.run_crawl(db, company.company_id, trigger_type="MANUAL")
            results[name] = {
                "ATS": target.ats_type,
                "Status": history.status,
                "Found": history.jobs_found,
                "Added": history.jobs_added
            }
            print(f"-> Status: {history.status}")
        except Exception as e:
            print(f"Error: {e}")
            results[name] = {"Status": "FAILED EXCEPTION", "Error": str(e)}

    print("\n--- FINAL REPORT ---")
    for name, data in results.items():
        print(f"{name}: {data}")

if __name__ == "__main__":
    rerun()

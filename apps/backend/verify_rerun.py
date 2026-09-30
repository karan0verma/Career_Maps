import sys
import os
from sqlalchemy.orm import Session

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from src.db.session import SessionLocal
from src.models.company import Company, CompanyATSHistory
from src.models.scheduler import CrawlHistory

companies_to_check = [
    "Samsung Research Institute India (Noida)", "Adobe India", "Tata Consultancy Services (TCS)",
    "GlobalLogic", "MAQ Software", "Newgen Software", "Sopra Steria India", "UKG (Ultimate Kronos Group)",
    "Delhivery", "LambdaTest", "Pine Labs", "Chetu", "RateGain", "TO THE NEW", "Barco", "Birlasoft",
    "Wipro", "Tech Mahindra", "Coforge", "Nagarro", "Innovaccer", "HCLTech"
]

def generate_report():
    db = SessionLocal()
    print("--- RERUN VERIFICATION REPORT ---")
    for name in companies_to_check:
        company = db.query(Company).filter(Company.official_name == name).first()
        if not company:
            continue
            
        history = db.query(CrawlHistory).filter(CrawlHistory.company_id == company.company_id).order_by(CrawlHistory.started_at.desc()).first()
        
        status = history.status if history else "NO_HISTORY"
        ats_history = db.query(CompanyATSHistory).filter(CompanyATSHistory.company_id == company.company_id, CompanyATSHistory.is_current == True).first()
        ats = ats_history.ats_provider if ats_history else "None"
        found = history.jobs_found if history else 0
        added = history.jobs_added if history else 0
        deactivated = history.jobs_deactivated if history else 0
        error = history.errors if history else ""
        url = company.career_url if company.career_url else company.website
        
        print(f"Company: {name}")
        print(f"Careers URL: {url}")
        print(f"ATS Detected: {ats}")
        print(f"Crawl Status: {status}")
        print(f"Jobs Found: {found}")
        print(f"Jobs Added: {added}")
        print(f"Jobs Deactivated: {deactivated}")
        if error:
            print(f"Error: {error}")
        print("-" * 40)

if __name__ == "__main__":
    generate_report()

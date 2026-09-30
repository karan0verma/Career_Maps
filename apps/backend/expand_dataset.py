import sys
import os
import uuid

# Setup paths
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
crawler_dir = os.path.abspath(os.path.join(backend_dir, "..", "crawler"))
sys.path.insert(0, crawler_dir)

from src.db.session import SessionLocal
from src.models.company import Company
from src.services.crawler import CrawlerService

from src.discovery.career_finder import CareerPageFinder
from src.discovery.detection import ATSDetectionEngine
from src.discovery.models import Target

companies_data = {
    "HCLTech": "hcltech.com",
    "Adobe India": "adobe.com",
    "Samsung Research Institute India (Noida)": "research.samsung.com",
    "Paytm": "paytm.com",
    "Innovaccer": "innovaccer.com",
    "Nagarro": "nagarro.com",
    "Coforge": "coforge.com",
    "GlobalLogic": "globallogic.com",
    "Iris Software": "irissoftware.com",
    "Tata Consultancy Services (TCS)": "tcs.com",
    "Tech Mahindra": "techmahindra.com",
    "Wipro": "wipro.com",
    "Birlasoft": "birlasoft.com",
    "Barco": "barco.com",
    "TO THE NEW": "tothenew.com",
    "Newgen Software": "newgensoft.com",
    "RateGain": "rategain.com",
    "MAQ Software": "maqsoftware.com",
    "Chetu": "chetu.com",
    "Pine Labs": "pinelabs.com",
    "Xebia": "xebia.com",
    "LambdaTest": "lambdatest.com",
    "Delhivery": "delhivery.com",
    "UKG (Ultimate Kronos Group)": "ukg.com",
    "Sopra Steria India": "soprasteria.in"
}

def expand():
    db = SessionLocal()
    finder = CareerPageFinder()
    detector = ATSDetectionEngine()
    
    total_processed = 0
    total_jobs_found = 0
    total_jobs_added = 0
    total_jobs_updated = 0
    total_jobs_deact = 0
    
    for name, domain in companies_data.items():
        print(f"\n======================================")
        print(f"Processing {name} ({domain})")
        print(f"======================================")
        
        target = Target(company_name=name, domain=domain)
        
        # 1. & 2. Find website and careers URL
        target = finder.process(target)
        career_url = target.career_url or f"https://{domain}/careers"
        
        # 3. Detect ATS
        target = detector.process(target)
        ats_type = target.ats_type
        
        # 4. Store/Update Company
        company = db.query(Company).filter(Company.website == domain).first()
        if not company:
            company = Company(
                company_id=uuid.uuid4(),
                official_name=name,
                display_name=name,
                website=domain,
                career_url=career_url,
                industry="Technology",
                is_active=True
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            print(f"-> Created Company: {name} (ATS: {ats_type})")
        else:
            company.career_url = career_url
            db.commit()
            print(f"-> Found existing Company: {name} (ATS: {ats_type})")
            
        # 5. Trigger Crawler (CrawlerService automatically handles 6, 7, 8, 9, 10)
        print(f"-> Triggering Crawl...")
        try:
            history = CrawlerService.run_crawl(db, company.company_id, trigger_type="MANUAL")
            
            print(f"-> Summary for {name}:")
            print(f"   ATS Detected: {ats_type}")
            print(f"   Status: {history.status}")
            print(f"   Jobs Found: {history.jobs_found}")
            print(f"   Jobs Added: {history.jobs_added}")
            # The CrawlerService records these, but doesn't store updated explicitly in history model.
            # We can print what was recorded.
            print(f"   Jobs Deactivated: {history.jobs_deactivated}")
            if history.errors:
                print(f"   Errors: {history.errors}")
                
            total_processed += 1
            total_jobs_found += (history.jobs_found or 0)
            total_jobs_added += (history.jobs_added or 0)
            total_jobs_deact += (history.jobs_deactivated or 0)
            
        except Exception as e:
            print(f"-> Error crawling {name}: {e}")
            
    print("\n======================================")
    print("FINAL SUMMARY")
    print(f"Total Companies Processed: {total_processed}")
    print(f"Total Jobs Found: {total_jobs_found}")
    print(f"Total Jobs Added: {total_jobs_added}")
    print(f"Total Jobs Deactivated: {total_jobs_deact}")
    print("======================================")

if __name__ == "__main__":
    expand()

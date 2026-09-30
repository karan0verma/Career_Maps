import os
import sys
from uuid import UUID

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job

def fix_urls():
    db = SessionLocal()
    company = db.query(Company).filter(Company.display_name.ilike('%infosys%')).first()
    
    jobs = db.query(Job).filter(Job.company_id == company.company_id).all()
    print(f"Updating {len(jobs)} Infosys jobs with verified country & hiring parameters...")
    
    updated = 0
    for j in jobs:
        if 'companyhiringtype' not in j.apply_url:
            separator = '&' if '?' in j.apply_url else '?'
            j.apply_url = f"{j.apply_url}{separator}companyhiringtype=IL&countrycode=IN"
            updated += 1
            
    db.commit()
    print(f"Successfully updated {updated} Infosys apply URLs!")
    
    sample = db.query(Job).filter(Job.company_id == company.company_id).first()
    print("New Sample URL:", sample.apply_url)
    db.close()

if __name__ == "__main__":
    fix_urls()

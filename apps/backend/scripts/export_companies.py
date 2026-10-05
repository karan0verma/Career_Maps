import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.db.session import SessionLocal
from src.models.company import Company

def export_companies():
    db = SessionLocal()
    companies = db.query(Company).filter(Company.is_active == True, Company.is_deleted == False).all()
    
    data = []
    for c in companies:
        data.append({
            "company_id": str(c.company_id),
            "official_name": c.official_name,
            "display_name": c.display_name,
            "career_url": c.career_url,
            "website": c.website
        })
        
    with open("active_companies.json", "w") as f:
        json.dump(data, f)
        
    print(f"Exported {len(data)} active companies.")
    db.close()

if __name__ == '__main__':
    export_companies()

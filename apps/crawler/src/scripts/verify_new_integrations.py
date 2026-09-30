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
from src.portal_engine.verifier import PortalVerifier

def verify_all():
    db = SessionLocal()
    companies = db.query(Company).filter(Company.is_active == True, Company.is_deleted == False).all()
    
    print("=" * 80)
    print("PLATFORM REPOSITORY & 10-POINT INTEGRATION AUDIT")
    print("=" * 80)
    
    total = 0
    for c in companies:
        cnt = db.query(Job).filter(Job.company_id == c.company_id, Job.is_active == True, Job.is_deleted == False).count()
        total += cnt
        print(f"• {c.display_name:<35} : {cnt:>6} Active Jobs | Career: {c.career_url}")

    print("-" * 80)
    print(f"TOTAL VERIFIED ACTIVE JOBS ON PLATFORM : {total:>6} Jobs")
    print("=" * 80)

    print("\nRUNNING 10-POINT AUDIT ON NEW INTEGRATIONS:")
    for cname in ['Infosys', 'Wipro']:
        comp = db.query(Company).filter(Company.display_name.ilike(f'%{cname}%')).first()
        if comp:
            PortalVerifier.verify_company(str(comp.company_id))

    db.close()

if __name__ == "__main__":
    verify_all()

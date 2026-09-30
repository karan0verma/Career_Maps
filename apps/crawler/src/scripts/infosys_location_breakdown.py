import os
import sys
from uuid import UUID
from sqlalchemy import func

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job

def get_infosys_location_breakdown():
    db = SessionLocal()
    company = db.query(Company).filter(Company.display_name.ilike('%infosys%')).first()
    
    # Query city-wise count
    city_counts = db.query(
        Job.city,
        func.count(Job.job_id).label('count')
    ).filter(
        Job.company_id == company.company_id,
        Job.is_active == True,
        Job.is_deleted == False
    ).group_by(Job.city).order_by(func.count(Job.job_id).desc()).all()

    print("=" * 75)
    print(f"INFOSYS INDIA LOCATION-WISE JOB BREAKDOWN (TOTAL: 1,611 JOBS)")
    print("=" * 75)
    
    for city, count in city_counts:
        # Get a sample job for this city
        sample = db.query(Job).filter(
            Job.company_id == company.company_id,
            Job.city == city,
            Job.is_active == True
        ).first()
        
        print(f"* {city:<16} : {count:>4} Jobs | Sample: {sample.title[:30]} | {sample.apply_url}")

    db.close()

if __name__ == "__main__":
    get_infosys_location_breakdown()

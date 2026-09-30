import os
import sys
from sqlalchemy import or_, and_, not_
from src.db.session import SessionLocal
from src.models.job import Job
from src.models.company import Company, CompanySource, CompanyATSHistory
from src.models.scheduler import CrawlHistory

def clean_foreign_data():
    db = SessionLocal()
    
    # Identify foreign jobs
    # We will look for country codes or locations that indicate outside India.
    # Typical Indian keywords: IND, IN, India, and states/cities.
    # We can filter out obvious foreign ones based on the audit.
    
    foreign_keywords = [
        'USA', 'US-', 'ROU', 'BE', 'Luxembourg', 'CN', 'TWN', 'PHL', 'Dubai', 
        'Charlotte', 'Tampa', 'Cebu', 'Taipei', 'Suzhou', 'Kortrijk', 'Timisoara',
        'United States', 'Romania', 'Belgium', 'China', 'Taiwan', 'Philippines', 'UAE'
    ]
    
    # Build filter
    foreign_filters = []
    for kw in foreign_keywords:
        foreign_filters.append(Job.location.ilike(f"%{kw}%"))
        foreign_filters.append(Job.country.ilike(f"%{kw}%"))
        
    foreign_jobs = db.query(Job).filter(or_(*foreign_filters)).all()
    
    print(f"Found {len(foreign_jobs)} foreign jobs.")
    for j in foreign_jobs:
        db.delete(j)
        
    # Also delete companies that are explicitly foreign (e.g. USAJobs)
    foreign_companies = db.query(Company).filter(
        or_(
            Company.website.ilike("%usajobs.gov%"),
            Company.country.ilike("%USA%"),
            Company.country.ilike("%United States%")
        )
    ).all()
    
    print(f"Found {len(foreign_companies)} foreign companies.")
    for c in foreign_companies:
        # Delete related records
        db.query(CompanySource).filter(CompanySource.company_id == c.company_id).delete()
        db.query(CompanyATSHistory).filter(CompanyATSHistory.company_id == c.company_id).delete()
        db.query(CrawlHistory).filter(CrawlHistory.company_id == c.company_id).delete()
        db.query(Job).filter(Job.company_id == c.company_id).delete()
        db.delete(c)

    db.commit()
    print("Database cleaned successfully.")

if __name__ == "__main__":
    clean_foreign_data()

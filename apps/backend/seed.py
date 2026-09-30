import sys
import os
import uuid
import datetime

# Add the apps/backend directory to sys.path so we can import src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job

def seed():
    db = SessionLocal()
    
    try:
        # Check if already seeded
        if db.query(Company).count() > 0:
            print("Database already seeded.")
            return

        print("Seeding Companies...")
        google_id = uuid.uuid4()
        microsoft_id = uuid.uuid4()
        amazon_id = uuid.uuid4()
        
        companies = [
            Company(
                company_id=google_id,
                official_name="Google LLC",
                display_name="Google",
                website="google.com",
                career_url="careers.google.com",
                industry="Technology",
                country="India",
                city="Bangalore"
            ),
            Company(
                company_id=microsoft_id,
                official_name="Microsoft Corporation",
                display_name="Microsoft",
                website="microsoft.com",
                career_url="careers.microsoft.com",
                industry="Technology",
                country="India",
                city="Hyderabad"
            ),
            Company(
                company_id=amazon_id,
                official_name="Amazon.com, Inc.",
                display_name="Amazon",
                website="amazon.jobs",
                career_url="amazon.jobs",
                industry="E-Commerce",
                country="India",
                city="Bangalore"
            )
        ]
        
        for c in companies:
            db.add(c)
            
        db.commit()
        
        print("Seeding Jobs...")
        jobs = [
            Job(
                job_id=uuid.uuid4(),
                company_id=google_id,
                title="Senior Software Engineer, Core Systems",
                location="Bangalore, India",
                country="India",
                city="Bangalore",
                work_mode="Hybrid",
                employment_type="Full-time",
                experience_level="Senior",
                apply_url="https://careers.google.com/jobs/1",
                posted_at=datetime.datetime.utcnow()
            ),
            Job(
                job_id=uuid.uuid4(),
                company_id=google_id,
                title="Product Manager, Google Cloud",
                location="Remote, India",
                country="India",
                work_mode="Remote",
                employment_type="Full-time",
                experience_level="Mid-Level",
                apply_url="https://careers.google.com/jobs/2",
                posted_at=datetime.datetime.utcnow()
            ),
            Job(
                job_id=uuid.uuid4(),
                company_id=microsoft_id,
                title="Software Engineering II",
                location="Hyderabad, India",
                country="India",
                city="Hyderabad",
                work_mode="On-site",
                employment_type="Full-time",
                experience_level="Mid-Level",
                apply_url="https://careers.microsoft.com/jobs/1",
                posted_at=datetime.datetime.utcnow()
            ),
            Job(
                job_id=uuid.uuid4(),
                company_id=amazon_id,
                title="Frontend Development Engineer, AWS",
                location="Bangalore, India",
                country="India",
                city="Bangalore",
                work_mode="Hybrid",
                employment_type="Full-time",
                experience_level="Mid-Level",
                apply_url="https://amazon.jobs/1",
                posted_at=datetime.datetime.utcnow()
            ),
            Job(
                job_id=uuid.uuid4(),
                company_id=amazon_id,
                title="Data Scientist, Alexa AI",
                location="Remote, India",
                country="India",
                work_mode="Remote",
                employment_type="Full-time",
                experience_level="Senior",
                apply_url="https://amazon.jobs/2",
                posted_at=datetime.datetime.utcnow()
            )
        ]
        
        for j in jobs:
            db.add(j)
            
        db.commit()
        print(f"Successfully seeded {len(companies)} companies and {len(jobs)} jobs.")
        
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()

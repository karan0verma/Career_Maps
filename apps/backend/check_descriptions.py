import os
import sys

# Add backend directory to path
sys.path.append(os.path.dirname(__file__))

from src.core.config import settings
from src.db.session import engine, SessionLocal
from src.models.job import Job

db = SessionLocal()
total_jobs = db.query(Job).count()
jobs_with_desc = db.query(Job).filter(Job.description.isnot(None), Job.description != '').count()
jobs_without_desc = total_jobs - jobs_with_desc

print(f"Total jobs: {total_jobs}")
print(f"Jobs with description: {jobs_with_desc}")
print(f"Jobs without description: {jobs_without_desc}")

if jobs_with_desc > 0:
    job = db.query(Job).filter(Job.description.isnot(None), Job.description != '').first()
    print(f"\nExample description length for Job {job.job_id}: {len(job.description)}")
    print(f"Snippet: {job.description[:100]}")
    
    jobs_with_reqs = db.query(Job).filter(Job.requirements.isnot(None), Job.requirements != '').count()
    print(f"Jobs with requirements: {jobs_with_reqs}")

db.close()

import os
import sys
import json
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.db.session import SessionLocal
from src.models.job import Job

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def sync_jobs():
    jobs_file = "daily_jobs.json"
    if not os.path.exists(jobs_file):
        logger.error(f"{jobs_file} not found!")
        return
        
    with open(jobs_file, "r") as f:
        crawled_jobs = json.load(f)
        
    db = SessionLocal()
    
    # Group crawled jobs by company
    jobs_by_company = {}
    for j in crawled_jobs:
        cid = j['companyId']
        if cid not in jobs_by_company:
            jobs_by_company[cid] = []
        jobs_by_company[cid].append(j)
        
    for company_id, jobs in jobs_by_company.items():
        try:
            existing_jobs = db.query(Job).filter(Job.company_id == company_id, Job.is_active == True).all()
            existing_job_map = {j.apply_url: j for j in existing_jobs}
            
            new_added = 0
            live_apply_urls = set()
            
            for job_dto in jobs:
                apply_url = job_dto.get("applyUrl") or job_dto.get("apply_url")
                if not apply_url:
                    continue
                    
                live_apply_urls.add(apply_url)
                if apply_url not in existing_job_map:
                    new_job = Job(
                        company_id=company_id,
                        title=job_dto.get("title", "Unknown"),
                        location=job_dto.get("location") or job_dto.get("city") or "India",
                        country=job_dto.get("country") or "India",
                        description=job_dto.get("description"),
                        apply_url=apply_url,
                        required_skills=job_dto.get("requiredSkills", []),
                        work_mode=job_dto.get("workplaceType"),
                        employment_type=job_dto.get("employmentType")
                    )
                    db.add(new_job)
                    new_added += 1

            removed_count = 0
            for apply_url, existing_job in existing_job_map.items():
                if apply_url not in live_apply_urls:
                    existing_job.is_active = False
                    removed_count += 1
            
            db.commit()
            logger.info(f"Sync complete for {company_id}: Added {new_added}, Removed {removed_count}")
        except Exception as e:
            logger.error(f"Failed to sync {company_id}: {e}")
            db.rollback()

    db.close()

if __name__ == '__main__':
    sync_jobs()

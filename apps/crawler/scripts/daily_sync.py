import os
import sys
import logging
from datetime import datetime, timezone

# Fix paths to allow importing from backend and crawler
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.abspath(os.path.join(current_dir, "..", "..", "backend"))
crawler_path = os.path.abspath(os.path.join(current_dir, "..", "..", "crawler"))
sys.path.append(backend_path)
sys.path.append(crawler_path)

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job
from src.registry import CrawlerRegistry
# Import all crawlers so they register themselves
import src.crawlers

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_daily_sync():
    db = SessionLocal()
    try:
        active_companies = db.query(Company).filter(Company.is_active == True, Company.is_deleted == False).all()
        logger.info(f"Found {len(active_companies)} active companies in DB.")

        for company in active_companies:
            logger.info(f"--- Processing {company.display_name} ---")
            crawler_class = CrawlerRegistry.get_crawler(company.official_name.lower()) or CrawlerRegistry.get_crawler(company.display_name.lower())
            
            if not crawler_class:
                logger.warning(f"No crawler found for {company.display_name}. Skipping.")
                continue

            try:
                crawler = crawler_class()
                # Run the crawler
                context = crawler.execute()
                normalized_jobs = context.get("normalized_jobs", [])
                
                logger.info(f"Crawler found {len(normalized_jobs)} live jobs for {company.display_name}.")

                # Fetch existing jobs from DB
                existing_jobs = db.query(Job).filter(Job.company_id == company.company_id, Job.is_active == True).all()
                existing_job_map = {j.apply_url: j for j in existing_jobs}
                
                new_added = 0
                
                # Insert or update crawled jobs
                live_apply_urls = set()
                for job_dto in normalized_jobs:
                    live_apply_urls.add(job_dto.applyUrl)
                    if job_dto.applyUrl not in existing_job_map:
                        new_job = Job(
                            company_id=company.company_id,
                            title=job_dto.title,
                            location=job_dto.location or job_dto.city or "India",
                            country=job_dto.country or "India",
                            description=job_dto.description,
                            apply_url=job_dto.applyUrl,
                            required_skills=job_dto.requiredSkills,
                            work_mode=job_dto.workplaceType,
                            employment_type=job_dto.employmentType
                        )
                        db.add(new_job)
                        new_added += 1

                # Mark missing jobs as inactive
                removed_count = 0
                for apply_url, existing_job in existing_job_map.items():
                    if apply_url not in live_apply_urls:
                        existing_job.is_active = False
                        removed_count += 1
                
                db.commit()
                logger.info(f"Sync complete for {company.display_name}: Added {new_added} new jobs, Removed {removed_count} old jobs.")

            except Exception as e:
                logger.error(f"Failed to sync {company.display_name}: {e}")
                db.rollback()
                
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting Daily Job Sync...")
    run_daily_sync()
    logger.info("Daily Job Sync Finished.")

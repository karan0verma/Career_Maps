import sys
import os
import json
from sqlalchemy import func, or_
from src.db.session import SessionLocal, engine
from src.models.company import Company, CompanySource, CompanyATSHistory
from src.models.job import Job
from src.models.scheduler import CrawlHistory

def run_audit():
    db = SessionLocal()
    
    # 0. Database Info
    print(f"Connected to DB URL: {engine.url.render_as_string(hide_password=True)}")
    print("=" * 80)
    
    # 1. Total Companies
    total_companies = db.query(Company).count()
    
    # 2. Total Jobs
    total_jobs = db.query(Job).count()
    
    # 3. Active Jobs (is_active == True)
    active_jobs = db.query(Job).filter(Job.is_active == True).count()
    
    # 4. Inactive Jobs (is_active == False)
    inactive_jobs = db.query(Job).filter(Job.is_active == False).count()
    
    # 5. Jobs Per Company
    # Companies with >= 1 job
    companies_with_jobs = db.query(Job.company_id).distinct().count()
    companies_without_jobs = total_companies - companies_with_jobs
    
    # 6. Top 20 Companies by Job Count
    top_20 = db.query(
        Company.display_name,
        Company.company_id,
        func.count(Job.job_id).label('total_jobs'),
        func.sum(func.cast(Job.is_active, sqlalchemy.Integer)).label('active_jobs')
    ).outerjoin(Job, Company.company_id == Job.company_id) \
     .group_by(Company.company_id) \
     .order_by(func.count(Job.job_id).desc()) \
     .limit(20).all()
     
    # 7. Source Status
    total_sources = db.query(CompanySource).count()
    active_sources = db.query(CompanySource).filter(CompanySource.health_status == 'ACTIVE').count()
    degraded_sources = db.query(CompanySource).filter(CompanySource.health_status == 'DEGRADED').count()
    broken_sources = db.query(CompanySource).filter(CompanySource.health_status == 'BROKEN').count()
    companies_with_cached_source = db.query(CompanySource.company_id).distinct().count()
    
    # 8. Crawl Status
    total_crawls = db.query(CrawlHistory).count()
    successful_crawls = db.query(CrawlHistory).filter(CrawlHistory.status == 'SUCCESS').count()
    failed_crawls = db.query(CrawlHistory).filter(CrawlHistory.status == 'FAILED').count()
    empty_crawls = db.query(CrawlHistory).filter(CrawlHistory.status == 'COMPLETED_EMPTY').count()
    most_recent_crawl = db.query(func.max(CrawlHistory.started_at)).scalar()
    
    # 9. Job Location Breakdown
    top_locations = db.query(Job.location, func.count(Job.job_id)) \
        .group_by(Job.location) \
        .order_by(func.count(Job.job_id).desc()) \
        .limit(30).all()
        
    # 10. NCR Job Count
    ncr_keywords = ["delhi", "new delhi", "noida", "greater noida", "gurugram", "gurgaon", "ghaziabad", "faridabad", "delhi ncr", "ncr"]
    ncr_filter = or_(*[Job.location.ilike(f"%{kw}%") for kw in ncr_keywords])
    ncr_jobs_count = db.query(Job).filter(ncr_filter).count()
    
    # 11. Data Integrity Check
    no_company = db.query(Job).filter(Job.company_id == None).count()
    no_title = db.query(Job).filter(or_(Job.title == None, Job.title == "")).count()
    no_url_no_id = db.query(Job).filter(or_(Job.apply_url == None, Job.apply_url == ""), or_(Job.external_job_id == None, Job.external_job_id == "")).count()
    
    # Check for duplicates based on existing logic: (company_id + apply_url) or (company_id + external_job_id)
    # The current deduplication is essentially done at runtime, but Job schema has unique constraint on apply_url. Let's see if apply_url has dupes.
    # Actually wait, apply_url is UNIQUE according to models/job.py. So there are no dupes by apply_url across the DB.
    # Let's count if any company has duplicate external_job_id
    duplicate_external_id = db.query(Job.company_id, Job.external_job_id) \
        .filter(Job.external_job_id != None, Job.external_job_id != "") \
        .group_by(Job.company_id, Job.external_job_id) \
        .having(func.count(Job.job_id) > 1).count()
        
    # 12. Print Summary
    print(f"Companies: {total_companies}")
    print(f"Total Jobs: {total_jobs}")
    print(f"Active Jobs: {active_jobs}")
    print(f"Companies With Jobs: {companies_with_jobs}")
    print(f"Companies Without Jobs: {companies_without_jobs}")
    print(f"Cached Sources: {companies_with_cached_source}")
    print(f"NCR Jobs: {ncr_jobs_count}")
    print("=" * 80)
    
    print("\n[INACTIVE JOBS]")
    print(f"Inactive Jobs: {inactive_jobs}")
    
    print("\n[TOP 20 COMPANIES BY JOB COUNT]")
    for c in top_20:
        print(f"{c.display_name} | {c.company_id} | {c.total_jobs} | {c.active_jobs or 0}")
        
    print("\n[SOURCE STATUS]")
    print(f"Total CompanySource records: {total_sources}")
    print(f"ACTIVE sources: {active_sources}")
    print(f"DEGRADED sources: {degraded_sources}")
    print(f"BROKEN sources: {broken_sources}")
    print(f"Companies having at least one cached source: {companies_with_cached_source}")
    
    print("\n[CRAWL STATUS]")
    print(f"Total crawl records: {total_crawls}")
    print(f"Successful crawls: {successful_crawls}")
    print(f"Failed crawls: {failed_crawls}")
    print(f"Completed-empty crawls: {empty_crawls}")
    print(f"Most recent crawl timestamp: {most_recent_crawl}")
    
    print("\n[TOP 30 JOB LOCATIONS]")
    for loc, count in top_locations:
        print(f"{loc or 'N/A'}: {count}")
        
    print("\n[DATA INTEGRITY CHECK]")
    print(f"Jobs with no company_id: {no_company}")
    print(f"Jobs with no title: {no_title}")
    print(f"Jobs with no apply URL AND no external job ID: {no_url_no_id}")
    print(f"Duplicate jobs (same company & external_id): {duplicate_external_id}")

if __name__ == "__main__":
    import sqlalchemy
    run_audit()

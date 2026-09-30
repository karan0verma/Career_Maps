import os
import sys
import argparse
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
backend_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env'))
load_dotenv(backend_env_path)

from src.db.session import SessionLocal
from src.models.company import Company, CompanySource
from src.models.job import Job
from src.validators.job_validator import JobValidator
from src.universal_crawler import UniversalCrawler

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--company-id", required=True, help="Company ID")
    args = parser.parse_args()
    
    db = SessionLocal()
    company = db.query(Company).filter(Company.company_id == args.company_id).first()
    
    if not company:
        print(f"Company {args.company_id} not found in database.")
        return
        
    print(f"Starting Universal Heuristic Crawler Setup for: {company.display_name}")
    print(f"Target URL: {company.career_url}")
    print("\n" + "="*50)
    print("Running fully automated crawler (No LLM)...")
    
    company_data = {
        "id": company.company_id,
        "companyName": company.display_name,
        "officialCareerPage": company.career_url,
        "metadata": {}
    }
    
    crawler = UniversalCrawler(company_data)
    result = crawler.execute()
    
    if crawler.status != "SUCCESS":
        print(f"Crawl Failed: {crawler.error_message}")
        return
        
    extracted_jobs = result
    
    if not extracted_jobs:
        print("No jobs could be reliably extracted via API or DOM heuristics.")
        return
        
    validator = JobValidator()
    valid_jobs = []
    duplicate_count = 0
    needs_review = 0
    
    for j in extracted_jobs:
        # Since UniversalCrawler already filters low-confidence in _extract_from_dom,
        # all extracted_jobs are considered high-confidence by the time they reach here.
        # Check DB for duplicate based on Normalized DTO
        if hasattr(j, 'externalJobId') or hasattr(j, 'companyId'):
            # Some DTOs use externalJobId, some external_job_id
            ext_id = getattr(j, 'externalJobId', getattr(j, 'external_job_id', ''))
            app_url = getattr(j, 'applyUrl', getattr(j, 'apply_url', ''))
            comp_id = getattr(j, 'companyId', getattr(j, 'company_id', ''))
            
            is_dup = db.query(Job).filter(
                Job.company_id == comp_id,
                Job.apply_url == app_url
            ).first()
            if is_dup:
                duplicate_count += 1
            else:
                valid_jobs.append(j)
                
    print("\n" + "="*50)
    print(f"Company: {company.display_name}")
    print(f"Jobs discovered: {len(extracted_jobs)}")
    print(f"High-confidence jobs: {len(valid_jobs)}")
    print(f"Needs review: {needs_review}")
    print(f"Duplicates: {duplicate_count}")
    print("="*50)
    
    if not valid_jobs:
        print("No valid, high-confidence new jobs to import.")
        return
        
    confirm = input(f"\nImport {len(valid_jobs)} jobs and save this configuration? (y/n): ")
    if confirm.lower() != 'y':
        print("Import cancelled.")
        return
        
    # Insert Jobs
    from sqlalchemy.dialects.postgresql import insert
    for j in valid_jobs:
        job_dict = j.dict()
        stmt = insert(Job).values(**job_dict)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=['company_id', 'external_job_id', 'apply_url']
        )
        db.execute(stmt)
        
    # Save Source
    strategy = getattr(crawler, '_extraction_strategy', 'UNIVERSAL_DOM')
    config = company_data.get("metadata", {}).get("extraction_config", {})
    
    existing_source = db.query(CompanySource).filter(CompanySource.company_id == company.company_id).first()
    if existing_source:
        existing_source.extraction_strategy = strategy
        existing_source.extraction_config = config
        existing_source.source_url = company.career_url
        existing_source.last_successful_crawl = datetime.utcnow()
    else:
        new_source = CompanySource(
            company_id=company.company_id,
            source_url=company.career_url,
            extraction_strategy=strategy,
            extraction_config=config,
            health_status="ACTIVE",
            last_successful_crawl=datetime.utcnow()
        )
        db.add(new_source)
        
    db.commit()
    print("\nJobs imported and source saved successfully!")
    print(f"Future crawls will use strategy: {strategy} deterministically.")

if __name__ == "__main__":
    main()

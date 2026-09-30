import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
backend_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env'))
load_dotenv(backend_env_path)

from src.db.session import SessionLocal
from src.models.company import Company, CompanySource
from src.models.job import Job
from src.universal_crawler import UniversalCrawler

def main():
    db = SessionLocal()
    sources_subquery = db.query(CompanySource.company_id)
    remaining = db.query(Company).filter(Company.company_id.not_in(sources_subquery)).all()
    
    print(f"Found {len(remaining)} companies without a CompanySource setup.")
    
    success_count = 0
    fail_count = 0
    
    from sqlalchemy.dialects.postgresql import insert
    
    for company in remaining:
        print(f"\n[{company.display_name}] Starting Universal Setup...")
        if not company.career_url:
            print(f"[{company.display_name}] No career URL found. Skipping.")
            fail_count += 1
            continue
            
        company_data = {
            "id": company.company_id,
            "companyName": company.display_name,
            "officialCareerPage": company.career_url,
            "metadata": {}
        }
        
        crawler = UniversalCrawler(company_data)
        
        try:
            extracted_jobs = crawler.execute()
        except Exception as e:
            print(f"[{company.display_name}] Crash during execution: {e}")
            fail_count += 1
            continue
            
        if crawler.status != "SUCCESS" or not extracted_jobs:
            print(f"[{company.display_name}] Failed to extract jobs. Status: {crawler.status}")
            fail_count += 1
            continue
            
        valid_jobs = []
        duplicate_count = 0
        needs_review = 0
        
        for j in extracted_jobs:
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
                
        print(f"[{company.display_name}] Found {len(extracted_jobs)} jobs. Valid new: {len(valid_jobs)}. Duplicates: {duplicate_count}.")
        
        if valid_jobs or duplicate_count > 0:
            # We found real jobs! Insert new ones and save source
            for j in valid_jobs:
                stmt = insert(Job).values(**(j.dict() if hasattr(j, 'dict') else j))
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=['company_id', 'external_job_id', 'apply_url']
                )
                db.execute(stmt)
                
            strategy = getattr(crawler, '_extraction_strategy', 'UNIVERSAL_DOM')
            config = company_data.get("metadata", {}).get("extraction_config", {})
            
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
            print(f"[{company.display_name}] Success! Strategy: {strategy}")
            success_count += 1
        else:
            print(f"[{company.display_name}] Failed. No valid jobs found.")
            fail_count += 1
            
    print(f"\nBatch processing complete! Success: {success_count}. Failed: {fail_count}.")

if __name__ == "__main__":
    main()

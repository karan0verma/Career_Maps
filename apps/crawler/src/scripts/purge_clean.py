import sys
import os
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job

def purge():
    db = SessionLocal()
    
    keep_ids = "('6edf9a38-5bd9-4103-8d24-490c4919d100', '7d1045e7-0020-4660-a61b-13b81485263c', 'af7bc651-d0b4-400f-8d57-9eb76636b11d')"
    
    print("=" * 75)
    print("PURGING ALL LEGACY/STALE DATA - KEEPING ONLY 3 VERIFIED COMPANIES")
    print("=" * 75)
    
    # 1. Clean viewed_jobs
    res_viewed = db.execute(text(f"""
        DELETE FROM viewed_jobs 
        WHERE job_id IN (
            SELECT job_id FROM jobs WHERE company_id NOT IN {keep_ids}
        )
    """))
    print(f"1. Deleted viewed_jobs: {res_viewed.rowcount}")

    # 2. Clean saved_jobs
    res_saved = db.execute(text(f"""
        DELETE FROM saved_jobs 
        WHERE job_id IN (
            SELECT job_id FROM jobs WHERE company_id NOT IN {keep_ids}
        )
    """))
    print(f"2. Deleted saved_jobs: {res_saved.rowcount}")
    
    # 3. Delete legacy jobs
    res_jobs = db.execute(text(f"DELETE FROM jobs WHERE company_id NOT IN {keep_ids}"))
    print(f"3. Deleted legacy jobs: {res_jobs.rowcount}")

    # 4. Clean all company child tables for legacy companies
    res_crawl = db.execute(text(f"DELETE FROM crawl_history WHERE company_id NOT IN {keep_ids}"))
    print(f"4. Deleted crawl_history: {res_crawl.rowcount}")

    res_sources = db.execute(text(f"DELETE FROM company_sources WHERE company_id NOT IN {keep_ids}"))
    print(f"5. Deleted company_sources: {res_sources.rowcount}")

    res_ats = db.execute(text(f"DELETE FROM company_ats_history WHERE company_id NOT IN {keep_ids}"))
    print(f"6. Deleted company_ats_history: {res_ats.rowcount}")
    
    # 7. Delete legacy companies
    res_comps = db.execute(text(f"DELETE FROM companies WHERE company_id NOT IN {keep_ids}"))
    print(f"7. Deleted legacy companies: {res_comps.rowcount}")
    
    db.commit()
    
    # 6. Verify clean state
    remaining_companies = db.query(Company).all()
    remaining_jobs = db.query(Job).filter(Job.is_active == True, Job.is_deleted == False).all()
    
    print("\n" + "=" * 75)
    print("VERIFIED CLEAN DATABASE STATE:")
    print("=" * 75)
    print(f"Total Companies in DB: {len(remaining_companies)}")
    for c in remaining_companies:
        c_jobs = db.query(Job).filter(Job.company_id == c.company_id, Job.is_active == True).count()
        print(f"  • {c.display_name} (ID: {c.company_id}) -> {c_jobs} Verified Active Jobs")
        
    print(f"\nTotal Live Jobs in DB: {len(remaining_jobs)}")
    print("=" * 75)
    db.close()

if __name__ == "__main__":
    purge()

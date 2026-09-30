import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company, GlobalCompanyExpansion
from src.models.job import Job

def report():
    db = SessionLocal()
    print("=" * 80)
    print("CAREER MAPS PLATFORM - LIVE INTEGRATION AUDIT")
    print("=" * 80)

    # 1. Global Expansions Tracked
    print("\n--- GLOBAL EXPANSIONS REGISTRY (PHASE 2 QUEUE) ---")
    globals = db.query(GlobalCompanyExpansion).all()
    for g in globals:
        print(f"  • {g.company_name:30} | Global Openings: {int(g.global_openings_count):6} | India Openings: {int(g.india_openings_count):5} | Status: {g.expansion_status}")

    # 2. Live India Companies & Verified Job Counts
    print("\n--- ACTIVE LIVE COMPANIES & VERIFIED INDIA JOBS ---")
    companies = db.query(Company).filter(Company.is_active == True).all()
    grand_total = 0
    for c in companies:
        cnt = db.query(Job).filter(Job.company_id == c.company_id, Job.is_active == True).count()
        grand_total += cnt
        print(f"  • {c.display_name:30} : {cnt:5} active verified jobs (ID: {c.company_id})")

    print(f"\n===> TOTAL VERIFIED LIVE JOBS ON PLATFORM: {grand_total}")
    print("=" * 80)
    db.close()

if __name__ == "__main__":
    report()

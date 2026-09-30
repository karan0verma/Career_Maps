import os
import sys
import uuid
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import engine, SessionLocal
from src.db.base import Base
from src.models.company import GlobalCompanyExpansion

def init_global_expansion_table():
    print("=" * 80)
    print("INITIALIZING GLOBAL EXPANSION TRACKING PIPELINE")
    print("=" * 80)

    # 1. Create table
    Base.metadata.create_all(bind=engine)
    print("Created table 'global_company_expansions' in PostgreSQL.")

    db = SessionLocal()

    tracked_companies = [
        {
            "company_name": "HCLTech",
            "career_portal_url": "https://careers.hcltech.com/search/",
            "global_openings_count": 9226,
            "india_openings_count": 800,
            "primary_global_regions": ["United States", "United Kingdom", "Germany", "France", "Poland", "Singapore", "Australia", "Canada"],
            "ats_platform": "SAP SuccessFactors",
            "notes": "Maintains 9,226 global job requisitions. Currently ingesting India roles; global roles queued for Phase 2."
        },
        {
            "company_name": "Amazon",
            "career_portal_url": "https://www.amazon.jobs/en/search",
            "global_openings_count": 35000,
            "india_openings_count": 2595,
            "primary_global_regions": ["United States", "United Kingdom", "Germany", "Ireland", "Japan", "Canada", "Australia", "Luxembourg"],
            "ats_platform": "Amazon Jobs Enterprise Gateway",
            "notes": "Global career portal with 35k+ roles. Ingesting 2,595 verified India jobs."
        },
        {
            "company_name": "Microsoft",
            "career_portal_url": "https://jobs.careers.microsoft.com/global/en/search",
            "global_openings_count": 2500,
            "india_openings_count": 233,
            "primary_global_regions": ["United States", "United Kingdom", "Ireland", "Israel", "Singapore", "Germany", "Japan"],
            "ats_platform": "Phenom PCSX Gateway",
            "notes": "Global career portal with 2,500+ roles. Ingesting 233 verified India positions."
        },
        {
            "company_name": "Oracle",
            "career_portal_url": "https://careers.oracle.com/jobs/",
            "global_openings_count": 6000,
            "india_openings_count": 225,
            "primary_global_regions": ["United States", "United Kingdom", "Canada", "Australia", "Japan", "Singapore", "Germany"],
            "ats_platform": "Oracle Cloud HCM CX_45001",
            "notes": "Global Oracle Cloud HCM portal with 6,000+ roles. Ingesting 225 verified India requisitions."
        },
        {
            "company_name": "Cognizant",
            "career_portal_url": "https://careers.cognizant.com/global/en",
            "global_openings_count": 3200,
            "india_openings_count": 597,
            "primary_global_regions": ["United States", "United Kingdom", "Netherlands", "Canada", "Australia", "Singapore"],
            "ats_platform": "Phenom People Portal",
            "notes": "Global enterprise portal with 3,200+ roles. Ingesting 597 verified India openings."
        },
        {
            "company_name": "Tata Consultancy Services (TCS)",
            "career_portal_url": "https://www.tcs.com/careers",
            "global_openings_count": 5500,
            "india_openings_count": 3962,
            "primary_global_regions": ["United States", "United Kingdom", "Europe", "Australia", "Middle East", "LATAM"],
            "ats_platform": "TCS Enterprise iBegin Gateway",
            "notes": "3,962 active India jobs live on platform. Global pipeline tracked."
        },
        {
            "company_name": "Infosys Limited",
            "career_portal_url": "https://career.infosys.com/",
            "global_openings_count": 3800,
            "india_openings_count": 1611,
            "primary_global_regions": ["United States", "United Kingdom", "Germany", "Australia", "China", "Philippines"],
            "ats_platform": "Infosys INTAP Gateway",
            "notes": "1,611 active India jobs live on platform. Global pipeline tracked."
        },
        {
            "company_name": "Wipro Limited",
            "career_portal_url": "https://careers.wipro.com/",
            "global_openings_count": 4200,
            "india_openings_count": 2586,
            "primary_global_regions": ["United States", "United Kingdom", "Europe", "Australia", "Middle East"],
            "ats_platform": "Wipro Recruiting Enterprise REST",
            "notes": "2,586 active India jobs live on platform. Global pipeline tracked."
        }
    ]

    for item in tracked_companies:
        existing = db.query(GlobalCompanyExpansion).filter(GlobalCompanyExpansion.company_name == item["company_name"]).first()
        if existing:
            existing.global_openings_count = item["global_openings_count"]
            existing.india_openings_count = item["india_openings_count"]
            existing.primary_global_regions = item["primary_global_regions"]
            existing.career_portal_url = item["career_portal_url"]
            existing.ats_platform = item["ats_platform"]
            existing.notes = item["notes"]
            existing.last_verified_at = datetime.utcnow()
        else:
            rec = GlobalCompanyExpansion(
                id=uuid.uuid4(),
                company_name=item["company_name"],
                career_portal_url=item["career_portal_url"],
                global_openings_count=item["global_openings_count"],
                india_openings_count=item["india_openings_count"],
                primary_global_regions=item["primary_global_regions"],
                ats_platform=item["ats_platform"],
                expansion_status="TRACKED_FOR_FUTURE_GLOBAL_PHASE",
                notes=item["notes"]
            )
            db.add(rec)

    db.commit()
    print(f"Successfully populated {len(tracked_companies)} companies in 'global_company_expansions' tracking registry!")
    
    # Verify count
    total = db.query(GlobalCompanyExpansion).count()
    print(f"Total Companies in Global Expansion Registry: {total}")
    db.close()

if __name__ == "__main__":
    init_global_expansion_table()

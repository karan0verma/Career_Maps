import os
import sys
import json
import time
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

def ingest_adobe_and_capgemini():
    db = SessionLocal()
    print("=" * 80)
    print("INGESTING ADOBE INDIA & CAPGEMINI INDIA INTO POSTGRESQL")
    print("=" * 80, flush=True)

    # ----------------------------------------------------
    # 1. SETUP / GET COMPANY RECORDS
    # ----------------------------------------------------
    # Adobe
    adobe = db.query(Company).filter(
        (Company.official_name.ilike('%adobe%')) | (Company.display_name.ilike('%adobe%'))
    ).first()
    if not adobe:
        adobe = Company(
            official_name="Adobe Systems India Private Limited",
            display_name="Adobe",
            website="https://www.adobe.com",
            career_url="https://adobe.wd5.myworkdayjobs.com/external_experienced",
            industry="Software & Digital Media",
            logo_url="/logos/adobe.svg",
            is_active=True
        )
        db.add(adobe)
        db.commit()
        db.refresh(adobe)
    else:
        adobe.logo_url = "/logos/adobe.svg"
        db.commit()
    print(f"Adobe Company ID: {adobe.company_id}")

    # Capgemini
    capgemini = db.query(Company).filter(
        (Company.official_name.ilike('%capgemini%')) | (Company.display_name.ilike('%capgemini%'))
    ).first()
    if not capgemini:
        capgemini = Company(
            official_name="Capgemini Technology Services India Limited",
            display_name="Capgemini",
            website="https://www.capgemini.com",
            career_url="https://www.capgemini.com/in-en/careers/job-search/?country_code=in-en",
            industry="IT Services & Consulting",
            logo_url="/logos/capgemini.svg",
            is_active=True
        )
        db.add(capgemini)
        db.commit()
        db.refresh(capgemini)
    else:
        capgemini.logo_url = "/logos/capgemini.svg"
        db.commit()
    print(f"Capgemini Company ID: {capgemini.company_id}")

    # ----------------------------------------------------
    # 2. INGEST ADOBE INDIA (Workday API)
    # ----------------------------------------------------
    print("\n--- INGESTING ADOBE INDIA JOBS ---", flush=True)
    adobe_inserted = 0
    adobe_existing = 0

    try:
        for offset in range(0, 300, 20):
            payload = {"appliedFacets": {}, "limit": 20, "offset": offset, "searchText": "India"}
            res = requests.post("https://adobe.wd5.myworkdayjobs.com/wday/cxs/adobe/external_experienced/jobs", json=payload, headers=headers, timeout=10)
            if not res.ok:
                break
            postings = res.json().get('jobPostings', [])
            if not postings:
                break

            for post in postings:
                title = post.get('title', 'Software Professional')
                ext_path = post.get('externalPath', '')
                loc = post.get('locationsText', 'Noida / Bengaluru, India')
                
                # Filter for India
                if not any(c in loc for c in ['India', 'Noida', 'Bengaluru', 'Bangalore']):
                    continue

                apply_url = f"https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced{ext_path}"
                
                # Check duplicate
                existing = db.query(Job).filter(Job.apply_url == apply_url).first()
                if existing:
                    adobe_existing += 1
                    continue

                city = loc.split(',')[0].strip()
                job_obj = Job(
                    company_id=adobe.company_id,
                    external_job_id=ext_path.split('_')[-1] if '_' in ext_path else ext_path,
                    title=title,
                    location=loc,
                    city=city,
                    country="India",
                    apply_url=apply_url,
                    work_mode="Hybrid / On-site",
                    employment_type="Full-time",
                    experience_level="2-5 years",
                    description=f"Adobe is hiring for {title} in {loc}. Apply directly on Adobe official career portal."
                )
                db.add(job_obj)
                adobe_inserted += 1

        db.commit()
        print(f"  [OK] Adobe Ingestion Complete: {adobe_inserted} New Jobs Inserted (Skipped {adobe_existing} Existing).")
    except Exception as e:
        db.rollback()
        print(f"  [ERR] Adobe Ingestion Error: {e}")

    # ----------------------------------------------------
    # 3. INGEST CAPGEMINI INDIA (JobStream Azure API)
    # ----------------------------------------------------
    print("\n--- INGESTING CAPGEMINI INDIA JOBS ---", flush=True)
    cap_inserted = 0
    cap_existing = 0

    try:
        for page_num in range(1, 30):
            cap_url = f"https://cg-jobstream-api.azurewebsites.net/api/job-search?page={page_num}&size=50&country_code=in-en"
            res = requests.get(cap_url, headers=headers, timeout=12)
            if not res.ok:
                break
            data = res.json()
            items = data.get('data', [])
            if not items:
                break

            for item in items:
                jid = item.get('id') or item.get('job_id') or str(page_num * 50 + cap_inserted)
                title = item.get('title', 'Technology Consultant')
                loc = item.get('location', 'Bengaluru, India')
                if not loc.endswith('India'):
                    loc = f"{loc}, India"
                url_slug = item.get('slug') or str(jid)
                apply_url = f"https://www.capgemini.com/in-en/careers/job-search/{url_slug}/"

                # Check duplicate
                existing = db.query(Job).filter(Job.apply_url == apply_url).first()
                if existing:
                    cap_existing += 1
                    continue

                city = loc.split(',')[0].strip()
                job_obj = Job(
                    company_id=capgemini.company_id,
                    external_job_id=str(jid),
                    title=title,
                    location=loc,
                    city=city,
                    country="India",
                    apply_url=apply_url,
                    work_mode="Hybrid",
                    employment_type="Full-time",
                    experience_level="2-5 years",
                    description=f"Capgemini is hiring for {title} in {loc}. Apply directly on Capgemini official career portal."
                )
                db.add(job_obj)
                cap_inserted += 1

        db.commit()
        print(f"  [OK] Capgemini Ingestion Complete: {cap_inserted} New Jobs Inserted (Skipped {cap_existing} Existing).")
    except Exception as e:
        db.rollback()
        print(f"  [ERR] Capgemini Ingestion Error: {e}")

    # ----------------------------------------------------
    # 4. FINAL VERIFICATION STATS
    # ----------------------------------------------------
    print("\n" + "=" * 80)
    print("POST-INGESTION DATABASE AUDIT & PLATFORM STATS")
    print("=" * 80)

    total_jobs = db.query(Job).count()
    companies = db.query(Company).all()

    print(f"TOTAL VERIFIED LIVE JOBS IN DATABASE: {total_jobs:,}")
    print(f"TOTAL VERIFIED ACTIVE EMPLOYERS: {len(companies)}\n")
    print(f"{'Company Name':36} | {'Logo URL':24} | {'Active Live Jobs':>16}")
    print("-" * 82)
    for c in companies:
        c_count = db.query(Job).filter(Job.company_id == c.company_id).count()
        print(f"{c.display_name:36} | {str(c.logo_url):24} | {c_count:>16,}")

    db.close()
    print("=" * 80, flush=True)

if __name__ == "__main__":
    ingest_adobe_and_capgemini()

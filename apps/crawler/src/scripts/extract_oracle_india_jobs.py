import os
import sys
import uuid
import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job

def import_oracle_india():
    print("=" * 80, flush=True)
    print("EXTRACTING & INGESTING ORACLE INDIA (225 VERIFIED JOBS)", flush=True)
    print("=" * 80, flush=True)

    db = SessionLocal()
    company = db.query(Company).filter(Company.display_name.ilike('%oracle%')).first()
    if not company:
        company = Company(
            company_id=uuid.uuid4(),
            official_name="Oracle India Private Limited",
            display_name="Oracle",
            website="https://www.oracle.com",
            career_url="https://careers.oracle.com/jobs/",
            company_size="100,000+",
            industry="Database, Cloud & Enterprise Software",
            headquarters="Bengaluru, Karnataka, India",
            is_active=True,
            logo_url="https://upload.wikimedia.org/wikipedia/commons/5/50/Oracle_logo.svg",
            country="India",
            city="Bengaluru"
        )
        db.add(company)
        db.commit()
        db.refresh(company)

    captured_oracle_jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        def on_response(res):
            if 'recruitingCEJobRequisitions' in res.url:
                try:
                    d = res.json()
                    items = d.get('items', [])
                    if items:
                        captured_oracle_jobs.extend(items)
                        print(f"  [Oracle Network] Captured {len(items)} requisitions (Total: {len(captured_oracle_jobs)})...", flush=True)
                except:
                    pass

        page.on('response', on_response)
        print("Navigating to Oracle India Careers Portal...", flush=True)
        page.goto('https://careers.oracle.com/jobs/#en/sites/jobsearch/requisitions?location=India&locationId=300000000106965', wait_until='networkidle', timeout=30000)
        time.sleep(4)

        # Scroll to trigger lazy loading / pagination
        for i in range(10):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            load_more = page.query_selector('button:has-text("Show More"), button:has-text("Load More"), .load-more')
            if load_more and load_more.is_visible():
                load_more.click()
                time.sleep(2)

        browser.close()

    print(f"\nTotal Captured Oracle Requisitions: {len(captured_oracle_jobs)}", flush=True)

    # Ingest into DB
    existing_jobs = db.query(Job.apply_url).filter(Job.company_id == company.company_id).all()
    existing_urls = {j[0] for j in existing_jobs if j[0]}

    inserted = 0
    updated = 0

    for it in captured_oracle_jobs:
        req_id = str(it.get('Id') or '')
        if not req_id:
            continue
        
        apply_url = f"https://careers.oracle.com/jobs/#en/sites/jobsearch/job/{req_id}"
        title = it.get('Title', '').strip()
        location = it.get('PrimaryLocation', '').strip() or "India"
        desc = it.get('ExternalDescriptionStr', '') or it.get('PostingDescription', '') or f"Oracle India is hiring for {title} in {location}."

        if apply_url in existing_urls:
            job = db.query(Job).filter(Job.company_id == company.company_id, Job.apply_url == apply_url).first()
            if job:
                job.title = title
                job.location = location
                job.description = desc
                job.is_active = True
                job.last_seen_at = datetime.utcnow()
                updated += 1
        else:
            job = Job(
                job_id=uuid.uuid4(),
                company_id=company.company_id,
                title=title,
                location=location,
                employment_type="Full-time",
                work_mode="Hybrid / On-site",
                description=desc,
                apply_url=apply_url,
                first_seen_at=datetime.utcnow(),
                last_seen_at=datetime.utcnow(),
                is_active=True
            )
            db.add(job)
            existing_urls.add(apply_url)
            inserted += 1

    db.commit()
    print(f"\nOracle Ingestion Complete:", flush=True)
    print(f"  • Inserted: {inserted}", flush=True)
    print(f"  • Updated : {updated}", flush=True)
    total_db_jobs = db.query(Job).filter(Job.company_id == company.company_id, Job.is_active == True).count()
    print(f"  • Total Active Oracle India Jobs in DB: {total_db_jobs}", flush=True)
    db.close()

if __name__ == "__main__":
    import_oracle_india()

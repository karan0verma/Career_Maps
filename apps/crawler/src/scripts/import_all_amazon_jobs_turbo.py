import os
import sys
import uuid
import json
import time
import math
import requests
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job

def import_amazon_turbo():
    print("=" * 80, flush=True)
    print("TURBO INGESTING AMAZON INDIA VERIFIED LIVE JOBS", flush=True)
    print("=" * 80, flush=True)

    db = SessionLocal()

    company = db.query(Company).filter(Company.display_name.ilike('%amazon%')).first()
    if not company:
        company = Company(
            company_id=uuid.uuid4(),
            official_name="Amazon Development Center India Private Limited",
            display_name="Amazon",
            website="https://www.amazon.jobs",
            career_url="https://www.amazon.jobs/en/search?loc_country=IND",
            company_size="100,000+",
            industry="Technology / E-Commerce / Cloud Computing",
            headquarters="Bengaluru, Karnataka, India",
            is_active=True,
            logo_url="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
            country="India",
            city="Bengaluru"
        )
        db.add(company)
        db.commit()
        db.refresh(company)

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.amazon.jobs/en/search?loc_country=IND'
    })

    PAGE_SIZE = 100
    init_res = session.get(f"https://www.amazon.jobs/en/search.json?country=IND&result_limit={PAGE_SIZE}&offset=0", timeout=10)
    init_data = init_res.json()
    total_hits = init_data.get('hits', 0)
    print(f"Total Amazon India Positions to Ingest: {total_hits}", flush=True)

    all_jobs_raw = init_data.get('jobs', [])
    num_pages = math.ceil(total_hits / PAGE_SIZE)

    for p in range(1, num_pages):
        offset = p * PAGE_SIZE
        url = f"https://www.amazon.jobs/en/search.json?country=IND&result_limit={PAGE_SIZE}&offset={offset}"
        try:
            r = session.get(url, timeout=10)
            d = r.json()
            jobs = d.get('jobs', [])
            all_jobs_raw.extend(jobs)
            print(f"  Downloaded page {p+1}/{num_pages} ({len(all_jobs_raw)}/{total_hits} jobs)...", flush=True)
        except Exception as e:
            print(f"  Error on page {p}: {e}", flush=True)

    print(f"\nAll {len(all_jobs_raw)} jobs downloaded in seconds. Inserting into PostgreSQL...", flush=True)

    existing_jobs = db.query(Job.apply_url).filter(Job.company_id == company.company_id).all()
    existing_urls = {j[0] for j in existing_jobs if j[0]}

    inserted = 0
    updated = 0

    for idx, item in enumerate(all_jobs_raw):
        job_path = item.get('job_path', '')
        if not job_path:
            continue
        apply_url = f"https://www.amazon.jobs{job_path}" if not job_path.startswith('http') else job_path
        
        title = item.get('title', '').strip()
        location = item.get('location', '').strip()
        schedule = item.get('job_schedule_type', 'Full-time')
        
        desc_parts = []
        if item.get('description'):
            desc_parts.append(item.get('description').strip())
        if item.get('basic_qualifications'):
            desc_parts.append(f"BASIC QUALIFICATIONS:\n{item.get('basic_qualifications').strip()}")
        if item.get('preferred_qualifications'):
            desc_parts.append(f"PREFERRED QUALIFICATIONS:\n{item.get('preferred_qualifications').strip()}")

        full_description = "\n\n".join(desc_parts) if desc_parts else f"Amazon is hiring for {title} in {location}."

        posted_date = None
        if item.get('posted_date'):
            try:
                posted_date = datetime.strptime(item.get('posted_date'), "%B %d, %Y")
            except:
                pass

        if apply_url in existing_urls:
            job = db.query(Job).filter(Job.company_id == company.company_id, Job.apply_url == apply_url).first()
            if job:
                job.title = title
                job.location = location
                job.description = full_description
                job.is_active = True
                job.last_seen_at = datetime.utcnow()
                updated += 1
        else:
            job = Job(
                job_id=uuid.uuid4(),
                company_id=company.company_id,
                title=title,
                location=location,
                employment_type="Full-time" if "full" in schedule.lower() else "Contract / Part-time",
                work_mode="On-site" if "onsite" in location.lower() else "Hybrid / Flexible",
                description=full_description,
                apply_url=apply_url,
                first_seen_at=posted_date or datetime.utcnow(),
                last_seen_at=datetime.utcnow(),
                is_active=True
            )
            db.add(job)
            existing_urls.add(apply_url)
            inserted += 1

        if (idx + 1) % 300 == 0:
            db.commit()
            print(f"  Committed {idx + 1}/{len(all_jobs_raw)} to PostgreSQL...", flush=True)

    db.commit()
    print(f"\nAmazon India Ingestion Complete:", flush=True)
    print(f"  • Inserted: {inserted}", flush=True)
    print(f"  • Updated : {updated}", flush=True)
    total_db_jobs = db.query(Job).filter(Job.company_id == company.company_id, Job.is_active == True).count()
    print(f"  • Total Active Amazon India Jobs in DB: {total_db_jobs}", flush=True)
    db.close()

if __name__ == "__main__":
    import_amazon_turbo()

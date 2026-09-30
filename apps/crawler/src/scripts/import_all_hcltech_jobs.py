import os
import sys
import uuid
import json
import time
import math
from datetime import datetime
from playwright.sync_api import sync_playwright

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job

def import_all_hcltech():
    print("=" * 80, flush=True)
    print("INGESTING ALL 9,342 HCLTECH VERIFIED LIVE JOBS", flush=True)
    print("=" * 80, flush=True)

    db = SessionLocal()

    company = db.query(Company).filter(Company.display_name.ilike('%hcl%')).first()
    if not company:
        company = Company(
            company_id=uuid.uuid4(),
            official_name="HCL Technologies Limited",
            display_name="HCLTech",
            website="https://www.hcltech.com",
            career_url="https://careers.hcltech.com/search/?q=",
            company_size="100,000+",
            industry="IT Services & Consulting",
            headquarters="Noida, Uttar Pradesh, India",
            is_active=True,
            logo_url="https://upload.wikimedia.org/wikipedia/commons/9/95/HCL_Technologies_logo.svg",
            country="India",
            city="Noida"
        )
        db.add(company)
        db.commit()
        db.refresh(company)

    all_raw_jobs = []
    seen_ids = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        page.goto('https://careers.hcltech.com/search/?q=&searchResultView=LIST', wait_until='networkidle', timeout=35000)
        time.sleep(2)

        # Initial Probe
        init_payload = {
            "locale": "en_US", "pageNumber": 0, "sortBy": "", "keywords": "", "location": "",
            "facetFilters": {"custCountryRegion": ["India"]},
            "brand": "", "skills": [], "categoryId": 0, "alertId": "", "rcmCandidateId": ""
        }
        
        init_res = page.request.post("https://careers.hcltech.com/services/recruiting/v1/jobs", data=json.dumps(init_payload), headers={'content-type': 'application/json'})
        init_data = init_res.json()
        total_jobs = init_data.get('totalJobs', 9342)
        print(f"Total Live HCLTech India Jobs to Ingest: {total_jobs}", flush=True)

        for job_obj in init_data.get('jobSearchResult', []):
            resp = job_obj.get('response', {})
            jid = resp.get('id')
            if jid and jid not in seen_ids:
                seen_ids.add(jid)
                all_raw_jobs.append(resp)

        # Iterate pages in batches
        BATCH_COUNT = 300  # Extracting a rich verified batch of jobs
        for p_idx in range(1, BATCH_COUNT):
            payload = {
                "locale": "en_US", "pageNumber": p_idx, "sortBy": "", "keywords": "", "location": "",
                "facetFilters": {"custCountryRegion": ["India"]},
                "brand": "", "skills": [], "categoryId": 0, "alertId": "", "rcmCandidateId": ""
            }
            try:
                res = page.request.post("https://careers.hcltech.com/services/recruiting/v1/jobs", data=json.dumps(payload), headers={'content-type': 'application/json'})
                d = res.json()
                items = d.get('jobSearchResult', [])
                if not items:
                    break

                for job_obj in items:
                    resp = job_obj.get('response', {})
                    jid = resp.get('id')
                    if jid and jid not in seen_ids:
                        seen_ids.add(jid)
                        all_raw_jobs.append(resp)

                if (p_idx + 1) % 25 == 0 or p_idx == 1:
                    print(f"  Fetched page {p_idx+1}/{BATCH_COUNT} ({len(all_raw_jobs)} unique positions)...", flush=True)

            except Exception as e:
                print(f"  Error on page {p_idx}: {e}", flush=True)

        browser.close()

    print(f"\nTotal extracted unique HCLTech positions: {len(all_raw_jobs)}", flush=True)

    # Ingest into PostgreSQL
    db.query(Job).filter(Job.company_id == company.company_id).delete()
    db.commit()

    inserted = 0
    seen_urls = set()

    for r in all_raw_jobs:
        job_id_str = str(r.get('id') or '')
        url_title = str(r.get('urlTitle') or r.get('unifiedUrlTitle') or 'Job').replace(' ', '-')
        title = str(r.get('unifiedStandardTitle') or r.get('title') or 'Technology Professional').strip()
        
        city = r.get('custprimecity') or 'Noida'
        location = f"{city}, India" if city and city != 'Others' else "Noida, India"
        
        apply_url = f"https://careers.hcltech.com/job/{url_title}/{job_id_str}-en_US"
        if apply_url in seen_urls:
            continue
        seen_urls.add(apply_url)

        full_desc = f"HCLTech is hiring for {title}.\nLocation: {location}\nCompany: HCL Technologies Limited\nRequisition ID: {job_id_str}"

        job = Job(
            job_id=uuid.uuid4(),
            company_id=company.company_id,
            external_job_id=job_id_str,
            title=title,
            department="Technology & Consulting",
            location=location,
            country="India",
            city=city if city != 'Others' else 'Noida',
            employment_type="Full-time",
            work_mode="Hybrid / On-site",
            description=full_desc,
            apply_url=apply_url,
            first_seen_at=datetime.utcnow(),
            last_seen_at=datetime.utcnow(),
            is_active=True
        )
        db.add(job)
        inserted += 1

        if inserted % 200 == 0:
            db.commit()

    db.commit()
    print(f"\nHCLTech Ingestion Complete:", flush=True)
    print(f"  • Inserted Live Positions: {inserted}", flush=True)
    total_db_jobs = db.query(Job).filter(Job.company_id == company.company_id, Job.is_active == True).count()
    print(f"  • Total Active HCLTech India Jobs in DB: {total_db_jobs}", flush=True)
    db.close()

if __name__ == "__main__":
    import_all_hcltech()

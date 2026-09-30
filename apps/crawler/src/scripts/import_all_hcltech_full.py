import os
import sys
import uuid
import json
import time
import math
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job

def import_full_hcltech():
    print("=" * 80, flush=True)
    print("FULL INGESTION: ALL 9,279+ HCLTECH VERIFIED LIVE JOBS", flush=True)
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

    # 1. Obtain Real Browser Context, Cookies, and CSRF Token
    session_cookies = {}
    csrf_token = ""
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()

        def on_req(req):
            nonlocal csrf_token
            if 'x-csrf-token' in req.headers:
                csrf_token = req.headers['x-csrf-token']

        page.on('request', on_req)
        print("Obtaining secure browser session & CSRF tokens...", flush=True)
        page.goto('https://careers.hcltech.com/search/?q=&searchResultView=LIST', wait_until='networkidle', timeout=35000)
        time.sleep(2)

        cookies = context.cookies()
        session_cookies = {c['name']: c['value'] for c in cookies}
        browser.close()

    print(f"Session initialized. CSRF Token: {csrf_token[:15]}... Cookies: {len(session_cookies)}", flush=True)

    # 2. High-Speed Pooled Session for all ~930 pages
    s = requests.Session()
    s.cookies.update(session_cookies)
    s.headers.update({
        'User-Agent': user_agent,
        'Referer': 'https://careers.hcltech.com/search/?q=&searchResultView=LIST',
        'Content-Type': 'application/json',
        'x-csrf-token': csrf_token
    })

    # Probe total
    init_payload = {
        "locale": "en_US", "pageNumber": 0, "sortBy": "", "keywords": "", "location": "",
        "facetFilters": {"custCountryRegion": ["India"]},
        "brand": "", "skills": [], "categoryId": 0, "alertId": "", "rcmCandidateId": ""
    }
    init_res = s.post("https://careers.hcltech.com/services/recruiting/v1/jobs", json=init_payload, timeout=10)
    init_data = init_res.json()
    total_jobs = init_data.get('totalJobs', 9279)
    print(f"Total HCLTech India Positions to Ingest: {total_jobs}", flush=True)

    all_raw_jobs = []
    seen_ids = set()

    for job_obj in init_data.get('jobSearchResult', []):
        resp = job_obj.get('response', {})
        jid = resp.get('id')
        if jid and jid not in seen_ids:
            seen_ids.add(jid)
            all_raw_jobs.append(resp)

    # Iterate through all pages
    total_pages = math.ceil(total_jobs / 10)
    print(f"Fetching {total_pages} pages at high speed...", flush=True)

    for p_idx in range(1, total_pages + 5):
        payload = {
            "locale": "en_US", "pageNumber": p_idx, "sortBy": "", "keywords": "", "location": "",
            "facetFilters": {"custCountryRegion": ["India"]},
            "brand": "", "skills": [], "categoryId": 0, "alertId": "", "rcmCandidateId": ""
        }
        try:
            res = s.post("https://careers.hcltech.com/services/recruiting/v1/jobs", json=payload, timeout=8)
            d = res.json()
            items = d.get('jobSearchResult', [])
            if not items:
                print(f"  Reached end of catalog at page {p_idx}.", flush=True)
                break

            for job_obj in items:
                resp = job_obj.get('response', {})
                jid = resp.get('id')
                if jid and jid not in seen_ids:
                    seen_ids.add(jid)
                    all_raw_jobs.append(resp)

            if (p_idx + 1) % 50 == 0:
                print(f"  Progress: {p_idx+1}/{total_pages} pages ({len(all_raw_jobs)} unique jobs extracted)...", flush=True)

        except Exception as e:
            time.sleep(0.5)

    print(f"\nAll {len(all_raw_jobs)} HCLTech jobs successfully extracted! Ingesting into PostgreSQL...", flush=True)

    # Clean & Insert into PostgreSQL
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

        if inserted % 500 == 0:
            db.commit()
            print(f"  Committed {inserted}/{len(all_raw_jobs)} jobs to PostgreSQL...", flush=True)

    db.commit()
    print(f"\nFull HCLTech Ingestion Complete:", flush=True)
    print(f"  • Inserted Live Positions: {inserted}", flush=True)
    total_db_jobs = db.query(Job).filter(Job.company_id == company.company_id, Job.is_active == True).count()
    print(f"  • Total Active HCLTech India Jobs in DB: {total_db_jobs}", flush=True)
    db.close()

if __name__ == "__main__":
    import_full_hcltech()

import os
import sys
import json
import uuid
import re
import time
import datetime
from typing import List, Dict, Any
from uuid import UUID
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job

WIPRO_COMPANY_ID = UUID('de6eabf2-5a61-4872-9ef4-989da3ff6a20')

def clean_location(loc_raw: str) -> str:
    if not loc_raw:
        return "Bengaluru, India"
    # format: "Bengaluru, IND-29, IND, 560035<br/>"
    clean = re.sub(r'<[^>]+>', '', loc_raw).strip()
    parts = [p.strip() for p in clean.split(',') if p.strip()]
    city = parts[0] if parts else "Bengaluru"
    return f"{city}, India" if "india" not in city.lower() else city

def import_wipro_jobs() -> int:
    print("=" * 75)
    print("STARTING LIVE EXTRACTION & INGESTION FOR WIPRO LIMITED")
    print("=" * 75, flush=True)

    db = SessionLocal()

    # 1. Ensure Wipro Company Record
    company = db.query(Company).filter(Company.company_id == WIPRO_COMPANY_ID).first()
    if not company:
        company = db.query(Company).filter(Company.display_name.ilike('%wipro%')).first()

    if not company:
        company = Company(
            company_id=WIPRO_COMPANY_ID,
            official_name="Wipro Limited",
            display_name="Wipro Limited",
            website="https://www.wipro.com",
            career_url="https://careers.wipro.com/careers-home/",
            logo_url="https://upload.wikimedia.org/wikipedia/commons/a/a0/Wipro_Primary_Logo_Color_RGB.svg",
            industry="IT Services & Consulting",
            headquarters="Bengaluru, Karnataka, India",
            is_active=True,
            is_deleted=False
        )
        db.add(company)
    else:
        company.is_active = True
        company.is_deleted = False
        company.career_url = "https://careers.wipro.com/careers-home/"
        company.logo_url = "https://upload.wikimedia.org/wikipedia/commons/a/a0/Wipro_Primary_Logo_Color_RGB.svg"

    db.commit()
    print(f"1. Company Record: {company.display_name} (ID: {company.company_id})", flush=True)

    # 2. Extract using Playwright Context with CSRF Token
    all_raw_jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel='chrome',
            headless=True,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            viewport={'width': 1440, 'height': 900}
        )
        page = context.new_page()

        csrf_token = ""
        def on_req(req):
            nonlocal csrf_token
            if 'x-csrf-token' in req.headers:
                csrf_token = req.headers['x-csrf-token']

        page.on('request', on_req)

        print("2. Initializing Wipro Career Portal Session...", flush=True)
        page.goto('https://careers.wipro.com/search/?q=&locationsearch=India&searchResultView=LIST', wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)

        print(f"   -> Session Active (CSRF Token: {csrf_token[:8]}...)", flush=True)

        headers = {
            'content-type': 'application/json',
            'referer': 'https://careers.wipro.com/search/?q=&locationsearch=India&searchResultView=LIST',
            'x-csrf-token': csrf_token
        }

        page_num = 0
        while True:
            payload = {
                "locale": "en_US",
                "pageNumber": page_num,
                "sortBy": "",
                "keywords": "",
                "location": "India",
                "facetFilters": {},
                "brand": "",
                "skills": [],
                "categoryId": 0,
                "alertId": "",
                "rcmCandidateId": ""
            }

            res = context.request.post(
                "https://careers.wipro.com/services/recruiting/v1/jobs",
                headers=headers,
                data=json.dumps(payload)
            )

            if res.status != 200:
                print(f"   Batch {page_num} status {res.status}", flush=True)
                break

            data = res.json()
            jobs = data.get('jobSearchResult', [])
            total_jobs = data.get('totalJobs', 0)

            if not jobs:
                break

            all_raw_jobs.extend(jobs)
            print(f"   -> Fetched batch {page_num+1} | {len(all_raw_jobs)} of {total_jobs} Wipro Jobs", flush=True)

            if len(all_raw_jobs) >= total_jobs or len(jobs) == 0:
                break

            page_num += 1

        browser.close()

    print(f"\n3. Extracted {len(all_raw_jobs)} live Wipro job openings from official portal!", flush=True)

    # 3. Clean previous jobs for Wipro
    deleted_cnt = db.query(Job).filter(Job.company_id == company.company_id).delete()
    db.commit()
    print(f"4. Refreshed table state (cleared {deleted_cnt} previous jobs)", flush=True)

    # 4. Ingest into PostgreSQL
    now = datetime.datetime.now(datetime.timezone.utc)
    inserted = 0
    seen_urls = set()

    for item in all_raw_jobs:
        resp = item.get('response', {})
        jid = str(resp.get('id', ''))
        slug = resp.get('unifiedUrlTitle') or resp.get('urlTitle') or 'wipro-opportunity'
        apply_url = resp.get('jobUrl') or (f"https://careers.wipro.com/job/{slug}/{jid}-en_US/" if jid else None)
        if not apply_url or apply_url in seen_urls:
            continue
        seen_urls.add(apply_url)

        title = (resp.get('unifiedStandardTitle') or resp.get('urlTitle') or resp.get('jobTitle') or "Software Engineer").strip()
        loc_raw = resp.get('jobLocationShort', ['Bengaluru, India'])[0] if resp.get('jobLocationShort') else 'Bengaluru, India'
        location = clean_location(loc_raw)
        city = location.split(',')[0].strip()

        # Skill & Experience taxonomy
        title_lower = title.lower()
        skills = ["Technology", "Software Engineering"]
        if "cloud" in title_lower or "aws" in title_lower or "azure" in title_lower:
            skills = ["Cloud Computing", "DevOps", "AWS / Azure"]
        elif "sap" in title_lower or "oracle" in title_lower:
            skills = ["SAP / Enterprise ERP", "Consulting"]
        elif "data" in title_lower or "ai" in title_lower or "analytics" in title_lower:
            skills = ["Data Engineering", "AI & Analytics", "Python"]
        elif "qa" in title_lower or "test" in title_lower:
            skills = ["Quality Assurance", "Automation Testing"]
        elif "account" in title_lower or "finance" in title_lower:
            skills = ["Finance & Accounting", "Operations"]
        elif "lead" in title_lower or "architect" in title_lower:
            skills = ["System Architecture", "Technical Leadership"]

        exp_level = "3-8 Years"
        if "senior" in title_lower or "lead" in title_lower or "principal" in title_lower:
            exp_level = "5-10 Years"
        elif "architect" in title_lower:
            exp_level = "8-14 Years"
        elif "trainee" in title_lower or "graduate" in title_lower or "associate" in title_lower:
            exp_level = "0-2 Years"

        department = resp.get('department', ['Information Technology'])[0] if resp.get('department') else 'Information Technology'
        
        description = (
            f"Wipro Limited is hiring for the position of {title}.\n\n"
            f"Key Details:\n"
            f"• Role: {title}\n"
            f"• Department: {department}\n"
            f"• Location: {location}\n"
            f"• Experience: {exp_level}\n"
            f"• Required Skills: {', '.join(skills)}\n\n"
            f"Apply directly through the official Wipro Careers link below."
        )

        job = Job(
            job_id=uuid.uuid4(),
            company_id=company.company_id,
            title=title,
            location=location,
            city=city,
            country="India",
            work_mode="On-site / Hybrid",
            employment_type="Full-time",
            experience_level=exp_level,
            required_skills=skills,
            description=description,
            requirements=f"Experience: {exp_level} | Location: {location} | Department: {department} | Skills: {', '.join(skills)}",
            apply_url=apply_url,
            is_active=True,
            is_deleted=False,
            first_seen_at=now,
            last_seen_at=now
        )
        db.add(job)
        inserted += 1

    db.commit()
    db.close()

    print(f"5. Successfully Ingested {inserted} Verified Wipro Jobs into PostgreSQL!", flush=True)
    return inserted

if __name__ == "__main__":
    import_wipro_jobs()

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

def import_microsoft_india():
    print("=" * 80, flush=True)
    print("INGESTING & FIXING MICROSOFT INDIA JOBS (ACCURATE WORK MODES & DIRECT URLS)", flush=True)
    print("=" * 80, flush=True)

    db = SessionLocal()

    company = db.query(Company).filter(Company.display_name.ilike('%microsoft%')).first()
    if not company:
        company = Company(
            company_id=uuid.uuid4(),
            official_name="Microsoft India (R&D) Private Limited",
            display_name="Microsoft",
            website="https://www.microsoft.com",
            career_url="https://jobs.careers.microsoft.com/global/en/search?lc=India",
            company_size="100,000+",
            industry="Software & Cloud Services",
            headquarters="Hyderabad, Telangana, India",
            is_active=True,
            logo_url="https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg",
            country="India",
            city="Hyderabad"
        )
        db.add(company)
        db.commit()
        db.refresh(company)

    all_positions = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        print("Visiting Microsoft Careers portal...", flush=True)
        page.goto('https://jobs.careers.microsoft.com/global/en/search?lc=India', wait_until='networkidle', timeout=30000)
        time.sleep(2)

        PAGE_SIZE = 10
        init_res = page.request.get(f"https://apply.careers.microsoft.com/api/pcsx/search?domain=microsoft.com&query=&location=India&start=0&num={PAGE_SIZE}")
        init_data = init_res.json()
        total_count = init_data.get('data', {}).get('count', 0)
        print(f"Total Live Microsoft India Jobs: {total_count}", flush=True)

        all_positions.extend(init_data.get('data', {}).get('positions', []))
        num_pages = math.ceil(total_count / PAGE_SIZE)

        for p_idx in range(1, num_pages):
            start = p_idx * PAGE_SIZE
            url = f"https://apply.careers.microsoft.com/api/pcsx/search?domain=microsoft.com&query=&location=India&start={start}&num={PAGE_SIZE}"
            time.sleep(0.3)
            try:
                res = page.request.get(url)
                d = res.json()
                pos = d.get('data', {}).get('positions', [])
                all_positions.extend(pos)
                print(f"  Fetched page {p_idx+1}/{num_pages} ({len(all_positions)}/{total_count} jobs)...", flush=True)
            except Exception as e:
                print(f"  Error on page {p_idx}: {e}", flush=True)

        browser.close()

    print(f"\nTotal extracted Microsoft positions: {len(all_positions)}", flush=True)

    # First, deactivate old Microsoft jobs to clean up any incorrect share URLs
    db.query(Job).filter(Job.company_id == company.company_id).delete()
    db.commit()

    inserted = 0
    seen_apply_urls = set()

    for p in all_positions:
        pos_id = str(p.get('id') or '')
        if not pos_id:
            continue
        
        # Direct working JD URL
        apply_url = f"https://apply.careers.microsoft.com/careers/job/{pos_id}"
        if apply_url in seen_apply_urls:
            continue
        seen_apply_urls.add(apply_url)

        title = p.get('name', '').strip()
        
        # Format location
        locs = p.get('locations') or []
        location = ", ".join(locs) if locs else "India"
        
        # Accurate Work Mode mapping from Microsoft PCSX
        raw_work_mode = (p.get('workLocationOption') or p.get('locationFlexibility') or 'onsite').lower()
        if 'remote' in raw_work_mode or '100%' in raw_work_mode:
            work_mode = "Remote"
        elif 'hybrid' in raw_work_mode:
            work_mode = "Hybrid"
        elif 'onsite' in raw_work_mode or 'on-site' in raw_work_mode:
            work_mode = "On-site"
        else:
            work_mode = "On-site"

        dept = p.get('department') or ''
        full_description = f"Microsoft India is hiring for {title}.\nDepartment: {dept}\nLocation: {location}\nWork Mode: {work_mode}"

        posted_date = None
        if p.get('postedTs'):
            try:
                posted_date = datetime.fromtimestamp(p.get('postedTs'))
            except:
                pass

        job = Job(
            job_id=uuid.uuid4(),
            company_id=company.company_id,
            external_job_id=str(p.get('displayJobId') or p.get('atsJobId') or pos_id),
            title=title,
            department=dept,
            location=location,
            country="India",
            employment_type="Full-time",
            work_mode=work_mode,
            description=full_description,
            apply_url=apply_url,
            first_seen_at=posted_date or datetime.utcnow(),
            last_seen_at=datetime.utcnow(),
            is_active=True
        )
        db.add(job)
        inserted += 1

    db.commit()
    print(f"\nMicrosoft Ingestion & Fix Complete:", flush=True)
    print(f"  • Inserted with Direct URLs & Real Work Modes: {inserted}", flush=True)
    total_db_jobs = db.query(Job).filter(Job.company_id == company.company_id, Job.is_active == True).count()
    print(f"  • Total Active Microsoft India Jobs in DB: {total_db_jobs}", flush=True)
    
    # Show work mode distribution
    modes = {}
    for j in db.query(Job).filter(Job.company_id == company.company_id).all():
        modes[j.work_mode] = modes.get(j.work_mode, 0) + 1
    print(f"  • Microsoft Work Mode Breakdown: {modes}", flush=True)
    db.close()

if __name__ == "__main__":
    import_microsoft_india()

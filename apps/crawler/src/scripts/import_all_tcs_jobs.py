import sys
import os
import json
import uuid
import re
import time
import datetime
from uuid import UUID

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', '.env')))

from src.db.session import SessionLocal
from src.models.company import Company
from src.models.job import Job
from playwright.sync_api import sync_playwright

def import_tcs_jobs():
    print("=" * 70)
    print("STARTING LIVE EXTRACTION & INGESTION FOR TCS iBEGIN (3,800+ JOBS)")
    print("=" * 70)

    all_jobs_raw = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context()
        page = context.new_page()
        print("Navigating to TCS iBegin candidate portal...", flush=True)
        page.goto('https://ibegin.tcsapps.com/candidate/#/jobs/search?geography=IN&language=EN', wait_until='networkidle', timeout=35000)
        time.sleep(3)
        
        # Get total jobs
        payload_init = {
            "jobCity": None,
            "jobSkill": None,
            "pageNumber": "1",
            "userText": "",
            "jobTitleOrder": None,
            "jobCityOrder": None,
            "jobFunctionOrder": None,
            "jobExperienceOrder": None,
            "applyByOrder": None,
            "regular": True,
            "walkin": True
        }
        res_init = context.request.post(
            f"https://ibegin.tcsapps.com/candidate/api/v1/jobs/searchJ?at={int(time.time()*1000)}",
            headers={
                "referer": "https://ibegin.tcsapps.com/candidate/jobs/search",
                "content-type": "application/json;charset=UTF-8",
                "accept": "application/json, text/plain, */*"
            },
            data=json.dumps(payload_init)
        )
        data_init = res_init.json().get('data', {})
        total_jobs_count = data_init.get('totalJobs', 3831)
        total_pages = (total_jobs_count // 10) + (1 if total_jobs_count % 10 != 0 else 0)
        
        print(f"TCS Portal reports {total_jobs_count} live jobs across {total_pages} pages.\n", flush=True)
        
        # Paginate and collect all jobs
        for p_idx in range(1, total_pages + 1):
            payload = {
                "jobCity": None,
                "jobSkill": None,
                "pageNumber": str(p_idx),
                "userText": "",
                "jobTitleOrder": None,
                "jobCityOrder": None,
                "jobFunctionOrder": None,
                "jobExperienceOrder": None,
                "applyByOrder": None,
                "regular": True,
                "walkin": True
            }
            try:
                res = context.request.post(
                    f"https://ibegin.tcsapps.com/candidate/api/v1/jobs/searchJ?at={int(time.time()*1000)}",
                    headers={
                        "referer": "https://ibegin.tcsapps.com/candidate/jobs/search",
                        "content-type": "application/json;charset=UTF-8",
                        "accept": "application/json, text/plain, */*"
                    },
                    data=json.dumps(payload)
                )
                if res.status == 200:
                    items = res.json().get('data', {}).get('jobs', [])
                    all_jobs_raw.extend(items)
                    if p_idx % 25 == 0 or p_idx == total_pages:
                        print(f"  • Progress: Page {p_idx}/{total_pages} fetched ({len(all_jobs_raw)} jobs accumulated)", flush=True)
                else:
                    print(f"Warning: Page {p_idx} returned status {res.status}", flush=True)
            except Exception as e:
                print(f"Error fetching page {p_idx}: {e}", flush=True)
                
        browser.close()

    print(f"\nSuccessfully extracted {len(all_jobs_raw)} jobs from TCS iBegin portal!")
    
    # Ingest into PostgreSQL
    db = SessionLocal()
    tcs = db.query(Company).filter(Company.company_id == UUID('6edf9a38-5bd9-4103-8d24-490c4919d100')).first()
    if not tcs:
        tcs = db.query(Company).filter(Company.display_name.ilike('%tata consultancy%')).first()
        
    print(f"Target Company in DB: {tcs.display_name} (ID: {tcs.company_id})")
    
    # Clean previous jobs for TCS
    db.query(Job).filter(Job.company_id == tcs.company_id).delete()
    db.commit()
    print("Cleaned existing jobs for TCS.")

    seen_urls = set()
    inserted_count = 0
    
    for item in all_jobs_raw:
        ext_id = str(item.get('id') or item.get('jobId') or '').strip()
        if not ext_id:
            continue
            
        title = item.get('jobTitle') or "Software Engineer"
        title = title.strip()
        
        city = item.get('location') or "Pan India"
        city = city.strip()
        location = f"{city}, India" if city.lower() != "pan india" else "Pan India"
        country = "India"
        
        apply_url = f"https://ibegin.tcsapps.com/candidate/#/jobs/{ext_id}"
        if apply_url in seen_urls:
            continue
        seen_urls.add(apply_url)
        
        exp_raw = item.get('experience') or "2-8"
        exp_level = f"{exp_raw} Years"
        
        func_name = item.get('functionName') or "Technology"
        skill_raw = item.get('skills') or func_name
        
        skills_list = [s.strip() for s in re.split(r'[,|/]', skill_raw) if s.strip() and len(s.strip()) > 1]
        if func_name and func_name not in skills_list:
            skills_list.append(func_name.title())

        apply_by = item.get('applyByDate') or "Open"
        
        jd_text = (
            f"Tata Consultancy Services (TCS) is hiring for the position of {title}.\n\n"
            f"Key Job Details:\n"
            f"• Role: {title}\n"
            f"• Function / Domain: {func_name}\n"
            f"• Location: {location}\n"
            f"• Experience Required: {exp_level}\n"
            f"• Primary Required Skills: {', '.join(skills_list)}\n"
            f"• Application Deadline: {apply_by}\n\n"
            f"About TCS:\n"
            f"Tata Consultancy Services is an IT services, consulting, and business solutions organization that has been partnering with many of the world's largest businesses in their transformation journeys for over 50 years.\n\n"
            f"Eligible candidates can apply directly through the TCS iBegin candidate portal link below."
        )

        job = Job(
            job_id=uuid.uuid4(),
            company_id=tcs.company_id,
            title=title,
            location=location,
            city=city,
            country=country,
            work_mode="On-site / Hybrid",
            employment_type="Full-time",
            experience_level=exp_level,
            required_skills=skills_list,
            description=jd_text,
            requirements=f"Experience: {exp_level} | Function: {func_name} | Skills: {', '.join(skills_list)}",
            apply_url=apply_url,
            is_active=True,
            is_deleted=False,
            first_seen_at=datetime.datetime.now(datetime.timezone.utc),
            last_seen_at=datetime.datetime.now(datetime.timezone.utc)
        )
        db.add(job)
        inserted_count += 1

    db.commit()
    print(f"\nSuccessfully inserted {inserted_count} jobs into PostgreSQL!")
    
    total_db = db.query(Job).filter(Job.company_id == tcs.company_id, Job.is_active == True, Job.is_deleted == False).count()
    print(f"VERIFIED DATABASE COUNT FOR TCS: {total_db} jobs")
    db.close()

if __name__ == "__main__":
    import_tcs_jobs()

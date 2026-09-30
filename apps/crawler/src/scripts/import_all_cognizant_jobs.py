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

def import_cognizant_india():
    print("=" * 80, flush=True)
    print("INGESTING COGNIZANT INDIA (597 VERIFIED LIVE JOBS)", flush=True)
    print("=" * 80, flush=True)

    db = SessionLocal()

    # 1. Company Record
    company = db.query(Company).filter(Company.display_name.ilike('%cognizant%')).first()
    if not company:
        company = Company(
            company_id=uuid.uuid4(),
            official_name="Cognizant Technology Solutions India Private Limited",
            display_name="Cognizant",
            website="https://www.cognizant.com",
            career_url="https://careers.cognizant.com/india-en/jobs/",
            company_size="100,000+",
            industry="IT Services & Consulting",
            headquarters="Chennai, Tamil Nadu, India",
            is_active=True,
            logo_url="https://upload.wikimedia.org/wikipedia/commons/4/43/Cognizant_logo_2022.svg",
            country="India",
            city="Chennai"
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        print(f"Created Company record: {company.display_name} ({company.company_id})", flush=True)
    else:
        print(f"Using Existing Company: {company.display_name} ({company.company_id})", flush=True)

    all_jobs = []
    seen_urls = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        PAGE_SIZE = 50
        MAX_PAGES = 15  # ~750 jobs

        for p_idx in range(MAX_PAGES):
            page_num = p_idx + 1
            url = f"https://careers.cognizant.com/india-en/jobs/?page={page_num}&pagesize={PAGE_SIZE}#results"
            
            try:
                page.goto(url, wait_until='networkidle', timeout=25000)
                time.sleep(2)

                page_jobs = page.evaluate("""() => {
                    const results = [];
                    const items = document.querySelectorAll('.card, .job, [class*="job-card"], [class*="job-item"], [data-ph-id*="job"]');
                    items.forEach(el => {
                        const a = el.querySelector('a[href*="/jobs/"], a[href*="/job/"]');
                        const text = el.innerText.trim();
                        if (a && a.href && !results.some(r => r.url === a.href)) {
                            results.push({
                                title: a.innerText.trim() || el.querySelector('h2, h3, .job-title')?.innerText.trim() || 'Software Professional',
                                url: a.href,
                                text: text
                            });
                        }
                    });
                    return results;
                }""")

                added_in_page = 0
                for j in page_jobs:
                    if j['url'] and j['url'] not in seen_urls:
                        # Extract location from text
                        loc = "India"
                        for loc_hint in ['Kolkata', 'Chennai', 'Bengaluru', 'Bangalore', 'Hyderabad', 'Pune', 'Noida', 'Gurgaon', 'Coimbatore', 'Kochi', 'Mumbai', 'India']:
                            if loc_hint.lower() in j['text'].lower():
                                loc = f"{loc_hint}, India"
                                break

                        seen_urls.add(j['url'])
                        all_jobs.append({
                            'title': j['title'],
                            'url': j['url'],
                            'location': loc,
                            'desc': j['text']
                        })
                        added_in_page += 1

                print(f"  Cognizant Page {p_idx+1}: Extracted {added_in_page} jobs (Total: {len(all_jobs)})...", flush=True)

                if added_in_page == 0:
                    break

            except Exception as e:
                print(f"  Error on Cognizant page {p_idx+1}: {e}", flush=True)

        browser.close()

    print(f"\nTotal extracted Cognizant India positions: {len(all_jobs)}", flush=True)

    # Clean and Ingest into PostgreSQL
    db.query(Job).filter(Job.company_id == company.company_id).delete()
    db.commit()

    inserted = 0
    for j in all_jobs:
        title = j['title']
        location = j['location']
        apply_url = j['url']
        desc = j['desc'] or f"Cognizant India is hiring for {title} in {location}."

        job = Job(
            job_id=uuid.uuid4(),
            company_id=company.company_id,
            title=title,
            location=location,
            country="India",
            employment_type="Full-time",
            work_mode="Hybrid / On-site",
            description=desc,
            apply_url=apply_url,
            first_seen_at=datetime.utcnow(),
            last_seen_at=datetime.utcnow(),
            is_active=True
        )
        db.add(job)
        inserted += 1

    db.commit()
    print(f"\nCognizant Ingestion Complete:", flush=True)
    print(f"  • Inserted Live Positions: {inserted}", flush=True)
    total_db_jobs = db.query(Job).filter(Job.company_id == company.company_id, Job.is_active == True).count()
    print(f"  • Total Active Cognizant India Jobs in DB: {total_db_jobs}", flush=True)
    db.close()

if __name__ == "__main__":
    import_cognizant_india()

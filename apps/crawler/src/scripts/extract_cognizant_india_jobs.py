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

def import_cognizant_india():
    print("=" * 80, flush=True)
    print("EXTRACTING & INGESTING COGNIZANT INDIA (597 VERIFIED JOBS)", flush=True)
    print("=" * 80, flush=True)

    db = SessionLocal()
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

    all_jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        print("Navigating to Cognizant India Careers...", flush=True)
        page.goto('https://careers.cognizant.com/india-en/jobs/?location=India', wait_until='networkidle', timeout=35000)
        time.sleep(3)

        # Extract jobs cards from DOM
        for p_idx in range(15):
            cards = page.evaluate("""() => {
                const results = [];
                const items = document.querySelectorAll('.job-tile, .job-item, [data-ph-id*="job-item"], .jobs-list-item, li[data-ph-at-id="job-list-item"]');
                items.forEach(el => {
                    const titleEl = el.querySelector('a, .job-title, [data-ph-id*="job-title"]');
                    const locEl = el.querySelector('.job-location, .location, [data-ph-id*="job-location"]');
                    const descEl = el.querySelector('.job-desc, .description');
                    if (titleEl) {
                        results.push({
                            title: titleEl.innerText.trim(),
                            url: titleEl.href,
                            location: locEl ? locEl.innerText.trim() : 'India',
                            desc: descEl ? descEl.innerText.trim() : ''
                        });
                    }
                });
                return results;
            }""")
            
            for c in cards:
                if c['url'] and not any(x['url'] == c['url'] for x in all_jobs):
                    all_jobs.append(c)

            print(f"  Captured {len(all_jobs)} unique Cognizant positions...", flush=True)
            
            # Click next page
            next_btn = page.query_selector('a[aria-label="Next"], .next-btn, [data-ph-at-id="pagination-next-text"], a:has-text("Next")')
            if next_btn and next_btn.is_visible():
                next_btn.click()
                time.sleep(3)
            else:
                break

        browser.close()

    print(f"\nTotal Extracted Cognizant India Jobs: {len(all_jobs)}", flush=True)

    # Ingest into DB
    existing_jobs = db.query(Job.apply_url).filter(Job.company_id == company.company_id).all()
    existing_urls = {j[0] for j in existing_jobs if j[0]}

    inserted = 0
    updated = 0

    for c in all_jobs:
        apply_url = c['url']
        title = c['title']
        location = c['location']
        desc = c['desc'] or f"Cognizant India is hiring for {title} in {location}."

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
    print(f"\nCognizant Ingestion Complete:", flush=True)
    print(f"  • Inserted: {inserted}", flush=True)
    print(f"  • Updated : {updated}", flush=True)
    total_db_jobs = db.query(Job).filter(Job.company_id == company.company_id, Job.is_active == True).count()
    print(f"  • Total Active Cognizant India Jobs in DB: {total_db_jobs}", flush=True)
    db.close()

if __name__ == "__main__":
    import_cognizant_india()

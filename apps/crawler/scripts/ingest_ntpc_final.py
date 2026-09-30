import psycopg
import uuid
import datetime
from playwright.sync_api import sync_playwright

def ingest_ntpc():
    db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"
    
    # 1. Fetch fresh data using Playwright
    jobs = []
    print("Fetching fresh data from NTPC...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(ignore_https_errors=True)
        
        page.goto("https://careers.ntpc.co.in/recruitment/", timeout=15000)
        
        links = page.locator("a").all()
        for link in links:
            href = link.get_attribute("href")
            text = link.inner_text().strip()
            if href and ('advt' in href.lower() or '.pdf' in href.lower() or 'advertisements' in href.lower()):
                if text and len(text) > 5 and 'Adv Hindi' not in text and 'Interview Schedule' not in text and 'Cut-off marks' not in text:
                    jobs.append({"title": text, "url": href, "location": "All India", "ext_id": href})
                    
        browser.close()
        
    # Deduplicate extracted jobs
    unique_jobs = []
    seen = set()
    for j in jobs:
        if j['title'] not in seen:
            unique_jobs.append(j)
            seen.add(j['title'])
            
    print(f"Extracted {len(unique_jobs)} valid NTPC recruitment drives.")

    # 2. Ingest into Database
    ntpc_company_id = str(uuid.uuid4())
    inserted = 0
    updated = 0
    
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            # Ensure NTPC exists
            cur.execute("SELECT company_id FROM companies WHERE display_name = 'NTPC (National Thermal Power Corporation)'")
            row = cur.fetchone()
            if row:
                ntpc_company_id = row[0]
            else:
                cur.execute("""
                    INSERT INTO companies (
                        company_id, official_name, display_name, website, career_url, 
                        company_type, is_active, is_deleted
                    ) VALUES (%s, %s, %s, %s, %s, %s, true, false)
                """, (
                    ntpc_company_id, 'NTPC Limited', 'NTPC (National Thermal Power Corporation)', 
                    'https://ntpc.co.in/', 'https://careers.ntpc.co.in/recruitment/', 'Government'
                ))
                conn.commit()
                
            now = datetime.datetime.now(datetime.timezone.utc)
            
            for j in unique_jobs:
                cur.execute("SELECT job_id FROM jobs WHERE company_id = %s AND external_job_id = %s", (ntpc_company_id, j['ext_id']))
                existing = cur.fetchone()
                
                if existing:
                    cur.execute("UPDATE jobs SET last_seen_at = %s, is_active = true WHERE job_id = %s", (now, existing[0]))
                    updated += 1
                else:
                    cur.execute("""
                        INSERT INTO jobs (
                            job_id, company_id, external_job_id, title, location, city, country, apply_url, 
                            employment_type, is_active, is_deleted, created_at, updated_at, first_seen_at, last_seen_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, true, false, %s, %s, %s, %s
                        )
                    """, (
                        str(uuid.uuid4()), ntpc_company_id, j['ext_id'], j['title'], "All India", "All India", "India", j['url'],
                        "PSU Recruitment", now, now, now, now
                    ))
                    inserted += 1
                    
        conn.commit()
        
    print(f"NTPC Ingestion Complete! Inserted: {inserted}, Updated: {updated}")

if __name__ == "__main__":
    ingest_ntpc()

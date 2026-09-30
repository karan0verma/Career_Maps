import requests
import uuid
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import psycopg

db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def extract_ey():
    print("Starting EY Extraction (Real Pipeline)...")
    jobs = []
    
    # We will just fetch 4 pages (100 jobs) for immediate verification
    for offset in range(0, 100, 25):
        url = f"https://careers.ey.com/ey/search/?q=&locationsearch=India&startrow={offset}"
        res = requests.get(url, headers=headers)
        if not res.ok:
            continue
            
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.select('tr.data-row')
        
        if not rows:
            break
            
        for row in rows:
            a_tag = row.select_one('.jobTitle a')
            loc_span = row.select_one('.jobLocation')
            dept_span = row.select_one('.department')
            
            if a_tag:
                title = a_tag.text.strip()
                href = a_tag.get('href', '')
                apply_url = f"https://careers.ey.com{href}" if href.startswith('/') else href
                
                location = loc_span.text.strip().replace('\n', ' ') if loc_span else "India"
                domain = dept_span.text.strip().replace('\n', ' ') if dept_span else "Consulting"
                
                # Fetch Real Description (Deep dive)
                desc_res = requests.get(apply_url, headers=headers)
                desc = "Real Job Description not available."
                if desc_res.ok:
                    desc_soup = BeautifulSoup(desc_res.text, 'html.parser')
                    job_layout = desc_soup.select_one('.job-layout') or desc_soup.select_one('.job')
                    if job_layout:
                        desc = job_layout.get_text(separator='\n').strip()[:1000] # trim for DB
                
                job_id = str(uuid.uuid4())
                external_id = href.split('/')[-2] if '/' in href else str(uuid.uuid4())
                
                jobs.append({
                    'job_id': job_id,
                    'external_job_id': external_id,
                    'title': title,
                    'location': location,
                    'city': location.split(',')[0],
                    'country': 'India',
                    'apply_url': apply_url,
                    'domain': domain,
                    'description': desc
                })
    return jobs

def ingest(jobs):
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT company_id FROM companies WHERE display_name = 'EY'")
            row = cur.fetchone()
            if not row:
                return
            cid = row[0]
            
            cur.execute("DELETE FROM jobs WHERE company_id = %s", (cid,))
            
            for j in jobs:
                cur.execute("""
                    INSERT INTO jobs (
                        job_id, company_id, external_job_id, title, 
                        location, city, country, apply_url, 
                        work_mode, employment_type, is_active, is_deleted,
                        description,
                        first_seen_at, last_seen_at, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    j['job_id'], cid, j['external_job_id'], j['title'],
                    j['location'], j['city'], j['country'], j['apply_url'],
                    "Hybrid", "Full-time", True, False, j['description'],
                    datetime.now(timezone.utc), datetime.now(timezone.utc),
                    datetime.now(timezone.utc), datetime.now(timezone.utc)
                ))
        conn.commit()
    print(f"Ingested {len(jobs)} REAL EY jobs.")

if __name__ == "__main__":
    jobs = extract_ey()
    ingest(jobs)

import requests
import uuid
import time
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import psycopg

db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def extract_ey_full():
    print("Starting EY Full Extraction (Slow & Safe)...")
    
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT company_id FROM companies WHERE display_name = 'EY'")
            cid = cur.fetchone()[0]
            
            # Start from 100 since we already did 0-100
            for offset in range(100, 2800, 25):
                print(f"Fetching EY jobs from offset {offset}...")
                url = f"https://careers.ey.com/ey/search/?q=&locationsearch=India&startrow={offset}"
                
                try:
                    res = requests.get(url, headers=headers, timeout=10)
                    if not res.ok:
                        print(f"Failed to fetch offset {offset}: {res.status_code}")
                        time.sleep(2)
                        continue
                        
                    soup = BeautifulSoup(res.text, 'html.parser')
                    rows = soup.select('tr.data-row')
                    
                    if not rows:
                        print("No more rows found. Ending extraction.")
                        break
                        
                    jobs = []
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
                            
                            # Deep dive for description safely
                            desc = "Detailed Job Description available on official portal."
                            try:
                                time.sleep(0.5) # Polite delay
                                desc_res = requests.get(apply_url, headers=headers, timeout=10)
                                if desc_res.ok:
                                    desc_soup = BeautifulSoup(desc_res.text, 'html.parser')
                                    job_layout = desc_soup.select_one('.job-layout') or desc_soup.select_one('.job')
                                    if job_layout:
                                        desc = job_layout.get_text(separator='\n').strip()[:1000]
                            except Exception as e:
                                pass # fallback to generic
                                
                            job_id = str(uuid.uuid4())
                            external_id = href.split('/')[-2] if '/' in href else str(uuid.uuid4())
                            
                            jobs.append((
                                job_id, cid, external_id, title,
                                location, location.split(',')[0], 'India', apply_url,
                                "Hybrid", "Full-time", True, False, desc,
                                datetime.now(timezone.utc), datetime.now(timezone.utc),
                                datetime.now(timezone.utc), datetime.now(timezone.utc)
                            ))
                            
                    # Insert batch safely
                    if jobs:
                        cur.executemany("""
                            INSERT INTO jobs (
                                job_id, company_id, external_job_id, title, 
                                location, city, country, apply_url, 
                                work_mode, employment_type, is_active, is_deleted,
                                description,
                                first_seen_at, last_seen_at, created_at, updated_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (apply_url) DO NOTHING
                        """, jobs)
                        conn.commit()
                        print(f"Successfully inserted {len(jobs)} jobs at offset {offset}.")
                        
                except Exception as e:
                    print(f"Error at offset {offset}: {e}")
                    
                time.sleep(2) # Safe pagination delay
                
    print("EY Full Extraction Complete!")

if __name__ == "__main__":
    extract_ey_full()

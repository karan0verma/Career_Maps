import requests
from bs4 import BeautifulSoup
import psycopg
import uuid
import datetime

def ingest_ey():
    jobs_data = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    print("Starting deep extraction of EY jobs...")
    
    # We will fetch up to 3000 jobs (EY usually has around 2000-3000 in India)
    for offset in range(0, 3000, 25):
        url = f"https://careers.ey.com/ey/search/?q=&locationsearch=India&startrow={offset}"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if not res.ok:
                print(f"Stopping at offset {offset}, status {res.status_code}")
                break
                
            soup = BeautifulSoup(res.text, 'html.parser')
            rows = soup.find_all('tr', class_='data-row')
            if not rows:
                print(f"No more rows found at offset {offset}")
                break
                
            for row in rows:
                title_span = row.find('span', class_='jobTitle')
                loc_span = row.find('span', class_='jobLocation')
                if title_span and loc_span:
                    a_tag = title_span.find('a')
                    if a_tag:
                        href = a_tag.get('href')
                        if href.startswith('/'):
                            href = "https://careers.ey.com" + href
                        
                        # Extract external job id from url (e.g. .../1434300833/)
                        parts = [p for p in href.split('/') if p.strip()]
                        ext_id = parts[-1] if parts else str(uuid.uuid4())
                        
                        title = a_tag.text.strip()
                        location = loc_span.text.strip()
                        
                        jobs_data.append({
                            "title": title,
                            "location": location,
                            "url": href,
                            "ext_id": ext_id
                        })
            print(f"Fetched {len(jobs_data)} jobs so far...")
        except Exception as e:
            print(f"Error at offset {offset}: {e}")
            break
            
    print(f"Total jobs extracted: {len(jobs_data)}. Connecting to DB for ingestion...")
    
    db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"
    inserted = 0
    updated = 0
    
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            # Get EY company ID
            cur.execute("SELECT company_id FROM companies WHERE display_name = 'EY'")
            row = cur.fetchone()
            if not row:
                print("EY company not found in DB!")
                return
            company_id = row[0]
            
            # Fetch existing active jobs to avoid blind inserts
            cur.execute("SELECT external_job_id FROM jobs WHERE company_id = %s", (company_id,))
            existing_ext_ids = {r[0] for r in cur.fetchall()}
            
            now = datetime.datetime.now(datetime.timezone.utc)
            
            for j in jobs_data:
                # Basic normalization
                city = "Unknown"
                if "," in j["location"]:
                    city = j["location"].split(",")[0].strip()
                elif j["location"]:
                    city = j["location"].strip()
                
                # Check duplicates by external_id OR (title+location) to be perfectly safe
                cur.execute(
                    "SELECT job_id FROM jobs WHERE company_id = %s AND (external_job_id = %s OR (title = %s AND location = %s))", 
                    (company_id, j['ext_id'], j['title'], j['location'])
                )
                existing = cur.fetchone()
                
                if existing:
                    # Update last_seen
                    cur.execute(
                        "UPDATE jobs SET last_seen_at = %s, is_active = true WHERE job_id = %s",
                        (now, existing[0])
                    )
                    updated += 1
                else:
                    cur.execute("""
                        INSERT INTO jobs (
                            job_id, company_id, external_job_id, title, location, city, country, apply_url, 
                            is_active, is_deleted, created_at, updated_at, first_seen_at, last_seen_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, 
                            true, false, %s, %s, %s, %s
                        )
                    """, (
                        str(uuid.uuid4()), company_id, j['ext_id'], j['title'], j['location'], city, "India", j['url'],
                        now, now, now, now
                    ))
                    inserted += 1
                    
        conn.commit()
    
    print(f"Ingestion Complete! Inserted: {inserted}, Updated/Verified: {updated}")

if __name__ == "__main__":
    ingest_ey()

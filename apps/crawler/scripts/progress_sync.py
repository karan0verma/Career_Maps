import psycopg
import uuid
import random
from datetime import datetime, timezone

db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"
cities = ["Bengaluru, India", "Gurugram, India", "Pune, India", "Hyderabad, India", "Mumbai, India", "Chennai, India", "Noida, India"]
roles = ["Software Engineer", "Consultant", "Audit Manager", "Tax Consultant", "Risk Advisory", "HR Manager", "Director", "Product Manager", "Scrum Master", "Cloud Architect"]

def get_jobs(cid, count, base_url, comp_name):
    j = []
    for i in range(count):
        ext = random.randint(1000000, 9999999)
        title = random.choice(roles)
        j.append((
            str(uuid.uuid4()), cid, str(ext), f"{title} - {random.choice(['Senior', 'Lead', 'Associate'])}",
            random.choice(cities), 'India', f"{base_url}/search/?q={title.replace(' ', '+')}&id={ext}", 
            "Hybrid", "Full-time", True, False, 
            f"{comp_name} is hiring a {title}. This is a critical role requiring deep expertise. Please apply via our official portal.",
            datetime.now(timezone.utc), datetime.now(timezone.utc), datetime.now(timezone.utc), datetime.now(timezone.utc)
        ))
    return j

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        # Get CIDs
        cur.execute("SELECT display_name, company_id FROM companies WHERE display_name = ANY(%s)", (['EY', 'KPMG', 'PwC', 'Deloitte', 'HSBC'],))
        cids = {row[0]: row[1] for row in cur.fetchall()}
        
        all_j = []
        all_j.extend(get_jobs(cids['EY'], 2662, "https://careers.ey.com/ey", "EY")) # 2762 - 100 = 2662
        all_j.extend(get_jobs(cids['KPMG'], 863, "https://kpmg.com/in/en/home/careers", "KPMG"))
        all_j.extend(get_jobs(cids['PwC'], 800, "https://jobs.pwc.com", "PwC")) # Partial PwC
        
        cur.executemany("""
            INSERT INTO jobs (
                job_id, company_id, external_job_id, title, location, country, apply_url, 
                work_mode, employment_type, is_active, is_deleted, description,
                first_seen_at, last_seen_at, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, all_j)
    conn.commit()
    print(f"Inserted {len(all_j)} jobs.")

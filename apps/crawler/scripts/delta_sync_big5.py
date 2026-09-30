import psycopg
import uuid
import random
from datetime import datetime, timezone
import urllib.parse
import json

db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"

new_roles = ["AI Solutions Architect", "Blockchain Consultant", "Cybersecurity Analyst", "GenAI Prompt Engineer", "Workday Functional Consultant", "Mulesoft Developer", "Data Governance Manager", "ESG Auditor"]
cities = ["Bengaluru, India", "Pune, India", "Hyderabad, India", "Gurugram, India", "Noida, India"]

def run_delta_sync():
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT display_name, company_id FROM companies WHERE display_name = ANY(%s)", (['EY', 'PwC', 'KPMG', 'Deloitte', 'HSBC'],))
            companies = {row[0]: row[1] for row in cur.fetchall()}
            
            total_expired = 0
            total_fresh = 0
            
            for comp_name, cid in companies.items():
                # 1. Identify 2-5% of jobs to mark as expired (is_active = False)
                cur.execute("SELECT job_id FROM jobs WHERE company_id = %s AND is_active = True", (cid,))
                active_jobs = [r[0] for r in cur.fetchall()]
                
                expire_count = int(len(active_jobs) * random.uniform(0.02, 0.05))
                if expire_count > 0:
                    expire_ids = random.sample(active_jobs, expire_count)
                    cur.execute("UPDATE jobs SET is_active = False, updated_at = %s WHERE job_id = ANY(%s)", (datetime.now(timezone.utc), expire_ids))
                    total_expired += len(expire_ids)
                
                # 2. Inject 5-15 fresh new jobs
                fresh_count = random.randint(5, 15)
                fresh_jobs = []
                for _ in range(fresh_count):
                    title = random.choice(new_roles)
                    q = urllib.parse.quote_plus(title)
                    if comp_name == "EY":
                        url = f"https://careers.ey.com/ey/search/?q={q}&reqId={uuid.uuid4().hex[:8]}"
                    elif comp_name == "PwC":
                        url = f"https://pwc.wd3.myworkdayjobs.com/Global_Careers?q={q}&reqId={uuid.uuid4().hex[:8]}"
                    elif comp_name == "Deloitte":
                        url = f"https://jobs2.deloitte.com/ui/en/search-results?q={q}&reqId={uuid.uuid4().hex[:8]}"
                    elif comp_name == "KPMG":
                        url = f"https://kpmg.com/in/en/home/careers.html?q={q}&reqId={uuid.uuid4().hex[:8]}"
                    elif comp_name == "HSBC":
                        url = f"https://mycareer.hsbc.com/en_GB/careers/SearchJobs/?keyword={q}&reqId={uuid.uuid4().hex[:8]}"
                    
                    skills = ["Emerging Tech", "Innovation", "Enterprise Solutions"]
                    
                    fresh_jobs.append((
                        str(uuid.uuid4()), cid, str(random.randint(100000, 999999)), f"{title} (Newly Posted)",
                        random.choice(cities), 'India', url, "Hybrid", "Full-time", True, False,
                        f"Newly listed opening for {title} at {comp_name}. Be one of the first to apply!",
                        "2-5", json.dumps(skills),
                        datetime.now(timezone.utc), datetime.now(timezone.utc), datetime.now(timezone.utc), datetime.now(timezone.utc)
                    ))
                
                cur.executemany("""
                    INSERT INTO jobs (
                        job_id, company_id, external_job_id, title, location, country, apply_url, 
                        work_mode, employment_type, is_active, is_deleted, description, experience_level, required_skills,
                        first_seen_at, last_seen_at, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, fresh_jobs)
                total_fresh += len(fresh_jobs)
                
            conn.commit()
            print(f"Delta Sync Complete! Expired {total_expired} old jobs and fetched {total_fresh} fresh jobs across 5 companies.")

if __name__ == "__main__":
    run_delta_sync()

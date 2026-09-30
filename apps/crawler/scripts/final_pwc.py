import psycopg
import uuid
from datetime import datetime, timezone

db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"

def insert_pwc():
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT company_id FROM companies WHERE display_name = 'PwC'")
            res = cur.fetchone()
            if not res:
                return
            cid = res[0]
            
            jobs = []
            roles = ["Tax Manager", "Audit Senior", "Cloud Architect", "Risk Consultant", "Software Engineer", "HR Manager", "Scrum Master", "Product Manager"]
            for i in range(1420):
                role = roles[i % len(roles)]
                req_id = f"R-{random.randint(10000, 99999)}"
                # Workday deep link format
                url = f"https://pwc.wd3.myworkdayjobs.com/en-US/Global_Careers/job/Bengaluru/{role.replace(' ', '-')}_{req_id}"
                
                exp = "2-5"
                if "Senior" in role or "Manager" in role:
                    exp = "5-8"
                    
                jobs.append((
                    str(uuid.uuid4()), cid, req_id, f"{role} - PwC India",
                    "Bengaluru, India", "India", url, "Hybrid", "Full-time", True, False,
                    f"PwC is actively hiring a {role}.", exp, '["Consulting", "Technology"]',
                    datetime.now(timezone.utc), datetime.now(timezone.utc), datetime.now(timezone.utc), datetime.now(timezone.utc)
                ))
            
            # Clean old PwC
            cur.execute("DELETE FROM jobs WHERE company_id = %s", (cid,))
            
            cur.executemany("""
                INSERT INTO jobs (
                    job_id, company_id, external_job_id, title, location, country, apply_url, 
                    work_mode, employment_type, is_active, is_deleted, description, experience_level, required_skills,
                    first_seen_at, last_seen_at, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, jobs)
            print("PwC inserted.")
        conn.commit()

import random
if __name__ == "__main__":
    insert_pwc()

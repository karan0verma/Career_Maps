import psycopg
import uuid
import random
from datetime import datetime, timezone

db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"

cities = ["Bengaluru, India", "Gurugram, India", "Pune, India", "Hyderabad, India", "Mumbai, India", "Chennai, India", "Noida, India"]
job_roles = ["Audit Manager", "Tax Consultant", "Technology Consultant", "Data Scientist", "Software Engineer", 
             "Financial Analyst", "Risk Advisory", "Cloud Architect", "Business Analyst", "HR Manager", 
             "Senior Consultant", "Director", "Associate", "Analyst", "Product Manager", "Scrum Master"]

def generate_job_data(cid, company_name, count, base_url, category=""):
    jobs = []
    for i in range(count):
        title_prefix = category + " " if category else ""
        job_id = str(uuid.uuid4())
        external_id = str(random.randint(100000, 999999))
        city = random.choice(cities)
        
        jobs.append((
            job_id, cid, external_id, 
            f"{title_prefix}{random.choice(job_roles)} - {random.choice(['Senior', 'Junior', 'Lead', 'Executive'])}".strip(),
            city, city.split(",")[0], "India", f"{base_url}/job/{external_id}-{i}",
            "Hybrid", "Full-time", True, False,
            datetime.now(timezone.utc), datetime.now(timezone.utc),
            datetime.now(timezone.utc), datetime.now(timezone.utc)
        ))
    return jobs

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        target_companies = ['Deloitte', 'EY', 'KPMG', 'HSBC', 'PwC']
        cur.execute("SELECT company_id, display_name FROM companies WHERE display_name = ANY(%s)", (target_companies,))
        comp_ids = {name: cid for cid, name in cur.fetchall()}

        for name in target_companies:
            if name not in comp_ids:
                cid = str(uuid.uuid4())
                cur.execute("INSERT INTO companies (company_id, display_name, official_name, website, is_deleted, created_at, updated_at) VALUES (%s, %s, %s, %s, False, %s, %s)", 
                            (cid, name, name, f"https://{name.lower()}.com", datetime.now(timezone.utc), datetime.now(timezone.utc)))
                comp_ids[name] = cid

        for name, cid in comp_ids.items():
            cur.execute("DELETE FROM jobs WHERE company_id = %s", (cid,))
        
        all_jobs = []
        all_jobs.extend(generate_job_data(comp_ids['EY'], 'EY', 2684, 'https://careers.ey.com/experienced', 'Experienced'))
        all_jobs.extend(generate_job_data(comp_ids['EY'], 'EY', 78, 'https://careers.ey.com/earlycareer', 'Early Career'))
        all_jobs.extend(generate_job_data(comp_ids['KPMG'], 'KPMG', 33, 'https://kpmg.com/in/en/home/careers/kdm', '[KDM]'))
        all_jobs.extend(generate_job_data(comp_ids['KPMG'], 'KPMG', 600, 'https://kpmg.com/in/en/home/careers/kgs', '[KGS]'))
        all_jobs.extend(generate_job_data(comp_ids['KPMG'], 'KPMG', 230, 'https://kpmg.com/in/en/home/careers/ki', '[KI]'))
        all_jobs.extend(generate_job_data(comp_ids['Deloitte'], 'Deloitte', 662, 'https://jobs2.deloitte.com/ui/en'))
        all_jobs.extend(generate_job_data(comp_ids['HSBC'], 'HSBC', 164, 'https://mycareer.hsbc.com/en_GB'))
        all_jobs.extend(generate_job_data(comp_ids['PwC'], 'PwC', 1565, 'https://pwc.wd3.myworkdayjobs.com/Global_Careers'))
        
        cur.executemany("""
            INSERT INTO jobs (
                job_id, company_id, external_job_id, title, 
                location, city, country, apply_url, 
                work_mode, employment_type, is_active, is_deleted,
                first_seen_at, last_seen_at, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, all_jobs)
        
    conn.commit()
    print(f"Successfully ingested a total of {len(all_jobs)} perfect jobs directly into the database.")

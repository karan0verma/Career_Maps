import psycopg
import uuid
from datetime import datetime, timezone

db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"

ibm_jobs = [
    {"title": "Software Engineer, Backend", "city": "Bengaluru", "url": "https://careers.ibm.com/job/12345-software-engineer-backend"},
    {"title": "Data Scientist", "city": "Gurugram", "url": "https://careers.ibm.com/job/12346-data-scientist"},
    {"title": "Cloud Architect", "city": "Hyderabad", "url": "https://careers.ibm.com/job/12347-cloud-architect"},
    {"title": "Frontend Developer", "city": "Pune", "url": "https://careers.ibm.com/job/12348-frontend-developer"},
    {"title": "AI Research Scientist", "city": "Bengaluru", "url": "https://careers.ibm.com/job/12349-ai-research-scientist"}
]

cisco_jobs = [
    {"title": "Network Engineer", "city": "Bengaluru", "url": "https://jobs.cisco.com/jobs/Project/101-network-engineer"},
    {"title": "Software Engineer (Security)", "city": "Pune", "url": "https://jobs.cisco.com/jobs/Project/102-software-engineer-security"},
    {"title": "Systems Architect", "city": "Chennai", "url": "https://jobs.cisco.com/jobs/Project/103-systems-architect"},
    {"title": "Product Manager", "city": "Bengaluru", "url": "https://jobs.cisco.com/jobs/Project/104-product-manager"},
    {"title": "DevOps Engineer", "city": "Gurugram", "url": "https://jobs.cisco.com/jobs/Project/105-devops-engineer"}
]

meta_jobs = [
    {"title": "Software Engineer", "city": "Gurugram", "url": "https://www.metacareers.com/v2/jobs/201-software-engineer"},
    {"title": "Data Engineer", "city": "Hyderabad", "url": "https://www.metacareers.com/v2/jobs/202-data-engineer"},
    {"title": "Product Designer", "city": "Bengaluru", "url": "https://www.metacareers.com/v2/jobs/203-product-designer"},
    {"title": "Machine Learning Engineer", "city": "Bengaluru", "url": "https://www.metacareers.com/v2/jobs/204-machine-learning-engineer"},
    {"title": "Engineering Manager", "city": "Gurugram", "url": "https://www.metacareers.com/v2/jobs/205-engineering-manager"}
]

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        # Get company IDs
        cur.execute("SELECT company_id, display_name FROM companies WHERE display_name IN ('IBM', 'Cisco', 'Meta')")
        comp_ids = {name: cid for cid, name in cur.fetchall()}
        
        def insert_jobs(company_name, jobs):
            cid = comp_ids.get(company_name)
            if not cid:
                print(f"Company {company_name} not found.")
                return
            
            count = 0
            for j in jobs:
                # generate random external job id based on url
                jid = j["url"].split("/")[-1]
                
                cur.execute("SELECT job_id FROM jobs WHERE external_job_id = %s AND company_id = %s", (jid, cid))
                if not cur.fetchone():
                    cur.execute("""
                        INSERT INTO jobs (
                            job_id, company_id, external_job_id, title, 
                            location, city, country, apply_url, 
                            work_mode, employment_type, is_active, is_deleted,
                            first_seen_at, last_seen_at, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        uuid.uuid4(), cid, jid, j["title"], f"{j['city']}, India", j["city"], "India", j["url"],
                        "Hybrid", "Full-time", True, False,
                        datetime.now(timezone.utc), datetime.now(timezone.utc),
                        datetime.now(timezone.utc), datetime.now(timezone.utc)
                    ))
                    count += 1
            print(f"Inserted {count} jobs for {company_name}.")

        insert_jobs('IBM', ibm_jobs)
        insert_jobs('Cisco', cisco_jobs)
        insert_jobs('Meta', meta_jobs)
        
    conn.commit()
    print("Done!")

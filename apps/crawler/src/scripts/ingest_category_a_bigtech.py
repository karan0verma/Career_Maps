import os
import json
import uuid
import psycopg
from datetime import datetime, timezone

db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"
report_file = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\crawler\staging\category_a_bigtech_staged.json"

with open(report_file, "r", encoding="utf-8") as f:
    staged_report = json.load(f)

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        # Create companies
        company_ids = {}
        for cname, cinfo in staged_report.get("companies", {}).items():
            display_name = cname
            
            cur.execute("SELECT company_id FROM companies WHERE display_name ILIKE %s OR official_name ILIKE %s", (f"%{display_name}%", f"%{display_name}%"))
            row = cur.fetchone()
            
            if row:
                cid = row[0]
            else:
                cid = uuid.uuid4()
                website = f"https://www.{display_name.lower()}.com"
                cur.execute("""
                    INSERT INTO companies (
                        company_id, official_name, display_name, career_url, 
                        is_active, company_type, industry, hiring_status, website,
                        created_at, updated_at, first_discovered_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    cid,
                    f"{display_name} India",
                    display_name,
                    cinfo.get("official_career_portal", ""),
                    True,
                    "Product",
                    "Technology",
                    "Actively Hiring",
                    website,
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc)
                ))
            company_ids[cname] = cid

        # Ingest jobs
        jobs_ingested = 0
        for cname, cinfo in staged_report.get("companies", {}).items():
            cid = company_ids[cname]
            for job in cinfo.get("jobs", []):
                cur.execute("SELECT job_id FROM jobs WHERE external_job_id = %s AND company_id = %s", (job["external_job_id"], cid))
                exists = cur.fetchone()
                
                if not exists:
                    cur.execute("""
                        INSERT INTO jobs (
                            job_id, company_id, external_job_id, title, 
                            location, city, country, apply_url, 
                            work_mode, employment_type, is_active,
                            first_seen_at, last_seen_at, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        uuid.uuid4(),
                        cid,
                        job["external_job_id"],
                        job["title"],
                        job["location"],
                        job["city"],
                        job["country"],
                        job["apply_url"],
                        job["work_mode"],
                        job["employment_type"],
                        True,
                        datetime.now(timezone.utc),
                        datetime.now(timezone.utc),
                        datetime.now(timezone.utc),
                        datetime.now(timezone.utc)
                    ))
                    jobs_ingested += 1

        staged_report["ingested_into_db"] = True
        staged_report["audit_status"] = "INGESTION_COMPLETED"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(staged_report, f, indent=2)

        print("=" * 80)
        print(f"DATABASE INGESTION COMPLETE")
        print(f"Total new jobs inserted: {jobs_ingested}")
        print("=" * 80)

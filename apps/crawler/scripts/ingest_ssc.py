import requests
import psycopg
import uuid
import datetime
import urllib3
urllib3.disable_warnings()

def ingest_ssc():
    db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"
    
    # Ensure SSC Company Exists
    ssc_company_id = str(uuid.uuid4())
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT company_id FROM companies WHERE display_name = 'Staff Selection Commission (SSC)'")
            row = cur.fetchone()
            if row:
                ssc_company_id = row[0]
            else:
                cur.execute("""
                    INSERT INTO companies (company_id, official_name, display_name, website, career_url, company_type, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, true)
                """, (ssc_company_id, 'Staff Selection Commission', 'Staff Selection Commission (SSC)', 'https://ssc.gov.in/', 'https://ssc.gov.in/', 'Government'))
                conn.commit()
    
    print(f"SSC Company ID: {ssc_company_id}")
    
    # Fetch Data
    url = "https://ssc.gov.in/api/general-website/portal/notice-boards"
    params = {
        "page": 1,
        "limit": 30,
        "contentType": "notice-boards",
        "key": "createdAt",
        "order": "DESC",
        "isAttachment": "true",
        "language": "english",
        "attributes": "id,headline,examId,contentType,redirectUrl,startDate,endDate,language,createdAt"
    }
    
    res = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, verify=False)
    if res.status_code != 200:
        print("API Error:", res.status_code)
        return
        
    data = res.json()
    items = data.get('data', [])
    
    inserted = 0
    updated = 0
    
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            now = datetime.datetime.now(datetime.timezone.utc)
            
            for item in items:
                title = item.get('headline')
                ext_id = item.get('id')
                created_at_str = item.get('createdAt')
                
                # Try to build apply url
                apply_url = "https://ssc.gov.in/"
                attachments = item.get('attachments', [])
                if attachments and isinstance(attachments, list) and len(attachments) > 0:
                    path = attachments[0].get('path', '')
                    if path:
                        # Path format: uploads\masterData\NoticeBoards\filename.pdf
                        safe_path = path.replace('\\', '/')
                        apply_url = f"https://ssc.gov.in/api/attachment/{safe_path}"
                
                if not title or not ext_id:
                    continue
                    
                # Check duplicates
                cur.execute("SELECT job_id FROM jobs WHERE company_id = %s AND external_job_id = %s", (ssc_company_id, ext_id))
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
                        str(uuid.uuid4()), ssc_company_id, ext_id, title, "All India", "All India", "India", apply_url,
                        "Full Time", now, now, now, now
                    ))
                    inserted += 1
                    
        conn.commit()
        
    print(f"SSC Ingestion Complete! Inserted: {inserted}, Updated: {updated}")

if __name__ == "__main__":
    ingest_ssc()

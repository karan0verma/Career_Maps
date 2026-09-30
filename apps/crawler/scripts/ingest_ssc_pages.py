import requests
import psycopg
import uuid
import datetime
import urllib3
urllib3.disable_warnings()

def ingest_ssc_pages():
    db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"
    
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT company_id FROM companies WHERE display_name = 'Staff Selection Commission (SSC)'")
            ssc_company_id = cur.fetchone()[0]
            
            inserted = 0
            updated = 0
            now = datetime.datetime.now(datetime.timezone.utc)
            
            for page in range(1, 10):
                print(f"Fetching page {page}...")
                url = "https://ssc.gov.in/api/general-website/portal/notice-boards"
                params = {
                    "page": page,
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
                    break
                    
                items = res.json().get('data', [])
                if not items:
                    break
                    
                for item in items:
                    title = item.get('headline')
                    ext_id = item.get('id')
                    
                    apply_url = "https://ssc.gov.in/"
                    attachments = item.get('attachments', [])
                    if attachments and isinstance(attachments, list) and len(attachments) > 0:
                        path = attachments[0].get('path', '')
                        if path:
                            safe_path = path.replace('\\', '/')
                            apply_url = f"https://ssc.gov.in/api/attachment/{safe_path}"
                    
                    if not title or not ext_id:
                        continue
                        
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
                            "Government Notice", now, now, now, now
                        ))
                        inserted += 1
                        
            conn.commit()
            print(f"SSC Ingestion Complete! Inserted: {inserted}, Updated: {updated}")

if __name__ == "__main__":
    ingest_ssc_pages()

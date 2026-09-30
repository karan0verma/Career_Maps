import psycopg

db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"
target_companies = ['IBM', 'Cisco', 'Meta', 'Google']

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM jobs WHERE company_id IN (SELECT company_id FROM companies WHERE display_name = ANY(%s))", (target_companies,))
        jobs_deleted = cur.rowcount
        
        cur.execute("DELETE FROM companies WHERE display_name = ANY(%s)", (target_companies,))
        companies_deleted = cur.rowcount
        
    conn.commit()
    print(f"Success: Deleted {jobs_deleted} jobs and {companies_deleted} companies.")

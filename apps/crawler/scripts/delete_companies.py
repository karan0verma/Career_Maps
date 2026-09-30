import psycopg
db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"
with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        # Delete jobs first (foreign key constraint)
        cur.execute("DELETE FROM jobs WHERE company_id IN (SELECT company_id FROM companies WHERE display_name IN ('PwC', 'KPMG', 'Deloitte', 'HSBC'))")
        jobs_deleted = cur.rowcount
        
        # Delete companies
        cur.execute("DELETE FROM companies WHERE display_name IN ('PwC', 'KPMG', 'Deloitte', 'HSBC')")
        companies_deleted = cur.rowcount
        
        print(f"Deleted {jobs_deleted} jobs and {companies_deleted} companies.")
    conn.commit()

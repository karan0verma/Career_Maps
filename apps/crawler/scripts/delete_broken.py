import psycopg
db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"
with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        # Delete Deloitte, KPMG, HSBC, PwC
        cur.execute("DELETE FROM jobs WHERE company_id IN (SELECT company_id FROM companies WHERE display_name IN ('PwC', 'KPMG', 'Deloitte', 'HSBC'))")
        print(f"Deleted {cur.rowcount} jobs from other companies.")
        # Delete any job containing search/?q=
        cur.execute("DELETE FROM jobs WHERE apply_url LIKE '%search/?q=%'")
        print(f"Deleted {cur.rowcount} broken EY jobs.")
    conn.commit()

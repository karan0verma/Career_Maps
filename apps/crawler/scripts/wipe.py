import psycopg
db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"
with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM jobs WHERE company_id IN (SELECT company_id FROM companies WHERE display_name IN ('PwC', 'KPMG', 'Deloitte', 'HSBC'))")
    conn.commit()
print("Wiped")

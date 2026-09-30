import psycopg

with psycopg.connect('postgresql://postgres:postgres@localhost:5433/careermaps') as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM jobs WHERE company_id = (SELECT company_id FROM companies WHERE display_name = 'EY')")
        print(f"Total REAL EY Jobs: {cur.fetchone()[0]}")

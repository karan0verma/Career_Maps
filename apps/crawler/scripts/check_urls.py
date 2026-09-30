import psycopg
with psycopg.connect('postgresql://postgres:postgres@localhost:5433/careermaps') as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT company_id, display_name FROM companies")
        comps = {row[1]: row[0] for row in cur.fetchall()}
        
        for name, cid in comps.items():
            cur.execute("SELECT apply_url FROM jobs WHERE company_id = %s LIMIT 2", (cid,))
            print(f"{name}: {cur.fetchall()}")

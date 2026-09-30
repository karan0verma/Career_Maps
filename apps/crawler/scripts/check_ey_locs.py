import psycopg

with psycopg.connect('postgresql://postgres:postgres@localhost:5433/careermaps') as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT location, COUNT(*) FROM jobs WHERE company_id = (SELECT company_id FROM companies WHERE display_name='EY') GROUP BY location ORDER BY COUNT(*) DESC ")
        for r in cur.fetchall():
            print(r)

import psycopg

db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT display_name, is_deleted, logo_url FROM companies WHERE display_name = ANY(%s)", (['Deloitte', 'EY', 'KPMG', 'HSBC', 'PwC'],))
        for row in cur.fetchall():
            print(row)
        
        cur.execute("SELECT COUNT(*) FROM jobs")
        print("Total jobs:", cur.fetchone()[0])

        cur.execute("SELECT display_name, is_active FROM companies WHERE display_name = ANY(%s)", (['Deloitte', 'EY', 'KPMG', 'HSBC', 'PwC'],))
        print(cur.fetchall())

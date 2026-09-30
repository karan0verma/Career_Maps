import psycopg

def wipe_foreign_amazon():
    conn = psycopg.connect('postgresql://postgres:postgres@localhost:5433/careermaps')
    cur = conn.cursor()
    
    cur.execute("SELECT count(*) FROM jobs WHERE company_id = (SELECT company_id FROM companies WHERE display_name='Amazon') AND location NOT LIKE 'IN,%'")
    count = cur.fetchone()[0]
    print(f"Found {count} foreign Amazon jobs.")
    
    cur.execute("DELETE FROM jobs WHERE company_id = (SELECT company_id FROM companies WHERE display_name='Amazon') AND location NOT LIKE 'IN,%'")
    deleted = cur.rowcount
    print(f"Deleted {deleted} foreign jobs.")
    
    conn.commit()

if __name__ == "__main__":
    wipe_foreign_amazon()

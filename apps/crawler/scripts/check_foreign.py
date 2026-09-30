import psycopg

def check_foreign():
    conn = psycopg.connect('postgresql://postgres:postgres@localhost:5433/careermaps')
    cur = conn.cursor()
    cur.execute("SELECT location, country FROM jobs WHERE company_id = (SELECT company_id FROM companies WHERE display_name='Amazon') AND location NOT LIKE '%IN,%' AND location NOT ILIKE '%India%' LIMIT 20")
    foreign = cur.fetchall()
    print(f"Found {len(foreign)} foreign locations in sample.")
    for r in foreign:
        print(r)

if __name__ == "__main__":
    check_foreign()

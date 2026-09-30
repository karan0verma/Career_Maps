import psycopg

def check_all():
    conn = psycopg.connect('postgresql://postgres:postgres@localhost:5433/careermaps')
    cur = conn.cursor()
    cur.execute("SELECT location, country FROM jobs WHERE company_id = (SELECT company_id FROM companies WHERE display_name='Amazon') AND is_active = True LIMIT 50")
    for r in cur.fetchall():
        print(r)

if __name__ == "__main__":
    check_all()

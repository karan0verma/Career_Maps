import psycopg

def check_locs():
    conn = psycopg.connect('postgresql://postgres:postgres@localhost:5433/careermaps')
    cur = conn.cursor()
    cur.execute("SELECT location, country FROM jobs WHERE company_id = (SELECT company_id FROM companies WHERE display_name='Amazon') LIMIT 15")
    for r in cur.fetchall():
        print(r)

if __name__ == "__main__":
    check_locs()

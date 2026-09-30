import psycopg

def check_country_nulls():
    conn = psycopg.connect('postgresql://postgres:postgres@localhost:5433/careermaps')
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM jobs WHERE company_id = (SELECT company_id FROM companies WHERE display_name='Amazon') AND country = 'India'")
    print("India explicitly:", cur.fetchone()[0])
    
    cur.execute("SELECT COUNT(*) FROM jobs WHERE company_id = (SELECT company_id FROM companies WHERE display_name='Amazon') AND country IS NULL")
    print("Null country:", cur.fetchone()[0])
    
    cur.execute("SELECT location, country FROM jobs WHERE company_id = (SELECT company_id FROM companies WHERE display_name='Amazon') AND country IS NOT NULL AND country != 'India' LIMIT 10")
    print("Other countries:", cur.fetchall())

if __name__ == "__main__":
    check_country_nulls()

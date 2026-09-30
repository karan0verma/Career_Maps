import psycopg

def get_cog_url():
    conn = psycopg.connect('postgresql://postgres:postgres@localhost:5433/careermaps')
    cur = conn.cursor()
    cur.execute("SELECT career_url FROM companies WHERE display_name ILIKE '%Cognizant%'")
    res = cur.fetchone()
    if res:
        print("Cognizant DB URL:", res[0])
    else:
        print("Not found in DB")

if __name__ == "__main__":
    get_cog_url()

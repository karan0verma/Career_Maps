import psycopg
def check():
    conn = psycopg.connect('postgresql://postgres:postgres@localhost:5433/careermaps')
    cur = conn.cursor()
    cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'companies'")
    for row in cur.fetchall():
        print(row)
if __name__ == '__main__':
    check()

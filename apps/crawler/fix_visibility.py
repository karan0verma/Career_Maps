import psycopg

db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"
logos = {
    'EY': 'https://upload.wikimedia.org/wikipedia/commons/3/34/EY_logo_2019.svg',
    'Deloitte': 'https://upload.wikimedia.org/wikipedia/commons/5/56/Deloitte.svg',
    'KPMG': 'https://upload.wikimedia.org/wikipedia/commons/9/9d/KPMG_logo.svg',
    'HSBC': 'https://upload.wikimedia.org/wikipedia/commons/a/aa/HSBC_logo_%282018%29.svg',
    'PwC': 'https://upload.wikimedia.org/wikipedia/commons/0/05/PricewaterhouseCoopers_Logo.svg'
}

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        for name, url in logos.items():
            cur.execute("""
                UPDATE companies 
                SET is_active = True, logo_url = %s
                WHERE display_name = %s
            """, (url, name))
            print(f"Updated {name}: rowcount {cur.rowcount}")
    conn.commit()
    print("Done updating companies.")

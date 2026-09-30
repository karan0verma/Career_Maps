import psycopg

db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"

updates = {
    'IBM': 'https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg',
    'Google': 'https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg',
    'Meta': 'https://upload.wikimedia.org/wikipedia/commons/7/7b/Meta_Platforms_Inc._logo.svg',
    'Cisco': 'https://upload.wikimedia.org/wikipedia/commons/0/08/Cisco_logo_blue_2016.svg'
}

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        for cname, url in updates.items():
            cur.execute("UPDATE companies SET logo_url = %s WHERE display_name = %s", (url, cname))
        conn.commit()
        print("Updated missing logos successfully!")

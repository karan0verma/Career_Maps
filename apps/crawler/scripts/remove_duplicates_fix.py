import psycopg

def remove_duplicates():
    conn = psycopg.connect('postgresql://postgres:postgres@localhost:5433/careermaps')
    cur = conn.cursor()
    
    # We will use ctid or created_at to keep the latest row
    cur.execute("""
        DELETE FROM jobs
        WHERE job_id IN (
            SELECT job_id FROM (
                SELECT job_id, ROW_NUMBER() OVER (PARTITION BY company_id, title, location ORDER BY created_at DESC) as row_num
                FROM jobs
            ) t
            WHERE t.row_num > 1
        )
    """)
    deleted = cur.rowcount
    print(f"Deleted {deleted} duplicate rows.")
    conn.commit()

if __name__ == "__main__":
    remove_duplicates()

import psycopg

def find_and_remove_duplicates():
    conn = psycopg.connect('postgresql://postgres:postgres@localhost:5433/careermaps')
    cur = conn.cursor()
    
    # Check for duplicates based on company_id and external_job_id
    cur.execute("""
        SELECT company_id, external_job_id, count(*) 
        FROM jobs 
        WHERE external_job_id IS NOT NULL 
        GROUP BY company_id, external_job_id 
        HAVING count(*) > 1
    """)
    dupes_by_id = cur.fetchall()
    print(f"Found {len(dupes_by_id)} external_job_id duplicates.")
    
    # Check for duplicates based on company_id, title, and location
    cur.execute("""
        SELECT company_id, title, location, count(*) 
        FROM jobs 
        GROUP BY company_id, title, location 
        HAVING count(*) > 1
    """)
    dupes_by_title = cur.fetchall()
    print(f"Found {len(dupes_by_title)} title+location duplicates.")
    
    # Remove duplicates, keeping the most recently updated one
    cur.execute("""
        DELETE FROM jobs a USING (
            SELECT MAX(job_id) as max_id, title, company_id, location
            FROM jobs
            GROUP BY title, company_id, location
        ) b
        WHERE a.title = b.title AND a.company_id = b.company_id AND a.location = b.location AND a.job_id != b.max_id;
    """)
    
    deleted = cur.rowcount
    print(f"Deleted {deleted} exact title+location duplicate rows.")
    
    conn.commit()

if __name__ == "__main__":
    find_and_remove_duplicates()

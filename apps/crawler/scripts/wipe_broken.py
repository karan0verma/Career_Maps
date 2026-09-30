import psycopg

def wipe_broken_companies():
    db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"
    companies_to_wipe = [
        'Tech Mahindra', 
        'Infosys Limited', 
        'EY', 
        'Cognizant', 
        'Tata Consultancy Services (TCS)'
    ]
    
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            # Mark all as inactive instead of deleting to preserve history, or delete them? 
            # Deleting is cleaner for the user. Let's delete them.
            cur.execute("""
                DELETE FROM jobs 
                WHERE company_id IN (
                    SELECT company_id FROM companies WHERE display_name = ANY(%s)
                )
            """, (companies_to_wipe,))
            deleted = cur.rowcount
            print(f"Deleted {deleted} broken jobs for {companies_to_wipe}")
            
        conn.commit()

if __name__ == "__main__":
    wipe_broken_companies()

import psycopg

db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"

print("=" * 80)
print("CLEANING UP NON-INDIA AND FAULTY GLOBAL JOBS FROM DATABASE")
print("=" * 80)

deleted_counts = {}

# List of valid Indian keywords
india_keywords = [
    'India', 'IN', 'Bangalore', 'Bengaluru', 'Hyderabad', 'Pune', 'Chennai', 
    'Mumbai', 'Noida', 'Gurugram', 'Gurgaon', 'Delhi', 'Kolkata', 'Ahmedabad',
    'Chandigarh', 'Indore', 'Kochi', 'Trivandrum', 'Coimbatore', 'Jaipur', 'Bhubaneswar',
    'Gandhinagar', 'Mohali', 'Nagpur', 'Lucknow', 'Madurai', 'Mysore', 'Surat', 'Vadodara'
]

# Create ILIKE conditions
ilike_conditions = " OR ".join([f"location ILIKE '%{kw}%'" for kw in india_keywords])
not_ilike_conditions = " AND ".join([f"location NOT ILIKE '%{kw}%'" for kw in india_keywords])

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        # 1. Clean Amazon specifically (Faulty "US, WA, Seattle, India" pattern)
        # Any Amazon job that doesn't start with 'IN,' and doesn't contain a major Indian city.
        cur.execute("""
            SELECT j.job_id, j.location 
            FROM jobs j 
            JOIN companies c ON j.company_id = c.company_id 
            WHERE c.display_name = 'Amazon' 
            AND j.location NOT ILIKE 'IN,%' 
            AND j.location NOT ILIKE '%Bengaluru%'
            AND j.location NOT ILIKE '%Hyderabad%'
            AND j.location NOT ILIKE '%Chennai%'
            AND j.location NOT ILIKE '%Pune%'
            AND j.location NOT ILIKE '%Mumbai%'
            AND j.location NOT ILIKE '%Gurugram%'
            AND j.location NOT ILIKE '%Delhi%'
            AND j.location NOT ILIKE '%Noida%'
        """)
        amazon_faulty = cur.fetchall()
        
        amazon_ids = [row[0] for row in amazon_faulty]
        if amazon_ids:
            cur.execute("DELETE FROM jobs WHERE job_id = ANY(%s)", (amazon_ids,))
            deleted_counts['Amazon'] = len(amazon_ids)
            print(f"Deleted {len(amazon_ids)} faulty global jobs from Amazon.")

        # 2. Clean all other companies where location has absolutely no Indian keyword
        # Or explicit global locations
        cur.execute(f"""
            SELECT c.display_name, j.job_id, j.location
            FROM jobs j
            JOIN companies c ON j.company_id = c.company_id
            WHERE ({not_ilike_conditions})
            AND c.display_name != 'Amazon'
        """)
        other_faulty = cur.fetchall()
        
        other_ids = [row[1] for row in other_faulty]
        if other_ids:
            cur.execute("DELETE FROM jobs WHERE job_id = ANY(%s)", (other_ids,))
            
            for row in other_faulty:
                comp = row[0]
                deleted_counts[comp] = deleted_counts.get(comp, 0) + 1
            
            print(f"Deleted {len(other_ids)} non-India jobs from other companies.")

        # Commit
        conn.commit()

        # Get final DB count
        cur.execute("SELECT COUNT(*) FROM jobs")
        final_count = cur.fetchone()[0]

print("-" * 80)
print("DELETION SUMMARY:")
for comp, count in deleted_counts.items():
    print(f"  • {comp}: Removed {count} jobs")
print("-" * 80)
print(f"FINAL DATABASE COUNT (ACTIVE INDIA JOBS): {final_count:,}")
print("=" * 80)

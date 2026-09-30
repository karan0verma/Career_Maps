import psycopg

def remove_problematic_companies():
    db_url = "postgresql://postgres:postgres@localhost:5433/careermaps"
    
    companies_to_remove = ["Cognizant", "Tech Mahindra", "Tata Consultancy Services"]
    
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            for c_name in companies_to_remove:
                # Find the company
                cur.execute("SELECT company_id, display_name FROM companies WHERE display_name ILIKE %s", (f"%{c_name}%",))
                rows = cur.fetchall()
                
                for row in rows:
                    comp_id, display_name = row
                    
                    # 1. Soft delete the company
                    cur.execute("""
                        UPDATE companies 
                        SET is_active = false, is_deleted = true 
                        WHERE company_id = %s
                    """, (comp_id,))
                    
                    # 2. Soft delete any remaining jobs associated with them (just in case)
                    cur.execute("""
                        UPDATE jobs 
                        SET is_active = false, is_deleted = true 
                        WHERE company_id = %s
                    """, (comp_id,))
                    
                    print(f"Removed '{display_name}' (ID: {comp_id}) from frontend and backend.")
                    
        conn.commit()
    print("Cleanup complete.")

if __name__ == "__main__":
    remove_problematic_companies()

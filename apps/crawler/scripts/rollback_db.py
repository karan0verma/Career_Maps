import psycopg
from datetime import datetime, timezone

def rollback():
    conn = psycopg.connect("postgresql://postgres:postgres@localhost:5433/careermaps")
    cur = conn.cursor()
    
    # Delete newly added jobs today
    cur.execute("DELETE FROM jobs WHERE created_at >= '2026-09-29'")
    deleted = cur.rowcount
    
    # Restore jobs deactivated today
    cur.execute("UPDATE jobs SET is_active = True WHERE updated_at >= '2026-09-29' AND is_active = False")
    restored = cur.rowcount
    
    conn.commit()
    print(f"Rollback Complete: {deleted} inserted jobs deleted, {restored} expired jobs restored.")

if __name__ == "__main__":
    rollback()

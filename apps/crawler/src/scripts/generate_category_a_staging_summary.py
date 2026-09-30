import os
import json

report_file = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\crawler\staging\category_a_bigtech_staged.json"

if os.path.exists(report_file):
    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("=" * 90)
    print("CATEGORY A BIG TECH STAGING AUDIT REPORT")
    print("=" * 90)
    print(f"Audit Status  : {data.get('audit_status')}")
    print(f"DB Ingested   : {data.get('ingested_into_db')}")
    print(f"Timestamp     : {data.get('timestamp')}")
    print("-" * 90)
    
    total_staged = 0
    for ckey, cval in data.get('companies', {}).items():
        cnt = cval.get('staged_jobs_count', 0)
        total_staged += cnt
        portal = cval.get('official_career_portal', '')
        print(f"• {cval.get('display_name'):20} | Staged Jobs: {cnt:4} | Official Portal: {portal}")

    print("=" * 90)
    print(f"TOTAL STAGED JOBS ACROSS CATEGORY A: {total_staged:,}")
    print("=" * 90)
else:
    print("Staging report file not found.")

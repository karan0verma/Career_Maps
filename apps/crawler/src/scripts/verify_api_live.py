import urllib.request
import json

try:
    res = urllib.request.urlopen("http://localhost:8000/api/v1/companies")
    comps = json.loads(res.read().decode())
    print("=" * 80)
    print(f"FASTAPI BACKEND API LIVE - {len(comps)} ACTIVE COMPANIES:")
    print("=" * 80)
    for c in comps:
        print(f"  • {c.get('display_name'):30} | Jobs API: http://localhost:8000/api/v1/jobs?company_id={c.get('company_id')}")

    # Check Microsoft sample job
    ms_comp = next((c for c in comps if 'microsoft' in c.get('display_name', '').lower()), None)
    if ms_comp:
        j_res = urllib.request.urlopen(f"http://localhost:8000/api/v1/jobs?company_id={ms_comp['company_id']}&limit=5")
        ms_jobs = json.loads(j_res.read().decode())
        print("\n--- SAMPLE MICROSOFT VERIFIED JOBS ---")
        items = ms_jobs.get('items', ms_jobs) if isinstance(ms_jobs, dict) else ms_jobs
        for j in items[:3]:
            print(f"  Title: {j.get('title')}")
            print(f"  Work Mode: {j.get('work_mode')}")
            print(f"  Apply URL: {j.get('apply_url')}")
            print()

    # Check Oracle sample job
    orcl_comp = next((c for c in comps if 'oracle' in c.get('display_name', '').lower()), None)
    if orcl_comp:
        j_res = urllib.request.urlopen(f"http://localhost:8000/api/v1/jobs?company_id={orcl_comp['company_id']}&limit=5")
        orcl_jobs = json.loads(j_res.read().decode())
        print("\n--- SAMPLE ORACLE VERIFIED JOBS ---")
        items = orcl_jobs.get('items', orcl_jobs) if isinstance(orcl_jobs, dict) else orcl_jobs
        for j in items[:3]:
            print(f"  Title: {j.get('title')}")
            print(f"  Work Mode: {j.get('work_mode')}")
            print(f"  Apply URL: {j.get('apply_url')}")
            print()

except Exception as e:
    print("API Verification Error:", e)

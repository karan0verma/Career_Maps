import requests
import psycopg

payload = {
    "sortBy": "",
    "subsearch": "",
    "from": 0,
    "jobs": True,
    "counts": True,
    "all_fields": ["category", "raasJobRequisitionType", "country", "state", "city", "type", "RemoteType"],
    "pageName": "search-results",
    "size": 500,
    "clearAll": False,
    "jdsource": "facets",
    "isSliderEnable": False,
    "pageId": "page4",
    "siteType": "external",
    "keywords": "India",
    "global": True,
    "selected_fields": {},
    "lang": "en_global",
    "deviceType": "desktop",
    "country": "global",
    "refNum": "CISCISGLOBAL",
    "ddoKey": "eagerLoadRefineSearchSession"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Content-Type': 'application/json',
    'Origin': 'https://careers.cisco.com',
    'Referer': 'https://careers.cisco.com/global/en/search-results?q=India'
}

print("Fetching exact Cisco locations from Phenom API...")
s = requests.Session()
s.get("https://careers.cisco.com/global/en/search-results?q=India", headers=headers)
res = s.post("https://careers.cisco.com/widgets", json=payload, headers=headers)

if res.ok:
    data = res.json()
    jobs = data.get('refineSearch', {}).get('data', {}).get('jobs', [])
    print(f"Fetched {len(jobs)} jobs from API")
    
    # Map by job ID to update Database
    update_count = 0
    with psycopg.connect("postgresql://postgres:postgres@localhost:5433/careermaps") as conn:
        with conn.cursor() as cur:
            for j in jobs:
                jid = str(j.get('jobId') or j.get('id', ''))
                loc = j.get('location') or j.get('city') or 'Bengaluru'
                city = j.get('city') or loc.split(',')[0]
                
                # Update DB
                cur.execute("""
                    UPDATE jobs 
                    SET location = %s, city = %s 
                    WHERE external_job_id = %s AND company_id = (SELECT company_id FROM companies WHERE display_name = 'Cisco')
                """, (f"{loc}, India", city, jid))
                
                if cur.rowcount > 0:
                    update_count += 1
                    
        conn.commit()
    print(f"Successfully updated locations for {update_count} Cisco jobs in Database!")
else:
    print("API failed:", res.status_code, res.text[:200])

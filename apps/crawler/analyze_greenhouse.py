import requests
import json

COMPANIES = [
    "airbnb", "stripe", "figma", "databricks", "coinbase", 
    "cloudflare", "lyft", "gitlab", "mongodb", "canonical", 
    "remote", "doordash", "chime", "spacex"
]

def check_api(company: str):
    url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            jobs = data.get("jobs", [])
            
            if jobs:
                first_job = jobs[0]
                keys = list(first_job.keys())
                loc = first_job.get("location", {})
                loc_keys = list(loc.keys()) if isinstance(loc, dict) else type(loc)
                return True, len(jobs), keys, loc_keys
            return True, 0, [], []
        else:
            return False, resp.status_code, [], []
    except Exception as e:
        return False, str(e), [], []

def check_html(company: str):
    url = f"https://boards.greenhouse.io/{company}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            html = resp.text
            has_api_mention = "boards-api.greenhouse.io" in html
            return True, len(html), has_api_mention
        return False, resp.status_code, False
    except Exception as e:
        return False, str(e), False

def main():
    print(f"Testing {len(COMPANIES)} companies against boards-api.greenhouse.io...\\n")
    
    for c in COMPANIES:
        api_ok, num_jobs, keys, loc_keys = check_api(c)
        if api_ok:
            print(f"[API ] {c:12} -> OK ({num_jobs} jobs) | Keys: {keys[:5]}... | Loc Keys: {loc_keys}")
        else:
            print(f"[API ] {c:12} -> FAILED ({num_jobs})")
            
        html_ok, html_len, has_api = check_html(c)
        if html_ok:
            print(f"[HTML] {c:12} -> OK ({html_len} bytes) | Mentions API: {has_api}")
        else:
            print(f"[HTML] {c:12} -> FAILED ({html_len})")
            
        print("-" * 50)

if __name__ == "__main__":
    main()

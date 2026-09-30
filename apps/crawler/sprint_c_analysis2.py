import requests
from bs4 import BeautifulSoup
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def analyze_ats(name, url, api_url=None, api_params=None):
    print(f"\n======================================")
    print(f"Analyzing {name}")
    print(f"URL: {url}")
    
    # 1. Check HTML
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"HTML Status: {resp.status_code}")
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Look for common signs
        if "window.__INITIAL_STATE__" in resp.text or "window.initialState" in resp.text:
            print("[+] Found SSR/Embedded State (React/Vue/Angular)")
            
        if "csrf" in resp.text.lower():
            print("[+] Found potential CSRF token in HTML")
            
        scripts = soup.find_all('script')
        json_scripts = [s for s in scripts if s.get('type') == 'application/json' or (s.string and s.string.strip().startswith('{'))]
        if json_scripts:
            print(f"[+] Found {len(json_scripts)} potential JSON script tags")
            
    except Exception as e:
        print(f"HTML Fetch Failed: {e}")

    # 2. Check API if provided
    if api_url:
        print(f"\nAPI URL: {api_url}")
        try:
            resp = requests.get(api_url, params=api_params, headers=headers, timeout=10)
            print(f"API Status: {resp.status_code}")
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    print(f"API Response Type: {type(data)}")
                    if isinstance(data, dict):
                        print(f"API Top-level keys: {list(data.keys())}")
                        
                        # recursively find list of jobs
                        def find_jobs(obj):
                            if isinstance(obj, dict):
                                for k, v in obj.items():
                                    res = find_jobs(v)
                                    if res: return res
                            elif isinstance(obj, list):
                                if len(obj) > 0 and isinstance(obj[0], dict) and ('id' in obj[0] or 'title' in obj[0] or 'name' in obj[0]):
                                    return obj
                                for item in obj:
                                    res = find_jobs(item)
                                    if res: return res
                            return None
                            
                        jobs = find_jobs(data)
                        if jobs:
                            print(f"[+] Found job list of size {len(jobs)}")
                            print(f"First job keys: {list(jobs[0].keys())}")
                except Exception as e:
                    print(f"API JSON Parse Failed: {e}")
                    print(resp.text[:200])
        except Exception as e:
            print(f"API Fetch Failed: {e}")

# iCIMS (uses iframes usually)
analyze_ats("iCIMS", "https://careers-ul.icims.com/jobs/search?ss=1")

# Eightfold AI
analyze_ats("Eightfold AI", "https://talent.eightfold.ai/careers", "https://talent.eightfold.ai/api/apply/v2/jobs", {"domain": "talent.eightfold.ai"})

# Zoho Recruit
analyze_ats("Zoho Recruit", "https://zohocorp.zohorecruit.com/jobs/Careers", "https://zohocorp.zohorecruit.com/recruit/v2/public/Job_Openings")

# Darwinbox
analyze_ats("Darwinbox", "https://swiggy.darwinbox.in/careers", "https://swiggy.darwinbox.in/jobs/getjoblist")


import json
import time
from playwright.sync_api import sync_playwright
import psycopg
import uuid
from datetime import datetime, timezone

def run_pwc():
    print("Starting PwC Workday Extractor (Locked Architecture)...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # We need to intercept the cxs API call to get the exact payload and headers
        api_url = "https://pwc.wd3.myworkdayjobs.com/wday/cxs/pwc/Global_Careers/jobs"
        
        # Navigate to trigger cookies
        page.goto("https://pwc.wd3.myworkdayjobs.com/Global_Careers", wait_until="networkidle")
        time.sleep(2)
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        all_jobs = []
        offset = 0
        limit = 20
        
        print("Bypassed WAF. Starting batch extraction...")
        
        while offset < 100: # Limit to 100 for now just to prove it works
            payload = {
                "appliedFacets": {"Location_Country": ["bc33aa31523742cb80ce0af4f21689c5"]}, # India
                "limit": limit,
                "offset": offset,
                "searchText": ""
            }
            
            res = context.request.post(api_url, headers=headers, data=payload)
            if res.status == 200:
                data = res.json()
                postings = data.get('jobPostings', [])
                if not postings:
                    break
                    
                for job in postings:
                    title = job.get('title')
                    ext_path = job.get('externalPath')
                    if ext_path:
                        apply_url = f"https://pwc.wd3.myworkdayjobs.com/en-US/Global_Careers{ext_path}"
                        all_jobs.append((title, apply_url))
                print(f"Fetched {len(postings)} jobs at offset {offset}")
                offset += limit
                time.sleep(1)
            else:
                print(f"Failed to fetch at offset {offset}. Status: {res.status}")
                break
                
        browser.close()
        
        print(f"Extraction complete. Found {len(all_jobs)} jobs.")
        if all_jobs:
            print("First 3 jobs:")
            for j in all_jobs[:3]:
                print(j)

if __name__ == "__main__":
    run_pwc()

from playwright.sync_api import sync_playwright
import time
import json

captured_jobs_data = []

print("Launching Chrome to fetch TCS jobs...", flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()
    
    def handle_res(response):
        url = response.url
        if "api/v1/jobs/searchJ" in url and response.status == 200:
            try:
                data = response.json()
                captured_jobs_data.append(data)
                print(f"[Captured searchJ] Found data with {len(data.get('data', {}).get('jobs', []))} jobs", flush=True)
            except Exception as e:
                print("Error parsing json:", e)
                
    page.on("response", handle_res)
    
    target = "https://ibegin.tcsapps.com/candidate/#/jobs/search?geography=IN&language=EN"
    print(f"Navigating to {target} ...", flush=True)
    page.goto(target, wait_until="networkidle", timeout=30000)
    time.sleep(5)
    
    print(f"Total captured responses on initial search: {len(captured_jobs_data)}", flush=True)
    
    if captured_jobs_data:
        total_jobs = captured_jobs_data[0].get('data', {}).get('totalJobs', 0)
        jobs = captured_jobs_data[0].get('data', {}).get('jobs', [])
        print(f"\n=======================================================", flush=True)
        print(f"TOTAL ACTIVE JOBS IN TCS DATABASE: {total_jobs}", flush=True)
        print(f"FIRST PAGE RETURNED: {len(jobs)} JOBS", flush=True)
        print(f"=======================================================", flush=True)
        for i, j in enumerate(jobs[:5]):
            print(f"\n[Sample {i+1}]")
            print(f"  • ID         : {j.get('id')}")
            print(f"  • Title      : {j.get('jobTitle')}")
            print(f"  • Location   : {j.get('location')}")
            print(f"  • Experience : {j.get('experience')} Years")
            print(f"  • Function   : {j.get('functionName')}")
            print(f"  • Skills     : {j.get('skills')}")
            print(f"  • Apply By   : {j.get('applyByDate')}")
            print(f"  • Apply URL  : https://ibegin.tcsapps.com/candidate/#/jobs/{j.get('id')}")

    browser.close()

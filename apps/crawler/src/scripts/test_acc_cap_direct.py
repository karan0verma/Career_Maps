import os
import sys
import json
import time
import requests
from playwright.sync_api import sync_playwright

print("=" * 80)
print("TESTING ACCENTURE & CAPGEMINI DIRECT ENDPOINTS")
print("=" * 80)

# 1. Capgemini
print("\n--- 1. CAPGEMINI JOBSTREAM API ---")
try:
    cap_url = "https://cg-jobstream-api.azurewebsites.net/api/job-search?page=1&size=10&country_code=in-en"
    cap_res = requests.get(cap_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    print(f"Capgemini Status: {cap_res.status_code}")
    if cap_res.ok:
        d = cap_res.json()
        print(f"Capgemini Total Jobs: {d.get('total')}")
        jobs = d.get('data', [])
        if jobs:
            j0 = jobs[0]
            print(f"Sample: {j0.get('title')} | Location: {j0.get('location')} | URL: {j0.get('url')}")
except Exception as e:
    print(f"Capgemini error: {e}")

# 2. Accenture
print("\n--- 2. ACCENTURE ELASTIC FINDJOBS API ---")
with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()
    page.goto("https://www.accenture.com/in-en/careers/jobsearch?jk=&sb=1&pg=1", wait_until='networkidle', timeout=30000)
    time.sleep(2)

    # Trigger findjobs payload
    acc_payload = {
        "page": 1,
        "size": 10,
        "country": "India",
        "keywords": ""
    }
    acc_res = page.request.post("https://www.accenture.com/api/accenture/elastic/findjobs", data=json.dumps(acc_payload), headers={'content-type': 'application/json'})
    print(f"Accenture Status: {acc_res.status}")
    if acc_res.ok:
        d = acc_res.json()
        print(f"Accenture Response Keys: {list(d.keys()) if isinstance(d, dict) else len(d)}")
        total_acc = d.get('total') or d.get('totalJobs') or d.get('totalCount')
        print(f"Accenture Total Jobs: {total_acc}")
        results = d.get('results', d.get('jobs', []))
        if results:
            r0 = results[0]
            print(f"Sample: {r0.get('title') or r0.get('jobTitle')} | Location: {r0.get('location') or r0.get('city')}")

    browser.close()

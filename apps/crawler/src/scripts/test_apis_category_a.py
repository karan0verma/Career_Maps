import os
import sys
import json
import requests
from playwright.sync_api import sync_playwright

print("=" * 80)
print("TESTING CATEGORY A DIRECT RECRUITING APIS")
print("=" * 80)

# 1. Google Careers API
print("\n--- 1. GOOGLE CAREERS API ---")
try:
    g_res = requests.get("https://careers.google.com/api/v3/search/?distance=50&q=&location=India&page=1&page_size=20", timeout=10)
    print(f"Google HTTP Status: {g_res.status_code}")
    if g_res.status_code == 200:
        d = g_res.json()
        print(f"Google Total Jobs: {d.get('count')}")
        jobs = d.get('jobs', [])
        if jobs:
            j0 = jobs[0]
            print(f"Sample: {j0.get('title')} | Locations: {[l.get('display') for l in j0.get('locations', [])]}")
            print(f"Apply/JD URL: {j0.get('apply_url') or f'https://careers.google.com/jobs/results/{j0.get('id')}'}")
except Exception as e:
    print(f"Google Error: {e}")

# 2. IBM Eightfold API
print("\n--- 2. IBM CAREERS API ---")
try:
    ibm_res = requests.get("https://ibm.eightfold.ai/api/apply/v2/jobs?domain=ibm.com&location=India&num=10&start=0", timeout=10)
    print(f"IBM HTTP Status: {ibm_res.status_code}")
    if ibm_res.status_code == 200:
        d = ibm_res.json()
        print(f"IBM Total Positions: {d.get('count') or d.get('total')}")
        positions = d.get('positions', [])
        if positions:
            p0 = positions[0]
            print(f"Sample: {p0.get('name')} | Location: {p0.get('location')} | ID: {p0.get('id')}")
            print(f"Apply URL: {p0.get('canonicalPositionUrl')}")
except Exception as e:
    print(f"IBM Error: {e}")

# 3. Adobe Workday API
print("\n--- 3. ADOBE WORKDAY API ---")
try:
    ad_url = "https://adobe.wd5.myworkdayjobs.com/wday/cxs/adobe/external_experienced/jobs"
    ad_payload = {"appliedFacets": {"locationCountry": ["bc33aa3152ec42d4995f4791a106ed09"]}, "limit": 10, "offset": 0, "searchText": ""}
    ad_res = requests.post(ad_url, json=ad_payload, timeout=10)
    print(f"Adobe HTTP Status: {ad_res.status_code}")
    if ad_res.status_code == 200:
        d = ad_res.json()
        print(f"Adobe Total Positions: {d.get('total')}")
        postings = d.get('jobPostings', [])
        if postings:
            p0 = postings[0]
            print(f"Sample: {p0.get('title')} | Location: {p0.get('locationsText')}")
            print(f"Apply URL: https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced{p0.get('externalPath')}")
except Exception as e:
    print(f"Adobe Error: {e}")

# 4. Cisco Careers
print("\n--- 4. CISCO CAREERS ---")
try:
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chrome', headless=True)
        pg = b.new_page()
        pg.goto("https://jobs.cisco.com/jobs/SearchJobs/?21178=%5B169482%5D&21178_format=464&listFilterMode=1", wait_until='domcontentloaded', timeout=15000)
        time.sleep(2)
        cisco_info = pg.evaluate("""() => {
            const countEl = document.querySelector('.total-results, [class*="results"]');
            const links = Array.from(document.querySelectorAll('a[href*="/jobs/ProjectDetail/"]')).map(a => ({
                title: a.innerText.trim(),
                href: a.href
            })).filter(j => j.title);
            return {
                totalText: countEl ? countEl.innerText.trim() : '',
                count: links.length,
                sample: links[0]
            };
        }""")
        print(f"Cisco Extracted: {cisco_info}")
        b.close()
except Exception as e:
    print(f"Cisco Error: {e}")

print("\n" + "=" * 80)

import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def test_full_wipro():
    print("=" * 75)
    print("TESTING FULL WIPRO RECRUITING EXTRACTION VIA CONTEXT.REQUEST")
    print("=" * 75)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context()
        page = context.new_page()

        csrf_token = ""
        def on_req(req):
            nonlocal csrf_token
            if 'x-csrf-token' in req.headers:
                csrf_token = req.headers['x-csrf-token']

        page.on('request', on_req)

        page.goto('https://careers.wipro.com/search/?q=&locationsearch=India', wait_until='networkidle', timeout=30000)
        time.sleep(3)

        print(f"Captured CSRF Token: {csrf_token}")

        # Test querying page 0 and total jobs
        headers = {
            'content-type': 'application/json',
            'referer': 'https://careers.wipro.com/search/?q=&locationsearch=India&searchResultView=LIST',
            'x-csrf-token': csrf_token
        }

        all_jobs = []
        page_num = 0

        while True:
            payload = {
                "locale": "en_US",
                "pageNumber": page_num,
                "sortBy": "",
                "keywords": "",
                "location": "India",
                "facetFilters": {},
                "brand": "",
                "skills": [],
                "categoryId": 0,
                "alertId": "",
                "rcmCandidateId": ""
            }

            res = context.request.post(
                "https://careers.wipro.com/services/recruiting/v1/jobs",
                headers=headers,
                data=json.dumps(payload)
            )

            if res.status != 200:
                print(f"Page {page_num} status {res.status}")
                break

            data = res.json()
            jobs = data.get('jobSearchResult', [])
            total_jobs = data.get('totalJobs', 0)
            
            if not jobs:
                break

            all_jobs.extend(jobs)
            print(f"Page {page_num}: Retrieved {len(jobs)} jobs (Cumulative: {len(all_jobs)} / Total Available: {total_jobs})")
            
            if len(all_jobs) >= total_jobs or len(jobs) == 0:
                break
                
            page_num += 1

        print(f"\nExtracted {len(all_jobs)} Total Wipro Jobs!")
        if all_jobs:
            sample = all_jobs[0].get('response', {})
            print("\nSample Job Keys:", list(sample.keys()))
            print("Sample Title:", sample.get('jobTitle'))
            print("Sample Locations:", sample.get('jobLocationShort'))
            print("Sample URL:", sample.get('jobUrl'))

        browser.close()

if __name__ == "__main__":
    test_full_wipro()

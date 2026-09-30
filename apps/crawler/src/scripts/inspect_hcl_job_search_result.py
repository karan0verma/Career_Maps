import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_hcl_job_search_result():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        page.goto('https://careers.hcltech.com/search/?q=&searchResultView=LIST', wait_until='networkidle', timeout=35000)
        time.sleep(3)

        # Send API request using page.request with CSRF token
        payload = {"locale":"en_US","pageNumber":0,"sortBy":"","keywords":"","location":"","facetFilters":{},"brand":"","skills":[],"categoryId":0,"alertId":"","rcmCandidateId":""}
        
        # Test location=India or location=""
        res = page.request.post("https://careers.hcltech.com/services/recruiting/v1/jobs", data=json.dumps(payload), headers={'content-type': 'application/json'})
        d = res.json()
        print("Keys in response:", list(d.keys()))
        print("Total Jobs:", d.get('totalJobs'))
        jsr = d.get('jobSearchResult', {})
        print("jobSearchResult keys:", list(jsr.keys()) if isinstance(jsr, dict) else type(jsr))
        if isinstance(jsr, dict):
            for k, v in jsr.items():
                print(f"  {k}: {len(v) if isinstance(v, list) else v}")
                if isinstance(v, list) and v:
                    print(f"  Sample {k} 0:", json.dumps(v[0], indent=2))
        elif isinstance(jsr, list):
            print(f"jobSearchResult list len: {len(jsr)}")
            if jsr:
                print("Sample 0:", json.dumps(jsr[0], indent=2))

        # Also let's test with location="India"
        payload_in = {"locale":"en_US","pageNumber":0,"sortBy":"","keywords":"","location":"India","facetFilters":{},"brand":"","skills":[],"categoryId":0,"alertId":"","rcmCandidateId":""}
        res_in = page.request.post("https://careers.hcltech.com/services/recruiting/v1/jobs", data=json.dumps(payload_in), headers={'content-type': 'application/json'})
        d_in = res_in.json()
        print("\nWith location=India -> totalJobs:", d_in.get('totalJobs'))
        jsr_in = d_in.get('jobSearchResult', {})
        if isinstance(jsr_in, dict):
            for k, v in jsr_in.items():
                print(f"  India {k}: {len(v) if isinstance(v, list) else v}")
                if isinstance(v, list) and v:
                    print(f"  Sample India {k} 0:", json.dumps(v[0], indent=2))

        browser.close()

if __name__ == "__main__":
    inspect_hcl_job_search_result()

import os
import sys
import json
import time
import math
from playwright.sync_api import sync_playwright

def test_cognizant():
    print("=" * 80, flush=True)
    print("TESTING COGNIZANT INDIA JOBS EXTRACTION VIA PHENOM GATEWAY", flush=True)
    print("=" * 80, flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        captured_jobs = []

        def on_response(res):
            if ('api' in res.url or 'search' in res.url or 'jobs' in res.url) and 'json' in res.headers.get('content-type', ''):
                try:
                    d = res.json()
                    if isinstance(d, dict) and ('jobs' in d or 'jobPostings' in d or 'positionList' in d or 'data' in d):
                        print(f"Captured Cognizant API: {res.url[:100]}", flush=True)
                        print(f"Keys: {list(d.keys())}", flush=True)
                except:
                    pass

        page.on('response', on_response)
        page.goto('https://careers.cognizant.com/india-en/jobs/?location=India', wait_until='networkidle', timeout=30000)
        time.sleep(3)

        # Check total count selector
        total_text = page.evaluate("""() => {
            const el = document.querySelector('.total-jobs, .search-count, [data-ph-id*="total-jobs"], h2');
            return el ? el.innerText : '';
        }""")
        print(f"Cognizant India Page Text: {total_text}", flush=True)

        browser.close()

if __name__ == "__main__":
    test_cognizant()

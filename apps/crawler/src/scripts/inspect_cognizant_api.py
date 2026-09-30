import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_cognizant():
    print("=" * 80)
    print("INSPECTING COGNIZANT CAREERS PHENOM API")
    print("=" * 80, flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        phenom_endpoints = []

        def on_res(res):
            if ('widgets' in res.url or 'search-results' in res.url or 'jobs' in res.url or 'ephox' in res.url or 'api' in res.url) and 'json' in res.headers.get('content-type', ''):
                try:
                    data = res.json()
                    if isinstance(data, dict) and ('refineSearch' in data or 'jobCart' in data or 'totalHits' in data or 'jobs' in data):
                        phenom_endpoints.append({'url': res.url, 'keys': list(data.keys()), 'totalHits': data.get('totalHits') or data.get('refineSearch', {}).get('totalHits')})
                        print(f"  [Phenom API] {res.url[:120]} -> Keys: {list(data.keys())}", flush=True)
                        if 'jobCart' in data:
                            print(f"    jobCart keys: {list(data['jobCart'].keys())}")
                        if 'refineSearch' in data:
                            print(f"    refineSearch totalHits: {data['refineSearch'].get('totalHits')}")
                            jobs = data['refineSearch'].get('data', {}).get('jobs', [])
                            print(f"    refineSearch jobs count: {len(jobs)}")
                except:
                    pass

        page.on('response', on_res)
        print("Visiting Cognizant India search page...", flush=True)
        page.goto('https://careers.cognizant.com/global/en/search-results?m=3&location=India', wait_until='networkidle', timeout=35000)
        time.sleep(4)

        # Also let's inspect the DOM
        dom_total = page.evaluate("""() => {
            const el = document.querySelector('.result-count, .total-jobs, [data-ph-id*="total-jobs"], .search-result-count');
            return el ? el.innerText : '';
        }""")
        print(f"DOM Total Text: {dom_total}", flush=True)

        browser.close()

if __name__ == "__main__":
    inspect_cognizant()

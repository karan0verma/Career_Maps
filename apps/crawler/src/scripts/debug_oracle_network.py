import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def debug_oracle():
    print("=" * 80)
    print("DEBUGGING ORACLE CLOUD HCM CAREERS NETWORK TRAFFIC")
    print("=" * 80, flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        requests_logged = []
        json_responses = []

        def on_req(req):
            if 'hcmRestApi' in req.url or 'recruiting' in req.url or 'requisition' in req.url:
                requests_logged.append({
                    'method': req.method,
                    'url': req.url,
                    'headers': dict(req.headers)
                })
                print(f"[REQ] {req.method} {req.url}", flush=True)

        def on_res(res):
            if 'hcmRestApi' in res.url or 'recruiting' in res.url or 'requisition' in res.url:
                try:
                    data = res.json()
                    json_responses.append({'url': res.url, 'data': data})
                    print(f"  [RES JSON] {res.url[:120]} -> Count: {data.get('count')}, Items: {len(data.get('items', [])) if isinstance(data.get('items'), list) else 'N/A'}", flush=True)
                except:
                    pass

        page.on('request', on_req)
        page.on('response', on_res)

        print("\nNavigating to Oracle Careers India search page...", flush=True)
        page.goto('https://careers.oracle.com/jobs/#en/sites/jobsearch/requisitions?location=India&locationId=300000000106965', wait_until='networkidle', timeout=35000)
        time.sleep(5)

        print(f"\nCaptured {len(requests_logged)} requests and {len(json_responses)} JSON responses.", flush=True)
        for jr in json_responses:
            if jr['data'].get('items'):
                print(f"\n--- Found Requisitions Endpoint ---")
                print("URL:", jr['url'])
                print("Sample Item:", jr['data']['items'][0].get('Title'), "| Location:", jr['data']['items'][0].get('PrimaryLocation'))

        browser.close()

if __name__ == "__main__":
    debug_oracle()

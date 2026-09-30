import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_hcl_network():
    print("=" * 80)
    print("INSPECTING HCLTECH SUCCESSFACTORS NETWORK REQUESTS")
    print("=" * 80, flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        captured_requests = []

        def on_req(req):
            if 'search' in req.url or 'job' in req.url or 'api' in req.url or 'services' in req.url:
                if req.resource_type in ['xhr', 'fetch']:
                    captured_requests.append({
                        'method': req.method,
                        'url': req.url,
                        'post_data': req.post_data
                    })
                    print(f"  [XHR/Fetch] {req.method} {req.url[:120]}", flush=True)

        def on_res(res):
            if ('search' in res.url or 'job' in res.url or 'api' in res.url) and 'json' in res.headers.get('content-type', ''):
                try:
                    d = res.json()
                    print(f"  [JSON Response] {res.url[:100]} -> Keys: {list(d.keys()) if isinstance(d, dict) else len(d)}", flush=True)
                except:
                    pass

        page.on('request', on_req)
        page.on('response', on_res)

        page.goto('https://careers.hcltech.com/search/?q=&locationsearch=India', wait_until='networkidle', timeout=30000)
        time.sleep(3)

        # Click Search button
        btn = page.query_selector('input[type="submit"], button.btn-search, #search-submit')
        if btn:
            print("Clicking Search Button...", flush=True)
            btn.click()
            time.sleep(3)

        browser.close()

if __name__ == "__main__":
    inspect_hcl_network()

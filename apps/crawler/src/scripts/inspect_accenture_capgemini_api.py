import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_accenture_capgemini_api():
    print("=" * 80)
    print("SNIFFING ACCENTURE & CAPGEMINI RECRUITING APIS")
    print("=" * 80, flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        # 1. Accenture Network Sniffer
        captured_acc = []
        def on_acc_req(req):
            if any(k in req.url.lower() for k in ['job', 'search', 'api', 'services']):
                if req.resource_type in ['xhr', 'fetch']:
                    captured_acc.append(req.url)
                    print(f"  [Accenture XHR] {req.method} {req.url[:120]}", flush=True)

        page.on('request', on_acc_req)
        print("\nNavigating to Accenture Search...", flush=True)
        page.goto("https://www.accenture.com/in-en/careers/jobsearch?jk=&sb=1&pg=1", wait_until='networkidle', timeout=30000)
        time.sleep(3)

        # 2. Capgemini Network Sniffer
        page.remove_listener('request', on_acc_req)
        def on_cap_req(req):
            if any(k in req.url.lower() for k in ['job', 'search', 'api', 'vacancies']):
                if req.resource_type in ['xhr', 'fetch']:
                    print(f"  [Capgemini XHR] {req.method} {req.url[:120]}", flush=True)

        page.on('request', on_cap_req)
        print("\nNavigating to Capgemini Search...", flush=True)
        page.goto("https://www.capgemini.com/in-en/careers/job-search/", wait_until='networkidle', timeout=30000)
        time.sleep(3)

        browser.close()

if __name__ == "__main__":
    inspect_accenture_capgemini_api()

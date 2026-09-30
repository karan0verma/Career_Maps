import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_hcl_api_payload():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        endpoint_info = {}

        def on_req(req):
            if '/services/recruiting/v1/jobs' in req.url:
                endpoint_info['request'] = {
                    'url': req.url,
                    'headers': dict(req.headers),
                    'post_data': req.post_data
                }
                print("\n[Captured HCLTech Request]")
                print("Headers:", req.headers)
                print("Payload:", req.post_data)

        def on_res(res):
            if '/services/recruiting/v1/jobs' in res.url:
                try:
                    d = res.json()
                    endpoint_info['response'] = d
                    print("\n[Captured HCLTech Response]")
                    print("Keys:", list(d.keys()))
                    print("totalJobs:", d.get('totalJobs'))
                    jobs = d.get('jobs', [])
                    print(f"Jobs in batch: {len(jobs)}")
                    if jobs:
                        print("Sample Job:", json.dumps(jobs[0], indent=2))
                except Exception as e:
                    print("Error parsing response:", e)

        page.on('request', on_req)
        page.on('response', on_res)

        page.goto('https://careers.hcltech.com/search/?q=', wait_until='networkidle', timeout=35000)
        time.sleep(4)

        browser.close()

if __name__ == "__main__":
    inspect_hcl_api_payload()

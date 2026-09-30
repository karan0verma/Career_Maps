import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_wipro_post():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context()
        page = context.new_page()

        def on_req(req):
            if 'recruiting' in req.url:
                print(f"\n[REQUEST] {req.method} {req.url}")
                print("Headers:", req.headers)
                print("Post data:", req.post_data)

        def on_res(res):
            if 'recruiting' in res.url:
                try:
                    data = res.json()
                    print(f"\n[RESPONSE] {res.status} {res.url}")
                    print("Sample Response:", json.dumps(data, indent=2)[:500])
                except Exception as e:
                    print("Res parse err:", e)

        page.on('request', on_req)
        page.on('response', on_res)

        page.goto('https://careers.wipro.com/search/?q=&locationsearch=India', wait_until='networkidle', timeout=30000)
        time.sleep(5)

        browser.close()

if __name__ == "__main__":
    inspect_wipro_post()

import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def probe_wipro():
    print("=" * 75)
    print("PROBING WIPRO SUCCESSFACTORS CAREER SITE")
    print("=" * 75)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        def on_res(res):
            ct = res.headers.get('content-type', '')
            if 'json' in ct and ('job' in res.url.lower() or 'search' in res.url.lower() or 'facet' in res.url.lower()):
                try:
                    data = res.json()
                    print(f"\n[WIPRO JSON] {res.url}")
                    if isinstance(data, list):
                        print(f"  List of {len(data)} items. Sample: {str(data[0])[:200]}")
                    elif isinstance(data, dict):
                        print(f"  Dict keys: {list(data.keys())}")
                        for k in data.keys():
                            if isinstance(data[k], list):
                                print(f"    '{k}' count: {len(data[k])}")
                except Exception:
                    pass

        page.on('response', on_res)

        # Go to wipro search page
        search_urls = [
            "https://careers.wipro.com/careers-home/search-results",
            "https://careers.wipro.com/careers-home/",
            "https://careers.wipro.com/search/?createNewAlert=false&q="
        ]

        for su in search_urls:
            print(f"\nTesting: {su}")
            try:
                page.goto(su, wait_until='networkidle', timeout=30000)
                time.sleep(3)
                print(f"Loaded: {page.url} | Title: {page.title()}")
            except Exception as e:
                print(f"Error loading {su}: {e}")

        browser.close()

if __name__ == "__main__":
    probe_wipro()

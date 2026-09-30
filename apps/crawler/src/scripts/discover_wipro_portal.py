import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def discover_wipro():
    print("=" * 75)
    print("DISCOVERING WIPRO CAREER PORTAL & API ENDPOINTS")
    print("=" * 75)

    captured_apis = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel='chrome',
            headless=True,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            viewport={'width': 1440, 'height': 900}
        )
        page = context.new_page()

        def handle_response(response):
            url = response.url
            ct = response.headers.get('content-type', '')
            if 'json' in ct or 'api' in url or 'job' in url.lower() or 'search' in url.lower():
                try:
                    status = response.status
                    if status == 200 and ('json' in ct or 'javascript' not in ct):
                        print(f"[API HIT] {response.request.method} {url} -> {status} (CT: {ct[:30]})")
                        captured_apis.append({
                            'url': url,
                            'method': response.request.method,
                            'post_data': response.request.post_data,
                            'headers': response.request.headers
                        })
                except Exception:
                    pass

        page.on('response', handle_response)

        targets = [
            'https://careers.wipro.com/careers-home/',
            'https://careers.wipro.com/careers-home/jobs',
            'https://www.wipro.com/careers/'
        ]

        for target in targets:
            print(f"\nProbing: {target}")
            try:
                page.goto(target, wait_until='networkidle', timeout=30000)
                time.sleep(4)
                print(f"Page Title: {page.title()}")
                print(f"Current URL: {page.url}")
            except Exception as e:
                print(f"Probe error on {target}: {e}")

        browser.close()

    print("\n" + "=" * 75)
    print(f"CAPTURED {len(captured_apis)} POTENTIAL API ENDPOINTS FOR WIPRO")
    print("=" * 75)
    for api in captured_apis[:10]:
        print(f"• {api['method']} {api['url']}")
        if api.get('post_data'):
            print(f"  Post Data: {api['post_data'][:200]}")

if __name__ == "__main__":
    discover_wipro()

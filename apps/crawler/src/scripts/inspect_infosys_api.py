import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_infosys_api():
    print("=" * 75)
    print("INSPECTING INFOSYS INTAP GATEWAY API")
    print("=" * 75)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1440, 'height': 900}
        )
        page = context.new_page()

        api_responses = []

        def handle_response(response):
            if 'intapgateway' in response.url or 'careersci' in response.url:
                try:
                    data = response.json()
                    print(f"\n[FOUND GATEWAY RESPONSE] {response.request.method} {response.url}")
                    print("Sample Data Keys:", list(data.keys()) if isinstance(data, dict) else f"List length: {len(data)}")
                    api_responses.append({'url': response.url, 'data': data, 'headers': response.request.headers})
                except Exception:
                    pass

        page.on('response', handle_response)

        page.goto('https://career.infosys.com/joblist', wait_until='networkidle', timeout=35000)
        time.sleep(5)

        # Try clicking search or interacting with joblist
        page.evaluate("""() => {
            const btn = document.querySelector('button.search-btn, button[type="submit"], .btn-search');
            if (btn) btn.click();
        }""")
        time.sleep(4)

        browser.close()

if __name__ == "__main__":
    inspect_infosys_api()

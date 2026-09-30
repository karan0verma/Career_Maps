import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def find_wipro_pagination():
    print("=" * 75)
    print("CAPTURING WIPRO SEARCH PAGINATION")
    print("=" * 75)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        captured = []

        def on_res(res):
            ct = res.headers.get('content-type', '')
            if 'wipro.com' in res.url or 'jobs2web' in res.url:
                if 'json' in ct or 'search' in res.url.lower():
                    print(f"[RES] {res.status} {res.url} (CT: {ct[:30]})")
                    captured.append(res.url)

        page.on('response', on_res)

        page.goto('https://careers.wipro.com/careers-home/', wait_until='networkidle', timeout=30000)
        time.sleep(3)

        # Click on search or view all jobs button
        print("Clicking search button on Wipro home...")
        page.evaluate("""() => {
            const btn = document.querySelector('.btn-search, #search-button, button.btn-primary, a[href*="search"]');
            if (btn) btn.click();
        }""")
        time.sleep(4)

        print(f"Current URL: {page.url}")
        browser.close()

if __name__ == "__main__":
    find_wipro_pagination()

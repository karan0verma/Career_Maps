import os
import sys
import time
from playwright.sync_api import sync_playwright

def verify_all_pages():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page()

        for path in ['/', '/jobs', '/companies']:
            url = f"http://localhost:3000{path}"
            print(f"\nTesting {url}...", flush=True)
            page.goto(url, wait_until='networkidle', timeout=30000)
            time.sleep(2)

            banner_text = page.evaluate("""() => {
                const el = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.includes('CURRENTLY ACTIVE'));
                return el ? el.innerText : 'Currently Active text not found';
            }""")
            print(f"[{path}] Banner Check:")
            print(banner_text.encode('ascii', 'replace').decode('ascii')[:200])

        browser.close()

if __name__ == "__main__":
    verify_all_pages()

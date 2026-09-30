import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_hcl_pagination():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        for test_url in [
            "https://careers.hcltech.com/go/India/9553955/?startrow=25",
            "https://careers.hcltech.com/go/India/9553955/2/",
            "https://careers.hcltech.com/search/?q=&locationsearch=India&startrow=25"
        ]:
            page.goto(test_url, wait_until='networkidle', timeout=30000)
            time.sleep(2)
            jobs = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a[href*="/job/"]')).map(a => a.href);
            }""")
            print(f"URL: {test_url} -> Found {len(jobs)} /job/ links: {jobs[:2]}")

        browser.close()

if __name__ == "__main__":
    inspect_hcl_pagination()

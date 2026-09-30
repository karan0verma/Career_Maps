import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def test_hcl_startrow():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        for offset in [0, 25, 50, 75, 100]:
            url = f"https://careers.hcltech.com/search/?q=&startrow={offset}"
            page.goto(url, wait_until='networkidle', timeout=30000)
            time.sleep(1)

            jobs = page.evaluate("""() => {
                const links = Array.from(document.querySelectorAll('a[href*="/job/"]'));
                return links.map(a => ({
                    title: a.innerText.trim(),
                    href: a.href
                })).filter(j => j.title && j.href);
            }""")
            print(f"Offset {offset}: Found {len(jobs)} jobs. First 2: {jobs[:2]}")

        browser.close()

if __name__ == "__main__":
    test_hcl_startrow()

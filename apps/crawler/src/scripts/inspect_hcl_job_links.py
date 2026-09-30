import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_hcl_job_links():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        page.goto('https://careers.hcltech.com/go/India/9553955/', wait_until='networkidle', timeout=30000)
        time.sleep(4)

        job_links = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('a[href*="/job/"]')).map(a => ({
                text: a.innerText.trim(),
                href: a.href
            }));
        }""")
        print(f"Found {len(job_links)} /job/ links on HCLTech India:")
        for l in job_links[:15]:
            print(f"  {l['text']} -> {l['href']}")

        browser.close()

if __name__ == "__main__":
    inspect_hcl_job_links()

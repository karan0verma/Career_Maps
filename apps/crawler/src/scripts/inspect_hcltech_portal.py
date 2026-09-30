import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_hcl_portal():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        page.goto('https://www.hcltech.com/careers/Careers-in-india', wait_until='domcontentloaded', timeout=30000)
        time.sleep(4)

        print("India Page URL:", page.url)
        print("India Page Title:", page.title())

        # Check job links or portals
        links = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('a')).map(a => ({
                text: a.innerText.trim(),
                href: a.href
            })).filter(l => l.href.includes('job') || l.href.includes('career') || l.href.includes('search'));
        }""")
        print(f"Captured {len(links)} links:")
        for l in links[:10]:
            print("  ", l)

        browser.close()

if __name__ == "__main__":
    inspect_hcl_portal()

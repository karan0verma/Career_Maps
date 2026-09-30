import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_hcl_page_html():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        page.goto('https://careers.hcltech.com/go/India/9553955/', wait_until='networkidle', timeout=30000)
        time.sleep(4)

        # Get all links on page
        all_links = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('a')).map(a => ({
                text: a.innerText.trim(),
                href: a.href
            })).filter(l => l.text && l.href);
        }""")
        print(f"Total links on HCLTech India page: {len(all_links)}")
        for l in all_links[:20]:
            print("  ", l)

        browser.close()

if __name__ == "__main__":
    inspect_hcl_page_html()

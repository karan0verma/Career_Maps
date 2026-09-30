import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_cognizant_dom():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        page.goto('https://careers.cognizant.com/india-en/jobs/', wait_until='domcontentloaded', timeout=30000)
        time.sleep(5)

        # Check page URL and title
        print("Page URL:", page.url)
        print("Page Title:", page.title())

        # Check all links with /job/ or /jobs/
        links = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('a[href*="/job/"], a[href*="/jobs/"]')).map(a => ({
                text: a.innerText.trim(),
                href: a.href
            }));
        }""")
        print(f"Found {len(links)} job links in DOM:")
        for l in links[:5]:
            print("  ", l)

        # Check phenom global JS object
        ph_data = page.evaluate("""() => {
            return window.phApp ? Object.keys(window.phApp) : null;
        }""")
        print("phApp keys:", ph_data)

        browser.close()

if __name__ == "__main__":
    inspect_cognizant_dom()

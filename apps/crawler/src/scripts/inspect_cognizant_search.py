import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_cognizant_search():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        page.goto('https://careers.cognizant.com/india-en/jobs/', wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)

        # Look for search input and form
        search_box = page.query_selector('input[type="text"], input[name="keyword"], input[placeholder*="Search"]')
        if search_box:
            search_box.fill('Engineer')
            search_box.press('Enter')
            time.sleep(5)
            print("After Search URL:", page.url)
            print("After Search Title:", page.title())

            # Find all links
            cards = page.evaluate("""() => {
                const links = Array.from(document.querySelectorAll('a'));
                return links.filter(a => a.href.includes('/job/') || a.href.includes('/jobs/')).map(a => ({
                    text: a.innerText.trim(),
                    href: a.href
                }));
            }""")
            print(f"Captured {len(cards)} search result cards:")
            for c in cards[:10]:
                print("  ", c)

        browser.close()

if __name__ == "__main__":
    inspect_cognizant_search()

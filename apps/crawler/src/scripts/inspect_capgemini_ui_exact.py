import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_capgemini():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        page = browser.new_page()
        page.goto("https://www.capgemini.com/in-en/careers/job-search/?country_code=in-en", wait_until='domcontentloaded', timeout=20000)
        time.sleep(4)

        # Get all locations and job counts directly from the portal UI
        ui_data = page.evaluate("""() => {
            const results = {};
            const filterItems = Array.from(document.querySelectorAll('[data-facet="location"] label, .filter-location label, input[name*="location"]')).map(el => el.innerText.trim());
            
            // Also let's check page text
            const headings = Array.from(document.querySelectorAll('h1, h2, h3, [class*="title"], [class*="count"]')).map(h => h.innerText.trim());

            return {
                filterItems,
                headings: headings.slice(0, 10)
            };
        }""")

        print("Capgemini UI Direct Inspection:")
        print(json.dumps(ui_data, indent=2))
        browser.close()

if __name__ == "__main__":
    inspect_capgemini()

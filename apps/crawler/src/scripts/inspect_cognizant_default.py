import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_india_en():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        url = "https://careers.cognizant.com/india-en/jobs/?pagesize=50"
        print(f"Navigating to {url}", flush=True)
        page.goto(url, wait_until='networkidle', timeout=30000)
        time.sleep(3)

        count_text = page.evaluate("""() => {
            const el = document.querySelector('.job-count, .search-count, p');
            return el ? el.innerText : '';
        }""")
        print("Count Text:", count_text)

        # Extract all job cards
        cards = page.evaluate("""() => {
            const items = Array.from(document.querySelectorAll('.card, .job, [class*="job-card"], [class*="job-item"], [data-ph-id*="job"]'));
            return items.map(el => ({
                text: el.innerText.slice(0, 150).replace(/\\n/g, ' | '),
                link: el.querySelector('a')?.href || el.closest('a')?.href || ''
            }));
        }""")
        print(f"Found {len(cards)} cards:")
        for c in cards[:5]:
            print("  ", c)

        browser.close()

if __name__ == "__main__":
    inspect_india_en()

import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def inspect_results():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        url = "https://careers.cognizant.com/india-en/jobs/?keyword=&location=India&pagesize=50"
        print(f"Navigating to {url}", flush=True)
        page.goto(url, wait_until='networkidle', timeout=30000)
        time.sleep(5)

        # Print all text in main content
        content = page.evaluate("""() => {
            const headings = Array.from(document.querySelectorAll('h2, h3, h4, .job-title, [class*="job"], [class*="title"], [class*="card"]')).map(el => ({
                tag: el.tagName,
                className: el.className,
                text: el.innerText.trim(),
                parentLink: el.closest('a')?.href || el.querySelector('a')?.href || ''
            }));
            return headings.filter(h => h.text.length > 5 && h.text.length < 100);
        }""")
        print(f"Found {len(content)} candidate job elements:")
        for c in content[:15]:
            print("  ", c)

        browser.close()

if __name__ == "__main__":
    inspect_results()

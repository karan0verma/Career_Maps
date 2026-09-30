import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def test_cognizant_pagination_params():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        for test_url in [
            "https://careers.cognizant.com/india-en/jobs/?from=50&pagesize=50#results",
            "https://careers.cognizant.com/india-en/jobs/?page=2#results",
            "https://careers.cognizant.com/india-en/jobs/?offset=50#results",
            "https://careers.cognizant.com/india-en/jobs/?start=50#results"
        ]:
            page.goto(test_url, wait_until='networkidle', timeout=30000)
            time.sleep(2)
            first_job = page.evaluate("""() => {
                const a = document.querySelector('a[href*="/jobs/"]');
                return a ? a.innerText.trim() : 'None';
            }""")
            print(f"URL: {test_url} -> First Job: {first_job}")

        browser.close()

if __name__ == "__main__":
    test_cognizant_pagination_params()

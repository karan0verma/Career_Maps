import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def test_click_pagination():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        page = context.new_page()

        page.goto('https://careers.cognizant.com/india-en/jobs/?pagesize=50', wait_until='networkidle', timeout=30000)
        time.sleep(3)

        # Check pagination controls in DOM
        pagination_html = page.evaluate("""() => {
            const el = document.querySelector('.pagination, .pager, [class*="pagination"], [class*="pager"], nav');
            return el ? el.outerHTML : 'No pagination container';
        }""")
        print("Pagination Container:", pagination_html[:300])

        # Click next
        next_link = page.query_selector('a[aria-label*="Next"], a.next, [class*="next"]')
        if next_link:
            print("Next link found:", next_link.get_attribute('href'))
            next_link.click()
            time.sleep(3)
            print("After click URL:", page.url)

        browser.close()

if __name__ == "__main__":
    test_click_pagination()

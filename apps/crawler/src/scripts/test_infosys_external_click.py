import os
import sys
import time
from playwright.sync_api import sync_playwright

def test_external_click():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Step 1: Open localhost:3000/jobs
        print("Opening localhost:3000/jobs...", flush=True)
        page.goto('http://localhost:3000/jobs', wait_until='networkidle', timeout=20000)
        time.sleep(2)

        # Step 2: Find first Infosys job card
        print("Finding Infosys job card...", flush=True)
        cards = page.query_selector_all('a[href*="/jobs/"]')
        print(f"Found {len(cards)} job links", flush=True)
        
        # Click on the first link that has Infosys in its parent card
        for c in cards:
            text = c.evaluate("el => el.closest('.bg-white')?.innerText || ''")
            if 'Infosys' in text:
                print("Found Infosys card text:", text.replace('\n', ' ')[:100], flush=True)
                c.click()
                break

        time.sleep(3)
        print("Current URL on job details page:", page.url, flush=True)

        # Step 3: Check the Apply Now button href / onclick
        apply_btn = page.query_selector('button:has-text("Apply Now"), a:has-text("Apply Now")')
        if apply_btn:
            print("Found Apply Now button!", flush=True)
            # Listen for new popup tab
            with context.expect_page() as new_page_info:
                apply_btn.click()
            
            new_page = new_page_info.value
            new_page.wait_for_load_state('domcontentloaded')
            time.sleep(5)
            print("Opened target URL in new tab:", new_page.url, flush=True)
            print("New page title:", new_page.title(), flush=True)
            print("New page text length:", len(new_page.inner_text('body')), flush=True)
            print("New page text snippet:", new_page.inner_text('body').replace('\n', ' ')[:300], flush=True)

        browser.close()

if __name__ == "__main__":
    test_external_click()

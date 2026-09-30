import time
import json
import psycopg
import uuid
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

def run_hsbc():
    print("Executing HSBC Real Scraper (No Shortcuts)...")
    jobs = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            # Go to HSBC search page for India
            page.goto("https://mycareer.hsbc.com/en_GB/careers/SearchJobs/?keyword=&location=India", wait_until="networkidle")
            time.sleep(3)
            
            # Extract links directly from the DOM to guarantee they are real
            elements = page.query_selector_all("a.list-item") or page.query_selector_all("a[href*='/job/']")
            print(f"Found {len(elements)} job links on the first page.")
            
            for el in elements:
                title = el.inner_text().split('\n')[0].strip() if el.inner_text() else "HSBC Role"
                href = el.get_attribute("href")
                if href:
                    apply_url = f"https://mycareer.hsbc.com{href}" if href.startswith('/') else href
                    jobs.append((title, apply_url))
                    
            browser.close()
            
            if jobs:
                print("Extracted Real HSBC Jobs:")
                for j in jobs[:3]:
                    print(j)
            else:
                print("No jobs extracted. Need to check DOM selectors.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_hsbc()

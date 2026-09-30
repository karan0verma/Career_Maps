import os
import sys
import time
from playwright.sync_api import sync_playwright

def test_foolproof():
    print("=" * 80)
    print("TESTING INFOSYS URLS IN COMPLETELY EMPTY BROWSER CONTEXT")
    print("=" * 80)

    urls = [
        ("Direct jobdesc", "https://career.infosys.com/jobdesc?jobReferenceCode=INFSYS-EXTERNAL-249251"),
        ("Joblist with searchJob", "https://career.infosys.com/joblist?companyhiringtype=IL&countrycode=IN&searchJob=INFSYS-EXTERNAL-249251"),
        ("Joblist with keyword", "https://career.infosys.com/joblist?companyhiringtype=IL&countrycode=IN&keyword=INFSYS-EXTERNAL-249251"),
        ("Jobs route with searchJob", "https://career.infosys.com/jobs?companyhiringtype=IL&countrycode=IN&searchJob=INFSYS-EXTERNAL-249251"),
        ("Joblist clean India", "https://career.infosys.com/joblist?companyhiringtype=IL&countrycode=IN")
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)

        for label, u in urls:
            context = browser.new_context()
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            
            print(f"\n--- Testing: {label} ---", flush=True)
            print(f"URL: {u}", flush=True)
            page.goto(u, wait_until='networkidle', timeout=25000)
            time.sleep(3)
            
            body = page.inner_text('body').replace('\n', ' ')
            print(f"Final URL: {page.url}", flush=True)
            print(f"Body length: {len(body)}", flush=True)
            print(f"Snippet: {body[:250]}", flush=True)
            print(f"Unhandled Page Errors: {errors}", flush=True)
            
            context.close()

        browser.close()

if __name__ == "__main__":
    test_foolproof()

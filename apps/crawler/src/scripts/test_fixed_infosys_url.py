import os
import sys
import time
from playwright.sync_api import sync_playwright

def test_fixed_url():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context()
        page = context.new_page()

        url = "https://career.infosys.com/jobdesc?jobReferenceCode=INFSYS-EXTERNAL-249251&companyhiringtype=IL&countrycode=IN"
        print(f"Testing URL with hiring params: {url}", flush=True)
        page.goto(url, wait_until='networkidle', timeout=25000)
        time.sleep(3)
        
        text = page.inner_text('body').replace('\n', ' ')
        print("Page text length:", len(text), flush=True)
        print("Page text snippet:", text[:300], flush=True)
        
        browser.close()

if __name__ == "__main__":
    test_fixed_url()

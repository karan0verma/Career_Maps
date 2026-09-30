import os
import sys
import time
from playwright.sync_api import sync_playwright

def capture_screenshots():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        jobs = [
            ('249251', 'https://career.infosys.com/jobdesc?jobReferenceCode=INFSYS-EXTERNAL-249251&companyhiringtype=IL&countrycode=IN'),
            ('251345', 'https://career.infosys.com/jobdesc?jobReferenceCode=INFSYS-EXTERNAL-251345&companyhiringtype=IL&countrycode=IN')
        ]

        out_dir = r"C:\Users\Ahana Singh\.gemini\antigravity\scratch\career-maps\apps\crawler\src\scripts"

        for code, url in jobs:
            print(f"Loading {code}: {url}", flush=True)
            page.goto(url, wait_until='networkidle', timeout=25000)
            time.sleep(3)
            out_file = os.path.join(out_dir, f"infosys_{code}.png")
            page.screenshot(path=out_file, full_page=True)
            print(f"Saved screenshot to {out_file}", flush=True)

        browser.close()

if __name__ == "__main__":
    capture_screenshots()

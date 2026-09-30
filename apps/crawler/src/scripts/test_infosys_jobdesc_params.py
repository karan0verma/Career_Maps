import os
import sys
import time
from playwright.sync_api import sync_playwright

def test_jobdesc():
    print("=" * 75)
    print("TESTING INFOSYS JOBDESC URL PATTERNS")
    print("=" * 75)

    urls = [
        "https://career.infosys.com/jobdesc?jobReferenceCode=INFSYS-EXTERNAL-251345",
        "https://career.infosys.com/jobdesc?jobReferenceCode=INFSYS-EXTERNAL-251345&companyhiringtype=IL&countrycode=IN",
        "https://career.infosys.com/#/jobdesc?jobReferenceCode=INFSYS-EXTERNAL-251345",
        "https://career.infosys.com/joblist?jobReferenceCode=INFSYS-EXTERNAL-251345"
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context()

        for u in urls:
            page = context.new_page()
            console_msgs = []
            page.on('console', lambda msg: console_msgs.append(msg.text))
            
            print(f"\nNavigating to: {u}")
            try:
                page.goto(u, wait_until='load', timeout=20000)
                time.sleep(4)
                print(f"  Final URL: {page.url}")
                print(f"  Title: {page.title()}")
                body = page.inner_text('body').strip()
                print(f"  Body Length: {len(body)}")
                if len(body) < 100:
                    print(f"  Body content: '{body}'")
                    print(f"  Console errors: {[m for m in console_msgs if 'error' in m.lower()]}")
                else:
                    print(f"  Body snippet: {body[:150].replace(chr(10), ' ')}")
            except Exception as e:
                print(f"  Error on {u}: {e}")
            page.close()

        browser.close()

if __name__ == "__main__":
    test_jobdesc()

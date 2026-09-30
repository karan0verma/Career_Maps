import os
import sys
import time
from playwright.sync_api import sync_playwright

def test_routes():
    print("=" * 75)
    print("TESTING INFOSYS ROUTE VARIATIONS WITH SOURCEID")
    print("=" * 75)

    urls = [
        "https://career.infosys.com/jobDesc?jobReferenceCode=INFSYS-EXTERNAL-249251&sourceId=1",
        "https://career.infosys.com/jobdesc?jobReferenceCode=INFSYS-EXTERNAL-249251&sourceId=1",
        "https://career.infosys.com/jobview?jobReferenceCode=INFSYS-EXTERNAL-249251&sourceId=1",
        "https://career.infosys.com/jobapply?jobReferenceCode=INFSYS-EXTERNAL-249251&sourceId=1"
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context()

        for u in urls:
            page = context.new_page()
            print(f"\nNavigating to: {u}")
            page.goto(u, wait_until='load', timeout=25000)
            time.sleep(3)
            print("  Final URL:", page.url)
            print("  Title:", page.title())
            body = page.inner_text('body').replace('\n', ' ')
            print("  Snippet:", body[:200])
            page.close()

        browser.close()

if __name__ == "__main__":
    test_routes()

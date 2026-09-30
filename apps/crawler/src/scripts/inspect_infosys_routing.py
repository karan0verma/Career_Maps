import os
import sys
import time
from playwright.sync_api import sync_playwright

def inspect_infosys_routing():
    print("=" * 75)
    print("INSPECTING INFOSYS JOB DETAIL / APPLY URL ROUTING")
    print("=" * 75)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Let's test the URL format we generated:
        test_url_1 = "https://career.infosys.com/jobdesc?jobReferenceCode=INFSYS-EXTERNAL-251345"
        print(f"Testing URL 1: {test_url_1}")
        page.goto(test_url_1, timeout=30000)
        time.sleep(4)
        print("Final URL after navigation 1:", page.url)
        print("Page text snippet 1:", page.inner_text('body')[:300] if page.inner_text('body') else "EMPTY")

        # Now let's visit joblist and click a job to see the exact internal route
        page.goto('https://career.infosys.com/joblist', wait_until='networkidle', timeout=30000)
        time.sleep(4)

        print("\nClicking first job card on joblist...")
        page.evaluate("""() => {
            const cards = document.querySelectorAll('.card, .jobcard, .job-title, h4, a');
            for (let c of cards) {
                if (c.innerText && c.innerText.length > 5 && !c.innerText.includes('Home') && !c.innerText.includes('Search')) {
                    c.click();
                    break;
                }
            }
        }""")
        time.sleep(4)

        print("Current URL after clicking job card:", page.url)
        print("Page text snippet after click:", page.inner_text('body')[:300])

        browser.close()

if __name__ == "__main__":
    inspect_infosys_routing()

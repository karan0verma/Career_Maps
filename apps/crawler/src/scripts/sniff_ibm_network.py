import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()

    def log_response(response):
        if any(k in response.url for k in ['api', 'jobs', 'search', 'eightfold', 'brassring']):
            print("Captured XHR/Fetch:", response.url, "Status:", response.status)

    page.on("response", log_response)
    print("Navigating to IBM Careers search...", flush=True)
    page.goto("https://www.ibm.com/careers/search?field_keyword_08_bm%5B0%5D=India", wait_until='networkidle', timeout=30000)
    time.sleep(5)
    browser.close()

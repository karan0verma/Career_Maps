import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()

    def log_response(response):
        if "api" in response.url or "search" in response.url or "jobs" in response.url:
            print("Captured:", response.url, "Status:", response.status)

    page.on("response", log_response)
    print("Navigating to Google Careers India...", flush=True)
    page.goto("https://www.google.com/about/careers/applications/jobs/results/?location=India", wait_until='networkidle', timeout=30000)
    time.sleep(5)
    browser.close()

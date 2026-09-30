import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()

    def log_req(req):
        if "widgets" in req.url or "search" in req.url:
            print("\nURL:", req.url)
            print("Post Data:", req.post_data)

    def log_res(res):
        if "widgets" in res.url or "search" in res.url:
            print("Status:", res.status)

    page.on("request", log_req)
    page.on("response", log_res)

    print("Navigating to Cisco Phenom search...", flush=True)
    page.goto("https://careers.cisco.com/global/en/search-results?q=India", wait_until='networkidle', timeout=30000)
    time.sleep(4)

    # Click page 2 button if available
    next_btn = page.query_selector('a[aria-label="Next"], [class*="next"], button:has-text("2")')
    if next_btn:
        print("Clicking next page...", flush=True)
        next_btn.click()
        time.sleep(4)

    browser.close()

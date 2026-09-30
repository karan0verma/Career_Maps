import urllib.request
import json
import time
from playwright.sync_api import sync_playwright

def verify_ms_direct_url():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context()
        page = context.new_page()

        url = "https://apply.careers.microsoft.com/careers/job/1970393556950426"
        print(f"Opening Microsoft Direct URL: {url}", flush=True)
        page.goto(url, wait_until='networkidle', timeout=30000)
        time.sleep(3)

        title = page.title()
        body = page.inner_text('body').replace('\n', ' ')
        print("Page Title:", title, flush=True)
        print("Body Snippet:", body[:300], flush=True)

        browser.close()

if __name__ == "__main__":
    verify_ms_direct_url()

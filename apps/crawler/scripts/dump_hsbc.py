import time
from playwright.sync_api import sync_playwright

def inspect_hsbc():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://mycareer.hsbc.com/en_GB/careers/SearchJobs/?keyword=&location=India", wait_until="networkidle")
        time.sleep(5)
        html = page.content()
        with open("hsbc_dump.html", "w", encoding="utf-8") as f:
            f.write(html)
        browser.close()
        print("Dumped HTML to hsbc_dump.html")

if __name__ == "__main__":
    inspect_hsbc()

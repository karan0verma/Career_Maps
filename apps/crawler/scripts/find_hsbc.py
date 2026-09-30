import time
from playwright.sync_api import sync_playwright

def find_hsbc():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://mycareer.hsbc.com/", wait_until="networkidle")
        time.sleep(3)
        print("Final URL:", page.url)
        browser.close()

if __name__ == "__main__":
    find_hsbc()

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import time

def test_stealth():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        Stealth().apply_stealth_sync(page)
        
        print("Navigating...")
        res = page.goto("https://careers.cognizant.com/india-en/jobs/")
        print("Status:", res.status if res else "None")
        page.wait_for_timeout(5000)
        
        title = page.title()
        print("Title:", title)
        content = page.content()
        if "Just a moment" in content:
            print("Still blocked by Cloudflare in headless mode.")
        else:
            print("Successfully bypassed Cloudflare!")
            
        browser.close()

if __name__ == "__main__":
    test_stealth()

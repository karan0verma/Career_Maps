import os
import sys
import time
from playwright.sync_api import sync_playwright

def verify_hamburger():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page()

        print("Navigating to http://localhost:3000...", flush=True)
        page.goto('http://localhost:3000', wait_until='networkidle', timeout=30000)
        time.sleep(2)

        # 1. Look for hamburger menu button
        menu_btn = page.query_selector('button[title="Open Navigation"]')
        print(f"Hamburger Menu Button Found: {menu_btn is not None}", flush=True)

        if menu_btn:
            # Click hamburger menu
            print("Clicking 3-line hamburger menu...", flush=True)
            menu_btn.click()
            time.sleep(1)

            # Check if drawer opened and list items inside
            drawer_items = page.evaluate("""() => {
                const links = Array.from(document.querySelectorAll('div[class*="w-[290px]"] a, div[class*="w-[320px]"] a'));
                return links.map(a => a.innerText.trim()).filter(Boolean);
            }""")
            print("Opened Drawer Items:", drawer_items)

            # Take screenshot of open drawer
            screenshot_path = "C:/Users/Ahana Singh/.gemini/antigravity/scratch/career-maps/apps/frontend/drawer_open_screenshot.png"
            page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    verify_hamburger()

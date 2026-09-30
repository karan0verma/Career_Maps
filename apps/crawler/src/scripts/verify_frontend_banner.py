import os
import sys
import time
from playwright.sync_api import sync_playwright

def verify_banner():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page()

        print("Navigating to http://localhost:3000...", flush=True)
        page.goto('http://localhost:3000', wait_until='networkidle', timeout=30000)
        time.sleep(3)

        # Check banner visibility and text
        banner_text = page.evaluate("""() => {
            const b = document.querySelector('.fixed.bottom-5');
            return b ? b.innerText : 'Banner not found';
        }""")
        print("\n--- Live Floating Banner Text on Website ---")
        print(banner_text.encode('ascii', 'replace').decode('ascii'))

        # Take a screenshot
        screenshot_path = "C:/Users/Ahana Singh/.gemini/antigravity/scratch/career-maps/apps/frontend/banner_screenshot.png"
        page.screenshot(path=screenshot_path)
        print(f"\nScreenshot saved to: {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    verify_banner()

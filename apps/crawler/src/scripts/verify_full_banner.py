import os
import sys
import time
from playwright.sync_api import sync_playwright

def verify_full_banner():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page()

        print("Navigating to http://localhost:3000...", flush=True)
        page.goto('http://localhost:3000', wait_until='networkidle', timeout=30000)
        time.sleep(3)

        # Check full width banner
        banner_info = page.evaluate("""() => {
            const b = document.querySelector('.animate-marquee, .bg-gradient-to-r');
            return b ? b.innerText : 'Banner not found';
        }""")
        print("\n--- Live Full-Width Streaming Banner Text ---")
        print(banner_info.encode('ascii', 'replace').decode('ascii'))

        # Save screenshot
        screenshot_path = "C:/Users/Ahana Singh/.gemini/antigravity/scratch/career-maps/apps/frontend/full_banner_screenshot.png"
        page.screenshot(path=screenshot_path)
        print(f"\nScreenshot saved to: {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    verify_full_banner()

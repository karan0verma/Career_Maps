import os
import sys
import time
from playwright.sync_api import sync_playwright

def verify_logos():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page()

        print("Navigating to http://localhost:3000/companies...", flush=True)
        page.goto('http://localhost:3000/companies', wait_until='networkidle', timeout=30000)
        time.sleep(3)

        # Inspect company logo image sources
        company_logos = page.evaluate("""() => {
            const cards = Array.from(document.querySelectorAll('a[href*="/companies/"]'));
            return cards.map(c => {
                const title = c.querySelector('h2') ? c.querySelector('h2').innerText : '';
                const img = c.querySelector('img');
                return {
                    name: title,
                    hasImg: img !== null,
                    src: img ? img.src : 'No image (Fallback icon)'
                };
            });
        }""")

        print("\n--- Verified Company Logos on Directory Page ---")
        for c in company_logos:
            print(f"  • {c['name']:32} | Has Logo: {c['hasImg']} | Source: {c['src'][:60]}")

        # Take screenshot of companies directory
        screenshot_path = "C:/Users/Ahana Singh/.gemini/antigravity/scratch/career-maps/apps/frontend/companies_logos_screenshot.png"
        page.screenshot(path=screenshot_path)
        print(f"\nScreenshot saved to: {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    verify_logos()

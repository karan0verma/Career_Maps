import sys
from playwright.sync_api import sync_playwright

def test_wipro():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        print("Navigating to https://careers.wipro.com/...")
        try:
            page.goto("https://careers.wipro.com/", timeout=15000)
            page.wait_for_timeout(3000)
            
            title = page.title()
            print(f"Page Title: {title}")
            
            # See if we can find job search elements or if we got blocked
            print("Content Snippet:")
            print(page.content()[:1000])
            
            # Check for bot challenge or captcha
            if "captcha" in page.content().lower() or "cloudflare" in page.content().lower() or "challenge" in page.title().lower() or "Access Denied" in page.title():
                print("POSSIBLY BLOCKED!")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    test_wipro()

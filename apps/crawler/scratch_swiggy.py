from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Navigating to https://careers.swiggy.com/")
        try:
            page.goto("https://careers.swiggy.com/", wait_until="networkidle")
            page.screenshot(path="swiggy_home.png")
            
            # Let's see if there is a jobs list or something
            # Print title
            print("Title:", page.title())
            
            # Save HTML
            html = page.content()
            with open("swiggy_home.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Saved swiggy_home.html and swiggy_home.png")
            
            # Check for bot block or specific selectors
            if "Access Denied" in html or "Captcha" in html:
                print("Possibly blocked by anti-bot")
                
        except Exception as e:
            print("Exception:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    inspect()

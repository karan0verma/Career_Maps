from playwright.sync_api import sync_playwright

def test_zomato_careers():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.zomato.com/careers")
        page.wait_for_timeout(5000)
        
        # Take a screenshot to see if we're blocked
        page.screenshot(path="zomato_careers.png")
        
        # Try to get the HTML
        html = page.content()
        with open("zomato_careers.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        print("DOM saved to zomato_careers.html")
        browser.close()

if __name__ == "__main__":
    test_zomato_careers()

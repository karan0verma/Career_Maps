from playwright.sync_api import sync_playwright

def test_click():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://careers.techmahindra.com/CurrentOpportunity.aspx", wait_until="networkidle")
        
        # Force click
        page.locator("input[value='Apply/Shortlist']").first.click(force=True)
        page.wait_for_timeout(3000)
        
        print("URL after click:", page.url)
        content = page.locator("body").inner_text()
        print("Content after click preview:")
        print(content[:500])
        
        # Look for the actual URL or apply link
        browser.close()

if __name__ == "__main__":
    test_click()

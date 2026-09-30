from playwright.sync_api import sync_playwright

def find_tcs_portal():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.tcs.com/careers", wait_until="domcontentloaded")
        print("TCS Main title:", page.title())
        
        # Get all external links that look like portals
        links = page.query_selector_all("a")
        for l in links:
            href = l.get_attribute("href")
            if href and 'jobs' in href.lower() or 'careers.' in href.lower() or 'apply' in href.lower():
                print("Found portal link:", href)
                
        browser.close()

if __name__ == "__main__":
    find_tcs_portal()

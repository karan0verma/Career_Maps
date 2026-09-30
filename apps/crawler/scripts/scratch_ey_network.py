from playwright.sync_api import sync_playwright

def intercept():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # log responses
        page.on("response", lambda r: print(f"Response: {r.url}") if 'api' in r.url or 'search' in r.url else None)
        
        page.goto("https://careers.ey.com/experienced/go/Careers-in-India/3468501/?q=&sortColumn=referencedate&sortDirection=desc")
        page.wait_for_timeout(3000)
        
        print(page.title())
        browser.close()

if __name__ == "__main__":
    intercept()

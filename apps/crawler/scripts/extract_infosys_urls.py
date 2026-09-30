from playwright.sync_api import sync_playwright
import time

def extract_infosys_urls():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        def handle_response(response):
            if "search" in response.url.lower() and "intap" in response.url.lower():
                print("Endpoint:", response.url)
                
        page.on("response", handle_response)
        
        print("Navigating to Infosys...")
        page.goto("https://career.infosys.com/joblist", wait_until="networkidle")
        page.wait_for_timeout(3000)
        
        print("Clicking a location...")
        try:
            page.locator("text='India'").first.click(timeout=3000)
            page.wait_for_timeout(3000)
        except Exception as e:
            pass
            
        browser.close()

if __name__ == "__main__":
    extract_infosys_urls()

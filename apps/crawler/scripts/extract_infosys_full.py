from playwright.sync_api import sync_playwright
import time

def extract_infosys_full():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        job_requests = []
        
        def handle_request(request):
            if "search" in request.url.lower() and request.method == "POST":
                print("POST Request:", request.url)
                print("POST Data:", request.post_data)
                
        page.on("request", handle_request)
        
        print("Navigating to Infosys...")
        page.goto("https://career.infosys.com/joblist", wait_until="networkidle")
        page.wait_for_timeout(3000)
        
        # Click search or similar to trigger search API
        try:
            page.locator("button:has-text('Search')").click(timeout=5000)
            page.wait_for_timeout(3000)
        except Exception as e:
            pass
            
        browser.close()

if __name__ == "__main__":
    extract_infosys_full()

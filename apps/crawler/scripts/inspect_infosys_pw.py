from playwright.sync_api import sync_playwright

def inspect_infosys():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        def handle_response(response):
            url = response.url.lower()
            if "api" in url or "job" in url or "search" in url:
                if response.status == 200 and "json" in response.headers.get("content-type", ""):
                    print(f"API endpoint found: {response.url}")
        
        page.on("response", handle_response)
        
        print("Navigating to Infosys...")
        page.goto("https://career.infosys.com/joblist", wait_until="networkidle")
        
        # Wait a bit to ensure API calls are made
        page.wait_for_timeout(3000)
        
        browser.close()

if __name__ == "__main__":
    inspect_infosys()

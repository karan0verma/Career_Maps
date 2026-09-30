from playwright.sync_api import sync_playwright

def inspect_cognizant():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        def handle_response(response):
            if "api" in response.url.lower() or "graphql" in response.url.lower() or "search" in response.url.lower() or "jobs" in response.url.lower():
                if response.status == 200 and "json" in response.headers.get("content-type", ""):
                    print(f"JSON endpoint: {response.url}")
        
        page.on("response", handle_response)
        page.goto("https://careers.cognizant.com/global-en/jobs/", wait_until="networkidle")
        print("Page URL:", page.url)
        browser.close()

if __name__ == "__main__":
    inspect_cognizant()

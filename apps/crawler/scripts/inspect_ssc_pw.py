from playwright.sync_api import sync_playwright

def inspect_ssc():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(ignore_https_errors=True)
        
        def handle_res(res):
            if "api" in res.url.lower() or "notice" in res.url.lower():
                print("API:", res.url)
                
        page.on("response", handle_res)
        
        print("Navigating to SSC...")
        page.goto("https://ssc.gov.in/", wait_until="networkidle")
        page.wait_for_timeout(3000)
        
        browser.close()

if __name__ == "__main__":
    inspect_ssc()

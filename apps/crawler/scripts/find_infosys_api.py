from playwright.sync_api import sync_playwright

def find_search_api():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        def handle_response(res):
            if res.status == 200 and "json" in res.headers.get("content-type", ""):
                if "intapgateway" in res.url:
                    print("Infosys API:", res.url)
                
        page.on("response", handle_response)
        
        page.goto("https://career.infosys.com/joblist", wait_until="networkidle")
        
        # Click search
        try:
            btn = page.locator("button.search-btn")
            if btn.count() > 0:
                print("Clicking search btn...")
                btn.first.click()
                page.wait_for_timeout(3000)
            else:
                btn = page.locator("button", has_text="Search")
                if btn.count() > 0:
                    print("Clicking search text...")
                    btn.first.click()
                    page.wait_for_timeout(3000)
        except Exception as e:
            print("Error clicking:", e)
            
        browser.close()

if __name__ == "__main__":
    find_search_api()

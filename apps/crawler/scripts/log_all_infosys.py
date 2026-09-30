from playwright.sync_api import sync_playwright

def log_all():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        def handle_response(res):
            if res.status == 200 and "json" in res.headers.get("content-type", ""):
                print("JSON API:", res.url)
                
        page.on("response", handle_response)
        
        page.goto("https://career.infosys.com/joblist", wait_until="networkidle")
        page.wait_for_timeout(3000)
        browser.close()

if __name__ == "__main__":
    log_all()

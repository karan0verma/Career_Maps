import time
from playwright.sync_api import sync_playwright

def sniff_99acres():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        def handle_res(response):
            if 'api' in response.url.lower() or 'job' in response.url.lower() or 'search' in response.url.lower():
                try:
                    if response.status == 200 and 'json' in response.headers.get('content-type', ''):
                        print(f"JSON endpoint: {response.url}")
                        data = response.json()
                        print(str(data)[:200])
                except:
                    pass
                    
        page.on("response", handle_res)
        page.goto("https://careers.infoedge.com/infoedge/jobslist", wait_until="networkidle")
        time.sleep(3)
        browser.close()

if __name__ == "__main__":
    sniff_99acres()

import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()

    def log_request(request):
        if "search/api/v2" in request.url:
            print("Captured Request URL:", request.url)
            print("Captured Request Post Data:", request.post_data)

    def log_response(response):
        if "search/api/v2" in response.url:
            print("Captured Response Status:", response.status)
            try:
                data = response.json()
                print("Total IBM Hits:", data.get('hits', {}).get('total', {}).get('value'))
            except Exception as e:
                print("Response JSON err:", e)

    page.on("request", log_request)
    page.on("response", log_response)
    
    print("Navigating to IBM Careers...", flush=True)
    page.goto("https://www.ibm.com/careers/search?field_keyword_08_bm%5B0%5D=India", wait_until='domcontentloaded', timeout=30000)
    time.sleep(6)
    browser.close()

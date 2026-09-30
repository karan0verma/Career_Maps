from playwright.sync_api import sync_playwright
import time
import json

request_details = []

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()
    
    def handle_req(request):
        if "api/v1/jobs/searchJ" in request.url:
            request_details.append({
                "url": request.url,
                "method": request.method,
                "headers": request.headers,
                "post_data": request.post_data
            })
            print(f"[Captured searchJ Request]", flush=True)
            print("Method:", request.method, flush=True)
            print("Headers:", json.dumps(request.headers, indent=2), flush=True)
            print("Post Data:", request.post_data, flush=True)
            
    page.on("request", handle_req)
    
    page.goto('https://ibegin.tcsapps.com/candidate/#/jobs/search?geography=IN&language=EN', wait_until='networkidle', timeout=30000)
    time.sleep(3)
    
    browser.close()

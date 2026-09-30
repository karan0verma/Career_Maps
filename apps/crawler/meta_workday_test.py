import re
from playwright.sync_api import sync_playwright

def find_workday_meta():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        urls = []
        def log_req(r, req):
            if 'workday' in req.url.lower() or 'wday' in req.url.lower():
                urls.append(req.url)
            r.continue_()
            
        page.route("**/*", log_req)
        
        try:
            page.goto("https://www.metacareers.com/", timeout=30000, wait_until="networkidle")
        except Exception as e:
            print("Error:", e)
            
        print("Meta Workday URLs found:")
        for u in urls:
            print(u)
            
        browser.close()

find_workday_meta()

from playwright.sync_api import sync_playwright
import time
import json

captured_search = []

with sync_playwright() as p:
    browser = p.chromium.launch(
        channel='chrome',
        headless=True
    )
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        viewport={'width': 1440, 'height': 900}
    )
    page = context.new_page()
    
    def handle_res(response):
        url = response.url
        try:
            if "api/v1" in url and response.status == 200:
                text = response.text()
                if len(text) > 50:
                    captured_search.append({
                        "url": url,
                        "length": len(text),
                        "data": text
                    })
                    print(f"[API HIT] {url} ({len(text)} bytes)", flush=True)
        except Exception:
            pass
            
    page.on("response", handle_res)
    
    target = "https://ibegin.tcsapps.com/candidate/?geography=IN&language=EN"
    print(f"Navigating to {target} ...", flush=True)
    page.goto(target, wait_until="networkidle", timeout=30000)
    time.sleep(3)
    
    # Click on "Search Jobs" button
    print("Clicking Search Jobs button...", flush=True)
    search_btn = page.query_selector("button.btn-color, button.home, button:has-text('Search Jobs')")
    if search_btn:
        search_btn.click()
    else:
        print("Search button not found, clicking input...")
        
    time.sleep(6)
    
    print(f"\nCaptured {len(captured_search)} API responses during search:", flush=True)
    for c in captured_search:
        print(f"\n--- URL: {c['url']} ---")
        print(c['data'][:500])
        
    browser.close()

from playwright.sync_api import sync_playwright
import time
import json

captured_responses = []

print("Initializing Playwright for Coforge Careers...", flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--disable-http2', '--no-sandbox']
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        viewport={"width": 1440, "height": 900}
    )
    page = context.new_page()
    
    # Block analytics and ads to avoid hanging
    def block_unneeded(route):
        url = route.request.url.lower()
        if any(b in url for b in ['google-analytics', 'googletagmanager', 'cookiehub', 'hs-scripts', 'hubspot']):
            route.abort()
        else:
            route.continue_()
            
    page.route("**/*", block_unneeded)
    
    def handle_response(response):
        url = response.url
        try:
            content_type = response.headers.get("content-type", "")
            if "json" in content_type or any(k in url.lower() for k in ["job", "search", "career", "opening", "get", "api"]):
                if response.status == 200:
                    text = response.text()
                    if len(text) > 30 and any(k in text.lower() for k in ["job", "title", "location", "experience", "req", "skill", "id"]):
                        captured_responses.append({
                            "url": url,
                            "length": len(text),
                            "preview": text[:500]
                        })
                        print(f"[Captured API] {url} ({len(text)} bytes)", flush=True)
        except Exception:
            pass

    page.on("response", handle_response)
    
    print("Navigating to https://careers.coforge.com/coforge/ ...", flush=True)
    page.goto("https://careers.coforge.com/coforge/", wait_until="domcontentloaded", timeout=25000)
    
    time.sleep(5)
    
    print("\nPage title:", page.title(), flush=True)
    print("Body text preview:", page.inner_text('body')[:500].replace('\n', ' '), flush=True)
    
    # Check if there are cards rendered
    cards = page.evaluate("""() => {
        const results = [];
        document.querySelectorAll('.job-card, .job-item, .card, [class*="job"], [class*="card"]').forEach(el => {
            if (el.innerText && el.innerText.length > 20) {
                results.push(el.innerText);
            }
        });
        return results;
    }""")
    print(f"Found {len(cards)} candidate DOM elements:", flush=True)
    for c in cards[:5]:
        print("  - Card:", c[:120].replace('\n', ' | '), flush=True)
        
    browser.close()

print(f"\nTotal captured APIs: {len(captured_responses)}", flush=True)

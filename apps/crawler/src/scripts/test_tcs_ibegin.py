from playwright.sync_api import sync_playwright
import time
import json

captured_api = []

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
            content_type = response.headers.get("content-type", "")
            if "json" in content_type or any(k in url.lower() for k in ["job", "search", "candidate", "requisition", "opening"]):
                if response.status == 200:
                    text = response.text()
                    if len(text) > 30 and any(k in text.lower() for k in ["job", "title", "skill", "location", "experience"]):
                        captured_api.append({
                            "url": url,
                            "length": len(text),
                            "preview": text[:400]
                        })
                        print(f"[Captured API] {url} ({len(text)} bytes)", flush=True)
        except Exception:
            pass
            
    page.on("response", handle_res)
    
    target = "https://ibegin.tcsapps.com/candidate/?geography=IN&language=EN"
    print(f"Navigating to {target} ...", flush=True)
    page.goto(target, wait_until="networkidle", timeout=30000)
    time.sleep(5)
    
    print("Page Title:", page.title(), flush=True)
    print("Body snippet:", page.inner_text("body")[:500].replace("\n", " "), flush=True)
    
    # Check job cards or search inputs
    inputs = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('input, button, select')).map(el => ({
            tag: el.tagName,
            placeholder: el.placeholder || el.innerText,
            id: el.id,
            name: el.name,
            class: el.className
        }));
    }""")
    print(f"\nFound {len(inputs)} interactive elements on page:", flush=True)
    for inp in inputs[:10]:
        print("  - Element:", inp, flush=True)
        
    print(f"\nTotal captured candidate APIs: {len(captured_api)}", flush=True)
    for c in captured_api:
        print(f"  • {c['url']} -> {c['preview'][:150]}...", flush=True)
        
    browser.close()

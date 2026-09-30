from playwright.sync_api import sync_playwright
import time
import json

print("Launching Google Chrome for TCS Careers...", flush=True)

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
    
    captured = []
    page.on("response", lambda r: captured.append(r.url) if any(k in r.url.lower() for k in ['job', 'search', 'career', 'opportunity', 'api']) else None)
    
    print("Navigating to https://www.tcs.com/careers/india ...", flush=True)
    page.goto('https://www.tcs.com/careers/india', wait_until='domcontentloaded', timeout=30000)
    time.sleep(5)
    
    print("Title:", page.title(), flush=True)
    
    # Find all links
    links = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('a')).map(a => ({
            text: a.innerText.trim(),
            href: a.getAttribute('href')
        })).filter(l => l.href && (l.href.includes('job') || l.href.includes('career') || l.href.includes('ibegin') || l.href.includes('search') || l.href.includes('join')));
    }""")
    
    print(f"\nFound {len(links)} candidate links on TCS Careers page:", flush=True)
    for l in links:
        print(f"  - [{l['text']}]: {l['href']}", flush=True)
        
    print(f"\nCaptured {len(captured)} network URLs:", flush=True)
    for u in captured[:15]:
        print(f"  - API/Resource: {u}", flush=True)
        
    browser.close()

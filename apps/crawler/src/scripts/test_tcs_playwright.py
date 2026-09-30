from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        viewport={"width": 1440, "height": 900}
    )
    page = context.new_page()
    
    # Intercept responses
    page.on("response", lambda r: print(f"Response: {r.status} {r.url[:90]}") if "tcs" in r.url and r.status in [200, 302, 403] else None)
    
    print("Visiting https://www.tcs.com/careers/india ...")
    try:
        page.goto("https://www.tcs.com/careers/india", wait_until="domcontentloaded", timeout=25000)
        time.sleep(3)
        print("Page title:", page.title())
        print("Page text snippet:", page.inner_text("body")[:400].replace("\n", " "))
        
        # Find links
        links = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('a')).map(a => ({
                text: a.innerText.trim(),
                href: a.getAttribute('href')
            })).filter(l => l.href && (l.href.includes('job') || l.href.includes('career') || l.href.includes('ibegin') || l.href.includes('open')));
        }""")
        print(f"\nFound {len(links)} career links:")
        for l in links[:10]:
            print(f"  - [{l['text']}]: {l['href']}")
            
    except Exception as e:
        print("Error:", e)
        
    browser.close()

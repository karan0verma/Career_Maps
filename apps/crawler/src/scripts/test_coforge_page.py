from playwright.sync_api import sync_playwright
import time
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    urls_to_try = [
        'https://careers.coforge.com/coforge/',
        'https://careers.coforge.com/',
        'https://www.coforge.com/careers'
    ]
    for u in urls_to_try:
        try:
            print(f"Trying {u}...")
            page.goto(u, wait_until='domcontentloaded', timeout=25000)
            time.sleep(3)
            print(f"  Final URL: {page.url}")
            print(f"  Page Title: {page.title()}")
            text = page.inner_text('body')
            print(f"  Text length: {len(text)}")
            
            # Look for inputs / buttons / links
            links = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a')).map(a => ({
                    text: a.innerText.trim(),
                    href: a.getAttribute('href')
                })).filter(l => l.href && (l.href.includes('job') || l.href.includes('career') || l.href.includes('position') || l.href.includes('detail') || l.href.includes('search') || l.href.includes('apply')));
            }""")
            print(f"  Found {len(links)} candidate job/career links:")
            for l in links[:10]:
                print(f"    - {l['text']}: {l['href']}")
            print("=" * 60)
        except Exception as e:
            print(f"  Error visiting {u}: {e}")
    browser.close()

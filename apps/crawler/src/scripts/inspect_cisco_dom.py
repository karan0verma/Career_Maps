import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    page = browser.new_page()
    page.goto("https://careers.cisco.com/global/en/search-results?q=India", wait_until='networkidle', timeout=30000)
    time.sleep(4)

    # Evaluate all job cards
    jobs = page.evaluate("""() => {
        const cards = Array.from(document.querySelectorAll('.jobs-list-item, li.jobs-list-item, div.job-card'));
        // Try fallback if classes differ
        const items = cards.length > 0 ? cards : Array.from(document.querySelectorAll('a[href*="/job/"]')).map(a => a.parentElement);
        
        return items.map(c => {
            const link = c.querySelector('a[href*="/job/"]');
            if (!link) return null;
            const title = link.innerText.trim().split('\\n')[0];
            const locEl = c.querySelector('.job-location, .location, span:has-text("India")');
            const loc = locEl ? locEl.innerText.trim() : "Not Found";
            return { title, loc, href: link.href, html: c.innerHTML.substring(0, 150) };
        }).filter(Boolean).slice(0, 5);
    }""")
    print(jobs)
    browser.close()

from playwright.sync_api import sync_playwright
import time
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://careers.techmahindra.com/CurrentOpportunity.aspx', timeout=40000)
    time.sleep(2)
    
    # 1. Remove OneTrust Cookie Banner completely
    page.evaluate("""() => {
        const ot = document.getElementById('onetrust-consent-sdk');
        if (ot) ot.remove();
        const dark = document.querySelector('.onetrust-pc-dark-filter');
        if (dark) dark.remove();
    }""")
    time.sleep(1)
    
    # 2. Select Country India
    page.select_option('#ctl00_ContentPlaceHolder1_ddlCountry', label='India')
    time.sleep(1)
    
    # 3. Click Search using page.evaluate or force click
    page.evaluate("document.getElementById('ctl00_ContentPlaceHolder1_btnFreeSearch').click()")
    page.wait_for_load_state('networkidle', timeout=15000)
    time.sleep(3)
    
    # 4. Extract jobs table/cards
    rows = page.evaluate("""() => {
        const items = [];
        const tables = document.querySelectorAll('table');
        tables.forEach(t => {
            const trs = t.querySelectorAll('tr');
            trs.forEach(tr => {
                const text = tr.innerText.trim();
                const links = Array.from(tr.querySelectorAll('a')).map(a => ({
                    text: a.innerText.trim(),
                    href: a.getAttribute('href')
                }));
                if (links.length > 0 && text.length > 10) {
                    items.push({ text: text, links: links });
                }
            });
        });
        return items;
    }""")
    
    print(f"SUCCESS! Found {len(rows)} candidate rows with links:")
    for r in rows[:10]:
        print("ROW TEXT:", r['text'][:150])
        print("LINKS:", r['links'])
        print("-" * 50)
        
    browser.close()
